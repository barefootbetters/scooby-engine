---
layout: default
title: "WP-047: Showdown's back alley"
---

# WP-047: Showdown's back alley: the snacks before the General Store (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-045 ✅ (the General Store), WP-038 ✅ (the bank vault), WP-024 ✅ (snacks), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Two hours
**Pre-flight:** [pre-flight-WP-047-2026-11-15](../reference/pre-flight-WP-047-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp048_ref.py`: WP-046's, plus the alley, written from the trace before the engine ran. It reads the placements, step counts, clickable states and `priority=` keys from the art and object.ini, and which scenes and sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 149 lines on Showdown: the earlier 145 and 4 for the alley. The reference prints the same 149, none different, on the first run. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**Entry.** From the store Fred walks in UL, and from the vault and the open safe Shaggy walks in UR. `Back_Alley.Snakes_Distant` plays. Hotspot 3 is a clickable at depth -1, hotspot 1 one at depth 1, its `priority=`. The opening is `350A_`, unplayed.<br>**The hotspots.** Hotspot 3's A has no line and moves to B. Its B gives one of its two lines on the tick it starts, not held. Hotspot 1 scares Daphne and Scooby on tick 25, its step 8.<br>**The way into the store.** At each level the gang is kept with `350B_`, `350B2_` or `350B3_`, held, and the toolbar opens for the flash. The way to the vault isn't kept. At level 1 the gang is kept after 0, 1 and 2 snacks, and goes through after 3. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from a profile in the original's form:<br>**The hotspots.** Hotspot 3's A played its 51 steps without a line. Its B gave `HOTSPOT3B2_` on the tick it started. Hotspot 1 played, and Daphne and Scooby said their frights (`Global.Scared.DAPHNE`, `Global.Scared.SCOOBY`).<br>**The store.** The way in gave `350B_` and the snack box flashed. After two snacks fed to Scooby, the gang walked into the General Store. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The earlier checks are identical to WP-046's run on both titles. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`4403e0b7e9`](https://github.com/barefootbetters/scummvm/commit/4403e0b7e9) (5 files staged by name) is pushed. |

**Deviations and gaps:**

- **Clicks act on the press,** like every click in the fork.

---

## Goal

Make Showdown's back alley play as the original does. It is the second
room from the [room class audit](../reference/room-class-audit-2026-11-15.md).
Until now:
- the gang went into the General Store without the snacks;
- the alley's hotspots had no lines or frights;
- no one walked in.

## Background

The back alley ([scooby-exe](../formats/scooby-exe.md#the-back-alley-wp-047))
lies between the bank vault and the General Store:
- **On entry:** rattlesnakes are heard in the distance.
- **The way into the store:** the gang won't go in until they've had
  level + 2 snacks here, as in the Sheriff's office.
- **The hotspots:** hotspot 3 has two lines, at random, and hotspot 1
  scares Daphne and Scooby.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BackAlleyRoom`:** the snacks before the store; the walk-ins; the
  snakes' sound; hotspot 3's lines and hotspot 1's fright.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the class;
   - the walk-ins from the store, the vault and the open safe; the
     snakes' sound; the hotspots; the opening;
   - hotspot 3's A without a line and its B with one, and hotspot 1's
     fright on its step 8, with their ticks;
   - the way into the store by level, the flash, and the snacks that let
     the gang through.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile in the original's form: hotspot
   3's line, hotspot 1's fright, the snack gate, two snacks, and the way
   into the store.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-back-alley-wp-047): the back
  alley.
