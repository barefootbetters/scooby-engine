---
layout: default
title: "WP-045: Showdown's General Store"
---

# WP-045: Showdown's General Store: the clock, the snake and the lantern (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-044 ✅ (the blanket), WP-043 ✅ (the hammer), WP-023 ✅ (inventory and requires objects), WP-022 ✅ (movies)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-045-2026-11-15](../reference/pre-flight-WP-045-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp045_ref.py`: WP-044's, plus the store, written from the trace before the engine ran. It reads the placements, step counts and clickable states from the art and object.ini, and which scenes and sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 139 lines on Showdown: the earlier 131 and 8 for the store. The first run matched every value. Two lines differed only in wording: the reference left out the word "scene" before two scene names. With that fixed, all 139 match. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The front.** The clock is a requires object at depth 0. The faceless clock is under layer 1 at depth 1, hidden. With `MoaningActive` (a new game's) the opening is `110A_`, unplayed; without it there is none. Fred walks in DL from Street 2. With the hammer used, the broken clock is in the toolbar, the clock is hidden, and the faceless clock is shown.<br>**Its lines.** The clock gives `A_Clock_`, `A_Clockb_`, `A_Clockb3_`, then `A_Clock_` again. The door gives one of its two, and hotspot 3 gives `110X_`, all held. With no sound playing, hotspot 1 scares Scooby on tick 1.<br>**The clock and the hammer.** `Take_Clock_` plays, held. The hammer is used up and the arrow is back. While the scene plays, nothing happens. The tick after it ends, the gang goes to the front through movie 2, and is back with the broken clock.<br>**Inside.** The snake is a requires object on its idle, stopped, and the lantern a requires object. There is no opening, and Shaggy walks in DL from the back alley. On tick 1 the snake idles, with `Snake_Idle`. Hotspot 1 gives `120X_` every time, and hotspot 2 gives `120X2_`. With the lantern taken it isn't built. With the blanket used, the snake is under it at depth 500 and Sfx.dat is at 93%.<br>**The snake.** Its lines come in turn, each with a strike. It strikes on tick 2, its first step 0 (`SNAKEANIM`, 42 steps, `Snake_Attack`), and idles again on tick 128 with `Snake_Idle`. The lantern before the blanket gets a snake line and a strike.<br>**The blanket.** `Click_Blanket_On_Snake_` plays, held; the blanket is used up and the arrow is back. On tick 1 Fred tosses it (22 steps) with input held. On tick 67 the snake is covered at depth 500 with Sfx.dat at 93%, and input is free.<br>**The lantern.** On tick 1 Fred grabs it (99 steps) and the lantern is hidden. `Fred_Takes_Lantern` isn't on the disc. The lantern goes in the toolbar on tick 187, his step 62, and `Click_On_Lantern_` plays on tick 298, held. Left halfway, the lantern is still taken. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**The front.** The clock gave `A_Clock_` and the door `Door_Locked_`. Hotspot 1 was clicked on tick 523, and its sound played; Scooby was scared on tick 545, 0.6 seconds in. The hammer on the clock gave `Take_Clock_`. Movie 2 played (46 frames), and the gang was back at the front with the broken clock in the toolbar and the faceless clock on the wall.<br>**Inside.** The snake struck at its line, and again at the lantern's. The blanket on it gave `Click_Blanket_On_Snake_`, and Fred covered the snake on tick 922, with Sfx.dat at 93%. The lantern click had Fred take it into the toolbar, with `Click_On_Lantern_`. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Phantom's earlier checks are identical to WP-044's run. Showdown's differ only by the profile check's sheriff clue, which is drawn at random on every run. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`1925cee79c`](https://github.com/barefootbetters/scummvm/commit/1925cee79c) (7 files staged by name) is pushed. |

**Deviations and gaps:**

- **Clicks act on the press,** like every click in the fork.
- **Hotspot 1's half second** is the mixer's elapsed time, where the original divides the play cursor by the bytes per second. The live run waited 0.6 seconds, the first tick past 0.5.

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

1. [x] Showdown matches an independent reference line for line:
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
2. [x] Live, in Showdown, from profiles in the original's form:
   - the front: the clock's and the door's lines, Scooby scared, and the
     hammer through movie 2 to the broken clock;
   - inside: the snake striking, the blanket over it, and Fred taking the
     lantern.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-general-store-wp-045): the
  General Store.
