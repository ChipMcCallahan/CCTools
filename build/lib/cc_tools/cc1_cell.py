"""Class that represents a single CC1 cell with a top and bottom element."""
from .cc1 import CC1


class CC1Cell:
    """Class that represents a single CC1 cell with a top and bottom element."""

    def __init__(self, top=CC1.FLOOR, bottom=CC1.FLOOR):
        self.top, self.bottom = top, bottom

    def __copy__(self):
        return CC1Cell(self.top, self.bottom)

    def __eq__(self, other):
        return (self.top, self.bottom) == (other.top, other.bottom)

    def __str__(self):
        return f"{{CC1Cell top={self.top} bottom={self.bottom}}}"

    def is_valid(self):
        """Check if this cell is invalid due to illegal buried tiles or invalid codes."""
        buried = (self.top not in CC1.mobs() and self.bottom != CC1.FLOOR)
        invalid_code = len({self.top, self.bottom}.intersection(CC1.invalid())) > 0
        buried_mob = self.bottom in CC1.mobs()
        return not (buried or invalid_code or buried_mob)

    def contains(self, elem):
        """Returns true if elem is present in cell.top or cell.bottom."""
        return elem in {self.top, self.bottom}

    def add(self, elem):
        """Intelligently add a CC1 tile here, maintaining validity."""
        is_mob = elem in CC1.mobs()
        mob_here = self.top in CC1.mobs()
        if is_mob:
            # If adding mob to terrain, move the terrain to the bottom layer.
            if not mob_here:
                self.bottom = self.top
            self.top = elem
        else:
            if mob_here:
                # If adding terrain where a mob exists, replace the terrain but not the mob.
                self.bottom = elem
            else:
                self.top = elem

    def remove(self, elem):
        """Intelligently remove a CC1 tile here, maintaining validity. Returns True if cell was
        altered, False if not."""
        if elem == CC1.FLOOR:
            # Floor is default. It can never be removed.
            return False
        if elem == self.top:
            self.top = self.bottom
            self.bottom = CC1.FLOOR
            return True
        if elem == self.bottom:
            self.bottom = CC1.FLOOR
            return True
        return False

    def erase(self):
        """Clear cell by setting top and bottom layers to floor."""
        self.top = CC1.FLOOR
        self.bottom = CC1.FLOOR
