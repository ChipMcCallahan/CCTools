from enum import Enum

class CC2(Enum):
    """
    An enumeration of tiles and objects used in Chip's Challenge 2 (CC2).
    Each member of this enumeration corresponds to a particular tile or entity
    within the CC2 game environment. Many of these elements have special behaviors
    or states, and some are directional or toggleable.

    The numeric values assigned to each member match the internal representation
    used in the CC2 level format (and often in the original CC1 format where
    there is overlap).
    """

    FLOOR = 0x01          # Basic floor tile.
    WALL = 0x02           # Standard wall tile.
    ICE = 0x03            # Ice floor tile (causes sliding).
    ICE_SW = 0x04         # Southwest ice corner.
    ICE_NW = 0x05         # Northwest ice corner.
    ICE_NE = 0x06         # Northeast ice corner.
    ICE_SE = 0x07         # Southeast ice corner.
    WATER = 0x08          # Water tile (requires flippers to cross safely).
    FIRE = 0x09           # Fire tile (requires fire boots to cross safely).
    FORCE_N = 0x0A        # Force floor pushing north.
    FORCE_E = 0x0B        # Force floor pushing east.
    FORCE_S = 0x0C        # Force floor pushing south.
    FORCE_W = 0x0D        # Force floor pushing west.
    GREEN_TOGGLE_WALL = 0x0E   # Wall controlled by green toggle switch.
    GREEN_TOGGLE_FLOOR = 0x0F  # Floor controlled by green toggle switch.
    RED_TELEPORT = 0x10         # Teleport tile (red).
    BLUE_TELEPORT = 0x11        # Teleport tile (blue).
    YELLOW_TELEPORT = 0x12      # Teleport tile (yellow).
    GREEN_TELEPORT = 0x13       # Teleport tile (green).
    EXIT = 0x14                 # Exit tile.
    SLIME = 0x15                # Slime floor tile.
    CHIP = 0x16                 # Chip character.
    DIRT_BLOCK = 0x17           # Movable dirt block.
    WALKER = 0x18               # Walker enemy.
    GLIDER = 0x19               # Glider enemy.
    ICE_BLOCK = 0x1A            # Movable ice block.
    THIN_WALL_S = 0x1B          # Thin wall facing south (CC1 legacy).
    THIN_WALL_E = 0x1C          # Thin wall facing east (CC1 legacy).
    THIN_WALL_SE = 0x1D         # Thin wall southeast corner (CC1 legacy).
    GRAVEL = 0x1E               # Gravel floor.
    GREEN_BUTTON = 0x1F         # Green button (activates green toggles).
    BLUE_BUTTON = 0x20          # Blue button (activates blue tanks).
    BLUE_TANK = 0x21            # Blue tank enemy (change direction on blue button press).
    RED_DOOR = 0x22             # Red door (requires red key).
    BLUE_DOOR = 0x23            # Blue door (requires blue key).
    YELLOW_DOOR = 0x24          # Yellow door (requires yellow key).
    GREEN_DOOR = 0x25           # Green door (requires green key).
    RED_KEY = 0x26              # Red key.
    BLUE_KEY = 0x27             # Blue key.
    YELLOW_KEY = 0x28           # Yellow key.
    GREEN_KEY = 0x29            # Green key.
    IC_CHIP = 0x2A              # Integrated circuit chip (collectible).
    EXTRA_IC_CHIP = 0x2B        # Extra (bonus) integrated circuit chip.
    CHIP_SOCKET = 0x2C          # Socket that requires IC chips to pass.
    POPUP_WALL = 0x2D           # Pop-up wall.
    APPEARING_WALL = 0x2E       # Appearing wall (reveals permanently when bumped).
    INVISIBLE_WALL = 0x2F       # Invisible wall (reveals temporarily when bumped).
    SOLID_BLUE_WALL = 0x30      # A blue wall that is solid.
    FALSE_BLUE_WALL = 0x31      # A blue wall that can be passed (fake).
    DIRT = 0x32                 # Dirt floor tile.
    ANT = 0x33                  # Ant enemy.
    CENTIPEDE = 0x34            # Centipede enemy.
    BALL = 0x35                 # Ball enemy.
    BLOB = 0x36                 # Blob enemy.
    RED_TEETH = 0x37            # Red teeth (enemy).
    FIREBALL = 0x38             # Fireball enemy.
    RED_BUTTON = 0x39           # Red button (activates clone machines).
    BROWN_BUTTON = 0x3A         # Brown button (activates traps).
    CLEATS = 0x3B               # Cleats item (prevents sliding on ice).
    SUCTION_BOOTS = 0x3C        # Suction boots item (prevents sliding on force floors).
    FIRE_BOOTS = 0x3D           # Fire boots item (walk on fire safely).
    FLIPPERS = 0x3E             # Flippers item (swim in water).
    TOOL_THIEF = 0x3F           # Thief that steals tools/boots.
    BOMB = 0x40                 # Bomb (explodes on contact).
    OPEN_TRAP = 0x41            # Open trap (unused).
    TRAP = 0x42                 # Trap (can hold creatures).
    CLONE_MACHINE_OLD = 0x43    # Old clone machine (CC1 legacy).
    CLONE_MACHINE = 0x44         # Modern clone machine (CC2).
    CLUE = 0x45                  # Clue item (displays message).
    FORCE_RANDOM = 0x46          # Random force floor (pushes in random directions).
    GRAY_BUTTON = 0x47           # Gray button (area effect).
    SWIVEL_DOOR_SW = 0x48        # Swivel door corner (southwest).
    SWIVEL_DOOR_NW = 0x49        # Swivel door corner (northwest).
    SWIVEL_DOOR_NE = 0x4A        # Swivel door corner (northeast).
    SWIVEL_DOOR_SE = 0x4B        # Swivel door corner (southeast).
    TIME_BONUS = 0x4C            # Time bonus item.
    STOPWATCH = 0x4D             # Stopwatch item (pauses/unpauses time).
    TRANSMOGRIFIER = 0x4E        # Transmogrifier (toggles Chip <--> Melinda).
    RAILROAD_TRACK = 0x4F        # Railroad track tile.
    STEEL_WALL = 0x50            # Steel wall (indestructible).
    TNT = 0x51                   # TNT item.
    HELMET = 0x52                # Helmet item.
    UNUSED_53 = 0x53             # Unused tile placeholder.
    UNUSED_54 = 0x54             # Unused tile placeholder.
    UNUSED_55 = 0x55             # Unused tile placeholder.
    MELINDA = 0x56               # Melinda character.
    BLUE_TEETH = 0x57            # Blue teeth enemy.
    EXPLOSION_ANIMATION = 0x58   # Explosion animation (unused).
    HIKING_BOOTS = 0x59          # Hiking boots item (walk on gravel/slime).
    MALE_ONLY_SIGN = 0x5A        # Indicates path only for Chip (male).
    FEMALE_ONLY_SIGN = 0x5B      # Indicates path only for Melinda (female).
    LOGIC_GATE = 0x5C            # Logic gate object (various uses in CC2 editor).
    UNUSED_5D = 0x5D             # Unused tile placeholder.
    PINK_BUTTON = 0x5E           # Pink button (activates wires).
    FLAME_JET_OFF = 0x5F         # Flame jet tile (off state).
    FLAME_JET_ON = 0x60          # Flame jet tile (on state).
    ORANGE_BUTTON = 0x61         # Orange button (toggles flame jets).
    LIGHTNING_BOLT = 0x62        # Lightning bolt item (activates wires).
    YELLOW_TANK = 0x63           # Yellow tank enemy.
    YELLOW_TANK_BUTTON = 0x64    # Button associated with yellow tank.
    MIRROR_CHIP = 0x65           # 'Mirror' version of Chip.
    MIRROR_MELINDA = 0x66        # 'Mirror' version of Melinda.
    UNUSED_67 = 0x67             # Unused tile placeholder.
    BOWLING_BALL = 0x68          # Bowling ball item (throwable).
    ROVER = 0x69                 # Rover enemy (moves in complicated patterns).
    TIME_PENALTY = 0x6A          # Time penalty tile/item.
    CUSTOM_FLOOR = 0x6B          # Custom floor (editor-defined).
    UNUSED_6C = 0x6C             # Unused tile placeholder.
    THIN_WALL_CANOPY = 0x6D      # Thin wall/canopy.
    UNUSED_6E = 0x6E             # Unused tile placeholder.
    RAILROAD_SIGN = 0x6F         # Railroad sign item.
    CUSTOM_WALL = 0x70           # Custom wall (editor-defined).
    LETTER_TILE_SPACE = 0x71     # Space for a letter tile.
    PURPLE_TOGGLE_FLOOR = 0x72   # Floor controlled by wires or grey button.
    PURPLE_TOGGLE_WALL = 0x73    # Wall controlled by wires or grey button.
    UNUSED_74 = 0x74             # Unused tile placeholder.
    UNUSED_75 = 0x75             # Unused tile placeholder.
    MODIFIER_8BIT = 0x76         # Modifier (8-bit).
    MODIFIER_16BIT = 0x77        # Modifier (16-bit).
    MODIFIER_32BIT = 0x78        # Modifier (32-bit).
    UNUSED_79 = 0x79             # Unused tile placeholder (invalid).
    FLAG_10 = 0x7A               # Bonus flag with value 10.
    FLAG_100 = 0x7B              # Bonus flag with value 100.
    FLAG_1000 = 0x7C             # Bonus flag with value 1000.
    SOLID_GREEN_WALL = 0x7D      # A green wall that is solid.
    FALSE_GREEN_WALL = 0x7E      # A green wall that is fake (passable).
    NOT_ALLOWED_MARKER = 0x7F    # Marker indicating something is not allowed.
    FLAG_2X = 0x80               # Flag with multiplier value x2.
    DIRECTIONAL_BLOCK = 0x81     # A movable block that has a facing/direction.
    FLOOR_MIMIC = 0x82           # Enemy that mimics floor.
    GREEN_BOMB = 0x83            # Bomb that toggles between bomb and chip states.
    GREEN_CHIP = 0x84            # Chip that toggles between chip and bomb states.
    UNUSED_85 = 0x85             # Unused tile placeholder.
    UNUSED_86 = 0x86             # Unused tile placeholder.
    BLACK_BUTTON = 0x87          # Black button (deactivates wires).
    SWITCH_OFF = 0x88            # Switch in "off" state (toggle).
    SWITCH_ON = 0x89             # Switch in "on" state (toggle).
    KEY_THIEF = 0x8A             # Thief that steals keys.
    GHOST = 0x8B                 # Ghost enemy (moves through walls).
    STEEL_FOIL = 0x8C            # Steel foil item (turns walls into steel walls).
    TURTLE = 0x8D                # Turtle (turns into water on exit).
    SECRET_EYE = 0x8E            # Secret eye item (reveals secrets).
    BRIBE = 0x8F                 # Bribe item (bypass thief actions).
    SPEED_BOOTS = 0x90           # Speed boots item (move faster).
    UNUSED_91 = 0x91             # Unused tile placeholder.
    HOOK = 0x92                  # Hook item (pull blocks).

    def dirs(self):
        """
        Determine whether this tile or object has a directional suffix
        (e.g., 'N', 'E', 'S', 'W', 'NE', 'NW', 'SE', 'SW') in its name.
        If so, return that suffix; otherwise, return an empty string.

        :return: The directional suffix, or an empty string if none is present.
        :rtype: str
        """
        suffix = self.name.rsplit('_', maxsplit=1)[-1]
        return suffix if suffix in ("N", "E", "S", "W", "NE", "NW", "SE", "SW") else ""

    def with_dirs(self, dirs):
        """
        Create a new enum member with the same base name but a different
        directional suffix.

        :param dirs: The new direction(s) to apply (e.g., 'N', 'NE', 'SW', '').
        :type dirs: str
        :return: A new CC2 enum member with the replaced direction suffix.
        :rtype: CC2
        :raises ValueError: If the provided direction(s) is invalid or
                            if the length of the existing direction suffix
                            and the provided suffix differ but non-zero.
        """
        if dirs not in ("", "N", "E", "S", "W", "NE", "NW", "SE", "SW"):
            raise ValueError(f"illegal direction(s) specified: {dirs}")
        if len(self.dirs()) != len(dirs):
            raise ValueError(f"lengths unequal: self: {len(self.dirs())} vs given: {dirs}")
        if len(dirs) == 0:
            return self
        # Construct a new enum member name by replacing the old suffix with the new one.
        return CC2[self.name[:-len(dirs)] + dirs]

    def right(self):
        """
        Rotate the directions in this tile's name to the right.
        For example, 'N' would become 'E', 'E' would become 'S',
        and a compound direction like 'NE' would become 'SE'.

        If this tile does not have a recognized direction suffix,
        it is returned unchanged.

        :return: A new CC2 enum member with directions rotated 90 degrees to the right.
        :rtype: CC2
        """
        if not self in CC2.values_with_hardcoded_directions():
            return self
        new_dirs = ""
        for d in self.dirs():
            # The string "NESW" is used like a circular buffer:
            # index(d) gets the position of d, then +1 moves clockwise, %4 wraps around.
            new_dirs = "NESW"[("NESW".index(d) + 1) % 4] + new_dirs
        return self.with_dirs(new_dirs)

    def reverse(self):
        """
        Reverse the direction of this tile's name. This is effectively
        performing two 'right' rotations, which is the same as a 180-degree turn.

        :return: A CC2 enum member with directions reversed.
        :rtype: CC2
        """
        return self.right().right()

    def left(self):
        """
        Rotate the directions in this tile's name to the left (counter-clockwise).
        This is equivalent to rotating right three times.

        :return: A CC2 enum member with directions rotated 90 degrees to the left.
        :rtype: CC2
        """
        return self.right().right().right()

    def toggle(self):
        """
        Toggle the state of this tile if it is part of a known pair of toggleable states.

        Examples of toggle pairs:
        - GREEN_CHIP <--> GREEN_BOMB
        - FLAME_JET_ON <--> FLAME_JET_OFF
        - GREEN_TOGGLE_FLOOR <--> GREEN_TOGGLE_WALL
        - PURPLE_TOGGLE_FLOOR <--> PURPLE_TOGGLE_WALL
        - SWITCH_ON <--> SWITCH_OFF

        If this tile is not in a toggleable pair, it is returned unchanged.

        :return: The toggled version of this tile, or the tile itself if no toggle is found.
        :rtype: CC2
        """

        # The 'pairs' structure groups known toggleable elements.
        pairs = (
            list(CC2.toggle_chips()),
            list(CC2.flame_jets()),
            list(CC2.green_toggles()),
            list(CC2.purple_toggles()),
            list(CC2.switches())
        )
        # Search each pair to find 'self' and return its partner if found.
        for pair in pairs:
            if self in pair:
                return pair[1] if self == pair[0] else pair[0]

        # If no toggleable pair is found, return self.
        return self

    @classmethod
    def values_with_hardcoded_directions(cls):
        """
        Return the set of CC2 tiles that have explicitly coded directions
        (e.g., ICE_NW or FORCE_W) and thus require special handling for rotations.

        :return: A set of CC2 members that have hardcoded directions in their names.
        :rtype: set
        """
        return cls.ice() | cls.forces() | cls.swivels() - {cls.FORCE_RANDOM, cls.ICE}

    @classmethod
    def values_with_hardcoded_states(cls):
        """
        Return the set of CC2 tiles that have explicitly coded 'state' toggles
        (e.g., SWITCH_ON vs SWITCH_OFF, FLAME_JET_ON vs FLAME_JET_OFF, etc.).

        :return: A set of CC2 members that may toggle between on/off or similar states.
        :rtype: set
        """
        return cls.switches() | cls.toggles() | cls.flame_jets() | cls.toggle_chips()

    @classmethod
    def ice(cls):
        """
        Return the set of all CC2 ice and ice corner tiles.

        :return: A set containing ICE and its corner variants (ICE_NE, ICE_NW, ICE_SE, ICE_SW).
        :rtype: set
        """
        return {cls.ICE, cls.ICE_NE, cls.ICE_NW, cls.ICE_SE, cls.ICE_SW}

    @classmethod
    def forces(cls):
        """
        Return the set of all CC2 force floor tiles.

        :return: A set of force floor tiles (force floors push objects in a certain direction).
        :rtype: set
        """
        return {cls.FORCE_RANDOM, cls.FORCE_E, cls.FORCE_N, cls.FORCE_S, cls.FORCE_W}

    @classmethod
    def walls(cls):
        """
        Return the set of major wall tiles in CC2, including steel, green, and blue walls,
        as well as invisible walls.

        :return: A set of walls.
        :rtype: set
        """
        return {cls.WALL, cls.STEEL_WALL, cls.SOLID_GREEN_WALL, cls.SOLID_BLUE_WALL} | cls.invisible_walls()

    @classmethod
    def panels(cls):
        """
        Return the set of 'panel'-like tiles (thin walls) often used in CC1 and CC2.

        :return: A set of thin wall variants.
        :rtype: set
        """
        return {cls.THIN_WALL_S, cls.THIN_WALL_E, cls.THIN_WALL_SE, cls.THIN_WALL_CANOPY}

    @classmethod
    def blocks(cls):
        """
        Return the set of movable block-like entities (e.g., dirt block, ice block, directional block).

        :return: A set of block tiles.
        :rtype: set
        """
        return {cls.DIRT_BLOCK, cls.ICE_BLOCK, cls.DIRECTIONAL_BLOCK}

    @classmethod
    def monsters(cls):
        """
        Return the set of non-block, non-player creatures in CC2 (various types of enemies).

        :return: A set of monster tiles.
        :rtype: set
        """
        return {
            cls.GLIDER, cls.FIREBALL, cls.ANT, cls.CENTIPEDE,
            cls.WALKER, cls.BALL, cls.RED_TEETH, cls.BLOB,
            cls.BLUE_TANK, cls.YELLOW_TANK, cls.BLUE_TEETH, cls.FLOOR_MIMIC,
            cls.MIRROR_CHIP, cls.MIRROR_MELINDA, cls.ROVER, cls.GHOST
        }

    @classmethod
    def mobs(cls):
        """
        Return the set of all 'mobile' entities, which includes monsters, blocks, and players.

        :return: A set containing all mobile CC2 tiles.
        :rtype: set
        """
        return cls.monsters() | cls.blocks() | cls.players()

    @classmethod
    def toggle_chips(cls):
        """
        Return the set of chip-like objects that can toggle between chip and bomb states
        (GREEN_CHIP and GREEN_BOMB).

        :return: A set of toggleable chip tiles.
        :rtype: set
        """
        return {cls.GREEN_CHIP, cls.GREEN_BOMB}

    @classmethod
    def ic_chips(cls):
        """
        Return the set of integrated circuit chips (normal and extra).

        :return: A set containing IC_CHIP and EXTRA_IC_CHIP.
        :rtype: set
        """
        return {cls.IC_CHIP, cls.EXTRA_IC_CHIP}

    @classmethod
    def all_chips(cls):
        """
        Return the union of all chip-related tiles (both toggle chips and IC chips).

        :return: A set containing GREEN_CHIP, GREEN_BOMB, IC_CHIP, EXTRA_IC_CHIP.
        :rtype: set
        """
        return cls.toggle_chips() | cls.ic_chips()

    @classmethod
    def swivels(cls):
        """
        Return the set of all swivel door tiles (NE, NW, SE, SW).

        :return: A set of swivel door tiles.
        :rtype: set
        """
        return {cls.SWIVEL_DOOR_NE, cls.SWIVEL_DOOR_NW, cls.SWIVEL_DOOR_SE, cls.SWIVEL_DOOR_SW}

    @classmethod
    def doors(cls):
        """
        Return the set of colored doors (red, blue, green, yellow) that require matching keys.

        :return: A set of door tiles.
        :rtype: set
        """
        return {cls.RED_DOOR, cls.BLUE_DOOR, cls.GREEN_DOOR, cls.YELLOW_DOOR}

    @classmethod
    def keys(cls):
        """
        Return the set of colored keys (red, blue, green, yellow).

        :return: A set of key tiles.
        :rtype: set
        """
        return {cls.RED_KEY, cls.BLUE_KEY, cls.GREEN_KEY, cls.YELLOW_KEY}

    @classmethod
    def tools(cls):
        """
        Return the set of tool/boot items in CC2 (e.g., flippers, fire boots, suction boots, etc.).

        :return: A set of tool tiles.
        :rtype: set
        """
        return {
            cls.FLIPPERS, cls.CLEATS, cls.FIRE_BOOTS, cls.SUCTION_BOOTS,
            cls.TNT, cls.BOWLING_BALL, cls.SECRET_EYE, cls.BRIBE,
            cls.SPEED_BOOTS, cls.RAILROAD_SIGN, cls.HIKING_BOOTS,
            cls.HELMET, cls.HOOK, cls.STEEL_FOIL, cls.LIGHTNING_BOLT
        }

    @classmethod
    def flags(cls):
        """
        Return the set of all 'flag' items (often used for scoring or puzzle logic).

        :return: A set of flag tiles.
        :rtype: set
        """
        return {cls.FLAG_10, cls.FLAG_100, cls.FLAG_1000, cls.FLAG_2X}

    @classmethod
    def time_pickups(cls):
        """
        Return the set of time-related pickups (bonus, penalty, stopwatch).

        :return: A set of time-modifying tiles.
        :rtype: set
        """
        return {cls.TIME_BONUS, cls.TIME_PENALTY, cls.STOPWATCH}

    @classmethod
    def bombs(cls):
        """
        Return the set of bomb-like tiles (standard bomb and green bomb).

        :return: A set of bomb tiles.
        :rtype: set
        """
        return {cls.GREEN_BOMB, cls.BOMB}

    @classmethod
    def pickups(cls):
        """
        Return the set of all collectible tiles, including keys, tools, flags, time pickups, and bombs.

        :return: A set of pickup tiles.
        :rtype: set
        """
        return cls.keys() | cls.tools() | cls.flags() | cls.time_pickups() | cls.bombs()

    @classmethod
    def blue_walls(cls):
        """
        Return the set of blue walls, which may be solid or fake.

        :return: A set containing FALSE_BLUE_WALL and SOLID_BLUE_WALL.
        :rtype: set
        """
        return {cls.FALSE_BLUE_WALL, cls.SOLID_BLUE_WALL}

    @classmethod
    def green_walls(cls):
        """
        Return the set of green walls, which may be solid or fake.

        :return: A set containing FALSE_GREEN_WALL and SOLID_GREEN_WALL.
        :rtype: set
        """
        return {cls.FALSE_GREEN_WALL, cls.SOLID_GREEN_WALL}

    @classmethod
    def invisible_walls(cls):
        """
        Return the set of walls that are invisible or appear only when stepped on.

        :return: A set containing INVISIBLE_WALL and APPEARING_WALL.
        :rtype: set
        """
        return {cls.INVISIBLE_WALL, cls.APPEARING_WALL}

    @classmethod
    def mystery_walls(cls):
        """
        Return the set of walls that have 'mystery' or hidden properties,
        including invisible walls and false/solid walls.

        :return: A set containing blue walls, green walls, and invisible walls.
        :rtype: set
        """
        return cls.blue_walls() | cls.green_walls() | cls.invisible_walls()

    @classmethod
    def switches(cls):
        """
        Return the set of switch tiles in on/off states.

        :return: A set containing SWITCH_ON and SWITCH_OFF.
        :rtype: set
        """
        return {cls.SWITCH_ON, cls.SWITCH_OFF}

    @classmethod
    def buttons(cls):
        """
        Return the set of all button tiles of various colors (red, green, blue, brown, etc.).

        :return: A set of button tiles.
        :rtype: set
        """
        return {
            cls.RED_BUTTON, cls.GREEN_BUTTON, cls.BLUE_BUTTON, cls.BROWN_BUTTON,
            cls.GRAY_BUTTON, cls.PINK_BUTTON, cls.BLACK_BUTTON, cls.ORANGE_BUTTON,
            cls.YELLOW_TANK_BUTTON
        }

    @classmethod
    def buttons_and_switches(cls):
        """
        Return the union of all buttons and switches.

        :return: A set containing both buttons and switches.
        :rtype: set
        """
        return cls.buttons() | cls.switches()

    @classmethod
    def purple_toggles(cls):
        """
        Return the set of tiles controlled by a purple toggle switch (floor/wall).

        :return: A set with PURPLE_TOGGLE_FLOOR and PURPLE_TOGGLE_WALL.
        :rtype: set
        """
        return {cls.PURPLE_TOGGLE_FLOOR, cls.PURPLE_TOGGLE_WALL}

    @classmethod
    def green_toggles(cls):
        """
        Return the set of tiles controlled by a green toggle switch (floor/wall).

        :return: A set with GREEN_TOGGLE_FLOOR and GREEN_TOGGLE_WALL.
        :rtype: set
        """
        return {cls.GREEN_TOGGLE_FLOOR, cls.GREEN_TOGGLE_WALL}

    @classmethod
    def flame_jets(cls):
        """
        Return the set of flame jet states (on/off).

        :return: A set containing FLAME_JET_ON and FLAME_JET_OFF.
        :rtype: set
        """
        return {cls.FLAME_JET_ON, cls.FLAME_JET_OFF}

    @classmethod
    def toggles(cls):
        """
        Return all toggleable floor/wall pairs (purple and green toggles).

        :return: A set of toggle floor/wall tiles.
        :rtype: set
        """
        return cls.purple_toggles() | cls.green_toggles()

    @classmethod
    def teleports(cls):
        """
        Return the set of teleport tiles (red, blue, yellow, green).

        :return: A set of teleport tiles.
        :rtype: set
        """
        return {cls.RED_TELEPORT, cls.BLUE_TELEPORT, cls.YELLOW_TELEPORT, cls.GREEN_TELEPORT}

    @classmethod
    def players(cls):
        """
        Return the set of player characters (Chip and Melinda).

        :return: A set containing CHIP and MELINDA.
        :rtype: set
        """
        return {cls.CHIP, cls.MELINDA}

    @classmethod
    def mirrors(cls):
        """
        Return the set of 'mirror' variants of players (MIRROR_CHIP, MIRROR_MELINDA).

        :return: A set containing MIRROR_CHIP and MIRROR_MELINDA.
        :rtype: set
        """
        return {cls.MIRROR_CHIP, cls.MIRROR_MELINDA}

    @classmethod
    def tanks(cls):
        """
        Return the set of tank enemies (blue tank and yellow tank).

        :return: A set containing BLUE_TANK and YELLOW_TANK.
        :rtype: set
        """
        return {cls.BLUE_TANK, cls.YELLOW_TANK}

    @classmethod
    def thieves(cls):
        """
        Return the set of thief tiles that steal either keys or tools.

        :return: A set containing KEY_THIEF and TOOL_THIEF.
        :rtype: set
        """
        return {cls.KEY_THIEF, cls.TOOL_THIEF}

    @classmethod
    def gender_signs(cls):
        """
        Return the set of tiles that restrict passage based on gender
        (male-only sign, female-only sign).

        :return: A set containing MALE_ONLY_SIGN and FEMALE_ONLY_SIGN.
        :rtype: set
        """
        return {cls.MALE_ONLY_SIGN, cls.FEMALE_ONLY_SIGN}

    @classmethod
    def unused(cls):
        """
        Return the set of all unused placeholders in this enumeration.

        :return: A set of CC2 members whose name contains 'UNUSED'.
        :rtype: set
        """
        return {member for name, member in cls.__members__.items() if "UNUSED" in name}

    @classmethod
    def invalid_mobs(cls):
        """
        Return the set of tiles that are considered invalid or require additional data
        (e.g., explosion animation, or placeholders that expect a direction byte).

        :return: A set of invalid/unusable mob tiles.
        :rtype: set
        """
        return {cls.EXPLOSION_ANIMATION, cls.UNUSED_79}

    @classmethod
    def all_mobs(cls):
        """
        Return the set of all possible mobile entities, including monsters, blocks, players,
        and invalid mobs.

        :return: A set of all mob tiles.
        :rtype: set
        """
        return cls.mobs() | cls.invalid_mobs()

    @classmethod
    def modifiers(cls):
        """
        Return the set of tiles that act as bit modifiers (MODIFIER_8BIT, MODIFIER_16BIT, MODIFIER_32BIT).

        :return: A set of modifier tiles.
        :rtype: set
        """
        return {cls.MODIFIER_8BIT, cls.MODIFIER_16BIT, cls.MODIFIER_32BIT}
