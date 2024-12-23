"""
Tests for C2M Handler.

This test suite exercises the functionality in `C2MHandler`, which is responsible
for parsing, writing, packing, and unpacking `.c2m` files (Chip's Challenge 2 maps).
We perform the following tasks:

1. Verify that known packed data can be unpacked and then repacked without data loss.
2. Parse a variety of local C2M files from a directory, test that packing/unpacking
   maps or replays yields correct data.
3. Test parse → write → parse round trips to ensure the final parsed object matches
   the original.
4. Check edge cases like empty files or invalid data.

Usage:
    python -m unittest path_to_this_file.py
"""

import importlib.resources
import logging
import os
import unittest

from cc_tools.c2m_handler import C2MHandler


def read_all_files(directory):
    """
    Read and return the raw bytes of all files within a directory (non-recursive).

    :param directory: A pathlib-like directory object.
    :return: A list of bytes, one entry per file.
    """
    all_files = []
    for file_name in os.listdir(directory):
        full_path = os.path.join(directory, file_name)
        if os.path.isfile(full_path):
            with open(full_path, "rb") as f:
                all_files.append(f.read())
    return all_files


class TestC2MHandlerOnLocalLevels(unittest.TestCase):
    """
    Tests for the C2MHandler class, focusing on local C2M files (read from disk).
    Verifies functionality around parsing, writing, packing, and unpacking C2M data.
    """

    def test_unpack_and_pack(self):
        """
        Test that known packed byte sequences (maps/replays) can be:
            - unpacked into raw (uncompressed) data
            - then packed again
            - and that the final packed result matches the original.

        This ensures we do not introduce errors in packing/unpacking logic.
        """
        packed_1 = (
            b'h\x00\x03\n\n\x02\x8a\x01\x01\x01\x87\x01\x04\x02\x02\x01'
            b'\x16\x88\r\x8d\x16\xa3\x14\x01\x14\x8d2\x89]'
        )
        packed_2 = (
            b'^\x04\t  \x02\x02\x15\x15\x15\x15\x02\x84\x01\x84\t\x88\x0c'
            b'\x8a\x05\x87\x16\x97\x07\xc0 \x01\x15\x89`\x01`\x91\x02\x8c '
            b'\x87\x0e\x9b@\x8a\xb8\x8d2\x8a@\x0e\x02\x01\x01\x01?w\x12\x04'
            b'O\x01w\x04\x02O\x8e\xd8\x8bF\r\x01V\x02\x0f\x03\x11\x01v\x02^'
            b'wh\x05\x88\'\x96M\x07v\x01O:w\x08\x03\x9aL\x13\t\t\x02\x02\x02'
            b'\t\t=\x02\x8b\x03v\x08Dm\x01v\x08^\x84\xf0\x96\xdb\x06\x02\x03'
            b'I\x01\x01\x01\x8c\xd0\x8f\xea\x06!\x03v\x04^m\x84\x9a\t&m\x01s'
            b'\x02\x81\x00\x01"\x8aN\x8f\xf7\x06\x15\x02v\x03\x01r\x9eP\x06'
            b'\x01\x01\x01\'\x01,\x96C\x01\x02\x84\x01\r\x81\x00\x05v\x06\x01'
            b'v\n\x01(s,\x14\x8c\x99\x01\x08\x89\x01\x0c\x02$m\x04\x0f<m\x06s'
            b'vL\x01\x84/\x02\x05\x01\x85:\x04\x08\x08\x08`\x86 \x87,\x84\x0e'
            b'\x03\x02\x01\x01\x86O\x03v\t^\x8bC\x8b&\x85R\x04#\x01v\x07\x85&'
            b'\x02\x08\x87\x88i\x93L\t\n\x02*rv\x1b\x01v\x08\x9cK\x04 -v\x03'
            b'\x96K\x8bY\x84\xeb\x02\t\t\x86\x05\x89\xd7\x8d\x9f\x84\xba\x06'
            b'\x01?\x01B\x1f\x02\x94@\x85\xda\x0bh\x01H\x11\x01=\x81\x00\x00'
            b'\x01-\x9eE\x02\x01\x01\x99E\x88\x01\x97\x85\x8b\xe7\x90\xc5\x90'
            b'\x02\xa0@\x88q\xc0 \x8e\x02\x8c\x17\x85\xd0'
        )

        # Test these two packed byte sequences
        for i, packed_data in enumerate((packed_1, packed_2)):
            with self.subTest(packed_index=i):
                unpacked_data = C2MHandler.Parser.unpack(packed_data)
                repacked_data = C2MHandler.Packer.pack(unpacked_data)
                self.assertEqual(
                    packed_data, repacked_data,
                    f"Unpack/Repack mismatch for packed_{i}."
                )

        # Now test any local C2M files:
        c2m_path = importlib.resources.files('cc_tools.sets.c2m')
        # Flatten the list of file bytes:
        all_c2m_files = sum((read_all_files(d) for d in c2m_path.iterdir() if d.is_dir()), [])

        for file_bytes in all_c2m_files:
            try:
                parsed_level = C2MHandler.Parser.parse_c2m(file_bytes)
            except ValueError as e:
                logging.error("Error parsing level bytes (size: %d): %s", len(file_bytes), e)
                continue

            # If there's a packed map, test a pack→unpack→pack cycle:
            if parsed_level.packed_map:
                with self.subTest(level_title=parsed_level.title, field="packed_map"):
                    self._verify_pack_cycle(parsed_level.packed_map, "map")

            # If there's a packed replay, test similarly:
            if parsed_level.packed_replay:
                with self.subTest(level_title=parsed_level.title, field="packed_replay"):
                    self._verify_pack_cycle(parsed_level.packed_replay, "replay")

    def _verify_pack_cycle(self, packed_data, data_label):
        """
        Helper method to:
            1) Unpack data
            2) Pack the result
            3) Unpack it again
            4) Check that the double-unpacked result matches the first unpack.

        :param packed_data: The initial compressed data.
        :param data_label: A string label (e.g. 'map' or 'replay') to identify data type in assertion messages.
        """
        # Unpack → Pack
        unpacked_data = C2MHandler.Parser.unpack(packed_data)
        repacked_data = C2MHandler.Packer.pack(unpacked_data)

        # Unpack again
        re_unpacked_data = C2MHandler.Parser.unpack(repacked_data)

        # Verify final result == original
        self.assertEqual(
            unpacked_data, re_unpacked_data,
            f"Double unpack mismatch for {data_label}."
        )

    def test_parse_write_parse(self):
        """
        Test a parse → write → parse cycle on local C2M files:
            - Parse a .c2m file into a ParsedC2MLevel namedtuple
            - Write it back out to raw bytes
            - Parse the newly written bytes again
            - Ensure that both parsed namedtuples match exactly
        """
        c2m_path = importlib.resources.files('cc_tools.sets.c2m')
        all_c2m_files = sum((read_all_files(d) for d in c2m_path.iterdir() if d.is_dir()), [])

        for idx, file_bytes in enumerate(all_c2m_files):
            try:
                parsed_level = C2MHandler.Parser.parse_c2m(file_bytes)
            except ValueError as e:
                logging.error("Error parsing c2m (size: %d): %s", len(file_bytes), e)
                continue

            # Write the parsed data back out
            try:
                c2m_written = C2MHandler.Writer.write_c2m(parsed_level)
            except Exception as e:
                self.fail(f"Error writing c2m (index {idx}): {e}")

            # Parse the just-written bytes
            try:
                parsed_level_again = C2MHandler.Parser.parse_c2m(c2m_written)
            except Exception as e:
                self.fail(f"Error re-parsing c2m after writing (index {idx}): {e}")

            # Compare the two parsed objects (both are namedtuples)
            self.assertEqual(
                parsed_level,
                parsed_level_again,
                f"Parse-Write-Parse mismatch (index {idx}); title: {parsed_level.title}"
            )

    def test_empty_file(self):
        """
        Test that parsing an empty file properly raises an error or
        fails in a predictable manner.
        """
        with self.assertRaises(EOFError, msg="Parsing empty file should fail with EOFError."):
            C2MHandler.Parser.parse_c2m(b"")

    def test_minimal_file(self):
        """
        Test that a file containing only an 'END ' marker (and nothing else)
        yields a valid, if minimal, ParsedC2MLevel object.
        """
        # Construct a minimal c2m file:  "END "
        minimal_c2m = b"END "
        parsed_level = C2MHandler.Parser.parse_c2m(minimal_c2m)
        # All fields should be None except the enumerated fields are present in the tuple
        # but they should be all None by default if not set.
        self.assertTrue(all(field is None for field in parsed_level), "All fields should be None in minimal file.")

    def test_corrupted_section_length(self):
        """
        Test that a file with a corrupted section length (e.g., negative or too large)
        raises an error.
        """
        # Example: "TITL" + length bytes that claims 9999, but the file ends immediately
        corrupted_c2m = b"TITL" + (9999).to_bytes(4, "little") + b"END "
        with self.assertRaises(EOFError, msg="Corrupted section length should raise EOFError."):
            C2MHandler.Parser.parse_c2m(corrupted_c2m)


if __name__ == "__main__":
    unittest.main()