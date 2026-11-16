---
layout: default
title: "WP-051: Showdown's saloon and Artie"
---

# WP-051: Showdown's saloon and Artie: the gag, the keys and the chains (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-050 ✅ (the whistle puzzle), WP-031 ✅ (suspects met), WP-021 ✅ (clickables), WP-019 ✅ (sound and lip sync)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-051-2026-11-15](../reference/pre-flight-WP-051-2026-11-15.md)

---

## Goal

Make Showdown's saloon, ROOM_P12_Saloon, and Artie's chains, ROOM_Artie,
play as the original does. Until now both had the base class:
- Artie was neither gagged nor chained;
- the hotspots hid no keys;
- nothing kept the gang in the saloon;
- the piano, the bull and the pump handle did nothing of their own.

## Background

The saloon ([scooby-exe](../formats/scooby-exe.md#the-saloon-and-artie-wp-051)):
- **Artie** is gagged and in three chains. Clicked, Velma takes the gag off.
- **Three keys** hide behind three of six hotspots, drawn at a new game.
  Each key found and clicked takes a chain off in ROOM_Artie.
- **Until he is free,** the gang won't leave. Free, he gives his clue.
- **The piano** stops the music while it plays. **The bull** takes the
  Buffalo nickel, and the pump handle falls from the chandelier.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SaloonRoom`:**
  - the placements under its own buffer sprite;
  - the gag, the keys and the exits it keeps;
  - Artie's clue;
  - the piano, the bull, the pump handle and the moans;
  - its keys in the profile.
- **`ArtieRoom`:** a chain off, and back.
- **The pieces they need:**
  - a character's looping special state (0xE) and its set;
  - a class's own buffer sprite in the room loader.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the classes;
   - the placements on entry, Artie gagged, and the class's values;
   - the exits kept while gagged;
   - the gag, with its ticks;
   - the six hotspots, the keys behind three;
   - the exits kept while chained, each key to ROOM_Artie and back, the
     chains, Artie's clue, GIVES and the thanks;
   - the piano and the music;
   - the bull and the pump handle;
   - the moans and the idle line;
   - the stage's snacks;
   - the keys saved and read.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form: the gag,
   a key found and used, ROOM_Artie and back.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-saloon-and-artie-wp-051): the
  saloon and Artie's chains.
