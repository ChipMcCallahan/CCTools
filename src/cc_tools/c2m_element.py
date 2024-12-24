from dataclasses import dataclass
from typing import Optional, List

from cc_tools.cc2 import CC2


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
