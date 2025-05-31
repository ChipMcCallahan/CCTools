from dataclasses import dataclass
from typing import Optional, List

from cc_tools.cc2 import CC2

_ORDER = "NESWC"
def _canon(s: str | None) -> str | None:
    return "".join(ch for ch in _ORDER if s and ch in s) if s else None

@dataclass(slots=True)
class C2MElement:
    """
    A memory-efficient dataclass that has 10 optional fields corresponding to
    typical modifiers. Using slots=True ensures there is no __dict__ per instance,
    conserving memory. Each attribute defaults to None.
    """
    id: CC2
    wires: Optional[str] = None
    wire_tunnels: Optional[str] = None
    char: Optional[str] = None
    direction: Optional[str] = None
    directions: Optional[str] = None
    color: Optional[str] = None
    gate: Optional[str] = None
    tracks: Optional[List[str]] = None
    active_track: Optional[str] = None
    initial_entry: Optional[str] = None

    def __repr__(self) -> str:
        included = []
        for f in fields(self):  # type: ignore
            val = getattr(self, f.name)
            if val is not None:
                included.append(f"{f.name}={val!r}")
        return f"{self.__class__.__name__}({', '.join(included)})"

    def layer(self) -> str:
        return self.id.layer()

    # ------------------------------------------------------------------
    #  Rotation helpers  (class-level constants)
    # ------------------------------------------------------------------
    _ORDER        = "NESW"
    _DIR_RIGHT    = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
    _DIR_LEFT     = {v: k for k, v in _DIR_RIGHT.items()}
    _DIR_REV      = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    _ARROW_RIGHT  = {'↑': '→', '→': '↓', '↓': '←', '←': '↑'}
    _ARROW_LEFT   = {v: k for k, v in _ARROW_RIGHT.items()}
    _ARROW_REV    = {'↑': '↓', '↓': '↑', '→': '←', '←': '→'}

    _TRACK_RIGHT  = {
        'NE': 'SE', 'SE': 'SW', 'SW': 'NW', 'NW': 'NE',
        'HORIZONTAL': 'VERTICAL', 'VERTICAL': 'HORIZONTAL',
        'SWITCH': 'SWITCH'
    }
    _TRACK_LEFT   = {v: k for k, v in _TRACK_RIGHT.items()}
    _TRACK_REV    = {
        'NE': 'SW', 'SW': 'NE', 'SE': 'NW', 'NW': 'SE',
        'HORIZONTAL': 'HORIZONTAL', 'VERTICAL': 'VERTICAL', 'SWITCH': 'SWITCH'
    }

    _ACTIVE_RIGHT = {
        'NE': 'SE', 'SE': 'SW', 'SW': 'NW', 'NW': 'NE',
        'HORIZONTAL': 'VERTICAL', 'VERTICAL': 'HORIZONTAL'
    }
    _ACTIVE_LEFT  = {v: k for k, v in _ACTIVE_RIGHT.items()}
    _ACTIVE_REV   = {
        'NE': 'SW', 'SW': 'NE', 'SE': 'NW', 'NW': 'SE',
        'HORIZONTAL': 'HORIZONTAL', 'VERTICAL': 'VERTICAL'
    }

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------
    def __post_init__(self):
        # canonicalise directional sets
        self.wires        = _canon(self.wires)
        self.wire_tunnels = _canon(self.wire_tunnels)
        self.directions   = _canon(self.directions)

    def _rotate_compound(self, s: str, dmap: dict[str, str]) -> str:
        """
        Rotate a compound direction string like "NE" or "NWC".
        Canopy 'C' (if present) is preserved at the end.
        """
        if not s:
            return s
        canopy = 'C' in s
        core   = ''.join(ch for ch in s if ch in self._ORDER)
        out    = "".join(dmap[ch] for ch in reversed(core))  # reverse order like CC2 suffixes
        if canopy:
            out += 'C'
        return out

    def _rotate_set_string(self, s: str, dmap: dict[str, str]) -> str:
        """
        Rotate a set–style string (order-insensitive), e.g. wires "NES".
        The result is canonicalised to ORDER.
        """
        if not s:
            return s
        rotated = {dmap.get(ch, ch) for ch in s}
        return "".join(ch for ch in self._ORDER if ch in rotated)

    def _rotated(
        self,
        dmap: dict[str, str],
        arrow: dict[str, str],
        tmap: dict[str, str],
        amap: dict[str, str],
        id_turn: str
    ) -> "C2MElement":
        # --- rotate the enum id (directional variants handled by CC2) ---
        new_id = getattr(self.id, id_turn)()  # .right() / .left() / .reverse()

        # --- simple one-letter direction ---
        new_direction      = dmap.get(self.direction, self.direction) if self.direction else None

        # --- compound direction strings ---
        new_directions     = self._rotate_compound(self.directions, dmap) if self.directions else None
        new_wires          = self._rotate_set_string(self.wires, dmap)    if self.wires else None
        new_wire_tunnels   = self._rotate_set_string(self.wire_tunnels, dmap) if self.wire_tunnels else None

        # --- railroad specifics ---
        new_tracks         = [tmap.get(t, t) for t in self.tracks] if self.tracks else None
        new_active_track   = amap.get(self.active_track, self.active_track) if self.active_track else None
        new_initial_entry  = dmap.get(self.initial_entry, self.initial_entry) if self.initial_entry else None

        # --- arrow character on letter tiles ---
        new_char = arrow.get(self.char, self.char) if self.char else None

        # --- build the rotated copy ---
        return C2MElement(
            id            = new_id,
            wires         = new_wires,
            wire_tunnels  = new_wire_tunnels,
            char          = new_char,
            direction     = new_direction,
            directions    = new_directions,
            color         = self.color,
            gate          = self.gate,
            tracks        = new_tracks,
            active_track  = new_active_track,
            initial_entry = new_initial_entry,
        )

    # ------------------------------------------------------------------
    #  Public rotation API
    # ------------------------------------------------------------------
    def right(self) -> "C2MElement":
        """Return a 90-degree clockwise-rotated copy of this element."""
        return self._rotated(
            self._DIR_RIGHT, self._ARROW_RIGHT,
            self._TRACK_RIGHT, self._ACTIVE_RIGHT, "right"
        )

    def left(self) -> "C2MElement":
        """Return a 90-degree counter-clockwise-rotated copy of this element."""
        return self._rotated(
            self._DIR_LEFT, self._ARROW_LEFT,
            self._TRACK_LEFT, self._ACTIVE_LEFT, "left"
        )

    def reverse(self) -> "C2MElement":
        """Return a 180-degree-rotated copy of this element."""
        return self._rotated(
            self._DIR_REV, self._ARROW_REV,
            self._TRACK_REV, self._ACTIVE_REV, "reverse"
        )

    # ------------------------------------------------------------------
    # 1) Tiles with wire/wire-tunnel modifiers
    # ------------------------------------------------------------------
    @staticmethod
    def floor(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.FLOOR, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def steel_wall(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.STEEL_WALL, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def transmogrifier(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.TRANSMOGRIFIER, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def blue_teleport(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.BLUE_TELEPORT, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def red_teleport(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.RED_TELEPORT, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def pink_button(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.PINK_BUTTON, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def black_button(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.BLACK_BUTTON, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def switch_on(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.SWITCH_ON, wires=wires, wire_tunnels=wire_tunnels)

    @staticmethod
    def switch_off(*, wires: str = "", wire_tunnels: str = "") -> "C2MElement":
        return C2MElement(id=CC2.SWITCH_OFF, wires=wires, wire_tunnels=wire_tunnels)

    # ------------------------------------------------------------------
    # 2) Letter-tile (single-char modifier)
    # ------------------------------------------------------------------
    @staticmethod
    def letter_tile_space(char: str | None = None) -> "C2MElement":
        return C2MElement(id=CC2.LETTER_TILE_SPACE, char=char)
    
    @staticmethod
    def letter_tile_n() -> "C2MElement":
        return C2MElement(id=CC2.LETTER_TILE_SPACE, char="↑")

    @staticmethod
    def letter_tile_e() -> "C2MElement":
        return C2MElement(id=CC2.LETTER_TILE_SPACE, char="→")

    @staticmethod
    def letter_tile_s() -> "C2MElement":
        return C2MElement(id=CC2.LETTER_TILE_SPACE, char="↓")

    @staticmethod
    def letter_tile_w() -> "C2MElement":
        return C2MElement(id=CC2.LETTER_TILE_SPACE, char="←")

    # ------------------------------------------------------------------
    # 3) Clone machine (four-direction bitmask)
    # ------------------------------------------------------------------
    @staticmethod
    def clone_machine(directions: str = "") -> "C2MElement":
        return C2MElement(id=CC2.CLONE_MACHINE, directions=directions)

    # ------------------------------------------------------------------
    # 4) Custom floor / wall color variants
    # ------------------------------------------------------------------
    @staticmethod
    def _custom(cid, col): return C2MElement(id=cid, color=col)

    # Custom floors
    @staticmethod
    def custom_floor_green():  return C2MElement._custom(CC2.CUSTOM_FLOOR, "Green")
    @staticmethod
    def custom_floor_pink():   return C2MElement._custom(CC2.CUSTOM_FLOOR, "Pink")
    @staticmethod
    def custom_floor_yellow(): return C2MElement._custom(CC2.CUSTOM_FLOOR, "Yellow")
    @staticmethod
    def custom_floor_blue():   return C2MElement._custom(CC2.CUSTOM_FLOOR, "Blue")

    # Custom walls
    @staticmethod
    def custom_wall_green():   return C2MElement._custom(CC2.CUSTOM_WALL, "Green")
    @staticmethod
    def custom_wall_pink():    return C2MElement._custom(CC2.CUSTOM_WALL, "Pink")
    @staticmethod
    def custom_wall_yellow():  return C2MElement._custom(CC2.CUSTOM_WALL, "Yellow")
    @staticmethod
    def custom_wall_blue():    return C2MElement._custom(CC2.CUSTOM_WALL, "Blue")

    # ------------------------------------------------------------------
    # 5) Logic-gate (gate string)
    # ------------------------------------------------------------------
    @staticmethod
    def _gate(g, d): return C2MElement(id=CC2.LOGIC_GATE, gate=g, direction=d)

    # Inverter
    @staticmethod
    def inverter_n(): return C2MElement._gate("Inverter", "N")
    @staticmethod
    def inverter_e(): return C2MElement._gate("Inverter", "E")
    @staticmethod
    def inverter_s(): return C2MElement._gate("Inverter", "S")
    @staticmethod
    def inverter_w(): return C2MElement._gate("Inverter", "W")

    # LatchCW
    @staticmethod
    def latch_cw_n(): return C2MElement._gate("LatchCW", "N")
    @staticmethod
    def latch_cw_e(): return C2MElement._gate("LatchCW", "E")
    @staticmethod
    def latch_cw_s(): return C2MElement._gate("LatchCW", "S")
    @staticmethod
    def latch_cw_w(): return C2MElement._gate("LatchCW", "W")

    # LatchCCW
    @staticmethod
    def latch_ccw_n(): return C2MElement._gate("LatchCCW", "N")
    @staticmethod
    def latch_ccw_e(): return C2MElement._gate("LatchCCW", "E")
    @staticmethod
    def latch_ccw_s(): return C2MElement._gate("LatchCCW", "S")
    @staticmethod
    def latch_ccw_w(): return C2MElement._gate("LatchCCW", "W")

    # AND gate
    @staticmethod
    def and_gate_n(): return C2MElement._gate("AND", "N")
    @staticmethod
    def and_gate_e(): return C2MElement._gate("AND", "E")
    @staticmethod
    def and_gate_s(): return C2MElement._gate("AND", "S")
    @staticmethod
    def and_gate_w(): return C2MElement._gate("AND", "W")

    # OR gate
    @staticmethod
    def or_gate_n(): return C2MElement._gate("OR", "N")
    @staticmethod
    def or_gate_e(): return C2MElement._gate("OR", "E")
    @staticmethod
    def or_gate_s(): return C2MElement._gate("OR", "S")
    @staticmethod
    def or_gate_w(): return C2MElement._gate("OR", "W")

    # XOR gate
    @staticmethod
    def xor_gate_n(): return C2MElement._gate("XOR", "N")
    @staticmethod
    def xor_gate_e(): return C2MElement._gate("XOR", "E")
    @staticmethod
    def xor_gate_s(): return C2MElement._gate("XOR", "S")
    @staticmethod
    def xor_gate_w(): return C2MElement._gate("XOR", "W")

    # NAND gate
    @staticmethod
    def nand_gate_n(): return C2MElement._gate("NAND", "N")
    @staticmethod
    def nand_gate_e(): return C2MElement._gate("NAND", "E")
    @staticmethod
    def nand_gate_s(): return C2MElement._gate("NAND", "S")
    @staticmethod
    def nand_gate_w(): return C2MElement._gate("NAND", "W")

    # ── Voodoo (hex argument) ─────────────────────────────────────────
    @staticmethod
    def voodoo(hex_val: int) -> "C2MElement":
        # hex_val: An integer 0–255 that will be formatted as two-digit hex.
        return C2MElement(id=CC2.LOGIC_GATE, gate=f"Voodoo_{hex_val:02X}")

    # ── Counter (digit 0–9) ───────────────────────────────────────────
    @staticmethod
    def counter(digit: int) -> "C2MElement":
        d = digit if 0 <= digit <= 9 else 0
        return C2MElement(id=CC2.LOGIC_GATE, gate=f"Counter_{d}")

    # ------------------------------------------------------------------
    # 6) Railroad-track (keyword modifiers)
    # ------------------------------------------------------------------
    @staticmethod
    def railroad_track(
        *,
        tracks: list[str] | None = None,
        active_track: str | None = None,
        initial_entry: str | None = None
    ) -> "C2MElement":
        return C2MElement(
            id=CC2.RAILROAD_TRACK,
            tracks=tracks,
            active_track=active_track,
            initial_entry=initial_entry
        )

    # ------------------------------------------------------------------
    # 7) Thin-wall canopy & directional block (direction string modifier)
    # ------------------------------------------------------------------
    @staticmethod
    def thin_wall_canopy(directions: str = "") -> "C2MElement":
        return C2MElement(id=CC2.THIN_WALL_CANOPY, directions=directions)

    @staticmethod
    def directional_block(directions: str = "") -> "C2MElement":
        return C2MElement(id=CC2.DIRECTIONAL_BLOCK, directions=directions)

    # ------------------------------------------------------------------
    # 8) Mobs
    # ------------------------------------------------------------------
    @staticmethod
    def ant_n() -> "C2MElement": return C2MElement(id=CC2.ANT, direction="N")
    @staticmethod
    def ant_e() -> "C2MElement": return C2MElement(id=CC2.ANT, direction="E")
    @staticmethod
    def ant_s() -> "C2MElement": return C2MElement(id=CC2.ANT, direction="S")
    @staticmethod
    def ant_w() -> "C2MElement": return C2MElement(id=CC2.ANT, direction="W")

    @staticmethod
    def ball_n() -> "C2MElement": return C2MElement(id=CC2.BALL, direction="N")
    @staticmethod
    def ball_e() -> "C2MElement": return C2MElement(id=CC2.BALL, direction="E")
    @staticmethod
    def ball_s() -> "C2MElement": return C2MElement(id=CC2.BALL, direction="S")
    @staticmethod
    def ball_w() -> "C2MElement": return C2MElement(id=CC2.BALL, direction="W")

    @staticmethod
    def blob_n() -> "C2MElement": return C2MElement(id=CC2.BLOB, direction="N")
    @staticmethod
    def blob_e() -> "C2MElement": return C2MElement(id=CC2.BLOB, direction="E")
    @staticmethod
    def blob_s() -> "C2MElement": return C2MElement(id=CC2.BLOB, direction="S")
    @staticmethod
    def blob_w() -> "C2MElement": return C2MElement(id=CC2.BLOB, direction="W")

    @staticmethod
    def blue_teeth_n() -> "C2MElement": return C2MElement(id=CC2.BLUE_TEETH, direction="N")
    @staticmethod
    def blue_teeth_e() -> "C2MElement": return C2MElement(id=CC2.BLUE_TEETH, direction="E")
    @staticmethod
    def blue_teeth_s() -> "C2MElement": return C2MElement(id=CC2.BLUE_TEETH, direction="S")
    @staticmethod
    def blue_teeth_w() -> "C2MElement": return C2MElement(id=CC2.BLUE_TEETH, direction="W")

    @staticmethod
    def blue_tank_n() -> "C2MElement": return C2MElement(id=CC2.BLUE_TANK, direction="N")
    @staticmethod
    def blue_tank_e() -> "C2MElement": return C2MElement(id=CC2.BLUE_TANK, direction="E")
    @staticmethod
    def blue_tank_s() -> "C2MElement": return C2MElement(id=CC2.BLUE_TANK, direction="S")
    @staticmethod
    def blue_tank_w() -> "C2MElement": return C2MElement(id=CC2.BLUE_TANK, direction="W")

    @staticmethod
    def centipede_n() -> "C2MElement": return C2MElement(id=CC2.CENTIPEDE, direction="N")
    @staticmethod
    def centipede_e() -> "C2MElement": return C2MElement(id=CC2.CENTIPEDE, direction="E")
    @staticmethod
    def centipede_s() -> "C2MElement": return C2MElement(id=CC2.CENTIPEDE, direction="S")
    @staticmethod
    def centipede_w() -> "C2MElement": return C2MElement(id=CC2.CENTIPEDE, direction="W")

    @staticmethod
    def fireball_n() -> "C2MElement": return C2MElement(id=CC2.FIREBALL, direction="N")
    @staticmethod
    def fireball_e() -> "C2MElement": return C2MElement(id=CC2.FIREBALL, direction="E")
    @staticmethod
    def fireball_s() -> "C2MElement": return C2MElement(id=CC2.FIREBALL, direction="S")
    @staticmethod
    def fireball_w() -> "C2MElement": return C2MElement(id=CC2.FIREBALL, direction="W")

    @staticmethod
    def floor_mimic_n() -> "C2MElement": return C2MElement(id=CC2.FLOOR_MIMIC, direction="N")
    @staticmethod
    def floor_mimic_e() -> "C2MElement": return C2MElement(id=CC2.FLOOR_MIMIC, direction="E")
    @staticmethod
    def floor_mimic_s() -> "C2MElement": return C2MElement(id=CC2.FLOOR_MIMIC, direction="S")
    @staticmethod
    def floor_mimic_w() -> "C2MElement": return C2MElement(id=CC2.FLOOR_MIMIC, direction="W")

    @staticmethod
    def glider_n() -> "C2MElement": return C2MElement(id=CC2.GLIDER, direction="N")
    @staticmethod
    def glider_e() -> "C2MElement": return C2MElement(id=CC2.GLIDER, direction="E")
    @staticmethod
    def glider_s() -> "C2MElement": return C2MElement(id=CC2.GLIDER, direction="S")
    @staticmethod
    def glider_w() -> "C2MElement": return C2MElement(id=CC2.GLIDER, direction="W")

    @staticmethod
    def ghost_n() -> "C2MElement": return C2MElement(id=CC2.GHOST, direction="N")
    @staticmethod
    def ghost_e() -> "C2MElement": return C2MElement(id=CC2.GHOST, direction="E")
    @staticmethod
    def ghost_s() -> "C2MElement": return C2MElement(id=CC2.GHOST, direction="S")
    @staticmethod
    def ghost_w() -> "C2MElement": return C2MElement(id=CC2.GHOST, direction="W")

    @staticmethod
    def mirror_chip_n() -> "C2MElement": return C2MElement(id=CC2.MIRROR_CHIP, direction="N")
    @staticmethod
    def mirror_chip_e() -> "C2MElement": return C2MElement(id=CC2.MIRROR_CHIP, direction="E")
    @staticmethod
    def mirror_chip_s() -> "C2MElement": return C2MElement(id=CC2.MIRROR_CHIP, direction="S")
    @staticmethod
    def mirror_chip_w() -> "C2MElement": return C2MElement(id=CC2.MIRROR_CHIP, direction="W")

    @staticmethod
    def mirror_melinda_n() -> "C2MElement": return C2MElement(id=CC2.MIRROR_MELINDA, direction="N")
    @staticmethod
    def mirror_melinda_e() -> "C2MElement": return C2MElement(id=CC2.MIRROR_MELINDA, direction="E")
    @staticmethod
    def mirror_melinda_s() -> "C2MElement": return C2MElement(id=CC2.MIRROR_MELINDA, direction="S")
    @staticmethod
    def mirror_melinda_w() -> "C2MElement": return C2MElement(id=CC2.MIRROR_MELINDA, direction="W")

    @staticmethod
    def red_teeth_n() -> "C2MElement": return C2MElement(id=CC2.RED_TEETH, direction="N")
    @staticmethod
    def red_teeth_e() -> "C2MElement": return C2MElement(id=CC2.RED_TEETH, direction="E")
    @staticmethod
    def red_teeth_s() -> "C2MElement": return C2MElement(id=CC2.RED_TEETH, direction="S")
    @staticmethod
    def red_teeth_w() -> "C2MElement": return C2MElement(id=CC2.RED_TEETH, direction="W")

    @staticmethod
    def rover_n() -> "C2MElement": return C2MElement(id=CC2.ROVER, direction="N")
    @staticmethod
    def rover_e() -> "C2MElement": return C2MElement(id=CC2.ROVER, direction="E")
    @staticmethod
    def rover_s() -> "C2MElement": return C2MElement(id=CC2.ROVER, direction="S")
    @staticmethod
    def rover_w() -> "C2MElement": return C2MElement(id=CC2.ROVER, direction="W")

    @staticmethod
    def walker_n() -> "C2MElement": return C2MElement(id=CC2.WALKER, direction="N")
    @staticmethod
    def walker_e() -> "C2MElement": return C2MElement(id=CC2.WALKER, direction="E")
    @staticmethod
    def walker_s() -> "C2MElement": return C2MElement(id=CC2.WALKER, direction="S")
    @staticmethod
    def walker_w() -> "C2MElement": return C2MElement(id=CC2.WALKER, direction="W")

    @staticmethod
    def yellow_tank_n() -> "C2MElement": return C2MElement(id=CC2.YELLOW_TANK, direction="N")
    @staticmethod
    def yellow_tank_e() -> "C2MElement": return C2MElement(id=CC2.YELLOW_TANK, direction="E")
    @staticmethod
    def yellow_tank_s() -> "C2MElement": return C2MElement(id=CC2.YELLOW_TANK, direction="S")
    @staticmethod
    def yellow_tank_w() -> "C2MElement": return C2MElement(id=CC2.YELLOW_TANK, direction="W")

    @staticmethod
    def chip_n() -> "C2MElement": return C2MElement(id=CC2.CHIP, direction="N")
    @staticmethod
    def chip_e() -> "C2MElement": return C2MElement(id=CC2.CHIP, direction="E")
    @staticmethod
    def chip_s() -> "C2MElement": return C2MElement(id=CC2.CHIP, direction="S")
    @staticmethod
    def chip_w() -> "C2MElement": return C2MElement(id=CC2.CHIP, direction="W")

    @staticmethod
    def melinda_n() -> "C2MElement": return C2MElement(id=CC2.MELINDA, direction="N")
    @staticmethod
    def melinda_e() -> "C2MElement": return C2MElement(id=CC2.MELINDA, direction="E")
    @staticmethod
    def melinda_s() -> "C2MElement": return C2MElement(id=CC2.MELINDA, direction="S")
    @staticmethod
    def melinda_w() -> "C2MElement": return C2MElement(id=CC2.MELINDA, direction="W")

    # ------------------------------------------------------------------
    # 9) All remaining CC2 tiles – simple no-argument factories
    # ------------------------------------------------------------------
    @staticmethod
    def wall() -> "C2MElement": return C2MElement(id=CC2.WALL)
    @staticmethod
    def ice() -> "C2MElement": return C2MElement(id=CC2.ICE)
    @staticmethod
    def ice_sw() -> "C2MElement": return C2MElement(id=CC2.ICE_SW)
    @staticmethod
    def ice_nw() -> "C2MElement": return C2MElement(id=CC2.ICE_NW)
    @staticmethod
    def ice_ne() -> "C2MElement": return C2MElement(id=CC2.ICE_NE)
    @staticmethod
    def ice_se() -> "C2MElement": return C2MElement(id=CC2.ICE_SE)
    @staticmethod
    def water() -> "C2MElement": return C2MElement(id=CC2.WATER)
    @staticmethod
    def fire() -> "C2MElement": return C2MElement(id=CC2.FIRE)
    @staticmethod
    def force_n() -> "C2MElement": return C2MElement(id=CC2.FORCE_N)
    @staticmethod
    def force_e() -> "C2MElement": return C2MElement(id=CC2.FORCE_E)
    @staticmethod
    def force_s() -> "C2MElement": return C2MElement(id=CC2.FORCE_S)
    @staticmethod
    def force_w() -> "C2MElement": return C2MElement(id=CC2.FORCE_W)
    @staticmethod
    def green_toggle_wall() -> "C2MElement": return C2MElement(id=CC2.GREEN_TOGGLE_WALL)
    @staticmethod
    def green_toggle_floor() -> "C2MElement": return C2MElement(id=CC2.GREEN_TOGGLE_FLOOR)
    @staticmethod
    def yellow_teleport() -> "C2MElement": return C2MElement(id=CC2.YELLOW_TELEPORT)
    @staticmethod
    def green_teleport() -> "C2MElement": return C2MElement(id=CC2.GREEN_TELEPORT)
    @staticmethod
    def exit() -> "C2MElement": return C2MElement(id=CC2.EXIT)
    @staticmethod
    def slime() -> "C2MElement": return C2MElement(id=CC2.SLIME)
    @staticmethod
    def dirt_block() -> "C2MElement": return C2MElement(id=CC2.DIRT_BLOCK)
    @staticmethod
    def ice_block() -> "C2MElement": return C2MElement(id=CC2.ICE_BLOCK)
    @staticmethod
    def thin_wall_s() -> "C2MElement": return C2MElement(id=CC2.THIN_WALL_S)
    @staticmethod
    def thin_wall_e() -> "C2MElement": return C2MElement(id=CC2.THIN_WALL_E)
    @staticmethod
    def thin_wall_se() -> "C2MElement": return C2MElement(id=CC2.THIN_WALL_SE)
    @staticmethod
    def gravel() -> "C2MElement": return C2MElement(id=CC2.GRAVEL)
    @staticmethod
    def green_button() -> "C2MElement": return C2MElement(id=CC2.GREEN_BUTTON)
    @staticmethod
    def blue_button() -> "C2MElement": return C2MElement(id=CC2.BLUE_BUTTON)
    @staticmethod
    def red_door() -> "C2MElement": return C2MElement(id=CC2.RED_DOOR)
    @staticmethod
    def blue_door() -> "C2MElement": return C2MElement(id=CC2.BLUE_DOOR)
    @staticmethod
    def yellow_door() -> "C2MElement": return C2MElement(id=CC2.YELLOW_DOOR)
    @staticmethod
    def green_door() -> "C2MElement": return C2MElement(id=CC2.GREEN_DOOR)
    @staticmethod
    def red_key() -> "C2MElement": return C2MElement(id=CC2.RED_KEY)
    @staticmethod
    def blue_key() -> "C2MElement": return C2MElement(id=CC2.BLUE_KEY)
    @staticmethod
    def yellow_key() -> "C2MElement": return C2MElement(id=CC2.YELLOW_KEY)
    @staticmethod
    def green_key() -> "C2MElement": return C2MElement(id=CC2.GREEN_KEY)
    @staticmethod
    def ic_chip() -> "C2MElement": return C2MElement(id=CC2.IC_CHIP)
    @staticmethod
    def extra_ic_chip() -> "C2MElement": return C2MElement(id=CC2.EXTRA_IC_CHIP)
    @staticmethod
    def chip_socket() -> "C2MElement": return C2MElement(id=CC2.CHIP_SOCKET)
    @staticmethod
    def popup_wall() -> "C2MElement": return C2MElement(id=CC2.POPUP_WALL)
    @staticmethod
    def appearing_wall() -> "C2MElement": return C2MElement(id=CC2.APPEARING_WALL)
    @staticmethod
    def invisible_wall() -> "C2MElement": return C2MElement(id=CC2.INVISIBLE_WALL)
    @staticmethod
    def solid_blue_wall() -> "C2MElement": return C2MElement(id=CC2.SOLID_BLUE_WALL)
    @staticmethod
    def false_blue_wall() -> "C2MElement": return C2MElement(id=CC2.FALSE_BLUE_WALL)
    @staticmethod
    def dirt() -> "C2MElement": return C2MElement(id=CC2.DIRT)
    @staticmethod
    def explosion_animation() -> "C2MElement": return C2MElement(id=CC2.EXPLOSION_ANIMATION)
    @staticmethod
    def red_button() -> "C2MElement": return C2MElement(id=CC2.RED_BUTTON)
    @staticmethod
    def brown_button() -> "C2MElement": return C2MElement(id=CC2.BROWN_BUTTON)
    @staticmethod
    def cleats() -> "C2MElement": return C2MElement(id=CC2.CLEATS)
    @staticmethod
    def suction_boots() -> "C2MElement": return C2MElement(id=CC2.SUCTION_BOOTS)
    @staticmethod
    def fire_boots() -> "C2MElement": return C2MElement(id=CC2.FIRE_BOOTS)
    @staticmethod
    def flippers() -> "C2MElement": return C2MElement(id=CC2.FLIPPERS)
    @staticmethod
    def tool_thief() -> "C2MElement": return C2MElement(id=CC2.TOOL_THIEF)
    @staticmethod
    def bomb() -> "C2MElement": return C2MElement(id=CC2.BOMB)
    @staticmethod
    def open_trap() -> "C2MElement": return C2MElement(id=CC2.OPEN_TRAP)
    @staticmethod
    def trap() -> "C2MElement": return C2MElement(id=CC2.TRAP)
    @staticmethod
    def clone_machine_old() -> "C2MElement": return C2MElement(id=CC2.CLONE_MACHINE_OLD)
    @staticmethod
    def clue() -> "C2MElement": return C2MElement(id=CC2.CLUE)
    @staticmethod
    def force_random() -> "C2MElement": return C2MElement(id=CC2.FORCE_RANDOM)
    @staticmethod
    def gray_button() -> "C2MElement": return C2MElement(id=CC2.GRAY_BUTTON)
    @staticmethod
    def swivel_door_sw() -> "C2MElement": return C2MElement(id=CC2.SWIVEL_DOOR_SW)
    @staticmethod
    def swivel_door_nw() -> "C2MElement": return C2MElement(id=CC2.SWIVEL_DOOR_NW)
    @staticmethod
    def swivel_door_ne() -> "C2MElement": return C2MElement(id=CC2.SWIVEL_DOOR_NE)
    @staticmethod
    def swivel_door_se() -> "C2MElement": return C2MElement(id=CC2.SWIVEL_DOOR_SE)
    @staticmethod
    def time_bonus() -> "C2MElement": return C2MElement(id=CC2.TIME_BONUS)
    @staticmethod
    def stopwatch() -> "C2MElement": return C2MElement(id=CC2.STOPWATCH)
    @staticmethod
    def tnt() -> "C2MElement": return C2MElement(id=CC2.TNT)
    @staticmethod
    def helmet() -> "C2MElement": return C2MElement(id=CC2.HELMET)
    @staticmethod
    def unused_53() -> "C2MElement": return C2MElement(id=CC2.UNUSED_53)
    @staticmethod
    def unused_54() -> "C2MElement": return C2MElement(id=CC2.UNUSED_54)
    @staticmethod
    def unused_55() -> "C2MElement": return C2MElement(id=CC2.UNUSED_55)
    @staticmethod
    def hiking_boots() -> "C2MElement": return C2MElement(id=CC2.HIKING_BOOTS)
    @staticmethod
    def male_only_sign() -> "C2MElement": return C2MElement(id=CC2.MALE_ONLY_SIGN)
    @staticmethod
    def female_only_sign() -> "C2MElement": return C2MElement(id=CC2.FEMALE_ONLY_SIGN)
    @staticmethod
    def unused_5d() -> "C2MElement": return C2MElement(id=CC2.UNUSED_5D)
    @staticmethod
    def flame_jet_off() -> "C2MElement": return C2MElement(id=CC2.FLAME_JET_OFF)
    @staticmethod
    def flame_jet_on() -> "C2MElement": return C2MElement(id=CC2.FLAME_JET_ON)
    @staticmethod
    def orange_button() -> "C2MElement": return C2MElement(id=CC2.ORANGE_BUTTON)
    @staticmethod
    def lightning_bolt() -> "C2MElement": return C2MElement(id=CC2.LIGHTNING_BOLT)
    @staticmethod
    def yellow_tank_button() -> "C2MElement": return C2MElement(id=CC2.YELLOW_TANK_BUTTON)
    @staticmethod
    def unused_67() -> "C2MElement": return C2MElement(id=CC2.UNUSED_67)
    @staticmethod
    def bowling_ball() -> "C2MElement": return C2MElement(id=CC2.BOWLING_BALL)
    @staticmethod
    def time_penalty() -> "C2MElement": return C2MElement(id=CC2.TIME_PENALTY)
    @staticmethod
    def unused_6c() -> "C2MElement": return C2MElement(id=CC2.UNUSED_6C)
    @staticmethod
    def unused_6e() -> "C2MElement": return C2MElement(id=CC2.UNUSED_6E)
    @staticmethod
    def railroad_sign() -> "C2MElement": return C2MElement(id=CC2.RAILROAD_SIGN)
    @staticmethod
    def purple_toggle_floor() -> "C2MElement": return C2MElement(id=CC2.PURPLE_TOGGLE_FLOOR)
    @staticmethod
    def purple_toggle_wall() -> "C2MElement": return C2MElement(id=CC2.PURPLE_TOGGLE_WALL)
    @staticmethod
    def unused_74() -> "C2MElement": return C2MElement(id=CC2.UNUSED_74)
    @staticmethod
    def unused_75() -> "C2MElement": return C2MElement(id=CC2.UNUSED_75)
    @staticmethod
    def modifier_8bit() -> "C2MElement": return C2MElement(id=CC2.MODIFIER_8BIT)
    @staticmethod
    def modifier_16bit() -> "C2MElement": return C2MElement(id=CC2.MODIFIER_16BIT)
    @staticmethod
    def modifier_32bit() -> "C2MElement": return C2MElement(id=CC2.MODIFIER_32BIT)
    @staticmethod
    def unused_79() -> "C2MElement": return C2MElement(id=CC2.UNUSED_79)
    @staticmethod
    def flag_10() -> "C2MElement": return C2MElement(id=CC2.FLAG_10)
    @staticmethod
    def flag_100() -> "C2MElement": return C2MElement(id=CC2.FLAG_100)
    @staticmethod
    def flag_1000() -> "C2MElement": return C2MElement(id=CC2.FLAG_1000)
    @staticmethod
    def solid_green_wall() -> "C2MElement": return C2MElement(id=CC2.SOLID_GREEN_WALL)
    @staticmethod
    def false_green_wall() -> "C2MElement": return C2MElement(id=CC2.FALSE_GREEN_WALL)
    @staticmethod
    def not_allowed_marker() -> "C2MElement": return C2MElement(id=CC2.NOT_ALLOWED_MARKER)
    @staticmethod
    def flag_2x() -> "C2MElement": return C2MElement(id=CC2.FLAG_2X)
    @staticmethod
    def green_bomb() -> "C2MElement": return C2MElement(id=CC2.GREEN_BOMB)
    @staticmethod
    def green_chip() -> "C2MElement": return C2MElement(id=CC2.GREEN_CHIP)
    @staticmethod
    def unused_85() -> "C2MElement": return C2MElement(id=CC2.UNUSED_85)
    @staticmethod
    def unused_86() -> "C2MElement": return C2MElement(id=CC2.UNUSED_86)
    @staticmethod
    def key_thief() -> "C2MElement": return C2MElement(id=CC2.KEY_THIEF)
    @staticmethod
    def steel_foil() -> "C2MElement": return C2MElement(id=CC2.STEEL_FOIL)
    @staticmethod
    def turtle() -> "C2MElement": return C2MElement(id=CC2.TURTLE)
    @staticmethod
    def secret_eye() -> "C2MElement": return C2MElement(id=CC2.SECRET_EYE)
    @staticmethod
    def bribe() -> "C2MElement": return C2MElement(id=CC2.BRIBE)
    @staticmethod
    def speed_boots() -> "C2MElement": return C2MElement(id=CC2.SPEED_BOOTS)
    @staticmethod
    def unused_91() -> "C2MElement": return C2MElement(id=CC2.UNUSED_91)
    @staticmethod
    def hook() -> "C2MElement": return C2MElement(id=CC2.HOOK)
