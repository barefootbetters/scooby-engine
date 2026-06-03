---
layout: default
title: "WP-007: Strings & Import Table"
---

# WP-007: `Scooby.exe` strings dump + import table extract

**Status:** ✅ Done (2026-06-02)
**Phase:** 0 — Pre-Work (before WP-001)
**Depends on:** —
**Unblocks (recommended, not strict):** WP-003, WP-001
**Companion EC:** — (single 15–30 min session; no checklist needed)
**Pre-flight required:** Yes — this WP writes facts into `docs/formats/scooby-exe.md`. See [pre-flight gate](../reference/pre-flight.md) → "format documentation under `docs/formats/**` that locks a fact."
**Pre-flight artifact:** [pre-flight-WP-007-2026-06-02-b](../reference/pre-flight-WP-007-2026-06-02-b.md) — verdict READY against commit `f3cd590`.
**Session prompt:** [session-WP-007-2026-06-02](../sessions/session-WP-007-2026-06-02.md).
**Targets generation(s):** Gen 1 (Showdown primary). Gen 1 (Phantom), Gen 2 (Jinx), Gen 3 (Case File #1) covered as in-scope cross-title runs — see §Cross-title runs.
**Estimated effort:** 20–40 min (single-title 15–20 min; +5–10 min per additional title). **Actual: ~30 min** (cross-title runs added negligible time; the bulk of the session was authoring the structured Findings in [scooby-exe](../formats/scooby-exe.md)).
**Findings landed in:** [scooby-exe.md §Binary identity](../formats/scooby-exe.md#binary-identity-wp-007-baseline) (4 rows + SHA-256 lock) · [§String literals](../formats/scooby-exe.md#string-literals-wp-007) (per-title subsections + Conclusions blocks) · [§Import table](../formats/scooby-exe.md#import-table-wp-007) (per-title grouped imports + Conclusions blocks) · [§Cross-title runtime dependencies](../formats/scooby-exe.md#cross-title-runtime-dependencies) (TBD/predicted cells replaced with import-verdict cells).

---

## Goal

Produce a deterministic, tool-independent baseline of:

1. All printable string literals (ANSI ≥ 6 chars, plus UTF-16LE wide strings ≥ 6 chars)
2. The full PE import table

…from `Scooby.exe` (and the other three available `*.exe` binaries), and persist
the structured results in `docs/formats/scooby-exe.md` under Findings.

This enables EC-001 Steps 3–4 to navigate directly to known string and IAT
anchors instead of discovering them ad hoc in Ghidra, and converts EC-001 Step 3
("Imports table review") from re-extraction into a cross-check against this WP's
output.

---

## Background

EC-001 Step 4 relies on locating known filename strings (e.g. `TGIFILE.ART`)
in Ghidra. Pre-extracting strings provides:

- Known search anchors
- Expected result counts (sanity check inside Ghidra)
- Visibility into asset naming patterns and path conventions
- A baseline that WP-003's pre-payload region scan can cross-check (if asset
  name strings live in that 1 MB region, they must also appear in this dump)

The import table determines:

- File I/O API surface (`CreateFileA` vs `CreateFileW`) — answers the Win32
  path-encoding question that the strings scan alone cannot
- Multimedia dependencies (DirectX, Bink/Smacker, etc.)
- CRT/runtime footprint

These materially influence WP-001 reverse engineering strategy and the
eventual `Common::File` abstraction design.

Running the same extraction across all four available exes in the same session
also locks the cross-title import-surface comparison that the [scooby-exe
cross-title section](../formats/scooby-exe.md#cross-title-runtime-dependencies)
currently lists as "predicted / TBD" for Phantom — at near-zero marginal cost,
since the binaries are already cached under `tools/exes/`.

---

## Scope

### In scope

1. Extract all printable ASCII strings ≥ 6 characters from `Scooby.exe` (Showdown)
2. Extract all UTF-16LE wide strings ≥ 6 characters from the same binary
3. Extract complete import table (DLL + function name or ordinal)
4. Normalize and group results
5. Record outputs in `docs/formats/scooby-exe.md` under **Findings**
6. **Cross-title runs** — repeat the same three extractions on Phantom, Jinx,
   and Case File #1 binaries (already cached locally per [tools/exes/README](../../tools/exes/README.md));
   record per-generation diffs in scooby-exe.md (see §Cross-title runs)
7. Record the SHA-256 of every binary the extraction ran against, in the
   corresponding Findings subsection

### Out of scope

- Any disassembly or Ghidra work (WP-001)
- Behavioral analysis of imports (e.g., "how is `CreateFileA` actually called")
- Asset *resolution* strategy (string-based vs index-based lookup) —
  determinable only from Ghidra, not from strings alone
- Resource directory contents (icons, version block, manifest)
- Case File #2 — disc not yet cached (WP-005 follow-up)

---

## Dependencies

- Binaries cached locally under `tools/exes/` per [tools/exes/README](../../tools/exes/README.md) (all titles renamed to the canonical `Scooby.exe` per the README's safety-net policy):
  - `tools/exes/showdown/Scooby.exe` — required
  - `tools/exes/phantom/Scooby.exe` — required for cross-title row
  - `tools/exes/jinx/Scooby.exe` — required for cross-title row
  - `tools/exes/casefile1/Scooby.exe` — required for cross-title row (original disc name: `Case File #1.exe`; record both in the Binary identity table)
- Record the SHA-256 of each binary the extraction ran against. Get them with:
  ```powershell
  Get-FileHash tools\exes\showdown\Scooby.exe -Algorithm SHA256
  ```
- Extraction method (choose one per artifact type and document which was used):
  - **Strings:** Python script in §Execution (preferred — handles both ANSI and
    UTF-16LE in one pass), or Sysinternals `strings.exe -n 6 -a` (ANSI) plus
    `strings.exe -n 6 -u` (Unicode)
  - **Imports:** Python `pefile` (`pip install pefile`), `dumpbin /IMPORTS`
    (MSVC toolchain), or PE-bear / CFF Explorer

---

## Execution (deterministic)

Output files (raw dumps) are **local-only** — gitignored under `tools/exes/*`
per [tools/exes/README](../../tools/exes/README.md). They may contain dialog or
error text that is copyrighted; only categorized samples + filenames + the
import surface get promoted into `scooby-exe.md` (see §Output specification).

### 1. Strings extraction

**Option A — Python (preferred; reproducible, no tool dependency, covers both
ANSI and UTF-16LE):**

```python
import re
import sys
from pathlib import Path

ASCII_RE = re.compile(rb'[\x20-\x7E]{6,}')
# UTF-16LE: ASCII char followed by 0x00, repeated >=6 times
UTF16LE_RE = re.compile(rb'(?:[\x20-\x7E]\x00){6,}')

def extract(path):
    data = Path(path).read_bytes()
    ansi = {m.group().decode('ascii').strip() for m in ASCII_RE.finditer(data)}
    wide = {m.group().decode('utf-16le').strip() for m in UTF16LE_RE.finditer(data)}
    return sorted(s for s in ansi if s), sorted(s for s in wide if s)

if __name__ == '__main__':
    exe = sys.argv[1]
    out_dir = Path(exe).parent
    ansi, wide = extract(exe)
    (out_dir / 'strings-ansi.txt').write_text('\n'.join(ansi), encoding='utf-8')
    (out_dir / 'strings-wide.txt').write_text('\n'.join(wide), encoding='utf-8')
    print(f'{exe}: ansi={len(ansi)} wide={len(wide)}')
```

Run: `python extract_strings.py tools/exes/showdown/Scooby.exe`

**Option B — Sysinternals `strings.exe` (two passes — ANSI and Unicode):**

```
strings.exe -n 6 -a tools\exes\showdown\Scooby.exe > tools\exes\showdown\strings-ansi.txt
strings.exe -n 6 -u tools\exes\showdown\Scooby.exe > tools\exes\showdown\strings-wide.txt
```

**Normalization rules (both options):**

- Deduplicate (set)
- Sort ascending (`LC_ALL=C` ordering — byte-order, not locale-aware)
- Preserve original casing
- Do not trim paths or filenames
- Strip leading/trailing whitespace per string but preserve internal whitespace
- Wide-string output is decoded UTF-16LE → UTF-8 for storage

### 2. Import table extraction

**Baseline — Python / pefile:**

```python
import pefile
import sys
from pathlib import Path

def extract(exe):
    pe = pefile.PE(exe)
    lines = []
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode(errors='ignore')
        for imp in entry.imports:
            name = imp.name.decode(errors='ignore') if imp.name else f'ord#{imp.ordinal}'
            lines.append(f'{dll}::{name}')
    return sorted(lines, key=str.lower)

if __name__ == '__main__':
    exe = sys.argv[1]
    out = Path(exe).parent / 'imports.txt'
    lines = extract(exe)
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{exe}: {len(lines)} imports -> {out}')
```

Run: `python extract_imports.py tools/exes/showdown/Scooby.exe`

**Normalization rules:**

- Format: `DLL::Function`
- One entry per line
- Preserve ordinal-only entries as `DLL::ord#N`
- Sort case-insensitively by DLL name, then function name

### 3. Cross-title runs

Repeat §1 and §2 against each cached binary:

```powershell
foreach ($t in 'showdown','phantom','jinx','casefile1') {
  $exe = "tools\exes\$t\Scooby.exe"
  if (-not (Test-Path $exe)) { Write-Warning "skip $t (missing $exe)"; continue }
  python tools\extract_strings.py $exe
  python tools\extract_imports.py $exe
}
```

Produces `tools/exes/<title>/strings-ansi.txt`, `strings-wide.txt`, and
`imports.txt` for each title (all gitignored).

---

## Output specification (MANDATORY)

Update `docs/formats/scooby-exe.md` → Findings with the sections below.
The structure is required — prose-only findings fail exit criteria.

Every finding states which generation + title it applies to. Cross-title
results go side-by-side in a single table when shape allows; otherwise as
labeled subsections (`#### Showdown (Gen 1)`, `#### Phantom (Gen 1)`, etc.).

### Section: Findings → Binary identity

Required table (one row per binary extracted against):

| Title | Generation | Path | Size | SHA-256 |
|---|---|---|---|---|
| Showdown | Gen 1 | `tools/exes/showdown/Scooby.exe` | `<bytes>` | `<sha256>` |
| ... | | | | |

Re-runs against a different SHA invalidate the corresponding Findings row.

### Section: Findings → String literals

Required subsections (per-title, or merged with title columns):

- **File / asset names** — filename strings (`TGIFILE.ART`, `object.ini`, etc.)
- **Paths / directories** — any directory or drive-letter strings
- **Error / debug strings** — error messages, assertions, log prefixes
  (cite a handful for shape; do not paste the full set — copyright)
- **Registry keys** — any `HKEY_*\...` strings or `RegOpen*` argument literals
- **Other notable strings** — anything that doesn't fit the above

Required conclusions block:

```md
#### Conclusions (per title)

- ANSI string count: <N>
- UTF-16LE string count: <N>  (≈0 expected for VC5/Win9x targets)
- Registry usage: [Yes — keys: ... | No]
- Hardcoded paths: [Yes — examples: ... | No]
- Filename anchors for Ghidra (≥ 3 required, must be asset/data filenames —
  not error strings): [e.g. TGIFILE.ART, object.ini, Music.dat, Scooby.eng]
- Cross-title delta vs Showdown: [identical | superset | disjoint | n/a]
```

Note: "asset resolution strategy" (string-based vs index-based) is **not**
answerable from this WP — it requires seeing how strings are used in code
and is deferred to EC-001 Step 4.

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
- **Input** (dinput.dll, user32 input APIs)
- **CRT / Standard Library** (msvcrt.dll, etc.)
- **Other** (anything not in the above)

Required conclusions block:

```md
#### Conclusions (per title, derived from imports)

- Path API encoding: [ANSI-only (`CreateFileA` present, `CreateFileW` absent)
  | Wide-only | Mixed | Neither — uses CRT only]
- Bink runtime: [present / absent]
- Smacker runtime: [present / absent]
- DirectDraw / Direct3D version: [DD7 / D3D7 / DD-only / ...]
- DirectSound: [present / absent]
- CRT: [msvcrt.dll | msvcr70.dll | static / none]
- Cross-title delta vs Showdown: [identical | added: ... | removed: ...]
```

This is the section that materially feeds the [scooby-exe cross-title
runtime-dependencies table](../formats/scooby-exe.md#cross-title-runtime-dependencies)
— update that table's "unverified" / "TBD" cells from the conclusions here.

---

## Exit criteria

1. Pre-flight verdict **READY** is committed to `docs/reference/pre-flight-WP-007-<date>.md` before extraction runs.
2. The Binary identity table in `scooby-exe.md` lists every binary the
   extraction ran against, with size and SHA-256 — at minimum Showdown; ideally
   all four cached titles.
3. Strings findings (ANSI + UTF-16LE) are deduplicated, sorted, derived via the
   documented method, and stored in the required subsection structure for each
   binary listed in the Binary identity table.
4. Import table is complete (no missing DLL blocks), normalized to
   `DLL::Function`, grouped by category, and per-title.
5. **Both** Conclusions blocks (strings + imports) are filled in — every bullet
   answered, no `TBD` and no placeholder text. The strings block does **not**
   try to answer asset-resolution strategy.
6. At least 3 **filename / data-file** anchor strings are named in the strings
   Conclusions block (e.g. `TGIFILE.ART`, `object.ini`, `Music.dat`,
   `Scooby.eng`). Error messages, dialog strings, and debug prefixes do not
   count toward this quota — they are useless as IAT navigation anchors.
7. Outputs are reproducible: re-running the documented command/script against
   the same SHA-256 produces byte-identical normalized output. The Python
   scripts in §Execution are committed under `tools/` (one-time addition).
8. Raw `strings-ansi.txt` / `strings-wide.txt` / `imports.txt` live under
   `tools/exes/<title>/` (gitignored). Nothing copyrighted reaches `docs/`.
9. The [scooby-exe cross-title runtime-dependencies table](../formats/scooby-exe.md#cross-title-runtime-dependencies)
   has every "TBD" / "unverified" / "predicted" cell replaced by the verdict
   from this WP's import findings.

Any criterion not met = WP not done. Partial findings with open conclusions
remain 🚧 In Progress.

---

## Deliverables

- Committed: [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) — Binary identity table, String literals subsection, Import table subsection, both Conclusions blocks, cross-title runtime-dependencies table updated
- Committed: `docs/reference/pre-flight-WP-007-<date>.md` (signed READY)
- Committed: `tools/extract_strings.py` and `tools/extract_imports.py` (one-time, if Option A was chosen)
- Local-only (gitignored): `tools/exes/<title>/strings-ansi.txt`, `strings-wide.txt`, `imports.txt` for each title extracted against

---

## Notes

- **Asset-like strings** (e.g. `"room_library"`, `"cursor_hand"`) are
  high-signal hits and should be called out in the strings Findings. They
  *suggest* string-keyed lookup but do not prove it — the prove-it step is
  EC-001 Step 4 (Ghidra xrefs from the string to the call site). Note them
  here; conclude on resolution strategy there.
- **Path API encoding** is answered by the imports table, not the strings
  scan: `CreateFileA` present + `CreateFileW` absent = ANSI-only path
  handling. Record this in the imports Conclusions block.
- **Hand-off to EC-001 Step 3.** EC-001 Step 3 currently reads "Open Symbol
  Tree → Imports … record imports grouped by category." Once WP-007 is done,
  Step 3 is a **cross-check** ("the imports recorded in scooby-exe.md match
  what Ghidra's Symbol Tree shows"), not a re-extraction. EC-001 itself
  isn't edited by this WP — WP-001's pre-flight notes the relationship.
- **Hand-off to WP-003.** The pre-payload region scan (`0x0F48`–`0x10017E`)
  looks for "asset name strings" as one of its hypotheses. WP-003 cross-checks
  any candidate names against `tools/exes/showdown/strings-ansi.txt` — if the
  byte at that region offset doesn't appear in the strings dump, the candidate
  wasn't loaded as a literal and the hypothesis weakens.
- **Cross-title is in scope, not stretch.** Running on all four cached
  binaries adds ~5 minutes total, lands the Phantom row of the [scooby-exe
  cross-title runtime-dependencies table](../formats/scooby-exe.md#cross-title-runtime-dependencies)
  that's currently "predicted same", and provides the import-side evidence
  for the Gen 1 → Gen 2 → Gen 3 boundary the engine-lineage finding asserts.
  Skipping cross-title titles is acceptable only if a binary is corrupt or
  unavailable; document the skip in the Binary identity table.
- **Copyright posture.** Raw strings dumps may contain dialog text, error
  messages, or copyright strings (e.g. `"© 2000 The Learning Company"`).
  Keep raw dumps under `tools/exes/<title>/` (gitignored). Into `docs/formats/`
  go only: structured anchor strings (filenames are functional/factual), a
  small handful of error-message samples for shape, and the full import table
  (function names are uncopyrightable interface data).
