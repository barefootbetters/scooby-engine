---
layout: default
title: "EC-008: Google TV app pipeline run sheet"
---

# EC-008: Google TV app pipeline — per-milestone device checks

**Paired WP:** [WP-085](../work-packets/WP-085-tv-app-pipeline.md)
**Purpose:** Verify each WP-085 milestone on the TCL 65Q77K before the next one
starts, with evidence. Defects are logged as one-line gaps; fixes go on the WP
branch before moving on.
**Status:** pre-flight READY (2026-11-26); execution not started. The
execution prompt is
[session-WP-085-2026-11-26](../sessions/session-WP-085-2026-11-26.md).

**Evidence rule:** every checked box cites a `logcat` excerpt, a command output
or a screenshot captured during the run. No capture, no check.

---

## Pre-flight

- [x] WP-085 D0–D4 answered; pre-flight verdict **READY**
      ([pre-flight-WP-085-2026-11-26](../reference/pre-flight-WP-085-2026-11-26.md)).
- [x] Fork branch and commit recorded: `wp-085-tv-app-pipeline` in
      `C:\claude-worktrees\scummvm-wp-085-tv-app-pipeline`, base
      `ff490ad9449f`. Toolchain recorded: `platforms/android-37.0`, NDK
      `23.2.8568313`, Oboe 1.11.0 for armeabi-v7a built against `android-16`
      (the TCL's ABI list is `armeabi-v7a,armeabi`). Outputs are in the
      [pre-flight §Repo + disc state](../reference/pre-flight-WP-085-2026-11-26.md#repo--disc-state).
- [ ] Test data staged outside both repos: BASS freeware at
      `P:\games\BeneathASteelSky\bass-cd-1.2.zip` (SHA-256 matches), Jeff's
      *Showdown* at `P:\scooby-engine\Showdown.iso` (`Scooby.exe` is the
      WP-079 identity). **Capture sink: open.** It's set up at the start of
      execution, with the peripheral check (keyboard, mouse and gamepad shown
      in `dumpsys input`), which the pre-flight carried forward.

## Step 1 — Milestone 1: app shell (time-box: 1:00)

- [ ] Fresh install over `adb`; the launcher tile shows the app's own banner
      and name.
- [ ] The library (ScummVM launcher, grid view) opens.
- [ ] Keyboard: typing and shortcuts work. Mouse: pointer, click, right-click,
      scroll. Gamepad: stick pointer, A/B, menus. Remote: reach and launch a
      library entry. Each: pass or gap.

## Step 2 — Milestone 2: import (time-box: 1:30)

- [ ] System file picker ("Add game"): present on the TCL? Adds BASS from USB
      storage? Pass or gap.
- [ ] Cloud download dialog: connect a test cloud drive, download BASS, add it.
      Pass or gap.
- [ ] `adb push` fallback works.
- [ ] Imported game launches; save, close the app, reopen, restore (logged).

## Step 3 — Milestone 3: test packages (time-box: 1:30)

- [ ] Advanced mode is hidden by default in a test build and opens by the
      agreed gesture; a Play-configured build doesn't include it (D4).
- [ ] Manifest fetched over HTTPS; packages listed.
- [ ] BASS package: downloaded from the URL its manifest entry gives (GitHub
      Releases in the dedicated test-package repo, per D3), SHA-256 verified,
      extracted, detected, launched (logged).
- [ ] Host independence: point the BASS entry's URL at a second HTTPS host
      and it downloads and verifies, with no app change (logged).
- [ ] A package with a deliberately wrong SHA-256 is refused (logged).
- [ ] Remove: game files and library entry gone, saves kept (logged).
- [ ] Diagnostics: engine version, detection results, log export.

## Step 4 — Milestone 4: updates (time-box: 1:30)

- [ ] Install a newer build over the old one: games, library and saves intact.
- [ ] Manifest bumps the BASS package version: update offered, verified, swapped.
- [ ] Interrupt an update (network off mid-download): the old version still
      launches and plays (logged).
- [ ] *Showdown* (TerraGlyph) imported by a non-public route launches and saves.

## Definition of done

All step outcomes recorded with captures, WP-085 exit criteria 2–6 met,
§Result written, WORK_INDEX updated.

## Out-of-scope captures

One-line follow-ups only (a TV-styled library, D-pad pointer, Play listing work,
billing) — then move on.
