# Format Spec: `TGIFILE.ART`

**Status:** Structural hypothesis confirmed — payload compression unresolved  
**Source disc:** *Scooby-Doo! Showdown in Ghost Town* (2000, The Learning Company)  
**Sample file:** `C:\pcloud\SCOOBY\Scooby Doo Showdown in Ghost Town.iso` → `scooby\TGIFILE.ART`  
**File size:** 144,592,896 bytes (≈ 144 MB)  
**Vision doc reference:** [`docs/01-VISION.md`](../01-VISION.md) — Phase 1 primary risk area

This file is the primary technical risk for the engine. The two-level index
structure is now understood (see Findings). The remaining unknown is the
per-entry payload compression scheme. Until at least one entry decodes to
a recognizable image, Phase 2 should not start.

---

## Findings

### Header layout

```
Offset  Size  Type      Value (Showdown)  Notes
------  ----  --------  ----------------  -----
0x0000     4  uint32LE  69 (0x45)         Top-level group count
0x0004   276  [69]u32   (see below)       Group descriptor table; 4 bytes × 69 entries
0x011C     4  uint32LE  453 (0x1C5)       Asset entry count (all groups combined)
0x0120  3624  [453]rec  (see below)       Asset entry table; 8 bytes × 453 entries
0x0F48     ?  blob      —                 Packed/padded region before first asset data
```

The first asset payload confirmed at offset **1,048,958 (0x10017E)**.

### Group descriptor table (offsets 0x04–0x117)

69 × 4-byte records. Values are monotonically increasing uint32s in the
range `0x34328117`–`0x44C440B9`. These do **not** appear to be raw file
offsets (all exceed the 144 MB file size). Working hypothesis: each
4-byte record encodes a packed (group_index, asset_index_start) pair, or
is a delta-compressed reference. Meaning TBD — these may not be needed
for extraction if asset entries are sufficient.

### Asset entry table (offsets 0x120–0xF47)

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

### Cross-title verification

Not yet performed. The `TGIFILE.ART` filename appears on all six ISOs —
confirm format is identical before implementing the parser.

---

## Remaining unknowns

- Meaning of the 69-entry group descriptor table.
- Payload compression algorithm (RLE variant? LZ? custom?).
- Pixel format: palette-indexed (8-bit) vs. truecolor; palette location.
- Whether sprite frames and backgrounds share a payload format or differ.
- Whether there is a name/ID mapping (how does `Scooby.exe` request a
  specific asset by logical ID?).

## Next steps

1. Write `tools/probe_art.py` — enumerate entries, dump payloads to files,
   attempt decode with raw `F0`-opcode RLE.
2. Try viewing raw payload as 640×480×1 (8-bit palette) — if a valid image
   appears, skip compression analysis.
3. Load `Scooby.exe` in Ghidra and find the `TGIFILE.ART` open/read call
   to trace the decode path (see [`scooby-exe.md`](scooby-exe.md)).
4. Once one entry decodes cleanly, cross-check against *Phantom of the
   Knight* `TGIFILE.ART` to confirm the format generalizes.

## Success condition

Render at least one *Showdown* background or sprite to PNG/BMP outside the
engine, visually matching in-game output.

---

## References

- Vision doc: [`docs/01-VISION.md`](../01-VISION.md) — Phase 1, primary risk area
- Companion specs: [`audio-archives.md`](audio-archives.md), [`scooby-exe.md`](scooby-exe.md)
