---
layout: default
title: "WP-030: Options and Credits"
---

# WP-030: The options and credits rooms (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-022 ✅ (movies), WP-027 ✅ (room classes, the main menu), WP-028 ✅ (Sign In, the new game)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-030-2026-11-14](../reference/pre-flight-WP-030-2026-11-14.md)

---

## Goal

Give the last two front-end rooms their classes:
- **Options:** the main menu's volume sliders for music, sound effects and
  voices.
- **Credits:** the game's ending, from the villain's movie to Sign In.

## Background

The main menu's Options button and the end of the story lead to rooms
that still run the base class. The original's classes (details in
[scooby-exe](../formats/scooby-exe.md#options-and-credits-wp-030)):
- **Options** strings three sliders between six markers placed in the
  room. A knob dragged along a line sets a volume, as a gain from 0.7 to
  1.0.
- **Credits** plays the villain's movie and movie 58, then scrolls three
  companies' logos and text while the gang talk, then goes to Sign In.
  Leaving it after movie 58 ends the game: the player's profile goes, and
  a new game starts with every movie seen.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`OptionsRoom`:**
  - the markers, sorted as the original sorts them;
  - the sliders' knobs and dragging;
  - ScummVM's music, sound-effect and speech volumes for the original's
    gains;
  - the samples played when a knob is let go.
- **`CreditsRoom`:**
  - the villain's movie and movie 58;
  - the three parts' logos, scrolling text and scenes;
  - skipping;
  - the end of the game.
- **The last movie played** (game `+0x90`), and `down` and `up` steps for
  `test_script`.
- **A `script` level 3 check:**
  - Options: the sliders' ends and knobs, and drags to points along and
    off each line with the volume and sample each leaves;
  - Credits: each villain's movie, and a full roll and a skipped one.

**Out of scope:**

- **Room music** (`Group%i_%i.Music`, `0x40AA10`): the fork has none yet.
  Options' music slider sets the volume without replaying music, and
  Credits' scenes don't fade it.
- **Big Head and the accusation**, which lead to Credits: the story rooms
  (WP-029).

## Exit criteria

1. [ ] Both discs match an independent reference line for line:
   - the markers, the sliders' ends and the starting knobs;
   - six drags per slider, with the volumes and samples;
   - each villain's movie;
   - the roll's parts, ticks and ending;
   - a skip.
2. [ ] Live, in Showdown:
   - the options screen;
   - a music knob dragged and a sound-effects knob dragged off its end,
     with the volumes saved;
   - the credits rolling with the gang's lines, and a skip to Sign In.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#options-and-credits-wp-030):
  Options, the slider and Credits.
