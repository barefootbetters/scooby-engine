---
layout: default
title: "EC-001: Ghidra Session Checklist"
---

# EC-001: Ghidra session — `Scooby.exe` analysis checklist

**Paired WP:** [WP-001](../work-packets/WP-001-ghidra-session.md)
**Purpose:** Step-by-step checklist for executing WP-001 without scope sprawl into general game-logic disassembly.
**Executed:** 2026-11-13, headless. See [WP-001 §Result](../work-packets/WP-001-ghidra-session.md#result-2026-11-13).

The Ghidra session has a habit of sprawling — once the binary is open, every interesting function is tempting. This checklist exists to keep the session scoped to the WP-001 goal: characterize the toolchain, map the runtime surface, and trace the `TGIFILE.ART` decode function. Anything else is logged for a future WP and **not pursued in this session**.

---

## Pre-flight

- [x] Pre-flight verdict: **READY** — complete [docs/reference/pre-flight](../reference/pre-flight.md) and commit the filled-in copy before proceeding; `NOT READY` blocks this session. *Filled in as [pre-flight-WP-001-2026-11-13](../reference/pre-flight-WP-001-2026-11-13.md). It was written after the session, not before; that record says so.*
- [x] Ghidra installed; version recorded here: **Ghidra 12.1.4** (build 2026-09-21) at `C:\Users\jjensen\AppData\Local\decompnet\toolchains\ghidra\`, run headless (`support\analyzeHeadless.bat`) on Java 27.0.1
- [x] PE inspector available (`CFF Explorer`, `PE-bear`, or Python `pefile`): Python `pefile`
- [x] `Scooby.exe` extracted from mounted Showdown ISO to a known local path; path recorded here: `C:\dev\scooby-engine\tools\exes\showdown\Scooby.exe` (SHA-256 `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478`)
- [x] Ghidra projects directory exists at `C:\dev\scooby-engine\ghidra\`
- [x] [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) open in a second window for note-taking

## Step 1 — Rich Header / toolchain check (time-box: 15 min)

- [x] Open `Scooby.exe` in PE inspector
- [x] Locate the Rich Header (between DOS stub and PE signature)
- [x] Decode `@comp.id` entries; identify compiler + linker version *(2026-06 reading "VC 5.0 / Linker 5.10" was a mislabel in `tools/rich_header.py`; corrected 2026-11-14 to Visual C++ 6.0, linker 6.00 from the PE header. See [scooby-exe §Toolchain](../formats/scooby-exe.md#toolchain).)*
- [x] Verify whether the binary is packed (UPX signature, anomalous section names, low entropy mismatch). If packed, unpack before continuing. *Not packed: Ghidra auto-analysis finds ordinary Visual C++ 6.0 code and `__FILE__` strings.*
- [x] Record findings in `scooby-exe.md` → Findings → "Toolchain"

**Outcome of this step:** Compiler family and version are known. Skip to Step 4 if the binary turns out to be packed (Ghidra on a packed binary is wasted time).

## Step 2 — Ghidra project setup (time-box: 30 min, mostly waiting)

- [x] Create new Ghidra project at `C:\dev\scooby-engine\ghidra\scooby.gpr`
- [x] Import `Scooby.exe`; accept defaults for PE format
- [x] Set the language/processor explicitly if Step 1 found a non-MSVC toolchain *(not needed: MSVC)*
- [x] Run auto-analysis with default analyzers enabled (no manual additions in this pass). *107 s.*
- [x] **While analysis runs, kick off WP-003 (pre-payload region inspection) in another window** — the 1 MB region is a fast win and pairs well with Ghidra's wait time *(WP-003 was already done)*
- [x] Save project after auto-analysis completes

## Step 3 — Imports table review (time-box: 30 min)

- [x] Open Symbol Tree → Imports. *Cross-check of the [WP-007 import table](../formats/scooby-exe.md#import-table-wp-007); no change.*
- [x] Record imports grouped by category in `scooby-exe.md` → Findings → "Imports / runtime surface" (done by WP-007):
  - File I/O: `CreateFileA`, `CreateFileW`, `ReadFile`, `SetFilePointer`, `CloseHandle`, `fopen`, `_lopen`
  - Graphics: `DirectDrawCreate`, `Direct3DCreate*`, GDI calls
  - Audio: `DirectSoundCreate`, `waveOut*`
  - Input: `DirectInputCreate*`, `GetAsyncKeyState`
  - Video: `BinkOpen`, `BinkDoFrame`, `BinkClose`, `BinkCopyToBuffer`
  - CRT: which CRT version (`MSVCRT.dll`, `MSVCR70.dll`, etc.) — informs C++ pattern recognition
- [x] Confirm whether `binkw32.dll` is statically referenced or loaded dynamically *(static, WP-007)*

**Outcome of this step:** A one-page architectural map of the runtime surface. This is high-value Ghidra output even if Steps 4–5 fail.

## Step 4 — File-I/O call site labeling (time-box: 1 hour)

- [x] In Defined Strings: find `"TGIFILE.ART"` (case-sensitive search first; if not found, case-insensitive). *Three strings (`TGIFILE.ART`, `%sTGIFILE.ART`, `%sTGIFILE%i.ART`), all used in `0x4327D0`.*
- [x] Right-click the string → References to → identify all call sites
- [x] Label the call site function as `open_tgifile_art` (or similar). *Labels use the WP-010 debug channels: `resource_GameResource_ctor`, `resource_GameResource_AddArtFile`, `resource_ArtFile_ctor`.*
- [x] Repeat for: `"object.ini"`, `"Scooby.eng"`, `"Music.dat"`, `"Sfx.dat"`, `"Voice.dat"`, and any `BK.XXX` Bink reference. *Done for `object.ini` and the three `.dat` files; `Scooby.eng` and the Bink path are not traced (follow-ups).*
- [x] Record the function names + addresses in `scooby-exe.md` → Findings → "Resource loading map"

**Outcome of this step:** Loader functions are labeled in Ghidra and recorded. This is the foundation for both WP-002 (decode) and any future Phase 4 puzzle disassembly.

## Step 5 — `TGIFILE.ART` decode trace (time-box: 2 hours; HARD STOP at 4 hours total elapsed)

*Narrowed 2026-11-13 after WP-002 decoded the images from the data. The targets were the descriptors, sequence records, room-block tables, mask roles, room names 18/19 and the WP-008 leads. See WP-001 §Result.*

- [x] Starting from `open_tgifile_art`, trace forward in the decompiled view
- [x] Identify the function chain: open → read header → read entry → decode payload → return surface. *`0x4327D0` → `0x4336F0` → `0x43A8B0` (header) → `0x43B080` / `0x43B3D0` (blocks) → `0x4398A0` (pixels) → `0x439C00` (draw).*
- [x] Decompile the decode function specifically (`0x4398A0`)
- [x] Capture the decompiled pseudo-C as a code block. *In [tgifile-art.md → Decode path in `Scooby.exe`](../formats/tgifile-art.md#decode-path-in-scoobyexe-wp-001), restated rather than pasted.*
- [x] Note any inline constants (palette indices, opcode tables, magic numbers) — these are gold for WP-002's Python port. *`0xF0` run marker; `0x3FFFF` sequence/frame masks; `0x3E0` green mask for the 555 path; layer depth `-110000 + 10000k`; 256-slot bitmap cache.*

**Hard stop:** at 4 hours total elapsed in this session. If the decode function isn't isolated by then, stop, write up "decode is in this region but not isolated" in `scooby-exe.md`, and switch to WP-002 with `probe_art.py` blind-decoding. Don't sink another day; the binary path can resume in a follow-up session once `probe_art.py` results give hints about what to look for.

## Definition of done

- [x] All five steps' outcomes recorded in `scooby-exe.md` and (for Step 5) `tgifile-art.md`
- [x] Ghidra project saved
- [x] WP-001 exit criteria #1–#5 all satisfied
- [x] WP-001 status updated to ✅ Done in [`WORK_INDEX.md`](../work-packets/WORK_INDEX.md)
- [x] WP-002 unblocked: either the decode algorithm is captured (best case) or the WP-002 strategy switches to blind decode (fallback case). *WP-002 finished blind first; WP-001 confirmed its algorithm and corrected the transparency and raw-cel rules.*

## Out-of-scope captures

Things you will be tempted to do during the session that are **not** WP-001's scope. Note them for future WPs and move on:

- [x] Save-game format → future Phase 4 WP
- [x] Puzzle / state machine functions → future Phase 4 WP
- [x] Audio loader → covered by WP-004's separate path *(the index layout fell out of the `scrappyid` trace and is recorded as a WP-004 lead; the codec was not touched)*
- [x] `object.ini` parser internals → covered by WP-001's Step 4 labeling only; full trace is Phase 3 work
- [x] Anything to do with Bink integration beyond confirming the imports → Phase 4

Recorded as one-line follow-ups in [scooby-exe.md §Follow-ups](../formats/scooby-exe.md#follow-ups-out-of-wp-001-scope).
