---
layout: default
title: "EC-002: probe_art.py Harness"
---

# EC-002: `probe_art.py` decode-strategy harness

**Paired WP:** [WP-002](../work-packets/WP-002-tgifile-art-decoder)
**Purpose:** Ordered enumeration of decode strategies to try against `TGIFILE.ART` entry 0, with stop conditions so the WP doesn't sink into infinite codec-guessing.

This checklist applies whether or not WP-001's Ghidra trace succeeded. If it did, run only the strategies the trace points at. If it didn't, work the list top-to-bottom; each strategy has a time-box.

---

## Pre-flight

- [ ] Python 3.x with `Pillow` installed
- [ ] WP-003 ran first if possible — palette extraction from the pre-payload region dramatically simplifies the "what pixel format?" question
- [ ] Reference screenshot from a Scooby Showdown YouTube longplay saved at `tools/samples/showdown-reference.png` — used for visual comparison
- [ ] `tools/probe_art.py` skeleton exists with: (a) entry extractor that reads the header and dumps entry N to a raw `.bin` file, (b) a registry of decode strategies to try

## Phase A — Extract first (no decoding yet, time-box: 30 min)

- [ ] Implement entry extraction: read the 12-byte header, walk the asset entry table, extract entry 0 to `tools/samples/tgifile-art-entry0.bin`
- [ ] Sanity check: file size of extracted entry matches `end - start` from the entry table
- [ ] Hex-dump the first 64 bytes; first 32 should match what's documented in `tgifile-art.md` (`F0 0C 25 5C 12 AE F0 08 ...`)

**If sanity checks fail, stop and recheck the entry-table walker — the bug is upstream of any decode strategy.**

## Phase B — Strategies, in order. Stop at the first one that produces a recognizable image.

### B1. Raw 8-bit palette-indexed at common resolutions (time-box: 30 min)

If WP-003 found a palette, this is the highest-probability first try.

- [ ] Try interpreting bytes as 8-bit palette indices at 640×480
- [ ] Try 320×240, 320×200, 800×600
- [ ] Save each attempt as a PNG; eyeball for recognizable structure (silhouettes, gradients, character shapes)

Stop condition: a recognizable image appears, OR all four resolutions look like pure noise → move to B2.

### B2. Raw 16-bit RGB565 / RGB555 at common resolutions (time-box: 20 min)

DirectX 7 truecolor surfaces are 16-bit; if the engine kept assets in that format, raw 16-bit is possible.

- [ ] Try RGB565 at 640×480, 320×240, 320×200
- [ ] Try RGB555 at the same three
- [ ] Save attempts; eyeball

Stop condition: recognizable image, OR uniform color noise → move to B3.

### B3. `F0`-opcode RLE — interpretation 1 (time-box: 1 hour)

Hypothesis: `F0 NN` = "literal run of NN bytes follows," `F0 00` or `0xFF` = end-of-row, other bytes = palette indices.

- [ ] Implement decoder; if first row decodes to a sensible-looking pixel band, continue for one frame
- [ ] Render output as palette-indexed PNG (use WP-003 palette if available; otherwise a default 256-grey)
- [ ] Visually inspect

Stop condition: recognizable image, OR decoder runs but output is jumbled → move to B4.

### B4. `F0`-opcode RLE — interpretation 2 (time-box: 1 hour)

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

- [ ] PNG output saved at `tools/samples/tgifile-art-entry0.png`
- [ ] `tools/probe_art.py` cleaned up — keep only the successful decode path, comment-out the failures, leave a one-line note explaining what was tried
- [ ] `tgifile-art.md` Findings → "Per-entry payload" populated with: algorithm name, pixel format, palette source, decode pseudocode or working Python excerpt
- [ ] WP-002 exit criteria #1–#4 verified
- [ ] WP-002 status updated to ✅ Done in [`WORK_INDEX.md`](../work-packets/WORK_INDEX)

## Phase D — Cross-title spot check (stretch, time-box: 30 min)

- [ ] Extract entry 0 from Phantom's `TGIFILE.ART` (after mounting Phantom ISO)
- [ ] Run the successful decoder against it
- [ ] If it produces a recognizable image, the TerraGlyph trio is engine-compatible at the asset-format level — record in WP-005's verdict
- [ ] If it fails, that itself is data: the trio diverges at the asset level even within the same developer, which has implications for the detection table

## Definition of done

- [ ] At least one PNG of a Scooby-Doo asset exists at `tools/samples/tgifile-art-entry0.png`
- [ ] `tgifile-art.md` documents the decode algorithm
- [ ] Phase 1 exit criterion #1 satisfied
