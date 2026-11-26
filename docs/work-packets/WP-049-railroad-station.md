---
layout: default
title: "WP-049: Showdown's railroad station"
---

# WP-049: Showdown's railroad station: Gummy, his dentures and his clue (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-038 ✅ (the dentures), WP-031 ✅ (suspects and clues), WP-022 ✅ (movies), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-049-2026-11-15](../reference/pre-flight-WP-049-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp050_ref.py`: WP-048's, plus the station, written from the trace before the engine ran. It reads the placements, positions, step counts, clickable states and `priority=` keys from the art and object.ini, and which scenes are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 160 lines on Showdown: the earlier 155 and 5 for the station. The reference prints the same 160, none different, on the first run. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **Who is here.** In a new game there is no Gummy, no donkey and no way to the chase. Shaggy walks in DR from Street 2, and the opening is `110A_`. With Artie met, Gummy SLEEPS (state 16) and the donkey idles. Once the puzzle is solved, the donkey has hit type 0 and the opening is the first hint, `220C_`. With his clue given, both stand 100 further right (x 397 and 465), and the way to the chase is built. `Intro_` has no lines on the disc, so it counts as played. Hotspots 2 and 3 are at depths 100000 and 200, their `priority=`.
   - **The clicks.** Before the puzzle, Gummy and the donkey lead to ROOM_Gummy. After it, Gummy's hints go `220C2_`, `220C3_`, `220C_`, `220C2_`, since arrival took the first. With the dentures had, they go `220C2_`, `220C_`, `220C2_`. With his clue given, one of `Global.1000GA_`–`GC_` plays, not held. The class doesn't take a click on Gummy with the hammer, or with the dentures before the puzzle.
   - **The dentures.** They are used up and the arrow is back. The gang goes out to the station itself with `220D_` and movie 30. Back, his clue is given and the opening is `220DP_`. Gummy gives on tick 1 (16 steps, input held), and the thanks come on tick 49.
   - **The hotspots.** Hotspot 2 gives `HOTSPOT2A_` on its B and `HOTSPOT2B_` on its C. Hotspot 3's C scares Scooby on tick 25, its step 8.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, from profiles in the original's form:
   - **Asleep.** With Artie met, Gummy slept. Clicked, he sent the gang to ROOM_Gummy.
   - **The dentures.** With the puzzle solved, Gummy's click gave `220C2_`. The dentures from the toolbar gave `220D_` and movie 30 (57 frames). Back, `220DP_` played, and Gummy gave his clue. The thanks took the gang to the suspects.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **Gummy's and the donkey's clicks act on the press,** like every click in the fork. The original reads the release and their clicked flags in its tick.
- **The original's reset skips the base reset.** `0x420820` doesn't call `0x40CD20`, so a new game leaves the station's own base state (its opening's played flag and snacks given) as it was. The fork resets the base state of every room on a new game. The station has no snack gate, and its opening is set unplayed on every arrival, so nothing changes in play.
- **ROOM_Gummy's music isn't on the disc.** Its constructor names `Gummy.Music`, and no sound archive has it. The live run logged it as missing, as the original's lookup would.

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

1. [x] Showdown matches an independent reference line for line:
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
2. [x] Live, in Showdown, from profiles in the original's form:
   - Gummy asleep, and his click to ROOM_Gummy;
   - a hint, then the dentures, movie 30, his clue and the suspects.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-railroad-station-wp-049): the
  railroad station.
