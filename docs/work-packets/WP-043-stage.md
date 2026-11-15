---
layout: default
title: "WP-043: Showdown's stage"
---

# WP-043: Showdown's stage: the sandbags, and Jenny under the trapdoor (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-031 ✅ (suspects and clues), WP-022 ✅ (movies), WP-021 ✅ (clickables), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-043-2026-11-15](../reference/pre-flight-WP-043-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp043_ref.py`: WP-042's, plus the stage, written from the trace before the engine ran. It reads the placements and step counts from the art and whether each opening has a first line from the sound archives' indexes, and never runs the engine. At `script` level 3 the chase check now logs 122 lines on Showdown, the earlier 114 and 8 for the stage; the reference prints the same 122, none different, on the first run. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The stage.** Hung by level: `0111` at levels 0 and 1, `1000` at level 2, `BagsRandomized` set, and a bag set by hand is kept on the next visit. Each sandbag at depth -1001, hidden while up. Before Jenny is met she isn't there and the way down is; Shaggy walks in DL from the saloon and UR from under the stage.<br>**Under the stage.** The levers clickables at depth -500, hit type 2; the sandbags on their last step at depth y - 240, a raised one on its RAISE; the trapdoor at -100; the way out at -1000. The knock countdown is -5 on entry, 72 after tick 1, -1 after tick 74 and 72 after tick 75. The openings: `370BS_` at level 0 on every visit; `370B_`, `370B2_`, `370B3_`, `370B3_` at levels 1 and 2.<br>**The levers.** From all four bags down, with the aliases in order: level 0 moves one bag, level 1 one or two, level 2 three, as the trace's table has it. Another alias set moves the alias's bags, and level 3 moves none. A pull raises the bag with `TRAPDOOR_SANDBAG1_RAISE`, the levers go to hit type 0, and they come back on tick 28 as the 9-step raise stops; the same lever then drops it again.<br>**The trapdoor.** The last bag up: DOOROPEN, Jenny met, `TRAPDOOR_DOOR_OPEN`, the way out and the levers at hit type 0. Out to the stage on tick 34 as the 11-step door stops, through movie 4; the stage on tick 35.<br>**Jenny.** The hammer, `Stage.380D2_` held, her clue, then GIVES (13 steps) on tick 1 with input held; the thanks on tick 40, then the suspects. Back, no scene. Clicked with the arrow she says one of her three lines, not held; with the hammer, nothing. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**The trapdoor.** At level 0 with one bag down, the click on lever 1 hit it, the bag rose and the trapdoor opened. Movie 4 played (785 frames). On the stage, the hammer was in the toolbar and Jenny said `Stage.380D2_`, gave, and the thanks took the gang to the suspects with her clue.<br>**A level 1 lever.** From all four down, lever 1 raised bags 1 and 2 together, with the opening `370B_`. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Phantom's earlier checks are identical to WP-042's run. Showdown's differ only by the setup check's trapdoor opening, which the class now sets. The room check is identical to WP-020's (69 and 53 rooms). Fork commits [`6173d2350c`](https://github.com/barefootbetters/scummvm/commit/6173d2350c) (7 files staged by name) and [`df7b297066`](https://github.com/barefootbetters/scummvm/commit/df7b297066) (a comment's knock period) are pushed. |

**Deviations and gaps:**

- **The way up is taken once.** The original's tick asks for it on every tick from the trapdoor stopping until the room changes. The fork asks once, and its room changes on the next tick.
- **Jenny's click acts on the press,** like every click in the fork; the original reads the release (game `+0x20` bit 4).

---

## Goal

Make Showdown's stage and the room under it play as the original does.
Until now they had the base class: the levers under the stage did
nothing, the trapdoor never opened, and Jenny never came out.

## Background

The stage ([scooby-exe](../formats/scooby-exe.md#the-stage-wp-043)) has
two rooms:
- **Under the stage:** Jenny is shut under the trapdoor, knocking and
  yelling. Four levers raise and drop four sandbags weighing it down. Which
  bags a lever moves depends on its alias, drawn by the new game, and on
  the level. With all four up, the trapdoor opens and the gang comes up on
  the stage.
- **The stage:** the sandbags hang over it, the ones that are down in
  sight. Once Jenny is out, she gives the gang the rusty hammer and her
  clue, and they go to the suspects.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`StageTrapdoorRoom`:** the levers, the sandbags and the trapdoor;
  the knocks; the openings by level; movie 4.
- **`StageRoom`:** hanging the sandbags by level; Jenny, the hammer, her
  scene, clue and thanks; her lines when clicked; Shaggy's walk-ins.
- **A clickable's callback** (`0x401740`), which the levers use.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The saloon,** ROOM_P12_Saloon, the stage's other way out.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the classes;
   - the stage's sandbags hung by level and kept, Jenny and the way down
     before she is met, and Shaggy's walk-ins;
   - under the stage, the placements, the knock countdown and the
     openings by level;
   - each lever at each level, another alias set, and a level with no
     moves;
   - a lever's sandbag, sound and the levers held until it stops, then
     the same lever again;
   - the trapdoor opening, Jenny met, and the way up through movie 4,
     with its ticks;
   - on the stage, the hammer, her scene, clue, giving and thanks with
     their ticks, and her lines when clicked.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the last sandbag raised, the trapdoor open, movie 4, and Jenny on
     the stage with the hammer, her clue and the suspects;
   - a level 1 lever moving two bags.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for what the stage sets. The fork
   diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-stage-wp-043): the stage.
