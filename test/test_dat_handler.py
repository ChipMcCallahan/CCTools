"""Tests for DAT Handler."""
import os
import unittest

from src.dat_handler import DATHandler
from src.cc1 import CC1, CC1Level, CC1Levelset


class TestParseAndWriteOnOfficialSets(unittest.TestCase):
    """Tests for DAT Handler parsing and rewriting official sets."""
    def test_parse_and_write(self):
        """Test that we can parse DAT files and rewrite them with no changes."""
        sets_dir = os.path.join(os.getcwd(), "sets/dat/")
        sets = []
        for set_name in os.listdir(sets_dir):
            with open(os.path.join(sets_dir, set_name), "rb") as f:
                sets.append(f.read())

        self.assertLess(0, len(sets))

        for s in sets:
            parsed_and_written_set = DATHandler.write(DATHandler.parse(s, as_tuple=True))
            self.assertEqual(s, parsed_and_written_set)

    def test_write_cc1level_and_cc1levelset(self):
        """Test that DATHandler does not throw for CC1Level or CC1Levelset classes."""
        level = CC1Level()
        level.time, level.chips, level.title = 200, 20, "New Chip On The Block"
        for i in range(112):
            level.add(i, CC1(i))
        levelset = CC1Levelset()
        levelset.levels.append(level)
        result = DATHandler.Writer.serialize(level)
        self.assertIsNotNone(result)
        result = DATHandler.Writer.serialize(levelset)
        self.assertIsNotNone(result)
        result = DATHandler.write(levelset)
        self.assertIsNotNone(result)
