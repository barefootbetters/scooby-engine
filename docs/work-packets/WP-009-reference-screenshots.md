---
layout: default
title: "WP-009: Reference Screenshot Library"
---

# WP-009: Reference screenshot library (*Showdown in Ghost Town*)

**Status:** 📦 Queued
**Phase:** Pre-Work (before WP-002)
**Depends on:** WP-008 ✅ (room IDs available — see §Notes)
**Companion EC:** — (no EC; inline operator checklist in §Execution)
**Estimated effort:** 1–2 hours

---

## Goal

Capture exactly one **clean, stationary frame** per distinct room/scene
in *Showdown in Ghost Town* from a YouTube longplay, store them as
`docs/assets/screenshots/showdown-screens/<room-id>.png` (git-tracked,
served by GitHub Pages — see §Notes for why `docs/assets/` and not
`tools/samples/`), and render them as a gallery page on the Pages site
at `https://github.barefootbetters.com/scooby-engine/docs/assets/screenshots/showdown-screens/`.
This `index.md` IS the canonical gallery page served by GitHub Pages
and is the primary deliverable of this WP.

These become the visual ground truth for WP-002's decoder: when
`probe_art.py` produces an image, the comparison target is a named file,
not a memory of what the game looked like.

**Capture rules (binary):**

- No transitions (fade, pan, cut) — wait for the room to fully render
  and the camera to settle.
- No motion blur or animation mid-frame — pause the longplay on a still
  beat.
- Player character allowed in frame but not blocking major background
  geometry; prefer frames where Scooby/Shaggy are off-center or absent.
- UI minimized where possible; if unavoidable, must not obscure key
  background geometry (no dialogue box across the wall, no full-width
  inventory bar over the floor).

## Background

EC-002 pre-flight already requires a reference screenshot to be in place
before running decode strategies. This WP creates that asset once,
properly named and provenance-logged, so it's reusable across WP-002 and
any future decoder debugging session.

Without this library, "does this look right?" requires searching a longplay
in real time. With it, it's a 10-second side-by-side against a known-good
file. For a decoder that may go through 5–6 strategy iterations (EC-002
Phases B1–B6), the savings compound.

## Scope

In scope:
- Locate a *Showdown in Ghost Town* YouTube longplay (search "Scooby-Doo
  Showdown in Ghost Town full game longplay" — several exist)
- Capture one clean stationary frame per visually distinct room per the
  §Goal capture rules
- File naming is **strictly canonical-first**:
  - MUST match a `destinationroom=` ID from the WP-008 asset catalog
    when the captured room corresponds to one (verbatim, e.g.
    `ROOM_P21_Boot_Hill1.png`). Source of truth: `tools/samples/asset-catalog.json`
    `rooms` map (gitignored — regenerate per WP-008 §Notes if missing).
  - If no match can be confidently made, name the file
    `UNMATCHED_<descriptive-slug>.png` and log the reason in the
    provenance table (e.g. `UNMATCHED_intro-cutscene-frame.png`).
  - No silent guessing, no approximate matches, no half-canonical
    filenames. Every file is either canonical or `UNMATCHED_`-prefixed.
- Store in `docs/assets/screenshots/showdown-screens/` (git-tracked,
  served by Pages — see §Notes for why not `tools/samples/`)
- Produce `docs/assets/screenshots/showdown-screens/index.md` — renamed
  from the existing `README.md` placeholder — as the gallery page:
  embeds each image at constrained display width with the provenance
  schema in §Deliverables. This `index.md` IS the canonical gallery
  page served by GitHub Pages and is the primary deliverable of this WP.
- Add **one or two** representative thumbnail teasers to the WORK_INDEX
  "Reference Screenshots" section, each linking to the gallery page.
  Do NOT inline the full 16+ image set in WORK_INDEX (it would bloat
  the master ledger; previous WORK_INDEX-rendering passes have already
  pulled large galleries out of that file).

**Screenshot quality requirements:**

- Minimum source quality: 720p (YouTube 720p PNG export is the floor).
- No compression artifacts that obscure shapes or colors — if the
  longplay's source quality is borderline, find a higher-quality
  longplay rather than capturing the artifact.
- Frame must be sharp (not mid-motion).
- Cropping is allowed ONLY to remove black borders / letterboxing —
  do not crop scene content (a cropped scene-content frame compromises
  decoder visual comparison).

Out of scope:
- Every animation frame, sprite pose, or inventory icon (Phase 4)
- UI-only screenshots (inventory screen, options screen)
- Cutscene frames — Bink decoder is handled separately
- Phantom, Jinx, or Case File screenshots (separate WPs if needed)

## Dependencies

- Internet access + YouTube
- Screenshot tool: Windows Snipping Tool, Greenshot, or OBS frame export
- WP-008 asset catalog (for room naming; not required to start)

## Exit criteria

1. **Coverage achieved.**
   - ≥ 16 TGIFILE.ART-backed rooms captured (the rooms in the WP-008
     catalog that have backing `entry[i]` payloads — primary WP-002
     decoder targets).
   - Attempt made to capture all 37 `destinationroom=` IDs present in
     the longplay (the additional 21 are scripted/code-rendered rooms;
     they're the visual ground truth for WP-001 Ghidra traces and Phase
     3 `*_Room.cpp` reimplementation).
   - Any of the 37 canonical IDs NOT captured MUST be listed in the
     provenance table with one of these explicit reasons:
     - `Not reached in longplay`
     - `Not observable in source video` (UI overlay, scene too brief,
       always behind transition)
     - `Uncertain match` (something visually similar appeared but
       couldn't be canonicalized — see `UNMATCHED_` fallback)
   - Partial coverage is acceptable ONLY if all gaps are explicitly
     logged in the provenance table.

2. **Naming compliance (binary).**
   - Every committed file is either:
     - A WP-008 canonical room ID verbatim (e.g.
       `ROOM_P21_Boot_Hill1.png`, `ROOM_P12_Saloon.png`), OR
     - Prefixed `UNMATCHED_<descriptive-slug>.png` with a `Match Status:
       Unmatched` row in the provenance table and a justification in
       the Notes column.
   - No silent slugs, no near-canonical names (`ROOM_P21_BootHill.png`
     when the catalog says `ROOM_P21_Boot_Hill1`), no half-matches.

3. **Gallery page rendered.**
   - `docs/assets/screenshots/showdown-screens/index.md` (renamed from
     `README.md` so the URL resolves cleanly) renders on the Pages site,
     using the provenance schema in §Deliverables — every row shows an
     embedded preview alongside Room ID / Source Video / Timestamp /
     Match Status / Notes.
   - This `index.md` IS the canonical gallery page; it is the primary
     deliverable of this WP, not a side artifact.

4. **Decoder-target validation.**
   - At least one captured image is:
     - A full-room static background (not a sprite-only frame, not a
       partial view, not a transition).
     - Clear and unobstructed (per §Goal capture rules).
     - Suitable for direct visual comparison with decoded `TGIFILE.ART`
       output — this is the frame EC-002 pre-flight will pull when
       running decode strategies.
   - At least one `OBJ_DAPHNE_A` (or other character sprite) capture is
     present — `entry[0]` of `TGIFILE.ART` is `OBJ_DAPHNE_A`, so this
     is the WP-002 first-decode comparison target. See §Notes.

5. **WORK_INDEX teaser updated.**
   - WORK_INDEX "Reference Screenshots" section carries one or two
     representative thumbnail teasers, each linking to the gallery
     page. The full 16+ image set does NOT live inline in WORK_INDEX.

6. **Pages render verified.**
   - Gallery page is visible at
     `https://github.barefootbetters.com/scooby-engine/docs/assets/screenshots/showdown-screens/`
     and all embedded images load (no broken images in the live render).

## Deliverables

- `docs/assets/screenshots/showdown-screens/<room-id>.png` × ≥ 16
  (full-size PNGs, typically 1280×720 from YouTube 720p; commit these
  as-is — they're the canonical assets).
- `docs/assets/screenshots/showdown-screens/index.md` — gallery page +
  provenance log. Renamed from `README.md` (already pre-renamed in the
  WP-009 prep pass; git tracks the move).

**Provenance schema (mandatory).**

The `index.md` provenance table MUST include exactly these columns:

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|

Where:

- **Preview** — `<a href="<file>.png"><img src="<file>.png" width="320"></a>`
  (full-size PNG linked from the inline thumbnail; HTML width caps the
  *displayed* size only — the underlying PNG is still full resolution
  for decoder comparison).
- **Room ID** — canonical ID in backticks, e.g. `` `ROOM_P21_Boot_Hill1` ``.
  For unmatched captures, use the `UNMATCHED_<slug>` filename here.
- **Source Video** — link to the YouTube longplay. The same longplay
  URL is declared once at the top of the page; per-row entries can
  short-form as `[YT](url)` or omit if the global URL applies (the
  global URL is the default; per-row only when a second source was
  needed for a specific room).
- **Timestamp** — `mm:ss` or `hh:mm:ss` into the source video. Required
  for every captured row; reproducibility hinges on this column.
- **Match Status** — one of: `Canonical`, `Unmatched`, `Uncertain`.
  `Canonical` = filename is an exact WP-008 catalog ID. `Unmatched` =
  `UNMATCHED_`-prefixed filename. `Uncertain` = canonical filename but
  the capture-to-ID mapping has a caveat (e.g. picked closest visual
  match between two similar chase rooms).
- **Notes** — any ambiguity, capture limitation, or context the next
  reader needs (UI partially obscuring scene, two visually similar rooms
  hard to distinguish, etc.). For gap rows (canonical IDs not captured),
  use the explicit reason strings from Exit criterion #1.

Page-weight sanity check: full-size PNGs run ~1–2 MB each; 16+ images
unconstrained would push the page past 30 MB. The `width="320"` embed
keeps the rendered page light without compromising the underlying
asset.

## Execution

Inline operator checklist (no separate EC — this WP is one continuous
capture session, not a multi-step branched workflow). Run top-to-bottom
once; check each item as completed.

**Setup**

- [ ] Locate a *Showdown in Ghost Town* YouTube longplay at ≥ 720p
- [ ] Record the longplay URL, uploader, and date in the `index.md`
      single-source block at the top of the gallery
- [ ] Open `tools/samples/asset-catalog.json` (regenerate if missing
      per WP-008 §Notes) and keep the `rooms` map visible for ID lookup
- [ ] Open `docs/assets/screenshots/showdown-screens/index.md` for
      editing alongside the longplay

**Per-room capture loop** (repeat for each distinct room encountered)

- [ ] Pause the longplay on a clean stationary frame (per §Goal
      capture rules: no transitions, no motion blur, no UI obstructing
      geometry)
- [ ] Confirm the room matches a WP-008 canonical ID; if uncertain, use
      the `UNMATCHED_<slug>.png` fallback
- [ ] Capture full-size PNG (no scene-content cropping; black-border
      crop only)
- [ ] Save as `docs/assets/screenshots/showdown-screens/<canonical-or-UNMATCHED-name>.png`
- [ ] Replace the `*(pending capture)*` cell in `index.md` with the
      `<a><img width="320"></a>` embed
- [ ] Fill in the row's Timestamp, Match Status, and Notes columns

**Close-out**

- [ ] Review the gallery table — every committed file appears as a
      row; every uncaptured canonical ID has a gap row with an explicit
      reason from Exit criterion #1
- [ ] Confirm at least one full-room background capture exists (Exit
      criterion #4 — decoder comparison target)
- [ ] Confirm at least one `OBJ_DAPHNE_A` (or other character sprite)
      capture exists (WP-002 first-decode target — see §Notes)
- [ ] Add 1–2 thumbnail teasers to the WORK_INDEX "Reference
      Screenshots" section linking to the gallery
- [ ] `git add` the PNGs + `index.md` changes + WORK_INDEX change; commit
- [ ] Push and verify the gallery renders at
      `https://github.barefootbetters.com/scooby-engine/docs/assets/screenshots/showdown-screens/`
      with all images loading
- [ ] Flip WP status from 📦 Queued → ✅ Done in WORK_INDEX

## Notes

- **Why `docs/assets/`, not `tools/samples/`:** `tools/` is excluded from the
  GitHub Pages build (`_config.yml`) and `tools/samples/*` is gitignored.
  Screenshots in `tools/` would never commit and never appear on the site.
  `docs/assets/screenshots/` is tracked, served by Pages, and referenceable
  from any markdown file with a relative path.
- **Copyright:** These are screen captures from publicly available YouTube
  footage, used for reverse-engineering reference — fair use, consistent with
  how ScummVM documents all supported games. No files extracted from the
  game disc are stored here. Do not store disc-extracted binaries, audio, or
  decoded images alongside these screenshots.
- Screen resolution does not need to match the original game resolution.
  YouTube 720p is fine — visual pattern matching (silhouettes, color
  palette, character placement) is sufficient to verify a decoded asset.
  You are not doing pixel-exact comparison.
- **WP-003 (2026-06-02) — negative palette finding.** No palette exists in
  the `TGIFILE.ART` pre-payload region; palette discovery moved into
  WP-002 (per-asset leading bytes or per-record metadata). The "compare
  palette colors against screenshots before decoding" shortcut therefore
  does not apply at this stage — once WP-002 locates the palette, the
  pre-decode color-distribution sanity check becomes available again
  and is still worth running.
- **WP-003 also unlocked canonical ROOM naming** (`ROOM_P21_Boot_Hill1`,
  `ROOM_P25A_Chase_B2_Closeup`, etc. — 42 ROOMs total, IDs `0x1B`–`0x44`,
  plus engine-room entries like `ROOM_Options`/`ROOM_Quit`/`ROOM_Credits`).
  The full list is at `tools/samples/wp003-name-table.txt` (gitignored,
  regenerable from the SHA-256-locked source binary). If screenshots are
  named with these IDs / suffixes (e.g. `P21-boot-hill1.png` or
  `P25A-chase-b2-closeup.png`), the cross-reference to WP-008's catalog
  is automatic and the WP-008-runs-first ordering becomes optional rather
  than load-bearing.
- **WP-008 (2026-06-03) — canonical room list now in the catalog.**
  The asset catalog at `tools/samples/asset-catalog.json` (gitignored,
  regenerable via `py -3 tools/parse_ini.py tools/exes/showdown/object.ini
  --catalog --eng tools/exes/showdown/Scooby.eng --name-table
  tools/samples/wp003-name-table.txt --out tools/samples/asset-catalog.json`)
  carries the 37 canonical `destinationroom=` IDs actually referenced
  by `object.ini` — a strict subset of the 42 ROOM entries in WP-003's
  name table. Use these 37 as the screenshot-naming source of truth
  (e.g. `ROOM_P21_Boot_Hill1.png`, `ROOM_P12_Saloon.png`,
  `ROOM_Main_Menu.png`). The 5 ROOM entries in WP-003 not referenced
  by `object.ini` (`ROOM_Cheat`, `ROOM_Options`, `ROOM_Quit`,
  `ROOM_Credits`, etc.) are reachable through menu/system paths and
  worth capturing if encountered, but they're not on the room-by-room
  gameplay path.
- **WP-008 (2026-06-03) — 21 ROOMs render via per-room code paths.**
  Per the [scooby-exe.md `object.ini` Findings](../formats/scooby-exe.md#objectini-interpreter-behavior),
  21 of the 37 `destinationroom=` values point at rooms that have **no
  `TGIFILE.ART` entry** — including `ROOM_Main_Menu`,
  `ROOM_P01_Town_Center`, `ROOM_P12_Saloon`,
  `ROOM_P30_Horseshoe_Corral` (minigame), `ROOM_P32_Pie_Noon`
  (minigame). For these rooms the WP-002 decoder will NOT produce a
  matching background, because there isn't one — they're rendered by
  per-room code (`\Scooby\GBH\Horseshoe_Corral_Room.cpp`,
  `Pie_Noon_Room.cpp`, etc. per the [Showdown source-tree
  strings](../formats/scooby-exe.md#showdown-gen-1)). Capture
  screenshots of these anyway: they're the visual ground truth for
  the per-room code paths that WP-001 will trace in Ghidra and
  ScummVM-side Phase 3 will need to reimplement.
- **WP-003 also revised the "first decode" target.** `entry[0]` is
  `OBJ_DAPHNE_A` — a character sprite, not a background. The screenshot
  library should include at least one clear shot of Daphne (idle or
  walk-cycle) so WP-002 has a visual comparison target for its first
  decode pass.
- The YouTube timestamp in the gallery's provenance column matters for
  reproducibility: if a decoded image is later disputed (e.g. different
  region disc has different art), you can trace the screenshot to its
  exact source frame and confirm whether the visual discrepancy is a
  decoding error or a version difference.
- **Gallery URL mechanics.** `_config.yml` applies `layout: default` to
  everything under `docs/` and has `permalink: pretty` set, so renaming
  `README.md` → `index.md` produces the clean URL
  `https://github.barefootbetters.com/scooby-engine/docs/assets/screenshots/showdown-screens/`.
  Keeping it as `README.md` would either serve at `…/readme/` or get
  shadowed by GitHub's own README rendering — `index.md` is the right
  filename for the Pages gallery.
- **WP-008 supersedes the earlier slug-fallback guidance.** WP-008 has
  landed, so the canonical room IDs (`ROOM_P21_Boot_Hill1` etc.) are
  available now — name files with those IDs directly. Descriptive slugs
  remain a last-resort fallback only when a captured frame doesn't match
  any of the 37 catalog IDs (unlikely on the room-by-room gameplay path).
