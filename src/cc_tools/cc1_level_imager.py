"""Class that creates images of CC1Levels"""
import math

from PIL import Image

from cc_tools import CC1
from cc_tools.cc1_sprite_set import CC1SpriteSet
from cc_tools.img_utils import draw_red_line, add_text_label_to_image, \
    make_semi_transparent, lighten_image, draw_directional_arrow


class CC1LevelImager:
    """Class that creates images of CC1Levels"""

    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.sprite_sets = CC1SpriteSet.create_sprite_sets()
        self.sprite_set_name = "default"
        self.sprite_set = self.sprite_sets[self.sprite_set_name]
        self.show_secrets = None
        self.set_show_secrets(True)
        self.show_connections = None
        self.set_show_connections(True)
        self.show_monster_order = None
        self.set_show_monster_order(True)

        self.arrows = {}
        sizes = [s.get_size_in_pixels() for s in self.sprite_sets.values()]
        for s in sizes:
            for d in "NESW":
                self.arrows[f"ARROW_{s}_{d}"] = draw_directional_arrow(s, d)

    def set_sprite_set(self, sprite_set_name):
        """Set the sprite set to use for level imaging."""
        self.sprite_set_name = sprite_set_name
        self.sprite_set = self.sprite_sets[sprite_set_name]

    def get_sprite_copy(self, cc1_elem):
        """Get copy of associated image for a CC1 element."""
        return self.sprite_set.get_sprite(cc1_elem).copy()

    def set_show_secrets(self, show_secrets):
        """Set the show_secrets boolean on self and CC1SpriteSet."""
        self.show_secrets = show_secrets

    def set_show_connections(self, show_connections):
        """Set the show_connections boolean."""
        self.show_connections = show_connections

    def set_show_monster_order(self, show_monster_order):
        """Set the show_monster_order boolean."""
        self.show_monster_order = show_monster_order

    def level_image(self, cc1level):
        """Create an 8x8 PNG image from a CC1Level."""
        size = self.sprite_set.get_size_in_pixels()
        map_img = Image.new("RGBA", (32 * size, 32 * size))

        for j in range(32):
            for i in range(32):
                cell = cc1level.map[j * 32 + i]
                tile_img = self.get_sprite_copy(cell.bottom)

                # If the top layer is different from the bottom, process it.
                if cell.top != cell.bottom:
                    self.process_top_layer(cell, tile_img)

                if self.show_monster_order and size >= 32:
                    # Draw the monster order as a number.
                    p = i + j * 32
                    scale = size / 32
                    if p in cc1level.movement:
                        index = str(cc1level.movement.index(p))
                        tile_img = add_text_label_to_image(tile_img, index,
                                                           (30 * scale,
                                                            20 * scale))

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
        top_img = self.get_sprite_copy(cell.top).convert('RGBA')
        if self.show_secrets and cell.top in CC1.blocks():
            # TODO: cache this.
            top_img = make_semi_transparent(top_img)

        if self.show_secrets and cell.top == CC1.BLUE_WALL_FAKE:
            top_img = lighten_image(top_img, 40)  # increase brightness by N %

        tile_img.paste(top_img, (0, 0), top_img)

        # Handle direction arrows and block transparency
        if self.show_secrets and cell.top in CC1.mobs():
            d = CC1.dirs(cell.top)
            if d:
                size = self.sprite_set.get_size_in_pixels()
                arrow = self.arrows[f"ARROW_{size}_{d}"]
                tile_img.paste(arrow, (0, 0), arrow)

    def save_png(self, level, filename):
        """Create an image from a CC1Level and save it to file."""
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
