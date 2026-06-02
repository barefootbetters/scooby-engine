---
layout: default
title: "WP-010: ScummVM Fork & Engine Scaffold"
---

# WP-010: ScummVM fork + empty `engines/scooby/` scaffold

**Status:** 📦 Queued
**Phase:** Pre-Work (before Phase 2; benefits Phase 1)
**Depends on:** —
**Companion EC:** [EC-005](../execution-checklists/EC-005-scummvm-scaffold)
**Estimated effort:** Half-day

---

## Goal

Fork `scummvm/scummvm` to `barefootbetters/scummvm`, create an
empty-but-compilable `engines/scooby/` skeleton, record the HEAD commit
hash in `docs/02-SCUMMVM-INTEGRATION.md`, and define the debug channel
names from §9. This pins the ScummVM API target before Phase 1 findings
are translated into implementation decisions, and defines the debugging
vocabulary **before** WP-001's Ghidra annotations are written.

## Background

`docs/02-SCUMMVM-INTEGRATION.md` currently reads **"ScummVM version pin:
TBD."** Every concrete API call and signature in that document is floating
against an unspecified target. Pinning the commit hash now means:

- API drift between "when docs were written" and "when code is written"
  surfaces immediately as a compile error — not a PR review comment six
  months from now.
- Debug channels (§9 of the integration doc) are defined as names before
  the WP-001 Ghidra session. When you label a function in Ghidra as
  "TGIFILE.ART loader → `resource` channel", that label uses the same
  channel name that will appear in the actual `debugC()` call. Naming
  channels after doing Ghidra instead of before guarantees a reconciliation
  pass.
- An empty-but-compiling scaffold proves the detection/engine compilation
  split (§10) works before there is real code to debug. The split is easy
  to get right on empty files; it is painful to retrofit.

This WP intentionally pulls forward a subset of Phase 2 scope. The Phase 2
WPs that implement actual engine behavior are unchanged — this only covers
the structural setup that makes Phase 2 implementable.

## Scope

In scope:
- Fork `scummvm/scummvm` → `barefootbetters/scummvm` on GitHub
- Clone fork locally to `C:\www\scummvm\`; create a `scooby-engine` branch
- Create `engines/scooby/` with the minimum files required for a clean build:
  - `scooby.h` + `scooby.cpp` — `ScoobyEngine : Engine`; empty `run()`
    returning `Common::kNoError`; debug channels registered in constructor
  - `detection.h` + `detection.cpp` — `MetaEngineDetection` stub;
    empty `ADGameDescription` table; compiled separately from engine
  - `metaengine.h` + `metaengine.cpp` — `MetaEngine` stub; `hasFeature()`
    returns `false` for all flags until Phase 2 implements them
  - `module.mk` — lists all `.o` targets; confirms detection/engine split
  - `configure.engine` — engine declaration, `default_state = disabled`
- Confirm clean build: `./configure --enable-engine=scooby && make`
- Confirm clean omission: `./configure --disable-engine=scooby && make`
- Record the forked HEAD commit hash in `docs/02-SCUMMVM-INTEGRATION.md`
- Define debug channel names in `scooby.cpp` via `DebugMan.addDebugChannel()`:
  `resource`, `graphics`, `audio`, `script`, `input`
- Push the branch to `barefootbetters/scummvm`

Out of scope:
- Any game logic, resource loading, or scene rendering (Phase 2/3)
- `ADGameDescription` table entries — require Phase 1 MD5 values not yet known
- `POTFILES` — premature until translatable strings exist
- macOS / Linux build verification (Phase 5 gate; Windows confirms scaffold correctness)

## Dependencies

- `scummvm/scummvm` GitHub fork (public repo; no special access)
- ScummVM Windows build prerequisites: mingw-w64 (or MSVC), SDL2, zlib
  (see `README.md` in the scummvm repo for the current Windows build guide)
- `docs/02-SCUMMVM-INTEGRATION.md` §10 for the exact `module.mk` and
  `configure.engine` patterns to follow

## Exit criteria

1. `barefootbetters/scummvm` exists on GitHub, forked from `scummvm/scummvm`.
2. Local clone at `C:\www\scummvm\` on a `scooby-engine` branch (not `master`
   — keeps the PR delta clean when the time comes).
3. `./configure --enable-engine=scooby && make` succeeds with zero errors.
4. `./configure --disable-engine=scooby && make` also succeeds cleanly.
5. HEAD commit hash of `scummvm/scummvm` at fork time recorded in
   `docs/02-SCUMMVM-INTEGRATION.md` header field "ScummVM version pin."
6. Debug channel names defined in `scooby.cpp` constructor via
   `DebugMan.addDebugChannel()` — even if they emit nothing yet.

## Deliverables

- `barefootbetters/scummvm` fork on GitHub, `scooby-engine` branch,
  `engines/scooby/` skeleton
- Updated [`docs/02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION) — commit hash + debug channel names

## Notes

- The `configure.engine` `default_state` must be **disabled** — standard for
  a new `ADGF_TESTING` engine. It is not promoted to enabled until the engine
  has shipped a stable upstream release.
- **Rebase discipline:** set up an `upstream` remote pointing at
  `scummvm/scummvm` and rebase the `scooby-engine` branch monthly. The longer
  the fork drifts, the harder the eventual upstream PR rebase becomes. Start
  the habit now while the diff is empty.
- The empty `ADGameDescription` table is correct at this stage. Populating it
  with real MD5 hashes and generation flags is Phase 2 work, after Phase 1
  produces canonical file fingerprints.
- Pick one build toolchain (mingw-w64 is the most common contributor path on
  Windows) and use it consistently through Phase 5. Switching toolchains
  mid-project creates subtle ABI and warning-set differences.
- WP-001 Ghidra session **can proceed in parallel** once this WP defines the
  debug channel names. The names are what WP-001 needs for Ghidra annotation
  alignment — a working engine is not required.
