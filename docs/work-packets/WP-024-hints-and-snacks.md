---
layout: default
title: "WP-024: Scrappy's hints and Scooby Snacks"
---

# WP-024: Scrappy's hints, Scooby Snacks and the speech lock (Gen 1)

**Status:** 🚧 In progress
**Phase:** 4 (game logic: the toolbar's helpers)
**Depends on:** WP-020 ✅ (characters, scenes, lip sync), WP-023 ✅ (the toolbar and the game cursor)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-024-2026-11-14](../reference/pre-flight-WP-024-2026-11-14.md)

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

1. [ ] Every exit's hint (and every met suspect's) on both discs matches an
   independent reference: what the cursor shows, and what is heard and
   said.
2. [ ] Every snack for Scooby and Shaggy matches it: the sequence, the line,
   the ticks until idle and the count.
3. [ ] Live, in Showdown: a hint on an exit, a snack for Scooby with the
   snack-given line, and the empty snack box.
4. [ ] Scooby-only build: 0 errors and 0 warnings. The exit, click and
   inventory checks are unchanged line for line. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): the speech lock, hint mode and
  snacks.
- [Integration §9](../02-SCUMMVM-INTEGRATION.md#9-debug-channels): the
  `test_script` key.
