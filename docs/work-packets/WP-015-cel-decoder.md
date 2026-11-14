---
layout: default
title: "WP-015: Cel Decoder and Room Background"
---

# WP-015: Cel decoder, and a room background on screen (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3 (resource loading; first graphics)
**Depends on:** WP-014 ✅ (`ArtArchive`), WP-001 ✅ (decode path traced), WP-002 ✅ (cel format)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-015-2026-11-14](../reference/pre-flight-WP-015-2026-11-14.md)

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

1. [ ] Every cel in Showdown and in Phantom decodes in the engine to the
   same pixels and coverage as `probe_art.py`. Checked by MD5 per cel,
   9,111 cels in Showdown.
2. [ ] The screen after drawing room 0 matches the background decoded by
   `probe_art.py`, pixel for pixel (MD5), for both titles.
3. [ ] A screenshot of the ScummVM window shows the room.
4. [ ] A malformed cel is rejected with a warning, not a crash.
5. [ ] Scooby-only build: 0 errors and 0 warnings in `engines/scooby/`.
   The fork diff stays inside `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §5](../02-SCUMMVM-INTEGRATION.md#5-graphics-output)
  implementation notes.
