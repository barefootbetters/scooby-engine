---
layout: default
title: "WP-020: The Exit Transition"
---

# WP-020: The exit transition: characters, scenes and the walk-off (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (game logic: the first scripted behaviour)
**Depends on:** WP-017 ✅ (sequence player), WP-018 ✅ (exit click), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** One day
**Pre-flight:** [pre-flight-WP-020-2026-11-14](../reference/pre-flight-WP-020-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Every exit matches the reference | ✅ At `script` level 3 the engine walks every exit of every room: the scene's lines as their clips resolve, then the walk-off simulated tick by tick with the scene skipped. A reference built on `probe_art.py`, `probe_audio.py` and `object.ini` computes the same plan in closed form. The logs are identical: Showdown 71 exits in 69 rooms, Phantom 82 in 53, none stuck. 42 exits have scene lines and 91 have walks. |
| 2. Live transition | ✅ In Showdown's Saloon, the exit to the Hotel Hall spoke `Saloon.360S1_` on the speech channel: Daphne at tick 76, Fred at 135 and Scooby at 247. Each line ended on its clip's length (1.59 s, 3.05 s and 0.58 s). All 190 lip-sync readings logged match the clips' bytes, and the byte index ran each clip's length at 12 fps. Fred then led the walk (`UR`, 21 steps). Daphne turned 39 ticks later, and the Hotel Hall loaded 60 ticks after the walk began, as the check predicts. Back in the Saloon, the same exit skipped its scene. |
| 3. No scene, no walkers, missing walks | ✅ Exits with no walkers change room on their first tick (`OBJ_HC_EXIT`, `OBJ_P12_SALOON_PIE_NOON`). In the data, every gang member left out of a walk-off has an empty direction (42 in Showdown, 77 in Phantom). A scratch copy of `object.ini` was edited to keep its length, so detection still passes: `fred=XX` and a scene with no clips. Fred was left out, Daphne led, the scene ended at once, and nothing crashed. The cached `object.ini` still matches its SHA-256. |
| 4. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Fork commit [`7e03ae779a`](https://github.com/barefootbetters/scummvm/commit/7e03ae779a) stages its 13 files by name, inside `engines/scooby/`, and is pushed. The WP-018 room renders and hit grids of all 122 rooms are unchanged. |

**Deviations:**

- **The 16 room overrides aren't implemented.** In the original, some exits are refused or play another scene until the story allows them (Town Center, for one). Here every room uses the default handler.
- **Taken exits last for the session.** Saves don't exist yet, so the `Exits` marks are kept in memory.
- **Characters keep their placement's sequence on entry.** The constructor's switch to `IDLE_MASTER` would only change the three set pieces, which their rooms' code drives.
- **The cursor hides at once**; the original fades it out over 18 ticks. Movies are logged, not played.

---

## Goal

Clicking an exit plays the original's transition: the gang speaks the
exit's scene with lip sync, then walks or turns off as the exit directs,
and the destination room loads when the last walk ends.

## Background

WP-018 loads the destination as soon as an exit is clicked. In `Scooby.exe`
the click goes further:

- **The click** (`0x402130`) packs the exit's keys (`0x404820`) and hands
  them to the current room object's vtable `+0x24` (`0x4024C0`). The keys
  are those the exit constructor (`0x401850`) reads: `destinationroom=`,
  `movie=`, `scene=`, and one direction per gang member (`fred=`,
  `daphne=`, `velma=`, `shaggy=`, `scooby=`). It never reads the
  `character=` and `direction=` keys that most exit sections also carry.
- **First use only.** The constructor clears `scene=` when the save file's
  `Exits` section marks the exit as taken (`1`, `on`, `On`, `ON` or `TRUE`).
  The click writes that mark, so each exit's scene plays once.
- **The default handler** (`0x40C1E0`) fades the cursor out, blocks input,
  starts the scene (`0x40B400`) and parks the exit on the room. 31 of
  Showdown's 47 room classes use it as is; the other 16 override it to
  gate exits on story state, and then call it.
- **The scene player** (room vtable `+0x38`, `0x40C810`) runs every tick.
  When the current speaker has finished, it moves to line *n* + 1 and
  looks for a clip named `<scene><n>_<NAME>` for each character in the
  room, in placement order, then an invisible `NARRATOR`. The first match
  speaks. When no character has line *n*, the scene ends.
- **A character** (`0x4048E0`) is a placement such as `OBJ_FRED_A`: name
  `FRED`, set `_A`. Its state machine (`0x405190`) picks a sequence and,
  when it changes, the object that holds it:

  | State | Object | Sequence | Mode | When the sequence ends |
  |---|---|---|---|---|
  | 6 idle | `OBJ_FRED_A` | `ANIM_FRED_AIDLE_MASTER` | loop | — |
  | 8 talk | `OBJ_FRED_A` | `ANIM_FRED_ATALKS` | stopped; lip sync sets the step | idle when the clip ends |
  | 0 walk | `OBJ_FRED_STARTWALK_UR_A` | `ANIM_FRED_STARTWALK_UR_A1` | once | stays on its last step |
  | 0 turn | `OBJ_FRED_A` | `ANIM_FRED_ATURN_UR` | once | stays on its last step |

  A direction starting with `TURN` turns in place; any other is a walk.
  A walk starting with `D` moves the character 50 in front (depth + 50),
  one starting with `U` 50 behind.
- **Lip sync** (`0x442DD0`): the talking step is the low nibble of the
  clip's lip-sync byte at `trunc(fps × seconds played)`, less 1; a nibble
  of 0 keeps the step.
- **The walk-off** (`0x40BE20`) runs each tick once the scene is over. It
  measures each gang member's walk, in steps; the longest is the leader,
  who starts at once. Each other character starts when the leader's steps
  still to go, less 1, are no more than its own walk. When the leader
  reaches its last step, the game goes to `destinationroom=` through game
  vtable `+0x08` (`0x42DE10`), which plays `movie=` first if it is set.

## Scope

**In scope (fork, `engines/scooby/` only):**

- `Character` (`character.{h,cpp}`): the idle, talk, walk and turn states,
  object switching, the end-of-sequence step, and lip-synced talking.
- `RoomScript` (`room_script.{h,cpp}`), the default room behaviour:
  - the room's characters, in placement order, plus the narrator;
  - the scene player;
  - the default exit handler and the walk-off.
- `Room`: switching a sprite's object and sequence, setting its depth, and
  reading a sequence's step count.
- `Sound`: one mixer handle per file, so a voice line doesn't stop the
  music, and each clip's lip-sync bytes.
- Exits taken in this session play their scene once. Saves don't exist
  yet, so the mark is kept in memory.
- Checks:
  - `script` level 3 simulates every exit of every room: the scene's
    lines and speakers, each walker's length and start tick, and the
    tick the room changes;
  - `script` level 1 logs each line, walk start and room change live.

**Out of scope:**

- The 16 room overrides (story gating and alternate scenes), arrival
  walks (`ENDWALK`), random idles, Velma's reaction turns, music ducking,
  the speech lock, Scrappy and the `ANIM_CURSORSCRAPPY_ANIM` hint.
- Movies (Bink). An exit with `movie=` logs it and goes on.
- The cursor's fade. The cursor hides at once.

## Exit criteria

1. [x] For every exit in every room of Showdown and Phantom, the engine's
   simulated transition matches an independent reference built on
   `probe_art.py` and `probe_audio.py`: the scene's lines and speakers,
   each walker's sequence, length and start tick, the leader, and the
   tick the room changes.
2. [x] Live, an exit with a scene plays its lines in order on the speech
   channel, the speaker's talking step follows the lip-sync bytes, the
   gang walks off, and the destination room loads. A second use of the
   same exit skips the scene.
3. [x] An exit with no scene and no walkers still loads its destination at
   once. A missing walk sequence leaves that character out, without a
   crash.
4. [x] Scooby-only build: 0 errors and 0 warnings. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §6](../02-SCUMMVM-INTEGRATION.md#6-audio) implementation
  notes: a handle per file, and lip sync.
- [scooby-exe](../formats/scooby-exe.md): the functions above, the
  `exitobject` keys, and a section on the transition.
- [audio-archives](../formats/audio-archives.md): how lip sync is read.
