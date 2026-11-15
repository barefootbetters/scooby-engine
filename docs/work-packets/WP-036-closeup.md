---
layout: default
title: "WP-036: Showdown's close-up"
---

# WP-036: Showdown's close-up: ICDouble's clue and the combination (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-035 ✅ (the chase), WP-034 ✅ (the clue a suspect gives), WP-023 ✅ (requires objects and the toolbar)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-036-2026-11-15](../reference/pre-flight-WP-036-2026-11-15.md)

---

## Goal

Make the chase's close-up, ROOM_P25A_Chase_B2_Closeup, play as the
original does. Until now it had the base class: ICDouble dug, and nothing
happened. WP-035 brought the run-offs into it and back.

## Background

The close-up ([scooby-exe](../formats/scooby-exe.md#the-close-up-p25a-wp-036))
takes the player through three visits:
- **Meeting ICDouble:** the first visit introduces him on Big Head, then
  goes to the artifact's room (the artifact puzzle, by type and level).
- **His clue:** once the artifact is built, he gives his clue, and the
  gang thanks him and goes to the suspects and clues.
- **The combination:** after that, the safe's combination blows in, and
  Shaggy takes it for the toolbar.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`CloseupRoom`:**
  - the entry, by whether ICDouble is met and whether the artifact is
    built;
  - his clue, through the other session's `giveClue`, GIVES and the
    thanks;
  - the clicks on ICDouble;
  - the combination's placement, blow-in, click and take;
  - the leave, the reset and `ComboBlewOn`.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The artifact rooms,** ROOM_Artifact_* (the puzzle). Only the way in is
  here.
- **The safe the combination opens.**

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the first visit's Big Head and the artifact's room, by type and level;
   - ICDouble clicked before and after the artifact;
   - his clue: the 260C lines, the clue, GIVES and the thanks, with their
     ticks;
   - the combination: its placement, the hold, the blow-in tick, the step
     it passes Shaggy, the tick input is free, and `ComboBlewOn`;
   - clicked: its scene, Shaggy's take and the toolbar, with their ticks;
   - leaving during the take, and the keys and the reset.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from profiles in the original's form:
   - not met: Big Head, then the artifact's room;
   - the artifact built: his clue, the thanks, the suspects and clues;
   - his clue given: the combination blows in, is clicked and taken, and
     ICDouble has a line.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-close-up-p25a-wp-036): the close-up.
