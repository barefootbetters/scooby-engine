---
layout: default
title: "WP-009: Reference Screenshot Library"
---

# WP-009: Reference screenshot library (*Showdown in Ghost Town*)

**Status:** 📦 Queued
**Phase:** Pre-Work (before WP-002)
**Depends on:** WP-008 ✅ (room IDs available — see §Notes)
**Companion EC:** — (manual capture; no checklist needed)
**Estimated effort:** 1–2 hours

---

## Goal

Capture one representative screenshot of each distinct room/scene in
*Showdown in Ghost Town* from a YouTube longplay, store them as
`tools/samples/showdown-screens/<room-id>.png`, and produce a provenance
README. These become the visual ground truth for WP-002's decoder: when
`probe_art.py` produces an image, the comparison target is a named file,
not a memory of what the game looked like.

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
- Capture one representative screenshot per visually distinct room: main
  background with game UI hidden or minimal; no loading or transition frames
- Name files by room ID from WP-008's catalog (preferred), or by
  descriptive slug if WP-008 hasn't run yet — names can be reconciled later
- Store in `tools/samples/showdown-screens/`
- Produce `tools/samples/showdown-screens/README.md` logging each file's
  room ID (or slug), YouTube URL, and approximate timestamp

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

1. `docs/assets/screenshots/showdown-screens/` exists with ≥ 8 distinct room
   background screenshots, covering the main gameplay areas.
2. Files are named consistently — by `object.ini` room ID (preferred)
   or by descriptive slug (e.g. `hotel-lobby`, `ghost-mine-entrance`).
3. `docs/assets/screenshots/showdown-screens/README.md` is updated listing each file,
   its room ID or slug, and the YouTube timestamp it was sourced from.
4. At least one screenshot is clearly a full-room background (not a
   partial view or transition frame) — this is the primary decoder target.
5. Screenshots are visible on the GitHub Pages site at
   `https://github.barefootbetters.com/scooby-engine/docs/assets/screenshots/showdown-screens/`
   and render in WORK_INDEX gallery section.

## Deliverables

- `docs/assets/screenshots/showdown-screens/<room-id>.png` × ≥ 8
- `docs/assets/screenshots/showdown-screens/README.md` — provenance + timestamp log (pre-seeded; add rows as captures are taken)

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
- The YouTube timestamp in the README matters for reproducibility: if a
  decoded image is later disputed (e.g. different region disc has different
  art), you can trace the screenshot to its exact source frame and confirm
  whether the visual discrepancy is a decoding error or a version difference.
- Naming by room ID saves reconciliation time later. If WP-008 produced
  a catalog with a `hotel_lobby` room ID, name the screenshot `hotel-lobby.png`
  (use hyphens for filesystem-safe slugs, underscores are fine too). If
  WP-008 hasn't run yet, use a descriptive slug and add a rename pass once
  WP-008 completes.
