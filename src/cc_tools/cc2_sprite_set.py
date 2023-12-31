"""
Module: CC2 Sprite Set
"""
from PIL import Image

from cc_tools.img_utils import load_sprite_file, make_transparent, flatten, \
    create_bounding_box_transparency, compass_paste_16

SIZE = 32
SM_SIZE = 16
MINT_GREEN = (81, 205, 106)


class CC2SpriteSet:
    def __init__(self):
        """
        Initializes the CC1SpriteSet.

        Args: size_in_pixels (int): Size of the sprites in pixels.
        """
        self.sprites = {}

    @staticmethod
    def factory(filename):
        """
        Factory method to create a sprite set from any standardized CC2
        bmp with mint green transparency.

        Returns: CC2SpriteSet: A new instance of CC2SpriteSet with pixel
        sprites.
        """

        raw = load_sprite_file(f"cc_tools.art.cc2", filename)
        raw = make_transparent(raw, [MINT_GREEN])

        assert raw.size == (16 * 32, 32 * 32)

        def tile(x_index, y_index):
            _i, _j = x_index * SIZE, y_index * SIZE
            return raw.crop((_i, _j, _i + SIZE, _j + SIZE))

        def tile16(x_index, y_index, sub_index):
            parent = tile(x_index, y_index)
            _i, _j = sub_index % 2 * SM_SIZE, sub_index // 2 * SM_SIZE
            return parent.crop((_i, _j, _i + SM_SIZE, _j + SM_SIZE))

        def tall_tile(x_index, y_index):
            tall_image = Image.new('RGBA', (SIZE, SIZE * 2))
            tall_image.paste(tile(x_index, y_index), (0, 0))  # top
            tall_image.paste(tile(x_index, y_index + 1), (0, SIZE))  # bottom
            return tall_image

        def wide_tile(x_index, y_index):
            wide_image = Image.new('RGBA', (SIZE * 2, SIZE))
            wide_image.paste(tile(x_index, y_index), (0, 0))  # left
            wide_image.paste(tile(x_index + 1, y_index), (SIZE, 0))  # right
            return wide_image

        def add_series(_x, _y, base_name, frames):
            start = _y * 16 + _x
            stop = start + frames
            for p in range(start, stop):
                _i, _j = p % 16, p // 16
                index = p - start
                frame = index % frames
                name = f"{base_name}"
                if frame > 0:
                    name += f"_{frame}"
                add(_i, _j, name)

        def add_directional(_x, _y, base_name, frames, dirs="NESW"):
            start = _y * 16 + _x
            for _i, _d in enumerate(dirs):
                local_start = start + _i * frames
                start_x, start_y = local_start % 16, local_start // 16
                add_series(start_x, start_y, f"{base_name}_{_d}", frames)

        spriteset = CC2SpriteSet()
        lib = spriteset.sprites

        # Process the yellow ASCII chars
        for ascii_value in range(32, 96):
            c = chr(ascii_value)
            x16 = (ascii_value - 32) % 32  # 0-31
            y16 = (ascii_value - 32) // 32  # 0-1
            x32 = x16 // 2  # 0-15
            y32 = 0  # always 0 for first bmp row
            sub = x16 % 2 + y16 * 2  # pos within the tile (NW, NE, SW, SE)
            key = c if ascii_value != 32 else "SPACE"
            small = tile16(x32, y32, sub)
            large = small.resize((SIZE, SIZE), Image.NEAREST)
            lib[f"CHAR_{key}_16"] = small
            lib[f"CHAR_{key}"] = large

        def add(_x, _y, label):
            lib[label] = tile(_x, _y)

        def add16(_x, _y, sub_index, label):
            lib[label] = tile16(_x, _y, sub_index)

        for i, color in enumerate(["RED", "BLUE", "YELLOW", "GREEN"]):
            add(i, 1, f"{color}_DOOR")
            add(i + 4, 1, f"{color}_KEY")

        add(8, 1, "BLOCK")
        add(9, 1, "BLOCK_TRANSPARENT")
        add(10, 1, "ICE")
        add(11, 1, "ICE_NW")
        add(12, 1, "ICE_NE")
        add(13, 1, "ICE_SW")
        add(14, 1, "ICE_SE")
        add(15, 1, "CLONER")
        add(0, 2, "FLOOR")
        add(1, 2, "WALL")
        add(2, 2, "SUNKEN_FLOOR")
        add(3, 2, "THIEF")
        add(4, 2, "SOCKET")
        add(5, 2, "HINT")

        add_series(6, 2, "EXIT", 4)

        add(10, 2, "ICE_BLOCK")
        add(11, 2, "ICE_BLOCK_TRANSPARENT")
        add(12, 2, "BONUS_1K")
        add(13, 2, "BONUS_100")
        add(14, 2, "BONUS_10")
        add(15, 2, "BONUS_X2")

        # Process the 7-segment display digits.
        for x in range(12):
            i = x * 24
            j = 3 * SIZE
            img = raw.crop((i, j, i + 24, j + SIZE))
            base32 = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
            base32.paste(img, (6, 0), img)
            lab = str(x) if x < 10 else {10: "BLUE", 11: "BLACK"}[x]
            lib[f"DIGIT_{lab}"] = base32

        add(9, 3, "GREEN_CHIP")
        add(10, 3, "EXTRA_CHIP")
        add(11, 3, "CHIP")
        add(12, 3, "BRIBE")
        add(13, 3, "SPEED_BOOTS")
        add(14, 3, "CANOPY")
        add(15, 3, "CANOPY_TRANSPARENT")

        add_series(0, 4, "TNT", 5)

        add(5, 4, "BOMB")
        add(6, 4, "GREEN_BOMB")

        # Process tiny explosions at 7, 4
        add16(7, 4, 0, "EXPLOSION_16")
        add16(7, 4, 1, "EXPLOSION_16_1")
        add16(7, 4, 2, "EXPLOSION_16_2")
        add16(7, 4, 3, "EXPLOSION_16_3")

        add(8, 4, "CUSTOM_FLOOR_GREEN")
        add(9, 4, "CUSTOM_FLOOR_PINK")
        add(10, 4, "CUSTOM_FLOOR_YELLOW")
        add(11, 4, "CUSTOM_FLOOR_BLUE")
        add(12, 4, "CUSTOM_WALL_GREEN")
        add(13, 4, "CUSTOM_WALL_PINK")
        add(14, 4, "CUSTOM_WALL_YELLOW")
        add(15, 4, "CUSTOM_WALL_BLUE")

        add_series(0, 5, "EXPLOSION", 4)
        add_series(4, 5, "SPLASH", 4)

        add(8, 5, "FLAME_OFF")

        add_series(9, 5, "FLAME_ON", 3)

        add(12, 5, "GREEN_WALL_REAL")
        add(13, 5, "GREEN_WALL_FAKE")
        add(14, 5, "NOT_ALLOWED_MARKER")
        add(15, 5, "DIRECTIONAL_BLOCK")
        add(0, 6, "FLIPPERS")
        add(1, 6, "FIRE_BOOTS")
        add(2, 6, "SKATES")
        add(3, 6, "SUCTION_BOOTS")
        add(4, 6, "DIRT_BOOTS")
        add(5, 6, "LIGHTNING_TOOL")
        add(6, 6, "SELECTION_BULLSEYE")
        add(7, 6, "SELECTION_CIRCLE")
        add(8, 6, "TANK_BUTTON")
        add(9, 6, "GREEN_BUTTON")
        add(10, 6, "CLONE_BUTTON")
        add(11, 6, "TRAP_BUTTON")
        add(12, 6, "PINK_BUTTON")
        add(13, 6, "BLACK_BUTTON")
        add(14, 6, "ORANGE_BUTTON")
        add(15, 6, "YELLOW_TANK_BUTTON")

        add_directional(0, 7, "ANT", 4)
        add_directional(0, 8, "TANK", 2)
        add_directional(8, 8, "GLIDER", 2)

        # Process toggle floors & walls
        inner_wall_img = tile(8, 9)
        for x in range(8):
            floor_img = tile(x, 9)
            wall_img = flatten(floor_img, inner_wall_img)
            n1, n2 = "TOGGLE_FLOOR", "TOGGLE_WALL"
            if x // 4 == 1:
                n1, n2 = f"PURPLE_{n1}", f"PURPLE_{n2}"
            if x % 4 > 0:
                n1, n2 = f"{n1}_{x % 4}", f"{n2}_{x % 4}"
            lib[n1] = floor_img
            lib[n2] = wall_img

        add(9, 9, "TRAP")
        add(10, 9, "TRAP_SHUT")
        add(11, 9, "AREA_BUTTON")

        add_series(12, 9, "FIREBALL", 4)

        add(0, 10, "BLUE_WALL_REAL")

        # ------------------
        # Process thin walls
        # ------------------
        horiz = tile(1, 10)
        vert = tile(2, 10)
        offset = 3
        n = create_bounding_box_transparency(horiz, (0, 0, 32, offset))
        e = create_bounding_box_transparency(vert, (32 - offset, 0, 32, 32))
        s = create_bounding_box_transparency(horiz, (0, 32 - offset, 32, 32))
        w = create_bounding_box_transparency(vert, (0, 0, offset, 32))
        for i, d in enumerate("NESW"):
            lib[f"PANEL_{d}"] = (n, e, s, w)[i]

        # ------------------
        # Process directional block arrows
        # ------------------
        arrows = tile(3, 10)
        offset = 6
        n = create_bounding_box_transparency(arrows, (0, 0, 32, offset))
        e = create_bounding_box_transparency(arrows, (32 - offset, 0, 32, 32))
        s = create_bounding_box_transparency(arrows, (0, 32 - offset, 32, 32))
        w = create_bounding_box_transparency(arrows, (0, 0, offset, 32))
        for i, d in enumerate("NESW"):
            lib[f"DIRECTIONAL_BLOCK_ARROW_{d}"] = (n, e, s, w)[i]

        add_series(4, 10, "TELEPORT", 4)

        add(8, 10, "POP_UP_WALL")
        add(9, 10, "GRAVEL")

        add_series(10, 10, "BALL", 5)

        add(15, 10, "STEEL_WALL")

        add_directional(0, 11, "TEETH", 3, dirs="SEW")

        add(9, 11, "REVOLVING_DOOR_SW")
        add(10, 11, "REVOLVING_DOOR_NW")
        add(11, 11, "REVOLVING_DOOR_NE")
        add(12, 11, "REVOLVING_DOOR_SE")
        add(13, 11, "REVOLVING_DOOR_BASE")

        # ------------------
        # Process wire tunnels.
        # ------------------
        tunnels = tile(14, 11)
        offset = 7
        n = create_bounding_box_transparency(tunnels, (0, 0, 32, offset))
        e = create_bounding_box_transparency(tunnels, (32 - offset, 0, 32, 32))
        s = create_bounding_box_transparency(tunnels, (0, 32 - offset, 32, 32))
        w = create_bounding_box_transparency(tunnels, (0, 0, offset, 32))
        for i, d in enumerate("NESW"):
            lib[f"WIRE_TUNNEL_{d}"] = (n, e, s, w)[i]

        add(15, 11, "TIME_PENALTY")

        add_directional(0, 12, "PARAMECIUM", 3)

        add(12, 12, "FOIL")

        add_series(13, 12, "TURTLE", 3)

        add(0, 13, "WALKER")

        lib["WALKER_VERTICAL_1"] = tall_tile(1, 13)
        lib["WALKER_VERTICAL_2"] = tall_tile(2, 13)
        lib["WALKER_VERTICAL_3"] = tall_tile(3, 13)
        lib["WALKER_VERTICAL_4"] = tall_tile(4, 13)
        lib["WALKER_VERTICAL_5"] = tall_tile(5, 13)
        lib["WALKER_VERTICAL_6"] = tall_tile(6, 13)
        lib["WALKER_VERTICAL_7"] = tall_tile(7, 13)

        lib["WALKER_HORIZONTAL_1"] = wide_tile(8, 13)
        lib["WALKER_HORIZONTAL_2"] = wide_tile(10, 13)
        lib["WALKER_HORIZONTAL_3"] = wide_tile(12, 13)
        lib["WALKER_HORIZONTAL_4"] = wide_tile(14, 13)
        lib["WALKER_HORIZONTAL_5"] = wide_tile(8, 14)
        lib["WALKER_HORIZONTAL_6"] = wide_tile(10, 14)
        lib["WALKER_HORIZONTAL_7"] = wide_tile(12, 14)

        add(14, 14, "TOGGLE_CLOCK")
        add(15, 14, "TIME_BONUS")

        add(0, 15, "BLOB")
        lib["BLOB_VERTICAL_1"] = tall_tile(1, 15)
        lib["BLOB_VERTICAL_2"] = tall_tile(2, 15)
        lib["BLOB_VERTICAL_3"] = tall_tile(3, 15)
        lib["BLOB_VERTICAL_4"] = tall_tile(4, 15)
        lib["BLOB_VERTICAL_5"] = tall_tile(5, 15)
        lib["BLOB_VERTICAL_6"] = tall_tile(6, 15)
        lib["BLOB_VERTICAL_7"] = tall_tile(7, 15)

        lib["BLOB_HORIZONTAL_1"] = wide_tile(8, 15)
        lib["BLOB_HORIZONTAL_2"] = wide_tile(10, 15)
        lib["BLOB_HORIZONTAL_3"] = wide_tile(12, 15)
        lib["BLOB_HORIZONTAL_4"] = wide_tile(14, 15)
        lib["BLOB_HORIZONTAL_5"] = wide_tile(8, 16)
        lib["BLOB_HORIZONTAL_6"] = wide_tile(10, 16)
        lib["BLOB_HORIZONTAL_7"] = wide_tile(12, 16)

        add(0, 16, "SELECTION_BOX_1")
        add(14, 16, "MIMIC")
        add(15, 16, "SELECTION_BOX_2")

        add_directional(0, 17, "BLUE_TEETH", 2, dirs="SEW")

        add(6, 17, "BOWLING_BALL")
        add(7, 17, "BOWLING_BALL_1")

        add_directional(8, 17, "YELLOW_TANK", 2)

        add_series(0, 18, "ROVER", 10)

        for i, d in enumerate("NEWS"):
            lib[f"ROVER_FACE_{d}"] = compass_paste_16(tile16(10, 18, i), d)

        add(11, 18, "SECRET_EYE")

        add_directional(12, 18, "GHOST", 1)

        add(0, 19, "FORCE_N")
        add(1, 19, "FORCE_S")
        add(2, 19, "FORCE_E")

        add_series(4, 19, "GREEN_TELEPORT", 4)
        add_series(8, 19, "YELLOW_TELEPORT", 4)
        add_series(12, 19, "TRANSMOGRIFIER", 4)

        add(2, 20, "FORCE_W")

        add_series(4, 20, "RED_TELEPORT", 4)
        add_series(8, 20, "SLIME", 8)
        add_series(0, 21, "FORCE_RANDOM", 8)

        add_directional(8, 21, "LATCH_GATE_R", 1)

        add(12, 21, "SWITCH_OFF")
        add(13, 21, "SWITCH_ON")
        add(14, 21, "SWITCH_BLANK")
        add(15, 21, "KEY_THIEF")

        add_directional(0, 22, "PLAYER", 8)
        add_directional(0, 24, "PLAYER_SWIMMING", 2)
        add_directional(8, 24, "PLAYER_PUSHING", 1)
        add_series(12, 24, "WATER", 4)

        add_directional(0, 25, "NOT_GATE", 1)
        add_directional(4, 25, "AND_GATE", 1)
        add_directional(8, 25, "OR_GATE", 1)
        add_directional(12, 25, "XOR_GATE", 1)
        add_directional(0, 26, "LATCH_GATE_L", 1)
        add_directional(4, 26, "NAND_GATE", 1)

        add(8, 26, "WIRE_FLOOR_JUNCTION")
        add(9, 26, "WIRE_WALL_JUNCTION")
        add(10, 26, "WIRE_FLOOR_OVERPASS")
        add(11, 26, "WIRE_WALL_OVERPASS")
        add(12, 26, "SPOOL")
        add(13, 26, "LOGIC_OFF_COLOR")
        add(14, 26, "DIGIT_DISPLAY")
        add(15, 26, "LOGIC_ON_COLOR")

        add_directional(0, 27, "PLAYER_2", 8)
        add_directional(0, 29, "PLAYER_2_SWIMMING", 2)
        add_directional(8, 29, "PLAYER_2_PUSHING", 1)
        add_series(12, 29, "FIRE", 4)

        add(0, 30, "RR_TIES_NE")
        add(1, 30, "RR_TIES_SE")
        add(2, 30, "RR_TIES_SW")
        add(3, 30, "RR_TIES_NW")
        add(4, 30, "RR_TIES_HORIZONTAL")
        add(5, 30, "RR_TIES_VERTICAL")
        add(6, 30, "RR_SWITCH")
        add(7, 30, "RR_RED_NE")
        add(8, 30, "RR_RED_SE")
        add(9, 30, "RR_RED_SW")
        add(10, 30, "RR_RED_NW")
        add(11, 30, "RR_RED_HORIZONTAL")
        add(12, 30, "RR_RED_VERTICAL")
        add(13, 30, "RR_NE")
        add(14, 30, "RR_SE")
        add(15, 30, "RR_SW")
        add(0, 31, "RR_NW")
        add(1, 31, "RR_HORIZONTAL")
        add(2, 31, "RR_VERTICAL")
        add(3, 31, "RR_TOOL")
        add(4, 31, "DIRT")
        add(5, 31, "MALE_ONLY")
        add(6, 31, "FEMALE_ONLY")
        add(7, 31, "HOOK")

        # ------------------
        # Process cloner arrows.
        # ------------------
        arrows = tile(8, 31)
        offset = 6
        n = create_bounding_box_transparency(arrows, (0, 0, 32, offset))
        e = create_bounding_box_transparency(arrows, (32 - offset, 0, 32, 32))
        s = create_bounding_box_transparency(arrows, (0, 32 - offset, 32, 32))
        w = create_bounding_box_transparency(arrows, (0, 0, offset, 32))
        for i, d in enumerate("NESW"):
            lib[f"CLONER_ARROW_{d}"] = (n, e, s, w)[i]
        lib["CLONER_CENTER"] = create_bounding_box_transparency(arrows, (
            offset, offset, 32 - offset, 32 - offset))

        add(9, 31, "INV_WALL_PERM")
        add(10, 31, "BLUE_WALL_FAKE")
        add(11, 31, "INV_WALL_APP")

        add16(12, 31, 0, "EDITOR_FLOOR")
        add16(12, 31, 1, "EDITOR_RR_SWITCH")
        add16(12, 31, 2, "EDITOR_ROTATE_R")
        add16(12, 31, 3, "EDITOR_ROTATE_L")

        add16(13, 31, 0, "EDITOR_2X")
        add16(13, 31, 1, "EDITOR_SPOOL")
        add16(13, 31, 2, "EDITOR_1X")
        add16(13, 31, 3, "EDITOR_4X")

        n = tile16(14, 31, 0)
        e = tile16(14, 31, 1)
        s = tile16(15, 31, 0)
        w = tile16(15, 31, 1)
        for i, d in enumerate("NESW"):
            lib[f"ARROW_{d}"] = compass_paste_16((n, e, s, w)[i], d)

        add16(14, 31, 2, "EDITOR_SELECT_1")
        add16(14, 31, 3, "EDITOR_SELECT_2")
        add16(15, 31, 2, "EDITOR_BUTTON_UNPRESSED")
        add16(15, 31, 3, "EDITOR_BUTTON_PRESSED")

        return spriteset
