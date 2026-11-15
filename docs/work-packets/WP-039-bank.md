---
layout: default
title: "WP-039: Showdown's bank"
---

# WP-039: Showdown's bank: the vault door and its clock (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-038 ✅ (the vault), WP-023 ✅ (requires objects)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-039-2026-11-15](../reference/pre-flight-WP-039-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
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
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the clock from the toolbar onto the door, its scene, and the dial;
   - both hands dragged to the time, the vault opening, and the door
     swinging open.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-bank-and-the-vault-clock-wp-039): the bank and the vault clock, and the mouse flags.
