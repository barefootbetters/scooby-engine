---
layout: default
title: "Format Spec: Scooby.exe"
---

# Format Spec: `Scooby.exe`

**Status:** Toolchain identified across all four available titles (Showdown, Phantom, Jinx, Case File #1). Showdown resource loading, animation, rendering, `object.ini` and sound-id paths traced in Ghidra ([WP-001](../work-packets/WP-001-ghidra-session.md), 2026-11-13; see [Resource loading map](#resource-loading-map)). Decompdecomp collaboration on Case File #1 under way ([WP-011](../work-packets/WP-011-casefile-decompdecomp.md): access received 2026-11-11, local trial pending)  
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
| Resource loading is centralized — a small number of functions open each archive | Standard architecture; small exe size supports it. **Confirmed by WP-001:** one `GameResource` object owns every art file, and one `GameSound` object owns the three sound files | Confirmed |
| Most gameplay rules are driven by `object.ini`, with the exe acting as interpreter | `object.ini` is 1,405 lines naming every object, room, and cursor. WP-001: object *kinds* and their keys come from `object.ini` (looked up live per object), but rooms are C++ objects and several override placements in code | Medium (asset binding confirmed; logic partly in code) |
| Puzzle state machines are exe-resident (not in `object.ini`) | `object.ini` shows static room/object data, not logic branches | Medium |
| The exe is single-threaded | Edutainment titles of the era rarely use worker threads | High |
| Compiler is MSVC (not Borland/Watcom) | Standard for Windows-first Learning Company titles of 2000. **Confirmed:** Visual C++ 6.0, linker 6.00 ([§Toolchain](#toolchain), corrected 2026-11-14) | Confirmed |

## Investigation plan

1. **Load + auto-analyze in Ghidra.** Create project `scooby.gpr` in
   `C:\dev\scooby-engine\ghidra\`. Let Ghidra's analyzers run a full pass. Save
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

## Two analysis tracks

The investigation plan above is **Track A**. **Track B** was added 2026-11-11. The two are complementary: B generates leads and code-equivalence evidence at volume, and A turns leads into understood, named, validated subsystems. Neither replaces the format-first strategy in the [Vision](../01-VISION.md#game-logic-strategy).

### Track A — focused Ghidra analysis ([WP-001](../work-packets/WP-001-ghidra-session.md))

Targeted manual work: entry points, imports, strings and cross-references, resource-loading functions, file signatures, format decoders, script dispatch, game-state structures, and naming and validating the major subsystems. Primary binary: Showdown (Gen 1). This stays the path to the Gen 1 blockers (`TGIFILE.ART` decode, the `object.ini` consumer, the `scrappyid` resolver).

### Track B — decompdecomp-assisted analysis ([WP-011](../work-packets/WP-011-casefile-decompdecomp.md))

Cooperative, AI-assisted decompilation with [decompdecomp](https://github.com/n-delic/decompdecomp): function extraction, candidate C reconstruction, byte matching against the original compiler output, parallel agent processing, a cooperative room that hands out unhandled functions to collaborators, and reuse and matching across related executables. Its output is a stream of leads for Track A. Initial binary: Case File #1 (Gen 3). Simeon Armenchev ([monyarm](https://github.com/monyarm)) started that decompilation in his private repository. Machine setup is in [Setting Up decompdecomp on Windows](../reference/decompdecomp-setup.md). Case File #1's place in the lineage rests on string, RTTI and source-path evidence, with the toolchain as support, and WP-005 found Case File #2 to be a different engine; see WP-011 §Background.

**A byte-identical match is evidence, not understanding.** It shows that candidate C is equivalent to the original bytes. It does not establish correct high-level semantics, suitable names, a readable architecture, or anything usable in ScummVM. Track B findings use the [WP-011 evidence model](../work-packets/WP-011-casefile-decompdecomp.md#evidence-model) (Reported → Observed → Matched → Corroborated → Integrated → Accepted). Matched C and generated assembly stay out of this public repo. The ScummVM engine is written independently from documented behavior.

## Success condition for Phase 1

A short written note in Findings covering:
- Compiler / toolchain identification.
- The `TGIFILE.ART` loader function labeled in Ghidra — cross-validates
  the format spec.
- First-pass answer: "interpreter over `object.ini`" or "significant
  independent logic in the exe."

## Findings

### Binary identity (WP-007 baseline)

Reference table for every binary the [WP-007](../work-packets/WP-007-strings-and-imports.md) strings + imports extraction ran against. Every subsequent Finding subsection cites the SHA-256 of the binary it derives from; a re-extraction against a different SHA invalidates the corresponding row.

| Title | Generation | Path | Size (bytes) | SHA-256 |
|---|---|---|---|---|
| Showdown | Gen 1 | `tools/exes/showdown/Scooby.exe` | 487,473 | `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` |
| Phantom | Gen 1 | `tools/exes/phantom/Scooby.exe` | 483,377 | `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED` |
| Jinx | Gen 2 | `tools/exes/jinx/Scooby.exe` | 847,872 | `136A276872803AC99B0D050B21CC3A83F8E1608F2394C33865CFFF781FB20271` |
| Case File #1 | Gen 3 | `tools/exes/casefile1/Scooby.exe` | 786,432 | `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8` |

Case File #2 was not covered by this baseline (its disc was not cached at the time). WP-005 (2026-11-13) later cached and examined it: `tools/exes/casefile2/Scooby.exe`, 774,144 bytes, SHA-256 `AB2B71FEEFF0777B26928E95C99F9936F5C4D87FE321ED4913B8956C83772BC8`. It is **not this engine**; see [Case File #2 (WP-005)](#case-file-2-wp-005).

Extraction tooling: [`tools/extract_strings.py`](../../tools/extract_strings.py) and [`tools/extract_imports.py`](../../tools/extract_imports.py). Raw outputs (`strings-ansi.txt`, `strings-wide.txt`, `imports.txt`) live under `tools/exes/<title>/`, gitignored per [tools/exes/README](../../tools/exes/README.md). Determinism confirmed: re-running each script against the same binary produces byte-identical output.

### Gen 1 discs are 2001 reissues (2026-11-14)

The cached Showdown and Phantom discs are **not first pressings**. They are
one re-pressing of both games, mastered by The Learning Company three
minutes apart on 2001-08-24, about ten months after the games first came
out. Everything below was read from the ISOs and the cached binaries:

| | Showdown | Phantom |
|---|---|---|
| ISO volume created | 2001-08-24 07:51 | 2001-08-24 07:48 |
| `Scooby.exe` PE timestamp (UTC) | 2001-08-23 01:47 | 2001-08-23 01:51 |
| `Scooby.exe` version resource | `Gold v1.19` (file 1.0.1.9), © 2000 TerraGlyph | `Gold v1.16` (file 1.0.1.6), © 2000 TerraGlyph |
| `TGIFILE.ART` file date | 2001-08-24 | 2001-08-24 |
| Game data (`*.dat`, `object.ini`) | 2000-08-31 to 2000-09-01 | 2000-09-19 to 2000-10-04 |
| Installer `Setup.inf` | SKU 380326, `S_VERSION = 1.2` | SKU 380325, `S_VERSION = 1.2` |
| Readme PDF | © 2001 TLC; Windows 95/98/Me/2000/XP; DirectX 8a | same |

Both discs carry the same 2001 installer kit (DirectX 8 dated 2001-06-08,
Acrobat Reader 4, the AOL and TLC e-registration bundles), the same
"Mystery Adventures" series branding, and the same "Groovy Goodies"
trailer for an upcoming Scooby-Doo movie. For comparison, Jinx's ISO was
mastered 2001-09-27 and *Activity Challenge*'s 2001-09-18.

**First release.** The game data dates and the "© 2000" in both exes fit
a 2000 release for both titles. Public listings agree on Showdown
(October 2000) but not on Phantom: Kotaku gives 2000-10-31; GamePressure
gives 2001-03-12. This repo's title tables keep their 2000 and 2001
until a primary source settles it.

**What this changes:**

- **The Gen 1 binaries are post-gold patch builds**, not the 2000 release
  builds. The toolchain rows below (VC6 build 8966) describe what TerraGlyph
  compiled in August 2001. What the 2000 release exes were compiled with
  is unknown: we don't have them.
- **The Gen 1 → Gen 2 toolchain change is not a sequence.** TerraGlyph
  built the Gen 1 reissue exes on 2001-08-23 with VC6 build 8966 and
  Jinx's on 2001-09-19 with build 8168, four weeks apart. That is two build
  environments in use at once, which supports the "different build
  environment, not an upgrade" reading below and rules out a mid-2001
  switch-over.
- **Showdown and Phantom sharing a build date is the reissue, not a
  shared original release cycle.** That they are the same engine build
  (WP-006: 71 functions byte-identical) is expected of two exes built four
  minutes apart.
- **The format specs describe the 2001 data.** `TGIFILE.ART` was rebuilt
  (or at least rewritten) for the reissue. A first-pressing disc could
  differ in its exe, its archive, or both. WP-012's detection entries
  (size and MD5 of three files) match only this pressing; a first-pressing
  disc would go undetected until one is found and added.

### Toolchain

**Corrected 2026-11-14: every title checked is Visual C++ 6.0, not 5.0.**
The 2026-06 reading ("Visual C++ 5.0 + MASM 6.13 + Cvtomf 5.10 + Linker
5.10") came from a wrong product-ID table in
[`tools/rich_header.py`](../../tools/rich_header.py). Three independent
sources agree on the correction:

- **Microsoft's own `prodid` enum** (names as tabulated in
  [kirschju/richheader](https://github.com/kirschju/richheader)
  `prodids.py`): 0x000A is `Utc12_C`, 0x000B is `Utc12_CPP` (the VC++ 6.0
  C and C++ compilers), 0x000E is `Masm613`, 0x000C is `AliasObj60`,
  0x0004 is `Linker600`, 0x0013 is `Linker512`, 0x0006 is `Cvtres500`, and
  0x0031 is `Utc12_2_CPP` (VC++ 6.0 with the Processor Pack).
- **richprint's empirical comp.id database**
  ([dishather/richprint](https://github.com/dishather/richprint)
  `comp_id.txt`), which matches the enum and ties builds to releases.
- **The PE optional header** of all five binaries says
  `MajorLinkerVersion.MinorLinkerVersion` = **6.00**. link.exe writes that
  field itself; Linker 5.10 would write 5.10.

The old script called the VC6 C compiler "Linker 5.10", the VC6 C++
compiler "MASM 6.13", MASM 6.13 "Cvtomf 5.10", and the linker 5.12
import records "MSVC 5.0 C++". It now uses the enum names and reads the
linker version from the PE header. VC6-era link.exe does not record itself
in the Rich Header; the `Linker*` entries that do appear are import/export
records inside linked `.lib` files.

**What each title's own code was compiled with** (the largest C++ entry;
service-pack attributions are richprint's, not checked against a
known-good binary here). The Showdown and Phantom rows are the August 2001
reissue builds; see [Gen 1 discs are 2001 reissues](#gen-1-discs-are-2001-reissues-2026-11-14):

| Title | Gen | Linker (PE header) | Game C++ code | Other compiled objects |
|---|---|---|---|---|
| Showdown | 1 | 6.00 | VC6 `Utc12_CPP` build **8966** (×114), richprint: VC6 SP5 | C 8047 (×113) and C++ 8047 (×10), which richprint marks "likely libs" |
| Phantom | 1 | 6.00 | VC6 `Utc12_CPP` build **8966** (×120) | same as Showdown |
| Jinx | 2 | 6.00 | VC6 `Utc12_CPP` build **8168** (×157), richprint: VC6 RTM | C 8168 (×160) |
| Activity Challenge | 2 (WP-013) | 6.00 | VC6 `Utc12_CPP` build **8447** (×135), plus 8168 (×8) | C 8168 (×160), as in Jinx |
| Case File #1 | 3 | 6.00 | VC6 Processor Pack `Utc12_2_CPP` build **8943** (×161), richprint: VC6 SP4 + Processor Pack | C 8797 (×126), C 8168 (×36), C++ 8797 (×8), one VS2002 `Utc13_C` 8830 object |
| Case File #2 | — | 6.00 | VC6 Processor Pack `Utc12_2_CPP` build **9044** (×71), richprint: VC6 SP5 + Processor Pack; plus VC6 `Utc12_CPP` 8966 (×53) | C 8966 (×26), C 8047 (×11), C++ 8047 (×2), one VS2002 `Utc13_CPP` 9178 object |

The CRT is linked statically in Gen 1–3 (see the import tables below), so
part of each title's C object count is CRT and library code, not game
code.

**What still holds.** The build numbers still split the titles into
groups that line up with the archive-format split (`TGIFILE.ART` →
`MMFW`) and the studio split (TerraGlyph → IBS): Showdown and Phantom are
identical, Jinx uses one compiler build throughout, and Case File #1
shares build 8168 with Jinx. **What changes:** the direction of the Gen 1
→ Gen 2 step, and what Case File #1's entries say about inheritance (see
below).

### Cross-title toolchain comparison (engine generations)

Rich Header entries by `prodid` enum name, from the corrected
`tools/rich_header.py` (2026-11-14). C and C++ are compiled objects;
`Linker512`/`Linker600`/`Implib*` are import/export records from linked
libraries; `Import0` is imports with no comp.id.

| Title | Gen | C++ (`Utc12_CPP` / `Utc12_2_CPP`) | C (`Utc12_C`) | MASM 6.13 | Import records | Other | Entries |
|---|---|---|---|---|---|---|---|
| Showdown | 1 | 8966 (×114), 8047 (×10) | 8047 (×113) | 7299 (×30) | `Linker512` 8034 (×16), 9049 (×10); `Linker600` 8447 (×13); `Import0` ×202 | `AliasObj60` 7291 (×1), `Cvtres500` 1735, unmarked ×2 | 11 |
| Phantom | 1 | 8966 (×120), 8047 (×10) | 8047 (×113) | 7299 (×30) | same as Showdown | same as Showdown | 11 |
| Jinx | 2 | **8168** (×157) | **8168** (×160) | 7299 (×29) | `Linker512` 8034 (×17); `Import0` ×278 | `Cvtres500` 1720 | 6 |
| Activity Challenge | 2 (WP-013) | 8447 (×135), **8168** (×8) | **8168** (×160) | 7299 (×29) | `Linker512` 8034 (×17); `Import0` ×280 | `Cvtres500` 1735 | 7 |
| Case File #1 | 3 | PP **8943** (×161), 8797 (×8) | 8797 (×126), **8168** (×36); VS2002 `Utc13_C` 8830 (×1) | 7299 (×30) | `Linker512` 8034 (×17); `Linker600` 8447 (×2); `Import0` ×248 | `Cvtres500` 1735 | 10 |
| Case File #2 | — (not this lineage, WP-005) | PP 9044 (×71), 8966 (×53), 8047 (×2); VS2002 `Utc13_CPP` 9178 (×1) | 8966 (×26), 8047 (×11) | 7299 (×2) | `Implib710` 2179 (×19); `Implib700` 9466 (×4); `Linker600` 8047 (×2); `Import0` ×363 | `AliasObj60` 7291 (×13), `Cvtres500` 1735 | 13 |

**Gen 1 (Showdown ↔ Phantom):** identical toolchain at every row. The
only difference is six more C++ objects in Phantom (×120 against ×114):
the same engine plus a few added source files. (The 2026-06 text said six
more *MASM* compilations; that was the mislabel.)

**Gen 2 (Jinx):** a different build environment, not an upgrade.
*Corrected 2026-11-14:* the 2026-06 text called this a pipeline upgrade
("newer linker build 8168"). Build 8168 is the VC6 release (RTM) compiler,
older than Gen 1's 8966. Jinx compiled everything, C and C++, with that
one build, and links neither `OLDNAMES.LIB` alias objects nor the
`Linker600` import libraries Gen 1 uses. Its compiled-object count is
higher (317 C and C++ objects against 237) and it imports through more
library records (278 against 202), consistent with a larger code base.
The Gen 1 exes compared here were built four weeks before Jinx's (both
in 2001), so the two environments ran side by side; see
[Gen 1 discs are 2001 reissues](#gen-1-discs-are-2001-reissues-2026-11-14).

**Gen 3 (Case File #1):** ImageBuilder Software (IBS) inherited
TerraGlyph's engine as **source** and rebuilt it with a newer compiler.
*Corrected 2026-11-14:* the 2026-06 text said IBS shipped TerraGlyph's
compiled `.obj` files directly, based on two mislabelled entries.

- Case File #1's C++ is all newer than Jinx's: 161 objects from the VC6
  Processor Pack (build 8943) and 8 from build 8797. **None of Jinx's
  8168 C++ objects is in it.** The `MM*` framework classes it shares with
  Jinx were recompiled. That fits the strings: its `MMVisualCursor.cpp`
  `__FILE__` path is IBS's own source tree (`F:\Scooby\Museum\framework\`),
  not Jinx's.
- 36 C objects carry **build 8168**, Jinx's compiler build, while the
  rest of Case File #1's C is 8797. They may be a C library carried over
  prebuilt from the Jinx-era tree. Build 8168 is the stock VC6 release,
  so this is suggestive, not proof.
- The `Linker512` build 8034 ×17 entry, identical in Jinx and Case File #1
  (Showdown has ×16), is **import records from linked import libraries**,
  not compiled code. It shows the same import-library set, which is weaker
  than the 2026-06 reading of "TerraGlyph's `.obj` files shipped
  byte-for-byte."
- The "one stray VC6 file" of the 2026-06 text is a single VS2002
  (`Utc13_C`) build 8830 C object, which richprint marks "likely libs".

The lineage verdict for Case File #1 still stands, but on the string,
RTTI and source-path evidence ([Case File #1 strings](#case-file-1-gen-3)),
with the toolchain as supporting evidence, not the "binary-confirmed
`.obj` inheritance" the 2026-06 text claimed.

### Cross-title runtime dependencies

Each cell is now a static-imports verdict from the WP-007 baseline. "Static import" means the symbol is in `Scooby.exe`'s PE `DIRECTORY_ENTRY_IMPORT` and the loader resolves it at process start — checkable by reading `tools/exes/<title>/imports.txt`. DLLs that sit on the disc but are not statically imported are noted in parentheses; they are either dynamically loaded (`LoadLibraryA` + `GetProcAddress`) or installer-only.

| Title | Bink runtime | Smacker runtime | QuickTime | XML parser | Cutscene/video path | DirectSound |
|---|---|---|---|---|---|---|
| Showdown (Gen 1) | static (`binkw32.dll`, 11 fns) | absent | absent | absent | Bink (`BK.XXX`) — `BinkOpen`/`BinkDoFrame` | static (`DSOUND.dll`, ordinal-only) |
| Phantom (Gen 1) | static (`binkw32.dll`, 11 fns — identical to Showdown) | absent | absent | absent | Bink (`BK.XXX`) | static (`DSOUND.dll`, ordinal-only) |
| Jinx (Gen 2) | absent from imports (DLL exists in `INSTALL\` — installer-only or dynamic) | absent from imports (DLL on disc — same caveat) | absent from imports (DLL on disc — same caveat) | absent | Video for Windows (`MSVFW32.dll`: `DrawDibDraw`/`DrawDibOpen`/`MCIWndRegisterClass`) for `.avi` | dynamic load (string `DSOUND.DLL` + `DirectSoundCreate`, no static import) |
| Case File #1 (Gen 3) | absent | absent | absent | **static (`libexpat.dll`, 7 fns: `XML_Parse`/`XML_ParserCreate`/`XML_SetElementHandler`/...)** | COM (`ole32.dll`: `CoCreateInstance`/`CoInitialize` — likely DirectShow filter graphs for raw `.avi`) | dynamic load (same pattern as Jinx) |

**Gen 1 → Gen 2 video boundary (load-bearing correction to prior table):** Jinx's `Scooby.exe` does **not** statically import `binkw32.dll`, `Smackw32.dll`, or `qtmlClient.dll`, contradicting the prior table cell that listed all three as runtime deps. The disc-side DLLs (`INSTALL\binkw32.dll` etc.) are present but not bound to the engine binary at link time. The engine's actual video path is Video-for-Windows `DrawDib` against `.avi` containers (`MSVFW32.dll`). The prior table was reading disc presence as runtime usage; the imports are the load-bearing evidence. WP-005's disc-surface notes still hold — those DLLs *exist* on the Jinx disc — but the engine binary does not bind them statically.

**Gen 2 → Gen 3 video boundary:** Case File #1 drops Video-for-Windows in favor of COM (`ole32.dll`). Combined with the disc-side raw `.avi` files (no Bink/Smacker DLLs anywhere on the Case File #1 disc), this strongly indicates DirectShow filter-graph playback — the standard COM-based Win32 multimedia path of the era. The exact `quartz.dll` symbols are dynamic (no static import), but `CoCreateInstance` of a filter graph is the canonical pattern. xref confirmation deferred to WP-001.

**XML parser boundary:** `libexpat.dll` is the only new statically-imported third-party DLL in Case File #1 vs. the earlier titles. The `XML_*` symbols in the import table match the strings finding of `launch.xml` and confirm the [engine-lineage finding](../01-VISION.md#engine-lineage-2026-06-finding) — IBS introduced XML-driven configuration as a Gen 3 architectural choice.

**DirectSound across all four titles:** Showdown and Phantom statically import `DSOUND.dll` (ordinal-only, the classic 16-byte ordinal-1 import for `DirectSoundCreate`). Jinx and Case File #1 do not statically import `DSOUND.dll` but contain the strings `DSOUND.DLL` and `DirectSoundCreate` — characteristic of `LoadLibraryA("DSOUND.DLL")` + `GetProcAddress("DirectSoundCreate")` dynamic loading. The Gen 2 / Gen 3 engine still uses DirectSound; the link strategy shifted to dynamic for graceful-degradation on systems without it.

The Gen 3 shift away from Bink/Smacker toward raw `.avi` files, plus
the XML parser introduction, is an IBS-era architectural choice — not
a TerraGlyph one — and the import-table evidence now corroborates the
disc-side evidence.

### Phantom archive format and engine code (WP-006)

Settled 2026-11-13. Phantom's `TGIFILE.ART` is the Gen 1 format and passes
every `--verify` check ([tgifile-art §Cross-title verification](tgifile-art.md#cross-title-verification-2026-06)),
and its `.dat` audio files pass `probe_audio.py --verify`
([audio-archives](audio-archives.md)).

The code agrees. All 71 functions labelled by WP-001
([`wp001-labels.txt`](../../tools/ghidra-scripts/wp001-labels.txt)) were
compared between the two `Scooby.exe` builds, with absolute addresses
and `call`/`jmp` targets masked. All 71 are identical over the compared span
(up to the next label, at most 2 KB). Functions below `0x40B000` (exit,
inventory, requires and clickable objects, characters, `object.ini`) sit at
the same addresses. From `0x430790` up (sprites, the sequence player, the
resource manager, the art-file loader and relocation, the renderer, audio)
Phantom's copies sit `0xD30` higher. So the WP-001 labels apply to Phantom
with that shift, and the character-name table moves from `0x46A720` to
`0x469720` with the same 20 entries. Showdown's engine was built with
Phantom's cast already in that table.

Method: a byte comparison in a session script. Ghidra was not run on
Phantom's binary.

### Activity Challenge (WP-013)

Settled 2026-11-14. *Scooby-Doo! Activity Challenge* (2001) runs Jinx's
`MMFW` framework: **Gen 2**. Its executable is
`INSTALL\HDINSTALL\Scooby.exe` on the disc (794,624 bytes, SHA-256
`CE2D0F51…F9A9AB8`; see the
[cache entry](../../tools/exes/README.md#activity-challenge-gen-2)). It
was compared with Jinx's using the WP-005 method.

| Marker | Jinx | Activity Challenge |
|---|---|---|
| `__FILE__` path | `C:\Projects\SCOOBY\mummy\Mmfw\MMVisualCursor.cpp` | `C:\Projects\Scooby\Bonus\Mmfw\MMVisualCursor.cpp` |
| PE timestamp (UTC) | 2001-09-19 20:49 | 2001-09-18 18:32 |
| RTTI type names | 551 | 510; 323 shared with Jinx |
| `MM*` framework classes | 119 | 112, **all** in Jinx |
| Title classes | `MummyApplication`, `MummyStage`, `MummyInteractionScene`, `MummyGameProgress` | `BonusApplication`, `BonusStage`, `BonusInteractionScene`, `BonusGameProgress` |
| Engine strings (non-RTTI, ≥ 8 chars) | 594 | 549; 532 shared |
| Archive names (wide strings) | `Mummy*.MM?`, `Hd.mma`, `Hd.mmp` | `Bonus.MMA`, `Bonus.MMF`, `Bonus.MMP`, `Bonus.MMS` |
| Company and title path string (no `ADVAPI32` import, so not a registry key) | `The Learning Company\Jinx At The Sphinx` | `The Learning Company\Campfire` |
| Imports | 204, from `GDI32`, `KERNEL32`, `MSVFW32`, `USER32`, `WINMM` | 206, same five DLLs; 202 shared |

- **Shared engine strings** include the `MMFW Films`, `Pictures`,
  `Scripts` and `Sounds` labels and every resource-file error template
  (`Bad header`, `Bad checksum`, `Bad time stamp` and `Bad version number
  in … resource file '%s'.`). Activity Challenge's binary still contains
  `Scooby Doo -- Jinx At The Sphinx`.
- **Jinx's seven extra `MM*` classes** are `MMBitmapPictureCollection`,
  `MMBitmapPictureManager` and their resource helper,
  `MM2DTransitionFadeToBlack`, `MM2DTransitionWipeLeft`,
  `MMHighlightable` and `MMSingleEventInterpreter`. Activity Challenge
  links a subset of the framework, and nothing from outside it.
- **Activity Challenge's own 187 type names** are mostly two mini-game
  namespaces, `KnightsTable` (86) and `PieNoon` (74). The rest are a
  skiing game (`SnowMonster`, `SkiingCharacter`), a campfire hub
  (`SceneCampFire`, `CampFireSequencePlayState`) and movement and input
  classes (`MovementThread`, `PollingMouseInputStrategy`,
  `DynamicMovingObject`).
- **Imports** differ by five functions: Activity Challenge adds `MulDiv`,
  `SetCursorPos` and `ShowCursor` and drops `SetEndOfFile` and `FillRect`.
  The video path (`MSVFW32` `DrawDib`) and the dynamic DirectSound load
  (`DSOUND.DLL`, `DirectSoundCreate`) are Jinx's.
- **Toolchain:** the C objects (8168 ×160), MASM (×29) and `Linker512`
  import records (×17) match Jinx exactly. The C++ was compiled with a
  later VC6 build, 8447 (×135), with 8 objects still at 8168. Both
  binaries are linker 6.00 with the same five sections and no version
  resource.

Reading: one source tree (`C:\Projects\Scooby\`) with a project folder per
title, each with its own `Mmfw` folder. The two games were built a
day apart. The format half is in
[mmfw-container](mmfw-container.md#confirmed-magic-bytes-across-samples).

### String literals (WP-007)

Per-title structured anchor strings extracted from each binary's PE data and PE rdata sections via [`tools/extract_strings.py`](../../tools/extract_strings.py). Raw dumps live under `tools/exes/<title>/strings-{ansi,wide}.txt` (gitignored). Only categorized anchor samples, hardcoded paths, registry keys, and a handful of error-message shapes are promoted here — the full dump is left local for copyright reasons (per [WP-007 §Copyright posture](../work-packets/WP-007-strings-and-imports.md#notes)). Every subsection labels its source title + generation; all anchors below come from the binary at the SHA-256 in the [Binary identity table](#binary-identity-wp-007-baseline).

#### Showdown (Gen 1)

SHA-256 of source binary: `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478`

**File / asset names** (filename anchors — load-bearing for Ghidra navigation in [EC-001](../execution-checklists/EC-001-ghidra-session.md) Step 4):

- `TGIFILE.ART`
- `object.ini`
- `Scooby.ini`
- `music.dat`
- `sfx.dat`
- `voice.dat`
- `binkw32.dll`

Format strings driving asset paths (each `%s` is a runtime-resolved directory prefix):

- `%sTGIFILE.ART` — primary archive
- `%sTGIFILE%i.ART` — multi-volume variant (currently unused on the shipped disc, which has only one `TGIFILE.ART`; suggests the loader supports volume-numbered files)
- `%sobject.ini`
- `%sScooby.ini`
- `%sBK.%.3d` — Bink cutscene path (`BK.001`–`BK.058`; numbering matches the disc inventory in [tools/exes/README](../../tools/exes/README.md) §Showdown)
- `%s%s%s.sav` / `%s%s*.sav` — save-game files (`*.sav`)

**Paths / directories** — none hardcoded (asset paths are all `%s`-prefixed; the prefix is resolved at runtime — likely from `Scooby.ini` or registry).

**Source-tree paths** (compile-time `__FILE__` strings, useful for Ghidra cross-referencing to label functions):

- `C:\Scooby\BaseLibrary\Win32\Win32File.cpp`
- `C:\Scooby\BaseLibrary\Win32\Win32Text.cpp`
- `C:\Scooby\BaseLibrary\Win32\Win32Time.cpp`
- `C:\Scooby\BaseLibrary\Win32\Win32Video.cpp`
- `C:\Scooby\Common\Inventory.cpp`
- `C:\Scooby\Common\OptionsSlider.cpp`
- `C:\Scooby\Common\ScoobyGame.cpp`
- `C:\Scooby\GBH\Horseshoe_Corral_Room.cpp` — per-title module is `GBH\` for Showdown
- `C:\Scooby\GBH\Pie_Noon_Room.cpp`
- `C:\Scooby\GBH\Options_Room.cpp`

Source tree shape `C:\Scooby\{BaseLibrary, Common, <title>}` — `BaseLibrary\Win32\` is the OS-abstraction layer, `Common\` the engine core, `<title>\` the per-game room/puzzle code.

**Error / debug strings** (handful of representative shapes; full set in `tools/exes/showdown/strings-ansi.txt`):

- `Failed to read from file TGIFILE.ART` — direct evidence the engine treats `TGIFILE.ART` as the canonical archive name
- `Failed to open music.dat` / `Failed to open sfx.dat` / `Failed to open voice.dat`
- `Failed to create primary drawing surface in video ram.` — DirectDraw primary-surface failure path
- `Failed to create palette for primary surface. Error=%d`
- `Failed set cooperation level, Direct Draw returned error code %d`
- `Failed to locate an ART file`
- `Failed to load room.`
- `Failed to locate id %s` / `Failed to locate object name %s`
- `Failed to initialize the Text Render Manager`
- `Failed to create stream!!!` (audio mixer)
- `Failed to create Semaphore '%s' - %i`

The asset-side failures (`Failed to locate id %s`, `Failed to locate object name %s`) are direct evidence of **string-keyed lookup** — the engine resolves assets by name at runtime, not by static index. xref-confirming this against the asset-key strings below is EC-001 Step 4's job.

**Registry keys**:

- `Software\TerraGlyph\%s` — per-title user-settings root under HKCU/HKLM (the `%s` is the title name, likely `"Showdown in Ghost Town"` or similar)
- `Software\Microsoft\DirectX` — DirectX version-probe key (read-only; used to verify DX 7.0+ presence)

ANSI-only registry calls (`RegOpenKeyExA`, `RegSetValueExA`) per the imports — Win9x-compatible registry usage.

**Asset-key naming convention** (high-signal for Ghidra xref work; these are runtime asset identifiers, not filenames):

- `ROOM_Main_Menu`, `ROOM_Options`, `ROOM_Credits`, `ROOM_Difficulty`, `ROOM_Cheat`, `ROOM_Ghost_Spot`, `ROOM_Gummy`, `ROOM_Artie`, `ROOM_Big_Head`, `ROOM_Open_Safe` — `ROOM_*` is the convention for screen/scene identifiers
- `ROOM_Artifact_Bowl_09`, `ROOM_Artifact_Deer_09`, `ROOM_Artifact_Vase_09` (+`_12`, `_15` variants) — sub-asset naming with numeric variant suffixes
- `ANIM_%s%sIDLE_MASTER`, `ANIM_%s%sBLINK`, `ANIM_%s%sIDLE_P?`, `ANIM_%s%sIDLE_S?`, `ANIM_%s%sSCARED`, `ANIM_%s%sSTAY_SCARED`, `ANIM_%s%sREACTS_CONV_LEFT`, `ANIM_%s%sREACTS_CONV_RIGHT` — `ANIM_<character><something>_<state>` animation lookup pattern (the `?` suffix is a literal char; probably an enumeration suffix in `object.ini`)

These strongly suggest a string-keyed `(category, identifier) → asset` lookup table inside the engine, populated from `object.ini` and `Scooby.eng` at boot. Resolution-strategy confirmation is EC-001 Step 4.

**Other notable strings**:

- `\Scooby-Doo(TM), Showdown in Ghost Town(TM)` — title-card string
- `Showdown.CD` — matches the 0-byte `showdown.cd` disc-presence marker file in the disc root (per [tools/exes/README](../../tools/exes/README.md) §Showdown root inventory)
- `Creating Bink Movie Manager` / `Destroying Bink Movie Manager` — Bink subsystem lifecycle log lines
- `DirectX Version :` — DX-version probe log prefix
- `This program requires a DirectX 7.0 compatible video card and drivers to be installed.` — DX 7.0 requirement gate
- `Try reinstalling DirectX (included on the program CD).` — user-facing fallback message

**Wide-string output:** 30 UTF-16LE strings extracted. Sample: standard CRT/locale wide-string fragments (`u`, `MZ`, etc.) — no UTF-16 asset names. Consistent with VC++ 5.0 / Win9x-targeted code that is ANSI-first across the engine surface; the wide-string pass is effectively negative evidence.

##### Conclusions (Showdown — strings)

- ANSI string count: 1959
- UTF-16LE string count: 30 (≈0 substantive — standard CRT locale fragments only)
- Registry usage: **Yes** — keys `Software\TerraGlyph\%s` (per-title settings), `Software\Microsoft\DirectX` (DX version probe)
- Hardcoded paths: **No** — all asset paths are `%s`-prefixed format strings (runtime-resolved prefix); only source-tree `__FILE__` paths (`C:\Scooby\...`) appear as literals
- Filename anchors for Ghidra (≥3 asset/data filenames required): **`TGIFILE.ART`, `object.ini`, `Scooby.ini`, `music.dat`, `sfx.dat`, `voice.dat`** (six anchors, all confirmed by matching disc-side files in [tools/exes/README](../../tools/exes/README.md) §Showdown)
- Cross-title delta vs Showdown: n/a (this is Showdown)

#### Phantom (Gen 1)

SHA-256 of source binary: `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED`

**File / asset names** — **identical set to Showdown.** Same anchor strings (`TGIFILE.ART`, `object.ini`, `Scooby.ini`, `music.dat`, `sfx.dat`, `voice.dat`, `binkw32.dll`) and same format-string templates (`%sTGIFILE.ART`, `%sTGIFILE%i.ART`, `%sobject.ini`, `%sScooby.ini`, `%sBK.%.3d`, `%s%s%s.sav`). The Gen 1 file-set is fully shared.

**Source-tree paths** — `BaseLibrary\Win32\*.cpp` and `Common\*.cpp` paths match Showdown exactly. Per-title module differs:

- `C:\Scooby\FBF\Drawbridge_Room.cpp` — per-title module is `FBF\` for Phantom (vs. `GBH\` for Showdown)
- `C:\Scooby\FBF\Knights_Table_Room.cpp`
- `C:\Scooby\FBF\Options_Room.cpp`

Both titles share `Common\Options_Room.cpp` and have their own `<title>\Options_Room.cpp` — suggests per-title room overrides over a shared core. This is direct source-tree evidence of the engine-lineage claim: TerraGlyph's `BaseLibrary` + `Common` is shared across Gen 1 titles; only the room/puzzle bundle differs.

**Error / debug strings** — substantively identical to Showdown's set (same `Failed to open music.dat`, `Failed to read from file TGIFILE.ART`, `Failed to locate id %s`, etc.). The Phantom-specific delta is in the room/puzzle code: e.g.

- `3 knight markers should be placed in KST` — `KST` likely "Knight's Square Table" or "Knight Storage" puzzle in Phantom

**Registry keys** — identical to Showdown: `Software\TerraGlyph\%s`, `Software\Microsoft\DirectX`.

**Asset-key naming convention** — same `ROOM_*` / `ANIM_*` patterns as Showdown, with Phantom-specific scene identifiers (e.g. `ANIM_KST_KNIGHT1ARMDRINKS`, `ANIM_KST_KNIGHT1WALKS`, `ANIM_KST_KNIGHT1STARTS_DRINKS`). The `KST_KNIGHT1` prefix is Phantom's `KST` (Knight Square Table) scene + character ID. Identical asset-key convention; different content set.

**Other notable strings** — same Bink lifecycle lines, same DirectX probe strings, same general engine messages. Title-card string is Phantom-specific.

**Wide-string output:** 30 UTF-16LE strings — same shape as Showdown (CRT locale fragments only).

##### Conclusions (Phantom — strings)

- ANSI string count: 1837
- UTF-16LE string count: 30
- Registry usage: **Yes** — same keys as Showdown (`Software\TerraGlyph\%s`, `Software\Microsoft\DirectX`)
- Hardcoded paths: **No** — same `%s`-prefixed pattern as Showdown
- Filename anchors for Ghidra: **`TGIFILE.ART`, `object.ini`, `Scooby.ini`, `music.dat`, `sfx.dat`, `voice.dat`** (identical set to Showdown)
- Cross-title delta vs Showdown: **near-identical** for the engine-surface strings (filename anchors, format strings, registry keys, error templates, asset-key conventions). The Phantom-specific delta is the per-title `FBF\` source module + per-title `ROOM_*`/`ANIM_*` content (`KST_*` etc.) — title content, not engine. Phantom has 122 fewer ANSI strings than Showdown (1837 vs 1959); the difference is entirely in per-title content strings (Showdown has more `ROOM_Artifact_*` variants and other content). The 4,096-byte size delta vs Showdown noted in [tools/exes/README](../../tools/exes/README.md) §Showdown — Phantom *smaller* despite six more C++ objects in the Rich Header — is consistent with Phantom having less per-title content; not surprising once strings counts are this close.

#### Jinx (Gen 2)

SHA-256 of source binary: `136A276872803AC99B0D050B21CC3A83F8E1608F2394C33865CFFF781FB20271`

**File / asset names** (Gen 2 engine — MMFW framework; concrete archive filenames like `Mummy.MMF` do NOT appear in static strings):

- `Scooby.ini` — only concrete asset filename in the EXE
- `MMFW Films`, `MMFW Pictures`, `MMFW Scripts`, `MMFW Sounds` — MMFW resource-type labels (load-bearing for Ghidra navigation: these strings are the lookup keys into the resource registration table)

The Gen 1 file-set (`TGIFILE.ART`, `object.ini`, `music.dat`, etc.) is **completely absent** from Jinx's strings, consistent with the [Gen 1 → Gen 2 archive-format jump](../01-VISION.md#engine-lineage-2026-06-finding) (`TGIFILE.ART` → `MMFW`). The disc-side archive filenames (`Mummy.MMF`, `Mummy.MMA`, `Mummy.MMP`, `Mummy.mms`, `Mummy_HD.MMF` per [tools/exes/README](../../tools/exes/README.md) §Jinx) appear nowhere in the EXE — strongly suggesting they are referenced indirectly via a config file resolved at runtime (most likely `Mummy.mms`, which is the right size and location for a Gen 2 config-archive analogue to Gen 1's `Scooby.eng`).

Format string: `%s_%s_%04X` — generic resource key template (likely `<type>_<name>_<hex-id>`).

**Paths / directories** — none.

**Source-tree paths**:

- `C:\Projects\SCOOBY\mummy\Mmfw\MMVisualCursor.cpp` — only source path retained in static strings

Note the source tree shape: `C:\Projects\SCOOBY\mummy\` (project root) → `Mmfw\` (framework module) → `<source>.cpp`. "Mummy" is Jinx's internal codename (consistent with the disc's `Mummy.*` archive names per [tools/exes/README](../../tools/exes/README.md) §Jinx). The `Mmfw\` subdirectory names the MMFW framework directly — this is the first time the codebase identifies its own framework name in source-tree form.

**Error / debug strings** (Gen 2 — MMFW resource-error templates; substantively different shape from Gen 1):

- `Bad checksum in film resource file '%s'.` / `Bad header in film resource file '%s'.` / `Cannot find film resource file '%s'.` / `Cannot open film resource file '%s'.`
- `Bad checksum in picture resource file '%s'.` (+ same per-error variants)
- `Bad checksum in script file '%s'.` (+ same per-error variants)
- `Bad checksum in sound resource file '%s'.` (+ same per-error variants)
- `MME_FILM_RESOURCE_FILE_BAD_CHECKSUM`, `MME_PICTURE_RESOURCE_FILE_BAD_HEADER`, etc. — MMFW error-code identifier strings (likely runtime-printable enum names)

The error-text structure proves MMFW's resource model: **four resource categories (film, picture, script, sound) × consistent per-category lifecycle errors (open/read/write/seek/header/checksum/version/timestamp)**. This is exactly the abstraction the disc-side `.MMA` / `.MMP` / `.MMF` / `.MMS` extensions would suggest — and confirms the [mmfw-container](mmfw-container.md) hypothesis that MMFW is a resource-typed container, not a single archive format.

**Registry keys** — **None.** Jinx does not statically import `ADVAPI32.dll`. Per-title configuration appears to live entirely on disc (in `Mummy.mms` or similar), not in the registry. This is a Gen 1 → Gen 2 architectural shift away from the TerraGlyph `Software\TerraGlyph\%s` convention.

**Asset-key naming convention** (high-signal):

- `SCENE_BOAT_DOCK`, `SCENE_BOAT_PUZZLE`, `SCENE_BOAT_TRIP`, `SCENE_BRAND`, `SCENE_CREDITS`, `SCENE_DIARY`, `SCENE_DIG_SITE`, `SCENE_EXIT_GAME`, `SCENE_FINALE`, `SCENE_FOOD_FIGHT`, `SCENE_GAME_CENTER`, `SCENE_KINGS_CHAMBER`, `SCENE_LEVEL`
- `SCENE_DEMO_*` variants (`SCENE_DEMO_INTRO`, `SCENE_DEMO_TOWN`, `SCENE_DEMO_SPHINX_INTERIOR`, `SCENE_DEMO_PYRAMID_CENTER`, etc.) — Jinx ships with a demo-mode subsystem

Naming convention shift: **`ROOM_*` (Gen 1) → `SCENE_*` (Gen 2)**. Same string-keyed lookup pattern, renamed identifier prefix — consistent with the MMFW framework using "scene" as its top-level visual unit (per the `MMScene`, `MMSceneParentMolecule`, `MM2DPlanarView` mangled class names elsewhere in the strings dump).

**C++ RTTI class names** (decoded from VC++ mangled-name format; high-signal for MMFW architecture mapping in WP-001):

- `MMAbstractThread`, `MMAct`, `MMScene`, `MMSceneParentMolecule`, `MMStage`, `MMPicture`, `MMSoundLoader`, `MMPictureLoader`, `MM2DFilmLoader`, `MMBitmapPictureCollection`, `MMPermanentPhysicalSoundChannel`, `MMVisualCursor`, `MM2DPlanarView`
- `UUList<T>`, `UUListNode<T>`, `UUOwned<T>`, `UUClassCallback<T>`, `UUClassCallback1Parameter<T1,T2>` — `UU*` utility templates (`UU` = "Utility" or "Universal"?)
- `MMClassSceneServices<T>`, `MMClassViewServices<T>`, `MMStandardResourceHelper<T>` — templated infrastructure
- Jinx-specific: `MummyInteractionScene`, `SphinxDoorPuzzleData`

This is a substantially different engine surface from Gen 1 — class-based, heavy templates, MM/UU prefix convention. The codebase visibly moved from a procedural Gen 1 style (Showdown's `Win32File.cpp`, `Inventory.cpp`, etc.) to a class-hierarchy Gen 2 style.

**Other notable strings**:

- `Scooby Doo` — title-screen string
- `Scooby Doo -- Jinx At The Sphinx` — title-card
- `Jinx At The Sphinx`
- `oops fftinit %d` — FFT-init error string (audio-side; FFT in the audio pipeline implies frequency-domain effects, possibly the audio engine itself is doing more than Bink's straight playback did in Gen 1)
- `MM_TIMESTAMP_MMF_0000`, `MM_TIMESTAMP_MMF_03E8`, `MM_TIMESTAMP_MMF_07D0`, `MM_TIMESTAMP_MMF_0BB8` — MMFW chunk-timestamp markers (likely chunk type IDs)

**Wide-string output:** 27 UTF-16LE strings — CRT locale fragments only, no asset names.

##### Conclusions (Jinx — strings)

- ANSI string count: 1751
- UTF-16LE string count: 27
- Registry usage: **No** — `ADVAPI32.dll` not statically imported; no `HKEY_*` / `Software\*` strings
- Hardcoded paths: **No** — generic `%s_%s_%04X` resource key template only; no asset paths in the binary
- Filename anchors for Ghidra (≥3 required — asset/data anchors): **`Scooby.ini`, `MMFW Films`, `MMFW Pictures`, `MMFW Scripts`, `MMFW Sounds`** (five anchors). Note: only `Scooby.ini` is a literal filename; the four `MMFW <category>` strings are MMFW-resource-type identifiers that play the same Ghidra-navigation role as Gen 1's filename anchors (xrefs lead to the resource-registration code paths). The actual archive filenames (`Mummy.*`) are not in the EXE — anchored by `MMFW *` instead. This is a real architectural difference from Gen 1, not a gap in the dump.
- Cross-title delta vs Showdown: **disjoint** for engine-surface strings (no `TGIFILE.ART`, no `object.ini`, no `Software\TerraGlyph\%s`, no Bink class strings). Asset-key convention renamed `ROOM_*` → `SCENE_*`. C++ class hierarchy visible (Gen 1's procedural style is gone). Confirms the [Gen 1 → Gen 2 boundary](../01-VISION.md#engine-lineage-2026-06-finding) at the source-string level: this is the same studio's engine *family*, but the framework was rewritten between Gen 1 and Gen 2 — MMFW is a substantively new abstraction layer over the same general engine concepts. (*Corrected 2026-11-14:* the 2026-06 text cited a shared "MSVC 5.0 C++ build 8034" entry here. That entry is `Linker512` import records from linked import libraries, which shows a shared library set, not shared code. Both titles are Visual C++ 6.0, with different compiler builds: 8966 for Gen 1, 8168 for Jinx.)

#### Case File #1 (Gen 3)

SHA-256 of source binary: `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8`

**File / asset names** (Gen 3 — MMFW continues; XML-driven configuration; raw `.avi` cutscenes):

- `launch.xml` — Gen 3 bootstrap XML config, parsed by `libexpat.dll`
- `TLC Case File #1 Users.dat` — user-database save file
- `TLC Case File #1 User #%d.dat` — per-user save (`#1`, `#2`, ... — multi-user support)
- `IBSlogo.avi`, `TLClogo.avi`, `WBlogo.avi` — branding/logo cutscenes
- `INTRO_01.avi`, `INTRO_02.avi`, `INTRO_03.avi` — opening cutscenes (matches disc-side root `\Scripts and Resources\` inventory per [tools/exes/README](../../tools/exes/README.md) §Case File #1)
- `ExitJoke.avi`, `GhostCapture.avi` — gameplay cutscenes
- `libexpat.dll`, `ole32.dll`, `SHFOLDER.DLL` — DLL reference strings (mix of static imports and dynamic-load candidates)
- `MMFW Films`, `MMFW Pictures`, `MMFW Scripts`, `MMFW Sounds` — same MMFW resource-type labels as Jinx (confirms MMFW carryover into Gen 3 — code inheritance evidence at the string level; the [cross-title toolchain comparison](#cross-title-toolchain-comparison-engine-generations) shows the `MM*` C++ was recompiled by IBS, with 36 C objects still at Jinx's compiler build 8168)

Format string: `%s_%s_%04X` — same generic resource key template as Jinx (carry-over from MMFW).

**Paths / directories** — none hardcoded.

**Source-tree paths**:

- `F:\Scooby\Museum\framework\MMVisualCursor.cpp` — only source path retained in static strings

Note `MMVisualCursor.cpp` is the **same file name** as Jinx's source path — direct code inheritance evidence at the `__FILE__` level (the file ImageBuilder shipped is at a different absolute path but is structurally the same MMFW source unit). Source tree shape: `F:\Scooby\Museum\framework\` — "Museum" is Case File #1's internal codename (matches the disc directory `F:\MUSEUM\` and the archive filenames `Museum.*` / `MuseumHD.*` / `MuseumCD.*`). `framework\` is the Gen 3 module name for what Jinx called `Mmfw\`.

**Error / debug strings** — substantively similar to Jinx's MMFW resource-error templates (same `Bad checksum in <category> resource file '%s'.` patterns, same `MME_*` enum-name strings). One Gen-3-specific addition:

- `Could not load the required library SHFOLDER.DLL` — `SHFOLDER.dll` (Special-Folder helper) is dynamically loaded; failure is fatal at startup. SHFOLDER is the Win9x/Me/2000 compatibility shim for `SHGetFolderPath` — needed for the per-user save path (`TLC Case File #1 User #%d.dat` likely lives under `My Documents\` or `Application Data\`).

**Registry keys** — **None statically present.** `ADVAPI32.dll` not in the imports table; no `Software\*` strings. Per-user configuration moved out of the registry entirely; it lives in `TLC Case File #1 Users.dat` + per-user `.dat` files. Consistent with the Gen 2 / Gen 3 shift away from registry-based config noted on the Jinx row.

**Asset-key naming convention**:

- The `SCENE_*` convention from Jinx is NOT visible in Case File #1's static strings — likely the asset-keying moved into the XML config (parsed by libexpat) and the EXE no longer carries asset-name string literals for them. This matches the disc-side observation in [tools/exes/README](../../tools/exes/README.md) §Case File #1 ("XML lives inside the archives, parsed by `libexpat.dll` at load time").
- Class names that survived (RTTI): `PGApplication`, `PGStageWindow`, `PGStageWindowClass`, `PGStageControlClass`, `PG2DMovieScene`, `PGMoviePlayerControl`, `PGStageServices`, `SMMovieScene`, `SMSuspectsAndCluesScene`, `SMGameActFactory`, `SMStageServices`, `InventoryState`, `IBState`, `IBEvent`, `IBEventHandler`, `IBStateEventThread`
- The class-name prefixes split into three families: `MM*` (MMFW carryover from Jinx), `PG*` (game-application layer — likely "Project Glow" or "Project Game"; this is the new Gen 3 IBS application-shell layer over MMFW), and `SM*` (Scooby-specific scene logic — likely "Scooby Museum" or "Suspect Manager") + `IB*` (ImageBuilder-named state/event infra).

This confirms the engine-lineage finding's claim of "TerraGlyph (MMFW) inherited, IBS added their own application + game-specific layers on top." The `PG*`/`SM*`/`IB*` class names are the IBS-added layers; the `MM*`/`UU*` classes are the inherited MMFW substrate.

**Other notable strings**:

- `Scooby4Museum, Copyright 2002, ImageBuilder Software Inc.` — IBS attribution (direct authorial confirmation of the IBS handoff; also reveals "Scooby4Museum" as the project's internal codename — the **4** is interesting and ambiguous: it could mean "Scooby (number) 4" suggesting this is IBS's fourth Scooby project, OR it could be a literal "4" in the title casing; the Phase 5 scope rule in [01-VISION](../01-VISION.md#phase-5--polish--contribution) treats Case File #1 as the third TLC Scooby and the first IBS one, so the "4" likely refers to IBS's own product line, not TLC's)
- `Scooby 4 Museum Save Data` — save-data identifier (similar codename use)
- `DSOUND.DLL`, `DirectSoundCreate` — dynamic-load string + entry-point name (consistent with the dynamic DirectSound loading seen on the Jinx row of the [Cross-title runtime dependencies](#cross-title-runtime-dependencies) table)

**Wide-string output:** 31 UTF-16LE strings — CRT locale fragments only, no asset names.

#### Case File #2 (WP-005)

SHA-256 of source binary: `AB2B71FEEFF0777B26928E95C99F9936F5C4D87FE321ED4913B8956C83772BC8`
(`Case File #2.exe` on the disc, cached as `tools/exes/casefile2/Scooby.exe`).
Strings (2,040 ANSI) and imports (330) were extracted with the WP-007 tools
on 2026-11-13. Both stay local.

**Verdict: a different engine, not part of the Gen 1–3 lineage.** The
evidence:

- **Rich Header (weak evidence; corrected 2026-11-14).** The 2026-06
  labels were wrong ([§Toolchain](#toolchain)). Read correctly, every
  binary here, Case File #2 included, is Visual C++ 6.0 with linker 6.00,
  so the compiler does not separate Case File #2 from the lineage. What
  differs is the linked libraries: every Gen 1–3 binary carries 16–17
  `Linker512` build 8034 import records, and Case File #2 has none; it
  links VS2002 and VS2003 import libraries instead (`Implib700` ×4,
  `Implib710` ×19). Its C and C++ builds 8047 and 8966 are the same VC6
  builds Showdown used, but the counts differ (C 8047 ×11 against ×113,
  C++ 8966 ×53 against ×114), and its largest C++ entry is a Processor
  Pack build (9044 ×71) that no lineage binary has. A shared compiler
  build shows the same compiler release, not shared code. The verdict
  rests on the next four points.
- **No shared engine strings.** Case File #2 shares 104–129 strings with
  each lineage binary. Minus what the lineage shares with itself, the
  overlap is Win32 API names, CRT code fragments, and product names
  (`Scooby-Doo`, `The Learning Company`). None of these appear in it:
  `MMFW` labels, `MME_*` error names, `Bad checksum in … resource file`
  templates, `__FILE__` source paths, `ROOM_`/`SCENE_` keys,
  `%s_%s_%04X`, or a single RTTI class name.
- **Different libraries and runtime.** It links the CRT dynamically
  (`MSVCRT.dll`, 84 imports); every lineage binary links it statically. It
  imports Miles (`mss32.dll`, 28) and Bink (`binkw32.dll`, 19), and it
  embeds LZO 1.04, IJG libjpeg and its own XML writer
  (`<?xml version="%s" standalone="%s"?>`) instead of Case File #1's
  `libexpat.dll`.
- **Its own class family.** `R*` names: `RScenePort`, `RWorldPort`,
  `RResourcePort`, `RHotSpot`, `RCharacter`, `RAnimation`,
  `RCompositeAction`, `RDialog`, `RBinkMovie`, `RSndWave`, `RXMLFile`,
  and others (31 in all).
- **The same engine in another game.** The Case File #2 disc carries a
  *Powerpuff Girls* demo (`GroovyGoodies\PPG2Demo\`) whose resources are
  the same `.bul`/`.inx` pair, run by `Powerpuff Girls.exe` plus engine
  DLLs. `trinket.dll` shares 17 of the `R*` class names with Case File #2,
  the bulk-file loader errors (`Bulkfile %s has not been defined in the
  index file.`, `Unable to open index file %s.`), and 542 other strings
  found in neither Showdown nor Case File #1. `ompp32x.dll` ("OM++",
  `OMSoundManager` over Miles), `tcx.dll` (LZO, scripts) and
  `rbink6x.dll` (`RBinkMovie`) account for the rest. Case File #2 is that
  framework linked into one executable.

The executables were read as data and not run. The demo's files were
extracted to the session scratchpad only.

The same framework also runs the publisher's launcher on both Case File
discs (`HD\LAUNCHER\`: `TLCLauncher.exe`, `launch.xml`, `.mps` scripts). On
Case File #1 the launcher ships `TLCLLTrinketcore.dll` and `ompp32x.tlc`.
So the trinket/OM++ framework was already present in Case File #1's
launcher, but not in Case File #1's game (`MMFW`). Case File #2's game is
built on it. The launcher also accounts for the `launch.xml` and
`TLCUser*.dat` strings both executables share.

##### Conclusions (Case File #1 — strings)

- ANSI string count: 1382
- UTF-16LE string count: 31
- Registry usage: **No** — same finding as Jinx; `ADVAPI32.dll` not in imports table
- Hardcoded paths: **No** — generic `%s_%s_%04X` resource key template only; asset names live in XML inside MMFW archives
- Filename anchors for Ghidra: **`launch.xml`, `TLC Case File #1 Users.dat`, `TLC Case File #1 User #%d.dat`, `IBSlogo.avi`, `TLClogo.avi`, `INTRO_01.avi`, `INTRO_02.avi`, `INTRO_03.avi`, `ExitJoke.avi`, `GhostCapture.avi`, `WBlogo.avi`** (eleven anchors — Gen 3 has more loose-file anchors than Gen 2 because raw `.avi` cutscenes are referenced by name)
- Cross-title delta vs Showdown: **disjoint** for engine-surface strings (no `TGIFILE.ART`, no `Bink*`, no `Software\TerraGlyph\%s`). MMFW resource-error templates inherited from Jinx (same `Bad <error> in <category> resource file` shapes). New: `launch.xml` (XML bootstrap), `IBS*.avi` / `INTRO_*.avi` filenames (raw AVI cutscenes), `PG*`/`SM*`/`IB*` class-name families (IBS-added layers over MMFW). The `MMFW Films/Pictures/Scripts/Sounds` resource-type labels carry forward from Jinx — confirms code-level inheritance of the MMFW resource subsystem.

### Import table (WP-007)

Per-title PE import tables extracted via [`tools/extract_imports.py`](../../tools/extract_imports.py) (Python `pefile` walking `DIRECTORY_ENTRY_IMPORT`). Entries are normalized to `DLL::Function`, sorted case-insensitively, deduplicated. Raw dumps under `tools/exes/<title>/imports.txt` (gitignored — function names are uncopyrightable interface data, but kept local for consistency with the strings dumps). Groupings here are by **function role** per WP-007 §Output specification, not by DLL — each role pulls from whichever DLL provides it.

Function names that route to the same Win32 surface across titles (e.g. `KERNEL32.dll::ReadFile`) are listed in each title's section verbatim — the goal is per-title auditability against the Binary identity SHA, not deduplication.

#### Showdown (Gen 1) — 216 entries

SHA-256 of source binary: `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478`

**Win32 File I/O** (23 entries):

- `KERNEL32.dll::CreateFileA` · `CloseHandle` · `ReadFile` · `WriteFile` · `SetFilePointer` · `SetEndOfFile` · `FlushFileBuffers` · `GetFileSize` · `GetFileType` · `GetFileAttributesA` · `DeleteFileA` · `CreateDirectoryA` · `FindClose` · `FindFirstFileA` · `FindNextFileA` · `GetDiskFreeSpaceA` · `GetDriveTypeA` · `GetWindowsDirectoryA` · `SetCurrentDirectoryA` · `GetModuleFileNameA`
- `KERNEL32.dll::GetPrivateProfileStringA` · `GetProfileStringA` · `WritePrivateProfileStringA` — INI-file parsing (consistent with `Scooby.ini` + `object.ini`)

**Memory / Process / Threading / CRT-shim** (90 entries):

- Heap: `HeapAlloc` · `HeapCreate` · `HeapDestroy` · `HeapFree` · `HeapReAlloc` · `HeapSize` · `GlobalAlloc` · `GlobalFree` · `GlobalSize` · `VirtualAlloc` · `VirtualFree`
- Module / process: `GetProcAddress` · `LoadLibraryA` · `FreeLibrary` · `GetModuleHandleA` · `GetCommandLineA` · `ExitProcess` · `GetCurrentProcess` · `TerminateProcess`
- Threading + sync: `CreateThread` · `ResumeThread` · `TerminateThread` · `GetCurrentThread` · `GetCurrentThreadId` · `GetExitCodeThread` · `WaitForSingleObject` · `CreateEventA` · `CreateSemaphoreA` · `SetEvent` · `ResetEvent` · `InitializeCriticalSection` · `EnterCriticalSection` · `LeaveCriticalSection` · `DeleteCriticalSection` · `InterlockedDecrement` · `InterlockedIncrement` · `TlsAlloc` · `TlsFree` · `TlsGetValue` · `TlsSetValue`
- Environment: `GetEnvironmentStrings` · `GetEnvironmentStringsW` · `GetEnvironmentVariableA` · `FreeEnvironmentStringsA` · `FreeEnvironmentStringsW` · `SetEnvironmentVariableA`
- Locale / code-page (CRT-shim): `GetACP` · `GetOEMCP` · `GetCPInfo` · `IsValidCodePage` · `IsValidLocale` · `EnumSystemLocalesA` · `GetLocaleInfoA` · `GetLocaleInfoW` · `GetSystemDefaultLangID` · `GetUserDefaultLCID` · `GetTimeZoneInformation` · `MultiByteToWideChar` · `WideCharToMultiByte` · `LCMapStringA` · `LCMapStringW` · `CompareStringA` · `CompareStringW` · `GetStringTypeA` · `GetStringTypeW` · `IsDBCSLeadByte` · `CharLowerA` *(USER32)* · `lstrcpyA` · `lstrlenA`
- Exception / debugging: `RaiseException` · `RtlUnwind` · `SetUnhandledExceptionFilter` · `UnhandledExceptionFilter` · `SetErrorMode` · `SetConsoleCtrlHandler` · `FatalAppExitA` · `DebugBreak` · `OutputDebugStringA` · `IsBadCodePtr` · `IsBadReadPtr` · `IsBadWritePtr` · `GetLastError` · `SetLastError`
- Misc: `Sleep` · `GetTickCount` · `GetStartupInfoA` · `GetVersion` · `GetVersionExA` · `GetStdHandle` · `SetStdHandle` · `SetHandleCount`

**Graphics / DirectX** (25 entries):

- `DDRAW.dll::DirectDrawCreate` — DirectDraw 7 graphics surface
- `GDI32.dll::BitBlt` · `CreateCompatibleDC` · `CreateDCA` · `CreateDIBSection` · `CreateFontIndirectA` · `CreateRectRgn` · `DeleteDC` · `DeleteObject` · `EndDoc` · `EndPage` · `GetDeviceCaps` · `GetStockObject` · `GetSystemPaletteEntries` · `GetTextExtentExPointA` · `GetTextMetricsA` · `OffsetRgn` · `SelectClipRgn` · `SelectObject` · `SetBkMode` · `SetTextColor` · `StartDocA` · `StartPage` · `StretchDIBits` · `TextOutA`

The `EndDoc`/`EndPage`/`StartDocA`/`StartPage` GDI functions are printing primitives, paired with the WINSPOOL imports below — Showdown can print (likely certificates/coloring pages, period-typical for edutainment).

**Audio / Video** (16 entries):

- `DSOUND.dll::ord#1` — DirectSound; ordinal 1 = `DirectSoundCreate`. Single ordinal-only import is the canonical DirectSound init footprint.
- `binkw32.dll::_BinkClose@4` · `_BinkCopyToBuffer@28` · `_BinkDDSurfaceType@4` · `_BinkDoFrame@4` · `_BinkGetSummary@8` · `_BinkNextFrame@4` · `_BinkOpen@8` · `_BinkOpenDirectSound@4` · `_BinkPause@8` · `_BinkSetSoundSystem@8` · `_BinkWait@4` — 11 Bink runtime symbols (full playback footprint: open/decode/wait/copy/close)
- `WINMM.dll::timeBeginPeriod` · `timeEndPeriod` · `timeGetDevCaps` · `timeGetTime` — high-resolution timer for frame pacing / Bink sync

**Input** (8 entries):

- `DINPUT.dll::DirectInputCreateEx` — DirectInput 7 keyboard/mouse
- `USER32.dll::GetAsyncKeyState` · `GetCursor` · `GetCursorPos` · `GetIconInfo` · `GetKeyboardLayout` · `LoadCursorA` · `SetCursor` · `ShowCursor` · `ClipCursor` — cursor + keyboard polling fallback alongside DirectInput

**CRT / Standard Library**: **none.** No `MSVCRT.dll`, no `MSVCR*.dll`, no `MSVCP*.dll`. The C runtime is **statically linked** — consistent with the heap/locale/exception KERNEL32 surface above being all the CRT shims need.

**Other** (54 entries):

- `ADVAPI32.dll::RegCloseKey` · `RegCreateKeyExA` · `RegOpenKeyExA` · `RegQueryValueExA` · `RegSetValueExA` — registry (matches `Software\TerraGlyph\%s` finding above; ANSI-only)
- `USER32.dll` window/message-pump: `BeginPaint` · `CloseWindow` · `CreateWindowExA` · `DefWindowProcA` · `DestroyWindow` · `DispatchMessageA` · `DrawIcon` · `EndPaint` · `FindWindowA` · `GetDC` · `GetFocus` · `GetMessageA` · `GetSystemMetrics` · `GetWindowRect` · `GetWindowRgn` · `IsWindow` · `MessageBoxA` · `OpenIcon` · `PeekMessageA` · `PostQuitMessage` · `RegisterClassA` · `ReleaseDC` · `SendMessageA` · `SetFocus` · `SetForegroundWindow` · `ShowWindow` · `SystemParametersInfoA` · `TranslateMessage` · `UpdateWindow`
- `IMM32.dll::ImmAssociateContext` · `ImmGetContext` · `ImmGetDefaultIMEWnd` · `ImmGetOpenStatus` · `ImmIsIME` · `ImmReleaseContext` — Input Method Editor (Asian-language IME compatibility — typical for Win9x apps)
- `SHELL32.dll::ExtractIconA` · `ShellExecuteA` · `SHGetMalloc` · `SHGetPathFromIDListA` · `SHGetSpecialFolderLocation` — shell namespace (likely for save-game directory under `My Documents\` etc.)
- `WINSPOOL.DRV::ClosePrinter` · `EnumJobsA` · `EnumPrintersA` · `GetPrinterA` · `OpenPrinterA` · `SetJobA` — printing API (edutainment certificate-print feature)

##### Conclusions (Showdown — imports)

- Path API encoding: **ANSI-only** — `CreateFileA` present, `CreateFileW` absent. Every file/directory/INI-profile entry uses the `*A` ANSI variant. Confirms what the strings scan alone could not — TerraGlyph wrote the Gen 1 engine against the ANSI Win32 surface, no Unicode path support.
- Bink runtime: **static** — `binkw32.dll` with 11 Bink symbols (full playback footprint)
- Smacker runtime: **absent**
- DirectDraw / Direct3D version: **DirectDraw 7** (`DirectDrawCreate`) — no D3D imports; 2D path only
- DirectSound: **static** — `DSOUND.dll` ordinal-1 (`DirectSoundCreate`)
- DirectInput: **static** — `DINPUT.dll::DirectInputCreateEx` (DirectInput 7)
- CRT: **static** — no `MSVCRT.dll` / `MSVCR*.dll` import; CRT linked into the binary at build time (Visual C++ 6.0 static CRT; see [§Toolchain](#toolchain))
- Cross-title delta vs Showdown: n/a (this is Showdown)
- Notable: WINSPOOL printing API + IMM32 IME — both are Win9x edutainment-app patterns rather than game-specific patterns

#### Phantom (Gen 1) — 216 entries

SHA-256 of source binary: `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED`

**Byte-identical to Showdown's import table.** SHA-256 of normalized `imports.txt` matches across both binaries (verified via `diff tools/exes/showdown/imports.txt tools/exes/phantom/imports.txt` returning empty). Every group above for Showdown applies to Phantom verbatim — same 216 entries in the same DLL distribution, including the 11 Bink symbols and the WINSPOOL/IMM32 surfaces.

This is the strongest possible cross-title evidence of engine-level identity at the Gen 1 link boundary: Phantom and Showdown were linked against the same import-library set with the same configuration. Combined with the [Rich Header match](#cross-title-toolchain-comparison-engine-generations) (the same VC6 builds and entries; Phantom has six more C++ objects), Showdown and Phantom are the same engine binary up to per-title content. The Phantom-specific `FBF\` source-tree paths in the [strings findings](#phantom-gen-1) are the only meaningful binary delta.

##### Conclusions (Phantom — imports)

- Path API encoding: **ANSI-only** (identical to Showdown)
- Bink runtime: **static** — `binkw32.dll`, 11 symbols (identical to Showdown)
- Smacker runtime: **absent** (identical to Showdown)
- DirectDraw / Direct3D version: **DirectDraw 7** (identical to Showdown)
- DirectSound: **static** — `DSOUND.dll` ordinal-1 (identical to Showdown)
- DirectInput: **static** — `DINPUT.dll::DirectInputCreateEx` (identical to Showdown)
- CRT: **static** (identical to Showdown)
- Cross-title delta vs Showdown: **identical** — zero import-table difference

#### Jinx (Gen 2) — 205 entries

SHA-256 of source binary: `136A276872803AC99B0D050B21CC3A83F8E1608F2394C33865CFFF781FB20271`

**Win32 File I/O** (17 entries):

- `KERNEL32.dll::CreateFileA` · `CloseHandle` · `ReadFile` · `WriteFile` · `SetFilePointer` · `SetEndOfFile` · `FlushFileBuffers` · `GetFileAttributesA` · `GetFileType` · `DeleteFileA` · `CreateDirectoryA` · `RemoveDirectoryA` · `FindClose` · `FindFirstFileA` · `FindNextFileA` · `GetCurrentDirectoryA` · `GetLogicalDriveStringsA` · `GetDriveTypeA` · `GetVolumeInformationA`
- `KERNEL32.dll::GetPrivateProfileStringA` — INI parsing (single call site; consistent with `Scooby.ini` being the only INI filename in Jinx's strings)
- `KERNEL32.dll::FindResourceA` — PE resource-table read (likely for embedded icon/version info, not for game assets)

**Memory / Process / Threading / CRT-shim** (~89 entries):

- Heap: `HeapAlloc` · `HeapCreate` · `HeapDestroy` · `HeapFree` · `HeapReAlloc` · `HeapSize` · `GlobalAlloc` · `GlobalFree` · `GlobalLock` · `GlobalUnlock` · `GlobalSize` · `GlobalAddAtomA` · `GlobalFindAtomA` · `GlobalDeleteAtom` · `VirtualAlloc` · `VirtualFree`
- Module / process: `GetProcAddress` · `LoadLibraryA` · `FreeLibrary` · `GetModuleHandleA` · `GetCommandLineA` · `GetModuleFileNameA` · `ExitProcess` · `ExitThread` · `GetCurrentProcess` · `TerminateProcess`
- Threading + sync: `CreateThread` · `ResumeThread` · `GetCurrentThread` · `GetCurrentThreadId` · `GetThreadPriority` · `SetThreadPriority` · `WaitForSingleObject` · `CreateEventA` · `CreateSemaphoreA` · `SetEvent` · `InitializeCriticalSection` · `EnterCriticalSection` · `LeaveCriticalSection` · `DeleteCriticalSection` · `InterlockedDecrement` · `InterlockedIncrement` · `TlsAlloc` · `TlsFree` · `TlsGetValue` · `TlsSetValue`
- Environment: `GetEnvironmentStrings` · `GetEnvironmentStringsW` · `FreeEnvironmentStringsA` · `FreeEnvironmentStringsW` · `SetEnvironmentVariableA`
- Locale / code-page: `GetACP` · `GetOEMCP` · `GetCPInfo` · `MultiByteToWideChar` · `WideCharToMultiByte` · `LCMapStringA` · `LCMapStringW` · `CompareStringA` · `CompareStringW` · `GetStringTypeA` · `GetStringTypeW` · `IsDBCSLeadByte` · `lstrcmpiA`
- Exception / debugging: `RaiseException` · `RtlUnwind` · `SetUnhandledExceptionFilter` · `UnhandledExceptionFilter` · `SetErrorMode` · `IsBadCodePtr` · `GetLastError` · `SetLastError` · `OutputDebugStringA` · `FormatMessageA`
- Time / misc: `Sleep` · `GetLocalTime` · `GetSystemTime` · `GetTimeZoneInformation` · `FileTimeToDosDateTime` · `GetStartupInfoA` · `GetVersion` · `GetVersionExA` · `GetStdHandle` · `SetStdHandle` · `SetHandleCount`

**Graphics / DirectX** (21 entries):

- `GDI32.dll::BitBlt` · `CreateCompatibleDC` · `CreateDIBSection` · `CreatePalette` · `CreateRectRgn` · `CreateSolidBrush` · `DeleteDC` · `DeleteObject` · `GdiSetBatchLimit` · `GetDeviceCaps` · `GetObjectA` · `GetStockObject` · `PatBlt` · `RealizePalette` · `SelectClipRgn` · `SelectObject` · `SelectPalette` · `SetBkMode` · `SetDIBColorTable` · `SetTextAlign` · `SetWindowOrgEx`

**No `DDRAW.dll` import.** Jinx renders via GDI DIBs (`CreateDIBSection` + `BitBlt` + palette management), not DirectDraw — a substantial Gen 1 → Gen 2 architectural shift. The disc-side `INSTALL\` may still drop DirectX runtime files for compatibility, but the engine binary itself is GDI-based.

**Audio / Video** (5 entries):

- `MSVFW32.dll::DrawDibClose` · `DrawDibDraw` · `DrawDibOpen` · `DrawDibSetPalette` · `MCIWndRegisterClass` — Video for Windows DrawDib + MCI window class. **This is Jinx's cutscene playback path**: AVI containers rendered through DrawDib into a GDI DIB surface. No Bink, no Smacker static imports.
- `WINMM.dll::timeGetTime` — single timer call (vs. Showdown's full `timeBeginPeriod`/`timeEndPeriod`/`timeGetDevCaps`/`timeGetTime` set; suggests Jinx no longer raises the OS timer resolution explicitly)

**No static `DSOUND.dll` import**, but `DSOUND.DLL` + `DirectSoundCreate` appear as strings — the strings finding above identifies this as dynamic `LoadLibraryA`/`GetProcAddress` loading. DirectSound is still the audio backend; only the link strategy changed.

**Input** (~10 entries, USER32-only):

- `USER32.dll::GetAsyncKeyState` · `GetKeyState` · `LoadCursorA` · `SetCursor` · `GetCursorPos` · `GetCapture` · `SetCapture` · `ReleaseCapture`

**No `DINPUT.dll` import.** Jinx polls keyboard/mouse through USER32 only (`GetAsyncKeyState`, `GetKeyState`, message-pump). The Gen 1 DirectInput-driven input path was dropped between Gen 1 and Gen 2.

**CRT / Standard Library**: **none** (CRT statically linked, same as Gen 1).

**Other** (~63 entries):

- `USER32.dll` window/message-pump: `AdjustWindowRectEx` · `AttachThreadInput` · `BeginPaint` · `CallWindowProcA` · `ChangeDisplaySettingsA` · `ChildWindowFromPointEx` · `CloseWindow` · `CreateWindowExA` · `DefWindowProcA` · `DestroyWindow` · `DispatchMessageA` · `EnableWindow` · `EndPaint` · `EnumChildWindows` · `EnumThreadWindows` · `FillRect` · `GetClassInfoA` · `GetClientRect` · `GetDC` · `GetFocus` · `GetMenu` · `GetMessageTime` · `GetParent` · `GetPropA` · `GetSystemMetrics` · `GetWindow` · `GetWindowLongA` · `GetWindowRect` · `GetWindowThreadProcessId` · `InvalidateRect` · `IsIconic` · `IsWindowEnabled` · `IsWindowVisible` · `KillTimer` · `LoadAcceleratorsA` · `LoadIconA` · `LoadStringA` · `MapWindowPoints` · `MessageBoxA` · `MoveWindow` · `MsgWaitForMultipleObjects` · `OpenIcon` · `PeekMessageA` · `PostMessageA` · `PostQuitMessage` · `PostThreadMessageA` · `RegisterClassExA` · `ReleaseDC` · `RemovePropA` · `ReplyMessage` · `ScreenToClient` · `SendMessageA` · `SendNotifyMessageA` · `SetFocus` · `SetMenu` · `SetPropA` · `SetTimer` · `SetWindowLongA` · `SetWindowPos` · `SetWindowTextA` · `ShowWindow` · `SystemParametersInfoA` · `TranslateAcceleratorA` · `TranslateMessage` · `WaitMessage`

**Notably absent vs Gen 1:** `ADVAPI32.dll` (no registry calls), `SHELL32.dll` (no shell namespace), `IMM32.dll` (no IME), `WINSPOOL.DRV` (no printing), `DDRAW.dll`, `DSOUND.dll`, `DINPUT.dll`, `binkw32.dll`. The Gen 2 engine binary is much more focused — GDI rendering, USER32 input, MSVFW32 video, dynamic-loaded DSound. Half the DLL surface of Gen 1 is gone.

##### Conclusions (Jinx — imports)

- Path API encoding: **ANSI-only** — `CreateFileA` present, `CreateFileW` absent. Same finding as Gen 1; the engine remains ANSI-bound at the Win32 file surface.
- Bink runtime: **absent from imports** (not statically linked). DLL exists on the disc in `INSTALL\` per [tools/exes/README](../../tools/exes/README.md) §Jinx but the engine binary does not call it. Strings dump has zero Bink references — Jinx is not a Bink consumer at all; the disc DLL is either installer-side or vestigial.
- Smacker runtime: **absent from imports** (same caveat — DLL on disc, no engine binding, no strings references)
- DirectDraw / Direct3D version: **DirectDraw dropped** — no `DDRAW.dll` import; rendering is GDI DIB (`CreateDIBSection` + `BitBlt` + `RealizePalette`). This is a substantive Gen 1 → Gen 2 architectural shift.
- DirectSound: **dynamic** — `DSOUND.dll` not statically imported; strings `DSOUND.DLL` + `DirectSoundCreate` present (LoadLibrary/GetProcAddress pattern). Audio backend is still DirectSound; link strategy changed.
- DirectInput: **dropped** — `DINPUT.dll` not imported; input polling moved to USER32 (`GetAsyncKeyState`, `GetKeyState`)
- CRT: **static** (identical to Gen 1)
- Cross-title delta vs Showdown: **removed** `DDRAW.dll`, `DSOUND.dll`, `DINPUT.dll`, `binkw32.dll`, `ADVAPI32.dll`, `SHELL32.dll`, `IMM32.dll`, `WINSPOOL.DRV`. **Added** `MSVFW32.dll` (Video for Windows for cutscene playback). The Gen 1 → Gen 2 jump is a substantial DLL-surface reduction + DirectX-static-link drop + MSVFW32 addition. This corroborates the [engine-lineage finding](../01-VISION.md#engine-lineage-2026-06-finding)'s "TerraGlyph upgraded the build pipeline mid-2001" comment — but the import-side evidence shows the change is more than a build-pipeline upgrade; it's an architectural rewrite of the OS-abstraction layer too.

#### Case File #1 (Gen 3) — 195 entries

SHA-256 of source binary: `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8`

**Win32 File I/O** (16 entries):

- `KERNEL32.dll::CreateFileA` · `CloseHandle` · `ReadFile` · `WriteFile` · `SetFilePointer` · `SetEndOfFile` · `FlushFileBuffers` · `GetFileAttributesA` · `GetFileType` · `DeleteFileA` · `CreateDirectoryA` · `RemoveDirectoryA` · `GetShortPathNameA` · `GetLogicalDriveStringsA` · `GetDriveTypeA` · `GetVolumeInformationA`

**Notably no `FindFirstFileA`/`FindNextFileA`/`FindClose`** in Case File #1's imports — Gen 3 dropped directory-enumeration, consistent with the disc-side observation that all assets live inside named MMFW archives (no need to glob disc directories at runtime). Also no `GetPrivateProfileStringA` — Gen 3 dropped INI parsing entirely in favor of `libexpat`-driven XML.

**Memory / Process / Threading / CRT-shim** (~84 entries):

- Heap: `HeapAlloc` · `HeapCreate` · `HeapDestroy` · `HeapFree` · `HeapReAlloc` · `HeapSize` · `GlobalAlloc` · `GlobalFree` · `GlobalLock` · `GlobalUnlock` · `GlobalSize` · `GlobalAddAtomA` · `GlobalFindAtomA` · `GlobalDeleteAtom` · `VirtualAlloc` · `VirtualFree`
- Module / process: `GetProcAddress` · `LoadLibraryA` · `FreeLibrary` · `GetModuleHandleA` · `GetCommandLineA` · `GetModuleFileNameA` · `ExitProcess` · `ExitThread` · `GetCurrentProcess` · `TerminateProcess`
- Threading + sync: `CreateThread` · `ResumeThread` · `GetCurrentThread` · `GetCurrentThreadId` · `GetThreadPriority` · `SetThreadPriority` · `WaitForSingleObject` · `CreateEventA` · `CreateSemaphoreA` · `SetEvent` · `InitializeCriticalSection` · `EnterCriticalSection` · `LeaveCriticalSection` · `DeleteCriticalSection` · `InterlockedDecrement` · `InterlockedIncrement` · `TlsAlloc` · `TlsFree` · `TlsGetValue` · `TlsSetValue`
- Environment: `GetEnvironmentStrings` · `GetEnvironmentStringsW` · `GetEnvironmentVariableA` · `FreeEnvironmentStringsA` · `FreeEnvironmentStringsW` · `SetEnvironmentVariableA`
- Locale / code-page: `GetACP` · `GetOEMCP` · `GetCPInfo` · `MultiByteToWideChar` · `WideCharToMultiByte` · `LCMapStringA` · `LCMapStringW` · `CompareStringA` · `CompareStringW` · `GetStringTypeA` · `GetStringTypeW` · `IsDBCSLeadByte` · `lstrcmpiA`
- Exception / debugging: `RaiseException` · `RtlUnwind` · `SetUnhandledExceptionFilter` · `UnhandledExceptionFilter` · `SetErrorMode` · `IsBadCodePtr` · `GetLastError` · `SetLastError` · `OutputDebugStringA`
- Time / misc: `Sleep` · `GetLocalTime` · `GetSystemTime` · `GetTimeZoneInformation` · `GetStartupInfoA` · `GetVersion` · `GetVersionExA` · `GetStdHandle` · `SetStdHandle` · `SetHandleCount`

The Memory/Process surface is near-identical to Jinx (same MMFW substrate); minor delta is `FormatMessageA`/`FindResourceA`/`FileTimeToDosDateTime` from Jinx are gone, and `GetEnvironmentVariableA` is back.

**Graphics / DirectX** (28 entries):

- `GDI32.dll::BitBlt` · `CreateCompatibleDC` · `CreateDIBSection` · `CreatePalette` · `CreatePen` · `CreateRectRgn` · `CreateSolidBrush` · `DeleteDC` · `DeleteObject` · `Ellipse` · `GdiSetBatchLimit` · `GetDeviceCaps` · `GetObjectA` · `GetStockObject` · `LineTo` · `MoveToEx` · `PatBlt` · `Polygon` · `Polyline` · `PolyPolygon` · `RealizePalette` · `Rectangle` · `SelectClipRgn` · `SelectObject` · `SelectPalette` · `SetBkMode` · `SetDIBColorTable` · `SetPixelV` · `SetTextAlign` · `SetWindowOrgEx`

Gen 3 GDI imports add **vector primitives** that Jinx didn't have: `Ellipse`, `LineTo`, `MoveToEx`, `Polygon`, `Polyline`, `PolyPolygon`, `Rectangle`, `SetPixelV`, `CreatePen`. The Gen 2 engine was pure DIB blits; the Gen 3 engine also does GDI vector drawing on top. Possible cause: the suspects-and-clues UI (per the `SMSuspectsAndCluesScene` class name) draws diagrammatic content via GDI primitives rather than pre-rendered bitmaps.

**No `DDRAW.dll` import** (same as Gen 2 — DirectDraw remains absent from Gen 3).

**Audio / Video** (1 entry):

- `WINMM.dll::timeGetTime` — single timer call

**Notably no `MSVFW32.dll` import.** Case File #1 dropped Video for Windows DrawDib (Jinx's cutscene path) — combined with the `ole32.dll` COM imports below and the disc-side raw `.avi` files, Gen 3's video path is **DirectShow** (COM filter graphs) rather than VfW DrawDib. The `quartz.dll` `IGraphBuilder`/`IMediaControl` interfaces are loaded indirectly through `CoCreateInstance`, so they don't appear in the static import table — but the pattern is unambiguous.

**No static `DSOUND.dll` import** (same dynamic-load pattern as Jinx — strings `DSOUND.DLL` + `DirectSoundCreate` present).

**Input** (~6 entries, USER32-only):

- `USER32.dll::GetAsyncKeyState` · `GetKeyState` · `LoadCursorA` · `SetCursor` · `GetCursorPos` · `GetCapture` · `SetCapture` · `ReleaseCapture` — same USER32-only input path as Jinx

**CRT / Standard Library**: **none** (CRT statically linked, same as Gen 1/2).

**XML parsing** (7 entries — **Gen 3 only**):

- `libexpat.dll::XML_Parse` · `XML_ParserCreate` · `XML_ParserFree` · `XML_SetElementHandler` · `XML_SetUserData` · `XML_GetCurrentByteCount` · `XML_GetCurrentByteIndex`

Confirms the [Cross-title runtime dependencies](#cross-title-runtime-dependencies) "XML parser: present" verdict at the static-import level. The Expat surface used is minimal — element-handler callbacks + byte-position tracking for error reporting — which is consistent with the `launch.xml`-class config files Case File #1 loads at startup.

**COM** (3 entries — **Gen 3 only**):

- `ole32.dll::CoCreateInstance` · `CoInitialize` · `CoUninitialize`

These three are the canonical COM-client initialization triad. Combined with the disc-side raw `.avi` files and the absence of any other AV runtime in the imports, this is strong indirect evidence of **DirectShow** filter-graph usage for video playback. The Gen 3 cutscene path is: `CoCreateInstance(CLSID_FilterGraph)` → build a filter graph for the AVI → `IMediaControl::Run()`. Exact `quartz.dll` symbols aren't in the static import table because COM is loosely typed; the verdict is "DirectShow, confirmed by elimination + disc-side `.avi` files."

**Other** (~50 entries):

- `USER32.dll` window/message-pump: `AdjustWindowRectEx` · `BeginPaint` · `ChangeDisplaySettingsA` · `ChildWindowFromPointEx` · `CreateWindowExA` · `DefWindowProcA` · `DestroyWindow` · `DispatchMessageA` · `EndPaint` · `EnumDisplaySettingsA` · `EnumWindows` · `FillRect` · `GetActiveWindow` · `GetClassInfoA` · `GetClientRect` · `GetDC` · `GetMenu` · `GetMessageTime` · `GetPropA` · `GetSystemMetrics` · `KillTimer` · `LoadIconA` · `LoadImageA` · `LoadStringA` · `MapWindowPoints` · `MessageBoxA` · `MsgWaitForMultipleObjects` · `PeekMessageA` · `PostMessageA` · `PostQuitMessage` · `RegisterClassExA` · `ReleaseDC` · `RemovePropA` · `ScreenToClient` · `ScrollDC` · `SetFocus` · `SetPropA` · `SetTimer` · `SetWindowLongA` · `SetWindowPos` · `SetWindowTextA` · `ShowWindow` · `TranslateAcceleratorA` · `TranslateMessage` · `UpdateWindow` · `WaitMessage`

**Notably new vs Gen 2:** `EnumDisplaySettingsA`/`ChangeDisplaySettingsA` (display-mode enumeration + change), `LoadImageA`/`LoadStringA` (PE resource loading), `ScrollDC` (scrollable surfaces).

**Notably absent vs Gen 1 still:** `ADVAPI32.dll` (no registry), `SHELL32.dll` (no shell), `IMM32.dll` (no IME), `WINSPOOL.DRV` (no printing), `DDRAW.dll`, `DSOUND.dll` (static), `DINPUT.dll`, `binkw32.dll`. The Gen 2 → Gen 3 transition kept Gen 2's reduced surface and added `libexpat.dll` + `ole32.dll`.

##### Conclusions (Case File #1 — imports)

- Path API encoding: **ANSI-only** — `CreateFileA` present, `CreateFileW` absent. Same finding across all three generations; the engine remains ANSI-bound at the Win32 file surface end-to-end.
- Bink runtime: **absent** (no `binkw32.dll` import; no Bink-related strings; no BK.* files on the Case File #1 disc per [tools/exes/README](../../tools/exes/README.md) §Case File #1)
- Smacker runtime: **absent**
- DirectDraw / Direct3D version: **DirectDraw dropped** (carried forward from Gen 2; rendering remains GDI DIB + new GDI vector primitives)
- DirectSound: **dynamic** (same `LoadLibraryA("DSOUND.DLL")` pattern as Jinx; strings present, no static import)
- DirectInput: **dropped** (carried forward from Gen 2)
- XML parser: **`libexpat.dll`, static** — 7 symbols (`XML_Parse`, `XML_ParserCreate`, `XML_ParserFree`, `XML_SetElementHandler`, `XML_SetUserData`, `XML_GetCurrentByteCount`, `XML_GetCurrentByteIndex`). Gen 3-only.
- COM: **`ole32.dll`, static** — `CoCreateInstance`, `CoInitialize`, `CoUninitialize`. Gen 3-only. Indirect evidence of DirectShow filter-graph cutscene playback (combined with disc-side raw `.avi` files).
- CRT: **static** (identical across Gen 1 / 2 / 3)
- Cross-title delta vs Showdown: **removed** the same DLL set Jinx removed (`DDRAW`, `DSOUND` static, `DINPUT`, `binkw32`, `ADVAPI32`, `SHELL32`, `IMM32`, `WINSPOOL`). **Removed** vs Jinx: `MSVFW32` (Video for Windows DrawDib dropped). **Added**: `libexpat.dll` (XML) and `ole32.dll` (COM). The Gen 2 → Gen 3 transition retains Gen 2's reduced DLL surface, drops VfW for COM, and adds XML configuration. Combined with the [strings finding](#case-file-1-gen-3) of MMFW resource-type labels (`MMFW Films`, etc.) carrying over from Jinx, the import-side evidence confirms **inheritance with extension**: MMFW from Jinx + new IBS-added XML + COM-video layers.

### Resource loading map

#### Showdown (Gen 1) — WP-001 Ghidra trace (2026-11-13)

Binary: `Scooby.exe`, SHA-256 `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478`.
Ghidra 12.1.4, default auto-analysis (107 s), project at
`C:\dev\scooby-engine\ghidra\scooby.gpr` (local, gitignored). The binary is
not packed: it is ordinary Visual C++ 6.0 code, and its `__FILE__` strings name the
source files, which anchor the subsystems.

Labels use the engine's debug channels (`resource`, `graphics`, `audio`,
`script`, `input`, fixed by WP-010 in `engines/scooby/detection.h`). The
address list is committed as
[`tools/ghidra-scripts/wp001-labels.txt`](../../tools/ghidra-scripts/wp001-labels.txt);
[`ApplyLabels.java`](../../tools/ghidra-scripts/ApplyLabels.java) re-applies
it to a fresh project (68 labels). Addresses are function entry points.
Four functions (`0x402130`, `0x402410`, `0x4091FF`, `0x43FB90`) are reached
only through vtables or pointer tables, so auto-analysis did not create
them. The label script does.

**Startup and file opening.** `resource_GameResource_ctor` (`0x4327D0`,
`GameResource.cpp`, logs `Creating Game Resource`) opens `TGIFILE.ART`, then
numbered volumes from the `%sTGIFILE%i.ART` pattern, then the
`%sTGIFILE.ART` path form if nothing opened yet. Each file that opens
becomes one art file (`resource_GameResource_AddArtFile`, `0x4336F0`, logs
`Loading art file '%s'`), up to 5. With none it fails `Failed to locate an
ART file`. It also creates a 16 MB `ResourceHeap`. Lookups search the art
files newest first, so a later volume overrides an earlier one by name.
Showdown ships one file.

**Art file** (`GameArtFile.cpp`; its read errors log `Failed to read from file
TGIFILE.ART`):

| Address | Label | What it does |
|---|---|---|
| `0x43A8B0` | `resource_ArtFile_ctor` | Reads sectors 0–63 (`0x20000` bytes), parses room count + descriptors, object count + descriptors, name count + 68-byte name records; sorts names for binary search |
| `0x43AED0` / `0x43ACE0` | `resource_ArtFile_ReadSectors(Alloc)` | Descriptor `d` → seek `(d >> 14) × 2048`, read `(d & 0x3FFF) × 2048` bytes in 512 KB chunks |
| `0x43B080` | `resource_ArtFile_LoadRoomBlock` | Name → id → room descriptor → read block; relocate layer, cel, `0xB0`, `0xB8` tables; RGB555 pass on 15-bit displays |
| `0x43B3D0` | `resource_ArtFile_LoadObjectResource` | Name → id → object descriptor → read into the resource heap; relocate tables, sequence polygons, frame cels, cel masks |
| `0x43B880` | `resource_ArtFile_LookupId` | Name → id |

**Resource manager** (`GameResource.cpp`):

| Address | Label | What it does |
|---|---|---|
| `0x432CC0` | `resource_GameResource_GetRoom` | Cached room block by `ROOM_*` name; `Failed to located room name %s` |
| `0x432E30` | `resource_GameResource_FreeRoom` | Frees the block and releases objects |
| `0x432F60` | `resource_GameResource_GetObject` | Reference-counted cache of object resources by `OBJ_*` name; evicts (`Resizing cache to load '%s'`) when the heap is full; `Failed to locate object name %s` |
| `0x433220` | `resource_GameResource_ReleaseObject` | Drops a reference; `Negative object reference count` |
| `0x433690` | `resource_GameResource_GetId` | Any name → id (used for ANIM names); `Failed to locate ID '%s'` |

These are the format facts that came out of the trace, each written up in
[tgifile-art.md](tgifile-art.md):
- The header is `u32` room descriptors, then `u32` object descriptors, then
  1,788 name records from `0x834`.
- A descriptor is `start_sector << 14 | sector_count`.
- Room block `i` is `ROOM` id `i`. The name table names all 69 rooms, so
  scene 18 is `ROOM_Artie` and scene 19 is `ROOM_Title_Screen`.
- A sequence step's frame ref is masked with `0x3FFFF`, and its polygon is
  the step's click region.
- An ANIM id is `0x3 | owner & 0xFF | sequence index`.
- Cel byte `0x10` marks a solid cel and byte `0x11` an RLE cel. Raw cels
  are little-endian.
- Mask A marks opaque RGB565 pixels and mask B translucent ARGB4444 pixels.

**Animation and drawing** (`graphics`, `input`):

| Address | Label | What it does |
|---|---|---|
| `0x430D60` | `graphics_Sprite_ctor` | Sprite node: holds an object resource (via `GetObject`), parent, depth; children kept sorted by depth |
| `0x430790` | `graphics_AnimSprite_ctor` | `(obj name, ANIM name, parent, depth, mode, ticks per step, start step)` |
| `0x430A00` | `graphics_AnimSprite_SetAnim` | ANIM name → id (`GetId`) → `sequences[id & 0x3FFFF]` of the held object |
| `0x430AA0` / `0x430890` | `graphics_AnimSprite_Start` / `_Tick` | Modes 1–5 (loop fwd/back, once fwd/back, jump to end); countdown of ticks per step. `_Tick` is sprite vtable slot `+8` |
| `0x431130` | (sprite tree tick) | Walks the tree front to back and calls each sprite's `+8` (tick) and `+0xC`, unless the subtree is marked done (`+0x30`). Each child's next sibling is read before the child is walked. WP-017, WP-055 |
| `0x431190` | (sprite tree sweep) | Right after `0x431130`, front to back: each sprite's `+0x10` (`0x4309C0`), or, marked done (`+0x30`), its deleting destructor. WP-055 |
| `0x435BC0` | (game tick loop) | `ticks = elapsed_ms × 36 / 1000 − done`. Runs each owed tick (tree tick, room update) and then draws once: **36 ticks per second**. Phantom: `0x4368F0`, byte-identical. WP-017 |
| `0x4309C0` | `graphics_AnimSprite_SelectFrame` | Current step's frame ref → frame record |
| `0x430D10`, `0x431350`, `0x4312A0` | `input_AnimSprite_HitTest`, `input_PolygonHitTest`, `input_PointInPolygon` | Step polygon: bounding box, then even-odd test |
| `0x4311F0` | (sprite hit walk, vtable `+0x14`) | Front to back in draw order; skips hidden (`+0x14`); calls `+0x1C` (type 1) or `+0x20` (type 2) by the sprite's `+4`. WP-018 |
| `0x431400` | (cel hit test, type 1) | Inside a cel: non-solid non-zero pixel, or mask B / mask A covers the point. WP-018 |
| `0x402410`, `0x4015F0`, `0x408450` | `input_ExitObject_GetRolloverCursor`, clickable and base rollover (vtable `+0x18`) | Exit: `rolloveranim=` (hint mode: `ANIM_CURSORSCRAPPY_ANIM`). Clickable: `ANIM_CURSOROPEN`. Base: none. WP-018 |
| `0x4313F0` | (sprite set hidden) | Writes `+0x14`; `0x4091FF` hides `OBJ_GHOST` with it. WP-018 |
| `0x438660` | `graphics_Renderer_RenderFrame` | Opaque pass front to back, then alpha regions back to front |
| `0x439C00` | `graphics_Renderer_DrawFrameRecord` | Intersect still-visible region with mask A (draw, subtract) and mask B (queue); `GameRenderer::AlphaRegion buffer` overflow error |
| `0x4398A0` | `graphics_Renderer_GetCelPixels` | The RLE decoder, with a 256-slot bitmap cache; `Out of space for the Bitmap Cache` |
| `0x439170` / `0x4394D0` | `graphics_BlendAlpha4444_565` / `_555` | ARGB4444 over RGB565 / RGB555 |
| `0x433AF0` | `graphics_ConvertCelTo555` | RGB565 → RGB555 over mask A, or of the solid colour |

The art is 16-bit. The engine checks the display's green mask (`0x3E0` =
RGB555) and, on a 555 display, converts each cel once at load, not per
frame.

**Rooms and `object.ini`** (`script`): see
[`object.ini` consumer](#objectini-consumer-wp-001) below, and
[the exit transition](#the-exit-transition-wp-020) for characters, scenes
and the walk-off.

**Sound** (`audio`, `GameSound.cpp` / `GameSoundFile.cpp`):

| Address | Label | What it does |
|---|---|---|
| `0x4344A0` | `audio_GameSound_ctor` | Opens `sfx.dat`, `voice.dat`, `music.dat`; `Failed to open <file>` |
| `0x43C5A0` | `audio_SoundFile_ctor` | Reads `u32 1` (else `Invalid sound data file`), `u32 count`, `u32 table offset`; loads `count` × 68-byte `(u32 offset, char[64] name)` records and sorts them by name |
| `0x434DC0` | `audio_GameSound_LookupId` | Name → sound id, searching `sfx.dat`, `voice.dat`, `music.dat` in that order; `Failed to locate id %s` |
| `0x434E30` / `0x43CF20` | `audio_GameSound_PreloadSection` | Preloads every `sfx.dat` sound whose name starts with a prefix |
| `0x446010` | `audio_SoundStream_Open` | Reads the clip's header sector, builds a PCM `WAVEFORMATEX` from it, keeps the lip-sync block, streams PCM from the next sector (WP-004) |
| `0x445550` | `audio_SoundStream_SetFormat` | Recreates the DirectSound buffer when the format changes; logs `Buffer format = %d channels, %d bits, %d` |
| `0x442FB0` | `audio_CopyLipSync` | Copies the clip's `(count, fps, bytes)` lip-sync block |

Sounds are named `<Section>.<Clip>` (for example `Global.Scrappy.Help.Wiggle`).
A numeric sound id is the file's base (`0x1000_0000` sfx, `0x2000_0000`
voice, `0x3000_0000` music) plus the clip's index in that file's
name-sorted table. On every room load `script_Game_LoadRoom` preloads the
`sfx.dat` clips of the `Global` section and of the room's own section. The
clips are uncompressed PCM; the full format is in
[audio-archives.md](audio-archives.md#clip-format) (WP-004).

For Case File #1 (Gen 3), the `MMFW` loader is the top research target of [WP-011](../work-packets/WP-011-casefile-decompdecomp.md#research-targets); its function map lands as its own subsection here once a finding reaches Observed.

### `object.ini` interpreter behavior

#### Gen 1 (Showdown)

Source binaries (committed to memory at the SHA-level, not the byte-level — files are not staged):

| File | Path | Size (bytes) | SHA-256 |
|---|---|---|---|
| `object.ini` | `tools/exes/showdown/object.ini` | 25,196 | `027928BB0219B9EADFEC1E066278D9BD3521B48B3E2D420DD7FEA69558A41C49` |
| `Scooby.eng` | `tools/exes/showdown/Scooby.eng` | 2,823 | `EE9BE93A024FF9B7F5EA1C2445B711FB7C13CEF61A079A4609EDF1201CBAB19B` |

The `Scooby.eng` row is **byte-identical between Showdown and Phantom** (same SHA-256, same 2,823-byte size) — a cross-Gen-1 finding pre-recorded in the [WP-008 pre-flight](../reference/pre-flight-WP-008-2026-06-03.md#repo--disc-state). Gen 1 ships a shared system-error string table across both titles. All `object.ini` behavior claims below are scoped to Showdown's binary; Phantom's `OBJECT.INI` is a different SHA / different size (28,788 bytes) and runs at its own WP if/when it's pulled in.

Catalog produced by [`tools/parse_ini.py`](../../tools/parse_ini.py) + [`tools/parse_eng.py`](../../tools/parse_eng.py); raw outputs (`tools/samples/asset-catalog.json`, `tools/samples/unmatched-assets.txt`) stay local-only per the WP-008 copyright posture. Findings below cite **counts, patterns, and structure** only.

##### Section structure (the surprise)

The file is **not** organized by entity type. It is a flat list of **215 `[OBJ_*]` sections**. There are zero top-level `[ROOM_*]`, `[CURSOR_*]`, `[INVENTORY_*]`, or `[GLOBAL]` sections. Entity-type discrimination happens through the `ID=` field on each `[OBJ_*]` section. Five values exist:

| `ID=` value | Count | Role |
|---|---|---|
| `exitobject` | 77 | Room-to-room navigation triggers. The constructor reads `destinationroom=`, `movie=`, `scene=` and a direction per gang member (`fred=` … `scooby=`); `character=` and `direction=` are never read ([exit transition](#the-exit-transition-wp-020)) |
| `clickableobject` | 103 | Interactive hotspots. Showdown's sections hold only `ID=`, sometimes `priority=` and `layer=`, and an empty `sequence=`; what a click does comes from the placed ANIM's name ([clickables](#clickables-wp-021)) |
| `inventoryobject` | 11 | Pickable items (carry `toolbaranim=`, `usecursor=`, `pickupanim/sfx/movie=`) |
| `requiresobject` | 13 | Hotspots gated by an inventory cursor (carry `requiredanim=`) |
| `simpleobject` | 11 | Pure visual hotspots (carry `sequence=`, `priority=`, `layer=`) |

Total: 215. Total v1-schema buckets after synthesis: **215 objects · 37 rooms · 23 cursors · 11 inventory** (`tools/samples/asset-catalog.json` `counts` block). The `rooms`/`cursors` buckets are derived during the post-parse cross-reference pass: rooms from the unique `destinationroom=` values, cursors from unique `ANIM_CURSOR*` references.

Section-attribute keys observed: `ID`, `character`, `daphne`, `destinationroom`, `direction`, `fred`, `layer`, `movie`, `pickupanim`, `pickupmovie`, `pickupsfx`, `priority`, `requiredanim`, `rolloveranim`, `scene`, `scooby`, `scrappyid`, `sequence`, `shaggy`, `toolbaranim`, `usecursor`, `velma`. No quoting, no multi-value lines, no backslash continuations. Sentinel values: `<none>` and `-1`.

##### Asset-reference format — the load-bearing finding

**The engine is name-driven.** Every asset reference in `object.ini` is a string in the WP-003 `TGIFILE.ART` name-table convention — `ROOM_*` for rooms, `ANIM_*` for animations, `OBJ_*` as the section-header convention itself. No numeric indices appear as asset references. The few numerics that do appear (`movie=-1`, `pickupmovie=-1`, `layer=1`, `priority=100`) are engine sentinels or render-order metadata, not asset-store lookups.

Parser mode selected per the [EC-004 Step 1 parser-mode-lock gate](../execution-checklists/EC-004-object-ini-catalog.md#parser-mode-lock-gate--do-not-skip): **MODE_A** — Direct TGIFILE name-table strings.

##### WP-003 name-table cross-check (Exit criterion #6)

The exit criterion specifies a four-number metric: total / matched / unmatched / rate. Computed against the [`TGIFILE.ART` pre-payload name table](tgifile-art.md#pre-payload-region--engine-name-table) regenerated at `tools/samples/wp003-name-table.txt` (811 records: 42 ROOM, 453 OBJ, 316 ANIM):

| Metric | Value |
|---|---|
| Total asset references in `object.ini` | **286** |
| Matched against WP-003 name table | **221** |
| Unmatched | **65** |
| Match rate | **77.27 %** |

77 % is below the pre-flight's "≥95 % → unambiguous name-driven evidence" threshold, but the 65 unmatched are not evidence of a non-name-driven mechanism — they are a coverage gap. Every unmatched reference is still a `ROOM_*`/`OBJ_*`/`ANIM_*` string in the WP-003 convention; the references just don't have corresponding `TGIFILE.ART` payloads. Bucketed:

| Unmatched bucket | Count | What it tells us |
|---|---|---|
| `ROOM_*` referenced by `destinationroom=` but absent from WP-003's 42-ROOM table | 21 | Includes `ROOM_Main_Menu` plus 20 `ROOM_P{NN}_<descriptive>` rooms. Either these rooms have no pre-rendered backgrounds (scripted/engine-rendered scenes — `ROOM_P30_Horseshoe_Corral`, `ROOM_P32_Pie_Noon` are minigames per the source-tree paths `\Scooby\GBH\Horseshoe_Corral_Room.cpp` and `\Scooby\GBH\Pie_Noon_Room.cpp` in the [Showdown strings findings](#showdown-gen-1)), or their backgrounds live in a separate archive. **Resolved 2026-11-13 (WP-002/WP-009): neither.** All 21 have ordinary scene-block backgrounds in `TGIFILE.ART`; they are only missing from the name table, which covers room ids 27–68. See [tgifile-art §Scene index = ROOM id](tgifile-art.md#scene-index--room-id-wp-009-2026-11-13). |
| `OBJ_*` section headers (hotspot / exit / overlay) with no `TGIFILE.ART` art payload | 25 | Names ending in `_HOTSPOT*`, `_TO_P*`, `_OVERLAY` — invisible click targets that don't need pre-rendered art. Corroborates the [Showdown strings finding](#showdown-gen-1) of `Failed to locate id %s` / `Failed to locate object name %s` as the engine's string-keyed lookup error path — not every `[OBJ_*]` ID is expected to resolve to an art entry. *(WP-001: still 25 against the full 1,788-record table. No room places any of them, so the placement path never reads these sections.)* |
| `ANIM_CURSOR<NAME>` and `ANIM_TOOLBAR<NAME>` for inventory items | 19 | All 11 `OBJ_INV_*` items reference a `ANIM_CURSOR<NAME>` + a `ANIM_TOOLBAR<NAME>`. **System** toolbar animations (`ANIM_TOOLBARCOMPUTER_IDLE`, `ANIM_TOOLBARSCRAPPY_IDLE`, `ANIM_TOOLBARMAGGLASS_IDLE`, etc.) **do** match the WP-003 table; the inventory-item variants do not. Either inventory animations live in a separate asset store, or `TGIFILE.ART` only carries the system toolbar animations and the inventory ones are generated/composited at runtime. New unknown for WP-001. **Resolved 2026-11-13 (WP-001): neither.** All 34 `ANIM_TOOLBAR*`/`ANIM_CURSOR*` references are in the full name table, as sequences of `OBJ_TOOLBAR` and `OBJ_CURSOR`. WP-003 had parsed only 811 of the 1,788 records. |

**Re-run against the full name table (WP-001, 2026-11-13):** 261 of 286
references resolve (91.26 %). The 25 that do not are the OBJ section headers
in the second row.

So the answer to WP-008's load-bearing question — **"is the engine name-driven (string references resolved through the WP-003 name table) or index-driven (numeric references that hit `TGIFILE.ART` entries directly)?"** — is **name-driven**, full stop. The 77 % match rate refines but does not refute this: `TGIFILE.ART` is one of multiple name-keyed asset stores. WP-002's `probe_art.py` can label decoded `TGIFILE.ART` entries directly via the WP-003 name table (per the [WP-008 §Notes deterministic naming rule](../work-packets/WP-008-object-ini-catalog.md#notes)); the 65 unmatched references just won't have a corresponding decoded entry to label.

##### Failure-handling synthetic-input checks

[`tools/parse_ini.py --self-test`](../../tools/parse_ini.py) runs four synthetic-input cases corresponding to the four policy lines in [WP-008 §Failure handling](../work-packets/WP-008-object-ini-catalog.md#failure-handling):

| Synthetic input | Expected behavior | Verified |
|---|---|---|
| Duplicate `[OBJ_A]` section | Hard-fail (`ParseError("duplicate section …")`) | ✅ |
| Unknown key `mysteryfield=42` inside known `[OBJ_X]` section | Preserved under `extra_fields` | ✅ |
| Malformed line `this line has no equals sign` inside known section | Hard-fail (`ParseError("unparseable line …")`) | ✅ |
| Unknown section type `[GLOBAL]` | Warned, recorded under `unknown_sections`; subsequent K/V lines silently skipped until next known section | ✅ |

##### `Scooby.eng` integration

`Scooby.eng` parses cleanly with [`tools/parse_eng.py`](../../tools/parse_eng.py): 10 messages, IDs `0001` and `0010`–`0018`, all system-error/init strings. All 5 spot-checked strings appear verbatim in `Scooby.exe`'s `strings-ansi.txt` (lines 1674–1683 per the [Showdown strings findings](#showdown-gen-1)), confirming the engine loads `Scooby.eng` at startup and renders these strings as-is for hardware-init / DirectX failure paths. The file documents its own format in its first ~25 lines (`^` comment marker, `[NNNN]` message-ID declaration, "line breaks taken literally" inside a message). Encoding: pure ASCII (0 high-bit bytes across all 2,823 bytes), CRLF line endings.

**No `object.ini` field is shaped like a `Scooby.eng` message ID.** The combined catalog records `object_ini_to_eng_resolutions: 0`. `Scooby.eng` is not a runtime localization table for `object.ini` strings; it is purely the boot/error-message table for `Scooby.exe`'s system-error paths (the `0010`–`0018` block matches the DirectDraw/DirectSound/CD-ROM failure surface called out in the [Known facts](#known-facts) section above and corroborated by the binary's import table). In-game dialogue text is not in `Scooby.eng`; it lives in `voice.dat` or in scripted dialogue elsewhere (a new unknown to scope as part of [WP-004](../work-packets/WP-004-audio-archive-decode.md)).

##### Data-driven vs implicit

`object.ini` carries **the asset-binding layer** end-to-end: every interactive object, every room exit, every cursor swap, every inventory item is named here. What it does *not* carry:

- **Puzzle state machines.** No conditional `requires=item_X then unlock_Y` structure exists — `requiresobject`'s only state is `requiredanim=<cursor>`, which gates the input event, not the puzzle outcome.
- **Room-to-room transition rules** beyond the immediate `destinationroom=`. No "if Scooby has the lantern, Tunnel_Dark becomes Tunnel_Lit" logic.
- **Background art bindings.** Rooms have no `bg=` field — the engine resolves the room background through a different lookup (most likely the canonical room name → `TGIFILE.ART` entry, which the WP-003 cross-check confirms is the bulk of the matched references on the room side).
- **The 5 `ID=` values are leaf categories**, not a state machine. Whatever ties a hotspot click to a puzzle outcome lives in the exe (or in a scripted dialogue file not yet parsed).

So the data-driven hypothesis stated under [Hypotheses (unverified)](#hypotheses-unverified) — *"Most gameplay rules are driven by `object.ini`, with the exe acting as interpreter"* — is **partially confirmed and importantly refined**: the *asset-binding and navigation graph* is data-driven, but the *puzzle/state logic* is not. WP-001 (Ghidra session) needs to find the function that consumes `object.ini` (likely the loader that triggers on the `Failed to load room.` error string per the [Showdown strings findings](#showdown-gen-1)) and the function that resolves cursor-key + click-target combinations to script invocations (probably keyed by the `scrappyid=Global.Scrappy.*` field, which suggests a script-table identifier resolved from a different file).

##### `object.ini` consumer (WP-001)

Traced in Ghidra on 2026-11-13. Function labels are listed in
[Resource loading map](#resource-loading-map).

**`object.ini` is never parsed into a table.** Every read is a live
`GetPrivateProfileStringA` call. `script_GetObjectIniString` (`0x40AB80`)
asks for a key in the section named after the object (`[OBJ_*]`), with a
default and a 1,000-byte buffer. It goes through the Win32 wrapper at
`0x43FB90`, the binary's only `GetPrivateProfileStringA` call site. The path
comes from `script_GetObjectIniPath` (`0x40AE40`, `%sobject.ini`, cached).
Keys are read when a placed object is built, by that object's constructor.
A ScummVM port can read the file with `Common::INIFile` and look keys up the
same way.

**Room load** (`script_Game_LoadRoom`, `0x435DC0`, `Game.cpp`):

1. Find the `Room` object for the `ROOM_*` name in the list the game builds
   at startup. Each room is a C++ object, and some have their own class
   (`Pie_Noon_Room.cpp`, `Horseshoe_Corral_Room.cpp`, `Options_Room.cpp`).
   If none matches: `Failed to load room.`
2. Load the room block (`resource_Room_LoadArt` → `GetRoom`) and create one
   sprite per used layer slot, at depth `-110000 + 10000 × slot`.
3. Offer each placement record to the room object's own handler first, a
   virtual call that matches OBJ names. The front-of-general-store room, for
   example, claims `OBJ_INV_CLOCK` and `OBJ_P10_FRONT_OF_GS_CLOCK_NOFACE`. If
   the room declines, `script_ScoobyGame_AddPlacement` (`0x4091FF`) builds
   the object:
   - `script_CreateObjectFromIniId` (`0x408F90`) reads `ID=` from the
     object's section, defaulting to `simpleobject`. It builds an
     `inventoryobject` (`0x4026B0`), `requiresobject` (`0x402D90`),
     `exitobject` (`0x401850`) or `clickableobject` (`0x408DC0`), each at the
     placement's `(x, y)`. This is the `ID=` switch WP-008 predicted.
   - `simpleobject` and unknown values fall through. Gang members
     (`OBJ_<character>`) become character actors (`0x4048E0`), whose depth
     follows y. `OBJ_GHOST` gets its own handling. Anything else becomes a
     plain animated sprite playing the placement's ANIM.
   - Each kind gets a parent layer and a depth, which together set the draw
     order. The table is in
     [tgifile-art §Rendering a room](tgifile-art.md#rendering-a-room-2026-11-13).
4. Preload the `Global` and room-section sounds (see
   [Resource loading map](#resource-loading-map), Sound), then log progress
   (`Been loading objects for 4 seconds`) during long loads.

**Correction to WP-008's "scripted-room render branch".** There is no branch
between "decode from `TGIFILE.ART`" and "render from code". Every room loads
its block from `TGIFILE.ART` (WP-009 had already shown that every room has a
background). Per-room code adds behaviour through the placement hook and
its own logic.

**`scrappyid` resolver.** `scrappyid=` values are **voice-clip names in
`Voice.dat`**, resolved by name through the sound manager. The exit-object
constructor stores the value. On a click (`script_ExitObject_OnClick`,
`0x402130`), if the cursor is `ANIM_CURSORSCRAPPY_ANIM` (Scrappy's hint
mode), it calls `audio_GameSound_LookupId(scrappyid)` and has the toolbar
Scrappy speak the clip. Otherwise it performs the exit: it writes the exit
to the save file's `Exits` section and hands it to the room
([the exit transition](#the-exit-transition-wp-020)). WP-018 read the
`Exits` write as a log channel. On rollover
(`input_ExitObject_GetRolloverCursor`, `0x402410`) the cursor becomes
`ANIM_CURSORSCRAPPY_ANIM` in hint mode when the object has a `scrappyid`,
and `rolloveranim=` otherwise. Inventory objects read `scrappyid` too.
Check against the data: 32 of the 35 distinct `scrappyid` values are clip
names in `Voice.dat`. The other three, `Global.Scrappy.Boot_Hill_1_to_Light_Tunnel`,
`…Boot_Hill_2_to_Boot_Hill_3` and `…Tunnel_Light_to_Boot_Hill_1`, have no
clip. `Voice.dat` has neighbours such as `…Boot_Hill_2_to_Light_Tunnel`, so
these are authoring mismatches. The lookup returns 0 for them and logs
`Failed to locate id %s`.

**Inventory animations.** `toolbaranim=` and `usecursor=` name sequences of
two ordinary objects: `OBJ_TOOLBAR` (id 295) and `OBJ_CURSOR` (id 20). All
34 such names are in the `TGIFILE.ART` name table. `script_Inventory_AddItem`
(`0x406DD0`, `Inventory.cpp`, `Out of Inventory space`) creates the toolbar
slot as an `OBJ_TOOLBAR` sprite playing the item's `toolbaranim`. The
cursor (`0x4089E0`) is an `OBJ_CURSOR` sprite, `ANIM_CURSORARROW` by
default. There is no separate inventory art store.

##### The exit transition (WP-020)

Traced 2026-11-14 for [WP-020](../work-packets/WP-020-exit-transition.md);
the fork plays it.

1. **The click** (`script_ExitObject_OnClick`, `0x402130`, the exit's
   vtable `+0x0C`, run each tick with a clicked flag at `+8`) writes the
   exit's name to the save file's `Exits` section. It then packs the exit
   (`0x404820`) and passes it to the current room object's vtable `+0x24`
   (`0x4024C0`).
2. **The handler.** The base room class (vtable `0x45E5FC`) uses
   `0x40C1E0`. It fades the cursor out (`0x435150`), blocks input (game
   `+0x24`), starts the scene (`0x40B400`) and parks the exit on the room.
   Showdown builds 47 room classes in its factory (`0x42E0E0`, game vtable
   `+0x14`). 31 keep `0x40C1E0`. The other 16 override it to gate exits
   on story state or swap in another scene, and each then calls
   `0x40C1E0`.
3. **The scene** (room vtable `+0x38`, `0x40C810`, every tick). Once the
   speaker is done (`0x406060`), it moves to line *n* + 1. The first
   character in the game's list (`+0x19C`: the room's character
   placements in order, then `OBJ_NARRATOR_A` from `0x409670`) that has a
   clip `<scene><n>_<NAME>` speaks it (`0x404DB0`). If none has one, the
   scene ends.
4. **The walk-off** (`0x40BE20`, from the room tick `0x40B490` once the
   scene is over). Each gang member's walk length is its sequence's step
   count (`0x404EA0`). The first strictly longest of Fred, Velma, Daphne,
   Shaggy and Scooby leads and starts at once. In the order Fred,
   Daphne, Velma, Shaggy, Scooby, each other member starts on the first
   tick when the leader's steps left, less 1, are no more than its own
   length. When the leader is on its last step, game vtable `+0x08`
   (`0x42DE10`) plays `movie=` if set and changes room.

**Exit keys.** The constructor (`0x401850`) reads `destinationroom=`,
`rolloveranim=`, `scrappyid=`, `movie=`, `scene=`, and one direction per
gang member: `fred=`, `daphne=`, `velma=`, `shaggy=`, `scooby=`. It never
reads `character=` or `direction=`. It clears `scene=` when the save's
`Exits` entry for the exit is `1`, `on`, `On`, `ON` or `TRUE`, so a scene
plays once.

**Characters** (`0x4048E0`). `OBJ_FRED_A` is named `FRED` with the set
`_A`. A state change (`0x405190`) builds an object and a sequence name,
switches the sprite's object when the name differs, and starts the
sequence:

| State | Object | Sequence | Mode | Then (`+0x78`) |
|---|---|---|---|---|
| 0, a direction such as `UR` | `OBJ_FRED_STARTWALK_UR_A` | `ANIM_FRED_STARTWALK_UR_A1` | once | 7: stay |
| 0, a direction such as `TURN_UR` | `OBJ_FRED_A` | `ANIM_FRED_ATURN_UR` | once | 7: stay |
| 6 idle | `OBJ_FRED_A` | `ANIM_FRED_AIDLE_MASTER` | loop | — |
| 8 talk | `OBJ_FRED_A` | `ANIM_FRED_ATALKS` | stopped | 6 when the clip ends |

The update (`0x404B70`, character vtable `+0x0C`) goes to the next state
when the sequence stops (states other than 6 and 8). While talking, it
shows step *shape* − 1 from the lip sync (`0x442DD0`). Starting a walk
(`0x405D90`) moves the character 50 in front for a direction starting
with `D`, and 50 behind for one starting with `U` (`0x430EE0`). States 2–5
and 9–17 (random idles, Velma's reactions, fright) are not traced here; 18 (`0x12`) is under [Clickables](#clickables-wp-021).

| Address | What it does |
|---|---|
| `0x40C1E0` | Default exit handler (room vtable `+0x24`) |
| `0x40B400` | Start a scene, if none is playing and no exit is parked |
| `0x40C810` | Scene player (room vtable `+0x38`) |
| `0x40B490` | Room tick (room vtable `+0x04`): scene, delayed scene, walk-off, snacks |
| `0x40BE20` | Walk-off |
| `0x4048E0` / `0x405190` / `0x404B70` | Character constructor, state change, update |
| `0x404DB0` / `0x406060` | Say a line; talking or a line waiting |
| `0x404EA0` / `0x405D90` | Walk length; start a walk |
| `0x40A800` | First character in the game's list with a name |
| `0x409670` | Add the narrator |
| `0x430EE0` | Move a sprite to a new depth among its siblings |
| `0x442DD0` | Lip-sync shape of a playing clip |
| `0x42DE10` | Game vtable `+0x08`: movie, then the next room |

##### Clickables (WP-021)

Traced 2026-11-14 for [WP-021](../work-packets/WP-021-clickable-actions.md),
in Showdown; Phantom has the same functions at the same addresses.

A clickable keeps a **state**, an ANIM name (`+0x60`), and a **sound**,
`SFX_` plus the state without `ANIM_` (`+0x68`). The state starts as the
placement's ANIM, or as the save file's `Clickables` entry for the object.
A click plays the state once (mode 3, 3 ticks per step) with its sound,
advances the state, and tells the room. When the sequence ends, the object
rests stopped on step 0 of its new state. The state advances by its last
character + 1, unless that gives a digit 1–9; a name the art file doesn't
have goes back to `A`. So `…HOTSPOT1A` → `…1B` → `…1C`, and a state with
no next letter stays. If the state is missing even then (Showdown's `…CHANDPUMA`),
`SetAnim` (`0x430A00`) stores id 0 and starts nothing; `SelectFrame`
(`0x4309C0`) selects no frame and the hit test (`0x430D10`) fails, so the
object is neither drawn nor clickable.

A click can call the **ghost** instead: if the clickable was built by the
default path, `rand() % 30 == 0`, and the room placed `OBJ_GHOST`. The
ghost is shown and plays once, `Ghost_Appears` plays, and every character
goes to state `0x12`: `ANIM_<NAME><set>STAY_SCARED` once, with
`Global.Scared.<NAME>`. When the ghost's sequence ends, the game loads
`ROOM_Ghost_Spot` ([the ghost spot](#the-ghost-spot-wp-056)).

| Address | What it does |
|---|---|
| `0x408DC0` | Build a clickable from a placement: `layer=` picks the parent, ghost flag set |
| `0x401000` / `0x401350` | Clickable constructor (reads `Clickables`) / destructor (writes it) |
| `0x401440` | Clickable update (vtable `+0x0C`): the click, the ghost's chance, the rest |
| `0x401650` | Advance the state; rebuild the sound name |
| `0x4015F0` | Rollover (vtable `+0x18`): `ANIM_CURSOROPEN` while the game cursor (`+0x238`) is the arrow (`+0xA0`); none while an item is in use ([WP-023](#the-inventory-and-the-toolbar-wp-023)) |
| `0x40A850` | Game vtable `+0x40`: pass a click to the room's vtable `+0x14` |
| `0x404440` | Default room `+0x14`: nothing. Story rooms override it (Boot Hill's graves: `0x40F250`) |
| `0x40A990` | The ghost appears |
| `0x409BCA` | When the ghost's sequence ends: go to `ROOM_Ghost_Spot` |
| `0x434CB0` / `0x434C70` | Stop / play a sound by id, in whichever file holds it |

##### The ghost spot (WP-056)

Traced 2026-11-16 for [WP-056](../work-packets/WP-056-ghost-spot.md), in
Showdown. `ROOM_Ghost_Spot`'s class (`0x4222E0`, vtable `0x45EEAC`) is the
same code in Phantom (`0x420350`, vtable `0x45EFD4`), compared byte for
byte apart from addresses. The game comes here once the ghost has scared
the gang.

- **Entry** (`0x422420`, after the base entry):
  - the background (layer 0, game `+0x58`) starts at x −1280;
  - input is held (game `+0x24`) and the cursor fades (`0x435150`, `0x12`);
  - the toolbar hides (`0x407CC0`);
  - the countdown (`+0xB8`) is 396 ticks, 11 seconds;
  - any music fade stops, with the music at full (`0x434F50`).
- **The placements** (`0x422490`):
  - `OBJ_TITLE_SCOOBY` and `OBJ_TITLE_DAPHNE` are sprites under the second
    layer (game `+0x5C`). No room has one, so they hang from the root.
    They sit at depths 1 and −1, looping, 3 ticks a step, as on the title.
  - The class's flags `+0xBC` and `+0xBD` would leave the five unbuilt.
    The constructor sets both and nothing clears them, so Shaggy, Velma and
    Fred go to the default path.
- **Each tick** (`0x422350`, after the base tick):
  1. A global toggle (`0x475F10`) counts 0, 1, 0, …, and lasts across
     visits.
  2. The countdown goes down.
  3. Until it reaches 0, and with no skip key, the background moves 6 pixels
     right on the ticks the toggle is 0, and back 1280 once past 0. It never
     gets there: 197 moves end at x −98.
  4. Then the game goes on (game vtable `+0x04`) to the room game vtable
     `+0x64` names.
- **The skip key** is input slot 5, while `0x475F00` is set, as on the
  title. It goes on at once and clears `0x475F00`.
- **Where it goes on to** (game vtable `+0x64`, called only from here):
  - Showdown's (`0x4303B0`) returns `ROOM_P01_Town_Center`.
  - Phantom's (`0x430DD0`) returns `ROOM_P27_Below_Balcony` when the room
    loaded (game `+0x04`'s name) is one of `ROOM_P29_Princess_Bedroom`,
    `ROOM_P28_Veranda`, `ROOM_P25_Wizards_Library`,
    `ROOM_P24_Wizards_Bedroom` or `ROOM_P26_Castle_Balcony`, and
    `ROOM_P04_Town` otherwise. From the ghost spot the room loaded is the
    ghost spot, so Phantom always goes on to its town.
  - So the gang never goes back to the room the ghost scared them in.
- **The rooms' size.** Showdown's ghost spot and title are 1920 × 480.
  Phantom's headers say 1280 × 480, but their backgrounds are 1920 wide,
  so the pan shows the same span on both.

| Address | What it does |
|---|---|
| `0x4222E0` | Constructor: the base room with `Ghost_Spot.Music`, the flags `+0xBC` and `+0xBD` set |
| `0x422350` (+0x04) | Tick: the toggle, the countdown, the pan, the skip key, then the town |
| `0x422420` (+0x0C) | Entry, after the base entry |
| `0x422490` (+0x18) | Placements: Scooby and Daphne |
| `0x4303B0` | Game vtable `+0x64` (Showdown): `ROOM_P01_Town_Center` |

##### Phantom's drawbridge and town (WP-057)

Traced 2026-11-16 for [WP-057](../work-packets/WP-057-drawbridge.md), in
Phantom's `Scooby.exe`, from an import of it in a scratch Ghidra project.
The addresses in this section are Phantom's.

**Phantom's functions against Showdown's.** Most of the engine is the same
code at other addresses. Matching each function's instruction sequence, with
addresses masked, pairs 980 of Phantom's 2756 functions with Showdown's. The
base room's functions keep their addresses, and so do the walk-ins this WP
calls (`0x405E60` `UR`, `0x405FE0` `U`, `0x406020` `D`, by their direction
strings). Among those that move:

| Phantom | Showdown | What it is |
|---|---|---|
| `0x4314C0` | `0x430790` | `graphics_AnimSprite_ctor` |
| `0x4317D0` | `0x430AA0` | Start (mode, ticks, start) |
| `0x431730` | `0x430A00` | Play an ANIM by name (vtable `+0x24`) |
| `0x435760` | `0x434A30` | The sound manager |
| `0x435AF0` / `0x4359A0` / `0x4359E0` / `0x435A10` | `0x434DC0` / `0x434C70` / `0x434CB0` / `0x434CE0` | Name → id; play, stop, is it over |
| `0x435B60` | `0x434E30` | `audio_GameSound_PreloadSection` |
| `0x437540` | `0x436810` | Restart the game's tick clock |

`0x406020` is the walk-in from `D`: the depth 50 in front, then state 1.

**A new game's story values** (game vtable `+0x4C`, `0x42E880`; the profile
writer `0x42FFE0` names them):
- `EwanPuzzle`, `MariaPuzzle`, `BradPuzzle`, `SkullPuzzle`, `SkullMovie`,
  `SkullPuzzleAttempted`, `CrestPuzzle`, `RedBallFound`, `BlueBallFound`,
  `BlueBallSeen`, `YellowBallFound`, `RedBallTaken`, `BlueBallTaken`,
  `YellowBallTaken`, `WellVisited`, `MazeEntered` and `PlaqueSeen` off;
- `Screaming` (`+0x288`) on;
- `Whodunit`: `MARIA`, `BRAD`, `EWAN`, `WIZARD` or `JESTER` (`rand() % 5`);
- `CrestSequence0`–`3`: 1–4, shuffled by five swaps of two `rand() & 3`
  places;
- `SkullCombo0`–`3`: `rand() & 3` each.

The Throne Room's entry clears `Screaming`.

**The drawbridge** (`ROOM_P01_Drawbridge`, `0x426730`, vtable `0x45F214`;
music `Drawbridge.Music`, opening `Drawbridge.100A_`). Four flags (P1–P4)
must wave their banners' colours (SP1–SP4).
- **Reset** (`0x426790`): the puzzle not done, the sign's first line next.
  Each banner's colour is `rand() & 3` + 1. Its flag starts one to three
  colours on: `((rand() % 3 + banner) & 3) + 1`.
- **Placements** (`0x426A80`), each under the first layer (game `+0x58`):
  - each flag at depth 0, a flag object (`0x427380`) set to its saved
    colour;
  - each banner at depth 0, waving `ANIM_P01_DRAWBRIDGE_SP<n>F<colour>`
    (mode 1, 4 ticks a step, from step `rand() & 3`);
  - the door at depth −1, stopped on its first step, or its last once the
    puzzle is done (mode 5);
  - the overlay at depth 0;
  - the way to the town (`OBJ_P01_TO_P04`) isn't built until the puzzle is
    done.
- **A flag** (`0x427380`, vtable `0x45F254`, 0x70 bytes): its colour
  `+0x5C`, next state `+0x60`, banner's colour `+0x64`, clickable `+0x68`,
  number `+0x6C`.
  - **States 1–4** (`0x427490`) wave that colour: `ANIM_P01_DRAWBRIDGE_P<n>F<colour>`,
    mode 1, 4 ticks a step, from step `rand() & 3`. A click goes on to 6, 8,
    10 or 12. On its banner's colour, `Drawbridge.Flag_Fanfare.1` plays,
    stopped and played again.
  - **States 5–12** play `Drawbridge.Flag_Raise` and move the pennant at 3
    ticks a step. The even states lower the colour (`…F<colour>_RISE`
    backwards, mode 4); the odd ones raise the next (mode 3). The cycle:
    6 → 7 → 2, 8 → 9 → 3, 10 → 11 → 4, 12 → 5 → 1.
  - **Moved off its banner's colour,** with Velma idle (state 6), she says
    `Drawbridge.100A_3_VELMA`.
  - **Its update** (`0x427430`, after its player): clicked with the arrow
    while clickable (game `+0x20` bit 4, its `+0x08`), or its sequence
    over, it goes on to its next state. A click during a move skips to the
    next.
  - **Its rollover** (`0x4273D0`) is `ANIM_CURSOROPEN` while clickable with
    the arrow.
- **Entry** (`0x426840`, after the base entry):
  - the `Drawbridge` sound section is preloaded (`0x435B60`);
  - `Drawbridge.Flag_Loop` plays;
  - one snack is needed (`+0x24`);
  - from the town, Velma walks in (`U`).
- **Each tick** (`0x4268D0`, after the base tick):
  - **The second fanfare over:** the door plays once (mode 3), `Drawbridge.Down`
    plays, the tick clock restarts (`0x437540`), and `Drawbridge.Enter_`
    starts, blocking.
  - **Until the puzzle is done,** each flag's colour is kept (`+0xEC`) while
    it matches its banner's. With all four right:
    - the puzzle is done (`+0xFC`);
    - the flags are no longer clickable;
    - the way to the town is built (`0x401850` under the first layer at
      depth −1, hit by its polygon);
    - `Drawbridge.Flag_Fanfare.2` plays, and its id is kept (`+0x104`).
- **The sign** (`0x427270`, room vtable `+0x14`, `OBJ_INV_1428_SIGN`):
  `Drawbridge.100X1_` and `…100X2_` in turn, not blocking.
- **Leaving** (`0x426EA0`): with no snack eaten here, `Drawbridge.110A_`
  plays, blocking, and the snack box flashes.
- **The profile** (`0x427010`, `0x427140`): `FlagState0`–`3` (`+0xEC`),
  `BannerState0`–`3` (`+0xDC`), then `PuzzleDone`.
- **The idle line** (`+0x28`, `0x4272D0`): Velma's
  `P01_Drawbridge.Idle.VELMA` becomes `Global.Idle.VELMA` once the puzzle is
  done.

**Who asks for the idle line** (room vtable `+0x28`). A character's state 4
(`0x405190`, Showdown) asks the room for its line, and plays it if the line
exists, else goes idle. The fork doesn't have state 4.

**The town** (`ROOM_P04_Town`, `0x4180F0`, vtable `0x45EC5C`; music
`Bagpipes.Music`, opening `Town.110_`). Entry (`0x418150`, after the base
entry):
- **Walk-ins:**
  - from the drawbridge, Velma (`D`);
  - from the souvenir shop, Shaggy (`UR`);
  - from the gardener's house, Fred (`UR`);
  - from the room of doors, Velma (`U`).
- **Screaming:** while `Screaming` is on, one of Jane's screams:
  `Town.Jane_Screaming1`, `…2`, `…3`, or `…5` for both 3 and 4
  (`rand() % 5`).

| Address | What it does |
|---|---|
| `0x426730` | Drawbridge constructor |
| `0x426790` (+0x08) | Reset: the colours |
| `0x426840` (+0x0C) | Entry |
| `0x4268D0` (+0x04) | Tick: the puzzle, the fanfare, the drawbridge down |
| `0x426A80` (+0x18) | Placements |
| `0x426EA0` (+0x24) | Leaving: a snack first |
| `0x427010` / `0x427140` (+0x1C / +0x20) | Save / load |
| `0x427270` (+0x14) | The sign |
| `0x4272D0` (+0x28) | Velma's idle line |
| `0x427380` / `0x427430` / `0x427490` | A flag: constructor, update, state |
| `0x4180F0` / `0x418150` (+0x0C) | Town: constructor, entry |
| `0x42E880` | Game vtable `+0x4C`: a new game's story values |

##### Phantom's souvenir shop (WP-058)

Traced 2026-11-16 for [WP-058](../work-packets/WP-058-souvenir-shop.md), in
Phantom's `Scooby.exe`. `ROOM_P03_Souvenir_Shop` (`0x416FE0`, vtable
`0x45EB9C`; music group 1, no opening of its own). The gang buys the empty
bottle with the tokens.

- **Reset** (`0x417040`): `IntroDone` (`+0xC2`) off.
- **Placements** (`0x417170`):
  - **The empty bottle**, once ever taken (`0x407060`): a sprite under the
    first layer at depth 0, showing `ANIM_INV_BOTTLE_EMPTYB`. Until then,
    a requires object (`0x408C80` with −1), kept (`+0xB8`); its
    `requiredanim=` is the tokens' cursor.
  - **Hotspot 1:** a clickable as the default path builds it (`0x408DC0`
    with 1, −1), kept (`+0xBC`).
- **Entry** (`0x4172D0`, after the base entry):
  - nothing bought or being fetched (`+0xC0`, `+0xC1`);
  - from the town, Fred walks in (`DL`, `0x405F20`);
  - without `Screaming`, the first time (`IntroDone` off), the opening
    becomes `Souvenir_Shop.1201_`, and `IntroDone` is set;
  - while `Screaming`, one of Jane's screams
    (`Souvenir_Shop.Jane_Screaming1`, `…2`, `…3`, or `…5` for 3 and 4,
    `rand() % 5`), and the opening becomes `Souvenir_Shop.330A1_`, on every
    visit;
  - either opening is unplayed (`+0x10`), and `+0x3C` (`0x40C7B0`) runs
    again, holding input for it.
- **Events** (`0x417060`):
  - **The bottle with the tokens:** they leave the toolbar (`0x406C80`),
    the cursor is the arrow again, and the bottle is bought (`+0xC0`).
  - **The bottle with the arrow:** `Souvenir_Shop.120A_`, blocking.
  - **The hotspot:** playing its B, `Souvenir_Shop.120X_`; else, if its
    next state is its A, `…120X1_`. Both blocking.
- **Each tick** (`0x417400`, after the base tick), while bought:
  1. Once Fred is idle, no scene plays, and the opening is done, he fetches
     the bottle:
     - `OBJ_FRED_P03_GET_WATER_BOTTLE`, state `0xD`, with
       `Souvenir_Shop.Fred_Takes_Bottle`;
     - the shelf shows `ANIM_INV_BOTTLE_EMPTYB`;
     - the tick clock restarts (`0x437540`).
  2. Input is held and the cursor hidden.
  3. Once Fred is idle again, the bottle goes in the toolbar
     (`ANIM_TOOLBARSPORTS_BOTTLE_EMPTY`, `ANIM_CURSORSPORTS_BOTTLE_EMPTY`)
     unless it was ever taken, and `Souvenir_Shop.120B_` plays, blocking.
- **Leaving** (`0x417580`, after the base leave): left while bought, the
  bottle goes in the toolbar.
- **The profile** (`0x4175D0`, `0x417610`): `IntroDone`.

| Address | What it does |
|---|---|
| `0x416FE0` | Constructor: music `1`, no opening |
| `0x417040` (+0x08) | Reset |
| `0x417060` (+0x14) | The bottle and the hotspot |
| `0x417170` (+0x18) | Placements |
| `0x4172D0` (+0x0C) | Entry: the walk-in, the opening, the scream |
| `0x417400` (+0x04) | Tick: Fred fetches the bottle |
| `0x417580` (+0x10) | Leave |
| `0x4175D0` / `0x417610` (+0x1C / +0x20) | Save / load |
| `0x405F20` | The walk-in from `DL` (Phantom, as Showdown) |

##### Movies (WP-022)

Traced 2026-11-14 for [WP-022](../work-packets/WP-022-movies.md); the
fork plays them through `Video::BinkDecoder`.

- **The request** (game vtable `+0x08`, `0x42DE10`) takes a movie id and
  the next room. An id outside 0–74 means no movie. Ids 0 and 25–28 are
  title movies, gated by `Scooby.ini`'s `GBHTitleMovies`. Any other id
  plays every time, and the game remembers it (`+0x10A` + id, saved as
  `MovieHistory%i`). The first viewing of a movie can't be skipped unless
  `Settings` / `AbortMovies` is on. Later viewings can. The flag is
  `+0x290`, read through game vtable `+0x3C`.
- **Playing** (`0x4362E0`, "Playing movie (%i)"). The main loop sees the
  id once the tick loop stops, and builds the name `%sBK.%.3d`: movie 32
  is `BK.032`. It tries the hard-disk folder, then the disc. It stops the
  sounds (`0x434BF0`), clears the screen, and opens the file in the Bink
  manager (`0x4422F0`: `BinkSetSoundSystem`, `BinkOpen`). The next room
  loads when the movie ends.
- **Skipping.** While a movie plays, input slot 5 or 4, or mouse button
  0 or 1, closes it (`0x4424F0`, `BinkClose`) if `+0x290` allows. The
  slots belong to the DirectInput layer, and which keys they hold was not
  traced.
- **The files.** Showdown has 42 movies (`BK.001`–`BK.042` without
  `BK.024`, and `BK.058`), and Phantom 56. All are Bink `BIKi`,
  640 × 480, at 8, 12 or 24 frames per second.

| Address | What it does |
|---|---|
| `0x42DE10` | Game vtable `+0x08`: next room, and the movie before it |
| `0x4362E0` | Main loop; plays a requested movie (`%sBK.%.3d`) |
| `0x42E0B0` | Game vtable `+0x3C`: whether the movie may be skipped (`+0x290`) |
| `0x442210` | Bink manager constructor ("Creating Bink Movie Manager") |
| `0x4422F0` / `0x4424F0` | Bink manager: open a movie / close it |

##### The inventory and the toolbar (WP-023)

Traced 2026-11-14 for [WP-023](../work-packets/WP-023-inventory.md), in
Showdown; the fork plays it on both discs.

**The game cursor.** Game `+0x238` holds the cursor's ANIM name, and game
`+0xA0` the arrow (`ANIM_CURSORARROW`, set by `0x4089E0`). An item in use
replaces the arrow. Every rollover (vtable `+0x18`) is empty while it does,
so the cursor shows the item. Exits act only for the arrow (`0x402130`).
Clickables act only while the cursor shows their own rollover
(`0x401440`).

**The toolbar** (`0x406620`, on every room entry, then parked by
`0x407D50`).
- **The van.** `OBJ_TOOLBAR` playing `ANIM_TOOLBARMYSTERY_MACHINE_IDLE` is
  a root sprite at depth 5000, so it is in front of the room. Its y is
  479 − its height.
- **What it tows.** The van's children, at depth 5000 and so in front of
  it, stand left of it by the sum of the widths so far, plus 20 pixels
  each. In order:
  - four slot sprites (`…FINGERPRINT_IDLE` if the slot has an item, else
    `…_DIM`), each with the item's `toolbaranim` as a child, at index 0–3;
  - the magnifying glass (7);
  - the snack box (8), with two digit sprites;
  - Scrappy (5);
  - quit (6).
- **Sizes.** The widths are `0x430C00`'s: the widest and the tallest cel
  over the sequence's steps, without cel offsets.
- **Blockers.** Two `OBJ_INVENTORY_BLOCK` hotspots sit at the root, at
  depths 5001 and 4999. The first is shown while the van drives, the second
  while the toolbar is open.
- **States** (`0x407AF0`):
  - parked at x 0;
  - open at 635 − the van's width;
  - driving in, between the two;
  - driving out, beyond either;
  - hidden (`0x407CC0`, x −(width + 30)), which many room classes set on
    entry ([Rooms that hide the toolbar](#rooms-that-hide-the-toolbar-wp-025)).

**Driving** (`0x407120`, the van's update after its click handler
`0x408060`).
- **Clicking the van** (`0x406A70` index 4) needs the arrow and the toolbar
  parked or open. Parked, it sets x to 15; open, to the open x + 15. Either
  way it plays `Global.Toolbar` and starts `…_ANIM`.
- **Each tick** the van then moves 15 pixels right:
  - Driving in, it stops at the open x.
  - Driving out, it goes off the right edge until x reaches the towed
    width + 640. It reappears at −(width + 1) and stops at 0.
- **Stopping.** A stop by clamping starts `…_STOP`, which plays into
  `…_IDLE`. A step landing exactly on the open x stops without it.

**Pick-up** (`inventoryobject`, `0x4026B0`; its update is `0x402B00`).
- **The click** needs the arrow. With `pickupmovie=-1`, the object waits
  (`+0x88`) and asks a parked toolbar to open (`0x407C00`).
  - When the toolbar is open, `0x406DD0` puts the item in the first free
    slot: `Out of Inventory space` past four.
  - The room's vtable `+0x14` then hears of it (game `+0x40`, 1), the
    object hides, and `pickupsfx` plays.
- **With a movie.** The click blocks input, asks for the movie, and reloads
  the same room (game vtable `+0x08`). It adds the item, and the toolbar
  opens after the room loads (game `+0x248`, `0x409510`).
- **The history.** Every item ever taken stays in a 32-entry history. The
  "has item" test (`0x407060`) reads the history, not the slots, and
  `0x402AD0` hides such an object when it is placed.
- **Rollover.** The open hand (`0x402D20`), except while waiting.

**Use** (`0x406A70` index 0–3, the slot's click).
- With the arrow, a slot that holds an item makes its `usecursor` the
  game cursor. The item sprite hides, and the slot plays `…_DIM`.
- Each tick (`0x407120`), an item whose cursor is no longer the game's
  shows again, and its slot plays `…_IDLE`.
- A `requiresobject` (`0x402D90`; click `0x402F20`) compares the cursor
  with its `requiredanim`, which is case-sensitive:
  - the same: the room hears (1);
  - else, the arrow: the room hears (0);
  - else: nothing.
  In the first two cases the cursor goes back to the arrow. Its rollover is
  the open hand.

**The wrong item** (`0x4098B0`, game vtable `+0x20`, after the room's
tick).
- **When.** An item has been the cursor for a tick (counter `0x475EFC`), a
  click comes, and nothing took the item.
- **Who speaks.** The gang flag (game `+0x240`, set on entry by
  `0x409510`) says whether Fred, Scooby, Shaggy or Velma is in the room.
  - With one of them there, `rand() % 4` picks Fred (`Global.WRONG_`),
    Shaggy (`…WRONGS_`), Velma (`…WRONGV_`) or Scooby (`…WRONGSC_`) until
    the one picked is there.
  - Without, the narrator says `…WRONGN_`.
  - The line plays as a scene that doesn't block input (`0x40B400`, last
    argument 0).
  - In a room with the echo flag (`+0x29`), Shaggy, Velma and Scooby say
    `…_Echo_` lines and Fred is never picked. Showdown never sets the flag.
    Phantom sets it in one place (`0x41529D`), beside its Mermaid's Cavern
    clip names: story code.
- **Then** the cursor goes back to the arrow, and the item to its slot.

**The other buttons.**
- **The magnifying glass** (7) goes to `ROOM_Suspect_Chooser`.
- **Quit** (6) plays `Sign_In.Quit_Button`, then goes to `ROOM_Main_Menu`.
- **The snack box** (`0x40D130`) and **Scrappy** (`0x40CD90`) have their own
  classes ([WP-024](#scrappys-hints-and-scooby-snacks-wp-024)). The snack box holds the snack count (`+0x30`, starting at 1;
  digits `0x40D3B0`). Its cursor, `ANIM_CURSORSNACK`, feeds Scooby or
  Shaggy. Scrappy's cursor, `ANIM_CURSORSCRAPPY`, makes an exit's
  `scrappyid` speak.

| Address | What it does |
|---|---|
| `0x4063C0` / `0x406530` | Inventory constructor / reset: no items, one snack |
| `0x406620` | Build the toolbar in the room |
| `0x406A70` | Toolbar click by index: a slot, the van, quit, the magnifying glass |
| `0x406C80` / `0x406DD0` | Take an item out of its slot / put one in the first free slot |
| `0x407060` | Has the item ever been taken (the history) |
| `0x407120` | Toolbar update: items back in their slots, the blockers, the drive |
| `0x407AF0` | Toolbar state |
| `0x407C00` / `0x407C60` / `0x407CC0` / `0x407D50` | Open if parked / close if open / hide / park |
| `0x407E50` / `0x408010` | Toolbar sprite constructor (index, `OBJ_TOOLBAR`, hit type 2) / the van |
| `0x407F30` / `0x407F80` | Toolbar sprite click / rollover (none over a slot) |
| `0x408060` | The van's update: its click, `…_STOP` into `…_IDLE`, then `0x407120` |
| `0x4026B0` / `0x402AD0` / `0x402B00` / `0x402D20` | Inventory object: constructor / hide if taken / update / rollover |
| `0x402D90` / `0x402F20` / `0x403010` | Requires object: constructor / click / rollover |
| `0x4098B0` | Game update (`+0x20`): the wrong-item line, the cursor sprite, the ghost's room |
| `0x409510` | Game `+0x18`, on entry: the arrow, the gang flag, open after a pick-up movie |
| `0x430C00` | A sprite's size: widest and tallest cel over its sequence |
| `0x40CD30` / `0x40D020` | Scrappy / the snack box |
| `0x407430` / `0x407780` | Read / write the save's `Inventory` section (`Slot%i`, `Anim%i`, `Cursor%i`, `History%i`, `Snacks`) |

##### Rooms that hide the toolbar (WP-025)

Traced 2026-11-14 for [WP-025](../work-packets/WP-025-toolbar-rooms.md).
The base room's entry (vtable `+0x0C`, `0x40B920`) builds the toolbar
parked. These rooms' classes then hide it (`0x407CC0`), or never call the
base entry, so it isn't built (¹).

The list comes from each title's room factory. Showdown's is `0x42E0E0`;
Phantom's room-name compares start at `0x42ED7F`. Each room name maps to
its class constructor, that constructor's vtable, and the calls in the
vtable's `+0x0C`. A room the factory doesn't name gets the base class
(`0x40B0F0`), which shows the toolbar. Names are compared exactly.

| Title | Rooms |
|---|---|
| Both | `Sign_In`, `Difficulty`, `Suspect_Chooser`¹, `Options`, `Main_Menu`, `Quit`¹, `Title_Screen`, `Big_Head`, `Credits`, `Cheat`¹, `Ghost_Spot` |
| Showdown | `P32_Pie_Noon`, `P06_Stage_Trapdoor`, `P24`–`P29_Chase_B1`–`B6`, `P30_Horseshoe_Corral`, `P33_Chase_C1`, `P37_Chase_C2`, `P38_Chase_C3`, `P39_Chase_C4`, `P34_Chase_C5`, `P35_Chase_C6`, `Artie`, the nine `Artifact_*`, `Sheriff`, `Gummy`, `Vault_Clock`, `Open_Safe`, `SB1`–`SB5`, `Test_Scroll` |
| Phantom | `P31_KST`¹, `P30_WFR`, `Ewan`, `Wizards_Skull`, `Brad_SPOOKY`, `Brad_SPOOKIER`, `Brad_SPOOKTACULAR`, `Maria`, `Hedge_Maze`, `Maze_Map`, `Garden_Plaque` |

That is 24 of Showdown's 47 classes (45 of its 69 rooms) and 20 of
Phantom's 51 (22 of 53). Adding an item (`0x406DD0`) or opening the toolbar
(`0x407C00`) clears the hidden flag. The van then comes in from the left
and parks.

##### Scrappy's hints and Scooby Snacks (WP-024)

Traced 2026-11-14 for [WP-024](../work-packets/WP-024-hints-and-snacks.md),
in Showdown; Phantom's executable carries the same names. The fork plays both.

**The speech lock** (game `+0x15C`, taken by `0x40A230`).
- **Who holds it.** A scene holds it from its first line to its end
  (`0x40C810`, `+0x84`). A character speaking outside a scene holds it too
  (`0x404DB0`, `+0xB4`), and so does Scrappy while he speaks.
- **What waits.** A scene waits while someone else holds it. The walk-off
  (`0x40B490` → `0x40BE20`) also waits for it.

**Scrappy's hint mode.**
- **Starting it.** A click on Scrappy (`0x40CD90`) with the arrow makes
  `ANIM_CURSORSCRAPPY` (game `+0x164`) the cursor. His rollover
  (`0x40CF50`) is that cursor in hint mode, and the open hand for the arrow.
- **Where a hint shows.** The cursor shows `ANIM_CURSORSCRAPPY_ANIM` over:
  - an exit with a `scrappyid` (`0x402410`);
  - a character that is a suspect already met (`0x4062E0`). The met list is
    game `+0x174`, five names, filled by story rooms through `0x40A8B0`.
    The character's hint is `Global.Scrappy.<NAME>`, looked up when it is
    built (`+0xA0`).
- **When it doesn't.** `0x4098B0` drops the hint while a scene plays, while
  the room's entry scene is due, or while the speech lock is held. The game
  cursor shows instead. When the hint does show, it plays
  `Global.Scrappy.Help.Wiggle`.
- **Clicking a hint** (`0x402130` for an exit, `0x404B70` for a character)
  hands the clip to Scrappy (`0x407DE0` → `0x40CEA0`). Then the arrow comes
  back.
  - Scrappy speaks only in hint mode, unless forced, and only if he gets the
    speech lock. He plays `ANIM_TOOLBARSCRAPPY_TALK` stopped, with its step
    from the clip's lip sync, as a character's (`0x40CD90`).
  - When the clip ends he stops on `…SCRAPPY_IDLE` and lets the lock go
    (`Scrappy::OnLogic - done talking`).
  - A `scrappyid` with no clip plays nothing, and the talk ends at once.
- **Clicking anything else** in hint mode puts the arrow back
  (`0x4098B0`). No WRONG line plays for Scrappy's cursor.

**Scooby Snacks.**
- **The count** is inventory `+0x30`. It starts at 1, and `0x407E00` caps
  it at 99. Only story rooms add snacks (`0x41CB50`, `0x41E1A0`).
- **The snack box** (`0x40D130`), clicked with the arrow:
  - With snacks, it plays `ANIM_TOOLBARSNACK_BOX_ANIM` once and
    `Global.Snack_Box`, and `ANIM_CURSORSNACK` becomes the cursor. The
    digits move off (x −5000) until the box's sequence stops.
  - With none, Scrappy is made to say `Global.940B_1_SCRAPPY` or
    `Global.940_1_SCRAPPY` (`rand() & 1`).
  - Clicked again with the snack, it takes the snack back. Its rollover
    (`0x40D410`) is the snack cursor while holding one, and the open hand
    for the arrow.
- **Feeding** (the room's update `0x40B490`, before `0x4098B0`). A click with
  the snack on Scooby or Shaggy puts the arrow back.
  - If the character isn't talking (`0x406060`), he plays
    `ANIM_<NAME><set>EAT_SNACK` once (`0x4061F0`, state `0xF`, then idle).
    One snack goes (`0x407E20`), and `Global.Scooby.Eat_Snack` plays.
  - **The snack-given line.** It is the room's own
    `<room without ROOM_>_Snack_Given`, if a character in the room has its
    line 1. Neither disc has one. Otherwise it is Fred's `Global.Snack_GivenA_`
    or `…B_`, or Velma's `…C_` (`rand() % 3`, Velma's only without Fred).
    It plays as a scene that leaves input on. The base room's threshold
    (`+0x24`) is 0, so every snack earns one.
  - Then an open toolbar drives off (`0x407C60`).
- **A snack anywhere else** gets the WRONG line, as any item does.

| Address | What it does |
|---|---|
| `0x40A230` | Take the speech lock (game `+0x15C`) |
| `0x40CD30` / `0x40CD90` / `0x40CF50` | Scrappy: constructor / update (hint mode, lip sync, done talking) / rollover |
| `0x407DE0` → `0x40CEA0` | Scrappy says a clip: hint mode or forced, with the speech lock |
| `0x402410` / `0x402130` | Exit rollover and click in hint mode |
| `0x4062E0` / `0x404B70` | Character rollover and click: a met suspect's hint |
| `0x40A8B0` / `0x40A930` | Add a met suspect / is one met |
| `0x40D020` / `0x40D130` / `0x40D410` | Snack box: constructor / click / rollover |
| `0x407E00` / `0x407E20` | One snack more (99 at most) / fewer |
| `0x4061F0` | A character plays `ANIM_<NAME><set><action>` once (state `0xF`) |
| `0x40B490` | The room's update: feeding Scooby or Shaggy, the snack-given line |

##### The player profile (WP-026)

Traced 2026-11-14 for [WP-026](../work-packets/WP-026-profile-saves.md),
in Showdown; the fork's saves hold this profile.

**No save slots.** The original keeps one profile per player, an INI file
that the Win32 profile API reads and writes. The Sign In room
(`0x425210`) picks the player and names the file `%s%s%s.sav` after the
player. Then it hands the file to the game (vtable `+0x58`, `0x42F640`,
read). The game writes the profile as it plays (vtable `+0x54`, `0x42F3A0`,
and the live writes below).

**Sections and keys.**

| Section | Keys | Written by | Read by |
|---|---|---|---|
| `Game` | `StartRoom`: the last room that isn't a menu (game `+0x24C`, set on entry by `0x40B920` through vtable `+0x48`; the menus are Main Menu, Options, Suspect Chooser, Sign In, Difficulty, Quit, Big Head) | `0x42F3A0` | `0x42F640`, which then goes there |
| `Game` | `Difficulty`, `Whodunit` (the villain, drawn by `0x42DBC0`), `FinalClue`, `CluesFound0`–`4`, `ClueOwners0`–`4`, `Suspect0`–`4` (met), `MovieHistory0`–`74` | `0x40A270` | `0x40A540` |
| `Game` | Story flags: `MoaningActive`, `SheriffPuzzle`, `SheriffWaiting`, `GummyPuzzle`, `TunnelLit`, `HotelHallDoor`, `VaultOpen`, `ArtifactType`, `GraveLocation`, `ClockHour`, `ClockMinute`, `StrongBox`, `ArtifactsBuilt`, `BagsRandomized`, `BagDown0`–`3`, `LeverAlias0`–`3` | `0x42F3A0` | `0x42F640` |
| *the room's name* | `OpeningPlayed`, `SnacksGiven`, then the room class's own keys (room vtable `+0x1C` / `+0x20`; the section is the room object's name, `+0x8`, [WP-029](#each-rooms-own-setup-wp-029)) | `0x40C410` | `0x40C470` |
| `Exits` | `<exit OBJ>=1`, when the exit is taken | `0x402130` | `0x401850` (taken for `1`, `on`, `On`, `ON`, `TRUE`) |
| `Clickables` | `<OBJ>=<state ANIM>` | `0x401350`, when the room is left | `0x401000` |
| `Inventory` | `Snacks`, `Slot0`–`3`, `Anim0`–`3`, `Cursor0`–`3`, `History0`–`31`; `Nothing` for an empty one | `0x407780` | `0x407430` (an empty `Snacks` is 1) |

**Value rules.**
- **Booleans** are written `Yes` or `No` (`0x40A070`). Only `Yes`, case
  and all, reads as true (`0x40A170`). A missing key leaves the value as
  it was.
- **Numbers** are written with `%i` (`0x409FD0`) and read with `atoi`
  (`0x40A0F0`).
- **`Scooby.ini`'s `Settings`** (`AbortMovies`, `WesternStartRoom`, …) are
  the machine's settings, not the player's (`0x409D70`).

##### Room classes and the front end (WP-027)

Traced 2026-11-14 for [WP-027](../work-packets/WP-027-front-end.md), in
Showdown. Phantom's classes are the same code with its own strings, compared
byte for byte at the title's entry and the level buttons: `FBFTitleMovies`
for `GBHTitleMovies`, and `ROOM_P01_Drawbridge` for `ROOM_P01_Town_Center`.

**Room classes.** The factory (game vtable `+0x14`, `0x42E0E0`) builds one
object per room name when the game starts, and keeps it. A class's state
therefore lasts across visits. The base class (vtable `0x45E5FC`) is the
default; a room class overrides some of these slots:

| Slot | Base | What it is |
|---|---|---|
| `+0x04` | `0x40B490` | Tick |
| `+0x08` | `0x40CD20` | Reset (when the game starts) |
| `+0x0C` | `0x40B920` | Entry, with the room left as the argument |
| `+0x14` | `0x404440` | An event from an object (game `+0x40`) |
| `+0x18` | `0x404450` | Claim a placement and build it (true) or leave it to the default path (false) |
| `+0x1C` / `+0x20` | `0x40C410` / `0x40C470` | Write / read its profile keys |
| `+0x24` | `0x40C1E0` | Leave by an exit |

The front end's classes:

| Room | Class (vtable) | Overrides |
|---|---|---|
| Title Screen | `0x428260` (`0x45F0A8`) | reset, tick, entry, placements |
| Main Menu | `0x4229C0` (`0x45EF2C`) | entry, placements |
| Difficulty | `0x422680` (`0x45EEEC`) | entry, placements |
| Quit | `0x423DB0` (`0x45EFB8`) | tick, entry |
| Sign In | `0x424770` (`0x45F024`) | tick, entry, `+0x10`, placements, exit ([WP-028](#sign-in-and-the-new-game-wp-028)) |
| Options | `0x4235D0` (`0x45EF6C`) | `+0x08`, entry, `+0x10`, placements ([WP-030](#options-and-credits-wp-030)) |
| Credits | `0x421740` (`0x45EE68`) | tick, `+0x08`, entry, `+0x10` ([WP-030](#options-and-credits-wp-030)) |

**The button** (`0x436C50`, vtable `0x45F4DC`).
- **What it is.** A sprite built stopped on step 0, with a sound (`+0x60`)
  and a second sound (`+0x64`), plus two callbacks into its room: click
  (`0x437070`, `+0x78`/`+0x7C`) and rollover (`0x437090`, `+0x80`/`+0x84`).
- **Its update** (vtable `+0x08`, `0x436D70`) sets the step to its state:
  0 at rest, 1 under the mouse, 2 pressed or clicked.
  - **Coming under the mouse** from rest plays its sound, unless that is
    the button sound already playing (`0x475F50`). A silent button stops
    that one. It also calls rollover(on).
  - **Leaving** state 1 calls rollover(off).
  - **A click** (mouse released over it) calls the click callback.
  - The second sound plays a second after the first ends; no front-end
    button has one.
- **Its hit test** (`0x436FC0`) is the step polygon if any step has one,
  else its cels.
- **Unresolved.** Every menu button of both titles has a polygon on step 0
  only. The hit test (`0x430D10`) reads the current step's, so taken
  literally a button would be lost the tick it shows step 1. The fork keeps
  step 0's shape for a button's other steps; what keeps the original
  steady isn't traced.

**The title** (`0x428380` entry, `0x4282E0` tick, `0x428480` placements).
- **Movies first.** The reset sets the step (`+0xBC`) to 2. Entry at steps
  1, 2 and 3 asks for title movie 26, 27 or 28 and this room again (game
  vtable `+0x08`), without the base entry, and moves to the next step. So
  a game starts with movies 27 and 28.
- **Then the title.** The base entry runs, and the background (layer 0)
  starts at x −640. Input stops, the cursor fades, and the toolbar hides.
  The countdown (`+0xB8`) is 324 ticks, and the machine's
  `GBHTitleMovies` becomes `Yes`.
- **The placements.** `OBJ_TITLE_SCOOBY`, `…DAPHNE` and `…LEGAL` are built
  at depths 1, −1 and 100.
- **Each tick** the layer moves 2 pixels right, and back 1280 once past 0,
  across the 1920-pixel room, until the countdown ends. Then the game goes
  to Sign In (game vtable `+0x04`); input slot 5 goes there at once.
- **Skipping the title movies.** `0x42DE10` treats ids 0 and 25–28 apart:
  they always play, and can be skipped only once `GBHTitleMovies` is
  `Yes`. They aren't kept in the movie history.

**The main menu** (`0x422A90` entry, `0x422B00` placements).
- **Entry** keeps the room it was opened from (`+0xBC`), unless that was
  Quit or Options, and hides the toolbar.
- **The buttons** are built from the placements `OBJ_MAIN_MENU_PLAY`,
  `…OPTIONS`, `…MYSTERY` and `…QUIT`, at the placement's x and y.
- **Where they go.** Each leaves by the room's exit (`+0x24`):

| Button | Click | Rollover |
|---|---|---|
| Play (`0x423120`) | Back to `+0xBC`; Sign In if that is the title | — |
| Options (`0x4233D0`) | `ROOM_Options` | `Main_Menu.Sound_NARRATOR` (`0x423580`) |
| New Mystery (`0x422FC0`) | `ROOM_Sign_In` | `Main_Menu.New_Mystery_NARRATOR` (`0x423530`) |
| Quit (`0x422E60`) | `ROOM_Quit` | — |

The menu is reached from a game through the toolbar's quit button
(`Sign_In.Quit_Button`, then `ROOM_Main_Menu`).

**The level select** (`0x4226E0` entry, `0x422700` placements).
- **The buttons** are `OBJ_DIFFICULTY_SPOOKY`, `…SPOOKIER` and
  `…SPOOKTAC`, built at (0, 0); the placement's x and y aren't read. Each
  sounds `Level_Select.SHAGGY.Spooky`, `…Spookier` or `…Spooktacular` under
  the mouse.
- **A click** (`0x422930`, `0x422960`, `0x422990`) sets the level (game
  `+0x160`: 0, 1, 2, the profile's `Difficulty`). It then asks for movie 1
  and `ROOM_P01_Town_Center`.

**The quit screen** (`0x423E90` entry, `0x424140` tick).
- **Entry** keeps the room it came from (`+0xB8`). It builds two buttons,
  `OBJ_QUIT_BUTTONS` playing `…YES` and `…NO`, the eyes (`…EYES`) and the
  mouth (`OBJ_QUIT_BIG_MOUTH`, `…TALKS`), all at (0, 0).
- **The eyes** look at Yes (step 2) or No (step 1) (`0x4240E0`,
  `0x424110`).
- **A click** stops input and has Scooby say `Quit_Screen.Yes_1_SCOOBY` or
  `…No_1_SCOOBY` (`0x424040`, `0x424090`), the mouth following the lip
  sync.
- **When the line ends,** Yes sets game `+0x110`, and the game quits. No
  leaves by the room's exit for the room it came from.

##### Sign In and the new game (WP-028)

Traced 2026-11-14 for [WP-028](../work-packets/WP-028-sign-in.md), in
Showdown. Phantom's Sign In is the same code: every function below
matches Showdown's byte for byte once addresses are masked (Phantom's
class sits `0x1F10` lower). The one difference is in the tick's delete
path, where Phantom builds a local object a few instructions earlier.
Phantom's story values (its game vtable `+0x4C`) aren't traced.

**Entry** (`0x425050`, after the base entry):
- hides the toolbar;
- sets the idle time (`+0xC4`) to 1080 ticks and the prompt countdown
  (`+0xCC`) to 90, with no leaving line (`+0xC8`) and typing off (`+0x100`);
- preloads the `Sign_In` sound section and reads the players (`0x426630`:
  `<save path>*.sav`, each name without `.sav`);
- builds four list rows at the list's top left, 30 pixels apart, and the
  typed field;
- clears the name (`+0x104`), with no row selected (`+0x10C`), none under
  the mouse (`+0x110`), and the scroll (`+0x114`) at 0.

**The placements** (`0x425560`):

| Placement | What it becomes |
|---|---|
| `OBJ_SIGN_IN_CHARACTERS` | A button, in a 560 × 125 box at (0, 350) that leaves it where it is placed. A click (`0x425B90`) types its ANIM's last letter, under 10 letters, with `Sign_In.Click`. |
| `OBJ_SIGN_IN_PLAY` / `…QUIT` | Buttons: Play (`0x425C70`), Quit (`0x425E00`). |
| `OBJ_SIGN_IN_U_ARROW` / `…D_ARROW` | Buttons that scroll the list (`0x4260D0`, `0x426070`). |
| `OBJ_SIGN_IN_R_ARROW` / `…L_ARROW` | Buttons for space (`0x425EF0`) and backspace (`0x425E70`). |
| `ANIM_SIGN_IN_TEXT_FIELDA` | Only its x and y: the typed field's top left. Not drawn. |
| `ANIM_SIGN_IN_TEXT_FIELDNAMES` | Only its x and y: the list's top left; the list is 240 × 120. Not drawn. |

The buttons are all placed at (0, 0); their cels carry where they show.
The characters' placement order is the art's: Showdown's and Phantom's
start with `M`, and put `0` where `M` would be.

**A text field** (`0x424340`, 140 bytes):
- **What it is.** A 240 × 30 box (`0x4370D0`) under the room's first layer
  (game `+0x58`), holding:
  - a highlight (`OBJ_SIGN_IN_TEXT_FIELD`, `ANIM_SIGN_IN_TEXT_FIELDHIGHLIGHT`,
    depth 0), shown on the selected row (`0x424660`);
  - ten letters (`OBJ_SIGN_IN_FONT`, `ANIM_SIGN_IN_FONTCHARSET`, depth 1).
  All start hidden.
- **The row under the mouse** switches its letters to
  `ANIM_SIGN_IN_FONTHIGHLIGHTED`, each on the step it shows (`0x424680`).
- **Laying out a line** (`0x4244F0`), which does nothing if the text is
  unchanged:
  - A letter's step is its value: `0`–`9` are steps 0–9, `A`–`Z` steps
    10–35.
  - Each letter goes at x = 1 + the widths before it, y = 1.
  - A letter's width is its first cel's (`0x430BA0`), plus 2.
  - A space is hidden and counts 10 + 2.
  - Then every letter moves right by (240 − the total) × 0.5, so the line
    is centred. The constants are floats at `0x45F01C`, `0x45E590`,
    `0x45EB18`, `0x45F020` and `0x45E7CC`.

**Each tick** (`0x424900`, after the base tick). Nothing is read while
leaving or while an exit runs.
- **Idle.** The idle time counts down. At 0 it goes back to 1080 and
  Shaggy says `Sign_In.SHAGGY.Type_Name_Idle`. If there are players and
  `rand()` is even, he says `…Saved_Game` instead.
- **The prompt.** The countdown reaches 0 at tick 90: Shaggy says
  `…Type_Name` (kept in `+0xD0`), the keys so far are dropped, and typing
  starts.
- **Typing** starts once the countdown is under 30. Until then the keys
  are dropped.
- **Keys** (`0x4264B0`), each resetting the idle time:
  - backspace;
  - space (as the right arrow);
  - `A`–`Z` and `0`–`9`, `a`–`z` made upper case, under 10 letters, with
    `Sign_In.Click`;
  - Enter plays.
- **The list** (`0x426280`). Inside the list's box, row r takes the mouse
  strictly between y + 30r and y + 30r + 30. Only rows holding a player
  count, at most four. A click selects the row; a second click on the
  selected row within 1000 ms plays.
- **A click in the typed field** (244 × 30) lets go of the selection.
- **The skip key** (input slot 5, while the flag `0x475F00` is set; entry
  clears it):
  - stops the prompt (or marks it said);
  - zeroes the countdown and starts typing;
  - stops a leaving line.
- **Leaving.** When the leaving line ends, the room leaves by its exit
  (`+0x24`): for `ROOM_Quit` after `Sign_In.Quit_Button`, else for
  `ROOM_Difficulty`.
- **A changed name** is laid out in the typed field, and the selection is
  let go.
- **The rows** (`0x426130`) show the players from the scroll.
  - **Up** shows if there are players and (the scroll isn't 0 or the
    selected row is past the first).
  - **Down** shows if there are players and (a selected row isn't the
    last player, or the scroll is under count − 4).
- **Deleting.** Input slot 18 (`0x12`) with a row selected deletes that
  player's `.sav`. The row is removed and the selection let go. The scroll
  goes back one if old count − 5 < scroll and the new count is over 3. The
  rows show it on the next tick.

**The buttons.**
- **Up** (`0x4260D0`) moves the selection up, or the scroll if the first
  row is selected or none is.
- **Down** (`0x426070`) moves the selection down, or the scroll if none is
  selected or the last row is.
- **Space** (`0x425EF0`) adds one under 10 letters, never first and never
  twice.
- **Backspace** (`0x425E70`).
- Each one plays `Sign_In.Click`.

**Play** (`0x425C70`) takes the selected row's player as the name.
- **With a name:** a trailing space goes. Shaggy says
  `Sign_In.SHAGGY.Click_Play` as the leaving line, every other sound
  stops, the selection goes, the cursor fades and input stops.
- **Without a name:** Shaggy says `…Type_Name_Idle`, unless he is saying
  it already.

**Quit** (`0x425E00`): `Sign_In.Quit_Button` as the leaving line, every
other sound stopped, the cursor faded and input stopped.

**The exit** (`0x425210`). Anywhere but `ROOM_Quit` starts a new game for
the name:
1. game vtable `+0x4C` (Showdown `0x42DBC0`, below);
2. every room object's reset (`0x435780`);
3. the inventory's reset (`+0x50`);
4. the player's name into game `+0x16C`.

A name in the list then reads that player's `%s%s%s.sav` (game `+0x58`),
which goes to its `StartRoom`. Otherwise the base exit goes to the level
select.

**The new game.** `0x4087B0`, shared by both titles:
- clears the level, the speech lock, the suspects, the clues and the
  player's name;
- seeds `rand()` from the clock;
- sets `StartRoom` to `ROOM_Difficulty`.

Showdown's `+0x4C` (`0x42DBC0`) then sets the story's values. Checked
against the writer `0x42F3A0` and the `0x40A270` it calls:

| Field | Value | Profile key |
|---|---|---|
| `+0x254`, `+0x26D` | 1 | `MoaningActive`, `SheriffWaiting` (`Yes`) |
| `+0x255`, `+0x26C`, `+0x274`, `+0x275`, `+0x276`, `+0x256` | 0 | `HotelHallDoor`, `SheriffPuzzle`, `GummyPuzzle`, `TunnelLit`, `VaultOpen`, `BagsRandomized` (`No`) |
| `+0x284`, `+0x288` | 12, 0 | `ClockHour`, `ClockMinute` |
| `+0x280` | `rand() % 9` | `GraveLocation` |
| `+0x28C` | `rand() & 3` | `StrongBox` |
| `+0x25C`–`+0x268` | `rand() & 3` each, drawn again until it differs from those before it | `LeverAlias0`–`3` |
| `+0x100` | `rand() % 5`: `ARTIE`, `ICDOUBLE`, `JENNY`, `SHERIFF`, `GUMMY` | `Whodunit` |
| `+0x278` | `rand() % 3`: `Bowl`, `Deer`, `Vase` | `ArtifactType` |
| `+0x10A`–`+0x154` | 0 | `MovieHistory0`–`74` |

Two more fields are zeroed with no key in the writer: the dword `+0x270`
and the byte `+0x290`.

| Address | What it does |
|---|---|
| `0x424340` / `0x4244F0` | Text field: constructor / lay out a line |
| `0x424660` / `0x424680` | Text field: highlight / font under the mouse |
| `0x424900` / `0x425050` | Sign In: tick / entry |
| `0x425560` / `0x425210` | Sign In: placements / exit |
| `0x4264B0` / `0x426280` / `0x426130` | Keys / the list under the mouse / the rows and arrows |
| `0x426630` | Read the players (`%s%s*.sav`) |
| `0x4087B0` / `0x42DBC0` | New game: shared / Showdown's story values |
| `0x435780` | Reset every room object (vtable `+0x08`) |

##### Options and Credits (WP-030)

Traced 2026-11-14 for [WP-030](../work-packets/WP-030-options-credits.md),
in Showdown, and compared with Phantom byte for byte once addresses are
masked.
- **Credits.** Every function matches, and so do its strings; only the
  factory's scenes differ.
- **Options** works the same way, with three differences:
  - its fields sit 4 bytes lower;
  - its markers are `OBJ_OPTIONS_SWORDS`;
  - its music callback replays a stored clip rather than music group 1.

**The base room's constructor** (`0x40B0F0`) takes the room's music
(`+0x68`) and its entry scene (`+0x78`). The factory gives most rooms the
music `"1"` (`0x46A108`). The base entry (`0x40B920`) reads the music:
- a number of 1 or more plays that music group (`0x40AA10`:
  `Group%i_%i.Music`, the second number counting up through the group's
  tracks);
- anything else stops the group and plays the clip of that name.

The fork has no room music yet.

**Options** (`0x4235D0`, vtable `0x45EF6C`): reset `0x423630`, entry
`0x423650`, `+0x10` `0x423A90`, placements `0x423B80`.
- **The markers.** The placements claim the six `OBJ_OPTIONS_NAIL`
  (Phantom `OBJ_OPTIONS_SWORDS`) for their places only; they aren't drawn.
  `0x423C20` keeps them sorted by y: a new marker goes before the first
  one lower down. More than six asserts.
- **Entry** asserts six markers and orders each pair left to right. The
  pairs from the top make three sliders (`0x4080F0`, class `0x45E568`):

| Pair | Slider | Volume (sound file) | Moving (`+0x64`) | Let go (`+0x5C`) |
|---|---|---|---|---|
| Top | `+0xF4` | Music (`+0x0C`) | `0x423CB0`: set it, replay the room's music | the same |
| Middle | `+0xF0` | Sound effects (`+0x04`) | — | `0x423CF0`: set it, play `Pie_Noon.Splat.0` (Phantom `Knights.Glass_Breaks.3`) |
| Bottom | `+0xF8` | Voices (`+0x08`) | — | `0x423D50`: set it, play `Level_Select.SHAGGY.Spooky` |

- **Leaving** (`+0x10`) clears the marker count and writes the three
  volumes to `Scooby.ini`'s `Scooby` section as `Sfx`, `Voice` and
  `Music` (`%f`).

**The slider** (`0x4080F0`, from `C:\Scooby\Common\OptionsSlider.cpp`).
- **What it is.** The marker's own OBJ and ANIM as a knob under the second
  layer (game `+0x5C`), at depth 5000, looping at 3 ticks a step.
- **Building it.** It keeps:
  - the ends (`+0x70`–`+0x7C`);
  - the unit normal (y1 − y2, x2 − x1) / length (`+0x80`, `+0x84`).
  A zero-length slider asserts.
- **Value and volume.** The knob sits at start + (end − start) × t, where
  t = (gain − 0.7) × 3.3333333. A volume is a gain from 0.7 to 1.0, set as
  0.7 + 0.3 t (`0x45EFB0`, `0x45EFB4`, `0x45EFAC`).
- **Its update** (vtable `+0x0C`, `0x4082A0`):
  - **Grabbing.** With the sprite's `+0x08` set (the fork reads it as the
    knob under the mouse) and the button just down (input `+0x20` flag 2),
    the knob is grabbed. The grab
    (`+0x88`, `+0x8C`) is the mouse less the knob.
  - **While dragging:**
    - p = mouse − grab, and d = (p − knob) · n;
    - q = p − d n is p brought onto the line;
    - t is q's distance along the line over the line's length, read along
      x or y, whichever the line spans more, and held in 0–1;
    - the knob moves to its new place, and the moving callback runs.
  - **Letting go.** With the button up (flag 1 clear), dragging stops and
    the let-go callback runs.

**Credits** (`0x421740`, vtable `0x45EE68`): reset `0x4218A0`, entry
`0x4218C0`, tick `0x421C60`, `+0x10` `0x422230`.
- **The factory** (Showdown `0x42EF50`, Phantom `0x42FE49`) gives it its
  entry scene and two more:

| | Entry scene (`+0x78`) | WB's (`+0xC8`) | TGI's (`+0xD0`) |
|---|---|---|---|
| Showdown | `Credits.1100A2_` | `Credits.1100D3_` | `Credits.1100D4_` |
| Phantom | `Credits.10002_` | `Credits.1000A_` | `Credits.1000B_` |

- **Entry.** The first two cases skip the base entry and ask for a movie
  and this room again (game vtable `+0x08`).
  - **From `ROOM_Big_Head`**, after the accusation, it asks for the
    villain's movie (`Whodunit`, game `+0x100`): `ARTIE` `0x21`, `GUMMY`
    `0x22`, `ICDOUBLE` `0x23`, `JENNY` `0x24`, `SHERIFF` `0x25`, `BRAD`
    `0x2D`, `JESTER` `0x2E`, `EWAN` `0x2F`, `MARIA` `0x30`, `WIZARD` `0x31`.
    Both titles' villains are in the one table; another name gets no movie.
  - **From `ROOM_Credits`** the first time (`+0xD8`, cleared by the reset)
    it asks for movie 58 (`0x3A`).
  - **Otherwise the roll:**
    - the base entry;
    - the cursor hidden, input held, the toolbar hidden;
    - the TLC logo (`OBJ_CREDITS_TLC`, `ANIM_CREDITS_TLCLOGO`) at (0, 0)
      under the second layer, depth 1;
    - its text (`…TLCTEXT`) under the first layer, depth 0, at y 480.
  - **The text** scrolls for its first cel's height + 350 (`+0xC0`; stage
    `+0xC4` = 0).
- **Each tick:**
  - the base tick, then the cursor hidden and input held;
  - **scrolling:** every third tick (a global counter, `0x475F0C`) the text
    rises 6 pixels (`0x45EEA8`), and so much less is left;
  - **skipping:** input slot 5 or 4 leaves for `ROOM_Sign_In`;
  - **the parts:** with nothing left to scroll, the stage moves on.
    - From 0: the TLC sprites go, `OBJ_CREDITS_WB` with its logo and text
      comes, and the WB's scene starts (`0x40B400`).
    - From 1: the TGI's, the same way.
    - From 2: leave for `ROOM_Sign_In`.
- **Starting a scene** (`0x40B400`) needs no scene playing and no exit
  under way. It turns the music down to 90% (`0x434F10`; see
  [the music's fade](#the-musics-fade-wp-032)).
- **Leaving** (`+0x10`). If the last movie played (game `+0x90`, set by
  the main loop `0x4362E0`) is 58, the game is over:
  - the player's `.sav` is deleted (`0x409740` names it);
  - a new game starts (game vtable `+0x4C`, `0x435780`, `+0x50`);
  - every movie in the history counts as seen (`0x40B0D0`).

| Address | What it does |
|---|---|
| `0x4080F0` / `0x4082A0` | Slider: constructor / update |
| `0x408260` / `0x408280` | Slider: set the let-go / moving callback |
| `0x423C20` | Options: add a marker, sorted by y |
| `0x40AA10` | Play music group n (`Group%i_%i.Music`), or stop it (−1) |
| `0x40B400` | Start a scene, fading the music |
| `0x40B0D0` | Every movie seen |
| `0x409740` | The player's `.sav` path |

##### Each room's own setup (WP-029)

Traced 2026-11-14 for [WP-029](../work-packets/WP-029-room-setup.md), in
Showdown. Phantom's base room functions (`0x40B0F0`, `0x40B920`,
`0x40B490`, `0x40AA10`, `0x40C7B0`, `0x40C6C0`, `0x40C410`, `0x40C470`) are
the same code at the same addresses; their decompiles differ only in
names.

**The base room's fields** (constructor `0x40B0F0`, which takes the room's
name, its music and its opening scene):

| Field | What it is |
|---|---|
| `+0x10` | The opening has played; saved as the room's `OpeningPlayed` |
| `+0x14` | The scene playing (`0x40B400`) |
| `+0x24` | Snacks Scooby needs here: 0, unless the class's reset sets it (Town Center: 1) |
| `+0x28` | The opening can be skipped: 1 |
| `+0x68` | The music, from the class constructor |
| `+0x74` | The opening's delay: 100 ticks, set again when the room is left (vtable `+0x10`, `0x40BB70`, from the room unload `0x435CD0`) |
| `+0x78` | The opening scene, from the class constructor |
| `+0x88` | Snacks eaten here; saved as the room's `SnacksGiven` |
| `+0xB4` | The idle timer: (`rand() % 30` + 25) × 36 ticks |

- **Music** (`0x40B920` → `0x40AA10`). `atoi` of the music: a group if 1
  or more, played as `Group<g>_<n>.Music`. Each time the group changes,
  `n` is the group's next variant (game `+0x1E4`), back to 1 when that clip
  doesn't exist. The game constructor (`0x408480`) starts with no group
  (`+0x20C` −1). The clip is stopped, then played (`0x434CB0`, `0x434C70`).
  Any other music, an empty string too, leaves no group and plays the clip
  by that name. So a room without a class keeps the music that was playing.
  While a group plays, the game's update (`0x409CB3`) picks its next variant
  once the clip is done (`0x434CE0`). Every music clip has the loop flag,
  so with looping clips this never fires.
- **The opening** (room vtable `+0x3C`, `0x40C7B0`, at the end of the base
  entry). If it isn't played and a character here (the game's list
  `+0x19C`) has its first line, `<scene>1_<NAME>` (`0x40C6C0`), the cursor
  fades and input is held. Otherwise the scene name is cleared, and it
  counts as played. The room's tick (`0x40B490`) starts it, blocking, when
  it isn't played, no exit is parked, no scene plays, and the delay has run
  out: on tick 100 after entry. Its end marks it played (`+0x80` points at
  `+0x10`). Input slot 5 marks it played and gives input back
  (`0x40B490`), and ends any scene playing (`0x40C810`). Entering any room
  from `ROOM_Ghost_Spot` sets its opening to one of
  `Global.Ghost_Spot_`, `…B_` or `…C_` (`rand() % 3`), not played.
- **Snacks** (`0x40B490`). Each snack Scooby or Shaggy eats here adds one
  to `+0x88`. The snack-given line, and the toolbar closing after it, wait
  until `+0x88` reaches `+0x24`.
- **Idle chatter** (room vtable `+0x34`). The scene player (`0x40C810`)
  starts the idle timer again on every tick a scene plays. When it runs
  out with no scene, and the opening played or there is none, the tick
  calls `+0x34` and starts it again. The base class does nothing.
- **The profile** (`0x40C410`, `0x40C470`). Every room writes its section:
  `OpeningPlayed` (`Yes`/`No`) and `SnacksGiven` (`%i`), then the class's own
  keys. Read back, only `Yes` is true. A missing key reads as empty, so `No`
  or 0 (`0x40C560`).

The rest of the room vtable:

| Slot | Base | What it is |
|---|---|---|
| `+0x10` | `0x40BB70` | Leave: the scene, the parked exit and the delay are reset; the speech lock is let go |
| `+0x28` | `0x40CB50` | An idle line's name: `<room>_Idle_<x>`, else `Global.Idle…`. A character's state 4 asks for it ([WP-057](#phantoms-drawbridge-and-town-wp-057)) |
| `+0x2C` | `0x404460` | On entry, with the room left: nothing |
| `+0x30` | `0x404810` | On entry, first: nothing |
| `+0x34` | `0x404470` | Idle chatter: nothing |
| `+0x38` | `0x40C810` | The scene player |
| `+0x3C` | `0x40C7B0` | The opening, at entry |

Each room's music and opening, from each class constructor's call to
`0x40B0F0`:

**Showdown** (rooms without a class: no music change, no opening):

| Music | Opening | Rooms |
|---|---|---|
| `Chase.Music` | — | P24_Chase_B1, P25_Chase_B2, P26_Chase_B3, P27_Chase_B4, P28_Chase_B5, P29_Chase_B6, P33_Chase_C1, P37_Chase_C2, P38_Chase_C3, P39_Chase_C4, P34_Chase_C5, P35_Chase_C6, P40_Chase_Start |
| `Ghost_Spot.Music` | — | Ghost_Spot |
| `Gummy.Music` | `Gummy_Puzzle.220B_` | Gummy |
| `Horseshoe_Corral.Music` | — | P30_Horseshoe_Corral |
| `Suspect.Music` | — | Suspect_Chooser |
| `Title_Screen.Music` | — | Title_Screen |
| `Track9.Music` | — | P25A_Chase_B2_Closeup, Artifact_Bowl_09, Artifact_Bowl_12, Artifact_Bowl_15, Artifact_Deer_09, Artifact_Deer_12, Artifact_Deer_15, Artifact_Vase_09, Artifact_Vase_12, Artifact_Vase_15 |
| group 1 | — | Sign_In, Difficulty, Options, Main_Menu, Quit, Test_Scroll |
| group 2 | `Street_3.320A_` | P11_Street3 |
| group 2 | `Town_Center.100B_` | P01_Town_Center |
| group 2 | — | P03_Street1, P04_Street2, P08_Post_Office, P09_Railroad_Station, P10_Front_Of_General_Store |
| group 3 | `Saloon.360A_` | P12_Saloon |
| group 3 | — | P17_Hotel_Hall, P20_Hotel_Room, Artie |
| group 4 | — | P05_Stage, P06_Stage_Trapdoor |
| group 5 | `Back_Alley.350A_` | P19_Back_Alley |
| group 5 | `Tunnel_Dark.170A_` | P14_Tunnel_Dark |
| group 5 | — | P02_Sheriffs_Office, P07_Jail, P13_Bank, P15_General_Store_Interior, P16_Bank_Vault, P18_Tunnel_Lit, Sheriff, Vault_Clock |
| group 6 | — | P21_Boot_Hill1, P22_Boot_Hill2, P23_Boot_Hill3, Cheat |
| — | — | P32_Pie_Noon, Big_Head, Open_Safe, SB1, SB2, SB3, SB4, SB5 |

**Phantom** (rooms without a class: no music change, no opening):

| Music | Opening | Rooms |
|---|---|---|
| `Bagpipes.Music` | `Town.110_` | P04_Town |
| `Drawbridge.Music` | `Drawbridge.100A_` | P01_Drawbridge |
| `Ghost_Spot.Music` | — | Ghost_Spot |
| `Hedge_Maze.Music` | — | Hedge_Maze |
| `Knights.Music` | `Knights_of_the_Snack_Table.350X_` | P31_KST |
| `Princess_Bedroom.Music` | `Princess_Bedroom.280_` | P29_Princess_Bedroom |
| `Princess_Bedroom.Music` | — | P26_Castle_Balcony, P27A_Below_Balcony_Door, P28_Veranda |
| `Skull_Puzzle.Music` | — | Wizards_Skull |
| `Title_Screen.Music` | — | Title_Screen |
| `Track6.Music` | — | Suspect_Chooser, Options, Main_Menu, Quit |
| group 1 | `Arena_1.170_` | P09_Arena1 |
| group 1 | `Arena_2.180A_` | P14_Arena2 |
| group 1 | `Ewan.NOTEBOOKPAGE_INTRO_` | Ewan |
| group 1 | `Fountain.250D_` | P44_Fountain_Closeup |
| group 1 | `Magic_Mirror_Room.310_` | P08_Magic_Mirror_Room |
| group 1 | `Mermaids_Cavern.340_` | P21_Mermaids_Cavern |
| group 1 | `Room_Of_Doors.140_` | P11_Room_Of_Doors |
| group 1 | `Royal_Gallery.210_` | P07_Royal_Gallery |
| group 1 | `Secret_Passage_2.380_` | P19_Secret_Passage2 |
| group 1 | `Storage_Room.370_` | P18_Storage |
| group 1 | `Throne_Room.160_` | P10_Throne_Room |
| group 1 | `Wizards_Library.300_` | P25_Wizards_Library |
| group 1 | — | P12_Dining_Room, P13_Kitchen, P03_Souvenir_Shop, P05_Gardeners_House, P06_Garden, P15_Secret_Passage1, P16_Treasury, P17_Kitchen_Storage, P20_Kings_Armory, P20_Kings_Armory_Slide, P22_Well_In_Maze, P23_Maze_Center, P24_Wizards_Bedroom, P27_Below_Balcony, Sign_In, Difficulty, Brad_SPOOKY, Brad_SPOOKIER, Brad_SPOOKTACULAR, Maria, Maze_Map |
| group 6 | — | Cheat |
| — | `Gardeners_House.130A_` | Garden_Plaque |
| — | — | P30_WFR, Big_Head |

The Credits room's opening comes from its factory call, which passes
`Credits.1100A2_` and `Credits.1100D3_`; which one the constructor keeps
isn't traced.

**Town Center** (`0x42CFD0`, vtable `0x45F300`). Its fields follow the base
room's:

| Address | Slot | What it does |
|---|---|---|
| `0x42D030` | `+0x08` reset | One snack needed (`+0x24`). The moan timer (`+0xBC`) at 36 ticks; the exit scene (`+0xB8`) and `SignClicked` (`+0xC0`) at 0 |
| `0x42D270` | `+0x0C` entry | From Street 1, Fred walks in `UL` (`0x405EE0`); from Street 2, Velma `U` (`0x405FE0`); from Street 3, Shaggy `UR` (`0x405E60`). Each keeps its depth (`+0x9C`), goes 50 behind it and starts state 1 |
| `0x42D800` | `+0x18` placements | `OBJ_INV_SIGN`: not built if the sign was ever taken (`0x407060`); else a requires object (`0x408C80`) under layer 1, depth 1 (`0x430EE0`), hidden until `SignClicked`. `OBJ_P01_TC_HOTSPOT4`: a clickable under layer 1, depth 1, hidden once `SignClicked`. `OBJ_P01_TC_HOTSPOT2`: a clickable under its `layer=`, kept |
| `0x42D7B0` | `+0x14` event | `OBJ_P01_TC_HOTSPOT4`: `SignClicked`. `OBJ_INV_SIGN`: take the sign (`+0xD0`) |
| `0x42D3F0` | `+0x04` tick | Below |
| `0x42D060` | `+0x24` exit | With no snack eaten here (`+0x88` = 0): `Town_Center.100A_`, `…100A2_`, `…100A3_` in turn, blocking, and the snack box flashes (`0x40D4D0`). Else the base exit |
| `0x42D340` | `+0x34` idle chatter | `rand() & 3`: `Town_Center.100B_`, `…100B2_`, `…100B3_` with `MoaningActive`, or `…1100D_`; none blocks |
| `0x42D970` / `0x42D9B0` | `+0x1C` / `+0x20` | The base keys, then `SignClicked` |

The tick, after the base tick:

- **Moans.** The timer counts down every tick. When it has run out and the
  story's `MoaningActive` (game `+0x254`, set by `0x42DBC0`, cleared by the
  Saloon at `0x414E95`) is on, `Town_Center.Moan.<1–4>` plays, and the next
  is 5–14 seconds away.
- **The hanging sign.** Clicked, it plays its state once. When that's over,
  the sign shows, the hanging sign hides, and `Town_Center.307_` plays,
  blocking.
- **The second hotspot.** On step 7 of `ANIM_P01_TC_HOTSPOT2C`, Daphne,
  Scooby and Shaggy go to state `0x11`: `ANIM_<NAME><set>SCARED` once, the
  line they were saying stopped, and `Global.Scared.<NAME>`. State `0x11`
  again in its first two steps changes nothing.
- **Scooby takes the sign.** From the sign's event until he has it, input
  is held and the cursor is faded. Once Scooby is idle (state 6), no scene
  plays and the opening is done: Scooby hides, and
  `OBJ_SCOOBY_P01_TAKES_SIGN` plays `ANIM_SCOOBY_P01_TAKES_SIGN1` once
  where he stands, under layer 1 at depth 10, with `Scooby.Takes.Sign`.
  The sign hides, and the game's idle time restarts (`0x436810`). When the
  sequence is over, Scooby shows. If the sign isn't in the history, it goes
  in the toolbar as `ANIM_TOOLBARPOP_SIGN` / `ANIM_CURSORPOP_SIGN`. Input
  comes back, and `Town_Center.360C_` plays, blocking.

**The snack box's flash** (`0x40D4D0` sets `+0x70`; the box's update
`0x40D130` acts on it). It waits for no scene and the opening done. With
the toolbar open, the box plays `ANIM_TOOLBARSNACK_BOX_ANIM` once with
`Global.Snack_Box`, the digits move away (x −5000.0) until it's over, and
the flag clears. Otherwise the toolbar opens first (`0x407C00`).

##### The accusation: suspects and clues, and Big Head (WP-031)

Traced 2026-11-14 for [WP-031](../work-packets/WP-031-accusation.md), in
Showdown, and compared with Phantom byte for byte once addresses are
masked.
- **Big Head** is the same code in both titles.
- **The suspects and clues** is the same code except where it names its
  suspects, movies and scenes: the entry, the accusation and the verdict.
  The tables below give both titles' values.

**The clue state on the game object**, written by `0x40A270` and read by
`0x40A540`:

| Field | Key | What it is |
|---|---|---|
| `+0x100` | `Whodunit` | The villain |
| `+0x108` | `FinalClue` | The final clue is found: the accusation is open |
| `+0xB0` + 8i | `CluesFound0`–`4` | Each clue found, by name (`ARTIE_MAP`, `EWAN_FILM`, …) |
| `+0xD8` + 8i | `ClueOwners0`–`4` | (not read by these rooms) |
| `+0x174` + 8i | `Suspect0`–`4` | The suspects met |
| `+0x109` | — | A clue just found, for Scrappy to name; not saved, cleared by `0x4087B0` |

**The suspects and clues** (`0x426910`, vtable `0x45F068`, music
`Suspect.Music`, Phantom `Track6.Music`): tick `0x4269E0`, entry `0x426B40`,
`+0x10` `0x4270E0`, placements `0x427100`, exit `0x426F30`.
- **Entry from the room itself** is the way back from the accusation's
  movie: the verdict, below.
- **Entry otherwise:**
  - the toolbar hides, and the room left (unless `ROOM_Quit`) is kept
    (`+0xE8`);
  - the idle time (`+0xF0`) is set to 360 ticks;
  - the introduction plays (`+0xF4`):
    `Suspect_and_Clues.Solve_Game` with the final clue, else
    `Suspect_and_Clues.SHAGGY_Introduce_Screen`.
- **The clues.** Each `CluesFound<i>` that isn't empty becomes:
  - a button (`OBJ_SUSPECT_CLUES`, `ANIM_SUSPECT_CLUES<name>`) at its
    slot's place: (90, 283), (184, 286), (286, 283), (372, 280),
    (473, 280);
  - a hotspot (`OBJ_SUSPECT_CLUES_HOTSPOT`,
    `ANIM_SUSPECT_CLUES_HOTSPOT<'1' + n>`) hit by its polygon.
  The hotspot is numbered by how many clues came before it, so a gap in
  the slots puts a clue and its hotspot apart. The final clue adds the
  hotspot `…HOTSPOT6`. Every clue, hotspot and picture has the rollover
  `ANIM_CURSOROPEN`.
- **The placements:**

| Placement | What it becomes |
|---|---|
| `OBJ_SUSPECT_PICTURES` `…PICTURES1`–`5` | A button at depth −1 for a met suspect (`0x40A930`); nothing otherwise |
| `OBJ_SUSPECT_CLUES`, `…CLUES_HOTSPOT` | Nothing: the entry builds its own |
| `OBJ_SUSPECT_CLUE_INFO` | The clue card, at the placement under the first layer, hidden |
| `OBJ_SUSPECT_FINAL_CLUE` | A button with the final clue; nothing otherwise |
| An ANIM ending `EXITICON` | Nothing, with the final clue: there's no way back |

| Picture | Showdown | Scrappy (`Suspect_and_Clues.SCRAPPY_<…>_Info`) | Phantom | Scrappy |
|---|---|---|---|---|
| 1 | `SHERIFF` | `Chuck` | `EWAN` | `Ewan` |
| 2 | `JENNY` | `Jenny` | `BRAD` | `Brad` |
| 3 | `ICDOUBLE` | `ICDouble` | `MARIA` | `Maria` |
| 4 | `ARTIE` | `Artie` | `WIZARD` | `Wizard` |
| 5 | `GUMMY` | `Gummy` | `JESTER` | `Chester` |

- **Each tick:**
  - **The new clue.** While a new clue is pending, input is held and the
    cursor hidden. Once the introduction is over, Scrappy says
    `Global.Scrappy.Clue.<CluesFound[count − 1]>`; the flag clears and
    input comes back.
  - **Idle.** Without the final clue, the line
    `Suspect_and_Clues.SHAGGY.Click_On_Back_Button` plays on the 361st
    tick, then every 361 ticks.
  - **The card** (`0x427AA0`). With a clue or its hotspot under the mouse,
    the card shows `ANIM_SUSPECT_CLUE_INFO<name>`; with the final clue or
    its hotspot, `…INFOFINAL_CLUE`. Otherwise it is hidden.
- **A clue clicked** (`0x4278C0`). Every sound stops, the idle time resets,
  and Scrappy says `Global.Scrappy.Clue.<name>`. The final clue's name is
  `FINAL_CLUE`; a hotspot's is its clue's.
- **A picture clicked** (`0x427600`). Every sound stops.
  - Before the final clue, Scrappy describes the suspect.
  - With it, the suspect is accused (`0x427C70`): whether they're the
    villain goes in `+0xFC`. The true villain's movie then plays, and this
    room comes again.

| Villain | Showdown movie | Reveal | Villain | Phantom movie | Reveal |
|---|---|---|---|---|---|
| `SHERIFF` | 13 | `…B_` | `EWAN` | 15 | `…A_` |
| `JENNY` | 12 | `…C_` | `BRAD` | 13 | `…B_` |
| `ICDOUBLE` | 11 | `…E_` | `MARIA` | 16 | `…C_` |
| `ARTIE` | 9 | `…A_` | `WIZARD` | 17 | `…E_` |
| `GUMMY` | 10 | `…D_` | `JESTER` | 14 | `…D_` |

- **The verdict** (`0x427DE0`). The scene is `Street_1.720<letter>_` for
  the right suspect and `…730<letter>_` for a wrong one (Phantom
  `Treasury.`). It goes to Big Head with:
  - `BIG_HEAD_BG_P03` (Phantom `…P16`);
  - then `ROOM_Credits`.

  `Scooby.ini`'s `Scooby` section gets `GBH=Yes` (Phantom `FBF=Yes`). Only
  this function references that key.
- **The exit** (`+0x24`) goes back to the room kept on entry. Leaving
  (`+0x10`) stops every sound.

**Big Head** (`0x403070`, vtable `0x45E44C`): entry `0x403180`, tick
`0x403C70`, `+0x10` `0x403920`, opening `+0x30` `0x4038F0`, scene step
`+0x38` `0x403940`.
- **The game sets three fields**, then asks for `ROOM_Big_Head` (game vtable
  `+0x04`):
  - the scene (game `+0x220`);
  - the background (`+0x228`);
  - the room after (`+0x230`).
- **Who uses it.**
  - The verdict, above.
  - Showdown's chase close-up (`0x412020`: `Chase_Branch_2.260A_` on
    `BIG_HEAD_BG_P25A`).
  - Phantom's rooms with the backgrounds `P10`, `P11`, `P13`, `P14`,
    `P44P22`, `PLAQUE` and `SKULLS`.
- **The opening** (`+0x30`) is the scene, marked unplayed.
- **Entry:**
  - keeps the room left (`+0xCC`);
  - loads `OBJ_BIG_HEAD_CLUES_<Whodunit>`;
  - takes the first line's speaker: the first of the 20 names (`0x46A720`)
    with a clip `<scene>1_<NAME>`;
  - builds the speaker's mouth (`OBJ_<NAME>_BIG_MOUTH`, `…_BIG_MOUTHTALKS`)
    and body (`OBJ_<NAME>_BIG_BODY`, `…_BIG_BODYA`), and a partner's pair,
    all under the first layer, stopped;
  - hides the toolbar.
- **The partner** (`0x403F90`):
  - Shaggy's is Scooby, in front (depth 1);
  - Scooby's is Shaggy, behind (−1);
  - Fred's is Daphne (1);
  - Daphne's is Fred (−1);
  - nobody else has one.
- **The background** (`0x404270`) is the first layer itself, set to
  `OBJ_<bg>` with `ANIM_<bg><NAME>`, or `ANIM_<bg>DEFAULT` if the art has
  none for that name.
- **The scene step** (`+0x38`) replaces the base scene player. With no line
  playing, the next line is `%s%i_%s`: the scene, the line number and the
  first name with that clip. That name's head comes up and the line plays.
  With no such clip the opening counts as played, and the next tick leaves
  for the room after.
- **Each tick:** the lip sync of the line playing (`0x434D40` → `0x442DD0`)
  gives two values.
  - **The low nibble** moves the mouth to step *shape* − 1.
  - **The high nibble, if 0,** shows the heads and the speaker's background.
  - **Otherwise** it hides the heads and puts the villain's clue picture on
    the first layer: `OBJ_BIG_HEAD_CLUES_<Whodunit>` with
    `ANIM_BIG_HEAD_CLUES_<Whodunit><n>`. Showdown has pictures 7 and 8 for
    each villain: the `0x70` and `0x80` bits
    [audio-archives](audio-archives.md#clip-format) noted.

| Address | What it does |
|---|---|
| `0x427C70` / `0x427DE0` | Accuse / the verdict |
| `0x4278C0` / `0x427600` / `0x427AA0` | Clue clicked / picture clicked / the clue card |
| `0x403F90` / `0x404270` | Big Head: the partner / the background |
| `0x40A930` | Is a suspect met |
| `0x404480` | The room after Big Head (game `+0x230`) |

##### The music's fade (WP-032)

Traced 2026-11-14 for [WP-032](../work-packets/WP-032-music-fade.md), in
Showdown. The sound manager (`0x475F48`, returned by `0x434A30`) keeps one
fade for the music file:

| Field | What it is |
|---|---|
| `+0x10` / `+0x11` | Fading down / up |
| `+0x14` | The target, in percent |
| `+0x18` | The interval, in game ticks |
| `+0x1C` | The countdown to the next step |
| Music file `+0x18` | The music's percent now (100 at start) |

| Address | What it does |
|---|---|
| `0x434F10` (target, interval) | Fade down: the down flag on, the up flag off, the countdown at the interval |
| `0x434F30` (target, interval) | Fade up, the same way |
| `0x434F50` | Stop either fade, and set every music clip to 100% (`0x43C940` with `0xFFFFFFF`) |
| `0x434C00` | Once a game tick (`0x435BC0`, after the room's tick): the countdown goes down by one; at 0 it starts again from the interval, and a fade moves the percent one step |
| `0x43C940` (clip, percent) | Store the music file's percent, and set each playing clip's volume to percent × the file's gain (`+0x14`, the Options slider's 0.7–1.0) |
| `0x43CC20` | Play a clip; its volume goes through the same driver call (`+0x18`). That it is the same product is an inference: Ghidra hides the `__ftol` operands there. Each clip has a buffer of its own (`+0x10` of its 0x14-byte entry). By the file's type (`+0x10`, set by `0x43C5A0`): `Sfx.dat` (0) keeps a clip's buffer and starts it again, and other clips play on; `Voice.dat` (1) makes a stream each time; `Music.dat` (2) plays nothing if the clip has a buffer, and frees every other clip's not kept (`+0x0C`) first. WP-055. A `Voice.dat` stream goes in the clip's own entry and frees no other clip's, so voice lines overlap, up to the driver's four streams ([voice lines overlap](#voice-lines-overlap-2026-11-16)) |

**A step** (`0x434C00`):
- **Fading up,** percent + 1. Reaching the target stops the fade and sets
  the target exactly.
- **Fading down,** percent − 1. Reaching the target, or passing it, stops
  the fade at the target.

A fade that starts at its target stops on its first step, with no change.

**Who fades the music:**

| Caller | When | Fade |
|---|---|---|
| `0x40B400` | A scene starts (openings, exits' scenes, the rooms' own) | Down to 90, a step every 2 ticks: 100 → 90 in 20 ticks |
| `0x40C810` (`0x40CA85`) | A scene ends, played out or skipped | Up to 100, a step every 4 ticks: 90 → 100 in 40 ticks |
| `0x435DC0` (`0x4360B0`) | A room has loaded, after its entry | Up to 100, a step every 3 ticks |
| `0x428380` (`0x42846E`) | The title shows | `0x434F50`: straight to 100 |
| `0x41936E` | A story room near P14 | `0x434F50` (not modelled yet) |
| `0x422478` | The ghost spot's entry ([WP-056](#the-ghost-spot-wp-056)) | `0x434F50`: straight to 100 |

**Big Head's own player** (`0x403940`) never reaches `0x40C810`'s end. A
Big Head scene therefore turns the music down when it starts, and it stays
down until the next room loads.

**The opening's delay applies to Big Head and Credits too.** Both rooms'
first scenes are their openings (`+0x78`). The base room starts an opening
100 ticks after entry (`+0x74`), holding input meanwhile (`0x40C7B0`), and
only then does `0x40B400` turn the music down. Credits' opening is the
factory's first scene: `Credits.1100A2_` (Phantom `Credits.10002_`).

##### Voice lines overlap (2026-11-16)

Traced 2026-11-16 in Showdown, for the gap WP-055 left. `0x43CC20` reaches
the sound driver through the base factory (`0x433C70`, vtable `0x45F570`):
its `+0x1C` (`0x43C020`) builds the driver once (`0x442510`, vtable
`0x45F744`).

| Address | What it does |
|---|---|
| `0x4428A0` (driver `+0x04`) | Create a stream in the first of the driver's four stream slots (`+0x3C`, 0x108 bytes each) not in use (slot `+0x68` bit 31). `0x445780` opens it and counts the slot's generation (`+0x104`, 1 to 512). The handle is `0x80000000` \| (generation × 4 + slot + 1). With all four in use the handle is 0, and `0x43CC20` logs `Failed to create stream` |
| `0x442910` (`+0x08`) | Create an effect buffer, the first free of 128 (`+0x40`, 0x1C bytes each); the handle is its index + 1 |
| `0x442970` / `0x442A60` (`+0x0C` / `+0x14`) | Free / stop a handle. A stream is destroyed either way, and only if the handle's generation is the slot's |
| `0x442C50` (`+0x20`) | Is a handle playing; a stream handle of an older generation is not |
| `0x442DD0` (`+0x28`) | A handle's lip sync: the shape, and the clue in the high nibble |
| `0x442D40` (`+0x30`) | A handle's seconds played |
| `0x445B30` | A stream slot's thread. When the clip ends, or the stream is freed, it destroys the stream and clears `+0x68`: the slot is free again |

**`Voice.dat`** (type 1): `0x43CC20` passes `0x4428A0` the clip's own entry
(`+0x10`) for the handle, and frees nothing else.
- **Lines from different clips overlap,** up to four streams at once. The
  music (`Music.dat`, type 2) is a stream too, so with a track playing three
  lines can.
- **A line played again** gets a new stream, and its entry's handle is
  overwritten. The old stream plays to its end out of reach: stop
  (`0x434CB0` → `0x43CB90`), stop effects (`0x434E10` → `0x43C850`) and the
  readers all find the new one.
- **With four streams playing** the entry's handle becomes 0. Nothing plays,
  and an older stream of the same clip is out of reach too.

**Every reader goes by clip id,** to the stream in its entry:
- over (`0x434CE0` → `0x43CE10` → `+0x20`);
- lip sync (`0x434D40` → `0x43CAF0` → `+0x28`);
- seconds (`0x434BA0` → `0x43CA60` → `+0x30`).

With two lines playing, each reader reads its own clip. Nothing in the
original reads a "clip played last".

##### Street 2 and Street 3 (WP-033)

Traced 2026-11-14 for [WP-033](../work-packets/WP-033-streets.md), in
Showdown. Both rooms have the music group 2 and no opening of their own
(their constructors pass `2` and an empty string; Street 3's passes
`Street_3.320A_`).

**Street 2** (`0x42C3E0`, vtable `0x45F27C`):

| Address | Slot | What it does |
|---|---|---|
| `0x42CB40` | `+0x30` | Before the opening: `Street_1.130A_` (`0x40C6B0`) while `MoaningActive`, else none; not played (`+0x10` = 0). So it plays on every visit while the moans are on. Street 1's `+0x30` (`0x42BCD0`) is the same |
| `0x42C440` | `+0x0C` entry | Gummy, if built: `SLEEPS` looping (`0x406210`, state `0x10`) until `GummyPuzzle`. With `GummyPuzzle` and Gummy a clue owner (`0x40A870`, `ClueOwners`, game `+0xD8`), he and the donkey are 50.0 along. Both get hit type 0 (`+0x4`). Walk-ins: from the general store Daphne `UR`; from the station Fred `UL`; from Town Center Fred `DL` (`0x405F20`) and Daphne `DR` (`0x405EA0`) |
| `0x42C7A0` | `+0x18` placements | `OBJ_DONKEY…` and `OBJ_GUMMY…`: not built until Artie is met (`0x40A930`). `OBJ_P04_STREET2_CLOCK`: a plain sprite in layer 0, depth 0, `ANIM_P04_STREET2_CLOCKA`, or `…CLOCKB` once `OBJ_INV_CLOCK` is taken. `OBJ_P04_STREET2_WINDOW`: a plain sprite in layer 0, depth −1, hit type 0, once Gummy is a clue owner; else not built |
| `0x42CAE0` | `+0x14` event | `OBJ_P04_STREET2_HOTSPOT1`: `Street_2.100C_`; `…HOTSPOT2`: `Street_2.100D_`; neither blocks |
| `0x42C600` | `+0x24` exit | To `ROOM_P10_Front_Of_General_Store`, the scene is `Street_2.General_Store1_` or `…2_` (`rand() & 1`); then the base exit |

**Street 3** (`0x42CB80`, vtable `0x45F2C0`):

| Address | Slot | What it does |
|---|---|---|
| `0x42CBE0` | `+0x08` reset | The moan timer (`+0xB8`) at 36 ticks; the music flag (`+0xBC`) on; the hotspot scene (`+0xC8`) at 0 |
| `0x42CE50` | `+0x0C` entry | From Town Center Fred `DL`; from the Saloon Velma `U`; from the Bank Shaggy `UR`. The music flag on |
| `0x42CD10` | `+0x04` tick | Moans (`Street_3.Moan.1`–`4`) every 5–14 seconds with `MoaningActive`. Hotspot 2 stopped with the music flag on: the flag off and the music group 2 (`0x40AA10`), whose next variant plays because the group changed. On step 3 with the hotspot's state (`+0x60`) `ANIM_P11_STREET3_HOTSPOT3B`, that is while it plays its A: `Street_3.HOTSPOT3_`, blocking |
| `0x42CF00` | `+0x18` placements | `OBJ_P11_STREET3_HOTSPOT2` and `…HOTSPOT3`: clickables under their `layer=`, kept |
| `0x42CC10` | `+0x14` event | `OBJ_P11_STREET3_HOTSPOT`: `Street_3.130X1_`, `…130X2_`, `…130X3_` in turn, blocking. `…HOTSPOT2`: the music group −1 and the music flag on. The hotspot's own sound, `SFX_P11_STREET3_HOTSPOT2A`, is in `Music.dat` and so replaces the music |
| `0x42CCC0` | `+0x34` idle chatter | `rand() & 1`: `Street_3.100B2_` with `MoaningActive`, or `Street_3.1100A_` |

**Shared pieces:**

- **Walk-ins** (`0x405E60` `UR`, `0x405EA0` `DR`, `0x405EE0` `UL`,
  `0x405F20` `DL`, `0x405FE0` `U`). Each keeps the depth (`+0x9C`), moves
  50 behind it for `U…` and 50 in front for `D…`, and goes to state 1.
- **State `0x10`** (`0x406210`): `ANIM_<NAME><set><action>` looping, and it
  stays.
- **Hit type 0** is never hit: the hit walk (`0x4311F0`) tests only types 1
  and 2.
- **A plain sprite** (`graphics_AnimSprite_ctor`) takes its parent, depth,
  mode (1, looping) and ticks a step (3); a room may set its hit type.
##### Street 1 and the clues (WP-034)

Traced 2026-11-14 for [WP-034](../work-packets/WP-034-street1.md), in
Showdown.

**The clue a suspect gives** (game vtable `+0x44`, `0x42F990`):

1. Nothing if the suspect is already one of `ClueOwners0`–`4` (`0x40A870`,
   game `+0xD8`), or if no `CluesFound` slot (game `+0xB0`) is empty.
2. **The villain** (`Whodunit`, game `+0x100`) gives a red herring
   (`0x4301E0`): `rand() % 5`, drawn until it is neither the villain's nor
   the giver's number, picks one of `RH_ARTIE_BRUSH`, `RH_GUMMY_CLOTH`,
   `RH_IC_SOAP`, `RH_JENNY_GHOSTLY_TALES`, `RH_SHERIFF_GOLD_STAR` (suspects
   numbered Artie, Gummy, ICDouble, Jenny, Sheriff).
3. **Anyone else** first draws `rand() & 1`. Their clues are five
   (`0x46FA3C`): three of their own (Artie: `ESCAPE_BOOK`, `CLASS_LIST`,
   `MAP`), then two more (`CLOTH`, `HATBAND`).
   - While any of their own three isn't found (`0x4301A0`, game vtable
     `+0x68`), one of the three (`rand() % 3`).
   - Once all three are, at level 0 (game `+0x160`) the fourth or fifth by
     the first draw; above it, a red herring as in 2.
4. A clue already found is drawn again. It goes to the first empty
   `CluesFound` slot, the suspect to `ClueOwners` at the same index, and
   game `+0x109` (a new clue, for Scrappy) is set.

**Street 1** (`0x42AE70`, vtable `0x45F23C`; music group 2):

| Address | Slot | What it does |
|---|---|---|
| `0x42AED0` | `+0x08` reset | Its flags, the pump count (`+0xC0`) and the hint (`+0xCC`) at 0 |
| `0x42BCD0` | `+0x30` | The moaning opening, as Street 2's |
| `0x42B960` | `+0x0C` entry | If the Sheriff isn't a clue owner and isn't waiting (`SheriffWaiting`, `+0x26D`): one of `Street_1.130C1_`–`3_`, blocking, his clue (`+0x44`), and he gives when idle (`+0xBD`). From Town Center Fred `DR`; from the Sheriff's office Shaggy `UR`. Once he is a clue owner, the Sheriff stands at (501.0, 270.0) |
| `0x42BD10` | `+0x18` placements | `OBJ_SHERIFF`: only once Artie is a clue owner and until the brick is taken. `OBJ_P03_TO_P02`: only in his puzzle (`SheriffPuzzle`, `+0x26C`) once he has the sign. `OBJ_P03_STREET1_DOOR_OVERLAY`: a plain sprite in layer 0 at depth −1000 otherwise. `OBJ_INV_STRONGBOXKEY`: a requires object, hidden until `KeyVisible`; not built once taken. `OBJ_P03_STREET1_TROUGH`: a requires object, playing `TROUGHB`, `C` or `D` for 1, 2 or 3+ pumps once the handle is on the pump (taken, not in a slot, `0x4070C0`); with the brick taken it asks for `ANIM_CURSORBRICK` (`+0x5C`). `OBJ_P03_STREET1_HOTSPOT2`: kept |
| `0x42AF60` | `+0x04` tick | Below |
| `0x42C120` | `+0x14` event | The trough with its cursor: the brick gives `Street_1.Wash_Brick_`, takes the brick and sets `FinalClue` (game `+0x108`) and `+0xC4`; the handle sets the pumps to 0, takes the handle, plays `Street_1.130E_` and asks for a pump (`+0xD0`). With the arrow: a pump once the handle is on, else `130D_`, `130D2_`, `130D3_` by the pump count, which wraps to 0. The key: Scooby takes it (`+0xD2`) |
| `0x42BB50` | `+0x24` exit | To the post office with the lantern taken, no scene |
| `0x42AF10` | `+0x10` leave | A key Scooby was taking goes in the toolbar |
| `0x42C2E0` / `0x42C360` | `+0x1C` / `+0x20` | The base keys, then `PumpAttempts` (`%i`), `SheriffIntroPlayed` and `KeyVisible` |

The tick:

- **The Sheriff gives** when idle after `+0xBD`: `ANIM_SHERIFFGIVES` once
  (`0x4061F0`), the cursor gone and input held (`+0xBE`). When he is idle
  again, or gone, the room's exit handler takes an exit to
  `ROOM_Suspect_Chooser` with the scene `Global.Thank_You_`.
- **A click on him** (game `+0x20` bit 4, the character's `+0x8`):
  - **with the sign**, in his puzzle and waiting (`ANIM_CURSORPOP_SIGN`):
    the sign is taken, the cursor is the arrow, `SheriffWaiting` goes off,
    and `Street_1.220D1_` plays, blocking, its done flag `+0xBC`.
  - **with the arrow**, the first time (`SheriffIntroPlayed`, `+0xC5`):
    Big Head (`Street_1.130B_` on `BIG_HEAD_BG_P03`, then `ROOM_Sheriff`),
    and he is met (`0x40A8B0`).
  - **with the arrow, later:** in his puzzle, `Global.1000SA_` once he has
    the sign, else `Street_1.Hint1_`–`3_` in turn, neither blocking; out of
    it, `ROOM_Sheriff`.
  - **with any other item**, nothing here.
- **`220D1_` over** and the Sheriff idle: one of `130C1_`–`3_`, his clue,
  and he gives (`+0xBD`).
- **The brick washed**, with no scene and the opening done: movie 14 and
  `ROOM_Suspect_Chooser` (game vtable `+0x08`).
- **The pump** (`+0xD0`), once Shaggy is idle with no scene: Shaggy plays
  an object of his own (`0x406130`, state `0xD`: the object, and
  `ANIM_<object without OBJ_>1` once), with its sound; the trough hides.
  - pump count 0: `OBJ_SHAGGY_P03_PUT_HANDLE`, `Shaggy.Puts.Handle.On`;
  - 1: `PUMPA`, `Shaggy.Pumps.Gets.Water`;
  - 2 (then 3) and 3: `PUMPB`, `Shaggy.Pumps.Gets.Key`;
  - 4 or more: `PUMPC`, `Shaggy.Pumps.No.Water`.

  Input is held. When he is idle again, the count goes up, and the old
  count picks the trough and the scene:

  | Old count | Scene | Trough |
  |---|---|---|
  | 0 | `Street_1.130F2_` | `TROUGHB` |
  | 1 | `Street_1.130F_` | `TROUGHC` |
  | 3 | `Street_1.130F3_` | `TROUGHD`, and the key shows (`KeyVisible`) |
  | 4+ | none | `TROUGHD` |

  Count 2 becomes 3 when Shaggy starts.
- **The key** (`+0xD2`), once Scooby is idle with no scene:
  `OBJ_SCOOBY_P03_TAKES_KEY` with `Scooby.Takes.Key`, the key hidden; when
  he is idle again, `OBJ_INV_STRONGBOXKEY` goes in the toolbar.
- **The second hotspot** playing, on step 0, with its state (`+0x60`)
  `ANIM_P03_STREET1_HOTSPOT2B`, so playing its A: `Street_1.HOTSPOT2A_`,
  blocking.

##### The chase (WP-035)

Traced 2026-11-14 for [WP-035](../work-packets/WP-035-chase.md), in
Showdown; Phantom has no chase. After ROOM_P40_Chase_Start (music only),
the gang runs through two kinds of room, both with `Chase.Music`:

- **Chase B**, the branches, P24 to P29 (`0x41E6B0`, vtable `0x45EDA8`): a
  fork in the path, with an OBJ_BRANCH sprite.
- **Chase C**, the run-offs, P33 to P39 (`0x41FBB0`, vtable `0x45EDE8`): a
  canned animation, then the next branch.

The close-up, P25A (`0x4119F0`), is ICDouble's scene: [below](#the-close-up-p25a-wp-036).

**Chase B's fields:** `+0xB8` the OBJ_BRANCH sprite; `+0xBC` the countdown;
`+0xC0` the pending room; `+0xC8` the oil can taken here; `+0xCC` the oil
can's requires object.

| Address | What it does |
|---|---|
| `0x41ED40` (+0x18) | Placements. OBJ_BRANCH* (the first 10 characters): a sprite under layer 0, depth 0, looping. OBJ_INV_OILCAN: a requires object (`0x408C80` with -1: layer 0) unless the oil can is held, then not built. OBJ_P25_OVERLAY: a sprite at depth -1 while OBJ_INV_SAFE_COMBO isn't held and ICDOUBLE is a clue owner (`0x40A870`, game `+0xD8`), else not built |
| `0x41FA80` (+0x2C) | The opening, by where the gang came from: `Chase_Branch_3.230_` in P26; none in P24, P27, or from the corral; otherwise `rand() & 3` of `Chase_Branch_3.230_`, `.230B2_`, `.230C_`, `.230D_`. Never marked played |
| `0x41F650` (+0x0C) | Entry: the countdown at 720, nothing pending. P27 leaves for C6 and P24 for C4 at once. From the close-up, `Chase.Branch_2` and ANIM_BRANCH2A_FIN, pending C3; from the corral, `Chase.Branch_5_from_HC` and ANIM_BRANCH5A_FIN, pending C6. ICDOUBLE is never hit |
| `0x41E7A0` (+0x24) | Leave for a room, once: it becomes pending, the branch plays its run-off (mode 3, 3 ticks a step) with its sound, and input stops (`0x435150`, game `+0x24`). The exit's own scene and walk-off never play |
| `0x41EBC0` (+0x14) | OBJ_INV_OILCAN taken: the flag, and leave for C5 |
| `0x41EFC0` (+0x04) | The countdown: when its old value is below 0 with nothing pending, it starts again at 2160 and B2 leaves for C3, B3 for C2, B5 for C6, B6 for C5. While something is pending: on step 22 of the run-off with the flag set, the oil can goes in the toolbar and its sprite hides; when the run-off has played out, the room changes (game `+0x04`), or to the corral through movie 8 (game `+0x08`) |
| `0x41E780` (+0x08) | Reset: the countdown at 720 |

**The run-offs** (`0x41E7A0`), by the room they lead to:

| To | Branch | Run-off | Sound |
|---|---|---|---|
| B2 | | ANIM_BRANCH3B | `Chase.Branch_3b` |
| C3 | | ANIM_BRANCH2B | `Chase.Branch_2` |
| P25A, the close-up | | ANIM_BRANCH2A | `Chase.Branch_2` |
| C2 | | ANIM_BRANCH3A | `Chase.Branch_3a` |
| C4 | | ANIM_BRANCH1A | `Chase.Branch_1a` |
| The corral | | ANIM_BRANCH5A | `Chase.Branch_5a` |
| C6 | OBJ_BRANCH5 | ANIM_BRANCH5B | `Chase.Branch_5b` |
| C5, the oil can taken | | ANIM_BRANCH6C | `Chase.Branch_6c` |
| C5 | | ANIM_BRANCH6A | `Chase.Branch_6a` |
| B4 | OBJ_BRANCH6 | ANIM_BRANCH6B | `Chase.Branch_6b` |
| C6 | OBJ_BRANCH4 | ANIM_BRANCH4A | `Chase.Branch_4` |

A destination with no run-off still holds input, and with the branch
still looping the room never changes; no room's exits lead to one.

**Chase C** (`0x420690`, `0x420510`, `0x41FC10`):
- **Placements:** OBJ_CANNED* is a sprite under layer 0, moved to depth −1
  and started once through (`graphics_AnimSprite_Start` 3, 3, −1).
- **Entry:** the toolbar hides, input stops, and `Chase.Canned_1` to `_6`
  plays (C1, C2, C3, C4, C5, C6).
- **Each tick** input stays held. When the run-off has played out, the
  default exit handler (`0x40C1E0`) takes C1 to B3, C2 to B1, C3 to B5,
  C4 to B6, and C5 and C6 back to ROOM_P40_Chase_Start through movie 31.
  It is called again every tick until the room changes; the fork calls it
  once.

##### The close-up, P25A (WP-036)

Traced 2026-11-15 for [WP-036](../work-packets/WP-036-closeup.md).
ROOM_P25A_Chase_B2_Closeup (`0x4119F0`, vtable `0x45E890`, `Track9.Music`)
has ICDouble digging, the gang, the exit back to P25, and the safe's
combination (OBJ_INV_SAFE_COMBO, an inventory object by `object.ini`). It
takes the player through three visits:
1. **Meeting ICDouble.**
2. **His clue,** once the artifact is built.
3. **The combination,** which blows in once he has given his clue.

**Its fields:**
- `+0xB8`: he gives when next idle.
- `+0xB9`: then the thanks.
- `+0xBC`: the combination's sprite.
- `+0xC0`: `Chase.Branch_2.486_`'s done flag.
- `+0xC1`: Shaggy is taking it.
- `+0xC2`: `ComboBlewOn`.
- `+0xC3`: ICDouble was a clue owner on entry.
- `+0xC4`: the countdown to the blow-in.

**The game fields it reads:** game `+0x270` is `ArtifactsBuilt`, `+0x278`
`ArtifactType` (Bowl, Deer, Vase), `+0x160` the level.

| Address | What it does |
|---|---|
| `0x412300` (+0x18) | Placements. OBJ_INV_SAFE_COMBO, unless held: a requires object (`0x408C80` with -1: layer 0) at depth 500, stopped on its last step (`graphics_AnimSprite_Start` 5, 3, -1), hidden until `ComboBlewOn`. Held: not built |
| `0x412020` (+0x0C) | Entry, after the base entry. `+0xC3` is whether ICDOUBLE is a clue owner (`0x40A870`). Not one, with `ArtifactsBuilt` exactly 1: `Chase_B2_Closeup.260C1_` to `260C3_` (`rand() % 3`), holding input, then his clue (game vtable `+0x44`) and `+0xB8`. Then `+0xC0`, `+0xC1` cleared and the countdown at 24. Not met yet (game `+0x174`): he is met, and Big Head plays `Chase.Branch_2.260A_` on `BIG_HEAD_BG_P25A`, then the artifact's room. Else, with the combination built, not blown in, and `+0xC3`: input holds |
| `0x412490` | The artifact's room: `ROOM_Artifact_<ArtifactType>_` and `09`, `12` or `15` by level ([the puzzle](#the-artifact-puzzle-wp-037)) |
| `0x411AC0` (+0x04) | The tick, after the base tick. See below |
| `0x411FC0` (+0x14) | OBJ_INV_SAFE_COMBO with the arrow: `Chase.Branch_2.486_`, its done flag `+0xC0`, told to hold input |
| `0x411A70` (+0x10) | Leave, after the base leave: `+0xC0` set, the combination goes in the toolbar if it isn't there |
| `0x411A50` (+0x08) | Reset: `+0xB8`, `+0xB9`, `+0xC2` cleared |
| `0x412410` / `0x412450` (+0x1C / +0x20) | `ComboBlewOn` in the room's section, after the base keys |

**The tick** (`0x411AC0`), in order:
1. **ICDouble clicked** with the arrow (game `+0x20` bit 4, his `+0x08`):
   - before the artifact is built (`ArtifactsBuilt` < 1), back to the
     artifact's room;
   - after, `Chase_B2_Closeup.1901_` to `1904_` (`rand() & 3`), not held.
2. **ICDouble idle with `+0xB8`:**
   - he plays GIVES, `+0xB9` is set, and input holds;
   - idle again with `+0xB9`: the room's exit handler (`+0x24`) with
     `Global.Thank_You_` to ROOM_Suspect_Chooser.
3. **`+0xC0` set, the combination's scene over:**
   - with Shaggy idle and no scene or opening, he plays
     `OBJ_SHAGGY_P25A_TAKE_COMBO`, the combination hides, and input holds;
   - idle again: OBJ_INV_SAFE_COMBO goes in the toolbar
     (ANIM_TOOLBARSAFE_COMBO, ANIM_CURSORSAFE_COMBO) and input is free.
4. **The blow-in:** with the combination built, not blown in, and `+0xC3`,
   the countdown's old value below 1:
   - `ComboBlewOn`, and it shows;
   - it plays once (3, 3, −1) at Shaggy's depth − 1, with
     `ICDouble.Combo.Blows.In`, 25 ticks after entry.
5. **On step 38,** while it plays, it moves to Shaggy's depth + 1.
6. **Once blown in and stopped,** with `+0xC3`, input is freed (`0x4351C0`,
   game `+0x24`) on every tick. That frees the hold of the combination's
   scene and of Shaggy taking it in the tick they start, so neither holds
   input.

##### The artifact puzzle (WP-037)

Traced 2026-11-15 for [WP-037](../work-packets/WP-037-artifact.md). The
nine ROOM_Artifact_<Bowl|Deer|Vase>_<09|12|15> rooms (`0x40D8A0`, vtable
`0x45E6CC`, `Track9.Music`) are the puzzle the close-up sends the gang to.
Each is a jigsaw of 9, 12 or 15 bones, by its level. Each room's
placements are:
- the exit back to the close-up;
- the artifact, `OBJ_ARTIFACT_<TYPE>`, which morphs when built;
- the pieces, one object (`OBJ_ARTIFACT_<size>_<TYPE>`) with one sequence
  per piece;
- the outline, that object's COMPLETE sequence.

**Its fields:**
- `+0xB8`: the pieces' sprites, numbered as they are built.
- `+0xF8`: the artifact's sprite.
- `+0xFC` and `+0x138`: each piece's place, its placement's position.
- `+0x174`: the piece count.
- `+0x178`: the piece carried, or −1.
- `+0x17C`: the artifact is morphing.
- `+0x180` and `+0x184`: the carried piece's offset from the mouse.
- `+0x188`: `PiecePlaced0`–`14`.

| Address | What it does |
|---|---|
| `0x40E0E0` (+0x18) | Placements, each a sprite under layer 0 hit by its cels (`0x430D60` sets `+4` to 1). The artifact: depth 2, hidden. The outline (the COMPLETE sequence): depth 0. Each piece: depth 1, at its start for the level, or at its place if `PiecePlaced` |
| `0x40E060` (+0x0C) | Entry, after the base entry: the toolbar slides off (`0x407CC0`), and `Artifact.Intro_1_ICDOUBLE` plays |
| `0x40DA50` (+0x04) | The tick. See below; the base tick runs last |
| `0x40D940` | A piece in its place: `Artifact.Clink1` to `3` (`rand() % 3`). With every piece exactly in its place, the artifact shows and plays once (3, 3, −1), `ArtifactsBuilt` (game `+0x270`) is 1, `+0x17C` is set, and `Artifact.Morph` plays |
| `0x40E0C0` (+0x10) | Leave, after the base leave: the piece count and the artifact cleared |
| `0x40D900` (+0x08) | Reset: the count, `+0x17C`, the artifact, the carried piece (−1) and every `PiecePlaced` cleared |
| `0x40E640` / `0x40E6F0` (+0x1C / +0x20) | `PiecePlaced0` to `14` in the room's section, after the base keys |

**Where the pieces start**, by level, in build order (`0x46AE10`,
`0x46AE58`, `0x46AEB8`; `(x, y)` in layer 0):

| Level | Starts |
|---|---|
| 09 | (133,185) (210,185) (317,188) (101,256) (207,256) (345,262) (73,350) (220,360) (382,360) |
| 12 | (136,178) (210,178) (315,178) (107,234) (218,234) (339,237) (91,300) (212,303) (358,299) (71,372) (218,378) (383,371) |
| 15 | (140,168) (223,167) (310,167) (115,217) (219,214) (335,213) (102,263) (224,263) (359,263) (88,314) (215,316) (372,311) (77,371) (219,380) (385,373) |

The tick (`0x40DA50`) reads the mouse from the cursor sprite (game `+0x18`,
its `+0xC`, `+0x10`) and the click from game `+0x20` bit 4:
1. **The cursor:** over a piece off its place on both axes, ANIM_CURSOROPEN;
   otherwise the default cursor.
2. **Not carrying, a click on a piece not in its place:**
   - within 10 pixels of its place on both axes, it snaps in: depth 1,
     `PiecePlaced`, then `0x40D940`;
   - otherwise it is carried: its offset from the mouse is kept, and its
     depth is its y.
3. **Carrying, no click:**
   - a piece exactly in its place stays carried;
   - otherwise, within 10 of its place it snaps in, as above, and is let
     go;
   - otherwise it follows the mouse at its offset, at the depth of its y.

   The snap tests where the piece was, so it comes a tick after the mouse
   brings it close.
4. **Carrying, a click:** the piece goes back to its start for the level
   (the last two letters of the room's name), at depth 1, with
   `Artifact.Wrong`.
5. **The artifact morphing,** played out and with `Artifact.Morph` over
   (`0x434CE0`): the room's exit handler takes the gang to
   ROOM_P25A_Chase_B2_Closeup.
6. **The cursor sprite** is hidden (`0x435150`) while a piece is carried,
   and shown (`0x4351C0`) otherwise. Input stays on.

##### The bank vault and the open safe (WP-038)

Traced 2026-11-15 for [WP-038](../work-packets/WP-038-vault.md). The bank
has five classes:

| Room | Class | Vtable |
|---|---|---|
| ROOM_P13_Bank (the vault door) | `0x428660` | `0x45F0E8` |
| ROOM_Vault_Clock (its dial) | `0x42A780` | `0x45F1E8` |
| ROOM_P16_Bank_Vault | `0x429220` | `0x45F128` |
| ROOM_Open_Safe | `0x429BE0` | `0x45F168` |
| ROOM_SB1 to SB5 | `0x42A340` | `0x45F1A8` |

This section covers the vault and the open safe; the bank and its clock
are [below](#the-bank-and-the-vault-clock-wp-039).

**ROOM_SB1 to SB5 are unreachable** in the shipped game (checked for
[WP-040](../work-packets/WP-040-boot-hill.md)):
- Only the factory names them; nothing in the art, `object.ini` or the
  executable sends the gang there, and no code builds the names.
- In play, the right strong box plays movie 38–41 instead (`0x429350`).
- Their class (`0x42A340`, vtable `0x45F1A8`; no music, no opening) shows a
  strong box's lid opening, then the vault again. The fork has it since
  [WP-053](../work-packets/WP-053-strong-boxes.md#result-2026-11-15).

| Address | What it does |
|---|---|
| `0x42A3A0` (+0x08) | Reset, after the base reset: `+0xB8` (the scene's done flag) and `+0xB9` (the lid opening) clear |
| `0x42A600` (+0x18) | Placements. `OBJ_SB1_LID` to `OBJ_SB5_LID` a sprite under the first layer at depth 0, stopped on step 0 (`graphics_AnimSprite_Start` 0, 3, −1), kept in `+0xBC`. The layer is the engine's `+0x58` through `0x475F4C`, which the engine's constructor sets to itself: the same object as `0x475F14` |
| `0x42A5B0` (+0x0C) | Entry, after the base entry: the toolbar hidden (`0x407CC0`), the cursor faded (`0x435150`, `0x12`), input held (game `+0x24`), and `+0xC0` 36 |
| `0x42A3C0` (+0x04) | The tick, after the base tick. `+0xC0` counts down; at 0, `Strongbox.opens` plays and the lid plays once at 5 ticks a step (`Start` 3, 5, −1), and `+0xB9` is set. The lid stopped with `+0xB9`: `Bank_Vault.340D_` (the narrator's), held, with `+0xB8` as its done flag. Set, the room's exit handler (the base's) to `ROOM_P16_Bank_Vault`, with no scene and movie −1 |
| `0x42A770` (+0x10) | Leave: the base leave only |

**ROOM_P16_Bank_Vault**'s placements:
- the gang;
- the exits to the bank and, through the safe, to ROOM_Open_Safe;
- the safe's door, OBJ_P16_DOOR, a requires object for ANIM_CURSORSAFE_COMBO;
- four strong boxes, hotspots 1–4, requires objects for
  ANIM_CURSORSTRONG_BOX_KEY;
- the dust, hotspot 6, a clickable.

**Its fields:**
- `+0xB8`: the door.
- `+0xBC`: the dust.
- `+0xC0`: `DustVisible`.
- `+0xC4`: which of two lines a box clicked with the arrow gets.
- `+0xC8`: the door clicked.
- `+0xC9`: Daphne has tried it.

An item **used** below is one taken (`0x407060`) and no longer in a slot
(`0x4070C0`).

| Address | What it does |
|---|---|
| `0x4295E0` (+0x18) | Placements. The door: a requires object (`0x408C80` with -1: layer 0) at depth 1, showing ANIM_P16_DOOROPEN on its last step (start 5) once the combination is used. Hotspots 1–5: not built once the key is used. Hotspot 6: a clickable (`script_CreateClickableObject` 1, -1), on ANIM_P16_BANK_VAULT_HOTSPOT6C (start 0) with its state set (`0x401780`) while `DustVisible` |
| `0x4292A0` (+0x0C) | Entry, after the base entry: `+0xC8` and `+0xC9` cleared; with the key used and the dentures never taken, OBJ_INV_DENTURES goes in the toolbar |
| `0x429350` (+0x14) | Events. See below |
| `0x429870` (+0x04) | The tick, after the base tick. See below |
| `0x429280` (+0x08) | Reset: `DustVisible` and `+0xC4` cleared |
| `0x4297F0` / `0x429830` (+0x1C / +0x20) | `DustVisible` in the room's section, after the base keys |

**The events** (`0x429350`):
- **The door:** with the combination, it is used (`0x406C80`) and the
  cursor goes back to the default. Either way `+0xC8` is set, and input
  holds.
- **A strong box with the arrow:** `Bank_Vault.340A_` and
  `Bank_Vault.340A2_` in turn, holding input.
- **A strong box with the key:**
  - in the right box, whose number less one is `StrongBox` (game
    `+0x28C`), the vault loads again through movie 38 + (box − 1) (game
    vtable `+0x08`, with the box's last character − `0xB`), and the key is
    used;
  - in a wrong box, `Bank_Vault.340B_`, `340B2_` or `340B3_`
    (`rand() % 3`), holding input.
- **The dust:**
  - until `DustVisible`, it becomes visible when its next state is
    ANIM_P16_BANK_VAULT_HOTSPOT6C;
  - after, `Bank_Vault.340X_` plays, and the dust is put back on C, its
    state too.

**The tick** (`0x429870`), only with `+0xC8` set:
1. **Daphne tries the safe.** With Daphne idle, no scene, and the opening
   done:
   - without the combination used, she plays
     `OBJ_DAPHNE_P16_NO_UNLOCK_SAFE` with `Daphne.No_Open_Safe`;
   - with it, she plays `OBJ_DAPHNE_P16_UNLOCK_SAFE` with
     `Daphne.Opens_Safe`, and the door hides.

   Then `+0xC9` is set.
2. **Input holds** on every tick.
3. **Daphne idle again** after her try:
   - without the combination, `Bank_Vault.340E_` plays;
   - with it, the door shows ANIM_P16_DOOROPEN (start 0, step 0) again,
     and the room's exit handler takes the gang to ROOM_Open_Safe.

   Then both flags clear.

**ROOM_Open_Safe** has no music. Its placements are the gang in the vault,
`OBJ_GANG_VAULT_<NAME>`, each a talking mouth.

| Address | What it does |
|---|---|
| `0x42A040` (+0x18) | Each of the gang a sprite under layer 1 (game `+0x5C`) at depth 1: Daphne `+0xC0`, Fred `+0xC4`, Velma `+0xC8`, Shaggy `+0xCC`, Scooby `+0xD0` |
| `0x429C40` (+0x0C) | Seen before (the opening played): ROOM_P19_Back_Alley. Then the base entry, the toolbar off (`0x407CC0`), the countdown `+0xBC` at 72, and `Open_Safe.340F_` started, holding input |
| `0x42A320` (+0x3C) | Input held and the cursor hidden, on every tick |
| `0x429CB0` (+0x38) | The scene's step, its own line player. See below |
| `0x429F10` (+0x04) | The tick. See below |

**The scene's step** (`0x429CB0`):
- **The next line:** with the countdown run out, the scene on and no line
  playing, it takes the first of the 20 speakers (`0x46A720`, Big Head's)
  with a clip `<scene><line>_<NAME>`, and plays it.
- **Its mouth** is the speaker's: Daphne, Fred, Scooby, Velma, or else
  Shaggy's.
- **The end:** with no line left, or on input slot 5 (which also stops the
  line), the scene is over.

**The tick** (`0x429F10`):
1. **The base tick,** with the scene's step in it.
2. **The mouths:** each of the gang goes to step 0, and the speaker's to
   the lip sync's shape − 1.
3. **A line over** (its position −1) frees the next.
4. **The scene over:** the opening counts as played, and ROOM_P19_Back_Alley
   loads.

##### The bank and the vault clock (WP-039)

Traced 2026-11-15 for [WP-039](../work-packets/WP-039-bank.md). These are
the other two of the [bank's five classes](#the-bank-vault-and-the-open-safe-wp-038).

**The mouse flags** that room classes read, game `+0x20`, are set each
frame from the mouse (`0x4359C0`):

| Bit | Meaning |
|---|---|
| 1 | The button is held |
| 2 | The button went down this frame |
| 4 | The button came up this frame |

A sprite under the mouse has its `+0x08` set.

**ROOM_P13_Bank**'s placements:
- the gang;
- the exits to Street 3 and, through the vault door, to the vault (scene
  `Bank.330D1_`);
- the vault door, OBJ_P13_DOOR, a requires object for
  ANIM_CURSORBROKEN_CLOCK;
- four clickables.

The broken clock is OBJ_INV_CLOCK in the toolbar, added with
ANIM_TOOLBARBROKEN_CLOCK and ANIM_CURSORBROKEN_CLOCK (`0x40FB70`).

**Its fields:**
- `+0xB8`: the door.
- `+0xBC`: the countdown to the door opening.
- `+0xC0`: the countdown to the next moan.
- `+0xC4`: which line the door clicked with the arrow gets.

| Address | What it does |
|---|---|
| `0x4286E0` (+0x30) | The opening: `Bank.330A_`, unplayed, on every visit while `MoaningActive` (game `+0x254`); none otherwise |
| `0x428EC0` (+0x18) | The door, a requires object (`0x408C80` with -1: layer 0) at depth 1. With `VaultOpen` (game `+0x276`), ANIM_P13_DOOROPEN on its last step (start 5); else, with the clock used, its step 0 (start 0) |
| `0x428FE0` (+0x0C) | Entry, after the base entry. With `VaultOpen` and from the dial: input held, the countdown at 36, the door on DOOROPEN step 0. The door's line back to the first. Fred walks in down-left (`0x405F20`) from Street 3, Daphne up-right (`0x405E60`) from the vault |
| `0x428710` (+0x14) | The door. See below |
| `0x4290D0` (+0x04) | The tick, after the base tick. See below |
| `0x4286C0` (+0x08) | Reset: the moan countdown at 36 |

**The door** (`0x428710`):
- **With the arrow and the clock used** (taken, not in a slot): the room's
  exit handler to ROOM_Vault_Clock, with no scene.
- **With the arrow otherwise:** `Bank.330B_`, `Bank.330B2_`, then
  `Bank.330C_` with the clock in a slot or `Bank.330B3_`, in turn, holding
  input.
- **With the clock:**
  - it is used and the cursor goes back to the default;
  - a time is drawn, `rand() % 10` from the level's table (game `+0x160`),
    and kept as `ClockHour` and `ClockMinute` (game `+0x284`, `+0x288`);
  - the room's exit handler takes the gang to ROOM_Vault_Clock with the
    scene `Bank_Vault.Clock_<level>_<%.2d%.2d>_`, which names the time.

| Draw | Spooky (09) | Spookier (12) | Spooktacular (15) |
|---|---|---|---|
| 0 | 2:00 | 1:40 | 1:14 |
| 1 | 3:00 | 2:50 | 2:26 |
| 2 | 4:00 | 3:10 | 3:18 |
| 3 | 5:00 | 4:20 | 4:08 |
| 4 | 6:00 | 5:30 | 5:16 |
| 5 | 7:00 | 6:40 | 7:49 |
| 6 | 8:00 | 7:50 | 8:02 |
| 7 | 9:00 | 10:10 | 10:23 |
| 8 | 10:00 | 11:20 | 11:57 |
| 9 | 11:00 | 12:30 | 12:31 |

Each of the 30 times has its own `ANIM_VAULT_CLOCK_TIME<hh>_<mm>` on the disc,
and no others do.

**The tick** (`0x4290D0`):
1. **The door's countdown** reaching 0: `Bank.330D_`, holding input, with
   `Bank.Vault_Opens`; the door plays DOOROPEN once (3, 3, −1); input is
   freed.
2. **The moans:** while the countdown's old value is above 0, nothing.
   Then, with `MoaningActive`, `Town_Center.Moan.1` to `4` (`rand() & 3`),
   and the countdown at (`rand() % 10` + 5) × 36.

**ROOM_Vault_Clock**'s placements:
- the exit back to the bank;
- the hour hand, 12 steps, and the minute hand, 60, both at (319, 289);
- the time to set, OBJ_VAULT_CLOCK_TIME.

**Its fields:**
- `+0xB8`: the hour hand.
- `+0xBC`: the minute hand.
- `+0xC0`: what is dragged (0 none, 1 the hour hand, 2 the minute hand).
- `+0xC4`: `Vault_Clock.Dial.Click`'s id.
- `+0xC8` and `+0xCC`: the hands' last steps.

| Address | What it does |
|---|---|
| `0x42A830` (+0x18) | The hands and the time, sprites at depth 0, stopped on step 0. The time starts `ANIM_VAULT_CLOCK_TIME%002i_%002i` of `ClockHour` and `ClockMinute`; an unknown name shows nothing |
| `0x42AA70` (+0x0C) | Entry: the toolbar slides off (`0x407CC0`), nothing dragged |
| `0x42AAA0` (+0x04) | The tick, after the base tick. See below |

**The tick** (`0x42AAA0`):
1. **Catching a hand:** with nothing dragged, the button going down (bit 2)
   on the hour hand drags it, else on the minute hand.
2. **Turning it:** dragged, the hand turns toward the mouse (game `+0x1C`,
   `+0x1E`), unless the mouse is at the dial's center (319, 285).
   - **The target:** `atan2(x − 319, −(y − 285))` ÷ 2π, plus 1 if it is
     negative, times the hand's steps, plus 0.5, truncated, modulo the
     steps.
   - **The step:** the hand is restarted every tick: stopped on the
     target; else one step forward (mode 1) or back (mode 2), the shorter
     way.

   So it turns a step a tick.
3. **Letting go:** the button coming up (bit 4) stops both hands.
4. **The vault opens:** with nothing dragged, the minute hand on
   `ClockMinute` and the hour hand on `ClockHour` mod 12, `VaultOpen` is
   set and the room's exit handler takes the gang back to the bank. It is
   called again every tick until the room changes; the fork calls it once.
5. **The click:** a hand on a new step plays `Vault_Clock.Dial.Click`
   again from its start.

##### Boot Hill (WP-040)

Traced 2026-11-15 for [WP-040](../work-packets/WP-040-boot-hill.md).
ROOM_P21_Boot_Hill1, ROOM_P22_Boot_Hill2 and ROOM_P23_Boot_Hill3 share one
class (`0x40ECB0`, vtable `0x45E74C`), one object a room. Each room has:
- the gang and the ghost;
- three graves, clickables;
- its exits (1 to 2 and 3; 2 to 1 and the lit tunnel; 3 to 1).

`GraveLocation` (game `+0x280`, drawn 0–8 by a new game) names the grave
with the brick: 0–2 Boot Hill 1's first to third, 3–5 Boot Hill 2's, 6–8
Boot Hill 3's.

**Its fields:**
- `+0xB8`: the dig scene's done flag.
- `+0xB9`: `DigScenePlayed`.
- `+0xBA`: the brick dug up, for the next entry.

| Address | What it does |
|---|---|
| `0x40ED30` (+0x30) | The opening. Dug up, without `DigScenePlayed`, in the brick's room: `Boot_Hill_1.210B_`, unplayed. Else in Boot Hill 2 `Boot_Hill_2.340E2_`, or none. `0x40C6B0` sets only the name, so whether it has played stays as it was |
| `0x40F4F0` (+0x18) | The graves are not built once the brick is dug up or was ever taken |
| `0x40EE10` (+0x0C) | Entry, after the base entry. See below |
| `0x40F250` (+0x14) | A grave clicked. See below |
| `0x40F210` (+0x04) | After the base tick: the dig scene over, the brick is dug up (`+0xBA`) and the room loads again through movie 3 (game vtable `+0x08`) |
| `0x40EFD0` (+0x24) | Boot Hill 2's way back to 1 or 3. See below |
| `0x40ED10` (+0x08) | Reset: the three flags cleared |
| `0x40F660` / `0x40F6A0` (+0x1C / +0x20) | `DigScenePlayed` in the room's section, after the base keys |

**The entry** (`0x40EE10`), after the base entry:
- `Boot_Hill.Ambient` plays.
- The room needs the level's snacks plus two (`+0x24`).
- **The brick:** dug up, it goes in the toolbar (ANIM_TOOLBARBRICK,
  ANIM_CURSORBRICK) if never taken. In a slot, `DigScenePlayed` is set.
- **The gang walks in:**
  - Velma up into 2 from 1;
  - Fred down-left into 3 from 1;
  - Daphne down-right into 1 from 2;
  - Shaggy up-right into 1 from 3;
  - Fred down-left from the lit tunnel.

**A grave clicked** (`0x40F250`):
- **The brick's grave:** with the brick never taken, no scene and the
  opening done, `Boot_Hill_1.190B_`, `190B2_` or `190B3_` (`rand() % 3`)
  plays, holding input, with its done flag.
- **Any other grave:** the ghost appears (`0x40A990`), and with it the
  ghost spot.

**Boot Hill 2's way back** (`0x40EFD0`): to Boot Hill 1 or 3, with fewer
snacks given (`+0x88`) than the level plus two:
- the gang stays;
- `Boot_Hill_1.190A_`, `190A2_` or `190A3_` by level plays, holding input;
- the snack box flashes (`0x40D4D0`).

Otherwise, and to the tunnel, the room's default exit handler runs.

##### The tunnel (WP-041)

Traced 2026-11-15 for [WP-041](../work-packets/WP-041-tunnel.md).

**ROOM_P14_Tunnel_Dark** (`0x4194D0`, vtable `0x45EB1C`):
- **The base's opening** is `Tunnel_Dark.170A_`.
- **Its placements:** Shaggy and Scooby; a way out to the post office;
  three clickables; and the crate, OBJ_P14_TUNNEL_DARK_CRATE, a requires
  object whose `requiredanim` is ANIM_CURSORARROW, so a click with the
  arrow counts as the right item.

**Its fields:**
- `+0xB8`: the crate.
- `+0xBC`: which line the way out gets.
- `+0xC0`: the crate clicked.
- `+0xC1`: Shaggy is at it.
- `+0xC4`: the tries this visit.

| Address | What it does |
|---|---|
| `0x419950` (+0x18) | The crate, a requires object (`0x408C80` with -1: layer 0) |
| `0x4199C0` (+0x0C) | Entry, after the base entry: the line, the tries and both flags back to 0 |
| `0x419920` (+0x14) | The crate with its item, the arrow: `+0xC0` |
| `0x419530` (+0x24) | A way out: `Tunnel_Dark.170A2_` and `170A3_` in turn, without holding input. The default handler isn't called, so the gang stays |
| `0x419610` (+0x04) | The tick, after the base tick. See below |

**The tick** (`0x419610`), while the crate is clicked; input is held on
every tick:
1. **Shaggy tries.** With Shaggy and Scooby idle, no scene and the opening
   done:
   - on the visit's first try, Shaggy plays `OBJ_SHAGGY_P14_NO_PUSH_CRATE`
     with `Shaggy.Cant.Push.Crate`;
   - on any later try, the crate and Scooby hide, and Shaggy plays
     `OBJ_SHAGGY_P14_PUSH_CRATE` with `Shaggy.Scooby.Push.Crate`.
2. **Shaggy idle again:**
   - after the first try, input is freed;
   - after a push, the crate shows ANIM_P14_TUNNEL_DARK_CRATEB, looping,
     and Shaggy hides. A sprite of his push's last step takes his place in
     layer 0 at depth 500, and ROOM_P08_Post_Office loads.

**ROOM_P18_Tunnel_Lit** (`0x4199F0`, vtable `0x45EB5C`) has the gang and
two ways out: to the post office, and to Boot Hill 2 with the scene
`Tunnel_Light.180A_`. Its exit handler (`0x419A50`, +0x24) keeps the
scene of the first way out the gang takes (`BootHillCommentPlayed`,
`+0xB8`). After that it clears the exit's scene, then calls the default
handler. So the way to Boot Hill has its comment only if it's the first
way out taken. `BootHillCommentPlayed` is saved in the room's section
(`0x419BD0`, `0x419C10`) and cleared by the reset (`0x419BB0`).

##### The hotel (WP-042)

Traced 2026-11-15 for [WP-042](../work-packets/WP-042-hotel.md).

**The music's volume.** `0x40AA10` takes a second argument, a volume in
percent. If the group asked for is already playing, only the volume
changes; otherwise the group starts, then takes the volume. The hall asks
for group 3 at 95, the room for group 3 at 90.

**ROOM_P17_Hotel_Hall** (`0x410BB0`, vtable `0x45E810`):
- **Its placements:** Daphne and Fred; ways out to the hotel room and the
  saloon; the door, OBJ_P17_HOTEL_HALL_DOOR, a requires object; and three
  clickables: hotspots 1 and 2, and the chandelier.
- **Its fields:** `+0xB8` `SecondEntrance`; `+0xC0` the door; `+0xC4` the
  chandelier's next line; `+0xC8` hotspot 1; `+0xCC` Daphne.

| Address | What it does |
|---|---|
| `0x410C10` (+0x08) | Reset, after the base reset: `SecondEntrance` cleared |
| `0x410CC0` (+0x30) | The opening `Hotel_Hall.1100BE3_` by name, whether it has played left as it was (`0x40C6B0`). Once it has played, and without `SecondEntrance`: `Hotel_Hall.1100B2_`, unplayed, and `SecondEntrance` set, so the second visit has its own opening once |
| `0x410DC0` (+0x18) | The door a requires object (`0x408C80` with -1: layer 0) at depth 1; hotspot 2 a clickable at depth -100; the chandelier a clickable at depth -1, or not built once the nickel has been used; hotspot 1 the default clickable |
| `0x410C40` (+0x0C) | Entry, after the base entry: with `HotelHallDoor` the door shows ANIM_P17_HOTEL_HALL_DOORANIM from step 5. From the saloon Daphne walks in from the left (`0x405F60`); from anywhere else Fred walks in from the right (`0x405FA0`). Both keep the character's depth. Then the music, and the chandelier's line back to the first |
| `0x410F80` (+0x14) | The door, with Fred idle (`+0x74` = 6), whatever the item: DOORANIM from step 5, `HotelHallDoor` (game `+0x255`), Fred's special OBJ_FRED_P17_OPEN_DOOR and the sound `Hotel_Hall.Unlocked_Door`. The chandelier: `Hotel_Hall.400A_`, `400A2_`, `400A3_` in turn, without holding input |
| `0x410D00` (+0x04) | The tick, after the base tick: hotspot 1 on step 6 of a sequence ending in A, or step 4 of one ending in B: Daphne scared (state `0x11`) and `Hotel_Hall.Scream_`, not held |
| `0x411090` / `0x4110D0` | Save / load `SecondEntrance` in the room's section |

Fred has no end-walk sequence from the right in Showdown's art
(OBJ_FRED_ENDWALK_R_B is missing). Starting it fails, which leaves his
sprite stopped (`0x430AA0`), so he goes idle on the next tick.

**ROOM_P20_Hotel_Room** (`0x411110`, vtable `0x45E850`):
- **Its placements:** Daphne and Fred; a way out to the hall; the window,
  OBJ_P20_HOTEL_WINDOW, a way out whose destination is the room itself;
  hotspots 2 and 4; and the nickel, OBJ_INV_NICKEL.
- **Its fields:**
  - `+0xB8` / `+0xBC`: hotspots 2 and 4.
  - `+0xC0`: the nickel.
  - `+0xC4`: the nickel clicked.
  - `+0xC5`: Daphne is picking it up.
  - `+0xC6`: `LookedOutAuto`.
  - `+0xC7`: the window still to take by itself.
  - `+0xC8`: the window count.

| Address | What it does |
|---|---|
| `0x411170` (+0x08) | Reset, after the base reset: the count, `LookedOutAuto` and `+0xC7` cleared |
| `0x411190` (+0x2C) | Arrival. See below |
| `0x411280` (+0x18) | Hotspots 2 and 4 clickables, as the default path builds them (`0x408DC0` with 1, -1: depth `priority=`, -1 and -102); the nickel a requires object (layer 0), hidden once it has been had |
| `0x411250` (+0x0C) | Entry, after the base entry: the music; `+0xC4` and `+0xC5` cleared |
| `0x4113B0` (+0x14) | Hotspot 2 while its state (`+0x60`) is ANIM_P20_HOTEL_HOTSPOT2C: `Hotel_Room.410X_`, not held. The nickel with the arrow as the cursor: `+0xC4` |
| `0x411440` (+0x24) | A way out. See below |
| `0x4115D0` (+0x04) | The tick, after the base tick. See below |
| `0x411910` (+0x10) | Leaving, after the base leave: the nickel clicked and not yet had goes in the toolbar |
| `0x411960` / `0x4119A0` | Save / load `LookedOutAuto` in the room's section |

**Arrival** (`0x411190`):
- **From the room itself** (through the window), without the brick: the
  count goes up by one. If it was 1, the opening is `Hotel_Room.410C_`; if
  it was 2, `Hotel_Room.410C2_`, and the count goes back to 1. Otherwise
  the opening is marked unplayed.
- **Else, without `LookedOutAuto`:** the opening `Hotel_Room.280C_`, and
  `LookedOutAuto` and `+0xC7` set.
- **Else:** no opening.

So the window's comments alternate, and with the brick there are none.

**A way out** (`0x411440`): an exit to the room itself, which is the
window, plays movie 15 + `GraveLocation`, one per grave. The first way out
taken keeps its scene and sets the count to 1; after that the exit's
scene is cleared. Then the default handler runs.

**The tick** (`0x4115D0`):
1. **The window by itself.** With `+0xC7`, no scene playing and the
   opening done, `+0xC7` is cleared and the room takes the window as if
   clicked. So the first visit ends with a look out of it.
2. **The nickel.** Clicked, with Daphne idle and the room free: Daphne
   plays OBJ_DAPHNE_P20_GRAB_COIN, input held. On her step 14 the nickel
   hides. Idle again: the nickel goes in the toolbar
   (ANIM_TOOLBARBuffalo_Nickel, cursor ANIM_CURSORBuffalo_Nickel), and
   `Hotel_Room.410A_` plays, blocking.
3. **Hotspot 4** on step 11: `Hotel_Room.HOTSPOT4_`.
4. **Hotspot 2** on step 18 of its C or D: Daphne scared.

##### The stage (WP-043)

Traced 2026-11-15 for [WP-043](../work-packets/WP-043-stage.md).

**A clickable's callback.** `0x401740` stores a function at a clickable's
`+0x78` and its context at `+0x74`. When the clickable is clicked
(`0x401440`), it starts its state's sequence and sound, moves to its next
state, sends the room event, and then calls the callback with the
clickable. A sprite's `+4` is its hit type (0 never hit, 1 its cels, 2 its
step polygon); the trapdoor sets it to switch its levers and its way out
off and on.

**The sandbags' story values.** Game `+0x256` is `BagsRandomized`, and
`+0x257`–`+0x25A` are `BagDown0`–`3`: 1 when that sandbag is down on the
trapdoor. `+0x25C`–`+0x268` are `LeverAlias0`–`3`, drawn by the new game.

**ROOM_P05_Stage** (`0x417C50`, vtable `0x45EA54`; music `4`):
- **Its placements:** Scooby, Shaggy and Velma; a way down to the
  trapdoor, OBJ_P05_T0_P06, and a way out to the saloon; four sandbags,
  all OBJ_P05_STAGE_SANDBAG, told apart by their sequence's digit; Jenny;
  and two clickables.
- **Its fields:** `+0xB8` Jenny gives when idle; `+0xB9` then the thanks;
  `+0xBC`–`+0xC8` the sandbags.

| Address | What it does |
|---|---|
| `0x417CB0` (+0x08) | Reset, after the base reset: `+0xB8` and `+0xB9` cleared |
| `0x4181B0` (+0x18) | Jenny, and OBJ_P05_STAGE_TRAPDOOR, not built until Jenny has been met (`0x40A930`). The way down not built once she has. Each sandbag a sprite under layer 0 at depth -1001, kept by its digit |
| `0x417F10` (+0x0C) | Entry. See below |
| `0x417CD0` (+0x04) | The tick, after the base tick. See below |

**Entry** (`0x417F10`), after the base entry:
1. **Jenny met:**
   - Without the hammer, she hands it over: OBJ_INV_HAMMER, with
     ANIM_TOOLBARRUSTY_HAMMER and cursor ANIM_CURSORRUSTY_HAMMER.
   - Before her clue: the scene `Stage.380D2_`, blocking; her clue (game
     vtable `+0x44`); and `+0xB8`.
2. **The sandbags hung,** once, without `BagsRandomized`. Below level 2 the
   first is up and the others down; at level 2 the first is down and the
   others up. Then `BagsRandomized` is set.
3. **Each sandbag shown** only while it is down (`0x4313F0`, sprite
   `+0x14`).
4. **Shaggy walks in:** from the saloon down and left (`0x405F20`), from
   the trapdoor up and right (`0x405E60`).

**The tick** (`0x417CD0`), with Jenny there:
1. **Jenny clicked** with the arrow (released this frame, her clicked flag
   at `+8`): `Stage.1801_`, `1802_` or `1803_` (`rand() % 3`), without
   holding input.
2. **Jenny idle with `+0xB8`:** she plays GIVES (`0x4061F0`). `+0xB8` is
   cleared, `+0xB9` set, the cursor fades and input is held.
3. **Jenny idle again**, or no Jenny, with `+0xB9`: the room's exit
   handler takes the gang to ROOM_Suspect_Chooser with
   `Global.Thank_You_`.

**ROOM_P06_Stage_Trapdoor** (`0x418430`, vtable `0x45EA94`; music `4`):
- **Its placements:**
  - four levers, all OBJ_TRAPDOOR_LEVER (ANIM_TRAPDOOR_LEVER1–4);
  - four sandbags, all OBJ_TRAPDOOR_SANDBAG (ANIM_TRAPDOOR_SANDBAG1–4_DROP);
  - the way out, OBJ_TRAPDOOR_EXIT, to the stage;
  - the trapdoor, OBJ_TRAPDOOR_DOOR;
  - two clickables.

  It has no gang placements.
- **Its fields:**
  - `+0xB8`–`+0xC4`: the levers.
  - `+0xC8`–`+0xD4`: the sandbags.
  - `+0xD8`: the trapdoor.
  - `+0xDC`: the trapdoor opening.
  - `+0xE0`: the knock countdown.
  - `+0xE4`: the visits, for the opening.
  - `+0xE8`: the way out.

| Address | What it does |
|---|---|
| `0x418510` (+0x08) | Reset, after the base reset: the countdown -10, `+0xDC` and `+0xE4` cleared |
| `0x418490` (+0x30) | The opening, unplayed on every visit. Level 0: `Stage_Trapdoor.370BS_`. Levels 1 and 2: `370B_` on the first visit, `370B2_` on the second, `370B3_` after that |
| `0x418A10` (+0x18) | Each lever a clickable at depth -500, with `0x418F50` as its callback, kept by its digit. Each sandbag a sprite under layer 0 at depth y - 240, started on its last step (mode 5), on ANIM_TRAPDOOR_SANDBAG%d_RAISE if it is up. The trapdoor a sprite under layer 0 at depth -100. The way out an exit object (`0x408D20`) at depth -1000 |
| `0x418870` (+0x0C) | Entry, after the base entry: the toolbar slides off (`0x407CC0`), the room's sounds are preloaded, and the countdown is -5 |
| `0x418F50` | A lever's callback. See below |
| `0x418D50` | Move sandbag i: up and to drop, it plays ANIM_TRAPDOOR_SANDBAG%d_DROP once, `BagDown` set, `Stage_Trapdoor.TRAPDOOR_SANDBAG1_DROP`; down and to raise, its RAISE, `BagDown` cleared, `TRAPDOOR_SANDBAG1_RAISE`. The sequence changes only if the current one ends the other way |
| `0x418540` (+0x04) | The tick. See below |
| `0x4188B0` (+0x24) | A way out: with the trapdoor open and stopped, movie 4. Then the default handler |

**A lever** (`0x418F50`), unless the trapdoor is opening:
1. **The bags it moves.** The digit at the end of the lever's sequence
   picks its alias (`LeverAlias`, game `+0x25C`). The alias and the level
   pick which sandbags it moves, each the other way:

   | Alias | Level 0 | Level 1 | Level 2 |
   |---|---|---|---|
   | 0 | 1 | 1, 2 | 1, 2, 3 |
   | 1 | 2 | 2 | 2, 3, 4 |
   | 2 | 3 | 3, 4 | 3, 4, 1 |
   | 3 | 4 | 4 | 4, 1, 2 |

2. **All four up:** the trapdoor plays ANIM_TRAPDOOR_DOOROPEN once and
   `+0xDC` is set. Jenny is met (`0x40A8B0`),
   `Stage_Trapdoor.TRAPDOOR_DOOR_OPEN` plays, and the way out's hit type
   goes to 0.
3. **The levers' hit types** go to 0.

**The tick** (`0x418540`):
1. **The trapdoor open and stopped:** the room's exit handler takes the
   gang to the stage with no scene. The handler makes it movie 4, 785
   frames long.
2. **The base tick.**
3. **The knocks.**
   - Below -5, the countdown plays `Stage_Trapdoor.Knock1` and goes to 72.
   - Each tick it then counts down. Below 0 it goes back to 72, and one of
     `Knock1`–`5` or `Yell1`–`4` plays (`rand() % 9`).
   - So the first comes on the first tick after entry, then one every 74
     ticks.
4. **Every sandbag stopped** and the trapdoor shut: the levers' hit types
   go back to 2, and the levers can be clicked again.

##### The jail (WP-044)

Traced 2026-11-15 for [WP-044](../work-packets/WP-044-jail.md).

**A clickable's depth.** The default path builds a clickable with
`0x408DC0(object, 1, -1)`, and so do the classes that keep one. It calls
`0x401000` with -10000, which sets the depth from the object's
`priority=` through `0x40AD50`: -1 when there is none. A clickable's
`+0x7C` gives it the open hand with the arrow (`0x4015F0`, its vtable
`+0x18`); `0x401770` clears it.

**ROOM_P07_Jail** (`0x412E60`, vtable `0x45E910`; music `5`, no opening):
- **Its placements:**
  - Shaggy and Scooby;
  - the blanket, OBJ_INV_BLANKET, over the bunk;
  - hotspot 2, the bed under it;
  - hotspot 3, the cell door;
  - hotspot 4, the window;
  - the hole and the stool, OBJ_P07_JAIL_OVERLAY_HOLE and `_STOOL`, for
    when the bed is broken.

  It has no exit object: the hole is the only way out.
- **Its fields:**
  - `+0xB8`: hotspot 3's next line.
  - `+0xBC`: Shaggy leaving by the exit handler.
  - `+0xBD`, `+0xBE`: the blanket clicked, and Shaggy taking it.
  - `+0xC0`, `+0xC4`, `+0xC8`: the blanket, the bed, hotspot 4.
  - `+0xCC`: `BedBroken`, saved in the room's section.
  - `+0xCD`, `+0xCE`: the bed clicked, and Scooby breaking it.
  - `+0xCF`: `150D_`'s done flag (`0x40B400`'s third argument). It isn't
    saved.
  - `+0xD0`: the two going down the hole.
  - `+0xD4`, `+0xD8`: the hole and the stool.

| Address | What it does |
|---|---|
| `0x412EC0` (+0x08) | Reset, after the base reset: `+0xB8`, `+0xBC`, `+0xCC` and `+0xCF` cleared |
| `0x413690` (+0x18) | The blanket a requires object under layer 0 at depth 1, hidden once taken (`0x407060`). Hotspots 2 and 4 clickables, as the default path builds them. The hole and the stool sprites under layer 0 at depths 0 and 500, hidden unless `BedBroken` |
| `0x413600` (+0x0C) | Entry, before the base entry: what was under way is cleared. With `BedBroken`, the bed is hidden without its open hand, and the hole and the stool are shown. With `+0xCF`, the room goes straight to ROOM_P14_Tunnel_Dark (game vtable `+0x04`), and the base entry doesn't run |
| `0x413310` (+0x10) | Leave, after the base leave: a blanket clicked goes in the toolbar, and a bed clicked sets `BedBroken` |
| `0x413470` (+0x14) | The room's event. See below |
| `0x412EF0` (+0x04) | The tick, after the base tick. See below |
| `0x413370` (+0x24) | The exit handler. See below |
| `0x4138B0`, `0x4138F0` (+0x1C, +0x20) | `BedBroken` saved and read, after the base keys |

**The event** (`0x413470`). Every scene here holds input.
- **The blanket** with the arrow: `+0xBD`, input held and the cursor
  faded.
- **Hotspot 4,** moved on to its B: `Jail_Cell.150X3_`.
- **The bed,** moved on to its B: `Jail_Cell.150X1_`. Moved back to its A,
  on the second click: `+0xCD`, its hit type 0, and its B looping
  (sprite vtable `+0x24`, mode 1).
- **Hotspot 3:** `Jail_Cell.150X2_` and `150X23_` in turn.

**The tick** (`0x412EF0`). Each step waits for Shaggy or Scooby to be idle.
1. **`+0xBC`:** Shaggy is hidden, and the room goes to the dark tunnel.
2. **The blanket:** Shaggy plays OBJ_SHAGGY_P07_TAKE_BLANKET (`0x406130`),
   and the blanket is hidden. Idle again, he puts OBJ_INV_BLANKET in the
   toolbar (ANIM_TOOLBARBLANKET, ANIM_CURSORBLANKET), and
   `Jail_Cell.150C_` plays.
3. **The bed:** Scooby plays OBJ_SCOOBY_P07_BREAK_BED, with the sound
   `Scooby_Breaks_Bed`. Idle again, the bed is hidden without its open
   hand, the hole and the stool are shown, and `BedBroken` is set.
4. **`BedBroken` without `+0xCF`:** `Jail_Cell.150D_`, with `+0xCF` as its
   done flag.
5. **`+0xCF`:** Shaggy plays OBJ_SHAGGY_P07_LEAVE_JAIL in front of the
   stool (its depth + 1). Scooby is hidden, and the sound
   `Scooby_Shaggy_Fall_In_Hole` is asked for. On Shaggy's step 6 he goes
   behind the stool (its depth - 1). Idle again, the room goes to the dark
   tunnel, and Shaggy is hidden.

While steps 2, 3 and 5 are under way, input is held and the cursor faded.

**The two sounds aren't on the disc.** `0x434DC0` looks a name up as it
is, and Sfx.dat names them `Scooby.Breaks.Bed` and
`Scooby.Shaggy.Fall.In.Hole`, with dots. The original logs "Failed to
locate id" and plays nothing.

**The exit handler** (`0x413370`) never calls the default one. It acts only
when all four of these hold:
- the blanket is in a slot (`0x4070C0`);
- `+0xBC` is clear;
- no scene is playing (`+0x14`);
- the opening is done.

It then sets `+0xBC`, and Shaggy plays OBJ_SHAGGY_P07_LEAVE_JAIL. The jail
has no exit object, so on this disc the handler runs only when something
else asks for it.

##### The General Store (WP-045)

Traced 2026-11-15 for [WP-045](../work-packets/WP-045-general-store.md).

**A file's volume.** `0x434B60` sets the volume of the sound file that
holds a clip (the file's `+0x18`, through `0x43C940`), as a percent of
each clip's own. It applies to that clip if it is playing, and to every
clip the file plays after. `0x434BA0` gives the seconds a clip has
played: the play cursor over the bytes per second (`0x4451F0`).
`0x434CE0` is true when it isn't playing.

**ROOM_P10_Front_Of_General_Store** (`0x40F6E0`, vtable `0x45E78C`;
music `2`):
- **Its placements:**
  - the gang;
  - the clock over the door, OBJ_INV_CLOCK, a requires object that
    answers the rusty hammer;
  - the clock without its face, OBJ_P10_FRONT_OF_GS_CLOCK_NOFACE;
  - hotspot 1, right of the door;
  - hotspot 2, the door;
  - hotspot 3, the sign.
- **Its fields:**
  - `+0xB8`, `+0xBC`: the clock and the faceless clock.
  - `+0xC0`: the clock broken; movie 2 when free.
  - `+0xC4`: the clock's next line.
  - `+0xC8`: hotspot 1 clicked.

| Address | What it does |
|---|---|
| `0x40F740` (+0x08) | Reset, after the base reset: `+0xC0` and `+0xC4` cleared |
| `0x40F890` (+0x30) | The opening. While `MoaningActive` it is `Front_of_General_Store.110A_`, unplayed. Otherwise there is none, and its played flag stays as it was (`0x40C6B0`) |
| `0x40FA40` (+0x18) | The clock a requires object (`0x408C80` with -1, as the default path builds one). The faceless clock a sprite under layer 1 (game `+0x5C`) at depth 1 |
| `0x40FB70` (+0x0C) | Entry, after the base entry. With the hammer used, OBJ_INV_CLOCK goes in the toolbar (ANIM_TOOLBARBROKEN_CLOCK, ANIM_CURSORBROKEN_CLOCK) and the clock is hidden. Otherwise the faceless clock is hidden. From Street 2, Fred walks in down and left. `+0xC8` is cleared |
| `0x40F8D0` (+0x14) | The room's event. See below |
| `0x40F760` (+0x04) | The tick, after the base tick. See below |

**The event** (`0x40F8D0`). Every scene here holds input.
- **The clock with the hammer:** `Front_of_General_Store.Take_Clock_`.
  `+0xC0` is set, the hammer is used up (`0x406C80`), and the cursor is
  the arrow again.
- **The clock otherwise:** `A_Clock_`, `A_Clockb_` and `A_Clockb3_` in turn.
- **The door:** `Door_Locked_` or `Door_Lockedb_`, by `rand() & 1`.
- **Hotspot 3:** `110X_`.
- **Hotspot 1:** `+0xC8`.

**The tick** (`0x40F760`):
1. **`+0xC0`, no scene and the opening done:** the gang comes back to the
   same room through movie 2 (game vtable `+0x08`). Movie 2 breaks the clock.
2. **`+0xC8`:** Scooby is scared (state `0x11`) as soon as neither of hotspot
   1's sounds, `SFX_P10_FRONT_OF_GS_HOTSPOT1A` and `1B`, is playing in its
   first half second.

**ROOM_P15_General_Store_Interior** (`0x4125D0`, vtable `0x45E8D0`;
music `5`, no opening):
- **Its placements:**
  - the gang;
  - the rattlesnakes, OBJ_P15_GSI_SNAKE, a requires object that answers the
    blanket;
  - the lantern, OBJ_INV_LANTERN, on the window ledge;
  - hotspots 1 to 5.
- **Its fields:**
  - `+0xB8`, `+0xBC`: the snake and the lantern.
  - `+0xC4`: hotspot 1's count.
  - `+0xC8`: the snake's next line.
  - `+0xCC`: a strike waiting.
  - `+0xCD`: `Click_Blanket_On_Snake_`'s done flag (`0x40B400`'s third
    argument).
  - `+0xCE`: Fred tossing the blanket.
  - `+0xCF`: the lantern clicked.
  - `+0xD0`: Fred taking the lantern.

| Address | What it does |
|---|---|
| `0x412630` (+0x08) | Reset, after the base reset: `+0xC4` cleared |
| `0x412BD0` (+0x18) | The snake a requires object, as the default path builds it. With the blanket used, `Snake_Idle` plays at 93% of its file (`0x434B60`), and the snake is on ANIM_P15_GSI_SNAKEBLANKET, looping, at depth 500. Otherwise it waits on ANIM_P15_GSI_SNAKEIDLE, stopped. The lantern a requires object under layer 0 until it has been taken |
| `0x412DF0` (+0x0C) | Entry, after the base entry: `+0xC8` to `+0xD0` cleared. From the back alley, Shaggy walks in down and left |
| `0x4129B0` (+0x10) | Leave, after the base leave: a lantern clicked goes in the toolbar |
| `0x412A00` (+0x14) | The room's event. See below |
| `0x412650` (+0x04) | The tick, after the base tick. See below |

**The event** (`0x412A00`). Every scene here holds input.
- **The snake with the blanket:** the blanket is used up and the arrow is
  back. `General_Store_Interior.Click_Blanket_On_Snake_` plays, with
  `+0xCD` as its done flag.
- **The snake otherwise,** or **the lantern with the arrow before the
  blanket is used:** `Click_On_Snake_`, `Click_On_Snakeb_` and
  `Click_On_Snakec_` in turn, and `+0xCC`.
- **The lantern with the arrow, the blanket used:** `+0xCF`.
- **Hotspot 1:** `120X_`. Its count goes back to 0 each time, so it is
  always this line.
- **Hotspot 2:** `120X2_`.

**The tick** (`0x412650`):
1. **The snake stopped:** `Snake_Idle`, and ANIM_P15_GSI_SNAKEIDLE looping.
2. **`+0xCD`:** Fred waits until he is idle, no scene plays and the opening
   is done. Then he plays OBJ_FRED_P15_TOSS_BLANKET. Idle again, he leaves
   the snake under the blanket at depth 500, and `Snake_Idle`'s file goes
   to 93%. Input is held until then, and freed after.
3. **`+0xCF`:** Fred waits as in step 2. Then the lantern is hidden,
   `Fred_Takes_Lantern` is asked for, and he plays
   OBJ_FRED_P15_GRAB_LANTERN. On his step 62 the lantern goes in the
   toolbar (ANIM_TOOLBARLANTERN, ANIM_CURSORLANTERN). Idle again, he says
   `Click_On_Lantern_`. Input is held until then.
4. **`+0xCC` on the snake's step 0:** `Snake_Idle` stops, `Snake_Attack`
   plays, and the snake strikes once (ANIM_P15_GSI_SNAKEANIM).

**`Fred_Takes_Lantern` isn't on the disc** under that name: Sfx.dat has
`Fred.Takes.Lantern`. Like the jail's two, it plays nothing.

##### The Sheriff's office (WP-046)

Traced 2026-11-15 for [WP-046](../work-packets/WP-046-sheriffs-office.md).

**ROOM_P02_Sheriffs_Office** (`0x4163A0`, vtable `0x45E9D0`; music `5`):
- **Its placements:**
  - Shaggy, Scooby and Velma;
  - the cell door, OBJ_P02_DOOR, a requires object that answers the oil
    can;
  - the way into the jail behind it, OBJ_P02_TO_P07 (movie 29);
  - the way out to Street 1;
  - hotspot 1, a clickable;
  - hotspot 4, a clickable over Shaggy.
- **Its fields:**
  - `+0xB8`: the stuck door's next line.
  - `+0xBC`: the door clicked.
  - `+0xBD`: Shaggy at the door.
  - `+0xBE`, `+0xBF`: the sandwich, and Shaggy eating it.
  - `+0xC0`: hotspot 4's C clicked.
  - `+0xC4`, `+0xC8`, `+0xCC`: the door, hotspot 1, hotspot 4.

| Address | What it does |
|---|---|
| `0x416680` (+0x30) | The opening, unplayed: `Sheriffs_Office.140A_` while `MoaningActive`, otherwise none |
| `0x416C30` (+0x18) | The door a requires object under layer 0 at depth 1. With the oil can used it is on ANIM_P02_DOOROPEN, or ANIM_P02_DOORBED_GONE once the blanket has been taken. The way into the jail isn't built once the blanket has been taken. Hotspots 1 and 4 are clickables, as the default path builds them |
| `0x416400` (+0x0C) | Entry, after the base entry: `+0xB8` to `+0xBF` cleared, the two Shaggy sounds preloaded, and the snacks needed (`+0x24`) set to level + 2 |
| `0x416AA0` (+0x14) | The room's event. See below |
| `0x4166C0` (+0x04) | The tick, after the base tick. See below |
| `0x416470` (+0x24) | The exit handler. Into the jail with fewer snacks given here (`+0x88`) than level + 2, it plays `150A_`, `150A2_` or `150A3_` by level, held, and the snack box flashes (`0x40D4D0`). Otherwise, and for every other exit, it calls the default handler |

**The event** (`0x416AA0`):
- **The door:** with the oil can, the oil can is used up and the arrow is
  back. Either way `+0xBC` is set, input is held and the cursor fades.
- **Hotspot 1,** moved on to its B: `Sheriffs_Office.140X_`; to its E:
  `140X3_`. Held.
- **Hotspot 4,** by the sequence it plays (sprite `+0x54`): A
  `HOTSPOT4A_`, B `HOTSPOT4A2_`, both held. C sets `+0xC0`.

**The tick** (`0x4166C0`). Shaggy's steps wait until he is idle, no scene
plays and the opening is done.
1. **`+0xC0` and hotspot 4 stopped:** the sandwich (`+0xBE`).
2. **The sandwich:** Shaggy plays OBJ_SHAGGY_P02_SANDWICH, with
   `Global.Idle.SHAGGY_S1_E`. Idle again, input is free. Input is held
   until then.
3. **The door** (`+0xBC`), with input held until Shaggy is idle again.
   - **With the oil can used, and the blanket not yet taken:** Shaggy plays
     OBJ_SHAGGY_P02_OIL_DOOR, with `Shaggy.Oils.Door`, and the door is
     hidden. Idle again, the door shows on ANIM_P02_DOOROPEN, and input is
     free.
   - **Otherwise:** Shaggy plays OBJ_SHAGGY_P02_NO_OIL_DOOR, with
     `Shaggy.Shakes.Bars`. Idle again, `150A1_`, `150A12_` and `150A13_`
     play in turn, not held.

##### The back alley (WP-047)

Traced 2026-11-15 for [WP-047](../work-packets/WP-047-back-alley.md).

**ROOM_P19_Back_Alley** (`0x40E7A0`, vtable `0x45E70C`; music `5`,
opening `Back_Alley.350A_`):
- **Its placements:**
  - the gang;
  - the way into the General Store;
  - the way to the bank vault;
  - hotspots 1 to 5. Hotspot 1 is under layer 1, at `priority=1`.
- **Its fields:** `+0xB8` and `+0xBC`, hotspots 3 and 1.

| Address | What it does |
|---|---|
| `0x40EAC0` (+0x18) | Hotspots 3 and 1, as the default path builds them (`0x408DC0` with 1, -1) |
| `0x40E800` (+0x0C) | Entry, after the base entry. `Back_Alley.Snakes_Distant` plays, and the snacks needed (`+0x24`) are level + 2. From the General Store, Fred walks in up and left (`0x405EE0`). From the bank vault or the open safe, Shaggy walks in up and right (`0x405E60`) |
| `0x40EBC0` (+0x04) | The tick, after the base tick. See below |
| `0x40E8B0` (+0x24) | The exit handler. Into the store with fewer snacks given here (`+0x88`) than level + 2, it plays `350B_`, `350B2_` or `350B3_` by level, held, and the snack box flashes. Otherwise, and for the way to the vault, it calls the default handler |

**The tick** (`0x40EBC0`):
1. **Hotspot 3 playing, on step 0, with a sequence ending in B:**
   `Back_Alley.HOTSPOT3B_` or `HOTSPOT3B2_`, by `rand() & 1`, not held.
   The B has one step, so this comes on each of its three ticks. The
   first starts the line; the scene playing stops the other two.
2. **Hotspot 1 on its step 8:** Daphne and Scooby are scared (state
   `0x11`).

**The ways in** use the walk-in entry points by direction: `0x405E60` UR,
`0x405EA0` DR, `0x405EE0` UL, `0x405F20` DL. Each keeps the character's
depth (`+0x9C`) and puts it 50 behind or in front.

##### The post office (WP-048)

Traced 2026-11-15 for [WP-048](../work-packets/WP-048-post-office.md).

**ROOM_P08_Post_Office** (`0x413930`, vtable `0x45E950`; music `2`):
- **Its placements:**
  - the gang, set B;
  - the way out to Street 1;
  - two holes in the floor down to the lit tunnel, OBJ_P08_POST_OFFICE_HOLE
    and `_HOLE_LIT`;
  - hotspots 1 to 3.
- **Its fields:**
  - `+0xB8`: the dark hole's next line.
  - `+0xBC`: hotspot 3's next line.
  - `+0xC0`: `OldRoomName`, saved in the room's section.
  - `+0xC8`, `+0xCC`: hotspots 3 and 2.
  - `+0xD0`: `160C_`'s done flag.
  - `+0xD1`: Fred tossing the lantern.
  - `+0xD4`, `+0xD8`: the lit hole and the dark one.

| Address | What it does |
|---|---|
| `0x413A00` (+0x08) | Reset, after the base reset: `+0xB8` and `+0xBC` cleared, and `OldRoomName` set to ROOM_P03_Street1 |
| `0x413F40` (+0x18) | The holes are exits at depth -1000 (`0x408D20`). The dark one is hidden with `TunnelLit` (game `+0x275`), the lit one without it. Hotspot 2 is a clickable under layer 1 (game `+0x5C`), and hotspot 3 is one as the default path builds it |
| `0x413EE0` (+0x2C) | The opening, unplayed: `Post_Office.160A_` while `MoaningActive`, `160D_` up from the dark tunnel. Otherwise there is none, and its played flag stays as it was |
| `0x413A30` (+0x0C) | Entry, after the base entry. The room come from is `OldRoomName`, unless it is the dark tunnel or Street 1. From the dark tunnel, Fred, Daphne and Velma are hidden, and hotspots 2 and 3 lose their open hand. Otherwise, before the lantern has been had, Scooby, Shaggy and Velma are hidden. `OldRoomName` is then the room come from |
| `0x4140F0` (+0x14) | The room's event. Hotspot 3 gives `P08_POST_OFFICE_HOTSPOT3A_`, `3B_` and `3C_` in turn. Hotspot 2, moved on to its C, gives `Post_Office.160X4_`. Both are held |
| `0x413BC0` (+0x24) | The exit handler. See below |
| `0x414270` (+0x04) | The tick, after the base tick. See below |
| `0x4141D0`, `0x414210` (+0x1C, +0x20) | `OldRoomName` saved and read, after the base keys |

**The exit handler** (`0x413BC0`). Down to the lit tunnel without the
lantern used, the gang stays, and a line plays, held:
- **With Daphne shown:** `160AA_` (or `160B_` once Artie has been met),
  `160B2_` and `160B3_` in turn.
- **With only Shaggy and Scooby:** `380A_` or `380A1_` (`rand() & 1`).

Otherwise, and for the way to Street 1, it calls the default handler.

**The tick** (`0x414270`):
1. **`160C_` over:** Fred waits until he is idle, no scene plays and the
   opening is done. Then he plays OBJ_FRED_P08_HOLD_LANTERN, with
   `Fred.Tosses.Lantern`. Input is held from the scene's end. On his step
   15 the dark hole is hidden and the lit one shown, and the room goes to
   the lit tunnel (game vtable `+0x04`).
2. **The dark hole clicked** (its `+8`) with ANIM_CURSORLANTERN as the
   cursor: the lantern is used up and the arrow is back. `TunnelLit` is
   set, and `160C_` plays, held, with `+0xD0` as its done flag.

##### The railroad station (WP-049)

Traced 2026-11-15 for [WP-049](../work-packets/WP-049-railroad-station.md).

**ROOM_P09_Railroad_Station** (`0x4207C0`, vtable `0x45EE28`; music `2`):
- **Its placements:**
  - the gang;
  - Gummy and his donkey, the characters GUMMY and DONKEY;
  - the way back to Street 2;
  - the way to the chase, OBJ_P09_TO_P40 (movie 32);
  - hotspots 1 to 3. Hotspot 2 is at `priority=100000`, hotspot 3 at 200.
- **Its fields:**
  - `+0xB8`, `+0xBC`: hotspots 2 and 3.
  - `+0xC0`: Gummy gives his clue when idle.
  - `+0xC1`: then the thanks.
  - `+0xC8`: Gummy's next hint.

| Address | What it does |
|---|---|
| `0x420820` (+0x08) | Reset: `+0xC0`, `+0xC1`, `+0xC4` and `+0xC8` cleared. It doesn't call the base reset (`0x40CD20`) |
| `0x4213C0` (+0x18) | OBJ_GUMMY* and OBJ_DONKEY* aren't built until Artie has been met, and the way to the chase isn't built until Gummy's clue has been given. Hotspots 2 and 3 are clickables, as the default path builds them |
| `0x4212C0` (+0x2C) | The opening, unplayed: `Railroad_Station.Intro_`, or `110A_` while `MoaningActive`. With the whistle puzzle solved (`GummyPuzzle`, game `+0x274`) and his clue not yet given, Gummy's next hint instead. Back from the station itself, `220DP_` |
| `0x4210F0` (+0x0C) | Entry, after the base entry. See below |
| `0x421070` (+0x14) | The room's event: hotspot 2, moved on to its B, `HOTSPOT2A_`; to its C, `HOTSPOT2B_`. Held |
| `0x420840` (+0x04) | The tick, after the base tick. See below |
| `0x421680` | Gummy's next hint: `220C_`, `220C2_`, `220C3_` in turn (`+0xC8`). With the dentures had, it goes back to `220C_` after `220C2_` |
| `0x4119E0` | The room's own name (`+8`) |

**Entry** (`0x4210F0`):
1. **Before the puzzle, with Artie met,** Gummy SLEEPS, looping
   (`0x406210`).
2. **After it,** the donkey's hit type is 0.
3. **With his clue given,** Gummy and the donkey stand 100 further right
   (their `+0xC`).
4. **Back from the station itself,** Gummy's clue is given (game vtable
   `+0x44`) and `+0xC0` is set.
5. **From Street 2,** Shaggy walks in down and right (`0x405EA0`).

**The tick** (`0x420840`):
1. **Gummy clicked** (its `+8`, on the release):
   - **With the dentures, the puzzle solved:** the dentures are used up and
     the arrow is back. The room's exit handler takes the gang to the
     station itself, with `220D_` and movie 30.
   - **With the arrow, before the puzzle:** the exit handler takes the gang
     to ROOM_Gummy.
   - **With the arrow, after the puzzle:** his next hint, held, until his
     clue has been given. After that, `Global.1000GA_`, `GB_` or `GC_`
     (`rand() % 3`), not held.
2. **No scene, the opening done, Gummy idle, and `+0xC0`:** Gummy plays
   GIVES. `+0xC1` is set, and input is held.
3. **`+0xC1`, with Gummy idle, looping, or not here:** the thanks
   (`Global.Thank_You_`) take the gang to ROOM_Suspect_Chooser.
4. **The donkey clicked with the arrow:** to ROOM_Gummy.
5. **Hotspot 3 on step 8 of its C:** Scooby is scared.

##### Gummy's whistle puzzle (WP-050)

Traced 2026-11-15 for [WP-050](../work-packets/WP-050-gummy.md).

**ROOM_Gummy** (`0x40FC40`, vtable `0x45E7D0`; music `Gummy.Music`, which
isn't on the disc; opening `Gummy_Puzzle.220B_`):
- **Its placements:**
  - Gummy asleep, OBJ_GUMMYSLEEP_GUMMY;
  - his donkey;
  - five bells, all OBJ_GUMMYSLEEP_BELLS, told apart by their sequence's
    digit;
  - the way back to the station.
- **Its fields:**
  - `+0xB8`–`+0xC8`: the bells.
  - `+0xCC`, `+0xD0`: the donkey and Gummy.
  - `+0xD4`: the whistle.
  - `+0xD8`: Gummy whistles again.
  - `+0xD9`: the bells play the tune back.
  - `+0xDC`: the sound waited for.
  - `+0xE0`: the tune's length.
  - `+0xE4`: its notes, as digits.
  - `+0xEC`: the next note.
  - `+0xF0`: the notes played back.
  - `+0xF4`–`+0x104`: each bell's note.
  - `+0x108`: the ticks to the station once the tune is rung.
  - `+0x10C`, `+0x110`: the donkey's blink and Gummy's snore.
  - `+0x114`: `220B2_`'s done flag.
  - `+0x118`: the state.

| Address | What it does |
|---|---|
| `0x410760` (+0x18) | The bells are clickables without the ghost (`0x408DC0` with 0, -1): bell 1 at depth 4, the others at 10, each with `0x410A00` as its callback. Gummy is a requires object on his snore, stopped, hit by his cels. The donkey is a sprite at depth 5, playing its idle once |
| `0x4102C0` (+0x0C) | Entry, after the base entry. See below |
| `0x4109B0` (+0x14) | The room's event: Gummy clicked, with the bells free in state 3, sets `+0xEC` to 0 and `+0xD8` |
| `0x410A00` | A bell's callback. See below |
| `0x40FD10` (+0x04) | The tick, after the base tick. See below |

**Entry** (`0x4102C0`):
1. **Set-up:** the toolbar slides off, the music file stops, and `rand()`
   is reseeded from the clock.
2. **The tune,** unless the gang is back from the quit screen: one of the
   level's three, by `rand() % 3`.

   | Level | Whistle | Tune | Bells' notes |
   |---|---|---|---|
   | 0 | `Gummy.Whistle1a`, `2a`, `3a` | `87656`, `77456`, `88645` | 4 5 6 7 8 |
   | 1 | `Gummy.Whistle1b`, `2b`, `3b` | `7844345`, `6665565`, `4566554` | 3 4 5 7 8; then 4 5 6 7 8 for `2b` and `3b` |
   | 2 | `Gummy.Whistle1c`, `2c`, `3c` | `76543454`, `41414564`, `456889864` | 3 4 5 6 7; 1 2 4 5 6; 4 5 6 8 9 |

3. **The rest:**
   - `+0xD8` is set, and `+0x108` is 1000000 (never).
   - The whole tune will be played back.
   - The snore comes in 108 ticks, and the blink in `(rand() & 7 + 3) * 36`.
   - The state is 3 if the opening has played, 0 otherwise.

**The tick** (`0x40FD10`). A sound is over when it isn't playing
(`0x434CE0`).
- **State 0,** the opening played: Gummy whistles, input is held, and it
  goes to state 1.
- **State 1,** the whistle over: `Gummy_Puzzle.220B2_` plays, held, with
  `+0x114` as its done flag. Then state 2.
- **State 2,** `220B2_` over: state 3.
- **State 3:**
  1. **Input** is held while `+0xD8` or `+0xD9` is set.
  2. **The sound waited for, over:**
     - **With `+0xD8`,** Gummy whistles again, and `+0xD9` is set.
     - **With `+0xD9`,** each note of the tune in turn plays
       `Gummy.Bell<digit>`, and every bell with that note rings. A ring
       (`0x401840`, the clickable's `+0x80`) waits until the bell is free.
     - **After the last note,** `+0xD9` is cleared and input is freed.
  3. **The station:** once the tune is rung, `+0x108` counts down, and
     below 0 the room's exit handler takes the gang to the station.
  4. **Gummy snores** every 108 ticks: `Gummy.Snore`, and his snore plays
     once.
  5. **The donkey** blinks or idles once (`rand() & 1`) every 3 to 10
     seconds, and is back on its idle, stopped, after a blink.
- **In every state,** while Gummy whistles, his step follows the whistle's
  lip sync (`0x434D40`).

**A bell's callback** (`0x410A00`). While `+0xD9` is set it does nothing.
Otherwise the bell plays `Gummy.Bell<its note>`:
- **The tune's next note:** it moves on. On the last note:
  - the cursor fades;
  - `GummyPuzzle` (game `+0x274`) is set;
  - Gummy is met (`0x40A8B0`);
  - the station comes 72 ticks later.
- **A wrong note:**
  - the notes played back become at least the notes reached + 1;
  - the tune starts over;
  - `+0xD8` is set.

  The bells free up in the same frame, before the room's tick, so Gummy
  whistles again at once.

##### The saloon and Artie (WP-051)

Traced 2026-11-15 for [WP-051](../work-packets/WP-051-saloon.md).

**ROOM_P12_Saloon** (`0x414430`, vtable `0x45E990`; music group 3; opening
`Saloon.360A_`). Artie is gagged and in three chains. Three keys hide
behind three of six hotspots; each one used takes a chain off in
ROOM_Artie.

**Its fields:**
- **`+0xB8`:** the piano (hotspot 1).
- **`+0xBC`:** the ticks to the next moan.
- **`+0xC0`:** music group 3 again once the piano stops.
- **Artie and the piano:**

  | Field | Key | Reset |
  |---|---|---|
  | `+0xC1` | `ArtieMasked` | 1 |
  | `+0xC4` | `ArtieChained` | 3 |
  | `+0xC8` | `ShaggyPiano` | 0 |

- **`+0xCC` + 16k, for hotspots 3–8 (k 0–5):**

  | Offset | What it holds | Key |
  |---|---|---|
  | `+0xCC` | the key shows | `KeyVisible%i` |
  | `+0xCD` | a key hides behind the hotspot | `KeyHidden%i` |
  | `+0xD0` | the hotspot | — |
  | `+0xD4` | its key | — |
  | `+0xD8` | the key shows once the hotspot stops | — |

- **`+0x12C`–`+0x131`:** `ClickableOpen%i`.
- **The thanks:** `+0x132` (Artie gives his clue when idle), then `+0x133`
  (the thanks).
- **`+0x134`:** the buffer sprite.
- **`+0x138`:** `BullRidden`.
- **`+0x13C`:** the bull's line.
- **`+0x140`–`+0x142`:** the gag coming off.

| Address | What it does |
|---|---|
| `0x414490` (+0x08) | Reset, after the base reset: the table above, the moan at 36, and three keys hidden by `rand() % 6` |
| `0x414FC0` (+0x18) | Placements. See below |
| `0x414540` (+0x0C) | Entry, after the base entry. See below |
| `0x414910` (+0x04) | The tick, after the base tick. See below |
| `0x415660` (+0x14) | The room's event. See below |
| `0x415C30` (+0x24) | The exit handler. See below |
| `0x4148D0` (+0x34) | Idle chatter: with Artie free (`+0xC4` = 0), `Saloon.1100C_` (its `rand() & 1` always passes) |
| `0x414820` (+0x10) | Leave, after the base leave: `ClickableOpen` is whether each hotspot's state ends in `B` |
| `0x416000` / `0x4161D0` (+0x1C / +0x20) | The keys: `ArtieMasked`, `ArtieChained` (`%i`, `0x40C5E0` / `0x40C670`), `ShaggyPiano`, `BullRidden`, `ClickableOpen0`–`5`; once ungagged, `KeyHidden%i` and `KeyVisible%i` for each hotspot |

**Placements** (`0x414FC0`). The first claim builds a `RENDER_ENTITY`: a
640 × 480 buffer sprite (`0x4370D0`) under the first layer (game `+0x58`)
at depth −1001. Everything below goes under it, but the bull:
- **The piano,** hotspot 1: a clickable (`0x408DC0` with 1) at depth −11,
  on its `B` (`0x401780`) once played.
- **Hotspots 2–8 and the keys:** clickables at `0x408DC0`'s depth
  (`priority=`, −1 without one). The keys are hidden (`0x4313F0`).
- **Hotspots 3–8:**
  - while Artie is gagged, without the open hand (`0x401770` clears the
    clickable's `+0x7C`);
  - one left open, on its `B`;
  - one with a key behind it, on its `K`.

  Each is stopped on step 0.
- **The open door:** a sprite (`0x430790`) at depth 0, looping, once the
  hotel hall's door is open (`HotelHallDoor`, game `+0x255`); else not
  built.
- **The chandelier:** a sprite at depth −1, looping, until the nickel is
  used. Used means had (`0x407060`) and in no slot (`0x4070C0`). Once used,
  it is not built.
- **The bull:** a requires object (`0x408C80` with −1: layer 0), looping
  `MECHBULLA`, or `MECHBULLB` once the nickel is used.
- **The way to Pie Noon:** not built while Artie is chained.

**Entry** (`0x414540`):
1. **Walk-ins:** from the hotel hall, Fred walks in `UR`; from Street 3,
   Daphne `UL`; from the stage, Velma `U`.
2. **Artie:**
   - chained, he is in his chains: the set `_<n>` (`0x406230`, the
     character's `+0x60`) and idle, `OBJ_ARTIE_<n>`;
   - gagged, `OBJ_ARTIE_MASKED` (`0x406190`: the object in `+0x8C`, state
     `0xE`, `ANIM_ARTIE_MASKED1` looping);
   - ungagged, at depth −1.
3. **Free, and not yet a clue owner:**
   - `Saloon.360C_` (`rand() % 3` = 0) or `360C3_`, held;
   - his clue (game vtable `+0x44`), and Artie met (`0x40A8B0`);
   - `+0x132`.
4. **The rest:**
   - the keys showing are shown at depth 1;
   - the nickel used and the pump handle never had, the pump handle goes
     in a slot;
   - the snacks needed (`+0x24`) are the level + 2.

**The tick** (`0x414910`):
1. **The moans:** `+0xBC` counts down every tick. Below 1 with
   `MoaningActive`, `Saloon.Moan.1`–`4` (`rand() & 3`), and the next in
   `(rand() % 10 + 5) × 36`.
2. **The piano** stopped with `+0xC0`: music group 3 (`0x40AA10`).
3. **Artie clicked** (game `+0x20` & 4 and his `+8`) with the arrow:
   - gagged, `+0x140`;
   - chained, `Saloon.360D2_`, held;
   - free, `Saloon.1601_`, `1701_` or `1801_`.
4. **Artie idle:**
   - with `+0x132`, he plays `GIVES` (`0x4061F0`) and input is held
     (`+0x133`);
   - idle again, `Global.Thank_You_` and `ROOM_Suspect_Chooser`, through
     the room's own exit handler.
5. **A key found:** shown at depth 1 once its hotspot stops, with
   `Saloon.360G_`, `360G2_` or `360G3_`.
6. **The gag** (`+0x140`), input held. With Velma idle, no scene and the
   opening done, she plays `OBJ_VELMA_P12_UNGAG_ARTIE` (`0x406130`) and
   `+0x141` is set. Then:
   - **her step 6:** `Saloon.360D_1_VELMA` plays once (`+0x142`), and the
     idle timer starts again;
   - **her step 33:** Artie is idle (ungagged), and `MoaningActive` is off;
   - **Velma idle:** Artie is ungagged (`+0xC1`), hotspots 3–8 get the
     open hand (`0x401760`), and `Saloon.GAG_GONE_` plays, held.
7. **Shaggy clicked with the nickel:** the bull's event with success, and
   the arrow.

**The room's event** (`0x415660`):
- **The piano:**
  - the first time, `Saloon.Piano_`;
  - moved on to anything but its `B` (it plays its tune), music group −1
    and `+0xC0`;
  - on its `A`, it goes to its `B`.
- **Hotspots 3–8,** once ungagged: a key behind one is found (`+0xD8`), and
  the hotspot goes to its state with `B`.
- **A key:**
  - hidden, and no longer showing;
  - a chain fewer (`+0xC4`);
  - the room's own exit to ROOM_Artie, with no scene.
- **The bull with the nickel:**
  - movie 5 and the saloon again (game vtable `+0x08`);
  - the nickel out of its slot (`0x406C80`), and the arrow;
  - `BullRidden`.
- **The bull without the nickel:** `Saloon.390A_`, `390A2_`, `390A3_` in
  turn; once it is used, `Saloon.120E2_`. Held.

**The exit handler** (`0x415C30`). Anywhere but ROOM_Artie:
- **Gagged, or chained with no key showing:** `Saloon.360A1_`, `360A2_`,
  `360A3_` or `Must_Free_Artie_` (`rand() & 3`), held. The gang stays.
- **Chained, with keys showing:** `Saloon.340A2_`, `G3_` or `360D3_`. It is
  `rand() & 1` with one key, `rand() % 3` with more. Held, and the gang
  stays.
- **To the stage without the level's snacks** (`+0x88` against level + 2):
  `Saloon.380A_`, `380A2_`, `380A3_` by level, held, and the snack box
  flashes (`0x40D4D0`).

Otherwise the default handler.

**ROOM_Artie** (`0x40D4E0`, vtable `0x45E68C`; music group 3; no opening).
Field `+0xB8` is `ChainsLocked`, 3 at reset (`0x40D540`); `+0xBC` the
chains; `+0xC0` a countdown.
- **Placements** (`0x40D6D0`): `OBJ_CHAINS` a sprite under the first layer
  at depth 0, on `ANIM_CHAINSA`, `B` or `C` by `ChainsLocked` 3, 2, 1,
  stopped on step 0.
- **Entry** (`0x40D680`):
  - input is held;
  - the cursor fades (`0x435150`, `0x12`);
  - the toolbar is hidden (`0x407CC0`);
  - the countdown is 36.
- **The tick** (`0x40D560`). Input is held. With the chains stopped, the
  countdown runs down:
  - **on step 0,** they play once (`graphics_AnimSprite_Start` 3, 3, −1)
    with `Artie.Chains_A`, `B` or `C`, and 36 more;
  - **played,** a chain fewer, and the saloon (game vtable `+0x04`); once
    none is left, through movie 6 (`+0x08`).
- **Keys** (`0x40D820` / `0x40D860`): `ChainsLocked` (`%i`).

##### The Sheriff's quiz (WP-052)

Traced 2026-11-15 for [WP-052](../work-packets/WP-052-sheriff-quiz.md).

**ROOM_Sheriff** (`0x416E20`, vtable `0x45EA10`; music group 5; no
opening). Street 1's class sends the gang here when the Sheriff is clicked
before his puzzle is done. Its fields:

| Field | What it holds |
|---|---|
| `+0xB8` | `CurrentQuestion`: the page less 1, −1 for none |
| `+0xBC` | the notebook |
| `+0xC0`–`+0xCE` | `Question0`–`14`: answered |
| `+0xD0`–`+0xDC` | the answers, A to D |
| `+0xE0`–`+0xEC` | their sounds |
| `+0xF0` | the page's sound |
| `+0xF4` | the sound waited for |
| `+0xF8` | the sound of what the mouse is over |
| `+0xFC` | its countdown |
| `+0x100` | the next page once the sound is over |
| `+0x104` | the state: 0 the page, 1–4 its answers, 5 free |
| `+0x108` | Street 1 once the sound is over |
| `+0x109` | a wrong answer |

`graphics_AnimSprite_Play(s, a, b, c)` (`0x430A80`) is
`graphics_AnimSprite_Start(s, b, c, a)`. Here it is always called with
mode 0, so it shows step `a`, stopped. The notebook and the answers have
three such steps: 0 at rest, 1 lit up, 2 pressed.

| Address | What it does |
|---|---|
| `0x416E80` (+0x08) | Reset, after the base reset: nothing answered, `+0xB8` −1, the sounds none |
| `0x417530` (+0x18) | Placements. `OBJ_SHERIFF_NOTEBOOK` a sprite under the first layer (game `+0x58`) at depth 0, looping. Each of the four `OBJ_SHERIFF_ANSWERS1` (kept by its sequence's letter) a requires object (`0x408C80` with −1) at depth 10, stopped on step 0, its callback (`0x402FF0`) the room's vtable `+0x40` through `0x4047F0`. The exit back to Street 1 is the default path's |
| `0x417220` (+0x0C) | Entry, after the base entry: the toolbar hidden (`0x407CC0`); `+0x108`, `+0x109` clear; with no question, one drawn (`rand() % 15` until it isn't 2, 5 or answered); then the page (`0x417300`) |
| `0x417300` | The page. With the level's count answered (level + 2), page 3, the last. The notebook on `ANIM_SHERIFF_NOTEBOOKPAGE<page>` (looping), its sound `Sheriff.NOTEBOOKPAGE<page>`. Each answer to the object `OBJ_SHERIFF_ANSWERS<page>` (`0x4313C0`) on `ANIM_SHERIFF_ANSWERS<page><letter>`, stopped on step 0, its sound `Sheriff.NOTEBOOKPAGE<page>_<letter>`. State 0. Page 3 has no such object: its answers show nothing |
| `0x416ED0` (+0x04) | The tick. See below |
| `0x4176E0` (+0x40) | An answer clicked. See below |
| `0x4172C0` (+0x10) | Leave, after the base leave: the level's count answered sets `SheriffPuzzle` (game `+0x26C`) |
| `0x4179B0` / `0x417A80` (+0x1C / +0x20) | The keys: `CurrentQuestion` (`%i`, atoi), `Question0`–`14` |

**The tick** (`0x416ED0`). Input is held (game `+0x24`) and the cursor
fades every tick. The rest waits until the sound waited for (`+0xF4`) is
over (`0x434CE0`):
1. **`+0x108`:** to `ROOM_P03_Street1` (game vtable `+0x04`).
2. **`+0x109`:** `Ewan.NOTEBOOKPAGE_ANSWER_WRONG_2`, then `+0x108`. The
   disc's line is `Sheriff.NOTEBOOK_ANSWER_WRONG_2`, so nothing plays.
3. **`+0x100`:** the next page (`0x417300`).
4. **By state:**
   - **0:** the page's sound, the page on step 1.
   - **1–4:** the page and the answers on step 0, the answer read on step
     1, and its sound.
   - **5:** input free, the cursor shown. What the mouse is over (its `+8`)
     is on step 1, the rest on step 0. Its sound goes in `+0xF8` and
     `+0xFC` is 9. While that sound isn't playing, `+0xFC` counts down; at
     0, the SFX and speech files are stopped (`0x434E10`), the sound
     plays, and `+0xFC` is 72. Over nothing, it is stopped.
5. **The level's count answered:** `+0x108`.

**An answer clicked** (`0x4176E0`, through its requires object's click
`0x402F20` with the arrow). The answer goes to step 2.
- **Right** (its sequence one of 1C, 2C, 4C, 5D, 6C, 7A, 8B, 9C, 10A, 11D,
  12B, 13D, 14C, 15A):
  - the page answered;
  - a `Sheriff.NOTEBOOK_ANSWER_RIGHT_` line;
  - a new page drawn as at entry;
  - `+0x100`.
- **Wrong:** a `Sheriff.NOTEBOOK_ANSWER_WRONG_1.` line, and `+0x109`.

Each line's digit comes from `0x417B70`. It draws `rand() % 9`, then
`rand()` modulo the last draw, and takes the first digit (draw + 1) the
disc has, or none. The SFX and speech files are stopped before the line.

##### The horseshoe corral (WP-054)

Traced 2026-11-16 for [WP-054](../work-packets/WP-054-horseshoe-corral.md).

**ROOM_P30_Horseshoe_Corral** (`0x41DA10`, vtable `0x45ED00`; music
`Horseshoe_Corral.Music`; no opening) is a game of horseshoes: Scooby and
Rascal pitch ten each at three pegs. The room's class has no tick (its
`+0x04` is the base's). The game is three sprite classes with updates of
their own (their vtable `+0x0C`). The tree tick (`0x431130`) calls each
right after the sprite's player, front to back.

**The room's fields:**
- **`+0xB8`:** whose turn: 0 Scooby, 1 Rascal.
- **`+0xBC`, `+0xC0`:** Scooby and Rascal.
- **`+0xC4`, `+0xC8`:** their piles.
- **`+0xCC`–`+0xD4`:** the pegs.
- **`+0xD8`–`+0xE4`:** the meter's placements' places.
- **`+0xE8`, `+0xEC`:** the counter's tens and ones.

| Address | What it does |
|---|---|
| `0x41DD00` (+0x18) | Placements. `OBJ_HC_SCOOBYPILE` and `OBJ_HC_RASCALPILE` sprites under the first layer, stopped, at depth 3 and 0. By their sequence: `ANIM_HC_METERA` and `ANIM_HC_METERARROW` are not built, only their places kept; `ANIM_HC_COUNTERBOX` a sprite at depth −10000, looping; `ANIM_HC_COUNTERNUMBERS` two sprites under the second layer (game `+0x5C`) at depth −9999, the left one the tens (a third is an error, not claimed). The exit back to Chase B5 is the default path's |
| `0x41DA80` (+0x0C) | Entry, after the base entry. See below |
| `0x41DCE0` (+0x10) | Leave, after the base leave: the counter's numbers forgotten |
| `0x41E140` | A throw over. Scooby's: Rascal's turn. Rascal's: Scooby's, or, with Scooby's pile on its step 10, `ROOM_P28_Chase_B5` (game vtable `+0x04`) |
| `0x41E1A0` | A snack (`0x407E00`: the inventory's `+0x30` plus 1, at most 99, and the snack box), and the counter on the snacks' tens and ones |

**Entry** (`0x41DA80`):
1. **Set-up:** the toolbar is hidden (`0x407CC0`).
2. **The actors:**
   - **Scooby** (`0x41E290`, 0x78 bytes): `OBJ_HC_SCOOBY` idle, looping,
     at depth 2, with the meter (`OBJ_HC_METER` on `ANIM_HC_METERARROW`,
     stopped, at depth −10, at the arrow's place).
   - **Rascal** (`0x41D770`, 0x74 bytes): `OBJ_HC_RASCAL`, his head
     (`RASCALHEAD_IDLE`, once) at depth −1 and his body (`RASCALBODY`,
     looping) one behind it.
   - **The pegs:** `OBJ_HC_PEG1`–`3`, idle, at depth −100.
3. **Sound:** the `Horseshoe_Corral` sound section is preloaded.
4. **The counter** shows the snacks.
5. **Scooby's turn,** unless his pile is on its step 10; then Chase B5.

**Scooby** (vtable `0x45ED40`; `+0x5C` his state, `+0x68` the meter, `+0x6C`
the strength, `+0x70` his horseshoe landed, `+0x74` the meter's way):

| State | Entered (`0x41E540`) | His update (`0x41E3A0`) |
|---|---|---|
| 0 | Idle, looping | — |
| 1 | The meter once forward from its step, at 9 − 3 × level ticks a step | The meter stopped: once back (mode 4), then once forward, at that speed. The button held (game `+0x20` bit 1): the meter stopped, its step the strength, state 2 |
| 2 | `+0x70` clear, `SCOOBYTHROW` once | His step 2: state 3. Then as state 3 |
| 3 | His pile one step on | His step 15: a horseshoe at his strength, state 4 |
| 4 | — | Stopped: state 5 |
| 5 | The meter stopped, `SCOOBYWATCH` once | Stopped, with `+0x70`: state 0, and the throw over |

**Rascal** (vtable `0x45ECD8`; `+0x5C` his state, `+0x68` a countdown, `+0x6C`
his horseshoe landed):

| State | Entered (`0x41D920`) | His update (`0x41D860`) |
|---|---|---|
| 0 | — | His head stopped: a countdown of `rand() % 60 + 48`; run out, his idle once again |
| 1 | — | His head stopped: state 2 |
| 2 | `+0x6C` clear, `RASCALHEAD_TOSS` once | His head's step 7: state 3 |
| 3 | A horseshoe at `rand() % 9 + 1`, his pile one step on | His head stopped: state 4 |
| 4 | `RASCALHEAD_IDLE` once | His head stopped, with `+0x6C`: state 0, and the throw over |

**A horseshoe** (`0x41D210`, vtable `0x45ECB0`) is a sprite under the first
layer at depth −2, playing once:
- **Scooby's** is `OBJ_HC_ARCS` on `ANIM_HC_ARCS<strength>x<nn>`:
  - **The digits:** `nn` is drawn from `rand() % 20`, then `rand()` modulo
    the draw before, until that name, or it with `H`, is in the art, or the
    draw is 0.
  - **A ringer:** the `H` arcs are ringers. With strength 1–3 one rings
    that peg (`+0x6C`).
  - **Depth:** `4x02` is drawn at depth 10000.
  - **Sound:** `Horseshoe_Corral.Arc_0<strength>x<nn>`, with `H` when that
    one isn't on the disc.
- **Rascal's** is `OBJ_HC_RASCAL_ARCS` on `ANIM_HC_RASCAL_ARCS<n>`:
  - **Strength:** an 8 is taken as 9.
  - **A ringer:** 1–3 rings that peg.
  - **Sound:** `Horseshoe_Corral.Rascal.Arc<n>`.

Its update (`0x41D5B0`):
1. **Landed** (stopped), on a peg: it becomes the peg with the horseshoe on
   it (`OBJ_HC_PEG<n>`, its `HORSESHOE_HIT` or `RASCAL_HIT` once), and
   `Horseshoe_Corral.Rascal.Peg<n>.Hit` plays, Scooby's ringer too (the
   disc's `Scooby.Peg<n>.Hit` sounds are never used). Then a countdown of
   36.
2. **Stopped, with the countdown run out:**
   - Scooby and Rascal are told (`0x41E630`, `0x41DA00`);
   - a ringer of Scooby's is a snack (`0x41E1A0`);
   - the sprite is marked done (`+0x30`), and the sweep after the walk
     (`0x431190`) deletes it. Corrected in
     [WP-055](../work-packets/WP-055-pie-noon.md): until then the fork kept
     each horseshoe in view.

Created during the tree walk, a horseshoe behind its thrower is reached in
the same walk: its player runs that tick.

##### Pie Noon (WP-055)

Traced 2026-11-16 for [WP-055](../work-packets/WP-055-pie-noon.md).

**ROOM_P32_Pie_Noon** (`0x41B840`, vtable `0x45EC3C`) is a pie fight on the
saloon's stage, until the clock chimes:
- **Scooby** walks along the front after the mouse and throws a pie at each
  press.
- **The ghost** walks along the back, throws pies back, and hides in smoke.
  A pie that reaches it is a snack.
- **The rest of the gang** run across three lanes in between, and a pie
  splats on them.
- **The chime over:** back to the saloon.

The audit's 602 instructions are only the room's own functions. Scooby, the
ghost and each runner are sprites with updates of their own (vtable `+0x0C`),
called in the tree walk. Each pie is a sprite the room's tick moves.

**The stage.** The placements give it:
- **Scooby's row,** and the ends of his walk.
- **The ghost's row,** and its four places, sorted by x.
- **Five start places,** sorted by y.

On entry, four edges run from the ghost's row to Scooby's. With `gy` the
ghost's row, the slopes are:
- `+0xB8` = (Scooby's left end − ghost x₁) / (Scooby's row − `gy`)
- `+0xBC` = (Scooby's right end − ghost x₂) / (Scooby's row − `gy`)
- `+0xC0` = (left end − x₀) / (Scooby's row − `gy`)
- `+0xC4` = (right end − x₃) / (Scooby's row − `gy`)

At a depth `z`, measured as a row, the edges are (`0x41C980`–`0x41C9E0`):

| Edge | At depth `z` |
|---|---|
| Left inner | (`z` − `gy`) × `+0xB8` + x₁ |
| Right inner | (`z` − `gy`) × `+0xBC` + x₂ |
| Left outer | (`z` − `gy`) × `+0xC0` + x₀ |
| Right outer | (`z` − `gy`) × `+0xC4` + x₃ |

The stage's width at a depth is the inner edges' gap.

**The lanes** (left end `+0x124`, right end `+0x118`, row `+0x130`):

| Lane | Ends | Row |
|---|---|---|
| 2, the back | The first two start places | The first's |
| 1, the middle | The next two | The third's |
| 0, the front | The other two lanes' ends, carried on | The fifth's |

On Showdown the front lane runs from −553 to 1017, well off the screen.

| Address | What it does |
|---|---|
| `0x41C190` (+0x18) | Placements, none of them built:<br>- **Scooby's** give his row (`+0xD0`) and the ends of his walk (`+0xCC`, `+0xC8`).<br>- **The ghost's** give its row (`+0xE4`) and four places (`+0xD4`), sorted.<br>- **The gang's** give five start places (`+0xEC`, `+0x100`), by y (`0x41C880`).<br>Built:<br>- **`OBJ_PIE_NOON_OVERLAY`s** ending `FR`, `FL`, `BR`, `BL` are sprites under the first layer, looping.<br>- **`OBJ_PIE_NOON_CLOCK`** is a sprite under the first layer, stopped on step level × 15.<br>- **`ANIM_PIE_NOON_COUNTERNUMBERS`** is two sprites under no layer at depth 9999, looping, the left one the tens. A third is an error |
| `0x41B8E0` (+0x0C) | Entry, after the base entry. See below |
| `0x41C130` (+0x10) | Leave, after the base leave: the places, the gang, Scooby and the counter forgotten |
| `0x41BF10` (+0x04) | The tick, after the base tick. See below |
| `0x41CC40` | One of the gang on: a lane drawn (`rand() % 3`). If it has been free over 10 ticks, a runner, running as the lane says (0 left, 1 right, 2 either, `rand()` even for right). The lane's time goes to 0 and its way to the runner's |
| `0x41CA00` | A pie in the first of ten free slots (`+0x154`) |
| `0x41CA90` | Tests a pie against the runners: Shaggy, Fred, Daphne, Velma |
| `0x41CB50` | A snack (`0x407E00`), and the counter |
| `0x41CD20` | Scooby may throw: lane 0's time is not below 0, and there is no chime |

**Entry** (`0x41B8E0`):
1. **The slopes and the lanes** as above.
2. **The ghost and Scooby.**
3. **The lanes:** each either way (2), with a time of −216.
4. **The counter** on the snacks.
5. **Sound:** `Pie_Noon.Music`, then `Pie_Noon.Intro`.
6. **The overlays:** `FR` and `FL` one in front of the middle lane's row; `BR`
   and `BL` one in front of the back lane's.
7. **The clock:** the intro set (`+0x1AC`) and the clock's step kept
   (`+0x1C4`). The next sound is a tick (`+0x1B8`).

**The tick** (`0x41BF10`), after the walk and its sweep:
1. **The cursor fades.**
2. **The gang:** each of Velma, Fred, Daphne and Shaggy not on may run on
   (`0x41CC40`).
3. **Hit countdowns:** each runner's (`0x41A4B0`), Shaggy, Daphne, Fred,
   Velma.
4. **The pies:** each updated (`0x41B2C0`); those done deleted. A kept one
   selects its frame (`0x4309C0`).
5. **Lane times:** each goes up 1; past 100 a lane is either way again.
6. **The clock:**
   - In the intro, once lane 0's time reaches 0, the clock runs from step 1
     at 36 ticks a step.
   - After it, back on step 0, it stops and `Pie_Noon.Clock_Chime` plays.
   - Each step it changes plays `Clock_Tick` or `Clock_Tock`, in turn.
7. **The chime over** (`0x434CE0`): `ROOM_P12_Saloon`.

On Showdown the clock has 60 steps. The intro is 216 ticks, and the chime
comes at tick 216 + 36 × 59 = 2340. The level changes only the step the
clock shows during the intro.

**A runner** (`0x419C50`, vtable `0x45EBA0`; `+0x5C` its state, `+0x68` its
name, `+0x70` running right, `+0x74` its lane, `+0x78` its speed, `+0x7C` its
target, `+0x80` its hit countdown, `+0x84` its hit ticks, `+0x88` its `Hit.X`
played) is a sprite under the first layer:
- **Its sequence:** `OBJ_PIE_NOON_<NAME>` on
  `ANIM_PIE_NOON_<NAME>RUN_<RIGHT|LEFT><lane + 1>`, looping (`0x41A310`).
- **Its course:** from one end of its lane to the other, at a hundredth of
  the lane a tick, at the lane's row and depth.
- **Its update** (`0x419DE0`):
  - **Running:** it moves on. Past the target, its slot is freed and it is
    marked done.
  - **Hit:** while its countdown runs, it counts hit ticks. Then it runs
    again, its `_Hit.X` stopped.

Its hit test (`0x419EB0`) passes three tests in turn:
1. The pie is within a tenth of the stage's width (at the lane's row) of
   that row.
2. The pie is inside its frame's first cel.
3. The pie is on its pixels: a hit.

Inside the cel but off the pixels, while it hasn't been hit, it plays
`Pie_Noon.<NAME>_Miss`.

A hit (`0x41A110`):
- **The sequence:** its `HIT`, looping.
- **The countdown:** 12.
- **The sound:** `Pie_Noon.<NAME>_Hit.<1|2>`, or once it has been hit over
  72 ticks, `_Hit.X` once.

**The ghost** (`0x41A550`, vtable `0x45EBDC`; `+0x5C` its speed, `+0x60` a
countdown, `+0x68` its state, `+0x6C` facing right, `+0x70` hidden, `+0x74`
its smoke, `+0x78` and `+0x7C` the throws and hits to its next line):
- **Where it starts:** a sprite under the first layer, half way along its
  row, facing right.
- **Its speed:** 0.005 of its row a tick.
- **Its draw** (`0x41B0D0`) skips it while it is hidden.

In each state, "side" is the way it faces:

| State | Entered (`0x41AA40`) | Its update (`0x41A650`), after deleting a stopped smoke |
|---|---|---|
| 0 | Shown; `IDLE_<side>`, looping; 25 ticks | Run out: `rand() % 7`. 0 → 5; 1–2 → 4; 3 → 6 (if no smoke is up, else 2); 4–6 → 2 |
| 1 | `HIT_<side>`, looping; 15 ticks. `Ghost_Hit` restarted. A `Good_Job.<1-8>` line every hit | Run out: `rand()` odd 4, else 2 |
| 2 | Scooby walking (state not 0 or 1) and the intro over: `THROW_<side>_TO_<other>` once, turned. Otherwise as 5 | Its step 2: a pie from its place, state 3, `Ghost_Throw`, and every 5–9 throws (the first at once) a `Lookout.<1-3>` line. Then as 3 |
| 3 | — | Stopped: 0 |
| 4 | `RUN_<other>_TO_<side>`, looping | Along its row. Past its end: `rand()` even 2, else 5. Otherwise 1 in 90: 0 |
| 5 | `TRANS_<side>_TO_<other>` once, turned | Stopped: `rand()` odd 0, else 4 |
| 6 | Smoke (`OBJ_PIE_NOON_SMOKE` on `SMOKECYCLE` once, under the first layer, a row in front) at its place; `Smoke_Cycle` | The smoke's step 5: 8 |
| 7 | Somewhere along its row (`rand()` / 32767), then as 6 | The smoke's step 5: 0 |
| 8 | Hidden; 20 ticks | Run out, and no smoke: 7 |

Its hit test (`0x41A9D0`): shown, and on its pixels.

**A pie** (`0x41B0F0`, vtable `0x45EC0C`; `+0x60` its state, `+0x64` across,
`+0x68` its depth as a row, `+0x6C` its size, `+0x70` thrown by the ghost,
`+0x74` the runner slot it hit):
- **Its sprite:** under the first layer, stopped, `OBJ_PIE_NOON_PIE`.
- **Thrown from the back half** (the ghost's): it shows `PIEG_THROW`, and
  "across" is its x along the ghost's places.
- **Thrown from the front:** it shows `PIETHROW`, and "across" is its x
  along Scooby's walk.
- **Its place:** x is "across" between the outer edges at its depth. y is
  its depth less 0.6 of the stage's width there.
- **Its size:** its step's first cel's width.

Its update (`0x41B2C0`):
1. **Landed:** once its sequence stops, it is done. Until then, a runner it
   splatted on keeps a countdown of 12 (`0x41A4D0`).
2. **Flying:**
   - **It moves** a tenth of the stage's width at its depth: back if it is
     Scooby's, forward if it is the ghost's.
   - **Its step grows** while a fifth of the width is under its size
     (Scooby's) or over it (the ghost's), up to 9.
   - **Its depth** is its row.
3. **In front of Scooby's row:** it is tested on Scooby's pixels (`0x41D160`)
   at its x, and a quarter and a half of its size either side.
   - **A hit** (`0x41D1B0`): his `HIT_<L|R>` once and `Scooby_Hit`; the pie
     shows `PIEG_HIT` once, one behind him.
   - **Otherwise:** done.
4. **Behind the ghost's row:** on the ghost, the ghost is hit, a snack (`0x41CB50`), and
   `PIEHIT3` once, one in front of the ghost. Otherwise it is done.
5. **Between the two:** the runners in turn. A hit splats:
   - **The sound:** `Pie_Noon.Splat.<n>`, from a global (`0x475F08`) that
     goes 0 to 4 in turn. The old value is pushed before the increment.
   - **The sequence:** `PIEHIT<lane + 1>` once.
   - **Its depth:** two in front of the runner, or two behind for a ghost's pie.

**Scooby** (`0x41CD50`, vtable `0x45EC7C`; `+0x60` a press used, `+0x64` his
state, `+0x68` facing right, `+0x6C` his throw's number):
- **Where he starts:** a sprite under no layer, at his row's depth, at his
  walk's left end, on `WALK_LEFT_ARM` stopped, walking (3).
- **Each update** (`0x41CE30`):
  - **The press:** let go, it can be used again.
  - **The target:** the mouse's x, kept to his walk.

| State | His update |
|---|---|
| 0 (hit) | Stopped: `LICK_<L\|R>` once and `Scooby_Lick`, state 1 |
| 1 | Stopped: his walk for his side, stopped, state 3 |
| 2 (thrown) | Stopped: turned, his walk for the new side, state 3 |
| 3 | There: stopped. Else 15 a tick at most, his walk restarted when stopped, from its step, a step a tick (left forward, right back). Then, a press not used and allowed (`0x41CD20`): a pie from his place, the press used, `THROW_L_TO_R` (or `R_TO_L`) once, state 2, the next of throws 1–3 and `Scooby_Throw.<n>` |

**The tree's sweep** (`0x431190`) runs after the walk each tick, front to
back. It selects each sprite's frame (`0x4309C0`) and deletes each sprite
marked done (`+0x30`) with its subtree. So "paused" in the walk's row above
means done: a runner past its lane's end is gone before the draw.

**A step past the last.** A pie's step can go one past its sequence's last
(`PIETHROW` and `PIEG_THROW` have 9). `0x4309C0` and `0x41B2C0` read it as
any other: the frame reference is the next sequence's step count. On
Showdown, Scooby's pie shows frame 9, a 3 × 5 speck, for its last few ticks.

##### Deterministic asset-naming rule for WP-002 hand-off

Confirmed: the [WP-008 §Notes naming rule](../work-packets/WP-008-object-ini-catalog.md#notes) — `entry_<index>_<sanitized_name>.png`, sanitization preserving uppercase verbatim and replacing anything outside `[A-Za-z0-9_]` with `_` — applies cleanly because every name observed in the cross-check matched the WP-003 convention already. Three worked examples directly from the catalog:

| Raw name (from WP-003 name table / `object.ini`) | Sanitized | Hypothetical `probe_art.py` output |
|---|---|---|
| `OBJ_DAPHNE_A` | `OBJ_DAPHNE_A` | `entry_<idx>_OBJ_DAPHNE_A.png` |
| `OBJ_P40_TO_P33` | `OBJ_P40_TO_P33` | `entry_<idx>_OBJ_P40_TO_P33.png` |
| `ANIM_CURSORARROW` | `ANIM_CURSORARROW` | `entry_<idx>_ANIM_CURSORARROW.png` |

No name observed required actual sanitization (no spaces, no punctuation, no non-`[A-Za-z0-9_]` characters) — the engine names are already filename-safe. The sanitization function ships in `parse_ini.py` as a documented no-op identity on the observed inputs; the rule is recorded for forward-compat with names from any future WP that finds them.

### Threading and event model

*TBD — single-threaded? message-pump? worker threads?*

### Save-game format

*TBD — deferred until Phase 4.*

### Follow-ups (out of WP-001 scope)

Things the WP-001 trace passed over, each a lead for a later work packet:

- ~~**Audio index and codec**~~ Done by [WP-004](../work-packets/WP-004-audio-archive-decode.md)
  (2026-11-13): uncompressed PCM, see [audio-archives](audio-archives.md#clip-format).
  Still open there: the lip-sync bytes' high bits.
- **Character actors** (Phase 4): `script_Character_ctor` (`0x4048E0`)
  looks up `Global.Scrappy.*` sounds, and `0x405190` formats
  `Global.Idle.%s_P%d%s` / `Global.Idle.%s_S%d%s` and `Global.Scared.*` sound
  names. The idle and scared behaviour lives there.
- **Per-room classes** (Phase 4): `Pie_Noon_Room.cpp`,
  `Horseshoe_Corral_Room.cpp`, `Options_Room.cpp` and the rooms that claim
  placements by OBJ name.
- **Room-block word `0x10`**, the placement field `+0x88` and object table 2
  have no traced reader (see
  [tgifile-art §Remaining unknowns](tgifile-art.md#remaining-unknowns)).
- **Bink**: imports confirmed (WP-007); integration not traced.
- **Save games** (`%s%s%s.sav`): the player profile, traced for WP-026 ([The player profile](#the-player-profile-wp-026)).

---

## References

- Vision doc: [Project Vision](../01-VISION.md)
- Companion specs: [tgifile-art](tgifile-art.md), [audio-archives](audio-archives.md)
- Ghidra project: `C:\dev\scooby-engine\ghidra\scooby.gpr` (local, gitignored; created 2026-11-13 by WP-001, labels re-applicable from [`tools/ghidra-scripts/`](../../tools/ghidra-scripts/wp001-labels.txt))
- Executable-analysis work packets: [WP-001](../work-packets/WP-001-ghidra-session.md) (Track A, Ghidra), [WP-011](../work-packets/WP-011-casefile-decompdecomp.md) (Track B, decompdecomp collaboration)
