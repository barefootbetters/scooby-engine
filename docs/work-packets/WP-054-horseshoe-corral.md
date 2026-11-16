---
layout: default
title: "WP-054: Showdown's horseshoe corral"
---

# WP-054: Showdown's horseshoe corral: ten throws each, a snack a ringer (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-035 ✅ (the chase, Chase B5), WP-021 ✅ (sprites and their players), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-054-2026-11-16](../reference/pre-flight-WP-054-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp055_ref.py`: WP-053's, plus the corral, written from the trace before the engine ran. It reads the placements and step counts from the art, and which sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 196 lines on Showdown: the earlier 190 and 6 for the corral. On Phantom both print the one line saying there is no chase.

The first run matched 195. The odd line was the reference's. It had Rascal toss as soon as his turn came, but he waits for his head to be still (`0x41D860`, state 1), and his head replays its idle at random while he waits. The run's turn came mid-idle. The check now times his horseshoe from his toss. The class didn't change, and the second run matched all 196.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**Entry.** The piles, the counter's box and numbers (0 and 1 for a new game's snack), the meter at the arrow's place sweeping forward, Scooby, Rascal's head and body, and the three pegs, each at its depth. The exit is there, the meter's placement isn't built, and it is Scooby's turn.<br>**The meter.** Back at tick 55, 37, 19 and forward at 109, 73, 37 by level: Scooby, in front, sees its end the tick after.<br>**A throw.** Held on step 2, strength 2. His pile goes on at tick 6, his horseshoe at 45 (one of strength 2's, ringing as its `H`). It lands and tells at arc + 3 × its steps + 3 × its peg's + 35, since it is ticked in the walk it is made in. Rascal's turn comes a tick later, and his horseshoe 21 ticks into his toss, by its rules.<br>**Chosen horseshoes:**<br>- `1x01H`: peg 1, a snack, done at tick 183.<br>- `3x00`: a miss, done at 87.<br>- `4x02`: at depth 10000, done at 96.<br>- Rascal's 2: peg 2, done at 165.<br>- Rascal's 8: taken as 9, done at 90.<br>- Rascal's 5: done at 117.<br>Each has its sound, and each stays paused on its last sequence.<br>**A whole game.** Ten throws each, both piles on step 10, 20 horseshoes paused, a snack per ringer, then Chase B5. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from a profile starting in the corral, with the button held to stop the meter:<br>**Scooby:** `2x02` and `1x04` miss; `1x06H` rings peg 1 with its peg sound, and the counter goes from 01 to 02.<br>**Rascal:** his 3 rings peg 3; his 6 and 9 miss. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The earlier checks are identical to WP-053's run on both titles. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`da9ad7b744`](https://github.com/barefootbetters/scummvm/commit/da9ad7b744) (7 files staged by name) is pushed. |

**Deviations and gaps:**

- **`rand()`:** Rascal's strength and waits and Scooby's arc digits come from the engine's own random source.
- **The button held** (game `+0x20` bit 1) is the engine's mouse-down state.
- **The sound section's preload** (`audio_GameSound_PreloadSection`) has no counterpart; the fork reads clips as they play.

**Found on the way:**

- **The audit counted only the room's own functions** (249 instructions); the game is in its three sprite classes.
- **Scooby's ringers play Rascal's peg sounds.** The disc's `Horseshoe_Corral.Scooby.Peg<n>.Hit` are never used.
- **Mismatched sounds.** `3x01H` is a ringer, but `Arc_03x01` (no `H`) is on the disc, so it plays that. Rascal's 8 is taken as 9: there is an `ANIM_HC_RASCAL_ARCS8`, but no `Rascal.Arc8` sound.

---

## Goal

Make Showdown's horseshoe corral, ROOM_P30_Horseshoe_Corral, play as the
original does. Chase B5 leads there. Until now it had the base class:
- nobody threw;
- the meter didn't sweep;
- the corral never sent the gang back to the chase.

## Background

The corral ([scooby-exe](../formats/scooby-exe.md#the-horseshoe-corral-wp-054)):
- **Scooby and Rascal** pitch horseshoes at three pegs, ten each, in turn.
- **Scooby's strength** is where the player stops a sweeping meter; it
  sweeps faster at higher levels. **Rascal's** is random.
- **A ringer** shows on its peg, and each of Scooby's is a snack.
- **After the last throws,** Chase B5.

The room's class has no tick of its own. Scooby, Rascal and each horseshoe
in the air are sprites with updates of their own, which the original's tree
tick calls right after each one's player.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`CorralRoom`:**
  - the placements;
  - Scooby and the meter;
  - Rascal;
  - the horseshoes and the pegs;
  - the turns;
  - the snack counter;
  - the way back to Chase B5.
- **The room's tick:** the tree walk with each sprite's update, for rooms
  with sprites that have one.
- **Claims:** they see their placement's sequence and place.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the class;
   - every sprite on entry, the counter, and the turn;
   - the meter's sweep at each level, with its ticks;
   - a throw by Scooby and Rascal's answer, with their ticks;
   - six chosen horseshoes, with their pegs, sounds, snacks and ticks;
   - a whole game, to Chase B5.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile starting in the corral: throws by
   both, a ringer by each, and the snack counter.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-horseshoe-corral-wp-054): the
  horseshoe corral.
