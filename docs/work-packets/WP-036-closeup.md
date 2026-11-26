---
layout: default
title: "WP-036: Showdown's close-up"
---

# WP-036: Showdown's close-up: ICDouble's clue and the combination (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-035 ✅ (the chase), WP-034 ✅ (the clue a suspect gives), WP-023 ✅ (requires objects and the toolbar)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-036-2026-11-15](../reference/pre-flight-WP-036-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp036_ref.py`: WP-035's, plus the close-up, written from the trace before the engine ran. It reads the step counts of the combination, ICDouble's GIVES and Shaggy's take from the disc, and never runs the engine. At `script` level 3 the chase check now logs 56 lines on Showdown, WP-035's 44 and 12 for the close-up; the reference prints the same 56, none different. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **The first visit.** ICDouble met, Big Head next on tick 1 with `Chase.Branch_2.260A_` on BIG_HEAD_BG_P25A, then ROOM_Artifact_Bowl, Deer or Vase, `_09`, `_12` or `_15` by level.
   - **ICDouble clicked.** Before the artifact, back to its room on tick 1; after his clue, all four of `Chase_B2_Closeup.1901_` to `1904_` over 40 clicks, not held.
   - **His clue.** All three 260C lines over 40 visits, holding input; a clue from ICDOUBLE that fits the rule; GIVES (33 steps) on tick 1 once the line is skipped, held; the thanks on tick 100 (3 × 33 later), then the suspects and clues.
   - **The combination.** A requires object at depth 500 on its last step (41 of 42), hidden, input held; blown in on tick 25 with `ICDouble.Combo.Blows.In`, one behind Shaggy; in front of him on tick 139 (step 38); over and input free on tick 151; `ComboBlewOn=Yes`. Back again: shown at once, not held.
   - **Clicked.** `Chase.Branch_2.486_`, not held; Shaggy takes it on tick 1 (11 steps), it hidden, not held; in the toolbar on tick 34. Back with it held: not built. Leaving during the take still puts it in the toolbar.
   - **The keys.** `ComboBlewOn=Yes` reads back; a reset clears it; a missing key reads false.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, each from a profile in the original's form (`start_profile`):
   - **Not met.** Big Head played `260A`'s eight lines (Shaggy, ICDouble, Scooby), then ROOM_Artifact_Deer_09 loaded.
   - **The artifact built.** `260C2_` played and he gave IC_MAP; GIVES started on tick 118, when his lines were over, the thanks on tick 217, then the suspects and clues.
   - **His clue given.** The combination blew in on tick 25 and came to rest at Shaggy's feet. Clicked, `486_` played; Shaggy took it on tick 459 and it was in the toolbar on tick 492. ICDouble clicked: `1902_`.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **Input once the combination is in.** The original frees input (game `+0x24`) on every tick once the combination has blown in. That also frees a hold the class didn't set, such as an exit's walk-off in the close-up. The fork frees only the class's own hold, and starts the combination's scene without one, which is what the original's per-tick release comes to.
- **The artifact rooms** have no class yet: ROOM_Artifact_* loads, and the puzzle isn't playable, so nothing in the fork sets `ArtifactsBuilt` yet.

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

1. [x] Showdown matches an independent reference line for line:
   - the first visit's Big Head and the artifact's room, by type and level;
   - ICDouble clicked before and after the artifact;
   - his clue: the 260C lines, the clue, GIVES and the thanks, with their
     ticks;
   - the combination: its placement, the hold, the blow-in tick, the step
     it passes Shaggy, the tick input is free, and `ComboBlewOn`;
   - clicked: its scene, Shaggy's take and the toolbar, with their ticks;
   - leaving during the take, and the keys and the reset.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - not met: Big Head, then the artifact's room;
   - the artifact built: his clue, the thanks, the suspects and clues;
   - his clue given: the combination blows in, is clicked and taken, and
     ICDouble has a line.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-close-up-p25a-wp-036): the close-up.
