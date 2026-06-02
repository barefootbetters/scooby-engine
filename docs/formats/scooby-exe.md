---
layout: default
title: "Format Spec: Scooby.exe"
---

# Format Spec: `Scooby.exe`

**Status:** Toolchain identified across all four available titles (Showdown, Phantom, Jinx, Case File #1); Ghidra session pending  
**Source discs:** five candidate titles (see Cross-title comparison below)  
**Per-title binary names:** `Scooby.exe` (Showdown/Phantom/Jinx), `Case File #1.exe` (Case File #1)  
**Vision doc reference:** [Project Vision](../01-VISION.md) — Phase 1 work item; Engine Lineage section for generation classification.

This is not a file-format spec in the traditional sense — `Scooby.exe` is a
Windows PE32 binary. This document tracks what we learn from disassembling
it, scoped to what the ScummVM engine needs to reimplement.

**Scope discipline:** Ghidra analysis is a fallback when `object.ini` and
other data files don't fully specify a behavior. Every function
reverse-engineered here should be justified by a concrete gap in the
data-driven path. Resist the urge to map the whole binary — the exe is
small (476 KB) but still contains far more than we need.

---

## Known facts

- Windows PE32 executable.
- Built against DirectX 7.0 (graphics + sound) and Bink (`binkw32.dll`).
- `Scooby.eng` error strings confirm DirectDraw, DirectSound, and CD-ROM
  access are the three hardware surfaces (`0x11`, `0x12`, `0x13`).
- `object.ini` (1,405 lines, plain INI) defines all interactive objects,
  room exits, inventory items, cursor animations, and destination rooms —
  suggesting the exe acts largely as a data-driven interpreter.
- The exe is small (476 KB), which supports the interpreter hypothesis:
  game logic is in the data files, not the binary.

## Key questions for Ghidra

| Question | Why it matters |
|---|---|
| How does the exe open and parse `TGIFILE.ART`? | Cross-validates the format spec; gives us the decode algorithm directly |
| How does the exe open and parse `Music.dat` / `Sfx.dat` / `Voice.dat`? | Reveals index layout and codec without needing to brute-force it |
| How does the exe consume `object.ini`? | Confirms how much logic is data-driven vs. hardcoded |
| What is the puzzle state machine? | Likely not in `object.ini`; must be reimplemented from disassembly |
| What is the save-game format? | Needed for ScummVM save/load integration |
| Is the exe single-threaded? | ScummVM requires single-threaded engines |

## Hypotheses (unverified)

| Hypothesis | Evidence | Confidence |
|---|---|---|
| Resource loading is centralized — a small number of functions open each archive | Standard architecture; small exe size supports it | High |
| Most gameplay rules are driven by `object.ini`, with the exe acting as interpreter | `object.ini` is 1,405 lines naming every object, room, and cursor | Medium |
| Puzzle state machines are exe-resident (not in `object.ini`) | `object.ini` shows static room/object data, not logic branches | Medium |
| The exe is single-threaded | Edutainment titles of the era rarely use worker threads | High |
| Compiler is MSVC (not Borland/Watcom) | Standard for Windows-first Learning Company titles of 2000 | Medium |

## Investigation plan

1. **Load + auto-analyze in Ghidra.** Create project `scooby.gpr` in
   `C:\www\scooby\ghidra\`. Let Ghidra's analyzers run a full pass. Save
   before doing anything else.
2. **Imports table review.** Scan the PE import table for: file I/O
   (`CreateFileA`, `ReadFile`), DirectDraw/Direct3D 7, DirectSound,
   DirectInput, Bink (`BinkOpen`, `BinkDoFrame`). This gives a one-page
   architectural map in ~30 minutes.
3. **File-I/O call sites.** Cross-reference `CreateFileA` / `fopen` call
   sites against the disc's known filenames. Label the loader function for
   each data file (`TGIFILE.ART`, `object.ini`, `Scooby.eng`, `Music.dat`,
   `Sfx.dat`, `Voice.dat`). This is the most valuable Ghidra session —
   probably 2–4 hours.
4. **`TGIFILE.ART` decode path.** Trace the function that opens
   `TGIFILE.ART` through to the function that returns a decoded image
   surface. This cross-validates the format spec in
   [`tgifile-art.md`](tgifile-art.md) and gives us the compression
   algorithm if the file probe alone doesn't reveal it.
5. **`object.ini` interpreter.** Trace where `object.ini` is read and how
   the parsed table is consumed. Answer: is room transition logic, cursor
   swapping, and inventory management driven purely by `object.ini` data, or
   does the exe apply additional hard-coded rules?
6. **Puzzle / state machine disassembly (deferred).** Only after Phase 3
   renders rooms — disassemble exactly the functions whose behavior
   `object.ini` doesn't cover.

## Success condition for Phase 1

A short written note in Findings covering:
- Compiler / toolchain identification.
- The `TGIFILE.ART` loader function labeled in Ghidra — cross-validates
  the format spec.
- First-pass answer: "interpreter over `object.ini`" or "significant
  independent logic in the exe."

## Findings

*To be populated during Phase 1.*

### Toolchain

**Family across all titles checked:** Visual C++ 5.0 (1997 toolchain) +
MASM 6.13 + Cvtomf 5.10 + Linker 5.10. TerraGlyph did not migrate to
VC6 before shipping any of Showdown/Phantom/Jinx, and ImageBuilder
Software did not migrate the inherited engine to VC6 for Case File #1
either (except for one stray VC6-compiled object file).

The toolchain *build numbers* split the titles into three generations
(see Cross-title comparison below) and that split aligns with the
archive-format split (`TGIFILE.ART` → `MMFW`) and the developer-studio
split (TerraGlyph → IBS) — strong corroboration that the engine
evolved along generation boundaries.

### Cross-title toolchain comparison (engine generations)

| Title | Gen | Linker 5.10 build(s) | MSVC 5.0 C++ build(s) | MASM 6.13 build(s) | Total entries | Verdict (rich_header.py) |
|---|---|---|---|---|---|---|
| Showdown | 1 | 8047 (×113) | 8034 (×16), 9049 (×10) | 8047 (×10), 8966 (×114) | 11 | Linker 5.10, build 8047 |
| Phantom  | 1 | 8047 (×113) | 8034 (×16), 9049 (×10) | 8047 (×10), 8966 (×120) | 11 | Linker 5.10, build 8047 |
| Jinx     | 2 | **8168** (×160) | 8034 (×17) | **8168** (×157) | 6 | Linker 5.10, build 8168 |
| Case File #1 | 3 | **8168** (×36) + **8797** (×126) | 8034 (×17) | 8797 (×8) | 10 | Linker 5.10, build 8797 |

**Gen 1 (Showdown ↔ Phantom):** identical toolchain at every row.
Only difference: Phantom carries 6 additional MASM 6.13 (build 8966)
compilations vs. Showdown. Same engine + incremental ASM additions
across the 2000–2001 release gap.

**Gen 2 (Jinx):** TerraGlyph upgraded the build pipeline mid-2001.
Newer linker build (8168 vs 8047), single dev environment (one MSVC
5.0 C++ build instead of two), dropped legacy tools (MASM 6.14,
cvtres). 39% more compiled units overall (Linker count 160 vs ~113;
.lib imports 278 vs 202). Consistent with engine evolution +
feature additions on the same core.

**Gen 3 (Case File #1):** the load-bearing finding —
ImageBuilder Software **inherited** TerraGlyph's compiled object files:

- The Linker 5.10 build **8168** entry (count 36) is the **same linker
  version Jinx used**. These are almost certainly inherited engine
  modules built with the Jinx-era toolchain.
- The Linker 5.10 build **8797** entry (count 126) is newer — fresh
  IBS-written code on top of the inherited engine.
- The MSVC 5.0 C++ build **8034** entry (count 17) is **identical
  byte-for-byte** to Jinx's (same product ID, same build, same count).
  This is the strongest possible signal: IBS shipped TerraGlyph's
  compiled `.obj` files directly into the Case File #1 link, then
  added their own code on top.
- One VC6 (`MSVC 6.0 C / Utc12_C_Book`) object file appears (count 1)
  — likely an experimental IBS file with a VC6-only dependency.
  Doesn't indicate engine migration; the bulk is still VC5.

This is **direct code-level inheritance from TerraGlyph to IBS**, not
just architectural reuse or source-code licensing. The post-shutdown
engine continuation is concrete and binary-confirmed.

### Cross-title runtime dependencies

| Title | Bink runtime | Smacker runtime | QuickTime | XML parser | Cutscene path |
|---|---|---|---|---|---|
| Showdown | `binkw32.dll` | absent | absent | absent | Bink (`BK.XXX`) |
| Phantom  | unverified, predicted same | TBD | TBD | absent | Bink (predicted) |
| Jinx     | `binkw32.dll` (in `INSTALL\`) | `Smackw32.dll` | `qtmlClient.dll` | absent | Bink + Smacker + AVI |
| Case File #1 | absent from disc surface | absent | absent | **`libexpat.dll`** (XML) | raw `.avi` files |

The Gen 3 shift away from Bink/Smacker toward raw `.avi` files, plus
the XML parser introduction, is an IBS-era architectural choice — not
a TerraGlyph one.

### Pending: Phantom archive format

Phantom's Rich Header matches Showdown's exactly (Gen 1 by toolchain),
but its archive format is not yet verified. Predicted to be Gen 1
`TGIFILE.ART`, not Gen 2 `MMFW`, but a one-minute
`Format-Hex E:\scooby\TGIFILE.ART -Count 8` check on the mounted
Phantom disc settles it.

### Imports / runtime surface

*TBD — DirectX surfaces in use, Bink integration, file I/O APIs.*

### Resource loading map

*TBD — which function opens which file; what the dispatch/lookup looks like.*

### `object.ini` interpreter behavior

*TBD — data-driven or not? What categories of logic live in the exe?*

### Threading and event model

*TBD — single-threaded? message-pump? worker threads?*

### Save-game format

*TBD — deferred until Phase 4.*

---

## References

- Vision doc: [Project Vision](../01-VISION.md)
- Companion specs: [tgifile-art](tgifile-art.md), [audio-archives](audio-archives.md)
- Ghidra project: `C:\www\scooby\ghidra\scooby.gpr` (to be created)
