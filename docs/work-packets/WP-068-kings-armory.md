---
layout: default
title: "WP-068: Phantom's king's armory and its slide"
---

# WP-068: Phantom's king's armory and its slide: the duster and the full bottle (Gen 1)

**Status:** ✅ Done (2026-11-17)
**Phase:** 4 (game logic)
**Depends on:** WP-065 ✅ (the full bottle), WP-061 ✅ (the duster used), WP-057 ✅ (Phantom's story values), WP-022 ✅ (movies)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-068-2026-11-17](../reference/pre-flight-WP-068-2026-11-17.md)

---

## Result (2026-11-17)

The reference is `wp069_ref.py`: WP-067's, plus the armory and its slide, written from the trace before the engine ran. It reads the placements and each sequence's steps from the art, and which clips are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 6 armory lines on Phantom (94 in all), and one on Showdown, which has no such room (225 in all).

The first run matched all 94 lines on Phantom and all 225 on Showdown, with no warnings.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **The classes:** both rooms get the armory's class.
   - **Placements:** in a new game the duster, the armour and the scratch are requires objects at depth 0; with the duster had, no duster.
   - **Entry:** without Jane screaming, each room plays `Kings_Armory.150_` the first time, holding input, and nothing after. Screaming, over 200 visits all five screams are drawn, and both `Intro_` and `Intro2_`. With the full bottle used, the armory leads to the slide; the slide stays.
   - **The duster:** Scooby takes it at tick 1 with `Scooby_Takes_Duster`, and it is hidden; at tick 43 it is in the toolbar and `150B_` holds input. Leaving at once gives it all the same.
   - **The scratch and armour:** the arrow on the scratch cycles `150C_`, `150C1_`, `150C2_`; on the armour, movie 44 back. The full bottle on either: movie 7 to the slide, the bottle out of its slot, the arrow back.
   - **The profile:** each room's `IntroDone` in its own section.
   - Showdown prints that it has no king's armory.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The duster:** a click on it, Scooby took it, and `150B_`.
   - **The full bottle** on the armour: movie 7, then the slide room with its intro.
   - **With the bottle used,** starting in the armory led straight to the slide.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-067's run. Phantom's differ in three ways:
   - the setup check now shows both rooms' intro as their opening (`starts 100`, was none);
   - the two rooms' `IntroDone` keys are new;
   - the drawbridge's random keys and Ewan's random `CurrentQuestion` vary by run.
   - Fork commit [`db26ae4418`](https://github.com/barefootbetters/scummvm/commit/db26ae4418) (7 files staged by name) is pushed.

**Deviations and gaps:**

- **The armory's redirect** to the slide skips the base entry in the original; the fork's base entry runs first, as in the throne room ([WP-062](WP-062-throne-room.md)).
- **The tick clock's restart** (`0x437540`) when Scooby takes the duster isn't kept, as in WP-057.
- **`Kings_Armory.Jane_Screaming5`** is drawn but isn't on the disc, so that scream is silent.

**Found on the way:**

- **One class, two rooms:** the factory builds the armory's class for the slide room too, each with its own state and its own `IntroDone`.
- **The full bottle opens the slide** on either the armour or the scratch, and from then on the armory itself leads there.
- **Unlike the other rooms' screams,** this one draws all five, the fourth included.

---

## Goal

Port Phantom's king's armory and its slide, `ROOM_P20_Kings_Armory` and
`ROOM_P20_Kings_Armory_Slide`, the last of the room of doors' rooms in
[its audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order).
Until now both had the base class: the duster was picked up as a plain
item, the full bottle did nothing, and neither room had its intro.

## Background

The armory ([scooby-exe](../formats/scooby-exe.md#phantoms-kings-armory-and-its-slide-wp-068)):
- **Scooby fetches the duster,** which Jane takes in the throne room
  ([WP-062](WP-062-throne-room.md)).
- **The full bottle** on the armour or the scratch opens the slide room.
- **The intro** plays once, or while Jane screams, a scream and one of two
  intros.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`KingsArmoryRoom`,** for both rooms: the duster, the scratch and the
  armour, the bottle, the redirect, the intros and screams, the profile key.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes and placements;
   - entry: the intro once, the screams, the redirect;
   - the duster, and leaving while it is taken;
   - the scratch and the armour, with the arrow and the bottle;
   - each room's profile key.

   Showdown prints that it has no king's armory, as its reference does.
2. [x] Live, in Phantom: the duster; the bottle into the slide; the
   redirect.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the new keys and openings. The fork
   diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-kings-armory-and-its-slide-wp-068):
  the king's armory and its slide.
