# CCTools
```
pip install git+https://github.com/ChipMcCallahan/CCTools.git
```
Tools for working with CC1 (DAT) and CC2 (C2M) files.

## CC1 API
### [CC1 Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1.py)
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
- This also works for ice corner tiles such as `CC1.ICE_NW`. 
- If an element cannot be rotated, the same element is returned.  

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
See [the code](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1.py) for a full list of prebuilt element sets.

### [CC1Cell Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1_cell.py)
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

### [CC1Level Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1_level.py)
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
p = (5, 0)
level.add(p, CC1.TEETH_S)
print(level.at(p))
level.add(p, CC1.GRAVEL)
print(level.at(p))
level.remove(p, CC1.TEETH_S)
print(level.at(p))
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
p1, p2 = (10, 10), (20, 20)
level.add(p1, CC1.TRAP_BUTTON)
level.add(p2, CC1.TRAP)
level.connect(p1, p2)
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

### [CC1Levelset Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1_levelset.py)
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

### [DATHandler Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/dat_handler.py)
```python
from cc_tools import DATHandler
```
This class obfuscates everything related to reading and writing CC1 DAT file formats. It can also fetch sets and set names from the [Gliderbot](https://bitbusters.club/gliderbot/sets/cc1/) repository.
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

### [CC1LevelTransformer Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1_level_transformer.py)
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

### [TWSHandler Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/tws_handler.py) (Limited Functionality)
```python
from cc_tools import TWSHandler
```
This class is intended to read a TWS file into a simple JSON format. See [TWS Spec](https://www.muppetlabs.com/~breadbox/software/tworld/tworldff.html#3).

- **This class is experimental and has limited functionality. Use at your own risk.**
#### TWS Parsing
- Can parse TWS file to JSON format.

**Code**
```python
result = TWSHandler('public_CCLP3.dac.tws').decode()
print(f"Levelset name is '{result['levelset_name']}'.")
print(f"Ruleset is {result['header']['ruleset']}.")
print(f"Found {len(result['records'])} records.")
```

**Output**
```
Levelset name is 'public_CCLP3.dac'.
Ruleset is MS.
Found 149 records.
```

**Code**
```python
record1 = result['records'][0]
print(f"Level: {record1['level_number']}.")
print(f"Password: {record1['level_password']}.")
print(f"RNG Value: {record1['rng_value']}.")
print(f"Solution Time in Ticks: {record1['time_in_ticks']}.")
print(f"First 2 moves: {record1['solution_moves'][:2]}")
```

**Output** (Refer to [TWS Spec](https://www.muppetlabs.com/~breadbox/software/tworld/tworldff.html#3) for how to interpret directions.)
```
Level: 1.
Password: LQXN.
RNG Value: 717110846.
Solution Time in Ticks: 2169.
First 2 moves: [{'time': 1, 'direction': 3}, {'time': 5, 'direction': 0}]
```

### [CC1LevelImager Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1_level_imager.py) (Limited Functionality)
```python
from cc_tools import CC1LevelImager
```
This class is intended to generate images of CC1 Levels.
- **This class is experimental and has limited functionality. Use at your own risk.**
- **Note: this class uses a custom 8x8 PNG tileset with no other options currently supported.**

#### Level PNG
Example:
```python
imager = CC1LevelImager()
imager.save_png(cc1.levels[0], "lesson1.png")
```
![image](https://user-images.githubusercontent.com/87612918/229225509-7a0cb92f-0e67-472b-ba92-d808d67903f6.png)

#### Levelset PNG
Example:
```python
imager.save_set_png(cc1, "cc1.png")
```
![image](https://user-images.githubusercontent.com/87612918/229226143-ae1e1d6c-b789-4d0a-a8ed-6e25e58a775b.png)

## CC2 API
### [CC2 Enum](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc2.py)
```python
from cc_tools import CC2

print(CC2.ICE_NE.right())               # CC2.ICE_SE
print(CC2.FORCE_N.reverse())            # CC2.FORCE_S
print(CC2.GREEN_CHIP.toggle())          # CC2.GREEN_BOMB
print(CC2.BLOB in CC2.monsters())       # True
print(CC2.DIRT_BLOCK in CC2.blocks())   # True
print(CC2.FLIPPERS in CC2.pickups())    # True
print(CC2.STEEL_WALL in CC2.walls())    # True
print(CC2.SWIVEL_DOOR_NW.dirs())        # 'NW'
print(CC2.FORCE_W.with_dirs('E'))       # CC2.FORCE_E
```

### [C2MCell](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/cc1_cell.py) & [C2MElement](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/c2m_element.py)
Allowed layers are [panel, mob, not_allowed, pickup, terrain].
```python
from cc_tools.cc2 import CC2
from cc_tools.c2m_cell import C2MCell
from cc_tools.c2m_element import C2MElement

terrain_floor   = C2MElement(CC2.FLOOR)                 
pickup_flippers = C2MElement(CC2.FLIPPERS)              
player_chip     = C2MElement(CC2.CHIP, direction='E')
cell = C2MCell(mob=player_chip,
                     pickup=pickup_flippers,
                     terrain=terrain_floor)


switch_cell  = C2MCell(terrain=C2MElement(CC2.SWITCH_OFF,  wires='E'))
toggle_cell  = C2MCell(terrain=C2MElement(CC2.GREEN_TOGGLE_FLOOR, wires='SW'))

track_tile = C2MElement(CC2.RAILROAD_TRACK,
                        tracks=['NE', 'SW'],
                        active_track='NE',
                        direction='S')
track_cell = C2MCell(terrain=track_tile)

dir_block  = C2MElement(CC2.DIRECTIONAL_BLOCK, direction='N')
gravel     = C2MElement(CC2.GRAVEL)
block_cell = C2MCell(mob=dir_block, terrain=gravel)

panel      = C2MElement(CC2.THIN_WALL_CANOPY)
forbidden  = C2MElement(CC2.NOT_ALLOWED_MARKER)
wall_cell  = C2MCell(panel=panel, not_allowed=forbidden)
```

### [C2MModifiers](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/c2m_modifiers.py)
```python
from cc_tools.cc2 import CC2
from cc_tools.c2m_element import C2MElement
from cc_tools.c2m_modifiers import C2MModifiers

switch = C2MElement(CC2.SWITCH_ON, wires="NS", wire_tunnels="E")
raw1   = C2MModifiers.build_modifier(switch)                # raw1 == b'\x25'
parsed1 = C2MElement(CC2.SWITCH_ON); C2MModifiers.parse_modifier(parsed1, raw1)   # parsed1.wires == 'NS'; parsed1.wire_tunnels == 'E'

letter = C2MElement(CC2.LETTER_TILE_SPACE, char='A')
raw2   = C2MModifiers.build_modifier(letter)                # raw2 == b'\x41'
parsed2 = C2MElement(CC2.LETTER_TILE_SPACE); C2MModifiers.parse_modifier(parsed2, raw2)   # parsed2.char == 'A'

clone = C2MElement(CC2.CLONE_MACHINE, directions='EW')
raw3  = C2MModifiers.build_modifier(clone)                  # raw3 == b'\x0A'
parsed3 = C2MElement(CC2.CLONE_MACHINE); C2MModifiers.parse_modifier(parsed3, raw3)   # parsed3.directions == 'EW'

cwall = C2MElement(CC2.CUSTOM_WALL, color='Pink')
raw4  = C2MModifiers.build_modifier(cwall)                  # raw4 == b'\x01'
parsed4 = C2MElement(CC2.CUSTOM_WALL); C2MModifiers.parse_modifier(parsed4, raw4)   # parsed4.color == 'Pink'

gate  = C2MElement(CC2.LOGIC_GATE, gate='NAND_W')
raw5  = C2MModifiers.build_modifier(gate)                   # raw5 == b'\x17'
parsed5 = C2MElement(CC2.LOGIC_GATE); C2MModifiers.parse_modifier(parsed5, raw5)   # parsed5.gate == 'NAND_W'

track = C2MElement(CC2.RAILROAD_TRACK, tracks=['NE','SW'], active_track='SW', initial_entry='E')
raw6  = C2MModifiers.build_modifier(track)                  # raw6 == b'\x05\x12'
parsed6 = C2MElement(CC2.RAILROAD_TRACK); C2MModifiers.parse_modifier(parsed6, raw6)
# parsed6.tracks == ['NE','SW']; parsed6.active_track == 'SW'; parsed6.initial_entry == 'E'
```

### [C2MMapDecoder](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/c2m_map_decoder.py) & [C2MMapEncoder](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/c2m_map_encoder.py)
```python
from cc_tools.c2m_cell        import C2MCell
from cc_tools.c2m_element     import C2MElement
from cc_tools.c2m_map_encoder import C2MMapEncoder
from cc_tools.c2m_map_decoder import C2MMapDecoder
from cc_tools.cc2             import CC2

row0_col0 = C2MCell(terrain=C2MElement(CC2.FLOOR))
row0_col1 = C2MCell(
    panel   = C2MElement(CC2.SWITCH_ON, wires='N'),
    terrain = C2MElement(CC2.FLOOR))
row1_col0 = C2MCell(
    mob     = C2MElement(CC2.CHIP, direction='E'),
    terrain = C2MElement(CC2.FLOOR))
row1_col1 = C2MCell(
    panel   = C2MElement(CC2.THIN_WALL_CANOPY, directions='NWC'), 
    terrain = C2MElement(CC2.GRAVEL))

grid = [[row0_col0, row0_col1],
        [row1_col0, row1_col1]]

raw_map  = C2MMapEncoder(grid).encode()
# raw_map some byte string like b'\x02\x02\x01\x76\x01\x89\x01\x16\x01\x01\x6D\x19\x1E'   
decoded  = C2MMapDecoder(raw_map).decode()

assert decoded[0][1].panel.wires          == 'N'
assert decoded[1][0].mob.id               is CC2.CHIP
assert decoded[1][1].panel.directions     == 'NWC'
assert decoded[0][0].terrain.id           is CC2.FLOOR
```


### [C2MHandler Class](https://github.com/ChipMcCallahan/CCTools/blob/main/src/cc_tools/c2m_handler.py) (Limited Functionality)
```python
from cc_tools import C2MHandler
```
This class is intended to obfuscate everything related to working with CC2 C2M file formats, as well as fetching files from the [Gliderbot](https://bitbusters.club/gliderbot/sets/cc2/) repository.

#### C2M Parsing
- Can parse C2M bytes to a tuple (not very useful yet).
```python
with open("local_file.c2m", "rb") as f:
    parsed_tuple = C2MHandler.Parser.parse_c2m(f.read())
```

#### C2M Packing and Unpacking
- Can pack and unpack C2M map data.
```python
unpacked = C2MHandler.Parser.unpack(parsed_tuple.packed_map)
repacked = C2MHandler.Packer.pack(unpacked)
```

# Enjoy!
- Please submit bugs, feature requests, or general feedback to thisischipmccallahan@gmail.com.
