---
layout: default
title: "WP-058: Phantom's souvenir shop"
---

# WP-058: Phantom's souvenir shop: the tokens buy Fred a bottle (Gen 1)

**Status:** 🚧 In progress (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-057 ✅ (Phantom's story values), WP-023 ✅ (the toolbar), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-058-2026-11-16](../reference/pre-flight-WP-058-2026-11-16.md)

---

## Result (2026-11-16)

Pending: the check against the reference, the live run and the regression.

---

## Goal

Make Phantom's souvenir shop, `ROOM_P03_Souvenir_Shop`, play as the
original does. Until now it had the base class:
- the tokens did nothing on the empty bottle;
- the shop had no introduction, and Jane never screamed there.

## Background

The souvenir shop ([scooby-exe](../formats/scooby-exe.md#phantoms-souvenir-shop-wp-058)):
- **The tokens buy the empty bottle.** Fred fetches it from the shelf, and
  it goes in the toolbar.
- **The opening** is the shop's introduction, the first time. While Jane is
  screaming, it is a scream and the gang's reply instead.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SouvenirShopRoom`:**
  - the bottle and the hotspot;
  - the openings;
  - Fred's fetch;
  - leaving while bought;
  - `IntroDone`.
- **`RoomScript::checkOpening()`:** the base room's `+0x3C`, so a class can
  run it again.
- **A `script` level 3 check** against an independent reference.

## Exit criteria

1. [ ] Both titles match an independent reference line for line:
   - the class;
   - the placements;
   - the openings by `IntroDone` and `Screaming`, with Fred's walk-in;
   - the screams;
   - the bottle with the arrow and with the tokens;
   - Fred's fetch, with its ticks;
   - the bottle once taken;
   - leaving while bought;
   - the hotspot's lines;
   - the profile.

   Showdown prints that it has no souvenir shop.
2. [ ] Live, in Phantom: the bottle with the arrow, then the tokens from
   the toolbar on it; Fred fetches it into the toolbar.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the shop's opening and key. The
   fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-souvenir-shop-wp-058): the
  souvenir shop.
