---
layout: default
title: "WP-047: Showdown's back alley"
---

# WP-047: Showdown's back alley: the snacks before the General Store (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-045 ✅ (the General Store), WP-038 ✅ (the bank vault), WP-024 ✅ (snacks), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Two hours
**Pre-flight:** [pre-flight-WP-047-2026-11-15](../reference/pre-flight-WP-047-2026-11-15.md)

---

## Goal

Make Showdown's back alley play as the original does. It is the second
room from the [room class audit](../reference/room-class-audit-2026-11-15.md).
Until now:
- the gang went into the General Store without the snacks;
- the alley's hotspots had no lines or frights;
- no one walked in.

## Background

The back alley ([scooby-exe](../formats/scooby-exe.md#the-back-alley-wp-047))
lies between the bank vault and the General Store:
- **On entry:** rattlesnakes are heard in the distance.
- **The way into the store:** the gang won't go in until they've had
  level + 2 snacks here, as in the Sheriff's office.
- **The hotspots:** hotspot 3 has two lines, at random, and hotspot 1
  scares Daphne and Scooby.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BackAlleyRoom`:** the snacks before the store; the walk-ins; the
  snakes' sound; hotspot 3's lines and hotspot 1's fright.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - the walk-ins from the store, the vault and the open safe; the
     snakes' sound; the hotspots; the opening;
   - hotspot 3's A without a line and its B with one, and hotspot 1's
     fright on its step 8, with their ticks;
   - the way into the store by level, the flash, and the snacks that let
     the gang through.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form: hotspot
   3's line, hotspot 1's fright, the snack gate, two snacks, and the way
   into the store.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-back-alley-wp-047): the back
  alley.
