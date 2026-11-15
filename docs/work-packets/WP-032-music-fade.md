---
layout: default
title: "WP-032: The music's fade"
---

# WP-032: The music's fades around scenes and room loads (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic)
**Depends on:** WP-019 ✅ (sound), WP-029 ✅ (room music and openings), WP-031 ✅ (Big Head)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-032-2026-11-14](../reference/pre-flight-WP-032-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp032_ref.py` with `wp032_fade.py`, written from the trace; it reads the sound indexes through the repo's probe and never runs the engine. At `script` level 3 the engine drives the fade through `Sound`, the rooms and Big Head and logs 10 lines; the reference prints the same 10 on each title, none different.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ On both titles:<br>**The steps.** Down to 90 every 2 ticks: 99 on tick 2, 90 on tick 20. Up to 100 every 4: 91 on tick 4, 100 on tick 40. A fade down cut short at 96 by up every 3 reaches 100 on tick 12. A fade down at 90 stops on its first step. The cancel leaves 100% and no fade.<br>**The channel.** The music clip's volume of 255 plays at 229 at 90%, and at 255 again after the cancel.<br>**The rooms.** A load fades up 100/3, a scene start down 90/2, a scene end up 100/4. The title leaves 100%. Big Head's opening starts on tick 101 with line 1, and the music reaches 90% on tick 120. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, with the audio channel logged:<br>**Town Center.** Its opening started on tick 100 and turned the music down; its end after two lines brought it back up.<br>**The ending.** Big Head's scene started after its delay and turned the music down; it came back up as the credits loaded.<br>**The credits.** Their opening, `Credits.1100A2_`, started on tick 100 with the music going down, as the room's opening. |
| 3. Build and diff | ✅ Scooby-only build: 23 files, 0 errors, 0 warnings. Every earlier check is identical to the run before, except the setup check's one credits line, which now has its opening (`'Credits.1100A2_', held 1, starts 100`; Phantom `'Credits.10002_'`). The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`819f0599ad`](https://github.com/barefootbetters/scummvm/commit/819f0599ad), on `1f002172c4`, stages its 10 files by name, inside `engines/scooby/`, and is pushed. |

**Deviations and gaps:**

- **The volume curve.** The original hands percent × gain to its DirectSound driver, which converts it to the buffer's attenuation (not traced); the fork scales the mixer channel linearly, so 90% is a gentle dip either way, but not the same one.
- **Two story rooms' cancels** (`0x41936E`, `0x422478`) aren't modelled; `Sound::cancelMusicFade()` is there for them.
- **Big Head's and the credits' first scenes** now start 100 ticks in. WP-030 and WP-031 started them at once.

---

## Goal

Turn the music down under dialogue and back up afterwards, as the original
does, and bring it up as each room loads. WP-029 left this as a gap: the
fork's music stayed level.

## Background

The original keeps one fade for its music file
([scooby-exe](../formats/scooby-exe.md#the-musics-fade-wp-032)):
- **Each game tick** the music moves one percent toward a target, every so
  many ticks.
- **Scenes:** a scene starting fades to 90%; a scene ending (played out or
  skipped) fades back to 100%.
- **Room loads** fade up to 100%.
- **The title** sets 100% at once.

Tracing it also showed that Big Head's and the credits' first scenes are
their rooms' openings, which the base room starts 100 ticks after entry.
WP-030 and WP-031 started them at once.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **The fade in `Sound`:** start it, step it, cancel it, and apply the
  percent to the music channel (a music clip starts at the percent now).
- **Where it starts:**
  - a scene starting (`RoomScript::startScene`) and ending
    (`RoomScript::endScene`);
  - a room's load, after its entry;
  - the title's cancel;
  - Big Head's opening;
  - a step every game tick.
- **Big Head** waits the opening's 100 ticks. The credits' first scene is
  the room's opening, in the setup table.
- **A `script` level 3 check** against an independent reference.

**Out of scope:**

- **Two story rooms' cancels** (`0x41936E`, `0x422478`). The API is
  `Sound::cancelMusicFade()`.

## Exit criteria

1. [x] Both discs match an independent reference line for line:
   - each fade's steps, by tick;
   - a fade cut short, and one at its target;
   - the cancel;
   - the music channel's volume at 90% and 100%;
   - the fade each room event starts;
   - the title;
   - Big Head's opening tick and its fade.
2. [x] Live, in Showdown:
   - Town Center's opening fading the music down and back up;
   - Big Head starting 100 ticks in and fading down;
   - the credits' opening playing 100 ticks in.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged, but for the credits' opening in the setup
   check. The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-musics-fade-wp-032): the fade.
