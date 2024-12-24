from typing import List

from cc_tools.c2m_cell import C2MCell
from cc_tools.c2m_element import C2MElement
from cc_tools.c2m_modifiers import C2MModifiers
from cc_tools.cc2 import CC2


class C2MMapDecoder:
    """
    Decodes a MAP/PACK data section into a 2D grid of C2MCell objects.

    Attributes:
        data (bytes):    The raw bytes of the MAP or PACK section (already unpacked).
        offset (int):    Internal read position pointer for 'data'.
    """

    def __init__(self, data: bytes):
        """
        Initialize the decoder with the binary map data and reset the read offset.

        :param data: The (already-unpacked) raw bytes for the MAP / PACK section.
        """
        self.data = data
        self.offset = 0  # We'll manually track our read position.

    def decode(self) -> List[List[C2MCell]]:
        """
        Decode the entire map from self.data. The map structure is:
          - First byte: width
          - Second byte: height
          - Then tile specifications (left->right, top->bottom).

        :return: A 2D list of C2MCell objects, with 'height' rows and 'width' columns.
        """
        # 1: read width + height
        width = int.from_bytes(self._read_bytes(1), byteorder="little")
        height = int.from_bytes(self._read_bytes(1), byteorder="little")

        cells_2d: List[List[C2MCell]] = []

        # 2: read each tile specification
        for y in range(height):
            row: List[C2MCell] = []
            for x in range(width):
                cell = C2MCell()
                # We loop until we have assigned 'terrain' because the logic
                # indicates that once 'terrain' is set, we stop reading further tiles for this cell.
                while cell.terrain is None:
                    elem = self._parse_elem()
                    if elem.id in CC2.panels():
                        cell.panel = elem
                    elif elem.id in CC2.all_mobs():
                        cell.mob = elem
                    elif elem.id == CC2.NOT_ALLOWED_MARKER:
                        cell.not_allowed = elem
                    elif elem.id in CC2.pickups():
                        cell.pickup = elem
                    else:
                        cell.terrain = elem
                row.append(cell)
            cells_2d.append(row)

        return cells_2d

    def _read_bytes(self, n: int = 1) -> bytes:
        """
        Read 'n' bytes from self.data at the current offset, return them as bytes,
        and increment the offset by n.

        :param n: Number of bytes to read.
        :return: The next 'n' bytes from self.data.
        """
        if self.offset + n > len(self.data):
            raise ValueError(f"Tried to read {n} bytes but only "
                             + f"{len(self.data) - self.offset} remain.")
        chunk = self.data[self.offset: self.offset + n]
        self.offset += n
        return chunk

    def _read_int(self, n: int = 1) -> int:
        """
        Read 'n' bytes from self.data at the current offset, interpret them
        in little-endian, return as an int, and increment the offset by n.

        :param n: Number of bytes to read.
        :return: A little-endian integer value for the read bytes.
        """
        if self.offset + n > len(self.data):
            raise ValueError(f"Tried to read {n} bytes but only "
                             + f"{len(self.data) - self.offset} remain.")
        chunk = self.data[self.offset: self.offset + n]
        self.offset += n
        return int.from_bytes(chunk, byteorder="little")

    def _parse_elem(self) -> C2MElement:
        """
        Parse a single tile element from the map data. Some tiles have
        additional modifiers to be read.

        Steps:
          1. Read the tile ID (1 byte).
          2. Create a C2MElement with that ID.
          3. Depending on the ID, read additional bytes and parse them
             (e.g. directions, thin wall canopy, etc.).
          4. If the tile is a modifier tile, we read extra bytes,
             parse them, and return the modified tile instead.

        :return: A new C2MElement reflecting the parsed tile + modifiers.
        """
        # 1: Read the tile ID.
        id_val = self._read_int(1)
        tile_id = CC2(id_val)
        elem = C2MElement(tile_id)

        # 2: Check if we need to parse direction, canopy, or other modifiers:
        if tile_id in CC2.all_mobs():
            # e.g. read direction
            C2MModifiers.parse_direction(elem, self._read_bytes(1))
            if tile_id == CC2.DIRECTIONAL_BLOCK:
                # also read arrow bits
                C2MModifiers.parse_dblock_arrows(elem, self._read_bytes(1))

        elif tile_id == CC2.THIN_WALL_CANOPY:
            C2MModifiers.parse_thinwall_canopy(elem, self._read_bytes(1))

        elif tile_id in CC2.modifiers():
            # For certain tiles, we read a specified number of bytes as the modifier
            #  and then parse another element (the tile being modified).
            if tile_id == CC2.MODIFIER_8BIT:
                modifier_bytes = self._read_bytes(1)
            elif tile_id == CC2.MODIFIER_16BIT:
                modifier_bytes = self._read_bytes(2)
            else:
                # fallback: read 4 bytes for other possible modifiers
                modifier_bytes = self._read_bytes(4)

            modified_elem = self._parse_elem()
            # Now apply the parsed modifier bytes to 'modified_elem'
            C2MModifiers.parse_modifier(modified_elem, modifier_bytes)
            return modified_elem

        return elem
