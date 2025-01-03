"""Tests for DAT Handler."""
import importlib.resources
import unittest

from cc_tools.cc1 import CC1
from cc_tools.cc1_level import CC1Level
from cc_tools.cc1_levelset import CC1Levelset
from cc_tools.dat_handler import DATHandler


class TestParseAndWriteOnOfficialSets(unittest.TestCase):
    """Tests for DAT Handler parsing and rewriting official sets."""
    def test_parse_and_write(self):
        """Test that we can parse DAT files and rewrite them with no changes."""
        dat_path = importlib.resources.files('cc_tools.sets.dat')
        sets = []

        for file in dat_path.iterdir():
            # Skip non-.dat files
            if file.is_file() and file.name.lower().endswith('.dat'):
                dat_file_path = dat_path / file.name  # same logic
                with open(dat_file_path, 'rb') as f:
                    sets.append(f.read())

        self.assertLess(0, len(sets))

        for s in sets:
            # Parse and rewrite checks
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
