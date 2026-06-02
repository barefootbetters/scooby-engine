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

Produce a deterministic, tool-independent baseline of:

1. All printable string literals (≥ 6 chars)
2. The full PE import table

…from `Scooby.exe`, and persist them in a structured, reviewable format in
`docs/formats/scooby-exe.md`.

This enables EC-001 Steps 3–4 to navigate directly to known string and IAT
anchors rather than discovering them ad hoc in Ghidra.

---

## Background

EC-001 Step 4 relies on locating known filename strings (e.g. `TGIFILE.ART`)
in Ghidra. Pre-extracting strings provides:

- Known search anchors
- Expected result counts (sanity check inside Ghidra)
- Visibility into asset naming patterns and path conventions

The import table determines:

- File I/O API surface (`CreateFileA` vs `CreateFileW`)
- Multimedia dependencies (DirectX, Bink/Smacker, etc.)
- CRT/runtime footprint

These materially influence WP-001 reverse engineering strategy and the
eventual `Common::File` abstraction design.

---

## Scope

### In scope

1. Extract all printable ASCII strings ≥ 6 characters from `Scooby.exe`
2. Extract complete import table (DLL + function name or ordinal)
3. Normalize and group results
4. Record outputs in `docs/formats/scooby-exe.md` under **Findings**

### Out of scope

- Any disassembly or Ghidra work (WP-001)
- Behavioral analysis of imports
- Cross-title comparison (optional stretch only)

---

## Dependencies

- `Scooby.exe` at one of:
  - `tools/exes/showdown/Scooby.exe`
  - Mounted Showdown ISO extraction
- Extraction method (choose one and document which was used):
  - Python `pefile` (`pip install pefile`)
  - `dumpbin /IMPORTS` (MSVC toolchain)
  - PE-bear / CFF Explorer

---

## Execution (deterministic)

### 1. Strings extraction

**Option A — Python (preferred; reproducible, no tool dependency):**

```python
import string

def extract_strings(path, min_len=6):
    with open(path, 'rb') as f:
        data = f.read()
    result, current = [], []
    for b in data:
        c = chr(b)
        if c in string.printable and c not in '\r\n\t\x0b\x0c':
            current.append(c)
        else:
            if len(current) >= min_len:
                result.append(''.join(current))
            current = []
    if len(current) >= min_len:
        result.append(''.join(current))
    return sorted(set(result))

for s in extract_strings('Scooby.exe'):
    print(s)
```

**Option B — Sysinternals `strings.exe`:**

```
strings.exe -n 6 Scooby.exe > strings-out.txt
```

**Normalization rules (both options):**

- Deduplicate (set)
- Sort ascending
- Preserve original casing
- Do not trim paths or filenames

### 2. Import table extraction

**Baseline — Python / pefile:**

```python
import pefile

pe = pefile.PE('Scooby.exe')
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode(errors='ignore')
    for imp in entry.imports:
        name = imp.name.decode(errors='ignore') if imp.name else f'ord#{imp.ordinal}'
        print(f"{dll}::{name}")
```

**Normalization rules:**

- Format: `DLL::Function`
- One entry per line
- Preserve ordinal-only entries as `DLL::ord#N`
- Sort by DLL name, then function name

---

## Output specification (MANDATORY)

Update `docs/formats/scooby-exe.md` → Findings with both sections below.
The structure is required — prose-only findings fail exit criteria.

### Section: Findings → String literals

Required subsections:

- **File / asset names** — filename strings (`TGIFILE.ART`, `object.ini`, etc.)
- **Paths / directories** — any directory or drive-letter strings
- **Error / debug strings** — error messages, assertions, log prefixes
- **Other notable strings** — anything that doesn't fit the above

Required conclusions block:

```md
#### Conclusions

- Encoding: [ANSI | Unicode | Mixed | Unknown]
- Registry usage: [Yes — keys: ... | No]
- Hardcoded paths: [Yes — examples: ... | No]
- Asset resolution strategy: [String-based | Index-based | Unknown]
- Anchor strings confirmed for Ghidra: [list ≥ 3, e.g. TGIFILE.ART, object.ini, Music.dat]
```

### Section: Findings → Import table

Required grouping (omit a group only if the exe has zero entries for it):

```md
- KERNEL32.dll
  - CreateFileA
  - ReadFile
  - SetFilePointer
  ...
```

Groups:

- **Win32 File I/O** (kernel32: `CreateFile`, `ReadFile`, `WriteFile`, `SetFilePointer`, etc.)
- **Memory / Process** (kernel32: `VirtualAlloc`, `HeapAlloc`, `GetProcAddress`, etc.)
- **Graphics / DirectX** (ddraw.dll, d3d*.dll, etc.)
- **Audio / Video** (dsound.dll, Bink/Smacker imports, etc.)
- **CRT / Standard Library** (msvcrt.dll, etc.)
- **Other** (anything not in the above)

---

## Exit criteria

1. ✅ Strings list is deduplicated, sorted, derived via documented method, and
   stored in the required subsection structure in `scooby-exe.md`.
2. ✅ Import table is complete (no missing DLL blocks), normalized to
   `DLL::Function`, and grouped by category.
3. ✅ Conclusions block explicitly answers all four questions: encoding,
   registry usage, hardcoded paths, asset resolution strategy.
4. ✅ All outputs are reproducible by re-running the documented command/script
   against the same binary without modification.
5. ✅ At least 3 anchor strings are named in the Conclusions block for use as
   immediate Ghidra navigation targets in EC-001.

Any criterion not met = WP not done. Partial findings with open conclusions
remain 🚧 In Progress.

---

## Deliverables

- Updated [`docs/formats/scooby-exe.md`](../formats/scooby-exe) — two structured Findings sections

---

## Notes

- Asset-like strings (e.g. `"room_library"`, `"cursor_hand"`) are **high signal**:
  they indicate string-based lookup paths and should be called out explicitly in
  the asset-resolution-strategy conclusion. This directly determines how
  load-bearing WP-008's catalog is.
- Absence of `CreateFileW` strongly implies ANSI-only path handling — record
  this explicitly in the Conclusions block rather than leaving it as an
  inference during WP-001.
- Cross-title stretch (optional, must not block completion): running the same
  extraction on Phantom / Jinx / Case File #1 exes takes 2 extra minutes and
  can confirm import surface evolution across generations (e.g. Jinx adding
  Smacker, Case File #1 adding libexpat.dll).
