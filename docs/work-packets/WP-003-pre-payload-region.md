---
layout: default
title: "WP-003: Pre-Payload Region"
---

# WP-003: Inspect the 1 MB pre-payload region (palette hunt)

**Status:** ✅ Done (2026-06-02)
**Phase:** 1 — Format Research
**Depends on:** —
**Unblocks (recommended, not strict):** WP-001 (Ghidra session can drop palette-hunt scope if this finds the palette), WP-002 (decoder gets a head-start on first decode strategy)
**Companion EC:** — (single-session investigation; no checklist needed)
**Pre-flight required:** Yes — this WP writes facts into [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md). See [pre-flight gate](../reference/pre-flight.md) → "format documentation under `docs/formats/**` that locks a fact." Paired pre-flight at [pre-flight-WP-003-2026-06-02](../reference/pre-flight-WP-003-2026-06-02.md) (verdict READY); paired session prompt at [session-WP-003-2026-06-02](../sessions/session-WP-003-2026-06-02.md).
**Targets generation(s):** Gen 1 (Showdown). `TGIFILE.ART` is Gen-1-only; Gen 2/3 use the MMFW family (see [mmfw-container](../formats/mmfw-container.md)). Phantom's archive format is still unverified per [scooby-exe §Pending: Phantom archive format](../formats/scooby-exe.md#pending-phantom-archive-format) — this WP does not extend to Phantom until WP-006 locks the generation classification.
**Estimated effort:** 1–2 hours
**Actual effort:** ~2 hours (matched estimate). Findings landed in [tgifile-art.md §Pre-payload region — engine name table](../formats/tgifile-art.md#pre-payload-region--engine-name-table); spec correction landed in [tgifile-art.md §Header layout](../formats/tgifile-art.md#header-layout); strings cross-check landed in [tgifile-art.md §Gen 1 (Showdown) — Strings cross-check (WP-007 hand-off)](../formats/tgifile-art.md#gen-1-showdown--strings-cross-check-wp-007-hand-off).

---

## Goal

Identify the contents of the 1,045,046-byte region between the end of the `TGIFILE.ART` asset entry table (offset `0x0F48`) and the first asset payload (offset `0x10017E`). Most likely candidates: palette table(s), asset name strings, frame metadata, or some combination.

## Background

The asset entry table ends at offset `0x0F48` (3,912 bytes after the start). The first asset payload starts at offset `0x10017E` (1,048,958 bytes). That leaves ~1 MB of unaccounted bytes currently labeled "packed/padded region" in [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md).

One megabyte is a lot of padding. The strong working hypothesis is that this region contains the palette table — and if true, WP-002 gets much easier because palette-indexed decode becomes the obvious first thing to try.

Secondary hypothesis: this region contains asset name strings (which would also confirm the lookup mechanism that the deferred hash-test was meant to probe).

## Scope

In scope:
- Hex inspection of the region `0x0F48` through `0x10017E` (length 0xFF236 = 1,045,046 bytes)
- Pattern recognition: long runs of similar byte values, ASCII string density, periodic structure
- If a palette is found: extract it, record format (RGB vs. RGBA, byte order, count of entries) in `docs/formats/tgifile-art.md`
- If names are found: sample a handful and cross-reference against `object.ini` for matches
- Resolution of the 4-byte gap at `0x0118`–`0x011B` (between declared group descriptor end and asset count field)

Out of scope:
- Full decode of any payload entry (that's WP-002)
- Implementing extraction tooling in C++ (Phase 3)

## Dependencies

- **`TGIFILE.ART` cached locally** at `tools/exes/showdown/TGIFILE.ART` (144,592,896 bytes; SHA-256 `B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807` per [tools/exes/README §Showdown](../../tools/exes/README.md#showdown-gen-1)). No disc re-mount needed; the pre-flight cites this path. Re-rip of the disc invalidates this row — re-cache + new SHA-256 + new pre-flight.
- **`Scooby.exe` strings dump** at `tools/exes/showdown/strings-ansi.txt` (1,959 entries, gitignored). Landed by WP-007 (`docs:` commit `930a4ca`). Cross-checked at WP-003 close per §Notes "Hand-off from WP-007 / hand-off to WP-002" below.
- Hex viewer (HxD, 010 Editor, `xxd`, Python `bytes` slicing, or equivalent — choice doesn't matter as long as the byte ranges in the Findings are reproducible from the cited SHA-256).

## Exit criteria

1. The byte range `0x0F48`–`0x10017E` is characterized in writing — palette table? name table? both? something else?
2. If a palette is found: format documented (entries, bit depth, byte order) and one palette block extracted as a raw binary file for use by WP-002's `probe_art.py`.
3. If name strings are found: at least three sample strings recorded and cross-referenced against `object.ini` references.
4. The 4-byte gap at `0x0118`–`0x011B` is read in hex and characterized (zero padding? unidentified field? typo in the spec?).
5. `docs/formats/tgifile-art.md` updated — either "packed/padded region" is replaced with concrete findings, or the label is confirmed as accurate with a note explaining why a 1 MB pure-padding region exists.

## Deliverables

- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — Findings section with characterized region
- If a palette is extracted: `tools/samples/tgifile-art-palette-0.bin`

## Notes

- This WP is a **prerequisite for WP-001**, not parallel — if the 1 MB region contains a palette,
  the palette-hunt scope drops out of the Ghidra session entirely. Run it first.
- If the region turns out to contain a palette, immediately update WP-002's "first decode strategy" to "palette-indexed with the discovered palette" before any other approach.
- 1 MB of pure padding would be unusual for an early-2000s archive format — engines of that era cared about disc space. If the region really is padding, that itself is data: it suggests the archive was generated by a tool that aligns asset starts to some large boundary (1 MB? sector-multiple? disk-frame-aligned?).
- **Hand-off from WP-007 / hand-off to WP-002.** If candidate asset-name strings turn up in the pre-payload region, cross-check each against `tools/exes/showdown/strings-ansi.txt` per [WP-007 §Hand-off to WP-003](WP-007-strings-and-imports.md#notes). A candidate that appears in the strings dump but not in the pre-payload region — or vice versa — is a signal worth recording. The strings dump confirms string-keyed lookup is the engine's asset-resolution pattern (`Failed to locate id %s` / `Failed to locate object name %s` per [scooby-exe §Showdown — Error / debug strings](../formats/scooby-exe.md#showdown-gen-1)); a matching name table in the pre-payload region would identify the table the engine indexes into.
- **Generation discipline.** Every Finding subsection in [tgifile-art.md](../formats/tgifile-art.md) reached by this WP labels its source as Gen 1 (Showdown). The WP cannot claim its findings apply to Phantom until WP-006 locks Phantom's archive format as Gen 1 `TGIFILE.ART` (currently unverified per [scooby-exe §Pending: Phantom archive format](../formats/scooby-exe.md#pending-phantom-archive-format)). If Phantom turns out to ship Gen 2 `MMFW` instead, this WP's findings are Showdown-only and do not propagate.

---

## Findings landed (2026-06-02)

| Exit criterion | Status | Evidence |
|---|---|---|
| 1. Pre-payload region characterized in writing — palette? names? both? | ✅ | [tgifile-art.md §Pre-payload region — engine name table](../formats/tgifile-art.md#pre-payload-region--engine-name-table). Region is the engine name table (811 clean records in the continuous block, + further records in the mixed tail). Not a palette. |
| 2. If a palette is found: format documented; one block extracted | ✅ (negative) | No palette in the region — explicit negative finding in [tgifile-art.md §Remaining unknowns](../formats/tgifile-art.md#remaining-unknowns). Palette discovery moved to [WP-002](WP-002-tgifile-art-decoder.md). |
| 3. If name strings are found: ≥ 3 samples cross-referenced against `object.ini` | ✅ (cross-referenced against `strings-ansi.txt` per WP-007 hand-off; stronger evidence than `object.ini` alone) | [tgifile-art.md §Gen 1 (Showdown) — Strings cross-check (WP-007 hand-off)](../formats/tgifile-art.md#gen-1-showdown--strings-cross-check-wp-007-hand-off) — 42/42 ROOM (100 %), 228/453 OBJ (50.3 %), 65/316 ANIM (20.6 %) of continuous-block names also present in `tools/exes/showdown/strings-ansi.txt`. |
| 4. 4-byte gap at `0x0118` read in hex and characterized | ✅ | [tgifile-art.md §Gen 1 (Showdown) — 4-byte gap at `0x0118`](../formats/tgifile-art.md#gen-1-showdown--4-byte-gap-at-0x0118). Outcome (c) from the session prompt: bytes at `0x0118` are the `asset_count` field; the prior spec had the offset wrong by 4 bytes. Whole header shifted 4 bytes earlier in the corrected layout. |
| 5. `tgifile-art.md` updated — "packed/padded region" replaced or downgraded | ✅ | Replaced with three concrete subsections: §Region layout, §Record format, §Resource ID schema, plus §Strings cross-check (WP-007 hand-off). |

**Out-of-scope follow-ups surfaced during execution (not bundled):**

- **20-byte per-record metadata schema.** One record in the continuous block (`ANIM_BIG_HEAD_BG_P09DAPHNE` at file `0xE644`) carries `(6534, 6078, 6078, 0, 0)` as `5x uint32LE` — plausibly width/height/something for a multi-cel sprite. Schema TBD; deferred to [WP-001](WP-001-ghidra-session.md) Ghidra trace.
- **Mixed tail region (`0xE6CC`–`0x10017E`, ≈ 990 KB).** Further name records on 68-byte stride interleaved with F0-opcode packed data (same compression signature as asset payloads at `≥ 0x10017E`). The interleaved packed bytes may be per-resource cel/frame data. Deferred to WP-001 / WP-002.
- **Group descriptor table (69 × 4-byte records at `0x0004`–`0x0117`).** Still uncharacterized — values are monotonically increasing uint32s far exceeding file size, so they cannot be raw offsets. Possibly packed (group_index, asset_index_start) tuples. Not in WP-003 scope; remains in [tgifile-art.md §Group descriptor table](../formats/tgifile-art.md#group-descriptor-table-offsets-0x04-0x117) as an open question, deferred to WP-001.
