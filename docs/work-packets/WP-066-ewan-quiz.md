---
layout: default
title: "WP-066: Phantom's Ewan's quiz"
---

# WP-066: Phantom's Ewan's quiz: the chalkboard and its eraser (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-065 ✅ (the kitchen), WP-052 ✅ (the Sheriff's quiz), WP-057 ✅ (Phantom's story values)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-066-2026-11-16](../reference/pre-flight-WP-066-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp067_ref.py`: WP-065's, plus Ewan's quiz, written from the trace before the engine ran. It reads each sequence's steps from the art and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 7 Ewan lines on Phantom (82 in all), and one on Showdown, which has no such room (223 in all).

The first run differed on one line, and the check was wrong. To ask page 4 it set the question and ticked, as the Sheriff's check does; but Ewan's class has no "next page" step to set a page up, so the board stayed on the page already drawn. The check now enters the room on page 4. The second run matched all 82 lines on Phantom and all 223 on Showdown, with no warnings.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **Entry** on page 1: the board shown and stopped at depth 0; the four answers as requires objects at depth 10; the eraser hidden at depth 100. The page's five sounds; the way back to the kitchen. With the opening unplayed, nothing is read. 100 drawn questions: never page 2 or 5.
   - **Reading:** the page lit (board step 1) with its sound, then each answer lit with its own; then free, input back.
   - **Hover:** an answer lit, said 37 ticks on, then again 73 ticks after its sound ends; the board likewise; nothing hovered, nothing lit.
   - **A right answer** (page 1, B): pressed, a `RIGHT_` line, the eraser played once with `Ewan.Erase_Board`, input held. At tick 54 the eraser is done and hidden, and a new page is on the board. **A wrong one** (page 4, A): a `WRONG_1.` line, then `WRONG_2`, then the kitchen, with no puzzle.
   - **Won** at each level with level + 3 right: the board and answers hidden, the kitchen, and `EwanPuzzle` on leaving.
   - **The keys:** a new game's `CurrentQuestion=-1`; `Question11` read alone gives `CurrentQuestion=0`.
   - Showdown prints that it has no Ewan's quiz.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **Page 1:** the narrator's introduction skipped, the page and its answers read aloud on the board; B clicked, `RIGHT_2` and the eraser's sound.
   - **Won,** with pages 1 and 3 done: page 6's A (cheeseburger) right, then back in the kitchen, where `EwanPuzzle` gave Ewan's clue (`190B_`, `EWAN_K`).
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-065's run but for the clue name that varies by run. Phantom's differ only by the quiz's 13 new profile keys and the drawbridge's random keys.
   - Fork commit [`f3b98b08ca`](https://github.com/barefootbetters/scummvm/commit/f3b98b08ca) (7 files staged by name) is pushed.

**Deviations and gaps:**

- **An answer's click** is the fork's click on its requires object with the arrow, as the Sheriff's is.
- **The right-answer table** names pages 2 and 5, which are never asked; the art has no board for either.

**Found on the way:**

- **Ewan's quiz is the Sheriff's rewritten,** not the same code: the eraser between pages, level + 3 where the Sheriff asks level + 2, a 36-tick hover where his is 9, and a wait for the opening.
- **The second wrong line,** `Ewan.NOTEBOOKPAGE_ANSWER_WRONG_2`, is on Phantom's disc. Showdown's Sheriff asks for the same name, which his disc lacks ([WP-052](WP-052-sheriff-quiz.md)).

---

## Goal

Port Phantom's Ewan's quiz, `ROOM_Ewan`, which the kitchen
([WP-065](WP-065-kitchen.md)) leads to. Until now it had the base class:
the board never showed a page, and nothing set `EwanPuzzle`.

## Background

Ewan's quiz ([scooby-exe](../formats/scooby-exe.md#phantoms-ewans-quiz-wp-066))
is the Sheriff's notebook quiz on a chalkboard: right answers are wiped
off by an eraser for the next page, and the level + 3 of them win it.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`EwanRoom`:** the board, answers and eraser, reading, hover, right and
  wrong answers, the win and the way back, the profile keys.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - entry, the opening's wait, the questions drawn;
   - reading and hover;
   - a right answer and the eraser, a wrong one;
   - the win at each level;
   - the keys.

   Showdown prints that it has no Ewan's quiz, as its reference does.
2. [x] Live, in Phantom: a page read and answered right; the quiz won and
   Ewan's clue in the kitchen.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-ewans-quiz-wp-066): Ewan's
  quiz.
