---
layout: default
title: "EC-002: probe_art.py Harness"
---

# EC-002: `probe_art.py` decode-strategy harness

**Paired WP:** [WP-002](../work-packets/WP-002-tgifile-art-decoder.md)
**Purpose:** Ordered enumeration of decode strategies to try against `TGIFILE.ART` entry 0, with stop conditions so the WP doesn't sink into infinite codec-guessing.

**Run 2026-11-13: decoded at Phase B, with B3 confirmed.** WP-001 was blocked, so this ran blind. The ordering below was adapted: B1/B2 were not run as written, because the bytes showed the B3 shape immediately. The real blocker was upstream of the codec. The entry table is not `(start, end)` offsets, so "entry 0" as extracted by Phase A was never an entry start (see [tgifile-art §Header layout](../formats/tgifile-art.md#header-layout)). Each item is annotated below. Outcome: [WP-002 §Outcome](../work-packets/WP-002-tgifile-art-decoder.md#outcome-2026-11-13).

This checklist applies whether or not WP-001's Ghidra trace succeeded. If it did, run only the strategies the trace points at. If it didn't, work the list top-to-bottom; each strategy has a time-box.

---

## Pre-flight

- [x] Pre-flight verdict: **READY** — [pre-flight-WP-002-2026-11-13](../reference/pre-flight-WP-002-2026-11-13.md) (written during the session, not before it; see its lessons learned)
- [x] Python 3.x with `Pillow` installed (3.12, Pillow 12)
- [x] WP-003 ran first if possible — palette extraction from the pre-payload region dramatically simplifies the "what pixel format?" question
- [ ] Reference screenshot from a Scooby Showdown YouTube longplay saved at `docs/assets/screenshots/showdown-screens/` — used for visual comparison (see [WP-009](../work-packets/WP-009-reference-screenshots.md)). **Not met: WP-009 has not run.** The check fell back to canonical character colors (Daphne, Fred, Scooby). Frame comparison is still owed to WP-009.
- [x] `tools/probe_art.py` exists. It replaced the planned skeleton: it walks object resources and scene blocks, not the entry table, and keeps only the decode path that works (per Phase C)

## Phase A — Extract first (no decoding yet, time-box: 30 min)

- [x] Implement entry extraction. Walking the entry table as written fails: 295 of 453 `end` values are impossible.
- [x] Sanity check: **failed, and that was the finding.** The entry table is not offsets. Extraction now walks sector-aligned object resources from `0x20000`.
- [x] Hex-dump the first 64 bytes at `0x10017E`: matches the doc (`F0 0C 25 5C 12 AE F0 08 ...`), but the offset is mid-cel inside OBJ 1, not an entry start

**If sanity checks fail, stop and recheck the entry-table walker — the bug is upstream of any decode strategy.** *(This is what happened. Following it found the archive layout.)*

## Phase B — Strategies, in order. Stop at the first one that produces a recognizable image.

### B1. Raw 8-bit palette-indexed at common resolutions (time-box: 30 min)

If WP-003 found a palette, this is the highest-probability first try.

- [ ] Try interpreting bytes as 8-bit palette indices at 640×480 — *skipped: the data is 16-bit, see B3*
- [ ] Try 320×240, 320×200, 800×600 — *skipped*
- [ ] Save each attempt as a PNG; eyeball for recognizable structure — *skipped*

Stop condition: a recognizable image appears, OR all four resolutions look like pure noise → move to B2.

### B2. Raw 16-bit RGB565 / RGB555 at common resolutions (time-box: 20 min)

DirectX 7 truecolor surfaces are 16-bit; if the engine kept assets in that format, raw 16-bit is possible.

- [ ] Try RGB565 at 640×480, 320×240, 320×200 — *skipped as raw; RGB565 (big-endian) is the pixel format inside the B3 runs*
- [x] Try RGB555 at the same three — *tested on decoded cels instead: wrong colors (green ascot, purple trousers on Fred)*
- [x] Save attempts; eyeball

Stop condition: recognizable image, OR uniform color noise → move to B3.

### B3. `F0`-opcode RLE — interpretation 1 (time-box: 1 hour)

Hypothesis: `F0 NN` = "literal run of NN bytes follows," `F0 00` or `0xFF` = end-of-row, other bytes = palette indices.

- [x] Implement decoder. Variant that works: `F0 count hi lo` is a run of one 16-bit pixel, and any other byte starts a 2-byte literal. Rows are implicit (`width` from the cel header), and there is no end-of-row code.
- [x] Render output: truecolor, no palette. RGB565 read big-endian.
- [x] Visually inspect: Fred (OBJ 1), then Daphne (OBJ 0), Scooby (OBJ 2), Ghost Town backgrounds. **Recognizable; stop here.**

Stop condition: recognizable image, OR decoder runs but output is jumbled → move to B4.

### B4. `F0`-opcode RLE — interpretation 2 *(not needed — B3 decoded; B4–B6 not run)* (time-box: 1 hour)

Hypothesis: `0xFn` is an opcode family where the low nibble carries an operand (run-length, distance, or offset). `F0 0C` → "opcode 0, operand 12"; `F0 08` → "opcode 0, operand 8."

- [ ] Try: low nibble = run length, next byte = the value to repeat
- [ ] Try: low nibble = distance back into output buffer, next byte = copy length (LZ-style with packed opcode)
- [ ] Render and inspect each

Stop condition: recognizable image, OR all variants produce noise → move to B5.

### B5. Standard LZ77 / LZSS (time-box: 1 hour)

If `F0` is a flag byte for the LZSS literal/match distinction (high bit set = literal, etc.):

- [ ] Try LZSS with `F0` as the bit-flag byte interpreted in MSB-first order
- [ ] Try with LSB-first
- [ ] Render and inspect

Stop condition: recognizable image, OR noise → move to B6.

### B6. Stop and reassess (HARD STOP after this point)

If B1–B5 all fail:
- [ ] Document each attempted strategy and what the output looked like in `tgifile-art.md`
- [ ] Escalate to the user: options are (a) extend WP-001 Ghidra session with a fresh look, (b) reduce Phase 5 scope to "TerraGlyph trilogy only, audio omitted," (c) accept failure and revisit later

**Do not** continue past B6 inventing new strategies blind. Past this point the cost-effective move is Ghidra, not Python.

## Phase C — Capture findings (time-box: 30 min after success)

- [x] PNG output saved at `tools/samples/tgifile-art-entry0.png` (committed as the one named exception to the `tools/samples/` policy)
- [x] `tools/probe_art.py` cleaned up. Only the successful path is kept; the failed strategies were never committed, and WP-002 §Outcome records what was tried.
- [x] `tgifile-art.md` Findings populated: [§Cel format](../formats/tgifile-art.md#cel-format) (algorithm, pixel format, no palette, pseudocode), plus §Archive layout, §Object resources, §Scene blocks
- [x] WP-002 exit criteria #1–#4 verified
- [x] WP-002 status updated to ✅ Done in [`WORK_INDEX.md`](../work-packets/WORK_INDEX.md)

## Phase D — Cross-title spot check (stretch, time-box: 30 min)

- [ ] Extract entry 0 from Phantom's `TGIFILE.ART` (after mounting Phantom ISO). **Not run: Phantom disc not mounted.** One command once it is: `py -3 tools/probe_art.py --art <path> --no-hash --verify`
- [ ] Run the successful decoder against it
- [ ] If it produces a recognizable image, the TerraGlyph trio is engine-compatible at the asset-format level — record in WP-005's verdict
- [ ] If it fails, that itself is data: the trio diverges at the asset level even within the same developer, which has implications for the detection table

## Definition of done

- [x] At least one PNG of a Scooby-Doo asset exists at `tools/samples/tgifile-art-entry0.png`
- [x] `tgifile-art.md` documents the decode algorithm
- [x] Phase 1 exit criterion #1 satisfied on recognizability; frame comparison against reference screenshots waits on WP-009
