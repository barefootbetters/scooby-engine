---
layout: default
title: "WP-030: Options and Credits"
---

# WP-030: The options and credits rooms (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-022 ✅ (movies), WP-027 ✅ (room classes, the main menu), WP-028 ✅ (Sign In, the new game)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-030-2026-11-14](../reference/pre-flight-WP-030-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp030_ref.py`, written from the trace. It reads the art and the sound indexes through the repo's probes, and never runs the engine. It works the sliders in 32-bit floats where the slider keeps floats. At `script` level 3 the engine drives both rooms through their classes and logs 16 lines; the reference prints the same 16 on each title, none different.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ On both titles:<br>**The sliders.** The six markers are hidden and give three sliders: Showdown 363,232–551,232, 359,282–549,281 and 363,334–550,331. Volumes 256, 205 and 150 start the knobs at 1, 0.3359 and 0 (150 is under the original's 0.7 floor).<br>**Dragging.** Each slider is dragged twice through six points along and across its line, ending past its right or its left end. The value and the knob's place match at each point, and so do the volume and sample left on release (179 at the left end, 256 at the right). Phantom's sample is `Knights.Glass_Breaks.3`.<br>**Credits.** Each of the ten villains gets movie `0x21`–`0x31` and another name none. Movie 58 comes next. In Showdown, the TLC, WB and TGI texts (3600, 1555 and 5800 pixels) change parts at ticks 1977 and 2931 and end at 6006, then Sign In; the game ends with the player gone, `StartRoom` `ROOM_Difficulty` and all 75 movies seen. A skip at tick 40 reaches Sign In at tick 41 with the player kept. |
| 2. Live, Showdown | ✅ The input played through `test_script`, minimized:<br>**Options.** The screen showed the three nails at 0.167 (ScummVM's default 192). The music nail was dragged by its head to 0.699 (volume 233), and the sounds nail past its left end (179, with the splat). Both volumes were in the config file afterwards.<br>**Credits.** The TLC logo and text rolled while Shaggy and Scooby said `Credits.1100A2_`'s four lines; Escape went to Sign In. |
| 3. Build and diff | ✅ Scooby-only build: 19 files, 0 errors, 0 warnings. The exit, click, inventory, hint, profile, menu and Sign In checks are identical to WP-028's run, and the room check to WP-020's (69 and 53 rooms). Fork commit [`7e184fcf1a`](https://github.com/barefootbetters/scummvm/commit/7e184fcf1a) stages its 10 files by name, inside `engines/scooby/`, and is pushed. |

**Deviations and gaps:**

- **No room music.** The original plays each room's music group, or a named clip, on entry. The fork has none yet, so:
  - Options' music slider sets the volume without replaying the room's music;
  - Credits' parts don't fade the music before their scenes.
- **Volumes are ScummVM's**, set to the original's gain × 256 and saved as each knob is let go. The original writes `Scooby.ini` when the room is left. A ScummVM volume under 179 puts the knob at its line's start; dragging can't go below 179, as the original can't go below 0.7.
- **Grabbing a knob** happens on the click that lands on it, through the hit walk. The original reads the sprite's `+0x08` flag on its update.
- **Credits' end of game** runs just before the exit to Sign In, not as the room is left.
- **Credits' entry scene** is started by the class; the base entry's scene (`+0x78`) isn't modelled for other rooms.
- **The skip** is Escape, Space or a click, standing in for input slots 5 and 4.

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

1. [x] Both discs match an independent reference line for line:
   - the markers, the sliders' ends and the starting knobs;
   - six drags per slider, with the volumes and samples;
   - each villain's movie;
   - the roll's parts, ticks and ending;
   - a skip.
2. [x] Live, in Showdown:
   - the options screen;
   - a music knob dragged and a sound-effects knob dragged off its end,
     with the volumes saved;
   - the credits rolling with the gang's lines, and a skip to Sign In.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#options-and-credits-wp-030):
  Options, the slider and Credits.
