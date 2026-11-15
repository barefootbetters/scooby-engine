---
layout: default
title: "WP-033: Street 2 and Street 3"
---

# WP-033: Showdown's Street 2 and Street 3 (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (game logic: the story rooms)
**Depends on:** WP-029 ✅ (room setup and the story-room hooks), WP-028 ✅ (the story's values), WP-031 ✅ (suspects met)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-033-2026-11-14](../reference/pre-flight-WP-033-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Street 2 against the trace | ✅ At `script` level 3, from Town Center:<br>• Fred walks in `DL` and Daphne `DR`, each 50 in front of their depth.<br>• `Street_1.130A_` holds input and starts on tick 100. It plays again on the next visit while the moans are on; with them off there is no opening.<br>• Before Artie is met, Gummy and the donkey aren't built.<br>• Once Artie is met, Gummy loops `ANIM_GUMMY_BSLEEPS` (state 16); neither he nor the donkey can be hit.<br>• With `GummyPuzzle` and Gummy a clue owner, he stands idle 50 pixels along (157 → 207), and so does the donkey (204 → 254). The window is built at depth −1, never hit.<br>• The clock plays `CLOCKA`, and `CLOCKB` once `OBJ_INV_CLOCK` is taken.<br>• The hotspots play `Street_2.100C_` and `100D_` with input on. The exit to the store plays `Street_2.General_Store1_` or `2_`. |
| 2. Street 3 against the trace | ✅ Fred walks in `DL` from Town Center, Velma `U` from the Saloon, and Shaggy `UR` from the Bank.<br>• The first hotspot plays `130X1_`, `130X2_`, `130X3_`, then `130X1_` again.<br>• The second takes the music out of its group while its 46 steps play. It is a `Music.dat` clip, so it replaces the music. After 138 ticks group 2 comes back on its next variant (`Group2_4` → `Group2_1`).<br>• The third plays `Street_3.HOTSPOT3_` on step 3 while it plays its A, when its state (`+0x60`) is already B; not while it plays B or C. *(Corrected 2026-11-14 in WP-034: `794cb1a830` tested the playing sequence and so fired during B.)*<br>• Idle chatter is `100B2_` or `1100A_` with the moans on, and only `1100A_` with them off. Moans come every 5–14 seconds. |
| 3. Live, Showdown | ✅ Started from a profile with the moans on and Town Center's snack eaten, driven by the engine's `test_script`:<br>• Town Center to Street 2: Fred and Daphne walk in, and the opening starts on tick 100. Escape skipped it, and the first hotspot gave `100C_`.<br>• Back through Town Center to Street 3: Fred walks in, and its opening plays.<br>• The second hotspot's `SFX_P11_STREET3_HOTSPOT2A` replaced the music, and then `Group2_2` came in.<br>• Six frames were captured. |
| 4. Build and regressions | ✅ Scooby-only build: 0 errors, 0 warnings in `engines/scooby/`. Fork commit [`794cb1a830`](https://github.com/barefootbetters/scummvm/commit/794cb1a830) is on WP-032's `819f0599ad`, inside `engines/scooby/`, and is pushed. Every earlier check's lines match on both titles: Showdown 1,347 and Phantom 1,256. Every room's music and opening still match WP-029's reference (0 differences in 69 and 53 rooms). |

**Deviations and gaps:**

- **Street 1 is WP-034.** It needs the clue each suspect gives (game vtable `+0x44`, `0x42F990`, chosen by the villain), the Sheriff, the pump, the strong box key and the brick that sets `FinalClue`.
- **Hit type 0** now means "never hit" for every sprite, as `0x4311F0` has it; before, the fork treated it as 1. Nothing else sets it.
- **A room's plain sprite is hit by its cels** (type 1), as `graphics_Sprite_ctor` (`0x430D60`) leaves it. Only the default placement path sets 2 (`0x4094C0`). This WP's sprite claims defaulted to 2, so Street 2's clock was hit by its polygon. The WP-001 session noticed it while doing WP-037. Fixed on 2026-11-15 in fork [`36ce94a2f5`](https://github.com/barefootbetters/scummvm/commit/36ce94a2f5). The default is now 1, which changes only the `hit` value in 16 check lines: Street 2's clock and the chase rooms' branches, P25 overlay and canned run-offs.
- **Not checked:** Daphne walking in `UR` from the general store, and Fred `UL` from the station. They are the same code as the walk-ins checked.

---

## Goal

Play Showdown's Street 2 and Street 3 as their room classes have them, and
add the hooks those rooms need for the rest of the story rooms.

## Background

Traced headless in Ghidra 12.1.4. Both classes' functions are listed in
[scooby-exe](../formats/scooby-exe.md#street-2-and-street-3-wp-033).

- **Street 2** (`0x42C3E0`, vtable `0x45F27C`): entry, placements, events,
  exit, and the opening on each visit (room vtable `+0x30`, `0x42CB40`).
- **Street 3** (`0x42CB80`, vtable `0x45F2C0`): reset, entry, tick, events
  and idle chatter.

## Scope

**In scope (fork, `engines/scooby/` only):**

- Both rooms' classes.
- Hooks:
  - room vtable `+0x30`;
  - an exit's scene changed by the class;
  - plain sprites as placement claims;
  - hit type 0;
  - walk-ins in front;
  - a looping action (state `0x10`);
  - music groups set by rooms;
  - clue owners (`0x40A870`).
- A `script` level 3 check.

**Out of scope:** Street 1 (WP-034).

## Exit criteria

1. [x] Street 2 matches the trace: openings, walk-ins, Gummy and the
   donkey as the story moves, the window, the clock, the hotspots and the
   store exit.
2. [x] Street 3 matches the trace: walk-ins, the three hotspots, the music,
   idle chatter.
3. [x] Live in Showdown: both streets from Town Center.
4. [x] Scooby-only build with 0 errors and 0 warnings; earlier checks
   unchanged; the fork diff stays inside `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): both rooms.
- WORK_INDEX row and findings line.
