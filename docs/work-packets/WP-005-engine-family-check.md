---
layout: default
title: "WP-005: Engine-Family Check"
---

# WP-005: Engine-family check across Case File ISOs

**Status:** ✅ Done (2026-11-13)
**Phase:** 1 — Format Research
**Depends on:** —
**Companion EC:** [EC-003](../execution-checklists/EC-003-engine-family-check.md)
**Estimated effort:** Half-day
**Pre-flight (Case File #2 half):** [pre-flight-WP-005-2026-11-13](../reference/pre-flight-WP-005-2026-11-13.md)

---

## Result (2026-11-13)

| Disc | Code lineage | Formats | Verdict |
|---|---|---|---|
| Case File #1 (2002) | Same lineage. Inherited TerraGlyph object files (an MSVC 5.0 C++ 8034 ×17 entry identical to Jinx's, plus Jinx's Linker build 8168); `MMFW` resource strings and `MMVisualCursor.cpp` shared with Jinx (2026-06) | `MMFW` archives and XML config, not `TGIFILE.ART` | **Same engine lineage, different formats.** Under EC-003's file-presence test it is INCOMPATIBLE (no `TGIFILE.ART` or `object.ini`). It stays in scope as the Gen 3 stretch tier because of the code inheritance, per VISION's 2026-06 revision of the scope rule, which this WP confirms. |
| Case File #2 (2003) | **Not the lineage.** No RTTI, `MMFW`, error templates, source paths or MSVC 5.0 C++ objects shared; dynamic CRT; `R*` framework with Miles, LZO, libjpeg | `.bul`/`.inx` bulk archives | **INCOMPATIBLE**: a different engine |

The deciding evidence for Case File #2: a *Powerpuff Girls* demo on the
same disc uses the same `.bul`/`.inx` resources. Its engine DLLs
(`trinket.dll`, `ompp32x.dll` "OM++", `tcx.dll`, `rbink6x.dll`) carry 17 of
Case File #2's `R*` class names and its bulk-file loader errors. The same
framework runs the publisher's launcher on both Case File discs. Full
evidence: [scooby-exe §Case File #2](../formats/scooby-exe.md#case-file-2-wp-005).

| Exit criterion | Result |
|---|---|
| 1. File listings for Case File #1 and #2 | ✅ Read from the ISOs with 7-Zip (Showdown 236 files, Case File #1 271, Case File #2 277, minus platform noise). Kept local; see below. |
| 2. Diff against Showdown | ✅ Shared basenames: Case File #1 122, Case File #2 48. All of them are installer, DirectX, registration, Acrobat, font, Bink or publisher files. **Neither disc has a single Gen 1 engine file** (`TGIFILE.ART`, `Scooby.exe`, `object.ini`, `Scooby.eng`, `*.dat`). Recorded here and in VISION. |
| 3. Verdict per disc | ✅ Table above |
| 4. `tgifile-art.md` cross-title section | ✅ Neither Case File has a `TGIFILE.ART` to compare; recorded |
| 5. VISION Phase 5 scope rule | ✅ Case File #2 moved to Excluded. The Engine Lineage section, implementation implication and cross-title risk are corrected (three generations, three archive formats). |

**Deliverable deviation:** the WP names `docs/findings/case-file-disc-diff.md`,
but `docs/findings/*` is gitignored except its README. The diff summary is
recorded in this section and in VISION instead, and the raw listings stay
in the session scratchpad.

**Not done here:** the project `README.md` title table still says
"engine-family verdict pending (WP-005)" for Case File #2, and
[WP-011](WP-011-casefile-decompdecomp.md) still plans a Case File #2
comparison as "Gen 4". Both sit outside this WP's scope lock and are listed
as follow-ups.

---

## Goal

Determine whether Case File #1 and Case File #2 use the same engine as the TerraGlyph trio (Showdown / Phantom / Jinx). Specifically: do their discs contain `TGIFILE.ART`, `Scooby.exe`, `object.ini` with compatible structure? Satisfies Phase 1 exit criterion #4 and locks Phase 5 scope per the vision's "Scope rule."

## Background

TerraGlyph Interactive Studios shut down in 2001 (Wikipedia-confirmed). The Case File titles (#1 = 2002, #2 = 2003) shipped after that closure under a different developer. The vision currently treats the Case Files as "conditional" — included if engine-compatible, excluded if not.

This WP is the empirical answer. The findings shape:
- Phase 5 scope rule (minimum / extended / conditional)
- `02-SCUMMVM-INTEGRATION.md` §3 detection table (one engine entry vs. two)
- Whether the eventual ScummVM PR claims 3 titles or 5

## Scope

In scope:
- Mount each Case File ISO read-only
- Generate a file listing (name + size) per disc
- Diff against Showdown's file listing
- For files that exist in both: hex-inspect the first 64 bytes of `TGIFILE.ART`, `Scooby.exe`, `object.ini` to check for matching structure
- Write a binary go/no-go per Case File ISO
- Record findings into `docs/formats/tgifile-art.md` Findings → "Cross-title verification" and `docs/01-VISION.md` Phase 5 scope rule

Out of scope:
- Decoding any payload in Case File `TGIFILE.ART` (out of WP-002 scope until base case works on Showdown)
- Phantom and Jinx verification — those are TerraGlyph titles and assumed compatible until proven otherwise; spot-check is optional
- Activity Challenge or Case File #3 verification — both already flagged as out of scope, no work needed

## Dependencies

- Disc mounting (Windows native, WinCDEmu, or equivalent)
- Hex viewer
- Disc-mounted Showdown for diff reference

## Exit criteria

1. File listing produced for Case File #1 and Case File #2 discs.
2. Diff against Showdown's listing produced and recorded in `docs/01-VISION.md` or a sibling note.
3. For each of Case File #1 and #2, a binary verdict: `COMPATIBLE` (shares engine with TerraGlyph trio), `INCOMPATIBLE` (different engine, treat as out of scope), or `INDETERMINATE` (file names match but headers don't — needs deeper inspection).
4. `docs/formats/tgifile-art.md` Cross-title verification section populated with what the first 64 bytes of each Case File `TGIFILE.ART` look like vs. Showdown's.
5. Vision doc Phase 5 scope rule confirmed or updated based on the verdict.

## Deliverables

- File listing diffs at `docs/findings/case-file-disc-diff.md` (new file, brief)
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — cross-title section
- Possible update to [`docs/01-VISION.md`](../01-VISION.md) Phase 5 scope rule

## Notes

- Parallel-safe with WP-001 through WP-004.
- This is a small WP but the answer it produces is load-bearing — it determines whether the ScummVM engine ships covering 3 titles or 5. Worth doing early so subsequent work is correctly scoped.
- Function-level evidence: [WP-011](WP-011-casefile-decompdecomp.md) (decompdecomp collaboration) plans identical-function counts for Jinx ↔ Case File #1, then Case File #1 ↔ Case File #2. Those counts are inputs to this WP's verdict, not a verdict themselves.
- If the answer is "INDETERMINATE," recommend re-running after WP-001 closes (Ghidra may reveal whether the same loader code is present in `Scooby.exe` across versions, even if archive bytes differ at the surface).
- The hypothesis from the vision is that the post-TerraGlyph studio inherited the engine via IP transfer through the TLC → Riverdeep acquisition. If true, the file structures will match. If false, the Case Files were rebuilt on a different engine and the structures will diverge clearly.
