from typing import Dict, Any
from enum import Enum, IntEnum

from .cc2 import CC2

# ------------------------------------------------
# Enums & Constants
# ------------------------------------------------

class Direction(IntEnum):
    """Represents a direction for logic gates, clone machines, and railroad entry."""
    N = 0
    E = 1
    S = 2
    W = 3


class CustomTileColor(IntEnum):
    """Represents the possible colors for custom floor/wall tiles."""
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
    VOODOO = "Voodoo"   # We store the base hex in data
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


class ModKey(Enum):
    """Enum representing all possible keys for modifier data."""
    WIRES = "wires"
    WIRE_TUNNELS = "wire_tunnels"
    CHAR = "char"
    DIRECTIONS = "directions"
    COLOR = "color"
    GATE = "gate"
    TRACKS = "tracks"
    ACTIVE_TRACK = "active_track"
    INITIAL_ENTRY = "initial_entry"


# Maps for arrow characters on letter tiles
ARROW_MAP = {
    0x1C: "↑",
    0x1D: "→",
    0x1E: "↓",
    0x1F: "←",
}
ARROW_MAP_INV = {v: k for k, v in ARROW_MAP.items()}


# ------------------------------------------------
# C2MModifiers class
# ------------------------------------------------

class C2MModifiers:
    @staticmethod
    def parse_modifier(tile_id: CC2, value: bytes) -> Dict[ModKey, Any]:
        """
        Parse the modifier bytes for the given tile (tile_id) and return
        a dictionary containing the relevant information.

        :param tile_id: The tile ID (from CC2).
        :param value: The raw modifier bytes for that tile.
        :return: A dictionary with parsed fields, e.g. { "wires": "NS", ... }
        """
        data: Dict[ModKey, Any] = {}

        # Validate length for either 1-byte or 2-byte modifiers
        if tile_id == CC2.RAILROAD_TRACK:
            if len(value) not in (1, 2):
                raise ValueError("Railroad track modifier must be 1 or 2 bytes.")
        else:
            if len(value) != 1:
                raise ValueError(f"Modifier must be exactly 1 byte for {tile_id}.")

        # ------------------ Wires & Wire Tunnels ------------------
        if tile_id in CC2.wired():
            wire_byte = value[0]
            directions_enum = [Direction.N, Direction.E, Direction.S, Direction.W]
            wires_list = []
            wire_tunnels_list = []

            for i, d in enumerate(directions_enum):
                if wire_byte & (1 << i):
                    wires_list.append(d.name)
                if wire_byte & (1 << (i + 4)):
                    wire_tunnels_list.append(d.name)

            data[ModKey.WIRES] = "".join(wires_list)
            data[ModKey.WIRE_TUNNELS] = "".join(wire_tunnels_list)

        # ------------------ Letter Tile ------------------
        elif tile_id == CC2.LETTER_TILE_SPACE:
            letter_val = value[0]
            if letter_val in ARROW_MAP:
                data[ModKey.CHAR] = ARROW_MAP[letter_val]
            elif 0x20 <= letter_val <= 0x5F:
                data[ModKey.CHAR] = chr(letter_val)
            else:
                data[ModKey.CHAR] = None

        # ------------------ Clone Machine ------------------
        elif tile_id == CC2.CLONE_MACHINE:
            clone_val = value[0]
            directions_enum = [Direction.N, Direction.E, Direction.S, Direction.W]
            result_dirs = []
            for d, bit_mask in zip(directions_enum, [0x01, 0x02, 0x04, 0x08]):
                if clone_val & bit_mask:
                    result_dirs.append(d.name)
            data[ModKey.DIRECTIONS] = "".join(result_dirs)

        # ------------------ Custom Floor/Wall ------------------
        elif tile_id in CC2.custom_tiles():
            color_val = value[0]
            try:
                # e.g. CustomTileColor.GREEN -> "GREEN", then capitalize -> "Green"
                data[ModKey.COLOR] = CustomTileColor(color_val).name.capitalize()
            except ValueError:
                raise ValueError(f"Unknown custom tile color value: {color_val}")

        # ------------------ Logic Gate ------------------
        elif tile_id == CC2.LOGIC_GATE:
            logic_val = value[0]
            if 0x1E <= logic_val <= 0x27:
                # e.g. 0x1E -> "Counter_0", 0x27 -> "Counter_9"
                digit = logic_val - 0x1E
                data[ModKey.GATE] = f"{LogicGateType.COUNTER.value}_{digit}"
            else:
                direction_idx = logic_val & 0x03
                try:
                    direction_str = Direction(direction_idx).name
                except ValueError:
                    direction_str = "N"

                # Determine gate type by range
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

                data[ModKey.GATE] = f"{gate_type}_{direction_str}"

        # ------------------ Railroad Track (8 or 16-bit) ------------------
        elif tile_id == CC2.RAILROAD_TRACK:
            track_val = value[0] | (value[1] << 8) if len(value) == 2 else value[0]
            low_byte = track_val & 0xFF
            high_byte = (track_val >> 8) & 0xFF

            # Track segments
            data[ModKey.TRACKS] = [
                seg.name for seg in TrackSegment if (low_byte & seg.value)
            ]

            # Active track (lower nibble of high byte)
            active_nibble = high_byte & 0x0F
            if active_nibble in ActiveTrack._value2member_map_:
                data[ModKey.ACTIVE_TRACK] = ActiveTrack(active_nibble).name
            else:
                data[ModKey.ACTIVE_TRACK] = None

            # Initial entry direction (upper nibble of high byte)
            entered_nibble = (high_byte >> 4) & 0x0F
            if entered_nibble in Direction._value2member_map_:
                data[ModKey.INITIAL_ENTRY] = Direction(entered_nibble).name
            else:
                data[ModKey.INITIAL_ENTRY] = None

        else:
            raise ValueError(f"Cannot apply modifier to tile with id={tile_id}")

        return data

    @staticmethod
    def build_modifier(tile_id: CC2, data: Dict[ModKey, Any]) -> bytes:
        """
        Given a tile id and a dictionary of fields (like the output of parse_modifier),
        build the corresponding bytes (1 or 2) for the tile's modifier.
        Raises ValueError for invalid data.
        """
        # ------------------ Wires & Wire Tunnels ------------------
        if tile_id in CC2.wired():
            wire_bits = 0
            directions_enum = [Direction.N, Direction.E, Direction.S, Direction.W]
            wires_str = data.get(ModKey.WIRES, "")
            wire_tunnels_str = data.get(ModKey.WIRE_TUNNELS, "")
            for i, d in enumerate(directions_enum):
                if d.name in wires_str:
                    wire_bits |= (1 << i)
                if d.name in wire_tunnels_str:
                    wire_bits |= (1 << (i + 4))
            return bytes([wire_bits])

        # ------------------ Letter Tile ------------------
        elif tile_id == CC2.LETTER_TILE_SPACE:
            c = data.get(ModKey.CHAR)
            if c is None:
                return bytes([0])
            if c in ARROW_MAP_INV:
                return bytes([ARROW_MAP_INV[c]])

            val = ord(c)
            if 0x20 <= val <= 0x5F:
                return bytes([val])
            return bytes([0])  # fallback

        # ------------------ Clone Machine ------------------
        elif tile_id == CC2.CLONE_MACHINE:
            clone_val = 0
            directions_enum = [Direction.N, Direction.E, Direction.S, Direction.W]
            directions_str = data.get(ModKey.DIRECTIONS, "")
            for d, bit_mask in zip(directions_enum, [0x01, 0x02, 0x04, 0x08]):
                if d.name in directions_str:
                    clone_val |= bit_mask
            return bytes([clone_val])

        # ------------------ Custom Floor/Wall ------------------
        elif tile_id in CC2.custom_tiles():
            color_str = data.get(ModKey.COLOR, "")
            try:
                color_val = CustomTileColor[color_str.upper()].value
            except KeyError:
                raise ValueError(f"Unknown custom tile color: {color_str}")
            return bytes([color_val])

        # ------------------ Logic Gate ------------------
        elif tile_id == CC2.LOGIC_GATE:
            gate_str = data.get(ModKey.GATE, "")
            if gate_str.startswith(f"{LogicGateType.COUNTER.value}_"):
                try:
                    digit_str = gate_str.replace(f"{LogicGateType.COUNTER.value}_", "")
                    digit = int(digit_str)
                except ValueError:
                    raise ValueError(f"Invalid counter gate string: {gate_str}")
                if not (0 <= digit <= 9):
                    raise ValueError(f"Counter value out of range: {digit}")
                logic_val = 0x1E + digit
            else:
                parts = gate_str.split("_")
                if len(parts) == 1:
                    # e.g. "AND" => default direction N
                    gate_type_str = parts[0]
                    direction_str = "N"
                elif len(parts) == 2:
                    gate_type_str, direction_str = parts
                else:
                    # Possibly "Voodoo_3A_N" => 3 parts
                    gate_type_str = "_".join(parts[:-1])
                    direction_str = parts[-1]

                try:
                    direction_val = Direction[direction_str].value
                except KeyError:
                    raise ValueError(f"Invalid direction '{direction_str}' in gate {gate_str}")

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
                    logic_val = 0x40 + direction_val
                elif gate_type_str.startswith(LogicGateType.VOODOO.value + "_"):
                    try:
                        # e.g. "Voodoo_3A" => "3A"
                        hex_str = gate_type_str.split("_", 1)[1]
                        base_val = int(hex_str, 16)
                    except (IndexError, ValueError):
                        raise ValueError(f"Error with voodoo logic gate '{gate_type_str}'")
                    logic_val = base_val + direction_val
                else:
                    raise ValueError(f"Unknown logic gate '{gate_type_str}' in '{gate_str}'")

            return bytes([logic_val])

        # ------------------ Railroad Track (16-bit) ------------------
        elif tile_id == CC2.RAILROAD_TRACK:
            low_byte = 0
            high_byte = 0

            # Build low_byte from track segments
            segments_str_list = data.get(ModKey.TRACKS, [])
            if not isinstance(segments_str_list, list):
                raise ValueError("Expected 'tracks' to be a list of track segment names.")
            for seg_str in segments_str_list:
                try:
                    seg_val = TrackSegment[seg_str].value
                except KeyError:
                    raise ValueError(f"Invalid track segment '{seg_str}'")
                low_byte |= seg_val

            # Build high_byte: lower nibble = active track, upper nibble = initial entry
            active_track_str = data.get(ModKey.ACTIVE_TRACK, ActiveTrack.NE.name)
            try:
                active_nib = ActiveTrack[active_track_str].value
            except KeyError:
                raise ValueError(f"Invalid active track '{active_track_str}'")

            init_entry_str = data.get(ModKey.INITIAL_ENTRY, Direction.N.name)
            try:
                init_nib = Direction[init_entry_str].value
            except KeyError:
                raise ValueError(f"Invalid initial entry direction '{init_entry_str}'")

            high_byte = (init_nib << 4) | active_nib
            return bytes([low_byte, high_byte])

        else:
            raise ValueError(f"Cannot build modifier for tile with id={tile_id}")

    # ---------------------------------------------------------------------
    # Additional parse/build helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def parse_direction(data: bytes) -> str:
        """
        Parse a single-byte direction (0=N,1=E,2=S,3=W).
        :param data: Exactly 1 byte.
        :return: One of {"N","E","S","W"}.
        """
        if len(data) != 1:
            raise ValueError("Direction byte must be exactly 1 byte")
        val = data[0]
        if val not in range(4):
            raise ValueError(f"Invalid direction byte {val}")
        return Direction(val).name

    @staticmethod
    def build_direction(direction_str: str) -> bytes:
        """
        Build a single-byte direction from a string in {"N","E","S","W"}.
        :param direction_str: e.g. "N"
        :return: A single byte with the direction value.
        """
        try:
            return bytes([Direction[direction_str].value])
        except KeyError:
            raise ValueError(f"Invalid direction string '{direction_str}'")

    @staticmethod
    def parse_thinwall_canopy(data: bytes) -> str:
        """
        Parse a single-byte thin wall/canopy bitmask.
          - Bits: 0x1(N),0x2(E),0x4(S),0x8(W),0x10(Canopy).
          - Returns e.g. "NWC".
        """
        assert len(data) == 1, "Thin wall/canopy bitmask must be exactly 1 byte"
        val = data[0]
        parts = []
        if val & 0x01: parts.append("N")
        if val & 0x02: parts.append("E")
        if val & 0x04: parts.append("S")
        if val & 0x08: parts.append("W")
        if val & 0x10: parts.append("C")
        return "".join(parts)

    @staticmethod
    def build_thinwall_canopy(walls_str: str) -> bytes:
        """Inverse of parse_thinwall_canopy, e.g. "NWC" -> b'\x19'."""
        val = 0
        if "N" in walls_str: val |= 0x01
        if "E" in walls_str: val |= 0x02
        if "S" in walls_str: val |= 0x04
        if "W" in walls_str: val |= 0x08
        if "C" in walls_str: val |= 0x10
        return bytes([val])

    @staticmethod
    def parse_dblock_arrows(data: bytes) -> str:
        """
        Parse a single-byte directional block bitmask:
          - Bits: 0x1(N),0x2(E),0x4(S),0x8(W).
          - Returns e.g. "NW".
        """
        assert len(data) == 1, "Directional block bitmask must be exactly 1 byte"
        val = data[0]
        parts = []
        if val & 0x01: parts.append("N")
        if val & 0x02: parts.append("E")
        if val & 0x04: parts.append("S")
        if val & 0x08: parts.append("W")
        return "".join(parts)

    @staticmethod
    def build_dblock_arrows(arrows_str: str) -> bytes:
        """Inverse of parse_dblock_arrows, e.g. "NW" -> b'\x09'."""
        val = 0
        if "N" in arrows_str: val |= 0x01
        if "E" in arrows_str: val |= 0x02
        if "S" in arrows_str: val |= 0x04
        if "W" in arrows_str: val |= 0x08
        return bytes([val])