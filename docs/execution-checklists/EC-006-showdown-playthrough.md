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
**Status:** Not executed (drafted 2026-11-19).

A full playthrough is the canonical sprawl case: every stuck exit invites a
detour into the room's code. This checklist holds the line — observe, log,
move on. The only thing that stops the run is a hard progression blocker (no
legal way forward), which is itself the top finding.

---

## Pre-flight

- [ ] Pre-flight verdict: **READY** — fill in `docs/reference/pre-flight-WP-079-YYYY-MM-DD.md` and commit it before the run; `NOT READY` blocks this session.
- [ ] Fork at `C:\dev\scummvm` on `scooby-engine`, built Scooby-only against the pin (`c553503d9d`): `0 errors, 0 warnings`. Build command + commit hash recorded here: ____
- [ ] *Showdown in Ghost Town* ISO mounted, unmodified; mount path + ISO SHA-256 recorded here: ____
- [ ] Capture sink ready for screenshots/logs under a gitignored path (per [tools/exes/README](../../tools/exes/README.md)); no raw game data leaves the gitignored tree.
- [ ] [WP-079](../work-packets/WP-079-showdown-closeout.md) open in a second window for the §Result write-up.

---

## Step 0 — Boot and new game (time-box: 15 min)

- [ ] Launcher detects the mounted disc as `scooby:showdown` with no manual identification (gate 3 evidence).
- [ ] Title → main menu → level select; start a **new game** at the level/difficulty recorded here: ____
- [ ] Sign In: create a player; the new game sets the story's start values ([WP-028](../work-packets/WP-028-sign-in.md)).
- [ ] First story room (Town Center) loads with its opening and music ([WP-029](../work-packets/WP-029-room-setup.md)).

**Outcome:** a running new game at Town Center, or the first blocker logged.

## Step 1 — Story playthrough (time-box: open; this is the run)

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

- [ ] Every beat reached; no missing asset, no crash, no assertion, no dead-end.
- [ ] Any ✗ captured (screenshot + the `--debugflags` log line) under the gitignored capture path.

**Outcome:** credits reached, or the run stopped at the first hard blocker
(logged as gap #1).

## Step 2 — Save/load cycle (time-box: 20 min)

- [ ] Mid-run, save through ScummVM's standard dialog before a room transition.
- [ ] Quit the engine fully; relaunch.
- [ ] Load the save; confirm room, inventory, clues and puzzle flags restore ([02-SCUMMVM-INTEGRATION §9](../02-SCUMMVM-INTEGRATION.md)).

## Step 3 — Acceptance-gate walk (time-box: 45 min)

Record pass/fail + evidence for each of the ten merge-blocking gates
([02-SCUMMVM-INTEGRATION §Acceptance gates](../02-SCUMMVM-INTEGRATION.md#acceptance-gates-tldr)).
Re-run the mechanical checks; do not quote an earlier WP.

| Gate | Check | Result | Evidence |
|---|---|---|---|
| 1 | Clean build against the pin | ☐ | |
| 2 | Registered via `MetaEngineDetection`, launcher discovers it | ☐ | |
| 3 | Detects *Showdown*, no false positive on unrelated files | ☐ | |
| 4 | `grep -E '(fopen|std::ifstream|CreateFile[AW]?)' engines/scooby/` → none outside comments | ☐ | |
| 5 | All audio via `Audio::Mixer`; no DirectSound/platform audio | ☐ | |
| 6 | Bink via `Video::BinkDecoder`; no `binkw32.dll` loaded | ☐ | |
| 7 | Single-threaded; no `pthread`/`std::thread`/worker threads | ☐ | |
| 8 | Passes `devtools/code_check.sh` with zero warnings | ☐ | |
| 9 | GPL-3.0 header on every engine `.cpp`/`.h` | ☐ | |
| 10 | Declared `ADGF_TESTING` (or higher) | ☐ | |

- [ ] Per-variant *Showdown* MD5s recorded from [`detection_tables.h`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/detection_tables.h).

## Step 4 — Wiki page + verdict (time-box: 45 min)

- [ ] Draft the ScummVM `Scooby` wiki-page content as a committed repo doc (e.g. `docs/reference/scummvm-wiki-scooby.md`): supported titles, known limitations, required game-data file list, save-state status ([§12](../02-SCUMMVM-INTEGRATION.md#12-upstream-pr-checklist)).
- [ ] Write the **go/no-go verdict** in [WP-079 §Result](../work-packets/WP-079-showdown-closeout.md): go only if Step 1 reached credits clean **and** every gate is green.
- [ ] Compile the **gap list**: every ⚠/✗ and failed gate, each tagged with the follow-up WP that owns its fix.

---

## Definition of done

- [ ] All step outcomes recorded; the beat table and gate table filled in.
- [ ] WP-079 exit criteria 1–6 each satisfied or explicitly marked unmet with its gap.
- [ ] Go/no-go verdict written; gap list complete with follow-up-WP tags.
- [ ] WP-079 status updated in [WORK_INDEX](../work-packets/WORK_INDEX.md) (✅ on a clean go; stays 🚧 if a blocker was hit).

## Out-of-scope captures

Temptations logged here as one-liners for future WPs, **not pursued in this
session**:

- (none yet — fill during the run)
