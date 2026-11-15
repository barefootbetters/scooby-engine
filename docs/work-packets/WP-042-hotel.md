---
layout: default
title: "WP-042: Showdown's hotel"
---

# WP-042: Showdown's hotel: the hall door, and the nickel by the window (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-040 ✅ (`GraveLocation`, which picks the window's movie), WP-023 ✅ (requires objects and the toolbar), WP-022 ✅ (movies), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-042-2026-11-15](../reference/pre-flight-WP-042-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp042_ref.py`: WP-041's, plus the hotel, written from the trace before the engine ran. It reads the placements and step counts from the art and whether each opening has a first line from the sound archives' indexes, and never runs the engine. At `script` level 3 the chase check now logs 114 lines on Showdown, the earlier 107 and 7 for the hotel; the reference prints the same 114, none different. On Phantom both print the one line saying there is no chase.

The first run differed on two lines, both the check's own doing. The door was clicked before any tick had let Fred finish walking in, and hotspot 4 was left stopped on step 11, so its scene started again and kept `410X_` from starting. With one tick before the door and hotspot 4 put back to step 0, all 114 match.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The hall.** The door a requires object at depth 1, hotspot 2 at -100, the chandelier at -1; the openings `Hotel_Hall.1100BE3_`, then `1100B2_` with `SecondEntrance`, then `1100BE3_` played; music at 95%. Daphne walks in from the saloon, Fred from the room, both at their depth; once the nickel is used, there's no chandelier.<br>**The door.** Fred opens it with OBJ_FRED_P17_OPEN_DOOR, `HotelHallDoor` set, and it is still open on a return. The chandelier says `400A_`, `400A2_`, `400A3_`, `400A_`, not held. Hotspot 1 on A's step 6 and B's step 4 scares Daphne with `Hotel_Hall.Scream_`; on A's step 5, nothing.<br>**The hotel room.** The first visit: `Hotel_Room.280C_`, `LookedOutAuto`, music at 90%. Then the window by itself, through movie 19 (`GraveLocation` 4) on tick 2. Back from it: `410C_`, `410C2_`, `410C_`, each window with no scene; with the brick, no opening.<br>**The nickel.** A requires object; clicked, input is held. Daphne starts GRAB_COIN (31 steps) on tick 1, the nickel is gone on tick 43, and on tick 94 it is in the toolbar with `410A_` blocking. Hidden on a return; had when the gang leaves mid pick-up.<br>**The hotspots.** Hotspot 4 on step 11 plays its scene; hotspot 2 on C's step 18 scares Daphne, and clicked in state C plays `410X_`. Both keys read back, and a reset clears them. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**The hall.** Clicking the door played `Hotel_Hall.Unlocked_Door`, Fred opened it and it stayed open. Clicking hotspot 1 played its animation, and on its step 6 `Hotel_Hall.Scream_` played.<br>**The hotel room.** `Hotel_Room.280C_` played; skipped, the room took the window by itself, movie 19 played (38 frames), and the room came back with `410C_`. The nickel clicked: Daphne picked it up, `410A_` played, and the nickel was in the toolbar. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Phantom's earlier checks are identical to WP-041's run. Showdown's differ only where the hotel now sets things: the setup check's two openings, and the profile check's `SecondEntrance` and `LookedOutAuto`, one key more each way; the Sheriff's first clue is random. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`e949d3437c`](https://github.com/barefootbetters/scummvm/commit/e949d3437c) stages its 9 files by name and is pushed. |

**Deviations and gaps:**

- **Walk-ins from the left or right now keep the character's depth,** as `0x405F60` and `0x405FA0` do. The fork had them going 50 behind, like a walk from U. No earlier room's check walked anyone in from the side, so nothing else changed.

---

## Goal

Make Showdown's two hotel rooms play as the original does. Until now they
had the base class: the hall's door stayed shut, the hotel room had no
opening, and its nickel did nothing.

## Background

The hotel ([scooby-exe](../formats/scooby-exe.md#the-hotel-wp-042)) has
two rooms:
- **The hall:** Fred opens the locked door. The chandelier has three
  lines, and a hotspot makes Daphne scream. The second visit has an
  opening of its own, once.
- **The hotel room:** the first visit ends with a look out of the window,
  which is a way out into the room itself through a movie chosen by
  `GraveLocation`. Back from it, the gang comments, alternating, until
  they have the brick. Daphne picks up a buffalo nickel. Two hotspots
  have a scene and a fright.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`HotelHallRoom`:** the door and `HotelHallDoor`; the chandelier's
  lines; hotspot 1's scream; the two openings and `SecondEntrance`; the
  walk-ins and the music.
- **`HotelRoomRoom`:** the openings and the window by itself
  (`LookedOutAuto`); the window's movie and the first way out's scene;
  the nickel; the two hotspots; the music.
- **The music's volume** (`0x40AA10`'s second argument), and walk-ins
  from the left or right keeping the character's depth.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The saloon,** ROOM_P12_Saloon, the hall's other way out.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the classes;
   - the hall's placements, its openings over three visits, the music,
     and who walks in from where;
   - the door opened by Fred, kept on a return; the chandelier's lines in
     turn; hotspot 1's scream on the right steps only;
   - the hotel room's first visit, the window by itself and its movie,
     the comments back from it in turn, none with the brick;
   - the nickel picked up, with its ticks, hidden on a return, and had
     when the gang leaves before Daphne finishes;
   - the hotspots and both keys.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the hall's door opened by Fred;
   - the hotel room's first visit out of the window and back, then the
     nickel in the toolbar.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for what the hotel sets. The fork
   diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-hotel-wp-042): the hotel.
