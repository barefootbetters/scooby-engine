---
layout: default
title: "Work Index — Scooby-Doo ScummVM Engine"
---

# scooby — Work Index

> Master ordered ledger of work packets (WPs) and execution checklists (ECs).
> Each WP is one unit of work with a goal, dependencies, and exit criteria.
> ECs are step-by-step checklists for the WPs most likely to sprawl.
>
> **Last updated:** 2026-06
>
> **Status vocabulary (closed set):**
> ✅ Done · 🚧 In Progress · 📝 Drafted (WP file authored, not yet started) · 📦 Queued (deps met, WP file not yet authored) · ⏸ Blocked (dep unmet) · 🔮 Placeholder (forward-looking, intentionally not authored)

---

## Current state

**Current phase:** Phase 0 → Phase 1 — Pre-Work then Format Research
**Primary blocker:** WP-002 (TGIFILE.ART payload decode). Phase 2 cannot start until at least one TGIFILE.ART entry is extracted to a recognizable image.
**Next unblocked:** Phase 0 pre-work. WP-007 ✅ landed 2026-06-02; WP-003 ✅ landed 2026-06-02; **WP-008 ✅ landed 2026-06-03** (object.ini interpreter behavior characterized; engine is name-driven, MODE_A). Remaining order: WP-009 → WP-010 → WP-001 → WP-002. The WP-003 baseline (pre-payload region characterized as the engine name table; no palette present; off-by-4 header-offset correction landed) is now available to WP-001 (palette-hunt scope drops from EC-001; the OBJ→asset-entry 1:1 mapping cuts asset-resolution scope) and to WP-002 (first-decode strategy: palette is NOT in the pre-payload region — it is either per-asset leading bytes or per-record metadata; investigate both). The WP-008 baseline (engine name-driven, 215 OBJ_* sections discriminated by `ID=`, deterministic naming rule confirmed) gives WP-002's `probe_art.py` a direct labeling path (`entry_<index>_<wp003_name>.png`) and gives WP-009 a canonical room-ID list to use for screenshot naming.

### Phase 1 findings landed (2026-06)

- **Engine generations identified.** Cross-title Rich Header + archive-format inspection (Showdown / Phantom / Jinx / Case File #1) reveals **one engine lineage spanning three format generations** — Gen 1 (Showdown, Phantom), Gen 2 (Jinx), Gen 3 (Case File #1). See [Engine Lineage in vision](../01-VISION.md#engine-lineage-2026-06-finding) and [scooby-exe.md cross-title comparison](../formats/scooby-exe.md#cross-title-toolchain-comparison-engine-generations).
- **Code-level inheritance from TerraGlyph to ImageBuilder Software confirmed.** Case File #1's binary embeds Jinx-era compiled object files directly (identical MSVC 5.0 build 8034 + Linker 5.10 build 8168 entries between Jinx and Case File #1). Documented in [scooby-exe](../formats/scooby-exe.md).
- **`MMFW` archive container documented.** New Gen 2/3 format spec at [mmfw-container](../formats/mmfw-container.md). Replaces `TGIFILE.ART` starting with Jinx (Oct 2001).
- **Scope rule revised.** Phase 5 scope tightened to ordered tiers: Minimum (Showdown), Extended-high-confidence (+ Phantom), Extended-medium-confidence (+ Jinx, requires Gen 2 parser), Stretch (+ Case Files, requires Gen 3 adapters).
- **WP-007 baseline landed (2026-06-02).** [`Scooby.exe` strings + import-table baseline](../formats/scooby-exe.md#binary-identity-wp-007-baseline) across all four cached binaries — Showdown (Gen 1), Phantom (Gen 1), Jinx (Gen 2), Case File #1 (Gen 3). Load-bearing corrections to the [cross-title runtime-dependencies table](../formats/scooby-exe.md#cross-title-runtime-dependencies): Jinx and Case File #1 do NOT statically import Bink/Smacker/QuickTime — Gen 2 uses MSVFW32 DrawDib for AVI playback, Gen 3 uses `ole32`/`libexpat` (COM filter-graph + XML config). Gen 2/3 also dropped registry usage (`ADVAPI32.dll` not imported) and load DirectSound dynamically. Phantom's import table is byte-identical to Showdown's. Source-tree path strings reveal `C:\Scooby\GBH\` (Showdown), `C:\Scooby\FBF\` (Phantom), `C:\Projects\SCOOBY\mummy\Mmfw\` (Jinx), `F:\Scooby\Museum\framework\` (Case File #1) — same `MMVisualCursor.cpp` filename in Jinx + Case File #1 is direct source-level inheritance evidence on top of the earlier Rich-Header `MSVC 5.0 build 8034` match.
- **WP-008 object.ini interpreter behavior characterized (2026-06-03).** [`object.ini` is a flat list of 215 `[OBJ_*]` sections](../formats/scooby-exe.md#objectini-interpreter-behavior) discriminated by an `ID=` field (5 values: `exitobject`, `clickableobject`, `inventoryobject`, `requiresobject`, `simpleobject`). No top-level rooms/cursors/inventory sections — those buckets are synthesized from cross-references (37 rooms, 23 cursors, 11 inventory). Asset-reference format: **MODE_A — direct WP-003 name-table strings** (`ROOM_*`/`OBJ_*`/`ANIM_*`); zero numeric indices. WP-003 cross-check: **221 / 286 match (77.27 %)** — the 65 unmatched are scripted/engine rooms with no pre-rendered backgrounds, invisible hotspot OBJs, and inventory-specific cursor/toolbar animations that live in other name-keyed stores. `Scooby.eng` is a 10-message system-error string table for `Scooby.exe`'s boot path; no `object.ini` field references it. Two source-binary SHAs (`object.ini`, `Scooby.eng`) propagated into [tools/exes/README §Showdown](../../tools/exes/README.md#showdown-gen-1); `Scooby.eng` SHA byte-identical to Phantom's. Parsers shipped under [`tools/parse_ini.py`](../../tools/parse_ini.py) + [`tools/parse_eng.py`](../../tools/parse_eng.py).
- **WP-003 pre-payload region characterized (2026-06-02).** [`TGIFILE.ART` pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table) is the **engine resource-name catalog** — 68-byte records (`4B uint32LE id + 44B zero-padded ASCII name + 20B metadata`) with type-tagged IDs (`0x10` = ROOM, `0x20` = OBJ, `0x3x` = ANIM). Continuous block at file `0x0F60`–`0xE6CC` has **811 records** (42 ROOM + 453 OBJ + 316 ANIM); the OBJ count exactly matches `asset_count` and OBJ IDs are contiguous 0–452, confirming `entry[i]` is the payload for `OBJ` id `i`. **Spec correction landed** — `asset_count` is at `0x0118` (not `0x011C`); the asset entry table is at `0x011C`–`0x0F43` (not `0x0120`–`0x0F47`); the pre-payload region begins at `0x0F44`. **Negative palette finding:** no 256-entry RGB / RGBA palette in the pre-payload region — palette discovery moves to WP-002 (per-asset leading bytes or per-record metadata). **Mixed tail region (`0xE6CC`–`0x10017E`, ≈ 990 KB):** further name records interleaved with F0-opcode packed data; schema deferred to WP-001 / WP-002. WP-007 strings cross-check: 100 % of ROOM names, 50.3 % of OBJ names, 20.6 % of ANIM names appear in `tools/exes/showdown/strings-ansi.txt` — corroborates the [scooby-exe interpreter hypothesis](../formats/scooby-exe.md#hypotheses-unverified) (most resource resolution is data-driven via name-table lookup, not hardcoded).

---

## Phase 0 — Pre-Work (run before WP-001)

These WPs require no Ghidra, no format decoding, and no binary analysis. They
build the ground-truth references that make Phase 1 debugging tractable, and
pin the ScummVM API target before implementation decisions are made. None block
each other; recommended execution order is left-to-right in the table.

| WP | Title | Status | Deps | EC | Notes |
|---|---|---|---|---|---|
| [WP-007](WP-007-strings-and-imports.md) | `Scooby.exe` strings dump + import table | ✅ Done (2026-06-02) | — | — | ~30 min actual (matched WP body's 20–40 min estimate, vs. the original 15–30 min Phase 0 placeholder). Findings landed in [scooby-exe](../formats/scooby-exe.md) §Binary identity / §String literals / §Import table; cross-title runtime-dependencies table now carries import-verdict cells (no remaining TBD/predicted). Primes EC-001 Steps 3–4. |
| [WP-003](WP-003-pre-payload-region.md) | Pre-payload region scan (palette hunt) | ✅ Done (2026-06-02) | WP-007 ✅ (recommended) | — | ~2 hrs actual (matched 1–2 hr estimate). Findings landed in [tgifile-art.md §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table). Region is the engine name table (811 clean records: 42 ROOM + 453 OBJ + 316 ANIM). Header offsets corrected by −4 (`asset_count` at `0x0118`). Negative palette finding — palette discovery moves to WP-002. Drops palette-hunt scope from EC-001. |
| [WP-008](WP-008-object-ini-catalog.md) | `object.ini` + `Scooby.eng` asset catalog | ✅ Done (2026-06-03) | — | [EC-004](../execution-checklists/EC-004-object-ini-catalog.md) | ~3 hrs actual (vs. half-day estimate). Findings landed in [scooby-exe.md §`object.ini` interpreter behavior](../formats/scooby-exe.md#objectini-interpreter-behavior). Engine is **name-driven** (MODE_A); 215 OBJ_* sections discriminated by `ID=`; 77.27 % cross-check vs WP-003 name table. Unblocks WP-009 naming + WP-002 first-decode labeling. |
| [WP-009](WP-009-reference-screenshots.md) | Reference screenshot library (*Showdown*) | 📦 Queued | WP-008 ✅ | — | 1–2 hrs; required by EC-002 pre-flight. **Canonical room-ID list now available** from the WP-008 catalog (`tools/samples/asset-catalog.json` → `rooms` map; 37 IDs in `ROOM_P{NN}_<Descriptive>` form). Use these IDs verbatim as screenshot filenames per the WP-008 sanitization rule. |
| [WP-010](WP-010-scummvm-scaffold.md) | ScummVM fork + empty `engines/scooby/` scaffold | 📦 Queued | — | [EC-005](../execution-checklists/EC-005-scummvm-scaffold.md) | Half-day; pins commit hash; defines debug channel names before Ghidra annotations |

---

## Phase 1 — Format Research

| WP | Title | Status | Deps | EC | Notes |
|---|---|---|---|---|---|
| [WP-001](WP-001-ghidra-session.md) | Ghidra session: `Scooby.exe` imports + `TGIFILE.ART` decode trace | 🚧 In Progress | WP-003 ✅, WP-007 ✅ (recommended) | [EC-001](../execution-checklists/EC-001-ghidra-session.md) | EC-001 Step 1 (PE Rich Header) ✅ done — toolchain identified across 4 titles. WP-007 baseline ✅ — Step 3 (Imports table review) is now a cross-check against [scooby-exe §Import table](../formats/scooby-exe.md#import-table-wp-007), not a re-extraction. WP-003 baseline ✅ — palette-hunt scope drops from the TGIFILE.ART decode trace; the OBJ→asset-entry 1:1 mapping cuts asset-resolution scope. Steps 2, 4, 5 (Ghidra load, file-I/O labeling, TGIFILE.ART decode trace) still pending. |
| [WP-002](WP-002-tgifile-art-decoder.md) | `TGIFILE.ART` payload decoder + first image extraction | 📝 Drafted | WP-001 (preferred, not strict) | [EC-002](../execution-checklists/EC-002-probe-art-harness.md) | Phase 1 exit criterion #1. WP-003 baseline ✅ — first-decode strategy: palette is NOT in the pre-payload region; investigate per-asset leading bytes and per-record metadata (offsets 48–67 of name-table records) as palette sources. The mixed tail region of the pre-payload (`0xE6CC`–`0x10017E`) also contains F0-opcode packed data and may co-locate per-asset palettes or pre-decoded frame data. **WP-008 baseline ✅** — engine is name-driven; `probe_art.py` can label decoded entries directly as `entry_<index>_<wp003_name>.png` (sanitization rule per [WP-008 §Notes](WP-008-object-ini-catalog.md#notes); a no-op on every observed name). The 65 unmatched references from the WP-008 cross-check are not expected to resolve to decoded entries — verifying that none of them do is part of EC-002's probe coverage. |
| [WP-003](WP-003-pre-payload-region.md) | Inspect the 1 MB region between asset entries and first payload (palette hunt) | ✅ Done (2026-06-02) | — | — | Also listed in Phase 0. Pre-payload region is the engine name table — see [tgifile-art.md §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table). Header offsets corrected by −4 bytes. No palette in this region (palette discovery → WP-002). |
| [WP-004](WP-004-audio-archive-decode.md) | Audio archive index + codec identification | 📝 Drafted | — | — | Phase 1 exit criterion #3 |
| [WP-005](WP-005-engine-family-check.md) | Engine-family check across Case File ISOs | 🚧 In Progress | — | [EC-003](../execution-checklists/EC-003-engine-family-check.md) | Case File #1 done — one engine lineage across three generations confirmed; code-level TerraGlyph→IBS inheritance confirmed. Case File #2 verification still owed. |
| [WP-006](WP-006-phantom-archive-format.md) | Phantom archive format verification (Gen 1 vs Gen 2) | 📝 Drafted | — | — | One-minute `Format-Hex` check; locks in Phantom's generation classification |

**Phase 1 exit gate:** see [Project Vision](../01-VISION.md) → "Phase 1 — Format Research" exit criteria. Summary: one `TGIFILE.ART` entry rendered to PNG/BMP, structure documented in `docs/formats/`, audio codec named, engine-family question answered.

---

## Phase 2 — ScummVM Engine Scaffold (placeholder)

Authored after Phase 1 exit. Tracked here to maintain phase ordering only.

| Provisional scope | Anchored to |
|---|---|
| Fork `scummvm/scummvm`; pin commit hash in `02-SCUMMVM-INTEGRATION.md` | **Moved to WP-010 (Phase 0)** |
| Create `engines/scooby/` skeleton with `module.mk`, `configure.engine`; debug channel stubs | **Moved to WP-010 (Phase 0)** |
| `MetaEngineDetection` + `MetaEngine` subclasses; engine class with empty `run()` | [`02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION.md) §1, §2 |
| `ADGameDescription` table populated from Phase 1 findings, **carrying a per-entry generation flag** (Gen 1/2/3) per the engine lineage finding | §3 |
| `POTFILES` (after translatable strings exist) | §10 |

---

## Phase 3 — Resource Loading (placeholder)

| Provisional scope |
|---|
| `TGIFILE.ART` parser as `Common::Archive` subclass (Gen 1) |
| `MMFW` container parser as `Common::Archive` subclass (Gen 2 / Gen 3) |
| Audio loader through `Audio::Mixer` |
| `Scooby.eng` parser (Gen 1 / Gen 2) |
| `object.ini` parser into engine structs (Gen 1 / Gen 2) |
| XML config parser (Gen 3) — likely wraps ScummVM's bundled libxml or a small in-engine parser |

---

## Phase 4 — Game Logic (placeholder)

| Provisional scope |
|---|
| Room/scene management and transitions |
| Cursor system and object interaction |
| Inventory |
| Bink video playback via ScummVM's decoder |
| Puzzle state machine — data-driven first, Ghidra-assisted where data falls short |

---

## Phase 5 — Polish & Contribution (placeholder)

| Provisional scope |
|---|
| Test in-scope titles per Phase 5 scope rule in vision |
| Save/load if engine supports it |
| ScummVM wiki page |
| PR to `scummvm/scummvm` targeting `ADGF_TESTING` |
| All twelve acceptance gates from `02-SCUMMVM-INTEGRATION.md` pass |

---

## Reference Screenshots — *Showdown in Ghost Town* (WP-009)

One screenshot per distinct room, captured from a YouTube longplay. Used as visual ground truth for WP-002's decoder (EC-002 pre-flight). Stored at [`docs/assets/screenshots/showdown-screens/`](../assets/screenshots/showdown-screens/README.md) — tracked in git, served by GitHub Pages.

Screenshots populate here once WP-009 runs. Embed syntax for adding a row:

```markdown
| ![Room name](../assets/screenshots/showdown-screens/room-slug.png) | Room name | `room-slug` |
```

| Screenshot | Room | ID |
|---|---|---|
| *(WP-009 not yet run)* | | |

---

## References

- Vision and phase plan: [docs/01-VISION](../01-VISION.md)
- ScummVM integration contract: [docs/02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md)
- WP lifecycle: [docs/reference/wp-lifecycle](../reference/wp-lifecycle.md)
- Pre-flight gate: [docs/reference/pre-flight](../reference/pre-flight.md)
- Format specs: [docs/formats/tgifile-art](../formats/tgifile-art.md), [audio-archives](../formats/audio-archives.md), [scooby-exe](../formats/scooby-exe.md), [mmfw-container](../formats/mmfw-container.md)
- Phase 0 WPs: [WP-007](WP-007-strings-and-imports.md), [WP-008](WP-008-object-ini-catalog.md), [WP-009](WP-009-reference-screenshots.md), [WP-010](WP-010-scummvm-scaffold.md)

---

*Promote Phase 2-5 entries to authored WPs as Phase 1 closes — not before. Premature WP authoring is its own form of churn.*
