"""Class that creates images of CC1Levels"""
import importlib.resources
import math

from PIL import Image, ImageOps


class CC1LevelImager:
    """Class that creates images of CC1Levels"""

    # pylint: disable=too-few-public-methods
    def __init__(self):
        # base_path = "https://raw.githubusercontent.com/ChipMcCallahan/CCTools/main/art/8x8/"
        image_files = [
            "ant_e_8.png",
            "ant_n_8.png",
            "ant_s_8.png",
            "ant_w_8.png",
            "ball_e_8.png",
            "ball_n_8.png",
            "ball_s_8.png",
            "ball_w_8.png",
            "blob_e_8.png",
            "blob_n_8.png",
            "blob_s_8.png",
            "blob_w_8.png",
            "block_8.png",
            "block_transparent_8.png",
            "blue_wall_fake_8.png",
            "blue_wall_real_8.png",
            "bomb_8.png",
            "button_8.png",
            "chip_8.png",
            "cloner_8.png",
            "dirt_8.png",
            "door_8.png",
            "exit_8.png",
            "fire_8.png",
            "fire_boots_8.png",
            "fireball_e_8.png",
            "fireball_n_8.png",
            "fireball_s_8.png",
            "fireball_w_8.png",
            "flippers_8.png",
            "floor_8.png",
            "force_random_8.png",
            "force_s_8.png",
            "glider_e_8.png",
            "glider_n_8.png",
            "glider_s_8.png",
            "glider_w_8.png",
            "gravel_8.png",
            "hint_8.png",
            "ice_8.png",
            "ice_ne_8.png",
            "ice_nw_8.png",
            "ice_se_8.png",
            "ice_sw_8.png",
            "inv_wall_app_8.png",
            "inv_wall_perm_8.png",
            "key_8.png",
            "panel_horizontal_8.png",
            "panel_se_8.png",
            "panel_vertical_8.png",
            "paramecium_e_8.png",
            "paramecium_n_8.png",
            "paramecium_s_8.png",
            "paramecium_w_8.png",
            "player_e_8.png",
            "player_n_8.png",
            "player_s_8.png",
            "player_w_8.png",
            "pop_up_wall_8.png",
            "skates_8.png",
            "socket_8.png",
            "suction_boots_8.png",
            "tank_e_8.png",
            "tank_n_8.png",
            "tank_s_8.png",
            "tank_w_8.png",
            "teeth_e_8.png",
            "teeth_n_8.png",
            "teeth_s_8.png",
            "teeth_w_8.png",
            "teleport_8.png",
            "thief_8.png",
            "toggle_floor_8.png",
            "toggle_wall_8.png",
            "trap_8.png",
            "walker_e_8.png",
            "walker_n_8.png",
            "walker_s_8.png",
            "walker_w_8.png",
            "wall_8.png",
            "water_8.png"
        ]
        self.images = {}
        for image_file in image_files:
            prefix = image_file.split('.')[0]
            self.images[prefix] = self.__load_img(image_file)
        colorize = CC1LevelImager.__colorize
        for color in ("red", "green", "blue", "yellow"):
            self.images[f"{color}_key_8"] = colorize(self.images["key_8"], color)
            self.images[f"{color}_door_8"] = colorize(self.images["door_8"], color)
        self.images["clone_button_8"] = colorize(self.images["button_8"], "red")
        self.images["trap_button_8"] = colorize(self.images["button_8"], "red")
        self.images["green_button_8"] = colorize(self.images["button_8"], "green")
        self.images["tank_button_8"] = colorize(self.images["button_8"], "blue")
        force = self.images["force_s_8"]
        self.images["force_e_8"] = force.rotate(90)
        self.images["force_n_8"] = force.rotate(180)
        self.images["force_w_8"] = force.rotate(270)
        for d in "nesw":
            self.images[f"clone_block_{d}_8"] = self.images["block_8"]
        floor = self.images["floor_8"].copy()
        h = self.images["panel_horizontal_8"]
        v = self.images["panel_vertical_8"]
        self.images["panel_n_8"] = floor.copy()
        self.images["panel_n_8"].paste(h, (0, 0), h)
        self.images["panel_e_8"] = floor.copy()
        self.images["panel_e_8"].paste(v, (6, 0), v)
        self.images["panel_s_8"] = floor.copy()
        self.images["panel_s_8"].paste(h, (0, 6), h)
        self.images["panel_w_8"] = floor.copy()
        self.images["panel_w_8"].paste(v, (0, 0), v)

    @staticmethod
    def __load_img(filename):
        file_path = importlib.resources.files('cc_tools.art.8x8') / filename

        # Directly open the image using PIL
        with Image.open(file_path) as img:
            # Check if the image is already in PNG format
            if img.format != 'PNG':
                raise ValueError("Image is not in PNG format.")
            return img.copy()

    @staticmethod
    def __colorize(img, color):
        """Colorize an image, maintaining transparency."""
        colors = {"red": "#FF0000", "yellow": "#FFFF00", "green": "#00FF00", "blue": "#0000FF",
                  "brown": "#A52A2A"}
        _, _, _, alpha = img.split()
        img_gray = ImageOps.grayscale(img)
        img_new = ImageOps.colorize(img_gray, "#00000000", colors[color])
        img_new.putalpha(alpha)
        return img_new

    def __get_image(self, cc1_elem):
        """Get associated image for a CC1 element."""
        image_key = cc1_elem.name.lower() + "_8"
        if image_key in self.images:
            return self.images[image_key].copy()  # important to not corrupt base image!
        return self.images["wall_8"].copy()  # If image is not found (invalid tile?) return wall.

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
