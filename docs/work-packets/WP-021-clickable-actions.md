---
layout: default
title: "WP-021: Clickable Actions"
---

# WP-021: Clickable actions: state letters, sounds and the ghost (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3 (game logic: the default object behaviour)
**Depends on:** WP-018 ✅ (hit test, rollover cursor), WP-019 ✅ (sound), WP-020 (characters, input lock)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** One day
**Pre-flight:** [pre-flight-WP-021-2026-11-14](../reference/pre-flight-WP-021-2026-11-14.md)

---

## Goal

Clicking a clickable object does what `Scooby.exe`'s default clickable
does: it plays the object's current animation once with its sound, moves
the object on to its next state, and remembers that state when the room is
left and entered again. Now and then a click calls the ghost instead.

## Background

WP-018 shows `ANIM_CURSOROPEN` over a clickable and does nothing on a
click. The 103 `clickableobject` sections in Showdown's `object.ini` carry
only `ID=`, and sometimes `priority=` and `layer=`. Their `sequence=` keys
are all empty. Everything a click does comes from the code and from the
names of the animations the room places.

Traced headless in Ghidra 12.1.4, in a scratch project of Showdown's
`Scooby.exe` (SHA-256 `1328…7478`):

- **The constructor** (`0x401000`, called from `0x408DC0` with the ghost
  flag set and `layer=` read from the ini) keeps two names:
  - **the state name** (`+0x60`): the placement's ANIM, or the one the save
    file's `Clickables` section holds for this object;
  - **the sound name** (`+0x68`): `SFX_` plus the state name without its
    `ANIM_` prefix (`0x401650`).

  It starts the sprite stopped at step 0 of the state name's sequence. If
  that name isn't in the art file, the last letter becomes `A`.
- **The update** (vtable `+0x0C`, `0x401440`) runs every tick:
  - A click counts when the mouse is over the object, the click bit is set
    (`game+0x20 & 4`), nothing is playing, and the cursor shows the
    object's rollover (`ANIM_CURSOROPEN`). Room code can also queue clicks
    (`+0x80`); none of that code is in scope.
  - **On a click**, unless the ghost comes (below):
    1. play the state's sequence once (mode 3, 3 ticks per step, from
       step 0);
    2. stop, then play, the sound named `+0x68`, if `Sfx.dat` has it
       (`0x434CB0`, `0x434C70`);
    3. **advance the state** (`0x401650`): the last character + 1, unless
       that gives a digit 1–9; if the new name isn't in the art file, the
       last character becomes `A`. So `…HOTSPOT1A` goes to `…HOTSPOT1B`,
       and back to `…HOTSPOT1A` when there is no `B`. Names ending in a
       digit (`ANIM_TRAPDOOR_LEVER2`) never change. The sound name follows
       the new state;
    4. tell the room: game vtable `+0x40` (`0x40A850`) calls the room's
       vtable `+0x14` with the object's name. The default room's handler
       (`0x404440`) does nothing; story rooms override it.
  - **When the sequence ends** (the player is back in mode 0), it starts
    the new state's sequence stopped at step 0.
- **The save** (`0x401350`, the destructor) writes the state name to the
  `Clickables` section under the object's name, unless it ends in a digit.
  The constructor reads it back, so a clickable stays in its state across
  room visits.
- **The ghost** (`0x40A990`). On a click, if the clickable's ghost flag is
  set, `rand() % 30 == 0`, and the room has an `OBJ_GHOST` sprite, the
  click calls the ghost instead of playing:
  - the ghost is shown and plays its sequence once (mode 3, 3 ticks per
    step);
  - `Ghost_Appears` plays;
  - every character goes to state `0x12` (`0x405190`): sequence
    `ANIM_<NAME>_<set>STAY_SCARED`, and voice line `Global.Scared.<NAME>`.

  When the ghost's sequence ends, the game loads `ROOM_Ghost_Spot`
  (`0x409BCA`).
- **Phantom** (`Scooby.exe`, SHA-256 in `tools/exes/README.md`) has the same
  functions at the same addresses. Their decompiles match apart from
  Ghidra's names.

**Data check** (scratch script over `probe_art.py` and `probe_audio.py`):

| | Showdown | Phantom |
|---|---|---|
| Clickable placements | 96 | 87 |
| … whose `SFX_` sound exists | 59 | 66 |
| … whose next state is a different ANIM | 40 | 49 |

Both titles have a `ROOM_Ghost_Spot` scene block.

Clickables without a sound are mostly ones story rooms drive (Boot Hill's
graves, the saloon keys, Gummy's bells). By default they still play their
animation and advance.

## Scope

**In scope (fork, `engines/scooby/` only):**

- `Room`: the clickable state and sound names, the update above, and
  starting a sprite's sequence by ANIM name.
- **The clickable state**, kept in memory per object name, as the save
  file's `Clickables` section would keep it. Saves don't exist yet.
- **The ghost**: its chance, sequence and sound, every character's
  `STAY_SCARED` state, and loading `ROOM_Ghost_Spot` when the sequence ends.
  The random source is ScummVM's, not the C runtime's.
- **Input**: no clickable fires while WP-020's input lock is on.
- **Checks:**
  - `script` level 3 simulates a click on every clickable of every room:
    the sequence and its step count, the sound, the next state, and the
    tick the object comes to rest;
  - `script` level 1 logs each click, sound and state change live.

**Out of scope:**

- The room handler (`+0x14`) overrides: per-room story code.
- Clickables that story rooms create in their own placement hooks (25 call
  sites of `0x408DC0`), and queued clicks.
- Inventory and requires objects, and the cursor that hides the open hand
  while an item is held.
- `ROOM_Ghost_Spot`'s own behaviour.

## Exit criteria

1. [ ] For every clickable in every room of Showdown and Phantom, the
   engine's simulated click matches an independent reference built on
   `probe_art.py` and `probe_audio.py`: the sequence, its step count, the
   sound (or none), the next state, and the tick the object comes to rest.
2. [ ] Live: a click on a clickable plays its animation once and its sound,
   and the object rests on its next state. Leaving the room and coming
   back keeps that state. A second click plays the next state.
3. [ ] Live: with the chance forced to 1 (a debug config key), a click in a
   Phantom ghost room shows the ghost, plays `Ghost_Appears`, scares the
   gang and loads `ROOM_Ghost_Spot`.
4. [ ] Scooby-only build: 0 errors and 0 warnings. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md) rows for the clickable functions.
- WORK_INDEX row and Phase 3 findings line.
