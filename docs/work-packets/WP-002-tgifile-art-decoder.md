---
layout: default
title: "WP-002: TGIFILE.ART Decoder"
---

# WP-002: `TGIFILE.ART` payload decoder + first image extraction

**Status:** 📝 Drafted
**Phase:** 1 — Format Research
**Depends on:** WP-001 (preferred — gives decode algorithm directly; can be started without if Ghidra path is blocked)
**Companion EC:** [EC-002](../execution-checklists/EC-002-probe-art-harness)
**Estimated effort:** Half-day if WP-001 succeeds; 1–2 days if blind-decoding

---

## Goal

Decode at least one `TGIFILE.ART` entry from *Showdown in Ghost Town* to a recognizable PNG or BMP that visually matches in-game output. This satisfies Phase 1 exit criterion #1 and unblocks Phase 2.

## Background

`TGIFILE.ART` structure is understood (69 groups, 453 asset entries, 8-byte `(start, end)` records — see `docs/formats/tgifile-art.md`). The remaining unknown is the per-entry payload compression. Opening bytes of entry 0 (`F0 0C 25 5C 12 AE F0 08`) match no standard codec.

Three viable strategies:

| Strategy | Time | Confidence | Trigger |
|---|---|---|---|
| Reimplement decode from Ghidra trace (WP-001 output) | Half-day | High | WP-001 succeeded |
| Blind decode-guessing: opcode RLE → 8-bit palette → LZ variants | 1–2 days | Medium | WP-001 blocked or partial |
| Hybrid — Ghidra gives algorithm name (e.g. "LZ77"), confirm by reimplementing standard variant | Half-day | High | WP-001 partial |

## Scope

In scope:
- `tools/probe_art.py` — Python harness for extracting and attempting to decode entries
- Decoder implementation in Python sufficient to render one entry to PNG/BMP
- Visual comparison against a screenshot from gameplay or a YouTube longplay
- Palette discovery (whether from the pre-payload region per WP-003 or from the decode logic itself)
- Recording the decode algorithm in `docs/formats/tgifile-art.md`

Out of scope:
- C++ decoder implementation in the ScummVM engine (Phase 3, WP-020 equivalent)
- Decoding all 453 entries — one is sufficient for Phase 1 exit
- Sprite/animation frame extraction beyond what's needed to verify the algorithm

## Dependencies

- `Scooby.exe` decode trace from WP-001 (preferred)
- Pre-payload region findings from WP-003 (palette table likely lives there)
- Python 3.x with `Pillow` for PNG output
- Hex viewer for sanity-checking decoded byte patterns

## Exit criteria

1. `tools/probe_art.py` runs and successfully extracts and decodes at least entry 0 of *Showdown*'s `TGIFILE.ART`.
2. Output PNG/BMP is visually recognizable as a Scooby-Doo asset (background, sprite frame, or UI element). Recognizability is the test, not pixel-exact match against a specific source.
3. `docs/formats/tgifile-art.md` Findings → "Per-entry payload" section populated with: compression algorithm name (or description), pixel format (palette vs. truecolor + bit depth), palette location and format, decode pseudocode or working Python.
4. Output PNG/BMP committed to `tools/samples/tgifile-art-entry0.png` for visual reference.

## Deliverables

- [`tools/probe_art.py`](../../tools/probe_art.py) — extraction + decode harness
- [`tools/samples/tgifile-art-entry0.png`](../../tools/samples/) — first successful decode
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art) — Findings section

## Notes

- The `F0` byte appearing twice in the first 8 bytes of entry 0 is the strongest pattern signal. EC-002 enumerates the specific opcodes and operand layouts to try.
- If the algorithm turns out to be a custom RLE, capture the full opcode table in the format spec — it's the load-bearing piece of intellectual property for Phase 3's C++ decoder.
- Cross-title verification (entry 0 of Phantom's `TGIFILE.ART` decodes with the same algorithm) is a stretch goal for this WP and a prerequisite for treating the TerraGlyph trilogy as engine-compatible.
- If after EC-002's full enumeration the decode still fails, the WP escalates: open a discussion with the user about whether to invest more time on Ghidra (WP-001 extension) or accept reduced Phase 5 scope.
