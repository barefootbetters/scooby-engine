---
layout: default
title: "WP-032: The music's fade"
---

# WP-032: The music's fades around scenes and room loads (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-019 ✅ (sound), WP-029 ✅ (room music and openings), WP-031 ✅ (Big Head)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-032-2026-11-14](../reference/pre-flight-WP-032-2026-11-14.md)

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

1. [ ] Both discs match an independent reference line for line:
   - each fade's steps, by tick;
   - a fade cut short, and one at its target;
   - the cancel;
   - the music channel's volume at 90% and 100%;
   - the fade each room event starts;
   - the title;
   - Big Head's opening tick and its fade.
2. [ ] Live, in Showdown:
   - Town Center's opening fading the music down and back up;
   - Big Head starting 100 ticks in and fading down;
   - the credits' opening playing 100 ticks in.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged, but for the credits' opening in the setup
   check. The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-musics-fade-wp-032): the fade.
