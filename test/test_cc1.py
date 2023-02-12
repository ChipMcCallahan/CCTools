"""Tests for CC1."""

import unittest
from src.cc1 import CC1


class TestCC1(unittest.TestCase):
    """Tests for CC1."""
    def test_sets(self):
        """Tests for CC1 tile code sets."""
        self.assertEqual(len(CC1.all()), 112)
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
