---
layout: default
title: "WP-050: Showdown's whistle puzzle"
---

# WP-050: Showdown's whistle puzzle: Gummy's tune on the bells (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-049 ✅ (the railroad station), WP-031 ✅ (suspects met), WP-021 ✅ (clickables and their callback), WP-019 ✅ (sound and lip sync)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-050-2026-11-15](../reference/pre-flight-WP-050-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp051_ref.py`: WP-049's, plus the puzzle, written from the trace before the engine ran. It reads the placements and step counts from the art, and which sounds and scenes are on the disc from the sound archives' indexes. The tunes are the trace's own table. It never runs the engine. At `script` level 3 the chase check now logs 166 lines on Showdown: the earlier 160 and 6 for the puzzle. On Phantom both print the one line saying there is no chase.

The first run matched 165. The odd line, the bells, came from two causes:
- **The reference.** A wrong bell's callback asks for the whistle again, and since the clickables tick before the room, the room starts it in the same frame. The reference had expected the request still waiting.
- **The class.** The play-back's rings went straight to the clickable, so a ring for a bell still swinging was lost; the original's clickable keeps a count of rings waiting (`+0x80`). The class now keeps that queue.

The check ends each sound itself. It now lets each note's ring go before ending the note, as a real note outlasts its bell's swing. With those changes all 166 match.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The tunes.** All nine match the trace's table: whistle, digits, the bells' notes and length.<br>**Entry.** Bell 1 is at depth 4 and the others at 10, clickables. Gummy is on his snore, stopped, a requires object hit by his cels. The donkey plays its idle once at depth 5. The opening is `Gummy_Puzzle.220B_`. The state is 0, Gummy will whistle again, the snore is 108, and the blink a multiple of 36 from 108 to 360.<br>**The whistle.** On tick 1 Gummy whistles `Gummy.Whistle1a`, with input held. Over, `220B2_` plays, held. Then state 3, and Gummy whistles again. The play-back goes `Gummy.Bell8` bell 5, `Bell7` bell 4, `Bell6` bell 3, `Bell5` bell 2, `Bell6` bell 3, the last ring bell 3's. Input is then free.<br>**The bells.** Bell 1, a wrong note, has Gummy whistle again at once, and the play-back repeats the whole tune. Bells 5, 4, 3, 2 and 3 then ring `Bell8`, `Bell7`, `Bell6`, `Bell5` and `Bell6`. With the last, `GummyPuzzle` is set, Gummy is met, the cursor is hidden, and the count is 71 after its tick. The station comes 74 ticks later.<br>**Gummy and the timers.** Clicking Gummy during the play-back does nothing; with the bells free, he whistles again. The snore comes 2 ticks after its count runs down (`Gummy.Snore`, his snore once), and the count goes back to 108. The blink plays the donkey's blink or idle once, with a new count. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from a profile in the original's form, repeated until the tune the clicks were for, `Gummy.Whistle1a`, came up (the fourth run):<br>**The whistle.** `220B_`, Gummy's whistle, `220B2_`, then the whistle and the play-back.<br>**A wrong bell.** Bell 1 brought the whistle again. In the play-back, the fifth note's ring waited for bell 3 to be free, then rang.<br>**The tune.** Bells 5, 4, 3, 2 and 3 rang it. The gang left for the railroad station 74 ticks later. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The earlier checks are identical to WP-049's run on both titles. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`ee1420a9c5`](https://github.com/barefootbetters/scummvm/commit/ee1420a9c5) (5 files staged by name) is pushed. |

**Deviations and gaps:**

- **`rand()` isn't reseeded.** The original reseeds it from the clock on entry; the fork draws from the engine's own random source.
- **The cursor once the tune is rung** is hidden (`RoomClass::hidesCursor`). The original passes 0x12 to its cursor's fade (`0x435150`), which wasn't traced further.
- **The bells' clicks act on the press,** like every click in the fork.

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

1. [x] Showdown matches an independent reference line for line:
   - the class, and the nine tunes;
   - the bells, Gummy, the donkey, the opening and the timers on entry;
   - the whistle, `220B2_`, and the play-back with each bell's ring;
   - a wrong bell, then the tune rung, `GummyPuzzle`, Gummy met, and the
     station, with their ticks;
   - Gummy clicked during and after the play-back; the snore and the
     blink.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile in the original's form: the
   whistle, the play-back, a wrong bell, the tune rung, and the station.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#gummys-whistle-puzzle-wp-050):
  the whistle puzzle.
