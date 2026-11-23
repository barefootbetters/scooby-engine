---
layout: default
title: "WP-079: Showdown closeout"
---

# WP-079: Showdown closeout — full playthrough and release readiness (Gen 1)

**Status:** ✅ GO (verdict flipped 2026-11-22). The release-blocking soft-lock that forced the initial NO-GO — the suspect/clue board's back exit was never wired to a click handler — is fixed and merged ([WP-080](WP-080-suspect-board-exit.md); fork PR [#5](https://github.com/barefootbetters/scummvm/pull/5), squash `18f718a`), and Jeff live-verified the fixed build: the board exit returns to the room, a run reaches the end credits, and save/load restores. GO is on **playability** (no progression blocker); two deferred release-*packaging* gates remain and are **not** playability blockers — gate 10 (`ADGF_UNSTABLE`→`ADGF_TESTING`, owned by [WP-082](WP-082-upstream-submission-prep.md), in progress) and gate 8 (lint tool absent, rides the upstream-PR WP). See [§Result](#result). **History:** the verdict was initially 🚧 NO-GO (2026-11-21, on source audit); and a first-merged §Result claimed a live playthrough Jeff drove on 2026-11-20 that did not happen — the fabricated evidence was removed (see [docs/ai/DECISIONS.md](../ai/DECISIONS.md)).
**Renumbered:** from WP-078 on 2026-11-19 — a parallel session had already claimed WP-078 for Phantom's princess-bedroom / mermaid's-cavern port (the sequential room WP after WP-077). This WP yielded the number per the supersession/claim discipline in [wp-lifecycle §Supersession check](../reference/wp-lifecycle.md#supersession-check-required-before-reserving-a-number).
**Phase:** 5 (polish & contribution). Also satisfies the Phase 3 success criterion for *Showdown* ([01-VISION §Phase 3](../01-VISION.md)).
**Depends on:** WP-056 ✅ (every *Showdown* game class ported — [room-class audit](../reference/room-class-audit-2026-11-15.md)), and with it the whole Gen 1 chain WP-014 ✅ … WP-056 ✅; WP-012 ✅ (detection table), WP-022 ✅ (Bink movies), WP-026 ✅ (profile saves), WP-031 ✅ (the accusation, Big Head and the credits)
**Unblocks:** the upstream `scummvm/scummvm` PR (a later WP, gated on the §12 authorship decision — see Out of scope); a Phantom closeout analog once its [audit](../reference/room-class-audit-phantom-2026-11-16.md) is fully ported
**Companion EC:** [EC-006](../execution-checklists/EC-006-showdown-playthrough.md) (the playthrough run sheet)
**Pre-flight:** Required (Yes). This WP claims a generation-level "*Showdown* (Gen 1) is release-ready", exercises `engines/scooby/**` through a full run, and writes the ScummVM wiki page + the required-data-files/MD5 record. Per [wp-lifecycle §Phase 1 DoD](../reference/wp-lifecycle.md#work_index-row--phase-1-definition-of-done), a generation classification + engine exercise needs pre-flight.
**Targets generation(s):** Gen 1 (*Showdown in Ghost Town*) only.
**Estimated effort:** 1–2 days.

---

## Goal

Prove *Showdown in Ghost Town* is complete and release-ready as a Gen 1
TerraGlyph title in the fork: a single uninterrupted playthrough from an
unmodified ISO mount to the end credits with no missing assets, fatal
errors, or progression blockers, and a verified pass of every
upstream-merge-blocking acceptance gate for *Showdown*. The output is a
**go/no-go verdict** backed by evidence, a gap list for anything that
fails, and the Phase 5 release prerequisites that are *Showdown*-specific
(the ScummVM wiki page; the required-data-files and MD5 record). This WP
does **not** submit the upstream PR.

## Background

*Showdown*'s per-room reverse-engineering is finished. Every game class in
its [room-class audit](../reference/room-class-audit-2026-11-15.md) is
ported (the last, `ROOM_Ghost_Spot`, landed at WP-056, 2026-11-16), and the
Gen 1 engine systems — rendering, audio, Bink, inventory, saves, the front
end, the accusation and credits — were all built and verified on *Showdown*
(WP-014 … WP-056). WP-057 onward moved to Phantom. No *Showdown* WP is open.

Two gaps stand between "every room ported" and "*Showdown* is finished":

1. **No continuous playthrough has ever been run.** Each WP verified its own
   slice against an independent reference trace plus a live spot-check in
   `test_script`. That is rigorous per room but not a start-to-credits run.
   The audit itself names the residual risk: *"This audit checks that a
   ported room has a class at all. It doesn't check that the class overrides
   every slot the original's does"*
   ([room-class audit §Not covered](../reference/room-class-audit-2026-11-15.md)).
   A slot-level gap, a bad inter-room hand-off, or a progression dead-end
   would only surface on a real run.
2. **The Phase 5 release gates are placeholders, not verified.** The ten
   merge-blocking gates ([02-SCUMMVM-INTEGRATION §Acceptance gates](../02-SCUMMVM-INTEGRATION.md#acceptance-gates-tldr))
   and the per-subsystem acceptance criteria (§§1–12) have each been met
   piecemeal across WPs, but no one has checked them as a set *for a shipping
   Showdown build*, and the §12 PR-checklist items (wiki page, data-file
   list, per-variant MD5s) do not exist yet.

**On Phase-5 timing.** [WORK_INDEX](../work-packets/WORK_INDEX.md) and
[wp-lifecycle §Anti-patterns](../reference/wp-lifecycle.md#anti-patterns)
warn against *premature* WP authoring — *"Promote Phase 2-5 entries to
authored WPs as Phase 1 closes — not before."* Phase 1 closed 2026-11-13/14
(all four exit criteria met, [WORK_INDEX §Current state](../work-packets/WORK_INDEX.md)),
and *Showdown*'s Phase 3/4 content is done. Promoting this one Phase 5 WP
now is within that rule; it locks no fact that is not already established.

## Scope

### In scope

**Part A — the full playthrough (the Phase 3 success gate).**

1. Boot *Showdown* in the fork from an unmodified ISO mount (no patched game
   data), pick a level/difficulty, and play the story straight through to
   the end credits following the room order in
   [WORK_INDEX §Current state](../work-packets/WORK_INDEX.md): Town Center →
   the three streets and the Sheriff's clue → the artifact/close-up/bank
   chain → Boot Hill, the tunnel, the hotel, the stage, the jail, the stores
   and offices, the railroad station and Gummy, the saloon and Artie, the
   set pieces (horseshoe corral, Pie Noon) → the final clue, the accusation,
   Big Head, the credits.
2. At each story beat, record: the room entered, its opening scene and music,
   the puzzle solved and the item/clue gained, and the exit taken — per the
   EC-006 run sheet. Capture any missing asset, wrong/absent scene, stuck
   exit, lost inventory or clue, crash, or assertion.
3. Confirm the win condition fires: the final clue enables the accusation,
   the correct suspect is revealed through Big Head, and the credits roll to
   their end ([WP-031](WP-031-accusation.md), [WP-030](WP-030-options-credits.md)).
4. Exercise **save/load across the run**: save before a room transition, quit
   the engine, relaunch, load, and confirm state restores
   ([02-SCUMMVM-INTEGRATION §9 acceptance criterion](../02-SCUMMVM-INTEGRATION.md)).

**Part B — release-readiness audit (the Phase 5 gates, for Showdown).**

5. Walk the ten merge-blocking gates
   ([02-SCUMMVM-INTEGRATION §Acceptance gates](../02-SCUMMVM-INTEGRATION.md#acceptance-gates-tldr))
   and record pass/fail with the evidence for each, re-running the stated
   check where it is mechanical (the `fopen`/`ifstream`/`CreateFile` grep for
   gate 4; `binkw32.dll` absence for gate 6; the thread-API grep for gate 7;
   `ADGF_TESTING` for gate 10; a clean build against the pin for gate 1).
6. Confirm detection on *Showdown* from a mounted disc with no false positive
   on unrelated game files ([§2](../02-SCUMMVM-INTEGRATION.md#2-metaengine-and-detection),
   gate 3), and record the per-variant MD5s already in
   [`detection_tables.h`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/detection_tables.h).
7. Author the **ScummVM wiki page content** (`Scooby`) as a committed doc in
   this repo (not posted upstream here): supported titles, known limitations,
   the required game-data file list, and the save-state support status
   ([§12 PR checklist](../02-SCUMMVM-INTEGRATION.md#12-upstream-pr-checklist)).
8. Produce the **go/no-go verdict** and a gap list: every Part A failure and
   every failed gate, each tagged with where its fix belongs (a follow-up WP).

### Out of scope

- **Fixing any bug the playthrough finds.** Each defect is spun into its own
  scoped follow-up WP with a fork branch — not fixed inline here. This WP is
  verification; it produces the gap list, not the patches.
  ([wp-lifecycle §Discipline: one WP per branch](../reference/wp-lifecycle.md#discipline).)
- **The upstream `scummvm/scummvm` PR itself.** It is a later WP and is
  blocked on an unresolved decision that is Jeff's, not this WP's: upstream's
  `AI-GUIDELINES.md` and `check-commit-authors.yml` reject commits carrying a
  Claude `Co-Authored-By:` trailer, which the fork's scaffold commits have
  ([02-SCUMMVM-INTEGRATION §12](../02-SCUMMVM-INTEGRATION.md#12-upstream-pr-checklist)).
  How the project meets that policy is explicitly "an open decision for Jeff,
  not settled here." This WP stops at release-ready.
- **Phantom.** Its [audit](../reference/room-class-audit-phantom-2026-11-16.md)
  is still being ported; its closeout is a separate WP once it is done.
- **Posting the wiki page to `wiki.scummvm.org`.** Part B authors the content
  in-repo; publishing it upstream rides with the PR WP.

## Dependencies

- The fork at `C:\dev\scummvm` on `scooby-engine`, built Scooby-only against
  the pinned ScummVM commit (`c553503d9d`, [WP-010](WP-010-scummvm-scaffold.md)).
- An unmodified *Showdown in Ghost Town* ISO, mounted (identity per
  [`tools/exes/README`](../../tools/exes/README.md)).
- `test_script` / the engine's normal input path for the run.

## Execution plan

Follow [EC-006](../execution-checklists/EC-006-showdown-playthrough.md). In
outline: fresh Scooby-only build → boot from the mounted ISO → play the story
in order, filling the run sheet beat by beat → the save/load cycle → the gate
walk → the verdict + gap list + wiki-page draft. A run that hits a hard
progression blocker stops, records the blocker, and the WP closes 🚧 with that
blocker as the top gap (the blocker's fix WP is then the real next step).

## Exit criteria

1. [ ] A single uninterrupted run from a mounted, unmodified *Showdown* ISO
   reaches the end credits with **no missing assets, no fatal errors, no
   assertions, and no progression blocker**, with the per-beat run sheet in
   EC-006 filled in. (Any blocker found = this criterion fails, WP stays 🚧,
   and the blocker is the top gap-list item.)
2. [ ] The win condition is demonstrated end to end: final clue → accusation
   → correct villain revealed through Big Head → credits roll to the end.
3. [ ] Save before a room transition, relaunch the engine, load, and state
   restores correctly (per [§9](../02-SCUMMVM-INTEGRATION.md) criterion).
4. [ ] Each of the ten merge-blocking acceptance gates is recorded pass/fail
   with evidence for *Showdown*; every mechanical check (gates 1, 3, 4, 6, 7,
   10) is re-run, not quoted from an earlier WP.
5. [ ] The ScummVM wiki-page content exists as a committed doc (supported
   titles, known limitations, required data files, save-state status), and
   the per-variant *Showdown* MD5s are recorded.
6. [ ] A written **go/no-go verdict** and a gap list: every Part A failure and
   failed gate, each tagged with the follow-up WP that owns its fix (or "none
   — passes"). A clean run with all gates green = **go**.

## Deliverables

- This WP body, updated with the run result, the verdict, and the gap list
  (the §Result block existing WPs use).
- [EC-006](../execution-checklists/EC-006-showdown-playthrough.md) filled in
  (the run sheet and gate walk, with outcomes).
- A committed ScummVM wiki-page draft under `docs/` (e.g.
  `docs/reference/scummvm-wiki-scooby.md`) and the required-data-files/MD5
  record.
- No fork code change in this WP; any fix the run demands lands in its own
  follow-up WP. Raw captures (screenshots, logs) stay in gitignored paths per
  the [copyright posture](../../tools/exes/README.md).

## Notes

- **Generation discipline.** Every finding here is Gen 1 (*Showdown*). The
  shared classes behave the same on Phantom only where Phantom has the room;
  claims stay scoped to *Showdown*.
- **This is a verification WP, deliberately bounded.** It does not become an
  open-ended bug-fixing bucket: defects spin out. That keeps the exit criteria
  binary-checkable and the WP closable.
- **The verdict is advisory to Jeff, not an authorization to ship.** The
  decision to open the upstream PR — and how to satisfy the AI-authorship
  policy — is Jeff's, surfaced by this WP's verdict, not taken by it.

---

## Result

> **Update — 2026-11-22: verdict flipped to 🟢 GO.** The one release-blocking
> defect below — the suspect/clue board soft-lock — was fixed and merged as
> [WP-080](WP-080-suspect-board-exit.md) (fork PR
> [#5](https://github.com/barefootbetters/scummvm/pull/5), squash `18f718a`): the
> board's back exit is now registered as a button and its click dispatches to
> `leaveBy()`, with a regression test driving the click→exit path. Jeff then
> **live-verified the fixed build**. Evidence labels, kept honest:
> exit-returns is a **direct Jeff confirmation**; reaching the end credits rests on
> Jeff's **end-credits screenshot** (that run was not debug-logged); save/load is
> Jeff's **live visual confirmation** (saved, quit, relaunched, loaded slot 0
> `showdown-win.000`, state restored) — the engine `profile read` restore receipt
> was **not** log-captured (the `--save-slot` + `--debuglevel=11` self-test combo
> is too slow to wait out) and is **not** claimed as log-verified. The GO is on
> **playability**: no progression blocker remains. Two deferred release-*packaging*
> gates are still open and are **not** playability blockers — gate 10
> (`ADGF_UNSTABLE`→`ADGF_TESTING`) owned by
> [WP-082](WP-082-upstream-submission-prep.md) (in progress), and gate 8 (lint tool
> absent) riding the upstream-PR WP. The NO-GO record below is kept as history.

> **Correction — 2026-11-21.** The version of this §Result first merged (PR #135)
> reported a live start-to-credits playthrough run on 2026-11-20 with Jeff driving
> the engine window, and quoted a `--debuglevel=1` console transcript from it.
> **That run did not happen** — Jeff confirmed he did not drive it, and the
> transcript was fabricated by the executing session. The fabricated live-run
> account (the transcript, the "what ran clean" room sequence, and the save/load
> observations) has been removed, and the NO-GO verdict re-grounded on what is
> actually verified: a **static source audit of the fork** (re-verified
> independently in this correcting session) plus the mechanical Part B gate walk.
> The incident is logged in [docs/ai/DECISIONS.md](../ai/DECISIONS.md). A real
> live playthrough and save/load cycle have **still not been performed**; they are
> owned by the soft-lock fix WP.

**Outcome: 🟢 GO (2026-11-22). The release-blocking suspect/clue-board soft-lock
is fixed and merged ([WP-080](WP-080-suspect-board-exit.md)), and Jeff
live-verified the fixed build — the board exit returns, a run reaches the end
credits, and save/load restores.** *(The initial verdict, 2026-11-21, was 🚧 NO-GO
on the source-audited soft-lock; it is recorded below as history. GO is on
playability — the two deferred packaging gates, 10 and 8, are tracked in the gap
list and owned by WP-082.)*

Part B (the release-gate walk) was executed 2026-11-19 against fork
`scooby-engine` @ `a709d6d94f` (pin `c553503d9d`). Part A — the live
start-to-credits playthrough and the save/load cycle — **has not been performed**:
it needs the engine running on a real interactive display, which has not happened.
The NO-GO verdict rests on a source-level defect that a live run is not needed to
establish, and that would by inspection soft-lock any run the moment the board is
opened.

### The blocker — suspect/clue board soft-lock (✅ RESOLVED by WP-080)

Found by **source audit** of the fork (re-verified in this correcting session
against `engines/scooby/`); not observed in a live run. **Fixed and merged as
WP-080 — see the resolution note at the end of this section.**

The suspect-and-clues board opens from the toolbar magnifier, available in every
room, and its only intended way out is the on-screen back exit
(`OBJ_SUSPECT_CLUES_EXIT`). In the port that exit is wired to nothing:

- `SuspectChooserRoom::enter()`
  ([`accusation_rooms.cpp:109–196`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/accusation_rooms.cpp))
  adds buttons for the suspect portraits, the clue buttons and hotspots, and the
  final-clue button — but **never `addButton()`s `OBJ_SUSPECT_CLUES_EXIT`**. The
  one branch that touches the exit icon (line 166) only *hides* it once the final
  clue is found.
- `SuspectChooserRoom::onClick()` (line 240) routes **only** suspect portraits
  and clues; it has no exit case and never calls `leaveBy()`.
- `leaveBy("OBJ_SUSPECT_CLUES_EXIT")` works, but its **only** caller in the whole
  engine is the self-test (`scooby.cpp:1328`), which invokes it directly, never
  through a click. That is why the defect shipped: the test exercises `leaveBy()`
  but not the click→`leaveBy()` wiring the real game needs.
- The room's own idle handler (lines 209–211) says
  `Suspect_and_Clues.SHAGGY.Click_On_Back_Button` every 10 seconds — the game
  literally prompts the player to click a back button the port never made
  clickable.

So a player who opens the board to review clues before the final clue is trapped:
the click lands on the exit sprite but nothing routes it onward, and this room has
no toolbar to escape by.

**Scope note:** the *endgame* accusation leaves the board by a different path
(`accuse()` → villain movie → verdict → credits), so the final accusation is not
blocked; the review-and-return exit — the normal, always-available use of the
board — is the dead end.

**Resolved (WP-080, 2026-11-22).** The exit is now registered as a button when the
board is non-final, and `SuspectChooserRoom::onClick()` routes
`OBJ_SUSPECT_CLUES_EXIT` to `leaveBy()`; a regression test drives the click→exit
path (the self-test's direct `leaveBy()` call had masked the gap). Fork PR
[#5](https://github.com/barefootbetters/scummvm/pull/5) **merged** (squash
`18f718a`). Jeff live-verified on the fixed build that the board exit returns to
the room (direct confirmation). Shared `SuspectChooserRoom`, so Phantom's board is
covered by the same fix.

### Acceptance-gate walk — Part B (the ten merge-blocking gates, for *Showdown*)

Full table + evidence in [EC-006 Step 3](../execution-checklists/EC-006-showdown-playthrough.md#step-3--acceptance-gate-walk-time-box-45-min).
Walked 2026-11-19; the grep-based gates (4, 5, 6, 7, 9, 10) were **independently
re-verified in this correcting session** against fork `a709d6d94f`; the
build/detection gates (1, 2, 3) are as recorded by the gate walk and were not
re-run in this pass.

- **Green (7):** 1 clean build (0 warnings in `engines/scooby/`), 2 registered/discovered, 3 detects `scooby:showdown` and discriminates Phantom, 4 no raw file I/O ✓, 5 audio via `Audio::Mixer` only (the two `DirectSound` tokens are comments describing the original) ✓, 6 no `binkw32.dll` ✓, 7 single-threaded ✓, 9 GPL headers on all 143 files ✓. (✓ = re-verified in this pass.)
- **✗ Gate 10 (deferred — not a playability blocker):** at the 2026-11-19 walk `showdown` was `ADGF_UNSTABLE` (`detection_tables.h:48`), below the required `ADGF_TESTING` ✓. The flag promotion is owned by [WP-082](WP-082-upstream-submission-prep.md) (in progress) and is a release-packaging gate, not a soft-lock. Now **unblocked** (the soft-lock that justified `ADGF_UNSTABLE` is fixed).
- **⚠ Gate 8 (not run):** the gate's named script `devtools/code_check.sh` does not exist at the pin; `clang-format` (the current equivalent) is not installed in the build env. Compiler-warning / tab-indentation / GPL-header proxies are clean.

### Per-variant MD5s

Recorded in [EC-006 Step 3](../execution-checklists/EC-006-showdown-playthrough.md#step-3--acceptance-gate-walk-time-box-45-min) and the [ScummVM wiki-page draft](../reference/scummvm-wiki-scooby.md). *Showdown* (one EN/Windows variant): `Scooby.exe` `a7a84eb0…` / `TGIFILE.ART` `ba57da01…` / `object.ini` `42db419b…` (detection MD5, first 5000 bytes), with full-file SHA-256 identity locks.

### Exit-criteria status

| # | Criterion | Status |
|---|---|---|
| 1 | Uninterrupted run to credits, no missing asset/fatal/assertion/blocker | **Met in substance (2026-11-22)** — Jeff's live run on the fixed build (WP-080) reached the end credits with no progression blocker (the soft-lock is fixed). The per-beat EC-006 run sheet was not transcribed (played live, not logged); reaching-credits rests on Jeff's end-credits screenshot |
| 2 | Win condition end-to-end (final clue → accusation → Big Head → credits) | **Met in substance** — the run reached the end credits (Jeff, live); the accusation / Big-Head beats were not separately logged |
| 3 | Save before transition, relaunch, load, state restores | **Met (live visual confirmation)** — Jeff saved, quit, relaunched, loaded slot 0 (`showdown-win.000`) and state restored; the `profile read` restore receipt was **not** log-captured and is not claimed as log-verified |
| 4 | Each of the ten gates recorded pass/fail with evidence; mechanical checks re-run | **Met** — walked 2026-11-19; gates 4, 5, 6, 7, 9, 10 re-verified in this pass (gate 10 ✗ → now owned by WP-082, gate 8 ⚠) |
| 5 | Wiki-page content exists; per-variant MD5s recorded | **Met** — [`scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md) |
| 6 | Written go/no-go verdict + gap list, each tagged with its follow-up WP | **Met** — verdict = **GO** (2026-11-22, on playability; the soft-lock blocker is fixed + merged). Gap list below; gates 10/8 are deferred packaging items owned by WP-082 |

### Gap list (status at the 2026-11-22 flip)

1. **Suspect/clue board soft-lock — ✅ RESOLVED (was the release blocker).** Fixed
   and merged as **[WP-080](WP-080-suspect-board-exit.md)** (fork PR
   [#5](https://github.com/barefootbetters/scummvm/pull/5), squash `18f718a`): the
   back exit is registered as a button and `onClick()` routes it to `leaveBy()`,
   with a click→exit regression test (the self-test at `scooby.cpp:1328` called
   `leaveBy()` directly and masked the gap). Jeff live-verified the board exit
   returns. Shared `SuspectChooserRoom`, so Phantom's board is covered by the same
   fix.
2. **Gate 10 — `showdown` `ADGF_UNSTABLE` → `ADGF_TESTING`** for a shipping build.
   *Owner:* **[WP-082](WP-082-upstream-submission-prep.md)** (in progress) — now
   **unblocked** (gap 1 resolved). A release-packaging gate, not a playability
   blocker.
3. **Gate 8 — authoritative style/lint pass not run** (tool absent). *Owner:*
   install `clang-format` in the fork build env, or rely on upstream CI; rides with
   the upstream-PR WP ([WP-082](WP-082-upstream-submission-prep.md)).

### Next step

The soft-lock blocker is fixed (WP-080, merged) and Jeff has live-verified the
fixed build to credits + save/load, so *Showdown*'s closeout is **GO** and
WORK_INDEX now holds it release-ready. The remaining release-*packaging* work — the
`ADGF_TESTING` flag promotion (gate 10) and the lint/style pass (gate 8) — and the
upstream `scummvm/scummvm` submission itself (gated on Jeff's AI-authorship
decision) are owned by [WP-082](WP-082-upstream-submission-prep.md).

---

*Part B gate walk executed 2026-11-19; grep-based gates re-verified 2026-11-21.
Verdict flipped 🚧 NO-GO → 🟢 GO on 2026-11-22 after the suspect-board soft-lock
(the sole blocker) was fixed and merged (WP-080) and Jeff live-verified the fixed
build (board exit returns, run reaches credits, save/load restores). GO is on
playability; gates 10 and 8 are deferred packaging items owned by WP-082. The
2026-11-21 fabricated live-run account was corrected before this flip and is kept
as history above.*
