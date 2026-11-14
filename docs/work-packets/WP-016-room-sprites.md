---
layout: default
title: "WP-016: Room Sprites and Translucent Blending"
---

# WP-016: A whole room on screen: placed sprites, draw order and translucent blending (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3 (resource loading; graphics)
**Depends on:** WP-015 ✅ (cel decoder), WP-001 ✅ (draw order and blitters traced), WP-008 ✅ (`object.ini`)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-016-2026-11-14](../reference/pre-flight-WP-016-2026-11-14.md)

---

## Goal

Draw a room in the ScummVM fork the way `Scooby.exe` sets it up on entry:
the background layers plus every placed object at step 0 of its sequence.
Use the traced sprite-tree draw order, and blend translucent (mask B) pixels
exactly as the original 565 blitter does.

## Background

- [tgifile-art §Rendering a room](../formats/tgifile-art.md#rendering-a-room-2026-11-13)
  traces the sprite tree and placement rules (`0x435DC0`, `0x430F40`,
  `0x431000`, `0x4091FF` …).
  - **Layers.** One sprite per used layer slot, at depth
    `-110000 + 10000 × slot`, under a root at `-0x7FFFFFFF`.
  - **Placements.** Each attaches by its `object.ini` kind. Characters go
    under layer 0 at depth `y − 200`. Inventory, requires and exit objects
    go under layer 0 at −100, 0 and −1000. Clickables go under layer
    `layer=` at depth `priority=`. Everything else goes under layer 1, or
    the root when that slot is empty, at depth 0.
  - **Order.** Children are sorted by descending depth, and a new child goes
    after every child of equal or higher depth. Drawing emits children with
    depth ≥ the parent's, then the parent, then the rest, which gives a
    front-to-back list.
- **Drawing.** The engine draws front to back with occlusion: opaque pixels
  first, translucent regions queued and blended back to front. For a single
  layer of sprites that gives the same pixels as painting back to front, an
  opaque copy for mask A and a blend for mask B.
- **The blend** (`0x439170`, decompiled for this WP) works per channel:

  ```
  a   = T4[src >> 12]
  out = (Tdst[dst channel] × (255 − a) + 0x80 + T4[src nibble] × a) >> 8
  ```

  The result is packed back to RGB565 (`>> 3` for red and blue, `>> 2` for
  green). The 4-, 5- and 6-bit expansion tables are static data at
  `0x4708DC`, `0x47075C` and `0x4707DC`. Phantom's are byte-identical.
  - `T4[i] = 17 × i`.
  - `T5[i] = round(255 × i / 31)` and `T6[i] = round(255 × i / 63)`.
    `probe_art.py`'s `rgb()` floors instead. Its RGBA renders are a visual
    reference, not an exact model of the 565 screen.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`object.ini`.** Read it through `Common::INIFile` (section and key names
  ignore case; the first match wins, as with `GetPrivateProfileString`).
  Only the kind, `layer=` and `priority=` are used for now, with the
  original's integer rule (`0x40AD50`).
- **Object resources.** Sequence (table 0) and frame (table 1) lookup:
  step 0 of a placement's ANIM sequence.
- **Room renderer.**
  - Builds the sprite tree with the traced rules and paints it into a
    room-sized RGB565 surface.
  - The blend uses the original's tables, computed from their closed form.
  - The screen shows the left 640 columns.
- **Checks.**
  - `graphics` level 2 logs a room's front-to-back draw order.
  - `graphics` level 3 renders every room offscreen and logs its draw order
    and an MD5 of the room surface.
- **Start room.** An optional `start_room` key in the game's ScummVM config
  domain picks the start room, for screenshots and testing. The console's
  `room` command still switches rooms.

**Out of scope:**

- Per-room code that claims an object by name (the Post Office trapdoor and
  the like).
- Animation (only step 0), scrolling, and input.
- RGB555 screens.

## Exit criteria

1. [ ] For every room in Showdown and Phantom, the engine's draw order
   matches `probe_art.py`'s traced order (`render_room`).
2. [ ] For every room in both titles, the room surface matches an exact
   565 model built on the probe's tree code and the dumped tables, by MD5.
   This includes the translucent pixels.
3. [ ] Screenshots of Town Center and Saloon in the ScummVM window match the
   probe's `--room` renders by eye.
4. [ ] Scooby-only build: 0 errors and 0 warnings in `engines/scooby/`.
   The fork diff stays inside `engines/scooby/`, and only named files are
   staged in the shared checkout.

## Deliverables

- Fork commit on `scooby-engine`.
- [tgifile-art](../formats/tgifile-art.md) §Cel format: the blend tables.
- Integration §5 note.
