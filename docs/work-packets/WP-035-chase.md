---
layout: default
title: "WP-035: Showdown's chase"
---

# WP-035: Showdown's chase: the branches and the canned run-offs (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-020 ✅ (exits), WP-022 ✅ (movies), WP-023 ✅ (requires objects), WP-025 ✅ (toolbar-hiding rooms), WP-029 ✅ (room classes and openings)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-035-2026-11-14](../reference/pre-flight-WP-035-2026-11-14.md)

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

1. [ ] Showdown matches an independent reference line for line:
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
2. [ ] Live, in Showdown:
   - the chain from C1 with no input: C1, B3's countdown, C2, B1, C4, B6's
     countdown, C5 and its movie;
   - the oil can taken in B6;
   - B5's exit to the corral and its movie.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-chase-wp-035): the chase.
