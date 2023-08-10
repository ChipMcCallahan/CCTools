"""Class that transforms CC1Levels"""
import copy
from enum import Enum
from .cc1 import CC1
from .cc1_cell import CC1Cell


class CC1LevelTransformer:
    """Class that transforms CC1Levels"""

    class Type(Enum):
        """Enum that represents allowed dihedral transformations of a CC1Level."""
        R90 = 1
        R180 = 2
        R270 = 3
        FLIP_HORIZONTAL = 4
        FLIP_VERTICAL = 5
        FLIP_NE_SW = 6
        FLIP_NW_SE = 7

    __xy_transformer = {
        Type.R90: lambda x, y: (31 - y, x),
        Type.R180: lambda x, y: (31 - x, 31 - y),
        Type.R270: lambda x, y: (y, 31 - x),
        Type.FLIP_VERTICAL: lambda x, y: (x, 31 - y),
        Type.FLIP_HORIZONTAL: lambda x, y: (31 - x, y),
        Type.FLIP_NE_SW: lambda x, y: (31 - y, 31 - x),
        Type.FLIP_NW_SE: lambda x, y: (y, x)
    }

    __element_transformer = {
        Type.R90: lambda e: e.right(),
        Type.R180: lambda e: e.reverse(),
        Type.R270: lambda e: e.left(),
        Type.FLIP_VERTICAL: lambda e: e.flip_vertical(),
        Type.FLIP_HORIZONTAL: lambda e: e.flip_horizontal(),
        Type.FLIP_NE_SW: lambda e: e.flip_ne_sw(),
        Type.FLIP_NW_SE: lambda e: e.flip_nw_se()
    }

    # pylint: disable=too-few-public-methods
    @staticmethod
    def __transform(level, _type):
        """Transform a CC1Level by various rules, but only if it does not contain CC1.PANEL_SE."""
        new_level = copy.deepcopy(level)
        if level.count(CC1.PANEL_SE) > 0:
            return new_level

        def transform(o):
            if isinstance(o, int):
                x, y = o % 32, o // 32
                nx, ny = CC1LevelTransformer.__xy_transformer[_type](x, y)
                return ny * 32 + nx
            return CC1LevelTransformer.__element_transformer[_type](o)

        for p in range(32 * 32):
            new_p = transform(p)
            cell = level.map[p]
            new_level.map[new_p] = CC1Cell(transform(cell.top), transform(cell.bottom))

        new_level.traps, new_level.cloners = {}, {}
        new_level.movement = []
        for k, v in level.traps.items():
            nk, nv = (transform(p) for p in (k, v))
            new_level.traps[nk] = nv
        for k, v in level.cloners.items():
            nk, nv = (transform(p) for p in (k, v))
            new_level.cloners[nk] = nv
        for p in level.movement:
            new_level.movement.append(transform(p))
        return new_level

    @staticmethod
    def rotate_90(level):
        """Rotate a CC1Level clockwise by 90 degrees, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.R90)

    @staticmethod
    def rotate_180(level):
        """Rotate a CC1Level clockwise by 180 degrees, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.R180)

    @staticmethod
    def rotate_270(level):
        """Rotate a CC1Level clockwise by 270 degrees, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.R270)

    @staticmethod
    def flip_horizontal(level):
        """Flip a CC1Level horizontally, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.FLIP_HORIZONTAL)

    @staticmethod
    def flip_vertical(level):
        """Flip a CC1Level vertically, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.FLIP_VERTICAL)

    @staticmethod
    def flip_ne_sw(level):
        """Flip a CC1Level along the NE/SW diagonal, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.FLIP_NE_SW)

    @staticmethod
    def flip_nw_se(level):
        """Flip a CC1Level along the NW/SE diagonal, if it does not contain SE panel."""
        return CC1LevelTransformer.__transform(level, CC1LevelTransformer.Type.FLIP_NW_SE)

    @staticmethod
    def replace(level, old, new):
        """Replace all CC1 elements in old with element new. Old may be CC1 element or iterable.
        New must be CC1 element. """
        level = copy.deepcopy(level)  # Do not modify original.
        assert isinstance(new, CC1), f"Expected CC1 element, got {new}."
        if isinstance(old, CC1):
            old = {old, }
        old = set(old)
        for p in range(32 * 32):
            here = level.map[p]
            for elem in old:
                if here.remove(elem):
                    here.add(new)
                elif elem is CC1.FLOOR:  # Since FLOOR is default, it never gets removed.
                    if here.top is CC1.FLOOR or here.top in CC1.mobs() and here.bottom is CC1.FLOOR:
                        here.add(new)
        return level

    @staticmethod
    def replace_mobs(level, old, new):
        """Replace all mobs in old with those in new, maintaining direction."""
        for d in "NESW":
            targets = {mob for mob in old if mob.name.endswith(f"_{d}")}
            replacements = tuple(mob for mob in new if mob.name.endswith(f"_{d}"))
            assert len(replacements) == 1, f"Expected only one matching mob for direction '{d}', " \
                                           f"found {replacements} "
            level = CC1LevelTransformer.replace(level, targets, replacements[0])
        return level

    @staticmethod
    def keep(level, elements_to_keep):
        """Erase everything except for specified elements."""
        level = copy.deepcopy(level)
        for p in range(32 * 32):
            here = level.map[p]
            present = {here.top, here.bottom}
            trash = present.difference(elements_to_keep)
            for item in trash:
                here.remove(item)
        return level
