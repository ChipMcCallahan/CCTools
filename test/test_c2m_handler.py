"""Tests for C2M Handler."""
import importlib.resources
import os
import unittest
import logging

from src.c2m_handler import C2MHandler


class TestC2MHandlerOnLocalLevels(unittest.TestCase):
    """Tests for C2MHandler working with local C2M files."""

    def test_unpack_and_pack(self):
        """Test packing and unpacking maps and replays."""
        packed_1 = (b'h\x00\x03\n\n\x02\x8a\x01\x01\x01\x87\x01\x04\x02\x02\x01'
                    b'\x16\x88\r\x8d\x16\xa3\x14\x01\x14\x8d2\x89]')
        packed_2 = (b'^\x04\t  \x02\x02\x15\x15\x15\x15\x02\x84\x01\x84\t\x88\x0c'
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
                    b'\x02\xa0@\x88q\xc0 \x8e\x02\x8c\x17\x85\xd0')

        for i, packed in enumerate((packed_1, packed_2)):
            unpacked = C2MHandler.Parser.unpack(packed)
            repacked = C2MHandler.Packer.pack(unpacked)
            self.assertEqual(packed, repacked, f"Unpack/Repack failed for local bytes packed_{i}.")

        c2m_path = importlib.resources.files('cc_tools.sets.c2m')

        # flatten the list of lists using 'sum'
        c2ms = sum([read_all_files(d) for d in c2m_path.iterdir() if d.is_file()], [])

        for c2m in c2ms:
            try:
                parsed_level = C2MHandler.Parser.parse_c2m(c2m)
            except ValueError as e:
                logging.error("Error parsing level %s: %s", c2m, e)
            if not parsed_level.packed_map:
                logging.warning("%s does not have a packed map section.", parsed_level.title)
                continue

            unpacked = C2MHandler.Parser.unpack(parsed_level.packed_map)
            repacked = C2MHandler.Packer.pack(unpacked)
            reunpacked = C2MHandler.Parser.unpack(repacked)

            self.assertEqual(unpacked, reunpacked,
                             f"Unpack/Repack map failed for {parsed_level.title}")

            if parsed_level.packed_replay:
                unpacked = C2MHandler.Parser.unpack(parsed_level.packed_replay)
                repacked = C2MHandler.Packer.pack(unpacked)
                reunpacked = C2MHandler.Parser.unpack(repacked)
                self.assertEqual(unpacked, reunpacked,
                                 f"Unpack/Repack replay failed for {parsed_level.title}")


def read_all_files(directory):
    """Read all files in a directory."""
    files = []
    for c2m in os.listdir(directory):
        with open(os.path.join(directory, c2m), "rb") as f:
            files.append(f.read())
    return files
