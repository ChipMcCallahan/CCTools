import unittest

from cc_tools.cc2 import CC2
from cc_tools.c2m_cell import C2MCell, Direction


class TestC2MCell(unittest.TestCase):
    def test_create_simple_tile(self):
        """Test creating a simple tile with no optional fields set."""
        floor_tile = C2MCell(tile_type=CC2.FLOOR)
        self.assertEqual(floor_tile.tile_type, CC2.FLOOR)
        self.assertIsNone(floor_tile.direction)
        self.assertIsNone(floor_tile.lower_layer)
        self.assertEqual(floor_tile.wire_bitmask, 0)
        self.assertEqual(floor_tile.track_mask, 0)
        self.assertEqual(floor_tile.track_active, 0)
        self.assertIsNone(floor_tile.track_enter_dir)
        self.assertIsNone(floor_tile.custom_style)
        self.assertIsNone(floor_tile.logic_modifier)
        self.assertIsNone(floor_tile.letter_symbol)
        self.assertEqual(floor_tile.raw_modifier_bytes, b"")

    def test_tile_with_direction(self):
        """Test creating a tile that includes a direction byte."""
        chip_tile = C2MCell(tile_type=CC2.CHIP, direction=Direction.N)
        self.assertEqual(chip_tile.tile_type, CC2.CHIP)
        self.assertEqual(chip_tile.direction, Direction.N)
        self.assertIsNone(chip_tile.lower_layer)

    def test_tile_with_lower_layer(self):
        """Test creating a tile that has a lower-layer tile."""
        floor_tile = C2MCell(tile_type=CC2.FLOOR)
        key_tile = C2MCell(tile_type=CC2.RED_KEY, lower_layer=floor_tile)

        self.assertEqual(key_tile.tile_type, CC2.RED_KEY)
        self.assertIsNotNone(key_tile.lower_layer)
        self.assertEqual(key_tile.lower_layer.tile_type, CC2.FLOOR)
        self.assertIsNone(key_tile.direction)

    def test_tile_with_wire_bitmask(self):
        """Test creating a tile that includes wire bits."""
        wired_floor = C2MCell(tile_type=CC2.FLOOR, wire_bitmask=0x0F)
        self.assertEqual(wired_floor.tile_type, CC2.FLOOR)
        self.assertEqual(wired_floor.wire_bitmask, 0x0F)

    def test_railroad_track_tile(self):
        """Test creating a tile that has track data."""
        track_tile = C2MCell(
            tile_type=CC2.RAILROAD_TRACK,
            track_mask=0x03,
            track_active=0x00,
            track_enter_dir=Direction.N
        )
        self.assertEqual(track_tile.tile_type, CC2.RAILROAD_TRACK)
        self.assertEqual(track_tile.track_mask, 0x03)
        self.assertEqual(track_tile.track_active, 0x00)
        self.assertEqual(track_tile.track_enter_dir, Direction.N)

    def test_custom_style_tile(self):
        """Test creating a tile that uses a custom style."""
        custom_floor = C2MCell(tile_type=CC2.CUSTOM_FLOOR, custom_style=2)
        self.assertEqual(custom_floor.tile_type, CC2.CUSTOM_FLOOR)
        self.assertEqual(custom_floor.custom_style, 2)

    def test_logic_modifier_tile(self):
        """Test a logic gate tile with a modifier."""
        logic_tile = C2MCell(tile_type=CC2.LOGIC_GATE, logic_modifier=0x4)
        self.assertEqual(logic_tile.tile_type, CC2.LOGIC_GATE)
        self.assertEqual(logic_tile.logic_modifier, 0x4)

    def test_letter_tile_symbol(self):
        """Test creating a tile that references a letter/ASCII symbol."""
        letter_tile = C2MCell(tile_type=CC2.LETTER_TILE_SPACE, letter_symbol='A')
        self.assertEqual(letter_tile.tile_type, CC2.LETTER_TILE_SPACE)
        self.assertEqual(letter_tile.letter_symbol, 'A')

    def test_modifier_tile(self):
        """Test creating a modifier tile that carries raw modifier bytes."""
        raw_mod = bytes([0x12, 0x34])
        modifier_tile = C2MCell(tile_type=CC2.MODIFIER_16BIT, raw_modifier_bytes=raw_mod)
        self.assertEqual(modifier_tile.tile_type, CC2.MODIFIER_16BIT)
        self.assertEqual(modifier_tile.raw_modifier_bytes, b'\x12\x34')

    def test_tile_repr(self):
        """Quick test to ensure __repr__ doesn't crash and looks sane."""
        tile = C2MCell(tile_type=CC2.FLOOR, direction=Direction.S, wire_bitmask=0x05)
        r = repr(tile)
        self.assertIn("FLOOR", r)
        self.assertIn("direction=S", r)
        self.assertIn("wire_bitmask=0x05", r)


if __name__ == '__main__':
    unittest.main()