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

### Binary identity (WP-007 baseline)

Reference table for every binary the [WP-007](../work-packets/WP-007-strings-and-imports.md) strings + imports extraction ran against. Every subsequent Finding subsection cites the SHA-256 of the binary it derives from; a re-extraction against a different SHA invalidates the corresponding row.

| Title | Generation | Path | Size (bytes) | SHA-256 |
|---|---|---|---|---|
| Showdown | Gen 1 | `tools/exes/showdown/Scooby.exe` | 487,473 | `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` |
| Phantom | Gen 1 | `tools/exes/phantom/Scooby.exe` | 483,377 | `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED` |
| Jinx | Gen 2 | `tools/exes/jinx/Scooby.exe` | 847,872 | `136A276872803AC99B0D050B21CC3A83F8E1608F2394C33865CFFF781FB20271` |
| Case File #1 | Gen 3 | `tools/exes/casefile1/Scooby.exe` | 786,432 | `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8` |

Case File #2 is not yet cached — disc not yet mounted — so it is not covered by this baseline. Per the [engine-lineage finding](../01-VISION.md#engine-lineage-2026-06-finding) it is predicted Gen 3 (IBS continuation of the MMFW codebase). The skip is intentional, not a gap to fill at this WP's scope.

Extraction tooling: [`tools/extract_strings.py`](../../tools/extract_strings.py) and [`tools/extract_imports.py`](../../tools/extract_imports.py). Raw outputs (`strings-ansi.txt`, `strings-wide.txt`, `imports.txt`) live under `tools/exes/<title>/`, gitignored per [tools/exes/README](../../tools/exes/README.md). Determinism confirmed: re-running each script against the same binary produces byte-identical output.

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

### Pending: Phantom archive format

Phantom's Rich Header matches Showdown's exactly (Gen 1 by toolchain),
but its archive format is not yet verified. Predicted to be Gen 1
`TGIFILE.ART`, not Gen 2 `MMFW`, but a one-minute
`Format-Hex E:\scooby\TGIFILE.ART -Count 8` check on the mounted
Phantom disc settles it.

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
- Cross-title delta vs Showdown: **near-identical** for the engine-surface strings (filename anchors, format strings, registry keys, error templates, asset-key conventions). The Phantom-specific delta is the per-title `FBF\` source module + per-title `ROOM_*`/`ANIM_*` content (`KST_*` etc.) — title content, not engine. Phantom has 122 fewer ANSI strings than Showdown (1837 vs 1959); the difference is entirely in per-title content strings (Showdown has more `ROOM_Artifact_*` variants and other content). The 4,096-byte size delta vs Showdown noted in [tools/exes/README](../../tools/exes/README.md) §Showdown — Phantom *smaller* despite +6 MASM 6.13 entries in the Rich Header — is consistent with Phantom having less per-title content; not surprising once strings counts are this close.

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
- Cross-title delta vs Showdown: **disjoint** for engine-surface strings (no `TGIFILE.ART`, no `object.ini`, no `Software\TerraGlyph\%s`, no Bink class strings). Asset-key convention renamed `ROOM_*` → `SCENE_*`. C++ class hierarchy visible (Gen 1's procedural style is gone). Confirms the [Gen 1 → Gen 2 boundary](../01-VISION.md#engine-lineage-2026-06-finding) at the source-string level: this is the same engine *family* (per the Rich Header sharing `MSVC 5.0 C++ build 8034`), but the framework was rewritten between Gen 1 and Gen 2 — MMFW is a substantively new abstraction layer over the same toolchain and the same general engine concepts.

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
- `MMFW Films`, `MMFW Pictures`, `MMFW Scripts`, `MMFW Sounds` — same MMFW resource-type labels as Jinx (confirms MMFW carryover into Gen 3 — direct code inheritance evidence at the string level, alongside the linker-build 8168 evidence from the [cross-title toolchain comparison](#cross-title-toolchain-comparison-engine-generations))

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
- CRT: **static** — no `MSVCRT.dll` / `MSVCR*.dll` import; CRT linked into the binary at build time (consistent with VC++ 5.0 single-environment build)
- Cross-title delta vs Showdown: n/a (this is Showdown)
- Notable: WINSPOOL printing API + IMM32 IME — both are Win9x edutainment-app patterns rather than game-specific patterns

#### Phantom (Gen 1) — 216 entries

SHA-256 of source binary: `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED`

**Byte-identical to Showdown's import table.** SHA-256 of normalized `imports.txt` matches across both binaries (verified via `diff tools/exes/showdown/imports.txt tools/exes/phantom/imports.txt` returning empty). Every group above for Showdown applies to Phantom verbatim — same 216 entries in the same DLL distribution, including the 11 Bink symbols and the WINSPOOL/IMM32 surfaces.

This is the strongest possible cross-title evidence of engine-level identity at the Gen 1 link boundary: Phantom and Showdown were linked against the same import-library set with the same configuration. Combined with the [Rich Header match](#cross-title-toolchain-comparison-engine-generations) (Linker 5.10 build 8047, identical compile-product distribution), Showdown and Phantom are the same engine binary up to per-title content. The Phantom-specific `FBF\` source-tree paths in the [strings findings](#phantom-gen-1) are the only meaningful binary delta.

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

*TBD — which function opens which file; what the dispatch/lookup looks like.*

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
| `exitobject` | 77 | Room-to-room navigation triggers (carry `destinationroom=`, `character=`, `direction=`, per-character `direction` overrides) |
| `clickableobject` | 103 | Interactive hotspots (carry `sequence=`, `priority=`, `layer=`, `rolloveranim=`) |
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
| `ROOM_*` referenced by `destinationroom=` but absent from WP-003's 42-ROOM table | 21 | Includes `ROOM_Main_Menu` plus 20 `ROOM_P{NN}_<descriptive>` rooms. Either these rooms have no pre-rendered backgrounds (scripted/engine-rendered scenes — `ROOM_P30_Horseshoe_Corral`, `ROOM_P32_Pie_Noon` are minigames per the source-tree paths `\Scooby\GBH\Horseshoe_Corral_Room.cpp` and `\Scooby\GBH\Pie_Noon_Room.cpp` in the [Showdown strings findings](#showdown-gen-1)), or their backgrounds live in a separate archive. |
| `OBJ_*` section headers (hotspot / exit / overlay) with no `TGIFILE.ART` art payload | 25 | Names ending in `_HOTSPOT*`, `_TO_P*`, `_OVERLAY` — invisible click targets that don't need pre-rendered art. Corroborates the [Showdown strings finding](#showdown-gen-1) of `Failed to locate id %s` / `Failed to locate object name %s` as the engine's string-keyed lookup error path — not every `[OBJ_*]` ID is expected to resolve to an art entry. |
| `ANIM_CURSOR<NAME>` and `ANIM_TOOLBAR<NAME>` for inventory items | 19 | All 11 `OBJ_INV_*` items reference a `ANIM_CURSOR<NAME>` + a `ANIM_TOOLBAR<NAME>`. **System** toolbar animations (`ANIM_TOOLBARCOMPUTER_IDLE`, `ANIM_TOOLBARSCRAPPY_IDLE`, `ANIM_TOOLBARMAGGLASS_IDLE`, etc.) **do** match the WP-003 table; the inventory-item variants do not. Either inventory animations live in a separate asset store, or `TGIFILE.ART` only carries the system toolbar animations and the inventory ones are generated/composited at runtime. New unknown for WP-001. |

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

**No `object.ini` field is shaped like a `Scooby.eng` message ID.** The combined catalog records `object_ini_to_eng_resolutions: 0`. `Scooby.eng` is not a runtime localization table for `object.ini` strings; it is purely the boot/error-message table for `Scooby.exe`'s system-error paths (the `0010`–`0018` block matches the DirectDraw/DirectSound/CD-ROM failure surface called out in the [Known facts](#known-facts) section above and corroborated by the binary's import table). In-game dialogue text is not in `Scooby.eng`; it lives in `voice.dat` or in scripted dialogue elsewhere (a new unknown to scope as part of [WP-004](../work-packets/WP-004-audio-archives.md)).

##### Data-driven vs implicit

`object.ini` carries **the asset-binding layer** end-to-end: every interactive object, every room exit, every cursor swap, every inventory item is named here. What it does *not* carry:

- **Puzzle state machines.** No conditional `requires=item_X then unlock_Y` structure exists — `requiresobject`'s only state is `requiredanim=<cursor>`, which gates the input event, not the puzzle outcome.
- **Room-to-room transition rules** beyond the immediate `destinationroom=`. No "if Scooby has the lantern, Tunnel_Dark becomes Tunnel_Lit" logic.
- **Background art bindings.** Rooms have no `bg=` field — the engine resolves the room background through a different lookup (most likely the canonical room name → `TGIFILE.ART` entry, which the WP-003 cross-check confirms is the bulk of the matched references on the room side).
- **The 5 `ID=` values are leaf categories**, not a state machine. Whatever ties a hotspot click to a puzzle outcome lives in the exe (or in a scripted dialogue file not yet parsed).

So the data-driven hypothesis stated under [Hypotheses (unverified)](#hypotheses-unverified) — *"Most gameplay rules are driven by `object.ini`, with the exe acting as interpreter"* — is **partially confirmed and importantly refined**: the *asset-binding and navigation graph* is data-driven, but the *puzzle/state logic* is not. WP-001 (Ghidra session) needs to find the function that consumes `object.ini` (likely the loader that triggers on the `Failed to load room.` error string per the [Showdown strings findings](#showdown-gen-1)) and the function that resolves cursor-key + click-target combinations to script invocations (probably keyed by the `scrappyid=Global.Scrappy.*` field, which suggests a script-table identifier resolved from a different file).

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

---

## References

- Vision doc: [Project Vision](../01-VISION.md)
- Companion specs: [tgifile-art](tgifile-art.md), [audio-archives](audio-archives.md)
- Ghidra project: `C:\www\scooby\ghidra\scooby.gpr` (to be created)
