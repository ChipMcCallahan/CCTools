"""Classes for retrieving, parsing, and writing CC1 DAT files."""
import logging
import requests
from bs4 import BeautifulSoup

from src.cc_binary_io import CCBinary
from src.dat import ParsedDATLevel, ParsedDATLevelset, DATConstants

GLIDERBOT_URL = "https://bitbusters.club/gliderbot/sets/cc1/"


class DATHandler:
    """Class for retrieving DAT files from Gliderbot"""

    def __init__(self):
        raise TypeError("Cannot create 'DATHandler' instances.")

    @staticmethod
    def fetch_set_names_from_gliderbot():
        """Retrieve a tuple of all available sets on Gliderbot."""
        try:
            # Retrieve the list of all available CC1 sets from Gliderbot.
            soup = BeautifulSoup(
                requests.get(
                    GLIDERBOT_URL,
                    timeout=10).text,
                "html.parser")

            # Ignore the first link, it is a link to parent directory.
            return (a.text for a in soup.find_all("a")[1:])
        except Exception as ex:
            raise f"Error retrieving list of sets from Gliderbot: {ex}"

    @staticmethod
    def fetch_set_from_gliderbot(levelset):
        """Retrieve a binary levelset by name from Gliderbot."""
        resp = requests.get(GLIDERBOT_URL + levelset, timeout=10)
        if resp.status_code < 300:
            logging.info("Successfully retrieved %s.", GLIDERBOT_URL + levelset)
            return DATHandler.Parser.parse_set(resp.content)
        raise Exception(
            f"Failed to retrieve {GLIDERBOT_URL + levelset}. {resp.status_code}: {resp.reason}")

    class Parser(CCBinary.Reader):
        """Class that parses raw bytes in DAT format."""

        @staticmethod
        def parse_set(raw_bytes):
            """Parses raw bytes in DAT format into elements of a CC1 Levelset."""
            parser = DATHandler.Parser(raw_bytes)
            magic_number = parser.long()
            num_levels = parser.short()
            return ParsedDATLevelset(
                tuple(parser.parse_level() for _ in range(num_levels)),
                magic_number
            )

        def parse_level(self):
            """Parses raw bytes in DAT format into elements of a CC1 Level."""
            # pylint: disable=too-many-locals
            self.short()  # level_size_bytes, UNUSED
            number, time, chips = self.short(), self.short(), self.short()
            map_detail = self.short()
            top = self.__parse_layer(self.bytes(self.short()))
            bottom = self.__parse_layer(self.bytes(self.short()))

            title, password, hint = None, None, None
            traps, cloners, movement = tuple(), tuple(), tuple()
            bytes_remaining = self.short()
            extra_fields = []
            field_numbers_in_order = []
            while bytes_remaining > 0:
                field, length = self.byte(), self.byte()
                field_numbers_in_order.append(field)
                content = self.bytes(length)
                bytes_remaining -= length + 2
                if field == DATConstants.TITLE_FIELD:
                    title = content[:-1].decode("utf-8")
                elif field == DATConstants.TRAPS_FIELD:
                    traps = self.__parse_traps(content)
                elif field == DATConstants.CLONERS_FIELD:
                    cloners = self.__parse_cloners(content)
                elif field == DATConstants.PASSWORD_FIELD:
                    password = ''.join([chr(b ^ 0x99) for b in content[:-1]])
                elif field == DATConstants.HINT_FIELD:
                    hint = content[:-1].decode("utf-8")
                elif field == DATConstants.MOVEMENT_FIELD:
                    movement = self.__parse_movement(content)
                else:
                    logging.warning(
                        "Encountered Unexpected Field %s", str(field))
                    extra_fields.append((field, content))

            return ParsedDATLevel(title, number, time, chips, hint, password,
                                  tuple(zip(top, bottom)), traps, cloners, movement,
                                  map_detail, tuple(field_numbers_in_order),
                                  tuple(extra_fields))

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
                open_or_shut = parser.short()
                controls.append((b_y * 32 + b_x, t_y * 32 + t_x, open_or_shut))
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

    class Writer(CCBinary.Writer):
        """Class that writes raw bytes in DAT format."""

        @staticmethod
        def write_set(levelset, *, filename=None):
            """Writes a CC1 levelset in DAT format. Writes to file only if filename is specified.
            Always returns the written DAT bytes."""
            writer = DATHandler.Writer()
            writer.long(levelset.magic_number or 0x0002AAAC)
            writer.short(len(levelset.levels))
            for level in levelset.levels:
                level_bytes = DATHandler.Writer.write_level(level)
                writer.short(len(level_bytes))
                writer.bytes(level_bytes)
            dat_bytes = writer.written()
            if filename:
                with open(filename, "wb") as file_obj:
                    file_obj.write(dat_bytes)
                    logging.info("Wrote set to file %s", filename)
            return dat_bytes

        @staticmethod
        def write_level(level):
            """Writes a CC1 level in DAT format and returns written DAT bytes. """
            # pylint: disable=too-many-locals, too-many-branches, too-many-statements
            writer_1 = DATHandler.Writer()
            writer_1.short(level.number)
            writer_1.short(level.time)
            writer_1.short(level.chips)
            writer_1.short(level.map_detail)
            layer_1, layer_2 = DATHandler.Writer.write_layers(level.map)
            writer_1.short(len(layer_1))
            writer_1.bytes(layer_1)
            writer_1.short(len(layer_2))
            writer_1.bytes(layer_2)

            writer_2 = DATHandler.Writer()
            ordered_fields = level.field_numbers_in_order or DATConstants.STANDARD_FIELDS
            ordered_fields = list(ordered_fields)
            if level.title and DATConstants.TITLE_FIELD not in ordered_fields:
                ordered_fields.append(DATConstants.TITLE_FIELD)
            if len(level.trap_controls) > 0 and DATConstants.TRAPS_FIELD not in ordered_fields:
                ordered_fields.append(DATConstants.TRAPS_FIELD)
            if len(level.clone_controls) > 0 and DATConstants.CLONERS_FIELD not in ordered_fields:
                ordered_fields.append(DATConstants.CLONERS_FIELD)
            if level.password and DATConstants.PASSWORD_FIELD not in ordered_fields:
                ordered_fields.append(DATConstants.PASSWORD_FIELD)
            if level.hint and DATConstants.HINT_FIELD not in ordered_fields:
                ordered_fields.append(DATConstants.HINT_FIELD)
            if len(level.movement) > 0 and DATConstants.MOVEMENT_FIELD not in ordered_fields:
                ordered_fields.append(DATConstants.MOVEMENT_FIELD)

            for field in ordered_fields:
                if field == DATConstants.TITLE_FIELD and level.title:
                    writer_2.byte(field)
                    title_bytes = level.title.encode('utf-8') + b'\x00'
                    writer_2.byte(len(title_bytes))
                    writer_2.bytes(title_bytes)
                elif field == DATConstants.TRAPS_FIELD and len(level.trap_controls) > 0:
                    writer_2.byte(field)
                    writer_2.byte(10 * len(level.trap_controls))
                    for t in level.trap_controls:
                        k, v = t[0], t[1]
                        open_or_shut = t[2] if len(t) > 2 else 0
                        writer_2.shorts(
                            (k % 32, k // 32, v % 32, v // 32, open_or_shut))
                elif field == DATConstants.CLONERS_FIELD and len(level.clone_controls) > 0:
                    writer_2.byte(field)
                    writer_2.byte(8 * len(level.clone_controls))
                    for k, v in level.clone_controls:
                        writer_2.shorts(
                            (k % 32, k // 32, v % 32, v // 32))
                elif field == DATConstants.PASSWORD_FIELD and level.password:
                    writer_2.byte(field)
                    password_bytes = DATHandler.Writer.encrypt(level.password.encode("utf-8"))
                    password_bytes += b'\x00'
                    writer_2.byte(len(password_bytes))
                    writer_2.bytes(password_bytes)
                elif field == DATConstants.HINT_FIELD and level.hint:
                    writer_2.byte(field)
                    hint_bytes = level.hint.encode("utf-8") + b'\x00'
                    writer_2.byte(len(hint_bytes))
                    writer_2.bytes(hint_bytes)
                elif field == DATConstants.MOVEMENT_FIELD and len(level.movement) > 0:
                    writer_2.byte(field)
                    writer_2.byte(2 * len(level.movement))
                    for p in level.movement:
                        writer_2.byte(p % 32)
                        writer_2.byte(p // 32)
                elif field not in DATConstants.STANDARD_FIELDS:
                    for extra_field, content in level.extra_fields:
                        if field == extra_field:
                            writer_2.byte(field)
                            writer_2.byte(len(content))
                            writer_2.bytes(content)
                            break
                else:
                    logging.warning("Field %s existed in level %s, but nothing was written. ",
                                    field, level)

            remaining_bytes = writer_2.written()
            writer_1.short(len(remaining_bytes))
            writer_1.bytes(remaining_bytes)
            return writer_1.written()

        @staticmethod
        def write_layers(level_map):
            """Writes and compresses top and bottom layers in a CC1 Level map."""
            top, bottom = DATHandler.Writer(), DATHandler.Writer()
            for cell in level_map:
                top.byte(cell[0])
                bottom.byte(cell[1])
            return tuple(DATHandler.Writer.compress_layer(layer.written())
                         for layer in (top, bottom))

        @staticmethod
        def compress_layer(layer):
            """Replaces any substrings containing [4, 255] of the same character with
            Run-Length Encoding"""
            index = 0
            writer = DATHandler.Writer()
            while index < len(layer):
                c = layer[index]
                end = index
                while end + 1 < len(layer) and layer[end + 1] == c and end + 1 - index < 255:
                    end += 1
                length = end + 1 - index
                if length <= 3:
                    writer.bytes(c.to_bytes(1, 'little') * length)
                else:
                    writer.byte(0xff)  # signify RLE
                    writer.byte(length)
                    writer.byte(c)
                index += length
            return writer.written()

        @staticmethod
        def encrypt(input_to_encrypt):
            """Encrypts a plain text password written in all caps."""
            writer = DATHandler.Writer()
            for c in input_to_encrypt:
                if c < 65 or c > 90:
                    raise f"password must be all caps, was {input_to_encrypt}"
                index = c - int.from_bytes(b'A', "big")
                writer.byte(DATConstants.ENCRYPTED_CHARS[index])
            return writer.written()
