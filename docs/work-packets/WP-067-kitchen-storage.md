---
layout: default
title: "WP-067: Phantom's kitchen storage room"
---

# WP-067: Phantom's kitchen storage room: the screwdriver, the shield and the door (Gen 1)

**Status:** ✅ Done (2026-11-17)
**Phase:** 4 (game logic)
**Depends on:** WP-065 ✅ (the kitchen), WP-066 ✅ (Ewan's quiz), WP-031 ✅ (suspects met), WP-022 ✅ (movies)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-067-2026-11-17](../reference/pre-flight-WP-067-2026-11-17.md)

---

## Result (2026-11-17)

The reference is `wp068_ref.py`: WP-066's, plus the storage room, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art. It never runs the engine. At `script` level 3 the chase check now has 6 storage-room lines on Phantom (88 in all), and one on Showdown, which has no such room (224 in all).

The first run differed on one line, and the check was wrong. Its helper that waits for the room to change tested its result before ticking, so after the first door exit it returned that exit's movie (65) for the next three. The engine's log showed each exit queued with its own movie. The helper now clears the result first. The second run matched all 88 lines on Phantom and all 224 on Showdown, with no warnings.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **Placements.** In a new game the door, the screwdriver and the shield are requires objects at depth 0, and Fred stands at (284, 376). With the door begun and both items had: the door's `+0x70` (kept as its rollover) is the screwdriver, neither item is built, and Fred is at (140, 363). Open: no door. Hotspot 3 is a clickable with the open hand.
   - **Entry:** the door open, from the kitchen, `200A_`; back through the first door movie, `200D_`; otherwise nothing.
   - **The door:** with the arrow, movie 65, then `200B1_`, `200B2_`, then movie 65 again. With the screwdriver: `DoorClicked` 1, the screwdriver out of its slot, the arrow back, the door's `+0x70` the screwdriver, movie 62. Then movies 63 and 64, each back to this room, to `DoorClicked` 3.
   - **Fred takes the screwdriver** at tick 1, with `Fred_Takes_Screwdriver`, the screwdriver hidden. It is in the toolbar at tick 100 (his step 33); at tick 118 he is idle and `200C_` holds input.
   - **Daphne takes the shield** likewise, then `400A_`; with Brad met, `200G_`.
   - **Leaving** while either is taken still gives both.
   - **The hotspots:** 1 and 2 cycle their three lines; 3 says `200XA_`.
   - **The profile:** a new game's `DoorClicked=0`, and read back.
   - Showdown prints that it has no kitchen storage room.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The takings:** a click on the shield, and Daphne took it (`400A_`); a click on the screwdriver, and Fred took it (`200C_`).
   - **The door,** with the screwdriver in the toolbar: on the door, movie 62 and `200D_`; two more clicks, movies 63 and 64. The door stood open, with Fred beside it.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-066's run but for the clue name that varies by run. Phantom's differ only by the room's new profile key, the drawbridge's random keys, and Ewan's `CurrentQuestion`, which is drawn at random.
   - Fork commit [`cb312009e9`](https://github.com/barefootbetters/scummvm/commit/cb312009e9) (7 files staged by name) is pushed.

**Deviations and gaps:**

- **The tick clock's restart** (`0x437540`) when Fred or Daphne takes an item isn't kept, as in WP-057.
- **The door's `+0x70`** is set to the screwdriver once begun. The fork keeps it as the door's rollover, but live the cursor over the door stays the open hand, since the fork's hover over a requires object doesn't read it. What `+0x70` does in the original isn't traced.

**Found on the way:**

- **The screwdriver and shield are placed as inventory objects** in `object.ini`, but the class builds them as requires objects the arrow answers, so a gang member fetches each.
- **The packed exit's directions** run Daphne, Fred, Scooby, Shaggy, Velma (`0x401850`), so the door's `TURN_UL` is Fred's.
- **The open door has no way through** in this room's placements; the only way out is back to the kitchen.

---

## Goal

Port Phantom's kitchen storage room, `ROOM_P17_Kitchen_Storage`, the last
of the kitchen's group in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now it had the base class: the screwdriver and shield were picked up
as plain inventory objects, and the door did nothing.

## Background

The storage room ([scooby-exe](../formats/scooby-exe.md#phantoms-kitchen-storage-room-wp-067)):
- **Fred takes the screwdriver,** which the kitchen's grease
  ([WP-065](WP-065-kitchen.md)) needs.
- **Daphne takes the shield.**
- **The door** is worked open with the screwdriver over three movies.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`KitchenStorageRoom`:** the takings, the door and its movies, Fred's
  place at it, the hotspots, the profile key.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the placements by the door's state;
   - entry's scenes;
   - the door with the arrow and the screwdriver, and its movies;
   - the takings and leaving during them;
   - the hotspots and the profile key.

   Showdown prints that it has no kitchen storage room, as its reference
   does.
2. [x] Live, in Phantom: both takings; the door opened through its three
   movies.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new profile key. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-kitchen-storage-room-wp-067):
  the kitchen storage room.
