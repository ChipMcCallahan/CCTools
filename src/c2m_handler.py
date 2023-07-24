"""Classes for retrieving, parsing, and writing C2M files."""
from collections import defaultdict, namedtuple
from enum import Enum

from .cc_binary import CCBinary

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc2/"


class C2MConstants:
    """Constants for working with C2M files."""

    # pylint: disable=too-few-public-methods
    def __init__(self):
        raise TypeError("Cannot create 'C2MConstants' instances.")

    class ParsedField(Enum):
        """Enumeration of parsed CC2 fields to store."""
        FILE_VERSION = "file_version"
        LOCK = "lock"
        TITLE = "title"
        AUTHOR = "author"
        EDITOR_VERSION = "editor_version"
        CLUE = "clue"
        NOTE = "note"
        TIME = "time"
        EDITOR_WINDOW = "editor_window"
        VERIFIED_REPLAY = "verified_replay"
        HIDE_MAP = "hide_map"
        READ_ONLY_OPTION = "read_only_option"
        REPLAY_HASH = "replay_hash"
        HIDE_LOGIC = "hide_logic"
        CC1_BOOTS = "cc1_boots"
        BLOB_PATTERNS = "blob_patterns"
        MAP = "map"
        PACKED_MAP = "packed_map"
        KEY = "key"
        REPLAY = "replay"
        PACKED_REPLAY = "packed_replay"
        READ_ONLY = "read_only"
        FIELDS_IN_ORDER = "fields_in_order"
        GLIDERBOT_URL = "gliderbot_url"
        CC2H = "cc2h"
        FILE = "file"
        TYPE = "type"
        NAME = "name"
        SAVE = "save"

    END = b"END "
    FILE_VERSION = b"CC2M"
    LOCK = b"LOCK"
    TITLE = b"TITL"
    AUTHOR = b"AUTH"
    EDITOR_VERSION = b"VERS"
    CLUE = b"CLUE"
    NOTE = b"NOTE"
    OPTIONS = b"OPTN"
    MAP = b"MAP "
    PACKED_MAP = b"PACK"
    KEY = b"KEY "
    REPLAY = b"REPL"
    PACKED_REPLAY = b"PRPL"
    READ_ONLY = b"RDNY"
    TEXT_FIELDS = frozenset(
        (FILE_VERSION, LOCK, TITLE, AUTHOR, EDITOR_VERSION, CLUE, NOTE))
    BYTE_FIELDS = frozenset((MAP, PACKED_MAP, KEY, REPLAY, PACKED_REPLAY))
    FIELD_MAP = {
        FILE_VERSION: ParsedField.FILE_VERSION,
        LOCK: ParsedField.LOCK,
        TITLE: ParsedField.TITLE,
        AUTHOR: ParsedField.AUTHOR,
        EDITOR_VERSION: ParsedField.EDITOR_VERSION,
        CLUE: ParsedField.CLUE,
        NOTE: ParsedField.NOTE,
        MAP: ParsedField.MAP,
        PACKED_MAP: ParsedField.PACKED_MAP,
        KEY: ParsedField.KEY,
        REPLAY: ParsedField.REPLAY,
        PACKED_REPLAY: ParsedField.PACKED_REPLAY,
    }


ParsedC2MLevel = namedtuple("ParsedC2MLevel", tuple(f.value for f in C2MConstants.ParsedField))

ParsedC2MLevelset = namedtuple(
    "ParsedC2MLevelset",
    (
        "name",
        "levels",
        "c2g"
    )
)


class C2MHandler:
    """Class for retrieving, parsing, and writing C2M files."""

    # pylint: disable=too-few-public-methods
    def __init__(self):
        raise TypeError("Cannot create 'C2MHandler' instances.")

    @staticmethod
    def fetch_set_names_from_gliderbot():
        """Fetch a tuple of all available CC2 sets from Gliderbot."""

    @staticmethod
    def fetch_set_from_gliderbot(levelset):
        """Fetches a CC2 levelset from Gliderbot."""

    class Parser(CCBinary.Reader):
        """Class that parses raw bytes in C2M format."""

        @staticmethod
        def parse_c2m(raw_bytes):
            """Parses raw bytes in C2M format into elements of a CC2 level."""
            # pylint: disable=too-many-branches
            parser = C2MHandler.Parser(raw_bytes)
            parts = defaultdict(lambda: None)
            section = parser.bytes(4)
            while section != C2MConstants.END:
                length = parser.long()
                if section in C2MConstants.TEXT_FIELDS:
                    parts[C2MConstants.FIELD_MAP[section]] = parser.text(length)
                elif section in C2MConstants.BYTE_FIELDS:
                    parts[C2MConstants.FIELD_MAP[section]] = parser.bytes(length)
                elif section == C2MConstants.OPTIONS:
                    read = 0
                    if read < length:
                        parts[C2MConstants.ParsedField.TIME] = parser.short()
                        read += 2
                    if read < length:
                        parts[C2MConstants.ParsedField.EDITOR_WINDOW] = parser.byte()
                        read += 1
                    if read < length:
                        parts[C2MConstants.ParsedField.VERIFIED_REPLAY] = parser.byte()
                        read += 1
                    if read < length:
                        parts[C2MConstants.ParsedField.HIDE_MAP] = parser.byte()
                        read += 1
                    if read < length:
                        parts[C2MConstants.ParsedField.READ_ONLY_OPTION] = parser.byte()
                        read += 1
                    if read < length:
                        parts[C2MConstants.ParsedField.REPLAY_HASH] = parser.bytes(16)
                        read += 16
                    if read < length:
                        parts[C2MConstants.ParsedField.HIDE_LOGIC] = parser.byte()
                        read += 1
                    if read < length:
                        parts[C2MConstants.ParsedField.CC1_BOOTS] = parser.byte()
                        read += 1
                    if read < length:
                        parts[C2MConstants.ParsedField.BLOB_PATTERNS] = parser.byte()
                        read += 1
                    assert read == length
                elif section == C2MConstants.READ_ONLY:
                    assert length == 0
                else:
                    raise ValueError(f"Unexpected section {section}. Parts are {parts}.")
                section = parser.bytes(4)
            return ParsedC2MLevel(*tuple(parts[f] for f in C2MConstants.ParsedField))

        @staticmethod
        def unpack(packed_bytes):
            """Unpacks according to C2M compression rules."""
            parser = C2MHandler.Parser(packed_bytes)
            writer = C2MHandler.Writer()
            uncompressed_length = parser.short()
            while len(writer.written()) < uncompressed_length:
                n = parser.byte()
                if n <= 0x7f:  # Data block
                    writer.bytes(parser.bytes(n))
                else:  # Back Reference block
                    count = n - 0x80
                    offset = parser.byte()
                    bytes_to_copy = writer.written()[-offset:]
                    substring = bytes_to_copy
                    while len(substring) < count:
                        substring += bytes_to_copy
                    writer.bytes(substring[:count])
            return writer.written()

    class Writer(CCBinary.Writer):
        """Writes to C2M format."""

    class Packer:
        """Packs or unpacks according to C2M compression rules."""

        def __init__(self):
            self.reader, self.writer = None, None

        @staticmethod
        def pack(unpacked_bytes):
            """Packs according to C2M compression rules."""
            p = C2MHandler.Packer()
            p.reader = C2MHandler.Parser(unpacked_bytes)
            p.writer = C2MHandler.Writer()
            p.writer.short(p.reader.size())
            while p.reader.remaining() > 0:
                p.pack_data_blocks()
                p.pack_back_ref_blocks()
            return p.writer.written()

        def pack_data_blocks(self):
            """Packs 1 or more data blocks according to C2M compression rules."""
            w, r = self.writer, self.reader
            start = r.current()
            # Up to 127 of the bytes we haven't processed yet.
            eligible = r.raw()[start:start + 0x7F]
            if len(eligible) == 0:
                return

            # We have seen all 4-length substrings up to 255 previous indices
            seen = set()
            offset_limit = max(start - 0xFF, 0)
            for i in range(offset_limit, start):
                substring = r.raw()[i:i + 4]
                if len(substring) == 4:
                    seen.add(substring)
            max_seen_index = start

            # We want to write all bytes up until the first substring that has already
            # been added to the set.
            for i in range(len(eligible) - 4):
                # make sure we have all substrings looking back a max of 255 bytes
                for j in range(max_seen_index, start + i):
                    seen.add(r.raw()[j:j + 4])
                max_seen_index = start + i

                substring = eligible[i:i + 4]
                if substring in seen:
                    if i > 0:
                        w.byte(i)
                        w.bytes(r.bytes(i))
                    return

            # If we got to this point, we should write all eligible bytes and then try
            # to write another data block.
            # if len(eligible) > 4:
            w.byte(len(eligible))
            w.bytes(r.bytes(len(eligible)))
            self.pack_data_blocks()

        def pack_back_ref_blocks(self):
            """Packs a single back reference block according to C2M compression rules."""
            w, r = self.writer, self.reader
            raw = r.raw()
            if r.remaining() < 4:
                return
            index = r.current()
            limit = min(index + 0x7F, r.size())  # limit how far forward to look
            offset = max(index - 0xFF, 0)  # limit how far back to look
            test = raw[index:index + 4]
            repeat_offset = r.size()
            repeat_length = 0
            while offset < index:
                if raw[offset:offset + 4] != test:
                    offset += 1
                    continue
                i = index + 4
                o = offset + 4
                while i < limit and raw[o] == raw[i]:
                    i += 1
                    o += 1
                length = i - index
                if length > repeat_length:
                    repeat_offset = offset
                    repeat_length = length
                offset += 1

            if repeat_length > 0:
                count = repeat_length
                offset = index - repeat_offset
                w.byte(0x80 | count)
                w.byte(offset)
                r.seek(index + count)
