---
layout: default
title: "WP-062: Phantom's throne room"
---

# WP-062: Phantom's throne room: Jane's movie, the duster and the ruby (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-061 ✅ (the duster used, the balls), WP-057 ✅ (Phantom's story values), WP-023 ✅ (items on requires objects), WP-022 ✅ (movies), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-062-2026-11-16](../reference/pre-flight-WP-062-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp063_ref.py`: WP-061's, plus the throne room, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art, and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 7 throne-room lines on Phantom (49 in all), and one on Showdown, which has no throne room (219 in all).

The first run matched all 49 lines on Phantom and all 219 on Showdown, with no warnings. The live run then found one bug the check couldn't: the duster on Jane got the game's wrong-item line instead. The fork runs the game's update (`0x4098B0`) before the room's class, so the duster went back before the class looked. The class now takes that click, as the saloon's, the station's and the post office's take theirs. The check calls the class's click itself, so it didn't see the order; it matched again after the fix.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**Placements.** The throne is a clickable at depth −1 until the three balls are found, then the requires object at depth 0, hidden once the ruby is used. The Jester only with the ruby taken and the balls not all found. The way to the secret passage at depth −1, the other exits at −1000.<br>**Entry.** The first visit asks for movie 18 back to the room, sets `JaneMoviePlayed` and stops `Screaming`. Velma walks in from the room of doors, Daphne from the first arena, Shaggy from the second; nobody from the secret passage.<br>**Jane and the duster.** With the arrow, nothing. With the duster, `Throne_Room.160E_` holds input, the duster leaves its slot (so it counts as used), and the cursor is the arrow.<br>**The third hotspot.** Clicked, it shows step 1 of its A on ticks 4–6, and the five are scared (state `0x11`).<br>**The throne.** Clicked without the balls, `160X_`. With them: the arrow, `160X_`; the ruby, movie 9 back to the room, the ruby out of its slot and the arrow back; then the throne hidden.<br>**The profile:** a new game's `JaneMoviePlayed=No`, `Entrances=0`; `Yes` after a visit, and read back.<br>Showdown prints that it has no throne room. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized:<br>**The first visit:** movie 18 played (96 s), then the throne room again, with no second movie.<br>**The duster:** given to Jane from the toolbar, it left its slot and Jane said `160E_`. The first try hit the open toolbar in front of her; the second got the wrong-item line (above); the third, after the fix, worked.<br>**The ruby,** with the three balls found: on the throne, movie 9, then the room again with the throne hidden. The same spot then hovers the way to the secret passage behind it. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms).<br>**Showdown:** its other checks are identical to WP-061's run but for the imported clue name, which varies by run. So a clickable's call to the room with 0 leaves Showdown's classes as they were.<br>**Phantom:** its checks differ in three ways, all expected:<br>• the throne room's two new profile keys;<br>• the drawbridge's random keys;<br>• the setup check's throne room: a new game's first visit now asks for Jane's movie on its first tick, so its opening doesn't start there (`starts -1`, was 100).<br>Fork commit [`c9968b94a3`](https://github.com/barefootbetters/scummvm/commit/c9968b94a3) (8 files staged by name) is pushed. |

**Deviations and gaps:**

- **The first visit's base entry** (`0x40B920`) runs in the fork before the class asks for Jane's movie; the original skips it. The room is left at once for the movie, so nothing of that entry is seen.
- **The throne's clickable has no ghost** in the original (`0x408DC0` with 0); the fork's ghost chance is the room's, for every clickable. The room has no ghost, so only the random numbers drawn differ.
- **Jane's click with the duster** is taken by the class, as other classes take an item on a character, not read from the button coming up. The fork runs the game's update (`0x4098B0`) before the room's class, where the original runs it after; taking the click keeps the wrong-item line from answering first.

**Found on the way:**

- **A clickable's click calls the room with 0** (`0x401440`), where the fork passed 1. A room can't tell it from the arrow on a requires object. Fixed here; no Showdown class read the value for a clickable.
- **The throne is a clickable or a requires object** by whether the three balls are found, so the ruby can't be used before then.
- **`Entrances`** is saved and loaded but nothing else touches it.
- **The way to the secret passage is behind the throne.** At depth −1 it takes the clicks the hidden throne no longer does.

---

## Goal

Port Phantom's throne room, `ROOM_P10_Throne_Room`, the next room in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now it had the base class:
- Jane's movie never played;
- Jane ignored the duster, so the room of doors' dining room stayed
  locked;
- the throne took the ruby whatever the balls, and never played its movie.

## Background

The throne room ([scooby-exe](../formats/scooby-exe.md#phantoms-throne-room-wp-062)):
- **The first visit** plays Jane's movie (18).
- **Jane** takes the duster; once it is used, the room of doors' dining
  room opens ([WP-061](WP-061-room-of-doors.md)).
- **The throne** answers the ruby only once the three balls are found,
  with movie 9.
- **A hotspot** scares the gang.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`ThroneRoomRoom`:** Jane's movie, the walk-ins, the duster, the third
  hotspot, the throne and the profile keys.
- **`RoomScript`:** a clickable's click calls the room with 0, as
  `0x401440` does.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the placements without and with the ruby and the balls, and the ruby
     used;
   - the first visit's movie, the walk-ins and `Screaming`;
   - Jane with the arrow and with the duster;
   - the third hotspot's fright;
   - the throne clicked, with the arrow and with the ruby;
   - the profile keys.

   Showdown prints that it has no throne room, as its reference does.
2. [x] Live, in Phantom: the first visit's movie; the duster given to
   Jane; the ruby on the throne with the balls found.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile keys and Jane's
   movie. The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-throne-room-wp-062):
  the throne room, and a clickable's call to the room.
