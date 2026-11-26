---
layout: default
title: "WP-069: Phantom's two arenas"
---

# WP-069: Phantom's two arenas: the sharp shears, Brad's rise and the mirror (Gen 1)

**Status:** ✅ Done (2026-11-17)
**Phase:** 4 (game logic)
**Depends on:** WP-062 ✅ (the throne room, between the arenas), WP-067 ✅ (the shield), WP-061 ✅ (a suspect's clue and the thanks; Big Head), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-069-2026-11-17](../reference/pre-flight-WP-069-2026-11-17.md)

---

## Result (2026-11-17)

The reference is `wp070_ref.py`: WP-068's, plus the two arenas, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art, and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 8 arena lines on Phantom (102 in all), and one on Showdown, which has no arenas (226 in all).

The first full run matched all 226 lines on Showdown, and all but the rise and the pile on Phantom. Both were faults in the check, not the class. The rise loop never ran: it started with the room the first arena's block had asked for still set. One pile click was swallowed by a rattle, as the game does too, since a rattle that lands while a click plays takes over its event. The check now clears the request and seeds the random source before each click. With both fixed, all 102 lines match.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **The classes:** each arena gets its own.
   - **The first arena:** Velma walks in from the throne room and from the second arena; back from the stone's movie, the toolbar opens. The arrow on the stone cycles `170XB_`, `170A_`, `170A1_`, `170A2_`; the rusty shears play movie 40 back into the room, out of their slot with the arrow back, and the sharp shears come on leaving. Hotspot 3 says `170X_` without holding input.
   - **The second arena's placements:** not won, the pile is a clickable and Brad is in it (`OBJ_BRAD_H`); won, `OBJ_BRAD` and no pile; the mirror at depth -480 until had; the pole on levels 1 and 2 and the arena's shield once the shield is used.
   - **The rise:** on the first visit Brad is hidden and the pile's first click is the room's own. After the opening's fifth line he rises (`ANIM_BRAD_HRISE`), the scene waits while he does, and his sixth line follows. The opening over, the party goes into his game.
   - **The pile:** the player's click leads to `ROOM_Brad_SPOOKY`, `SPOOKIER` or `SPOOKTACULAR` by level; over 6000 ticks it rattles a few times and never changes the room.
   - **The shield:** Big Head through movie 29, `180E_` on `BIG_HEAD_BG_P14` and back. Back, Brad stands 50 aside and Velma takes the mirror into the toolbar.
   - **His clue:** won, `180B_`, his clue, then `Global.Thank_You_` into the suspects and clues.
   - **Idles:** hotspot 2's line on its B; Brad's three idle lines and the chatter once won.
   - Showdown prints that it has no arenas.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The rusty shears** on the stone: movie 40, then the sharp shears in the slot.
   - **The first visit to the second arena:** the opening's eight lines, Brad's head out of the pile after the fifth, and on into `ROOM_Brad_SPOOKY`.
   - **The shield** on Brad: movie 29, Big Head's two lines, back to the arena, and Velma takes the mirror into the toolbar.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). The other checks are identical to WP-068's run, except for random keys that vary by run: the drawbridge's on Phantom, and on Showdown the first clue found in the profile check's import.
   - Fork commit [`eb9f997ae5`](https://github.com/barefootbetters/scummvm/commit/eb9f997ae5) (10 files staged by name) is pushed.

**Deviations and gaps:**

- **The tick clock's restart** (`0x437540`) when Brad rises isn't kept, as in WP-057.
- **The fork's queued click** is taken while the clickable isn't playing; the original tests `+0x70` and its pending click (`+0x7E`).
- **Brad's game** (`0x41E9E0`) is the next packet's, WP-070. The pile leads into its rooms, which still have the base class.
- **The live run's Big Head** logged that it couldn't set `ANIM_BIG_HEAD_CLUES_GUMMY10`. The live harness's base profile names Showdown's `GUMMY` as the villain, which Phantom doesn't have. The arena isn't involved.

**Found on the way:**

- **The party never chooses Brad's game the first time:** at the end of the opening the room queues a click on the pile as the player's, and the event takes them in.
- **The rattle can swallow a click:** a rattle while the player's click plays marks the next event as the room's own, so that click does nothing.
- **Two save/load rows** for the kitchen and Ewan's quiz (WP-065, WP-066) had been filed under the newest room's table in [scooby-exe](../formats/scooby-exe.md); they are back in their own.

---

## Goal

Port Phantom's two arenas, `ROOM_P09_Arena1` and `ROOM_P14_Arena2`, next
in [its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now both had the base class: the rusty shears did nothing on the
stone, Brad stood in plain sight, the pile was an ordinary clickable, and
the shield and mirror did nothing.

## Background

The arenas ([scooby-exe](../formats/scooby-exe.md#phantoms-two-arenas-wp-069)):
- **The grindstone** sharpens the rusty shears.
- **Brad** hides in the armour pile until his game is won, and rises
  during the opening; the pile leads to his game.
- **The shield,** given him on Big Head, frees the mirror for Velma.

The audit groups Brad's game (`0x41E9E0`, three levels) with the arenas;
it is a set piece of its own, split off as WP-070.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`Arena1Room`:** the stone, the shears, the walk-ins and the toolbar.
- **`Arena2Room`:** the placements; the rise before the scene player; the
  pile's queued clicks into Brad's game; his clue and the thanks; the
  shield and the mirror; his idle lines.
- **Shared:** queued clicks on clickables; the hook before the scene
  player; Big Head through a movie.
- **A `script` level 3 check** against an independent reference, on both
  titles.

**Out of scope:** Brad's game (WP-070).

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes and the second arena's placements;
   - the first arena's walk-ins, the stone and the shears;
   - the rise, with the scene held, and on into Brad's game;
   - the pile by level, and its rattles;
   - the shield, Big Head and the mirror;
   - his clue and the thanks; the idle lines.

   Showdown prints that it has no arenas, as its reference does.
2. [x] Live, in Phantom: the shears; the rise into his game; the shield
   and the mirror.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for random keys. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-two-arenas-wp-069):
  the two arenas and queued clicks.
