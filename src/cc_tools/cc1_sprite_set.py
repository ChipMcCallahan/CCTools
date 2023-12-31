"""
Module: CC1 Sprite Set

This module provides the CC1SpriteSet class, which is designed for managing and rendering
sprites used in the Chip's Challenge 1 (CC1) game. The class facilitates loading sprite images,
applying transformations like colorization and rotation, and preparing them for use in game level
visualization.

The module utilizes PIL (Python Imaging Library) for image processing and manipulation,
allowing for the dynamic creation of game graphics based on sprite sets. It supports
loading sprite images from specified subdirectories within a package, handling different
sprite configurations (e.g., 8x8 pixel sprites), and providing utility methods for accessing
and manipulating these sprites.

Classes:
    CC1SpriteSet: Manages a collection of sprites for CC1 game levels. It provides methods
                  for loading, accessing, and manipulating sprite images.

Key Functionalities:
    - Sprite loading from files within a package directory.
    - Dynamic colorization of sprites to represent various game elements.
    - Support for different sprite sizes and transformations.
    - Utility methods for accessing and validating sprite sets.

Usage:
    This module is intended to be used in conjunction with other modules that handle the
    rendering and display of CC1 game levels, such as level editors, game engines, or
    visualization tools.

Example:
    Creating an instance of CC1SpriteSet and loading sprites from a specified directory:

    ```
    sprite_set = CC1SpriteSet(size_in_pixels=8)
    sprite_set.load_sprite_file("example_sprite.png")
    ```

Dependencies:
    - PIL (Python Imaging Library): For image processing and manipulation.
    - importlib.resources: For loading sprite files from within the package.
"""

import importlib.resources
from PIL import Image, ImageOps
from .cc1 import CC1

RED = "RED"
YELLOW = "YELLOW"
GREEN = "GREEN"
BLUE = "BLUE"
BROWN = "BROWN"

COLORS = {
    RED: "#FF0000",
    YELLOW: "#FFFF00",
    GREEN: "#00FF00",
    BLUE: "#0000FF",
    BROWN: "#A52A2A"
}


class CC1SpriteSet:
    """
    Class for managing a set of sprites used in CC1 (Chip's Challenge 1) game levels.

    This class loads and stores sprites from image files in a specified subdirectory,
    and provides methods to access and manipulate these sprites.

    Attributes:
        sprites (dict): A dictionary mapping sprite names to PIL Image objects.
        size_in_pixels (int): The pixel size for each sprite.
        show_secrets (bool): A flag to indicate whether to show secret elements.

    Methods:
        get_sprite: Retrieve a sprite by its name or corresponding CC1 enum.
        validate: Ensure all necessary sprites are loaded.
        set_transparency: Enable or disable sprite transparency.
        get_size_in_pixels: Get the size of sprites in pixels.
        load_sprite_file: Load an individual sprite from a file.
        factory_8x8: Static method to create an 8x8 pixel sprite set.
        available_sprite_sets: Static method to list available sprite sets.
        load_set_by_name: Static method to load a sprite set by name.
    """

    SHOW_SECRETS_MAP = {
        "BLOCK": "BLOCK_TRANSPARENT",
        "CLONE_BLOCK_N": "BLOCK_TRANSPARENT",
        "CLONE_BLOCK_E": "BLOCK_TRANSPARENT",
        "CLONE_BLOCK_S": "BLOCK_TRANSPARENT",
        "CLONE_BLOCK_W": "BLOCK_TRANSPARENT",
    }
    HIDE_SECRETS_MAP = {
        "BLUE_WALL_FAKE": "BLUE_WALL_REAL",
        "INV_WALL_PERM": "FLOOR",
        "INV_WALL_APP": "FLOOR"
    }

    def __init__(self, size_in_pixels):
        """
        Initializes the CC1SpriteSet.

        Args: size_in_pixels (int): Size of the sprites in pixels.
        """
        self.sprites = {}
        self.size_in_pixels = size_in_pixels
        self.show_secrets = True

    def get_sprite(self, lookup_key):
        """
        Retrieve a sprite image by its corresponding CC1 enum value or name.

        Args:
            lookup_key (CC1 Enum or str): The key to look up the sprite image.

        Returns:
            PIL.Image.Image: The corresponding sprite image.
        """
        name = lookup_key.name if isinstance(lookup_key, CC1) else lookup_key
        name = (
            CC1SpriteSet.SHOW_SECRETS_MAP.get(name, name)
            if self.show_secrets
            else CC1SpriteSet.HIDE_SECRETS_MAP.get(name, name)
        )

        return self.sprites[name]

    def validate(self):
        """
        Validates that all valid sprites required by the CC1 enum are loaded
        in the sprite set.

        Raises:
            ValueError: If any sprite required by the CC1 enum is missing.
        """
        missing = [e for e in CC1.valid() if e not in self.sprites]
        if missing:
            raise ValueError(f"Missing sprites for: {missing}")

    def set_show_secrets(self, value: bool):
        """
        Sets the show_secrets flag for the sprite set.

        Args:
            value (bool): True to enable showing secrets, False to disable.
        """
        self.show_secrets = value

    def get_size_in_pixels(self):
        """
        Gets the size of the sprites in pixels.

        Returns:
            int: The size of the sprites in pixels.
        """
        return self.size_in_pixels

    @staticmethod
    def __colorize(img, color):
        """
        Colorize an image while maintaining its transparency.

        Args:
            img (PIL.Image.Image): The image to be colorized.
            color (str): The color to apply to the image.

        Returns:
            PIL.Image.Image: The colorized image.
        """
        _, _, _, alpha = img.split()
        img_gray = ImageOps.grayscale(img)
        img_new = ImageOps.colorize(img_gray, "#00000000", COLORS.get(color))
        img_new.putalpha(alpha)
        return img_new

    @staticmethod
    def load_sprite_file(package, filename):
        """
        Load a sprite image from a file within the specified package.

        Args:
            package (str): The package path of the sprite image to load.
            filename (str): The filename of the sprite image to load.

        Returns:
            PIL.Image.Image: The loaded sprite image.
        """
        with importlib.resources.path(package, filename) as path:
            return Image.open(path)

    @staticmethod
    def factory_8x8():
        """
        Factory method to create a sprite set from the "8x8" set of sprites.

        Returns: CC1SpriteSet: A new instance of CC1SpriteSet with 8x8 pixel
        sprites.
        """
        spriteset = CC1SpriteSet(size_in_pixels=8)
        package = "cc_tools.art.8x8"
        try:
            # Use files() to get a Traversable object for the directory
            directory = importlib.resources.files(package)
            # Iterate over the directory contents
            image_files = [f.name for f in directory.iterdir() if
                           f.name.lower().endswith('.png')]
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Package '{package}' not "
                                    f"found or cannot be accessed.") from exc

        for image_file in image_files:
            prefix = image_file.split('.')[0]
            load = CC1SpriteSet.load_sprite_file
            spriteset.sprites[prefix] = load(package, image_file)
        colorize = CC1SpriteSet.__colorize
        for color in (RED, GREEN, BLUE, YELLOW):
            spriteset.sprites[f"{color}_KEY"] = colorize(
                spriteset.sprites["KEY"], color)
            spriteset.sprites[f"{color}_DOOR"] = colorize(
                spriteset.sprites["DOOR"], color)
        spriteset.sprites["CLONE_BUTTON"] = colorize(
            spriteset.sprites["BUTTON"], RED)
        spriteset.sprites["TRAP_BUTTON"] = colorize(
            spriteset.sprites["BUTTON"], BROWN)
        spriteset.sprites["GREEN_BUTTON"] = colorize(
            spriteset.sprites["BUTTON"], GREEN)
        spriteset.sprites["TANK_BUTTON"] = colorize(
            spriteset.sprites["BUTTON"], BLUE)

        # Rotate is unintuitively COUNTER clockwise.
        force = spriteset.sprites["FORCE_S"]
        spriteset.sprites["FORCE_E"] = force.rotate(90)
        spriteset.sprites["FORCE_N"] = force.rotate(180)
        spriteset.sprites["FORCE_W"] = force.rotate(270)
        for d in "NESW":
            spriteset.sprites[f"CLONE_BLOCK_{d}"] = spriteset.sprites["BLOCK"]
        floor = spriteset.sprites["FLOOR"].copy()
        h = spriteset.sprites["PANEL_HORIZONTAL"]
        v = spriteset.sprites["PANEL_VERTICAL"]
        spriteset.sprites["PANEL_N"] = floor.copy()
        spriteset.sprites["PANEL_N"].paste(h, (0, 0), h)
        spriteset.sprites["PANEL_E"] = floor.copy()
        spriteset.sprites["PANEL_E"].paste(v, (6, 0), v)
        spriteset.sprites["PANEL_S"] = floor.copy()
        spriteset.sprites["PANEL_S"].paste(h, (0, 6), h)
        spriteset.sprites["PANEL_W"] = floor.copy()
        spriteset.sprites["PANEL_W"].paste(v, (0, 0), v)

        # Rotate is unintuitively COUNTER clockwise.
        arrow = spriteset.sprites["ARROW_E"]
        spriteset.sprites["ARROW_N"] = arrow.rotate(90)
        spriteset.sprites["ARROW_W"] = arrow.rotate(180)
        spriteset.sprites["ARROW_S"] = arrow.rotate(270)
        return spriteset

    @staticmethod
    def make_transparent(image, colors):
        """
        Makes specified colors in a PIL Image object transparent.

        Args: image (PIL.Image.Image): The image to process. colors (list or
        tuple): A list or tuple of color values to make transparent. Each
        color should be in the format (R, G, B) or (R, G, B, A).

        Returns:
        PIL.Image.Image: A new image with specified colors made transparent.
        """

        # Ensure image is in RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Create a new image for output
        new_image = Image.new('RGBA', image.size)
        width, height = image.size

        # Iterate through each pixel
        for x in range(width):
            for y in range(height):
                current_color = image.getpixel((x, y))

                # Check if the current color matches any in the list
                if current_color[:3] in [color[:3] for color in colors]:
                    # Make transparent
                    new_image.putpixel((x, y), (0, 0, 0, 0))
                else:
                    # Copy pixel
                    new_image.putpixel((x, y), current_color)

        return new_image

    @staticmethod
    def create_transparent_image(white_tile, black_tile):
        """
        Creates a transparent image from two tiles: one on a white background and one on a black background.
        Any pixel that is white in the white image and black in the black image becomes transparent.

        Args:
            white_tile (PIL.Image.Image): The tile image on a white background.
            black_tile (PIL.Image.Image): The tile image on a black background.

        Returns:
            PIL.Image.Image: A new image with specified pixels made transparent.
        """

        # Ensure both images are in RGBA mode
        white_tile = white_tile.convert("RGBA")
        black_tile = black_tile.convert("RGBA")

        width, height = white_tile.size
        transparent_img = Image.new("RGBA", (width, height))

        for y in range(height):
            for x in range(width):
                white_pixel = white_tile.getpixel((x, y))
                black_pixel = black_tile.getpixel((x, y))

                # Check if the pixel is white in white_tile and black in black_tile
                if white_pixel[:3] == (255, 255, 255) and black_pixel[:3] == (
                0, 0, 0):
                    # Make the pixel fully transparent
                    alpha = 0
                else:
                    # Keep the pixel from the white_tile and fully opaque
                    alpha = 255

                new_pixel = (*white_pixel[:3], alpha)
                transparent_img.putpixel((x, y), new_pixel)

        return transparent_img

    @staticmethod
    def factory(filename):
        """
        Factory method to create a sprite set from any standardized MSCC
        bmp which uses magenta for transparency.

        Returns: CC1SpriteSet: A new instance of CC1SpriteSet with 8x8 pixel
        sprites.
        """
        mscc = filename in ["mscc.bmp"]
        subdir = "mscc" if mscc else "tw"

        raw = CC1SpriteSet.load_sprite_file(f"cc_tools.art.{subdir}", filename)

        raw = CC1SpriteSet.make_transparent(
            raw, [(255, 0, 255)]
        ) if raw.mode != 'RGBA' and not mscc else raw

        width, height = raw.size
        assert (height % 16 == 0)
        size = height // 16

        def tile(x_index, y_index):
            i, j = x_index * size, y_index * size
            return raw.crop((i, j, i + size, j + size))

        spriteset = CC1SpriteSet(size_in_pixels=size)
        for index, elem in enumerate(CC1):
            x, y = index // 16, index % 16
            if mscc and x > 3:
                white_tile = tile(x + 3, y)
                black_tile = tile(x + 6, y)
                spriteset.sprites[
                    elem.name] = CC1SpriteSet.create_transparent_image(
                    white_tile,
                    black_tile)
            else:
                spriteset.sprites[elem.name] = tile(x, y)
        return spriteset

    @staticmethod
    def available_sprite_sets():
        """
        Lists the available sprite sets.

        Returns: dict: A dictionary of available sprite sets with their
        names as keys.
        """
        return ["8x8", "felix32", "steam32", "lynx_for_twms48",
                "silly_world_ms48", "tileworld48", "mscc"]

    @staticmethod
    def load_set_by_name(name):
        """
        Load a sprite set by its name.

        Args:
            name (str): The name of the sprite set to load.

        Returns:
            CC1SpriteSet: The loaded sprite set.

        Raises: ValueError: If the given name does not correspond to any
        available sprite set.
        """
        if name == "8x8":
            return CC1SpriteSet.factory_8x8()
        elif name in ["steam32", "lynx_for_twms48",
                      "silly_world_ms48", "tileworld48"]:
            return CC1SpriteSet.factory(f"{name}.bmp")
        elif name in ["felix32"]:
            return CC1SpriteSet.factory(f"{name}.png")
        elif name in ["mscc"]:
            return CC1SpriteSet.factory(f"mscc.bmp")
        raise ValueError(f"{name} not a valid sprite set name")
