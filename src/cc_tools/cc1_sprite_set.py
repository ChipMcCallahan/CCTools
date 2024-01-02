"""
Module: CC1 Sprite Set

This module provides the CC1SpriteSet class, which is designed for managing
and rendering sprites used in the Chip's Challenge 1 (CC1) game. The class
facilitates loading sprite images, applying transformations like colorization
and rotation, and preparing them for use in game level visualization.

The module utilizes PIL (Python Imaging Library) for image processing and
manipulation, allowing for the dynamic creation of game graphics based on
sprite sets. It supports loading sprite images from specified subdirectories
within a package, handling different sprite configurations (e.g., 8x8 pixel
sprites), and providing utility methods for accessing and manipulating these
sprites.

Classes: CC1SpriteSet: Manages a collection of sprites for CC1 game levels.
It provides methods for loading, accessing, and manipulating sprite images.

Key Functionalities:
    - Sprite loading from files within a package directory.
    - Dynamic colorization of sprites to represent various game elements.
    - Support for different sprite sizes and transformations.
    - Utility methods for accessing and validating sprite sets.

Usage: This module is intended to be used in conjunction with other modules
that handle the rendering and display of CC1 game levels, such as level
editors, game engines, or visualization tools.

Dependencies:
    - PIL (Python Imaging Library): For image processing and manipulation.
    - importlib.resources: For loading sprite files from within the package.
"""

import importlib.resources
from .cc1 import CC1
from .img_utils import RED, GREEN, BLUE, YELLOW, colorize, BROWN, \
    make_transparent, apply_alpha_mask, load_sprite_file


class CC1SpriteSet:
    """
    Class for managing a set of sprites used in CC1 (Chip's Challenge 1) game
    levels.

    This class loads and stores sprites from image files in a specified
    subdirectory, and provides methods to access and manipulate these sprites.
    """

    def __init__(self, size_in_pixels):
        self.sprites = {}
        self.size_in_pixels = size_in_pixels

    def get_sprite(self, lookup_key):
        """
        Retrieve a sprite image by its corresponding CC1 enum value or name.
        """
        name = lookup_key.name if isinstance(lookup_key, CC1) else lookup_key
        return self.sprites[name]

    def get_size_in_pixels(self):
        """Gets the size of the sprites in pixels."""
        return self.size_in_pixels

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
            spriteset.sprites[prefix] = load_sprite_file(package, image_file)
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

        for elem in CC1:
            if elem.name not in spriteset.sprites:
                spriteset.sprites[elem.name] = spriteset.sprites["HINT"]
        return spriteset

    @staticmethod
    def factory(filename):
        """
        Factory method to create a sprite set from any standardized MSCC
        bmp which uses magenta for transparency.

        Returns: CC1SpriteSet: A new instance of CC1SpriteSet with 8x8 pixel
        sprites.
        """
        raw = load_sprite_file("cc_tools.art.tw", filename)

        width, height = raw.size
        assert height % 16 == 0
        size = height // 16
        mscc = width == size * 13

        if not mscc:
            r, g, b, a = raw.getpixel((width - 1, 0)) # top right pixel
            if a != 0: # not transparent
                raw = make_transparent(raw, [(r, g, b)])

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
                    elem.name] = apply_alpha_mask(
                    white_tile,
                    black_tile)
            else:
                spriteset.sprites[elem.name] = tile(x, y)

        return spriteset

    @staticmethod
    def create_sprite_sets():
        """Create all available sprite sets and return as dict."""
        package = 'cc_tools.art.tw'
        sprite_sets = {}

        directory = importlib.resources.files(package)
        # Iterate over the directory contents
        for file in directory.iterdir():
            # 'stem' gives the filename without the extension
            filename_without_extension = file.stem
            # Call the factory function for each file
            sprite_set = CC1SpriteSet.factory(file.name)
            sprite_sets[filename_without_extension] = sprite_set

        sprite_sets["8x8"] = CC1SpriteSet.factory_8x8()
        return sprite_sets
