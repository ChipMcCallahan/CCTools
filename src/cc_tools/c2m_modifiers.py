from typing import Dict, Any
from enum import Enum, IntEnum

from .cc2 import CC2


# -----------------------
# Enums & Constants
# -----------------------

class Direction(IntEnum):
    """Represents a direction for logic gates, clone machines, and railroad entry."""
    N = 0
    E = 1
    S = 2
    W = 3


class CustomTileStyle(IntEnum):
    """Represents the possible styles for custom floor/wall tiles."""
    GREEN = 0
    PINK = 1
    YELLOW = 2
    BLUE = 3


class LogicGateType(Enum):
    """Represents the recognized logic gate types."""
    INVERTER = "Inverter"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    LATCH_CW = "LatchCW"
    NAND = "NAND"
    LATCH_CCW = "LatchCCW"
    VOODOO = "Voodoo"   # This one is special; we store the base hex in data
    COUNTER = "Counter" # This is for Counter_0..Counter_9


class TrackSegment(IntEnum):
    """Represents each possible railroad track segment bit in the low byte."""
    NE = 1
    SE = 2
    SW = 4
    NW = 8
    HORIZONTAL = 16
    VERTICAL = 32
    SWITCH = 64


class ActiveTrack(IntEnum):
    """Represents the possible active tracks in the lower nibble of the high byte."""
    NE = 0
    SE = 1
    SW = 2
    NW = 3
    HORIZONTAL = 4
    VERTICAL = 5


# Maps for arrow characters on letter tiles
ARROW_MAP = {
    0x1C: "↑",
    0x1D: "→",
    0x1E: "↓",
    0x1F: "←",
}

ARROW_MAP_INV = {v: k for k, v in ARROW_MAP.items()}  # e.g. {"↑": 0x1C, "→": 0x1D, ...}


# -----------------------
# C2MModifiers class
# -----------------------

class C2MModifiers:
    @staticmethod
    def parse(tile_id: CC2, value: bytes) -> Dict[str, Any]:
        """
        Parse the modifier bytes for the given tile (tile_id) and return
        a dictionary containing the relevant information.
        """
        data: Dict[str, Any] = {}

        # Validate length for either 1-byte or 2-byte modifiers
        if tile_id == CC2.RAILROAD_TRACK:
            if len(value) != 2:
                raise ValueError("Railroad track modifier must be exactly 2 bytes.")
        else:
            if len(value) != 1:
                raise ValueError("Modifier must be exactly 1 byte (except railroad track).")

        # -- Wire modifier (8-bit) -------------------------------------------
        if tile_id in CC2.wired():
            wire_byte = value[0]
            # For wires and wire tunnels, use the lowest 4 bits for wires, highest 4 bits for tunnels
            all_dirs = [Direction.N, Direction.E, Direction.S, Direction.W]
            wire_dirs = []
            wire_tun_dirs = []
            for i, d in enumerate(all_dirs):
                if wire_byte & (1 << i):
                    wire_dirs.append(d.name)
                if wire_byte & (1 << (i + 4)):
                    wire_tun_dirs.append(d.name)

            data["wires"] = "".join(wire_dirs)
            data["wire_tunnels"] = "".join(wire_tun_dirs)

        # -- Letter tile modifier (8-bit) ------------------------------------
        elif tile_id == CC2.LETTER_TILE_SPACE:
            letter_val = value[0]

            # Use arrow if in ARROW_MAP, else ASCII char if in [0x20..0x5F], else None
            if letter_val in ARROW_MAP:
                data["char"] = ARROW_MAP[letter_val]
            elif 0x20 <= letter_val <= 0x5F:
                data["char"] = chr(letter_val)
            else:
                data["char"] = None

        # -- Clone machine arrow modifier (8-bit) ----------------------------
        elif tile_id == CC2.CLONE_MACHINE:
            clone_val = value[0]
            all_dirs = [Direction.N, Direction.E, Direction.S, Direction.W]
            directions = []
            for d, bit in zip(all_dirs, [0x01, 0x02, 0x04, 0x08]):
                if clone_val & bit:
                    directions.append(d.name)
            data["directions"] = "".join(directions)

        # -- Custom floor/wall modifier (8-bit) ------------------------------
        elif tile_id in CC2.custom_tiles():
            style_val = value[0]
            try:
                data["style"] = CustomTileStyle(style_val).name.capitalize()  # e.g. "Green"
            except ValueError:
                raise ValueError(f"Unknown custom tile style value: {style_val}")

        # -- Logic modifier (8-bit) ------------------------------------------
        elif tile_id == CC2.LOGIC_GATE:
            logic_val = value[0]
            # Check for counter range
            if 0x1E <= logic_val <= 0x27:
                # e.g. 0x1E -> Counter_0, 0x27 -> Counter_9
                digit = logic_val - 0x1E
                data["gate"] = f"{LogicGateType.COUNTER.value}_{digit}"
            else:
                # direction = logic_val % 4
                direction_idx = logic_val & 0x03
                try:
                    direction_str = Direction(direction_idx).name
                except ValueError:
                    direction_str = "N"  # fallback, or raise an error

                # Gate type depends on which range it's in
                gate_type = None
                if 0x00 <= logic_val <= 0x03:
                    gate_type = LogicGateType.INVERTER.value
                elif 0x04 <= logic_val <= 0x07:
                    gate_type = LogicGateType.AND.value
                elif 0x08 <= logic_val <= 0x0B:
                    gate_type = LogicGateType.OR.value
                elif 0x0C <= logic_val <= 0x0F:
                    gate_type = LogicGateType.XOR.value
                elif 0x10 <= logic_val <= 0x13:
                    gate_type = LogicGateType.LATCH_CW.value
                elif 0x14 <= logic_val <= 0x17:
                    gate_type = LogicGateType.NAND.value
                elif 0x40 <= logic_val <= 0x43:
                    gate_type = LogicGateType.LATCH_CCW.value
                else:
                    # treat it as Voodoo
                    gate_type = f"{LogicGateType.VOODOO.value}_{logic_val:02X}"

                data["gate"] = f"{gate_type}_{direction_str}"

        # -- Railroad track modifier (16-bit, little endian) -----------------
        elif tile_id == CC2.RAILROAD_TRACK:
            track_val = value[0] | (value[1] << 8)  # little endian
            data["track_value"] = track_val

            low_byte = track_val & 0xFF
            high_byte = (track_val >> 8) & 0xFF

            # Track segments in the low byte
            segments = []
            for seg_enum in TrackSegment:
                if low_byte & seg_enum.value:
                    segments.append(seg_enum.name)
            data["tracks"] = segments

            # Active track in lower nibble of high_byte
            active_nibble = high_byte & 0x0F
            try:
                data["active_track"] = ActiveTrack(active_nibble).name
            except ValueError:
                data["active_track"] = "Unknown"

            # Initial entry direction in upper nibble of high_byte
            entered_nibble = (high_byte >> 4) & 0x0F
            try:
                data["initial_entry"] = Direction(entered_nibble).name
            except ValueError:
                data["initial_entry"] = "Unknown"

        else:
            raise ValueError(f"Cannot apply modifier to tile with id={tile_id}")

        return data

    @staticmethod
    def build(tile_id: CC2, data: Dict[str, Any]) -> bytes:
        """
        Given a tile id and a dictionary of fields (like the output of parse),
        build the corresponding bytes (1 or 2) for the tile's modifier.
        Raises ValueError for invalid data.
        """
        # -- Wire modifier (8-bit) -------------------------------------------
        if tile_id in CC2.wired():
            # data["wires"] = e.g. "NESW" subset
            # data["wire_tunnels"] = e.g. "NESW" subset
            wire_bits = 0
            all_dirs = [Direction.N, Direction.E, Direction.S, Direction.W]
            wires_str = data.get("wires", "")
            wire_tunnels_str = data.get("wire_tunnels", "")
            for i, d in enumerate(all_dirs):
                if d.name in wires_str:
                    wire_bits |= (1 << i)
                if d.name in wire_tunnels_str:
                    wire_bits |= (1 << (i + 4))
            return bytes([wire_bits])

        # -- Letter tile modifier (8-bit) ------------------------------------
        elif tile_id == CC2.LETTER_TILE_SPACE:
            # data["char"] could be arrow or ASCII
            c = data.get("char")
            if c is None:
                return bytes([0])

            if c in ARROW_MAP_INV:
                return bytes([ARROW_MAP_INV[c]])

            val = ord(c)
            # ASCII in [0x20..0x5F]
            if 0x20 <= val <= 0x5F:
                return bytes([val])
            return bytes([0])  # fallback if invalid

        # -- Clone machine arrow modifier (8-bit) ----------------------------
        elif tile_id == CC2.CLONE_MACHINE:
            clone_val = 0
            all_dirs = [Direction.N, Direction.E, Direction.S, Direction.W]
            directions_str = data.get("directions", "")
            for d, bit in zip(all_dirs, [0x01, 0x02, 0x04, 0x08]):
                if d.name in directions_str:
                    clone_val |= bit
            return bytes([clone_val])

        # -- Custom floor/wall modifier (8-bit) ------------------------------
        elif tile_id in CC2.custom_tiles():
            style_str = data.get("style", "")
            # We expect "Green", "Pink", "Yellow", "Blue" (capitalized from enum.name)
            # Attempt to match an enum:
            try:
                style_val = CustomTileStyle[style_str.upper()].value
            except KeyError:
                raise ValueError(f"Unknown custom tile style: {style_str}")
            return bytes([style_val])

        # -- Logic modifier (8-bit) ------------------------------------------
        elif tile_id == CC2.LOGIC_GATE:
            gate_str = data.get("gate", "")
            if gate_str.startswith(f"{LogicGateType.COUNTER.value}_"):
                # "Counter_X"
                try:
                    digit_str = gate_str.replace(f"{LogicGateType.COUNTER.value}_", "")
                    digit = int(digit_str)
                except ValueError:
                    raise ValueError(f"Invalid counter gate string: {gate_str}")
                if not (0 <= digit <= 9):
                    raise ValueError(f"Counter value out of range (0..9): {digit}")
                logic_val = 0x1E + digit

            else:
                # e.g. "AND_E", "Inverter_W", "Voodoo_3A_N", etc.
                parts = gate_str.split("_")
                if len(parts) == 1:
                    # e.g. "AND" (no direction) => default N
                    gate_type_str = parts[0]
                    direction_str = "N"
                elif len(parts) == 2:
                    gate_type_str, direction_str = parts
                else:
                    # Possibly "Voodoo_3A_N" => 3 parts
                    gate_type_str = "_".join(parts[:-1])  # e.g. "Voodoo_3A"
                    direction_str = parts[-1]

                # Validate direction
                try:
                    direction_val = Direction[direction_str].value
                except KeyError:
                    raise ValueError(f"Invalid direction '{direction_str}' in gate {gate_str}")

                # Map gate types to logic_val
                if gate_type_str == LogicGateType.INVERTER.value:
                    logic_val = 0x00 + direction_val
                elif gate_type_str == LogicGateType.AND.value:
                    logic_val = 0x04 + direction_val
                elif gate_type_str == LogicGateType.OR.value:
                    logic_val = 0x08 + direction_val
                elif gate_type_str == LogicGateType.XOR.value:
                    logic_val = 0x0C + direction_val
                elif gate_type_str == LogicGateType.LATCH_CW.value:
                    logic_val = 0x10 + direction_val
                elif gate_type_str == LogicGateType.NAND.value:
                    logic_val = 0x14 + direction_val
                elif gate_type_str == LogicGateType.LATCH_CCW.value:
                    # 0x40..0x43
                    logic_val = 0x40 + direction_val
                elif gate_type_str.startswith(LogicGateType.VOODOO.value + "_"):
                    # e.g. "Voodoo_3A"
                    try:
                        # after 'Voodoo_', we have "3A"
                        hex_str = gate_type_str.split("_", 1)[1]
                        base_val = int(hex_str, 16)
                    except (IndexError, ValueError):
                        raise ValueError(f"Error with voodoo logic gate '{gate_type_str}'")
                    logic_val = base_val + direction_val
                else:
                    raise ValueError(f"Unknown logic gate '{gate_type_str}' in '{gate_str}'")

            return bytes([logic_val])

        # -- Railroad track modifier (16-bit, little endian) -----------------
        elif tile_id == CC2.RAILROAD_TRACK:
            low_byte = 0
            high_byte = 0

            # 1) Build low_byte from track segments
            segments_str_list = data.get("tracks", [])
            if not isinstance(segments_str_list, list):
                raise ValueError("Expected 'tracks' to be a list of track segment names.")
            for seg_str in segments_str_list:
                try:
                    seg_val = TrackSegment[seg_str].value
                except KeyError:
                    raise ValueError(f"Invalid track segment '{seg_str}'")
                low_byte |= seg_val

            # 2) Build high_byte: lower nibble = active track, upper nibble = initial entry
            active_track_str = data.get("active_track", ActiveTrack.NE.name)
            try:
                active_nib = ActiveTrack[active_track_str].value
            except KeyError:
                raise ValueError(f"Invalid active track '{active_track_str}'")

            init_entry_str = data.get("initial_entry", Direction.N.name)
            try:
                init_nib = Direction[init_entry_str].value
            except KeyError:
                raise ValueError(f"Invalid initial entry direction '{init_entry_str}'")

            high_byte = (init_nib << 4) | active_nib

            return bytes([low_byte, high_byte])

        else:
            raise ValueError(f"Cannot build modifier for tile with id={tile_id}")
