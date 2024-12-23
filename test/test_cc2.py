import unittest
from cc_tools.cc2 import CC2  # Adjust import to match your project structure, e.g. `from your_module_file import CC2`

class TestCC2Dirs(unittest.TestCase):
    """
    Tests related to the dirs(), with_dirs(), and directional manipulation methods.
    """

    def test_dirs_no_direction(self):
        """A tile with no direction suffix should return an empty string."""
        self.assertEqual(CC2.FLOOR.dirs(), "")

    def test_dirs_single_direction(self):
        """A tile with a single direction suffix, e.g. ICE_NW, should return 'NW'."""
        self.assertEqual(CC2.ICE_NW.dirs(), "NW")
        self.assertEqual(CC2.FORCE_W.dirs(), "W")
        self.assertEqual(CC2.ICE_SE.dirs(), "SE")

    def test_with_dirs_valid(self):
        """with_dirs should replace the existing direction suffix correctly."""
        tile = CC2.ICE_NW
        # Replace NW with NE
        replaced = tile.with_dirs("NE")
        self.assertEqual(replaced, CC2.ICE_NE)
        # Replace NW with NW (no-op)
        replaced = tile.with_dirs("NW")
        self.assertEqual(replaced, tile)

    def test_with_dirs_empty(self):
        """If tile has no direction suffix, providing empty dirs should return the tile itself."""
        tile = CC2.FLOOR
        replaced = tile.with_dirs("")
        self.assertEqual(replaced, CC2.FLOOR)

    def test_with_dirs_invalid_direction(self):
        """Invalid direction suffixes should raise a ValueError."""
        with self.assertRaises(ValueError):
            CC2.ICE_NW.with_dirs("XYZ")
        with self.assertRaises(ValueError):
            CC2.ICE_NW.with_dirs("NWS")  # length mismatch

    def test_right_no_direction(self):
        """Tiles without direction suffix should remain unchanged when rotated right."""
        self.assertEqual(CC2.FLOOR.right(), CC2.FLOOR)

    def test_right_single_direction(self):
        """Single-direction suffixes should rotate as N -> E -> S -> W -> N."""
        self.assertEqual(CC2.FORCE_N.right(), CC2.FORCE_E)
        self.assertEqual(CC2.FORCE_E.right(), CC2.FORCE_S)
        self.assertEqual(CC2.FORCE_S.right(), CC2.FORCE_W)
        self.assertEqual(CC2.FORCE_W.right(), CC2.FORCE_N)

    def test_right_double_direction(self):
        """Multi-direction suffixes (e.g. NW) should rotate as NW -> NE -> SE -> SW -> NW."""
        tile = CC2.ICE_NW
        r1 = tile.right()
        r2 = r1.right()
        r3 = r2.right()
        r4 = r3.right()
        self.assertEqual(r1, CC2.ICE_NE)   # NW -> NE
        self.assertEqual(r2, CC2.ICE_SE)   # NE -> SE
        self.assertEqual(r3, CC2.ICE_SW)   # SE -> SW
        self.assertEqual(r4, CC2.ICE_NW)   # SW -> NW (full cycle)

    def test_reverse(self):
        """Reversing is effectively a 180-degree turn (two 'right' rotations)."""
        self.assertEqual(CC2.FORCE_N.reverse(), CC2.FORCE_S)
        self.assertEqual(CC2.FORCE_E.reverse(), CC2.FORCE_W)
        self.assertEqual(CC2.ICE_NE.reverse(), CC2.ICE_SW)
        self.assertEqual(CC2.ICE_NW.reverse(), CC2.ICE_SE)

    def test_left(self):
        """Rotating left is the same as rotating right 3 times."""
        self.assertEqual(CC2.FORCE_N.left(), CC2.FORCE_W)
        self.assertEqual(CC2.FORCE_W.left(), CC2.FORCE_S)
        self.assertEqual(CC2.FORCE_S.left(), CC2.FORCE_E)
        self.assertEqual(CC2.FORCE_E.left(), CC2.FORCE_N)


class TestCC2Toggle(unittest.TestCase):
    """
    Tests related to toggle() method, ensuring it correctly toggles known pairs
    (GREEN_CHIP <-> GREEN_BOMB, FLAME_JET_ON <-> FLAME_JET_OFF, etc.).
    """

    def test_toggle_green_chip(self):
        """GREEN_CHIP should toggle to GREEN_BOMB and back."""
        self.assertEqual(CC2.GREEN_CHIP.toggle(), CC2.GREEN_BOMB)
        self.assertEqual(CC2.GREEN_BOMB.toggle(), CC2.GREEN_CHIP)

    def test_toggle_flame_jet(self):
        """FLAME_JET_ON should toggle to FLAME_JET_OFF and back."""
        self.assertEqual(CC2.FLAME_JET_ON.toggle(), CC2.FLAME_JET_OFF)
        self.assertEqual(CC2.FLAME_JET_OFF.toggle(), CC2.FLAME_JET_ON)

    def test_toggle_switch(self):
        """SWITCH_ON should toggle to SWITCH_OFF and back."""
        self.assertEqual(CC2.SWITCH_ON.toggle(), CC2.SWITCH_OFF)
        self.assertEqual(CC2.SWITCH_OFF.toggle(), CC2.SWITCH_ON)

    def test_toggle_green_toggle_floor_wall(self):
        """GREEN_TOGGLE_FLOOR <-> GREEN_TOGGLE_WALL."""
        self.assertEqual(CC2.GREEN_TOGGLE_FLOOR.toggle(), CC2.GREEN_TOGGLE_WALL)
        self.assertEqual(CC2.GREEN_TOGGLE_WALL.toggle(), CC2.GREEN_TOGGLE_FLOOR)

    def test_toggle_purple_toggle_floor_wall(self):
        """PURPLE_TOGGLE_FLOOR <-> PURPLE_TOGGLE_WALL."""
        self.assertEqual(CC2.PURPLE_TOGGLE_FLOOR.toggle(), CC2.PURPLE_TOGGLE_WALL)
        self.assertEqual(CC2.PURPLE_TOGGLE_WALL.toggle(), CC2.PURPLE_TOGGLE_FLOOR)

    def test_toggle_non_toggle_tile(self):
        """A tile that isn't in a toggle pair should remain itself."""
        self.assertEqual(CC2.WALL.toggle(), CC2.WALL)
        self.assertEqual(CC2.FLOOR.toggle(), CC2.FLOOR)


class TestCC2Sets(unittest.TestCase):
    """
    Tests for class methods returning sets of CC2 members (e.g., CC2.walls(), CC2.blocks(), etc.).
    """

    def test_ice_set(self):
        """ice() should return {ICE, ICE_NE, ICE_NW, ICE_SE, ICE_SW}."""
        ice_set = CC2.ice()
        self.assertIn(CC2.ICE, ice_set)
        self.assertIn(CC2.ICE_NW, ice_set)
        self.assertIn(CC2.ICE_NE, ice_set)
        self.assertIn(CC2.ICE_SW, ice_set)
        self.assertIn(CC2.ICE_SE, ice_set)
        self.assertEqual(len(ice_set), 5)

    def test_forces_set(self):
        """forces() should return {FORCE_RANDOM, FORCE_E, FORCE_N, FORCE_S, FORCE_W}."""
        force_set = CC2.forces()
        self.assertIn(CC2.FORCE_RANDOM, force_set)
        self.assertIn(CC2.FORCE_E, force_set)
        self.assertIn(CC2.FORCE_N, force_set)
        self.assertIn(CC2.FORCE_S, force_set)
        self.assertIn(CC2.FORCE_W, force_set)
        self.assertEqual(len(force_set), 5)

    def test_walls_set(self):
        """
        walls() should include WALL, STEEL_WALL, SOLID_GREEN_WALL, SOLID_BLUE_WALL,
        plus invisible walls.
        """
        walls_set = CC2.walls()
        self.assertIn(CC2.WALL, walls_set)
        self.assertIn(CC2.STEEL_WALL, walls_set)
        self.assertIn(CC2.SOLID_GREEN_WALL, walls_set)
        self.assertIn(CC2.SOLID_BLUE_WALL, walls_set)
        # Also check invisible walls
        self.assertIn(CC2.INVISIBLE_WALL, walls_set)
        self.assertIn(CC2.APPEARING_WALL, walls_set)

    def test_panels_set(self):
        """panels() should include THIN_WALL_S, THIN_WALL_E, THIN_WALL_SE, THIN_WALL_CANOPY."""
        panels_set = CC2.panels()
        self.assertIn(CC2.THIN_WALL_S, panels_set)
        self.assertIn(CC2.THIN_WALL_E, panels_set)
        self.assertIn(CC2.THIN_WALL_SE, panels_set)
        self.assertIn(CC2.THIN_WALL_CANOPY, panels_set)

    def test_blocks_set(self):
        """blocks() should include DIRT_BLOCK, ICE_BLOCK, DIRECTIONAL_BLOCK."""
        blocks_set = CC2.blocks()
        self.assertIn(CC2.DIRT_BLOCK, blocks_set)
        self.assertIn(CC2.ICE_BLOCK, blocks_set)
        self.assertIn(CC2.DIRECTIONAL_BLOCK, blocks_set)
        self.assertEqual(len(blocks_set), 3)

    def test_monsters_set(self):
        """monsters() should contain known enemy types, excluding players/blocks."""
        monsters_set = CC2.monsters()
        # A few examples
        self.assertIn(CC2.GLIDER, monsters_set)
        self.assertIn(CC2.BALL, monsters_set)
        self.assertIn(CC2.BLUE_TEETH, monsters_set)
        # Ensure a non-monster is not in there
        self.assertNotIn(CC2.CHIP, monsters_set)
        self.assertNotIn(CC2.FLOOR, monsters_set)

    def test_mobs_set(self):
        """
        mobs() = monsters() U blocks() U players().
        Check that it includes at least one monster, one block, and one player.
        """
        mobs_set = CC2.mobs()
        self.assertIn(CC2.CHIP, mobs_set)  # player
        self.assertIn(CC2.DIRT_BLOCK, mobs_set)  # block
        self.assertIn(CC2.BALL, mobs_set)  # monster

    def test_all_chips_set(self):
        """
        all_chips() = toggle_chips() U ic_chips().
        Must contain GREEN_CHIP, GREEN_BOMB, IC_CHIP, EXTRA_IC_CHIP.
        """
        all_chips = CC2.all_chips()
        self.assertIn(CC2.GREEN_CHIP, all_chips)
        self.assertIn(CC2.GREEN_BOMB, all_chips)
        self.assertIn(CC2.IC_CHIP, all_chips)
        self.assertIn(CC2.EXTRA_IC_CHIP, all_chips)
        self.assertEqual(len(all_chips), 4)

    def test_swivels_set(self):
        """swivels() should contain four directions of swivel doors."""
        swivels_set = CC2.swivels()
        self.assertIn(CC2.SWIVEL_DOOR_NE, swivels_set)
        self.assertIn(CC2.SWIVEL_DOOR_NW, swivels_set)
        self.assertIn(CC2.SWIVEL_DOOR_SE, swivels_set)
        self.assertIn(CC2.SWIVEL_DOOR_SW, swivels_set)

    def test_pickups_set(self):
        """
        pickups() should contain keys, tools, flags, bombs, and time pickups.
        For instance, check a few examples from each category.
        """
        pickups_set = CC2.pickups()
        # Keys
        self.assertIn(CC2.RED_KEY, pickups_set)
        self.assertIn(CC2.BLUE_KEY, pickups_set)
        # Tools
        self.assertIn(CC2.FLIPPERS, pickups_set)
        self.assertIn(CC2.FIRE_BOOTS, pickups_set)
        # Flags
        self.assertIn(CC2.FLAG_10, pickups_set)
        # Time pickups
        self.assertIn(CC2.TIME_BONUS, pickups_set)
        self.assertIn(CC2.STOPWATCH, pickups_set)
        # Bombs
        self.assertIn(CC2.BOMB, pickups_set)
        self.assertIn(CC2.GREEN_BOMB, pickups_set)

    def test_unused_set(self):
        """unused() should include all enum members whose name contains 'UNUSED'."""
        unused_set = CC2.unused()
        self.assertIn(CC2.UNUSED_53, unused_set)
        self.assertIn(CC2.UNUSED_54, unused_set)
        self.assertIn(CC2.UNUSED_55, unused_set)
        self.assertIn(CC2.UNUSED_5D, unused_set)
        self.assertIn(CC2.UNUSED_67, unused_set)
        self.assertIn(CC2.UNUSED_6C, unused_set)
        self.assertIn(CC2.UNUSED_6E, unused_set)
        self.assertIn(CC2.UNUSED_74, unused_set)
        self.assertIn(CC2.UNUSED_75, unused_set)
        self.assertIn(CC2.UNUSED_79, unused_set)
        self.assertIn(CC2.UNUSED_85, unused_set)
        self.assertIn(CC2.UNUSED_86, unused_set)
        self.assertIn(CC2.UNUSED_91, unused_set)
        self.assertEqual(len(unused_set), 13)

    def test_invalid_mobs_set(self):
        """invalid_mobs() should include EXPLOSION_ANIMATION and UNUSED_79."""
        invalid_mobs = CC2.invalid_mobs()
        self.assertIn(CC2.EXPLOSION_ANIMATION, invalid_mobs)
        self.assertIn(CC2.UNUSED_79, invalid_mobs)

    def test_all_mobs_set(self):
        """all_mobs() = mobs() U invalid_mobs(). Must contain a known monster, block, player, and an invalid mob."""
        all_mobs = CC2.all_mobs()
        self.assertIn(CC2.CHIP, all_mobs)  # from players
        self.assertIn(CC2.DIRT_BLOCK, all_mobs)  # from blocks
        self.assertIn(CC2.BALL, all_mobs)  # from monsters
        self.assertIn(CC2.EXPLOSION_ANIMATION, all_mobs)  # from invalid_mobs


if __name__ == '__main__':
    unittest.main()
