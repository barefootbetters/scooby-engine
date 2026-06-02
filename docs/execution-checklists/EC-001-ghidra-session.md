---
layout: default
title: "EC-001: Ghidra Session Checklist"
---

# EC-001: Ghidra session — `Scooby.exe` analysis checklist

**Paired WP:** [WP-001](../work-packets/WP-001-ghidra-session)
**Purpose:** Step-by-step checklist for executing WP-001 without scope sprawl into general game-logic disassembly.

The Ghidra session has a habit of sprawling — once the binary is open, every interesting function is tempting. This checklist exists to keep the session scoped to the WP-001 goal: characterize the toolchain, map the runtime surface, and trace the `TGIFILE.ART` decode function. Anything else is logged for a future WP and **not pursued in this session**.

---

## Pre-flight

- [ ] Ghidra installed; version recorded here: __________
- [ ] PE inspector available (`CFF Explorer`, `PE-bear`, or Python `pefile`)
- [ ] `Scooby.exe` extracted from mounted Showdown ISO to a known local path; path recorded here: __________
- [ ] Ghidra projects directory exists at `C:\www\scooby\ghidra\`
- [ ] [`docs/formats/scooby-exe.md`](../formats/scooby-exe) open in a second window for note-taking

## Step 1 — Rich Header / toolchain check (time-box: 15 min)

- [ ] Open `Scooby.exe` in PE inspector
- [ ] Locate the Rich Header (between DOS stub and PE signature)
- [ ] Decode `@comp.id` entries; identify compiler + linker version
- [ ] Verify whether the binary is packed (UPX signature, anomalous section names, low entropy mismatch). If packed, unpack before continuing.
- [ ] Record findings in `scooby-exe.md` → Findings → "Toolchain"

**Outcome of this step:** Compiler family and version are known. Skip to Step 4 if the binary turns out to be packed (Ghidra on a packed binary is wasted time).

## Step 2 — Ghidra project setup (time-box: 30 min, mostly waiting)

- [ ] Create new Ghidra project at `C:\www\scooby\ghidra\scooby.gpr`
- [ ] Import `Scooby.exe`; accept defaults for PE format
- [ ] Set the language/processor explicitly if Step 1 found a non-MSVC toolchain
- [ ] Run auto-analysis with default analyzers enabled (no manual additions in this pass)
- [ ] **While analysis runs, kick off WP-003 (pre-payload region inspection) in another window** — the 1 MB region is a fast win and pairs well with Ghidra's wait time
- [ ] Save project after auto-analysis completes

## Step 3 — Imports table review (time-box: 30 min)

- [ ] Open Symbol Tree → Imports
- [ ] Record imports grouped by category in `scooby-exe.md` → Findings → "Imports / runtime surface":
  - File I/O: `CreateFileA`, `CreateFileW`, `ReadFile`, `SetFilePointer`, `CloseHandle`, `fopen`, `_lopen`
  - Graphics: `DirectDrawCreate`, `Direct3DCreate*`, GDI calls
  - Audio: `DirectSoundCreate`, `waveOut*`
  - Input: `DirectInputCreate*`, `GetAsyncKeyState`
  - Video: `BinkOpen`, `BinkDoFrame`, `BinkClose`, `BinkCopyToBuffer`
  - CRT: which CRT version (`MSVCRT.dll`, `MSVCR70.dll`, etc.) — informs C++ pattern recognition
- [ ] Confirm whether `binkw32.dll` is statically referenced or loaded dynamically

**Outcome of this step:** A one-page architectural map of the runtime surface. This is high-value Ghidra output even if Steps 4–5 fail.

## Step 4 — File-I/O call site labeling (time-box: 1 hour)

- [ ] In Defined Strings: find `"TGIFILE.ART"` (case-sensitive search first; if not found, case-insensitive)
- [ ] Right-click the string → References to → identify all call sites
- [ ] Label the call site function as `open_tgifile_art` (or similar)
- [ ] Repeat for: `"object.ini"`, `"Scooby.eng"`, `"Music.dat"`, `"Sfx.dat"`, `"Voice.dat"`, and any `BK.XXX` Bink reference
- [ ] Record the function names + addresses in `scooby-exe.md` → Findings → "Resource loading map"

**Outcome of this step:** Loader functions are labeled in Ghidra and recorded. This is the foundation for both WP-002 (decode) and any future Phase 4 puzzle disassembly.

## Step 5 — `TGIFILE.ART` decode trace (time-box: 2 hours; HARD STOP at 4 hours total elapsed)

- [ ] Starting from `open_tgifile_art`, trace forward in the decompiled view
- [ ] Identify the function chain: open → read header → read entry → decode payload → return surface
- [ ] Decompile the decode function specifically
- [ ] Capture the decompiled pseudo-C as a code block — paste into `tgifile-art.md` → Findings → "Per-entry payload" → new subsection "Decode algorithm (from `Scooby.exe`)"
- [ ] Note any inline constants (palette indices, opcode tables, magic numbers) — these are gold for WP-002's Python port

**Hard stop:** at 4 hours total elapsed in this session. If the decode function isn't isolated by then, stop, write up "decode is in this region but not isolated" in `scooby-exe.md`, and switch to WP-002 with `probe_art.py` blind-decoding. Don't sink another day; the binary path can resume in a follow-up session once `probe_art.py` results give hints about what to look for.

## Definition of done

- [ ] All five steps' outcomes recorded in `scooby-exe.md` and (for Step 5) `tgifile-art.md`
- [ ] Ghidra project saved
- [ ] WP-001 exit criteria #1–#5 all satisfied
- [ ] WP-001 status updated to ✅ Done in [`WORK_INDEX.md`](../work-packets/WORK_INDEX)
- [ ] WP-002 unblocked: either the decode algorithm is captured (best case) or the WP-002 strategy switches to blind decode (fallback case)

## Out-of-scope captures

Things you will be tempted to do during the session that are **not** WP-001's scope. Note them for future WPs and move on:

- [ ] Save-game format → future Phase 4 WP
- [ ] Puzzle / state machine functions → future Phase 4 WP
- [ ] Audio loader → covered by WP-004's separate path
- [ ] `object.ini` parser internals → covered by WP-001's Step 4 labeling only; full trace is Phase 3 work
- [ ] Anything to do with Bink integration beyond confirming the imports → Phase 4

Record each as a one-line "follow-up" at the bottom of `scooby-exe.md` so they don't get lost.
