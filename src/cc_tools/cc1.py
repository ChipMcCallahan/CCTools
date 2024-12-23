from enum import Enum

# ----------------------------------------------------------------------
# Enhanced flipping logic
# ----------------------------------------------------------------------
# Instead of restricting flips to specific sets, we define direction maps
# that handle all known direction suffixes (N, E, S, W, NE, NW, SE, SW).
#
# * flip_horizontal:  E <-> W,  N stays N,  S stays S,
#                     NE <-> NW,  SE <-> SW
# * flip_vertical:    N <-> S,  E stays E,  W stays W,
#                     NE <-> SE,  NW <-> SW
# * flip_ne_sw:       reflects across a diagonal line from NE to SW
# * flip_nw_se:       reflects across a diagonal line from NW to SE
#
# If the tile is directionless or has a special case (e.g. FORCE_RANDOM),
# we leave it alone by default, but you can customize as needed.

FLIP_HORIZONTAL_MAP = {
    "N": "N",
    "S": "S",
    "E": "W",
    "W": "E",
    "NE": "NW",
    "NW": "NE",
    "SE": "SW",
    "SW": "SE"
}

FLIP_VERTICAL_MAP = {
    "N": "S",
    "S": "N",
    "E": "E",
    "W": "W",
    "NE": "SE",
    "SE": "NE",
    "NW": "SW",
    "SW": "NW"
}

FLIP_NE_SW_MAP = {
    "N": "E",  # N flips to E
    "E": "N",  # E flips to N
    "S": "W",  # S flips to W
    "W": "S",  # W flips to S
    "NE": "NE",  # NE remains NE
    "SE": "SW",  # SE flips to SW
    "NW": "NW",  # NW remains NW
    "SW": "SE",  # SW flips to SE
}

FLIP_NW_SE_MAP = {
    "N": "W",  # N flips to W
    "W": "N",  # W flips to N
    "S": "E",  # S flips to E
    "E": "S",  # E flips to S
    "NE": "NW",  # NE flips to NW
    "NW": "NE",  # NW flips to NE
    "SE": "SE",  # SE remains SE
    "SW": "SW",  # SW remains SW
}

class CC1(Enum):
    """Enumeration of tile codes used in CC1 DAT files, and associated utils."""

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

    # ----------------------------------------------------------------------
    # Direction helpers
    # ----------------------------------------------------------------------

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
        if not dirs:
            return self
        return CC1[self.name[:-len(dirs)] + dirs]

    def right(self):
        """Rotate this tile’s direction(s) 90° clockwise."""
        dir_suffix = self.dirs()
        # No direction => unchanged; skip certain exceptions if you want them unchanged:
        if not dir_suffix or self == CC1.PANEL_SE or self == CC1.FORCE_RANDOM:
            return self

        new_dirs = ""
        for d in dir_suffix:
            # Using the 'NESW' circular buffer: index(d)+1 => rotate right
            new_dirs = "NESW"[("NESW".index(d) + 1) % 4] + new_dirs
        return self.with_dirs(new_dirs)

    def reverse(self):
        """Reverse the tile’s direction(s), i.e. 180° turn (two rights)."""
        return self.right().right()

    def left(self):
        """Rotate this tile’s direction(s) 90° counterclockwise (three rights)."""
        return self.right().right().right()

    def flip_horizontal(self):
        """Flip horizontally: E <-> W, NE <-> NW, SE <-> SW, etc."""
        if not self.dirs():
            return self
        flipped = FLIP_HORIZONTAL_MAP[self.dirs()]
        return self.with_dirs(flipped)

    def flip_vertical(self):
        """Flip vertically: N <-> S, NE <-> SE, NW <-> SW, etc."""
        if not self.dirs():
            return self
        flipped = FLIP_VERTICAL_MAP[self.dirs()]
        return self.with_dirs(flipped)

    def flip_ne_sw(self):
        """
        Flip along the diagonal from NE to SW:
          - N <-> E
          - S <-> W
          - NE stays NE
          - SE <-> SW
          - NW stays NW
        """
        if not self.dirs():
            return self
        flipped = FLIP_NE_SW_MAP[self.dirs()]
        return self.with_dirs(flipped)

    def flip_nw_se(self):
        """
        Flip along the diagonal from NW to SE:
          - N <-> W
          - S <-> E
          - NE <-> NW
          - SE stays SE
          - SW stays SW
        """
        if not self.dirs():
            return self
        flipped = FLIP_NW_SE_MAP[self.dirs()]
        return self.with_dirs(flipped)

    # ----------------------------------------------------------------------
    # Class methods returning sets
    # ----------------------------------------------------------------------

    @classmethod
    def __compass(cls, prefix):
        """Helper: {prefix}_N, {prefix}_E, {prefix}_S, {prefix}_W."""
        return {cls[prefix + "_" + d] for d in "NESW"}

    @classmethod
    def all(cls):
        """Return a set of all CC1 tile codes."""
        return set(cls)

    @classmethod
    def invalid(cls):
        """Return a set of all invalid CC1 tiles."""
        return {
            cls.NOT_USED_0, cls.DROWN_CHIP, cls.BURNED_CHIP0, cls.BURNED_CHIP1,
            cls.NOT_USED_1, cls.NOT_USED_2, cls.NOT_USED_3, cls.CHIP_EXIT,
            cls.UNUSED_EXIT_0, cls.UNUSED_EXIT_1,
            cls.CHIP_SWIMMING_N, cls.CHIP_SWIMMING_E,
            cls.CHIP_SWIMMING_S, cls.CHIP_SWIMMING_W,
        }

    @classmethod
    def valid(cls):
        """Return a set of all valid CC1 tiles."""
        return cls.all().difference(cls.invalid())

    @classmethod
    def ice(cls):
        """Return a set of all CC1 ice and ice corner tiles."""
        return {cls.ICE} | {cls["ICE_" + d] for d in ("NE", "NW", "SE", "SW")}

    @classmethod
    def forces(cls):
        """Return a set of all CC1 force floor tiles."""
        return {cls.FORCE_RANDOM} | cls.__compass("FORCE")

    @classmethod
    def walls(cls):
        """Return a set of all CC1 wall tiles."""
        return {cls.WALL, cls.INV_WALL_PERM, cls.INV_WALL_APP, cls.BLUE_WALL_REAL}

    @classmethod
    def panels(cls):
        """Return a set of all CC1 panel (thin wall) tiles."""
        return {cls.PANEL_SE} | cls.__compass("PANEL")

    @classmethod
    def clone_blocks(cls):
        """Return a set of all CC1 clone block tiles."""
        return cls.__compass("CLONE_BLOCK")

    @classmethod
    def blocks(cls):
        """Return a set of all CC1 block and clone block tiles."""
        return cls.clone_blocks() | {cls.BLOCK}

    @classmethod
    def players(cls):
        """Return a set of all CC1 player tiles."""
        return cls.__compass("PLAYER")

    @classmethod
    def ants(cls):
        """Return a set of all CC1 ant (spider) tiles."""
        return cls.__compass("ANT")

    @classmethod
    def paramecia(cls):
        """Return a set of all CC1 paramecium tiles."""
        return cls.__compass("PARAMECIUM")

    @classmethod
    def gliders(cls):
        """Return a set of all CC1 glider tiles."""
        return cls.__compass("GLIDER")

    @classmethod
    def fireballs(cls):
        """Return a set of all CC1 fireball tiles."""
        return cls.__compass("FIREBALL")

    @classmethod
    def tanks(cls):
        """Return a set of all CC1 tank tiles."""
        return cls.__compass("TANK")

    @classmethod
    def balls(cls):
        """Return a set of all CC1 ball tiles."""
        return cls.__compass("BALL")

    @classmethod
    def walkers(cls):
        """Return a set of all CC1 walker tiles."""
        return cls.__compass("WALKER")

    @classmethod
    def teeth(cls):
        """Return a set of all CC1 teeth tiles."""
        return cls.__compass("TEETH")

    @classmethod
    def blobs(cls):
        """Return a set of all CC1 blob tiles."""
        return cls.__compass("BLOB")

    @classmethod
    def monsters(cls):
        """Return a set of all CC1 monster tiles."""
        return (
            cls.gliders()
            | cls.ants()
            | cls.paramecia()
            | cls.fireballs()
            | cls.teeth()
            | cls.tanks()
            | cls.blobs()
            | cls.walkers()
            | cls.balls()
        )

    @classmethod
    def mobs(cls):
        """Return a set of all CC1 monster, block, and player tiles."""
        return cls.monsters() | cls.blocks() | cls.players()

    @classmethod
    def nonmobs(cls):
        """Return a set of all CC1 tiles that are not monsters, blocks, or players."""
        return cls.all().difference(cls.mobs())

    @classmethod
    def doors(cls):
        """Return a set of all CC1 door tiles."""
        return {cls.RED_DOOR, cls.GREEN_DOOR, cls.YELLOW_DOOR, cls.BLUE_DOOR}

    @classmethod
    def keys(cls):
        """Return a set of all CC1 key tiles."""
        return {cls.RED_KEY, cls.GREEN_KEY, cls.YELLOW_KEY, cls.BLUE_KEY}

    @classmethod
    def boots(cls):
        """Return a set of all CC1 boot tiles."""
        return {cls.SKATES, cls.SUCTION_BOOTS, cls.FIRE_BOOTS, cls.FLIPPERS}

    @classmethod
    def pickups(cls):
        """Return a set of all CC1 boot, key, and chip tiles."""
        return cls.boots() | cls.keys() | {cls.CHIP}

    @classmethod
    def buttons(cls):
        """Return a set of all CC1 button tiles."""
        return {cls.GREEN_BUTTON, cls.TRAP_BUTTON, cls.CLONE_BUTTON, cls.TANK_BUTTON}

    @classmethod
    def toggles(cls):
        """Return a set of all CC1 toggle tiles."""
        return {cls.TOGGLE_WALL, cls.TOGGLE_FLOOR}
