from dataclasses import dataclass
from typing import Optional, Literal

from cc_tools.c2m_element import C2MElement


@dataclass(slots=True)
class C2MCell:
    """
    Represents a single cell on the map. Each cell can contain up to five
    possible C2MElement objects (panel, mob, not_allowed, pickup, terrain),
    each of which may or may not be present. Using slots=True ensures there
    is no __dict__ per instance, conserving memory. Each attribute defaults to None.
    """
    panel: Optional[C2MElement] = None
    mob: Optional[C2MElement] = None
    not_allowed: Optional[C2MElement] = None
    pickup: Optional[C2MElement] = None
    terrain: Optional[C2MElement] = None

    def __repr__(self) -> str:
        """
        Return a string representation that includes only the fields
        (panel, mob, not_allowed, pickup, terrain) which are not None.
        Example:
            C2MCell(mob=C2MElement(id=CC2.CHIP, ...), terrain=C2MElement(id=CC2.FLOOR, ...))
        """
        fields = [
            f"{name}={value!r}"
            for name, value in self.__dict__.items()
            if value is not None
        ]
        return f"C2MCell({', '.join(fields)})"

    # ----------------------------------------------------------------------
    #  Rotation helpers
    # ----------------------------------------------------------------------
    _LAYERS = ("panel", "mob", "not_allowed", "pickup", "terrain")

    def _rotated(self, turn: Literal["right", "left", "reverse"]) -> "C2MCell":
        """
        Internal helper used by .right(), .left() and .reverse().
        Produces a *new* C2MCell whose non-empty elements are rotated.
        """
        kwargs = {}
        for layer in self._LAYERS:
            elt = getattr(self, layer)
            if elt is not None:                         # C2MElement already provides .right/.left/.reverse
                kwargs[layer] = getattr(elt, turn)()    # call it, store rotated copy
        return C2MCell(**kwargs)

    def right(self) -> "C2MCell":
        """Return a new cell rotated 90° clockwise."""
        return self._rotated("right")

    def left(self) -> "C2MCell":
        """Return a new cell rotated 90° counter-clockwise."""
        return self._rotated("left")

    def reverse(self) -> "C2MCell":
        """Return a new cell rotated 180°."""
        return self._rotated("reverse")

    # ----------------------------------------------------------------------
    #  Mutating helpers
    # ----------------------------------------------------------------------
    def add(self, element: "C2MElement") -> "C2MCell":
        """
        Insert or replace an element in the correct layer, as decided
        by `element.layer()`.  Returns *self* so you can chain calls.

            cell.add(e1).add(e2)
        """
        layer = element.layer()
        if layer not in self._LAYERS:
            raise ValueError(f"unrecognised layer {layer!r} for {element!r}")
        setattr(self, layer, element)
        return self

    def clear(self) -> "C2MCell":
        """
        Remove everything from the cell (sets all layers to None).
        Returns *self* for chaining.
        """
        for layer in self._LAYERS:
            setattr(self, layer, None)
        return self