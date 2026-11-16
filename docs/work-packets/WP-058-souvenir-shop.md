---
layout: default
title: "WP-058: Phantom's souvenir shop"
---

# WP-058: Phantom's souvenir shop: the tokens buy Fred a bottle (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-057 ✅ (Phantom's story values), WP-023 ✅ (the toolbar), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-058-2026-11-16](../reference/pre-flight-WP-058-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `wp060_ref.py`: WP-057's, plus the souvenir shop, written from the trace before the engine ran. It reads the placements, the hotspot's states and Fred's fetch from the art and `object.ini`, and which scenes and lines are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now has 7 shop lines on Phantom (25 in all), and one on Showdown, which has no souvenir shop (216 in all).

The first run differed on two lines, both the check's own bugs:
- it took Jane's scream names for 30 characters long (they are 29), so it saw none;
- it read eight toolbar slots where there are four, so it read past the end.

The second run matched all 25 lines on Phantom and all 216 on Showdown.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**The placements.** The bottle a requires object at depth 0; the hotspot a clickable at its `priority=` 150, placed on its B.<br>**The openings.** From the town, Fred walks in (`DL`, 50 in front). The first visit has `Souvenir_Shop.1201_`, holding input, and sets `IntroDone`; the next has none. While `Screaming`, `330A1_` and one of Jane's screams, 1, 2, 3 and 5 over 100 visits.<br>**The bottle.** With the arrow, `120A_` holds input. With the tokens, they leave the toolbar, the cursor is the arrow, and the shop holds input. Fred fetches it at tick 1 (`OBJ_FRED_P03_GET_WATER_BOTTLE`, state 13, with `Fred_Takes_Bottle`); the shelf shows `EMPTYB`. At tick 67 the bottle is in the toolbar and `120B_` holds input. On the next visit the bottle is a plain sprite.<br>**Leaving while bought** still puts the bottle in the toolbar.<br>**The hotspot:** B gives `120X_`, C nothing, D (next A) `120X1_`.<br>**The profile:** `IntroDone`, cleared by the reset.<br>Showdown prints that it has no souvenir shop. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized, from a profile with the tokens in the toolbar:<br>**The arrow:** the bottle clicked with the arrow gave `120A_`, Shaggy and Fred.<br>**The tokens:** taken from the open toolbar onto the bottle, they left their slot. Fred fetched the bottle with `Fred_Takes_Bottle`; it went in the toolbar's first slot, and Fred said `120B_`. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms).<br>**Showdown:** its other checks are identical to WP-057's run but for the imported clue name in the profile check. That line differs between this build's own two runs, so it varies by run (see below).<br>**Phantom:** its checks differ only as expected:<br>• the setup check now shows the shop's first-visit opening;<br>• the profile has the shop's `IntroDone`;<br>• the drawbridge's keys are random by design.<br>Fork commit [`831ce91cc3`](https://github.com/barefootbetters/scummvm/commit/831ce91cc3) (9 files staged by name) is pushed. |

**Deviations and gaps:**

- **The tick clock's restart** (`0x437540`) at Fred's fetch isn't kept, as in WP-057.

**Found on the way:**

- **The profile check's imported clue name varies between runs.** Two runs of this WP's build gave `SHERIFF_FEATHER` and `SHERIFF_MAP`. WP-055 and WP-056 had put the flip down to their own changes; their pages now carry a correction.
- **The shop's hotspot starts on its B,** so its first click gives `120X_`.
- **While Jane screams, the shop's introduction never plays,** and `IntroDone` stays off until a visit without her.

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

1. [x] Both titles match an independent reference line for line:
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
2. [x] Live, in Phantom: the bottle with the arrow, then the tokens from
   the toolbar on it; Fred fetches it into the toolbar.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for the shop's opening and key. The
   fork diff stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-souvenir-shop-wp-058): the
  souvenir shop.
