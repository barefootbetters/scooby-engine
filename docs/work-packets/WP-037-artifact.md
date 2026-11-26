---
layout: default
title: "WP-037: Showdown's artifact puzzle"
---

# WP-037: Showdown's artifact puzzle: ICDouble's bones (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-036 ✅ (the close-up), WP-025 ✅ (toolbar-hiding rooms)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-037-2026-11-15](../reference/pre-flight-WP-037-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp037_ref.py`: WP-036's, plus the puzzle, written from the trace before the engine ran. It reads each room's placements from the disc and the start tables straight from `Scooby.exe`, and never runs the engine. At `script` level 3 the chase check now logs 72 lines on Showdown, the earlier 56 and 16 for the puzzle; the reference prints the same 72, none different. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **The rooms.** All nine get the class. Each room's pieces, in build order, start where the level's table puts them, with their places from the placements, at depth 1, hit by their cels; the outline at depth 0; the artifact (5 steps) at depth 2, hidden; `Artifact.Intro_1_ICDOUBLE`.
   - **With the mouse, in Deer 09.** The open hand over a loose piece, the arrow elsewhere. A click picks piece 0 up at depth 185 (its y), the cursor hidden. Carried 15 to the right of its place it follows; at 5 and 5 it follows; the next tick it snaps in at depth 1, with a clink. Over a placed piece, the arrow, and a click does nothing.
   - **The drop.** Piece 1 dropped elsewhere goes back to its start with `Artifact.Wrong`.
   - **Exactly on its place.** Piece 2 carried exactly onto its place stays carried; the next click sends it back to its start.
   - **Built.** The ninth piece builds it: `ArtifactsBuilt` 1, `Artifact.Morph`, the artifact shown and playing; PiecePlaced 0-8 Yes; the morph over on tick 15, the close-up on tick 16. Back again, all nine in place.
   - **The keys.** They read back; a reset clears them.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, from a profile in the original's form starting in ROOM_Artifact_Deer_09:
   - **The drop.** Piece 0 was picked up, carried with the cursor hidden, and dropped back.
   - **The puzzle.** All nine went in, each about 9 ticks after it was picked up, and the artifact was built on tick 312 and morphed.
   - **The close-up.** It loaded on tick 341, when the morph's sound was over. `260C3_` played and ICDouble gave IC_EYE_DOCTOR; then the suspects and clues.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **The base tick runs first.** The original's tick runs the base tick (`0x40B490`) last; the fork's room classes run after it. Nothing in the base tick reads what the puzzle sets in the same tick.
- **The positions are whole pixels.** The original keeps them as floats, but every start, place and mouse position is whole, so the tests come out the same.
- **The hook in the shared files.** `RoomClass::hidesCursor()` hides the cursor while input stays on, as `0x435150` does on the cursor sprite alone.

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

1. [x] Showdown matches an independent reference line for line:
   - the class for all nine rooms;
   - each room's pieces, in build order: start, place, depth and hit test;
   - the outline and the artifact;
   - with the mouse: the cursor, the pick-up, the carry, the snap a tick
     after the mouse brings the piece close, the drop, and a piece carried
     exactly onto its place;
   - the last piece building the artifact, `ArtifactsBuilt`, the morph's
     ticks, the way back, and the keys and the reset.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile in the original's form: a piece
   dropped back, all nine carried in, the artifact built, and on through
   the close-up's clue to the suspects and clues.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-artifact-puzzle-wp-037): the puzzle.
