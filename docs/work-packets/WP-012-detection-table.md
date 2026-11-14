---
layout: default
title: "WP-012: Detection Table with Generation Flag"
---

# WP-012: Detection table with a per-entry generation flag

**Status:** 🚧 In progress
**Phase:** 2 (ScummVM engine scaffold)
**Depends on:** WP-010 ✅ (scaffold and pin), WP-005 ✅ (which titles are in scope), WP-006 ✅ (Phantom is Gen 1)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-012-2026-11-14](../reference/pre-flight-WP-012-2026-11-14.md)

---

## Goal

Fill the empty `ADGameDescription` table in the fork's `engines/scooby/`
with one entry per in-scope title, each carrying the engine generation (1,
2 or 3). ScummVM should then recognise each disc from its files, and the
engine should know at startup which format family it is running.

## Background

WP-010 left `detection_tables.h` empty on purpose: entries need each
release's signature files, sizes and MD5s, and Phase 1 had to settle which
titles share the engine first. That is now settled:

- Showdown and Phantom are Gen 1 (WP-006).
- Jinx is Gen 2 and Case File #1 is Gen 3 (WP-005, WP-007).
- Case File #2 runs a different engine and is excluded (WP-005).
- Case File #3 is a Director title and is out of scope (vision doc).

Integration §3 calls the generation flag the load-bearing piece. Phase 3
archive readers dispatch on it, so the table should not need restructuring
when they arrive.

## Scope

**In scope (fork `C:\dev\scummvm`, branch `scooby-engine`, `engines/scooby/` only):**

- A `ScoobyGameDescription` struct that wraps `ADGameDescription` and adds a
  `generation` field, and the detection and meta-engine classes switched to
  it.
- Four entries: Showdown, Phantom, Jinx and Case File #1. Each matches three
  signature files on MD5 (first 5,000 bytes, the detector default) and size.
- Gen 1 entries flagged `ADGF_UNSTABLE`. Gen 2 and Gen 3 entries flagged
  `ADGF_UNSUPPORTED` until their archive readers exist.
- Detection from the disc root, through `_maxScanDepth` and
  `_directoryGlobs`.
- `ScoobyEngine::getGeneration()`, plus a `resource`-channel debug line at
  startup that shows the value reached the engine.

**In scope (this repo):** integration §2 and §3, this WP, a pre-flight, and
WORK_INDEX.

**Out of scope:**

- Installed (hard-disk) layouts.
- Other languages or regional releases; none are on hand.
- Any file reading beyond detection (Phase 3).

## Exit criteria

1. [ ] Each in-scope disc, mounted from its ISO, is detected by
   `scummvm --detect` from the disc root, with the right title.
2. [ ] Each entry carries the right generation: Showdown 1, Phantom 1,
   Jinx 2, Case File #1 3. The value reaches the engine (debug line).
3. [ ] Case File #2, Case File #3 and an unrelated directory produce no
   match.
4. [ ] Scooby-only build: no errors, no warnings in `engines/scooby/`.
   Build with scooby disabled still compiles `detection.o`.
5. [ ] Fork diff touches only `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`: the generation struct and the four entries.
- [Integration §2 and §3](../02-SCUMMVM-INTEGRATION.md#3-game-detection-table-adgamedescription)
  implementation notes, with the signature files per title.

## Notes

- Detection IDs avoid names other engines already use. At the pin `phantom`
  is MADS's *Return of the Phantom* and `jinx` is a Glk/Adrift game, and a
  bare ID on the command line is ambiguous when two engines share it.
