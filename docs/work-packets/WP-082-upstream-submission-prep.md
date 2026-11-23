---
layout: default
title: "WP-082: Upstream submission prep"
---

# WP-082: Prepare the `scooby` engine for upstream ScummVM submission (Gen 1)

**Status:** 🚧 In progress — technical prep done on branch `wp-082-upstream-prep`;
acceptance gated on Jeff's AI-authorship decision (see
[decision brief](../reference/upstream-submission-decision-brief.md)) and on the
fixed-build release playthrough (owned with WP-079/WP-080). See [§Result](#result).
**Claim:** branch `wp-082-upstream-prep` on the fork (the claim per
[wp-lifecycle §5](../reference/wp-lifecycle.md#5-branch--a-fork-worktree-conditional--substantive-code-wps-only)).
WP-081 was already held by a parallel "wizards-bedroom-veranda" session, and
WP-080 by the soft-lock fix; this WP took the next free number, 082.
**Phase:** 5 (polish & contribution).
**Depends on:** WP-079 ✅-partial (Showdown closeout / gate walk), WP-080 ✅ (the
suspect-board soft-lock fix, fork PR [#5](https://github.com/barefootbetters/scummvm/pull/5)
merged 2026-11-21 — `origin/scooby-engine` @ `18f718a1a9`).
**Unblocks:** the upstream `scummvm/scummvm` PR itself — **only** if Jeff elects a
submission path in the [decision brief](../reference/upstream-submission-decision-brief.md).
**Pre-flight:** this WP modifies `engines/scooby/**` (the `ADGF_TESTING` flag) and
claims a release-readiness posture; per [wp-lifecycle §Phase 1 DoD](../reference/wp-lifecycle.md#work_index-row--phase-1-definition-of-done)
that warrants pre-flight. Executed as governed prep off the fixed fork head; the
scope lock is `engines/scooby/detection_tables.h` (flag only) plus this repo's
`docs/**`. No behaviour change beyond the flag.
**Targets generation(s):** Gen 1 (*Showdown*) only. Phantom stays `ADGF_UNSTABLE`.
**Estimated effort:** ~half a day.

---

## Goal

Make the `scooby` engine **mechanically submission-ready** for `scummvm/scummvm`
and hand Jeff the **one decision** that gates an actual PR. Concretely: flip
*Showdown* to `ADGF_TESTING` now that the WP-080 soft-lock fix has landed; re-run
the ten acceptance gates with fresh evidence against both the pinned ScummVM and
current `master`; run a real code-style pass; finalize the ScummVM wiki page; and
produce an honest decision brief on upstream's AI-authorship policy and the
realistic odds of acceptance. **This WP does not open the upstream PR, post the
wiki, or rewrite the fork's history** — those wait on the decision.

## Background

*Showdown*'s content is complete (every room ported, WP-014…WP-056), its closeout
([WP-079](WP-079-showdown-closeout.md)) walked the release gates, and the one
release-blocking defect it found — the suspect/clue-board soft-lock — was fixed in
[WP-080](https://github.com/barefootbetters/scummvm/pull/5) (merged 2026-11-21).
The pieces for a submission are therefore in place, but two things stood between
"done" and "submittable":

1. **Mechanical readiness wasn't re-confirmed as a set** against a current tree:
   the `ADGF_UNSTABLE`→`ADGF_TESTING` flip (gate 10) was blocked on the soft-lock
   (now cleared); the code-style gate (8) had never run (tool absent); and the pin
   is 797 commits behind `master`, so "builds against upstream" needed re-checking.
2. **The authorship policy is unresolved and is Jeff's call.** Upstream's
   [`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md)
   bars AI (co-)authorship of code, requires a human sole author and maintainer,
   and `check-commit-authors.yml` auto-closes PRs with `Co-Authored-By: Claude`
   trailers — which every fork commit carries. This is not a formatting problem;
   it's an authorship/maintainership one. [02-SCUMMVM-INTEGRATION §12](../02-SCUMMVM-INTEGRATION.md#12-upstream-pr-checklist)
   records it as "an open decision for Jeff, not settled here."

## Scope

### In scope

1. Flip *Showdown* `ADGF_UNSTABLE`→`ADGF_TESTING` in `detection_tables.h` (gate 10);
   leave Phantom `ADGF_UNSTABLE` and Gen 2/3 `ADGF_UNSUPPORTED`.
2. Re-run the ten acceptance gates with fresh evidence on the fixed fork head;
   re-run every mechanical check (don't quote earlier WPs).
3. Run a real code-style pass: identify ScummVM's current lint (`clang-format` +
   root `.clang-format`), install it, and assess `engines/scooby/` drift honestly.
4. Confirm the engine builds against **current** upstream `master` (not just the
   pin), resolving any API drift — recorded as the reusable, decision-independent
   part of "rebase onto master."
5. Confirm the §12 PR checklist mechanically (detection/engine split, no data
   blobs / `binkw32.dll`, MD5s, commit convention).
6. Finalize the [ScummVM wiki-page content](../reference/scummvm-wiki-scooby.md)
   for posting — **not** posted upstream here.
7. Produce the [AI-authorship decision brief](../reference/upstream-submission-decision-brief.md)
   with an honest acceptance-likelihood read, and hand the decision back to Jeff.

### Out of scope

- **Opening the upstream `scummvm/scummvm` PR, posting the wiki, or engaging the
  ScummVM Discord/forum.** All wait on the §7 decision.
- **Rewriting the fork's commit history (the authorship squash).** Not done until
  Jeff picks a path; the squash *is* the master-rebase and is done once, as part
  of the chosen submission path (see the [decision brief §5](../reference/upstream-submission-decision-brief.md)).
- **The *Showdown* release GO verdict / live playthrough.** That belongs to
  WP-079 and the fixed-build run; this WP records its status, it does not own it.
- **Phantom.** Stays `ADGF_UNSTABLE`; its closeout is a separate WP.
- **Engine behaviour changes** beyond the flag flip.

## Dependencies

- Fork worktree `wp-082-upstream-prep` off `origin/scooby-engine` @ `18f718a1a9`
  (has the WP-080 fix), built Scooby-only with MSYS2 UCRT64 (g++ 16.2.0, SDL2
  2.32.10, GNU Make 4.4.1) — the recorded Phase 2–5 toolchain.
- `clang-format` (installed this WP: 23.1.5, `mingw-w64-ucrt-x86_64-clang`).
- Upstream `master` @ `2982fe324b` for the drift build.

## Exit criteria

1. [ ] *Showdown* is `ADGF_TESTING` (phantom `ADGF_UNSTABLE`), on the branch.
2. [ ] Each of the ten gates recorded pass/fail with fresh evidence; mechanical
   checks re-run on the fixed head.
3. [ ] Code-style pass run (tool installed), drift assessed honestly against
   upstream's own engines as a baseline.
4. [ ] Engine builds against current `master` (API drift resolved or listed).
5. [ ] §12 checklist mechanically confirmed.
6. [ ] Wiki-page content finalized (not posted).
7. [ ] AI-authorship decision brief delivered; the one decision is stated and
   handed to Jeff.

## Deliverables

- The `ADGF_TESTING` flip on `wp-082-upstream-prep` (not merged to `scooby-engine`
  without Jeff's say).
- This WP body with the §Result gate walk.
- The [decision brief](../reference/upstream-submission-decision-brief.md).
- The finalized [wiki page](../reference/scummvm-wiki-scooby.md).
- No upstream PR, no wiki post, no history rewrite.

---

## Result

**Outcome: 🚧 mechanically submission-ready; the PR is gated on Jeff's
authorship decision, and the *Showdown* GO is gated on the fixed-build
playthrough (WP-079/WP-080).**

Executed on branch `wp-082-upstream-prep`, forked from `origin/scooby-engine @
18f718a1a9` (includes the WP-080 soft-lock fix — verified: the board's back exit
now dispatches to `leaveBy()` at `accusation_rooms.cpp:254`).

### Acceptance-gate walk (ten gates, *Showdown*, fresh evidence)

| # | Gate | Status | Evidence (this WP) |
|---|---|---|---|
| 1 | Compiles clean vs pinned ScummVM | ✅ | Scooby-only build (UCRT64) exit 0; **0 warnings in `engines/scooby/`** (the build's 2 warnings are upstream `gob/dataio.cpp` and `audio/mac/halestorm.cpp`) |
| 2 | Registered via `MetaEngineDetection`, discovered | ✅ | Detection/engine split holds: `module.mk` puts `detection.o` in `DETECT_OBJS`, engine objs in `MODULE_OBJS`; configure builds detection-only |
| 3 | Detects *Showdown*, no false positives | ✅ | ScummVM run log (2026-11-21 13:20) loads `showdown` with the three detection MD5s matching `detection_tables.h`; Phantom discriminated at `G:\scooby`, Showdown at `H:\scooby` |
| 4 | File I/O via `Common::File`/`Common::Archive` only | ✅ | grep for `fopen`/`CreateFile*`/`std::ifstream` across 149 engine files: no matches outside comments |
| 5 | Audio via `Audio::Mixer` only | ✅ | No `DirectSound`/`waveOut`/`XAudio` except two comment tokens (`sound.cpp:109`, `sound_archive.cpp:179`) describing the original |
| 6 | Bink via `Video::BinkDecoder`; no `binkw32.dll` | ✅ | No `binkw32`/`LoadLibrary` anywhere in the engine |
| 7 | Single-threaded | ✅ | No `pthread`/`std::thread`/`CreateThread`/`std::async` |
| 8 | Code style (ScummVM lint) | ⚠️→ℹ️ | Tool installed (`clang-format` 23.1.5). Wholesale `clang-format --dry-run` drift is **not** ScummVM's gate: upstream's own engines drift at similar rates (director 51/53, sci 16/19, bolt 8/15 vs scooby 138/149). A blind reformat would hurt. Compiler-clean + tabs + GPL headers are the load-bearing proxies and pass. Targeted style review rides with whichever submission path §7 picks |
| 9 | GPL-3.0 header on every file | ✅ | All 149 `.cpp`/`.h` carry the header |
| 10 | `ADGF_TESTING` (or higher) | ✅ | Flipped `showdown` → `ADGF_TESTING` (`detection_tables.h:48`), now unblocked by the WP-080 fix; phantom stays `ADGF_UNSTABLE` |

### Build against current upstream master (the reusable half of "rebase onto master")

The pin (`c553503d9d`, 2026-11-13) is **797 commits** behind `master`
(`2982fe324b`, 2026-11-21). Rather than replay the co-authored history (throwaway
— see [decision brief §5](../reference/upstream-submission-decision-brief.md)), the
engine tree was overlaid onto a `master` checkout (`2982fe324b`) and built
Scooby-only: **configure + make both exit 0, `scummvm.exe` produced with `scooby`
linked (`--list-engines` lists it), and 0 warnings in `engines/scooby/`** (the 2
build warnings are the same upstream `gob`/`audio` ones). **No API drift affects
the engine across the 797 commits** — gate 1 holds on current master, so the
eventual rebase/squash onto master compiles without drift resolution. This is the
reusable result regardless of which submission path §7 picks.

### §12 PR checklist (mechanical)

- ✅ `ADGF_TESTING` for initial merge (gate 10).
- ✅ Detection split builds detection-only (`DETECT_OBJS`).
- ✅ No copyrighted data / asset blobs / `binkw32.dll` in the engine tree (only
  `.cpp/.h/.mk/.engine` + `credits.pl`; no game data).
- ✅ Per-variant MD5s recorded ([wiki page](../reference/scummvm-wiki-scooby.md),
  `detection_tables.h`).
- ✅ Commit convention `SCOOBY: <subsystem>: <description>` (fork PRs #1–#5).
- ⛔ **Blocker (policy, not mechanics):** every fork commit carries
  `Co-Authored-By: Claude`; `check-commit-authors.yml` auto-closes such PRs, and
  `AI-GUIDELINES.md` bars AI (co-)authorship. **This is the decision.**

### The one decision for Jeff

See the **[AI-authorship decision brief](../reference/upstream-submission-decision-brief.md)**.
In short: passing the trailer-check bot is trivial (squash to clean commits);
clearing the *policy* is not, because upstream explicitly does not want engines
"fully reversed by a swarm of agents" and requires a genuine human
author-maintainer. Options: (A) stay a fork [lowest-friction, most honest],
(B) ask the ScummVM team openly first, (C) honest disclosed submission only if
Jeff can stand as the real maintainer, (D) human re-authorship. Handed back to
Jeff; no PR opened.

### Status of the *Showdown* GO (not owned here)

The *Showdown* release GO is WP-079's. Jeff ran a real playthrough on 2026-11-21
(logged launch 13:20 + today's saves) on a **pre-WP-080** build, so it validates
main progression but not the fixed board-exit path. A fixed-build playthrough
(this WP's `wp-082` binary, which has WP-080) exercising the board open/return and
a save→quit→reload is the outstanding step before WORK_INDEX flips *Showdown* to ✅.

---

*Prepared under WP-082. No upstream PR opened, no ScummVM wiki posted, no fork
history rewritten.*
