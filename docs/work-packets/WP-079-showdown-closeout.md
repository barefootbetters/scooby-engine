---
layout: default
title: "WP-079: Showdown closeout"
---

# WP-079: Showdown closeout — full playthrough and release readiness (Gen 1)

**Status:** 🚧 NO-GO — not release-ready (verdict 2026-11-21, on **static source audit**). A release-blocking defect was found by source audit of the fork: the suspect/clue board's back exit is never wired to a click handler, so opening the board traps the player. The live start-to-credits playthrough and the save/load cycle have **not** been run (deferred to the fix WP). Part B (release-gate walk) complete. See [§Result](#result). **Correction 2026-11-21:** the first-merged §Result claimed a live playthrough Jeff drove on 2026-11-20, with a console transcript; that run did not happen and the fabricated evidence has been removed — see §Result and [docs/ai/DECISIONS.md](../ai/DECISIONS.md).
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

**Outcome: 🚧 NO-GO (source audit). A release-blocking progression defect was
found in the suspect/clue board. The live playthrough has not been run.**

Part B (the release-gate walk) was executed 2026-11-19 against fork
`scooby-engine` @ `a709d6d94f` (pin `c553503d9d`). Part A — the live
start-to-credits playthrough and the save/load cycle — **has not been performed**:
it needs the engine running on a real interactive display, which has not happened.
The NO-GO verdict rests on a source-level defect that a live run is not needed to
establish, and that would by inspection soft-lock any run the moment the board is
opened.

### The blocker — suspect/clue board soft-lock (release-blocking)

Found by **source audit** of the fork (re-verified in this correcting session
against `engines/scooby/`); not observed in a live run.

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

*(A live run would confirm the symptom — a click on the exit with no room change.
The source alone establishes the exit is unreachable by click; that live
confirmation is deferred to the fix WP's re-run.)*

### Acceptance-gate walk — Part B (the ten merge-blocking gates, for *Showdown*)

Full table + evidence in [EC-006 Step 3](../execution-checklists/EC-006-showdown-playthrough.md#step-3--acceptance-gate-walk-time-box-45-min).
Walked 2026-11-19; the grep-based gates (4, 5, 6, 7, 9, 10) were **independently
re-verified in this correcting session** against fork `a709d6d94f`; the
build/detection gates (1, 2, 3) are as recorded by the gate walk and were not
re-run in this pass.

- **Green (7):** 1 clean build (0 warnings in `engines/scooby/`), 2 registered/discovered, 3 detects `scooby:showdown` and discriminates Phantom, 4 no raw file I/O ✓, 5 audio via `Audio::Mixer` only (the two `DirectSound` tokens are comments describing the original) ✓, 6 no `binkw32.dll` ✓, 7 single-threaded ✓, 9 GPL headers on all 143 files ✓. (✓ = re-verified in this pass.)
- **✗ Gate 10 (gap):** `showdown` is `ADGF_UNSTABLE` (`detection_tables.h:48`), below the required `ADGF_TESTING` ✓. A shipping/initial-merge build must flip the flag.
- **⚠ Gate 8 (not run):** the gate's named script `devtools/code_check.sh` does not exist at the pin; `clang-format` (the current equivalent) is not installed in the build env. Compiler-warning / tab-indentation / GPL-header proxies are clean.

### Per-variant MD5s

Recorded in [EC-006 Step 3](../execution-checklists/EC-006-showdown-playthrough.md#step-3--acceptance-gate-walk-time-box-45-min) and the [ScummVM wiki-page draft](../reference/scummvm-wiki-scooby.md). *Showdown* (one EN/Windows variant): `Scooby.exe` `a7a84eb0…` / `TGIFILE.ART` `ba57da01…` / `object.ini` `42db419b…` (detection MD5, first 5000 bytes), with full-file SHA-256 identity locks.

### Exit-criteria status

| # | Criterion | Status |
|---|---|---|
| 1 | Uninterrupted run to credits, no missing asset/fatal/assertion/blocker | **Not run** — the live playthrough was not performed. A release-blocking soft-lock found by source audit makes a GO impossible until it is fixed; the run is owned by the fix WP |
| 2 | Win condition end-to-end (final clue → accusation → Big Head → credits) | **Not run** |
| 3 | Save before transition, relaunch, load, state restores | **Not run** — the save/load cycle was not exercised |
| 4 | Each of the ten gates recorded pass/fail with evidence; mechanical checks re-run | **Met** — walked 2026-11-19; gates 4, 5, 6, 7, 9, 10 re-verified in this pass (gate 10 ✗, gate 8 ⚠) |
| 5 | Wiki-page content exists; per-variant MD5s recorded | **Met** — [`scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md) |
| 6 | Written go/no-go verdict + gap list, each tagged with its follow-up WP | **Met** — verdict = **NO-GO** (on the source-audited soft-lock); gap list below |

### Gap list (each tagged with the follow-up that owns its fix)

1. **Suspect/clue board soft-lock — the blocker (release-blocking).** The board's
   back exit (`OBJ_SUSPECT_CLUES_EXIT`) is never `addButton()`-ed and `onClick()`
   has no exit case, so a click on it is never dispatched to `leaveBy()`; the room
   has no toolbar and no Esc/right-click escape. Opening the board (available from
   every room's magnifier) traps the player. *Owner:* **WP-080** — route the exit
   object to `leaveBy()` in `SuspectChooserRoom` (register it as a room exit, or
   add it as a button whose click calls `leaveBy("OBJ_SUSPECT_CLUES_EXIT")`), and
   add a regression test that drives the **click→exit** path, not just `leaveBy()`
   directly (the self-test at `scooby.cpp:1328` calls `leaveBy()` directly and
   masked this). Phantom shares this room class — verify the same fix and check
   Phantom's board before its own closeout. *(Fix in progress: fork PR
   [barefootbetters/scummvm#5](https://github.com/barefootbetters/scummvm/pull/5),
   open, pending review — not merged.)*
2. **Gate 10 — `showdown` is `ADGF_UNSTABLE`, needs `ADGF_TESTING`** for a
   shipping build. *Owner:* its own one-line `detection_tables.h` follow-up WP —
   **blocked on gap 1**: the flag cannot be promoted while the game is
   soft-lockable.
3. **Gate 8 — authoritative style/lint pass not run** (tool absent). *Owner:*
   install `clang-format` in the fork build env, or rely on upstream CI; rides
   with the upstream-PR WP.

### Next step

Gap 1 (the soft-lock) is the real next piece of work; its fix is in flight as
WP-080 / fork PR #5 (held for honest review, not auto-merged). Once it lands, the
live start-to-credits playthrough and the save/load cycle — **which have never
been run** — must actually be performed to reach a GO. Until then WORK_INDEX holds
*Showdown* at 🚧 / not-release-ready; the row flips to ✅ only on a clean live run
with all gates green.

---

*Part B gate walk executed 2026-11-19; grep-based gates re-verified 2026-11-21.
Part A (live playthrough + save/load) not yet performed. Verdict NO-GO on a
source-audited suspect-board soft-lock. §Result corrected 2026-11-21 after the
originally merged live-run account was found to be fabricated.*
