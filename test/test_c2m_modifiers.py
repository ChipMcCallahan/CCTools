import unittest

# Import both the C2MModifiers class and the ModKey enum:
from cc_tools.c2m_modifiers import C2MModifiers, ModKey
from cc_tools.cc2 import CC2

class TestC2MModifiers(unittest.TestCase):

    def test_wire_modifier_parse(self):
        """
        Test parsing wire modifiers on a tile known to be "wired".
        Example: tile_id = 0x50.
        """
        tile_id = CC2.FLOOR  # in CC2.wired()
        # Byte example: 0b10010010 = 0x92
        #   - wires (lowest nibble) = 0b0010 => East
        #   - wire_tunnels (upper nibble) = 0b1001 => North, West
        test_value = bytes([0x92])

        result = C2MModifiers.parse_modifier(tile_id, test_value)
        self.assertIn(ModKey.WIRES, result)
        self.assertIn(ModKey.WIRE_TUNNELS, result)
        self.assertEqual(result[ModKey.WIRES], "E")     # East only
        self.assertEqual(result[ModKey.WIRE_TUNNELS], "NW")  # North, West

    def test_wire_modifier_build(self):
        """
        Test building wire modifiers.
        """
        tile_id = CC2.FLOOR  # in CC2.wired()
        data = {
            ModKey.WIRES: "SE",         # South, East
            ModKey.WIRE_TUNNELS: "N",   # North
        }
        # wires (S,E) => bits 2,1 => 0b0110 = 0x06
        # wire_tunnels (N) => bit 4 => 0b10000 = 0x10
        # combined => 0x16
        result_bytes = C2MModifiers.build_modifier(tile_id, data)
        self.assertEqual(result_bytes, bytes([0x16]))

    def test_wire_modifier_invalid_length(self):
        """
        Test that parsing an invalid byte length for a wired tile raises ValueError.
        """
        tile_id = CC2.FLOOR
        with self.assertRaises(ValueError):
            C2MModifiers.parse_modifier(tile_id, bytes([0x01, 0x02]))  # 2 bytes is invalid

    def test_letter_tile_parse(self):
        """
        Test parsing a letter tile (including arrow and ASCII checks).
        """
        tile_id = CC2.LETTER_TILE_SPACE

        # 0x1E => "↓" arrow
        result_arrow = C2MModifiers.parse_modifier(tile_id, bytes([0x1E]))
        self.assertEqual(result_arrow[ModKey.CHAR], "↓")

        # 0x41 => 'A'
        result_char = C2MModifiers.parse_modifier(tile_id, bytes([0x41]))
        self.assertEqual(result_char[ModKey.CHAR], "A")

        # 0x1B => outside arrow range, not ASCII 20..5F => None
        result_none = C2MModifiers.parse_modifier(tile_id, bytes([0x1B]))
        self.assertIsNone(result_none[ModKey.CHAR])

    def test_letter_tile_build(self):
        """
        Test building letter tile modifiers from arrow or ASCII.
        """
        tile_id = CC2.LETTER_TILE_SPACE

        # Arrow
        data_arrow = {ModKey.CHAR: "←"}
        result_arrow = C2MModifiers.build_modifier(tile_id, data_arrow)
        self.assertEqual(result_arrow, bytes([0x1F]))

        # ASCII
        data_char = {ModKey.CHAR: "Z"}
        result_char = C2MModifiers.build_modifier(tile_id, data_char)
        self.assertEqual(result_char, bytes([0x5A]))  # 'Z' => 0x5A

        # None or invalid => 0
        data_invalid = {ModKey.CHAR: "ß"}  # outside 0x20..0x5F
        result_invalid = C2MModifiers.build_modifier(tile_id, data_invalid)
        self.assertEqual(result_invalid, bytes([0x00]))

    def test_clone_machine_parse(self):
        """
        Test parsing clone machine directions.
        """
        tile_id = CC2.CLONE_MACHINE
        # 0x0D => binary 0b1101 => N (1), E (0), S (1), W (1)
        result = C2MModifiers.parse_modifier(tile_id, bytes([0x0D]))
        self.assertEqual(result[ModKey.DIRECTIONS], "NSW")

    def test_clone_machine_build(self):
        """
        Test building clone machine directions.
        """
        tile_id = CC2.CLONE_MACHINE
        # directions = "NEW" => bits for N=1, E=2, W=8 => total 0x0B
        data = {ModKey.DIRECTIONS: "NEW"}
        result_bytes = C2MModifiers.build_modifier(tile_id, data)
        self.assertEqual(result_bytes, bytes([0x0B]))

    def test_custom_tiles_parse(self):
        """
        Test parsing custom tiles (floor/wall) color.
        """
        tile_id = CC2.CUSTOM_FLOOR
        # Suppose 0 => Green, 1 => Pink, 2 => Yellow, 3 => Blue
        result = C2MModifiers.parse_modifier(tile_id, bytes([2]))
        self.assertEqual(result[ModKey.COLOR], "Yellow")

        # Invalid color
        with self.assertRaises(ValueError):
            C2MModifiers.parse_modifier(tile_id, bytes([9]))

    def test_custom_tiles_build(self):
        """
        Test building custom tile modifiers.
        """
        tile_id = CC2.CUSTOM_FLOOR
        data = {ModKey.COLOR: "Blue"}
        result = C2MModifiers.build_modifier(tile_id, data)
        self.assertEqual(result, bytes([3]))  # 'Blue' => 3

        # Invalid color
        data_invalid = {ModKey.COLOR: "Rainbow"}
        with self.assertRaises(ValueError):
            C2MModifiers.build_modifier(tile_id, data_invalid)

    def test_logic_gate_parse_inverter(self):
        """
        Test logic gate parse: Inverter facing East => 0x01.
        """
        tile_id = CC2.LOGIC_GATE
        result = C2MModifiers.parse_modifier(tile_id, bytes([0x01]))
        self.assertEqual(result[ModKey.GATE], "Inverter_E")

    def test_logic_gate_parse_counter(self):
        """
        Test logic gate parse: Counter_5 => 0x1E + 5 = 0x23.
        """
        tile_id = CC2.LOGIC_GATE
        result = C2MModifiers.parse_modifier(tile_id, bytes([0x23]))
        self.assertEqual(result[ModKey.GATE], "Counter_5")

    def test_logic_gate_build_xor_south(self):
        """
        Test building a logic gate: XOR facing South => base=0x0C plus direction=2 => 0x0E
        """
        tile_id = CC2.LOGIC_GATE
        data = {ModKey.GATE: "XOR_S"}
        result = C2MModifiers.build_modifier(tile_id, data)
        self.assertEqual(result, bytes([0x0E]))

    def test_logic_gate_build_counter(self):
        """
        Test building a logic gate for Counter_9 => 0x1E + 9 => 0x27
        """
        tile_id = CC2.LOGIC_GATE
        data = {ModKey.GATE: "Counter_9"}
        result = C2MModifiers.build_modifier(tile_id, data)
        self.assertEqual(result, bytes([0x27]))

    def test_logic_gate_build_invalid_direction(self):
        """
        Test building a logic gate with an invalid direction should raise ValueError.
        """
        tile_id = CC2.LOGIC_GATE
        with self.assertRaises(ValueError):
            C2MModifiers.build_modifier(tile_id, {ModKey.GATE: "XOR_X"})

    def test_railroad_track_parse(self):
        """
        Test parsing a 2-byte railroad track modifier.

        Example:
            - low_byte=0x0D => segments NE(1), SW(4), NW(8) => 0b1101
            - high_byte=0x31 =>
                - lower nibble=0x1 => ActiveTrack.SE
                - upper nibble=0x3 => Direction.W

        This means:
            - Track segments: ["NE", "SW", "NW"]
            - Active track: "SE"
            - Initial entry direction: "W"
        """
        tile_id = CC2.RAILROAD_TRACK
        # low_byte=0x0D => NE(1) + SW(4) + NW(8) => 0b1101
        # high_byte=0x31 =>
        #     - lower nibble=0x1 => ActiveTrack.SE
        #     - upper nibble=0x3 => Direction.W
        track_bytes = bytes([0x0D, 0x31])
        result = C2MModifiers.parse_modifier(tile_id, track_bytes)

        # Ensure 'tracks' key exists and contains the correct segments
        self.assertIn(ModKey.TRACKS, result)
        self.assertCountEqual(result[ModKey.TRACKS], ["NE", "SW", "NW"])  # from 0x0D

        # Verify the active track is correctly parsed
        self.assertEqual(result[ModKey.ACTIVE_TRACK], "SE")

        # Verify the initial entry direction is correctly parsed
        self.assertEqual(result[ModKey.INITIAL_ENTRY], "W")

    def test_railroad_track_build(self):
        """
        Test building a 2-byte railroad track modifier from dictionary data.
        """
        tile_id = CC2.RAILROAD_TRACK
        data = {
            ModKey.TRACKS: ["SE", "SW", "VERTICAL"],  # SE=2, SW=4, Vertical=32 => total 0x26
            ModKey.ACTIVE_TRACK: "NE",                # NE => 0
            ModKey.INITIAL_ENTRY: "S",                # S => 2
        }
        # low_byte=0x26, high_byte => (2 << 4) | 0 => 0x20
        # => resulting bytes = [0x26, 0x20]
        result = C2MModifiers.build_modifier(tile_id, data)
        self.assertEqual(result, bytes([0x26, 0x20]))

    def test_railroad_track_invalid_length(self):
        """
        Test parsing an invalid length for railroad track (must be 2 bytes if 2 bytes are present).
        """
        tile_id = CC2.RAILROAD_TRACK
        with self.assertRaises(ValueError):
            C2MModifiers.parse_modifier(tile_id, bytes([0x01] * 4))  # 4 bytes is invalid

    def test_cannot_apply_modifier_to_unknown_tile(self):
        """
        Test that parse fails if tile_id is not recognized.
        """
        with self.assertRaises(ValueError):
            C2MModifiers.parse_modifier(CC2.WATER, bytes([0x00]))  # Tile that does not accept modifiers.

        with self.assertRaises(ValueError):
            C2MModifiers.build_modifier(CC2.WATER, {})  # same for build

    # ---------------------------------------
    # Tests for parse_direction / build_direction
    # ---------------------------------------
    def test_direction_valid(self):
        """
        Test building/ parsing all valid directions: N, E, S, W.
        """
        cases = [
            ("N", 0),
            ("E", 1),
            ("S", 2),
            ("W", 3),
        ]
        for dir_str, expected_val in cases:
            with self.subTest(direction=dir_str):
                built = C2MModifiers.build_direction(dir_str)
                self.assertEqual(built, bytes([expected_val]),
                                 f"build_direction({dir_str}) should produce 0x{expected_val:02X}")

                parsed = C2MModifiers.parse_direction(built)
                self.assertEqual(parsed, dir_str,
                                 f"parse_direction({built}) should return '{dir_str}'")

    def test_direction_invalid_string(self):
        """
        Test that building a direction with an invalid string raises ValueError.
        """
        with self.assertRaises(ValueError):
            C2MModifiers.build_direction("X")  # invalid direction letter

    def test_direction_invalid_byte(self):
        """
        Test that parsing an invalid direction byte raises ValueError.
        """
        for invalid_val in [4, 5, 99]:
            with self.subTest(val=invalid_val):
                with self.assertRaises(ValueError):
                    C2MModifiers.parse_direction(bytes([invalid_val]))

    def test_direction_wrong_length(self):
        """
        Test that parse_direction fails if byte length != 1.
        """
        # No bytes
        with self.assertRaises(ValueError):
            C2MModifiers.parse_direction(b"")
        # More than 1 byte
        with self.assertRaises(ValueError):
            C2MModifiers.parse_direction(b"\x00\x01")

    # ---------------------------------------
    # Tests for parse_thinwall_canopy / build_thinwall_canopy
    # ---------------------------------------
    def test_thinwall_canopy_valid(self):
        """
        Test round-trip build->parse for several thin wall/canopy combos.
        'C' indicates canopy bit.
        """
        cases = [
            ("", 0x00),     # no walls, no canopy
            ("N", 0x01),    # north
            ("E", 0x02),    # east
            ("S", 0x04),    # south
            ("W", 0x08),    # west
            ("C", 0x10),    # canopy only
            ("NW", 0x09),   # north + west
            ("NWC", 0x19),  # north + west + canopy
            ("NESW", 0x0F), # all walls
            ("NESWC", 0x1F) # all walls + canopy
        ]
        for walls_str, expected_val in cases:
            with self.subTest(walls=walls_str):
                built = C2MModifiers.build_thinwall_canopy(walls_str)
                self.assertEqual(built, bytes([expected_val]),
                                 f"build_thinwall_canopy({walls_str}) -> 0x{expected_val:02X}")

                parsed = C2MModifiers.parse_thinwall_canopy(built)
                self.assertEqual(parsed, walls_str,
                                 f"parse_thinwall_canopy({built}) -> '{walls_str}'")

    def test_thinwall_canopy_wrong_length(self):
        """Ensure parse fails if not exactly 1 byte."""
        with self.assertRaises(AssertionError):
            C2MModifiers.parse_thinwall_canopy(b"")
        with self.assertRaises(AssertionError):
            C2MModifiers.parse_thinwall_canopy(b"\x00\x10")

    # ---------------------------------------
    # Tests for parse_dblock_arrows / build_dblock_arrows
    # ---------------------------------------
    def test_dblock_arrows_valid(self):
        """
        Test round-trip for directional block arrows: bits for N/E/S/W.
        """
        cases = [
            ("", 0x00),
            ("N", 0x01),
            ("E", 0x02),
            ("S", 0x04),
            ("W", 0x08),
            ("NE", 0x03),
            ("NES", 0x07),
            ("NESW", 0x0F),
            ("NW", 0x09),
        ]
        for arrows_str, expected_val in cases:
            with self.subTest(arrows=arrows_str):
                built = C2MModifiers.build_dblock_arrows(arrows_str)
                self.assertEqual(built, bytes([expected_val]),
                                 f"build_dblock_arrows({arrows_str}) -> 0x{expected_val:02X}")

                parsed = C2MModifiers.parse_dblock_arrows(built)
                self.assertEqual(parsed, arrows_str,
                                 f"parse_dblock_arrows({built}) -> '{arrows_str}'")

    def test_dblock_arrows_wrong_length(self):
        """Ensure parse fails if not exactly 1 byte."""
        with self.assertRaises(AssertionError):
            C2MModifiers.parse_dblock_arrows(b"")
        with self.assertRaises(AssertionError):
            C2MModifiers.parse_dblock_arrows(b"\x00\x01")

if __name__ == "__main__":
    unittest.main()
