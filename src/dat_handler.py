"""Classes for retrieving, parsing, and writing CC1 DAT files."""
import io
import struct
import logging
from collections import namedtuple
import requests
from bs4 import BeautifulSoup

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc1/"


class DATHandler:
    """Class for retrieving DAT files from Gliderbot"""
    # pylint: disable-msg=too-few-public-methods
    def __init__(self):
        try:
            # Retrieve the list of all available CC1 sets from Gliderbot.
            soup = BeautifulSoup(
                requests.get(
                    GLIDERBOT_URL,
                    timeout=10).text,
                "html.parser")

            # Ignore the first link, it is a link to parent directory.
            self.available_sets = [a.text for a in soup.find_all("a")[1:]]
        except Exception as ex:
            raise f"Error retrieving list of sets from Gliderbot: {ex}"

        # Cache results as we retrieve sets to minimize HTTP requests.
        self.cache = {}

    def fetch(self, levelset):
        """Retrieve a binary levelset by name from Gliderbot."""
        if levelset in self.cache:
            return self.cache[levelset]
        if levelset not in self.available_sets:
            raise Exception(f"{levelset} was not found on gliderbot.")
        resp = requests.get(GLIDERBOT_URL + levelset, timeout=10)

        if resp.status_code < 300:
            logging.info("Successfully retrieved %s.", GLIDERBOT_URL + levelset)
            self.cache[levelset] = resp.content
            return DATHandler.Parser.parse(resp.content)

        raise Exception(
            f"Failed to retrieve {GLIDERBOT_URL + levelset}. {resp.status_code}: {resp.reason}")

    class Parser:
        """Class that parses raw bytes in DAT format."""
        def __init__(self, raw_bytes=None):
            self.bytes_io = io.BytesIO(raw_bytes)

        Levelset = namedtuple(
            "ParsedDATLevelset",
            ("levels",
             "magic_number"))
        Level = namedtuple(
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
             "extra_fields"
             ))

        @staticmethod
        def parse(raw_bytes):
            """Parses raw bytes in DAT format into elements of a CC1 Levelset."""
            parser = DATHandler.Parser(raw_bytes)
            magic_number = parser.long()
            num_levels = parser.short()
            return DATHandler.Parser.Levelset(
                [parser.parse_level() for _ in range(num_levels)],
                magic_number
            )

        def parse_level(self):
            """Parses raw bytes in DAT format into elements of a CC1 Level."""
            # pylint: disable-msg=too-many-locals
            self.short()  # level_size_bytes, UNUSED
            number, time, chips = self.short(), self.short(), self.short()
            map_detail = self.short()
            top = self.__parse_layer(self.bytes(self.short()))
            bottom = self.__parse_layer(self.bytes(self.short()))

            title, password, hint = None, None, None
            traps, cloners, movement = None, None, None
            bytes_remaining = self.short()
            extra_fields = []
            while bytes_remaining > 0:
                field, length = self.byte(), self.byte()
                content = self.bytes(length)
                bytes_remaining -= length + 2
                if field == 3:
                    title = content[:-1].decode("utf-8")
                elif field == 4:
                    traps = self.__parse_traps(content)
                elif field == 5:
                    cloners = self.__parse_cloners(content)
                elif field == 6:
                    password = ''.join([chr(b ^ 0x99) for b in content[:-1]])
                elif field == 7:
                    hint = content[:-1].decode("utf-8")
                elif field == 10:
                    movement = self.__parse_movement(content)
                else:
                    logging.warning("Encountered Unexpected Field %s", str(field))
                    extra_fields.append((field, content))

            return DATHandler.Parser.Level(title, number, time, chips, hint, password,
                                           tuple(zip(top, bottom)), traps, cloners, movement,
                                           map_detail, tuple(extra_fields))

        @staticmethod
        def __parse_layer(layer_bytes):
            parser = DATHandler.Parser(layer_bytes)
            layer = []
            while len(layer) < 32 * 32:
                next_byte = parser.byte()
                if next_byte == 0xFF:  # run length encoding
                    length, tilecode = parser.byte(), parser.byte()
                    layer.extend([tilecode] * length)
                else:
                    layer.append(next_byte)
            return tuple(layer)

        @staticmethod
        def __parse_traps(traps_bytes):
            parser = DATHandler.Parser(traps_bytes)
            controls = []
            for _ in range(len(traps_bytes) // 10):
                b_x, b_y = parser.short(), parser.short()
                t_x, t_y = parser.short(), parser.short()
                parser.short()  # open/closed, unused
                controls.append((b_y * 32 + b_x, t_y * 32 + t_x))
            return tuple(controls)

        @staticmethod
        def __parse_cloners(cloners_bytes):
            parser = DATHandler.Parser(cloners_bytes)
            controls = []
            for _ in range(len(cloners_bytes) // 8):
                b_x, b_y = parser.short(), parser.short()
                c_x, c_y = parser.short(), parser.short()
                controls.append((b_y * 32 + b_x, c_y * 32 + c_x))
            return tuple(controls)

        @staticmethod
        def __parse_movement(movement_bytes):
            parser = DATHandler.Parser(movement_bytes)
            movement = []
            for _ in range(len(movement_bytes) // 2):
                monster_x, monster_y = parser.byte(), parser.byte()
                movement.append(monster_y * 32 + monster_x)
            return tuple(movement)

        def byte(self):
            """Read a byte from IO."""
            return struct.unpack("<B", self.bytes_io.read(1))[0]

        def short(self):
            """Read a short (2 bytes) from IO."""
            return struct.unpack("<H", self.bytes_io.read(2))[0]

        def long(self):
            """Read a long (4 bytes) from IO."""
            return struct.unpack("<L", self.bytes_io.read(4))[0]

        def bytes(self, n_bytes):
            """Read n bytes from IO."""
            return self.bytes_io.read(n_bytes)
