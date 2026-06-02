---
layout: default
title: "WP-007: Strings & Import Table"
---

# WP-007: `Scooby.exe` strings dump + import table extract

**Status:** 📦 Queued
**Phase:** Pre-Work (before WP-001)
**Depends on:** —
**Companion EC:** — (single 15–30 min session; no checklist needed)
**Estimated effort:** 15–30 min

---

## Goal

Before opening Ghidra, extract all string literals and the full PE import
table from `Scooby.exe` and record them in `docs/formats/scooby-exe.md`.
This primes EC-001 Steps 3–4 so the Ghidra session navigates to known
locations rather than discovering from scratch.

## Background

EC-001 Step 4 instructs searching Ghidra's Defined Strings for
`"TGIFILE.ART"`. That search is faster and more confident when you already
know: (a) which filename strings exist, (b) roughly how many call sites to
expect, and (c) what the complete file I/O API set looks like.

The import table also resolves a question that affects the `Common::File`
wrapper: if the exe uses `CreateFileA` (ANSI) but not `CreateFileW`
(Unicode), all disc paths are ANSI — relevant for how path resolution is
handled in the ScummVM engine.

Both pieces of information are available in under 30 minutes without
touching a disassembler.

## Scope

In scope:
- Run `strings` (or Python `pefile` string extraction) on `Scooby.exe` — extract all printable sequences ≥ 6 chars
- Export the full import table using `pefile`, CFF Explorer, or `dumpbin /IMPORTS` — record DLL name + function name for every import
- Record findings in two new sections of `docs/formats/scooby-exe.md` → Findings

Out of scope:
- Any disassembly or decompilation (WP-001)
- Analysis of what each function does (Ghidra scope)
- Cross-title import comparison (optional stretch goal only)

## Dependencies

- `Scooby.exe` extracted from the mounted Showdown ISO (or at `tools/exes/showdown/Scooby.exe`)
- One of: Python `pefile` (`pip install pefile`), CFF Explorer, PE-bear, or MSVC `dumpbin`

## Exit criteria

1. `docs/formats/scooby-exe.md` → Findings → "String literals" section populated with:
   all filename strings (e.g. `TGIFILE.ART`, `object.ini`, `Music.dat`),
   error-message strings, and any asset-name or path strings.
2. `docs/formats/scooby-exe.md` → Findings → "Import table" section populated with:
   all imported DLLs and functions, grouped by category (Win32 file I/O, DirectX, CRT, Bink).
3. The string-literals section explicitly answers: are all file paths ANSI or Unicode?
   Any registry keys? Any hardcoded disc paths?

## Deliverables

- Updated [`docs/formats/scooby-exe.md`](../formats/scooby-exe) — two new Findings sections

## Notes

- Quick `pefile` one-liner for imports:
  ```python
  import pefile
  pe = pefile.PE('Scooby.exe')
  for entry in pe.DIRECTORY_ENTRY_IMPORT:
      for imp in entry.imports:
          print(entry.dll_name.decode(), imp.name.decode() if imp.name else f'ord#{imp.ordinal}')
  ```
- String literals that look like asset names — e.g. `"room_library"`, `"cursor_hand"` — are
  particularly valuable: they reveal whether the exe resolves assets by logical string name
  (which makes WP-008's catalog directly load-bearing) or by numeric index.
- Cross-title stretch: if Phantom, Jinx, and Case File #1 exes are already in `tools/exes/`,
  running the same extraction takes 2 extra minutes and surfaces any import surface changes
  between generations (e.g. Jinx adding Smacker imports, Case File #1 adding libexpat).
