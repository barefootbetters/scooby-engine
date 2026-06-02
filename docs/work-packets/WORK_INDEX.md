# scooby — Work Index

> Master ordered ledger of work packets (WPs) and execution checklists (ECs).
> Each WP is one unit of work with a goal, dependencies, and exit criteria.
> ECs are step-by-step checklists for the WPs most likely to sprawl.
>
> **Last updated:** 2026-06
>
> **Status vocabulary (closed set):**
> ✅ Done · 🚧 In Progress · 📝 Drafted (WP file authored, not yet started) · 📦 Queued (deps met, WP file not yet authored) · ⏸ Blocked (dep unmet) · 📝 Placeholder (forward-looking, intentionally not authored)

---

## Current state

**Current phase:** Phase 1 — Format Research
**Primary blocker:** WP-002 (TGIFILE.ART payload decode). Phase 2 cannot start until at least one TGIFILE.ART entry is extracted to a recognizable image.
**Next unblocked:** WP-001 (Ghidra session) → unlocks WP-002 with the decode algorithm directly. WP-003 / WP-004 / WP-005 are parallel-safe with WP-001 and can run any time.

---

## Phase 1 — Format Research

| WP | Title | Status | Deps | EC | Notes |
|---|---|---|---|---|---|
| [WP-001](WP-001-ghidra-session.md) | Ghidra session: `Scooby.exe` imports + `TGIFILE.ART` decode trace | 📝 Drafted | — | [EC-001](../execution-checklists/EC-001-ghidra-session.md) | Highest-leverage Phase 1 move; gives decode algorithm directly |
| [WP-002](WP-002-tgifile-art-decoder.md) | `TGIFILE.ART` payload decoder + first image extraction | 📝 Drafted | WP-001 (preferred, not strict) | [EC-002](../execution-checklists/EC-002-probe-art-harness.md) | Phase 1 exit criterion #1 |
| [WP-003](WP-003-pre-payload-region.md) | Inspect the 1 MB region between asset entries and first payload (palette hunt) | 📝 Drafted | — | — | Half-day; may dramatically shortcut WP-002 if it contains palette data |
| [WP-004](WP-004-audio-archive-decode.md) | Audio archive index + codec identification | 📝 Drafted | — | — | Phase 1 exit criterion #3 |
| [WP-005](WP-005-engine-family-check.md) | Engine-family check across Case File ISOs | 📝 Drafted | — | [EC-003](../execution-checklists/EC-003-engine-family-check.md) | Answers Phase 1 exit criterion #4; scope-defining |

**Phase 1 exit gate:** see [`docs/01-VISION.md`](../01-VISION.md) → "Phase 1 — Format Research" exit criteria. Summary: one `TGIFILE.ART` entry rendered to PNG/BMP, structure documented in `docs/formats/`, audio codec named, engine-family question answered.

---

## Phase 2 — ScummVM Engine Scaffold (placeholder)

Authored after Phase 1 exit. Tracked here to maintain phase ordering only.

| Provisional scope | Anchored to |
|---|---|
| Fork `scummvm/scummvm` into `C:\www\scummvm\`; pin commit hash in `02-SCUMMVM-INTEGRATION.md` | [`02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION.md) §1, §11 |
| Create `engines/scooby/` skeleton with `module.mk`, `configure.engine`, `POTFILES` | §10 |
| `MetaEngineDetection` + `MetaEngine` subclasses; engine class with empty `run()` | §1, §2 |
| `ADGameDescription` table populated from Phase 1 findings (MD5/sizes from `tgifile-art.md`) | §3 |
| Debug channels registered | §9 |

---

## Phase 3 — Resource Loading (placeholder)

| Provisional scope |
|---|
| `TGIFILE.ART` parser as `Common::Archive` subclass |
| Audio loader through `Audio::Mixer` |
| `Scooby.eng` parser |
| `object.ini` parser into engine structs |

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

- Vision and phase plan: [`docs/01-VISION.md`](../01-VISION.md)
- ScummVM integration contract: [`docs/02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION.md)
- Format specs: [`docs/formats/`](../formats/)

---

*Promote Phase 2-5 entries to authored WPs as Phase 1 closes — not before. Premature WP authoring is its own form of churn.*
