---
layout: default
title: "WP-017: Sprite Animation at the Original Tick Rate"
---

# WP-017: Sprite animation at the original tick rate (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (graphics; leads into Phase 4 room logic)
**Depends on:** WP-016 ✅ (rooms with placed sprites), WP-001 ✅ (sprite player traced)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-017-2026-11-14](../reference/pre-flight-WP-017-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Tick 0 and tick 37 match | ✅ At `graphics` level 3 the engine loads each room, hashes it, runs 37 ticks and hashes it again. A reference model logs the same hashes; it uses the probe's tree, the WP-016 blend model, and each placement at step `floor(T / 3) mod n`. The logs are identical: 69 Showdown rooms (55 of which change by tick 37) and 53 Phantom rooms (34 change). Draw orders still match too. |
| 2. 36 ticks per second | ✅ A live run of the Saloon logged 36, 72 … 360 ticks at 1,000 … 10,000 ms, and 432 at 12,002 ms. That is exact, because the engine counts ticks from `getMillis()` with the original's integer formula. |
| 3. Captures differ | ✅ Two window captures 0.25 s apart differ: Scooby's tail, the chandelier candles and the steam over the pie. Both were sent to Jeff and are not in git. |
| 4. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Fork commit [`7fd40d5da6`](https://github.com/barefootbetters/scummvm/commit/7fd40d5da6) stages its four files by name, inside `engines/scooby/`, and is pushed. |

**Notes:**

- **Some props loop that shouldn't.** Every placement starts in mode 1, because that's the default placement path. In the Saloon the root-beer sign and the piano bench cycle through what look like one-shot puzzle animations. In the game, the room's own code would hold or trigger those. That is the same per-room override WP-016 left out, and it belongs to Phase 4.
  - *Corrected by [WP-018](WP-018-hotspots-and-exits.md) (2026-11-14).* Not every placement starts in mode 1: clickables start stopped and `OBJ_GHOST` starts hidden. The root-beer sign and piano bench are clickables, so the correct default already holds them; per-room code was not the cause.
- **The tick trace.**
  - `0x430890` is slot `+8` of the sprite vtables (18 of them).
  - Its only driver is the tree walk `0x431130`, called once per tick from `0x435BC0`.
  - `0x431110`, which the main loop also calls, is an empty recursion, likely compiled-out code.
- **Cost.** Redraws repaint the room from cached cels only when a step changes, at most 12 times a second for the default placements.

---

## Goal

Make the rooms move. Each placed sprite plays its sequence the way
`Scooby.exe` does, at the original game-tick rate, and the screen redraws
when a step changes.

## Background

From WP-001's decompile, read again for this WP:

- **Tick rate (`0x435BC0`).** The game loop counts ticks as
  `elapsed_ms × 36 / 1000` since a base time and runs every tick it is
  behind. A tick:
  - walks the sprite tree front to back, calling each sprite's tick
    (`0x431130`, skipped for paused subtrees);
  - runs the room's update;
  - draws once.

  The constant is 36 (`0x24`), so there are **36 ticks per second**.
  Phantom's code is byte-identical (`0x4368F0`).
- **Player (`0x430890`, `0x430AA0`).** A sprite holds a mode, a ticks-per-step
  value, a countdown and a step. Each tick decrements the countdown. When it
  reaches 0 the countdown is reset and the step moves:

  | Mode | Each step |
  |---|---|
  | 1 | step + 1; past the end, back to 0 |
  | 2 | step − 1; below 0, to the last step |
  | 3 | step + 1; at the end, hold the last step and stop (mode 0) |
  | 4 | step − 1; at 0, stop |
  | 5 | (at start) jump to the last step and stop |

  Start sets the countdown to the ticks per step. A start step of −1 means
  step 0 for modes 1 and 3 and the last step for modes 2 and 4; a start step
  past the end becomes the last step.
- **Default placement.** The default placement path starts every placed
  sprite in mode 1 at 3 ticks per step from step 0
  ([tgifile-art §Sequences](../formats/tgifile-art.md#sequences-table-0)).
  That is 12 steps per second, and after `T` ticks a sprite shows step
  `floor(T / 3) mod n`.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`Room`.** The sprite tree built once on room entry, from WP-016's rules,
  holding each placed sprite's player state (modes 1–5). Then it draws the
  current steps.
- **Cel cache.** Each `(block, cel)` is decoded once per room, so a frame
  redraw doesn't decode again.
- **Engine loop.** Count ticks at 36 per second from `getMillis()` with the
  original's integer formula, run the owed ticks, and redraw when any sprite
  changed step.
- **Checks.**
  - `graphics` level 3: every room is checked at tick 0 and after a fixed
    number of ticks. Each check logs the draw order and a surface MD5.
  - `graphics` level 1: once a second, log the tick count since the room
    started.

**Out of scope:**

- Room scripts that start other sequences or modes, hotspots and input
  (Phase 4).
- Scrolling, and sound tied to animation.

## Exit criteria

1. [x] After 0 and after 37 ticks (step 12 mod `n`), every room in Showdown
   and Phantom matches a reference model (MD5), which uses the probe's tree
   and blend model with each sprite at step `floor(T / 3) mod n`.
2. [x] The engine's tick counter advances 36 ticks per second of wall time,
   within ±1 over 10 s.
3. [x] Two window captures a fraction of a second apart show the same room
   at different steps.
4. [x] Scooby-only build: 0 errors and 0 warnings in `engines/scooby/`. The
   fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md) and
  [tgifile-art](../formats/tgifile-art.md) notes on the tick rate and start
  step.
