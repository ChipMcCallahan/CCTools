"""Constants and primitives for working with DAT files."""
from collections import namedtuple

ParsedDATLevelset = namedtuple(
    "ParsedDATLevelset",
    ("levels",
     "magic_number"))
ParsedDATLevel = namedtuple(
    "ParsedDATLevel",
    ("title",
     "number",
     "time",
     "chips",
     "hint",
     "password",
     "map",
     "trap_controls",
     "clone_controls",
     "movement",
     "map_detail",
     "field_numbers_in_order",
     "extra_fields"
     ))


class DATConstants:
    """Constants for working with DAT files."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        raise TypeError("Cannot create 'DATConstants' instances.")

    ENCRYPTED_CHARS = [0xD8, 0xDB, 0xDA, 0xDD, 0xDC, 0xDF, 0xDE, 0xD1, 0xD0, 0xD3, 0xD2, 0xD5,
                       0xD4, 0xD7, 0xD6, 0xC9, 0xC8, 0xCB, 0xCA, 0xCD, 0xCC, 0xCF, 0xCE, 0xC1,
                       0xC0, 0xC3]

    STANDARD_FIELDS = (3, 4, 5, 6, 7, 10)

    TITLE_FIELD = 3
    TRAPS_FIELD = 4
    CLONERS_FIELD = 5
    PASSWORD_FIELD = 6
    HINT_FIELD = 7
    MOVEMENT_FIELD = 10
    STANDARD_FIELDS = (
        TITLE_FIELD,
        TRAPS_FIELD,
        CLONERS_FIELD,
        PASSWORD_FIELD,
        HINT_FIELD,
        MOVEMENT_FIELD
    )
