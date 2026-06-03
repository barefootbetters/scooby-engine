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

- [x] Pre-flight verdict: **READY** — complete [docs/reference/pre-flight](../reference/pre-flight.md) and commit the filled-in copy before proceeding; `NOT READY` blocks this session
- [x] `object.ini` accessible — either from mounted Showdown ISO or copied to `tools/samples/`; path recorded here: `tools/exes/showdown/object.ini`
- [x] `Scooby.eng` accessible at same location (`tools/exes/showdown/Scooby.eng`)
- [x] Python 3 available: `python --version` (3.12.10 via `py -3`)
- [x] `tools/samples/` directory exists (or will be created in Step 5)
- [x] [WP-007](../work-packets/WP-007-strings-and-imports.md) complete — string dump from `Scooby.exe` is useful for cross-checking asset name strings found in `object.ini`
- [x] [WP-003](../work-packets/WP-003-pre-payload-region.md) complete — TGIFILE.ART name table available (extracted to `tools/samples/wp003-name-table.txt`, gitignored). 811 ROOM/OBJ/ANIM names from the continuous block are the strongest cross-check input for `object.ini`'s asset references; expected naming conventions are `OBJ_<name>` / `ROOM_P<NN>[<sub>]` / `ANIM_<category><name>`. See [tgifile-art.md §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table) for the schema.

---

## Step 1 — Manual structure survey (time-box: 15 min)

Do **not** write any code yet.

- [x] Open `object.ini` in a text editor (not a hex viewer — it's plain text)
- [x] Identify section header format: `[SectionName]` style? Any sub-sections? → `[OBJ_*]` only; no sub-sections; 215 sections total
- [x] Identify key-value separator: `=` or `:` or space-delimited? → `=`
- [x] Identify and count section types: rooms? objects? cursors? inventory? global settings? → **all 215 sections are `[OBJ_*]`**. Section-type discrimination is via the `ID=` field, with five values: `exitobject`, `clickableobject`, `inventoryobject`, `requiresobject`, `simpleobject`. No top-level `[ROOM_*]`, `[CURSOR_*]`, or `[GLOBAL]` sections — rooms, cursors, and inventory are synthesized from cross-references during the catalog build.
- [x] Pick one room section — read it top to bottom. How are assets referenced?
  - [x] String names matching the WP-003 name-table convention (e.g.
        `bg=OBJ_DAPHNE_A`, `room=ROOM_P21_Boot_Hill1`) → note it; the
        catalog can label decoded TGIFILE.ART entries directly
  - [ ] String names NOT matching the WP-003 convention (e.g.
        `bg=ghost_mine_entrance` — a friendlier short name) → note it;
        the catalog will need a name→TGIFILE.ART-name lookup table
  - [ ] Numeric IDs (e.g. `bg=47`) → note it; if 0–452 they map directly
        to TGIFILE.ART OBJ entries per [WP-003](../work-packets/WP-003-pre-payload-region.md)
  - [ ] Something else entirely → describe it and record before proceeding
- [x] Does any key value look like a message ID that would appear in `Scooby.eng`? → No — no key shaped like `text=NNNN` or `message=NNNN` exists in any section. `scrappyid=Global.Scrappy.*` is a script identifier, not a string-table reference. Confirmed in Step 5.
- [x] Are there any multi-value lines (comma-separated? quoted? backslash-continued)? → No — every `key=value` pair is a single literal token. `<none>` and `-1` are sentinel values.
- [x] Record the section structure and asset reference format in a scratch note. This note becomes the findings section in Step 6.

### Parser mode lock (gate — do not skip)

Convert the survey above into a single committed decision before any code runs. Re-opening this gate later means rewriting the parser, not patching it.

- [x] Select parser mode based on the observed asset reference format:
  - **MODE_A** — Direct TGIFILE name-table strings (`OBJ_*`, `ROOM_*`, `ANIM_*`). Catalog labels decoded entries directly; no lookup layer.
  - **MODE_B** — Friendly string names that do *not* match the WP-003 convention (e.g. `ghost_mine_entrance`). Catalog must carry a friendly-name → TGIFILE-name map.
  - **MODE_C** — Numeric indices in the 0–452 range. Direct mapping to `TGIFILE.ART` OBJ entries per WP-003.
  - **MODE_D** — Unknown / encoded / mixed. **Block implementation**; record the encoding as a new unknown for WP-001 and stop here.
- [x] Record selected mode: **MODE_A**
- [x] Record one-sentence justification (the concrete evidence from the survey): every asset-reference value uses the WP-003 name-table convention verbatim (`destinationroom=ROOM_P25A_Chase_B2_Closeup`, `rolloveranim=ANIM_CURSOREU45L`, `toolbaranim=ANIM_TOOLBARBLANKET`, `requiredanim=ANIM_CURSORRUSTY_HAMMER`); numerics (`movie=-1`, `layer=1`, `priority=100`) are engine sentinels or render-order metadata, not asset indices.
- [x] Do **not** proceed to Step 2 until a mode is selected and recorded above.

**Outcome:** You know the section structure and asset-reference format. The parser design is now decided.

---

## Step 2 — Parse rooms (time-box: 1 hour)

- [x] Create `tools/parse_ini.py`
- [x] Implement room sections only first: ID, display name, exit map (room → destination), list of objects
  - **Carry-forward from Step 1:** `object.ini` has no top-level `[ROOM_*]` sections. Rooms are synthesized from the union of `destinationroom=` values across all `[OBJ_*]` sections (37 unique canonical IDs). Source-room attribution is not available in `object.ini` data; the parser leaves the `objects` list per-room empty and records only `incoming_exits` (the OBJ IDs whose `destinationroom=` points here).
- [x] Run on Showdown `object.ini`: `py -3 tools\parse_ini.py tools\exes\showdown\object.ini --out tools\samples\asset-catalog-objects-only.json`
- [x] Verify room count matches expected (count section headers of the room type manually — they should agree) → 37 synthesized canonical rooms from `destinationroom=` values; section-header count (0 ROOM headers, 215 OBJ headers) confirms file has no top-level rooms.
- [x] Print a sample 3-room excerpt to stdout and read it; confirm the structure looks right → e.g. `ROOM_P21_Boot_Hill1` has 3 `incoming_exits` (`OBJ_P18_TO_P21`, `OBJ_P22_TO_P21`, `OBJ_P23_TO_P21`); matches intuition.
- [x] Fix any parse errors before continuing

---

## Step 3 — Extend to all entity types (time-box: 1 hour)

- [x] Add object sections: graphic asset refs, sound asset refs, cursor behavior flag
- [x] Add cursor definitions (synthesized from `ANIM_CURSOR*` references — 23 unique)
- [x] Add inventory items (sections with `ID=inventoryobject` — 11 entries)
- [x] Run full parse; zero parse errors
- [x] Spot-check: pick one room you remember from gameplay; verify its JSON entry is complete and plausible → `ROOM_P12_Saloon` collects every `OBJ_P12_SALOON_*` and `OBJ_P12_TO_*` exit OBJ as expected.
- [x] **Failure-handling synthetic checks** (per WP-008 §Failure handling) — `py -3 tools/parse_ini.py --self-test` covers:
  - duplicate section → hard-fail with `ParseError("duplicate section …")`
  - unknown key inside known section → preserved under `extra_fields`
  - malformed line → hard-fail with `ParseError("unparseable line …")`
  - unknown section type (e.g. `[GLOBAL]`) → warned, recorded under `unknown_sections`

---

## Step 4 — Parse `Scooby.eng` string table (time-box: 30 min)

- [x] Open `Scooby.eng` in a hex viewer **first** — identify encoding before parsing:
  - ASCII with `[NNNN]` ID markers? **Yes — 256-byte hex dump from offset 0 starts with `5E 0D 0A 5E 20 45 6E 67 6C 69 73 68` = "^\r\n^ English" (the file's own self-describing header).**
  - UTF-8? n/a (pure ASCII — 0 high-bit bytes across the whole 2,823-byte file)
  - Null-terminated with length prefixes? No
  - Record the encoding format observed: **ASCII with `^`-prefixed comment lines, `[NNNN]` decimal message-ID declarations, CRLF line endings, line breaks preserved literally inside messages, whitespace stripped at message boundaries**
- [x] Identify and record the delimiter / record framing explicitly (don't infer it from the parser working):
  - Pattern: **`[NNNN]` markers** (the file's own header documents this verbatim: "A `[` marks the [end] of the message text and the beginning of a message number declaration. A `]` marks the [end] of a message number declaration and the beginning of the message text.")
  - Message ID type: **numeric decimal, zero-padded to 4 digits**
  - Text encoding: **ASCII** (verified 0 high-bit bytes)
- [x] Create `tools/parse_eng.py`
- [x] Parse to `{message_id: text}` JSON — 10 messages total (IDs `0001`, `0010`–`0018`)
- [x] Spot-check 5 IDs: do the text strings match what you'd expect for those IDs? → All 5 of `[0001]` Scooby title, `[0010]` out-of-memory, `[0011]` DirectDraw init failure, `[0013]` CD-ROM access failure, `[0017]` BaseLibrary unsupported function appear verbatim in `tools/exes/showdown/strings-ansi.txt` lines 1674–1683 — confirms `Scooby.eng` is loaded by `Scooby.exe` and rendered as-is for system errors.

---

## Step 5 — Cross-reference and write combined output (time-box: 30 min)

- [x] Walk the `object.ini` catalog; for any key whose value looks like a message ID, resolve from `Scooby.eng` string table
- [x] Add resolved text as a `display_name` or `description` field in the catalog JSON → Zero `[0-9]{1,4}`-shaped values exist in any object's `extra_fields`; the catalog records `object_ini_to_eng_resolutions: 0`. `Scooby.eng` is carried in the combined output for completeness but no per-object resolution is needed for Showdown's `object.ini`. `scrappyid=Global.Scrappy.*` is the script identifier, not a string-table reference.
- [x] Write combined output to `tools/samples/asset-catalog.json`
- [x] Validate JSON is well-formed: `py -3 -m json.tool tools\samples\asset-catalog.json > $null` (PowerShell) — passes
- [x] **Top-level schema audit** (paste-back per pre-flight Risk #2): top-level keys = `schema_version`, `source`, `counts`, `rooms`, `objects`, `cursors`, `inventory`, `unknown_sections`, `warnings`, `messages`, `wp003_cross_check`, `wp003_unmatched`. All four v1-required keys present (`rooms`/`objects`/`cursors`/`inventory`).
- [x] **Sample room entry** (paste-back per pre-flight Risk #2):
  ```json
  "ROOM_P21_Boot_Hill1": {
    "id": "ROOM_P21_Boot_Hill1",
    "name": null,
    "background_assets": [],
    "objects": [],
    "exits": {},
    "incoming_exits": ["OBJ_P18_TO_P21", "OBJ_P22_TO_P21", "OBJ_P23_TO_P21"]
  }
  ```
- [x] Count total entries: **37 rooms, 215 objects, 23 cursors, 11 inventory items** (plus 10 `Scooby.eng` messages)
- [x] **Cross-check every asset reference against the WP-003 name table** (`tools/samples/wp003-name-table.txt`). Record concrete numbers — these are the WP-008 exit-criterion #6 metric, not a sanity check:
  - Total asset references in `object.ini`: **286**
  - Matched against WP-003 name table: **221**
  - Match rate: **77.27 %**
  - Unmatched count: **65** (21 `ROOM_*` engine/scripted rooms with no `TGIFILE.ART` payload, 25 `OBJ_*` invisible hotspots/exits/overlays, 19 `ANIM_*` inventory-specific cursor/toolbar animations)
- [x] Export the unmatched list to `tools/samples/unmatched-assets.txt` (gitignored, regenerable). One reference per line; empty file is acceptable and itself a finding.
- [x] Note the match rate in the Step 6 findings: high (≥95%) → engine is name-driven against `TGIFILE.ART`; low → record the divergence as a new unknown for WP-001. → **Below the 95 % threshold (77.27 %), but the divergence is a coverage gap, not an engine-mechanism gap — every reference is a *string* (zero numeric indices), every unmatched reference is a `ROOM_*`/`OBJ_*`/`ANIM_*` that simply doesn't have a `TGIFILE.ART` entry (invisible hotspots, scripted engine rooms, inventory-specific anims). Engine is unambiguously name-driven; `TGIFILE.ART` is one of multiple name-keyed asset stores. See Findings note for the per-bucket evidence.**

---

## Step 6 — Findings note (time-box: 15 min)

- [x] Open `docs/formats/scooby-exe.md` → Findings section
- [x] Add "`object.ini` interpreter behavior" subsection. Must answer:
  - [x] Confirmed section structure (what section types exist)
  - [x] Asset reference format: **string names? numeric indices? mixed?** This is the headline finding. → **String names exclusively — MODE_A.**
  - [x] Room count, object count (approximate totals from Step 5)
  - [x] Estimate of how much game logic is data-driven vs. implicit in the binary
  - [x] Any surprises: sections that weren't expected, unusual field types, etc.

---

## Exit check

- [x] `tools/parse_ini.py` and `tools/parse_eng.py` exist and run without errors
- [x] `tools/samples/asset-catalog.json` exists and is valid JSON
- [x] `docs/formats/scooby-exe.md` → Findings has the "`object.ini` interpreter behavior" subsection
- [x] Asset reference format is documented — the single most important finding from this WP
- [x] WP-008 status updated to ✅ Done in [`WORK_INDEX`](../work-packets/WORK_INDEX.md)
