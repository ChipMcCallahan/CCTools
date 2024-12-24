import unittest
from cc_tools.cc2 import CC2
from cc_tools.c2m_element import C2MElement
from cc_tools.c2m_modifiers import C2MModifiers


class TestC2MModifiers(unittest.TestCase):
    """
    A comprehensive unittest suite for testing the C2MModifiers class and its
    helper methods. This test class ensures both parsing and building of
    modifiers for various CC2 tile types is verified thoroughly, including error
    handling paths.
    """

    # ---------------------------------------------------
    # parse_modifier / build_modifier tests
    # ---------------------------------------------------

    def test_parse_modifier_wires(self):
        """Test parsing wires & wire tunnels (1-byte)."""
        # Suppose tile_id is a wired tile (fake example).
        c2m = C2MElement(id=CC2.FLOOR)  # or any tile that belongs to CC2.wired()
        # For example: the lower nibble is wires, upper nibble is tunnels:
        #   bit0 = N-wire, bit1 = E-wire, bit4 = N-tunnel, etc.
        # Let’s encode N-wire and E-wire, plus S-tunnel (bit2=1 => E-wire, bit5=1 => E-tunnel).
        wire_byte = 0b00100111
        #   bit 0 = N-wire
        #   bit 1 = E-wire
        #   bit 2 = S-wire
        #   bit 5 = E-tunnel

        C2MModifiers.parse_modifier(c2m, bytes([wire_byte]))
        self.assertEqual(c2m.wires, "NES", "Wires should be 'NES'")
        self.assertEqual(c2m.wire_tunnels, "E", "Wire tunnels should be 'E'")

    def test_build_modifier_wires(self):
        """Test building wires & wire tunnels into 1-byte."""
        c2m = C2MElement(id=CC2.FLOOR, wires="NES", wire_tunnels="E")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, bytes([0b00100111]), "Should match the wire byte 0b00100111")

    def test_parse_modifier_letter_tile(self):
        """Test parsing a single letter tile byte."""
        c2m = C2MElement(id=CC2.LETTER_TILE_SPACE)
        # Suppose we pass the 'A' char => 0x41
        C2MModifiers.parse_modifier(c2m, b"\x41")
        self.assertEqual(c2m.char, "A")

        # Now test an arrow char, e.g. 0x1E => "↓"
        c2m2 = C2MElement(id=CC2.LETTER_TILE_SPACE)
        C2MModifiers.parse_modifier(c2m2, b"\x1E")
        self.assertEqual(c2m2.char, "↓")

    def test_build_modifier_letter_tile(self):
        """Test building a single letter tile byte."""
        c2m = C2MElement(id=CC2.LETTER_TILE_SPACE, char="Z")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x5A", "Z => ASCII 0x5A")

        # Arrow char
        c2m2 = C2MElement(id=CC2.LETTER_TILE_SPACE, char="←")
        built2 = C2MModifiers.build_modifier(c2m2)
        self.assertEqual(built2, bytes([0x1F]), "← => 0x1F")

    def test_parse_modifier_clone_machine(self):
        """Test parsing the directions for a clone machine tile."""
        c2m = C2MElement(id=CC2.CLONE_MACHINE)
        # Suppose the byte is 0x05 => bits 0 and 2 => N and S
        C2MModifiers.parse_modifier(c2m, b"\x05")
        self.assertEqual(c2m.directions, "NS")

    def test_build_modifier_clone_machine(self):
        """Test building the directions for a clone machine tile."""
        c2m = C2MElement(id=CC2.CLONE_MACHINE, directions="NS")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x05")

    def test_parse_modifier_custom_tile(self):
        """Test parsing a custom floor/wall color tile."""
        c2m = C2MElement(id=CC2.CUSTOM_FLOOR)
        # Suppose the color is YELLOW => 2
        C2MModifiers.parse_modifier(c2m, b"\x02")
        self.assertEqual(c2m.color, "Yellow")

    def test_build_modifier_custom_tile(self):
        """Test building a custom floor/wall color tile."""
        c2m = C2MElement(id=CC2.CUSTOM_FLOOR, color="Pink")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x01", "Pink => 1")

    def test_parse_modifier_logic_gate_counter(self):
        """Test parsing a logic gate set to a counter with digit."""
        c2m = C2MElement(id=CC2.LOGIC_GATE)
        # Suppose the byte is 0x24 => 0x1E + 6 => 'Counter_6'
        C2MModifiers.parse_modifier(c2m, b"\x24")
        self.assertEqual(c2m.gate, "Counter_6")

    def test_build_modifier_logic_gate_counter(self):
        """Test building a logic gate set to 'Counter_6'."""
        c2m = C2MElement(id=CC2.LOGIC_GATE, gate="Counter_6")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x24")

    def test_parse_modifier_logic_gate_inverter(self):
        """Test parsing an inverter gate with direction E."""
        c2m = C2MElement(id=CC2.LOGIC_GATE)
        # 0x01 => direction=1 => 'E', gate type=0 => 'Inverter'
        C2MModifiers.parse_modifier(c2m, b"\x01")
        self.assertEqual(c2m.gate, "Inverter_E")

    def test_build_modifier_logic_gate_inverter(self):
        """Test building an inverter gate with direction E => byte=0x01."""
        c2m = C2MElement(id=CC2.LOGIC_GATE, gate="Inverter_E")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x01")

    def test_parse_modifier_logic_gate_voodoo(self):
        """Test parsing a 'Voodoo_3A' with direction W => 0x3A + direction(3)."""
        c2m = C2MElement(id=CC2.LOGIC_GATE)
        C2MModifiers.parse_modifier(c2m, b"\x3D")
        self.assertEqual(c2m.gate, "Voodoo_3D")

    def test_build_modifier_logic_gate_voodoo(self):
        """Test building a 'Voodoo_3D' => base 0x3D."""
        c2m = C2MElement(id=CC2.LOGIC_GATE, gate="Voodoo_3D")
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x3D")

    def test_parse_modifier_railroad_track_8bit(self):
        """Test parsing an 8-bit railroad track byte."""
        c2m = C2MElement(id=CC2.RAILROAD_TRACK)
        # Suppose 0x13 => 00010011 => NE(1) + SE(2) + HORIZONTAL(8) => also active nibble=0 => NE
        # High nibble is 0, so initial_entry=0 => 'N'
        C2MModifiers.parse_modifier(c2m, b"\x13")
        self.assertEqual(c2m.tracks, ["NE", "SE", "HORIZONTAL"])
        self.assertEqual(c2m.active_track, "NE")     # lower nibble of high byte = 0
        self.assertEqual(c2m.initial_entry, "N")     # upper nibble of high byte = 0

    def test_parse_modifier_railroad_track_16bit(self):
        """Test parsing a 16-bit railroad track value."""
        c2m = C2MElement(id=CC2.RAILROAD_TRACK)
        # Suppose value = [0x1F, 0x21]
        #   low_byte=0x1F => NE, SE, SW, NW, HORIZONTAL
        #   high_byte=0x21 => 0x2(LS nibble=1 => 'SE', MS nibble=2 => 'S')
        # But note: high_byte=0x21 => binary(0010 0001)
        #   lower nibble = 1 => 'SE'
        #   upper nibble = 2 => 'S'
        # So initial_entry='S'
        C2MModifiers.parse_modifier(c2m, b"\x1F\x21")
        self.assertEqual(c2m.tracks, ["NE", "SE", "SW", "NW", "HORIZONTAL"])
        self.assertEqual(c2m.active_track, "SE")
        self.assertEqual(c2m.initial_entry, "S")

    def test_build_modifier_railroad_track_8bit(self):
        """Test building an 8-bit railroad track value."""
        c2m = C2MElement(
            id=CC2.RAILROAD_TRACK,
            tracks=["NE", "SE", "NW"],
            active_track="NE",    # => nibble=0
            initial_entry="N",    # => nibble=0
        )
        # This should build low_byte=NE(1) + SE(2) + NW(8)=0x0B => binary(1011)
        # Actually 1+2+8=11 decimal => 0x0B
        # Then high_byte= (N<<4 | NE) = (0<<4 | 0) = 0 => 0x00
        # => bytes([0x0B, 0x00])
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x0B\x00")

    def test_build_modifier_railroad_track_16bit(self):
        """Test building a 16-bit railroad track value."""
        c2m = C2MElement(
            id=CC2.RAILROAD_TRACK,
            tracks=["NE", "SE", "SW", "NW"],
            active_track="SE",    # => nibble=1
            initial_entry="S",    # => nibble=2
        )
        # low_byte=NE(1) + SE(2) + SW(4) + NW(8) = 15 => 0x0F
        # high_byte=(2<<4 | 1)=0x21
        # => bytes([0x0F, 0x21])
        built = C2MModifiers.build_modifier(c2m)
        self.assertEqual(built, b"\x0F\x21")

    def test_parse_modifier_invalid_length(self):
        """Test parse_modifier raises ValueError for invalid byte lengths."""
        c2m = C2MElement(id=CC2.LETTER_TILE_SPACE)
        with self.assertRaises(ValueError):
            # LETTER_TILE_SPACE expects exactly 1 byte
            C2MModifiers.parse_modifier(c2m, b"\x00\x01")

        c2m2 = C2MElement(id=CC2.RAILROAD_TRACK)
        with self.assertRaises(ValueError):
            # RAILROAD_TRACK expects 1 or 2 bytes, not 3
            C2MModifiers.parse_modifier(c2m2, b"\x00\x01\x02")

    def test_build_modifier_invalid_tile(self):
        """Test build_modifier raises ValueError for an unrecognized tile id."""
        # Tile that does not expect modifiers, e.g. WALL.
        c2m = C2MElement(id=CC2.WALL)
        with self.assertRaises(ValueError):
            C2MModifiers.build_modifier(c2m)

    def test_build_modifier_invalid_color(self):
        """Test build_modifier raises ValueError for an invalid custom color."""
        c2m = C2MElement(id=CC2.CUSTOM_FLOOR, color="Purple")
        with self.assertRaises(ValueError):
            C2MModifiers.build_modifier(c2m)

    def test_build_modifier_invalid_gate(self):
        """Test build_modifier raises ValueError for an unknown logic gate string."""
        c2m = C2MElement(id=CC2.LOGIC_GATE, gate="UNKNOWN_GATE_N")
        with self.assertRaises(ValueError):
            C2MModifiers.build_modifier(c2m)

    # ------------------------------------------------
    # parse_direction / build_direction tests
    # ------------------------------------------------

    def test_parse_direction(self):
        """Test parse_direction with valid and invalid data."""
        c2m = C2MElement(id=CC2.FLOOR)  # just pick any tile for demonstration
        C2MModifiers.parse_direction(c2m, b"\x02")  # => S
        self.assertEqual(c2m.direction, "S")

        with self.assertRaises(ValueError):
            C2MModifiers.parse_direction(c2m, b"\x05")  # invalid: only 0..3

        with self.assertRaises(ValueError):
            C2MModifiers.parse_direction(c2m, b"")  # missing byte

    def test_build_direction(self):
        """Test build_direction with valid and invalid direction strings."""
        c2m = C2MElement(id=CC2.FLOOR, direction="W")
        out = C2MModifiers.build_direction(c2m)
        self.assertEqual(out, b"\x03")

        c2m2 = C2MElement(id=CC2.FLOOR, direction="Z")
        with self.assertRaises(ValueError):
            C2MModifiers.build_direction(c2m2)

    # ------------------------------------------------
    # parse_thinwall_canopy / build_thinwall_canopy tests
    # ------------------------------------------------

    def test_parse_thinwall_canopy(self):
        """Test parse_thinwall_canopy with valid data."""
        c2m = C2MElement(id=CC2.THIN_WALL_CANOPY)
        C2MModifiers.parse_thinwall_canopy(c2m, b"\x19")
        # 0x19 = binary(11001) => bits: N(1), W(8), C(16) => "NWC"
        self.assertEqual(c2m.directions, "NWC")

        with self.assertRaises(ValueError):
            # must be exactly 1 byte
            C2MModifiers.parse_thinwall_canopy(c2m, b"\x01\x02")

    def test_build_thinwall_canopy(self):
        """Test build_thinwall_canopy to ensure correct bitmask."""
        c2m = C2MElement(id=CC2.THIN_WALL_CANOPY, directions="NWC")
        out = C2MModifiers.build_thinwall_canopy(c2m)
        self.assertEqual(out, b"\x19")

    # ------------------------------------------------
    # parse_dblock_arrows / build_dblock_arrows tests
    # ------------------------------------------------

    def test_parse_dblock_arrows(self):
        """Test parse_dblock_arrows with valid data."""
        c2m = C2MElement(id=CC2.DIRECTIONAL_BLOCK)  # pretend tile
        C2MModifiers.parse_dblock_arrows(c2m, b"\x09")
        # 0x09 = binary(1001) => N(1), W(8) => "NW"
        self.assertEqual(c2m.directions, "NW")

        with self.assertRaises(ValueError):
            # must be exactly 1 byte
            C2MModifiers.parse_dblock_arrows(c2m, b"\x01\x02")

    def test_build_dblock_arrows(self):
        """Test build_dblock_arrows to ensure correct bitmask."""
        c2m = C2MElement(id=CC2.DIRECTIONAL_BLOCK, directions="NW")
        out = C2MModifiers.build_dblock_arrows(c2m)
        self.assertEqual(out, b"\x09")

# ------------------------------------------------
# (Optionally) if you want to run via python -m unittest
# ------------------------------------------------
if __name__ == "__main__":
    unittest.main()
