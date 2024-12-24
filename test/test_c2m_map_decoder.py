import unittest
from unittest.mock import patch

from cc_tools.cc2 import CC2
from cc_tools.c2m_cell import C2MCell
from cc_tools.c2m_element import C2MElement
from cc_tools.c2m_modifiers import C2MModifiers
from cc_tools.c2m_map_decoder import C2MMapDecoder

class TestC2MMapDecoder(unittest.TestCase):
    """
    Comprehensive tests for the C2MMapDecoder class.
    Verifies decoding logic, out-of-bounds checks, and interaction with modifiers.
    """

    def test_decode_basic(self):
        """
        Test a basic map of width=2, height=1, plus some fake tile IDs.
        We'll just store two tiles, each with known IDs.
        """
        # Construct data:
        #  First byte: width=2
        #  Second byte: height=1
        #  Then tile IDs for left->right, top->bottom (2 tiles total).
        #  We'll do: [  CC2.FLOOR (0x02), CC2.WALL (0x03) ] as placeholders.
        data = bytes([
            0x02,  # width
            0x01,  # height
            0x02,  # tile ID #1 => e.g. CC2.FLOOR
            0x03,  # tile ID #2 => e.g. CC2.WALL
        ])

        decoder = C2MMapDecoder(data)
        result = decoder.decode()

        # We expect a 1-row, 2-column list of lists
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)

        # Check the first tile
        cell1: C2MCell = result[0][0]
        self.assertIsNotNone(cell1.terrain)
        self.assertEqual(cell1.terrain.id, CC2(0x02))

        # Check the second tile
        cell2: C2MCell = result[0][1]
        self.assertIsNotNone(cell2.terrain)
        self.assertEqual(cell2.terrain.id, CC2(0x03))

    def test_decode_multi_row(self):
        """
        Test a map with width=2, height=2 => 4 tiles in total.
        """
        # Layout:
        #   row0: [0x02, 0x03]
        #   row1: [0x05, 0x06]
        data = bytes([
            2,  # width
            2,  # height
            0x02,  # tile #1
            0x03,  # tile #2
            0x05,  # tile #3
            0x06,  # tile #4
        ])
        decoder = C2MMapDecoder(data)
        grid = decoder.decode()

        self.assertEqual(len(grid), 2)       # 2 rows
        self.assertEqual(len(grid[0]), 2)    # row0 has 2 cells
        self.assertEqual(len(grid[1]), 2)    # row1 has 2 cells

        # row0 col0 => tile=0x02
        self.assertEqual(grid[0][0].terrain.id, CC2(0x02))
        # row0 col1 => tile=0x03
        self.assertEqual(grid[0][1].terrain.id, CC2(0x03))
        # row1 col0 => tile=0x05
        self.assertEqual(grid[1][0].terrain.id, CC2(0x05))
        # row1 col1 => tile=0x06
        self.assertEqual(grid[1][1].terrain.id, CC2(0x06))

    def test_decode_modifier_tile(self):
        """
        Test a scenario where we encounter a MODIFIER tile that references another tile.
        For example, CC2.MODIFIER_8BIT => read 1 extra byte, then parse the next tile.
        """
        # Test CC2.MODIFIER_8BIT, which means:
        #   - read 1 byte as 'modifier_bytes'
        #   - then parse the next tile's ID
        #   - apply parse_modifier
        # We'll just do a minimal mock: next tile => 0x10, plus 1 modifier byte => 0xAA
        # Enough to show the flow.

        data = bytes([
            1,  # width
            1,  # height
            CC2.MODIFIER_8BIT.value,
            0xAA,  # 1 byte of modifier data
            0x10,  # the "modified" tile ID
        ])

        decoder = C2MMapDecoder(data)

        with patch.object(C2MModifiers, 'parse_modifier', autospec=True) as mock_parse:
            grid = decoder.decode()
            # Ensure parse_modifier was called with a C2MElement(0x10) and bytes([0xAA]).
            mock_parse.assert_called_once()
            args, kwargs = mock_parse.call_args
            modified_elem_arg, modifier_bytes_arg = args
            self.assertIsInstance(modified_elem_arg, C2MElement)
            self.assertEqual(modified_elem_arg.id, CC2(0x10))
            self.assertEqual(modifier_bytes_arg, b"\xAA")

            # Check that result is 1x1 with terrain=0x10
            self.assertEqual(len(grid), 1)
            self.assertEqual(len(grid[0]), 1)
            cell = grid[0][0]
            self.assertEqual(cell.terrain.id, CC2(0x10))

    def test_decode_all_mobs(self):
        """
        Test reading a tile ID that is in CC2.all_mobs(), ensuring parse_direction is called.
        We'll mock parse_direction to verify it's used.
        """
        mob_to_test = CC2.BLOB  # any mob tile ID
        data = bytes([
            1,  # width
            1,  # height
            mob_to_test.value,
            0x01,  # direction byte
            CC2.FLOOR.value,  # Give a terrain ID to satisfy the decoder
        ])
        decoder = C2MMapDecoder(data)

        with patch.object(C2MModifiers, 'parse_direction', autospec=True) as mock_dir:
            grid = decoder.decode()
            mock_dir.assert_called_once()
            # ensure cell.mob is set (since it's in all_mobs)
            self.assertIsNotNone(grid[0][0].mob)
            self.assertEqual(grid[0][0].mob.id, mob_to_test)

    def test_out_of_bounds_read_bytes(self):
        """
        Test that _read_bytes raises ValueError if data is too short.
        """
        # Data has only 1 byte, but we'll try to decode 2x2 => 4 tiles => out of bounds
        data = bytes([2])  # width=2, missing the height => out of bounds
        decoder = C2MMapDecoder(data)
        with self.assertRaises(ValueError) as ctx:
            decoder.decode()
        self.assertIn("Tried to read", str(ctx.exception))

    def test_out_of_bounds_read_int(self):
        """
        Test that _read_int raises ValueError if offset + n > len(data).
        """
        data = b"\x02"  # only 1 byte (width=2), missing height
        decoder = C2MMapDecoder(data)
        with self.assertRaises(ValueError) as ctx:
            decoder.decode()
        self.assertIn("Tried to read", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
