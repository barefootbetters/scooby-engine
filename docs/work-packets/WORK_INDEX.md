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
**Next unblocked:** Phase 0 pre-work. Execute in order: WP-007 (15 min) → WP-003 → WP-008 + WP-009 → WP-010 → WP-001. All four Phase 0 WPs are newly added — see Phase 0 section below.

### Phase 1 findings landed (2026-06)

- **Engine generations identified.** Cross-title Rich Header + archive-format inspection (Showdown / Phantom / Jinx / Case File #1) reveals **one engine lineage spanning three format generations** — Gen 1 (Showdown, Phantom), Gen 2 (Jinx), Gen 3 (Case File #1). See [Engine Lineage in vision](../01-VISION.md#engine-lineage-2026-06-finding) and [scooby-exe.md cross-title comparison](../formats/scooby-exe.md#cross-title-toolchain-comparison-engine-generations).
- **Code-level inheritance from TerraGlyph to ImageBuilder Software confirmed.** Case File #1's binary embeds Jinx-era compiled object files directly (identical MSVC 5.0 build 8034 + Linker 5.10 build 8168 entries between Jinx and Case File #1). Documented in [scooby-exe](../formats/scooby-exe.md).
- **`MMFW` archive container documented.** New Gen 2/3 format spec at [mmfw-container](../formats/mmfw-container.md). Replaces `TGIFILE.ART` starting with Jinx (Oct 2001).
- **Scope rule revised.** Phase 5 scope tightened to ordered tiers: Minimum (Showdown), Extended-high-confidence (+ Phantom), Extended-medium-confidence (+ Jinx, requires Gen 2 parser), Stretch (+ Case Files, requires Gen 3 adapters).

---

## Phase 0 — Pre-Work (run before WP-001)

These WPs require no Ghidra, no format decoding, and no binary analysis. They
build the ground-truth references that make Phase 1 debugging tractable, and
pin the ScummVM API target before implementation decisions are made. None block
each other; recommended execution order is left-to-right in the table.

| WP | Title | Status | Deps | EC | Notes |
|---|---|---|---|---|---|
| [WP-007](WP-007-strings-and-imports.md) | `Scooby.exe` strings dump + import table | 📦 Queued | — | — | 15–30 min; primes EC-001 Steps 3–4; run first |
| [WP-003](WP-003-pre-payload-region.md) | Pre-payload region scan (palette hunt) | 📝 Drafted | WP-007 (recommended) | — | **Run before WP-001** — may drop the palette-hunt scope from the Ghidra session entirely |
| [WP-008](WP-008-object-ini-catalog.md) | `object.ini` + `Scooby.eng` asset catalog | 📦 Queued | — | [EC-004](../execution-checklists/EC-004-object-ini-catalog.md) | Half-day; grounds "visually matches" decoder verification |
| [WP-009](WP-009-reference-screenshots.md) | Reference screenshot library (*Showdown*) | 📦 Queued | WP-008 (for naming) | — | 1–2 hrs; required by EC-002 pre-flight |
| [WP-010](WP-010-scummvm-scaffold.md) | ScummVM fork + empty `engines/scooby/` scaffold | 📦 Queued | — | [EC-005](../execution-checklists/EC-005-scummvm-scaffold.md) | Half-day; pins commit hash; defines debug channel names before Ghidra annotations |

---

## Phase 1 — Format Research

| WP | Title | Status | Deps | EC | Notes |
|---|---|---|---|---|---|
| [WP-001](WP-001-ghidra-session.md) | Ghidra session: `Scooby.exe` imports + `TGIFILE.ART` decode trace | 🚧 In Progress | WP-003, WP-007 (recommended) | [EC-001](../execution-checklists/EC-001-ghidra-session.md) | EC-001 Step 1 (PE Rich Header) ✅ done — toolchain identified across 4 titles. Steps 2–5 (Ghidra load, imports, file-I/O labeling, TGIFILE.ART decode trace) still pending. |
| [WP-002](WP-002-tgifile-art-decoder.md) | `TGIFILE.ART` payload decoder + first image extraction | 📝 Drafted | WP-001 (preferred, not strict) | [EC-002](../execution-checklists/EC-002-probe-art-harness.md) | Phase 1 exit criterion #1 |
| [WP-003](WP-003-pre-payload-region.md) | Inspect the 1 MB region between asset entries and first payload (palette hunt) | 📝 Drafted | — | — | Also listed in Phase 0 — **run before WP-001**, not in parallel; may dramatically shortcut WP-002 |
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
