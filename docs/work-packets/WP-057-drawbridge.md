---
layout: default
title: "WP-057: Phantom's drawbridge and town"
---

# WP-057: Phantom's drawbridge and town: four flags to the banners (Gen 1)

**Status:** 🚧 In progress (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-029 ✅ (room setup), WP-026 ✅ (the profile), WP-024 ✅ (the snack box), WP-021 ✅ (clickables), WP-056 ✅ (the check's place)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-057-2026-11-16](../reference/pre-flight-WP-057-2026-11-16.md)

---

## Result (2026-11-16)

Pending: the check against the reference, the live run and the regression.

---

## Goal

Port Phantom's first two rooms, the first of the 38 game classes in
[Phantom's audit](../reference/room-class-audit-phantom-2026-11-16.md):
- **ROOM_P01_Drawbridge,** where a new game starts. Until now it had the
  base class: the flags didn't move, and its way to the town was there from
  the start.
- **ROOM_P04_Town,** the hub. Until now nobody walked in and Jane never
  screamed.

## Background

The drawbridge ([scooby-exe](../formats/scooby-exe.md#phantoms-drawbridge-and-town-wp-057))
is a puzzle: four flags must wave their banners' colours. Each click on a
flag lowers its pennant and raises the next colour. With all four right, a
fanfare plays, the drawbridge comes down, and the way to the town opens.

Phantom's `Scooby.exe` is mostly Showdown's code at other addresses. A
function-by-function match between the two maps Phantom's helpers to the
ones already traced.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`DrawbridgeRoom`:** the colours, the flags and banners, the puzzle, the
  fanfares, the drawbridge, the way out, the sign and the profile keys.
- **`TownRoom`:** the walk-ins and Jane's screams.
- **A Phantom new game's story values** (`0x42E880`), which the town reads.
- **`Room`:** an exit built after loading, and `startAnim` at a given tick
  rate.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the classes;
   - a new game's story values;
   - the drawbridge's reset;
   - its entry: each flag, banner, the door, the overlay and the way out,
     the snacks needed, Velma's walk-in and the sounds;
   - a flag's click, its moves with their ticks, and a click during one;
   - Velma's line when a flag leaves its banner's colour;
   - the puzzle done: the way out, the fanfares, the drawbridge down;
   - the way out before and after a snack;
   - the profile keys, and a visit with the puzzle done;
   - the sign's lines;
   - the town's walk-ins and screams.

   Showdown prints that it has no drawbridge, as its reference does.
2. [ ] Live, in Phantom: the puzzle solved with a click, the drawbridge
   down; then through it to the town, with a walk-in and a scream.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile keys and story
   values. The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-drawbridge-and-town-wp-057):
  the drawbridge, the town, a Phantom new game's story values, and the
  functions matched between the titles.
