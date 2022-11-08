"""Classes for retrieving, parsing, and writing C2M files."""
from collections import defaultdict

from src import CCBinary
from src.c2m import C2MConstants, ParsedC2MLevel

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc2/"


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
            parser = C2MHandler.Parser(raw_bytes)
            fields_in_order = []
            parts = defaultdict(lambda: None)
            section = parser.bytes(4)
            while section != C2MConstants.END:
                fields_in_order.append(section)
                length = parser.long()
                print(f"{section}, {length} bytes")
                if section in C2MConstants.UTF8_FIELDS:
                    parts[C2MConstants.FIELD_MAP[section]] = parser.bytes(length,
                                                                          convert_to_utf8=True)[:-1]
                elif section in C2MConstants.BYTE_FIELDS:
                    parts[C2MConstants.FIELD_MAP[section]] = parser.bytes(length)[:-1]
                elif section == C2MConstants.OPTIONS:
                    parts[C2MConstants.ParsedField.TIME] = parser.short()
                    parts[C2MConstants.ParsedField.EDITOR_WINDOW] = parser.byte()
                    parts[C2MConstants.ParsedField.VERIFIED_REPLAY] = parser.byte()
                    parts[C2MConstants.ParsedField.HIDE_MAP] = parser.byte()
                    parts[C2MConstants.ParsedField.READ_ONLY_OPTION] = parser.byte()
                    parts[C2MConstants.ParsedField.REPLAY_HASH] = parser.bytes(16)
                    parts[C2MConstants.ParsedField.HIDE_LOGIC] = parser.byte()
                    parts[C2MConstants.ParsedField.CC1_BOOTS] = parser.byte()
                    parts[C2MConstants.ParsedField.BLOB_PATTERNS] = parser.byte()
                elif section == C2MConstants.READ_ONLY:
                    assert length == 0
                else:
                    raise ValueError(f"Unexpected section {section}")
                section = parser.bytes(4)
            return ParsedC2MLevel(*tuple(parts[f.value] for f in C2MConstants.ParsedField))

        @staticmethod
        def unpack(packed_bytes):
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
