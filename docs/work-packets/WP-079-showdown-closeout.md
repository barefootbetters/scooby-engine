---
layout: default
title: "WP-079: Showdown closeout"
---

# WP-079: Showdown closeout — full playthrough and release readiness (Gen 1)

**Status:** 🚧 In Progress (2026-11-19) — Part B (release-gate walk) complete; Part A (live playthrough) + save/load **pending a live interactive-desktop run**. See [§Result](#result-2026-11-19).
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

## Result (2026-11-19)

**Outcome: Part B done, Part A not run. Go/no-go verdict WITHHELD.**

Executed against fork `scooby-engine` @ `a709d6d94f` (pin `c553503d9d`
reachable) with the genuine *Showdown* disc mounted at `H:\scooby\`
(`Scooby.exe` SHA-256 `1328454334…7478`, matching the identity lock;
`showdown.cd` present). The release-gate walk (Part B) was completed with
fresh evidence — not quoted from earlier WPs. The continuous playthrough
(Part A) and the save/load cycle did **not** run: the engine requires a real
interactive desktop, which the build/CLI context does not provide (the SDL
backend hangs or fails to allocate a surface headlessly — see EC-006 Step 0).
A continuous start-to-credits run also cannot be scripted blind through the
`test_script` harness, and fabricating beat results is out of bounds. So the
one deliverable the WP exists to produce — evidence the game plays through to
credits — is the open item, and the verdict is **withheld**, not **go** (not
demonstrated) and not a 🚧 **no-go blocker** (no hard dead-end was found).

### Acceptance-gate walk (the ten merge-blocking gates, for *Showdown*)

Full table + evidence in [EC-006 Step 3](../execution-checklists/EC-006-showdown-playthrough.md#step-3--acceptance-gate-walk-time-box-45-min). Summary:

- **Green (7):** 1 clean build (0 warnings in `engines/scooby/`), 2 registered/discovered, 3 detects `scooby:showdown` and discriminates Phantom with no false positive, 4 no raw file I/O, 5 audio via `Audio::Mixer` only, 6 no `binkw32.dll`, 7 single-threaded, 9 GPL headers on all 143 files.
- **✗ Gate 10 (gap):** `showdown` is `ADGF_UNSTABLE`, below the required `ADGF_TESTING`. A shipping/initial-merge build must flip the flag.
- **⚠ Gate 8 (not definitively run):** the gate's named script `devtools/code_check.sh` does not exist at the pin; `clang-format` (the current equivalent) is not installed in the build env. Compiler-warning / tab-indentation / GPL-header proxies are clean.

### Per-variant MD5s

Recorded in [EC-006 Step 3](../execution-checklists/EC-006-showdown-playthrough.md#step-3--acceptance-gate-walk-time-box-45-min) and the [ScummVM wiki-page draft](../reference/scummvm-wiki-scooby.md). *Showdown* (one EN/Windows variant): `Scooby.exe` `a7a84eb0…` / `TGIFILE.ART` `ba57da01…` / `object.ini` `42db419b…` (detection MD5, first 5000 bytes), with full-file SHA-256 identity locks.

### Exit-criteria status

| # | Criterion | Status |
|---|---|---|
| 1 | Uninterrupted run to credits, no missing asset/fatal/assertion/blocker | **Unmet — not run** (needs interactive desktop) |
| 2 | Win condition end-to-end (final clue → accusation → Big Head → credits) | **Unmet — not run** |
| 3 | Save before transition, relaunch, load, state restores | **Unmet — not run** (scriptable via `test_script` `save`/`load` once a display exists) |
| 4 | Each of the ten gates recorded pass/fail with evidence; mechanical checks re-run | **Met** — all ten walked with fresh evidence (gate 10 ✗, gate 8 ⚠) |
| 5 | Wiki-page content exists; per-variant MD5s recorded | **Met** — [`scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md) |
| 6 | Written go/no-go verdict + gap list, each tagged with its follow-up WP | **Met** — verdict = **withheld**; gap list below |

### Gap list (each tagged with the follow-up that owns its fix)

1. **Live playthrough + save/load not run** (exit criteria 1–3). *Owner:* the live-run session (this WP, resumed on an interactive desktop — see hand-off). Not a code defect; no follow-up WP until the run surfaces one.
2. **Gate 10 — `showdown` is `ADGF_UNSTABLE`, needs `ADGF_TESTING`** for a shipping build. *Owner:* its own one-line `detection_tables.h` follow-up WP, gated on the live-run verdict confirming the game is playable.
3. **Gate 8 — authoritative style/lint pass not run** (tool absent). *Owner:* install `clang-format` in the fork build env, or rely on upstream CI; rides with the upstream-PR WP.

### Live-run hand-off (what's left, and the options)

The only thing standing between here and a **go** verdict is the single
continuous playthrough (plus the mid-run save/load) — on a real desktop.
The build, detection and all mechanical gates are done; a fresh
`scummvm.exe` is linked at `C:\dev\scummvm\scummvm.exe`. Options:

- **Jeff drives it** (knows the game; the 1–2-day estimate is for a human run), reporting per-beat observations to fill [EC-006 Step 1](../execution-checklists/EC-006-showdown-playthrough.md) and the save/load result; this session writes the verdict.
- **This session drives it via desktop control** (computer-use) — tractable for boot + the save/load cycle; the full 23-beat puzzle playthrough is slow and would likely need Jeff's help at the hard puzzles. Higher cost, uncertain.

WORK_INDEX stays as-is (📝/🚧); the row flips to ✅ only on a clean go after
the run.

---

*Drafted 2026-11-19. Part B executed 2026-11-19; Part A (live playthrough)
pending an interactive-desktop session.*
