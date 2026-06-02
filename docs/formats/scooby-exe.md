# Format Spec: `Scooby.exe`

**Status:** Pre-investigation — not yet loaded into Ghidra  
**Source disc:** *Scooby-Doo! Showdown in Ghost Town* (2000, The Learning Company)  
**Sample file:** `C:\pcloud\SCOOBY\Scooby Doo Showdown in Ghost Town.iso` → `scooby\Scooby.exe`  
**File size:** 487,473 bytes (≈ 476 KB)  
**Vision doc reference:** [`docs/01-VISION.md`](../01-VISION.md) — Phase 1 work item

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

*TBD — compiler, linker, runtime library.*

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

- Vision doc: [`docs/01-VISION.md`](../01-VISION.md)
- Companion specs: [`tgifile-art.md`](tgifile-art.md), [`audio-archives.md`](audio-archives.md)
- Ghidra project: `C:\www\scooby\ghidra\scooby.gpr` (to be created)
