"""Class that creates images of CC1Levels"""
import math

from PIL import Image

from cc_tools.cc1_sprite_set import CC1SpriteSet


class CC1LevelImager:
    """Class that creates images of CC1Levels"""

    # pylint: disable=too-few-public-methods
    def __init__(self, sprite_set_name="8x8"):
        self.sprite_set = CC1SpriteSet.load_set_by_name(sprite_set_name)

    def __get_image(self, cc1_elem):
        """Get associated image for a CC1 element."""
        return self.sprite_set.get_sprite(cc1_elem.name).copy()

    def image8(self, cc1level):
        """Create an 8x8 PNG image from a CC1Level."""
        map_img = Image.new("RGBA", (32 * 8, 32 * 8))
        for i in range(32):
            for j in range(32):
                cell = cc1level.map[j * 32 + i]
                tile_img = self.__get_image(cell.bottom)
                if cell.top != cell.bottom:
                    paste = self.__get_image(cell.top)
                    tile_img.paste(paste, (0, 0), paste)
                map_img.paste(tile_img, (i * 8, j * 8))
        return map_img

    def save_png(self, level, filename):
        """Create an 8x8 PNG image from a CC1Level and save it to file."""
        self.image8(level).save(filename, format='png')

    def save_set_png(self, levelset, filename, *, levels_per_row=10, margin=8):
        """Create a large image containing all the level images in a set and save to file."""
        # pylint: disable=too-many-locals
        n_levels = len(levelset.levels)
        width = levels_per_row * 8 * 32 + (levels_per_row + 1) * margin
        n_rows = math.ceil(n_levels / levels_per_row)
        height = n_rows * 8 * 32 + (n_rows + 1) * margin
        disp_img = Image.new("RGBA", (width, height), color="black")
        for i, level in enumerate(levelset.levels):
            level_img = self.image8(level)
            lvl_x = i % levels_per_row
            lvl_y = i // levels_per_row
            x = lvl_x * (32 * 8 + margin) + margin
            y = lvl_y * (32 * 8 + margin) + margin
            disp_img.paste(level_img, (x, y))
        disp_img.save(filename, format='png')
