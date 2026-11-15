---
layout: default
title: "WP-042: Showdown's hotel"
---

# WP-042: Showdown's hotel: the hall door, and the nickel by the window (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-040 ✅ (`GraveLocation`, which picks the window's movie), WP-023 ✅ (requires objects and the toolbar), WP-022 ✅ (movies), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-042-2026-11-15](../reference/pre-flight-WP-042-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
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
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the hall's door opened by Fred;
   - the hotel room's first visit out of the window and back, then the
     nickel in the toolbar.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for what the hotel sets. The fork
   diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-hotel-wp-042): the hotel.
