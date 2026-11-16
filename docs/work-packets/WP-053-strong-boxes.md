---
layout: default
title: "WP-053: Showdown's strong boxes"
---

# WP-053: Showdown's strong boxes: a lid opens, then the vault (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-040 ✅ (the bank vault, and these rooms found unreachable), WP-019 ✅ (sound)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Two hours
**Pre-flight:** [pre-flight-WP-053-2026-11-15](../reference/pre-flight-WP-053-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line: the class
   for all five rooms; in each, the lid, the sound, the scene and the way
   back, with their ticks. Phantom prints that it has no chase, as its
   reference does.
2. [ ] Live, in Showdown, from a profile starting in ROOM_SB1: the lid
   opens, `340D_` plays, and the vault follows.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-bank-vault-and-the-open-safe-wp-038):
  the strong boxes' class.
