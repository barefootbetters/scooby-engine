---
layout: default
title: "WP-056: The ghost spot"
---

# WP-056: The ghost spot: the scared gang's pan, then on to the town (Gen 1)

**Status:** 🚧 In progress (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-027 ✅ (room classes and the title), WP-025 ✅ (the toolbar's rooms), WP-021 ✅ (the ghost), WP-032 ✅ (the music's fade)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-056-2026-11-16](../reference/pre-flight-WP-056-2026-11-16.md)

---

## Result (2026-11-16)

Pending: the check against the reference, the live run and the regression.

---

## Goal

Make `ROOM_Ghost_Spot` play as the original does, in both Gen 1 titles.
The game goes there once the ghost has scared the gang. Until now it had
the base class:
- the background stood still;
- the game stayed there for good.

## Background

The ghost spot ([scooby-exe](../formats/scooby-exe.md#the-ghost-spot-wp-056)):
- **The gang runs** while the town pans behind them, 6 pixels every other
  tick, for 11 seconds with input held.
- **Then the game goes on** to its town: Showdown's Town Center, Phantom's
  Town. A skip key goes there at once.

The class is the same code in both titles. Only the game's choice of town
(game vtable `+0x64`) differs.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`GhostSpotRoom`:**
  - the entry: the pan's start, the countdown, the music fade stopped;
  - the placements: Scooby and Daphne;
  - the tick: the toggle, the pan, and on to the town;
  - the skip key.
- **A `script` level 3 check** against an independent reference, at the
  start of the chase check, on both titles.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the class;
   - the entry: the pan's start, the background's size, the countdown,
     the music, and each sprite;
   - the pan to the town, with its ticks;
   - a skip, and the toggle on the next visit;
   - a click while input is held;
   - where each title goes on to, by the room loaded.
2. [ ] Live: in Showdown, from a clickable's ghost through the ghost spot
   to Town Center, and a skip key; in Phantom, through the ghost spot to
   its town.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-ghost-spot-wp-056): the ghost
  spot, and both titles' game vtable `+0x64`.
