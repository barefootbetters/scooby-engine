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

This WP has two tiers, addressing two distinct downstream consumers:

- **Required tier — decoder anchors (WP-002 consumer):**
  - All 16 `TGIFILE.ART`-backed canonical rooms from the WP-008 catalog
    (the rooms where `entry[i]` payloads exist — primary decoder
    comparison targets).
  - At least one character sprite capture, `OBJ_DAPHNE_A.png` minimum
    (`entry[0]` of `TGIFILE.ART` — WP-002 first-decode target). Sprites
    are a small auxiliary set within this WP, not a separate WP: the
    operator is already in the longplay with capture tooling open, and
    rerouting them to a WP-002 pre-flight forces a second session.
  - Files in this tier are committed as **PNG** (lossless). Lossy
    compression here would introduce artifacts that could be mistaken
    for decoding errors; the decoder also outputs PNG, so same-format
    comparison is the natural fit.

- **Stretch tier — gameplay reference (WP-001 / Phase 3 consumer):**
  - The remaining 21 code-rendered canonical rooms (per [WP-008 §Notes —
    21 ROOMs render via per-room code paths](#notes)). These have no
    `TGIFILE.ART` entry; they're visual ground truth for the per-room
    `*_Room.cpp` traces in WP-001 Ghidra and the Phase 3 reimplementation.
  - Capture opportunistically as the longplay reaches each room.
  - Files in this tier may be **PNG or high-quality WebP** (≥ 90 quality,
    no visible artifacts). Lossless isn't load-bearing here — there's no
    decoder comparison, only human visual reference.

### Per-tier scope details

In scope (both tiers):
- Locate a *Showdown in Ghost Town* YouTube longplay (search "Scooby-Doo
  Showdown in Ghost Town full game longplay" — several exist)
- Capture one clean stationary frame per visually distinct room per the
  §Goal capture rules
- File naming is **strictly canonical-first**:
  - MUST match a `destinationroom=` ID from the WP-008 asset catalog
    when the captured room corresponds to one (verbatim, e.g.
    `ROOM_P21_Boot_Hill1.png`). Source of truth: `tools/samples/asset-catalog.json`
    `rooms` map (gitignored — regenerate per WP-008 §Notes if missing).
  - If no canonical match can be confidently made, name the file
    `UNMATCHED_<descriptive-slug>.png` and log the reason in the
    provenance table (e.g. `UNMATCHED_phantom-chase-corridor.png` for
    a chase-sequence frame that doesn't clearly map to any of the
    `ROOM_P*_Chase_*` IDs).
  - "Uncertain but probably matches" is NOT a third path — if you can't
    canonicalize confidently, it's `UNMATCHED_`. The status stays
    `Unmatched` until a later pass resolves it to a canonical ID and
    the file is renamed. No silent guessing, no half-canonical names.
- The gallery scaffold has already been pre-seeded: `index.md` carries
  all 37 canonical room IDs as `*(pending capture)*` rows in five area
  tables, plus the `OBJ_DAPHNE_A` row in the Character sprites section
  and an empty Unmatched captures table. Capture work is fill-in-cells,
  not table construction.
- Store in `docs/assets/screenshots/showdown-screens/` (git-tracked,
  served by Pages — see §Notes for why not `tools/samples/`)
- Add **one or two** representative thumbnail teasers to the WORK_INDEX
  "Reference Screenshots" section, each linking to the gallery page.
  Do NOT inline the full 16+ image set in WORK_INDEX.

**Capture quality requirements (both tiers):**

- Minimum source quality: 720p (YouTube 720p export is the floor).
- No compression artifacts that obscure shapes or colors — if the
  longplay's source quality is borderline, find a higher-quality
  longplay rather than capturing the artifact.
- Frame must be sharp (not mid-motion).
- Cropping is allowed ONLY to remove black borders / letterboxing —
  do not crop scene content (a cropped scene-content frame compromises
  decoder visual comparison and Phase 3 reference).

Out of scope:
- Every animation frame, sprite pose, or inventory icon beyond the
  single Required-tier sprite anchor (Phase 4)
- UI-only screenshots (inventory screen, options screen)
- Cutscene frames — Bink decoder is handled separately
- Phantom, Jinx, or Case File screenshots (separate WPs if needed)

## Dependencies

- Internet access + YouTube
- Screenshot tool: Windows Snipping Tool, Greenshot, or OBS frame export
- WP-008 asset catalog (for room naming; not required to start)

## Exit criteria

1. **Required-tier coverage achieved (binary gate — WP cannot close
   without this).**
   - All 16 `TGIFILE.ART`-backed canonical rooms captured as PNG files.
   - At least one character sprite anchor captured as `OBJ_DAPHNE_A.png`
     (or substituted sprite if `OBJ_DAPHNE_A` is unobservable in the
     longplay — log substitution reason in the Notes column).
   - Any Required-tier ID NOT captured MUST be listed in the provenance
     table with Match Status `Gap` and one of these explicit reasons:
     - `Not reached in longplay`
     - `Not observable in source video` (UI overlay, scene too brief,
       always behind transition)
   - The Required tier has no "uncertain" escape — every Required-tier
     row is either a captured canonical file or a `Gap` row with a
     reason. (Uncertain captures are saved as `UNMATCHED_<slug>` and
     listed in the Unmatched table; they do NOT satisfy Required-tier
     coverage.)

2. **Stretch-tier coverage logged.**
   - For each of the 21 code-rendered canonical rooms, the gallery row
     is either a captured file (PNG or high-quality WebP) or a `Gap`
     row with the same reason set as Required tier.
   - Partial coverage is acceptable at this tier; the gate is honest
     accounting, not completion.

3. **Naming compliance (binary, both tiers).**
   - Every committed file is either:
     - A WP-008 canonical room or object ID verbatim (e.g.
       `ROOM_P21_Boot_Hill1.png`, `OBJ_DAPHNE_A.png`), OR
     - Prefixed `UNMATCHED_<descriptive-slug>.png` (or `.webp`) with a
       `Match Status: Unmatched` row in the Unmatched captures table
       and a justification in the Notes column.
   - No silent slugs, no near-canonical names (`ROOM_P21_BootHill.png`
     when the catalog says `ROOM_P21_Boot_Hill1`), no half-matches.

4. **Gallery page rendered.**
   - `docs/assets/screenshots/showdown-screens/index.md` (pre-renamed
     from `README.md`) renders on the Pages site, using the provenance
     schema in §Deliverables — every row shows an embedded preview
     alongside Room ID / Source Video / Timestamp / Match Status /
     Notes.
   - This `index.md` IS the canonical gallery page; it is the primary
     deliverable of this WP, not a side artifact.

5. **Decoder-anchor validation (Required-tier sanity check).**
   - At least one Required-tier capture is a full-room static background
     (not a partial view, not a transition), clear and unobstructed per
     §Goal capture rules — suitable for direct visual comparison with
     decoded `TGIFILE.ART` output. This is the frame EC-002 pre-flight
     will pull when running decode strategies.
   - The `OBJ_DAPHNE_A` (or substitute) sprite anchor is present and
     clear — `entry[0]` of `TGIFILE.ART` is `OBJ_DAPHNE_A`, so this is
     the WP-002 first-decode comparison target. See §Notes.

6. **WORK_INDEX teaser updated.**
   - WORK_INDEX "Reference Screenshots" section carries one or two
     representative thumbnail teasers, each linking to the gallery
     page. The full 16+ image set does NOT live inline in WORK_INDEX.

7. **Pages render verified.**
   - Gallery page is visible at
     `https://github.barefootbetters.com/scooby-engine/docs/assets/screenshots/showdown-screens/`
     and all embedded images load (no broken images in the live render).

## Deliverables

- **Required-tier files** (PNG, lossless):
  - `docs/assets/screenshots/showdown-screens/<ROOM_id>.png` × 16
    (TGIFILE.ART-backed canonical rooms; full-size, typically 1280×720
    from YouTube 720p).
  - `docs/assets/screenshots/showdown-screens/OBJ_DAPHNE_A.png` × 1
    (or substituted sprite if `OBJ_DAPHNE_A` is unobservable; note in
    table).
- **Stretch-tier files** (PNG or high-quality WebP):
  - `docs/assets/screenshots/showdown-screens/<ROOM_id>.{png,webp}` × up
    to 21 (code-rendered canonical rooms; opportunistic).
- **Unmatched files** (PNG or WebP, same tier as the room they would
  belong to if canonicalized):
  - `docs/assets/screenshots/showdown-screens/UNMATCHED_<slug>.{png,webp}` × any
- `docs/assets/screenshots/showdown-screens/index.md` — gallery page +
  provenance log. Pre-renamed from `README.md` in the WP-009 prep pass;
  the scaffold (37 canonical room IDs + sprite anchor row + Unmatched
  table) is already in place.

**Provenance schema (mandatory).**

The `index.md` provenance table MUST include exactly these columns:

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|

Where:

- **Preview** — `<a href="<file>"><img src="<file>" width="320"></a>`
  (full-size file linked from the inline thumbnail; HTML width caps the
  *displayed* size only — the underlying file is still full resolution
  for downstream comparison).
- **Room ID** — canonical ID in backticks, e.g. `` `ROOM_P21_Boot_Hill1` ``.
  For unmatched captures, use the `UNMATCHED_<slug>` filename here.
- **Source Video** — link to the YouTube longplay. The same longplay
  URL is declared once at the top of the page; per-row entries can
  short-form as `[YT](url)` or omit if the global URL applies (the
  global URL is the default; per-row only when a second source was
  needed for a specific room).
- **Timestamp** — `mm:ss` or `hh:mm:ss` into the source video. Required
  for every captured row; reproducibility hinges on this column.
- **Match Status** — one of: `Canonical`, `Unmatched`, `Gap`.
  - `Canonical` — filename is an exact WP-008 catalog ID, capture is
    committed.
  - `Unmatched` — `UNMATCHED_`-prefixed filename, capture is committed
    in the Unmatched table; the canonical row stays as `Gap` until the
    file can be resolved to a canonical ID and renamed.
  - `Gap` — canonical ID not captured; Preview and Timestamp are blank,
    Notes carries one of the explicit reason strings from Exit
    criterion #1.
  - There is no `Uncertain` status. "Uncertain but probably matches" is
    not a valid path — if you can't canonicalize confidently, save as
    `UNMATCHED_<slug>` and leave the canonical row as `Gap`.
- **Notes** — any ambiguity, capture limitation, or context the next
  reader needs (UI partially obscuring scene, two visually similar rooms
  hard to distinguish, etc.). For `Gap` rows, use the explicit reason
  strings from Exit criterion #1.

Page-weight sanity check: full-size PNGs run ~1–2 MB each; WebP at
quality 90 runs ~150–300 KB. The `width="320"` embed keeps the rendered
gallery light regardless of file format; the underlying file is
unchanged.

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
      editing alongside the longplay — the scaffold is already
      pre-seeded with all 37 canonical room IDs and the sprite anchor
      row; this WP is fill-in-cells, not table construction
- [ ] Identify which 16 rooms are TGIFILE.ART-backed (Required tier)
      vs which 21 are code-rendered (Stretch tier) per
      [WP-008 §Notes](#notes); mark Required-tier rows in the scaffold
      if helpful

**Per-room capture loop** (repeat for each distinct room encountered)

- [ ] Pause the longplay on a clean stationary frame (per §Goal
      capture rules: no transitions, no motion blur, no UI obstructing
      geometry)
- [ ] Match the room to a WP-008 canonical ID with confidence:
  - If confident → file is `<canonical-id>.png` (Required tier) or
    `<canonical-id>.{png,webp}` (Stretch tier), Match Status `Canonical`
  - If NOT confident → file is `UNMATCHED_<slug>.{png,webp}`, Match
    Status `Unmatched`, row added to the Unmatched table; the canonical
    row stays as `Gap` until resolved
- [ ] Capture at full source resolution (no scene-content cropping;
      black-border crop only). Required tier: PNG. Stretch tier: PNG or
      WebP quality ≥ 90.
- [ ] Save to `docs/assets/screenshots/showdown-screens/`
- [ ] Replace the `*(pending capture)*` cell in the appropriate table
      row with the `<a><img width="320"></a>` embed
- [ ] Fill in the row's Timestamp, Match Status, and Notes columns

**Close-out**

- [ ] Required-tier check (Exit criterion #1): all 16 TGIFILE.ART-backed
      rooms either captured or marked `Gap` with an explicit reason;
      `OBJ_DAPHNE_A` (or substitute) sprite anchor present
- [ ] Stretch-tier check (Exit criterion #2): each of the 21
      code-rendered rooms either captured or marked `Gap`
- [ ] Confirm at least one Required-tier capture is a full-room static
      background suitable for EC-002 visual comparison (Exit criterion #5)
- [ ] Add 1–2 thumbnail teasers to the WORK_INDEX "Reference
      Screenshots" section linking to the gallery
- [ ] `git add` the PNG/WebP files + `index.md` changes + WORK_INDEX
      change; commit
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
