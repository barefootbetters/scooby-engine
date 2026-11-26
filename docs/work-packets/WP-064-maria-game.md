---
layout: default
title: "WP-064: Phantom's Maria game"
---

# WP-064: Phantom's Maria game: balance the dishes on her trays (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-063 ✅ (the dining room), WP-055 ✅ (a set piece's engine sprites), WP-037 ✅ (dragging with the mouse), WP-025 ✅ (no toolbar)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-064-2026-11-16](../reference/pre-flight-WP-064-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp065_ref.py`: WP-063's, plus Maria's game, written from the trace before the engine ran. It flies the items itself, rounding to 32-bit floats after each step as the original stores them. It reads the art's names and the disc's clips, and never runs the engine. At `script` level 3 the chase check now has 10 Maria lines on Phantom (67 in all), and one on Showdown, which has no Maria game (221 in all).

The first run matched all 67 lines on Phantom and all 221 on Showdown, with no warnings.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **The items,** 40 draws at each level: 6, 8 and 10 of them. Each is drawn, weighs 2, 1 or 4 as a cup or plate, rests on a floor of 443–469 at x 20–619 and depth floor − 393, and the set always splits into two equal trays.
   - **The room:** Maria `HAPPY`, stopped on step 2 at depth −10; the way out to the dining room; the hour's timer.
   - **A throw** from (300, 200) at (4, 0): it lands at tick 32 at (428, 460), `Maria.Spin` while it flies and stopped a tick after, then `Maria.Floor.Cup`.
   - **The right wall:** x 639, its speed −6, `Maria.Bounce`; 633 the next tick.
   - **Carried:** taken with the cursor hidden and its offset kept, then let go at (360, 430). It is thrown at (4, −2), spinning forwards, with `Maria.Throw.Cup`, and the cursor shows again.
   - **Into the first tray** from (200, 120): it lands at tick 14 with `Maria.Place.Cup`. Maria is `EXCITED` on step 1 and the cup moves with the tray to (221, 170), at depth 1. She's done balancing a tick later, and `HAPPY` again at tick 50.
   - **The top item only:** of two in a tray, the bottom one can't be taken, and the top one goes back to depth 50.
   - **Tipped over** by 5: Maria goes to steps 1 and 0, then everything falls off at tick 3, back at its floor's depth, and she comes back to 2.
   - **Won** with every item in a tray: `MariaPuzzle` at once, input held; 73 ticks later the way back to `ROOM_P12_Dining_Room`.
   - Showdown prints that it has no Maria game.
2. **Live, Phantom:** ✅
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-063's run but for the clue name that varies by run, and Phantom's but for the drawbridge's random keys.
   - Fork commit [`83b49202d2`](https://github.com/barefootbetters/scummvm/commit/83b49202d2) (7 files staged by name) is pushed. Its item log line came after the check run; the room check and the live runs used the final build.

**Deviations and gaps:**

- **An item's stop step** (`+0x88`) isn't set by its constructor in the original. The fork starts it at −1, so an item's `IDLE` loops until it is first thrown.
- **A click** is the fork's button going down; the items read the button coming up (game `+0x20` bit 4), as in earlier rooms.
- **The hour's timer** (129600 ticks) isn't run through by the check.
- **The random draws** are the fork's random source, not the C library's `rand()`; the check tests what holds for every draw.

**Found on the way:**

- **Every group the game makes balances,** so the set always splits into two equal trays.
- **A difference past 4 empties both trays,** once Maria has tilted all the way, scattering every item back to the floor.
- **WP-063 put the way back at 72 ticks;** it is 73, since the timer is checked before it counts down. Corrected in [scooby-exe](../formats/scooby-exe.md#phantoms-dining-room-wp-063).

---

## Goal

Port Phantom's Maria game, `ROOM_Maria`, split off from
[WP-063](WP-063-dining-room.md). Until now it had the base class: nothing
in it set `MariaPuzzle`, so Maria never gave her clue.

## Background

Maria's game ([scooby-exe](../formats/scooby-exe.md#phantoms-maria-game-wp-064)):
cups and plates on the floor are carried and thrown onto Maria's two trays.
She tilts by the difference in weight; past four steps everything falls
off. Every item on a tray and the trays equal wins it.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`MariaGameRoom`:** the items, carrying and throwing, the flight and the
  landings, the trays and Maria's balance, the win and the way back.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the items each level makes;
   - Maria, the way out, the timers;
   - a throw, a wall, an item carried and let go;
   - an item into a tray, Maria's tilt and her return to `HAPPY`;
   - the top item only; a tip-over;
   - the win and the way back.

   Showdown prints that it has no Maria game, as its reference does.
2. [x] Live, in Phantom: a game played to a win, and Maria's clue after.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-maria-game-wp-064):
  Maria's game.
