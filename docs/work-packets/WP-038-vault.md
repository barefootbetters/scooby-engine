---
layout: default
title: "WP-038: Showdown's bank vault"
---

# WP-038: Showdown's bank vault: the safe and the open safe (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-036 ✅ (the combination), WP-034 ✅ (Street 1's strongbox key), WP-023 ✅ (requires objects)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-038-2026-11-15](../reference/pre-flight-WP-038-2026-11-15.md)

---

## Goal

Make Showdown's bank vault and the safe ICDouble's combination opens play
as the original does. Until now ROOM_P16_Bank_Vault and ROOM_Open_Safe had
the base class: the safe and the strong boxes did nothing with their items,
and the open safe's scene never played.

## Background

The vault ([scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038))
holds three things:
- **The safe:** Daphne opens it with ICDouble's combination (WP-036). The
  gang then climbs through to ROOM_Open_Safe, where they talk, and on to
  the back alley.
- **The strong boxes:** Street 1's key (WP-034) opens the right one, and
  the dentures come out.
- **The dust:** clicked, it uncovers a scene.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BankVaultRoom`:**
  - the safe's door and Daphne's try;
  - the strong boxes, their lines, the movie, and the dentures;
  - the dust;
  - the reset and `DustVisible`.
- **`OpenSafeRoom`:** its own line player, the gang's mouths on the lip
  sync, held input, the skip, and the back alley.
- **A setter for a clickable's state** (`0x401780`).
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The bank and its vault door:** ROOM_P13_Bank and ROOM_Vault_Clock (the
  dial).
- **The strong boxes' own rooms,** ROOM_SB1 to SB5.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the classes;
   - the placements, with the combination and the key used, and the
     dentures once;
   - the safe with the arrow and with the combination: Daphne's try, its
     ticks, the scene or the door and the open safe;
   - the strong boxes with the arrow, a wrong box, and the right box's
     movie;
   - the dust's three clicks, `DustVisible`, and the keys;
   - the open safe: the gang, the lines and their mouths, the ticks, the
     back alley, a second visit, and the skip.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form:
   - the dust and a strong box clicked;
   - the combination taken from the toolbar to the safe;
   - Daphne opening it, the open safe's scene, and the back alley.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038): the vault and the open safe.
