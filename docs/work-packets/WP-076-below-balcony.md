---
layout: default
title: "WP-076: Phantom's below-the-balcony and its door"
---

# WP-076: Phantom's below-the-balcony and its door (Gen 1)

**Status:** 📝 Drafted (2026-11-19)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-023 ✅ (the inventory), WP-057 ✅ (Phantom's new game and first room), WP-072 ✅ (the royal gallery — the door's exit target and the shared Jester), WP-074 ✅ (the hedge maze and maze map — the `BALCONY` marker that reaches this room), WP-075 ✅ (the maze interior — the sibling rooms)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-076-2026-11-19](../reference/pre-flight-WP-076-2026-11-19.md)

---

## Goal

Port the last of Phantom's group-7 rooms, `ROOM_P27_Below_Balcony` and
`ROOM_P27A_Below_Balcony_Door`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 7, the maze — the entry pair landed in WP-074, the interior in WP-075).
Until now they have the base class: the rooms draw, but the vines do nothing,
the sharp shears cut nothing, and the ball below the balcony cannot be found or
taken.

## Background

Below the balcony
([scooby-exe](../formats/scooby-exe.md), to be extended by this WP) is the
pocket of the maze reached from the hedge maze and the maze map's `BALCONY`
marker (WP-074's `MazeMapRoom`, handler `0x42A9A0`, jumps straight to
`ROOM_P27_Below_Balcony`; the hedge maze's start-cell routing clears the
`MazeCenterFromGarden` flag on entry from here, which WP-074 already reads). It
is also where Phantom's ghost-spot skip sends the gang when they are scared in
the upstairs rooms (game vtable `+0x64`, `0x430DD0`: `ROOM_P27_Below_Balcony`
when the room is one of the Princess's bedroom, the veranda, the wizard's
library or bedroom, or the castle balcony).

Per the [Phantom audit](../reference/room-class-audit-phantom-2026-11-16.md)
group-7 table (the symbol names below are the audit's; the execution trace
confirms the mechanic):

- **`ROOM_P27_Below_Balcony`** (`0x40F220`, vtable `0x45E750`, 206 lines, music
  group 1). Overrides `tick, reset, event, claim, save, load` (**no opening**).
  Names `OBJ_INV_SHARP_SHEARS` (the shears sharpened at WP-069's arena
  grindstone) and the handlers `VineClicks`, `PlayBallScene`, `ShowBall`: the
  gang works the vines, the sharp shears cut the way, and a ball scene plays to
  reveal the ball.
- **`ROOM_P27A_Below_Balcony_Door`** (`0x4106B0`, vtable `0x45E850`, 109 lines,
  `Princess_Bedroom.Music`). Overrides `tick, reset, enter, event, claim`. Names
  `OBJ_INV_BALL_BLUE`, `OBJ_INV_BOTTLE_FULL`, and exits to
  `ROOM_P07_Royal_Gallery`. It runs the shared Jester tick (`0x4107D0`, one of
  the Jester member's four callers alongside the room of doors, the royal
  gallery and the well), which takes the blue ball once found
  (`TAKES_BLUE` / `BlueBallTaken`).

This closes the maze group and, with it, the blue ball's half of the
three-ball Jester chain (the red ball came from the magic mirror room in
WP-072; the yellow from the well in WP-075).

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BelowBalconyRoom`:** the vine clickables, the sharp-shears cut, the
  ball scene (`PlayBallScene` / `ShowBall`), the hotspot lines, the save/load
  state, and the ways in from the hedge maze, the maze map and the ghost-spot
  skip.
- **`BelowBalconyDoorRoom`:** the blue ball and its take by the shared Jester,
  the full bottle, the `Princess_Bedroom.Music`, the entry, and the exit back to
  the royal gallery.
- **A `script` check** against an independent reference, on both titles
  (Showdown has neither room).

**Out of scope:** any change to a sibling room class is **not expected** —
WP-074's maze map already jumps to the `BALCONY` marker, WP-072's royal gallery
is the door's exit target, and the Jester member is already ported. If the trace
surfaces a one-line hook into a sibling class (as WP-075 needed in
`maze_rooms.cpp`), it is staged by name and called out, not folded in silently.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the two classes, the clips (dotted voice lines probed by prefix, flat sfx
     ids exact — the WP-074/075 trap);
   - the vine/ball-scene placements and their gating (the sharp shears, the
     found blue ball), the save/load state, the Jester's blue-ball take, the
     exit to the royal gallery.

   Showdown prints that it has neither room.
2. [ ] Live, in Phantom: below the balcony is reached (from the maze map's
   `BALCONY` marker) and draws its placements; the door room plays its music,
   the blue ball is reachable, and its exit returns to the royal gallery.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual per-run random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine` (files staged by name: `below_balcony_rooms.{h,cpp}`,
  `below_balcony_check.cpp`, a factory line, the module entries, the check's
  declaration and its call).
- [scooby-exe](../formats/scooby-exe.md): below the balcony and its door.
- `WORK_INDEX` row and ledger line flipped to ✅ Done on close.
