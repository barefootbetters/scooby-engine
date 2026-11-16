---
layout: default
title: "WP-046: Showdown's Sheriff's office"
---

# WP-046: Showdown's Sheriff's office: the cell door, the oil can and the snacks (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-044 ✅ (the jail), WP-024 ✅ (snacks), WP-023 ✅ (inventory and requires objects), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-046-2026-11-15](../reference/pre-flight-WP-046-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
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
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the stuck door;
   - the oil can opening it;
   - the snack gate, two snacks, and the way into the jail.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-sheriffs-office-wp-046): the
  Sheriff's office.
