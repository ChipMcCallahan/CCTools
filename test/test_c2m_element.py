from __future__ import annotations

import inspect
import unittest
from types import FunctionType
from typing import Callable, Iterable, List, get_type_hints

from cc_tools.cc2 import CC2
from cc_tools.c2m_element import C2MElement

def static_factories() -> Iterable[tuple[str, Callable]]:
    """All static convenience factories declared on C2MElement."""
    for name, value in C2MElement.__dict__.items():
        if isinstance(value, staticmethod):               # noqa: E721
            fn: FunctionType = value.__func__
            yield name, fn


class TestFactoryBasics(unittest.TestCase):
    def test_all_factories_return_element(self) -> None:
        """Every factory returns a C2MElement instance and assigns a CC2 id."""
        for name, fn in static_factories():
            sig = inspect.signature(fn)
            # Call only if all parameters have defaults (i.e. optional)
            if all(p.default is not inspect._empty for p in sig.parameters.values()):
                elem: C2MElement = fn()  # type: ignore[arg-type]
                self.assertIsInstance(elem, C2MElement, msg=name)
                self.assertIsInstance(elem.id, CC2, msg=name)

    def test_required_arg_factories(self) -> None:
        lt = C2MElement.letter_tile_space(char="↑")
        self.assertEqual((lt.id, lt.char), (CC2.LETTER_TILE_SPACE, "↑"))

        cm = C2MElement.clone_machine(directions="NESW")
        self.assertEqual((cm.id, cm.directions), (CC2.CLONE_MACHINE, "NESW"))

        self.assertEqual(C2MElement.custom_floor_green().color, "Green")
        self.assertEqual(C2MElement.custom_wall_blue().color, "Blue")

        rt = C2MElement.railroad_track(
            tracks=["NE", "HORIZONTAL"],
            active_track="NE",
            initial_entry="N",
        )
        self.assertEqual(rt.id, CC2.RAILROAD_TRACK)
        self.assertListEqual(rt.tracks or [], ["NE", "HORIZONTAL"])


class TestRotationSimpleFields(unittest.TestCase):
    def test_direction_field(self) -> None:
        elem = C2MElement.blob_n()
        self.assertEqual(elem.right().direction, "E")
        self.assertEqual(elem.left().direction,  "W")
        self.assertEqual(elem.reverse().direction, "S")

    def test_arrow_char(self) -> None:
        e = C2MElement.letter_tile_space(char="↑")
        self.assertEqual(e.right().char, "→")
        self.assertEqual(e.left().char,  "←")
        self.assertEqual(e.reverse().char, "↓")


class TestRotationCompoundFields(unittest.TestCase):
    def test_compound_directions(self) -> None:
        elem = C2MElement.thin_wall_canopy(directions="NW")
        self.assertEqual(elem.right().directions, "NE")
        self.assertEqual(elem.left().directions,  "SW")
        self.assertEqual(elem.reverse().directions, "ES")  # normalized in NESW order

    def test_canopy_preserved(self) -> None:
        elem = C2MElement.thin_wall_canopy(directions="NC")
        self.assertEqual(elem.right().directions, "EC")
        self.assertEqual(elem.left().directions,  "WC")
        self.assertEqual(elem.reverse().directions, "SC")

    def test_wire_sets(self) -> None:
        elem = C2MElement.floor(wires="NES", wire_tunnels="EW")
        r = elem.right()
        self.assertEqual(r.wires,         "ESW")
        self.assertEqual(r.wire_tunnels,  "NS")


class TestRotationRailroad(unittest.TestCase):
    def setUp(self) -> None:
        self.base = C2MElement.railroad_track(
            tracks=["NE", "HORIZONTAL"],
            active_track="NE",
            initial_entry="N",
        )

    def test_track_list(self) -> None:
        self.assertListEqual(self.base.right().tracks, ["SE", "VERTICAL"])
        self.assertListEqual(self.base.left().tracks, ["NW", "VERTICAL"])
        self.assertListEqual(self.base.reverse().tracks, ["SW", "HORIZONTAL"])

    def test_active_and_entry(self) -> None:
        r = self.base.right()
        self.assertEqual(r.active_track,  "SE")
        self.assertEqual(r.initial_entry, "E")

        l = self.base.left()
        self.assertEqual(l.active_track,  "NW")
        self.assertEqual(l.initial_entry, "W")

        rev = self.base.reverse()
        self.assertEqual(rev.active_track,  "SW")
        self.assertEqual(rev.initial_entry, "S")


class TestRotationEnumIDs(unittest.TestCase):
    def test_directional_id(self) -> None:
        f = C2MElement.force_n()
        self.assertEqual(f.right().id, CC2.FORCE_E)
        self.assertEqual(f.left().id,  CC2.FORCE_W)
        self.assertEqual(f.reverse().id, CC2.FORCE_S)

    def test_non_directional_id_unchanged(self) -> None:
        w = C2MElement.wall()
        self.assertIs(w.right().id, w.id)
        self.assertIs(w.left().id,  w.id)
        self.assertIs(w.reverse().id, w.id)


class TestRotationAlgebra(unittest.TestCase):
    def test_left_then_right(self) -> None:
        e = C2MElement.blob_e()
        self.assertEqual(e.left().right(), e)
        self.assertEqual(e.right().left(), e)

    def test_double_right_equals_reverse(self) -> None:
        e = C2MElement.blue_teeth_s()
        self.assertEqual(e.right().right(), e.reverse())


class TestC2MElementCanonicalisation(unittest.TestCase):
    """Verify that __post_init__ sorts directional-set strings to 'NESWC' order."""

    def test_unsorted_strings_are_canonicalised(self):
        elem = C2MElement(
            id=CC2.FLOOR,
            wires="SWEN",            # out of order
            wire_tunnels="WC",       # out of order but already canonical subset
            directions="CNSEW"       # contains all + canopy
        )
        self.assertEqual(elem.wires, "NESW")
        self.assertEqual(elem.wire_tunnels, "WC")   # W then C per canonical order
        self.assertEqual(elem.directions, "NESWC")

    def test_duplicates_and_missing_fields(self):
        elem = C2MElement(
            id=CC2.FLOOR,
            wires="SSSEN",   # duplicates + out of order
            wire_tunnels="", # empty should be treated as None
        )
        self.assertEqual(elem.wires, "NES")         # duplicates removed, canonical order
        self.assertIsNone(elem.wire_tunnels)        # empty string becomes None
        self.assertIsNone(elem.directions)          # untouched field stays None