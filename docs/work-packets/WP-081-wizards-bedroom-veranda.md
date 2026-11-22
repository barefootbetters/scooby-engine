---
layout: default
title: "WP-081: Phantom's wizard's bedroom and veranda"
---

# WP-081: Phantom's wizard's bedroom and veranda (Gen 1)

**Status:** ✅ Done (2026-11-21)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-023 ✅ (the inventory — `OBJ_INV_MAZE_MAP`), WP-031 ✅ (the accusation — `ROOM_Suspect_Chooser`, Big Head), WP-057 ✅ (Phantom's new game and first room)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-081-2026-11-21](../reference/pre-flight-WP-081-2026-11-21.md)

---

## Goal

Port the third pair of Phantom's group-8 rooms, `ROOM_P24_Wizards_Bedroom`
and `ROOM_P28_Veranda`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 8, Upstairs — the third sub-bullet). Until now they have the base class:
the rooms draw, but the wizard's bedroom does nothing with the wizard or the
maze-map scroll, and the veranda's well gives no line.

The fourth and last group-8 sub-bullet, `ROOM_P30_WFR` (the Wizard's Rule Room,
the game's largest class at 1022 lines), is **its own packet** — WP-083 — and is
**not** in scope here.

## Background

The wizard's bedroom and the veranda
([scooby-exe](../formats/scooby-exe.md), to be extended by this WP) are the
third pair of the Upstairs rooms. The bedroom is the wizard's lair: it is where
the wizard is met and, on the return from the Wizard's Rule Room, where the gang
accuses him. The veranda overlooks the well.

Per the [Phantom audit](../reference/room-class-audit-phantom-2026-11-16.md)
group-8 table (the symbol names below are the audit's; the execution trace
confirms the mechanic):

- **`ROOM_P24_Wizards_Bedroom`** (`0x42CCF0`, vtable `0x45F444`, 179 lines,
  music `1`, no opening). Overrides `tick, reset, enter, claim`. Names
  `OBJ_INV_MAZE_MAP` (the scroll) and leads to `ROOM_P30_WFR` and
  `ROOM_Suspect_Chooser`.
- **`ROOM_P28_Veranda`** (`0x4183B0`, vtable `0x45ECDC`, 136 lines, music
  `Princess_Bedroom.Music` — shared with WP-076's below-balcony door, no
  opening). Overrides `reset, event, save, load, arrive`. Keeps `WellClicks` and
  leads to `ROOM_Big_Head`.

Both rooms already have their `room_setup` entry (music; neither has an opening
scene), so no `room_setup` edit is expected. This continues the Upstairs group;
only the WFR (WP-083) then remains.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`WizardsBedroomRoom`:** the wizard met (`meetSuspect`), the clue and the
  GIVES pose on the return from the WFR, the accusation it arms
  (`ROOM_Suspect_Chooser` / `Global.Thank_You_`, as the dining room and arenas
  do), the maze-map scroll (`OBJ_INV_MAZE_MAP`, an inventory placement) and
  `Wizards_Bedroom.Scroll`.
- **`VerandaRoom`:** the well hotspot's cycling line
  (`Veranda.290B_` / `290X1_` / `290X2_`) over Big Head, the first-entry and
  pre-click openings (`Veranda.270D_`, `Veranda.290_`), and the saved
  `Entrances` / `WellClicks`.
- **A `script` check** against an independent reference, on both titles
  (Showdown has neither room).

**Out of scope:** `ROOM_P30_WFR` (WP-083). No change to a sibling room class is
expected.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the two classes, the clips (dotted voice lines probed by prefix);
   - the bedroom's wizard flow (met, clue, GIVES, the `Global.Thank_You_`
     accusation), the maze-map scroll's inventory claim and
     `Wizards_Bedroom.Scroll`; the veranda's cycling well line, its openings and
     the saved `Entrances` / `WellClicks`.

   Showdown prints that it has neither room.
2. [ ] Live, in Phantom: the bedroom draws and plays its music; the veranda
   plays its first-entry opening `Veranda.270D_` and, on the well, a line over
   Big Head.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual per-run random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine` (files staged by name: the new
  `wizards_bedroom_rooms.{h,cpp}` and `wizards_bedroom_check.cpp`, a factory line
  and include in `room_class.cpp`, the two `module.mk` entries, and the check's
  declaration (`scooby.h`) and call (`chase_check.cpp`)).
- [scooby-exe](../formats/scooby-exe.md): the wizard's bedroom and veranda.
- `WORK_INDEX` row and ledger line flipped to ✅ Done on close.

---

## Result (2026-11-21)

`WizardsBedroomRoom` and `VerandaRoom` in fork commit `ce1846a567`
(scummvm [PR #6](https://github.com/barefootbetters/scummvm/pull/6)), files
staged by name: `wizards_bedroom_rooms.{h,cpp}`, `wizards_bedroom_check.cpp`, the
factory line and include in `room_class.cpp`, the two `module.mk` entries, the
check's declaration (`scooby.h`) and call (`chase_check.cpp`). No `room_setup` or
sibling-room edit — both rooms' music was already present and neither has an
opening.

**Exit criteria.**

1. **Engine == reference.** On Phantom the self-test reports: both classes
   (`Wizards_Bedroom bedroom; Veranda veranda`); the bedroom's
   `Wizards_Bedroom.Scroll` (by prefix), the accusation scene `Global.Thank_You_`
   → `ROOM_Suspect_Chooser`, and the `OBJ_INV_MAZE_MAP` **inventory** claim; the
   veranda's `Veranda.270D_` / `290_` / `290B_` / `290X1_` / `290X2_` (all by
   prefix), music `Princess_Bedroom.Music`, Big Head `BIG_HEAD_BG_P44P22`.
   **Showdown prints it has neither room** (`wizard's bedroom check: no wizard's
   bedroom`).
2. **Live (Phantom).** The bedroom enters on load (its debug fires from the maze
   centre / drawbridge); the veranda draws its placements (the well hotspot
   `OBJ_P28_VERANDA_HOTSPOT1` in the draw order), a stable room md5, 0 hit misses.
3. **Scooby-only build:** `--disable-all-engines --enable-engine=scooby`, **0
   errors, 0 warnings** in `engines/scooby/` (the two pre-existing gob / halestorm
   warnings are not scooby). The fork diff stays inside `engines/scooby/`, staged
   by name.

**One check correction.** `Global.Thank_You_` is a scene (the accusation the
dining room and arenas use), not a sound clip, so it is named, not prefix-probed —
a probe read "0" of a name that is right (the WP-074 anim-vs-clip trap).

**Verification.** One session traced both rooms; each engine call was cross-checked
against the fork's existing siblings (the dining room's accusation, the post
office's `arrive`, the below-balcony door's save/load), and the string-compare
polarity (the WP-077 trap) was pinned by decompiling both helpers (`0x433360`
true on equal, `0x433460` on not equal). The from-WFR arming path (the clue,
GIVES and the armed accusation) fires only on the return from `ROOM_P30_WFR`,
which is not yet ported (WP-083); the self-test verifies the wiring, and the
identical `Global.Thank_You_` → `ROOM_Suspect_Chooser` idiom is exercised live by
the dining room (WP-063) and the arenas (WP-069).

See [scooby-exe → the wizard's bedroom and veranda](../formats/scooby-exe.md#phantoms-wizards-bedroom-and-veranda-wp-081).

## Notes

- Third packet of the audit's group 8 (Upstairs). The WFR (the Wizard's Rule
  Room), the audit's fourth sub-bullet and the game's largest class, is split
  off to WP-083.
- The bedroom's accusation is the same idiom as the dining room (WP-063) and the
  arenas (WP-069): the suspect GIVES, and when idle the exit handler takes the
  gang to `ROOM_Suspect_Chooser` with `Global.Thank_You_`.
- The veranda shares `Princess_Bedroom.Music` with WP-076's below-balcony door.
