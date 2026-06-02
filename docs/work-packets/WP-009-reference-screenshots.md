---
layout: default
title: "WP-009: Reference Screenshot Library"
---

# WP-009: Reference screenshot library (*Showdown in Ghost Town*)

**Status:** 📦 Queued
**Phase:** Pre-Work (before WP-002)
**Depends on:** WP-008 (for room ID naming — can run without it using descriptive slugs)
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
- If WP-003 has run and a palette was found: glance at the palette color
  distribution vs. the screenshots before decoding. If the palette's
  dominant colors match the screenshots, it's a strong pre-confirmation
  that the indexed-color decode strategy will work.
- The YouTube timestamp in the README matters for reproducibility: if a
  decoded image is later disputed (e.g. different region disc has different
  art), you can trace the screenshot to its exact source frame and confirm
  whether the visual discrepancy is a decoding error or a version difference.
- Naming by room ID saves reconciliation time later. If WP-008 produced
  a catalog with a `hotel_lobby` room ID, name the screenshot `hotel-lobby.png`
  (use hyphens for filesystem-safe slugs, underscores are fine too). If
  WP-008 hasn't run yet, use a descriptive slug and add a rename pass once
  WP-008 completes.
