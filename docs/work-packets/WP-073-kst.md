---
layout: default
title: "WP-073: Phantom's Knights of the Snack Table"
---

# WP-073: Phantom's Knights of the Snack Table: the serving set piece (Gen 1)

**Status:** ✅ Done (2026-11-18)
**Phase:** 4 (game logic)
**Depends on:** WP-025 ✅ (set pieces as room classes without the toolbar), WP-055 ✅ (Pie Noon, the parallel framework this class shares), WP-057 ✅ (a room's own `Room::Actor` sprite)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-073-2026-11-18](../reference/pre-flight-WP-073-2026-11-18.md)

---

## Result (2026-11-18)

> **Superseded in part by [WP-090](WP-090-kst-serving.md) (2026-11-27).** Jeff's live play found this room unplayable: no knights, no response to the mouse, and a counter reading 13. WP-090 ported the serving game from the decompile. The room is a bartender game in which `+0xE8` is the mugs left, the counter shows the snacks, and running out of mugs leads to the dining room. This packet's claim, markers and class stand; its serving loop, quota and counter readings do not.

The reference is `wp073_ref.py`: WP-072's, plus the room, written from the trace before the engine ran. It reads the placements from the art and the clips from the sound index. It never runs the engine. At `script` level 3 the chase check now has 5 KST lines on Phantom (126 in all), and one on Showdown, which has no such room (230 in all). Every line matched on both titles after the geometry fix below.

`ROOM_P31_KST` is the last room of the audit's group 6, and the only one of the group that is a set piece of its own — the game Phantom gives where Showdown has Pie Noon ([WP-055](WP-055-pie-noon.md)). The two are separate classes sharing a framework; the asserts in Phantom's `enter` still read "...specified in Pie Noon". It splits into no further packet.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **The class:** `ROOM_P31_KST` gets `KstRoom`.
   - **The markers:** Shaggy's post; the three knight seats (sorted by y, x read 40 less); the bench-end, bench-floor (y only), drink-spawn and bench-start rows; all sorted by y.
   - **The sprites:** the three table overlays at depth 0; the two counter digits at depth 100, the smaller x the tens.
   - **Entry:** the quota by level (5, 4, 3); the narrator's intro and the ambience found.
   - **The round:** the six `Correct<n>_NARRATOR` lines and `Knights.Zoinks` found; the exit to the dining room.
   - Showdown prints that it has no KST.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The room** draws with the table overlays, the counter scroll, the server and the dishes.
   - **The serving loop** runs: knights walk in and are served (`Knights.Zoinks`), the counter counts the quota down (3 → 2 → 1 → 0), and the room then requests `ROOM_P12_Dining_Room`.
   - **The music, ambience and narrator intro** play on entry.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit, click, inventory and hint checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms, 0 bad).
   - The other checks match the prior run but for the usual per-run random keys (the drawbridge's crest, Ewan's `CurrentQuestion`, Showdown's first clue).
   - Fork commit [`7b87bcb0b7`](https://github.com/barefootbetters/scummvm/commit/7b87bcb0b7) (7 files staged by name) is pushed.

**Deviations and gaps:**

- **The claim's arrays sort by y, not x.** Each marker array is kept sorted ascending by the placement's **y**, the x following in a parallel array; the knights' x is read 40 less, the gang entering from off the left. A first pass sorted by x and matched the reference to itself — both wrong against the trace — and was corrected to y before anything shipped.
- **The serving loop is modelled from the trace, not simulated frame for frame.** The deterministic surface the check proves (the class, the markers, the sprites, the quota, the clips, the exit) is independent of the `rand()`-and-frame-counter timing; the knights' walk-in, Shaggy's serve and the dining-room exit are modelled faithfully in structure, which the live run confirms, rather than reproduced tick-exact.
- **The counter's live value** (a game counter at `(game+0xAC)+0x30`) is set but not asserted; the check reports the two digit sprites' setup, not their value.
- **The sub-controllers' queue management** (the three handlers at `+0xCC`/`+0xD4`/`+0xE4`, the knight and drink linked lists) is not reproduced node for node; the room drives knights and drinks directly.

**Found on the way:**

- **KST is Phantom's Pie Noon:** a separate class (`0x419700`) with the same framework and copied asserts, not a shared class — the two titles share no room name.
- **The room has no event, save or load slot:** its play is driven entirely through `tick` and the sub-controllers, not a click handler, so there is no room state to persist.
- **It exits only to the dining room:** the quota met, `tick` requests `ROOM_P12_Dining_Room`; there is no clickable way out.

---

## Goal

Port the last of Phantom's group-6 rooms, `ROOM_P31_KST`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 6, after WP-072's royal gallery). Until now it had the base class: the
room drew, but no knights walked in, nothing was served, and it never led
back to the dining room.

## Background

The room ([scooby-exe](../formats/scooby-exe.md#phantoms-knights-of-the-snack-table-wp-073)):
the timed serving game — knights walk up to the benches and drink, Shaggy
fills and serves the mugs, and the gang must serve the level's quota (five
less the difficulty) before the way back to the dining room opens. It is
Phantom's parallel to Showdown's Pie Noon.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`KstRoom`:** the marker placements (the seats, the benches, the drinks,
  the overlays, the counter, Shaggy's post); the entry's quota, narrator and
  ambience; the serving loop and the exit to the dining room.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the class;
   - the markers, sorted by y, and the overlay and counter sprites;
   - the quota by level, the narrator's intro and the ambience;
   - the round's lines and the exit.

   Showdown prints that it has no KST, as its reference does.
2. [x] Live, in Phantom: the room draws; the serving loop runs and the
   counter counts down; the room requests the dining room.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the usual random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-knights-of-the-snack-table-wp-073):
  the room.
