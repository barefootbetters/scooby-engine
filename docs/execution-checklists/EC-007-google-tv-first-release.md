---
layout: default
title: "EC-007: First Google TV release run sheet"
---

# EC-007: First Google TV release — build, device run and Play checklist

**Paired WP:** [WP-084](../work-packets/WP-084-google-tv-first-release.md)
**Purpose:** Keep the first Google TV release reproducible and honest: one
build from a tagged commit, one logged device run, one Play submission path.
Defects found are logged as one-line gaps and the run continues; fixes go to
the WP's branch or a follow-up WP, never improvised mid-run.
**Status:** not started. ⏸ Blocked on WP-084 Gate 0.

**Evidence rule:** every checked box cites a log line, a command output or a
screenshot captured during the run. A box with no capture stays unchecked.

---

## Pre-flight

- [ ] WP-084 Gate 0 recorded in [DECISIONS](../ai/DECISIONS.md); D1–D5 answered.
- [ ] Pre-flight verdict **READY** in `docs/reference/pre-flight-WP-084-<date>.md`.
- [ ] Fork worktree `wp-084-google-tv-first-release` off a freshly fetched
      `origin/scooby-engine`; commit hash recorded.
- [ ] Toolchain recorded: SDK platform 37, NDK 23.2.8568313, Oboe for both
      ABIs, Gradle wrapper version, `bundletool` version.
- [ ] Capture sink ready outside both repos (logs, screenshots, AAB/APKs).

## Step 1 — Game data (time-box: 0:20)

- [ ] `bass-cd-1.2.zip` downloaded from downloads.scummvm.org; SHA-256 equals
      `53209b9400eab6fd7fa71518b2f357c8de75cfeaa5ba57024575ab79cc974593`.
- [ ] Unpacked to the staging folder; `sky.dsk` size matches a v0.0372 CD
      entry (72,395,713 or 73,123,264 bytes); the readme is present and unedited.
- [ ] Desktop sanity check: the fork's Windows build detects it as `sky` (CD).

## Step 2 — Build (time-box: 2:00)

- [ ] `configure` line and make target recorded verbatim.
- [ ] AAB built; `bundletool dump` (or unzip listing) shows
      `lib/armeabi-v7a` and `lib/arm64-v8a`, and the game under the
      `mainAssets` pack's `assets/games/`.
- [ ] 16 KB alignment of the arm64 `.so` files checked; output recorded.
- [ ] `bundletool build-apks --mode=universal` (or device-targeted) APKs
      produced for sideloading.

## Step 3 — First run on the TCL 65Q77K (time-box: 0:30)

- [ ] Previous builds uninstalled; fresh install over `adb`; `logcat` capture
      running.
- [ ] Launcher tile shows the app's banner with its name.
- [ ] First launch adds the bundled game and **starts BASS directly** (log
      line + screenshot); no ScummVM launcher appears.
- [ ] Second launch starts BASS directly again.

## Step 4 — Playthrough with a gamepad (time-box: 4:00)

- [ ] Bluetooth gamepad paired; no mouse, keyboard or touch used.
- [ ] Pointer movement, A (walk/look/talk), B (use), Y (skip), X (control
      panel) all work; gaps logged.
- [ ] Control panel dialogs (save, restore, volume, quit) operable from the
      gamepad.
- [ ] Playthrough reaches the end credits (screenshot of the credits, log
      excerpt). Gaps logged with location.

## Step 5 — Save / restore and exit (time-box: 0:30)

- [ ] Save from the control panel mid-game; quit; relaunch; restore resumes
      the saved position (log + screenshots before and after).
- [ ] Back from gameplay leads to the TV home screen (TV-DB); quitting the
      game exits the app.

## Step 6 — Licenses and source (time-box: 1:00)

- [ ] Licenses screen shows GPLv3, ScummVM `COPYING` / `COPYRIGHT` /
      `AUTHORS`, applicable `LICENSES/*`, Oboe Apache-2.0, the BASS readme and
      the source URL (screenshots).
- [ ] Fork tag pushed; source archive, `BUILDING.md` and checksums published at
      the permanent URL; a clean rebuild from the tag produces the native
      libraries (result recorded).

## Step 7 — Google Play (time-box: 2:00 + closed-test wall clock)

- [ ] App created; Play App Signing configured per D4; upload key stored
      offline.
- [ ] Listing: description with "Powered by ScummVM", the GPL source link and
      the Revolution credit; 1280×720 banner; TV screenshots from the run.
- [ ] Privacy policy URL; data safety; content rating questionnaire; target
      audience per D5; ads / health / financial declarations.
- [ ] Android TV form factor opted in; TV review policy accepted.
- [ ] Closed test track live; tester count and start date recorded (personal
      account: 12 testers, 14 consecutive days).
- [ ] **Stop.** Production release waits for Jeff's explicit go
      (WP-084 exit criterion 12).

## Definition of done

All step outcomes recorded with captures, WP-084 exit criteria 3–11 met,
WP-084 §Result written, WORK_INDEX status updated.

## Out-of-scope captures

Record temptations here as one-line follow-ups (for example a D-pad pointer,
compressed audio, more freeware titles, store listings elsewhere) and move on.
