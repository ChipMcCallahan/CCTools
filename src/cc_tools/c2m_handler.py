"""
C2M Handler
-----------

This module provides classes and utilities for working with C2M files, which are part
of the Chip's Challenge 2 (CC2) file format ecosystem. It includes functionality for
parsing (reading) C2M data, writing (assembling) it back into C2M format, and
optionally fetching levelsets from the Gliderbot service.

Usage Overview:

    from your_project.c2m_handler import C2MHandler, ParsedC2MLevel

    # Reading (Parsing) a C2M file:
    with open("some_level.c2m", "rb") as f:
        raw_data = f.read()
    parsed_level = C2MHandler.Parser.parse_c2m(raw_data)

    # Writing (Assembling) back into C2M format:
    raw_data_out = C2MHandler.Writer.write_c2m(parsed_level)
    with open("some_level_out.c2m", "wb") as f:
        f.write(raw_data_out)

    # Packing and Unpacking with C2M compression:
    packed_bytes = C2MHandler.Packer.pack(unpacked_bytes)
    unpacked_bytes = C2MHandler.Parser.unpack(packed_bytes)

Classes:
- C2MConstants
- ParsedC2MLevel, ParsedC2MLevelset
- C2MHandler
  - Parser
  - Writer
  - Packer
"""

from collections import defaultdict, namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from .cc2 import CC2
from .cc_binary import CCBinary

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc2/"

@dataclass(slots=True)
class C2MElement:
    """
    A memory-efficient dataclass that has 10 optional fields corresponding to
    typical modifiers. Using slots=True ensures there is no __dict__ per instance,
    conserving memory. Each attribute defaults to None.
    """
    id: CC2
    wires: Optional[str] = None
    wire_tunnels: Optional[str] = None
    char: Optional[str] = None
    direction: Optional[str] = None
    directions: Optional[str] = None
    color: Optional[str] = None
    gate: Optional[str] = None
    tracks: Optional[List[str]] = None
    active_track: Optional[str] = None
    initial_entry: Optional[str] = None

class C2MConstants:
    """
    Constants and enumerations for working with C2M files.

    This class contains:
    - A ParsedField Enum representing logically parsed fields in a CC2 level.
    - Raw byte tags used in C2M files (e.g., b"LOCK", b"AUTH", etc.).
    - Helpful sets (TEXT_FIELDS, BYTE_FIELDS) for classifying which fields
      belong to text data vs. binary data.
    """

    def __init__(self):
        """
        This class is not meant to be instantiated.
        """
        raise TypeError("Cannot create 'C2MConstants' instances.")

    class ParsedField(Enum):
        """
        Enumeration of parsed CC2 fields to store.
        Each enum member corresponds to a known field in the C2M file format.
        """
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

    # Tag markers in the binary C2M file
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

    # Classification of which fields are treated as text vs. raw bytes
    TEXT_FIELDS = frozenset(
        (FILE_VERSION, LOCK, TITLE, AUTHOR, EDITOR_VERSION, CLUE, NOTE)
    )
    BYTE_FIELDS = frozenset((MAP, PACKED_MAP, KEY, REPLAY, PACKED_REPLAY))

    # Mapping from raw byte tags -> ParsedField enum
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


# Named tuples for storing parsed information
ParsedC2MLevel = namedtuple("ParsedC2MLevel", tuple(f.value for f in C2MConstants.ParsedField))

ParsedC2MLevelset = namedtuple(
    "ParsedC2MLevelset",
    (
        "name",
        "levels",
        "c2g",
    ),
)


class C2MHandler:
    """
    Primary class for working with C2M files, providing:
    - Retrieval from Gliderbot (if needed).
    - Parsing to and from in-memory representations.
    - Packing/unpacking using C2M compression.
    """

    def __init__(self):
        """
        This class is not meant to be instantiated directly.
        """
        raise TypeError("Cannot create 'C2MHandler' instances.")

    @staticmethod
    def fetch_set_names_from_gliderbot():
        """
        Fetch a tuple of all available CC2 sets from Gliderbot.
        (Not Implemented)
        """
        # Implementation could go here, e.g.:
        # response = requests.get(GLIDERBOT_URL + 'sets.json')
        # return tuple(response.json())
        pass

    @staticmethod
    def fetch_set_from_gliderbot(levelset):
        """
        Fetches a CC2 levelset from Gliderbot.
        (Not Implemented)

        :param levelset: The name of the levelset to fetch.
        """
        # Example:
        # url = f"{GLIDERBOT_URL}{levelset}.c2m"
        # response = requests.get(url)
        # return response.content
        pass

    class Parser(CCBinary.Reader):
        """
        A parser for reading C2M data from raw bytes.

        Inherits from CCBinary.Reader to provide low-level methods:
        - bytes(n)
        - text(n)
        - long()
        - short()
        - byte()
        - etc.

        Provides two main functionalities:
        1. parse_c2m(raw_bytes): Parse the entire C2M file structure into a
           ParsedC2MLevel namedtuple.
        2. unpack(packed_bytes): Unpack (decompress) data that was packed
           using C2M compression.
        """

        @staticmethod
        def parse_c2m(raw_bytes) -> ParsedC2MLevel:
            """
            Parse raw bytes in C2M format into elements of a CC2 level.

            :param raw_bytes: The raw bytes of the C2M file.
            :return: A ParsedC2MLevel namedtuple with parsed fields.
            :raises ValueError: If an unexpected section tag is encountered.
            """
            parser = C2MHandler.Parser(raw_bytes)
            parts = defaultdict(lambda: None)

            # Read 4-byte section tags until we encounter the 'END ' tag
            section = parser.bytes(4)
            while section != C2MConstants.END:
                length = parser.long()

                if section in C2MConstants.TEXT_FIELDS:
                    # Read a text field
                    parts[C2MConstants.FIELD_MAP[section]] = parser.text(length)
                elif section in C2MConstants.BYTE_FIELDS:
                    # Read a raw byte field
                    parts[C2MConstants.FIELD_MAP[section]] = parser.bytes(length)
                elif section == C2MConstants.OPTIONS:
                    # OPTIONS field is read in multiple smaller pieces
                    read_so_far = 0
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.TIME] = parser.short()
                        read_so_far += 2
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.EDITOR_WINDOW] = parser.byte()
                        read_so_far += 1
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.VERIFIED_REPLAY] = parser.byte()
                        read_so_far += 1
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.HIDE_MAP] = parser.byte()
                        read_so_far += 1
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.READ_ONLY_OPTION] = parser.byte()
                        read_so_far += 1
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.REPLAY_HASH] = parser.bytes(16)
                        read_so_far += 16
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.HIDE_LOGIC] = parser.byte()
                        read_so_far += 1
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.CC1_BOOTS] = parser.byte()
                        read_so_far += 1
                    if read_so_far < length:
                        parts[C2MConstants.ParsedField.BLOB_PATTERNS] = parser.byte()
                        read_so_far += 1

                    assert read_so_far == length, (
                        f"OPTIONS section length mismatch: "
                        f"expected {length}, read {read_so_far}"
                    )

                elif section == C2MConstants.READ_ONLY:
                    # READ_ONLY has length == 0
                    assert length == 0, (
                        "READ_ONLY section must have length 0, "
                        f"got {length} instead."
                    )

                else:
                    # Unexpected section
                    raise ValueError(
                        f"Unexpected section '{section}'. Current parts: {parts}."
                    )

                section = parser.bytes(4)

            # Return a namedtuple in the same order as C2MConstants.ParsedField
            return ParsedC2MLevel(*(parts[field] for field in C2MConstants.ParsedField))

        @staticmethod
        def unpack(packed_bytes: bytes) -> bytes:
            """
            Unpacks data from packed C2M format (C2M compression).

            :param packed_bytes: Data compressed using C2M compression rules.
            :return: Uncompressed data as raw bytes.
            """
            parser = C2MHandler.Parser(packed_bytes)
            writer = C2MHandler.Writer()

            # The first two bytes represent the uncompressed length
            uncompressed_length = parser.short()

            while len(writer.written()) < uncompressed_length:
                n = parser.byte()
                if n <= 0x7F:
                    # Data block: read n raw bytes
                    writer.bytes(parser.bytes(n))
                else:
                    # Back Reference block
                    count = n - 0x80
                    offset = parser.byte()

                    # The 'offset' indicates how far back to read
                    # from the already-written data
                    previously_written = writer.written()[-offset:]
                    chunk = previously_written

                    # Ensure the chunk covers 'count' bytes
                    while len(chunk) < count:
                        chunk += previously_written

                    writer.bytes(chunk[:count])

            return writer.written()

    class Writer(CCBinary.Writer):
        """
        Writer for assembling a ParsedC2MLevel back into raw C2M bytes.

        Inherits from CCBinary.Writer, which provides methods:
        - bytes(data: bytes)
        - text(s: str, encoding: str = 'windows-1252')
        - long(val: int)
        - short(val: int)
        - byte(val: int)
        - etc.

        Usage:
            raw_bytes = C2MHandler.Writer.write_c2m(parsed_level)
        """

        @staticmethod
        def write_c2m(parsed_level: ParsedC2MLevel) -> bytes:
            """
            Given a ParsedC2MLevel namedtuple, assemble the data into
            valid C2M format and return the raw bytes.

            :param parsed_level: A ParsedC2MLevel namedtuple containing
                                 the fields of a CC2 level.
            :return: Raw bytes conforming to the C2M file specification.
            """
            writer = C2MHandler.Writer()
            parts_dict = parsed_level._asdict()  # Convert namedtuple -> dict

            # 1) Write out text fields (FILE_VERSION, LOCK, TITLE, AUTHOR, EDITOR_VERSION, CLUE, NOTE)
            for section_tag, parsed_field in C2MConstants.FIELD_MAP.items():
                if section_tag in C2MConstants.TEXT_FIELDS:
                    value = parts_dict[parsed_field.value]
                    if value is not None:
                        writer.bytes(section_tag)
                        writer.long(len(value))
                        writer.bytes(value.encode("windows-1252"))

            # 2) Write out byte fields (MAP, PACKED_MAP, KEY, REPLAY, PACKED_REPLAY)
            for section_tag, parsed_field in C2MConstants.FIELD_MAP.items():
                if section_tag in C2MConstants.BYTE_FIELDS:
                    value = parts_dict[parsed_field.value]
                    if value is not None:
                        writer.bytes(section_tag)
                        writer.long(len(value))
                        writer.bytes(value)

            # 3) Write the OPTIONS section (time, editor_window, verified_replay, etc.) if needed
            subwriter = C2MHandler.Writer()
            bytes_written = 0

            def _append_short_if_not_none(field):
                nonlocal bytes_written
                val = parts_dict[field.value]
                if val is not None:
                    subwriter.short(val)
                    bytes_written += 2

            def _append_byte_if_not_none(field):
                nonlocal bytes_written
                val = parts_dict[field.value]
                if val is not None:
                    subwriter.byte(val)
                    bytes_written += 1

            # TIME (short)
            _append_short_if_not_none(C2MConstants.ParsedField.TIME)
            # EDITOR_WINDOW (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.EDITOR_WINDOW)
            # VERIFIED_REPLAY (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.VERIFIED_REPLAY)
            # HIDE_MAP (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.HIDE_MAP)
            # READ_ONLY_OPTION (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.READ_ONLY_OPTION)

            # REPLAY_HASH (16 bytes)
            replay_hash = parts_dict[C2MConstants.ParsedField.REPLAY_HASH.value]
            if replay_hash is not None:
                subwriter.bytes(replay_hash)
                bytes_written += 16

            # HIDE_LOGIC (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.HIDE_LOGIC)
            # CC1_BOOTS (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.CC1_BOOTS)
            # BLOB_PATTERNS (byte)
            _append_byte_if_not_none(C2MConstants.ParsedField.BLOB_PATTERNS)

            # If any of these fields were present, write the OPTIONS section
            if bytes_written > 0:
                writer.bytes(C2MConstants.OPTIONS)
                writer.long(bytes_written)
                writer.bytes(subwriter.written())

            # 4) If there's a separate read-only chunk, the parser checks that length == 0
            #    Typically, you would write this only if parsed_level.READ_ONLY is True
            #    or parts_dict[ParsedField.READ_ONLY.value] is True. Adjust as needed.
            if parts_dict[C2MConstants.ParsedField.READ_ONLY.value]:
                writer.bytes(C2MConstants.READ_ONLY)
                writer.long(0)

            # 5) Write "END " to mark the end of the file
            writer.bytes(C2MConstants.END)

            return writer.written()

    class Packer:
        """
        The Packer class handles packing (compressing) data using the C2M
        compression scheme. It also relies on the Parser class for reading.

        The compression rules operate with the notion of 'data blocks' and
        'back references,' akin to a simple RLE or LZ77 approach.

        Usage:
            packed_data = C2MHandler.Packer.pack(unpacked_bytes)
        """

        def __init__(self):
            self.reader = None
            self.writer = None

        @staticmethod
        def pack(unpacked_bytes: bytes) -> bytes:
            """
            Compress (pack) data according to the C2M rules.

            :param unpacked_bytes: The raw data to be compressed.
            :return: The compressed data as a bytes object.
            """
            packer = C2MHandler.Packer()
            packer.reader = C2MHandler.Parser(unpacked_bytes)
            packer.writer = C2MHandler.Writer()

            # First, write the uncompressed length (2 bytes, short)
            packer.writer.short(packer.reader.size())

            # Keep packing blocks (data or backref) until we exhaust the reader
            while packer.reader.remaining() > 0:
                packer._pack_data_blocks()
                packer._pack_back_ref_blocks()

            return packer.writer.written()

        def _pack_data_blocks(self):
            """
            Pack one or more 'data blocks' according to C2M compression rules.
            A data block is indicated by a byte n <= 0x7F, followed by n raw bytes.
            """
            start_index = self.reader.current()
            # Up to 127 unprocessed bytes
            chunk = self.reader.raw()[start_index : start_index + 0x7F]

            if len(chunk) == 0:
                return  # Nothing to pack

            seen_substrings = set()
            offset_limit = max(start_index - 0xFF, 0)
            max_seen_index = start_index

            # Collect previously seen 4-byte substrings within a 255-byte window
            for i in range(offset_limit, start_index):
                substring = self.reader.raw()[i : i + 4]
                if len(substring) == 4:
                    seen_substrings.add(substring)

            # We'll try to find the first 4-byte substring in `chunk` that we've
            # already seen, so we know where a back-ref block might start.
            for i in range(len(chunk) - 4):
                # Add new 4-byte substrings that come into range
                for j in range(max_seen_index, start_index + i):
                    sub4 = self.reader.raw()[j : j + 4]
                    if len(sub4) == 4:
                        seen_substrings.add(sub4)
                max_seen_index = start_index + i

                current_sub4 = chunk[i : i + 4]
                if current_sub4 in seen_substrings:
                    # We've hit a repeat substring; write all data bytes up to here
                    if i > 0:
                        self.writer.byte(i)  # length of data block
                        self.writer.bytes(self.reader.bytes(i))
                    return

            # If no repeats found in the chunk, write out all of it as a data block
            self.writer.byte(len(chunk))
            self.writer.bytes(self.reader.bytes(len(chunk)))

            # Attempt to pack more data blocks recursively
            self._pack_data_blocks()

        def _pack_back_ref_blocks(self):
            """
            Attempt to pack a single 'back reference block,' indicated by:
            - a byte n, where n = 0x80 + length
            - a byte offset (how far back to read)

            If insufficient repeating data is found, this method does nothing (no-op).
            """

            # If fewer than 4 bytes remain unread, we can't form a back-ref block.
            if self.reader.remaining() < 4:
                return

            current_pos = self.reader.current()
            # We'll look forward up to 0x7F bytes from the current position.
            forward_limit = min(current_pos + 0x7F, self.reader.size())
            # We'll look backward up to 0xFF bytes from the current position.
            backward_limit = max(current_pos - 0xFF, 0)

            # The candidate substring is the next 4 bytes at the current reader position.
            candidate_substring = self.reader.raw()[current_pos: current_pos + 4]

            best_match_offset = None
            best_match_length = 0

            # Search backward in a 255-byte window to find the longest match.
            search_index = backward_limit
            while search_index < current_pos:
                window_substring = self.reader.raw()[search_index: search_index + 4]

                # If the 4-byte window matches our candidate, see how far it extends.
                if window_substring == candidate_substring:
                    forward_index = current_pos + 4
                    window_index = search_index + 4

                    # Continue matching bytes while within forward_limit.
                    while (
                            forward_index < forward_limit
                            and self.reader.raw()[window_index] == self.reader.raw()[forward_index]
                    ):
                        forward_index += 1
                        window_index += 1

                    # Calculate the total length of the matched substring.
                    current_match_length = forward_index - current_pos

                    # Update our best match if this one is longer.
                    if current_match_length > best_match_length:
                        best_match_length = current_match_length
                        best_match_offset = search_index

                search_index += 1

            # If a match was found, write the back-ref block.
            if best_match_length > 0 and best_match_offset is not None:
                # The byte n is 0x80 + match_length.
                self.writer.byte(0x80 | best_match_length)
                # The offset is how far back from the current position the match begins.
                self.writer.byte(current_pos - best_match_offset)
                # Advance the reader by the length of the matched block.
                self.reader.seek(current_pos + best_match_length)

