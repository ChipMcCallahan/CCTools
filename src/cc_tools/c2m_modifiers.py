from enum import Enum, IntEnum

from .c2m_handler import C2MElement
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
    VOODOO = "Voodoo"     # We store the base hex in data
    COUNTER = "Counter"   # This is for Counter_0..Counter_9


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
ARROW_MAP_INV = {v: k for k, v in ARROW_MAP.items()}

# ------------------------------------------------
# C2MModifiers class
# ------------------------------------------------

class C2MModifiers:
    @staticmethod
    def parse_modifier(c2m: C2MElement, value: bytes) -> None:
        """
        Parse the modifier bytes for the given C2MElement's tile ID (c2m.id).
        The parsed information is stored directly in the fields of `c2m`.

        :param c2m: A C2MElement whose 'id' indicates the tile type, and whose
                    fields will be mutated in-place to store the parsed data.
        :param value: The raw modifier bytes for that tile (1 or 2 bytes).
        :return: None
        """

        tile_id = c2m.id

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

            c2m.wires = "".join(wires_list)
            c2m.wire_tunnels = "".join(wire_tunnels_list)

        # ------------------ Letter Tile ------------------
        elif tile_id == CC2.LETTER_TILE_SPACE:
            letter_val = value[0]
            if letter_val in ARROW_MAP:
                c2m.char = ARROW_MAP[letter_val]
            elif 0x20 <= letter_val <= 0x5F:
                c2m.char = chr(letter_val)
            else:
                c2m.char = None

        # ------------------ Clone Machine ------------------
        elif tile_id == CC2.CLONE_MACHINE:
            clone_val = value[0]
            directions_enum = [Direction.N, Direction.E, Direction.S, Direction.W]
            result_dirs = []
            for d, bit_mask in zip(directions_enum, [0x01, 0x02, 0x04, 0x08]):
                if clone_val & bit_mask:
                    result_dirs.append(d.name)
            c2m.directions = "".join(result_dirs)

        # ------------------ Custom Floor/Wall ------------------
        elif tile_id in CC2.custom_tiles():
            color_val = value[0]
            try:
                # e.g. CustomTileColor.GREEN -> "GREEN", then "Green"
                c2m.color = CustomTileColor(color_val).name.capitalize()
            except ValueError:
                raise ValueError(f"Unknown custom tile color value: {color_val}")

        # ------------------ Logic Gate ------------------
        elif tile_id == CC2.LOGIC_GATE:
            logic_val = value[0]
            if 0x1E <= logic_val <= 0x27:
                # e.g. 0x1E -> "Counter_0", 0x27 -> "Counter_9"
                digit = logic_val - 0x1E
                c2m.gate = f"{LogicGateType.COUNTER.value}_{digit}"
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
                    c2m.gate = gate_type

                c2m.gate = c2m.gate or f"{gate_type}_{direction_str}"

        # ------------------ Railroad Track (8 or 16-bit) ------------------
        elif tile_id == CC2.RAILROAD_TRACK:
            track_val = value[0] | (value[1] << 8) if len(value) == 2 else value[0]
            low_byte = track_val & 0xFF
            high_byte = (track_val >> 8) & 0xFF

            # Track segments
            segments = []
            for seg in TrackSegment:
                if low_byte & seg.value:
                    segments.append(seg.name)
            c2m.tracks = segments

            # Active track (lower nibble of high byte)
            active_nibble = high_byte & 0x0F
            if active_nibble in ActiveTrack._value2member_map_:
                c2m.active_track = ActiveTrack(active_nibble).name
            else:
                c2m.active_track = None

            # Initial entry direction (upper nibble of high byte)
            entered_nibble = (high_byte >> 4) & 0x0F
            if entered_nibble in Direction._value2member_map_:
                c2m.initial_entry = Direction(entered_nibble).name
            else:
                c2m.initial_entry = None

        else:
            raise ValueError(f"Cannot apply modifier to tile with id={tile_id}")

    @staticmethod
    def build_modifier(c2m: C2MElement) -> bytes:
        """
        Given a C2MElement (with a tile id in c2m.id and fields that have been
        set accordingly), build the corresponding bytes (1 or 2) for the tile's
        modifier. Raises ValueError for invalid data.

        :param c2m: A C2MElement with its fields (e.g. wires, gate, etc.) set.
        :return: A bytes object containing the built modifier bytes.
        """
        tile_id = c2m.id

        # ------------------ Wires & Wire Tunnels ------------------
        if tile_id in CC2.wired():
            wire_bits = 0
            directions_enum = [Direction.N, Direction.E, Direction.S, Direction.W]
            wires_str = c2m.wires or ""
            wire_tunnels_str = c2m.wire_tunnels or ""
            for i, d in enumerate(directions_enum):
                if d.name in wires_str:
                    wire_bits |= (1 << i)
                if d.name in wire_tunnels_str:
                    wire_bits |= (1 << (i + 4))
            return bytes([wire_bits])

        # ------------------ Letter Tile ------------------
        elif tile_id == CC2.LETTER_TILE_SPACE:
            c = c2m.char
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
            directions_str = c2m.directions or ""
            for d, bit_mask in zip(directions_enum, [0x01, 0x02, 0x04, 0x08]):
                if d.name in directions_str:
                    clone_val |= bit_mask
            return bytes([clone_val])

        # ------------------ Custom Floor/Wall ------------------
        elif tile_id in CC2.custom_tiles():
            color_str = c2m.color or ""
            try:
                color_val = CustomTileColor[color_str.upper()].value
            except KeyError:
                raise ValueError(f"Unknown custom tile color: {color_str}")
            return bytes([color_val])

        # ------------------ Logic Gate ------------------
        elif tile_id == CC2.LOGIC_GATE:
            gate_str = c2m.gate or ""
            if gate_str.startswith(f"{LogicGateType.COUNTER.value}_"):
                # e.g. "Counter_3"
                try:
                    digit_str = gate_str.replace(f"{LogicGateType.COUNTER.value}_", "")
                    digit = int(digit_str)
                except ValueError:
                    raise ValueError(f"Invalid counter gate string: {gate_str}")
                if not (0 <= digit <= 9):
                    raise ValueError(f"Counter value out of range: {digit}")
                logic_val = 0x1E + digit

            elif gate_str.startswith(f"{LogicGateType.VOODOO.value}_"):
                # e.g. "Voodoo_3A"
                try:
                    hex_str = gate_str.split("_", 1)[1]
                    logic_val = int(hex_str, 16)
                except (IndexError, ValueError):
                    raise ValueError(f"Error with voodoo logic gate '{gate_str}'")

            else:
                # Everything else uses direction bits
                parts = gate_str.split("_")
                if len(parts) == 1:
                    # e.g. "AND" => default direction = "N"
                    gate_type_str = parts[0]
                    direction_str = "N"
                elif len(parts) == 2:
                    gate_type_str, direction_str = parts
                else:
                    # e.g. "LatchCW_N"
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
                else:
                    raise ValueError(f"Unknown logic gate '{gate_type_str}' in '{gate_str}'")

            return bytes([logic_val])

        # ------------------ Railroad Track (16-bit) ------------------
        elif tile_id == CC2.RAILROAD_TRACK:
            low_byte = 0
            high_byte = 0

            # Build low_byte from track segments
            segments_str_list = c2m.tracks if c2m.tracks is not None else []
            if not isinstance(segments_str_list, list):
                raise ValueError("Expected 'tracks' to be a list of track segment names.")
            for seg_str in segments_str_list:
                try:
                    seg_val = TrackSegment[seg_str].value
                except KeyError:
                    raise ValueError(f"Invalid track segment '{seg_str}'")
                low_byte |= seg_val

            # Build high_byte: lower nibble = active track, upper nibble = initial entry
            active_track_str = c2m.active_track if c2m.active_track is not None else ActiveTrack.NE.name
            try:
                active_nib = ActiveTrack[active_track_str].value
            except KeyError:
                raise ValueError(f"Invalid active track '{active_track_str}'")

            init_entry_str = c2m.initial_entry if c2m.initial_entry is not None else Direction.N.name
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
    def parse_direction(c2m: C2MElement, data: bytes) -> None:
        """
        Parse a single-byte direction (0=N,1=E,2=S,3=W) into c2m.direction.
        :param c2m: The C2MElement to update.
        :param data: Exactly 1 byte indicating the direction.
        :return: None
        """
        if len(data) != 1:
            raise ValueError("Direction byte must be exactly 1 byte")
        val = data[0]
        if val not in range(4):
            raise ValueError(f"Invalid direction byte {val}")
        c2m.direction = Direction(val).name

    @staticmethod
    def build_direction(c2m: C2MElement) -> bytes:
        """
        Build a single-byte direction from c2m.direction (one of {"N","E","S","W"}).
        :param c2m: The C2MElement whose 'direction' field is used.
        :return: A single byte with the direction value.
        """
        direction_str = c2m.direction or "N"  # default to "N" if not set
        try:
            return bytes([Direction[direction_str].value])
        except KeyError:
            raise ValueError(f"Invalid direction string '{direction_str}'")

    @staticmethod
    def parse_thinwall_canopy(c2m: C2MElement, data: bytes) -> None:
        """
        Parse a single-byte thin wall/canopy bitmask into c2m.directions.
          - Bits: 0x1(N),0x2(E),0x4(S),0x8(W),0x10(Canopy).
          - Example result: "NWC".
        :param c2m: The C2MElement to update.
        :param data: Exactly 1 byte indicating the wall/canopy bits.
        :return: None
        """
        if len(data) != 1:
            raise ValueError("Thin wall/canopy bitmask must be exactly 1 byte")
        val = data[0]
        parts = []
        if val & 0x01: parts.append("N")
        if val & 0x02: parts.append("E")
        if val & 0x04: parts.append("S")
        if val & 0x08: parts.append("W")
        if val & 0x10: parts.append("C")
        c2m.directions = "".join(parts)

    @staticmethod
    def build_thinwall_canopy(c2m: C2MElement) -> bytes:
        """
        Build a single-byte thin wall/canopy bitmask from c2m.directions.
        Inverse of parse_thinwall_canopy, e.g. "NWC" -> b'\\x19'.
        :param c2m: The C2MElement whose 'directions' field is used.
        :return: A single byte with the wall/canopy bits.
        """
        walls_str = c2m.directions or ""
        val = 0
        if "N" in walls_str: val |= 0x01
        if "E" in walls_str: val |= 0x02
        if "S" in walls_str: val |= 0x04
        if "W" in walls_str: val |= 0x08
        if "C" in walls_str: val |= 0x10
        return bytes([val])

    @staticmethod
    def parse_dblock_arrows(c2m: C2MElement, data: bytes) -> None:
        """
        Parse a single-byte directional block bitmask into c2m.directions.
          - Bits: 0x1(N),0x2(E),0x4(S),0x8(W).
          - Example result: "NW".
        :param c2m: The C2MElement to update.
        :param data: Exactly 1 byte indicating the directional block bits.
        :return: None
        """
        if len(data) != 1:
            raise ValueError("Directional block bitmask must be exactly 1 byte")
        val = data[0]
        parts = []
        if val & 0x01: parts.append("N")
        if val & 0x02: parts.append("E")
        if val & 0x04: parts.append("S")
        if val & 0x08: parts.append("W")
        c2m.directions = "".join(parts)

    @staticmethod
    def build_dblock_arrows(c2m: C2MElement) -> bytes:
        """
        Build a single-byte directional block bitmask from c2m.directions.
        Inverse of parse_dblock_arrows, e.g. "NW" -> b'\\x09'.
        :param c2m: The C2MElement whose 'directions' field is used.
        :return: A single byte with the directional block bits.
        """
        arrows_str = c2m.directions or ""
        val = 0
        if "N" in arrows_str: val |= 0x01
        if "E" in arrows_str: val |= 0x02
        if "S" in arrows_str: val |= 0x04
        if "W" in arrows_str: val |= 0x08
        return bytes([val])
