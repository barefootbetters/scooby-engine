---
layout: default
title: "WP-056: The ghost spot"
---

# WP-056: The ghost spot: the scared gang's pan, then on to the town (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-027 ✅ (room classes and the title), WP-025 ✅ (the toolbar's rooms), WP-021 ✅ (the ghost), WP-032 ✅ (the music's fade)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-056-2026-11-16](../reference/pre-flight-WP-056-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp057_ref.py`: WP-055's, plus the ghost spot, written from the trace before the engine ran. It reads each title's start, pan, wrap and countdown from that title's own `Scooby.exe`, the placements and the background's size from the art, and whether the music is on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now starts with six ghost spot lines on both titles: 214 lines on Showdown (the earlier 208 and 6), and 7 on Phantom (6 and the line saying there is no chase). The first clean run matched them all.

**Exit criteria:**

1. **Against the reference:** ✅ Both titles:
   - **The class.** `ROOM_Ghost_Spot` builds the ghost spot's.
   - **Entry.** Layer 0 at x −1280; the background 1920 × 480 on both; the countdown 396; input held; `Ghost_Spot.Music` playing. Scooby and Daphne at depths 1 and −1, hit by their cels, under the root. Shaggy, Velma and Fred as the default path builds them: depth 0, hit by their step polygon.
   - **The pan.** x −1280, −1274, −1274, −1268, … by tick; −98 after tick 395; on at tick 396 to Showdown's `ROOM_P01_Town_Center` or Phantom's `ROOM_P04_Town`, the toggle back at 0.
   - **A skip** after 10 ticks: on at tick 11, the toggle left at 1, so the next visit's background moves on its first tick.
   - **A click** while input is held is the skip key.
   - **The towns.** Showdown's is Town Center from every room. Phantom's is Below Balcony from its five castle rooms, else Town.
2. **Live:** ✅ Through `test_script`, minimized:
   - **Showdown.** In Street 3, with the ghost's chance at 1, a click on hotspot 2 calls the ghost. It plays out, and the ghost spot pans while the gang runs. Then Town Center, where Fred starts `Global.Ghost_SpotB_`. In a run started in the ghost spot, Escape after 3 seconds goes on at once to Town Center.
   - **Phantom.** Through the ghost spot to `ROOM_P04_Town`, where Daphne starts `Global.Ghost_Spot_`.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **The skip key** is Escape, Space or a click, as on the title; the original's input slot 5 isn't traced to keys. The original takes it only once the slot has been up since entry (`0x475F00`). A key press here always has been.
- **The skip** is seen in the next tick, as the original reads the slot in its tick.

**Found on the way:**

- **The gang never goes back** to the room the ghost scared them in: Showdown always goes on to Town Center, Phantom to its Town.
- **Phantom's choice of town looks at the room loaded,** which from the ghost spot is the ghost spot, so its castle branch never fires from here. In Showdown's decompile nothing else calls game vtable `+0x64`.
- **The class's two flags** (`+0xBC`, `+0xBD`) would leave the gang unbuilt, but nothing clears them.
- **Phantom's title and ghost spot** say 1280 × 480 in their headers, but their backgrounds are 1920 wide.
- **Corrected in [WP-058](WP-058-souvenir-shop.md):** the profile check's imported clue name (`CluesFound1`) also differs between two runs of the same build, so this WP's change can't be shown to have caused the flip.

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

1. [x] Both titles match an independent reference line for line:
   - the class;
   - the entry: the pan's start, the background's size, the countdown,
     the music, and each sprite;
   - the pan to the town, with its ticks;
   - a skip, and the toggle on the next visit;
   - a click while input is held;
   - where each title goes on to, by the room loaded.
2. [x] Live: in Showdown, from a clickable's ghost through the ghost spot
   to Town Center, and a skip key; in Phantom, through the ghost spot to
   its town.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-ghost-spot-wp-056): the ghost
  spot, and both titles' game vtable `+0x64`.
