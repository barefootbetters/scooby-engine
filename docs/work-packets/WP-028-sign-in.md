---
layout: default
title: "WP-028: Sign In and the new game"
---

# WP-028: Sign In, players and the new game (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-026 ✅ (the profile and saves), WP-027 ✅ (room classes, the title and the level select)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-028-2026-11-14](../reference/pre-flight-WP-028-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp028_ref.py`, written from the trace. It reads the art and the sound indexes through the repo's probes, and never runs the engine. At `script` level 3 the engine drives Sign In through its class and logs 41 lines; the reference prints the same 41 on each title, none different.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ On both titles:<br>**The room.** The list and the typed field are where their placements say (Showdown 184,210 and 192,153; Phantom 118,187 and 157,130). The 36 letter buttons type `M123456789ABCDEFGHIJKL0NOPQRSTUVWXYZ` in placement order. Typing starts on tick 61, the prompt on tick 90, and the idle line on tick 1080.<br>**Names.** Five names lay out letter by letter at the font's first-cel widths, centred in 240 pixels.<br>**Typing.** Keys and buttons: case, the 10-letter limit, no leading or double space, backspace, and Enter playing. Keys before the prompt are dropped.<br>**The list.** Hover holds strictly inside each row, the arrows show and hide over 14 clicks, and Delete removes the scrolled-to last player.<br>**Leaving.** A saved player clicked twice loads their slot. A new player gets a new game at the level select, with Showdown's story values (Phantom: none). Quit goes to `ROOM_Quit`. |
| 2. Live, Showdown | ✅ The input played through `test_script`, minimized, with keys sent as key events:<br>**A new player.** `scooby` typed, the `1` button and backspace showed `SCOOBY` centred. Play: Shaggy's 5.4 s line, a new game, slot 1, the level select. Spooky played movie 1 and opened Town Center, and `SCOOBY` was saved in slot 1.<br>**The saved player.** The next start listed `SCOOBY`, lit up the name under the mouse, and loaded Town Center on two clicks.<br>**Delete.** A third start selected `SCOOBY` and Delete removed the save. |
| 3. Build and diff | ✅ Scooby-only build: 18 files, 0 errors, 0 warnings. The exit, click, inventory, hint, profile (with the WP-026 import) and menu checks are identical to WP-027's run. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`c575e2625f`](https://github.com/barefootbetters/scummvm/commit/c575e2625f) stages its 12 files by name, inside `engines/scooby/`, and is pushed. |

**Deviations and gaps:**

- **A player is a save** whose description is the name. It is written as each game room starts; when the original writes `<name>.sav` (game vtable `+0x54`) isn't traced. Saves named otherwise, and the autosave, aren't players. Loading a player's save from ScummVM's menus signs them in.
- **WP-026's saves never showed in ScummVM's lists.** The metaengine left out `kSimpleSavesNames`, so the lists looked for `showdown.sNN` while the engine wrote `showdown.NNN`. WP-026's live test loaded by slot number and never listed. Fixed here, since Sign In's list needs it.
- **Menus don't autosave.** ScummVM autosaves before every load, which from Sign In put a blank new game over the last autosave.
- **Stand-in keys.** Delete is the original's input slot 18; its key isn't traced. Skip is slot 5, as in WP-027: Escape, Space before typing starts, or a click while Shaggy's leaving line plays. The flag `0x475F00` that also gates the skip isn't modelled.
- **The random values** come from ScummVM's random source, not `rand()`: same ranges, different draws.
- **Phantom's new game** runs the shared reset only; its story values (`+0x4C`) aren't traced.

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

1. [x] Both discs match an independent reference line for line:
   - the fields' places, the letter buttons, the timers;
   - names laid out with the font's widths;
   - keys and buttons typing;
   - the list's hover, arrows and delete;
   - a saved player loading;
   - a new player's new game and Showdown's story values;
   - Quit.
2. [x] Live, in Showdown:
   - a typed name, a button letter and backspace;
   - Play, the level select and the game, with the player saved;
   - the player in the list, under the mouse and loaded by two clicks;
   - Delete.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#sign-in-and-the-new-game-wp-028):
  Sign In and the new game.
