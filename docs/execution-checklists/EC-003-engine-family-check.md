---
layout: default
title: "EC-003: Engine-Family Check Protocol"
---

# EC-003: Engine-family check protocol

**Paired WP:** [WP-005](../work-packets/WP-005-engine-family-check.md)
**Executed:** 2026-11-13 (Case File #2 half; Case File #1 in 2026-06). See [WP-005 §Result](../work-packets/WP-005-engine-family-check.md#result-2026-11-13).
**Purpose:** Procedural checklist for diffing Case File #1 and Case File #2 disc contents against Showdown, producing a binary engine-compatibility verdict per disc.

The trap this checklist exists to prevent: hand-waving "looks similar" verdicts. Compatibility is a structural question with a structural answer. If the answer comes back as "INDETERMINATE," that's a real verdict — record it; don't fudge it to COMPATIBLE.

---

## Pre-flight

- [x] Disc-mount tooling available (Windows native mount, WinCDEmu, or `7z l` for direct ISO listing) *7-Zip `7z l -slt` on the ISOs; no mount.*
- [x] Hex viewer available *Python.*
- [x] Showdown ISO mounted or extracted to known location; path: __________ *`C:\pcloud\scooby-engine\Scooby Doo Showdown in Ghost Town.iso` (listed, not mounted).*
- [x] `docs/findings/` directory exists (create if missing) *`docs/findings/*` is gitignored except its README, so the outputs live in the session scratchpad and their summary in WP-005 §Result.*

## Step 1 — File listings (time-box: 30 min)

For each disc — Showdown (reference), Case File #1, Case File #2:

- [x] Generate a file listing (name + size) of every file on the disc *Showdown 236, Case File #1 271, Case File #2 277 files.*
- [x] Save listings as `docs/findings/disc-listing-showdown.txt`, `disc-listing-case-file-1.txt`, `disc-listing-case-file-2.txt` *Local only (see above).*
- [x] Strip platform metadata noise (Windows thumbs.db, Mac DS_Store, autorun.inf) before diffing

**Quick win:** if a disc lacks `TGIFILE.ART` or `Scooby.exe` entirely, the verdict is immediately INCOMPATIBLE — no further work needed for that disc.

## Step 2 — Filename-level diff (time-box: 15 min)

For each Case File disc:

- [x] Compute: files in Showdown ∩ files in Case File (intersection) *By basename: Case File #1 122, Case File #2 48. All installer, DirectX, registration, Acrobat, font, Bink or publisher files.*
- [x] Compute: files in Showdown \ files in Case File (Showdown-only — could indicate missing engine pieces) *Showdown-only: 95 / 169, including every Gen 1 engine file.*
- [x] Compute: files in Case File \ files in Showdown (Case-File-only — could indicate new engine pieces) *Case-File-only: 108 / 219.*
- [x] Record intersection size and the two "missing" sets in `docs/findings/case-file-disc-diff.md` *Recorded in WP-005 §Result.*

**Decision rule for this step:**

| Outcome | Action |
|---|---|
| `TGIFILE.ART`, `Scooby.exe`, `object.ini` all present in Case File | Continue to Step 3 |
| Any of the three is absent | Verdict for this disc = INCOMPATIBLE; skip Step 3; document |
| All three present + intersection ≥ 80% of Showdown's file count | High confidence in compatibility; continue to Step 3 |
| All three present + intersection < 50% | Likely INCOMPATIBLE despite filename match; Step 3 will confirm |

## Step 3 — Structural spot-check (time-box: 1 hour total, ~20 min per disc)

For each Case File disc, hex-inspect the first 64 bytes of:

- [x] `TGIFILE.ART` — compare against Showdown's known opener: *Absent on both Case File discs. The decision rule makes both format-INCOMPATIBLE.*
  - First 4 bytes: should be `45 00 00 00` (69, little-endian) if same group count
  - Bytes 4–7 should look like a 4-byte value in the same range as Showdown's group descriptors (`0x34328117`–`0x44C440B9`)
- [x] `Scooby.exe` — compare PE header characteristics: *Went further than the PE header for Case File #2: Rich Header, imports, strings and RTTI (scooby-exe §Case File #2).*
  - DOS stub identical?
  - PE signature offset identical?
  - Timestamp (different is expected — different build date)
  - Section count identical?
- [x] `object.ini` — compare structurally (not byte-for-byte; content will differ): *Absent on both Case File discs.*
  - First non-blank line: section header in `[Name]` format?
  - Same section names appearing (e.g. `[Rooms]`, `[Objects]`, `[Cursors]`)?

Record each comparison as a row in `docs/findings/case-file-disc-diff.md`.

## Step 4 — Verdict (time-box: 15 min)

For each of Case File #1 and Case File #2, produce one of three verdicts:

| Verdict | Criteria |
|---|---|
| **COMPATIBLE** | All three files present; `TGIFILE.ART` opener matches Showdown's structure; `Scooby.exe` PE structure consistent; `object.ini` uses same section naming |
| **INCOMPATIBLE** | Any of the three target files missing, OR `TGIFILE.ART` opener structurally divergent (different magic, different group descriptor range, clearly different format) |
| **INDETERMINATE** | Filenames match but structures disagree in ways that don't cleanly resolve (e.g. `TGIFILE.ART` opener has same shape but different sized group descriptor table). Requires Ghidra session (extension of WP-001) on Case File `Scooby.exe` to settle. |

Do not pick COMPATIBLE if the data is INDETERMINATE. The vision's Phase 5 scope rule treats COMPATIBLE as a green light to ship those titles in the upstream PR — false COMPATIBLE = bad PR.

## Step 5 — Document and propagate (time-box: 30 min)

- [x] Final verdict per disc recorded in `docs/findings/case-file-disc-diff.md` *In WP-005 §Result.*
- [x] `docs/formats/tgifile-art.md` → Findings → "Cross-title verification" populated with the comparison
- [x] `docs/01-VISION.md` → Phase 5 scope rule updated: *Mixed outcome: Case File #1 stays in the Gen 3 stretch tier (code inheritance, the 2026-06 revision), and Case File #2 moves to Excluded.*
  - If both COMPATIBLE: extend the "Extended" tier to include Case Files explicitly
  - If both INCOMPATIBLE: move Case Files to "Excluded" tier; PR scope is TerraGlyph trio only
  - If mixed: split — name which Case File goes where
  - If any INDETERMINATE: leave under "Conditional" with a note that WP-001 extension is the resolver
- [x] WP-005 status updated to ✅ Done in [`WORK_INDEX.md`](../work-packets/WORK_INDEX.md)

## Definition of done

- [x] `docs/findings/case-file-disc-diff.md` exists with binary verdicts for Case Files #1 and #2 *Deviation: verdicts are in WP-005 §Result, because `docs/findings/` is gitignored.*
- [x] Vision doc Phase 5 scope rule reflects the verdicts
- [x] WP-005 exit criteria #1–#5 satisfied
