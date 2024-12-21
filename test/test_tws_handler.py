"""Tests for TWS Handler."""
import unittest
import importlib.resources
import logging

from cc_tools.tws_handler import TWSHandler


class TestParseOfficialReplays(unittest.TestCase):
    """Tests for TWS Handler parsing official replays."""
    
    def test_parse(self):
        """Test that we can parse TWS files with no errors and correct # of records."""
        # Access the 'replays' directory within the 'cc_tools' package
        tws_path = importlib.resources.files('cc_tools.replays')
        
        # Iterate over each item in the 'replays' directory
        for tws_name in tws_path.iterdir():
            # Check if the current item is a file and ends with '.tws'
            if tws_name.is_file() and tws_name.name.lower().endswith('.tws'):
                try:
                    # Decode the TWS file
                    results = TWSHandler(tws_path / tws_name).decode()
                    
                    # Determine the expected number of replays based on the filename
                    if "CC1-lynx" in tws_name.name:
                        expected_length = 148
                    else:
                        expected_length = 149
                    
                    # Assert that the number of replays matches the expected count
                    self.assertEqual(
                        len(results.replays),
                        expected_length,
                        msg=f"File {tws_name.name} expected {expected_length} replays, got {len(results.replays)}"
                    )
                
                except Exception as e:
                    self.fail(f"Failed to parse {tws_name.name}: {e}")
            else:
                # Optionally, log or skip non-.tws files if they exist
                logging.info(f"Skipping non-TWS file: {tws_name.name}")