---
layout: default
title: "WP-077: Phantom's wizard's skull and library"
---

# WP-077: Phantom's wizard's skull and library (Gen 1)

**Status:** ✅ Done (2026-11-19)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-023 ✅ (the inventory — `OBJ_INV_SPELL_BOOK`), WP-031 ✅ (Big Head — `ROOM_Big_Head`, the library's reveal), WP-057 ✅ (Phantom's new game and first room), WP-072 ✅ (the magic mirror room — the skull's exit target and the `OBJ_P08_TO_WIZARDS_SKULL` way in)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-077-2026-11-19](../reference/pre-flight-WP-077-2026-11-19.md)

---

## Goal

Port the first pair of Phantom's group-8 rooms, `ROOM_Wizards_Skull` and
`ROOM_P25_Wizards_Library`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 8, Upstairs — the first sub-bullet). Until now they have the base class:
the rooms draw, but the skull puzzle does nothing, the spell book is inert, and
the library's hotspots give no lines.

## Background

The wizard's skull and library
([scooby-exe](../formats/scooby-exe.md), to be extended by this WP) are the
first of the Upstairs rooms, reached from the magic mirror room: WP-072's
`MagicMirrorRoom` builds `OBJ_P08_TO_WIZARDS_SKULL` as the way in, and
`ROOM_Wizards_Skull` exits back to `ROOM_P08_Magic_Mirror_Room`.

Per the [Phantom audit](../reference/room-class-audit-phantom-2026-11-16.md)
group-8 table (the symbol names below are the audit's; the execution trace
confirms the mechanic):

- **`ROOM_Wizards_Skull`** (`0x42D7B0`, vtable `0x45F4C4`, 463 lines, music
  `Skull_Puzzle.Music`, **no opening**). Overrides `tick, reset, enter, leave,
  event, claim, save, load`. Names `IntroDone`; exits to
  `ROOM_P08_Magic_Mirror_Room`. The largest class of this packet — a puzzle
  room (the "Skull Puzzle" its music names), with its own save/load state.
- **`ROOM_P25_Wizards_Library`** (`0x42D1F0`, vtable `0x45F484`, 202 lines,
  music `1`, opening `Wizards_Library.300_`). Overrides `reset, enter, event,
  claim`. Names `OBJ_INV_SPELL_BOOK`, `ROOM_Big_Head` and `ROOM_Wizards_Skull`:
  the spell book, a Big Head reveal, and the way to the skull room.

Both rooms already have their `room_setup` entry (music and opening), as
WP-076's did — no `room_setup` edit is expected. This opens the Upstairs group;
the Princess's bedroom, the veranda, the wizard's bedroom and the WFR follow in
later packets.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`WizardsSkullRoom`:** the skull puzzle (`IntroDone` and whatever the trace
  shows the puzzle to be), its placements and hotspot lines, the save/load
  state, the entry from the magic mirror room, and the exit back to it.
- **`WizardsLibraryRoom`:** the spell book, the Big Head reveal, the hotspot
  lines, the opening (`Wizards_Library.300_`), and the way to the skull room.
- **A `script` check** against an independent reference, on both titles
  (Showdown has neither room).

**Out of scope:** any change to a sibling room class is **not expected** —
WP-072's magic mirror room already builds `OBJ_P08_TO_WIZARDS_SKULL` and is the
skull's exit target, and `ROOM_Big_Head` (WP-031) already exists. If the trace
surfaces a one-line hook into a sibling class, it is staged by name and called
out, not folded in silently.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the two classes, the clips (dotted voice lines probed by prefix, flat sfx
     ids exact — the WP-074/075 trap);
   - the skull puzzle's placements and gating, its save/load state, the entry
     and the exit to the magic mirror room; the library's spell book, Big Head
     reveal, opening, and way to the skull room.

   Showdown prints that it has neither room.
2. [ ] Live, in Phantom: the skull room plays its `Skull_Puzzle.Music` and draws
   its placements, and its exit returns to the magic mirror room; the library
   plays its opening and draws its placements, and its way to the skull room is
   present.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual per-run random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine` (files staged by name: `wizards_rooms.{h,cpp}`,
  `wizards_check.cpp`, a factory line, the module entries, the check's
  declaration and its call).
- [scooby-exe](../formats/scooby-exe.md): the wizard's skull and library.
- `WORK_INDEX` row and ledger line flipped to ✅ Done on close.

---

## Result (2026-11-19)

`WizardsSkullRoom` and `WizardsLibraryRoom` in fork commit `f25f682f01`
(scooby-engine [PR #3](https://github.com/barefootbetters/scummvm/pull/3)),
files staged by name: `wizards_rooms.{h,cpp}`, `wizards_check.cpp`, the factory
line and include in `room_class.cpp`, the two `module.mk` entries, and the
check's declaration (`scooby.h`) and call (`chase_check.cpp`). No sibling-room or
`room_setup` edit was needed — WP-072's magic mirror room already builds
`OBJ_P08_TO_WIZARDS_SKULL`, `ROOM_Big_Head` (WP-031) exists, and both rooms'
music and opening were already in `room_setup`.

**Exit criteria.**

1. **Engine == reference, line for line.** On Phantom the check reports: both
   classes build; every clip ships (the voice lines `Wizards_Library.300D_`,
   `Magic_Mirror_Room.Wizard_`, `Wizards_Skull.Skull_Slide`, `300C_` / `300C1_` /
   `300C2_` / `300F_` / `300F1_` / `300F2_` / `HOTSPOT1_` / `HOTSPOT3_`, all by
   prefix); the skull's four clickables each showing `ANIM_SKULL{n}` + its saved
   rotation (a loaded `Skull1=2` → `ANIM_SKULL1C`), the hidden hand sprite, the
   exit; the save/load round-trip of `Skull1..4` and `IntroDone` with their reset
   defaults; the flow (`SkullPuzzleAttempted` / `SkullMovie`, solve →
   `ROOM_P24_Wizards_Bedroom` movie 6 + `SkullPuzzle`, demo done →
   `ROOM_P08_Magic_Mirror_Room` movie 31); the library's gated placements
   (`UNDERLAY` skip→sprite depth −1001, `SHELF` clickable→skip, `TO_P24`
   skip→default) and the Big-Head reveal (`300C_` on `BIG_HEAD_BG_SKULLS`, movie
   61). **Showdown prints it has neither room.**
2. **Live (Phantom).** Started in each room (`start_room`): the skull room draws
   the four skull clickables, the exit, and the hidden hand sprite, plays its
   intro, no opening; the library draws the shelf clickable with the underlay and
   the way to P24 skipped (unsolved), and plays `Wizards_Library.300_`. (The
   wizard-hand demo runs only on entry from the mirror room, not reached by
   `start_room`; it is ported from the reconciled trace.)
3. **Scooby-only build:** `--disable-all-engines --enable-engine=scooby`,
   **0 errors, 0 warnings** in `engines/scooby/` (the two pre-existing
   `gob`/`halestorm` warnings are not scooby). The fork diff stays inside
   `engines/scooby/`, staged by name.

**The one real catch — the strcmp polarity.** The room-name compare (`0x433360`)
returns **true when the strings are equal**; the first trace read it as `strcmp`
(0 on equal) and so reversed the skull's `enter` branches. The second,
independent trace — handed the raw addresses, not a name/flag map — read them the
other way, and the library's own code settles it (its taunt fires on
`from == ROOM_Wizards_Skull`, and its shelf/hotspot dispatch both need
equal→true). The corrected branches (hand demo from the mirror room, the attempt
from elsewhere) landed before the build. The three `Skull*` flag names
(`SkullPuzzle` 0x257, `SkullMovie` 0x258, `SkullPuzzleAttempted` 0x259) were
anchored on the functions that touch them, not the list order (the WP-076 hazard).

See [scooby-exe → the wizard's skull and library](../formats/scooby-exe.md#phantoms-wizards-skull-and-library-wp-077).

## Notes

- First packet of the audit's group 8 (Upstairs). The dependency — the magic
  mirror room / royal gallery (WP-072) — is done.
- **`SkullCombo0-3`** (the per-skull target rotations) are randomised at new game
  (`0x42E880`) and persisted to the profile (`profile.cpp`), read via
  `getGameInt`. The second trace confirmed they are not loaded from a fixed key
  into the struct — the fork's profile-backed game state is the equivalent.
