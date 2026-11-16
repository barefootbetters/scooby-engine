---
layout: default
title: "WP-060: Phantom's gardener's house, garden and plaque"
---

# WP-060: Phantom's gardener's house, garden and plaque: the crest's order (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-057 ✅ (Phantom's story values), WP-058 ✅ (`checkOpening`), WP-031 ✅ (Big Head), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-060-2026-11-16](../reference/pre-flight-WP-060-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp061_ref.py`: WP-058's, plus the three rooms, written from the trace before the engine ran. It reads the placements, `object.ini` and each sequence's steps from the art, and which openings and scenes have lines from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 7 garden lines on Phantom (32 in all), and one on Showdown, which has no gardener's house (217 in all).

The first run differed on one line, and the reference was wrong. The garden's tracks have no `priority=` key, and the default path (`0x408DC0`) reads a missing one as −1; the reference had taken 0. The corrected reference matches all 32 lines on Phantom and all 217 on Showdown.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**The house, unsolved:** the plaque a requires object; no way to the garden; the door stopped on its first step. From the town, Daphne walks in.<br>**The house, solved:** no plaque; the way to the garden built by the default path; the door on its last step. From the garden, Fred walks in.<br>**While Jane screams,** over 100 visits: both `Intro_` and `Intro2_`, and screams 1, 2, 3 and 5.<br>**Back from the plaque:**<br>• untried: no opening, no sound;<br>• four wrong tries: `130B_`, `130B1_`, `130B2_`, `130B_`, each with `Puzzle_Wrong`;<br>• solved: `130C_`, `Puzzle_Right` and `Door`, the door opening.<br>**The house's plaque:** Big Head's `130A_`, `130A1_`, `130A2_`, `130A_` on `BIG_HEAD_BG_PLAQUE`, each back to the house; `PlaqueSeen`. With any one ball found, the plaque's puzzle.<br>**The garden:** no tracks until `MazeEntered`; then a clickable at depth −1 whose lines are `230X_`, `230X1_`, `230X2_`, `230X_`. From the house, Velma walks in.<br>**The plaque's buttons:** requires objects on step 0; under the mouse, step 1. The crest 2, 4, 1, 3 pressed as deer, dragon, bush, lion: each on step 2. Pressing the dragon twice counts once. After the fourth, back to the house with input held, `CrestPuzzle`, and `Button_Click`.<br>**A wrong order:** back to the house without `CrestPuzzle`. A new game clears the try.<br>Showdown prints that it has no gardener's house. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized, from a profile with a red ball found and the crest 2, 4, 1, 3:<br>**To the crest:** the house's plaque led to the plaque room, whose narrator reads it (`130A_`).<br>**The buttons:** deer, dragon, bush and lion pressed, each with `Button_Click`; then "done, right".<br>**Back in the house:** `Puzzle_Right` and `Door` played, the plaque wasn't built, the way to the garden was, and `130C_` started. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms).<br>**The other checks,** against WP-058's run, leaving out WP-059's new "idle check" lines: they differ only in the lines that vary by run, the imported clue name on Showdown and the drawbridge's random keys on Phantom.<br>Fork commit [`7aaee53315`](https://github.com/barefootbetters/scummvm/commit/7aaee53315) (7 files staged by name) is pushed. |

**Deviations and gaps:**

- **Game `+0x287`** (the plaque tried) is kept by the class file, not the game; like the original, the profile doesn't keep it.

**Found on the way:**

- **The plaque gives Big Head's lines until any of the three balls is found;** only then the puzzle.
- **The house's plaque answers a cursor nobody uses** (`requiredanim=ANIM_BRAD_ARMOR_HEADBLINKS_A`); a click with the arrow tells the room all the same.
- **A clickable with no `priority=`** sits at depth −1, as the default path reads the missing key.

---

## Goal

Port three of Phantom's rooms, the third step in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order):
- **ROOM_P05_Gardeners_House:** its plaque, its door and its openings.
  Until now the plaque did nothing, and the way to the garden was always
  open.
- **ROOM_Garden_Plaque:** the crest puzzle. Until now its buttons did
  nothing.
- **ROOM_P06_Garden:** its tracks, which until now were there from the
  start and said nothing.

## Background

The gardener's house ([scooby-exe](../formats/scooby-exe.md#phantoms-gardeners-house-garden-and-plaque-wp-060)):
- **Its plaque** gives Big Head's lines until a ball is found. After that
  it leads to a crest of four buttons, which must be pressed in the order a
  new game drew.
- **Solved,** the door to the garden opens. Coming back, the gang's opening
  says how it went.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`GardenersHouseRoom`:** the placements, the openings by where the gang
  came from, the walk-ins, the door, the screams, and the plaque.
- **`GardenPlaqueRoom`:** the buttons, the mouse over them, the crest's
  order, and back to the house.
- **`GardenRoom`:** the tracks and their lines.
- **A `script` level 3 check** against an independent reference.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes;
   - the house's placements, unsolved and solved, with its walk-ins;
   - the openings and screams while `Screaming`;
   - the returns from the plaque: untried, four wrong tries, solved;
   - the plaque's Big Head lines, and the puzzle once a ball is found;
   - the garden's tracks and lines;
   - the plaque's buttons, the mouse over one, a right order with a
     button pressed twice, a wrong order, and a new game.

   Showdown prints that it has no gardener's house.
2. [x] Live, in Phantom: the house's plaque to the crest, the buttons
   pressed in order, and back to the house with the door opening.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-gardeners-house-garden-and-plaque-wp-060):
  the gardener's house, the garden and the plaque.
