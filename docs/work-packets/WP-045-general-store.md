---
layout: default
title: "WP-045: Showdown's General Store"
---

# WP-045: Showdown's General Store: the clock, the snake and the lantern (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-044 ✅ (the blanket), WP-043 ✅ (the hammer), WP-023 ✅ (inventory and requires objects), WP-022 ✅ (movies)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-045-2026-11-15](../reference/pre-flight-WP-045-2026-11-15.md)

---

## Goal

Make Showdown's two General Store rooms play as the original does. Until
now they had the base class:
- the hammer did nothing to the clock;
- the snake never struck or took the blanket;
- the lantern couldn't be had.

## Background

The store ([scooby-exe](../formats/scooby-exe.md#the-general-store-wp-045))
has two rooms:
- **The front:** the clock over the door has lines of its own. The rusty
  hammer from the stage breaks it; after movie 2 its broken face is in the
  toolbar, which the bank's vault door takes.
- **Inside:** a nest of rattlesnakes lies in front of the lantern. Clicked,
  they get a line and strike. The blanket from the jail goes over them,
  Fred tosses it, and then he can take the lantern.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`StoreFrontRoom`:** the clock and the hammer, through movie 2; the
  door's, the sign's and the clock's lines; hotspot 1 scaring Scooby; the
  opening while `MoaningActive`.
- **`GeneralStoreRoom`:** the snake, its lines and strikes; the blanket
  over it; the lantern; the hotspots' lines.
- **A file's volume** (`0x434B60`) and **a clip's position** (`0x434BA0`)
  in `Sound`, which the two classes use.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **Street 2 and the back alley,** the ways in.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the classes;
   - the front's placements, its opening with and without `MoaningActive`,
     and Fred's walk-in; with the hammer used, the broken clock;
   - the clock's lines in turn, the door's, the sign's, and Scooby scared;
   - the hammer on the clock: its scene, the hammer used up, movie 2 back
     to the front, the broken clock;
   - inside, the placements, the snake's idle and its sound, Shaggy's
     walk-in and the hotspots' lines; with the lantern taken, and with the
     blanket used;
   - the snake's lines in turn, its strike and its idle again, with their
     ticks;
   - the blanket over the snake: its scene, Fred, the file at 93%, with
     their ticks;
   - the lantern: Fred, the toolbar on his step 62, the scene, with their
     ticks; and taken when leaving.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the front: the clock's and the door's lines, Scooby scared, and the
     hammer through movie 2 to the broken clock;
   - inside: the snake striking, the blanket over it, and Fred taking the
     lantern.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-general-store-wp-045): the
  General Store.
