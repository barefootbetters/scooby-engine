---
layout: default
title: "WP-038: Showdown's bank vault"
---

# WP-038: Showdown's bank vault: the safe and the open safe (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-036 ✅ (the combination), WP-034 ✅ (Street 1's strongbox key), WP-023 ✅ (requires objects)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-038-2026-11-15](../reference/pre-flight-WP-038-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp038_ref.py`: WP-037's, plus the vault and the open safe, written from the trace before the engine ran. It reads the placements and step counts from the art, and the open safe's lines from the sound archives' indexes, and never runs the engine. At `script` level 3 the chase check now logs 83 lines on Showdown, the earlier 72 and 11 for the vault; the reference prints the same 83, none different. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **The placements.** The safe's door a requires object at depth 1, the four strong boxes, the dust a clickable. With the combination and the key used, the door is open and the boxes are gone, and the dentures come once.
   - **The safe with the arrow.** Held; Daphne tries it on tick 1 (54 steps, `Daphne.No_Open_Safe`); on tick 163 `Bank_Vault.340E_`, which holds input to its end.
   - **The safe with the combination.** It is used; Daphne opens it on tick 1 (26 steps, `Daphne.Opens_Safe`), the door hidden; on tick 79 the door is shown open and the open safe loads on tick 80.
   - **The strong boxes.** With the arrow, `340A_` and `340A2_` in turn. With the key in a wrong box, all three of `340B_`, `340B2_`, `340B3_` over 40 tries. In the right box, the key is used and the vault loads through movie 40; there, the dentures, and no boxes.
   - **The dust.** A, then B (its next C makes it visible), then C with `Bank_Vault.340X_`, staying on C, also after leaving and coming back. `DustVisible` reads back, and a reset clears it.
   - **The open safe.** The gang under layer 1, the cursor hidden and clicks taken; the first line on tick 73, then Fred, Daphne, Shaggy and Scooby, each on their own mouth; the back alley on tick 81, the scene marked played. Seen, straight to the alley on tick 1; skipped during the first line, likewise.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, from a profile in the original's form starting in the vault with the combination in the toolbar:
   - **The dust and a box.** The dust played its A; strong box 1 with the arrow played `340A_`.
   - **The safe.** The combination from the toolbar onto the safe: Daphne opened it on tick 294 and the open safe loaded on tick 372.
   - **The open safe.** The gang looked out of the safe and said their four lines, with their mouths moving, and the back alley loaded and played `Back_Alley.350A_`.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **The open safe's input.** The original holds input every tick (`0x42A320`) and only input slot 5 skips. The fork hides the cursor and takes clicks without a skip, because the fork treats a click as a skip in a class that holds input (the title's rule).
- **The bank's other rooms** have no class yet: ROOM_P13_Bank and its vault door, ROOM_Vault_Clock, and ROOM_SB1 to SB5.

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

1. [x] Showdown matches an independent reference line for line:
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
2. [x] Live, in Showdown, from a profile in the original's form:
   - the dust and a strong box clicked;
   - the combination taken from the toolbar to the safe;
   - Daphne opening it, the open safe's scene, and the back alley.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038): the vault and the open safe.
