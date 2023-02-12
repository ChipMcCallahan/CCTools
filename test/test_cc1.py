"""Tests for CC1."""

import unittest
from src.cc1 import CC1


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
