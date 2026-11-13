---
layout: default
title: "Format Spec: TGIFILE.ART"
---

# Format Spec: `TGIFILE.ART`

**Status:** Payload decoded (WP-002, 2026-11-13). Every image in the file decodes: 453 object resources and 69 scene backgrounds, 9,111 cels. Remaining unknowns are the header descriptor values and part of the animation-sequence tables.  
**Engine generation:** **Gen 1** (Showdown 2000, Phantom 2001 — Phantom's archive format unverified but predicted Gen 1)  
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
0x00000000–0x00000F43      Header: scene count, scene descriptors, object count,
                           object descriptors (see Header layout)
0x00000F44–0x00000F5F      Zero padding
0x00000F60–~0x0001E328     Engine name table (68-byte records, see below)
~0x0001E328–0x0001FFFF     Non-record bytes up to the first sector-aligned block
0x00020000–0x06864873      453 object resources, back to back, each sector-padded
0x06865000–0x089E4FFF      69 scene blocks, back to back, each sector-padded;
                           the last one ends exactly at end of file (0x089E5000)
```

Evidence: walking `offset → align(offset + u32 size at offset)` from
`0x20000` visits exactly 453 blocks whose header tables validate (see
[Object resources](#object-resources)). The same walk then visits exactly 69
scene blocks and lands on the file size, 144,592,896, with no remainder. The
two counts equal the header's `object_count` (453 at `0x0118`) and its first
`u32` (69 at `0x0000`). A brute-force scan for valid object-resource headers
at every 2,048-byte boundary of the file finds the same 453 and no others.

The bytes between the last name record and `0x20000` are not records. They
include Win9x kernel-range pointers (`0xBFF7xxxx`) and the ASCII string
`Interface and Startup`. They look like uninitialized buffer contents written
by the authoring tool, which is an inference, not a decoded structure.

### Header layout

```
Offset     Size       Type      Value (Showdown)  Notes
------     ----       --------  ----------------  -----
0x0000        4       uint32LE  69 (0x45)         Scene count (= number of scene blocks)
0x0004      276       [69]u32   (see below)       Scene descriptor table; meaning unknown
0x0118        4       uint32LE  453 (0x1C5)       Object count (= number of object resources)
0x011C    3,624       [453]rec  (see below)       Object descriptor table; 8 bytes × 453; meaning unknown
0x0F44       28       zero      —                 Padding
0x0F60      var       records   —                 Engine name table (WP-003)
0x20000     var       blocks    —                 First object resource (OBJ id 0, OBJ_DAPHNE_A)
```

**Correction (WP-002, 2026-11-13).** This page previously listed the first
asset payload at `0x10017E` and called the 453 eight-byte records
`(start, end)` file offsets, with a "confirmed values" table. Both were
wrong. Read as offsets, 295 of the 453 records are impossible (end before
start, or end beyond the end of the file), and 46 starts go backwards. Offset
`0x10017E` is not a payload start: it lies inside the second object resource
(`OBJ_FRED_A`, `0xDF000`–`0x168810`), in the middle of a cel's pixel stream.
Its leading bytes `F0 0C 25 5C` are a run of 12 pixels of color `0x255C`
(blue, Fred's trousers). The engine does not need these descriptor records to
find the resources, because the block walk above does. What they encode is
still open (see [Remaining unknowns](#remaining-unknowns)).

**Correction (WP-003, 2026-06-02):** prior versions of this doc placed `asset_count` at `0x011C` and the asset entry table at `0x0120`–`0x0F48`. Direct hex inspection against the SHA-256-locked binary shows the structure is shifted 4 bytes earlier: `asset_count` is at `0x0118`, the entry table starts at `0x011C`, and the pre-payload region begins at `0x0F44`. See the "4-byte gap at `0x0118`" subsection below for the diagnostic.

### Group descriptor table (offsets 0x04–0x117)

69 × 4-byte records. Values are monotonically increasing uint32s in the
range `0x34328117`–`0x44C440B9`. They are not file offsets (all exceed the
144 MB file size). WP-002 found that the count, 69, equals the number of
scene blocks, so these are one descriptor per scene, but the encoding is
still unknown. Extraction does not need them.

### Object descriptor table (offsets 0x011C–0x0F43)

453 × 8-byte records, two `uint32LE` each, one per object resource. Not
file offsets (see the correction above). The last record (OBJ 452) is
`(0, 0)`; OBJ 452's resource is 116 bytes with no cels. Example values:
OBJ 0 `(0x0010017E, 0x006F8114)`, OBJ 11 `(0x063B4001, 0x063B8002)`.
Meaning unknown; extraction does not need them.

#### Gen 1 (Showdown) — 4-byte gap at `0x0118`

WP-003 step 2 resolved this. The 4 bytes at file offset `0x0118`–`0x011B` are not padding and not an unidentified field — they are the `asset_count` (`uint32LE` = `0x000001C5` = 453). Prior spec offset for `asset_count` was `0x011C`; the diagnostic that pins the correction:

- Hex window @ `0x0110`–`0x0123` (cited verbatim from cached `TGIFILE.ART`):

  ```
  22 C1 7B 44   B9 40 C4 44   C5 01 00 00   7E 01 10 00   14 81 6F 00
  ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^
  desc[67]      desc[68]      asset_count   objdesc[0].a  objdesc[0].b
  ```

- `0x0118` decodes as `uint32LE` = 453 (matches the documented count).
- `0x011C` and `0x0120` are the two fields of the first object descriptor. WP-003 read them as `entry[0].start` / `entry[0].end`; WP-002 showed they are not offsets (see [Header layout](#header-layout)).

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
| 0 | Sequence records | `u32 size, u32 n, n × 12 bytes`; each 12-byte entry holds a `u32` ID of the form `0x8010_00xx` and a `u32` that is either 0 or a resource-relative frame-record offset | Layout observed on a sample; not checked across the corpus |
| 1 | Frame records | `u32 size (= 8 + 8n), u32 n, n × (i16 x, i16 y, u32 cel_offset)` | All 9,229 records conform; `n` is 0 or 1; every `cel_offset` is in table 3 |
| 2 | Polygons | `u32 size (= 16 + 4n), u32 n, i16 x, i16 y, i16 w, i16 h, n × (i16 x, i16 y)` | All 467 records conform; the box is the polygon's bounding box |
| 3 | Cels | see [Cel format](#cel-format) | All 9,042 sprite cels decode |

The frame record's `(x, y)` is the cel's draw offset from the object's
anchor. For Fred's first frame it is `(-40, -177)` against a 67 × 193 cel,
which puts the anchor near the feet. The polygons look like click regions:
Fred's first polygon is a 4-point, 67 × 193 rectangle at `(245, -54)`, the
same size as his first cel. Both
readings are inferred from the numbers and not traced in the executable.

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

69 blocks after the last object resource, one per scene descriptor. Each
holds an object placement list and a full-screen background cel.

```
Offset  Size  Type      Field
------  ----  --------  -----
0x00    4     uint32LE  block size (a multiple of 2,048 on every block)
0x0A    2     uint16LE  scene ID: 0x9000 + 0x10 × index on every block
0x0C    2     uint16LE  width (640; 1920 on scenes 19 and 51)
0x0E    2     uint16LE  height (480 on every block)
0x10    2     uint16LE  2 on 59 blocks, 1 on 10 (meaning unknown)
0xC0    4     uint32LE  placement count
0xC4    4     uint32LE  offset of the first placement record (0xD8 on every block)
0xD8    148 × count     placement records
...                     background cel, immediately after the placements
```

A placement record names an object and its animation in two zero-padded
ASCII fields (for example `OBJ_DAPHNE_A` and `ANIM_DAPHNE_AIDLE_MASTER`) and
ends in three `uint16` values. In scene 0, Daphne's are
`(0x00F1, 0x0155, 0x0161)`, which are plausibly x, y and depth. The background
cel starts at `0xD8 + 148 × count`. This rule holds on all 69 blocks, since
every background decodes and ends where its mask chunk begins. Further tables
follow the cel, and the header words at `0x80` and `0xAC` point near them;
their schema is open. Scenes 19 and 51 are 1920 × 480. Scene 51's background
repeats after 1280 pixels, which suggests a wrapping scroll. Which `ROOM_*` name goes with
which scene ID is not yet known.

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
16      4     uint32LE  flags? 0x100 on 9,086 of 9,111 cels; 0 on 18, 0x101 on 4,
                        and three large values with the low bit set. Meaning unknown;
                        the decode ignores it.
20      4     uint32LE  0 on every cel
24      var   bytes     RLE pixel stream, then up to 3 pad bytes, then the mask chunks
```

**Pixel stream.** A byte stream, read until `width × height` pixels have
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

**Pixel format.** 16-bit RGB565 stored **big-endian**:
`r = p >> 11`, `g = (p >> 5) & 63`, `b = p & 31`. The colors pin this.
Read big-endian, Fred's shirt is `0xF79E` (white), his trousers `0x255C`
(blue), hair `0xFFAD` (yellow) and skin `0xFF57` (peach). His ascot comes out
orange only under RGB565; RGB555 makes it green and his trousers purple.
Read little-endian, every color is wrong. There is no palette anywhere: the
image is truecolor, which closes the palette hunt of WP-003 and WP-002.

**Transparency.** In sprites, pixel `0x0000` is transparent, and sprites
decoded that way composite cleanly. Long transparent spans are runs of
`0x0000` (`F0 nn 00 00`). Whether backgrounds treat `0x0000` as opaque black
was not tested; the decoder renders them opaque.

**Mask chunks.** Each present mask is a size-prefixed span list:

```
u32 size, u16 x, u16 y, u16 w, u16 h,
then records until h rows are covered:
    u16 repeat_rows, u16 n, u16 runs[n]     # runs alternate skip, opaque, skip, ...
```

All 17,407 mask chunks in the file parse to exactly their declared size and
row count. A sprite's two masks differ slightly in box: Fred's cel 14
(76 × 194 pixels, at `0xFEF78`) has mask A at `(0, 1)` 75 × 193 and mask B at
`(0, 0)` 76 × 194. Their roles (hit-testing, shadow, outline) are not known.
A background's single mask is the full screen as one record:
`480 rows × (skip 0, opaque 640)`.

**Verification.** `py -3 tools/probe_art.py --verify` decodes all 9,111 cels
(9,042 sprite cels in 453 objects, 69 backgrounds). Every pixel stream
produces exactly `width × height` pixels and ends 0–2 bytes before its first
mask chunk, or before the cel end when it has no masks. Every mask chunk
parses exactly. Run time is about 20 s.

### Pre-payload region — engine name table

**Region:** file `0x0F44` to `0x20000` (exclusive). WP-003 placed its end at
`0x10017E` and described the part from `0xE6CC` as a "mixed region" of name
records interleaved with F0-opcode packed data. WP-002 corrected this. The
F0 data in that range is the first object resource (`OBJ_DAPHNE_A`,
`0x20000`–`0xDEF5C`) and the start of the second (`OBJ_FRED_A`, from
`0xDF000`). The name table itself ends near `0x1E328`. A local-only dump of
WP-003's range is preserved at `tools/samples/tgifile-art-prepayload-dump.bin`
(gitignored; SHA-256 `2AC950F319C4A7F550746EABD35DB3E873A92727E8A4FF43C5EB03BD7337FA4D`).

This region is the **engine's resource-name catalog**, with type-tagged 32-bit IDs mapping to fixed-width ASCII names (and, for some records, per-record metadata).

#### Gen 1 (Showdown) — Region layout

```
Sub-range            Length     Content
------------------   --------   -----------------------------------------------
0x0F44–0x0F5F          28 B     Zero padding
0x0F60–0xE6CC      55,148 B     Continuous 68-byte-stride name records (811 records).
                                Sub-sections: 42 ROOM + 453 OBJ + 316 ANIM (see below).
0xE6CC–~0x1E328     ~64 KB      Further name records on a 68-byte stride (WP-003
                                counted ≈ 611 more), several with non-zero metadata.
                                The last name string is `ANIM_HC_ARCS0x03` at 0x1E2E4.
~0x1E328–0x1FFFF     ~7 KB      Non-record bytes (see Archive layout)
```

#### Gen 1 (Showdown) — Record format

```
Offset within record   Size   Type        Notes
--------------------   ----   --------    -----
0                         4   uint32LE    Resource ID — see ID schema below
4                        44   char[44]    NUL-terminated ASCII name, zero-padded to 44 bytes
48                       20   bytes       Per-record metadata (mostly zero across the
                                          continuous block; carries non-zero data for a
                                          minority of records — schema TBD, see below)
```

Record stride is 68 bytes throughout the continuous block (0x0F60–0xE6CC). Of the 811 records in that block, exactly one (`ANIM_BIG_HEAD_BG_P09DAPHNE` at file `0xE644`, id `0x3A800000`) carries a non-zero 20-byte metadata payload:

```
metadata bytes (offset 48–67 of record): 86 19 00 00  BE 17 00 00  BE 17 00 00  00 00 00 00  00 00 00 00
as 5x uint32LE:                          6,534         6,078         6,078         0             0
```

WP-003 read these as plausibly `(width, height_a, height_b)`. That reading
is unlikely now that cel dimensions are known: no cel in the file is
thousands of pixels in size. The metadata is not a palette index either,
because the images are truecolor. Schema still open.

#### Gen 1 (Showdown) — Resource ID schema

The high byte of each `uint32LE id` is a type tag:

```
Tag        Type   Records in continuous block   Notes
--------   ----   ---------------------------   -----
0x10       ROOM   42                            IDs span 0x1000001B–0x10000044 (room numbers 27–68)
0x20       OBJ    453                           IDs span 0x20000000–0x200001C4 (contiguous; count
                                                matches `object_count`)
0x31–0x3F  ANIM   316                           Interleaved sub-tags; second byte appears to encode
                                                an animation sub-category (e.g. 0x40 = CURSOR,
                                                0x70 = TOOLBAR, 0xA0 = ARTIE character, 0x50 = PIE_NOON
                                                sequence). Stored in load order, not sorted.
```

OBJ ids index the object resources directly. WP-003 inferred this from the
count; WP-002 confirmed it by decoding resources 0–2 and matching them to
`OBJ_DAPHNE_A`, `OBJ_FRED_A` and `OBJ_SCOOBY_A`. ROOM and ANIM names have no
resource block of their own: ANIM names appear inside scene placement
records, next to the OBJ they animate.

#### Gen 1 (Showdown) — Strings cross-check (WP-007 hand-off)

Sample names from the continuous-block name table were cross-referenced against `tools/exes/showdown/strings-ansi.txt` (1,959 unique ANSI strings extracted from `Scooby.exe` by [WP-007](../work-packets/WP-007-strings-and-imports.md)):

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
- **Phantom:** disc inspection pending; toolchain (Rich Header) matches Showdown identically — Phantom is classified Gen 1 and is *predicted* to use `TGIFILE.ART`, but the archive header hasn't been hex-checked yet. Lock in next time the disc is mounted with `Format-Hex E:\scooby\TGIFILE.ART -Count 8` and compare against `45 00 00 00`. Once mounted, `py -3 tools/probe_art.py --art <Phantom TGIFILE.ART> --no-hash --verify` is the cross-title check (EC-002 Phase D).
- **Jinx (Gen 2):** uses `MMFW`-wrapped archives (`Mummy.MMF`, `HD.MMA`, `HD.MMP`) — confirmed not `TGIFILE.ART`. See [`mmfw-container.md`](mmfw-container.md).
- **Case File #1 (Gen 3):** uses `MMFW`-wrapped archives (`MuseumCD.MMP`, `MuseumCD.MMA`) — same wrapper as Jinx. See [`mmfw-container.md`](mmfw-container.md).

The `TGIFILE.ART` format is **specific to Gen 1**. Cross-title implementation does not generalize to Gen 2/3 via this spec — those need the separate MMFW parser. Whether the Gen 2/3 picture payloads reuse this cel format (`F0` runs over big-endian RGB565) is now a cheap test, the hypothesis in [mmfw-container](mmfw-container.md#hypotheses-unverified).

---

## Remaining unknowns

- Encoding of the 69 scene descriptors (`0x0004`) and the 453 object
  descriptors (`0x011C`). Not offsets. Not needed to extract images, but the
  engine presumably reads them.
- Which `ROOM_*` name goes with which scene block. There are 42 ROOM names
  and 69 scene blocks; scene IDs run `0x9000`–`0x9440`.
- Sequence records (table 0 of each object resource): the meaning of the
  `0x8010_00xx` IDs and how a sequence orders frames. The object's ANIM
  names, as used in scene placements, presumably resolve here.
- The scene block header words at `0x10`, `0x80` and `0xAC`, and the tables
  after the background cel.
- Roles of the two per-cel mask chunks.
- The 20-byte per-record metadata in the name table.
- Whether backgrounds treat pixel `0x0000` as transparent.

The decode itself has no open questions.

## Next steps

1. Phase 2 can start: [WP-010](../work-packets/WP-010-scummvm-scaffold.md)
   and the Phase 3 `Common::Archive` reader can be written from this page.
   The object-resource walk, cel header and RLE loop are small enough to port
   directly from `tools/probe_art.py`.
2. Map scene blocks to `ROOM_*` names, then render one room with its placed
   objects. This exercises placement records and frame anchors end to end.
3. Decode sequence records (table 0) to drive animation playback. The
   [WP-001](../work-packets/WP-001-ghidra-session.md) Ghidra trace now has a
   narrower target: the sequence interpreter and the descriptor tables, not
   the image decode.
4. Run `--verify` against Phantom's `TGIFILE.ART` (EC-002 Phase D).

## Success condition

Render at least one *Showdown* background or sprite to PNG/BMP outside the
engine, visually matching in-game output. **Met (WP-002, 2026-11-13).**
`OBJ_DAPHNE_A` cel 0 decodes to Daphne in her canonical colors, and scene
blocks decode to full Ghost Town backgrounds. No WP-009 reference screenshots
exist yet, so the visual check was against the characters' canonical look,
not a captured frame.

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Phase 1, primary risk area
- Companion specs: [audio-archives](audio-archives.md), [scooby-exe](scooby-exe.md)
- Decoder: [`tools/probe_art.py`](../../tools/probe_art.py)
