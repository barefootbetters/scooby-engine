---
layout: default
title: "WP-052: Showdown's Sheriff's quiz"
---

# WP-052: Showdown's Sheriff's quiz: his notebook, page by page (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-051 ✅ (the saloon), WP-021 ✅ (clickables and requires objects), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-052-2026-11-15](../reference/pre-flight-WP-052-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp053_ref.py`: WP-051's, plus the quiz, written from the trace before the engine ran. It reads the placements from the art, and which sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 184 lines on Showdown: the earlier 177 and 7 for the quiz. On Phantom both print the one line saying there is no chase. The first run matched all 184, and so did the run of the committed build.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**Entry.** The notebook is a sprite at depth 0, on `PAGE1`, looping. The four answers are requires objects at depth 10, on `ANSWERS1A`–`D`, stopped on step 0. The exit to Street 1 is there. The page's five sounds are found. 100 questions drawn: none page 3 or 6.<br>**The reading.** On tick 1 the page is read on step 1. Then each answer is read on its step 1, the rest on step 0, with input held. Then input is free, and everything is on step 0.<br>**The hover.** B hovered is on step 1 with its sound and a countdown of 8 after its first tick. It is read on tick 10, and again 73 ticks after it ends. The page hovered goes on step 1; nothing hovered, everything goes back to step 0.<br>**The answers.** Page 1's C is right: step 2, one of `RIGHT_1`–`3`, the page answered, a new one drawn. Over, page 4: the answers become `OBJ_SHERIFF_ANSWERS4`. Page 4's A is wrong: `WRONG_1.1`, then nothing (the exe's `Ewan.` line isn't on the disc), then `ROOM_P03_Street1`. `SheriffPuzzle` stays unset, and the page is kept.<br>**The last page.** At each level, level + 2 right brings page 3, whose answers draw nothing. It is read, then Street 1, and `SheriffPuzzle` is set on leaving.<br>**The keys.** A new game writes `CurrentQuestion=-1`; a missing one reads 0. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**Page 1.** It is read with its four answers. Hovering B lights it up and repeats its line. Clicking C plays `RIGHT_1`, then the next page (5) is read.<br>**Page 4.** Clicking A plays `WRONG_1.1`, then Street 1. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. On Phantom the earlier checks are identical to WP-051's run. On Showdown only the profile check differs: it writes the 16 new keys (427 to 443) and reads 16 back on import (449 to 465), plus its `CluesFound1`, random each run. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`d59a4e001d`](https://github.com/barefootbetters/scummvm/commit/d59a4e001d) (7 files staged by name) is pushed. |

**Deviations and gaps:**

- **`rand()`:** the question drawn and the right line's digit come from the engine's own random source.
- **Input held and the cursor fades** (`0x435150`, `0x4351C0`) are `isBusy`.
- **The hover** (a sprite's `+8`) is the engine's sprite under the mouse.
- **The answers' object refresh** (vtable `+0x10` after `0x4313C0`) isn't traced; the fork doesn't call it.

**Found on the way:**

- **The second wrong line never plays.** The exe asks for `Ewan.NOTEBOOKPAGE_ANSWER_WRONG_2`; the disc has `Sheriff.NOTEBOOK_ANSWER_WRONG_2`.
- **Pages 3 and 6 are never drawn.** Page 3 is the last page, shown once the count is reached; page 6 has a right answer (6C) but never comes up.

---

## Goal

Make Showdown's Sheriff's quiz, ROOM_Sheriff, play as the original does.
Street 1's class already sends the gang there when the Sheriff is clicked.
Until now the room had the base class:
- no page was read;
- the answers did nothing;
- `SheriffPuzzle` was never set.

## Background

The quiz ([scooby-exe](../formats/scooby-exe.md#the-sheriffs-quiz-wp-052)):
- **A page of his notebook,** drawn at random, is read out, then each of
  its four answers, each lit up in turn.
- **Hovered,** the page or an answer lights up and is read again.
- **A right answer** brings the next page. The level's count of them
  (level + 2) brings the last page and, back on Street 1, `SheriffPuzzle`.
- **A wrong one** sends the gang back to Street 1, with the page kept.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SheriffRoom`:**
  - the notebook and the answers;
  - the reading;
  - the hover;
  - the answers' callback;
  - the last page;
  - its keys in the profile.
- **The sound manager's stop of the SFX and speech files** (`0x434E10`).
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the class;
   - the placements, the page's sounds, and the questions drawn;
   - the reading, state by state;
   - the hover, with its ticks;
   - a right answer, the next page, a wrong answer and Street 1;
   - the last page by level, and `SheriffPuzzle`;
   - the keys.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile in the original's form: the page
   read, a right answer and the next page, a wrong answer and Street 1.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-sheriffs-quiz-wp-052): the
  Sheriff's quiz.
