---
layout: default
title: "WP-071: Phantom's secret passages, storage room and treasury"
---

# WP-071: Phantom's secret passages, storage room and treasury: the wall of fire, the rope and the final clue (Gen 1)

**Status:** ✅ Done (2026-11-17)
**Phase:** 4 (game logic)
**Depends on:** WP-068 ✅ (the armory's slide), WP-067 ✅ (an item taken after a line), WP-047 ✅ (a way that wants snacks), WP-031 ✅ (the final clue and the accusation)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-071-2026-11-17](../reference/pre-flight-WP-071-2026-11-17.md)

---

## Result (2026-11-17)

The reference is `wp072_ref.py`: WP-070's, plus the four rooms, written from the trace before the engine ran. It reads the placements and Velma's steps from the art. It never runs the engine. At `script` level 3 the chase check now has 5 passage lines on Phantom (115 in all), and one on Showdown, which has no such rooms (228 in all).

The first run matched every line but the storage room's, and both differences there were in the check, not the class:
- **The take timing:** the check counted Velma's take from the tick after the line ended, though it starts in the same tick, and it skipped a take that began in tick 0.
- **The opening:** the storage room's opening starts at tick 100, and the check clicked a hotspot before it, while input was still held.

With the check now letting each room's opening play through first, all 115 lines match.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**The classes:** each room gets its own.<br>**The first passage:** Velma walks in from the armory's slide, Daphne from the storage room, and nobody from the second passage.<br>**The wall of fire:** a requires object burning (`FLAMEA`) with its sound. At each level it needs the level's snacks plus two. Clicked with none, or with one too few, it gives that level's line, holding input, and the snack box flashes. With enough, it goes out through movie 39. Back in the room it shows `FLAMEB` without the sound. `GargoyleFlameActive` saves as `No`; only `Yes` loads as burning, and a new game lights it again.<br>**The storage room:** the rope is a requires object until had. The hotspots' lines run `370X_`, `370X1_`, `370X2_`, then start over, without holding input; hotspot 3 has none. The rope with the arrow gives `370B_` before the well and `370A_` after it, holding input. As the line ends, Velma takes the rope in the same tick, with the cursor out and input held. The rope reaches the toolbar 102 ticks later (her step 34), and she is done at 165. Leaving before then still gives the rope.<br>**The treasury:** the Princess clicked with the arrow sets `FinalClue` and goes to `ROOM_Suspect_Chooser` through movie 55. With an item, or a click elsewhere, nothing happens.<br>Showdown prints that it has no secret passages. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized:<br>**The fire** clicked with no snacks: `Treasury.360A_`.<br>**Starting with `GargoyleFlameActive=No`:** the gargoyle with the fire out.<br>**The rope:** `370B_`, then Velma took it, and it went into the toolbar.<br>**The Princess:** movie 55, then the suspects with the final clue. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit, click, inventory and hint checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms).<br>The other checks match WP-070's run, except that Phantom's profile check now writes and imports `GargoyleFlameActive`, and some random keys vary by run: the drawbridge's, Ewan's `CurrentQuestion`, and Showdown's first clue.<br>Fork commit [`287fe5637b`](https://github.com/barefootbetters/scummvm/commit/287fe5637b) (7 files staged by name) is pushed. |

**Deviations and gaps:**

- **The tick clock's restart** (`0x437540`) when Velma takes the rope isn't kept, as in WP-057.
- **The rope line's done flag** is set by the class's tick once the scene's name changes, as the Jester's are ([WP-061](WP-061-room-of-doors.md)); the original's scene player sets it.
- **The cursor's fades** are taken as hidden or shown, as in [WP-064](WP-064-maria-game.md).

**Found on the way:**

- **The fire never takes an item:** its `requiredanim=` is one of Brad's head sequences, never a cursor, so the snacks are all it asks for.
- **After the fire is out it can still be clicked;** with the snacks given, each click plays movie 39 again.
- **The treasury is the end of the story's path:** the Princess gives the final clue and opens the accusation directly.
- **Two of the classes index the game as an `int *`.** Index `+0x42` is byte `+0x108`, `FinalClue`.

---

## Goal

Port four of Phantom's rooms: the two secret passages, the storage room and
the treasury. They come next in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
where the gallery, the magic mirror and `ROOM_P31_KST` follow. Until now
these rooms had the base class:
- the wall of fire did nothing;
- the rope was picked up as a plain item;
- the Princess only idled.

## Background

The rooms ([scooby-exe](../formats/scooby-exe.md#phantoms-secret-passages-storage-room-and-treasury-wp-071)):
- **The second passage's wall of fire** wants the level's snacks before it
  goes out.
- **The storage room's rope** is Velma's to take, after a line.
- **The treasury's Princess** ends the search: the final clue and the
  accusation.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SecretPassage1Room`, `SecretPassage2Room`, `StorageRoomP18` and
  `TreasuryRoom`:** the walk-ins; the fire, its snacks, movie and profile
  key; the hotspots and the rope; the Princess.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes and the first passage's walk-ins;
   - the fire by level, with and without the snacks, and its profile key;
   - the rope's placement, the hotspots, the rope's lines and Velma's
     take, and leaving during it;
   - the Princess.

   Showdown prints that it has no secret passages, as its reference does.
2. [x] Live, in Phantom: the fire's line; the fire out; the rope; the
   Princess into the accusation.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile key and random
   keys. The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-secret-passages-storage-room-and-treasury-wp-071):
  the four rooms.
