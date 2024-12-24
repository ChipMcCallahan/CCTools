from dataclasses import dataclass
from typing import Optional

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
