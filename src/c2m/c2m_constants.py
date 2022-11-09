"""Constants and primitives for working with C2M files."""
from collections import namedtuple
from enum import Enum


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
    UTF8_FIELDS = frozenset(
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
