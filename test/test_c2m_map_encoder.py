import unittest
from unittest.mock import patch

from cc_tools.cc2 import CC2
from cc_tools.c2m_cell import C2MCell
from cc_tools.c2m_element import C2MElement
from cc_tools.c2m_modifiers import C2MModifiers
from cc_tools.c2m_map_decoder import C2MMapDecoder
from cc_tools.c2m_map_encoder import C2MMapEncoder

class TestC2MMapEncoder(unittest.TestCase):
    """
    Tests for the C2MMapEncoder class, ensuring that we can properly encode
    a 2D grid of C2MCell objects and then decode them back via C2MMapDecoder.
    """

    def test_empty_map(self):
        """
        Ensure that encoding an empty 2D list yields 0,0 for width and height.
        """
        cells_2d = []
        encoder = C2MMapEncoder(cells_2d)
        encoded = encoder.encode()

        # We expect just two zero bytes [ 00 00 ]
        self.assertEqual(encoded, b"\x00\x00")

        # Decoding that should produce an empty list
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()
        self.assertEqual(decoded, [])

    def test_basic_map(self):
        """
        Test a 2x1 map with two simple terrain tiles.
        """
        # Create a row: [C2MCell(terrain=FLOOR), C2MCell(terrain=WALL)]
        row = [
            C2MCell(terrain=C2MElement(CC2.FLOOR)),
            C2MCell(terrain=C2MElement(CC2.WALL)),
        ]
        cells_2d = [row]

        # Encode
        encoder = C2MMapEncoder(cells_2d)
        encoded = encoder.encode()

        # Decode
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()

        self.assertEqual(len(decoded), 1, "Should have 1 row")
        self.assertEqual(len(decoded[0]), 2, "Should have 2 columns")

        # Check first cell => terrain=FLOOR
        self.assertIsNotNone(decoded[0][0].terrain)
        self.assertEqual(decoded[0][0].terrain.id, CC2.FLOOR)

        # Check second cell => terrain=WALL
        self.assertIsNotNone(decoded[0][1].terrain)
        self.assertEqual(decoded[0][1].terrain.id, CC2.WALL)

    def test_mob_with_direction(self):
        """
        Test a single-cell map containing a mob tile (in CC2.all_mobs()),
        with direction bits set. We'll patch build_direction to ensure it's called.
        """
        # Suppose CC2.BALL is in all_mobs()
        # Let's set direction="E" in the C2MElement
        c2m_elem = C2MElement(id=CC2.BALL, direction="E")
        row = [C2MCell(mob=c2m_elem, terrain=C2MElement(id=CC2.FLOOR))]
        cells_2d = [row]

        with patch.object(C2MModifiers, 'build_direction', wraps=C2MModifiers.build_direction) as mock_dir:
            encoder = C2MMapEncoder(cells_2d)
            encoded = encoder.encode()
            # Ensure build_direction was called
            mock_dir.assert_called_once()

        # Now decode to verify round-trip
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()

        self.assertEqual(len(decoded), 1)
        self.assertEqual(len(decoded[0]), 1)
        self.assertIsNotNone(decoded[0][0].mob)
        self.assertEqual(decoded[0][0].mob.id, CC2.BALL)
        self.assertEqual(decoded[0][0].mob.direction, "E")

    def test_directional_block_arrows(self):
        """
        Test a single-cell map containing a DIRECTIONAL_BLOCK tile,
        which requires both direction and dblock_arrows.
        """
        # Suppose CC2.DIRECTIONAL_BLOCK is also in all_mobs().
        c2m_elem = C2MElement(id=CC2.DIRECTIONAL_BLOCK, direction="N", directions="NW")
        # 'directions' is used for dblock_arrows => "NW" => bits 0x09
        row = [C2MCell(mob=c2m_elem, terrain=C2MElement(id=CC2.FLOOR))]
        cells_2d = [row]

        encoder = C2MMapEncoder(cells_2d)
        encoded = encoder.encode()

        # decode
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()

        self.assertEqual(decoded[0][0].mob.id, CC2.DIRECTIONAL_BLOCK)
        self.assertEqual(decoded[0][0].mob.direction, "N")
        self.assertEqual(decoded[0][0].mob.directions, "NW")  # dblock_arrows

    def test_thin_wall_canopy(self):
        """
        Test a single-cell map containing a thin wall canopy tile,
        which requires canopy bits.
        """
        # Suppose CC2.THIN_WALL_CANOPY => we'll store e.g. 'NWC'
        c2m_elem = C2MElement(id=CC2.THIN_WALL_CANOPY, directions="NWC")
        row = [C2MCell(panel=c2m_elem, terrain=C2MElement(id=CC2.FLOOR))]
        cells_2d = [row]

        encoder = C2MMapEncoder(cells_2d)
        encoded = encoder.encode()
        # decode
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()

        self.assertEqual(decoded[0][0].panel.id, CC2.THIN_WALL_CANOPY)
        self.assertEqual(decoded[0][0].panel.directions, "NWC")

    def test_modified_tile_zero_value(self):
        """
        Test a tile in CC2.modified_tiles() but build_modifier => 00 bytes,
        meaning we skip the modifier tile and write only the tile's ID.
        """
        # Suppose CC2.LOGIC_GATE is in modified_tiles().
        # We'll mock build_modifier to return b'\x00'
        c2m_elem = C2MElement(id=CC2.LOGIC_GATE)
        row = [C2MCell(terrain=c2m_elem)]
        cells_2d = [row]

        with patch.object(C2MModifiers, 'build_modifier', return_value=b'\x00'):
            encoder = C2MMapEncoder(cells_2d)
            encoded = encoder.encode()

        # decode
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()

        # If the mod_val was zero, we wrote the tile's ID directly => LOGIC_GATE
        self.assertEqual(decoded[0][0].terrain.id, CC2.LOGIC_GATE)

    def test_modified_tile_8bit(self):
        """
        Test a tile in CC2.modified_tiles() whose modifier bytes fit in 1 byte => 8bit.
        """
        # Suppose CC2.RAILROAD_TRACK is in modified_tiles().
        c2m_elem = C2MElement(id=CC2.RAILROAD_TRACK)
        # We'll simulate build_modifier => b'\x13' => 8-bit
        with patch.object(C2MModifiers, 'build_modifier', return_value=b'\x13') as mock_mod:
            row = [C2MCell(terrain=c2m_elem)]
            cells_2d = [row]
            encoder = C2MMapEncoder(cells_2d)
            encoded = encoder.encode()

        # decode
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()

        # The decode sees => [ MODIFIER_8BIT(0x76?), 13, tile ID=RR track ]
        # So we expect terrain.id=RR track
        self.assertEqual(decoded[0][0].terrain.id, CC2.RAILROAD_TRACK)
        # No direct check of 'tracks' or 'active_track' here, but you could test further
        # if your parse_modifier logic sets them for the value 0x13.

    def test_modified_tile_16bit(self):
        """
        Test a tile in CC2.modified_tiles() whose modifier bytes are 2 bytes => 16bit.
        """
        c2m_elem = C2MElement(id=CC2.RAILROAD_TRACK)
        with patch.object(C2MModifiers, 'build_modifier', return_value=b'\xAB\xCD'):
            row = [C2MCell(terrain=c2m_elem)]
            cells_2d = [row]
            encoder = C2MMapEncoder(cells_2d)
            encoded = encoder.encode()

        # decode
        decoder = C2MMapDecoder(encoded)
        decoded = decoder.decode()
        self.assertEqual(decoded[0][0].terrain.id, CC2.RAILROAD_TRACK)

if __name__ == "__main__":
    unittest.main()
