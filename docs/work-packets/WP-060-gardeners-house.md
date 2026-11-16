---
layout: default
title: "WP-060: Phantom's gardener's house, garden and plaque"
---

# WP-060: Phantom's gardener's house, garden and plaque: the crest's order (Gen 1)

**Status:** 🚧 In progress (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-057 ✅ (Phantom's story values), WP-058 ✅ (`checkOpening`), WP-031 ✅ (Big Head), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-060-2026-11-16](../reference/pre-flight-WP-060-2026-11-16.md)

---

## Result (2026-11-16)

Pending: the check against the reference, the live run and the regression.

---

## Goal

Port three of Phantom's rooms, the third step in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order):
- **ROOM_P05_Gardeners_House:** its plaque, its door and its openings.
  Until now the plaque did nothing, and the way to the garden was always
  open.
- **ROOM_Garden_Plaque:** the crest puzzle. Until now its buttons did
  nothing.
- **ROOM_P06_Garden:** its tracks, which until now were there from the
  start and said nothing.

## Background

The gardener's house ([scooby-exe](../formats/scooby-exe.md#phantoms-gardeners-house-garden-and-plaque-wp-060)):
- **Its plaque** gives Big Head's lines until a ball is found. After that
  it leads to a crest of four buttons, which must be pressed in the order a
  new game drew.
- **Solved,** the door to the garden opens. Coming back, the gang's opening
  says how it went.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`GardenersHouseRoom`:** the placements, the openings by where the gang
  came from, the walk-ins, the door, the screams, and the plaque.
- **`GardenPlaqueRoom`:** the buttons, the mouse over them, the crest's
  order, and back to the house.
- **`GardenRoom`:** the tracks and their lines.
- **A `script` level 3 check** against an independent reference.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the classes;
   - the house's placements, unsolved and solved, with its walk-ins;
   - the openings and screams while `Screaming`;
   - the returns from the plaque: untried, four wrong tries, solved;
   - the plaque's Big Head lines, and the puzzle once a ball is found;
   - the garden's tracks and lines;
   - the plaque's buttons, the mouse over one, a right order with a
     button pressed twice, a wrong order, and a new game.

   Showdown prints that it has no gardener's house.
2. [ ] Live, in Phantom: the house's plaque to the crest, the buttons
   pressed in order, and back to the house with the door opening.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-gardeners-house-garden-and-plaque-wp-060):
  the gardener's house, the garden and the plaque.
