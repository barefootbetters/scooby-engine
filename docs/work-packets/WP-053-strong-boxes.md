---
layout: default
title: "WP-053: Showdown's strong boxes"
---

# WP-053: Showdown's strong boxes: a lid opens, then the vault (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-040 ✅ (the bank vault, and these rooms found unreachable), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Two hours
**Pre-flight:** [pre-flight-WP-053-2026-11-15](../reference/pre-flight-WP-053-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp054_ref.py`: WP-052's, plus the strong boxes, written from the trace before the engine ran. It reads the lids and their step counts from the art, and which sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 190 lines on Showdown: the earlier 184 and 6 for the strong boxes. On Phantom both print the one line saying there is no chase. The first run matched all 190.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown: the class for all five rooms. In each, the lid (`OBJ_SB<n>_LID` on `ANIM_SB<n>_LIDA`) is a sprite at depth 0, stopped on step 0, with input held and a countdown of 36. `Strongbox.opens` plays on tick 37 with the lid playing once. `Bank_Vault.340D_` comes on tick 37 + 5 × the lid's steps (62, or 57 for SB2), held. Skipped, the exit goes to ROOM_P16_Bank_Vault with no scene and movie −1. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from a profile starting in ROOM_SB1: `Strongbox.opens`, the lid open on the dentures, the narrator's three `340D_` lines from tick 62, and the vault. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The earlier checks are identical to WP-052's run on both titles, but for the profile check's `CluesFound1`, random each run. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`5a0c4eaddc`](https://github.com/barefootbetters/scummvm/commit/5a0c4eaddc) (7 files staged by name) is pushed. |

**Deviations and gaps:**

- **The cursor fade** (`0x435150`, 0x12) and held input are `isBusy`.
- **The scene's done flag** is the class watching the scene end, as for WP-050's `220B2_`.

**Found on the way:**

- **`0x475F4C` is the engine itself.** Its constructor stores itself there, so `+0x58` through it is the first layer, as through `0x475F14`. That settles the layer of Gummy's donkey (WP-050) and Street 2's clock too.

---

## Goal

Give ROOM_SB1 to ROOM_SB5 the original's shared class. Nothing in the
shipped game sends the gang to them ([scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038)):
the right strong box plays a movie instead. The class is still the
original's, and the audit lists it. Until now the rooms had the base
class, so a lid never opened.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`StrongBoxRoom`:** the lid, `Strongbox.opens`, `Bank_Vault.340D_` and
  the way back to the vault.
- **The room's sequence player:** a ticks-per-step argument.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [x] Showdown matches an independent reference line for line: the class
   for all five rooms; in each, the lid, the sound, the scene and the way
   back, with their ticks. Phantom prints that it has no chase, as its
   reference does.
2. [x] Live, in Showdown, from a profile starting in ROOM_SB1: the lid
   opens, `340D_` plays, and the vault follows.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038):
  the strong boxes' class.
