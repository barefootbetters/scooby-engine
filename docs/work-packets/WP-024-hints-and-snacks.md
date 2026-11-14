---
layout: default
title: "WP-024: Scrappy's hints and Scooby Snacks"
---

# WP-024: Scrappy's hints, Scooby Snacks and the speech lock (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic: the toolbar's helpers)
**Depends on:** WP-020 ✅ (characters, scenes, lip sync), WP-023 ✅ (the toolbar and the game cursor)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-024-2026-11-14](../reference/pre-flight-WP-024-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp024_ref.py`, written from the trace. It reads `TGIFILE.ART` through `tools/probe_art.py`, plus `object.ini` and the sound indexes, and never runs the engine. At `script` level 3 the engine logs one line per hint and per snack, and the reference prints the same lines: 126 on Showdown, 138 on Phantom, none different.

| Exit criterion | Result |
|---|---|
| 1. Every hint | ✅ 78 hints on Showdown and 82 on Phantom match. With Scrappy's cursor, each exit with a `scrappyid` shows the hint cursor (50 and 56 do). The wiggle plays, Scrappy says the clip, and the arrow comes back. An exit without one shows Scrappy's cursor, and a click puts the arrow back with no line. Each character with a `Global.Scrappy.<NAME>` clip gets its hint once met. Every hint clip a placed exit names exists. |
| 2. Every snack | ✅ 46 on Showdown and 54 on Phantom match. The box plays `Global.Snack_Box` and hands over the snack. Scooby or Shaggy plays `ANIM_<NAME><set>EAT_SNACK` and is idle again after 3 ticks a step (18, 27 or 45 ticks); the count goes from 1 to 0. Fred's `Global.Snack_GivenA_` follows where Fred is in the room, Velma's `…C_` where he isn't. No room has a line of its own. With no snacks left, the box has Scrappy say `Global.940B_1_SCRAPPY`. |
| 3. Live, Showdown | ✅ The run played its input through the engine's new `test_script`, with the window minimized; the host's mouse wasn't touched, since Jeff was at the machine. In Town Center: the van drove in, a click on Scrappy gave his cursor, and the road exit showed the hint. A click there played `Global.Scrappy.Town_Center_to_Street3`, and his lock was released when it ended. The snack went to Scooby, who ate it, and Fred said `Global.Snack_GivenB_1_FRED` (a random pick) while the toolbar drove off. Reopened, the empty box had Scrappy say `Global.940_1_SCRAPPY`. |
| 4. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit check (71 and 82), click check (191 and 174) and inventory check (24 and 33 lines) are identical to WP-023's run, so the speech lock left scene timing alone. Fork commit [`550cbb48fa`](https://github.com/barefootbetters/scummvm/commit/550cbb48fa) stages its 8 files by name, inside `engines/scooby/`, and is pushed. |

**Deviations and gaps:**

- **No suspect is met yet,** and no snacks are gained after the first. Both come from story rooms. Character hints show only through the check's `meetSuspect()`.
- **The room's entry scene** also holds off a hint in the original. The fork has no entry scenes yet.
- **A character clicked with the arrow** (its random reaction) is still not implemented. The original's characters show the open hand there; the fork's show the arrow.
- **A room's snack count** (`+0x88`) isn't kept. With the base threshold 0, every snack earns the line anyway.

---

## Goal

Make the last two working buttons of the toolbar act as the original's do.
Scrappy gives hints about exits and suspects. The snack box hands out Scooby
Snacks for Scooby and Shaggy to eat.

## Background

WP-023 drew Scrappy and the snack box but left their clicks out. In
`Scooby.exe` (details in
[scooby-exe](../formats/scooby-exe.md#scrappys-hints-and-scooby-snacks-wp-024)):

- **The speech lock** (game `+0x15C`). A scene holds it while it plays.
  Scrappy holds it while he speaks. Whoever finds it held waits or stays
  quiet, and the walk-off waits for it.
- **Hint mode.** Clicking Scrappy makes his cursor the game's.
  - Over an exit with a `scrappyid`, or a suspect already met, the cursor
    shows the hint and Scrappy wiggles.
  - A click there has Scrappy say the clip, with lip sync, and the arrow
    comes back.
- **Snacks.** The snack box makes the snack the cursor, or has Scrappy say
  there are none.
  - A snack on Scooby or Shaggy plays their `EAT_SNACK` once and counts
    down.
  - Fred or Velma then says a snack-given line, and an open toolbar drives
    off.

## Scope

**In scope (fork, `engines/scooby/` only):**

- The speech lock in `RoomScript`: scenes hold it, and the walk-off waits.
- `Character` state `0xF`: an action sequence once, then idle.
- In `Inventory`:
  - Scrappy's button, his talking and lip sync;
  - the hint rollovers and the wiggle;
  - hint clicks on exits and characters;
  - the snack box and its digits;
  - feeding and the snack-given line;
  - the met-suspects list.
- `Inventory::getCursorFor()`: the whole cursor rule in one place.
- A `test_script` config key, which plays input and saves screenshots for
  live tests without the host's mouse.
- A `script` level 3 check, from a new game and a fresh room each time:
  - every exit's hint;
  - every suspect's hint, once met;
  - a snack for every Scooby and Shaggy;
  - the empty snack box.

**Out of scope:**

- Who becomes a met suspect, and who gains snacks: story rooms
  (`0x40A8B0`, `0x407E00`).
- A character's reaction to the arrow (`0x404B70`, the random idles).
- The room's entry scene, which also holds off a hint.

## Exit criteria

1. [x] Every exit's hint (and every met suspect's) on both discs matches an
   independent reference: what the cursor shows, and what is heard and
   said.
2. [x] Every snack for Scooby and Shaggy matches it: the sequence, the line,
   the ticks until idle and the count.
3. [x] Live, in Showdown: a hint on an exit, a snack for Scooby with the
   snack-given line, and the empty snack box.
4. [x] Scooby-only build: 0 errors and 0 warnings. The exit, click and
   inventory checks are unchanged line for line. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): the speech lock, hint mode and
  snacks.
- [Integration §9](../02-SCUMMVM-INTEGRATION.md#9-debug-channels): the
  `test_script` key.
