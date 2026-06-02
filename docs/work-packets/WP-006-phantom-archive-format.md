---
layout: default
title: "WP-006: Phantom Archive Format"
---

# WP-006: Phantom archive format verification (Gen 1 vs Gen 2)

**Status:** 📦 Queued
**Phase:** 1 — Format Research (follow-on to the Engine Lineage finding in WP-005)
**Depends on:** —
**Companion EC:** — (single hex dump; no checklist needed)
**Estimated effort:** 1 minute

---

## Goal

Determine whether *Scooby-Doo! Phantom of the Knight*'s archive format is
**Gen 1** (`TGIFILE.ART`, same as Showdown) or **Gen 2** (`MMFW` wrapper,
same as Jinx). The Rich Header data classifies Phantom as Gen 1 by
toolchain (identical to Showdown's Linker 5.10 build 8047), but the
archive format is the other half of the generation classification and
hasn't been inspected on the Phantom disc yet.

## Background

The Phase 1 Engine Lineage finding identified three format generations:
Gen 1 (Showdown / Phantom predicted), Gen 2 (Jinx), Gen 3 (Case File #1
+ Case File #2 predicted). Toolchain build numbers and archive format
*coincide* across generation boundaries — same Linker 5.10 build 8047
appears with `TGIFILE.ART` (Showdown); same build 8168 appears with
`MMFW` (Jinx); both 8168 and 8797 appear with `MMFW` (Case File #1).

Phantom's Rich Header matches Showdown's exactly (build 8047). The
prediction is that Phantom's archives are therefore also Gen 1
`TGIFILE.ART`. But Phantom shipped in Aug 2001 and Jinx in Oct 2001 —
TerraGlyph cut the Gen 2 format somewhere in that window, and we don't
know yet which side of the cut Phantom lands on.

Locking this in matters for:

- [`docs/01-VISION.md`](../01-VISION.md) Engine Lineage table — currently
  shows Phantom as Gen 1 with archive format flagged unverified
- [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) Cross-title
  verification section
- The Phantom row in the eventual `ADGameDescription` detection table's
  generation flag

## Scope

In scope:
- Mount Phantom's ISO (or copy the archive files to
  `tools/exes/phantom/` per the project convention)
- Identify archive file(s) at the disc root or under `scooby\`
- Run `Format-Hex` on the first 16 bytes of the largest archive file
- Compare against:
  - Gen 1 marker: `45 00 00 00` (Showdown's `TGIFILE.ART` opening)
  - Gen 2 marker: ASCII `MMFW` at offset 0
- Update the two doc references with the verdict

Out of scope:
- Decoding any Phantom archive payload (that's Phase 2+ once Showdown's
  `TGIFILE.ART` payload format is cracked)
- Bit-level comparison of Phantom's `Scooby.exe` against Showdown's
  (interesting trivia, not needed for this verdict)
- Anything else on the Phantom disc

## Dependencies

- Phantom ISO mountable (already on disk at `C:\pcloud\SCOOBY\Scooby Doo Phantom of the Knight.iso`)
- `Format-Hex` (built into PowerShell)

## Exit criteria

1. The verdict is binary — Phantom is **Gen 1** or Phantom is **Gen 2** — recorded in both:
   - [`docs/01-VISION.md`](../01-VISION.md) Engine Lineage table (the Phantom row's "Archive" cell stops saying "unverified")
   - [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) Cross-title verification section (the Phantom bullet stops saying "predicted")
2. The hex bytes that produced the verdict are pasted into the appropriate format spec (`tgifile-art.md` if Gen 1, `mmfw-container.md` if Gen 2).

## Deliverables

- Updated [`docs/01-VISION.md`](../01-VISION.md) — Engine Lineage table Phantom row
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — Cross-title verification
- Possibly updated [`docs/formats/mmfw-container.md`](../formats/mmfw-container.md) — only if Phantom turns out to be Gen 2

## Notes

- **Expected result:** Gen 1. The build-pipeline upgrade that introduced Gen 2 (newer linker 8168, dropped MASM 6.14 + cvtres) coincides with the archive format change, and Phantom's Rich Header shows the *old* toolchain (linker 8047). If the format follows the toolchain, Phantom is Gen 1.
- **If the result is unexpectedly Gen 2,** that's meaningful: it would mean the engine evolved during a single linker build cycle, with archive format changing at a different cadence than toolchain. Worth a one-paragraph follow-up in [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) Findings → cross-generation analysis.
- **Worth caching while you're at it:** since you'll have the Phantom disc mounted, copy `Scooby.exe` (and the archive file you Format-Hex'd) into `tools/exes/phantom/` per the [tools/exes/ README](../../tools/exes/README.md). Future analysis won't need to re-mount.
