---
layout: default
title: "WP-057: Phantom's drawbridge and town"
---

# WP-057: Phantom's drawbridge and town: four flags to the banners (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-029 ✅ (room setup), WP-026 ✅ (the profile), WP-024 ✅ (the snack box), WP-021 ✅ (clickables), WP-056 ✅ (the check's place)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-057-2026-11-16](../reference/pre-flight-WP-057-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp059_ref.py`: WP-056's, plus the drawbridge and the town, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art, and which sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 11 drawbridge lines on Phantom (18 in all) and one on Showdown, which has no drawbridge (215 in all).

The first run differed on one line, and the reference was wrong. Entering the drawbridge, its unplayed opening holds input until the first skip, as `0x40C7B0` has it; the reference had left that out. The second run matched all 18 lines on Phantom and all 215 on Showdown.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**The classes** for both rooms.<br>**A new game:** the 17 flags off, `Screaming` on, a villain of the five, the crest a permutation of 1–4, the skull's digits 0–3.<br>**The reset,** 200 times: every banner colour, and each flag one to three colours on from its banner, never on it.<br>**Entry from the town:** each flag waving its saved colour from a random step, clickable with the open hand; each banner waving its colour; the door stopped on its first step at depth −1; no way out yet; one snack needed; Velma walking in, 50 behind; `Fanfare.1` for the flag already right, then `Flag_Loop`.<br>**A flag click:** lowered at tick 1, the next colour raised at tick 22, waving at 43, with `Flag_Raise` twice. A click during the lowering raises at once (tick 2, waving at 23).<br>**Velma,** idle, comments when a flag leaves its banner's colour.<br>**Solved** at tick 43: the flags no longer clickable, the way out built (depth −1, hit by its polygon, to `ROOM_P04_Town`), both fanfares. The door waits while the second plays. When it ends: the door plays once, `Drawbridge.Down`, and `Drawbridge.Enter_` holds input.<br>**The way out:** `110A_` and the snack box's flash before a snack; then it leaves.<br>**The profile:** `FlagState0`–`3`, `BannerState0`–`3`, `PuzzleDone`. Loaded, the flags are not clickable, the door is down (its last step), and the default path builds the way out.<br>**The sign:** `100X1_`, `100X2_`, `100X1_`.<br>**The town:** Velma in from the drawbridge (50 in front), Shaggy from the shop and Fred from the gardener's house (50 behind), Velma from the room of doors; nobody from elsewhere. Screams 1, 2, 3 and 5 over 199 visits; none without `Screaming`.<br>Showdown prints that it has no drawbridge. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized:<br>**The puzzle,** with three flags right: one click on flag 4 lowered and raised its pennants, then both fanfares, `Drawbridge.Down`, and Fred's two `Drawbridge.Enter_` lines.<br>**The town,** from a solved drawbridge with a snack given: the way out in the castle's doorway led to `ROOM_P04_Town`. Velma walked in from the drawbridge, `Town.Jane_Screaming2` played, and the opening `Town.110_` followed. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-056's run. Phantom's differ in two ways, both expected:<br>• the profile check writes and imports the drawbridge's nine keys, which are random from its reset;<br>• the sign-in check now lists Phantom's story values where it printed `none`.<br>Fork commit [`35eea2ae51`](https://github.com/barefootbetters/scummvm/commit/35eea2ae51) (12 files staged by name) is pushed. |

**Deviations and gaps:**

- **Velma's idle line** (`+0x28`) isn't ported: the fork has no character state 4, which asks for it. Ported in [WP-059](WP-059-idle-states.md).
- **The sound section's preload** (`0x435B60`) has no counterpart; the fork reads clips as they play.
- **The tick clock's restart** (`0x437540`) after the fanfare isn't kept.
- **A flag's click** is read from the engine's click on it, as the artifact puzzle's is, not from the button coming up.

**Found on the way:**

- **Phantom's engine is Showdown's at other addresses.** Matching instruction sequences with addresses masked pairs 980 functions, which made the trace a lookup.
- **A Phantom new game sets 27 story values** (`0x42E880`); until now the fork set none, so nothing that reads them could fire.
- **Jane's fourth scream is never played:** `rand() % 5` gives 1, 2, 3 and twice 5.
- **The drawbridge's way out is in the castle's doorway,** behind the lowered drawbridge, which takes clicks in front of it.

---

## Goal

Port Phantom's first two rooms, the first of the 38 game classes in
[Phantom's audit](../reference/room-class-audit-phantom-2026-11-16.md):
- **ROOM_P01_Drawbridge,** where a new game starts. Until now it had the
  base class: the flags didn't move, and its way to the town was there from
  the start.
- **ROOM_P04_Town,** the hub. Until now nobody walked in and Jane never
  screamed.

## Background

The drawbridge ([scooby-exe](../formats/scooby-exe.md#phantoms-drawbridge-and-town-wp-057))
is a puzzle: four flags must wave their banners' colours. Each click on a
flag lowers its pennant and raises the next colour. With all four right, a
fanfare plays, the drawbridge comes down, and the way to the town opens.

Phantom's `Scooby.exe` is mostly Showdown's code at other addresses. A
function-by-function match between the two maps Phantom's helpers to the
ones already traced.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`DrawbridgeRoom`:** the colours, the flags and banners, the puzzle, the
  fanfares, the drawbridge, the way out, the sign and the profile keys.
- **`TownRoom`:** the walk-ins and Jane's screams.
- **A Phantom new game's story values** (`0x42E880`), which the town reads.
- **`Room`:** an exit built after loading, and `startAnim` at a given tick
  rate.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes;
   - a new game's story values;
   - the drawbridge's reset;
   - its entry: each flag, banner, the door, the overlay and the way out,
     the snacks needed, Velma's walk-in and the sounds;
   - a flag's click, its moves with their ticks, and a click during one;
   - Velma's line when a flag leaves its banner's colour;
   - the puzzle done: the way out, the fanfares, the drawbridge down;
   - the way out before and after a snack;
   - the profile keys, and a visit with the puzzle done;
   - the sign's lines;
   - the town's walk-ins and screams.

   Showdown prints that it has no drawbridge, as its reference does.
2. [x] Live, in Phantom: the puzzle solved with a click, the drawbridge
   down; then through it to the town, with a walk-in and a scream.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile keys and story
   values. The fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-drawbridge-and-town-wp-057):
  the drawbridge, the town, a Phantom new game's story values, and the
  functions matched between the titles.
