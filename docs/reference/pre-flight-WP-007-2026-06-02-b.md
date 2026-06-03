---
layout: default
title: "Pre-Flight — WP-007 — 2026-06-02 (re-run, READY)"
---

# Pre-Flight — WP-007 — 2026-06-02 (re-run, READY)

> Re-run of [pre-flight-WP-007-2026-06-02](pre-flight-WP-007-2026-06-02.md) (NOT READY). The blocker (§Repo + disc state — binaries not cached) is cleared by commit `0da45e3` (cached SHA-256s for all four target binaries + disc inventories landed in [tools/exes/README](../../tools/exes/README.md)). Same-day re-run; `-b` suffix per the convention from [wp-lifecycle](wp-lifecycle.md).
>
> Filled-in copy of [docs/reference/pre-flight](pre-flight.md) for [WP-007](../work-packets/WP-007-strings-and-imports.md). Verdict at the bottom.

---

## Header

- **WP:** `WP-007`
- **Title:** `Scooby.exe` strings dump + import table extract
- **Pre-flight date:** `2026-06-02` (re-run; supersedes the morning NOT READY)
- **Targets generation(s):** Gen 1 (Showdown — primary), Gen 1 (Phantom), Gen 2 (Jinx), Gen 3 (Case File #1) — per [vision §Engine Lineage](../01-VISION.md#engine-lineage-2026-06-finding)
- **Targets disc(s):** Showdown, Phantom, Jinx, Case File #1
- **Prior pre-flight:** [pre-flight-WP-007-2026-06-02](pre-flight-WP-007-2026-06-02.md) — NOT READY (blocker: binaries not cached)

## Pre-flight intent

> Re-validating readiness for `WP-007` against the post-cache repo state. Not implementing, not editing engine code, not annotating Ghidra. Verdict only.

## Dependency check

Unchanged from the prior pre-flight. [WORK_INDEX](../work-packets/WORK_INDEX.md) row for WP-007 shows `Deps: —` (no prereq WPs). Vacuously satisfied.

| Prereq | Status in `WORK_INDEX` | Locked on | Notes |
|---|---|---|---|
| — | n/a (no prereqs) | n/a | Phase 0 head; WP-007 sits at the front of pre-work |

## Repo + disc state

- [x] Working tree clean — `git status --short` returns empty after the wp-lifecycle commit (`f3cd590`)
- [x] HEAD on `main` at commit `f3cd590` ("docs: add WP lifecycle reference doc + wire into pre-flight and WORK_INDEX"). Cache landed two commits earlier in `0da45e3`.
- [x] **Disc-on-hand: SATISFIED.** All four target binaries are cached under `tools/exes/<title>/Scooby.exe`. Cache state + SHA-256s + per-title disc inventories are recorded in [tools/exes/README](../../tools/exes/README.md) (committed in `0da45e3`).
- [x] Directory casing normalized to canonical lowercase (sweep recorded in the same commit)
- [x] No prior Ghidra `.gpr` is being re-used — WP-007 is a pre-Ghidra WP
- [x] No prior tool output is being re-used — this is the first run of strings/imports extraction

**Binary identity table** (carry-forward into the execution session's first commit on `scooby-exe.md`):

| Title | Generation | Path | Size (bytes) | SHA-256 |
|---|---|---|---|---|
| Showdown | Gen 1 | `tools/exes/showdown/Scooby.exe` | 487,473 | `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478` |
| Phantom | Gen 1 | `tools/exes/phantom/Scooby.exe` | 483,377 | `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED` |
| Jinx | Gen 2 | `tools/exes/jinx/Scooby.exe` | 847,872 | `136A276872803AC99B0D050B21CC3A83F8E1608F2394C33865CFFF781FB20271` |
| Case File #1 | Gen 3 | `tools/exes/casefile1/Scooby.exe` | 786,432 | `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8` |

**Additionally cached** (gitignored; available for analysis convenience):

- `tools/exes/showdown/Scooby.eng` (2,823 bytes) and `tools/exes/showdown/object.ini` (25,196 bytes) — Gen 1 plain-data files for textual cross-generation comparison
- `tools/exes/casefile1/libexpat.dll` (122,880 bytes) — Gen 3 XML-parser dependency at static path

ISOs are not needed for execution — extraction operates against the cached EXEs. If a future re-run requires re-mounting (e.g., extracting `MMS` payload contents for Gen 2/3 archive-format work), the ISO paths are recorded in the prior NOT READY artifact.

## Scope lock

Unchanged from the prior pre-flight. Anything not explicitly allowed is forbidden.

**Allowed paths for `WP-007`:**

```
docs/formats/scooby-exe.md
docs/reference/pre-flight-WP-007-2026-06-02-b.md
docs/work-packets/WORK_INDEX.md
docs/work-packets/WP-007-strings-and-imports.md
tools/extract_strings.py
tools/extract_imports.py
```

Allowed but local-only (never committed; covered by `.gitignore` on `tools/exes/*`):

```
tools/exes/<title>/strings-ansi.txt
tools/exes/<title>/strings-wide.txt
tools/exes/<title>/imports.txt
```

**Forbidden (any change fails the WP):**

- Game data binaries committed to git (any `*.exe`, `*.eng`, `*.dat`, `*.iso`, `*.ART`, `*.MMF`, `*.MMA`, `*.MMP`, `*.MMS`) — copyright; safety-net in `.gitignore`
- `engines/scooby/**` — engine code is out of scope for this WP (scaffold is WP-010)
- `docs/formats/` files other than `scooby-exe.md` (no spec changes to `tgifile-art.md`, `mmfw-container.md`, `audio-archives.md` from this WP)
- `docs/execution-checklists/EC-001-ghidra-session.md` — the WP-007 → EC-001 Step 3 hand-off is documented in WP-007 §Notes; EC-001 itself is amended later via WP-001's pre-flight, not here
- Any path outside the allowlist above

**Exit check (must run before staging a commit):**

```pwsh
git diff --cached --name-only
```

Any file in the output that doesn't match the allowed list = scope violation. Remediate with `git restore`, not by widening the allowlist post-hoc.

## Risk review

Carried forward from the prior pre-flight with the binaries-missing risk removed (resolved by `0da45e3`).

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Disc mismatch / ISO drift** — cached binaries differ from canonical disc-pressed (re-rip, region variant) | low (post-cache) | high | SHA-256 in the Binary identity table above is the lock. Every Finding in `scooby-exe.md` MUST cite the SHA-256 of the binary it derives from. A re-run against a different SHA invalidates the corresponding row. |
| **Generation conflation** — finding stated as "the engine does X" when X is generation-specific | med | med | Every Findings subsection labeled `#### <Title> (Gen N)`. The Cross-title delta bullet in both Conclusions blocks forces explicit comparison. |
| **Copyright leak** — raw strings dumps containing dialog/error text staged into `docs/formats/scooby-exe.md` wholesale | med | high | Raw `strings-ansi.txt` / `strings-wide.txt` / `imports.txt` files live only under `tools/exes/<title>/` (gitignored). Only structured categorized samples + filename anchors + import surface reach `docs/`. `git diff --cached --name-only` check above is the gate. |
| **Tool output non-determinism** — sort order, locale, or pefile internal iteration changes between runs | low | med | Python scripts in WP-007 §Execution use `sorted(...)` with explicit keys. Run each script twice against the Showdown binary, hash both outputs, confirm identical before promoting any finding. |
| **Scope creep into EC-001 Step 3 re-extraction** — temptation to also document import xrefs and call-site locations | low | med | The §Out of scope bullet "Behavioral analysis of imports" is the boundary. If a finding requires xrefs to justify, it belongs in WP-001's Findings, not WP-007's. |
| **WORK_INDEX inconsistency post-completion** — row still says "15–30 min" but WP body estimates "20–40 min" with cross-title in scope | low | low | Status bump to ✅ Done at WP completion updates the effort estimate in that cell. Already inside §Scope lock allowlist. |

## Verdict

- [x] **READY TO EXECUTE**
- [ ] **NOT READY**

**Rationale:** every section above carries concrete content. The prior NOT READY's sole blocker (binaries not cached) is resolved — all four target binaries are cached with SHA-256s recorded and verifiable. Scope lock is explicit. Risk review carries six concrete mitigations, each tied to a specific WP discipline.

**Authorization:** the executing session may open against the §Scope lock allowlist above. Outputs land per WP-007 §Output specification. The §Exit criteria from the WP body govern when the WP can flip to ✅ Done.

**Reviewer:** Jeff (BarefootBetters)
**Date:** 2026-06-02 (re-run)

A `READY` verdict authorizes opening the execution session. It does not authorize any change beyond the §Scope lock allowlist.

---

## After execution — lessons learned

*To be filled by the executing session after WP-007 closes. If the WP surfaced a preventable gap pre-flight should have caught, record one line here. A WP that closes with "No lessons learned" is a complete and valid outcome — write it explicitly rather than leaving the section blank.*
