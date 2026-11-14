---
layout: default
title: "Format Spec: TGIFILE.ART"
---

# Format Spec: `TGIFILE.ART`

**Status:** Payload decoded (WP-002, 2026-11-13) and cross-checked against the loader, sequence player and renderer in `Scooby.exe` (WP-001, 2026-11-13). Every image in the file decodes: 453 object resources and 69 room backgrounds, 9,111 cels. The header descriptors, the full name table, sequence records, mask roles and room names are now resolved. Open: room-block word `0x10`, the placement field at `+0x88`, and a few never-populated room tables. *Phantom of the Knight*'s file passes the same checks (WP-006, 2026-11-13).  
**Engine generation:** **Gen 1** (Showdown 2000, Phantom 2001). Phantom verified by WP-006 (2026-11-13): the same layout, every check in `--verify`, and the same loader and renderer code. See [Cross-title verification](#cross-title-verification-2026-06).  
**Source disc:** *Scooby-Doo! Showdown in Ghost Town* (2000, The Learning Company)  
**Sample file:** `scooby\TGIFILE.ART` on the Showdown disc  
**File size:** 144,592,896 bytes (≈ 144 MB)  
**Source binary SHA-256:** `B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807` (cached `tools/exes/showdown/TGIFILE.ART` per [tools/exes/README §Showdown](../../tools/exes/README.md#showdown-gen-1)). Every Findings subsection below derives from this binary; a re-rip producing a different SHA invalidates the corresponding rows.  
**Decoder:** [`tools/probe_art.py`](../../tools/probe_art.py) (WP-002). `--verify` re-runs every structural check cited on this page.  
**Vision doc reference:** [Project Vision](../01-VISION.md) — Phase 1 primary risk area; see "Engine Lineage" section for generation classification.

This file was the primary technical risk for the engine. [WP-002](../work-packets/WP-002-tgifile-art-decoder.md)
decoded it from the data file alone: images are run-length-encoded 16-bit
RGB565 pixels stored big-endian, in "cels" carried by sector-aligned object
resources and scene blocks. Decoded sprite and background output was checked
by eye: Daphne, Fred and Scooby in their canonical colors, and Ghost Town
backgrounds. Phase 1 exit criterion #1 is met.

**Generation scope:** this format spec covers **Gen 1** titles only.
Jinx (Gen 2) and Case File #1 (Gen 3) use the `MMFW` wrapper container
format — see [`mmfw-container.md`](mmfw-container.md) for that spec. The
two formats are not interchangeable; the ScummVM engine will need both
parsers selected by the detection-time generation flag.

---

## Findings

### Archive layout

WP-002 finding. The file is a header and name table, then two runs of
sector-aligned blocks. A "sector" here is 2,048 bytes; every block starts on
a sector boundary and is padded to the next one.

```
File range                 Content
-------------------------  ------------------------------------------------------
0x00000000–0x0000082F      Header: room count, room descriptors, object count,
                           object descriptors (see Header layout)
0x00000830–0x0001E323      Name count (1,788), then the engine name table
                           (68-byte records, see below)
0x0001E324–0x0001FFFF      Non-record bytes up to the first sector-aligned block
0x00020000–0x06864873      453 object resources, back to back, each sector-padded
0x06865000–0x089E4FFF      69 room (scene) blocks, back to back, each
                           sector-padded; the last one ends exactly at end of
                           file (0x089E5000)
```

`Scooby.exe` reads the first 64 sectors (`0x20000` bytes) in one call and
parses everything up to the end of the name table from that buffer (WP-001,
art-file constructor at `0x43A8B0`).

Evidence: walking `offset → align(offset + u32 size at offset)` from
`0x20000` visits exactly 453 blocks whose header tables validate (see
[Object resources](#object-resources)). The same walk then visits exactly 69
scene blocks and lands on the file size, 144,592,896, with no remainder. The
two counts equal the header's `object_count` (453 at `0x0118`) and its first
`u32` (69 at `0x0000`). A brute-force scan for valid object-resource headers
at every 2,048-byte boundary of the file finds the same 453 and no others.
The engine does not walk the blocks: it seeks with the descriptors (see
[Header layout](#header-layout)), which span the same blocks.

The bytes between the last name record and `0x20000` are not records. They
include Win9x kernel-range pointers (`0xBFF7xxxx`) and the ASCII string
`Interface and Startup`. They look like uninitialized buffer contents written
by the authoring tool, which is an inference, not a decoded structure. The
engine reads them into its header buffer but never parses them.

### Header layout

```
Offset     Size       Type      Value (Showdown)  Notes
------     ----       --------  ----------------  -----
0x0000        4       uint32LE  69 (0x45)         Room count (= number of room blocks)
0x0004      276       [69]u32   (see below)       Room descriptors, indexed by ROOM id
0x0118        4       uint32LE  453 (0x1C5)       Object count (= number of object resources)
0x011C    1,812       [453]u32  (see below)       Object descriptors, indexed by OBJ id
0x0830        4       uint32LE  1,788 (0x6FC)     Name count
0x0834  121,584       [1788]rec —                 Engine name table, 68-byte records
0x20000     var       blocks    —                 First object resource (OBJ id 0, OBJ_DAPHNE_A)
```

The counts are not fixed offsets in the engine: each table starts where the
previous one ends (`0x43A8B0` reads count, array, count, array, count,
records). The offsets above are Showdown's values.

**Correction (WP-001, 2026-11-13).** The object descriptors are 453 `u32`
values, not 453 eight-byte records. The previous reading ran the table into
the name count at `0x0830` and the first 27 name records, which is why it
reported a "zero padding" run at `0x0F44`–`0x0F5F` (the tail of the record
for `ROOM_P19_Back_Alley`) and a name table starting at `0x0F60`. The name
table starts at `0x0834` and has 1,788 records, not 811 plus a mixed tail.

#### Descriptors (room `0x0004`, object `0x011C`)

A descriptor locates its block in 2,048-byte sectors:

```
start_sector = d >> 14         (offset = start_sector × 0x800)
sector_count = d & 0x3FFF      (length = sector_count × 0x800)
```

The engine's sector reader (`0x43AED0`, and `0x43ACE0` which also allocates)
decodes them this way, seeks to the offset, and reads the length in 512 KB
chunks. Example: OBJ 0's descriptor `0x0010017E` is sector `0x40`
(offset `0x20000`), 382 sectors; OBJ 1's `0x006F8114` is sector `0x1BE`
(`0xDF000`), 276 sectors. `probe_art.py --verify` checks that all 69 room and
453 object descriptors span exactly the sector-padded blocks the block walk
finds. A 14-bit sector count caps a block at 32 MB; the largest object uses
1,887 sectors, the largest room 768.

Lookup is by name. `0x43B080` (load room) and `0x43B3D0` (load object)
binary-search the name table for the name, take `id & 0x0FFFFFFF` as an index
into the room or object descriptor array, and read that block.

**Correction (WP-002, 2026-11-13).** This page previously listed the first
asset payload at `0x10017E` and called the 453 eight-byte records
`(start, end)` file offsets, with a "confirmed values" table. Both were
wrong. Read as offsets, 295 of the 453 records are impossible (end before
start, or end beyond the end of the file), and 46 starts go backwards. Offset
`0x10017E` is not a payload start: it lies inside the second object resource
(`OBJ_FRED_A`, `0xDF000`–`0x168810`), in the middle of a cel's pixel stream.
Its leading bytes `F0 0C 25 5C` are a run of 12 pixels of color `0x255C`
(blue, Fred's trousers). `0x0010017E` is OBJ 0's sector descriptor (see
[Descriptors](#descriptors-room-0x0004-object-0x011c)).

**Correction (WP-003, 2026-06-02):** prior versions of this doc placed `asset_count` at `0x011C` and the asset entry table at `0x0120`–`0x0F48`. Direct hex inspection against the SHA-256-locked binary shows the structure is shifted 4 bytes earlier: `asset_count` is at `0x0118` and the entry table starts at `0x011C`. (WP-003's "pre-payload region begins at `0x0F44`" was itself superseded by WP-001: the name count is at `0x0830`.)

#### Gen 1 (Showdown) — 4-byte gap at `0x0118`

WP-003 step 2 resolved this. The 4 bytes at file offset `0x0118`–`0x011B` are not padding and not an unidentified field — they are the `asset_count` (`uint32LE` = `0x000001C5` = 453). Prior spec offset for `asset_count` was `0x011C`; the diagnostic that pins the correction:

- Hex window @ `0x0110`–`0x0123` (cited verbatim from cached `TGIFILE.ART`):

  ```
  22 C1 7B 44   B9 40 C4 44   C5 01 00 00   7E 01 10 00   14 81 6F 00
  ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^
  desc[67]      desc[68]      asset_count   objdesc[0]    objdesc[1]
  ```

- `0x0118` decodes as `uint32LE` = 453 (matches the documented count).
- `0x011C` and `0x0120` are the descriptors of OBJ 0 and OBJ 1. WP-003 read them as `entry[0].start` / `entry[0].end`; WP-001 showed each is one sector descriptor (see [Descriptors](#descriptors-room-0x0004-object-0x011c)).

### Object resources

One block per OBJ id, in id order: resource `i` is the art for name-table
`OBJ` id `i`. Evidence: resource 0 decodes to Daphne (`OBJ_DAPHNE_A`, id 0),
resource 1 to Fred (`OBJ_FRED_A`, id 1), resource 2 to Scooby
(`OBJ_SCOOBY_A`, id 2).

```
Offset  Size     Type          Field
------  -------  ------------  -----
0       4        uint32LE      total size of the resource (before sector padding)
4       4 × 8    (u32, u32)    four (count, offset) pairs; offsets are resource-relative
36      var      chunks        cels, frame records, polygons, sequence records
end-?   var      u32 arrays    the four offset tables the header points at
```

The four tables are contiguous `uint32LE` arrays at the end of the
resource. Each table's offset equals the previous table's offset plus
`4 × count`, and the last table ends at `total size`. All 453 resources
satisfy this; `probe_art.py` rejects any that don't. Each table entry is a
resource-relative offset to a size-prefixed chunk:

| Table | Points at | Record layout | Verified |
|---|---|---|---|
| 0 | Sequences (animations) | `u32 size (= 8 + 12n), u16 n, u16 flags?, n × step`; see [Sequences](#sequences-table-0) | All 1,266 records conform; all 12,451 steps check (`--verify`) |
| 1 | Frame records | `u32 size (= 8 + 8n), u16 n, u16 0, n × (i16 x, i16 y, u32 cel_offset)` | All 9,229 records conform; `n` is 0 or 1; every `cel_offset` is in table 3 |
| 2 | Polygons | `u32 size (= 16 + 4n), u32 n, i16 x, i16 y, i16 w, i16 h, n × (i16 x, i16 y)` | All 467 records conform; the box is the polygon's bounding box |
| 3 | Cels | see [Cel format](#cel-format) | All 9,042 sprite cels decode |

The engine loads a resource whole and turns every resource-relative offset
into a pointer in place (`0x43B3D0`): the four table bases, each table
entry, each sequence step's polygon offset, each frame record's cel offset,
and each cel's two mask offsets. Polygons (table 2) have no internal
offsets.

The frame record's `(x, y)` is the cel's draw offset from the object's
anchor. For Fred's first frame it is `(-40, -177)` against a 67 × 193 cel,
which puts the anchor near the feet. The renderer adds it to the sprite
position (`0x439C00`). A frame record with `n` entries draws `n` cels; the
data only has 0 or 1.

#### Sequences (table 0)

A sequence is one named animation. Each 12-byte step is:

```
Offset  Size  Type      Field
------  ----  --------  -----
0       4     uint32LE  0 on every Showdown step; not read by the player
4       4     uint32LE  frame ref: 0x8000_0000 | (owner OBJ id << 20) | frame index
8       4     uint32LE  polygon offset (resource-relative), or 0
```

The player (`0x4309C0`) selects the step's frame record as
`frames[ref & 0x3FFFF]`. Every step in the file names its own object in
bits 20–30 and a frame index below that object's frame count. The polygon
is that step's click shape: `0x430D10` tests the cursor against it with a
bounding-box check and then an even-odd point-in-polygon test (`0x431350`,
`0x4312A0`). So hit regions change per animation step, and a step with no
polygon is not clickable. Fred's idle steps point at 4-point polygons.

The `u16` at offset 6 of the sequence header is 0 on 1,263 sequences, 1 on
two and 2 on one. The traced player does not read it.

Phantom sets the step's first word on exactly two of its 8,304 steps, both
in sequence 3 of `OBJ_KST_MUG`: `0xFFEE000A` and `0xFFE3000E`. Read as two
`i16`, that is (10, −18) and (14, −29), which looks like a per-step x, y
offset for a mug being lifted (inference). Phantom's player code is
byte-identical to Showdown's (WP-006), and no traced reader touches this
word, so the engine ignores it. Two Phantom sequence headers also carry a
non-zero `u16` at offset 6. `--verify` lists non-zero first words instead of
failing on them.

Playback state lives in the sprite, not the file (`0x430AA0`, `0x430890`):
a mode, a step index, and a ticks-per-step countdown. The modes are 1 =
loop forward, 2 = loop backward, 3 = play forward once and hold the last
step, 4 = play backward once and hold the first, and 5 = jump to the last
step and stop. 0 = stopped. Step timing comes from the caller, not from
the data: the animated-sprite constructor (`0x430790`) takes object name,
ANIM name, parent, depth, mode, ticks per step and start step. Every
placement constructor passes 3 ticks per step and step 0. The mode depends
on the kind (WP-018): 1 for most, but **0 (stopped) for `clickableobject`
and `OBJ_GHOST`**. See [Rendering a room](#rendering-a-room-2026-11-13).

**Tick unit and start step (WP-017, 2026-11-14).**

- **The tick unit.** The game loop (`0x435BC0`) owes `elapsed_ms × 36 / 1000` ticks since
  its base time. It runs each owed tick, then draws once. A tick walks the
  sprite tree front to back, calling every sprite's tick (`0x431130`, skipped
  for paused subtrees). So a tick is 1/36 s, and a looping placement shows
  12 steps per second: after `T` ticks it is at step `floor(T / 3) mod n`.
  Phantom's loop is byte-identical.
- **The countdown.** Start (`0x430AA0`) sets it to the ticks per step. Each
  tick decrements it, and at 0 it resets and the step moves by the mode.
- **The start step.** −1 is step 0 in modes 1 and 3 and the last step in
  modes 2 and 4. A value past the end becomes the last step.

**ANIM names select a sequence.** There are exactly as many `ANIM` names in
the name table (1,266) as sequences in all objects. An ANIM id is:

```
0x3000_0000 | (owner OBJ id & 0xFF) << 20 | sequence index
```

The sprite stores the ANIM id and indexes `sequences[id & 0x3FFFF]` of the
object it already holds (`0x430A00`). The owner field keeps only 8 bits, so
the 453 objects share 256 groups and 241 ANIM ids collide (for example
`ANIM_DAPHNE_ABLINK` and `ANIM_P05_TO_P12EXIT` are both `0x30000000`;
`OBJ_DAPHNE_A` is id 0, `OBJ_P05_TO_P12` is id 256). The id alone does not
name an object. The object always comes from context: the placement record,
an `object.ini` field on that object's section, or code. Every one of the
615 room placements pairs an object with one of its own sequences.
`--verify` checks the sum per owner group, the step layout, and every
placement pair.

Example, `OBJ_FRED_A` at `0xDF000`:

```
DF000  10 98 08 00  0C 00 00 00  E0 95 08 00  41 00 00 00
       total=0x89810  seq n=12  @0x895E0      frames n=65
DF010  10 96 08 00  02 00 00 00  14 97 08 00  3D 00 00 00
       @0x89610      polys n=2   @0x89714     cels n=61
DF020  1C 97 08 00  A8 24 00 00  43 00 C1 00  B8 19 00 00
       @0x8971C     first cel: size=0x24A8, 67 x 193, mask_a=0x19B8 ...
```

### Scene blocks

69 blocks after the last object resource, one per room descriptor. Each
holds an object placement list and a full-screen background cel. The
engine calls them rooms; this page also says "scene" for the same block.

```
Offset  Size  Type      Field
------  ----  --------  -----
0x00    4     uint32LE  block size (a multiple of 2,048 on every block)
0x0A    2     uint16LE  scene ID: 0x9000 + 0x10 × index on every block
0x0C    2     uint16LE  width (640; 1920 on scenes 19 and 51)
0x0E    2     uint16LE  height (480 on every block)
0x10    2     uint16LE  2 on 59 blocks, 1 on 10 (meaning unknown; no reader found)
0x80    4 × 10          layer slots: offset of a frame record, or 0
0xA8    4     uint32LE  cel count (1 on every block)
0xAC    4     uint32LE  offset of the cel table (u32 offsets)
0xB0    4     uint32LE  count of a further table (0 on every block)
0xB4    4     uint32LE  its offset
0xB8    4     uint32LE  count of embedded object resources (0 on every block)
0xBC    4     uint32LE  offset of their table
0xC0    4     uint32LE  placement count
0xC4    4     uint32LE  offset of the first placement record (0xD8 on every block)
0xD8    148 × count     placement records
...                     background cel, immediately after the placements
...                     cel table (one entry: the background cel), then the
                        layer-0 frame record
```

The room loader (`0x43B080`) converts every offset above to a pointer,
including each cel's mask offsets, so all offsets are relative to the block.
The words at `0x00`–`0x7F` other than those listed are zero on every block.

- **Layers.** Each non-zero slot at `0x80` is a frame record (the same
  layout as table 1 of an object resource). `0x435DC0` creates one sprite
  per used slot, at depth `-110000 + 10000 × slot`, so layer 0 is the
  furthest back. In Showdown only slot 0 is used, on all 69 blocks, and it
  is always `n = 1, (0, 0), background cel`.
- **Cel table** at `0xAC`: one entry, the background cel. The renderer frees
  and converts cels through this table (for example the RGB565 → RGB555 pass
  on 15-bit displays).
- **`0xB0` table:** the loader relocates the `u32` at `+0xC` of each entry
  unless the byte at `+9` is set. **`0xB8` table:** each entry is relocated
  like a whole object resource (`0x43B6C0`), so a room can embed its own
  objects. Both are empty in every room of Showdown and of Phantom
  (WP-006), so no shipped Gen 1 data shows their payload.

A placement record is 148 bytes:

```
Offset  Size  Type      Field
------  ----  --------  -----
0x00    64    char[64]  OBJ name, NUL-terminated
0x40    64    char[64]  ANIM name, NUL-terminated (a sequence of that object)
0x80    4     2 × i16   0 on all 615 placements
0x84    2     int16     x
0x86    2     int16     y
0x88    4     uint32LE  per-object constant (see below)
0x8C    8               0 on all 615 placements
```

Every placement handler in `Scooby.exe` reads the position from `+0x84`
and `+0x86`. In scene 0 Daphne is at `(241, 341)`. The value at `+0x88` is
a per-object constant: it is the same everywhere an object is placed, it
differs between all 300 placed objects, and it runs from 4 to 456. It is
not the OBJ id (Daphne's is 353). No traced handler reads it.
(WP-002 read the three `u16` values from `+0x84` as x, y and depth.)

The background cel starts at `0xD8 + 148 × count`. This rule holds on all 69
blocks, since every background decodes and ends where its mask chunk begins.
Scenes 19 and 51 are 1920 × 480. Scene 51's background repeats after 1280
pixels, which suggests a wrapping scroll.

`--verify` checks the layer-0 record, the cel table and every placement's
OBJ/ANIM pair on all 69 blocks.

#### Rendering a room (2026-11-13)

`py -3 tools/probe_art.py --room ROOM_P12_Saloon` (or a room index)
composites a room the way the engine sets it up on entry. The output goes
to `tools/samples/`, which is gitignored.

1. Draw each used layer slot's frame record at `(0, 0)`, slot 0 first.
2. For each placement, look up the OBJ and ANIM names in the name table.
   Take sequence `anim_id & 0x3FFFF` of that object, at step 0: the default
   placement path starts mode 1 at step 0. Draw the step's frame record:
   each entry's cel goes at `(x + dx, y + dy)`, with the placement's `(x, y)`
   from `+0x84` and the frame's offset `(dx, dy)`. Cels composite through
   their masks, so A pixels are opaque and B pixels are alpha-blended
   ARGB4444.
3. Placements whose step frame has `n = 0` draw nothing: exits and most
   hotspots are invisible click regions.

**Draw order (traced).** The engine keeps a tree of sprites. Each sprite
has a parent and a depth, and its children are kept sorted by descending
depth (`0x430F40`). To draw a sprite (`0x431000`), the engine first emits
its children whose depth is at least its own, then the sprite itself, then
its remaining children. The result is a front-to-back list, which the
renderer draws with occlusion (see [Cel format](#cel-format)). Higher depth
is nearer the viewer; among equal depths, the earlier-added sprite is in
front.

On room entry (`0x435DC0`), the root sprite (depth `-0x7FFFFFFF`) gets one
child per used layer slot, at depth `-110000 + 10000 × slot`. The game
keeps those layer sprites in a 10-entry array (Game `+0x58`), which its
reset (`0x435CD0`) clears. Placements then attach by kind
(`0x4091FF`, `0x408F90`, `0x408DC0`, `0x401000`):

| Placement kind | Parent | Depth |
|---|---|---|
| Character: `OBJ_<NAME>` or `OBJ_<NAME>_<x>` for a name in the table at `0x46A720` (NARRATOR, the gang, ARTIE, JENNY, SHERIFF, ICDOUBLE, GUMMY, DONKEY, …), and `OBJ_GHOST` | layer 0 | `y − 200` |
| `ID=inventoryobject` | layer 0 | −100 |
| `ID=requiresobject` | layer 0 | 0 |
| `ID=exitobject` | layer 0 | −1000 |
| `ID=clickableobject` | layer `layer=` (missing or −1 → 0) | `priority=` (missing → −1) |
| anything else (`simpleobject`, no section) | layer 1 | 0 |

**How each kind starts (WP-018, 2026-11-14).** The constructors decide more
than parent and depth:

| Kind | Constructor | Start mode | Hidden | Hit test |
|---|---|---|---|---|
| exit, requires, inventory | `0x401850`, `0x402D90`, `0x4026B0` | 1 | no | step polygon (type 2) |
| clickable | `0x401000` (via `0x408DC0`) | **0** | no | step polygon (type 2) |
| character | `0x4048E0` | 1 | no | cels (type 1) |
| `OBJ_GHOST` | `0x430790`, then `0x4313F0(1)` and `Start(0, 3, −1)` | **0** | **yes** | cels (type 1), but hidden sprites are skipped |
| anything else | `0x430790` | 1 | no | step polygon (type 2) |

- **Clickables.** The constructor can resume a sequence saved under a
  `Clickables` settings key. A fresh game has none.
- **Hidden sprites.** `+0x14` is neither drawn (`0x431000`) nor hit-tested
  (`0x4311F0`), but it still ticks.
- **What WP-016/017 got wrong.** Both treated every placement as visible and looping.
  - At tick 0 that changes no Showdown room: its ghost's first frame is empty, and clickables start at step 0 either way.
  - It does change the 5 Phantom rooms with a ghost: its first frame has art there.
  - By tick 37 it changes 22 Showdown and 23 Phantom rooms.
- **`--room`** now hides the ghost.

**Hit testing (WP-018, 2026-11-14).** The hit walk (`0x4311F0`, sprite vtable
`+0x14`) visits sprites in the draw order, front to back, skipping hidden
ones. The first sprite whose test passes is under the cursor.

- **Type 2, the step polygon** (`0x430D10` → `0x431350` → `0x4312A0`).
  - It uses the current step's polygon (the step's third word), with
    coordinates relative to the sprite: `(x, y) = (px − sx, py − sy)`.
  - The box test is strict on both sides: `bx < x < bx + w` and
    `by < y < by + h`.
  - Then comes an even-odd crossing test. For each edge `(i, j = previous)`,
    toggle when `(yi ≤ y < yj or yj ≤ y < yi)` and
    `x < (xj − xi)(y − yi) / (yj − yi) + xi`, with C integer division.
  - A step with no polygon is never hit.
- **Type 1, the cels** (`0x431400`). Inside a cel's rectangle
  `[cx, cx + w) × [cy, cy + h)`, the sprite is hit if the cel isn't solid
  and its pixel is non-zero, or if mask B or mask A covers the point.
  Background layers are type 1, so every point in a room hits something.

**Rollover cursors (sprite vtable `+0x18`).**

- Exits (`0x402410`) return `rolloveranim=` while the default cursor is up,
  and `ANIM_CURSORSCRAPPY_ANIM` in Scrappy's hint mode.
- Clickables (`0x4015F0`) return `ANIM_CURSOROPEN`.
- The base class (`0x408450`) returns nothing.
- The cursor itself is an `OBJ_CURSOR` sprite (`0x4089E0`), `ANIM_CURSORARROW`
  by default.

Showdown never fills layer slot 1. A sprite whose parent slot is empty
attaches to the root (`0x430F40`). So `simpleobject` placements and
`layer=1` clickables sit in front of the whole background subtree, gang
included. That is how overlays such as `OBJ_P01_TC_OVERLAY` (the cactus
and fence) end up in front of the characters. The table models the
default placement path only. A room's own class can claim an OBJ by name
first (see [scooby-exe](scooby-exe.md#objectini-consumer-wp-001)); the tool
does not model that, and the Post Office trapdoor may be such a case. The
character name list includes `BRAD`, `EWAN`, `MARIA`, `JANE`, `WIZARD`,
`JESTER`, `PRINCESS` and `UNICYCLE`, which do not appear in Showdown's
data. They are Phantom's cast: Phantom's `Scooby.exe` carries the same
20-name table (at `0x469720`), and its name table holds objects for exactly
those eight plus the gang (WP-006). One table serves both titles, so
`--room` renders Phantom rooms unchanged.

**Checked against WP-009 frames:**

- **Town Center:** the cactus-and-fence overlay covers the gang's feet. The
  `POPULATION` signpost, whose base is near the bottom of the screen, draws
  in front of Fred. (The frame was captured after the sign was taken, so it
  cannot confirm the sign.)
- **Saloon:** the gang positions and overlaps match, with Scooby in front of
  Velma and Velma in front of Artie.
- **Railroad Station:** the gang trio matches.

The remaining differences are game state, not format. The video catches
props already moved or picked up and NPCs mid-animation, while the tool
shows every placement at step 0. All 69 rooms render without errors (497
visible placements). An earlier version of the tool (2026-11-13, before
this trace) inferred the order; switching to the traced rules changed 26
of the 69 renders.

#### Scene index = ROOM id (WP-009, 2026-11-13)

Scene block `i` is the room whose name-table id is `0x10000000 + i`.
**WP-001 confirmed this in code and named every room.** The engine indexes
the room descriptor array with `id & 0x0FFFFFFF` (`0x43B080`), and the
name table holds a record for all 69 room ids. Ids 0–26 sit at
`0x0834`–`0x0F5F`, the part WP-003 read as the end of the descriptor table.
They name scene 18 `ROOM_Artie` (it places `OBJ_CHAINS`; `Sfx.dat` has
`Artie.Chains_A`–`C`) and scene 19 `ROOM_Title_Screen`. The other 25 names
match the WP-009 derivations below exactly. Two pieces of evidence came
before the code trace:

- **Name table vs placements.** The name table names 42 rooms, ids 27–68.
  For all 42, scene `i` places that room's own objects. Examples:
  `ROOM_P21_Boot_Hill1` (id 27) and scene 27 places `OBJ_P21_*`;
  `ROOM_P18_Tunnel_Lit` (42) and `OBJ_P18_*`; `ROOM_Options` (47) and
  `OBJ_OPTIONS_*`; `ROOM_Gummy` (50) and `OBJ_GUMMYSLEEP_*`;
  `ROOM_Open_Safe` (62) and `OBJ_GANG_VAULT*`; `ROOM_SB1`–`SB5` (63–67) and
  `OBJ_SB1_LID`–`OBJ_SB5_LID`.
- **Video match.** Each of the 35 catalog rooms in the WP-009 longplay was
  matched to a decoded background by image similarity (scores 0.75–1.00),
  and every match is the scene this rule predicts. See the
  [reference gallery](../assets/screenshots/showdown-screens/index.md).

WP-009 believed ids 0–26 had no name-table record and derived their names
from the `OBJ_P<nn>_*` objects each scene places, cross-checked against
`object.ini`'s `destinationroom=` values and the `ROOM_*` strings in
`Scooby.exe`. The name table now confirms them:

| Scenes | Rooms |
|---|---|
| 0–8 | `P01_Town_Center`, `P11_Street3`, `P12_Saloon`, `P17_Hotel_Hall`, `P32_Pie_Noon`, `P20_Hotel_Room`, `P30_Horseshoe_Corral`, `P03_Street1`, `P04_Street2` |
| 9–11 | `Sign_In`, `Difficulty`, `Main_Menu` (placements `OBJ_SIGN_IN_*`, `OBJ_DIFFICULTY_*`, `OBJ_MAIN_MENU_*`) |
| 12–16 | `P02_Sheriffs_Office`, `P08_Post_Office`, `P09_Railroad_Station`, `P10_Front_Of_General_Store`, `P13_Bank` |
| 17 | `Suspect_Chooser` (`OBJ_SUSPECT_*`) |
| 18–19 | `Artie`, `Title_Screen` (from the name table, WP-001; WP-009 had them unresolved) |
| 20–26 | `P05_Stage`, `P06_Stage_Trapdoor`, `P07_Jail`, `P14_Tunnel_Dark`, `P15_General_Store_Interior`, `P16_Bank_Vault`, `P19_Back_Alley` |

(Room names in the table drop the `ROOM_` prefix.) The scene ID field at
`0x0A` is `0x9000 + 0x10 × i`, so it encodes the same index.

**Correction to WP-008.** WP-008 listed 21 `destinationroom=` rooms as
having no `TGIFILE.ART` entry and probably rendering from code, among them
Town Center, Saloon, Main Menu, Pie Noon and Horseshoe Corral. All 37
catalog rooms have a scene block with a background. Those 21 were missing
from the part of the name table WP-003 had parsed (ids 27–68), not from the
archive. WP-001 found the records for ids 0–26 as well.
Pie Noon and Horseshoe Corral still have their own `*_Room.cpp` code, but
their backgrounds are ordinary scene blocks.

### Cel format

Every image in the file, sprite or background, is a cel:

```
Offset  Size  Type      Field
------  ----  --------  -----
0       4     uint32LE  cel size, including this header and its mask chunks
4       2     uint16LE  width
6       2     uint16LE  height
8       4     uint32LE  mask A offset, or 0 if absent (relative to the owning resource or scene block)
12      4     uint32LE  mask B offset, or 0 if absent (same base)
16      1     uint8     solid: 1 = paint mask A with solid_color (7 cels), else 0
17      1     uint8     rle: 1 = RLE pixel stream (9,093 cels), 0 = raw pixels (18 cels)
18      2     uint16LE  solid_color, RGB565 (0 unless solid)
20      4     uint32LE  0 in the file; the renderer keeps its bitmap-cache slot here
24      var   bytes     pixels (RLE stream or raw), then up to 3 pad bytes, then the mask chunks
```

WP-002 read bytes 16–19 as one flags word (`0x100` on 9,086 cels, 0 on 18,
`0x101` on 4, three large values with the low bit set). The engine reads
them as two flag bytes and a colour (`0x4398A0`, `0x433AF0`, `0x438660`).
The three "large values" are solid cels with colours `0xF800` (red, twice)
and `0xED1C`. The solid cels are two text-field boxes in `OBJ_SIGN_IN_TEXT_FIELD`,
three 1-pixel-high lines, and the backgrounds of scenes 52 and 53. Their
pixel streams are present but unused: the engine fills mask A with the
colour instead.

**Raw cels** (`rle` = 0): `width × height` 16-bit pixels stored
**little-endian**, unlike the RLE stream. The engine hands back `cel + 24`
with no byte swap, while its RLE decoder swaps every word. The data agrees:
read little-endian, all 250 mask-B pixels in raw cels have alpha 1–14 (see
below); read big-endian, 69 do not. All 18 raw cels are tiny (at most
4 × 16). WP-002 decoded them as RLE, which happens to consume the same bytes
but gives byte-swapped colours.

**Pixel stream** (`rle` = 1). A byte stream, read until `width × height` pixels have
been produced, in row-major order with no per-row markers (runs cross row
boundaries):

```
while produced < width * height:
    if byte[q] == 0xF0:          # run
        count = byte[q+1]        # 1..255
        pixel = byte[q+2] << 8 | byte[q+3]
        emit pixel, count times
        q += 4
    else:                        # literal
        emit byte[q] << 8 | byte[q+1]
        q += 2
```

A literal pixel whose high byte is `0xF0` cannot be sent as a literal, so the
encoder sends it as a run of length 1. That happens 9,662 times across the
sprite corpus. No run has length 0.

**Pixel format.** Where mask A covers a pixel, the word is 16-bit RGB565
(stored big-endian in the RLE stream):
`r = p >> 11`, `g = (p >> 5) & 63`, `b = p & 31`. The colors pin this.
Read big-endian, Fred's shirt is `0xF79E` (white), his trousers `0x255C`
(blue), hair `0xFFAD` (yellow) and skin `0xFF57` (peach). His ascot comes out
orange only under RGB565; RGB555 makes it green and his trousers purple.
Read little-endian, every color is wrong. There is no palette anywhere: the
image is truecolor, which closes the palette hunt of WP-003 and WP-002.
On a 15-bit display the engine converts the mask-A pixels of each cel to
RGB555 once, at load (`0x433AF0`).

Where mask B covers a pixel, the word is **ARGB4444**: alpha in the top
nibble, then 4-bit red, green and blue. The blitter (`0x439170` for a 565
screen, `0x4394D0` for 555) expands each nibble to 8 bits through a table
and blends `out = (dst × (255 − a) + src × a + 0x80) >> 8`.

**Blend tables (WP-016, 2026-11-14).** The 565 blitter expands every channel through static
`int32` tables in `.data`. Showdown has them at `0x4708DC` (4-bit), `0x47075C` (5-bit) and
`0x4707DC` (6-bit); Phantom's bytes are identical.

```
T4[i] = 17 × i
T5[i] = round(255 × i / 31)   (= (255i + 15) / 31)
T6[i] = round(255 × i / 63)   (= (255i + 31) / 63)

a   = T4[src >> 12]
R8  = (T5[dst >> 11]        × (255 − a) + 0x80 + T4[src >> 8 & 15] × a) >> 8
G8  = (T6[dst >> 5 & 63]    × (255 − a) + 0x80 + T4[src >> 4 & 15] × a) >> 8
B8  = (T5[dst & 31]         × (255 − a) + 0x80 + T4[src & 15]      × a) >> 8
out = (R8 >> 3) << 11 | (G8 >> 2) << 5 | (B8 >> 3)
```

`probe_art.py`'s `rgb()` floors the 5- and 6-bit expansion, and its renders
composite in 8-bit RGBA. They are a visual reference, not the exact 565
screen.

**Transparency.** The masks decide it, not the pixel value. Mask A marks
opaque pixels, mask B translucent ones, and every other pixel is
transparent. Checked over all 9,042 sprite cels (`--verify`): masks A and B
never overlap; every pixel outside both is `0x0000`; every mask-B pixel has
alpha 1–14 (never 0 or 15), 6.4 M pixels in all. 5.9 M mask-A pixels are
`0x0000`, opaque black outlines and fills. WP-002's rule (`0x0000` is
transparent) therefore loses black ink and draws the antialiased edges as
solid colour. Backgrounds have only a mask A, covering the full screen, on
all 69 blocks, so they are opaque, black included.

**Mask chunks.** Each present mask is a size-prefixed span list:

```
u32 size, u16 x, u16 y, u16 w, u16 h,
then records up to the chunk end:
    u16 repeat_rows, u16 n, u16 runs[n]     # runs alternate skip, covered, skip, ...
```

Each of the `repeat_rows` rows starts at column `x`; the runs are
`(skip, covered)` pairs. This is how the engine walks them (`0x433AF0` and
the blitters). All 17,407 mask chunks in the file parse to exactly their
declared size and row count. A sprite's mask B box is a little larger than
its mask A box, because it holds the antialiased rim. Fred's cel 14
(76 × 194 pixels, at `0xFEF78`) has mask A at `(0, 1)` 75 × 193 and mask B at
`(0, 0)` 76 × 194. A background's single mask is the full screen as one
record: `480 rows × (skip 0, covered 640)`.

**How the engine draws.** `0x439C00` walks the render list front to back,
keeping a span region of screen pixels still uncovered. For each cel it
intersects that region with mask A, draws those pixels opaque, and
subtracts them from the region. It intersects the region with mask B and
queues the result as an "alpha region" (the overflow error string
`GameRenderer::AlphaRegion buffer` anchors this). After the opaque pass,
`0x438660` blends the queued regions back to front. So nothing behind an
opaque pixel is ever drawn, and translucent edges blend over whatever ended
up beneath them.

**Verification.** `py -3 tools/probe_art.py --verify` decodes all 9,111 cels
(9,042 sprite cels in 453 objects, 69 backgrounds). Every pixel stream
produces exactly `width × height` pixels and ends 0–2 bytes before its first
mask chunk, or before the cel end when it has no masks. Every mask chunk
parses exactly. Since WP-001 it also checks the descriptors, the name table,
every sequence step, the room tables and placements, and the mask partition
described above. Run time is about 50 s.

#### Decode path in `Scooby.exe` (WP-001)

The decode runs in `GameRenderer.cpp` (named from the `__FILE__` string
passed with its "Out of space for the Bitmap Cache" error). Its function is
`graphics_Renderer_GetCelPixels` at `0x4398A0` (Ghidra label). It decodes a
cel on first use into a 256-slot bitmap cache and returns the cached
buffer afterwards. Restated as pseudo-C:

```c
u16 *GetCelPixels(Cel *cel)
{
    if (!cel->rle)                   /* byte 0x11 */
        return (u16 *)(cel + 1);     /* raw: little-endian words, used in place */
    if (cel->cache_slot)             /* u32 at 0x14, runtime only */
        return cel->cache_slot->pixels;
    CacheSlot *slot = AllocSlot(width * height * 2);   /* evicts old cels if full */
    cel->cache_slot = slot;
    u8 *src = (u8 *)(cel + 1);
    u16 *dst = slot->pixels;
    for (n = 0; n < width * height; ) {
        if (src[0] == 0xF0) {        /* run: F0 count hi lo */
            for (k = src[1]; k; k--) dst[n++] = src[2] << 8 | src[3];
            src += 4;
        } else {                     /* literal: hi lo */
            dst[n++] = src[0] << 8 | src[1];
            src += 2;
        }
    }
    return dst;
}
```

This is the WP-002 algorithm, confirmed. The decoder knows nothing about
the masks: it decodes every pixel, and the draw code reads only the pixels
the masks select. Solid cels never reach it (`0x438660` and `0x439C00` test
byte `0x10` first and fill with the colour). Callers: the renderer
(`0x438660`, `0x439C00`) and the RGB555 conversion (`0x433AF0`).

### Pre-payload region — engine name table

**Region:** the name count at `0x0830` and 1,788 records from `0x0834` to
`0x1E324` (WP-001). WP-003 started the table at `0x0F60`, after the first 27
records, and ended it at `0x10017E` with a "mixed region" from `0xE6CC` of
name records interleaved with F0-opcode packed data. WP-002 showed the F0
data was the first object resources (`OBJ_DAPHNE_A` from `0x20000`,
`OBJ_FRED_A` from `0xDF000`). A local-only dump of WP-003's range is
preserved at `tools/samples/tgifile-art-prepayload-dump.bin` (gitignored;
SHA-256 `2AC950F319C4A7F550746EABD35DB3E873A92727E8A4FF43C5EB03BD7337FA4D`).

This region is the **engine's resource-name catalog**: type-tagged 32-bit
IDs mapped to ASCII names. The engine copies every record into a table,
sorts it by name, and binary-searches it for every name lookup
(`0x43A8B0`, then `0x43B970` from the room, object and id lookups). It also
copies the ROOM names into an array indexed by room id and the OBJ names
into one indexed by object id. Those arrays build the
`Added rooms` / `Added objects` lists that merge several art files.

#### Gen 1 (Showdown) — Region layout

```
Sub-range            Length     Content
------------------   --------   -----------------------------------------------
0x0830–0x0833           4 B     Name count (1,788)
0x0834–0x1E323    121,584 B     1,788 name records: 69 ROOM + 453 OBJ + 1,266 ANIM.
                                The last name is `ANIM_HC_ARCS0x03`.
0x1E324–0x1FFFF     ~7 KB      Non-record bytes (see Archive layout)
```

The records are grouped by type, the 69 ROOMs, then the 453 OBJs, then the
1,266 ANIMs, and are not sorted by name within a group.

#### Gen 1 (Showdown) — Record format

```
Offset within record   Size   Type        Notes
--------------------   ----   --------    -----
0                         4   uint32LE    Resource ID — see ID schema below
4                        64   char[64]    NUL-terminated ASCII name
```

**The "20-byte metadata" is not a field.** WP-003 split the record into a
44-byte name and 20 bytes of metadata. The engine copies the name as a
C string from offset 4 and never reads past its NUL (`0x43A8B0`, which then
advances 68 bytes). The non-zero bytes some records carry after the NUL
(210 of 1,788) are never read. They look like stale contents of the
authoring tool's buffer, which is an inference. One example is
`ANIM_BIG_HEAD_BG_P09DAPHNE`, whose trailing bytes WP-003 read as
`(6534, 6078, 6078, 0, 0)`.

#### Gen 1 (Showdown) — Resource ID schema

The top nibble of each `uint32LE id` is a type tag:

```
Tag     Type   Records   Id layout
------  ----   -------   ---------
0x1     ROOM   69        0x1000_0000 | room id (0–68); room id = scene block index
0x2     OBJ    453       0x2000_0000 | object id (0–452); object id = object resource index
0x3     ANIM   1,266     0x3000_0000 | (owner OBJ id & 0xFF) << 20 | sequence index
```

ROOM and OBJ ids index the room and object descriptor arrays
(`id & 0x0FFFFFFF`). WP-002 matched object resources 0–2 to `OBJ_DAPHNE_A`,
`OBJ_FRED_A` and `OBJ_SCOOBY_A` by eye. An ANIM names one sequence of one
object (see [Sequences](#sequences-table-0)). WP-003's reading of the
ANIM id's second byte as a sub-category (`0x40` = CURSOR, `0x70` = TOOLBAR)
was the owner's low byte: `0x314…` ids belong to `OBJ_CURSOR` (id 20 =
`0x14`), and `0x327…` ids to `OBJ_TOOLBAR` (id 295 = `0x127`).

#### Gen 1 (Showdown) — Strings cross-check (WP-007 hand-off)

This cross-check predates WP-001 and covers only the 811 records WP-003 had
parsed, not the full 1,788. Sample names from that block were cross-referenced against `tools/exes/showdown/strings-ansi.txt` (1,959 unique ANSI strings extracted from `Scooby.exe` by [WP-007](../work-packets/WP-007-strings-and-imports.md)):

| Section | Records | Names also present in `strings-ansi.txt` |
|---|---|---|
| ROOM (42)  | 42  | 42 (100.0 %) |
| OBJ (453)  | 453 | 228 (50.3 %) |
| ANIM (316) | 316 | 65 (20.6 %) |
| **Total**  | 811 | 335 (41.3 %) |

Sample matches (3 per section):

```
[X] ROOM   ROOM_P21_Boot_Hill1
[X] ROOM   ROOM_P25A_Chase_B2_Closeup
[X] ROOM   ROOM_P40_Chase_Start
[X] OBJ    OBJ_DAPHNE_A
[ ] OBJ    OBJ_P09_RAILROAD_STATION_HOTSPOT1
[ ] OBJ    OBJ_P40_TO_P33
[X] ANIM   ANIM_CURSORARROW
[X] ANIM   ANIM_P17_HOTEL_HALL_DOORANIM
[ ] ANIM   ANIM_BIG_HEAD_BG_P09FRED
```

Interpretation: ROOM names are universally referenced as static strings in `Scooby.exe` (likely the room-transition / load path is string-keyed at compile time). OBJ names hit ~50 % — consistent with `object.ini` driving most OBJ resolution by name (no static string in the binary needed) while ~half are also referenced from code. ANIM names hit only ~21 % — consistent with animations being almost entirely data-driven (looked up by ID via the name table, with the binary holding only a small set of statically-referenced animation names). This corroborates the [scooby-exe interpreter hypothesis](scooby-exe.md#hypotheses-unverified) — most resource resolution is data-driven, not hardcoded.

The full continuous-block record listing (811 entries, with per-record strings-present flag) is preserved at `tools/samples/wp003-name-table.txt` (gitignored; regenerable from the SHA-256-locked source binary).

### Cross-title verification (2026-06)

- **Showdown (Gen 1):** documented above. `TGIFILE.ART` present at disc root.
- **Phantom (Gen 1, verified by WP-006, 2026-11-13):** the same format. `scooby\TGIFILE.ART`, 114,386,944 bytes, SHA-256 `AC24E9AE…BF04` ([tools/exes/README §Phantom](../../tools/exes/README.md#phantom-gen-1)). The header follows the same count-driven layout with Phantom's own counts:

  ```
  Field          Showdown                  Phantom
  first u32      45 00 00 00 (69 rooms)    35 00 00 00 (53 rooms)
  object count   0x0118: 453               0x00D8: 433
  name count     0x0830: 1,788             0x07A0: 1,634 (53 ROOM + 433 OBJ + 1,148 ANIM)
  first record   ROOM_P01_Town_Center      ROOM_P31_KST
  ```

  The first `u32` is the room count, not a magic number, so the old "compare against `45 00 00 00`" test would have misread Phantom. `py -3 tools/probe_art.py --art <Phantom TGIFILE.ART> --no-hash --verify` passes in full. All 5,810 cels decode with exact mask chunks. All descriptors span their blocks. The ANIM count equals the sequence count (1,148). All 8,304 sequence steps name their owner and a frame in range. All 552 placements pair an object with its own sequence. The masks partition every sprite cel. The one difference is the unread step word described in [Sequences](#sequences-table-0). Room blocks match Showdown's field for field: word `0x10` is 1 or 2, only layer slot 0 is used, the `0xB0`/`0xB8` tables are empty, and `+0x88` is again a distinct per-object constant (1–437, not the OBJ id, not the `object.ini` section order). Two Phantom rooms are 1280 × 480, the title screen and `ROOM_Ghost_Spot`. `--room` renders them, the KST tavern and the sign-in screen cleanly (local only).
- **Jinx (Gen 2):** uses `MMFW`-wrapped archives (`Mummy.MMF`, `HD.MMA`, `HD.MMP`) — confirmed not `TGIFILE.ART`. See [`mmfw-container.md`](mmfw-container.md).
- **Case File #1 (Gen 3):** uses `MMFW`-wrapped archives (`MuseumCD.MMP`, `MuseumCD.MMA`) — same wrapper as Jinx. See [`mmfw-container.md`](mmfw-container.md). No `TGIFILE.ART` on the disc (WP-005 listing, 2026-11-13), so there is no first-64-bytes comparison to make.
- **Case File #2:** no `TGIFILE.ART`, `object.ini` or `.dat` audio on the disc; its archives are `.bul`/`.inx` bulk files. WP-005 (2026-11-13) places it on a different engine altogether ([scooby-exe §Case File #2](scooby-exe.md#case-file-2-wp-005)).

The `TGIFILE.ART` format is **specific to Gen 1**. Cross-title implementation does not generalize to Gen 2/3 via this spec — those need the separate MMFW parser. Whether the Gen 2/3 picture payloads reuse this cel format (`F0` runs over big-endian RGB565) is now a cheap test, the hypothesis in [mmfw-container](mmfw-container.md#hypotheses-unverified).

---

## Remaining unknowns

Resolved by WP-001 (2026-11-13), each with its section above: the room and
object descriptors (sector spans), room names for scenes 18 and 19, sequence
records and ANIM ids, the room-block tables at `0x80`–`0xC4`, the roles of
the two masks, the name-table "metadata" (not a field), and background
transparency (opaque).

Still open:

- Room-block word `0x10` (2 on 59 blocks, 1 on 10; Phantom 2 on 43, 1 on
  10). No reader was found in the decompiled code.
- The placement field at `+0x88`, a unique per-object constant that no
  traced handler reads. Phantom has the same pattern. It is not the OBJ id,
  the sorted-name rank or the `object.ini` section order in either title.
- The `u16` at offset 6 of a sequence header (non-zero on 3 of 1,266) and
  the step's first `u32` (0 on every Showdown step, a likely x, y offset on
  two Phantom steps). The player does not read them.
- Object table 2 (polygons). Its consumer was not traced. The per-step
  polygons are the ones the hit test uses.
- The room-block `0xB0` and `0xB8` tables. The loader supports them, but
  they are empty in every Showdown and Phantom room, so their payloads are
  unknown.

The decode itself has no open questions.

## Next steps

1. ~~Phase 2 can start: WP-010 and the Phase 3 `Common::Archive` reader can
   be written from this page~~ Done:
   [WP-010](../work-packets/WP-010-scummvm-scaffold.md) (scaffold) and
   [WP-014](../work-packets/WP-014-tgifile-art-archive.md) (2026-11-14,
   `ArtArchive` in the fork). The reader seeks with the descriptors, as the
   engine does. Its block list matches `probe_art.py` on both Gen 1 titles.
2. ~~Render one room with its placed objects~~ Done 2026-11-13: see
   [Rendering a room](#rendering-a-room-2026-11-13), including the traced
   draw order. Per-room placement overrides are the part not modelled.
3. ~~Run `--verify` against Phantom's `TGIFILE.ART`~~ Done 2026-11-13
   (WP-006): it passes, and the `0xB0`/`0xB8` tables are empty there too.
   The Phase 3 reader can treat both Gen 1 titles as one format.

## Success condition

Render at least one *Showdown* background or sprite to PNG/BMP outside the
engine, visually matching in-game output. **Met (WP-002, 2026-11-13).**
`OBJ_DAPHNE_A` cel 0 decodes to Daphne in her canonical colors, and scene
blocks decode to full Ghost Town backgrounds. **Matched against in-game
frames (WP-009, 2026-11-13):** 35 decoded room backgrounds and Daphne's
cel 0 line up with captured longplay frames in layout and color. See the
[reference gallery](../assets/screenshots/showdown-screens/index.md).
**Whole rooms (2026-11-13):** Town Center, Saloon and Railroad Station
composited with their placed objects match the gallery frames in layout and
overlap (see [Rendering a room](#rendering-a-room-2026-11-13)).

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Phase 1, primary risk area
- Companion specs: [audio-archives](audio-archives.md), [scooby-exe](scooby-exe.md)
- Decoder: [`tools/probe_art.py`](../../tools/probe_art.py)
