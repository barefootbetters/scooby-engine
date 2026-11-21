---
layout: default
title: "WP-078: Phantom's Princess's bedroom and Mermaid's cavern"
---

# WP-078: Phantom's Princess's bedroom and Mermaid's cavern (Gen 1)

**Status:** ✅ Done (2026-11-19)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-023 ✅ (the inventory — `OBJ_INV_SPELL_BOOK`), WP-057 ✅ (Phantom's new game and first room)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-078-2026-11-19](../reference/pre-flight-WP-078-2026-11-19.md)

---

## Goal

Port the second pair of Phantom's group-8 rooms, `ROOM_P29_Princess_Bedroom`
and `ROOM_P21_Mermaids_Cavern`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 8, Upstairs — the second sub-bullet). Until now they have the base class:
the rooms draw, but the bedroom's placements and whatever yields the spell book
do nothing, and the cavern's one event gives no line.

## Background

The Princess's bedroom and the Mermaid's cavern
([scooby-exe](../formats/scooby-exe.md), to be extended by this WP) are the
second pair of the Upstairs rooms. The bedroom names `OBJ_INV_SPELL_BOOK` — the
spell book the wizard's library (WP-077, merged) consumes on its shelf — so the
bedroom is where the book is obtained.

Per the [Phantom audit](../reference/room-class-audit-phantom-2026-11-16.md)
group-8 table (the symbol names below are the audit's; the execution trace
confirms the mechanic):

- **`ROOM_P29_Princess_Bedroom`** (`0x415350`, vtable `0x45EA5C`, 133 lines,
  music `Princess_Bedroom.Music`, opening `Princess_Bedroom.280_`). Overrides
  `tick, enter, leave, event, claim`. Names `OBJ_INV_SPELL_BOOK`: the spell book
  the library uses. The larger class of this packet.
- **`ROOM_P21_Mermaids_Cavern`** (`0x415280`, vtable `0x45EA1C`, ~15 lines,
  music `1`, opening `Mermaids_Cavern.340_`). Overrides `event` only. The small
  class of the packet — a single hotspot/line behaviour.

Both rooms already have their `room_setup` entry (music and opening): the
bedroom's `Princess_Bedroom.Music` is the music WP-076's below-balcony door and
the veranda share, and both openings are already present — no `room_setup` edit
is expected. This continues the Upstairs group; the wizard's bedroom, the
veranda and the WFR follow in the last packet.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`PrincessBedroomRoom`:** the bedroom's placements and hotspot lines, the
  spell book (`OBJ_INV_SPELL_BOOK`) and whatever yields it, any save/load state
  the trace shows, and the opening (`Princess_Bedroom.280_`).
- **`MermaidsCavernRoom`:** the one `event` the trace shows (a hotspot line), and
  the opening (`Mermaids_Cavern.340_`).
- **A `script` check** against an independent reference, on both titles
  (Showdown has neither room).

**Out of scope:** any change to a sibling room class is **not expected** —
WP-077's wizard's library already consumes `OBJ_INV_SPELL_BOOK`. If the trace
surfaces a one-line hook into a sibling class, it is staged by name and called
out, not folded in silently.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the two classes, the clips (dotted voice lines probed by prefix, flat sfx
     ids exact — the WP-074/075 trap);
   - the bedroom's placements and gating, the spell book and what yields it, any
     save/load state, the opening; the cavern's one event line.

   Showdown prints that it has neither room.
2. [ ] Live, in Phantom: the bedroom plays its `Princess_Bedroom.280_` opening
   and `Princess_Bedroom.Music`, draws its placements; the cavern plays its
   `Mermaids_Cavern.340_` opening and draws its placements.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual per-run random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine` (files staged by name: the new
  `<group>_rooms.{h,cpp}` and `<group>_check.cpp`, a factory line and include in
  `room_class.cpp`, the two `module.mk` entries, and the check's declaration
  (`scooby.h`) and call (`chase_check.cpp`)).
- [scooby-exe](../formats/scooby-exe.md): the Princess's bedroom and Mermaid's
  cavern.
- `WORK_INDEX` row and ledger line flipped to ✅ Done on close.

---

## Result (2026-11-19)

`PrincessBedroomRoom` and `MermaidsCavernRoom` in fork commit `873cbd3677`
(scooby-engine [PR #4](https://github.com/barefootbetters/scummvm/pull/4)),
files staged by name: `princess_rooms.{h,cpp}`, `princess_check.cpp`, the factory
line and include in `room_class.cpp`, the two `module.mk` entries, the check's
declaration (`scooby.h`) and call (`chase_check.cpp`), and the echo hook
(`RoomHooks::isEcho` in `room_script.h`, the Mermaid's override, and the
wrong-item selector in `inventory.cpp`). No `room_setup` or sibling-room edit —
both rooms' music and opening were already present.

**Exit criteria.**

1. **Engine == reference, line for line.** On Phantom the check reports: both
   classes build (`Princess_Bedroom` echo 0, `Mermaids_Cavern` echo 1); the clips
   ship (the bedroom's `Princess_Bedroom.280_` / `280A_` / `280XA_` /
   `Daphne_Takes_Book` and the cavern's `Mermaids_Cavern.340_`, all by prefix; the
   wrong-item lines `Global.WRONGS_` dry and `Global.WRONGS_Echo_` /
   `WRONGV_Echo_` / `WRONGSC_Echo_`); the claims (`HOTSPOT1` clickable at depth
   300; `SPELL_BOOK` fresh → requires, held → skip). **Showdown prints it has
   neither room** (`princess check: no princess bedroom`).
2. **Live (Phantom).** Started in each room (`start_room`): the bedroom draws the
   spell book (a requires object) and the hotspot (a clickable at depth 300) and
   plays its opening `Princess_Bedroom.280_`; the cavern is reached and plays its
   opening `Mermaids_Cavern.340_` (its three-line intro). The spell-book take and
   the mermaid scare run on a click, ported from the reconciled trace.
3. **Scooby-only build:** `--disable-all-engines --enable-engine=scooby`,
   **0 errors, 0 warnings** in `engines/scooby/` (the two pre-existing
   `gob`/`halestorm` warnings are not scooby). The fork diff stays inside
   `engines/scooby/`, staged by name.

**No catch this packet.** The two independent traces agreed on every slot, clip,
flag and gate with no correction. The one interpretive call — the spell-book
`event` guard, which the original makes on the cursor being the settled default —
is ported as a plain-click guard (`Inventory::isDefaultCursor`). The echo flag
(`+0x29`) was anchored on its only reader (the wrong-item selector `0x4098B0`),
not the flag list, and the fork already carried the comment anticipating it.

See [scooby-exe → the Princess's bedroom and Mermaid's cavern](../formats/scooby-exe.md#phantoms-princesss-bedroom-and-mermaids-cavern-wp-078).

## Notes

- Second packet of the audit's group 8 (Upstairs). The dependency chain runs the
  other way from WP-077: the bedroom yields the spell book the library (WP-077,
  merged) consumes.
- The Mermaid's cavern is one of the smallest Phantom classes (`event` only);
  its single hotspot line is traced the same way as the larger rooms, clip name
  anchored on the function, probed by prefix.
