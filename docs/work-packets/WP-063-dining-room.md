---
layout: default
title: "WP-063: Phantom's dining room"
---

# WP-063: Phantom's dining room: Maria's movie, her clue and the burger (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-062 ✅ (the room before it), WP-061 ✅ (Phantom's clues, a suspect's thanks), WP-059 ✅ (the idle line), WP-057 ✅ (Phantom's story values)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-063-2026-11-16](../reference/pre-flight-WP-063-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp064_ref.py`: WP-062's, plus the dining room, written from the trace before the engine ran. It reads the placements, the room's layers and each sequence's name from the art, and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 8 dining-room lines on Phantom (57 in all), and one on Showdown, which has no dining room (220 in all).

The first run matched all 57 lines on Phantom and all 220 on Showdown, with no warnings.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**Placements.** The class builds the burger, the mug and hotspots 2–4 under the second layer, which this room doesn't have, so they attach to the root. The burger is an inventory object at depth 1, hidden until Maria's game is won. The mug is an exit at depth 1000 to `ROOM_P31_KST`. The hotspots are clickables at depths 10000, 1 and 2. Hotspot 1 is as the default path builds it.<br>**Entry.** The first visit asks for movie 35 into `ROOM_Maria` and sets `MariaMoviePlayed`; Maria isn't met. After, she is met, one snack is needed, and nothing plays. With her game won, `Dining_Room.350A_` holds input and she gives one of her own clues; back again, no second scene.<br>**Her clue:** `350A_`, her `GIVES`, then `Global.Thank_You_` and `ROOM_Suspect_Chooser`.<br>**A click on Maria** with the arrow: before her game is won, to `ROOM_Maria`; after, nothing.<br>**Hotspot 2** scares all five (state `0x11`).<br>**Idle:** Velma's `GLASSES` and `Global.1000A2_`, input free. Maria's idle line is the base one until her game is won, then `1010I1_`, `1010I3_` and `1010I4_`; Fred's stays the base one.<br>**The profile:** a new game's `MariaMoviePlayed=No`; `Yes` after a visit, and read back.<br>Showdown prints that it has no dining room. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized:<br>**The first visit:** movie 35 (32 s), then `ROOM_Maria`.<br>**Her game won:** on entry Maria said `350A_` and gave `MARIA_KEYS`; then `Global.Thank_You_`, and the suspects and clues opened on her clue.<br>**A click on Maria** before her game is won took the gang to `ROOM_Maria`. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms), so the new claim kinds leave every room as it was.<br>**Showdown:** its other checks are identical to WP-062's run.<br>**Phantom:** its checks differ only by the dining room's new profile key and the drawbridge's random keys.<br>Fork commit [`aa1723370a`](https://github.com/barefootbetters/scummvm/commit/aa1723370a) (9 files staged by name) is pushed. |

**Deviations and gaps:**

- **The first visit's base entry** (`0x40B920`) runs in the fork before the class asks for Maria's movie; the original skips it. The room is left at once, as in the throne room ([WP-062](WP-062-throne-room.md)).
- **Maria's game** (`ROOM_Maria`) still has the base class: nothing in it sets `MariaPuzzle` yet. Ported in [WP-064](WP-064-maria-game.md).
- **Maria's click** is read from the engine's click on her, as the Jester's is.

**Found on the way:**

- **The first visit goes straight into Maria's game,** through her movie; the dining room proper is only seen after.
- **The class builds under a layer the room doesn't have.** The original passes game `+0x5C`, empty here; the sprites end up with the root, as the default path's do.
- **`Global.Thank_You_` has no clips on Phantom's disc,** so the thanks is silent, as the Jester's is.

---

## Goal

Port Phantom's dining room, `ROOM_P12_Dining_Room`, the next room in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now it had the base class:
- Maria's movie and her game were never reached;
- she never gave her clue;
- the burger was there from the start.

## Background

The dining room ([scooby-exe](../formats/scooby-exe.md#phantoms-dining-room-wp-063)):
- **The first visit** plays Maria's movie into her game.
- **Maria** sends the gang back to her game until it is won; then she gives
  her clue.
- **The burger** shows once her game is won.

Maria's game itself, `ROOM_Maria`, is as large as the artifact jigsaw, and
is split off as WP-064.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`DiningRoomRoom`:** Maria's movie, her clue, a click on her, the
  burger, the mug and hotspots, the idle chatter and line, the profile key.
- **`Room`:** a class can build an inventory object or an exit under a
  layer and at a depth of its own.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the placements before and after her game is won;
   - the first visit's movie; Maria met, the snack, her clue on entry;
   - her clue, `GIVES` and the thanks;
   - a click on her before and after her game is won;
   - hotspot 2's fright;
   - the idle chatter and the idle lines;
   - the profile key.

   Showdown prints that it has no dining room, as its reference does.
2. [x] Live, in Phantom: the first visit's movie into her game; her clue
   with the game won; a click on her into her game.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile key. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-dining-room-wp-063): the
  dining room.
