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

**Current phase:** Phase 1 — Format Research
**Primary blocker:** WP-002 (TGIFILE.ART payload decode). Phase 2 cannot start until at least one TGIFILE.ART entry is extracted to a recognizable image.
**Next unblocked:** WP-001 Ghidra deep-dive (Step 1 PE Rich Header complete; full Ghidra trace still pending).

### Phase 1 findings landed (2026-06)

- **Engine generations identified.** Cross-title Rich Header + archive-format inspection (Showdown / Phantom / Jinx / Case File #1) reveals **one engine lineage spanning three format generations** — Gen 1 (Showdown, Phantom), Gen 2 (Jinx), Gen 3 (Case File #1). See [Engine Lineage in vision](../01-VISION#engine-lineage-2026-06-finding) and [scooby-exe.md cross-title comparison](../formats/scooby-exe#cross-title-toolchain-comparison-engine-generations).
- **Code-level inheritance from TerraGlyph to ImageBuilder Software confirmed.** Case File #1's binary embeds Jinx-era compiled object files directly (identical MSVC 5.0 build 8034 + Linker 5.10 build 8168 entries between Jinx and Case File #1). Documented in [scooby-exe](../formats/scooby-exe).
- **`MMFW` archive container documented.** New Gen 2/3 format spec at [mmfw-container](../formats/mmfw-container). Replaces `TGIFILE.ART` starting with Jinx (Oct 2001).
- **Scope rule revised.** Phase 5 scope tightened to ordered tiers: Minimum (Showdown), Extended-high-confidence (+ Phantom), Extended-medium-confidence (+ Jinx, requires Gen 2 parser), Stretch (+ Case Files, requires Gen 3 adapters).

---

## Phase 1 — Format Research

| WP | Title | Status | Deps | EC | Notes |
|---|---|---|---|---|---|
| [WP-001](WP-001-ghidra-session) | Ghidra session: `Scooby.exe` imports + `TGIFILE.ART` decode trace | 🚧 In Progress | — | [EC-001](../execution-checklists/EC-001-ghidra-session) | EC-001 Step 1 (PE Rich Header) ✅ done — toolchain identified across 4 titles. Steps 2–5 (Ghidra load, imports, file-I/O labeling, TGIFILE.ART decode trace) still pending. |
| [WP-002](WP-002-tgifile-art-decoder) | `TGIFILE.ART` payload decoder + first image extraction | 📝 Drafted | WP-001 (preferred, not strict) | [EC-002](../execution-checklists/EC-002-probe-art-harness) | Phase 1 exit criterion #1 |
| [WP-003](WP-003-pre-payload-region) | Inspect the 1 MB region between asset entries and first payload (palette hunt) | 📝 Drafted | — | — | Half-day; may dramatically shortcut WP-002 if it contains palette data |
| [WP-004](WP-004-audio-archive-decode) | Audio archive index + codec identification | 📝 Drafted | — | — | Phase 1 exit criterion #3 |
| [WP-005](WP-005-engine-family-check) | Engine-family check across Case File ISOs | 🚧 In Progress | — | [EC-003](../execution-checklists/EC-003-engine-family-check) | Case File #1 done — one engine lineage across three generations confirmed; code-level TerraGlyph→IBS inheritance confirmed. Case File #2 verification still owed. |
| [WP-006](WP-006-phantom-archive-format) | Phantom archive format verification (Gen 1 vs Gen 2) | 📝 Drafted | — | — | One-minute `Format-Hex` check; locks in Phantom's generation classification |

**Phase 1 exit gate:** see [Project Vision](../01-VISION) → "Phase 1 — Format Research" exit criteria. Summary: one `TGIFILE.ART` entry rendered to PNG/BMP, structure documented in `docs/formats/`, audio codec named, engine-family question answered.

---

## Phase 2 — ScummVM Engine Scaffold (placeholder)

Authored after Phase 1 exit. Tracked here to maintain phase ordering only.

| Provisional scope | Anchored to |
|---|---|
| Fork `scummvm/scummvm`; pin commit hash in `02-SCUMMVM-INTEGRATION.md` | [`02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION) §1, §11 |
| Create `engines/scooby/` skeleton with `module.mk`, `configure.engine`, `POTFILES` | §10 |
| `MetaEngineDetection` + `MetaEngine` subclasses; engine class with empty `run()` | §1, §2 |
| `ADGameDescription` table populated from Phase 1 findings, **carrying a per-entry generation flag** (Gen 1/2/3) per the engine lineage finding | §3 |
| Debug channels registered | §9 |

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

## References

- Vision and phase plan: [docs/01-VISION](../01-VISION)
- ScummVM integration contract: [docs/02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION)
- Format specs: [docs/formats/tgifile-art](../formats/tgifile-art), [audio-archives](../formats/audio-archives), [scooby-exe](../formats/scooby-exe), [mmfw-container](../formats/mmfw-container)

---

*Promote Phase 2-5 entries to authored WPs as Phase 1 closes — not before. Premature WP authoring is its own form of churn.*
