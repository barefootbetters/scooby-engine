---
layout: default
title: "WP-051: Showdown's saloon and Artie"
---

# WP-051: Showdown's saloon and Artie: the gag, the keys and the chains (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-050 ✅ (the whistle puzzle), WP-031 ✅ (suspects met), WP-021 ✅ (clickables), WP-019 ✅ (sound and lip sync)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-051-2026-11-15](../reference/pre-flight-WP-051-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp052_ref.py`: WP-050's, plus the saloon and ROOM_Artie, written from the trace before the engine ran. It reads the placements and step counts from the art, and which sounds and scenes are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 177 lines on Showdown: the earlier 166 and 11 for the saloon. On Phantom both print the one line saying there is no chase.

The first run matched 173. The four other lines came from two causes, both in the check:
- **A stale build.** The run used a build from before the check's last edits, so three lines still had their old wording.
- **The order of the keys line.** The check read the class's keys, then left the saloon for Street 3. Leaving sets `ClickableOpen` again from the hotspots' states (`0x414820`), so the key read was lost. The check now reads them in Street 3.

The class and the reference didn't change. With the check rebuilt, all 177 match.

**Exit criteria:**

1. **Against the reference:** ✅ Showdown:
   - **Entry.** A render entity at depth −1001 under layer 0 holds the piano (depth −11), hotspots 2–8 and the keys (depth −1, the keys hidden) and the chandelier (depth −1, looping); the bull is a requires object in layer 0. The hotspots with keys (4, 5, 8) are on their `K`; 3–8 have no open hand. Artie is in state 14 as `OBJ_ARTIE_MASKED`, set `_3`; Daphne walks in. The opening is `Saloon.360A_`, the snacks needed 2.
   - **The exits,** gagged: each keeps the gang here with one of the four lines, held.
   - **The gag.** Artie clicked: Velma's `UNGAG_ARTIE` (55 steps) on tick 1. Her line on tick 19, Artie idle as `OBJ_ARTIE_3` and the moans off on tick 100, and on tick 166 `GAG_GONE_`, held, with the six open hands.
   - **The keys.** Each hotspot's click, its next state and the tick it stops; the three keys show at depth 1 with a `360G` line.
   - **The chains.** With three keys, then one, the exits keep the gang with the matching lines. Each key: ROOM_Artie, the chains on `A`, `B`, `C`, their sound on tick 36, and the saloon 71 + 3 × their steps ticks after entry, through movie 6 the last time. Back, Artie is `OBJ_ARTIE_2`, then `_1`, then free: a `360C` line, his clue, met, `GIVES` and the thanks.
   - **The piano, the bull, the moans, the stage, the keys saved:** the music group off while it plays its tune; `390A_`–`390A3_`, movie 5 and the pump handle; a moan on tick 37; `380A_`–`380A3_` by level; the keys written and read back.
2. **Live, Showdown:** ✅ Through `test_script`, minimized, from profiles in the original's form:
   - **The gag.** Artie clicked; Velma's line; `GAG_GONE_`, said by Artie, now ungagged.
   - **A key.** Hotspot 4 (on its `K`) clicked: it rests on `B` and `360G_` plays. The key clicked: ROOM_Artie, the chains and `Artie.Chains_A`, then the saloon again.
3. **Build and diff:** ✅

**Deviations and gaps:**

- **`rand()`:** the keys at reset and the random lines draw from the engine's own random source.
- **The cursor fades** (`0x435150` with 0, and with 0x12 in ROOM_Artie) are the hidden cursor of `isBusy`.
- **Velma's vtable `+0x10`** after her ungag starts isn't traced; the fork doesn't call it.
- **Artie and Shaggy clicked** (game `+0x20` & 4, their `+8`) are the class's `click()`. Like every click in the fork, they act on the press.

**Found on the way:**

- **A hotspot's `K` is hit elsewhere.** The `K` sequences have their own hit polygons: hotspot 4 is hit at (36, 212) on `K`, (52, 276) on `A`.
- **A missing count reads 0.** `0x40C670` is atoi on the profile string, so a profile without `ChainsLocked` reads 0. ROOM_Artie then has no chains sequence to stop on, and nothing happens; the original does the same. A profile the game writes always has the key.

---

## Goal

Make Showdown's saloon, ROOM_P12_Saloon, and Artie's chains, ROOM_Artie,
play as the original does. Until now both had the base class:
- Artie was neither gagged nor chained;
- the hotspots hid no keys;
- nothing kept the gang in the saloon;
- the piano, the bull and the pump handle did nothing of their own.

## Background

The saloon ([scooby-exe](../formats/scooby-exe.md#the-saloon-and-artie-wp-051)):
- **Artie** is gagged and in three chains. Clicked, Velma takes the gag off.
- **Three keys** hide behind three of six hotspots, drawn at a new game.
  Each key found and clicked takes a chain off in ROOM_Artie.
- **Until he is free,** the gang won't leave. Free, he gives his clue.
- **The piano** stops the music while it plays. **The bull** takes the
  Buffalo nickel, and the pump handle falls from the chandelier.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`SaloonRoom`:**
  - the placements under its own buffer sprite;
  - the gag, the keys and the exits it keeps;
  - Artie's clue;
  - the piano, the bull, the pump handle and the moans;
  - its keys in the profile.
- **`ArtieRoom`:** a chain off, and back.
- **The pieces they need:**
  - a character's looping special state (0xE) and its set;
  - a class's own buffer sprite in the room loader.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the classes;
   - the placements on entry, Artie gagged, and the class's values;
   - the exits kept while gagged;
   - the gag, with its ticks;
   - the six hotspots, the keys behind three;
   - the exits kept while chained, each key to ROOM_Artie and back, the
     chains, Artie's clue, GIVES and the thanks;
   - the piano and the music;
   - the bull and the pump handle;
   - the moans and the idle line;
   - the stage's snacks;
   - the keys saved and read.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from a profile in the original's form: the gag,
   a key found and used, ROOM_Artie and back.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-saloon-and-artie-wp-051): the
  saloon and Artie's chains.
