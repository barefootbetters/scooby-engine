---
layout: default
title: "WP-072: Phantom's royal gallery and magic mirror room"
---

# WP-072: Phantom's royal gallery and magic mirror room: the hung mirror, the red ball and the snack gate (Gen 1)

**Status:** ✅ Done (2026-11-18)
**Phase:** 4 (game logic)
**Depends on:** WP-061 ✅ (the room of doors' `JesterControl`, which the gallery embeds), WP-047 ✅ (a way that wants snacks), WP-057 ✅ (a room's own animated sprite), WP-067 ✅ (a character acting after a line)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-072-2026-11-18](../reference/pre-flight-WP-072-2026-11-18.md)

---

## Result (2026-11-18)

The reference is `wp073_ref.py`: WP-071's, plus the two rooms, written from the trace before the engine ran. It reads the placements from the art. It never runs the engine. At `script` level 3 the chase check now has 6 gallery lines on Phantom (121 in all), and one on Showdown, which has no such rooms (229 in all). Every line matched on both titles on the first run after one fix in the check (its `findSprite` matched the sprite's label, not its object name, so it missed the mirror).

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **The classes:** each room gets its own.
   - **The gallery's entry:** from the dining room Velma walks in, from the magic mirror room Shaggy; the way on needs the level's snacks plus two (2, 3, 4).
   - **The mirror:** bare it is stopped and the way on hidden. Clicked, it cycles `210A_`, `210A1_`, `210A2_`. The found mirror used on it, Shaggy hangs it (`Shaggy_Puts_Mirror`), it loops, the way on opens, `210B_` by level plays and the snack box flashes. On return it is hung for good.
   - **The red ball** shown: `RedBallFound` set, and the gallery re-entered through movie 3.
   - **The way to the magic mirror room:** with too few snacks it blocks, `210C_` by level and the snack box; with enough, it lets through.
   - **The magic mirror room:** its hum; `HOTSPOT2` toggles `310X1_`/`310X2_`, `HOTSPOT3` holds for `HOTSPOT3_`, `HOTSPOT4` cycles `310X2_`/`310XA2_`/`310XA3_`; the fifth hotspot and the skull are sprites, the four cameras exits.
   - Showdown prints that it has no gallery.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The gallery** draws with the mirror, the hotspots, the red ball and both ways out hit-testable.
   - **The bare mirror** clicked: `Royal_Gallery.210A_`.
   - **The way to the magic mirror room** clicked with no snacks: `Royal_Gallery.210C_`, blocked.
   - **The found mirror used:** Shaggy hangs it (`Royal_Gallery.Shaggy_Puts_Mirror`), the mirror shows and the way on opens.
   - **The magic mirror room** draws, and its hotspots give their lines.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit, click, inventory and hint checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms, 0 bad).
   - The other checks match WP-071's run but for the usual per-run random keys (the drawbridge's crest, Ewan's `CurrentQuestion`, Showdown's first clue).
   - Fork commit [`df99151f9b`](https://github.com/barefootbetters/scummvm/commit/df99151f9b) (7 files staged by name) is pushed.

**Deviations and gaps:**

- **The gallery embeds the room of doors' `JesterControl` by value** (`+0xC8`); it is the same class, not a copy, entered and ticked each visit.
- **The hung mirror is a claimed requires-object placement the class drives** (`setPlayer`), as the drawbridge's flags are, rather than the original's separately allocated sprite (`0x402D90`).
- **The game's pending-opening string** the mirror's use writes (`+0x8E`) names no clip and has no effect; the fork does not reproduce it.
- **The tick clock's restart** (`0x437540`) when Shaggy hangs the mirror isn't kept, as in WP-057.

**Found on the way:**

- **The red ball is found in the gallery, not the room of doors:** the gallery's event sets `RedBallFound`, and the room of doors' Jester then takes it.
- **The mirror persists through the inventory, not a room key:** it is hung whenever the found mirror has been had (`0x407060`) and is no longer in a slot (`0x4070C0`), so the gallery saves nothing of its own.
- **The way to the magic mirror room is doubly gated:** hidden until the mirror is hung, then blocked until the level's snacks are given.

---

## Goal

Port two of Phantom's rooms: the royal gallery and the magic mirror room.
They come next in
[the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order)
(group 6, after WP-071's passages), where `ROOM_P31_KST` follows (WP-073).
Until now these rooms had the base class:
- the gallery's mirror could not be hung, and the way on never opened;
- the red ball did nothing;
- the magic mirror room's hotspots were silent.

## Background

The rooms ([scooby-exe](../formats/scooby-exe.md#phantoms-royal-gallery-and-magic-mirror-room-wp-072)):
- **The gallery** keeps the found red ball (shown to the Jester), the mirror
  the gang hangs on the wall, and the Jester himself.
- **The magic mirror room** hums, its hotspots give their lines, and its
  cameras and the way to the wizard's skull are built as it is entered.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`RoyalGalleryRoom` and `MagicMirrorRoom`:** the walk-ins; the mirror,
  its hanging, the way on and the snack gate; the red ball; the Jester; the
  magic mirror room's hum, hotspots and placements.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes and the gallery's walk-ins and snacks;
   - the mirror, bare and hung, and the red ball;
   - the snack gate to the magic mirror room;
   - the magic mirror room's hum, hotspots and placements.

   Showdown prints that it has no gallery, as its reference does.
2. [x] Live, in Phantom: the mirror's line; the snack gate; the found mirror
   hung; the magic mirror room's hotspots.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the usual random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-royal-gallery-and-magic-mirror-room-wp-072):
  the two rooms.
