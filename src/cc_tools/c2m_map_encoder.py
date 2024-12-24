from typing import List
from cc_tools.c2m_cell import C2MCell
from cc_tools.c2m_element import C2MElement
from cc_tools.c2m_modifiers import C2MModifiers
from cc_tools.cc2 import CC2


class C2MMapEncoder:
    """
    Encodes a 2D grid of C2MCell objects into the same byte format
    that C2MMapDecoder (MAP/PACK) expects.

    Notes:
      - Writes width and height as 1-byte each (little-endian).
      - Then encodes each cell, row by row, left to right.
      - Each cell may have multiple 'layers' (panel, mob, not_allowed, pickup, terrain).
      - For tiles with extra data (e.g. direction, canopy bits, arrow bits),
        we replicate the logic from decode() in reverse, calling the relevant
        C2MModifiers build_... method to generate the extra bytes.
    """

    def __init__(self, cells_2d: List[List[C2MCell]]):
        """
        :param cells_2d: A 2D grid of C2MCell objects (height rows x width columns).
        """
        self.cells_2d = cells_2d

    def encode(self) -> bytes:
        """
        Encode the grid into bytes: width (1 byte), height (1 byte),
        then each tile (panel, mob, not_allowed, pickup, terrain) for each cell.

        :return: A bytes object suitable for decoding by C2MMapDecoder.
        """
        # We'll build up a list of byte chunks, then join them at the end.
        data_chunks = []

        # Handle empty map edge case
        if not self.cells_2d:
            data_chunks.append((0).to_bytes(1, "little"))  # width=0
            data_chunks.append((0).to_bytes(1, "little"))  # height=0
            return b"".join(data_chunks)

        height = len(self.cells_2d)
        width = len(self.cells_2d[0])
        # Write width + height
        data_chunks.append(width.to_bytes(1, "little"))
        data_chunks.append(height.to_bytes(1, "little"))

        # For each row, for each cell, output panel -> mob -> not_allowed -> pickup -> terrain
        for row in self.cells_2d:
            for cell in row:
                for elem in (cell.panel, cell.mob, cell.not_allowed, cell.pickup, cell.terrain):
                    if elem is not None:
                        data_chunks.append(self._encode_element(elem))

        return b"".join(data_chunks)

    def _encode_element(self, elem: C2MElement) -> bytes:
        """
        Encode a single tile element according to the logic in C2MMapDecoder,
        but reversed. For example:
          - If tile is in CC2.all_mobs(): write tile ID, then direction byte,
            plus arrow bits if it's CC2.DIRECTIONAL_BLOCK.
          - If tile is CC2.THIN_WALL_CANOPY: write ID, then canopy bits.
          - If tile is in CC2.modified_tiles(): write modifier ID, then modifier bytes,
            then tile ID.
          - Otherwise, just write tile ID.

        :param elem: The C2MElement to encode.
        :return: A bytes object for that tile, matching the decode() logic.
        """
        out = bytearray()
        tile_id = elem.id

        # 1) If tile is a mob => (ID, direction, maybe arrows)
        if tile_id in CC2.all_mobs():
            out.append(tile_id.value)  # 1 byte ID
            # direction
            dir_bytes = C2MModifiers.build_direction(elem)
            out += dir_bytes
            # if DIRECTIONAL_BLOCK => also arrow bits
            if tile_id == CC2.DIRECTIONAL_BLOCK:
                arrow_bytes = C2MModifiers.build_dblock_arrows(elem)
                out += arrow_bytes

        # 2) If tile is thin wall canopy => (ID, canopy bits)
        elif tile_id == CC2.THIN_WALL_CANOPY:
            out.append(tile_id.value)
            canopy_bytes = C2MModifiers.build_thinwall_canopy(elem)
            out += canopy_bytes

        # 3) If tile is a modified tile => (modifier ID, modifier_bytes, ID)
        elif tile_id in CC2.modified_tiles():
            # 1) Build the raw modifier bytes (1, 2, or 4 bytes) for this tile
            mod_bytes = C2MModifiers.build_modifier(elem)

            # 2) Convert them to a little-endian integer so we can see if high bytes are zero
            mod_val = int.from_bytes(mod_bytes, byteorder="little")

            # 3) If the entire value is zero => omit the modifier tile & bytes
            #    (just write out the final tile id).
            if mod_val == 0:
                out.append(tile_id.value)
                return bytes(out)

            # 4) Otherwise, shrink to as few bytes as possible:
            if mod_val <= 0xFF:
                # Only 1 byte needed => use MODIFIER_8BIT
                out.append(CC2.MODIFIER_8BIT.value)
                out.append(mod_val & 0xFF)
            elif mod_val <= 0xFFFF:
                # Fits in 2 bytes => use MODIFIER_16BIT
                out.append(CC2.MODIFIER_16BIT.value)
                out += (mod_val & 0xFFFF).to_bytes(2, 'little')
            else:
                # Otherwise, use MODIFIER_32BIT (4 bytes)
                out.append(CC2.MODIFIER_32BIT.value)
                out += mod_val.to_bytes(4, 'little')

            # 5) Finally, write the real tile ID (the tile being "modified")
            out.append(tile_id.value)

        # 4) Otherwise => just (ID)
        else:
            out.append(tile_id.value)

        return bytes(out)
