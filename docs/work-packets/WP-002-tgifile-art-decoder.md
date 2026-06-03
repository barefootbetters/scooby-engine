---
layout: default
title: "WP-002: TGIFILE.ART Decoder"
---

# WP-002: `TGIFILE.ART` payload decoder + first image extraction

**Status:** 📝 Drafted
**Phase:** 1 — Format Research
**Depends on:** WP-001 (preferred — gives decode algorithm directly; can be started without if Ghidra path is blocked)
**Companion EC:** [EC-002](../execution-checklists/EC-002-probe-art-harness.md)
**Estimated effort:** Half-day if WP-001 succeeds; 1–2 days if blind-decoding

---

## Goal

Decode at least one `TGIFILE.ART` entry from *Showdown in Ghost Town* to a recognizable PNG or BMP that visually matches in-game output. This satisfies Phase 1 exit criterion #1 and unblocks Phase 2.

## Background

`TGIFILE.ART` structure is understood (69 groups, 453 asset entries, 8-byte `(start, end)` records — see `docs/formats/tgifile-art.md`). The remaining unknown is the per-entry payload compression. Opening bytes of entry 0 (`F0 0C 25 5C 12 AE F0 08`) match no standard codec.

**WP-003 baseline (2026-06-02) — first-decode strategy revised.** [WP-003](WP-003-pre-payload-region.md)
established three facts that change how this WP should approach the first decode:

1. **Entry 0 is `OBJ_DAPHNE_A`**, not an unnamed background. WP-003 confirmed
   `entry[i]` is the payload for OBJ id `i`, and the OBJ name table maps
   id 0 → `OBJ_DAPHNE_A`. The "first image" target is a character sprite
   (Daphne, presumably idle or one walk-cycle frame), not a full-screen
   background. Visual verification should look for a Daphne-shaped
   silhouette, not a room. WP-009's reference screenshot library should
   include at least one clear Daphne sprite shot.
2. **Palette is NOT in the pre-payload region.** WP-003 ran exhaustive
   stride-3 / stride-4 / 768-byte / 1024-byte scans on `0x0F44`–`0x10017E`
   and found nothing palette-shaped. Palette discovery now has two
   leading candidates: (a) per-asset leading bytes inside each
   payload — the palette is co-located with the asset; (b) the 20-byte
   per-record metadata field at offsets 48–67 of name-table records —
   the palette index or a small per-resource palette lives there. The
   "blind decode-guessing" strategy should test (a) first by probing
   for a 256-entry RGB or RGBA block in the first 768–1024 bytes of
   entry 0's payload.
3. **The 20-byte metadata field carries `(6534, 6078, 6078, 0, 0)`** on
   at least one record (`ANIM_BIG_HEAD_BG_P09DAPHNE` at file `0xE644`),
   plausibly `(width, height_a, height_b)`. If the per-record metadata
   on `OBJ_DAPHNE_A`'s name-table record carries similar values, that's
   a free pre-decode dimensions hint. Worth reading the metadata field
   of name-table records on the OBJ section before running blind decode.

**WP-008 baseline (2026-06-03) — labeling rule confirmed + coverage expectations sharpened.** The [Showdown `object.ini` analysis](../formats/scooby-exe.md#objectini-interpreter-behavior) confirmed the engine is name-driven (MODE_A), so the deterministic naming rule from [WP-008 §Notes](WP-008-object-ini-catalog.md#notes) — `entry_<index>_<wp003_name>.png`, sanitization preserving uppercase verbatim, anything outside `[A-Za-z0-9_]` → `_` — applies directly. Confirmed clean: every observed name (`OBJ_DAPHNE_A`, `OBJ_P40_TO_P33`, `ANIM_CURSORARROW`) is already filename-safe; sanitization is a no-op on every observed input. The 65 unmatched references from the WP-008 cross-check (21 scripted/engine `ROOM_*`, 25 invisible-hotspot `OBJ_*`, 19 inventory-specific `ANIM_*`) are **not expected to resolve to decoded `TGIFILE.ART` entries** — they're hotspots without art payloads, scripted rooms rendered by per-room functions (see [WP-001 §Background](WP-001-ghidra-session.md#background)), and inventory animations that live in another store. EC-002's probe coverage should treat their absence as expected, not as a decoder bug; verifying zero of them produce decoded output is itself a finding worth recording.

Two additional test corpus opportunities WP-003 surfaced:

- **F0-opcode packed data interleaved in the pre-payload mixed region**
  (`0xE6CC`–`0x10017E`, ~990 KB) uses the same compression signature as
  the asset payloads. Smaller chunks may be easier to test against
  than the 6 MB entry 0 — useful for fast iteration on the decode
  algorithm before committing to a full-asset decode pass.
- **Header offsets corrected** — `asset_count` is at `0x0118` (not
  `0x011C`); the asset entry table is at `0x011C`–`0x0F43`. The decoder
  should read entry records from the corrected offsets per
  [tgifile-art.md §Header layout](../formats/tgifile-art.md#header-layout).

Three viable strategies:

| Strategy | Time | Confidence | Trigger |
|---|---|---|---|
| Reimplement decode from Ghidra trace (WP-001 output) | Half-day | High | WP-001 succeeded |
| Blind decode-guessing: opcode RLE → 8-bit palette → LZ variants | 1–2 days | Medium | WP-001 blocked or partial |
| Hybrid — Ghidra gives algorithm name (e.g. "LZ77"), confirm by reimplementing standard variant | Half-day | High | WP-001 partial |

## Scope

In scope:
- `tools/probe_art.py` — Python harness for extracting and attempting to decode entries
- Decoder implementation in Python sufficient to render one entry to PNG/BMP
- Visual comparison against a screenshot from gameplay or a YouTube longplay
- **Palette discovery** — WP-003 ruled out the pre-payload region (no 256-entry RGB / RGBA palette anywhere in `0x0F44`–`0x10017E`). Investigate **(a) per-asset leading bytes** (probe for a 256×3 or 256×4 block at the start of entry 0's payload) and **(b) the 20-byte per-record metadata field** at offsets 48–67 of name-table records (may carry a palette index or small palette per resource). One of these is the right answer; both are cheap to test.
- **Reading the 20-byte metadata field on `OBJ_DAPHNE_A`'s name-table record** at the start of decode to grab any free dimensions / palette-index hint (per WP-003 §Record format)
- Output filenames should use the WP-003 name table (e.g. `tgifile-art-entry000-OBJ_DAPHNE_A.png`) for self-describing decode outputs
- Recording the decode algorithm in `docs/formats/tgifile-art.md`

Out of scope:
- C++ decoder implementation in the ScummVM engine (Phase 3, WP-020 equivalent)
- Decoding all 453 entries — one is sufficient for Phase 1 exit
- Sprite/animation frame extraction beyond what's needed to verify the algorithm

## Dependencies

- `Scooby.exe` decode trace from WP-001 (preferred)
- Pre-payload region findings from WP-003 (✅ landed 2026-06-02 — name table, header offsets corrected, negative palette finding, 20-byte metadata field surfaced)
- Python 3.x with `Pillow` for PNG output
- Hex viewer for sanity-checking decoded byte patterns

## Exit criteria

1. `tools/probe_art.py` runs and successfully extracts and decodes at least entry 0 of *Showdown*'s `TGIFILE.ART`.
2. Output PNG/BMP is visually recognizable as a Scooby-Doo asset (background, sprite frame, or UI element). Recognizability is the test, not pixel-exact match against a specific source.
3. `docs/formats/tgifile-art.md` Findings → "Per-entry payload" section populated with: compression algorithm name (or description), pixel format (palette vs. truecolor + bit depth), palette location and format, decode pseudocode or working Python.
4. Output PNG/BMP committed to `tools/samples/tgifile-art-entry0.png` for visual reference.

## Deliverables

- [`tools/probe_art.py`](../../tools/probe_art.py) — extraction + decode harness
- [`tools/samples/tgifile-art-entry0.png`](../../tools/samples/) — first successful decode
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — Findings section

## Notes

- The `F0` byte appearing twice in the first 8 bytes of entry 0 is the strongest pattern signal. EC-002 enumerates the specific opcodes and operand layouts to try.
- If the algorithm turns out to be a custom RLE, capture the full opcode table in the format spec — it's the load-bearing piece of intellectual property for Phase 3's C++ decoder.
- Cross-title verification (entry 0 of Phantom's `TGIFILE.ART` decodes with the same algorithm) is a stretch goal for this WP and a prerequisite for treating the TerraGlyph trilogy as engine-compatible.
- If after EC-002's full enumeration the decode still fails, the WP escalates: open a discussion with the user about whether to invest more time on Ghidra (WP-001 extension) or accept reduced Phase 5 scope.
