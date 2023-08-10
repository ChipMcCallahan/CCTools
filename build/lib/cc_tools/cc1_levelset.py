"""Class that represents a CC1 Levelset."""
from .cc1_level import CC1Level


class CC1Levelset:
    """Class that represents a CC1 Levelset."""

    # pylint: disable=too-few-public-methods
    def __init__(self, parsed=None):
        self.levels = [CC1Level(level) for level in parsed.levels] if parsed else []

    def __str__(self):
        return f"{{CC1Levelset, {len(self.levels)} levels}}"
