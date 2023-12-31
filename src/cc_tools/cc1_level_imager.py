"""Class that creates images of CC1Levels"""
import math

from PIL import Image

from cc_tools import CC1
from cc_tools.cc1_sprite_set import CC1SpriteSet
from cc_tools.img_utils import draw_red_line


class CC1LevelImager:
    """Class that creates images of CC1Levels"""

    # pylint: disable=too-few-public-methods
    def __init__(self, sprite_set_name="8x8"):
        self.sprite_set = CC1SpriteSet.load_set_by_name(sprite_set_name)
        self.show_secrets = None
        self.set_show_secrets(True)
        self.show_connections = None
        self.set_show_connections(True)

    def set_sprite_set(self, sprite_set_name):
        """Set the sprite set to use for level imaging."""
        self.sprite_set = CC1SpriteSet.load_set_by_name(sprite_set_name)

    def get_sprite_copy(self, cc1_elem):
        """Get copy of associated image for a CC1 element."""
        name = cc1_elem.name if isinstance(cc1_elem, CC1) else cc1_elem
        return self.sprite_set.get_sprite(name).copy()

    def set_show_secrets(self, show_secrets):
        """Set the show_secrets boolean on self and CC1SpriteSet."""
        self.show_secrets = show_secrets
        self.sprite_set.set_show_secrets(show_secrets)

    def set_show_connections(self, show_connections):
        """Set the show_secrets boolean on self and CC1SpriteSet."""
        self.show_connections = show_connections

    def level_image(self, cc1level):
        """Create an 8x8 PNG image from a CC1Level."""
        size = self.sprite_set.get_size_in_pixels()
        map_img = Image.new("RGBA", (32 * size, 32 * size))

        for j in range(32):
            for i in range(32):
                cell = cc1level.map[j * 32 + i]
                tile_img = self.get_sprite_copy(cell.bottom)

                # If the top layer is different from the bottom, process it
                if cell.top != cell.bottom:
                    self.process_top_layer(cell, tile_img)

                map_img.paste(tile_img, (i * size, j * size))

        if self.show_connections:
            for p1, p2 in list(cc1level.traps.items()) + list(
                    cc1level.cloners.items()):
                x1, y1 = p1 % 32, p1 // 32
                x2, y2 = p2 % 32, p2 // 32
                i1, j1, i2, j2 = (n * size + size // 2 for n in
                                  (x1, y1, x2, y2))
                draw_red_line(map_img, i1, j1, i2, j2)

        return map_img

    def process_top_layer(self, cell, tile_img):
        """Process the top layer of a cell and paste it onto the tile image."""
        paste = self.get_sprite_copy(cell.top).convert('RGBA')
        mask = paste.split()[3]  # Use alpha channel as mask
        tile_img.paste(paste, (0, 0), mask)

        # Add a direction arrow for mobs if necessary and secrets are shown
        if (self.show_secrets and
                cell.top in CC1.mobs() and cell.top != CC1.BLOCK):
            d = CC1.dirs(cell.top)
            arrow = self.get_sprite_copy(f"ARROW_{d}")
            tile_img.paste(arrow, (0, 0), arrow)

    def save_png(self, level, filename):
        """Create an 8x8 PNG image from a CC1Level and save it to file."""
        self.level_image(level).save(filename, format='png')

    def save_set_png(self, levelset, filename, *, levels_per_row=10, margin=8):
        """Create a large image containing all the level images in a set and
        save to file. """
        # pylint: disable=too-many-locals
        size = self.sprite_set.get_size_in_pixels()
        assert size == 8  # TODO: allow scaling other tile sets to 8x8
        n_levels = len(levelset.levels)
        width = levels_per_row * size * 32 + (levels_per_row + 1) * margin
        n_rows = math.ceil(n_levels / levels_per_row)
        height = n_rows * size * 32 + (n_rows + 1) * margin
        disp_img = Image.new("RGBA", (width, height), color="black")
        for i, level in enumerate(levelset.levels):
            level_img = self.level_image(level)
            lvl_x = i % levels_per_row
            lvl_y = i // levels_per_row
            x = lvl_x * (32 * size + margin) + margin
            y = lvl_y * (32 * size + margin) + margin
            disp_img.paste(level_img, (x, y))
        disp_img.save(filename, format='png')
