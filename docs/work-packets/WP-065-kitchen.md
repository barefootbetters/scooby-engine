---
layout: default
title: "WP-065: Phantom's kitchen"
---

# WP-065: Phantom's kitchen: Ewan, his clue and the grease (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-064 ✅ (the room before it), WP-063 ✅ (a suspect's clue on entry), WP-061 ✅ (Big Head on a first click), WP-058 ✅ (the empty bottle)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-065-2026-11-16](../reference/pre-flight-WP-065-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp066_ref.py`: WP-064's, plus the kitchen, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art, and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 8 kitchen lines on Phantom (75 in all), and one on Showdown, which has no kitchen (222 in all).

The first run matched all 75 lines on Phantom and all 222 on Showdown, with no warnings.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **Placements.** In a new game neither the grease nor the way to the storage room. With the quiz won and the screwdriver: the grease, a requires object at depth 0, and the way out at −1000. With the full bottle had, no grease.
   - **Walk-ins:** Daphne from the dining room; Fred and Daphne from the storage room; nobody from the town.
   - **Ewan on entry:** before his quiz, idle, hit by his step polygon. Won: `Kitchen.190B_` holds input, his own clue, and he is to give it. Given: he stirs at depth −1; with the screwdriver he sleeps; with the mirror used he stirs again.
   - **His clue:** `190B_`, his `GIVES`, `Global.Thank_You_` and the suspects.
   - **A click on him:** the first time, met, and Big Head with `Kitchen.190A_` on `BIG_HEAD_BG_P13`, on to `ROOM_Ewan`; after, straight to `ROOM_Ewan`. Won: `1010G_`, `1010G1_`, `1010G3_` and `1010G_` again, each holding the speech lock, freed after. Asleep: `190F_`, `190F1_`, `190F2_`, `190F_`, each blocking.
   - **The grease:** with the arrow, `190C_`. With the empty bottle input is held. Fred fetches it at tick 1, with `Get_Grease`; the grease hides, the bottle leaves its slot and the arrow is back. At tick 82 the full bottle, and `190G_`. Leaving at once gives the full bottle all the same.
   - **Hotspot 3** scares Daphne. The way to the storage room's movie is 8, and none with the screwdriver.
   - **The profile:** a new game's `EwanIntro=No`, and read back.
   - Showdown prints that it has no kitchen.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **His introduction:** a click on Ewan at the cauldron met him and started Big Head with `190A_` on `BIG_HEAD_BG_P13`, three lines, headed for `ROOM_Ewan`. The run ended during the third line, before the room changed.
   - **His clue,** with his quiz won: `190B_`, `EWAN_COUPON`, `Global.Thank_You_` and the suspects.
   - **The grease,** with the screwdriver had and the empty bottle in the toolbar: Fred fetched it with `Get_Grease`, the bottle filled, and Fred and Daphne said `190G_`.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-064's run but for the clue name that varies by run. Phantom's differ only by the kitchen's new profile key and the drawbridge's random keys.
   - Fork commit [`12d16950e8`](https://github.com/barefootbetters/scummvm/commit/12d16950e8) (9 files staged by name) is pushed.

**Deviations and gaps:**

- **`Kitchen.Ewan_Sleeping`** isn't on the disc, so the fork plays nothing for it.
- **The tick clock's restart** (`0x437540`) when Ewan sleeps isn't kept, as in WP-057.
- **Ewan's click** is read from the engine's click on him, as the Jester's is.

**Found on the way:**

- **The audit pairs three classes here.** Ewan's quiz (`ROOM_Ewan`) and the storage room (`ROOM_P17_Kitchen_Storage`) are each their own WP, after this one.
- **Ewan is drawn at the cauldron behind Fred,** and is hit by his step polygon, which reaches past Fred.
- **The way to the storage room plays a movie (8)** only until the screwdriver has been had.

---

## Goal

Port Phantom's kitchen, `ROOM_P13_Kitchen`, the next room in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now it had the base class:
- Ewan never introduced himself, nor led to his quiz;
- he never gave his clue, stirred or slept;
- the grease never filled the bottle, and the storage room was open from
  the start.

## Background

The kitchen ([scooby-exe](../formats/scooby-exe.md#phantoms-kitchen-wp-065)):
- **Ewan** introduces himself on Big Head and leads to his quiz until it is
  won; then he gives his clue.
- **The grease** fills the empty bottle once the screwdriver has been had.
- **The storage room** opens once his quiz is won.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`KitchenRoom`:** the walk-ins, Ewan's introduction, clue, lines, stirring
  and sleeping, the grease, the way to the storage room, the profile key.
- **`RoomScript`:** the room's exit handler may change an exit's movie.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the placements;
   - the walk-ins;
   - Ewan on entry, before and after his quiz;
   - his clue and the thanks;
   - a click on him, before his quiz, awake and asleep;
   - the grease, and leaving with it;
   - hotspot 3, the way to the storage room's movie, the profile key.

   Showdown prints that it has no kitchen, as its reference does.
2. [x] Live, in Phantom: his introduction; his clue; the grease.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile key. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-kitchen-wp-065): the
  kitchen.
