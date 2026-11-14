---
layout: default
title: "WP-021: Clickable Actions"
---

# WP-021: Clickable actions: state letters, sounds and the ghost (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (game logic: the default object behaviour)
**Depends on:** WP-018 ✅ (hit test, rollover cursor), WP-019 ✅ (sound), WP-020 ✅ (characters, input lock)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** One day
**Pre-flight:** [pre-flight-WP-021-2026-11-14](../reference/pre-flight-WP-021-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Every click matches | ✅ At `script` level 3 the engine loads each room afresh for each clickable and clicks it twice. For each click it logs the state played, its step count, the sound (or `-`), the next state and the ticks until the object rests. An independent Python reference implements `0x401440`/`0x401650` on `probe_art.py` and `probe_audio.py`. The logs are identical: Showdown 192 lines (191 clicks; the chandelier pump can't be clicked a second time), Phantom 174 clicks (MD5 `6003f21c…` and `f5899fef…`), 0 stuck. |
| 2. Live click, state kept | ✅ A real mouse click on Town Center's `OBJ_P01_TC_HOTSPOT1` played `ANIM_P01_TC_HOTSPOT1A` with `SFX_P01_TC_HOTSPOT1A`, and the object rested on `…1B` 54 ticks later (18 steps × 3). The gang went to Street 3 and back. Town Center then drew with a different MD5, showing `…1B`, and a second click played `…1B` with its sound and rested on `…1C`. |
| 3. Live ghost | ✅ `ghost_chance=1`, in Phantom's Souvenir Shop. A click on `OBJ_P03_SOUVENIR_STORE_HOTSPOT1` played `Ghost_Appears`, and each character's `Global.Scared` line where the clip exists (there is none for Scooby). The ghost played its 75 ticks, and `ROOM_Ghost_Spot` loaded (1280×480). |
| 4. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Fork commits [`b18b5f6a53`](https://github.com/barefootbetters/scummvm/commit/b18b5f6a53) and [`4f135d3a9f`](https://github.com/barefootbetters/scummvm/commit/4f135d3a9f) stage their files by name, inside `engines/scooby/`, on top of WP-020's `7e03ae779a`, and are pushed. |

**Deviations:**

- **Two clickable sounds are in `Music.dat`.** `SFX_P11_STREET3_HOTSPOT2A` and `SFX_P12_SALOON_HOTSPOT1B` are stored with the music. The original's lookup searches all three files, so they play. In the fork they play on the music channel, and would stop room music if any were playing. The reference first searched `Sfx.dat` only, and the comparison caught it.
- **One sound at a time per file.** WP-019 gives each file one mixer handle. A clickable's sound stops any other effect. When the ghost scares the gang, each line replaces the one before, so only the last character's line is heard. Whether the original mixed them is not traced.
- **The ghost's odds** come from ScummVM's random source, not the C runtime's `rand()`.
- **A missing state.** Showdown's chandelier pump goes from `ANIM_P12_SALOON_CHANDPUMP` to `…CHANDPUMQ`, then to `…CHANDPUMA`. Neither name exists. `SetAnim` (`0x430A00`) stores id 0 and starts nothing, `SelectFrame` (`0x4309C0`) selects no frame, and the hit test (`0x430D10`) fails. So after one click the pump is neither drawn nor clickable. The Saloon's own code drives that object, which is out of scope here.
- **The ghost room** loads but does nothing yet: it is per-room code.
- **Corrected the same day.** The first engine commit and the first reference both played the object's sequence 0 for an unknown name. They agreed because both followed the same wrong reading of `0x430A00`. The WP-001 session found the error in the decompile. Fork commit `4f135d3a9f` fixes the engine, and the reference now models the original.

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

1. [x] For every clickable in every room of Showdown and Phantom, the
   engine's simulated click matches an independent reference built on
   `probe_art.py` and `probe_audio.py`: the sequence, its step count, the
   sound (or none), the next state, and the tick the object comes to rest.
2. [x] Live: a click on a clickable plays its animation once and its sound,
   and the object rests on its next state. Leaving the room and coming
   back keeps that state. A second click plays the next state.
3. [x] Live: with the chance forced to 1 (a debug config key), a click in a
   Phantom ghost room shows the ghost, plays `Ghost_Appears`, scares the
   gang and loads `ROOM_Ghost_Spot`.
4. [x] Scooby-only build: 0 errors and 0 warnings. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md) rows for the clickable functions.
- WORK_INDEX row and Phase 3 findings line.
