---
layout: default
title: "WP-018: Placement Kinds, Hotspots, Cursor and Exits"
---

# WP-018: Placement kinds, hotspots, the cursor and exits (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3–4 (first interaction)
**Depends on:** WP-017 ✅ (animation), WP-016 ✅ (room build), WP-001 ✅ (placement and input code labelled)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** One day
**Pre-flight:** [pre-flight-WP-018-2026-11-14](../reference/pre-flight-WP-018-2026-11-14.md)

---

## Goal

Make rooms respond to the mouse as `Scooby.exe` does:

- Hover over an object finds the same object the original would.
- An exit shows its rollover cursor.
- Clicking an exit goes to its destination room.

Getting this right also corrects how each kind of placement starts. WP-016
and WP-017 assumed every placement is visible and loops.

## Background

Read for this WP from WP-001's decompile, plus vtable-only functions
decompiled headless:

- **Placement constructors** (`0x4091FF`, `0x408F90`, `0x401850`, `0x402D90`,
  `0x4026B0`, `0x401000`, `0x4048E0`).

  | Kind | Start mode | Hidden | Hit test |
  |---|---|---|---|
  | `exitobject`, `requiresobject`, `inventoryobject` | 1 (loop) | no | step polygon (type 2) |
  | `clickableobject` | **0 (stopped at step 0)** | no | step polygon (type 2) |
  | simple sprite (no or unknown `ID=`) | 1 | no | step polygon (type 2) |
  | character (`OBJ_<NAME>[_x]`) | 1 | no | cel pixels and masks (type 1) |
  | `OBJ_GHOST` | **0** | **yes** (`0x4313F0` sets `+0x14`) | — |

  The clickable constructor also checks a saved "Clickables" state, which is
  empty on a fresh game. Layer sprites are the base sprite class, hit type 1.
- **Hit walk (`0x4311F0`, vtable `+0x14`).** It goes front to back in the
  draw order, skips hidden sprites, and the first hit wins.
  - **Type 2 (`0x430D10` → `0x431350` → `0x4312A0`).** Take the polygon of
    the current step, `(px − x, py − y)` relative to the sprite. Test the
    polygon's box with strict bounds on both sides. Then do an even-odd
    crossing test with C integer division.
  - **Type 1 (`0x431400`).** For each cel of the current frame, inside
    `[x, x + w) × [y, y + h)`: hit if the cel isn't solid and its pixel is
    non-zero, or if mask B or mask A covers the point.
- **Rollover (vtable `+0x18`).**
  - Exits (`0x402410`): `rolloveranim=` while the default cursor is up.
    (Scrappy's hint mode, which shows `ANIM_CURSORSCRAPPY_ANIM`, is out of
    scope.)
  - Clickables (`0x4015F0`): `ANIM_CURSOROPEN`.
  - Others (`0x408450`): none.
  - The cursor is an `OBJ_CURSOR` sprite, `ANIM_CURSORARROW` by default
    (`0x4089E0`).
- **Exit click (`0x402130`).** Logs to the `Exits` channel and starts the
  transition to `destinationroom=`. The transition walks characters and
  plays movies (`0x404820`).

## Scope

**In scope (fork, `engines/scooby/` only):**

- Per-kind start mode, hidden flag and hit type, as in the table.
- `Room::hitTest()` with both test types, exactly as traced.
- **Cursor.** An `OBJ_CURSOR` sprite drawn at the mouse:
  - `ANIM_CURSORARROW` by default;
  - the hovered object's rollover when it has one (exit: `rolloveranim=`;
    clickable: `ANIM_CURSOROPEN`).
- **Exit clicks.** Go straight to `destinationroom=`.
- **Checks.** `input` level 3: a grid hit test of every room at tick 0. It
  logs an MD5 of the hit labels and how many points each sprite owns.

**This repo:**

- Correct tgifile-art §Rendering a room ("mode 1 for every placement") and
  §Sequences.
- Make `probe_art.py --room` hide `OBJ_GHOST`.

**Out of scope:**

- The exit transition (character walk, movie).
- Hint mode, inventory and requires interactions.
- Per-room code, and the saved "Clickables" state.

## Exit criteria

1. [ ] Every room in Showdown and Phantom, at tick 0 and tick 37, matches the
   reference model with the corrected kinds (ghost hidden, clickables
   stopped). Checked by MD5.
2. [ ] For every room in both titles, a 4-pixel grid hit test at tick 0
   matches a reference that implements `0x4312A0`/`0x431350`/`0x431400`
   independently in Python. Checked by MD5 of the hit labels.
3. [ ] Live: hovering an exit shows its rollover cursor (capture), and
   clicking it loads `destinationroom=` (log).
4. [ ] Scooby-only build: 0 errors and 0 warnings. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [tgifile-art](../formats/tgifile-art.md) corrections and the hit-test spec.
  [scooby-exe](../formats/scooby-exe.md) rows for the hit walk and rollovers.
- The `probe_art.py` ghost fix.
