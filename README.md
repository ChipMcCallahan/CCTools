# CCTools
```
pip install git+https://github.com/ChipMcCallahan/CCTools.git
```
Tools for working with CC1 (DAT) and CC2 (C2M) files.

### [CC1 Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L10-L344)
```python
from cc_tools import CC1
```
This class is basically an enum of CC1 tile codes, along with some very useful utilities as described below.
#### Direction Utils
```python
tank = CC1.TANK_N
print(tank.left())
print(tank.reverse())
print(tank.right())
```
```
CC1.TANK_W
CC1.TANK_S
CC1.TANK_E
```
This works for ice corner tiles such as `CC1.ICE_NW`. If an element cannot be rotated, the same element is returned.  

You can also get the directions on an element, or update the element with new directions.
```python
ice_corner = CC1.ICE_SE
print(ice_corner.dirs())
print(ice_corner.with_dirs("NW"))
```
```
SE
CC1.ICE_NW
```
#### Element Set Utils
Easily make comparisons using prebuilt element sets.
```python
for e in (CC1.TANK_N, CC1.BLOCK, CC1.PLAYER_N, CC1.NOT_USED_0):
    print("-" * 20)
    if e in CC1.tanks():
        print(f"{e} is a tank.")
    if e in CC1.blocks():
        print(f"{e} is a block.")
    if e in CC1.players():
        print(f"{e} is a player.")
    if e in CC1.monsters():
        print(f"{e} is a monster.")
    if e in CC1.mobs():
        print(f"{e} is a mob.")
    if e in CC1.invalid():
        print(f"{e} is invalid.")
```
```
--------------------
CC1.TANK_N is a tank.
CC1.TANK_N is a monster.
CC1.TANK_N is a mob.
--------------------
CC1.BLOCK is a block.
CC1.BLOCK is a mob.
--------------------
CC1.PLAYER_N is a player.
CC1.PLAYER_N is a mob.
--------------------
CC1.NOT_USED_0 is invalid.
```
See [the code](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L196-L344) for a full list of prebuilt element sets.

### [CC1Cell Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L347-L404)
```python
from cc_tools import CC1Cell
```
This class represents a single (x, y) location in a CC1 Level. It holds two CC1 elements (`top` and `bottom`). It can intelligently add and remove elements while doing its best to maintain CC1 validity; however, **it is always recommended to use the CC1Level object to add or remove elements, since the CC1Level object will also update trap controls, clone controls, and movement data**.

```python
cell = CC1Cell(CC1.TEETH_S, CC1.GRAVEL)
print(cell)
cell.add(CC1.BLOB_S)
print(cell)
cell.add(CC1.DIRT)
print(cell)
cell.remove(CC1.BLOB_S)
print(cell)
```
```
{CC1Cell top=CC1.TEETH_S bottom=CC1.GRAVEL}
{CC1Cell top=CC1.BLOB_S bottom=CC1.GRAVEL}
{CC1Cell top=CC1.BLOB_S bottom=CC1.DIRT}
{CC1Cell top=CC1.DIRT bottom=CC1.FLOOR}
```

### [CC1Level Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L407-L490)
```python
from cc_tools import CC1Level
```

#### Properties
- `title`, `chips`, `time`, `password`, and `hint` are all simple properties.
```python
level = CC1Level()
level.title = "Old Frog 2"
level.chips = 30
level.time = 300
level.password = "ABCD"
level.hint = "Remember TMET."
```
- `map` and `movement` (lists) as well as `traps` and `cloners` (dicts) are properties as well and can be accessed directly; however, **they should be edited through utility methods whenever possible**.

#### Utility Methods
- Get or edit map elements with `.at()`, `.add()`, and `.remove()`.
  - Added monsters get appended to `movement`. Deleted monsters get removed from `movement`.
  - If a connected trap/cloner/button is removed, it will get removed from `traps` or `cloners`.
  - If a trap/cloner/button is added, it will not be connected. Use `.connect()` to manually connect traps and cloners.
```python
level.add((5, 0), CC1.TEETH_S)
print(level.at((5, 0)))
level.add((5, 0), CC1.GRAVEL)
print(level.at((5, 0)))
level.remove((5, 0), CC1.TEETH_S)
print(level.at((5, 0)))
```
```
{CC1Cell top=CC1.TEETH_S bottom=CC1.FLOOR}
{CC1Cell top=CC1.TEETH_S bottom=CC1.GRAVEL}
{CC1Cell top=CC1.GRAVEL bottom=CC1.FLOOR}
```
- Connect traps and cloners with `.connect()`.
```python
level = CC1Level()
print(len(level.traps))
level.add((10, 10), CC1.TRAP_BUTTON)
level.add((20, 20), CC1.TRAP)
level.connect((10, 10), (20, 20))
print(len(level.traps))
```
```
0
1
```
- Check if a level is valid with `.is_valid()`.
```python
level = CC1Level()
print(level.is_valid())
level.add((20, 20), CC1.NOT_USED_0)
print(level.is_valid())
```
```
True
False
```
- Count elements in a level with `.count()`.
```python
for i in range(10):
    level.add((i, 0), CC1.CHIP)
print(level.count(CC1.CHIP))
```
```
10
```

### [CC1Levelset Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L493-L498)
```python
from cc_tools import CC1Levelset
```
This class just holds a list of levels.
```python
lset = CC1Levelset()
print(len(lset.levels))
lset.levels.append(CC1Level())
print(len(lset.levels))
```
```
0
1
```

### [DATHandler Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/dat_handler.py#L63-L374)
```python
from cc_tools import DATHandler
```
This class obfuscates everything related to reading and writing CC1 DAT file formats. It can also fetch sets and set names from the Gliderbot repository.
#### Reading and Writing
- `.read()` reads a DAT levelset from the local filesystem and returns a CC1Levelset.
```python
cclp1 = DATHandler.read("CCLP1.dat")
print(len(cclp1.levels))
```
```
149
```
- `.write()` returns the DAT binary format of the given CC1Levelset. If an optional `filename` in specified, it writes to disk.
```python
levelset_binary = DATHandler.write(cc1_levelset)
DATHandler.write(cc1_levelset, filename="local_file.dat")
```
#### Fetching from Gliderbot
- `.fetch_set_names()` returns a list of all available CC1 sets on [Gliderbot](https://bitbusters.club/gliderbot/sets/cc1/)
```python
sets = DATHandler.fetch_set_names()
print(len(sets))
```
```
543
```
- `.fetch_set()` fetches a DAT file from [Gliderbot](https://bitbusters.club/gliderbot/sets/cc1/) and converts it to a CC1Levelset.
    - **Note that currently the filename must exactly match, i.e. "CCLP1.dat" will work but "CCLP1.DAT" will not.**
```python
cclp1 = DATHandler.fetch_set("CCLP1.dat")
print(cclp1)
```
```
{CC1Levelset, 149 levels}
```

### [CC1LevelTransformer Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L501-L641)
```python
from cc_tools import CC1LevelTransformer
```
This class transforms CC1Level objects according to certain rules.

#### Replacements
- `.replace()` intelligently replaces an element or set of elements `old` with an element `new`.
    - Uses `.add()` and `.remove()` methods on CC1Level instance to maintain traps, cloners, movement, and tile validity.
- Example (Replaces all monsters with chips):
```python
replaced = CC1LevelTransformer.replace(level, CC1.monsters(), CC1.CHIP)
```
- `.replace_mobs()` intelligently replaces a mob or set of mobs `old` with a mob `new`, maintaining directions.
    - It is generally intended to use prebuilt element sets from the `CC1` class with this method, however feel free to experiment.
- Example (Replaces all teeth with blobs):
```python
replaced = CC1LevelTransformer.replace_mobs(level, CC1.teeth(), CC1.blobs())
```
- `.keep()` deletes everything from the level that is not specified in `elements_to_keep`.
    - Great for building "Walls Of" sets and variations.
- Example (Keeps all walls (including blue and invisible) as well as all thin walls a.k.a. panels):
```python
replaced = CC1LevelTransformer.keep(level, CC1.walls().union(CC1.panels()))
```

#### Rotations
- Rotations rotate a CC1Level by 90, 180, or 270 degrees, if possible.
    - If a level contains a CC1.PANEL_SE tile, an identical copy of the level will be returned (with nothing rotated).
    - Directions of CC1 elements are intelligently swapped. 
    - Trap and cloner connections are maintained, along with monster movement.
Examples:
```python
r90 = CC1LevelTransformer.rotate_90(level)
r180 = CC1LevelTransformer.rotate_180(level)
r270 = CC1LevelTransformer.rotate_270(level)
```

#### Flips
- Flips flip a CC1Level horizontally, vertically, or along either diagonal, if possible.
    - If a level contains a CC1.PANEL_SE tile, an identical copy of the level will be returned (with nothing flipped).
    - Directions of CC1 elements are intelligently swapped.  
    - Trap and cloner connections are maintained, along with monster movement.
Examples:
```python
horiz = CC1LevelTransformer.flip_horizontal(level)
vert = CC1LevelTransformer.flip_vertical(level)
diag1 = CC1LevelTransformer.flip_ne_sw(level)
diag2 = CC1LevelTransformer.flip_nw_se(level)
```


### [C2MHandler Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/c2m_handler.py#L95-L279) (Limited Functionality)
```python
from cc_tools import C2MHandler
```

### [CC1LevelImager Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc1.py#L644-L814) (Limited Functionality)
```python
from cc_tools import CC1LevelImager
```
