---
layout: default
title: "WP-044: Showdown's jail"
---

# WP-044: Showdown's jail: the blanket, the bed and the hole under it (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-041 ✅ (the dark tunnel), WP-023 ✅ (inventory and requires objects), WP-021 ✅ (clickables), WP-020 ✅ (scenes)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-044-2026-11-15](../reference/pre-flight-WP-044-2026-11-15.md)

---

## Goal

Make Showdown's jail cell play as the original does. Until now it had the
base class: the blanket couldn't be taken, the bed never broke, and the
gang had no way out of the cell.

## Background

The jail ([scooby-exe](../formats/scooby-exe.md#the-jail-wp-044)) locks
Shaggy and Scooby in a cell with no exit object:
- **The blanket:** clicked with the arrow, Shaggy takes it off the bunk
  and it goes in the toolbar.
- **The bed:** the first click gets a line; the second has Scooby break
  it, which uncovers a hole and a stool.
- **The hole:** after their scene, the two drop through it into the dark
  tunnel. Once they have, the jail leads straight back there.
- **The door and the window** have lines of their own.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`JailRoom`:** the blanket; the bed, the hole and the stool, saved as
  `BedBroken`; the drop into the dark tunnel; the door's and the
  window's lines; the room's leave and its exit handler.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The Sheriff's office,** ROOM_P02_Sheriffs_Office, the way in.
- **The dark tunnel,** done in WP-041.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - the placements, with and without the blanket taken;
   - the door's lines in turn, the window's on its B, the bed's first
     click;
   - the blanket: not with an item; with the arrow, Shaggy, the toolbar
     and 150C_, with their ticks;
   - the bed: Scooby, the sound, the hole and the stool, 150D_, with their
     ticks;
   - the drop: Shaggy's depths by the stool, Scooby gone, the room, and
     the jail again;
   - `BedBroken` saved and read, and a new game's reset;
   - what leaving finishes, and the exit handler.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the door and the window, the blanket, the bed twice, 150D_ and the
     dark tunnel;
   - a saved broken bed: the hole at once, 150D_ and the dark tunnel.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-jail-wp-044): the jail.
