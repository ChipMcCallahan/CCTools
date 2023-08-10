"""Tests for CC1."""
import importlib.resources
import unittest
from src.cc1 import CC1
from src.cc1_cell import CC1Cell
from src.cc1_level import CC1Level
from src.cc1_level_transformer import CC1LevelTransformer
from src.dat_handler import DATHandler


class TestCC1(unittest.TestCase):
    """Tests for CC1."""

    def test_sets(self):
        """Tests for CC1 tile code sets."""
        self.assertEqual(len(CC1.all()), 112)
        self.assertEqual(len(CC1.invalid()), 14)
        self.assertEqual(len(CC1.valid()), 112 - 14)
        self.assertEqual(len(CC1.ice()), 5)
        self.assertEqual(len(CC1.forces()), 5)
        self.assertEqual(len(CC1.walls()), 4)
        self.assertEqual(len(CC1.panels()), 5)
        self.assertEqual(len(CC1.clone_blocks()), 4)
        self.assertEqual(len(CC1.blocks()), 5)
        self.assertEqual(len(CC1.players()), 4)
        self.assertEqual(len(CC1.ants()), 4)
        self.assertEqual(len(CC1.paramecia()), 4)
        self.assertEqual(len(CC1.gliders()), 4)
        self.assertEqual(len(CC1.fireballs()), 4)
        self.assertEqual(len(CC1.tanks()), 4)
        self.assertEqual(len(CC1.balls()), 4)
        self.assertEqual(len(CC1.walkers()), 4)
        self.assertEqual(len(CC1.teeth()), 4)
        self.assertEqual(len(CC1.blobs()), 4)
        self.assertEqual(len(CC1.monsters()), 9 * 4)
        self.assertEqual(len(CC1.mobs()), 10 * 4 + 5)
        self.assertEqual(len(CC1.nonmobs()), 112 - (10 * 4 + 5))
        self.assertEqual(len(CC1.doors()), 4)
        self.assertEqual(len(CC1.keys()), 4)
        self.assertEqual(len(CC1.boots()), 4)
        self.assertEqual(len(CC1.pickups()), 9)
        self.assertEqual(len(CC1.buttons()), 4)
        self.assertEqual(len(CC1.toggles()), 2)

    def test_rotations(self):
        """Unit tests for rotating CC1 tiles."""
        # pylint:disable=invalid-name
        for prefix in (
                "PLAYER", "BLOB", "WALKER", "TEETH", "GLIDER", "TANK", "BALL", "FIREBALL", "ANT",
                "FORCE", "CLONE_BLOCK", "PANEL"):
            n, e, s, w = (CC1[prefix + "_" + d] for d in "NESW")
            self.assertEqual(n.right(), e)
            self.assertEqual(e.right(), s)
            self.assertEqual(s.right(), w)
            self.assertEqual(w.right(), n)
            self.assertEqual(n.left(), w)
            self.assertEqual(e.left(), n)
            self.assertEqual(s.left(), e)
            self.assertEqual(w.left(), s)
            self.assertEqual(n.reverse(), s)
            self.assertEqual(e.reverse(), w)
            self.assertEqual(s.reverse(), n)
            self.assertEqual(w.reverse(), e)

        nw, ne, sw, se = (CC1["ICE_" + d] for d in ("NW", "NE", "SW", "SE"))
        self.assertEqual(nw.right(), ne)
        self.assertEqual(ne.right(), se)
        self.assertEqual(sw.right(), nw)
        self.assertEqual(se.right(), sw)
        self.assertEqual(nw.left(), sw)
        self.assertEqual(ne.left(), nw)
        self.assertEqual(sw.left(), se)
        self.assertEqual(se.left(), ne)
        self.assertEqual(nw.reverse(), se)
        self.assertEqual(ne.reverse(), sw)
        self.assertEqual(sw.reverse(), ne)
        self.assertEqual(se.reverse(), nw)

        for t in CC1.valid().difference(CC1.mobs(), CC1.forces(), CC1.ice(), CC1.panels()).union(
                {CC1.FORCE_RANDOM, CC1.ICE, CC1.PANEL_SE, CC1.BLOCK}):
            self.assertEqual(t, t.right())
            self.assertEqual(t, t.left())
            self.assertEqual(t, t.reverse())


class TestCC1Cell(unittest.TestCase):
    """Tests for CC1Cell."""

    def test_is_valid(self):
        """Unit tests for CC1 cell validity."""
        for element in CC1.nonmobs().difference({CC1.FLOOR}):
            buried = CC1Cell(CC1.FLOOR, element)
            self.assertFalse(buried.is_valid())

        for element in CC1.invalid():
            invalid = CC1Cell(element)
            self.assertFalse(invalid.is_valid())

        for element in CC1.mobs():
            buried_mob = CC1Cell(CC1.FLOOR, element)
            self.assertFalse(buried_mob.is_valid())

        for mob in CC1.mobs():
            for terrain in CC1.nonmobs().difference(CC1.invalid()):
                self.assertTrue(CC1Cell(mob, terrain).is_valid())

    def test_contains(self):
        """Unit tests for checking if a cell contains an element."""
        cell = CC1Cell(CC1.PLAYER_S, CC1.EXIT)
        self.assertTrue(cell.contains(CC1.PLAYER_S))
        self.assertTrue(cell.contains(CC1.EXIT))
        self.assertFalse(cell.contains(CC1.PLAYER_W))

    def test_add(self):
        """Unit tests for adding elements to cells."""
        cell = CC1Cell(CC1.WALL)
        cell.add(CC1.FIRE)
        self.assertEqual(cell, CC1Cell(CC1.FIRE))

        cell = CC1Cell(CC1.TEETH_S, CC1.GRAVEL)
        cell.add(CC1.FIRE)
        self.assertEqual(cell, CC1Cell(CC1.TEETH_S, CC1.FIRE))

        cell = CC1Cell(CC1.TEETH_S, CC1.GRAVEL)
        cell.add(CC1.PLAYER_S)
        self.assertEqual(cell, CC1Cell(CC1.PLAYER_S, CC1.GRAVEL))

        cell = CC1Cell(CC1.WALL)
        cell.add(CC1.BLOCK)
        self.assertEqual(cell, CC1Cell(CC1.BLOCK, CC1.WALL))

    def test_remove(self):
        """Unit tests for removing elements from cells."""
        cell = CC1Cell(CC1.WALL)
        self.assertFalse(cell.remove(CC1.BLOCK))
        self.assertEqual(cell, CC1Cell(CC1.WALL))

        cell = CC1Cell(CC1.WALL)
        self.assertTrue(cell.remove(CC1.WALL))
        self.assertEqual(cell, CC1Cell())

        cell = CC1Cell(CC1.TEETH_S, CC1.WALL)
        self.assertTrue(cell.remove(CC1.WALL))
        self.assertEqual(cell, CC1Cell(CC1.TEETH_S))

        cell = CC1Cell(CC1.TEETH_S, CC1.WALL)
        self.assertTrue(cell.remove(CC1.TEETH_S))
        self.assertEqual(cell, CC1Cell(CC1.WALL))

    def test_erase(self):
        """Unit test for erasing cells."""
        cell = CC1Cell(CC1.TEETH_S, CC1.WALL)
        cell.erase()
        self.assertEqual(cell, CC1Cell())


class TestCC1Level(unittest.TestCase):
    """Tests for CC1Level."""

    def test_is_valid(self):
        """Unit tests for CC1 Level validity."""
        level = CC1Level()
        self.assertTrue(level.is_valid())
        level.map[0] = CC1Cell(CC1.NOT_USED_0)
        self.assertFalse(level.is_valid())

    def test_add(self):
        """Unit tests for adding elements to levels."""
        level = CC1Level()
        level.add(22, CC1.WALL)
        self.assertEqual(level.map[22], CC1Cell(CC1.WALL))

        level.add(22, CC1.GRAVEL)
        self.assertEqual(level.map[22], CC1Cell(CC1.GRAVEL))

        level.add(22, CC1.BLOB_S)
        self.assertEqual(level.map[22], CC1Cell(CC1.BLOB_S, CC1.GRAVEL))
        self.assertEqual(level.movement, [22])

        level.add(22, CC1.WALL)
        self.assertEqual(level.map[22], CC1Cell(CC1.BLOB_S, CC1.WALL))

        level.add(22, CC1.BALL_S)
        self.assertEqual(level.map[22], CC1Cell(CC1.BALL_S, CC1.WALL))
        self.assertEqual(level.movement, [22])

        level.add(22, CC1.BLOCK)
        self.assertEqual(level.map[22], CC1Cell(CC1.BLOCK, CC1.WALL))
        self.assertEqual(level.movement, [])

        level.add(22, CC1.BALL_S)
        self.assertEqual(level.map[22], CC1Cell(CC1.BALL_S, CC1.WALL))
        self.assertEqual(level.movement, [22])

        level.add(22, CC1.PLAYER_S)
        self.assertEqual(level.map[22], CC1Cell(CC1.PLAYER_S, CC1.WALL))
        self.assertEqual(level.movement, [])

        level.add(33, CC1.TRAP_BUTTON)
        level.add(34, CC1.TRAP_BUTTON)
        level.add(35, CC1.TRAP_BUTTON)
        level.add(44, CC1.TRAP)
        level.traps[33] = 44
        level.traps[34] = 44
        level.traps[35] = 44
        level.add(34, CC1.GRAVEL)
        self.assertEqual(level.traps, {33: 44, 35: 44})
        level.add(44, CC1.GRAVEL)
        self.assertEqual(len(level.traps), 0)

        level.add(33, CC1.CLONE_BUTTON)
        level.add(34, CC1.CLONE_BUTTON)
        level.add(35, CC1.CLONE_BUTTON)
        level.add(44, CC1.CLONER)
        level.cloners[33] = 44
        level.cloners[34] = 44
        level.cloners[35] = 44
        level.add(34, CC1.GRAVEL)
        self.assertEqual(level.cloners, {33: 44, 35: 44})
        level.add(44, CC1.GRAVEL)
        self.assertEqual(len(level.cloners), 0)

    def test_remove(self):
        """Unit tests for removing elements from levels."""
        level = CC1Level()
        level.add(22, CC1.BLOB_S)
        self.assertEqual(level.movement, [22])
        level.remove(22, CC1.BLOB_S)
        self.assertEqual(level.map[22], CC1Cell())
        self.assertEqual(level.movement, [])

        level.add(22, CC1.BLOB_S)
        level.add(22, CC1.GRAVEL)
        level.remove(22, CC1.BLOB_S)
        self.assertEqual(level.map[22], CC1Cell(CC1.GRAVEL))

        level.add(33, CC1.TRAP_BUTTON)
        level.add(34, CC1.TRAP_BUTTON)
        level.add(35, CC1.TRAP_BUTTON)
        level.add(44, CC1.TRAP)
        level.traps[33] = 44
        level.traps[34] = 44
        level.traps[35] = 44
        level.remove(34, CC1.TRAP_BUTTON)
        self.assertEqual(level.traps, {33: 44, 35: 44})
        level.remove(44, CC1.TRAP)
        self.assertEqual(len(level.traps), 0)

        level.add(33, CC1.CLONE_BUTTON)
        level.add(34, CC1.CLONE_BUTTON)
        level.add(35, CC1.CLONE_BUTTON)
        level.add(44, CC1.CLONER)
        level.cloners[33] = 44
        level.cloners[34] = 44
        level.cloners[35] = 44
        level.remove(34, CC1.CLONE_BUTTON)
        self.assertEqual(level.cloners, {33: 44, 35: 44})
        level.remove(44, CC1.CLONER)
        self.assertEqual(len(level.cloners), 0)

    def test_count(self):
        """Unit test for counting elements in a level."""
        level = CC1Level()
        n = 10
        for i in range(n):
            level.add(i, CC1.CHIP)
            level.add(i, CC1.TANK_N)
            level.add(i + n, CC1.TANK_E)
            level.add(i + 2 * n, CC1.TANK_S)
            level.add(i + 3 * n, CC1.TANK_W)

        self.assertEqual(level.count(CC1.CHIP), 10)
        self.assertEqual(level.count(CC1.tanks()), 40)
        self.assertEqual(level.count(CC1.blobs()), 0)


class TestCC1LevelTransformer(unittest.TestCase):
    """Tests for CC1LevelTransformer."""

    def test_rotate(self):
        """Unit test for rotating a CC1Level."""
        r90 = CC1LevelTransformer.rotate_90
        r180 = CC1LevelTransformer.rotate_180
        r270 = CC1LevelTransformer.rotate_270

        dat_file_path = importlib.resources.files('cc_tools.sets.dat') / 'CCLP1.dat'
        with open(dat_file_path, 'rb') as f:
            cclp1 = DATHandler.parse(f.read())

        for level in cclp1.levels[100:]:  # Save time on unit tests
            if level.count(CC1.PANEL_SE) > 0:
                self.assertEqual(level, r90(level))
                self.assertEqual(level, r180(level))
                self.assertEqual(level, r270(level))
            else:
                n, e, s, w = level, r90(level), r180(level), r270(level)
                self.assertNotEqual(n, e)
                self.assertNotEqual(n, s)
                self.assertNotEqual(n, w)

                self.assertEqual(r90(e), s)
                self.assertEqual(r270(w), s)
                self.assertEqual(r90(w), n)
                self.assertEqual(r270(e), n)

    def test_flip(self):
        """Unit test for mirroring (flipping) a CC1Level horizontally."""
        dat_file_path = importlib.resources.files('cc_tools.sets.dat') / 'CCLP1.dat'
        with open(dat_file_path, 'rb') as f:
            cclp1 = DATHandler.parse(f.read())

        h, v = CC1LevelTransformer.flip_horizontal, CC1LevelTransformer.flip_vertical
        ne, nw = CC1LevelTransformer.flip_ne_sw, CC1LevelTransformer.flip_nw_se
        for level in cclp1.levels[100:]:  # Save time on unit tests
            if level.count(CC1.PANEL_SE) > 0:
                self.assertEqual(level, h(level))
                self.assertEqual(level, v(level))
                self.assertEqual(level, ne(level))
                self.assertEqual(level, nw(level))
            else:
                for flip in (h, v, ne, nw):
                    flipped = flip(level)
                    self.assertNotEqual(level, flipped)
                    self.assertEqual(level, flip(flipped))

    def test_replace(self):
        """Unit test for transforming a CC1Level by element replacement."""
        level = CC1Level()
        n = 20
        for i in range(n):
            level.add(i, CC1.FIRE)
            level.add(i, CC1.FIREBALL_N)
            level.add(i + n, CC1.WATER)

        # Should do nothing, but new level should be deep copy.
        level2 = CC1LevelTransformer.replace(level, CC1.GRAVEL, CC1.DIRT)
        self.assertEqual(level, level2)
        self.assertIsNot(level, level2)

        # Replace all floor with gravel.
        level3 = CC1LevelTransformer.replace(level2, CC1.FLOOR, CC1.GRAVEL)
        self.assertEqual(level3.count(CC1.GRAVEL), 1024 - n * 2)
        self.assertEqual(level3.count(CC1.GRAVEL), 1024 - n * 2)

        # Replace all fire with water.
        level4 = CC1LevelTransformer.replace(level3, CC1.FIRE, CC1.WATER)
        self.assertEqual(level4.count(CC1.FIRE), 0)
        self.assertEqual(level4.count(CC1.WATER), n * 2)
        self.assertEqual(level4.count(CC1.FIREBALL_N), n)

        # Replace all fireball with blob.
        level5 = CC1LevelTransformer.replace(level4, CC1.FIREBALL_N, CC1.BLOB_N)
        self.assertEqual(level5.count(CC1.WATER), n * 2)
        self.assertEqual(level5.count(CC1.FIREBALL_N), 0)
        self.assertEqual(level5.count(CC1.BLOB_N), n)

        level6 = CC1LevelTransformer.replace(level5, {CC1.WATER, CC1.GRAVEL, CC1.BLOB_N}, CC1.FLOOR)
        self.assertEqual(level6.count(CC1.FLOOR), 1024)
        self.assertEqual(level6.count(CC1.WATER), 0)
        self.assertEqual(level6.count(CC1.GRAVEL), 0)
        self.assertEqual(level6.count(CC1.BLOB_N), 0)

    def test_keep(self):
        """Unit test for transforming a CC1Level by keeping only selected elements."""
        level = CC1Level()

        # Add one of everything to the level
        for i, elem in enumerate(CC1):
            level.add(i, elem)

        elements_to_keep = {CC1.FIRE, CC1.GRAVEL, CC1.DIRT, CC1.WATER}
        level2 = CC1LevelTransformer.keep(level, elements_to_keep)
        for elem in elements_to_keep:
            self.assertEqual(level2.count(elem), 1)
        for elem in CC1.all().difference(elements_to_keep).difference({CC1.FLOOR, }):
            self.assertEqual(level2.count(elem), 0)

    def test_replace_mobs(self):
        """Unit test for transforming a CC1Level by replacing mobs, keeping direction."""
        level = CC1Level()

        for p in range(20):
            d = "NESW"[p % 4]
            mob = CC1[f"TEETH_{d}"]
            level.add(p, mob)
        for p in range(20, 40):
            d = "NESW"[p % 4]
            mob = CC1[f"BLOB_{d}"]
            level.add(p, mob)
        for p in range(40, 60):
            d = "NESW"[p % 4]
            mob = CC1[f"PLAYER_{d}"]
            level.add(p, mob)
        for p in range(60, 80):
            d = "NESW"[p % 4]
            mob = CC1[f"TANK_{d}"]
            level.add(p, mob)
        for p in range(80, 100):
            d = "NESW"[p % 4]
            mob = CC1[f"BALL_{d}"]
            level.add(p, mob)

        self.assertEqual(level.count(CC1.teeth()), 20)
        self.assertEqual(level.count(CC1.blobs()), 20)
        self.assertEqual(level.count(CC1.players()), 20)
        self.assertEqual(level.count(CC1.tanks()), 20)
        self.assertEqual(level.count(CC1.balls()), 20)

        level2 = CC1LevelTransformer.replace_mobs(level, CC1.balls(), CC1.walkers())
        self.assertEqual(level2.count(CC1.balls()), 0)
        self.assertEqual(level2.count(CC1.walkers()), 20)
        for d in "NESW":
            self.assertEqual(level2.count(CC1[f"WALKER_{d}"]), 5)

        level3 = CC1LevelTransformer.replace_mobs(level, CC1.monsters(), CC1.blocks())
        self.assertEqual(level3.count(CC1.monsters()), 0)
        self.assertEqual(level3.count(CC1.blocks()), 80)
        for d in "NESW":
            self.assertEqual(level3.count(CC1[f"CLONE_BLOCK_{d}"]), 20)
        self.assertEqual(level3.count(CC1.players()), 20)

        level4 = CC1LevelTransformer.replace_mobs(level, CC1.mobs(), CC1.teeth())
        self.assertEqual(level4.count(CC1.teeth()), 100)
