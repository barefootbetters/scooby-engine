---
layout: default
title: "WP-046: Showdown's Sheriff's office"
---

# WP-046: Showdown's Sheriff's office: the cell door, the oil can and the snacks (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-044 ✅ (the jail), WP-024 ✅ (snacks), WP-023 ✅ (inventory and requires objects), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-046-2026-11-15](../reference/pre-flight-WP-046-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp047_ref.py`: the hotel fix's, plus the office, written from the trace before the engine ran. It reads the placements, step counts, clickable states and `priority=` keys from the art and object.ini, and which scenes and sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 145 lines on Showdown: the earlier 139 and 6 for the office. The reference prints the same 145, none different, on the first run. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The placements.** The door is a requires object at depth 1, on its closed state. The way into the jail is an exit at depth -1000. Hotspots 1 and 4 are clickables at depth -1. With `MoaningActive` (a new game's) the opening is `140A_`, unplayed; without it there is none. With the oil can used the door is open. Once the blanket has been taken too, it shows the bed gone, and the way into the jail isn't built.<br>**The hotspots.** Hotspot 1 gives `140X_` on its B and `140X3_` on its E, held, and nothing on C, D, F and A. Hotspot 4 gives `HOTSPOT4A_` and `HOTSPOT4A2_`. On its C, Shaggy starts his sandwich on tick 52, when the C stops (11 steps, with `Global.Idle.SHAGGY_S1_E`, input held), and input is free on tick 85.<br>**The stuck door.** Four times: input is held, and on tick 1 Shaggy shakes the bars (91 steps, `Shaggy.Shakes.Bars`). On tick 274 comes `150A1_`, `150A12_`, `150A13_`, then `150A1_` again, not held, and input is free.<br>**The oil can.** It is used up and the arrow is back, with input held. On tick 1 Shaggy oils the door (134 steps, `Shaggy.Oils.Door`) and the door is hidden. On tick 403 it shows open and input is free. Back again, it is open.<br>**The way into the jail.** At each level the gang is kept with `150A_`, `150A2_` or `150A3_`, held, and the toolbar opens for the flash. The way to Street 1 isn't kept. At level 1 the gang is kept after 0, 1 and 2 snacks, and goes through after 3. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**The stuck door.** Shaggy shook the bars, and `150A1_` followed, not held.<br>**The oil can.** Used on the door, Shaggy oiled it, and it was open on tick 586.<br>**The jail.** With the door open, the way in gave `150A_` and the snack box flashed. Fed two snacks from the toolbar, Scooby took them. The way in then walked the gang off through movie 29 (360 frames) into the jail. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. Phantom's earlier checks are identical to the hotel fix's run. Showdown's differ only by the profile check's sheriff clue, which is drawn at random on every run. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`9918eae5d3`](https://github.com/barefootbetters/scummvm/commit/9918eae5d3) (5 files staged by name) is pushed. |

**Deviations and gaps:**

- **Clicks act on the press,** like every click in the fork.
- **Input after the stuck door's line.** The original sets game `+0x24` while Shaggy is at the door. After the bars it doesn't clear it, as it does after the oil can, and the line that follows doesn't hold input. The fork's hold is the class's own and ends with the door's turn either way. Whether something outside the class clears `+0x24` after the bars wasn't traced.

---

## Goal

Make Showdown's Sheriff's office play as the original does. It is the
first of the rooms the [room class audit](../reference/room-class-audit-2026-11-15.md)
found still on the base class. Until now:
- the cell door didn't stick;
- the oil can did nothing;
- the way into the jail didn't wait for the snacks.

## Background

The office ([scooby-exe](../formats/scooby-exe.md#the-sheriffs-office-wp-046)):
- **The cell door:** it sticks. Clicked, Shaggy shakes the bars and the
  gang has a line. The oil can opens it, and once the blanket has been
  taken from the cell it shows the bed gone.
- **The way into the jail:** the gang won't go in until they've had the
  level's snacks here, level + 2.
- **The hotspots:** two give lines, and one has Shaggy eat a sandwich.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SheriffsOfficeRoom`:** the door and the oil can; the snacks before
  the jail; the hotspots' lines and the sandwich; the opening while
  `MoaningActive`.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **Street 1 and the jail,** the rooms on either side.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the class;
   - the placements, and the opening with and without `MoaningActive`;
   - the door with the oil can used, and with the blanket taken;
   - hotspot 1's lines on its B and E, hotspot 4's on A and B, and the
     sandwich after its C, with their ticks;
   - the stuck door four times, with its lines in turn;
   - the oil can on the door, Shaggy, and the door open, with their ticks;
   - the way into the jail by level, the flash, and the snacks that let
     the gang through.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the stuck door;
   - the oil can opening it;
   - the snack gate, two snacks, and the way into the jail.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-sheriffs-office-wp-046): the
  Sheriff's office.
