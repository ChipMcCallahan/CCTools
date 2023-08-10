"""Tests for TWS Handler."""
import unittest
import importlib.resources

from src.tws_handler import TWSHandler

class TestParseOfficialReplays(unittest.TestCase):
    """Tests for TWS Handler parsing official replays."""
    def test_parse(self):
        """Test that we can parse TWS files with no errors and correct # of records."""
        tws_path = importlib.resources.files('cc_tools.replays')

        for tws_name in tws_path.iterdir():
            results = TWSHandler(tws_path / tws_name).decode()
            expected_length = 148 if "CC1-lynx" in str(tws_name) else 149
            self.assertEqual(len(results["records"]), expected_length)
