---
layout: default
title: "WP-061: Phantom's room of doors and its Jester"
---

# WP-061: Phantom's room of doors and its Jester: the locked door, the balls and his clue (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-060 ✅ (the crest, `PlaqueSeen`), WP-057 ✅ (Phantom's story values), WP-031 ✅ (clues and Big Head), WP-036 ✅ (a suspect's clue and thanks)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-061-2026-11-16](../reference/pre-flight-WP-061-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp062_ref.py`: WP-060's, plus the room of doors, its Jester and Phantom's clues, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art, and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 10 room-of-doors lines on Phantom (42 in all), and one on Showdown, which has no room of doors (218 in all).

The first run differed on two lines, both the check's own: it called the code under test inside the same `format()` that printed its results, and C++ leaves argument order open. It also logged eight warnings from the engine's code: the Jester's thanks is an exit with no object, and the room asked `object.ini` for an empty section. The room now passes such an exit on. The second run matched all 42 lines on Phantom and all 218 on Showdown, with no warnings.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **Clues.** The Jester's own is one of his three; as the villain, he gives a red herring not his own.
   - **Placements.** Until the duster is used, neither the dining room's door nor the Jester. Used: the door at depth −1000 and the Jester. Each walk-in by the room left.
   - **Jane's crying** and a scream on entry.
   - **The ways out:**
     - to the armory, `140A_`, `140A1_` and `140A2_` all seen;
     - to the throne room, first `160D1_`, with the crying stopped, then `140B_`, `140B1_` and `140B2_`;
     - to the dining room, `140C_` and `140C1_`;
     - back again, no scream.
   - **The locked door:** Velma tries it at tick 1, `Velma_Door_Locked` playing; at tick 160, `130B_` holds input.
   - **Idle chatter:** none while Jane cries; then all five.
   - **The Jester:** the first click meets him, with `220B_` on Big Head back here; later clicks give one of his lines. With the red ball found, he takes it (`TAKES_RED`) and talks `220D2_`, `220D4_`, `220D1_`, `220D3_`. With the plaque seen, `220E_`, `220E2_`, `220E4_`, `220E1_`, `220E3_`, `220E5_`, `220E6_` follow.
   - **All three balls:** `Global.Jester.Clue_`, his clue, then `Global.Thank_You_` and the suspects. With the crest solved, the room again through movie 57.
   - **The profile:** a new game's `Crying=Yes`.
   - Showdown prints that it has no room of doors.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The locked door:** the way to the dining room kept the gang; Velma tried the door with `Velma_Door_Locked`, then said `130B_`.
   - **The Jester,** from a profile with the duster used and the red ball found: he talked through the crest's four digits, and a click introduced him on Big Head.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms).
   - **Showdown:** its other checks are identical to WP-060's run but for the imported clue name, which varies by run, so `giveClue`'s change to tables per title leaves Showdown as it was.
   - **Phantom:** its checks differ only by the room of doors' three new profile keys and the drawbridge's random keys.
   - Fork commit [`548d197118`](https://github.com/barefootbetters/scummvm/commit/548d197118) (8 files staged by name) is pushed.

**Deviations and gaps:**

- **The tick clock's restart** (`0x437540`) when Velma tries the door isn't kept, as in WP-057.
- **The Jester in the other three rooms that carry him** (the royal gallery, the well, the balcony's door) waits for their classes; his logic is ready for them.

**Found on the way:**

- **Phantom's clue rule is Showdown's** with its own tables, and two red herrings a suspect where Showdown has one.
- **The Jester talks the gang through the crest's order,** digit by digit, once the first ball is taken.
- **Jane's fourth scream is stopped but never played** here either.

---

## Goal

Port Phantom's room of doors, `ROOM_P11_Room_Of_Doors`, the fourth step in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now it had the base class:
- the dining room's door opened at once;
- Jane cried for good;
- the Jester stood there from the start and did nothing.

## Background

The room of doors ([scooby-exe](../formats/scooby-exe.md#phantoms-room-of-doors-its-jester-and-phantoms-clues-wp-061)):
- **The dining room's door** is locked until the duster has been used;
  Velma tries it.
- **Jane cries** until the gang goes to the throne room.
- **The Jester's logic** is a member of the room's class, and three
  other rooms' classes carry it too:
  - he takes each ball the gang finds;
  - he talks them through the crest's order;
  - he introduces himself once;
  - once all three balls are found, he gives his clue.

His clue needs Phantom's clue tables. The fork's clue giver had only
Showdown's.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`RoomOfDoorsRoom`:** the placements, the walk-ins, Jane's crying, the
  ways out and their scenes, the locked door, the idle chatter, the
  profile.
- **`JesterControl`:** the balls, the talk, the clue and thanks, and a
  click's introduction, talk, lines, or the room again through a movie.
- **`giveClue`:** each title's tables.
- **A `script` level 3 check** against an independent reference.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the class;
   - Phantom's clues, the Jester's own and as the villain;
   - the placements without and with the duster used, and the walk-ins;
   - Jane's crying and the ways out's scenes;
   - the locked door with Velma, with its ticks;
   - the idle chatter;
   - the Jester's introduction and lines;
   - his talk through the crest, without and with the plaque seen;
   - his clue and the thanks;
   - the crest solved;
   - the profile.

   Showdown prints that it has no room of doors.
2. [x] Live, in Phantom: the locked door; the Jester's talk and his
   introduction on Big Head.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-room-of-doors-its-jester-and-phantoms-clues-wp-061):
  the room of doors, the Jester and Phantom's clues.
