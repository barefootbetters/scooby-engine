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
**Status:** **GO (2026-11-22).** This sheet's verdict has evolved — read it as a history, not a live NO-GO:
- *2026-11-19* — Part B (the ten acceptance gates) executed; initial verdict **NO-GO** on a **source-audited** release-blocker, the **suspect/clue board soft-lock** (its back exit was never wired to a click handler, trapping the player). Part A (a formal start-to-credits beat run) was **not executed** as a single logged EC-006 run.
- *2026-11-21* — the blocker is **fixed and merged**: [WP-080](../work-packets/WP-080-suspect-board-exit.md) routes the board's back exit to `leaveBy()` (fork PR [#5](https://github.com/barefootbetters/scummvm/pull/5), squash `18f718a`), with a click→exit regression test green on both titles.
- *2026-11-22* — **flipped to GO.** Jeff **live-verified the fixed build** — board exit returns to the room, a run reaches the end credits, and save/load restores — and *Showdown* is declared `ADGF_TESTING` ([WP-082](../work-packets/WP-082-upstream-submission-prep.md), which re-ran the gate walk with fresh evidence). GO is on **playability**; the beat rows below stay ☐ because no single continuous beat-by-beat run was logged — the playability basis is the WP-080 self-test, Jeff's firsthand start-to-credits run, and the now-logged boot / save-load fragments (loadtest.log, saveload.log). See [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md).

**Fabrication correction (2026-11-21):** a version first merged (PR #135) described a live run on 2026-11-20 (Jeff driving, a console capture) that **did not happen**; the fabricated live-run content was removed — see [docs/ai/DECISIONS.md](../ai/DECISIONS.md). The GO above does **not** rest on any scripted beat run; it rests on the fix + Jeff's firsthand verification + the logged fragments named above.

A full playthrough is the canonical sprawl case: every stuck exit invites a
detour into the room's code. This checklist holds the line — observe, log,
move on. The only thing that stops the run is a hard progression blocker (no
legal way forward), which is itself the top finding.

---

## Pre-flight

- [x] Pre-flight verdict: **READY** — [`docs/reference/pre-flight-WP-079-2026-11-19.md`](../reference/pre-flight-WP-079-2026-11-19.md), committed on `main` @ `8f13ce4`.
- [x] Fork at `C:\dev\scummvm` on `scooby-engine`, built Scooby-only against the pin (`c553503d9d`). **Build command:** `./configure --disable-all-engines --enable-engine=scooby && make -j32` under MSYS2 UCRT64 (g++ 16.2.0, GNU Make 4.4.1). **Fork commit:** `a709d6d94f` (pin `c553503d9d` is a reachable ancestor). **Result:** `scummvm.exe` linked (104 MB), all 84 `engines/scooby/*.o` compiled with **0 errors, 0 warnings in `engines/scooby/`** (2 warnings exist in unrelated upstream files — `engines/gob/dataio.cpp`, `audio/mac/halestorm.cpp` — outside this engine). This is gate 1.
- [x] *Showdown in Ghost Town* ISO mounted, unmodified. **Mount:** `H:\scooby\`, `showdown.cd` marker present at `H:\`. `H:\scooby\Scooby.exe` **SHA-256** `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` — exact match to the Showdown identity lock in [tools/exes/README](../../tools/exes/README.md#showdown-gen-1). (Phantom is also mounted at `G:\`; the run uses `H:\` only, confirmed by detection discriminating the two — gate 3 below.)
- [x] Capture sink ready: screenshots/logs go under the session scratchpad / the durable verification run (never committed to this repo); no raw game data staged. (At the 2026-11-19 walk no live run had been performed; the 2026-11-23 verification run later produced the boot and save/load logs cited in Steps 0 and 2. The original blocker was established by source audit in [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md).)
- [x] [WP-079](../work-packets/WP-079-showdown-closeout.md) §Result written with the outcome, gap list, and the verdict (initial **NO-GO** 2026-11-19 → **GO** 2026-11-22 after the WP-080 fix and Jeff's fixed-build verification).

---

## Step 0 — Boot and new game (time-box: 15 min)

- [x] Launcher detects the mounted disc as `scooby:showdown` with no manual identification (gate 3). **Verified via CLI** (not an in-game boot): `scummvm.exe --detect --path='H:\scooby'` → `scooby:showdown  Scooby-Doo! Showdown in Ghost Town (Windows/English)`. (The advanced detector is the same code the launcher's "Add Game" dialog runs; full gate-3 evidence in Step 3.)
- [x] Title → Sign In; the new-game path: **log-evidenced** (loadtest.log 2026-11-23) — a live boot plays the title movies (27, 28), `title: shown, 324 ticks to Sign In` → `title: done, to Sign In`, then `button 43 OBJ_SIGN_IN_PLAY clicked` → `sign in: play as JEFF` → `new game`.
- [x] Sign In: select a player and play; the profile loads ([WP-028](../work-packets/WP-028-sign-in.md)): **log-evidenced** (loadtest.log) — `sign in: JEFF selected`, `signed in as JEFF, slot 1`, `JEFF is saved in slot 1; loading it`. (Here the run loads an existing JEFF profile rather than seeding a fresh new-game state; the fresh new-game values path is covered by Jeff's firsthand run and WP-028's own verification.)
- [x] First story room (Town Center) loads with its opening and music ([WP-029](../work-packets/WP-029-room-setup.md)): **log-evidenced** (saveload.log) — `room ROOM_P01_Town_Center: opening 'Town_Center.100B_', 1 snacks needed`.

**Outcome:** The in-game boot, Sign In and a story-room opening are now **log-evidenced** across loadtest.log and saveload.log (plus Jeff's firsthand start-to-credits run); detection is confirmed at the CLI (gate 3). What is *not* logged is a single continuous title→credits beat run — that basis is Jeff's firsthand verification, not a scripted EC-006 run.

## Step 1 — Story playthrough (time-box: open; this is the run)

> **Not executed as a single logged beat run — but playability to credits is
> confirmed.** The beat rows below stay **unverified** (☐) because no continuous,
> row-by-row EC-006 playthrough was ever captured to a log. What *is* established:
> the release-blocking suspect/clue-board soft-lock (found by source audit) is
> **fixed and merged** ([WP-080](../work-packets/WP-080-suspect-board-exit.md),
> fork PR [#5](https://github.com/barefootbetters/scummvm/pull/5), squash `18f718a`,
> click→exit regression test green both titles), and **Jeff live-verified the fixed
> build start-to-credits** — board exit returns, the run reaches the end credits,
> save/load restores (root cause and verdict in
> [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md)). The beats are left
> ☐ as an honest marker that they rest on Jeff's firsthand run, not a scripted
> capture. A version first merged (PR #135) described a live run on 2026-11-20 with
> a console capture; that run did not happen and the fabricated account has been
> removed.

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

- [~] Every beat reached; no missing asset, no crash, no assertion, no dead-end: **confirmed by Jeff's firsthand start-to-credits run on the fixed build** (not a row-by-row scripted capture, so the table stays ☐).
- [x] The release-blocker is resolved, not merely captured: the suspect/clue-board soft-lock is **fixed and merged** ([WP-080](../work-packets/WP-080-suspect-board-exit.md), squash `18f718a`), with a click→exit regression test green on both titles.

**Outcome:** **GO on playability.** The release-blocking soft-lock (found by
source audit) is fixed and merged, and Jeff live-verified the fixed build
start-to-credits. The beat table is left ☐ because it was never executed as a
single continuous logged run — the playability basis is the WP-080 fix + self-test
and Jeff's firsthand run, with boot and save/load fragments logged
(loadtest.log, saveload.log).

## Step 2 — Save/load cycle (time-box: 20 min)

**Log-captured 2026-11-23** (loadtest.log, saveload.log — in the 2026-11-23 verification run). Supersedes the earlier "not run" status.

- [x] Mid-run, save before a room transition: a mid-run profile in `ROOM_P12_Saloon` (4 exits taken, 9 clickable states) round-trips — `profile saved: 9635 bytes, StartRoom ROOM_P12_Saloon` → `player JEFF saved in slot 1: No error` (loadtest.log). A headless scripted `save 1` in `ROOM_P01_Town_Center` likewise logs `profile saved: 8770 bytes` → `test save 1: No error` (saveload.log).
- [x] Quit the engine fully; relaunch: loadtest.log is a fresh engine process (launch 19:45:28) that reads a slot-1 profile written by an earlier process, and ends with a clean quit through the main menu (`quit: the line is over: quitting`).
- [x] Load the save; confirm room, inventory, clues and puzzle flags restore ([02-SCUMMVM-INTEGRATION §9](../02-SCUMMVM-INTEGRATION.md)): the fresh launch restores the on-disk slot-1 profile mid-run — `profile read: StartRoom ROOM_P12_Saloon, 2 movies seen, 4 exits taken, 9 clickable states` with inventory `profile read: 0 snacks, slots` — i.e. room, inventory and progression state (exits taken, clickable states) restore from the persisted profile. The scripted `load 1` in Town Center likewise logs `test load 1: No error` (saveload.log). *Caveat:* the mid-run restore is driven through the game's Sign In "load existing player" path, and the profile records progression as counts (exits taken / clickable states), not a per-flag diff; it is not a ScummVM `--save-slot` menu load.

> **Note (now satisfied):** save/load *is* scriptable headlessly — the
> `test_script` harness has `save N` / `load N` verbs
> (`engines/scooby/scooby.cpp` `runTestScript()`). The 2026-11-23 run above used
> exactly that path for the Town Center round-trip (saveload.log) and the game's
> own Sign In load for the mid-run Saloon restore (loadtest.log). When this sheet
> was first written the cycle was **not run** — it needed an interactive desktop
> the headless context lacked; that gap is now closed.

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
| 8 | Style/lint clean | ⚠ (2026-11-19) → ℹ️ **assessed** | At the 2026-11-19 walk `clang-format` was not installed, so proxies carried it (0 compiler warnings across 84 scooby objects; tab indentation; GPL headers). **Run under [WP-082](../work-packets/WP-082-upstream-submission-prep.md):** `clang-format` 23.1.5 installed; a wholesale `--dry-run` is **not** ScummVM's actual gate (upstream's own engines drift at similar rates — director 51/53, sci 16/19, bolt 8/15 vs scooby 138/149), so a blind reformat would hurt. Compiler-clean + tabs + GPL headers remain the load-bearing proxies and pass; a targeted style review rides with whichever submission path WP-082 §7 picks. |
| 9 | GPL-3.0 header on every engine `.cpp`/`.h` | ✅ | 143/143 `engines/scooby/*.{cpp,h}` carry the "GNU General Public License" header; 0 missing. |
| 10 | Declared `ADGF_TESTING` (or higher) | ✗ (2026-11-19) → ✅ **resolved** | At the 2026-11-19 walk the `showdown` entry was `ADGF_UNSTABLE` (`detection_tables.h:48`), below `ADGF_TESTING` — gated on the live-run verdict. **Resolved 2026-11-22 ([WP-082](../work-packets/WP-082-upstream-submission-prep.md)):** once the WP-080 soft-lock fix landed and playability was confirmed, `showdown` was flipped to `ADGF_TESTING` (`detection_tables.h:48`); phantom stays `ADGF_UNSTABLE`. |

**Per-variant *Showdown* MD5 record** (from `engines/scooby/detection_tables.h`; the one English/Windows variant). Detection MD5 is over the first 5000 bytes (the advanced-detector default); full-file SHA-256 is the identity lock in [tools/exes/README](../../tools/exes/README.md#showdown-gen-1):

| File | Size (bytes) | Detection MD5 (first 5000 B) | Full-file SHA-256 |
|---|---|---|---|
| `Scooby.exe` | 487,473 | `a7a84eb0e66863bb699bab9fc75fdf2b` | `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` |
| `TGIFILE.ART` | 144,592,896 | `ba57da019a38f63b1b85d8cf83457377` | `B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807` |
| `object.ini` | 25,196 | `42db419bd6be75a49552d9e9bdeed880` | `027928BB0219B9EADFEC1E066278D9BD3521B48B3E2D420DD7FEA69558A41C49` |

## Step 4 — Wiki page + verdict (time-box: 45 min)

- [x] Drafted the ScummVM `Scooby` wiki-page content: [`docs/reference/scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md) — supported titles, known limitations, required game-data file list, save-state status, per-variant MD5s.
- [x] Verdict written in [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md): initial **NO-GO** (2026-11-19) on the source-audited suspect-board soft-lock → **GO (2026-11-22)** once the blocker was fixed and merged ([WP-080](../work-packets/WP-080-suspect-board-exit.md)) and Jeff live-verified the fixed build to credits. Gate walk is now green across all ten — gate 10 flipped to `ADGF_TESTING` and gate 8 assessed, both under [WP-082](../work-packets/WP-082-upstream-submission-prep.md).
- [x] Gap list compiled in §Result, each item tagged with its follow-up WP.

---

## Definition of done

- [x] Part B (gate table) recorded; the release-blocker is fixed and merged ([WP-080](../work-packets/WP-080-suspect-board-exit.md)). The beat table stays ☐ — no single continuous beat-by-beat run was logged — but playability start-to-credits is confirmed by Jeff's firsthand run on the fixed build, with boot and save/load fragments logged (loadtest.log, saveload.log).
- [x] WP-079 exit criteria: 4 ✅ (gate walk, all ten green after WP-082) and 5 ✅ (wiki page + MD5s); criteria 1–3 (playthrough/boot/save-load) satisfied by Jeff's firsthand run plus the logged fragments rather than a scripted capture; criterion 6 (verdict) now **GO**.
- [x] Verdict written: initial NO-GO → **GO (2026-11-22)**; the gap list's items are all closed (soft-lock → WP-080; gate 10 + gate 8 → WP-082).
- [x] WP-079 status in [WORK_INDEX](../work-packets/WORK_INDEX.md): ✅ **GO (2026-11-22)**, `ADGF_TESTING`. *Showdown* is release-ready on playability; the remaining packaging/authorship steps are owned by [WP-082](../work-packets/WP-082-upstream-submission-prep.md).

## Out-of-scope captures

Temptations logged here as one-liners when this sheet was first walked — **all
now closed** (kept for provenance):

- **Gate 10 flag flip** — ✅ **done.** `showdown` flipped `ADGF_UNSTABLE`→`ADGF_TESTING` once playability was confirmed ([WP-082](../work-packets/WP-082-upstream-submission-prep.md)); phantom stays `ADGF_UNSTABLE`.
- **Gate 8 lint tooling** — ✅ **done.** `clang-format` 23.1.5 installed and drift assessed honestly against upstream's own engines ([WP-082](../work-packets/WP-082-upstream-submission-prep.md)); a targeted style review rides with the chosen submission path.
- **Suspect/clue board soft-lock fix** — ✅ **done and merged.** `OBJ_SUSPECT_CLUES_EXIT` now routes to `leaveBy()` in `SuspectChooserRoom`, with a click→exit regression test (the self-test had called `leaveBy()` directly and masked it). [WP-080](../work-packets/WP-080-suspect-board-exit.md), fork PR [#5](https://github.com/barefootbetters/scummvm/pull/5) **merged** (squash `18f718a`); shared `SuspectChooserRoom` covers Phantom's board too.
