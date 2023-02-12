"""Tests for DAT Handler."""
import os
import unittest

from src.dat_handler import DATHandler


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
            parsed_and_written_set = DATHandler.Writer.write(DATHandler.Parser.parse(s))
            self.assertEqual(s, parsed_and_written_set)
