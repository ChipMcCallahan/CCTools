"""Tests for DAT Handler."""
import importlib.resources
import struct
import unittest
from unittest.mock import patch

from cc_tools.cc1 import CC1
from cc_tools.cc1_level import CC1Level
from cc_tools.cc1_levelset import CC1Levelset
from cc_tools.dat_handler import DATHandler, ParsedDATLevel, ParsedDATLevelset

def _load_all_official_sets():
    """Helper: load all official .dat set bytes from cc_tools.sets.dat."""
    dat_path = importlib.resources.files("cc_tools.sets.dat")
    sets = []
    for file in dat_path.iterdir():
        if file.is_file() and file.name.lower().endswith(".dat"):
            with open(file, "rb") as f:
                sets.append(f.read())
    return sets


class TestParseAndWriteOnOfficialSets(unittest.TestCase):
    """Tests for DAT Handler parsing and rewriting official sets."""

    def test_parse_and_write_roundtrip_raw_bytes(self):
        """
        Test that we can parse official DAT files to a ParsedDATLevelset and
        rewrite them with no byte level changes.
        """
        sets = _load_all_official_sets()
        self.assertLess(0, len(sets), "Expected at least one official .dat file")

        for raw in sets:
            parsed_tuple = DATHandler.parse(raw, as_tuple=True)
            self.assertIsInstance(parsed_tuple, ParsedDATLevelset)
            rewritten = DATHandler.write(parsed_tuple)
            self.assertEqual(raw, rewritten)

    def test_parse_as_tuple_and_as_levelset_have_matching_level_counts(self):
        """
        For at least one official DAT file, ensure that parse(as_tuple=True)
        and parse(as_tuple=False) see the same number of levels.
        """
        sets = _load_all_official_sets()
        self.assertLess(0, len(sets))

        raw = sets[0]  # one file is enough for this structural check
        levelset_tuple = DATHandler.parse(raw, as_tuple=True)
        levelset_obj = DATHandler.parse(raw, as_tuple=False)

        self.assertIsInstance(levelset_tuple, ParsedDATLevelset)
        self.assertIsInstance(levelset_obj, CC1Levelset)
        self.assertEqual(len(levelset_tuple.levels), len(levelset_obj.levels))


class TestRoundTripCC1Level(unittest.TestCase):
    """Roundtrip tests that exercise the CC1Level/CC1Levelset path."""

    def test_roundtrip_simple_level_via_dat_bytes(self):
        """
        Build a simple CC1Level (no traps/cloners/movement), write it to DAT and
        parse back to a CC1Levelset, and ensure value equality holds.
        """
        level = CC1Level()
        level.title = "Roundtrip Test"
        level.time = 123
        level.chips = 7
        level.hint = "Collect all the chips!"
        level.password = "ABCD"
        level.author = "UnitTest"

        # Place some non mob tiles on the map to ensure map contents survive.
        # Avoid mobs so movement stays empty and equality is simpler.
        for i in range(10):
            level.add(i, CC1.WALL)

        levelset = CC1Levelset()
        levelset.levels.append(level)

        dat_bytes = DATHandler.write(levelset)
        parsed_levelset = DATHandler.parse(dat_bytes)  # default as_tuple=False

        self.assertIsInstance(parsed_levelset, CC1Levelset)
        self.assertEqual(len(parsed_levelset.levels), 1)
        self.assertEqual(levelset, parsed_levelset)


class TestWriterHelpers(unittest.TestCase):
    """Tests for low level writer helpers like write_layers and compress_layer."""

    def test_write_layers_and_parse_layer_roundtrip(self):
        """
        Ensure write_layers() + __parse_layer() roundtrips a simple constant map
        for both top and bottom layers.
        """
        # Build a 32x32 map where top is 5 and bottom is 7 everywhere.
        tile_pairs = [(5, 7)] * (32 * 32)

        layer_1, layer_2 = DATHandler.Writer.write_layers(tile_pairs)

        # Decompress with the internal parser and verify values.
        parse_layer = DATHandler.Parser._Parser__parse_layer  # type: ignore[attr-defined]

        top = parse_layer(layer_1)
        bottom = parse_layer(layer_2)

        self.assertEqual(top, tuple(5 for _ in range(32 * 32)))
        self.assertEqual(bottom, tuple(7 for _ in range(32 * 32)))

    def test_compress_layer_roundtrip_with_rle(self):
        """
        Ensure compress_layer() followed by __parse_layer() roundtrips tile data
        and actually performs some compression when there are long runs.
        """
        # Build a pattern with some runs <=3 and some runs >3
        pattern = [1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3]
        target_len = 32 * 32
        values = (pattern * ((target_len // len(pattern)) + 1))[:target_len]
        original = bytes(values)

        compressed = DATHandler.Writer.compress_layer(original)
        parse_layer = DATHandler.Parser._Parser__parse_layer  # type: ignore[attr-defined]
        decompressed = parse_layer(compressed)

        self.assertEqual(tuple(values), decompressed)
        # Because of multiple runs >3 we should see some size reduction.
        self.assertLess(len(compressed), len(original))


class TestParserHelpers(unittest.TestCase):
    """Tests for the internal trap/cloner/movement parsing helpers."""

    def test_parse_traps(self):
        """
        __parse_traps should interpret 10 byte blocks as b_x, b_y, t_x, t_y, open_or_shut
        and convert coordinates to linear indices.
        """
        b_x, b_y = 1, 2
        t_x, t_y = 10, 20
        open_or_shut = 7

        traps_bytes = struct.pack("<HHHHH", b_x, b_y, t_x, t_y, open_or_shut)
        parse_traps = DATHandler.Parser._Parser__parse_traps  # type: ignore[attr-defined]

        traps = parse_traps(traps_bytes)
        self.assertEqual(len(traps), 1)

        expected_button = b_y * 32 + b_x
        expected_trap = t_y * 32 + t_x
        self.assertEqual(traps[0], (expected_button, expected_trap, open_or_shut))

    def test_parse_cloners(self):
        """
        __parse_cloners should interpret 8 byte blocks as b_x, b_y, c_x, c_y
        and convert coordinates to linear indices.
        """
        b_x, b_y = 3, 4
        c_x, c_y = 7, 9

        cloners_bytes = struct.pack("<HHHH", b_x, b_y, c_x, c_y)
        parse_cloners = DATHandler.Parser._Parser__parse_cloners  # type: ignore[attr-defined]

        cloners = parse_cloners(cloners_bytes)
        self.assertEqual(len(cloners), 1)

        expected_button = b_y * 32 + b_x
        expected_cloner = c_y * 32 + c_x
        self.assertEqual(cloners[0], (expected_button, expected_cloner))

    def test_parse_movement(self):
        """
        __parse_movement should treat pairs of bytes as (x, y) coordinates and
        convert them to linear indices.
        """
        x1, y1 = 1, 2
        x2, y2 = 10, 20
        movement_bytes = bytes([x1, y1, x2, y2])

        parse_movement = DATHandler.Parser._Parser__parse_movement  # type: ignore[attr-defined]
        movement = parse_movement(movement_bytes)

        self.assertEqual(movement, (y1 * 32 + x1, y2 * 32 + x2))


class TestEncrypt(unittest.TestCase):
    """Tests for password encryption helper."""

    def test_encrypt_xors_with_0x99(self):
        """
        encrypt() should XOR each byte with 0x99 and return the encrypted bytes.
        """
        plaintext = b"ABCD"  # all caps, within Windows-1252
        encrypted = DATHandler.Writer.encrypt(plaintext)
        expected = bytes(c ^ 0x99 for c in plaintext)
        self.assertEqual(encrypted, expected)

    def test_encrypt_invalid_byte_raises(self):
        """
        encrypt() should raise some form of exception when given an out-of-range byte.
        """
        # 0 is invalid according to the implementation (must be 1-255).
        with self.assertRaises(Exception):
            DATHandler.Writer.encrypt(b"\x00")


class TestSerialize(unittest.TestCase):
    """Tests for Writer.serialize with both level and levelset inputs."""

    def test_serialize_cc1level_and_cc1levelset(self):
        level = CC1Level()
        level.title = "New Chip On The Block"
        level.time, level.chips = 200, 20
        # Add a variety of elements just to exercise the map serialization.
        for i in range(112):
            level.add(i, CC1(i))

        levelset = CC1Levelset()
        levelset.levels.append(level)

        parsed_level = DATHandler.Writer.serialize(level)
        self.assertIsInstance(parsed_level, ParsedDATLevel)

        parsed_levelset = DATHandler.Writer.serialize(levelset)
        self.assertIsInstance(parsed_levelset, ParsedDATLevelset)
        self.assertEqual(len(parsed_levelset.levels), 1)

        # Also ensure full write does not throw and returns non empty bytes.
        dat_bytes = DATHandler.write(levelset)
        self.assertIsInstance(dat_bytes, (bytes, bytearray))
        self.assertGreater(len(dat_bytes), 0)

    def test_serialize_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            DATHandler.Writer.serialize("not a level or levelset")  # type: ignore[arg-type]


class TestFetchFromGliderbot(unittest.TestCase):
    """Tests for fetch_set_names and fetch_set using mocks to avoid real HTTP."""

    @patch("cc_tools.dat_handler.requests.get")
    def test_fetch_set_names_parses_anchor_texts(self, mock_get):
        html = """
        <html><body>
            <a href="../">Parent</a>
            <a href="set1.dat">SetOne</a>
            <a href="set2.dat">SetTwo</a>
        </body></html>
        """
        mock_get.return_value.text = html

        names = DATHandler.fetch_set_names()
        self.assertEqual(names, ("SetOne", "SetTwo"))

    @patch("cc_tools.dat_handler.DATHandler.parse")
    @patch("cc_tools.dat_handler.requests.get")
    def test_fetch_set_success_calls_parse_and_returns_result(self, mock_get, mock_parse):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"DAT_BYTES"
        mock_get.return_value.reason = "OK"

        sentinel = object()
        mock_parse.return_value = sentinel

        result = DATHandler.fetch_set("test.dat")
        self.assertIs(result, sentinel)
        mock_parse.assert_called_once_with(b"DAT_BYTES")

    @patch("cc_tools.dat_handler.requests.get")
    def test_fetch_set_failure_raises_runtime_error(self, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.content = b""
        mock_get.return_value.reason = "Not Found"

        with self.assertRaises(RuntimeError):
            DATHandler.fetch_set("missing.dat")