"""Tests for CC1."""

import os
import unittest
from src.cc1 import CC1, CC1Cell, CC1Level, CC1LevelTransformer
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
        with open(os.path.join(os.getcwd(), "sets/dat/CCLP1.dat"), "rb") as f:
            cclp1 = DATHandler.parse(f.read())

        for level in cclp1.levels:
            if level.count(CC1.PANEL_SE) > 0:
                self.assertEqual(level, CC1LevelTransformer.rotate(level))
            else:
                # Should not be equal after 90-degree rotation
                rotated = CC1LevelTransformer.rotate(level)
                self.assertNotEqual(level, rotated)
                # Should be equal again after 360 degrees
                for _ in range(3):
                    rotated = CC1LevelTransformer.rotate(rotated)
                self.assertEqual(level, rotated)
