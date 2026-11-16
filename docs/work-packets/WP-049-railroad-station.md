---
layout: default
title: "WP-049: Showdown's railroad station"
---

# WP-049: Showdown's railroad station: Gummy, his dentures and his clue (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-038 ✅ (the dentures), WP-031 ✅ (suspects and clues), WP-022 ✅ (movies), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-049-2026-11-15](../reference/pre-flight-WP-049-2026-11-15.md)

---

## Goal

Make Showdown's railroad station play as the original does. It is the
fourth room from the [room class audit](../reference/room-class-audit-2026-11-15.md).
Until now:
- Gummy and his donkey were always there;
- the dentures did nothing;
- his clue never came;
- the way to the chase was always open.

Gummy's whistle puzzle, ROOM_Gummy, is its own WP.

## Background

The station ([scooby-exe](../formats/scooby-exe.md#the-railroad-station-wp-049)):
- **Gummy and his donkey** are there once Artie has been met.
- **Before his whistle puzzle** Gummy sleeps, and he or the donkey leads to
  it.
- **After it** he has hints until he gets his dentures. Given them, the
  station plays again through movie 30. He then gives his clue, and the
  thanks lead to the suspects.
- **The way to the chase** opens once his clue has been given.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`RailroadStationRoom`:**
  - Gummy and the donkey, and what clicking them does;
  - the dentures, the clue and the thanks;
  - the hints and lines;
  - the way to the chase;
  - the hotspots;
  - the openings.
- **`Room::getOffsetX` and `getOffsetY`,** to move Gummy and the donkey.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **ROOM_Gummy,** the whistle puzzle: its own WP.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - who is here by Artie, the puzzle and his clue; the way to the chase;
     the hotspots; the openings;
   - Gummy and the donkey clicked before the puzzle; his hints after it,
     with and without the dentures had; his lines after his clue; and the
     clicks that aren't the class's;
   - the dentures, movie 30, his clue, GIVES and the thanks, with their
     ticks;
   - hotspot 2's lines and hotspot 3's fright, with their ticks.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from profiles in the original's form:
   - Gummy asleep, and his click to ROOM_Gummy;
   - a hint, then the dentures, movie 30, his clue and the suspects.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-railroad-station-wp-049): the
  railroad station.
