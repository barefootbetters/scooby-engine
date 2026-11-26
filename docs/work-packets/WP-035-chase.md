---
layout: default
title: "WP-035: Showdown's chase"
---

# WP-035: Showdown's chase: the branches and the canned run-offs (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic)
**Depends on:** WP-020 ✅ (exits), WP-022 ✅ (movies), WP-023 ✅ (requires objects), WP-025 ✅ (toolbar-hiding rooms), WP-029 ✅ (room classes and openings)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-035-2026-11-14](../reference/pre-flight-WP-035-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp035_ref.py`, written from the trace before the engine ran. It reads the rooms' placements, the sequences' step counts and `object.ini`'s exits from the disc, and never runs the engine. At `script` level 3 the engine drives each chase room through `showRoom`, its exits and its ticks and logs 44 lines on Showdown; the reference prints the same 44, none different. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **The classes.** B for P24 to P29, C for P33 to P39, none for the close-up and P40.
   - **The openings.** Over 40 visits each: P26 always `Chase_Branch_3.230_`; P24, P27 and from the corral none; P25, P28 and P29, and P25 from the close-up, all four of `230_`, `230B2_`, `230C_`, `230D_`. None is ever marked played.
   - **The placements.** Each OBJ_BRANCH at depth 0, looping, or already running off in B1 and B4; the oil can as a requires object in B6. The close-up's overlay only while ICDouble has given his clue and the combination isn't held, at depth −1; ICDouble never hit.
   - **The run-offs.** All seven exits, B1's and B4's on entry, the four countdowns and both returns: the run-off and its sound, input held, and the next room on tick 3 × its steps (B5 to the corral 96, through movie 8), or 722 + 3 × its steps by the countdown (B2 833, B3 905, B5 857, B6 815). A second click while one runs changes nothing.
   - **The oil can.** ANIM_BRANCH6C; in the toolbar on tick 66, its sprite hidden; C5 on tick 96. Once held, it isn't built, and B6's exit to C5 plays 6A.
   - **Chase C.** Each `Chase.Canned_<n>`, the canned sprite at depth −1 playing once, input held; over on tick 3 × its steps, the room changing a tick later: C1 to B3, C2 to B1, C3 to B5, C4 to B6, C5 and C6 to P40 through movie 31.
2. **Live, Showdown:** ✅ Through `test_script`, minimized:
   - **The chain, no input.** C1's run-off ended on tick 225 and B3 loaded; its opening played; the countdown ran out on tick 722 and 3A took the gang to C2. Then C2 led to B1, whose 1A started on entry, then C4, then B6. B6's countdown sent the gang on with 6A to C5, and movie 31 played before P40 loaded.
   - **The oil can.** Clicked in B6 after the opening: 6C started, the oil can reached the toolbar, then C5.
   - **The corral.** B5's exit: 5A, then movie 8, then the corral.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **Chase C's exit is taken once.** The original calls the default exit handler on every tick until the room changes; the fork calls it once, which ends the same way.
- **A live click before a branch's opening ends is ignored,** as the base room holds input for the opening; that is the original's behaviour, not a gap.
- **The close-up, P25A,** is next (WP-036): the run-offs into it and back are here.

---

## Goal

Make Showdown's chase play as the original does. Until now every chase room
had the base class: the branches' exits walked the gang off like any room's,
nothing ran on by itself, and the canned run-offs never ended.

## Background

The chase starts at ROOM_P40_Chase_Start and runs through two kinds of room
([scooby-exe](../formats/scooby-exe.md#the-chase-wp-035)):
- **The branches, Chase B** (P24 to P29): a fork in the path. Clicking an
  exit, or waiting out the room's countdown, plays the branch's run-off,
  and the next room loads when it has played out. B1 and B4 have no choice.
  In B6 the oil can can be taken on the way.
- **The run-offs, Chase C** (P33 to P39): a canned animation with its
  sound, no input, then the next branch. C5 and C6 lead back to the start
  through a movie.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`ChaseBRoom`:** the placements it claims; its openings; its entry,
  run-offs, countdown and the oil can; the room change, through movie 8 to
  the corral.
- **`ChaseCRoom`:** the canned sprite, its sound, held input, and the exit,
  through movie 31 back to the start.
- **The factory lines,** a `RoomHooks::arrive(from)` hook (room vtable
  +0x2C), and an optional movie on `ScoobyEngine::exitTo`.
- **A `script` level 3 check** against an independent reference.

**Out of scope:**

- **The close-up, P25A** (ICDouble's scene). It gives his clue, which needs
  the other session's clue API. The run-offs into it and back are in.
- **The corral, P30** (the horseshoe game). Only the way in and back is in.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the factory's classes;
   - each branch's openings, over 40 visits;
   - the placements the class claims, and the close-up's overlay by the
     story's state;
   - every exit's run-off, B1's and B4's on entry, the countdown's, and the
     two returns, with the ticks to the next room and its movie;
   - the oil can's run-off, the tick it reaches the toolbar, and B6 once
     it is held;
   - each canned run-off, the tick it ends and the room after.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown:
   - the chain from C1 with no input: C1, B3's countdown, C2, B1, C4, B6's
     countdown, C5 and its movie;
   - the oil can taken in B6;
   - B5's exit to the corral and its movie.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-chase-wp-035): the chase.
