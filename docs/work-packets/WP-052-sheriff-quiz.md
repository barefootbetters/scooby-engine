---
layout: default
title: "WP-052: Showdown's Sheriff's quiz"
---

# WP-052: Showdown's Sheriff's quiz: his notebook, page by page (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-051 ✅ (the saloon), WP-021 ✅ (clickables and requires objects), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-052-2026-11-15](../reference/pre-flight-WP-052-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - the placements, the page's sounds, and the questions drawn;
   - the reading, state by state;
   - the hover, with its ticks;
   - a right answer, the next page, a wrong answer and Street 1;
   - the last page by level, and `SheriffPuzzle`;
   - the keys.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form: the page
   read, a right answer and the next page, a wrong answer and Street 1.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-sheriffs-quiz-wp-052): the
  Sheriff's quiz.
