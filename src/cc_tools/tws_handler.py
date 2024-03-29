# pylint: disable=invalid-name
"""This module contains two classes, TWSSolutionMoveDecoder and TWSHandler,
which are used to decode a TWS file. TWS files are typically used to store
solutions to the game Chip's Challenge. The TWSSolutionMoveDecoder class
decodes solution moves in various formats, while TWSHandler class decodes the
header, first record, level number, password and full records from the TWS
file. For an explanation of the TWS format,
see https://www.muppetlabs.com/~breadbox/software/tworld/tworldff.html#3."""
import struct

from collections import defaultdict


class TWSSolutionMoveDecoder:
    # pylint: disable=too-few-public-methods
    """
    This class is used to decode the solution moves in a TWS file. The
    solution moves can be encoded in different formats and this class handles
    those formats. The class stores the decoded moves and keeps track of the
    formats it has encountered during the decoding.
    """

    def __init__(self, solution_moves):
        """This function initializes the class with a sequence of solution
        moves."""
        self.absolute_time = 0
        self.decoded_moves = []
        self.formats_seen = defaultdict(int)
        self.iterator = iter(solution_moves)

    def _decode_format_1_one_byte(self, b1):
        """Decodes a solution move that is encoded in the 1-byte version of
        the first format, e.g. TTTDDD01"""
        time = (b1 & 0b11100000) >> 5
        direction = (b1 & 0b11100) >> 2
        self.absolute_time += time + 1
        self.decoded_moves.append(
            {'tick': self.absolute_time, 'direction': direction,
             'bytes': (b1,), 'format': '1'})
        self.formats_seen["format_1_one_byte"] += 1

    def _decode_format_1_two_bytes(self, b1):
        """Decodes a solution move that is encoded in the 2-byte version of
        the first format, e.g. TTTTTTTT TTTDDD10 (bytes 2, 1)"""
        b2 = next(self.iterator)
        time = (b2 << 3) | ((b1 & 0b11100000) >> 5)
        direction = (b1 & 0b11100) >> 2
        self.absolute_time += time + 1
        self.decoded_moves.append(
            {'tick': self.absolute_time, 'direction': direction,
             'bytes': (b2, b1), 'format': '1'})
        self.formats_seen["format_1_two_bytes"] += 1

    def _decode_format_2(self, b1):
        """Decodes a solution move that is encoded in the second format, using
        4 bytes, e.g. 0000TTTT TTTTTTTT TTTTTTTT TTT0DD11 (bytes 4, 3, 2, 1)"""
        b2, b3, b4 = next(self.iterator), next(self.iterator), next(
            self.iterator)
        time = ((b4 & 0b1111) << (24 - 5)) | (b3 << (16 - 5)) | (
                b2 << (8 - 5)) | (
                       (b1 & 0b11100000) >> 5)
        direction = (b1 & 0b1100) >> 2
        self.absolute_time += time + 1
        self.decoded_moves.append(
            {'tick': self.absolute_time, 'direction': direction,
             'bytes': (b4, b3, b2, b1), 'format': '2'})
        self.formats_seen["format_2_four_bytes"] += 1

    def _decode_format_3(self, b1):
        """Decodes a solution move that is encoded in the third format, using
        1 byte, e.g. FFEEDD00."""
        for direction in (
                (b1 & 0b1100) >> 2, (b1 & 0b110000) >> 4,
                (b1 & 0b11000000) >> 6):
            self.absolute_time += 4
            self.decoded_moves.append(
                {'tick': self.absolute_time, 'direction': direction,
                 'bytes': (b1,), 'format': '3'})
        self.formats_seen["format_3_one_byte"] += 1

    def _decode_format_4(self, b1):
        """Decodes a solution move that is encoded in the fourth format,
        using 2-5 bytes, e.g. 000TTTTT TTTTTTTT TTTTTTTT TTDDDDDD DDD1NN11 (
        bytes 5, 4, 3, 2, 1)."""
        N = (b1 & 0b1100) >> 2
        additional_bytes = [next(self.iterator) for _ in range(N + 1)]
        b2 = additional_bytes[0]
        direction = ((b2 & 0b00111111) << (8 - 5)) | ((b1 & 0b11100000) >> 5)
        b3 = additional_bytes[1] if len(additional_bytes) > 1 else 0
        b4 = additional_bytes[2] if len(additional_bytes) > 2 else 0
        b5 = additional_bytes[3] if len(additional_bytes) > 3 else 0
        time = ((b5 & 0b11111) << (24 - 6)) | (b4 << (16 - 6)) | (
                b3 << (8 - 6)) | (
                       (b2 & 0b11000000) >> 6)
        direction = ((b2 & 0b111111) << (8 - 5)) | ((b1 & 0b11100000) >> 5)
        self.absolute_time += time + 1
        self.decoded_moves.append(
            {'tick': self.absolute_time, 'direction': direction,
             'bytes': tuple(reversed(additional_bytes)), 'format': '4'})
        self.formats_seen["format_4_variable_bytes"] += 1

    def decode(self):
        """Iterates through all the solution moves, decodes them using the
        appropriate format, and returns the decoded moves and the formats that
        were seen."""
        while True:
            try:
                self.decode_one()
            except StopIteration:
                break
        return self.decoded_moves, self.formats_seen

    def decode_one(self):
        """Decodes the next solution move. Raises StopIteration if there are
        no more moves."""
        b1 = next(self.iterator)

        if b1 & 0b11 == 1:
            self._decode_format_1_one_byte(b1)
        elif b1 & 0b11 == 2:
            self._decode_format_1_two_bytes(b1)
        elif b1 & 0b10011 == 3:
            self._decode_format_2(b1)
        elif b1 & 0b11 == 0:
            self._decode_format_3(b1)
        else:
            self._decode_format_4(b1)


class TWSHandler:
    # pylint: disable=too-few-public-methods
    """This class is used to handle a TWS file. It reads the file and decodes
    the information in it, which includes the header, optional first record,
    level number, password and full records. The class stores the decoded
    records and keeps track of the formats it has encountered during the
    decoding."""

    def __init__(self, binary_file_name):
        """This function initializes the class with the name of the binary
        file that is to be decoded."""
        self.binary_file_name = binary_file_name
        self.records = []
        self.formats_seen = defaultdict(int)

    @staticmethod
    def _decode_header(f):
        """This static method decodes the header of the TWS file."""
        signature, ruleset, visited_level, remainder_count = struct.unpack(
            '<IHBb', f.read(8))
        if signature != 0x999B3335:
            raise ValueError(
                f'Invalid file format. Expected signature 0x999B3335, got '
                f'{signature}')
        f.seek(remainder_count, 1)
        return {
            'signature': signature,
            'ruleset': ('Lynx' if ruleset == 1
                        else 'MS' if ruleset == 2
            else 'Unknown'),
            'last_visited_level': visited_level,
            'bytes_left_in_header': remainder_count,
        }

    @staticmethod
    def _decode_first_record(f):
        """This static method decodes the optional first record of the TWS
        file."""
        f.seek(16, 1)  # skip the next 16 bytes which are ignored
        level_set_name = bytearray()
        while True:  # read until we encounter a zero byte
            byte = f.read(1)
            if byte == b'\x00' or not byte:
                break
            level_set_name.append(ord(byte))
        return level_set_name.decode()

    @staticmethod
    def _parse_level_number_and_password(f):
        """This static method parses the level number and password from a
        record in the TWS file."""
        # read the next two bytes to determine the record type
        level_number_data = f.read(2)
        if not level_number_data:  # end of file
            return None

        level_number = struct.unpack('<H', level_number_data)[0]

        # read the next 4 bytes for the level password
        level_password = f.read(4).decode('ascii')

        return {
            'level_number': level_number,
            'level_password': level_password,
        }

    def _parse_full_record(self, f, remaining_bytes):
        """This method parses the full record from the TWS file, which
        includes the solution moves."""
        flag = struct.unpack('<B', f.read(1))[0]

        # read the rest of the larger record header
        slide_direction_and_stepping, rng_value, time_in_ticks = struct.unpack(
            '<BIi', f.read(9))

        # read the solution moves as a byte string until the start of the
        # next record (or EOF)
        solution_moves = f.read(remaining_bytes - 10)
        decoded_solution, new_formats_seen = TWSSolutionMoveDecoder(
            solution_moves).decode()
        for k, v in new_formats_seen.items():
            self.formats_seen[k] += v
        return {
            'flag': flag,
            'slide_direction_and_stepping': slide_direction_and_stepping,
            'rng_value': rng_value,
            'time_in_ticks': time_in_ticks,
            'solution_moves': decoded_solution
        }

    def decode(self):
        """This method opens the TWS file, decodes the header, first record,
        level number, password and full records, and returns the decoded
        information."""
        with open(self.binary_file_name, 'rb') as f:
            header = self._decode_header(f)
            levelset_name = "Unspecified"
            while True:
                next_bytes = f.read(4)
                if not next_bytes:
                    break
                record_size = struct.unpack('<i', next_bytes)[0]

                if len(self.records) == 0 and f.peek(6)[:6] == b'\x00' * 6:
                    # handle the optional first record differently
                    levelset_name = self._decode_first_record(f)
                    continue

                record = self._parse_level_number_and_password(f)
                if not record:
                    break

                # there's more data, so it's a larger record
                if record_size > 6:
                    record.update(self._parse_full_record(f, record_size - 6))
                    self.records.append(record)

        kwargs = {
            "header": header,
            "levelset_name": levelset_name,
            "records": self.records,
            "formats_seen": self.formats_seen
        }
        return TWSReplaySet(**kwargs)


class TWSMove:
    def __init__(self, **kwargs):
        self.tick = kwargs["tick"]
        self.direction = kwargs["direction"]
        self.bytes = kwargs["bytes"]
        self.format = kwargs["format"]


class TWSReplay:
    def __init__(self, **kwargs):
        self.level_number = kwargs["level_number"]
        self.password = kwargs["level_password"]
        self.flag = kwargs["flag"]
        self.slide_d_and_step = kwargs["slide_direction_and_stepping"]
        self.rng = kwargs["rng_value"]
        self.ticks = kwargs["time_in_ticks"]
        self.moves = tuple(TWSMove(**move) for move in kwargs["solution_moves"])

    def __str__(self):
        return (f"level_num {self.level_number} ({self.password}): "
                f"{len(self.moves)} moves.")


class TWSReplaySet:
    def __init__(self, **kwargs):
        self.header = kwargs["header"]
        self.levelset_name = kwargs["levelset_name"]
        self.formats_seen = kwargs["formats_seen"]
        self.replays = tuple(
            TWSReplay(**record) for record in kwargs["records"])

    def __str__(self):
        return f"{len(self.replays)} replays for {self.levelset_name}."
