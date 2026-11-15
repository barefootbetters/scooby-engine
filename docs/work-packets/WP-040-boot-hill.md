---
layout: default
title: "WP-040: Showdown's Boot Hill"
---

# WP-040: Showdown's Boot Hill: the grave with the brick (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-034 ✅ (the brick's use on Street 1), WP-029 ✅ (room classes and openings), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-040-2026-11-15](../reference/pre-flight-WP-040-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
   - the classes and the grave each `GraveLocation` names;
   - each room's graves, opening, and snacks needed by level;
   - for three locations: a wrong grave's ghost, the dig scenes, movie 3,
     the room again with its opening, the brick and no graves, and then
     without the opening;
   - Boot Hill 2's way back by level, and the snack box;
   - the gang walking in, and the keys.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the brick's grave dug, movie 3, and the brick in the toolbar;
   - a wrong grave and the ghost;
   - Boot Hill 2's way back refused and the snack box flashing.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#boot-hill-wp-040): Boot Hill, and the strong-box rooms' note.
