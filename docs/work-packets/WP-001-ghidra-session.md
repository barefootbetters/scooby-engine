---
layout: default
title: "WP-001: Ghidra Session"
---

# WP-001: Ghidra session — `Scooby.exe` imports + `TGIFILE.ART` decode trace

**Status:** 📝 Drafted
**Phase:** 1 — Format Research
**Depends on:** —
**Companion EC:** [EC-001](../execution-checklists/EC-001-ghidra-session)
**Estimated effort:** 1 day (Ghidra auto-analysis included)

---

## Goal

Load `Scooby.exe` into Ghidra, identify the function chain that opens and decodes a `TGIFILE.ART` entry, and record enough understanding to reimplement that decode in C++ for the ScummVM engine.

## Background

WP-002 (`TGIFILE.ART` decoder) is the bottleneck for Phase 1 exit. Two paths exist to crack it: blind decode-guessing (`probe_art.py` trying RLE / palette / LZ variants), or tracing the decode function inside the binary that already does it correctly. The binary path is higher-confidence — the decode algorithm is guaranteed to be in there.

`Scooby.exe` is small (476 KB), which supports the hypothesis that it's largely an interpreter over `object.ini` + a thin set of resource loaders. That makes finding the relevant function tractable rather than a multi-week archaeology project.

## Scope

In scope:
- PE Rich Header inspection (toolchain identification, 5 min)
- Ghidra project setup at `C:\www\scooby\ghidra\scooby.gpr`
- Auto-analysis pass
- Imports table review (DirectDraw / DirectSound / DirectInput / Bink / Win32 file I/O)
- Locating and labeling the `TGIFILE.ART` file open call and the function chain it dispatches into
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

- Updated [`docs/formats/scooby-exe.md`](../formats/scooby-exe) — Findings sections.
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art) — decode algorithm sub-section.
- Ghidra project file at `C:\www\scooby\ghidra\scooby.gpr`.

## Notes

- If Ghidra auto-analysis takes longer than ~45 minutes, queue up WP-003 and the PE Rich Header check in parallel while it runs.
- If the decode function turns out to be inlined or split across many helpers, time-box the trace at 4 hours and fall back to WP-002 with `probe_art.py` — record what was learned so far and what remains unknown.
- If the binary turns out to be packed (UPX or similar), unpack first; record the packer in `scooby-exe.md`.
- The PE Rich Header check is cheap enough that it should run before Ghidra (so Ghidra can be told the right calling convention from the start).
