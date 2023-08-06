"""Tests for TWS Handler."""
import os
import unittest

from src.tws_handler import TWSHandler

class TestParseOfficialReplays(unittest.TestCase):
    """Tests for TWS Handler parsing official replays."""
    def test_parse(self):
        """Test that we can parse TWS files with no errors and correct # of records."""
        tws_dir = os.path.join(os.getcwd(), "replays/")
        for tws_name in os.listdir(tws_dir):
            results = TWSHandler(os.path.join(tws_dir, tws_name)).decode()
            expected_length = 148 if tws_name.startswith("CC1-lynx") else 149
            self.assertEqual(len(results["records"]), expected_length)
