---
layout: default
title: "WP-043: Showdown's stage"
---

# WP-043: Showdown's stage: the sandbags, and Jenny under the trapdoor (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-031 ✅ (suspects and clues), WP-022 ✅ (movies), WP-021 ✅ (clickables), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-043-2026-11-15](../reference/pre-flight-WP-043-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
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
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the last sandbag raised, the trapdoor open, movie 4, and Jenny on
     the stage with the hammer, her clue and the suspects;
   - a level 1 lever moving two bags.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for what the stage sets. The fork
   diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-stage-wp-043): the stage.
