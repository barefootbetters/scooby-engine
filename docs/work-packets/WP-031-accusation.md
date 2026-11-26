---
layout: default
title: "WP-031: The accusation and Big Head"
---

# WP-031: The suspects and clues, the accusation, and Big Head (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-024 ✅ (suspects met), WP-027 ✅ (room classes), WP-029 (room setup, music; fork pushed, docs in PR #68), WP-030 ✅ (Credits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-031-2026-11-14](../reference/pre-flight-WP-031-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp031_ref.py`, written from the trace. It reads the art and the sound indexes through the repo's probes, and never runs the engine. At `script` level 3 the engine drives both rooms through their classes and logs 14 lines; the reference prints the same 14 on each title, none different. The test game has Artie (Phantom: Wizard) as the villain, three clues in slots 0, 1 and 3, and pictures 1, 3 and 4 met.

**Exit criteria:**

1. **Against the reference:** ✅ On both titles:
   - **The clue book.** The three clues sit at their slots' places with hotspots 1–3; the clue in slot 3 gets hotspot 3. Only the met suspects are buttons. With the final clue there is a final-clue button and hotspot 6, and the exit is gone.
   - **Cards and lines.** Every card and every Scrappy line match: the clues', the final clue's, and the suspects' (`Chuck`, `ICDouble`, `Artie`; Phantom `Ewan`, `Maria`, `Wizard`). The idle line comes on tick 361, and not with the final clue.
   - **The new clue.** It holds input until Scrappy names `CluesFound2`, which is empty here: the original's slot gap. The exit goes back to the first story room.
   - **The accusation.** All five suspects accused get the true villain's movie (Showdown 9, Phantom 17), then `720` for the villain and `730` for the others, on `BIG_HEAD_BG_P03` (`P16`), then the credits.
   - **Big Head.** Six lines with their partners and backgrounds. Showdown: Shaggy with Scooby, Artie, Velma, Fred with Daphne, Scooby with Shaggy, Daphne with Fred. Then the credits.
2. **Live, Showdown:** ✅ From an original-format profile (`start_profile`), through `test_script`, minimized:
   - **The clue book.** It opened in solve mode, and the map's card showed under the mouse.
   - **The accusation.** Artie's poster accused him. Movie 9 (6.5 s) played, then Big Head: Shaggy beside Scooby on the P03 ruins, then Velma's line showing Artie's archaeology class list (clue picture 7), then Fred with Daphne.
   - **The credits.** After six lines, Artie's movie 33 and movie 58, then the credits rolled.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **Nothing finds a clue yet.** The story rooms set `CluesFound<i>`, `FinalClue` and the new-clue flag (through `setNewClue()`); the check and the live run set them directly.
- **The placements are built, then hidden or turned into buttons**, rather than claimed. The room's placement hook only names the object, and these rooms need each placement's ANIM and place.
- **`GBH=Yes` / `FBF=Yes`** is kept as ScummVM's `game_finished` config key; nothing in either game reads it back.
- **Big Head's skip** ends the scene, as the other rooms' openings do (WP-029).

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

1. [x] Both discs match an independent reference line for line:
   - the clues' buttons, places and hotspots;
   - the met suspects' pictures;
   - the final clue and the exit;
   - every card and Scrappy line;
   - the idle line;
   - the new clue;
   - the way back;
   - each suspect accused, with the movie and the reveal;
   - Big Head's speakers, partners and backgrounds, line by line.
2. [x] Live, in Showdown, from an original-format profile with the final
   clue: the clue book, a clue's card, the accusation, the movie, Big Head
   (heads, partner, a clue picture) and the credits.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-accusation-suspects-and-clues-and-big-head-wp-031):
  the clue state, the suspects and clues, and Big Head;
  [audio-archives](../formats/audio-archives.md): the lip sync's high nibble.
