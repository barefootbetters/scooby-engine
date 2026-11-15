---
layout: default
title: "WP-025: Toolbar Rooms"
---

# WP-025: The rooms that hide the toolbar (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (game logic: the default object behaviour)
**Depends on:** WP-023 ✅ (the toolbar), WP-024 ✅ (built on its fork commit)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-025-2026-11-14](../reference/pre-flight-WP-025-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Every room matches the trace | ✅ At `script` level 3 the engine enters every room and logs whether its toolbar is shown or hidden: Showdown hides it in 45 of 69 rooms, Phantom in 22 of 53. An independent script reads the trace's own output, not the engine's table. It maps each factory's room names to their classes, and each class's vtable `+0x0C` to whether it calls `0x40B920` and `0x407CC0`. It predicts the same state for all 122 rooms. |
| 2. Items still work in those rooms | ✅ Showdown's one pickup in a hiding room, the oilcan in `ROOM_P29_Chase_B6`, takes 46 ticks in the engine and in the WP-023 reference (37 elsewhere). Adding the item clears the hidden flag, the van comes back to parked, and then it drives open. Every requires object in a hiding room (the four Garden Plaques and `OBJ_SUSPECT_FINAL_CLUE`) still takes and drops its items. |
| 3. Live | ✅ `start_room=ROOM_P29_Chase_B6`: the room drew with no toolbar. A click on the oilcan brought the Mystery Machine in and opened it with `Global.Toolbar`, and the oilcan sat on pad 0. Both frames were captured from the window. |
| 4. Build and regressions | ✅ Scooby-only build: 0 errors, 0 warnings. Fork commit [`ec9a31a9f4`](https://github.com/barefootbetters/scummvm/commit/ec9a31a9f4), on WP-024's `550cbb48fa`, stages its 6 files by name inside `engines/scooby/` and is pushed. The exit, click, inventory, hint and snack checks pass on both titles with 0 stuck. |

**Changes to WP-023's check:**

- **The drive test** now runs in the first room that shows the toolbar. Phantom's room 0, `ROOM_P31_KST`, never builds it.
- **The requires test** in a hiding room now waits for the toolbar to park, not open. A slot click works while parked (`0x406A70`).

---

## Goal

Close WP-023's open deviation, "The toolbar is in every room". Hide the
toolbar in the rooms whose class hides it, as the original does.

## Background

The base room's entry (room vtable `+0x0C`, `0x40B920`) builds the toolbar
and parks it (`0x406620`, `0x407D50`). Each title's room factory gives
named rooms their own classes; every other room gets the base class.
Some classes' entries:

- **call the base entry and then `0x407CC0`**, which sets the hidden flag
  (`+0x1B4`) and moves the van to x = −(width + 30), off the left edge;
- **or never call the base entry**, so no toolbar is built
  (`ROOM_Suspect_Chooser`, `ROOM_Quit`, `ROOM_Cheat`, Phantom's
  `ROOM_P31_KST`).

Traced headless in Ghidra 12.1.4, in this session's scratch projects of
both `Scooby.exe`s:

1. **Each factory's room-name compares**, read from the listing: Showdown
   `0x42E0E0`; Phantom's start at `0x42ED7F`. Each name maps to the class
   constructor its branch calls. Names that share a class jump to one
   body; a name no compare matches gets the base class (`0x40B0F0`).
2. **Each constructor's vtable** (the `MOV [ESI], 0x45…` store) and that
   vtable's `+0x0C`.
3. **Each `+0x0C`'s calls**, across the whole function body: does it call
   `0x40B920`, and does it call `0x407CC0`?

The result is 24 of Showdown's 47 classes and 20 of Phantom's 51. The room
list is in [scooby-exe](../formats/scooby-exe.md#rooms-that-hide-the-toolbar-wp-025).

**Adding an item** (`0x406DD0`) or **opening** the toolbar (`0x407C00`)
clears the flag. The tick (`0x407120`) then moves the van right from
x < 0 until it parks at 0. So a pickup in a hiding room brings the
toolbar back, as Chase B6's oilcan shows.

## Scope

**In scope (fork, `engines/scooby/` only):**

- A room table (`toolbar_rooms.{h,cpp}`) and `Inventory::hideToolbar()`
  (`0x407CC0`), called on room entry.
- A per-room line in the `script` level 3 inventory check.

**Out of scope:** everything else those rooms' classes do: menus, chases,
close-ups and set pieces.

## Exit criteria

1. [x] For every room of Showdown and Phantom, the toolbar's state on entry
   matches an independent reading of the trace output.
2. [x] Pickups and requires objects in hiding rooms still work, and the
   pickup's tick count matches the WP-023 reference.
3. [x] Live: a hiding room shows no toolbar until an item is taken.
4. [x] Scooby-only build with 0 errors and 0 warnings. The earlier checks
   still pass. The fork diff stays inside `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): the room table.
- WORK_INDEX row and Phase 3 findings line; WP-023's deviation marked
  closed.
