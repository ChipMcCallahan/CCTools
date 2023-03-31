"""Enumeration of tile codes used in CC1 DAT files, and associated utils."""
import copy
import io
import math
from enum import Enum
import requests
from PIL import Image, ImageOps


class CC1(Enum):
    """Enumeration of tile codes used in CC1 DAT files, and associated utils."""
    # pylint: disable=too-many-public-methods
    FLOOR = 0
    WALL = 1
    CHIP = 2
    WATER = 3
    FIRE = 4
    INV_WALL_PERM = 5
    PANEL_N = 6
    PANEL_W = 7
    PANEL_S = 8
    PANEL_E = 9
    BLOCK = 10
    DIRT = 11
    ICE = 12
    FORCE_S = 13
    CLONE_BLOCK_N = 14
    CLONE_BLOCK_W = 15
    CLONE_BLOCK_S = 16
    CLONE_BLOCK_E = 17
    FORCE_N = 18
    FORCE_E = 19
    FORCE_W = 20
    EXIT = 21
    BLUE_DOOR = 22
    RED_DOOR = 23
    GREEN_DOOR = 24
    YELLOW_DOOR = 25
    ICE_SE = 26
    ICE_SW = 27
    ICE_NW = 28
    ICE_NE = 29
    BLUE_WALL_FAKE = 30
    BLUE_WALL_REAL = 31
    NOT_USED_0 = 32
    THIEF = 33
    SOCKET = 34
    GREEN_BUTTON = 35
    CLONE_BUTTON = 36
    TOGGLE_WALL = 37
    TOGGLE_FLOOR = 38
    TRAP_BUTTON = 39
    TANK_BUTTON = 40
    TELEPORT = 41
    BOMB = 42
    TRAP = 43
    INV_WALL_APP = 44
    GRAVEL = 45
    POP_UP_WALL = 46
    HINT = 47
    PANEL_SE = 48
    CLONER = 49
    FORCE_RANDOM = 50
    DROWN_CHIP = 51
    BURNED_CHIP0 = 52
    BURNED_CHIP1 = 53
    NOT_USED_1 = 54
    NOT_USED_2 = 55
    NOT_USED_3 = 56
    CHIP_EXIT = 57
    UNUSED_EXIT_0 = 58
    UNUSED_EXIT_1 = 59
    CHIP_SWIMMING_N = 60
    CHIP_SWIMMING_W = 61
    CHIP_SWIMMING_S = 62
    CHIP_SWIMMING_E = 63
    ANT_N = 64
    ANT_W = 65
    ANT_S = 66
    ANT_E = 67
    FIREBALL_N = 68
    FIREBALL_W = 69
    FIREBALL_S = 70
    FIREBALL_E = 71
    BALL_N = 72
    BALL_W = 73
    BALL_S = 74
    BALL_E = 75
    TANK_N = 76
    TANK_W = 77
    TANK_S = 78
    TANK_E = 79
    GLIDER_N = 80
    GLIDER_W = 81
    GLIDER_S = 82
    GLIDER_E = 83
    TEETH_N = 84
    TEETH_W = 85
    TEETH_S = 86
    TEETH_E = 87
    WALKER_N = 88
    WALKER_W = 89
    WALKER_S = 90
    WALKER_E = 91
    BLOB_N = 92
    BLOB_W = 93
    BLOB_S = 94
    BLOB_E = 95
    PARAMECIUM_N = 96
    PARAMECIUM_W = 97
    PARAMECIUM_S = 98
    PARAMECIUM_E = 99
    BLUE_KEY = 100
    RED_KEY = 101
    GREEN_KEY = 102
    YELLOW_KEY = 103
    FLIPPERS = 104
    FIRE_BOOTS = 105
    SKATES = 106
    SUCTION_BOOTS = 107
    PLAYER_N = 108
    PLAYER_W = 109
    PLAYER_S = 110
    PLAYER_E = 111

    def dirs(self):
        """Return the cardinal direction(s) associated with this element."""
        suffix = self.name.rsplit('_', maxsplit=1)[-1]
        return suffix if suffix in ("N", "E", "S", "W", "NE", "NW", "SE", "SW") else ""

    def with_dirs(self, dirs):
        """Returns the same element but with the cardinal direction(s) replaced by {dirs} if
        possible. Throws if invalid operation."""
        if dirs not in ("", "N", "E", "S", "W", "NE", "NW", "SE", "SW"):
            raise ValueError(f"illegal direction(s) specified: {dirs}")
        if len(self.dirs()) != len(dirs):
            raise ValueError(f"lengths unequal: self: {len(self.dirs())} vs given: {dirs}")
        if len(dirs) == 0:
            return self
        return CC1[self.name[:-len(dirs)] + dirs]

    def right(self):
        """Rotate to the right."""
        if len(self.dirs()) == 0 or self == CC1.PANEL_SE:
            return self
        new_dirs = ""
        for d in self.dirs():
            # Build the string backwards so "NE" becomes "SE" instead of "ES"
            new_dirs = "NESW"[("NESW".index(d) + 1) % 4] + new_dirs
        return self.with_dirs(new_dirs)

    def reverse(self):
        """Reverse direction."""
        return self.right().right()

    def left(self):
        """Rotate to the left."""
        return self.right().right().right()

    def flip_horizontal(self):
        """Flip horizontal."""
        if self in CC1.mobs() and self.dirs() in "EW":
            return self.reverse()
        if self in CC1.ice():
            return self.left() if self in (CC1.ICE_NE, CC1.ICE_SW) else self.right()
        return self

    def flip_vertical(self):
        """Flip vertical."""
        if self in CC1.mobs() and self.dirs() in "NS":
            return self.reverse()
        if self in CC1.ice():
            return self.left() if self in (CC1.ICE_NW, CC1.ICE_SE) else self.right()
        return self

    def flip_ne_sw(self):
        """Flip along diagonal from NE to SW."""
        if self in (CC1.ICE_NW, CC1.ICE_SE):
            return self.reverse()
        if self in CC1.mobs():
            return self.left() if self.dirs() in "EW" else self.right()
        return self

    def flip_nw_se(self):
        """Flip along diagonal from NW to SE."""
        if self in (CC1.ICE_NE, CC1.ICE_SW):
            return self.reverse()
        if self in CC1.mobs():
            return self.left() if self.dirs() in "NS" else self.right()
        return self

    @classmethod
    def __compass(cls, prefix):
        return {cls[prefix + "_" + d] for d in "NESW"}

    @classmethod
    def all(cls):
        """The set of all CC1 tile codes."""
        return set(cls)

    @classmethod
    def invalid(cls):
        """The set of all invalid CC1 tiles."""
        return {cls.NOT_USED_0, cls.DROWN_CHIP, cls.BURNED_CHIP0, cls.BURNED_CHIP1, cls.NOT_USED_1,
                cls.NOT_USED_2, cls.NOT_USED_3, cls.CHIP_EXIT, cls.UNUSED_EXIT_0, cls.UNUSED_EXIT_1,
                cls.CHIP_SWIMMING_N, cls.CHIP_SWIMMING_E, cls.CHIP_SWIMMING_S, cls.CHIP_SWIMMING_W}

    @classmethod
    def valid(cls):
        """The set of all valid CC1 tiles."""
        return cls.all().difference(cls.invalid())

    @classmethod
    def ice(cls):
        """The set of all CC1 ice and ice corner tiles."""
        return {cls.ICE}.union({cls["ICE_" + d] for d in ("NE", "NW", "SE", "SW")})

    @classmethod
    def forces(cls):
        """The set of all CC1 force floor tiles."""
        return {cls.FORCE_RANDOM}.union(cls.__compass("FORCE"))

    @classmethod
    def walls(cls):
        """The set of all CC1 wall tiles."""
        return {cls.WALL, cls.INV_WALL_PERM, cls.INV_WALL_APP, cls.BLUE_WALL_REAL}

    @classmethod
    def panels(cls):
        """The set of all CC1 panel (thin wall) tiles."""
        return {cls.PANEL_SE}.union(cls.__compass("PANEL"))

    @classmethod
    def clone_blocks(cls):
        """The set of all CC1 clone block tiles."""
        return cls.__compass("CLONE_BLOCK")

    @classmethod
    def blocks(cls):
        """The set of all CC1 block and clone block tiles."""
        return cls.clone_blocks().union({cls.BLOCK})

    @classmethod
    def players(cls):
        """The set of all CC1 player tiles."""
        return cls.__compass("PLAYER")

    @classmethod
    def ants(cls):
        """The set of all CC1 ant (spider) tiles."""
        return cls.__compass("ANT")

    @classmethod
    def paramecia(cls):
        """The set of all CC1 paramecium tiles."""
        return cls.__compass("PARAMECIUM")

    @classmethod
    def gliders(cls):
        """The set of all CC1 glider tiles."""
        return cls.__compass("GLIDER")

    @classmethod
    def fireballs(cls):
        """The set of all CC1 fireball tiles."""
        return cls.__compass("FIREBALL")

    @classmethod
    def tanks(cls):
        """The set of all CC1 tank tiles."""
        return cls.__compass("TANK")

    @classmethod
    def balls(cls):
        """The set of all CC1 ball tiles."""
        return cls.__compass("BALL")

    @classmethod
    def walkers(cls):
        """The set of all CC1 walker tiles."""
        return cls.__compass("WALKER")

    @classmethod
    def teeth(cls):
        """The set of all CC1 teeth tiles."""
        return cls.__compass("TEETH")

    @classmethod
    def blobs(cls):
        """The set of all CC1 blob tiles."""
        return cls.__compass("BLOB")

    @classmethod
    def monsters(cls):
        """The set of all CC1 monster tiles."""
        return set().union(cls.gliders(),
                           cls.ants(),
                           cls.paramecia(),
                           cls.fireballs(),
                           cls.teeth(),
                           cls.tanks(),
                           cls.blobs(),
                           cls.walkers(),
                           cls.balls())

    @classmethod
    def mobs(cls):
        """The set of all CC1 monster, block, and player tiles."""
        return set().union(cls.monsters(), cls.blocks(), cls.players())

    @classmethod
    def nonmobs(cls):
        """The set of all CC1 tiles that are not monsters, blocks, and players."""
        return cls.all().difference(cls.mobs())

    @classmethod
    def doors(cls):
        """The set of all CC1 door tiles."""
        return {cls.RED_DOOR, cls.GREEN_DOOR, cls.YELLOW_DOOR, cls.BLUE_DOOR}

    @classmethod
    def keys(cls):
        """The set of all CC1 key tiles."""
        return {cls.RED_KEY, cls.GREEN_KEY, cls.YELLOW_KEY, cls.BLUE_KEY}

    @classmethod
    def boots(cls):
        """The set of all CC1 boot tiles."""
        return {cls.SKATES, cls.SUCTION_BOOTS, cls.FIRE_BOOTS, cls.FLIPPERS}

    @classmethod
    def pickups(cls):
        """The set of all CC1 boot, key, and chip tiles."""
        return set.union(cls.boots(), cls.keys(), {cls.CHIP})

    @classmethod
    def buttons(cls):
        """The set of all CC1 button tiles."""
        return {cls.GREEN_BUTTON, cls.TRAP_BUTTON, cls.CLONE_BUTTON, cls.TANK_BUTTON}

    @classmethod
    def toggles(cls):
        """The set of all CC1 toggle tiles."""
        return {cls.TOGGLE_WALL, cls.TOGGLE_FLOOR}


class CC1Cell:
    """Class that represents a single CC1 cell with a top and bottom element."""

    def __init__(self, top=CC1.FLOOR, bottom=CC1.FLOOR):
        self.top, self.bottom = top, bottom

    def __copy__(self):
        return CC1Cell(self.top, self.bottom)

    def __eq__(self, other):
        return (self.top, self.bottom) == (other.top, other.bottom)

    def __str__(self):
        return f"{{CC1Cell top={self.top} bottom={self.bottom}}}"

    def is_valid(self):
        """Check if this cell is invalid due to illegal buried tiles or invalid codes."""
        buried = (self.top not in CC1.mobs() and self.bottom != CC1.FLOOR)
        invalid_code = len({self.top, self.bottom}.intersection(CC1.invalid())) > 0
        buried_mob = self.bottom in CC1.mobs()
        return not (buried or invalid_code or buried_mob)

    def contains(self, elem):
        """Returns true if elem is present in cell.top or cell.bottom."""
        return elem in {self.top, self.bottom}

    def add(self, elem):
        """Intelligently add a CC1 tile here, maintaining validity."""
        is_mob = elem in CC1.mobs()
        mob_here = self.top in CC1.mobs()
        if is_mob:
            # If adding mob to terrain, move the terrain to the bottom layer.
            if not mob_here:
                self.bottom = self.top
            self.top = elem
        else:
            if mob_here:
                # If adding terrain where a mob exists, replace the terrain but not the mob.
                self.bottom = elem
            else:
                self.top = elem

    def remove(self, elem):
        """Intelligently remove a CC1 tile here, maintaining validity. Returns True if cell was
        altered, False if not."""
        if elem == CC1.FLOOR:
            # Floor is default. It can never be removed.
            return False
        if elem == self.top:
            self.top = self.bottom
            self.bottom = CC1.FLOOR
            return True
        if elem == self.bottom:
            self.bottom = CC1.FLOOR
            return True
        return False

    def erase(self):
        """Clear cell by setting top and bottom layers to floor."""
        self.top = CC1.FLOOR
        self.bottom = CC1.FLOOR


class CC1Level:
    """Class that represents a CC1 level."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parsed=None):
        self.title = parsed.title if parsed else "Untitled"
        self.time = parsed.time if parsed else 0
        self.chips = parsed.chips if parsed else 0
        self.hint = parsed.hint if parsed else ""
        self.password = parsed.password if parsed else ""
        self.map = []
        for i in range(32 * 32):
            cell = CC1Cell()
            if parsed:
                cell.top, cell.bottom = (CC1(integer) for integer in parsed.map[i])
            self.map.append(cell)
        self.traps = {t[0]: t[1] for t in parsed.trap_controls} if parsed else {}
        self.cloners = {t[0]: t[1] for t in parsed.clone_controls} if parsed else {}
        self.movement = list(parsed.movement) if parsed else []

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self):
        return f"{{CC1Level title='{self.title}'}}"

    def at(self, pos):
        """Returns the CC1Cell at the given {pos}."""
        pos = self.__normalize_position(pos)  # If position in (x, y) format convert to y * 32 + x.
        return self.map[pos]

    def connect(self, pos1, pos2):
        """Connect a trap/clone button with its target."""
        pos1, pos2 = self.__normalize_position(pos1), self.__normalize_position(pos2)
        c1, c2 = self.at(pos1), self.at(pos2)
        e1 = c1.top if c1.top in CC1.nonmobs() else c1.bottom
        e2 = c2.top if c2.top in CC1.nonmobs() else c2.bottom
        if {e1, e2} == {CC1.TRAP_BUTTON, CC1.TRAP}:
            source, dest = (pos2, pos1) if e1 == CC1.TRAP else (pos1, pos2)
            self.traps[source] = dest
            return True
        if {e1, e2} == {CC1.CLONE_BUTTON, CC1.CLONER}:
            source, dest = (pos2, pos1) if e1 == CC1.CLONER else (pos1, pos2)
            self.cloners[source] = dest
            return True
        return False

    def is_valid(self):
        """Returns whether this level map is valid by CC1 rules."""
        return False not in {cell.is_valid() for cell in self.map}

    def add(self, pos, elem):
        """Add an element at a position, maintaining validity, traps, cloners, and movement."""
        pos = self.__normalize_position(pos)  # If position in (x, y) format convert to y * 32 + x.
        cell = self.map[pos]
        old_cell = copy.copy(cell)
        was_monster = cell.top in CC1.monsters()
        cell.add(elem)
        is_monster = cell.top in CC1.monsters()

        # Keep monster movement order in sync.
        if was_monster and not is_monster:
            self.movement.remove(pos)
        # DAT files can only support 127 movement entries.
        # See https://wiki.bitbusters.club/Monster
        if is_monster and not was_monster and len(self.movement) < 127:
            self.movement.append(pos)

        # Remove trap and cloner connections if they were deleted.
        # Note: If adding traps and cloners, they will NOT be connected here.
        for code in (CC1.TRAP, CC1.TRAP_BUTTON, CC1.CLONER, CC1.CLONE_BUTTON):
            was_removed = old_cell.contains(code) and not cell.contains(code)
            if was_removed:
                self.__update_controls(pos, code)

    def remove(self, pos, elem):
        """Remove an element at a position, maintaining validity, traps, cloners, and movement."""
        pos = self.__normalize_position(pos)  # If position in (x, y) format convert to y * 32 + x.
        removed = self.map[pos].remove(elem)
        if removed:
            if elem in CC1.monsters() and pos in self.movement:
                self.movement.remove(pos)
            self.__update_controls(pos, elem)

    def count(self, elem):
        """Counts all the occurrences of an element or set of elements in the level. Note: If two
        elements are stacked, only counts one of them. """
        elem_set = {elem, } if isinstance(elem, CC1) else set(iter(elem))
        for e in elem_set:
            assert isinstance(e, CC1)
        count = 0
        for p in range(32 * 32):
            count += len(elem_set.intersection({self.map[p].top, self.map[p].bottom}))
        return count

    def __update_controls(self, pos, elem):
        pos = self.__normalize_position(pos)  # If position in (x, y) format convert to y * 32 + x.
        if elem == CC1.TRAP:
            for k, v in tuple(self.traps.items()):
                if v == pos:
                    self.traps.pop(k, None)
        elif elem == CC1.TRAP_BUTTON:
            self.traps.pop(pos, None)
        elif elem == CC1.CLONER:
            for k, v in tuple(self.cloners.items()):
                if v == pos:
                    self.cloners.pop(k, None)
        elif elem == CC1.CLONE_BUTTON:
            self.cloners.pop(pos, None)

    @staticmethod
    def __normalize_position(p):
        if isinstance(p, int):
            return p
        if len(p) == 2:
            x, y = p
            return y * 32 + x
        raise ValueError(f"Invalid position {p}")


class CC1Levelset:
    """Class that represents a CC1 Levelset."""

    # pylint: disable=too-few-public-methods
    def __init__(self, parsed=None):
        self.levels = [CC1Level(level) for level in parsed.levels] if parsed else []

    def __str__(self):
        return f"{{CC1Levelset, {len(self.levels)} levels}}"


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


class CC1LevelImager:
    """Class that creates images of CC1Levels"""

    # pylint: disable=too-few-public-methods
    def __init__(self):
        base_path = "https://raw.githubusercontent.com/ChipMcCallahan/CCTools/main/art/8x8/"
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
            self.images[prefix] = Image.open(
                io.BytesIO(requests.get(base_path + image_file, timeout=5).content))
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
