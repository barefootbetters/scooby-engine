---
layout: default
title: "Format Spec: TGIFILE.ART"
---

# Format Spec: `TGIFILE.ART`

**Status:** Structural hypothesis confirmed — payload compression unresolved  
**Engine generation:** **Gen 1** (Showdown 2000, Phantom 2001 — Phantom's archive format unverified but predicted Gen 1)  
**Source disc:** *Scooby-Doo! Showdown in Ghost Town* (2000, The Learning Company)  
**Sample file:** `scooby\TGIFILE.ART` on the Showdown disc  
**File size:** 144,592,896 bytes (≈ 144 MB)  
**Source binary SHA-256:** `B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807` (cached `tools/exes/showdown/TGIFILE.ART` per [tools/exes/README §Showdown](../../tools/exes/README.md#showdown-gen-1)). Every Findings subsection below derives from this binary; a re-rip producing a different SHA invalidates the corresponding rows.  
**Vision doc reference:** [Project Vision](../01-VISION.md) — Phase 1 primary risk area; see "Engine Lineage" section for generation classification.

This file is the primary technical risk for the engine. The two-level index
structure is now understood (see Findings). The remaining unknown is the
per-entry payload compression scheme. Until at least one entry decodes to
a recognizable image, Phase 2 should not start.

**Generation scope:** this format spec covers **Gen 1** titles only.
Jinx (Gen 2) and Case File #1 (Gen 3) use the `MMFW` wrapper container
format — see [`mmfw-container.md`](mmfw-container.md) for that spec. The
two formats are not interchangeable; the ScummVM engine will need both
parsers selected by the detection-time generation flag.

---

## Findings

### Header layout

```
Offset     Size       Type      Value (Showdown)  Notes
------     ----       --------  ----------------  -----
0x0000        4       uint32LE  69 (0x45)         Top-level group count
0x0004      276       [69]u32   (see below)       Group descriptor table; 4 bytes × 69 entries
0x0118        4       uint32LE  453 (0x1C5)       Asset entry count (all groups combined)
0x011C    3,624       [453]rec  (see below)       Asset entry table; 8 bytes × 453 entries
0x0F44 1,045,050      blob      (see Findings)    Pre-payload region — engine name table + per-record metadata + packed data (WP-003)
0x10017E    var       blob      —                 First asset payload
```

The first asset payload confirmed at offset **1,048,958 (0x10017E)**.

**Spec correction (WP-003, 2026-06-02):** prior versions of this doc placed `asset_count` at `0x011C` and the asset entry table at `0x0120`–`0x0F48`. Direct hex inspection against the SHA-256-locked binary shows the structure is shifted 4 bytes earlier: `asset_count` is at `0x0118`, the entry table starts at `0x011C`, and the pre-payload region begins at `0x0F44`. The mismatch was visible because the bytes at `0x011C`–`0x011F` decode as `7E 01 10 00` = `0x0010017E` = 1,048,958, which is `entry[0].start` (not an asset count). See the "4-byte gap at `0x0118`" subsection below for the diagnostic.

### Group descriptor table (offsets 0x04–0x117)

69 × 4-byte records. Values are monotonically increasing uint32s in the
range `0x34328117`–`0x44C440B9`. These do **not** appear to be raw file
offsets (all exceed the 144 MB file size). Working hypothesis: each
4-byte record encodes a packed (group_index, asset_index_start) pair, or
is a delta-compressed reference. Meaning TBD — these may not be needed
for extraction if asset entries are sufficient.

### Asset entry table (offsets 0x011C–0x0F43)

453 × 8-byte records: two `uint32LE` fields per entry.

```
Offset within record  Field     Notes
--------------------  -----     -----
0                     start     Absolute byte offset of asset payload in the file
4                     end       Absolute byte offset of the next asset boundary
```

Payload size = `end - start`. Confirmed values:

| Entry | start      | end        | size (bytes) |
|-------|------------|------------|--------------|
| 0     | 1,048,958  | 7,307,540  | 6,258,582    |
| 1     | 11,829,687 | 19,022,169 | 7,192,482    |
| 2     | 24,674,616 | 29,786,878 | 5,112,262    |
| 3     | 42,336,796 | 51,183,818 | 8,847,022    |

Average compressed size ≈ 2–9 MB per entry. The large spread suggests a
mix of multi-frame sprite animations and single-frame backgrounds.

### Per-entry payload

No standard image magic bytes at the tested offsets. First 8 bytes at
entry 0 (offset 1,048,958):

```
F0 0C 25 5C 12 AE F0 08  ...
```

Observations:
- `F0` appears frequently — consistent with an opcode or run-length control byte.
- No RIFF, BMP, PNG, or PCX signatures found.
- Likely a proprietary RLE or LZ variant. Next step: write a Python probe
  script under `tools/probe_art.py` that tries common decode strategies
  (raw RLE with 0xF0 as control, LZ with sliding window, raw 8-bit palette).

#### Gen 1 (Showdown) — 4-byte gap at `0x0118`

WP-003 step 2 resolved this. The 4 bytes at file offset `0x0118`–`0x011B` are not padding and not an unidentified field — they are the `asset_count` (`uint32LE` = `0x000001C5` = 453). Prior spec offset for `asset_count` was `0x011C`; the diagnostic that pins the correction:

- Hex window @ `0x0110`–`0x0123` (cited verbatim from cached `TGIFILE.ART`):

  ```
  22 C1 7B 44   B9 40 C4 44   C5 01 00 00   7E 01 10 00   14 81 6F 00
  ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^   ^^^^^^^^^^^
  desc[67]      desc[68]      asset_count   entry[0].start entry[0].end
  ```

- `0x0118` decodes as `uint32LE` = 453 (matches the documented count).
- `0x011C` decodes as `uint32LE` = `0x0010017E` = 1,048,958 (which is `entry[0].start` from the existing confirmed-values table above).
- `0x0120` decodes as `uint32LE` = `0x006F8114` = 7,307,540 (which is `entry[0].end` from the same table).

The whole header was shifted 4 bytes later in the prior spec. The corrected table is now in the [Header layout](#header-layout) section above; this subsection records the diagnostic.

### Pre-payload region — engine name table

**Region:** file `0x0F44` to `0x10017E` (exclusive), 1,045,050 bytes (`0xFF23A`).

This region was previously labeled "Packed/padded region before first asset data." WP-003 characterizes it as the **engine's resource-name catalog**, with type-tagged 32-bit IDs mapping to fixed-width ASCII names (and, for some records, per-record metadata). A local-only dump of the full region is preserved at `tools/samples/tgifile-art-prepayload-dump.bin` (gitignored; SHA-256 `2AC950F319C4A7F550746EABD35DB3E873A92727E8A4FF43C5EB03BD7337FA4D`), regenerable via `bytes_for_region = Path('tools/exes/showdown/TGIFILE.ART').read_bytes()[0x0F44:0x10017E]`.

#### Gen 1 (Showdown) — Region layout

```
Sub-range            Length     Content
------------------   --------   -----------------------------------------------
0x0F44–0x0F5F          28 B     Zero padding (alignment between asset entry table
                                end at 0x0F44 and first name record at 0x0F60)
0x0F60–0xE6CC      55,148 B     Continuous 68-byte-stride name records (811 records).
                                Sub-sections: 42 ROOM + 453 OBJ + 316 ANIM (see below).
0xE6CC–0x10017E   989,874 B     Mixed region: additional 68-byte-aligned name records
                                interleaved with F0-opcode packed binary data. Approx.
                                611 further valid name-record positions on a 68-byte
                                stride (e.g., last clean record at file 0x1DEE4 =
                                `ANIM_SUSPECT_CLUE_INFORH_SHERIFF_GOLD_STAR`,
                                id 0x3F90001C). The interleaved packed data shares the
                                same F0-byte signature as the asset payloads (≥ 0x10017E)
                                and is plausibly per-resource animation cel / frame data
                                co-located with each record. Schema TBD — deferred to
                                [WP-001](../work-packets/WP-001-ghidra-session.md)
                                (Ghidra trace) and [WP-002](../work-packets/WP-002-tgifile-art-decoder.md)
                                (decoder).
```

The full byte range is accounted for: 28 B padding + 55,148 B clean name table + 989,874 B mixed region = 1,045,050 B = `PRE_END - PRE_START` (`0x10017E - 0x0F44`).

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

Plausibly `(width, height_a, height_b, ?, ?)` for a multi-cel sprite, but the precise schema is unresolved — WP-001 should trace the loader function in `Scooby.exe` against this offset to disambiguate. The same metadata field is non-zero on an unknown number of records in the **mixed region** (0xE6CC–0x10017E); those records were not enumerated in WP-003 scope.

#### Gen 1 (Showdown) — Resource ID schema

The high byte of each `uint32LE id` is a type tag:

```
Tag        Type   Records in continuous block   Notes
--------   ----   ---------------------------   -----
0x10       ROOM   42                            IDs span 0x1000001B–0x10000044 (room numbers 27–68)
0x20       OBJ    453                           IDs span 0x20000000–0x200001C4 (contiguous; count
                                                matches `asset_count`)
0x31–0x3F  ANIM   316                           Interleaved sub-tags; second byte appears to encode
                                                an animation sub-category (e.g. 0x40 = CURSOR,
                                                0x70 = TOOLBAR, 0xA0 = ARTIE character, 0x50 = PIE_NOON
                                                sequence). Stored in load order, not sorted.
```

The **OBJ count exactly matches `asset_count` (453)** and OBJ IDs are contiguous 0–452, strongly suggesting `OBJ`-tagged records are 1:1 with the asset entry table — i.e., `entry[i]` is the payload for `OBJ` id `i`. ROOM and ANIM records exceed the asset count; those resources are referenced by name elsewhere (e.g. `object.ini` lookups, hardcoded engine references) but do not have a direct asset payload in `TGIFILE.ART`. This answers the prior "Remaining unknown — how does `Scooby.exe` request a specific asset by logical ID?" — by `(type_tag, sub_index)` from the name table, with OBJ IDs indexing the asset entry table directly.

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
- **Phantom:** disc inspection pending; toolchain (Rich Header) matches Showdown identically — Phantom is classified Gen 1 and is *predicted* to use `TGIFILE.ART`, but the archive header hasn't been hex-checked yet. Lock in next time the disc is mounted with `Format-Hex E:\scooby\TGIFILE.ART -Count 8` and compare against `45 00 00 00`.
- **Jinx (Gen 2):** uses `MMFW`-wrapped archives (`Mummy.MMF`, `HD.MMA`, `HD.MMP`) — confirmed not `TGIFILE.ART`. See [`mmfw-container.md`](mmfw-container.md).
- **Case File #1 (Gen 3):** uses `MMFW`-wrapped archives (`MuseumCD.MMP`, `MuseumCD.MMA`) — same wrapper as Jinx. See [`mmfw-container.md`](mmfw-container.md).

The `TGIFILE.ART` format is **specific to Gen 1**. Cross-title implementation does not generalize to Gen 2/3 via this spec — those need the separate MMFW parser.

---

## Remaining unknowns

- Meaning of the 69-entry group descriptor table.
- Payload compression algorithm (RLE variant? LZ? custom?). Note: WP-003
  found F0-opcode packed data **also** present inside the pre-payload
  region (0xE6CC–0x10017E), interleaved with name records. The same
  decoder will need to handle both locations.
- Pixel format: palette-indexed (8-bit) vs. truecolor. **WP-003 negative
  finding:** no contiguous 256-entry RGB or RGBA palette exists anywhere in
  the pre-payload region — stride-3 / stride-4 / 768-byte / 1024-byte
  scans all came back empty. If the payload is palette-indexed, the
  palette lives either *inside* each asset payload's leading bytes
  (per-asset palette) or *inside* the 20-byte per-record metadata field
  on OBJ records in the mixed region (per-resource palette index).
  Either way, palette discovery moves to [WP-002](../work-packets/WP-002-tgifile-art-decoder.md).
- Whether sprite frames and backgrounds share a payload format or differ.
- Schema for the 20-byte per-record metadata field (offsets 48–67 of
  each name-table record). One record in the continuous block carries
  three uint32LE values that may be `(width, height_a, height_b)`;
  the full schema applies to an unknown number of records in the mixed
  region. Deferred to [WP-001](../work-packets/WP-001-ghidra-session.md)
  Ghidra trace.
- Structure of the mixed region (0xE6CC–0x10017E, ≈ 990 KB) — name
  records interleaved with F0-opcode packed data, alignment and per-record
  layout TBD. Deferred to WP-001 / WP-002.

## Next steps

1. Write `tools/probe_art.py` — enumerate entries, dump payloads to files,
   attempt decode with raw `F0`-opcode RLE.
2. Try viewing raw payload as 640×480×1 (8-bit palette) — if a valid image
   appears, skip compression analysis.
3. Load `Scooby.exe` in Ghidra and find the `TGIFILE.ART` open/read call
   to trace the decode path (see [scooby-exe](scooby-exe.md)).
4. Once one entry decodes cleanly, cross-check against *Phantom of the
   Knight* `TGIFILE.ART` to confirm the format generalizes.

## Success condition

Render at least one *Showdown* background or sprite to PNG/BMP outside the
engine, visually matching in-game output.

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Phase 1, primary risk area
- Companion specs: [audio-archives](audio-archives.md), [scooby-exe](scooby-exe.md)
