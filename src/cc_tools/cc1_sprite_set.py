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
    sprite_set = CC1SpriteSet(size_in_pixels=8, subdirectory="path/to/sprites")
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
        package (str): The package directory from which sprites are loaded.

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

    def __init__(self, size_in_pixels, subdirectory):
        """
        Initializes the CC1SpriteSet with sprites of a specified size from a
        given subdirectory.

        Args: size_in_pixels (int): Size of the sprites in pixels.
        subdirectory (str): Subdirectory within the package containing the
        sprite images.
        """
        self.sprites = {}
        self.size_in_pixels = size_in_pixels
        self.show_secrets = True
        self.package = f"cc_tools.art.{subdirectory}"

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

    def load_sprite_file(self, filename):
        """
        Load a sprite image from a file within the specified package.

        Args:
            filename (str): The filename of the sprite image to load.

        Returns:
            PIL.Image.Image: The loaded sprite image.
        """
        with importlib.resources.path(self.package, filename) as path:
            return Image.open(path)

    @staticmethod
    def factory_8x8():
        """
        Factory method to create a sprite set with 8x8 pixel sprites.

        Returns: CC1SpriteSet: A new instance of CC1SpriteSet with 8x8 pixel
        sprites.
        """
        spriteset = CC1SpriteSet(size_in_pixels=8, subdirectory="8x8")
        try:
            # Use files() to get a Traversable object for the directory
            directory = importlib.resources.files(spriteset.package)
            # Iterate over the directory contents
            image_files = [f.name for f in directory.iterdir() if
                           f.name.lower().endswith('.png')]
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Package '{spriteset.package}' not "
                                    f"found or cannot be accessed.") from exc

        spriteset.sprites = {}
        for image_file in image_files:
            prefix = image_file.split('.')[0]
            spriteset.sprites[prefix] = spriteset.load_sprite_file(image_file)
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
    def available_sprite_sets():
        """
        Lists the available sprite sets.

        Returns: dict: A dictionary of available sprite sets with their
        names as keys.
        """
        return {"8x8": CC1SpriteSet.factory_8x8()}

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
        raise ValueError(f"{name} not a valid sprite set name")
