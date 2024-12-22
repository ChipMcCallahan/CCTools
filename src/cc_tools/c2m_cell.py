from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, Union

class Direction(IntEnum):
    N = 0
    E  = 1
    S = 2
    W  = 3

@dataclass
class C2MCell:
    """
    Dataclass to represent a cell (1 or more tiles) in C2M format.
    """
    tile_type: CC2
    direction: Optional[Direction] = None
    lower_layer: Optional[C2MCell] = None

    # Wires (if applicable), default 0 = no wires.
    wire_bitmask: int = 0

    # For track tiles, storing track data (mask, active track, and initial "entered" dir).
    track_mask: int = 0
    track_active: int = 0
    track_enter_dir: Optional[Direction] = None

    # For custom floor/wall styles (0..3), logic gate modifiers, letter tiles, etc.
    custom_style: Optional[int] = None
    logic_modifier: Optional[int] = None
    letter_symbol: Optional[str] = None

    # Raw modifier bytes if this is a MODIFIER tile (0x76, 0x77, 0x78).
    raw_modifier_bytes: bytes = field(default_factory=bytes)

    def __repr__(self) -> str:
        """String representation for debugging."""
        fields = [f"tile_type={self.tile_type.name}"]
        if self.direction is not None:
            fields.append(f"direction={self.direction.name}")
        if self.lower_layer is not None:
            fields.append(f"lower_layer={self.lower_layer}")
        if self.wire_bitmask != 0:
            fields.append(f"wire_bitmask=0x{self.wire_bitmask:02X}")
        if self.track_mask != 0:
            fields.append(f"track_mask=0x{self.track_mask:02X}")
        if self.track_active != 0:
            fields.append(f"track_active=0x{self.track_active:02X}")
        if self.track_enter_dir is not None:
            fields.append(f"track_enter_dir={self.track_enter_dir.name}")
        if self.custom_style is not None:
            fields.append(f"custom_style={self.custom_style}")
        if self.logic_modifier is not None:
            fields.append(f"logic_modifier={self.logic_modifier}")
        if self.letter_symbol is not None:
            fields.append(f"letter_symbol={repr(self.letter_symbol)}")
        if self.raw_modifier_bytes:
            fields.append(f"raw_modifier_bytes={self.raw_modifier_bytes!r}")
        return f"C2MCell({', '.join(fields)})"