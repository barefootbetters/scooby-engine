---
layout: default
title: "WP-023: The inventory and the toolbar"
---

# WP-023: The inventory, the toolbar and requires objects (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic: inventory)
**Depends on:** WP-018 ✅ (kinds, hit test, cursor), WP-019 ✅ (sound), WP-020 ✅ (characters, scenes), WP-021 ✅ (clicks reach the room)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-023-2026-11-14](../reference/pre-flight-WP-023-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp023_ref.py`, written from the trace. It reads `TGIFILE.ART` through `tools/probe_art.py`, plus `object.ini` and the sound indexes, and never runs the engine. At `script` level 3 the engine's check logs one line per toolbar phase, pick-up and requires object, and the reference prints the same lines.

| Exit criterion | Result |
|---|---|
| 1. The toolbar | ✅ Both titles match line for line: each sprite's position, size and ANIM, parked and open. The van is 93 pixels wide on both and opens at x 542, after 36 ticks. Parking takes 48 ticks: off the right edge, back in from the left. On the tick the van stops, the blocker in front of it is still shown. The reference got this wrong at first; `0x407120` returns before hiding it, and the engine does the same. |
| 2. Every pick-up | ✅ 7 on Showdown and 10 on Phantom match. Each item without a movie lands in slot 0 on tick 37, when the toolbar is open. In order: `Global.Toolbar`, the room hears of it, the object hides, and `pickupsfx` plays (none exist). The object stays hidden on return. Phantom's three movie items (10, 37, 38) add the item at once and ask for the movie and the same room. |
| 3. Every requires object | ✅ 13 on Showdown and 19 on Phantom match. With the arrow, the room hears 0, except Showdown's dark-tunnel crate, which asks for the arrow and hears 1. 20 have an item that gives their cursor; with it, the room hears 1 and the item goes back. With another item, the room hears nothing, the gang member the trace picks says the `Global.WRONG…` line, and the item goes back. That is the narrator in Phantom's 6 rooms without the gang. 12 ask for a cursor no item gives: story items, the arrow, `ANIM_CURSOROPEN` and one blank. |
| 4. Live, Showdown | ✅ In Town Center, a click on the fallen sign drove the toolbar in, and the sign landed in slot 0. Its slot's click made it the cursor. A click on the road with it drew Shaggy's `Global.WRONGS_1_SHAGGY`, and the sign went back. In the Bank Vault, with `start_items=OBJ_INV_STRONGBOXKEY`, the key used on the chest (hotspot 4) gave `room event OBJ_P16_BANK_VAULT_HOTSPOT4 1`. In an earlier attempt, the key clicked on the exit drew Velma's line instead, as the trace says it should. |
| 5. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit check (71 and 82), click check (191 and 174) and room check (69 and 53 rooms, every line as in WP-020) are unchanged. Fork commit [`b67042410e`](https://github.com/barefootbetters/scummvm/commit/b67042410e) stages its 11 files by name, inside `engines/scooby/`, and is pushed. |

**Deviations and gaps:**

- ~~**The toolbar is in every room.**~~ Closed by [WP-025](WP-025-toolbar-rooms.md): the rooms whose classes hide it (`0x407CC0`) or never build it now start without it.
- **No story yet.** Pick-ups and uses reach the room as events that the base room ignores, as the original's base class does. Doors and puzzles wait for the story rooms' code.
- **The snack box and Scrappy** draw, but their clicks do nothing yet.
- **The inventory lasts the session.** The save's `Inventory` section is not written.
- **Not tested live:** closing the toolbar by its van. The check covers the drive and its tick count. The live click lost focus to another window, so the run stopped there rather than fight for the mouse.

---

## Goal

Give the Gen 1 engine its inventory as the original has it. Picking up an
`inventoryobject` puts the item in the Mystery Machine toolbar. An item
from the toolbar becomes the cursor. A `requiresobject` answers the item it
asks for, and any other use puts the item back with a gang member's line.

## Background

WP-018 built `inventoryobject` and `requiresobject` placements with their
kinds, and left their clicks for later. In `Scooby.exe` (`Inventory.cpp`,
the object at game `+0xAC`):

- **The toolbar** (`0x406620`, built on every room entry). The van,
  `OBJ_TOOLBAR` playing `ANIM_TOOLBARMYSTERY_MACHINE_IDLE`, stands on the
  screen's last row. It tows the four item slots (fingerprints), the
  magnifying glass, the snack box, Scrappy and the quit button. Each sits
  20 pixels left of the last, by widths `0x430C00` measures. The van parks
  at x 0, with the rest off the left edge.
  - **Driving in.** A click on the van (`0x408060` → `0x406A70`) drives it
    right at 15 pixels a tick (`0x407120`) until it stands at 635 − its
    width. The slots are then in view.
  - **Driving out.** A second click drives it off the right edge, back in
    from the left, and to x 0.
- **Pick-up** (`0x402B00`). A click with the arrow asks the toolbar to open.
  The item lands in the first free slot on the tick the toolbar is open.
  The room then hears of it, the object hides, and `pickupsfx` plays. A
  `pickupmovie` instead adds the item, plays the movie and loads the room
  again. An item ever taken stays in a 32-entry history, and its object is
  hidden on every later visit (`0x402AD0`).
- **Use.** A click on a slot's item makes its `usecursor` the game's cursor
  (game `+0x238`), and the slot dims.
  - A `requiresobject` (`0x402F20`) given its `requiredanim`, or the arrow,
    tells the room, and the cursor goes back to the arrow.
  - Any other click with an item (`0x4098B0`) does the same, after one of
    the gang in the room says a `Global.WRONG…` line. If none of the gang
    is in the room, the narrator says it.
  - The item returns to its slot on the next tick.
- **Exits and clickables** answer only the arrow.

## Scope

**In scope (fork, `engines/scooby/` only):**

- `Inventory`: the slots, the history, the game cursor, the toolbar sprites
  and their drive, pick-up, use, requires objects and the wrong-item line,
  in the original's tick order.
- `Room`: sprites the engine adds itself, placed relative to a parent, and
  the `0x430C00` size.
- `RoomScript`: a scene that doesn't block input, and whether a character
  is in the room.
- The cursor shows the hovered object's rollover, which is empty for every
  object while an item is the cursor. Otherwise it shows the game cursor.
- The magnifying glass goes to `ROOM_Suspect_Chooser`, and quit to
  `ROOM_Main_Menu` after its sound.
- Console `inv`, `inv_add` and `inv_remove`, and a `start_items` config key,
  for testing.
- A `script` level 3 check. It drives the toolbar in and out. From a new
  game, it picks up every inventory object, and uses every requires object
  with the arrow, with its item and with another item.

**Out of scope:**

- What a room does when it hears of a pick-up or a use (room vtable
  `+0x14`): the 16 story rooms' own classes. The base room does nothing.
- The snack box and Scrappy's hint mode (their own cursors and clips).
- Hiding the toolbar in menu rooms (their classes call `0x407CC0`).
- The save file's `Inventory` section (`0x407430` / `0x407780`).

## Exit criteria

1. [x] The toolbar matches an independent reference on both discs:
   - every sprite's position, size and ANIM, parked and open;
   - the ticks to open and to park.
2. [x] Every inventory object, picked up from a new game, matches the
   reference: what happens, in order, the ticks until it lands, its slot,
   and whether it hides now and on return.
3. [x] Every requires object matches the reference when clicked with the
   arrow, with the item it asks for (where an item gives it), and with
   another item.
4. [x] Live, in Showdown:
   - an item is picked up into the toolbar;
   - used on nothing, it draws a gang member's line and goes back;
   - used on its requires object, it tells the room.
5. [x] Scooby-only build: 0 errors and 0 warnings. The exit, click and room
   checks are unchanged. The fork diff stays inside `engines/scooby/`,
   staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): the inventory functions.
- [Integration §5](../02-SCUMMVM-INTEGRATION.md#5-graphics-output): the
  toolbar and the cursor.
