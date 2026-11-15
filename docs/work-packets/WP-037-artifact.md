---
layout: default
title: "WP-037: Showdown's artifact puzzle"
---

# WP-037: Showdown's artifact puzzle: ICDouble's bones (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-036 ✅ (the close-up), WP-025 ✅ (toolbar-hiding rooms)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-037-2026-11-15](../reference/pre-flight-WP-037-2026-11-15.md)

---

## Goal

Make Showdown's artifact puzzle play as the original does. The close-up
sends the gang to one of nine ROOM_Artifact_* rooms, and until now they had
the base class: the bones lay where the room placed them, and nothing could
build the artifact, so ICDouble could never give his clue.

## Background

The puzzle ([scooby-exe](../formats/scooby-exe.md#the-artifact-puzzle-wp-037))
is a jigsaw of 9, 12 or 15 bones, one room per artifact (bowl, deer, vase)
and level:
- **Carrying a bone:** a click picks it up, and it follows the mouse.
- **Placing it:** within 10 pixels of its place it snaps in; a second click
  drops it back where it started.
- **The artifact:** with every bone in place the artifact morphs,
  `ArtifactsBuilt` becomes 1, and the gang goes back to the close-up, where
  ICDouble gives his clue (WP-036).

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`ArtifactRoom`:**
  - the placements, and each piece's start by level;
  - the cursor, the pick-up, the carry, the snap and the drop;
  - the morph, `ArtifactsBuilt`, and the way back to the close-up;
  - the reset and `PiecePlaced0`–`14`.
- **A room-class hook** that hides the cursor while input stays on.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The safe the combination opens.**

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class for all nine rooms;
   - each room's pieces, in build order: start, place, depth and hit test;
   - the outline and the artifact;
   - with the mouse: the cursor, the pick-up, the carry, the snap a tick
     after the mouse brings the piece close, the drop, and a piece carried
     exactly onto its place;
   - the last piece building the artifact, `ArtifactsBuilt`, the morph's
     ticks, the way back, and the keys and the reset.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form: a piece
   dropped back, all nine carried in, the artifact built, and on through
   the close-up's clue to the suspects and clues.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-artifact-puzzle-wp-037): the puzzle.
