---
layout: default
title: "WP-034: Street 1 and the Clues"
---

# WP-034: Showdown's Street 1, and the clue a suspect gives (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (game logic: the story rooms)
**Depends on:** WP-033 ✅ (the street hooks), WP-031 ✅ (Big Head, the suspects and clues), WP-028 ✅ (the story's values)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-034-2026-11-14](../reference/pre-flight-WP-034-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. The clue a suspect gives | ✅ `giveClue()` follows `0x42F990`. At `script` level 3 the check draws 40 times for each of the 25 villain and giver pairs, from fresh clue slots. Every rule held: the villain's red herring is about neither of them (200 of 200), and anyone else gives one of their own three (800 of 800). With all three of theirs found, level 0 gives their fourth or fifth (800 of 800) and level 1 a red herring (800 of 800). A clue owner gives nothing more (1,000 of 1,000). |
| 2. Street 1 against the trace | ✅ From Town Center, Fred walks in `DR`, with the moaning opening.<br>• No Sheriff before Artie's clue. The office door is shut and its exit not built.<br>• The Sheriff's first click goes to `ROOM_Big_Head` with him met; the next goes to `ROOM_Sheriff`. In his puzzle, waiting, the hints play `Hint1_`, `Hint2_`, `Hint3_`, `Hint1_` with input on.<br>• The sign given: he has it, `SheriffWaiting` goes off, and `220D1_` plays. Then one of `130C1_` to `130C3_` and one of his own three clues; he plays `ANIM_SHERIFFGIVES`, input held, then `Global.Thank_You_` and `ROOM_Suspect_Chooser`.<br>• Back: the office is open, he stands at (501, 270), and he says `Global.1000SA_`.<br>• The trough says `130D_`, `130D2_`, `130D3_`, `130D_` before the handle. With it, `130E_`; then `PUT_HANDLE` with `130F2_` and `TROUGHB`, `PUMPA` with `130F_` and `TROUGHC`, `PUMPB` with `130F3_`, `TROUGHD` and the key, then `PUMPC` with no scene.<br>• Scooby takes the key as `OBJ_SCOOBY_P03_TAKES_KEY` (60 ticks).<br>• `PumpAttempts`, `SheriffIntroPlayed` and `KeyVisible` read back.<br>• The second hotspot's scene comes as it plays A.<br>• With the brick taken, the Sheriff is gone and the trough asks for the brick. Washed, it gives `Wash_Brick_` and `FinalClue`, then movie 14 and `ROOM_Suspect_Chooser`.<br>• To the post office with the lantern, no scene. |
| 3. Live, Showdown | ✅ Started from a profile in the Sheriff's puzzle with the sign in the toolbar, driven by the engine's `test_script`:<br>• A click on the Sheriff gave `Hint1_`. The van opened the toolbar, and the sign's pad made it the cursor.<br>• The Sheriff took the sign (`220D1_`) and gave `SHERIFF_SPURS` after `130C2_`. He played `GIVES`, and `Global.Thank_You_` took the gang to the suspects and clues, which showed Artie's map and the Sheriff's spurs.<br>• Six frames were captured. |
| 4. Build and regressions | ✅ Scooby-only build: 0 errors, 0 warnings in `engines/scooby/`. Fork commit [`93cc76ae2f`](https://github.com/barefootbetters/scummvm/commit/93cc76ae2f) is on WP-033's `794cb1a830`, inside `engines/scooby/`, and is pushed. Against WP-033 the earlier checks match line for line, except Street 1's three new profile keys (Showdown 268 → 271) and Street 3's corrected hotspot line. Phantom: 0 differences. The story checks give the same 128 lines on three runs. Every room's music and opening still match WP-029's reference. |

**Deviations and gaps:**

- **Street 3's third hotspot** (WP-033) tested the sequence playing. The trace reads the clickable's state (`+0x60`), so its scene comes while it plays A. Fixed here, and WP-033's result is corrected.
- **The Sheriff's click** is taken by the room's class as the mouse is clicked, not in the room's tick (`0x42AF60` reads the click flags there). Clicks with other items go on to the game's wrong-item line, as before.
- **Phantom's clue function** isn't traced; `giveClue()` is Showdown's. The check runs only on Showdown.
- **The setup check now starts from a new game's `SheriffWaiting`.** With no story state, Street 1 owes the Sheriff his clue on entry and starts that scene, which is right but isn't what the setup check measures.

---

## Goal

Play Showdown's Street 1 as its class has it, with the clue each suspect
gives (game vtable `+0x44`), which Street 1 is the first to call.

## Background

Traced headless in Ghidra 12.1.4; the functions are in
[scooby-exe](../formats/scooby-exe.md#street-1-and-the-clues-wp-034).

## Scope

**In scope (fork, `engines/scooby/` only):**

- `giveClue()` (`0x42F990`, `0x4301E0`, `0x4301A0`).
- Street 1's class.
- Hooks:
  - the room left (vtable `+0x10`);
  - a requires object's own cursor, and the sequence of any claimed placement;
  - character state `0xD`.
- `script` level 3 checks.

**Out of scope:** Phantom's clue function; the Sheriff's close-up room
(`ROOM_Sheriff`).

## Exit criteria

1. [x] `giveClue()` follows `0x42F990` for every villain and giver.
2. [x] Street 1 matches the trace.
3. [x] Live in Showdown: the Sheriff, the sign, his clue.
4. [x] Scooby-only build with 0 errors and 0 warnings; earlier checks
   unchanged except as listed; the fork diff stays inside `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): Street 1 and the clues.
- WORK_INDEX row and findings line.
