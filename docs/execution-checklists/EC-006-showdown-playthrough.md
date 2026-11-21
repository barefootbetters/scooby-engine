---
layout: default
title: "EC-006: Showdown playthrough run sheet"
---

# EC-006: Showdown closeout — playthrough and gate-walk checklist

**Paired WP:** [WP-079](../work-packets/WP-079-showdown-closeout.md)
**Purpose:** Keep the *Showdown* closeout run scoped and reproducible — a
single start-to-credits playthrough plus the release-gate walk — without it
sprawling into inline bug-fixing. Every defect found is **logged as a one-line
gap and the run continues**; fixes are follow-up WPs, never done here.
**Status:** Executed — **NO-GO** (Part B 2026-11-19; Part A live run 2026-11-20). Part B (release-gate walk) is complete with fresh evidence. Part A was run live on a real interactive desktop (Jeff driving, this session reading the `--debugflags=script,input --debuglevel=1` console): boot, the front end and the first rooms played clean, then the run hit a **hard progression blocker — the suspect/clue board soft-lock** (its back exit is unresponsive, no Esc/right-click escape), which traps the player and halts the run. Per the stop rule below, that blocker is the top finding and the go/no-go verdict is **NO-GO** — see [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md).

A full playthrough is the canonical sprawl case: every stuck exit invites a
detour into the room's code. This checklist holds the line — observe, log,
move on. The only thing that stops the run is a hard progression blocker (no
legal way forward), which is itself the top finding.

---

## Pre-flight

- [x] Pre-flight verdict: **READY** — [`docs/reference/pre-flight-WP-079-2026-11-19.md`](../reference/pre-flight-WP-079-2026-11-19.md), committed on `main` @ `8f13ce4`.
- [x] Fork at `C:\dev\scummvm` on `scooby-engine`, built Scooby-only against the pin (`c553503d9d`). **Build command:** `./configure --disable-all-engines --enable-engine=scooby && make -j32` under MSYS2 UCRT64 (g++ 16.2.0, GNU Make 4.4.1). **Fork commit:** `a709d6d94f` (pin `c553503d9d` is a reachable ancestor). **Result:** `scummvm.exe` linked (104 MB), all 84 `engines/scooby/*.o` compiled with **0 errors, 0 warnings in `engines/scooby/`** (2 warnings exist in unrelated upstream files — `engines/gob/dataio.cpp`, `audio/mac/halestorm.cpp` — outside this engine). This is gate 1.
- [x] *Showdown in Ghost Town* ISO mounted, unmodified. **Mount:** `H:\scooby\`, `showdown.cd` marker present at `H:\`. `H:\scooby\Scooby.exe` **SHA-256** `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` — exact match to the Showdown identity lock in [tools/exes/README](../../tools/exes/README.md#showdown-gen-1). (Phantom is also mounted at `G:\`; the run uses `H:\` only, confirmed by detection discriminating the two — gate 3 below.)
- [x] Capture sink: screenshots/logs under the session scratchpad (never committed); no raw game data staged. The live run's debug console + screenshots stayed in gitignored session paths; the blocker's evidence is quoted (not raw-captured) in [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md).
- [x] [WP-079](../work-packets/WP-079-showdown-closeout.md) §Result written with the outcome, gap list, and the **NO-GO** verdict.

---

## Step 0 — Boot and new game (time-box: 15 min)

- [x] Launcher detects the mounted disc as `scooby:showdown` with no manual identification (gate 3 evidence). **Verified** via `scummvm.exe --detect --path='H:\scooby'` → `scooby:showdown  Scooby-Doo! Showdown in Ghost Town (Windows/English)  H:\scooby\`. (The advanced detector is the same code the launcher's "Add Game" dialog runs.)
- [x] Title → main menu; start a **new game** at a difficulty: **✅** — title movies (27, 28) played, `ROOM_Title_Screen` → Sign In → `ROOM_Difficulty`; picked Spooky; intro movie 1 (671 frames) played to `ROOM_P01_Town_Center`.
- [x] Sign In: create a player; the new game sets the story's start values ([WP-028](../work-packets/WP-028-sign-in.md)): **✅** — `sign in: play as J` → `new game` → `signed in as J, slot 2`; first-room profile saved (`player J saved in slot 2: No error`).
- [x] First story room (Town Center) loads with its opening and music ([WP-029](../work-packets/WP-029-room-setup.md)): **✅** — `ROOM_P01_Town_Center` opened scene `Town_Center.100B_` with Town-Center music; characters, hotspots and exits present.

**Outcome:** **✅ boot clean, on a real interactive desktop (2026-11-20).** Detection, title sequence, sign-in, difficulty, intro movie and the first room all rendered and played correctly. (The earlier headless/`test_script` boot attempts failed only because the SDL backend needs an interactive desktop — not an engine defect; the live run supersedes them.)

## Step 1 — Story playthrough (time-box: open; this is the run)

> **Run executed 2026-11-20 — halted early by a cross-cutting blocker.** On a
> real desktop the gang moved through the opening rooms cleanly (Town Center →
> Street 2 → Street 3 → Saloon; scenes, music, walking, the snack-to-Scooby
> mechanic and every room exit worked). But before the story beats below were
> completed, opening the suspect/clue board (the toolbar magnifier, available in
> every room) **soft-locked the game** — its back exit is unresponsive and there
> is no Esc/right-click escape (full evidence + root cause in
> [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md)). Because the
> blocker is reachable from any room, the run could not continue, so the numbered
> story beats below stay **unverified** (☐) — they were not individually
> completed, and marking them otherwise would be fabrication. The blocker, not a
> beat-table row, is the finding.

Play straight through in the room order from
[WORK_INDEX §Current state](../work-packets/WORK_INDEX.md). Fill one row per
beat as you reach it. **Result** is one of ✅ (as expected) / ⚠ (works, minor
drift) / ✗ (blocker or missing asset — log in the gap list). Do not fix ✗
inline.

| # | Beat / room | Expected (opening · puzzle · item/clue · exit) | Result | Note / gap ref |
|---|---|---|---|---|
| 1 | Town Center + the 3 streets | first clue from the Sheriff (Street 1, washed brick for the final clue) | ☐ | |
| 2 | Chase → close-up (ICDouble) | his clue once the artifact is built; the safe combination | ☐ | |
| 3 | Artifact puzzle (bones) | drag jigsaw → `ArtifactsBuilt` → back to ICDouble | ☐ | |
| 4 | Bank → vault door clock | drag the hands to the named time → vault opens | ☐ | |
| 5 | Bank vault | combination opens the safe; strong box → dentures key | ☐ | |
| 6 | Back alley / open safe | climb through to the back alley | ☐ | |
| 7 | Boot Hill (×3) | dig the right grave for the brick; wrong grave = ghost | ☐ | |
| 8 | Tunnel (dark → lit) | push the crate through to the post office | ☐ | |
| 9 | Post office | lantern on the hole → lit tunnel | ☐ | |
| 10 | Hotel | Fred opens the hall; Daphne takes the nickel | ☐ | |
| 11 | Stage (levers) | raise the sandbags; free Jenny → hammer + clue | ☐ | |
| 12 | Jail | blanket, break the bed, drop into the dark tunnel | ☐ | |
| 13 | General Store | hammer breaks the clock; blanket on snakes → lantern | ☐ | |
| 14 | Sheriff's office | oil can frees the cell door; snacks before the jail | ☐ | |
| 15 | Railroad station + Gummy | whistle puzzle → `GummyPuzzle` → dentures → his clue | ☐ | |
| 16 | Saloon + Artie | ungag Artie; three keys free him | ☐ | |
| 17 | Sheriff's quiz | level + 2 right → `SheriffPuzzle` | ☐ | |
| 18 | Horseshoe corral | ten ringers each → Chase B5 | ☐ | |
| 19 | Pie Noon | pie fight until the chime → back to the saloon | ☐ | |
| 20 | Ghost spot(s) | pan, then on to Town Center ([WP-056](../work-packets/WP-056-ghost-spot.md)) | ☐ | |
| 21 | Final clue → accusation | clue book complete → accuse | ☐ | |
| 22 | Big Head + reveal | correct villain revealed ([WP-031](../work-packets/WP-031-accusation.md)) | ☐ | |
| 23 | Credits | roll to the end ([WP-030](../work-packets/WP-030-options-credits.md)) | ☐ | |

*(The exact beat order and difficulty-gated snack counts vary per run; the
table is the spine, not a script — follow the game's own flow and log what
actually happens.)*

- [x] Every beat reached; no missing asset, no crash, no assertion, no dead-end: **✗** — a hard progression blocker (the suspect-board soft-lock) was found and halted the run before the story beats completed.
- [x] Any ✗ captured (screenshot + the `--debugflags` log line) under the gitignored capture path: **✅** — the soft-lock's console lines (`suspects: … back to ROOM_P12_Saloon`, the exit click with no `exit … going to` dispatch) and screenshots captured in session paths; quoted in WP-079 §Result.

**Outcome:** **✗ HARD PROGRESSION BLOCKER** — the suspect/clue board soft-lock
(see WP-079 §Result for evidence and root cause). Per the stop rule, the run
stops here and the blocker is the top gap. Everything before it (boot, front
end, the opening rooms) ran clean.

## Step 2 — Save/load cycle (time-box: 20 min)

- [~] Mid-run, save before a room transition: **Partial** — the engine's per-transition **auto-save** was observed writing cleanly on every room change in the live run (`profile saved: NNNN bytes, StartRoom ROOM_…` → `player J saved in slot 2: No error`). The explicit manual save-slot step was **not reached** — the run hit the board soft-lock first.
- [ ] Quit the engine fully; relaunch: **NOT REACHED** (blocked).
- [ ] Load the save; confirm room, inventory, clues and puzzle flags restore ([02-SCUMMVM-INTEGRATION §9](../02-SCUMMVM-INTEGRATION.md)): **NOT REACHED** (blocked). The full save → quit → relaunch → load cycle moves to the blocker's fix WP, which resumes the run past the board.

> **Note for the live run:** save/load *is* scriptable headlessly once a
> display is available — the `test_script` harness has `save N` / `load N`
> verbs (`engines/scooby/scooby.cpp` `runTestScript()`), so the cycle can be a
> `start_room=…; save 1; quit` run followed by a `load 1; shot` run with a
> frame-compare, without solving any puzzle. It still needs the interactive
> desktop that Step 0 established is missing from the headless context.

## Step 3 — Acceptance-gate walk (time-box: 45 min)

Record pass/fail + evidence for each of the ten merge-blocking gates
([02-SCUMMVM-INTEGRATION §Acceptance gates](../02-SCUMMVM-INTEGRATION.md#acceptance-gates-tldr)).
Re-run the mechanical checks; do not quote an earlier WP.

| Gate | Check | Result | Evidence (fork `a709d6d94f`, re-run 2026-11-19) |
|---|---|---|---|
| 1 | Clean build against the pin | ✅ | `./configure --disable-all-engines --enable-engine=scooby && make -j32` (MSYS2 UCRT64, g++ 16.2.0). 84 `engines/scooby/*.o`, `scummvm.exe` linked, **0 warnings/0 errors in `engines/scooby/`**. (2 warnings in unrelated upstream files: `engines/gob/dataio.cpp`, `audio/mac/halestorm.cpp`.) |
| 2 | Registered via `MetaEngineDetection`, launcher discovers it | ✅ | `scummvm.exe --list-engines` → `scooby  Scooby-Doo (TerraGlyph)`; `--list-debugflags=scooby` lists the 5 channels (resource/graphics/audio/script/input). |
| 3 | Detects *Showdown*, no false positive on unrelated files | ✅ | `--detect --path='H:\scooby'` → `scooby:showdown`. Discrimination: `--path='G:\scooby'` (Phantom disc) → `scooby:phantomknight`, **not** showdown. Negative control: `--path='C:\dev\scummvm\dists'` → "could not find any game". |
| 4 | `grep -E '(fopen\|std::ifstream\|CreateFile[AW]?)' engines/scooby/` → none outside comments | ✅ | `grep -rnE '(fopen\|std::ifstream\|CreateFile[AW]?)' engines/scooby/` → **no matches.** |
| 5 | All audio via `Audio::Mixer`; no DirectSound/platform audio | ✅ | No `DirectSound`/`waveOut`/`XAudio`/`OpenAL`/`SDL_OpenAudio` calls; the only `DirectSound` tokens are two comments describing the *original* engine (`sound.cpp:109`, `sound_archive.cpp:179`). 45 `Audio::Mixer`-path references. |
| 6 | Bink via `Video::BinkDecoder`; no `binkw32.dll` loaded | ✅ | `grep -rniE 'binkw32' engines/scooby/` → **no matches.** (Movies play via `Video::BinkDecoder` per WP-022.) |
| 7 | Single-threaded; no `pthread`/`std::thread`/worker threads | ✅ | `grep -rnE '(pthread_\|std::thread\|CreateThread\|_beginthread)' engines/scooby/` → **no matches.** |
| 8 | Style/lint clean | ⚠ **not definitively run** | The gate's named script `devtools/code_check.sh` **does not exist at the pin**; `.clang-format` is present but `clang-format` is not installed in the build env (available via pacman; not installed to avoid an unprompted toolchain change). Proxies clean: 0 compiler warnings across 84 scooby objects; indentation is tab-based (the only space-prefixed lines are legitimate zero-base alignment continuations); GPL headers present (gate 9). **Gap: run clang-format (or rely on upstream CI) to get the authoritative pass** — rides with the upstream-PR WP. |
| 9 | GPL-3.0 header on every engine `.cpp`/`.h` | ✅ | 143/143 `engines/scooby/*.{cpp,h}` carry the "GNU General Public License" header; 0 missing. |
| 10 | Declared `ADGF_TESTING` (or higher) | ✗ **gap** | `detection_tables.h:48` — the `showdown` entry is `ADGF_UNSTABLE`, which is **below** `ADGF_TESTING` in ScummVM's stability ladder (`UNSTABLE` < `TESTING` < stable). For a shipping/initial-merge build the flag must be flipped to `ADGF_TESTING`. **Follow-up WP** (one-line `detection_tables.h` change, gated on the live-run verdict confirming the game is playable). |

**Per-variant *Showdown* MD5 record** (from `engines/scooby/detection_tables.h`; the one English/Windows variant). Detection MD5 is over the first 5000 bytes (the advanced-detector default); full-file SHA-256 is the identity lock in [tools/exes/README](../../tools/exes/README.md#showdown-gen-1):

| File | Size (bytes) | Detection MD5 (first 5000 B) | Full-file SHA-256 |
|---|---|---|---|
| `Scooby.exe` | 487,473 | `a7a84eb0e66863bb699bab9fc75fdf2b` | `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` |
| `TGIFILE.ART` | 144,592,896 | `ba57da019a38f63b1b85d8cf83457377` | `B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807` |
| `object.ini` | 25,196 | `42db419bd6be75a49552d9e9bdeed880` | `027928BB0219B9EADFEC1E066278D9BD3521B48B3E2D420DD7FEA69558A41C49` |

## Step 4 — Wiki page + verdict (time-box: 45 min)

- [x] Drafted the ScummVM `Scooby` wiki-page content: [`docs/reference/scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md) — supported titles, known limitations, required game-data file list, save-state status, per-variant MD5s.
- [x] Verdict written in [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md): **NO-GO** — the live run hit a hard progression blocker (the suspect-board soft-lock). Gate walk is green except gate 10 (✗ flag gap) and gate 8 (⚠ tool not run).
- [x] Gap list compiled in §Result, each item tagged with its follow-up WP.

---

## Definition of done

- [x] All step outcomes recorded; the **gate table is filled** (Part B) and the live run (Part A) is recorded with its blocker. The beat table stays ☐ — the run was halted by the cross-cutting board soft-lock before the story beats completed (not fabricated).
- [x] WP-079 exit criteria: 4 ✅ (gate walk) and 5 ✅ (wiki page + MD5s); criterion 1 **✗ NO-GO** (blocker), 2 not reached, 3 partial (auto-save clean; full cycle not reached); criterion 6 (verdict) satisfied as **NO-GO**.
- [x] Verdict written (NO-GO); gap list complete with follow-up-WP tags.
- [x] WP-079 status in [WORK_INDEX](../work-packets/WORK_INDEX.md): closed 🚧 **NO-GO** (not ✅). *Showdown* is not release-ready until the blocker's fix WP lands and the run reaches credits.

## Out-of-scope captures

Temptations logged here as one-liners for future WPs, **not pursued in this
session**:

- **Gate 10 flag flip** — `showdown` is `ADGF_UNSTABLE`; a shipping build needs `ADGF_TESTING`. Own follow-up WP, gated on the live-run verdict.
- **Gate 8 lint tooling** — install `clang-format` (ucrt-x86_64-clang-tools-extra) in the fork build env, or rely on upstream CI, to get an authoritative style pass. Rides with the upstream-PR WP.
- **Suspect/clue board soft-lock fix** — the blocker found by the live run: route `OBJ_SUSPECT_CLUES_EXIT` to `leaveBy()` in `SuspectChooserRoom` and add a click→exit regression test (the self-test at `scooby.cpp:1328` calls `leaveBy()` directly and masked it). Its own follow-up WP; it also resumes the playthrough past the board (beats 1–23) and runs the save/load cycle. Check Phantom's shared board too.
