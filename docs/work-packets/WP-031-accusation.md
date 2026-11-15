---
layout: default
title: "WP-031: The accusation and Big Head"
---

# WP-031: The suspects and clues, the accusation, and Big Head (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-024 ✅ (suspects met), WP-027 ✅ (room classes), WP-029 ✅ (room setup, music), WP-030 ✅ (Credits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-031-2026-11-14](../reference/pre-flight-WP-031-2026-11-14.md)

---

## Goal

End the story the way the original does:
- **The clue book.** The magnifying glass opens the suspects and clues: the
  clues found, the suspects met, and Scrappy on each.
- **The accusation.** Once the final clue is found, a suspect's picture
  accuses them.
- **The reveal.** The villain's movie plays, then Big Head unmasks them,
  then the credits.

## Background

Credits (WP-030) is entered from Big Head, but neither Big Head nor the
suspects and clues has a class yet (details in
[scooby-exe](../formats/scooby-exe.md#the-accusation-suspects-and-clues-and-big-head-wp-031)):
- **The suspects and clues** builds buttons for the clues found and the
  suspects met, shows a card for the clue under the mouse, and has Scrappy
  explain either. With the final clue, a picture accuses.
- **Big Head** is a general cutscene room. The game gives it a scene, a
  background and the room after. Each line shows the speaker's big head,
  and some lines show the villain's clue pictures instead: the lip sync's
  high nibble, which WP-004 left unexplained.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SuspectChooserRoom`:**
  - the placements, clues, hotspots and card;
  - Scrappy's lines and the idle line;
  - the new-clue announcement;
  - the accusation and the verdict, for both titles' suspects;
  - the way back.
- **`BigHeadRoom`:**
  - the speaker, partner and background for each line;
  - the line player;
  - the clue pictures from the lip sync's high nibble;
  - the room after.
- **Engine:**
  - `startBigHead()`, for the verdict and the story rooms;
  - the new-clue flag (game `+0x109`);
  - the lip sync's high nibble;
  - a `start_profile` test key.
- **A `script` level 3 check** of both rooms, against an independent
  reference.

**Out of scope:**

- **Finding clues and the final clue** in the story rooms (WP-029 and
  later). They set the keys this packet reads.
- **The chase close-up's** use of Big Head (a story room).

## Exit criteria

1. [ ] Both discs match an independent reference line for line:
   - the clues' buttons, places and hotspots;
   - the met suspects' pictures;
   - the final clue and the exit;
   - every card and Scrappy line;
   - the idle line;
   - the new clue;
   - the way back;
   - each suspect accused, with the movie and the reveal;
   - Big Head's speakers, partners and backgrounds, line by line.
2. [ ] Live, in Showdown, from an original-format profile with the final
   clue: the clue book, a clue's card, the accusation, the movie, Big Head
   (heads, partner, a clue picture) and the credits.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-accusation-suspects-and-clues-and-big-head-wp-031):
  the clue state, the suspects and clues, and Big Head;
  [audio-archives](../formats/audio-archives.md): the lip sync's high nibble.
