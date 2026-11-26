---
layout: default
title: "WP-039: Showdown's bank"
---

# WP-039: Showdown's bank: the vault door and its clock (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-038 ✅ (the vault), WP-023 ✅ (requires objects)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-039-2026-11-15](../reference/pre-flight-WP-039-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp039_ref.py`: WP-038's, plus the bank and the clock, written from the trace before the engine ran. It reads the placements and step counts from the art and checks that each time in the trace's tables has its own clock-time sequence on the disc; it never runs the engine. At `script` level 3 the chase check now logs 95 lines on Showdown, the earlier 83 and 12 for the bank and the clock; the reference prints the same 95, none different. On Phantom both print the one line saying there is no chase.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **The door.** A requires object at depth 1, closed; the opening `Bank.330A_` with the moans, none without; with the clock on it, DOOROPEN's step 0; with the vault open, its last step.
   - **The door with the arrow.** `330B_`, `330B2_`, `330B3_`, then `330B_` again, held; with the clock in the toolbar the third is `330C_`. With the clock on the door, straight to the dial on tick 1.
   - **The clock on the door.** Over 80 draws for each level, all ten of its times; the scene names the time kept as `ClockHour` and `ClockMinute`; the clock used; then the dial.
   - **The way back.** The door on step 0, held; on tick 36 `Bank.330D_` with `Bank.Vault_Opens` and the door playing; the class's hold off that tick; the door open on tick 66.
   - **The moans.** The first on tick 37, all four, every 5-14 seconds; none without the moans. Fred walks in from Street 3, Daphne from the vault.
   - **The dial.** The hands stopped on step 0 and the time `ANIM_VAULT_CLOCK_TIME10_23`; where a hand points for seven mouse positions; the minute hand caught and turned 23 steps forward, on 23 by tick 25, with 23 clicks; the hour hand turned 2 steps back to 10 by tick 4, with 2 clicks; let go, the vault opens and the bank loads.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, from profiles in the original's form:
   - **The clock on the door.** The van opened the toolbar, the broken clock went onto the vault door, the bank drew 5:00, `Bank_Vault.Clock_Spooky_0500_` played, and the dial loaded.
   - **The dial.** From a profile with the time 10:23, the minute hand and then the hour hand dragged there with the button held; the vault opened on tick 223 (220 on a second run), and back in the bank the door swung open on tick 36.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **The press, not the release.** The original's rooms that read a click from game `+0x20` bit 4 act on the button coming up (the close-up's ICDouble, the artifact's pieces). The fork's clicks act on it going down. The dial needs both, and uses the fork's press and the button's state.
- **The dial's exit is taken once.** The original calls it on every tick until the room changes.
- **A new game's dial opens the vault.** `ClockHour` 12 and `ClockMinute` 0 match the hands' start, as in the original; the dial is reached only after the clock has drawn another time.

---

## Goal

Make Showdown's bank and the clock that opens its vault play as the
original does. Until now ROOM_P13_Bank and ROOM_Vault_Clock had the base
class: the vault door did nothing with the broken clock, and the dial's
hands couldn't be turned, so the vault never opened.

## Background

The bank ([scooby-exe](../formats/scooby-exe.md#the-bank-and-the-vault-clock-wp-039))
has the vault door, which works with the broken clock:
- **The clock on the door:** a scene names a time, drawn by level, and the
  gang goes to the clock's dial.
- **The dial:** the two hands are dragged round with the mouse to that
  time.
- **The way in:** the vault opens, and back in the bank the door swings
  open onto the vault (WP-038).

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BankRoom`:**
  - the door's lines, and the clock on the door with the time it draws;
  - the opening, the moans, and the gang walking in;
  - the door opening on the way back.
- **`VaultClockRoom`:** the hands caught, turned and let go; the click;
  the time shown; the vault opening.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The strong boxes' own rooms,** ROOM_SB1 to SB5.
- **The bank's four clickables,** which have no code in the bank's class.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the classes;
   - the door and the opening, by the story's state;
   - the door with the arrow, and with the clock on it;
   - the time drawn for each level, the scene that names it, the clock
     used, and the dial;
   - the door opening on the way back, with its ticks;
   - the moans, and the gang walking in;
   - the dial: its placements, where a hand points, and both hands dragged
     to the time, a step a tick, with their clicks, the vault opening and
     the way back.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the clock from the toolbar onto the door, its scene, and the dial;
   - both hands dragged to the time, the vault opening, and the door
     swinging open.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-bank-and-the-vault-clock-wp-039): the bank and the vault clock, and the mouse flags.
