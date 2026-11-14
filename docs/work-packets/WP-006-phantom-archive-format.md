---
layout: default
title: "WP-006: Phantom Archive Format"
---

# WP-006: Phantom archive format verification (Gen 1 vs Gen 2)

**Status:** ✅ Done (2026-11-13)
**Phase:** 1 — Format Research (follow-on to the Engine Lineage finding in WP-005)
**Depends on:** —
**Companion EC:** — (single hex dump; no checklist needed)
**Estimated effort:** 1 minute
**Pre-flight:** [pre-flight-WP-006-2026-11-13](../reference/pre-flight-WP-006-2026-11-13.md)

---

## Result (2026-11-13)

**Verdict: Gen 1.** Phantom's `TGIFILE.ART` is the same format as
Showdown's, checked structurally rather than by its first four bytes. Its
engine code is the same build.

| Exit criterion | Result |
|---|---|
| 1. Verdict recorded in VISION and `tgifile-art.md` | ✅ VISION's Phantom bullet now cites WP-006 (the Engine Lineage table row already read `TGIFILE.ART`). `tgifile-art.md` engine-generation line and Cross-title verification bullet updated. |
| 2. Hex bytes in the format spec | ✅ A header comparison table in [tgifile-art §Cross-title verification](../formats/tgifile-art.md#cross-title-verification-2026-06): `35 00 00 00` (53 rooms), object count at `0xD8`, name count at `0x7A0`, first record `ROOM_P31_KST` |
| 3. Structural checks pass | ✅ Went beyond the two checks: `probe_art.py --verify` passes in full on Phantom (5,810 cels, descriptors, name table, 8,304 sequence steps, 552 placements, mask partition) |

**Deviation from §Scope:** the WP fixes the name table at `0x0F60` and the
object count at `0x0118`. Both offsets are Showdown's, and WP-001 showed
the header is count-driven: rooms, then objects, then names. Phantom has
53 rooms, so its object count sits at `0xD8` and its name count at `0x7A0`.
The checks followed the header. Likewise, `45 00 00 00` is Showdown's room
count, not a Gen 1 marker. Phantom opens with `35 00 00 00`.

**Beyond the WP:**

- **Same engine code.** All 71 WP-001-labelled functions are byte-identical
  in Phantom's `Scooby.exe` with addresses masked (`+0xD30` from
  `0x430790` up), and the 20-name character table is the same list. See
  [scooby-exe §Phantom](../formats/scooby-exe.md#phantom-archive-format-and-engine-code-wp-006).
- **Audio** (scope amendment in the pre-flight): `probe_audio.py --verify`
  passes on Phantom's `Sfx.dat`, `Voice.dat` and `Music.dat` (1,067 clips).
- **One data difference:** two steps of `OBJ_KST_MUG` set the sequence
  step's first word, which reads as an x, y offset. The engine never reads
  it. `--verify` now reports such words instead of failing (Showdown passes
  unchanged).
- **Still open in both titles:** room word `0x10`, placement `+0x88`, and
  the `0xB0`/`0xB8` room tables, which are empty in Phantom too.

**Not done:** the WP's note to cache Phantom's files was already met on
2026-06-03. No Phantom images or audio are committed. Renders stayed in the
session scratchpad.

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
  - Gen 1 marker: `45 00 00 00` (Showdown's `TGIFILE.ART` opening — `group_count` = 69)
  - Gen 2 marker: ASCII `MMFW` at offset 0
- **If the first-marker check is Gen 1, run two additional structural checks** (per [WP-003](WP-003-pre-payload-region.md) baseline — the prior version of this WP would have given a Gen 1 verdict on coincidence-prone evidence). These turn a 4-byte coincidence into a structural verdict:
  1. **Header layout check** — Phantom's `TGIFILE.ART` should match the corrected Gen 1 layout from [tgifile-art.md §Header layout](../formats/tgifile-art.md#header-layout): `asset_count` at offset `0x0118` (uint32LE, plausible small integer in the low-thousands range; Showdown's is 453). If it's at `0x011C` instead, Phantom is a Gen 1.5 variant worth recording, not vanilla Gen 1.
  2. **Name-table check** — bytes at offset `0x0F60` should begin with the 68-byte name-record pattern (4-byte `uint32LE` id with type-tag high byte in `{0x10, 0x20, 0x31–0x3F}`, followed by an ASCII string starting with `ROOM_`, `OBJ_`, or `ANIM_`). If the first record at `0x0F60` decodes as a `ROOM_*` name, Phantom is structurally Gen 1.
- Update the two doc references with the verdict (plus any structural surprises)

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
3. **If verdict is Gen 1:** the two structural checks from §Scope (header layout per WP-003 corrected offsets + name-table sanity at `0x0F60`) both pass, OR any deviation is documented as a "Phantom Gen 1.x variant" finding in [tgifile-art.md](../formats/tgifile-art.md).

## Deliverables

- Updated [`docs/01-VISION.md`](../01-VISION.md) — Engine Lineage table Phantom row
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — Cross-title verification
- Possibly updated [`docs/formats/mmfw-container.md`](../formats/mmfw-container.md) — only if Phantom turns out to be Gen 2

## Notes

- **Expected result:** Gen 1. The build-pipeline upgrade that introduced Gen 2 (newer linker 8168, dropped MASM 6.14 + cvtres) coincides with the archive format change, and Phantom's Rich Header shows the *old* toolchain (linker 8047). If the format follows the toolchain, Phantom is Gen 1.
- **If the result is unexpectedly Gen 2,** that's meaningful: it would mean the engine evolved during a single linker build cycle, with archive format changing at a different cadence than toolchain. Worth a one-paragraph follow-up in [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) Findings → cross-generation analysis.
- **Worth caching while you're at it:** since you'll have the Phantom disc mounted, copy `Scooby.exe` (and the archive file you Format-Hex'd) into `tools/exes/phantom/` per the [tools/exes/ README](../../tools/exes/README.md). Future analysis won't need to re-mount.
