"""Unit testing for artwork."""
import logging
import os
import unittest


class Test8x8ArtworkPresent(unittest.TestCase):
    """Unit testing for 8x8 artwork."""

    def test_8x8(self):
        """Test that all expected files exist."""
        expected = {
            # FLOOR = 0
            "floor_8.png",
            # WALL = 1
            "wall_8.png",
            # CHIP = 2
            "chip_8.png",
            # WATER = 3
            "water_8.png",
            # FIRE = 4
            "fire_8.png",
            # INV_WALL_PERM = 5
            "inv_wall_perm_8.png",
            # PANEL_N = 6
            # PANEL_W = 7
            # PANEL_S = 8
            # PANEL_E = 9
            "panel_horizontal_8.png",
            "panel_vertical_8.png",
            # BLOCK = 10
            "block_8.png",
            "block_transparent_8.png",
            # DIRT = 11
            "dirt_8.png",
            # ICE = 12
            "ice_8.png",
            # FORCE_S = 13
            "force_s_8.png",
            # CLONE_BLOCK_N = 14
            # CLONE_BLOCK_W = 15
            # CLONE_BLOCK_S = 16
            # CLONE_BLOCK_E = 17
            # FORCE_N = 18
            # FORCE_E = 19
            # FORCE_W = 20
            # EXIT = 21
            "exit_8.png",
            # BLUE_DOOR = 22
            # RED_DOOR = 23
            # GREEN_DOOR = 24
            # YELLOW_DOOR = 25
            "door_8.png",
            # ICE_SE = 26
            "ice_se_8.png",
            # ICE_SW = 27
            "ice_sw_8.png",
            # ICE_NW = 28
            "ice_nw_8.png",
            # ICE_NE = 29
            "ice_ne_8.png",
            # BLUE_WALL_FAKE = 30
            "blue_wall_fake_8.png",
            # BLUE_WALL_REAL = 31
            "blue_wall_real_8.png",
            # NOT_USED_0 = 32
            # THIEF = 33
            "thief_8.png",
            # SOCKET = 34
            "socket_8.png",
            # GREEN_BUTTON = 35
            # CLONE_BUTTON = 36
            "button_8.png",
            # TOGGLE_WALL = 37
            "toggle_wall_8.png",
            # TOGGLE_FLOOR = 38
            "toggle_floor_8.png",
            # TRAP_BUTTON = 39
            # TANK_BUTTON = 40
            # TELEPORT = 41
            "teleport_8.png",
            # BOMB = 42
            "bomb_8.png",
            # TRAP = 43
            "trap_8.png",
            # INV_WALL_APP = 44
            "inv_wall_app_8.png",
            # GRAVEL = 45
            "gravel_8.png",
            # POP_UP_WALL = 46
            "pop_up_wall_8.png",
            # HINT = 47
            "hint_8.png",
            # PANEL_SE = 48
            "panel_se_8.png",
            # CLONER = 49
            "cloner_8.png",
            # FORCE_RANDOM = 50
            "force_random_8.png",
            # DROWN_CHIP = 51
            # BURNED_CHIP0 = 52
            # BURNED_CHIP1 = 53
            # NOT_USED_1 = 54
            # NOT_USED_2 = 55
            # NOT_USED_3 = 56
            # CHIP_EXIT = 57
            # UNUSED_EXIT_0 = 58
            # UNUSED_EXIT_1 = 59
            # CHIP_SWIMMING_N = 60
            # CHIP_SWIMMING_W = 61
            # CHIP_SWIMMING_S = 62
            # CHIP_SWIMMING_E = 63
            # ANT_N = 64
            "ant_n_8.png",
            # ANT_W = 65
            "ant_w_8.png",
            # ANT_S = 66
            "ant_s_8.png",
            # ANT_E = 67
            "ant_e_8.png",
            # FIREBALL_N = 68
            "fireball_n_8.png",
            # FIREBALL_W = 69
            "fireball_w_8.png",
            # FIREBALL_S = 70
            "fireball_s_8.png",
            # FIREBALL_E = 71
            "fireball_e_8.png",
            # BALL_N = 72
            "ball_n_8.png",
            # BALL_W = 73
            "ball_w_8.png",
            # BALL_S = 74
            "ball_s_8.png",
            # BALL_E = 75
            "ball_e_8.png",
            # TANK_N = 76
            "tank_n_8.png",
            # TANK_W = 77
            "tank_w_8.png",
            # TANK_S = 78
            "tank_s_8.png",
            # TANK_E = 79
            "tank_e_8.png",
            # GLIDER_N = 80
            "glider_n_8.png",
            # GLIDER_W = 81
            "glider_w_8.png",
            # GLIDER_S = 82
            "glider_s_8.png",
            # GLIDER_E = 83
            "glider_e_8.png",
            # TEETH_N = 84
            "teeth_n_8.png",
            # TEETH_W = 85
            "teeth_w_8.png",
            # TEETH_S = 86
            "teeth_s_8.png",
            # TEETH_E = 87
            "teeth_e_8.png",
            # WALKER_N = 88
            "walker_n_8.png",
            # WALKER_W = 89
            "walker_w_8.png",
            # WALKER_S = 90
            "walker_s_8.png",
            # WALKER_E = 91
            "walker_e_8.png",
            # BLOB_N = 92
            "blob_n_8.png",
            # BLOB_W = 93
            "blob_w_8.png",
            # BLOB_S = 94
            "blob_s_8.png",
            # BLOB_E = 95
            "blob_e_8.png",
            # PARAMECIUM_N = 96
            "paramecium_n_8.png",
            # PARAMECIUM_W = 97
            "paramecium_w_8.png",
            # PARAMECIUM_S = 98
            "paramecium_s_8.png",
            # PARAMECIUM_E = 99
            "paramecium_e_8.png",
            # BLUE_KEY = 100
            # RED_KEY = 101
            # GREEN_KEY = 102
            # YELLOW_KEY = 103
            "key_8.png",
            # FLIPPERS = 104
            "flippers_8.png",
            # FIRE_BOOTS = 105
            "fire_boots_8.png",
            # SKATES = 106
            "skates_8.png",
            # SUCTION_BOOTS = 107
            "suction_boots_8.png",
            # PLAYER_N = 108
            "player_n_8.png",
            # PLAYER_W = 109
            "player_w_8.png",
            # PLAYER_S = 110
            "player_s_8.png",
            # PLAYER_E = 111
            "player_e_8.png",
        }
        actual = set(os.listdir(os.path.join(os.getcwd(), "art/8x8/")))
        for missing in expected.difference(actual):
            logging.error(f"missing {missing}")
        self.assertEqual(expected, actual)
