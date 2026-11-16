---
layout: default
title: "WP-061: Phantom's room of doors and its Jester"
---

# WP-061: Phantom's room of doors and its Jester: the locked door, the balls and his clue (Gen 1)

**Status:** 🚧 In progress (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-060 ✅ (the crest, `PlaqueSeen`), WP-057 ✅ (Phantom's story values), WP-031 ✅ (clues and Big Head), WP-036 ✅ (a suspect's clue and thanks)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-061-2026-11-16](../reference/pre-flight-WP-061-2026-11-16.md)

---

## Result (2026-11-16)

Pending: the check against the reference, the live run and the regression.

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
- **The Jester's logic** is a member of the room's class, and other rooms
  that place him carry it too:
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

1. [ ] Both titles match an independent reference line for line:
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
2. [ ] Live, in Phantom: the locked door; the Jester's talk and his
   introduction on Big Head.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-room-of-doors-its-jester-and-phantoms-clues-wp-061):
  the room of doors, the Jester and Phantom's clues.
