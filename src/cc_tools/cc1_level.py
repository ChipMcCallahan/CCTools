"""Class that represents a CC1 level."""
import copy

from .cc1 import CC1
from .cc1_cell import CC1Cell


class CC1Level:
    """Class that represents a CC1 level."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parsed=None):
        self.title = parsed.title if parsed else "Untitled"
        self.time = parsed.time if parsed else 0
        self.chips = parsed.chips if parsed else 0
        self.hint = parsed.hint if parsed else ""
        self.password = parsed.password if parsed else ""
        self.author = parsed.author if parsed else ""
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
