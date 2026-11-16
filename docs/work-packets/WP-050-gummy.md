---
layout: default
title: "WP-050: Showdown's whistle puzzle"
---

# WP-050: Showdown's whistle puzzle: Gummy's tune on the bells (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-049 ✅ (the railroad station), WP-031 ✅ (suspects met), WP-021 ✅ (clickables and their callback), WP-019 ✅ (sound and lip sync)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-050-2026-11-15](../reference/pre-flight-WP-050-2026-11-15.md)

---

## Goal

Make Showdown's whistle puzzle, ROOM_Gummy, play as the original does.
Until now it had the base class:
- Gummy never whistled;
- the bells did nothing;
- the puzzle couldn't be solved.

## Background

The puzzle ([scooby-exe](../formats/scooby-exe.md#gummys-whistle-puzzle-wp-050)):
- **Gummy whistles a tune** in his sleep, one of three for the level, and
  the bells play it back note by note.
- **Ringing the bells** in the tune's order solves it: `GummyPuzzle` is set,
  Gummy is met, and the gang goes back to the railroad station.
- **A wrong bell** has Gummy whistle it again.
- **Meanwhile** he snores and the donkey blinks.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`GummyRoom`:**
  - the tunes and their bells;
  - the whistle, the play-back and the rings;
  - the bells' callback;
  - the snore, the blink and the lip sync;
  - the way back to the station.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class, and the nine tunes;
   - the bells, Gummy, the donkey, the opening and the timers on entry;
   - the whistle, `220B2_`, and the play-back with each bell's ring;
   - a wrong bell, then the tune rung, `GummyPuzzle`, Gummy met, and the
     station, with their ticks;
   - Gummy clicked during and after the play-back; the snore and the
     blink.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form: the
   whistle, the play-back, a wrong bell, the tune rung, and the station.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#gummys-whistle-puzzle-wp-050):
  the whistle puzzle.
