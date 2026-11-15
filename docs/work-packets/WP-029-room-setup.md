---
layout: default
title: "WP-029: Room Setup and Town Center"
---

# WP-029: Each room's own setup, and Town Center (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (game logic: the story rooms)
**Depends on:** WP-024 ✅ (snacks), WP-026 ✅ (the profile), WP-027 ✅ (room classes), WP-028 ✅ (the story's values: `MoaningActive`)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-029-2026-11-14](../reference/pre-flight-WP-029-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Every room's music and opening | ✅ At `script` level 3 the engine enters each room from a fresh start and logs four things: the music clip playing, the opening, whether input is held, and the tick the opening starts. The reference, `wp029_ref.py`, reads the trace's output (each class constructor's call to `0x40B0F0`, with its strings read from the exe), `TGIFILE.ART`'s placements and the sound files' clip names. It never reads the engine's table. **0 differences in 69 Showdown and 53 Phantom rooms.** Every opening in the table has a first line someone in its room can say: 6 rooms in Showdown, 17 in Phantom. Each holds input and starts on tick 100. The variants rotate as traced. Showdown's group 2 alternating with group 3 plays `Group2_1` to `Group2_4`, then back to `_1`. Phantom's group 1 has seven variants, and when each clip ends the next one plays. |
| 2. Town Center against the trace | ✅ From Street 1 after a new game, Fred walks in on `ANIM_FRED_ENDWALK_UL_A1`. The opening `Town_Center.100B_` holds input and starts on tick 100. Escape marks it played. Exits before a snack play `100A_`, `100A2_`, `100A3_`, then `100A_` again. The room stays, the toolbar opens and the snack box flashes. A snack for Scooby counts one, plays the snack-given line, and the next exit leaves for Street 3. The hanging sign is a clickable in layer 1 at depth 1; the sign a hidden requires object, likewise. Clicked, the hanging sign plays 13 steps; then the sign shows and `Town_Center.307_` plays. The sign clicked: input is held, Scooby takes it a tick later, and 50 ticks after that it is in slot 0, with `Town_Center.360C_`. The second hotspot's C state frightens Daphne, Scooby and Shaggy (state 17) on its step 7. `SignClicked` reads back. A visit after the sign is taken doesn't build it, and keeps the hanging sign hidden. Saved and loaded, all 69 rooms have a section, and Town Center's `OpeningPlayed=Yes`, `SnacksGiven=1` and `SignClicked=Yes` read back. Moans come every 5–14 seconds, and idle chatter after 25–54 seconds: `100B…` or `1100D_`. |
| 3. Live, Showdown | ✅ `start_room=ROOM_P01_Town_Center`, driven by the engine's `test_script`, with real Escape key events (`key 27`):<br>• The opening held input and started on tick 100; Escape skipped it.<br>• The exit gave `Town_Center.100A_`, the toolbar came in, and the snack box flashed.<br>• Scooby ate the snack.<br>• The hanging sign came down, and Scooby carried the sign into the toolbar.<br>• The exit then walked the gang to Street 3, whose opening `Street_3.320A_` started on tick 100.<br>Nine frames were captured from the screen. |
| 4. Build and regressions | ✅ Scooby-only build: 0 errors, 0 warnings in `engines/scooby/`. Fork commit [`2de5b85eea`](https://github.com/barefootbetters/scummvm/commit/2de5b85eea) is on WP-028/030's `7e184fcf1a`, inside `engines/scooby/`, and is pushed. Against that head, every earlier check's lines match on both titles: exits, clicks, inventory, hints and snacks, profile, menus, Sign In, Options and Credits, movies. The one exception is the profile's key count (Showdown 129 → 268, Phantom 128 → 234), since every room now writes its section. |

**Deviations and gaps:**

- **The music never rotates on its own.** Every music clip has the loop flag, so `0x409CB3`'s "clip over" never comes. The rotation runs as traced; the check forces it by stopping the clip.
- **Follow-up fork commit [`1f002172c4`](https://github.com/barefootbetters/scummvm/commit/1f002172c4)** makes the Town Center check identical from run to run. The idle chatter and the snack-given line come from `rand()`, so the check now reports what the trace fixes, not which line was drawn. The WP-001 session spotted it.
- **Not done:** the game's idle time restarting when Scooby takes the sign (`0x436810`, game `+0x34`/`+0x3C`, not modelled).
- **Not traced: the music during scenes.** Every scene start calls `0x434F10(90, 2)` (`0x40B400`). Every scene end calls `0x434F30(100, 4)` (`0x40C810`), and the room load calls `0x434F30(100, 3)`. These are probably the music fading down and back. The fork's music stays level.
- **Not traced:** the idle line's name (`+0x28`, `0x40CB50`), and which of its two factory scenes the Credits room keeps as its opening.
- **Background music isn't "the sound".** The fork's log and the menu check follow the clip played last. Room music doesn't become it, or the music restarting after a check stops every sound would hide the button's sound.
- **Walk-ins checked from Street 1 only.** Velma's (Street 2) and Shaggy's (Street 3) are the same code with another character and direction.
- **The other story rooms** are next, a few rooms a packet: Showdown's streets (`P03`, `P04`, `P11`) first.

## Goal

Give every room the setup its class gives it in the original, and play
the first story room, Showdown's Town Center, as its class has it. This is
the groundwork every later story room builds on.

## Background

Every room is an object the factory builds at startup (Showdown
`0x42E0E0`). Each class constructor passes two strings to the base
constructor (`0x40B0F0`), and its reset (vtable `+0x08`) can set a third
value:

- **Music** (`+0x68`). A number picks a music group: entry (`0x40B920` →
  `0x40AA10`) plays `Group<g>_<n>.Music`, and the next variant `n` each
  time the group changes (game `+0x1E4`), wrapping to 1 when the name is
  missing. A name plays that clip. Rooms without a class pass an empty
  string and keep the music that was playing. While a group is current, the
  game's update picks the next variant when the clip ends (`0x409CB3`).
- **The opening scene** (`+0x78`). At entry (vtable `+0x3C`, `0x40C7B0`),
  if it isn't played and a character here has its first line
  (`0x40C6C0`), input is held and the cursor fades. Otherwise it counts as
  played. The room's tick (`0x40B490`) starts it, blocking, 100 ticks
  (`+0x74`) after the room was built, once no scene is playing and no exit
  is parked. Input slot 5 skips it (`+0x28`). Played (`+0x10`) is saved as
  the room's `OpeningPlayed`. Entering any room from `ROOM_Ghost_Spot`
  makes its opening one of `Global.Ghost_Spot[B|C]_`, not yet played.
- **Snacks needed** (`+0x24`, 0 unless the reset sets it). Each snack eaten
  here counts (`+0x88`, saved as `SnacksGiven`). The snack-given line plays
  only once the count reaches the number needed.
- **Idle chatter** (vtable `+0x34`). Every 25–54 seconds with no scene and
  the opening played (or none), the tick calls it. The base class does
  nothing; Town Center's plays one of its `100B` scenes.

The setup of every room of both titles, from the trace, is in
[scooby-exe](../formats/scooby-exe.md#each-rooms-own-setup-wp-029).

**Town Center** (`0x42CFD0`, vtable `0x45F300`):

- **Reset:** one snack needed; the moan timer at 36 ticks.
- **Entry from** Street 1, Street 2 or Street 3: Fred walks `UL`, Velma
  `U`, or Shaggy `UR` (character state 1).
- **Placements:** the sign (`OBJ_INV_SIGN`) becomes a requires object in
  layer 1, unless it was ever taken, and stays hidden until the hanging
  sign (`OBJ_P01_TC_HOTSPOT4`, a clickable in layer 1) is clicked.
  `OBJ_P01_TC_HOTSPOT2` is a clickable in its own layer.
- **Events:** the hanging sign sets `SignClicked` (saved). The sign clicked
  with the arrow starts Scooby taking it.
- **Tick:** with the story's `MoaningActive`, a moan every 5–14 seconds.
  When the hanging sign's click is over, the sign shows and scene
  `Town_Center.307_` plays. At step 7 of `ANIM_P01_TC_HOTSPOT2C`, Daphne,
  Scooby and Shaggy go to state 17. Scooby taking the sign: once he is
  idle and no scene plays, he hides behind `ANIM_SCOOBY_P01_TAKES_SIGN1`
  with `Scooby_Takes_Sign`, input held. When it ends, the sign is in the
  toolbar and scene `Town_Center.360C_` plays.
- **Exit:** until Scooby has eaten a snack here, an exit plays
  `Town_Center.100A_`, `100A2_`, `100A3_` in turn and flashes the snack box
  instead of leaving.
- **Idle chatter:** one of `Town_Center.100B_`, `100B2_`, `100B3_` (with
  `MoaningActive`) or `1100D_`.

## Scope

**In scope (fork, `engines/scooby/` only):**

- A setup table for every room of Showdown and Phantom: music, opening
  scene, snacks needed.
- Music on entry and the variant rotation; the opening scene, its delay and
  skip; snacks needed and given; the idle chatter timer; `OpeningPlayed` and
  `SnacksGiven` in each room's profile section.
- `RoomClass` hooks the story rooms need: reset, an object's event,
  claiming a placement, the exit, idle chatter, and the room's profile keys.
- Town Center's class.
- A `script` level 3 check.

**Out of scope:** every other story room; the Credits room's opening (its
factory passes two scenes, not traced).

## Exit criteria

1. [ ] Every room of both titles: the music played on entry and the
   opening scene match a reference that reads the trace output and the
   sound files, not the engine's table.
2. [ ] Town Center from a new game, against the trace: the opening at tick
   100; exits blocked, rotating scenes, until a snack; the snack-given
   line; the hanging sign, the sign, Scooby taking it, the item and the
   scenes; `SignClicked`, `OpeningPlayed` and `SnacksGiven` saved and read
   back.
3. [ ] Live, in Showdown: Town Center's opening, the blocked exit, feeding
   Scooby, and the sign into the toolbar.
4. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks pass.
   The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): each room's setup, and Town
  Center.
- WORK_INDEX row and findings line.
