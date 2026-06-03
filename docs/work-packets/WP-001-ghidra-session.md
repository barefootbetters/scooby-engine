---
layout: default
title: "WP-001: Ghidra Session"
---

# WP-001: Ghidra session — `Scooby.exe` imports + `TGIFILE.ART` decode trace

**Status:** 📝 Drafted
**Phase:** 1 — Format Research
**Depends on:** WP-003 (palette hunt — run first; may eliminate palette-hunt scope from this session), WP-007 (strings dump — recommended; primes Steps 3–4)
**Companion EC:** [EC-001](../execution-checklists/EC-001-ghidra-session.md)
**Estimated effort:** 1 day (Ghidra auto-analysis included)

---

## Goal

Load `Scooby.exe` into Ghidra, identify the function chain that opens and decodes a `TGIFILE.ART` entry, and record enough understanding to reimplement that decode in C++ for the ScummVM engine.

## Background

WP-002 (`TGIFILE.ART` decoder) is the bottleneck for Phase 1 exit. Two paths exist to crack it: blind decode-guessing (`probe_art.py` trying RLE / palette / LZ variants), or tracing the decode function inside the binary that already does it correctly. The binary path is higher-confidence — the decode algorithm is guaranteed to be in there.

`Scooby.exe` is small (476 KB), which supports the hypothesis that it's largely an interpreter over `object.ini` + a thin set of resource loaders. That makes finding the relevant function tractable rather than a multi-week archaeology project.

**WP-003 baseline (2026-06-02) — concrete Ghidra targets unlocked.** [WP-003](WP-003-pre-payload-region.md)
landed the pre-payload region characterization in [tgifile-art.md §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table)
and also corrected the header offsets (`asset_count` is at `0x0118`, not
`0x011C`; whole header shifted +4 in the prior spec). For this Ghidra
session that means four specific function targets to hunt for, on top of
the generic file-I/O surface:

- **Name-table loader.** A routine that reads the 68-byte name records
  (4 B id + 44 B ASCII name + 20 B metadata) from `TGIFILE.ART` into
  memory and populates a lookup structure. Known shape: count probably
  derived from an iterator that runs at least 811 times (the continuous
  block) and likely more (the mixed tail region carries ~600 more
  records on the same stride). Recognizable by the 68-byte stride, the
  `(id >> 24)` type-tag switch, and the ASCII-string-copy pattern.
- **OBJ-id → asset-entry resolver.** WP-003 confirmed that `entry[i]`
  is the payload for `OBJ` id `i` (453 OBJ records, IDs contiguous 0–452,
  matching `asset_count`). This is a one-line indexer — `asset_table[obj_id].start`
  — and the simplest, cleanest landing zone for "find the function that
  resolves a logical asset name to a file offset."
- **20-byte per-record metadata consumers.** WP-003 found one record
  (`ANIM_BIG_HEAD_BG_P09DAPHNE` at file `0xE644`) carrying `(6534, 6078,
  6078, 0, 0)` as `5x uint32LE` in the metadata field; the rest of the
  continuous block has zero metadata. Schema is unresolved — finding
  code that reads offset 48 of name-table records pins it down.
  Plausible candidates: per-frame dimensions, palette index, animation
  duration.
- **69-entry group descriptor table.** The 4-byte records at `0x0004`–`0x0117`
  remain uncharacterized (values are monotonically increasing uint32s
  exceeding file size, so not raw offsets). Ghidra trace may reveal
  whether the engine actually reads this table at runtime, or whether
  it's link-time-only dead weight.

WP-003 also produced a **negative palette finding** — no 256-entry RGB or
RGBA palette exists in the pre-payload region. Palette discovery moved
to WP-002 (per-asset leading bytes or per-record metadata). For this
Ghidra session, that means palette-load code is *not* expected to read
from the pre-payload region; it's expected to read from inside an asset
payload at or after `0x10017E`, or from the 20-byte metadata field on
OBJ records.

## Scope

In scope:
- PE Rich Header inspection (toolchain identification, 5 min)
- Ghidra project setup at `C:\www\scooby\ghidra\scooby.gpr`
- Auto-analysis pass
- Imports table review (DirectDraw / DirectSound / DirectInput / Bink / Win32 file I/O)
- Locating and labeling the `TGIFILE.ART` file open call and the function chain it dispatches into
- **Locating and labeling the name-table loader** (per WP-003 baseline — see §Background): the routine that reads the 68-byte records at file offset `≥ 0x0F60` into memory
- **Locating and labeling the OBJ-id → asset-entry resolver** (one-line indexer; cleanest landing zone for asset-name → file-offset resolution)
- **Recording any code accessing offsets 48–67 of name-table records** (resolves the 20-byte metadata schema; the field is non-zero on at least one ANIM record per WP-003)
- **Checking whether the 69-entry group descriptor table (0x0004–0x0117) is read at runtime** (still uncharacterized post-WP-003)
- Decompiling the decode function to readable pseudo-C
- Recording findings into `docs/formats/scooby-exe.md` → Findings section

Out of scope:
- Full disassembly of game logic (puzzle state machines, room transitions) — that's Phase 4 work
- Save-game format reverse engineering — deferred until Phase 4
- Audio archive decode functions — covered by WP-004 if needed
- Cross-title comparison (e.g. analyzing Phantom's exe) — covered by WP-005

## Dependencies

- Ghidra installed locally (any recent version; record version in EC-001 pre-flight)
- `Scooby.exe` extracted from the mounted Showdown ISO to `C:\pcloud\SCOOBY\extracted\showdown\Scooby.exe` (or equivalent local path)
- A PE inspector for the Rich Header check (`CFF Explorer`, `PE-bear`, or `pefile` Python lib)

## Exit criteria

1. `docs/formats/scooby-exe.md` Findings → "Toolchain" populated with confirmed compiler + linker.
2. `docs/formats/scooby-exe.md` Findings → "Imports / runtime surface" populated with the DirectX surfaces in use, Bink integration, and file I/O API set.
3. `docs/formats/scooby-exe.md` Findings → "Resource loading map" populated with at least the `TGIFILE.ART` open + dispatch path labeled in Ghidra.
4. The `TGIFILE.ART` decode function is identified (Ghidra function name + entry address recorded) and its pseudo-C decompilation is captured as a code block in `docs/formats/tgifile-art.md` Findings → "Per-entry payload" → new subsection "Decode algorithm (from `Scooby.exe`)".
5. Ghidra project saved at `C:\www\scooby\ghidra\scooby.gpr` with the labels above intact.

## Deliverables

- Updated [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) — Findings sections.
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — decode algorithm sub-section.
- Ghidra project file at `C:\www\scooby\ghidra\scooby.gpr`.

## Notes

- If Ghidra auto-analysis takes longer than ~45 minutes, queue up WP-003 and the PE Rich Header check in parallel while it runs.
- If the decode function turns out to be inlined or split across many helpers, time-box the trace at 4 hours and fall back to WP-002 with `probe_art.py` — record what was learned so far and what remains unknown.
- If the binary turns out to be packed (UPX or similar), unpack first; record the packer in `scooby-exe.md`.
- The PE Rich Header check is cheap enough that it should run before Ghidra (so Ghidra can be told the right calling convention from the start).
