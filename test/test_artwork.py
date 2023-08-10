"""Unit testing for artwork."""
import logging
import unittest
import importlib.resources
from src.cc1 import CC1LevelImager


class Test8x8ArtworkPresent(unittest.TestCase):
    """Unit testing for 8x8 artwork."""
    img_prefixes = {
        "floor_8",
        "wall_8",
        "chip_8",
        "water_8",
        "fire_8",
        "inv_wall_perm_8",
        "panel_horizontal_8",
        "panel_vertical_8",
        "block_8",
        "block_transparent_8",
        "dirt_8",
        "ice_8",
        "force_s_8",
        "exit_8",
        "door_8",
        "ice_se_8",
        "ice_sw_8",
        "ice_nw_8",
        "ice_ne_8",
        "blue_wall_fake_8",
        "blue_wall_real_8",
        "thief_8",
        "socket_8",
        "button_8",
        "toggle_wall_8",
        "toggle_floor_8",
        "teleport_8",
        "bomb_8",
        "trap_8",
        "inv_wall_app_8",
        "gravel_8",
        "pop_up_wall_8",
        "hint_8",
        "panel_se_8",
        "cloner_8",
        "force_random_8",
        "ant_n_8",
        "ant_w_8",
        "ant_s_8",
        "ant_e_8",
        "fireball_n_8",
        "fireball_w_8",
        "fireball_s_8",
        "fireball_e_8",
        "ball_n_8",
        "ball_w_8",
        "ball_s_8",
        "ball_e_8",
        "tank_n_8",
        "tank_w_8",
        "tank_s_8",
        "tank_e_8",
        "glider_n_8",
        "glider_w_8",
        "glider_s_8",
        "glider_e_8",
        "teeth_n_8",
        "teeth_w_8",
        "teeth_s_8",
        "teeth_e_8",
        "walker_n_8",
        "walker_w_8",
        "walker_s_8",
        "walker_e_8",
        "blob_n_8",
        "blob_w_8",
        "blob_s_8",
        "blob_e_8",
        "paramecium_n_8",
        "paramecium_w_8",
        "paramecium_s_8",
        "paramecium_e_8",
        "key_8",
        "flippers_8",
        "fire_boots_8",
        "skates_8",
        "suction_boots_8",
        "player_n_8",
        "player_w_8",
        "player_s_8",
        "player_e_8",
    }

    def test_8x8(self):
        """Test that all expected files exist."""
        art_path = importlib.resources.files('cc_tools.art.8x8')
        actual = {f.name[:-4] for f in art_path.iterdir() if f.is_file()}
        expected = self.img_prefixes
        for missing in expected.difference(actual):
            logging.error("missing %s", missing)
        self.assertEqual(expected, actual)

    def test_imager_initialize(self):
        """Test that the imager initializes."""
        CC1LevelImager()
        