---
layout: default
title: "EC-004: object.ini Catalog Checklist"
---

# EC-004: `object.ini` + `Scooby.eng` asset catalog checklist

**Paired WP:** [WP-008](../work-packets/WP-008-object-ini-catalog.md)
**Purpose:** Step-by-step checklist for executing WP-008 without skipping the
manual structure survey that determines the entire parse strategy.

The key risk in WP-008 is writing a parser against assumptions about the file
format before actually reading it. If asset references turn out to be numeric
indices rather than string names (or vice versa), a parser written against the
wrong assumption needs a full rewrite. This checklist front-loads the 15-minute
manual survey that locks in the correct approach before any code is written.

---

## Pre-flight

- [ ] Pre-flight verdict: **READY** — complete [docs/reference/pre-flight](../reference/pre-flight.md) and commit the filled-in copy before proceeding; `NOT READY` blocks this session
- [ ] `object.ini` accessible — either from mounted Showdown ISO or copied to `tools/samples/`; path recorded here: __________
- [ ] `Scooby.eng` accessible at same location
- [ ] Python 3 available: `python --version`
- [ ] `tools/samples/` directory exists (or will be created in Step 5)
- [ ] [WP-007](../work-packets/WP-007-strings-and-imports.md) complete — string dump from `Scooby.exe` is useful for cross-checking asset name strings found in `object.ini`

---

## Step 1 — Manual structure survey (time-box: 15 min)

Do **not** write any code yet.

- [ ] Open `object.ini` in a text editor (not a hex viewer — it's plain text)
- [ ] Identify section header format: `[SectionName]` style? Any sub-sections?
- [ ] Identify key-value separator: `=` or `:` or space-delimited?
- [ ] Identify and count section types: rooms? objects? cursors? inventory? global settings?
- [ ] Pick one room section — read it top to bottom. How are assets referenced?
  - [ ] String names (e.g. `bg=ghost_mine_entrance`) → note it
  - [ ] Numeric IDs (e.g. `bg=47`) → note it
  - [ ] Something else entirely → describe it and record before proceeding
- [ ] Does any key value look like a message ID that would appear in `Scooby.eng`?
- [ ] Are there any multi-value lines (comma-separated? quoted? backslash-continued)?
- [ ] Record the section structure and asset reference format in a scratch note. This note becomes the findings section in Step 6.

**Outcome:** You know the section structure and asset-reference format. The parser design is now decided.

---

## Step 2 — Parse rooms (time-box: 1 hour)

- [ ] Create `tools/parse_ini.py`
- [ ] Implement room sections only first: ID, display name, exit map (room → destination), list of objects
- [ ] Run on Showdown `object.ini`: `python tools\parse_ini.py <path\to\object.ini>`
- [ ] Verify room count matches expected (count section headers of the room type manually — they should agree)
- [ ] Print a sample 3-room excerpt to stdout and read it; confirm the structure looks right
- [ ] Fix any parse errors before continuing

---

## Step 3 — Extend to all entity types (time-box: 1 hour)

- [ ] Add object sections: graphic asset refs, sound asset refs, cursor behavior flag
- [ ] Add cursor definitions
- [ ] Add inventory items
- [ ] Run full parse; zero parse errors
- [ ] Spot-check: pick one room you remember from gameplay; verify its JSON entry is complete and plausible

---

## Step 4 — Parse `Scooby.eng` string table (time-box: 30 min)

- [ ] Open `Scooby.eng` in a hex viewer **first** — identify encoding before parsing:
  - ASCII with `[NNNN]` ID markers?
  - UTF-8?
  - Null-terminated with length prefixes?
  - Record the encoding format observed: __________
- [ ] Create `tools/parse_eng.py`
- [ ] Parse to `{message_id: text}` JSON
- [ ] Spot-check 5 IDs: do the text strings match what you'd expect for those IDs?
  If you have WP-009 screenshots, verify 1–2 strings appear visibly in those screenshots.

---

## Step 5 — Cross-reference and write combined output (time-box: 30 min)

- [ ] Walk the `object.ini` catalog; for any key whose value looks like a message ID, resolve from `Scooby.eng` string table
- [ ] Add resolved text as a `display_name` or `description` field in the catalog JSON
- [ ] Write combined output to `tools/samples/asset-catalog.json`
- [ ] Validate JSON is well-formed: `python -m json.tool tools\samples\asset-catalog.json > nul`
- [ ] Count total entries: __ rooms, __ objects, __ cursors, __ inventory items

---

## Step 6 — Findings note (time-box: 15 min)

- [ ] Open `docs/formats/scooby-exe.md` → Findings section
- [ ] Add "`object.ini` interpreter behavior" subsection. Must answer:
  - [ ] Confirmed section structure (what section types exist)
  - [ ] Asset reference format: **string names? numeric indices? mixed?** This is the headline finding.
  - [ ] Room count, object count (approximate totals from Step 5)
  - [ ] Estimate of how much game logic is data-driven vs. implicit in the binary
  - [ ] Any surprises: sections that weren't expected, unusual field types, etc.

---

## Exit check

- [ ] `tools/parse_ini.py` and `tools/parse_eng.py` exist and run without errors
- [ ] `tools/samples/asset-catalog.json` exists and is valid JSON
- [ ] `docs/formats/scooby-exe.md` → Findings has the "`object.ini` interpreter behavior" subsection
- [ ] Asset reference format is documented — the single most important finding from this WP
- [ ] WP-008 status updated to ✅ Done in [`WORK_INDEX`](../work-packets/WORK_INDEX.md)
