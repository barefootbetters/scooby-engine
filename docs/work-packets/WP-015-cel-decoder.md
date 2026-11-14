---
layout: default
title: "WP-015: Cel Decoder and Room Background"
---

# WP-015: Cel decoder, and a room background on screen (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (resource loading; first graphics)
**Depends on:** WP-014 ✅ (`ArtArchive`), WP-001 ✅ (decode path traced), WP-002 ✅ (cel format)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-015-2026-11-14](../reference/pre-flight-WP-015-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Every cel matches `probe_art.py` | ✅ Both titles were started from their mounted ISOs at `graphics` level 3. The engine logged an MD5 of each cel's coverage and colour (solid colour where it applies). A reference built on `probe_art.py`'s decoder logged the same per-cel MD5s. The two logs are identical: Showdown 9,111 cels (453 objects + 69 rooms), Phantom 5,810, 0 bad. |
| 2. Screen matches | ✅ Screen MD5 after drawing room 0: Showdown `ROOM_P01_Town_Center` `4addb408…8109`, Phantom `ROOM_P31_KST` `9401c2a4…2dfd`. Both equal the probe's composite of the room's layers. |
| 3. Screenshot | ✅ Both rooms were captured from the ScummVM window, which scales to 960 × 720, and sent to Jeff. They are not in git. |
| 4. Malformed cel rejected | ✅ Room 0's background cel header was corrupted in a scratch copy, past the detection MD5 range: mask A offset out of the block, 65,535 × 65,535 size, and height 20,000 so the stream overruns its block. Each gets a warning naming the cel, the room is not drawn, and the engine keeps running. The copy was restored, hash-checked and deleted. |
| 5. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The fork diff stays inside `engines/scooby/`. Commit [`644305dddc`](https://github.com/barefootbetters/scummvm/commit/644305dddc), pushed. |

**Deviations:**

- **First run found two oversized cels.** The decoder's first size guard capped each side at 4,096 pixels. Each title has one taller cel, 400 × 5,800 (Showdown) and 400 × 5,400 (Phantom), and both were rejected. The guard now caps the pixel count at 2²⁴, and both decode and match.
- **The fork commit also holds the *Activity Challenge* detection entry.** It is in `detection.h` and `detection_tables.h`. Another session had written it uncommitted in the shared `C:\dev\scummvm` checkout, and `git add engines/scooby` swept it into this commit before it was pushed. Its values match [WP-013](WP-013-activity-challenge-engine-check.md) §Detection. Splitting it out would need a force-push. Jeff chose to leave it in this commit (2026-11-14). [Integration §3](../02-SCUMMVM-INTEGRATION.md#3-game-detection-table-adgamedescription) lists the entry (PR #46).

---

## Goal

Decode `TGIFILE.ART` cels in the engine and draw a room background in the
ScummVM window. This is the first time the fork shows Showdown's or
Phantom's art.

## Background

[tgifile-art §Cel format](../formats/tgifile-art.md#cel-format) specifies
the cel completely, and `probe_art.py --verify` decodes all of them:

- **Header.** 24 bytes: size, width, height, the mask A and mask B offsets,
  a solid flag, an RLE flag and the solid colour.
- **Pixels.**
  - RLE: `F0 count hi lo` is a run, anything else a 2-byte literal; words
    are big-endian.
  - Raw cels: little-endian words.
  - Solid cels: mask A is filled with the solid colour.
- **Masks.** Mask A pixels are opaque RGB565, mask B pixels are
  translucent ARGB4444, and every other pixel is transparent.
- **Mask encoding.** Each mask is a span list: a box, then `repeat_rows`,
  `n`, and `n` runs alternating skip and covered.

A room block names its art through ten layer slots at `0x80`. Each non-zero
slot points to a frame record: `n` entries of `(i16 x, i16 y, u32 cel
offset)`. The renderer creates one sprite per used slot. In both Gen 1
titles only slot 0 is used, and it holds the full-screen background at
`(0, 0)`.

## Scope

**In scope (fork, `engines/scooby/` only):**

- `Cel` (`cel.{h,cpp}`) decodes one cel from a block in memory into 16-bit
  pixel words plus a per-pixel coverage map (none, opaque, translucent).
  Every offset, run and span is checked against the block and the cel
  bounds.
- `Cel::drawOpaque()` copies the opaque pixels onto an RGB565 surface.
- A room renderer that draws the cels of every used layer slot of a room
  block, in the opaque pass only.
- **Startup.** For Gen 1, the engine draws room 0 once the art file is open.
  The console command `room <ROOM_name>` switches rooms.
- **Checks.**
  - `graphics` level 3: decode every cel in the file and log an MD5 of its
    pixels and coverage.
  - `graphics` level 1: log an MD5 of the screen after a room is drawn.

**Out of scope:**

- Translucent (mask B) blending, which backgrounds don't use. It comes with
  sprites, where it can be checked.
- Placed objects, sequences and animation.
- Scrolling in the 1,920-pixel rooms; the left 640 pixels are shown.
- RGB555 screens.

## Exit criteria

1. [x] Every cel in Showdown and in Phantom decodes in the engine to the
   same pixels and coverage as `probe_art.py`. Checked by MD5 per cel,
   9,111 cels in Showdown.
2. [x] The screen after drawing room 0 matches the background decoded by
   `probe_art.py`, pixel for pixel (MD5), for both titles.
3. [x] A screenshot of the ScummVM window shows the room.
4. [x] A malformed cel is rejected with a warning, not a crash.
5. [x] Scooby-only build: 0 errors and 0 warnings in `engines/scooby/`.
   The fork diff stays inside `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §5](../02-SCUMMVM-INTEGRATION.md#5-graphics-output)
  implementation notes.
