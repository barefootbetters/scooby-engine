---
layout: default
title: "WP-093: Phantom's fountain piranha and the tokens"
---

# WP-093: Phantom's fountain piranha and the tokens (Gen 1)

**Status:** ✅ Done (2026-11-27). Fork PR [barefootbetters/scummvm#17](https://github.com/barefootbetters/scummvm/pull/17) is open.
**Phase:** 5 (a soft-lock found while checking WP-075's modelled items)
**Depends on:** WP-075 ✅ (the maze interior: the fountain and the centre the way back leads to)
**Companion EC:** none (inline checklist under Exit criteria)
**Pre-flight:** [pre-flight-WP-093-2026-11-27](../reference/pre-flight-WP-093-2026-11-27.md). Required: the packet modifies `engines/terraglyph/**`.
**Targets generation(s):** Gen 1, *Phantom of the Knight* only. Showdown has no such room.
**Estimated effort:** Two hours

---

## Goal

Port the fountain close-up's piranha (`ROOM_P44_Fountain_Closeup`, class
`0x429740`) from the decompile, so feeding it the burger gives the tokens
as the original does.

## Background

[WP-075](WP-075-maze-interior.md) ported the fountain and noted under
Deviations that "the piranha eat … [is] modelled, not frame-exact".
[WP-092](WP-092-well-jester.md) found that WP-075's other modelled item hid a
missing behaviour, so Jeff asked for this one next.

**The fork at `8410401`** (source, then live — session):

- **The burger spent and no tokens.** Feeding the burger removed it and set
  the room "fed". The tick then waited for a `SHAGGY` character to stand
  idle before giving the tokens, and the close-up has no Shaggy character
  (only the `OBJ_SHAGGY_P44_GRAB_TOKENS` sprite). The tokens never came.
- **A frozen piranha.** The eat called `setPlayer(piranha, 3, 3, -1)` on
  whatever the piranha was playing, at −1 ticks a step, so it froze.
- **A piranha that took no clicks.** It was claimed as a plain sprite, so a
  click aimed at it fell through to the tokens behind it.
- **No lunge, no grab, no way back.** The lunge sound was declared but never
  played, Shaggy's grab never showed, and the exit to the centre never ran.

The tokens are what the empty bottle asks for (`OBJ_INV_BOTTLE_EMPTY`,
`requiredanim=ANIM_CURSORTOKENS`). The burger is an `inventoryobject`
placement, which by the inventory rules is picked up once (inferred, not
replayed). A player who fed the piranha on the old build therefore couldn't
reach the bottle chain: **a progression soft-lock.**

## Scope

**In scope:**

1. **Fork, `maze_interior_rooms.{h,cpp}`:** `FountainCloseupRoom`'s claim,
   reset, entry, event, tick and leave from the trace.
2. **Fork, `maze_interior_check.cpp`:** the room played through the engine's
   tick. WP-075's claim line is reworded to what the claim now decides.
3. **Docs:** this packet, its pre-flight, the fountain's section in
   [scooby-exe](../formats/scooby-exe.md#phantoms-maze-interior--the-centre-the-fountain-and-the-well-wp-075),
   the correction in WP-075, and the index row.

**Out of scope:**

- The game's `+0x238` string, which the original sets to the current room
  when the burger is fed. Nothing in this room reads it, and its reader is
  unidentified.
- `0x437540`, which restarts the game's tick clock (WP-055 notes it). The
  fork has no counterpart.

## Exit criteria

1. [x] **Self-test.** The new fountain lines match text written from the
   trace before the run. The rest of the self-test matches the `8410401`
   baseline except the per-run random keys (and WP-075's reworded claim
   line). No new warnings.
2. [x] **Live (session).** The burger fed to the piranha gives the tokens and
   takes the gang back to the centre. A plain click plays a line, and the
   piranha lunges.
3. [x] **Process.** The fork PR against `scooby-engine` is open, and each claim
   carries its evidence label.

## Result

Every claim is Gen 1, Phantom. Evidence labels: **source** (the decompile),
**self-test**, **log** (the engine's debug log of a live run), **live —
session** (a scripted run this session drove). Nothing here is **live —
Jeff**.

**What the original does (source).** This is recorded in full in
[scooby-exe](../formats/scooby-exe.md#phantoms-maze-interior--the-centre-the-fountain-and-the-well-wp-075),
from `Scooby.exe` (SHA-256 `619EA687…AF807ED`, Ghidra 12.1.4 headless):

- **The piranha** is a requires object (`0x402D90`) wanting the burger.
  Before the burger is used it plays its idle once, with its swim, and then
  again each time it ends.
- **A lunge** is pending from reset and after each plain click. It fires when
  the idle next ends (`ANIM_PIRANHALUNGE_ATTACK`).
- **The burger** starts it eating, with input held. When `EAT_START` ends,
  the piranha and the tokens are hidden while Shaggy's grab plays. When the
  grab ends:
  - the tokens go into the toolbar;
  - the piranha comes back with `EAT_FINISH`, then `FULL`, looping;
  - an exit to `ROOM_P23_Maze_Center` with `Fountain.250F_` is built and
    taken.

**The port (source).** On `wp-093-fountain-piranha` (`7db942e513`): the
claim, reset, entry, event, tick and leave follow the trace. The piranha's
sequence is set at entry, since the fork's claim can't set a once-only
start. A plain click is recognised by `Inventory::isDefaultCursor()`; the
original checks for the open-hand cursor.

**Self-test (self-test).** Five lines were written from the trace before the
run, using the step counts in `TGIFILE.ART`: idle 35, attack 30, eat start
17, eat finish 13, grab 13, at 3 ticks a step. All match:

- **A fresh visit:** the piranha is a requires object, hit 2, depth −1,
  playing `ANIM_PIRANHAIDLE` once with a lunge pending, and the grab is
  hidden and stopped. It lunges at tick 105 and plays its idle again at
  tick 195, with no lunge pending.
- **A click:** a lunge pending, `Fountain.250D_`, cycle 1. On the tokens:
  `Fountain.250D1_`, cycle 2.
- **The burger:** it is out of the slots, the piranha plays
  `ANIM_PIRANHALUNGE_EAT_START`, input is held and the cursor hidden.
  - At tick 51 the grab shows, with the piranha and the tokens hidden.
  - At tick 90 the tokens are in the toolbar, the piranha plays `EAT_FINISH`,
    and the grab is hidden again; input is free.
  - The scene `Fountain.250F_` plays, and the gang goes to
    `ROOM_P23_Maze_Center`.
- **After:** the piranha plays `ANIM_PIRANHAFULL` in mode 1, and the tokens
  aren't placed.
- **The claims:** the piranha is a requires object in layer 0 at depth −1,
  before and after the burger; the grab is a sprite in layer 1 at depth
  100, hidden.

The rest of the self-test matches the `8410401` baseline from
`C:\dev\scummvm`, run alone this time, with 1828 lines each. The only
differences are the per-run random keys and WP-075's claim line, which now
reports the build, layer and depth instead of the sequences the claim no
longer sets. The runtime warnings match the baseline's, 18 each.

**Build (log).** Terraglyph only, in the fork worktree; no warnings in the
changed files.

**Live (live — session, with log).** All runs used
`start_room=ROOM_P44_Fountain_Closeup` and `start_items=OBJ_INV_BURGER`:

- **The lunge:** `fountain: the piranha lunges` about 3 s after entry.
- **A plain click** after the opening (which holds input until it ends) lands
  on the tokens and plays `Fountain.250D_`. The piranha lunges when its idle
  ends, a second later.
- **The burger:** the burger is taken from the toolbar and used on the
  piranha (`click at 340,170 on 2 OBJ_PIRANHA`). The log then reads:
  - `the piranha is fed`;
  - `Shaggy grabs the tokens`;
  - `scene Fountain.250F_ starts`;
  - `exit : scene 'Fountain.250F_', then ROOM_P23_Maze_Center`;
  - `going to ROOM_P23_Maze_Center`.

  The screenshots show the piranha with the burger, the piranha gone under
  with the tokens left behind, Shaggy's hand, the piranha back and full, the
  tokens in the toolbar, then the maze centre.
- **The same burger script on `8410401`:** the click aimed at the piranha
  lands on `OBJ_INV_TOKENS`, `the piranha is fed` is logged, and then
  nothing. The piranha is frozen in two screenshots 7 s apart, and no tokens
  arrive.

## Deliverables

- Fork: `wp-093-fountain-piranha`, PR [barefootbetters/scummvm#17](https://github.com/barefootbetters/scummvm/pull/17)
  (`7db942e513`). Staged by name: `maze_interior_rooms.{h,cpp}` and
  `maze_interior_check.cpp`.
- Docs: this packet, its pre-flight, the fountain's section in scooby-exe,
  the correction in WP-075, and the index row.
- Local only: the decompile dump, the self-test and live logs, and the
  screenshots.

## Notes

- **WP-075's modelled items are now all checked.** The well's was the
  Jester ([WP-092](WP-092-well-jester.md)); the fountain's was this
  soft-lock.
- **The lesson** (the same as WP-090's): a Deviations note that says
  "modelled, not frame-exact" and a self-test of the setup only can hide an
  unplayable path. The check here drives the path through the tick.
- **Running checks:** the arena pile check's level-0 line matched in this
  packet's baseline, run alone. It printed `-` in WP-092's baseline run,
  which shared the machine with another run. Run baselines one at a time.
