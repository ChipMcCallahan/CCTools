"""Enumeration of tile codes used in CC1 DAT files, and associated utils."""
from enum import Enum


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

    def right(self):
        """Rotate to the right."""
        dirs = ("_N", "_E", "_S", "_W")
        if self.name[-2:] in dirs:
            index = (dirs.index(self.name[-2:]) + 1) % 4
            return CC1[self.name[:-2] + dirs[index]]
        dirs = ("_NW", "_NE", "_SE", "_SW")
        if self.name[:-3] == "ICE" and self.name[-3:] in dirs:
            index = (dirs.index(self.name[-3:]) + 1) % 4
            return CC1[self.name[:-3] + dirs[index]]
        return self

    def reverse(self):
        """Reverse direction."""
        return self.right().right()

    def left(self):
        """Rotate to the left."""
        return self.right().right().right()

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
