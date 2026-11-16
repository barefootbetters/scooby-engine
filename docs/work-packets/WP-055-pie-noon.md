---
layout: default
title: "WP-055: Showdown's Pie Noon"
---

# WP-055: Showdown's Pie Noon: pies until the clock chimes, a snack a ghost hit (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-054 ✅ (the tree walk with sprite updates), WP-051 ✅ (the saloon), WP-021 ✅ (sprites and their hit tests), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-055-2026-11-16](../reference/pre-flight-WP-055-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp056_ref.py`: WP-054's, plus Pie Noon, written from the trace before the engine ran. It reads the placements and step counts from the art, and which sounds are on the disc from the sound archives' indexes. It simulates the pies and runners with floats rounded as the original stores them, and decodes the cels from the art for every hit test. It never runs the engine. At `script` level 3 the chase check now logs 208 lines on Showdown: the earlier 196 and 12 for Pie Noon. On Phantom both print the one line saying there is no chase.

The first run differed on 4 lines. Three were the check's or the reference's:
- the ghost's states counted the entry's sounds;
- the reference still printed the runner's step at its hit;
- it showed Scooby's pie before its first flight, which comes in the tick he throws it.

The fourth was the engine's. The clock's chime and its last tock play in the same tick, and the fork's single handle for `Sfx.dat` let the tock cut the chime, so the room left at once. The original gives each clip a buffer of its own (`0x43CC20`). Effects now play on handles of their own, at most 16 at a time, and the second clean run matched all 208.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The stage.** Scooby 4–605 at 635, the ghost's places 221, 288, 338, 403 at 210, the five starts by y, the four slopes, the lanes (the front one −553 to 1017), and the edges at three depths.<br>**Entry.** The overlays one in front of the middle and back lanes, the clock stopped on step level × 15 (0, 15, 30), the counter on 01, Scooby stopped at his walk's left end, the ghost idle half way along its row; none of the gang's places built; the Music and the Intro.<br>**The ghost's states.** Each entered from idle: hit, a turn (a throw in the intro turns instead), walking, smoke at its place or along its row, hidden.<br>**Runners.** Fred right across lane 1 and Velma left across lane 0, each gone at tick 101 and 100, deleted, its slot free.<br>**The ghost hit.** A pie from x 276 flies 18 ticks, on step 9 for its last three (frame 9, read past `PIETHROW`'s end). It hits the idle ghost: its `HIT`, `Ghost_Hit` and a `Good_Job` line, snacks to 2, the pie on `PIEHIT3`, gone at tick 33, the ghost moving on at 34.<br>**Runner hits.** Fred: a miss at tick 50 (`FRED_Miss` isn't on the disc), a hit at 51, `Splat.0`, running again at 78 after 26 hit ticks. Daphne: a hit at 47 and `Splat.1`.<br>**Scooby hit.** A ghost's pie from x 240 hits him at tick 21: his `HIT_L`, `Scooby_Hit`, licking at 27, walking at 63.<br>**Scooby walk.** After the mouse at 15 a tick, stopped on step 7. No throw in the intro; then three throws, `Scooby_Throw.2`, `.3`, `.1`, one per press.<br>**The ghost's throw.** Its pie at tick 222 from its place, `Ghost_Throw` and a `Lookout` line, idle again at 234.<br>**The clock.** The intro over at tick 216, Velma on at 228, the chime at 2340 after 60 ticks and tocks; the room stays while it plays, then the saloon. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from a profile starting in Pie Noon, with eight throws at chosen places:<br>**Scooby** walked and threw five times, the three throw lines in turn; the other three presses came while he was hit or throwing. He was hit and licked the pie off five times.<br>**Pies** splatted Velma (`Splat.0`), hit the ghost twice (the counter from 01 to 03), and missed Fred twice and Shaggy twice.<br>**The ghost** threw, smoked and hid.<br>**The chime** came after 30 ticks and 30 tocks, then the saloon. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Phantom's other checks are identical to WP-054's run. On Showdown one line differs, the clue name the profile check imports (`SHERIFF_SPURS` for `SHERIFF_FEATHER`). Pie Noon now plays during the exit and click checks and draws random numbers there: its ghost throws and Shaggy is splatted before the profile check runs. Fork commit [`6f1eaf9113`](https://github.com/barefootbetters/scummvm/commit/6f1eaf9113) (9 files staged by name) is pushed. |

**Deviations and gaps:**

- **`rand()`:** the gang's lanes and sides, the ghost's choices and lines come from the engine's own random source.
- **The mouse** is the engine's position and button; pans (from the pie's or the ghost's x) are ignored, as everywhere in the fork.
- **At most 16 earlier sound effects** play at once (ScummVM's mixer slots); DirectSound had no such limit.
- **Voice clips** still share one handle; the original gives each a stream.
- **A runner's `_Hit.X`** after 72 hit ticks is implemented but not checked.

**Found on the way:**

- **The audit counted only the room's own functions** (602 instructions); the game is in four sprite classes.
- **Sprites marked done are deleted** by a sweep after the walk (`0x431190`), so the corral's spent horseshoes go too (corrected in [WP-054](WP-054-horseshoe-corral.md)).
- **A pie steps one past its last step.** Scooby's shows frame 9, a 3 × 5 speck, as the original reads past the sequence's end.
- **The level changes nothing but the clock's face in the intro:** the clock then runs from step 1 at every level.
- **The splat sound's number is global** (`0x475F08`) and runs 0 to 4; the old value is pushed before the increment.
- **Every hit and miss line is on the disc but `FRED_Miss`.**

---

## Goal

Make Showdown's Pie Noon, ROOM_P32_Pie_Noon, play as the original does. The
saloon builds it once Artie is free. Until now it had the base class:
- nobody moved and nothing was thrown;
- the clock never ran;
- the room never sent the gang back to the saloon.

## Background

Pie Noon ([scooby-exe](../formats/scooby-exe.md#pie-noon-wp-055)):
- **Scooby** walks along the front of the stage after the mouse and throws
  a pie at each press.
- **The ghost** walks along the back, throws pies back, and hides in smoke.
  A pie that reaches it is a snack.
- **The rest of the gang** run across three lanes in between, and pies splat
  on them.
- **When the clock chimes,** back to the saloon.

The pies fly in a perspective the room works out from its placements: four
edges from the ghost's row to Scooby's. Scooby, the ghost and the runners
update themselves in the tree walk; the room's tick moves the pies.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`PieNoonRoom`:**
  - the placements and the stage;
  - Scooby, the ghost, the runners and the pies;
  - the clock and the way back to the saloon;
  - the snack counter.
- **Sound:** a handle per sound effect, as the original's buffer per clip.
- **The tree:**
  - the walk as the original's list;
  - the sweep after it, which deletes sprites marked done;
  - a step past a sequence's last.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the class;
   - the stage: its places, slopes, lanes and edges;
   - every sprite on entry, and the clock by level;
   - the ghost's states;
   - two runners across their lanes;
   - a pie on the ghost, two on runners and one on Scooby, each with its
     flight, ticks, sounds and what follows;
   - Scooby after the mouse, and his throws;
   - the ghost's throw;
   - the clock to the chime and the saloon.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile starting in Pie Noon: Scooby walks
   and throws, and the clock's chime leads back to the saloon.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#pie-noon-wp-055): Pie Noon, the
  tree's sweep, and a step past a sequence's last.
