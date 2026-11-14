---
layout: default
title: "WP-026: The player profile and saves"
---

# WP-026: The player profile, and ScummVM saves that hold it (Gen 1)

**Status:** 🚧 In progress
**Phase:** 4 (game logic: saves)
**Depends on:** WP-020 ✅ (exits), WP-021 ✅ (clickables), WP-022 ✅ (movies), WP-023 ✅ and WP-024 ✅ (the inventory, snacks, suspects)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-026-2026-11-14](../reference/pre-flight-WP-026-2026-11-14.md)

---

## Goal

Save and load a Gen 1 game in ScummVM, keeping the original's own record
of a game. That record is the player's profile: an INI file the game
writes as it plays.

## Background

The original has no save slots (details in
[scooby-exe](../formats/scooby-exe.md#the-player-profile-wp-026)):

- **Choosing a profile.** The Sign In room picks a player, and that
  player's `<name>.sav` becomes the profile.
- **The sections.**
  - `Game`: the start room, the movies seen, the suspects met, and the
    story's flags.
  - `Exits`: the exits taken, written as each is taken.
  - `Clickables`: each object's state, written as a room is left.
  - `Inventory`.
- **Loading** reads the profile and goes to its `StartRoom`.

The fork kept these as session state (WP-020 to WP-024), so they were lost
when the game closed.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **Building and applying the profile** (`profile.cpp`).
  - Build: the original's keys, from the start room, movies, exits,
    clickables, the inventory and the suspects met.
  - Apply: read them back by the original's rules, then go to
    `StartRoom`.
  - Keys the fork doesn't model, such as the story's flags, are kept as
    read.
- **ScummVM saves.**
  - `saveGameStream()` / `loadGameStream()` hold the profile's text.
  - The metaengine lists, deletes and loads saves at startup, in the
    extended format with thumbnails.
  - Saving is refused while a scene or an exit plays.
- **`StartRoom`** follows the original: the last room that isn't a menu.
- **Testing aids.** A console `profile` command, and `save N` / `load N`
  steps for `test_script`.
- **A `script` level 3 check.**
  - A round trip: a state of every kind, written, read into a new game and
    written again.
  - An import: an original-format profile read in and written out again.

**Out of scope:**

- The Sign In room and one profile per player name; ScummVM's slots stand
  in for them.
- The story flags' meaning, and the per-room classes' own keys. Those are
  kept as read but not used.
- Exporting a profile to a `.sav` file on disk.

## Exit criteria

1. [ ] On both discs, the profile the check writes matches an independent
   reference key for key, and reading it back writes the same text.
2. [ ] An original-format profile matches the reference after reading and
   writing. That covers CRLF lines, a lowercase `yes`, `TRUE`/`on` exits,
   an empty `Snacks`, `Nothing` slots and story keys.
3. [ ] Live, in Showdown:
   - a save after a pick-up, then a walk to another room, and a load
     brings the room and the item back;
   - starting with `save_slot` loads it too.
4. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks are
   unchanged line for line. The fork diff stays inside `engines/scooby/`,
   staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): the profile's sections and rules.
- [Integration §8](../02-SCUMMVM-INTEGRATION.md#8-save--load): the
  implementation notes.
