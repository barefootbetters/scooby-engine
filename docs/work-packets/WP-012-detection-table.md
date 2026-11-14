---
layout: default
title: "WP-012: Detection Table with Generation Flag"
---

# WP-012: Detection table with a per-entry generation flag

**Status:** ✅ Done (2026-11-14)
**Phase:** 2 (ScummVM engine scaffold)
**Depends on:** WP-010 ✅ (scaffold and pin), WP-005 ✅ (which titles are in scope), WP-006 ✅ (Phantom is Gen 1)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-012-2026-11-14](../reference/pre-flight-WP-012-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Each disc detected from its root | ✅ Each ISO was mounted with `Mount-DiskImage`, and `scummvm --detect --path=<root>` named the right title: `scooby:showdown`, `scooby:phantomknight`, `scooby:jinxsphinx`, `scooby:casefile1`. Showdown and Phantom are also detected from `\scooby\`. Jinx from `\Jinx\` and Case File #1 from `\MUSEUM\` are not, because a signature file sits elsewhere on the disc. |
| 2. Right generation, and the engine sees it | ✅ Showdown and Phantom start and log `Starting <id> (generation 1)` on the `resource` channel, after the detector lists the three matched files with their MD5s. Jinx (2) and Case File #1 (3) stop at the unsupported-game dialog, before the engine is created. |
| 3. No false positives | ✅ No match on Case File #2, Case File #3, *Activity Challenge*, the `tools/exes/casefile2/` cache, or `C:\Windows\System32\drivers`. |
| 4. Builds | ✅ Scooby-only build: 0 errors, 0 warnings. Build with scooby disabled: only `engines/scooby/detection.o` recompiles, it links, and scooby is not listed. |
| 5. Fork diff | ✅ `git diff --name-only upstream/master...scooby-engine` lists only `engines/scooby/` files. The commit is [`5a88016fea`](https://github.com/barefootbetters/scummvm/commit/5a88016fea), pushed to `scooby-engine`. |

**Deviations:**

- **Four entries, not five.** Integration §3 asked for Case File #2 as Gen 3. WP-005 excluded it, so §3 is revised.
- **Signature files differ from §3's draft.** The draft named `Mummy*.MMF`, `HD.*`, `libexpat.dll` and loose `*.xml`. The entries use the files on the discs; see [§3](../02-SCUMMVM-INTEGRATION.md#3-game-detection-table-adgamedescription).
- **Game ids** `phantomknight` and `jinxsphinx`, not `phantom` and `jinx`, which other engines use.
- **"Add Game" dialog not clicked through.** `--detect` runs the same detector code. Starting a game was tested from the command line.

**Found in passing:** `ScoobyDoo.iso` (*Scooby-Doo! Activity Challenge*, 2001) ships MMFW archives (`BONUS.MMF`, `.MMA`, `.MMP`, `Bonus.mms`, all starting `MMFW`) and `INSTALL\HDINSTALL\Scooby.exe` (794,624 bytes), alongside the IBS logo video. That is Jinx's layout. The [vision doc](../01-VISION.md) assumes it uses a different engine. It looks like the same lineage, which would make it a fifth candidate. Not classified here. [WP-013](WP-013-activity-challenge-engine-check.md) has since classified it: Gen 2, Jinx's engine. Its detection entry is not part of this WP; it was added afterwards in fork commit [`644305dddc`](https://github.com/barefootbetters/scummvm/commit/644305dddc) (see [WP-013 §Detection](WP-013-activity-challenge-engine-check.md#detection)).

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

1. [x] Each in-scope disc, mounted from its ISO, is detected by
   `scummvm --detect` from the disc root, with the right title.
2. [x] Each entry carries the right generation: Showdown 1, Phantom 1,
   Jinx 2, Case File #1 3. The value reaches the engine (debug line).
3. [x] Case File #2, Case File #3 and an unrelated directory produce no
   match.
4. [x] Scooby-only build: no errors, no warnings in `engines/scooby/`.
   Build with scooby disabled still compiles `detection.o`.
5. [x] Fork diff touches only `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`: the generation struct and the four entries.
- [Integration §2 and §3](../02-SCUMMVM-INTEGRATION.md#3-game-detection-table-adgamedescription)
  implementation notes, with the signature files per title.

## Notes

- Detection IDs avoid names other engines already use. At the pin `phantom`
  is MADS's *Return of the Phantom* and `jinx` is a Glk/Adrift game, and a
  bare ID on the command line is ambiguous when two engines share it.
