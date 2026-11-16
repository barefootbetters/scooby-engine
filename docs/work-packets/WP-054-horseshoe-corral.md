---
layout: default
title: "WP-054: Showdown's horseshoe corral"
---

# WP-054: Showdown's horseshoe corral: ten throws each, a snack a ringer (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-035 ✅ (the chase, Chase B5), WP-021 ✅ (sprites and their players), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-054-2026-11-16](../reference/pre-flight-WP-054-2026-11-16.md)

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

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - every sprite on entry, the counter, and the turn;
   - the meter's sweep at each level, with its ticks;
   - a throw by Scooby and Rascal's answer, with their ticks;
   - six chosen horseshoes, with their pegs, sounds, snacks and ticks;
   - a whole game, to Chase B5.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile starting in the corral: throws by
   both, a ringer by each, and the snack counter.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-horseshoe-corral-wp-054): the
  horseshoe corral.
