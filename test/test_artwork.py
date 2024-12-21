"""Unit testing for artwork."""
import logging
import unittest
import importlib.resources


class Test8x8ArtworkPresent(unittest.TestCase):
    """Unit testing for 8x8 artwork."""
    img_prefixes = {
        "FLOOR",
        "WALL",
        "CHIP",
        "WATER",
        "FIRE",
        "INV_WALL_PERM",
        "PANEL_HORIZONTAL",
        "PANEL_VERTICAL",
        "BLOCK",
        "BLOCK_TRANSPARENT",
        "DIRT",
        "ICE",
        "FORCE_S",
        "EXIT",
        "DOOR",
        "ICE_SE",
        "ICE_SW",
        "ICE_NW",
        "ICE_NE",
        "BLUE_WALL_FAKE",
        "BLUE_WALL_REAL",
        "THIEF",
        "SOCKET",
        "BUTTON",
        "TOGGLE_WALL",
        "TOGGLE_FLOOR",
        "TELEPORT",
        "BOMB",
        "TRAP",
        "INV_WALL_APP",
        "GRAVEL",
        "POP_UP_WALL",
        "HINT",
        "PANEL_SE",
        "CLONER",
        "FORCE_RANDOM",
        "ANT_N",
        "ANT_W",
        "ANT_S",
        "ANT_E",
        "FIREBALL_N",
        "FIREBALL_W",
        "FIREBALL_S",
        "FIREBALL_E",
        "BALL_N",
        "BALL_W",
        "BALL_S",
        "BALL_E",
        "TANK_N",
        "TANK_W",
        "TANK_S",
        "TANK_E",
        "GLIDER_N",
        "GLIDER_W",
        "GLIDER_S",
        "GLIDER_E",
        "TEETH_N",
        "TEETH_W",
        "TEETH_S",
        "TEETH_E",
        "WALKER_N",
        "WALKER_W",
        "WALKER_S",
        "WALKER_E",
        "BLOB_N",
        "BLOB_W",
        "BLOB_S",
        "BLOB_E",
        "PARAMECIUM_N",
        "PARAMECIUM_W",
        "PARAMECIUM_S",
        "PARAMECIUM_E",
        "KEY",
        "FLIPPERS",
        "FIRE_BOOTS",
        "SKATES",
        "SUCTION_BOOTS",
        "PLAYER_N",
        "PLAYER_W",
        "PLAYER_S",
        "PLAYER_E",
        "ARROW_E"
    }

    def test_8x8(self):
        """Test that all expected files exist, excluding __init__.py."""
        art_path = importlib.resources.files('cc_tools.art.8x8')
        
        # Exclude '__init__.py' from the actual set
        actual = {f.name[:-4] for f in art_path.iterdir() if f.is_file() and f.name != '__init__.py'}
        
        expected = self.img_prefixes
        
        for missing in expected.difference(actual):
            logging.error("missing %s", missing)
        
        self.assertEqual(expected, actual)
