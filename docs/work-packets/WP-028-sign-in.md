---
layout: default
title: "WP-028: Sign In and the new game"
---

# WP-028: Sign In, players and the new game (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-026 ✅ (the profile and saves), WP-027 ✅ (room classes, the title and the level select)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-028-2026-11-14](../reference/pre-flight-WP-028-2026-11-14.md)

---

## Goal

Make Sign In work, as the original's does:
- the player types a name, or picks a saved player;
- a saved player's profile loads and the game goes back to where they
  were;
- a new name starts a new game at the level select.

The new game sets the story's random values.

## Background

WP-027 leads the title and New Mystery to a Sign In room that does
nothing. The original's Sign In class (details in
[scooby-exe](../formats/scooby-exe.md#sign-in-and-the-new-game-wp-028)):
- **Players.** It lists the players: one `<name>.sav` profile each.
- **Typing.** It takes letters from the keyboard or from buttons, and
  centres the name in its own font.
- **Leaving.** When Shaggy's line ends, it either loads the player's
  profile or starts a new game.
- **The new game** resets the game. In Showdown it also draws the
  villain, the artifact, the grave, the strong box and the levers.

ScummVM has save slots, not files named after players. WP-026 made a
save hold the profile, so here a player is a save whose description is
the player's name.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SignInRoom`.** Entry, placements, tick, keys, the list and its
  arrows, the buttons, Play, Quit, Delete, and the exit.
- **Players.** The saves whose description is a player's name (1–10 of
  `A`–`Z`, `0`–`9` and space), by name. A new player takes the first free
  slot. The signed-in player's save is written as each game room starts.
  Loading a player's save signs them in.
- **The new game:**
  - the level, the movies, the exits, the clickables, every room class's
    reset and the inventory;
  - `StartRoom` `ROOM_Difficulty`;
  - Showdown's story values into the profile.
- **Key dispatch** to the room's class, and `type` and `key` steps for
  `test_script`.
- **A `script` level 3 check:** where the fields and buttons are, how
  names lay out, what keys and buttons type, the prompt's and the idle
  line's ticks, the list's rows, hover, arrows and delete, and where Play
  and Quit go.

**Out of scope:**

- **Phantom's story values** (its game vtable `+0x4C`): not traced.
- **The story rooms** that read the values.
- **When the original writes the profile** (game vtable `+0x54`).
- **Options and Credits.**

## Exit criteria

1. [ ] Both discs match an independent reference line for line:
   - the fields' places, the letter buttons, the timers;
   - names laid out with the font's widths;
   - keys and buttons typing;
   - the list's hover, arrows and delete;
   - a saved player loading;
   - a new player's new game and Showdown's story values;
   - Quit.
2. [ ] Live, in Showdown:
   - a typed name, a button letter and backspace;
   - Play, the level select and the game, with the player saved;
   - the player in the list, under the mouse and loaded by two clicks;
   - Delete.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#sign-in-and-the-new-game-wp-028):
  Sign In and the new game.
