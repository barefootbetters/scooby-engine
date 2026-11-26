---
layout: default
title: "WP-040: Showdown's Boot Hill"
---

# WP-040: Showdown's Boot Hill: the grave with the brick (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-034 ✅ (the brick's use on Street 1), WP-029 ✅ (room classes and openings), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-040-2026-11-15](../reference/pre-flight-WP-040-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp040_ref.py`: WP-039's, plus Boot Hill, written from the trace before the engine ran. It reads the rooms' graves from the art and which openings someone in the room has a first line of from the sound archives' indexes, and never runs the engine. At `script` level 3 the chase check now logs 103 lines on Showdown, the earlier 95 and 8 for Boot Hill; the reference prints the same 103, none different. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **The rooms.** All three get the class; `GraveLocation` 0-8 names Boot Hill 1's graves, then 2's, then 3's. Each room's three graves are clickables; Boot Hill 2's opening is `340E2_`, the others none; each needs the level's snacks plus two (2, 3, 4).
   - **The graves,** for locations 0, 4 and 8. A wrong grave brings the ghost, input held. The brick's grave gives all three dig scenes over 40 tries, held; the room comes back through movie 3 on tick 1. There, `210B_` unplayed, the brick in the toolbar, no graves, `DigScenePlayed`. Next visit, no `210B_`; the grave does nothing.
   - **The snacks.** Boot Hill 2's way back keeps the gang at each level with `190A_`, `190A2_`, `190A3_`, and the toolbar opens for the snack box. The tunnel's way isn't kept, nor the way back with two snacks.
   - **Walking in.** Velma, Fred, Daphne, Shaggy and Fred, as the trace has them. The keys read back, and a reset clears them.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, from profiles in the original's form (`GraveLocation` 1):
   - **The dig.** Boot Hill 1's second grave: `190B2_`, then movie 3. Back, the graves weren't built, `210B_` played, and the brick was in the toolbar.
   - **The ghost.** The first grave: the ghost appeared, the gang scared, and the ghost spot loaded.
   - **The snacks.** Boot Hill 2's exit to Boot Hill 1: the gang stayed with `190A_`, and the snack box flashed when it ended.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **The strong-box rooms are not ported.** ROOM_SB1 to SB5 are unreachable in the shipped game; they keep the base class.
- **The snacks needed are set after the base entry.** The base room's setup logs 0 for these rooms; the class then sets the level's plus two, as `0x40EE10` does after `0x40B920`.

---

## Goal

Make Showdown's graveyard, Boot Hill, play as the original does. Until now
its three rooms had the base class: the graves did nothing, so the brick
(which Street 1 asks for) could never be found.

## Background

The three rooms share one class
([scooby-exe](../formats/scooby-exe.md#boot-hill-wp-040)):
- **The graves:** one of their nine graves holds the brick. Clicking it,
  the gang digs it up; any other grave brings the ghost.
- **The snacks:** Boot Hill 2 keeps the gang until Scooby has had the
  level's snacks.

This packet first took the bank's strong-box rooms, ROOM_SB1 to SB5. They
turned out to be unreachable in the shipped game, so Jeff chose to note
that and move on ([scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038)).

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BootHillRoom`:**
  - the graves, the dig, movie 3, and the brick;
  - the ghost on a wrong grave;
  - the openings, the snacks needed, and Boot Hill 2's way back;
  - the gang walking in;
  - the reset and `DigScenePlayed`.
- **Two calls for a room's class** on `RoomScript`: the snacks needed, and
  the ghost now.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The lit tunnel,** ROOM_P18_Tunnel_Lit; only the way in from it is here.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the classes and the grave each `GraveLocation` names;
   - each room's graves, opening, and snacks needed by level;
   - for three locations: a wrong grave's ghost, the dig scenes, movie 3,
     the room again with its opening, the brick and no graves, and then
     without the opening;
   - Boot Hill 2's way back by level, and the snack box;
   - the gang walking in, and the keys.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the brick's grave dug, movie 3, and the brick in the toolbar;
   - a wrong grave and the ghost;
   - Boot Hill 2's way back refused and the snack box flashing.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#boot-hill-wp-040): Boot Hill, and the strong-box rooms' note.
