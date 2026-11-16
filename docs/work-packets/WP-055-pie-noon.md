---
layout: default
title: "WP-055: Showdown's Pie Noon"
---

# WP-055: Showdown's Pie Noon: pies until the clock chimes, a snack a ghost hit (Gen 1)

**Status:** 🚧 In progress (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-054 ✅ (the tree walk with sprite updates), WP-051 ✅ (the saloon), WP-021 ✅ (sprites and their hit tests), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-055-2026-11-16](../reference/pre-flight-WP-055-2026-11-16.md)

---

## Result (2026-11-16)

Pending: the check against the reference, the live run and the regression.

---

## Goal

Make Showdown's Pie Noon, ROOM_P32_Pie_Noon, play as the original does. The
saloon builds it once Artie is free. Until now it had the base class:
- nobody moved and nothing was thrown;
- the clock never ran;
- the room never sent the gang back to the saloon.

## Background

Pie Noon ([scooby-exe](../formats/scooby-exe.md#pie-noon-wp-055)):
- **Scooby** walks along the front of the stage after the mouse and throws
  a pie at each press.
- **The ghost** walks along the back, throws pies back, and hides in smoke.
  A pie that reaches it is a snack.
- **The rest of the gang** run across three lanes in between, and pies splat
  on them.
- **When the clock chimes,** back to the saloon.

The pies fly in a perspective the room works out from its placements: four
edges from the ghost's row to Scooby's. Scooby, the ghost and the runners
update themselves in the tree walk; the room's tick moves the pies.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`PieNoonRoom`:**
  - the placements and the stage;
  - Scooby, the ghost, the runners and the pies;
  - the clock and the way back to the saloon;
  - the snack counter.
- **Sound:** a handle per sound effect, as the original's buffer per clip.
- **The tree:**
  - the walk as the original's list;
  - the sweep after it, which deletes sprites marked done;
  - a step past a sequence's last.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - the stage: its places, slopes, lanes and edges;
   - every sprite on entry, and the clock by level;
   - the ghost's states;
   - two runners across their lanes;
   - a pie on the ghost, two on runners and one on Scooby, each with its
     flight, ticks, sounds and what follows;
   - Scooby after the mouse, and his throws;
   - the ghost's throw;
   - the clock to the chime and the saloon.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile starting in Pie Noon: Scooby walks
   and throws, and the clock's chime leads back to the saloon.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#pie-noon-wp-055): Pie Noon, the
  tree's sweep, and a step past a sequence's last.
