---
layout: default
title: "WP-005: Engine-Family Check"
---

# WP-005: Engine-family check across Case File ISOs

**Status:** 📝 Drafted
**Phase:** 1 — Format Research
**Depends on:** —
**Companion EC:** [EC-003](../execution-checklists/EC-003-engine-family-check.md)
**Estimated effort:** Half-day

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
- If the answer is "INDETERMINATE," recommend re-running after WP-001 closes (Ghidra may reveal whether the same loader code is present in `Scooby.exe` across versions, even if archive bytes differ at the surface).
- The hypothesis from the vision is that the post-TerraGlyph studio inherited the engine via IP transfer through the TLC → Riverdeep acquisition. If true, the file structures will match. If false, the Case Files were rebuilt on a different engine and the structures will diverge clearly.
