---
layout: default
title: "WP-008: object.ini Asset Catalog"
---

# WP-008: `object.ini` + `Scooby.eng` logical asset catalog

**Status:** ✅ Done (2026-06-03)
**Phase:** Pre-Work (before WP-002)
**Depends on:** —
**Companion EC:** [EC-004](../execution-checklists/EC-004-object-ini-catalog.md)
**Estimated effort:** Half-day
**Actual effort:** ~3 hours (single session, 2026-06-03)
**Findings landed in:** [scooby-exe.md → `object.ini` interpreter behavior](../formats/scooby-exe.md#objectini-interpreter-behavior)
**Headline answer:** Engine is **name-driven**. 100 % of `object.ini` asset references are strings in the WP-003 name-table convention (`ROOM_*`/`OBJ_*`/`ANIM_*`); zero numeric indices. 77.27 % cross-check match rate (221 / 286) against the `TGIFILE.ART` name table — the 65 unmatched are scripted/engine-rendered rooms, invisible hotspot objects, and inventory-specific cursor animations that live in other name-keyed stores.

---

## Goal

Parse `object.ini` (1,405 lines, plain INI) and `Scooby.eng` (localized
string table) into machine-readable JSON structures, producing a logical
asset catalog that maps room IDs → objects → asset references. This
becomes the ground-truth reference for decoder verification: when
`probe_art.py` decodes TGIFILE.ART entry N, you can look up what that
entry is supposed to represent.

Because of [WP-003](WP-003-pre-payload-region.md)'s baseline (engine
name table is 1:1 with the OBJ entry table), this WP is also a **truth
test**: it determines whether the engine is **name-driven** (string
references resolved through the name table) or **index-driven** (numeric
references that hit `TGIFILE.ART` entries directly). That answer
constrains WP-001 decoder design and WP-002's labeling strategy.

## Background

Without a logical asset map, Phase 1 exit criterion #1 — "visually matches
in-game output" — is an honor-system claim. With one, it becomes a testable
assertion: "Entry 47 is the asset referenced by `[Library]`'s background
field; the decoded image should show the library entrance."

Both source files are **human-readable, available today, with zero RE
dependency**. This is pure data engineering. The earlier it runs, the more
useful WP-002 and WP-003 outputs become.

**WP-003 baseline (2026-06-02) — partial pre-answer to the "asset reference format" question.**
[WP-003](WP-003-pre-payload-region.md) characterized the `TGIFILE.ART`
pre-payload region as the engine's resource-name catalog and established
that the **OBJ section of that name table is 1:1 with the asset entry
table** (453 OBJ records, IDs contiguous 0–452, matching `asset_count` —
see [tgifile-art.md §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table)).
This means `entry[i]` in `TGIFILE.ART` is the payload for OBJ id `i`. Two
practical consequences for WP-008:

1. **`object.ini` references almost certainly use either `OBJ_<name>` strings
   or numeric OBJ IDs 0–452.** The "indirect / encoded references" branch
   in §Notes is now much less likely — WP-003 didn't find an encoded
   indirection layer. The catalog's primary verification surface becomes
   "do `object.ini`'s asset references match the TGIFILE.ART OBJ name table
   1:1?"
2. **Concrete naming priors WP-003 observed in the name table:**
   - ROOMs use `ROOM_P<NN>[<sub>]` (e.g. `ROOM_P21_Boot_Hill1`,
     `ROOM_P25A_Chase_B2_Closeup`), plus a small set of named engine rooms
     (`ROOM_Options`, `ROOM_Quit`, `ROOM_Credits`, `ROOM_Cheat`)
   - OBJs use `OBJ_<name>` (e.g. `OBJ_DAPHNE_A`, `OBJ_P40_TO_P33`)
   - ANIMs use `ANIM_<category><name>` (e.g. `ANIM_CURSORARROW`,
     `ANIM_TOOLBARCOMPUTER_IDLE`, `ANIM_FRED_ENDWALK_DL_A1`)

If `object.ini`'s strings match these patterns, the catalog can label
decoded `TGIFILE.ART` entries directly (e.g. `entry_000_DAPHNE_A.png`)
without any further reverse engineering. If they diverge, that divergence
is itself a finding worth recording.

## Scope

In scope:
- `tools/parse_ini.py` — reads `object.ini`, emits structured JSON with:
  - All rooms: ID, display name, exit map (room → destination room ID),
    list of objects in room, background asset reference(s)
  - All objects: ID, room, graphic asset reference(s), sound asset
    reference(s), cursor behavior
  - All cursor definitions: ID, animation asset reference(s)
  - All inventory items: ID, graphic reference(s)
- `tools/parse_eng.py` — reads `Scooby.eng`, emits `{message_id: text}` JSON
- Cross-reference: match message IDs appearing in `object.ini` to their
  text strings from `Scooby.eng`
- **Cross-reference: match `object.ini` ROOM/OBJ/ANIM references against
  the `TGIFILE.ART` name table** (per [WP-003 §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table)).
  The extracted name table is preserved at `tools/samples/wp003-name-table.txt`
  (gitignored, regenerable from the SHA-256-locked source binary). The check
  is: every asset name in `object.ini` should appear in the WP-003 name
  table; any name in one but not the other is a finding worth recording.
- `tools/samples/asset-catalog.json` — combined output

### Output schema (v1)

The catalog JSON is a stable contract for downstream tools (WP-002
probe labeling, WP-003 name-table cross-check). Top-level shape:

```json
{
  "rooms":     { "<room_id>":   { ... } },
  "objects":   { "<object_id>": { ... } },
  "cursors":   { "<cursor_id>": { ... } },
  "inventory": { "<item_id>":   { ... } }
}
```

Room entry:

```json
{
  "id": "<string|int>",
  "name": "<string|null>",
  "background_assets": ["<asset_ref>"],
  "objects": ["<object_id>"],
  "exits": { "<direction_or_trigger>": "<room_id>" }
}
```

Object entry:

```json
{
  "id": "<string|int>",
  "room": "<room_id>",
  "graphics": ["<asset_ref>"],
  "sounds": ["<asset_ref>"],
  "cursor": "<cursor_id|null>"
}
```

`<asset_ref>` is whichever literal form `object.ini` uses (string name
or numeric index — locked in EC-004 Step 1). Unknown keys inside a known
section type are preserved under `extra_fields` rather than dropped.

### Failure handling

Parser policy (no silent drift):
- Unknown section type → log warning, continue (record under
  `unknown_sections` in output for the findings note).
- Unknown key inside a known section → preserve under `extra_fields`.
- Unparseable line inside a known section → **hard error, fail fast**
  (do not skip; the file is small enough that ambiguity must be resolved,
  not papered over).
- Duplicate IDs within a section → **hard error**.
- Malformed JSON output → **hard error** (validated via
  `python -m json.tool` per EC-004 Step 5).

Out of scope:
- Mapping logical asset names to `TGIFILE.ART` entry indices (that mapping
  comes from WP-001/WP-002 once the exe's lookup mechanism is known)
- Parsing `object.ini` for puzzle state-machine logic (Phase 4)
- Case File XML config parsing (different format, Phase 3)

## Dependencies

- `object.ini` and `Scooby.eng` from the mounted Showdown ISO (or at
  `tools/` — they're small, plain-text files worth copying once)
- Python 3.x stdlib only — no pip install required for INI parsing

## Exit criteria

1. `tools/parse_ini.py` runs on Showdown's `object.ini` without errors.
2. `tools/samples/asset-catalog.json` exists with room, object, cursor,
   and inventory entries capturing all asset name references.
3. The catalog captures every asset name string present in `object.ini`
   (e.g. if `object.ini` uses `bg=ghost_mine_entrance`, that string
   appears in the JSON).
4. `Scooby.eng` string table is parsed and cross-referenced: each message
   ID appearing in `object.ini` resolves to its display text.
5. A brief findings note added to `docs/formats/scooby-exe.md` → Findings
   → "`object.ini` interpreter behavior" subsection, answering:
   - Confirmed section structure (room/object/cursor/inventory divisions)
   - Asset reference format: string name? numeric index? something else?
   - Room count and object count
   - How much logic appears to be data-driven vs. implicit
6. **Name-table cross-check report.** Records, as concrete numbers:
   - Total asset references found in `object.ini`: __
   - Matches against the WP-003 name table: __ (and as %)
   - Unmatched references exported to
     `tools/samples/unmatched-assets.txt` (gitignored).
   A high match rate confirms the engine is name-driven against
   `TGIFILE.ART`; a low match rate is itself the finding and feeds
   back into WP-001's scope.

## Deliverables

- [`tools/parse_ini.py`](../../tools/parse_ini.py) — `object.ini` parser
- [`tools/parse_eng.py`](../../tools/parse_eng.py) — `Scooby.eng` parser
- [`tools/samples/asset-catalog.json`](../../tools/samples/asset-catalog.json) — combined output
- Findings note in [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) → "`object.ini` interpreter behavior"

## Notes

- **Asset reference format is the key finding.** Three outcomes, each with different implications:
  - String names (e.g. `bg=ghost_mine`): the catalog directly labels decoded TGIFILE.ART entries.
    WP-002's `probe_art.py` can output `entry_047_ghost_mine.png` rather than `entry_047.png`.
  - Numeric IDs (e.g. `bg=47`): if they map directly to TGIFILE.ART indices, this WP
    trivially answers "what should entry N look like?" with no further RE.
  - Indirect / encoded references: record the encoding scheme as a new unknown for WP-001.
- Even partial results are useful — if only room exits and object locations are readable
  but asset references are opaque, you've still confirmed the "data-driven interpreter"
  hypothesis and narrowed what Ghidra needs to explain.
- Stretch: run the same parsers on Phantom's `object.ini` (if extracted). Section
  structure match → cross-title asset-catalog format compatibility confirmed before
  any binary analysis.
- **Deterministic asset-naming rule for WP-002 hand-off.** If `object.ini`'s
  references match the WP-003 name table 1:1, decoded `TGIFILE.ART` entries
  should be written as `entry_<index>_<sanitized_name>.png` (e.g.
  `entry_000_DAPHNE_A.png`). Sanitization: uppercase preserved verbatim;
  any character outside `[A-Za-z0-9_]` replaced with `_`. Locking the rule
  here prevents a naming debate in WP-002 and keeps probe outputs
  diff-friendly across iterations.
