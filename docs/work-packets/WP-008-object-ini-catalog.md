---
layout: default
title: "WP-008: object.ini Asset Catalog"
---

# WP-008: `object.ini` + `Scooby.eng` logical asset catalog

**Status:** 📦 Queued
**Phase:** Pre-Work (before WP-002)
**Depends on:** —
**Companion EC:** [EC-004](../execution-checklists/EC-004-object-ini-catalog)
**Estimated effort:** Half-day

---

## Goal

Parse `object.ini` (1,405 lines, plain INI) and `Scooby.eng` (localized
string table) into machine-readable JSON structures, producing a logical
asset catalog that maps room IDs → objects → asset references. This
becomes the ground-truth reference for decoder verification: when
`probe_art.py` decodes TGIFILE.ART entry N, you can look up what that
entry is supposed to represent.

## Background

Without a logical asset map, Phase 1 exit criterion #1 — "visually matches
in-game output" — is an honor-system claim. With one, it becomes a testable
assertion: "Entry 47 is the asset referenced by `[Library]`'s background
field; the decoded image should show the library entrance."

Both source files are **human-readable, available today, with zero RE
dependency**. This is pure data engineering. The earlier it runs, the more
useful WP-002 and WP-003 outputs become.

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
- `tools/samples/asset-catalog.json` — combined output

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

## Deliverables

- [`tools/parse_ini.py`](../../tools/parse_ini.py) — `object.ini` parser
- [`tools/parse_eng.py`](../../tools/parse_eng.py) — `Scooby.eng` parser
- [`tools/samples/asset-catalog.json`](../../tools/samples/asset-catalog.json) — combined output
- Findings note in [`docs/formats/scooby-exe.md`](../formats/scooby-exe) → "`object.ini` interpreter behavior"

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
