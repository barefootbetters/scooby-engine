---
layout: default
title: "WP-085: Google TV app pipeline"
---

# WP-085: Google TV app pipeline — library, import, test packages and updates

**Status:** 📝 Drafted · **pre-flight READY 2026-11-26**
([pre-flight](../reference/pre-flight-WP-085-2026-11-26.md); execution prompt
[session-WP-085-2026-11-26](../sessions/session-WP-085-2026-11-26.md)). Claimed:
fork worktree `wp-085-tv-app-pipeline` off `ff490ad9449f`. Not blocked on any rights holder: it distributes no
game, and tests only with legally obtained data. **Built first:** Jeff chose
"Pipeline first (a)" on 2026-11-26, so this app ships to Google Play through
[WP-084](WP-084-google-tv-first-release.md) once it's done
([D0](#decisions-for-jeff)).
**Phase:** 5 (polish & distribution).
**Depends on:** WP-079 ✅ (the fork's TV build path proven on the TCL 65Q77K,
per the [smart-TV guide](../reference/scummvm-smart-tv.md#tv-smoke-test)).
**Unblocks:** any Google Play release of the studio's TV app (WP-084 or its
successor), and the delivery path for licensed TerraGlyph game data.
**Companion EC:** [EC-008](../execution-checklists/EC-008-tv-app-pipeline.md).
**Pre-flight required:** **Yes.** It changes the fork outside
`engines/terraglyph/` (the Android backend and build configuration) and adds
network download code.
**Targets generation(s):** none directly. TerraGlyph is compiled in and tested
with Gen 1 (*Showdown*) data; no engine code changes.
**Estimated effort:** about 2 weeks across four milestones, each verified on
the TV before the next starts.

---

## Goal

Prove the studio can deliver and maintain a complete ScummVM-powered game
experience on Google TV: an app with its own identity that contains the fork's
runtime, shows a library of installed games, imports legally obtained games,
downloads and installs authorized game-data packages with integrity checks,
removes them, and keeps games and saves through app and game-data updates.
**The milestone is the pipeline, not any particular game.** It's built and
verified by sideloading; the Google Play release is a separate step.

## Background

- **Where this comes from.** Microsoft Copilot's 2026-11-26 recommendation,
  relayed by Jeff: build the delivery pipeline first and choose the first
  shipped game later. It follows the
  [decision to ship a free Google TV app first](../ai/DECISIONS.md#2026-11-26--ship-the-free-google-tv-app-first)
  and WP-084, which first planned a single-game app; this WP plans a
  multi-game app, and Jeff's D0 answer puts it first, with WP-084 re-scoped as
  its Play release. See [§Decisions](#decisions-for-jeff).
- **What ScummVM's Android port already provides**
  (`origin/scooby-engine` `ff490ad9449f`):
  - **The library:** ScummVM's launcher (list and grid views) with detection,
    "Add game" and mass add. On Android, "Add game" goes through the system
    file picker (the Storage Access Framework).
  - **Bundled games:** `GAMES_BUNDLE_DIRECTORY` in `android.mk`, added on the
    first run after each version update by `OSystem_Android::updateStartSettings`.
  - **App Bundle with an install-time asset pack:** `make androidbundlerelease`
    (`bundleRelease -PsplitAssets`), and `fatbundle.mk` for all ABIs.
  - **Networking:** an Android HTTP backend (`backends/networking/basic/android/`),
    cloud storage, and a remote browser and download dialog
    (`gui/remotebrowser.cpp`, `gui/downloaddialog.cpp`) for fetching game files
    from a connected cloud drive.
  - **A game-download feature:** `backends/dlc/` (`--enable-dlc`,
    `--enable-scummvmdlc`) downloads a zip, extracts it and adds the game. But
    it's wired only into the SDL (desktop) backends, its store URL is
    commented as a "temporary mock api", and it has **no integrity check**.
    Not usable as-is on Android.
  - **Saves** live in app-specific storage, which survives app updates and is
    deleted on uninstall.
- **The hard step today.** Getting game data onto a TV is the hardest part of
  the [smart-TV guide](../reference/scummvm-smart-tv.md#add-your-game-data).
  The official ScummVM app on Play ships no game data and expects users to
  find it themselves; ScummVM's own reply to a review on that listing says
  adding a game folder takes six steps. Easy, verified installation is this app's reason to exist.
- **Google rules this WP must follow** (read 2026-11-26):
  - [Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/16559646):
    a Play app may not update itself outside Play, and may not download
    executable code (dex, JAR, `.so`) from outside Play. Code run by a virtual
    machine or interpreter is exempt. **Game data interpreted by ScummVM's
    engines is allowed; downloading native engine builds is not.** Test engine
    builds go through Play's internal or closed testing tracks.
  - [TV app quality](https://developer.android.com/docs/quality-guidelines/tv-app-quality):
    app functionality must be navigable with a five-way D-pad **unless the app
    requires a game controller** (TV-DP, TV-DK, TV-GP). There is no equivalent
    exemption for a mouse; pointer support (TV-TO) is a recommendation.

## Scope

### In scope

**Milestone 1 — the app shell.**
1. Our own `applicationId`, app name, icon and TV banner (per D1), containing
   the fork's runtime with `sky` and `terraglyph` engines (and any engine the
   test data needs).
2. The library is ScummVM's launcher (grid view), not a new UI, for v1.
3. Input: Bluetooth keyboard and mouse work throughout; a gamepad works
   throughout (left stick moves the pointer); the TV remote reaches and
   launches games in the library. Each recorded as pass/gap on the TCL. The
   Play release declares a gamepad required ([D2](#decisions-for-jeff);
   WP-084 §6 sets the manifest); keyboard and mouse stay supported.

**Milestone 2 — importing a legally obtained game.**
4. On the TCL, test each import route and record which work: the system file
   picker ("Add game", including from USB storage); ScummVM's cloud download
   dialog; `adb push` to the app's folder (developer fallback).
5. An imported game is detected, appears in the library, launches, saves, and
   restores after the app is closed and reopened.

**Milestone 3 — authorized test packages (an advanced mode).**
6. A hidden advanced mode (off by default) that lists packages from a
   manifest fetched over HTTPS. **Test builds only** ([D4](#decisions-for-jeff)):
   the Play build doesn't include it.
7. Each package is a zip of **game data only**. The manifest gives its id,
   version, size, SHA-256 and **download URL**. The downloader takes any HTTPS
   URL from the manifest and hard-codes no host, so packages can move between
   hosts without an app change ([D3](#decisions-for-jeff)). The app downloads to a temporary folder,
   **refuses any file whose SHA-256 doesn't match**, extracts into app-specific
   storage (not the bundled-assets path, which `updateStartSettings` prunes),
   runs ScummVM's add/detection, and shows it in the library.
8. Remove: deletes the game's files and its library entry; its saves are kept
   unless the user deletes them too.
9. Advanced mode also shows the engine version, the detection result for each
   installed game, and a shareable diagnostic log.
10. Implementation preference: Android-side (Java) download, verify and extract,
    feeding ScummVM's existing add path; keep C++ changes minimal. Porting
    `backends/dlc/` to Android is the alternative if it proves smaller (it
    would still need the integrity check added).

**Milestone 4 — updates.**
11. App updates: a newer build installed over an older one (sideload now; Play
    later) keeps installed games, library entries and saves.
12. Game-data updates: a manifest with a newer package version offers an
    update; the new package is downloaded and verified before the old one is
    touched, then swapped in; a failed or interrupted update leaves the old
    version playable.
13. Verified end to end on the TCL with the test data in
    [§Dependencies](#dependencies).

### Out of scope

- **Any Google Play release, price or listing.** WP-084 (or its successor,
  per D0) owns store publishing; commercial terms are tracked privately.
- **Any commercial system: in-app purchases, payment processing, commercial
  licensing integration, a custom storefront.** A later phase, with its own
  architecture and license review: Play Billing can't be linked into the GPL
  runtime. WP-085 is one app with one runtime; no separate runtime install.
- **Downloading executable code** of any kind, including test engine builds.
  Play policy forbids it; test builds use Play's testing tracks.
- **Distributing any game without the rights holder's permission.** Test
  packages are limited per [§Dependencies](#dependencies).
- **A new library UI.** ScummVM's launcher is the v1 library; a TV-styled
  front end is a later WP.
- **D-pad-only pointer control.** Stays the open remote-first item.
- **Upstreaming** the backend changes (separate decision under the
  [fork decision](../reference/why-forked-scummvm.md)).

## Decisions for Jeff

| # | Decision | Recommendation |
|---|---|---|
| D0 | **How this WP relates to WP-084 and the logged "free Google TV app first" decision.** (a) WP-085 comes first and WP-084 becomes the store release of this app; (b) WP-084 ships first as planned and WP-085 follows; (c) WP-085 replaces WP-084 | **Answered 2026-11-26 — (a).** Jeff: "Pipeline first (a)". WP-084 is re-scoped as this app's Google Play release |
| D1 | App identity (tracked privately, not in this public WP) | **Answered 2026-11-26; tracked privately.** The package id is treated as permanent: once published on Play it can't change, and this app may become the shared runtime other apps detect by that id (see [Notes](#notes)) |
| D2 | **Input requirement for a Play release.** Gamepad required (meets TV-GP), keyboard and mouse supported; D-pad required (Copilot's proposal; the D-pad moves ScummVM's pointer today but lacks the fine movement needed to click a button or object, per Jeff on the TCL, 2026-11-26); or mouse required (no TV-quality exemption; risks TV review) | **Answered 2026-11-26.** Jeff: "Gamepad required (Rec)". Gamepad required for Play; keyboard and mouse supported and tested now. The D-pad-only pointer stays out of scope |
| D3 | Where test packages are hosted | **Answered 2026-11-26.** Jeff: "Split, own repo (Rec)". Freely redistributable packages (the BASS freeware, readme intact) go on **GitHub Releases in a dedicated repo**, which keeps game data out of the engine repos; anything licensed goes on **Cloudflare behind Access**. The downloader is host-independent (§Scope 7). WP-085 hosts only BASS, so the Access host isn't built here: it's set up when licensed data first needs it |
| D4 | Whether advanced mode ships in the Play build or only in test builds | **Answered 2026-11-26.** Jeff: "Test builds only (Rec)". Test builds only for v1; revisit after the first Play release |

### Pre-flight answers (2026-11-26)

Put to Jeff at the [pre-flight](../reference/pre-flight-WP-085-2026-11-26.md),
recommendation first. The answers are the option labels he picked.

| # | Question | Jeff's answer |
|---|---|---|
| Q1 | Keeping the package id private on the public fork | "Inject at build time (Rec)". The fork keeps `org.scummvm.scummvm` and ScummVM's name and art as defaults. The real id, label and art come from Gradle properties (`tvAppId`, `tvAppLabel`, `tvAppResDir`) in the build environment's user-level `gradle.properties`, outside every repo, with the values recorded privately. `namespace` is unchanged |
| Q2 | The test-package repo's name | "tv-test-packages (Rec)": `barefootbetters/tv-test-packages`. Created on Jeff's go during Milestone 3 |
| Q3 | Icon and banner for sideloaded test builds | "Placeholders OK (Rec)". The real art is needed only for the Play release |

### Engineering calls (pre-flight, 2026-11-26)

Reasoning and code citations are in the
[pre-flight](../reference/pre-flight-WP-085-2026-11-26.md#engineering-calls-claudes-with-reasoning).

1. **Java download, verify and extract** (§Scope 10's preference), feeding
   ScummVM's own `--add --path=… --recursive --no-exit`. Porting `backends/dlc/`
   would also need a SHA-256 implementation, Android store wiring, a manifest
   adapter and update logic.
2. **D4 by build-type source sets:** the advanced-mode classes are compiled
   into the debug (test) build only, with a stub in release, so the Play build
   holds no advanced-mode code. EC-008 Step 3 checks the release APK with
   `apkanalyzer` and a dex string search.
3. **Packages live in `getFilesDir()/packages/<id>/<version>/`**, staged in
   `packages/.staging/`. App updates keep folders in the data dir, and only
   `assets/` and `doc/` are resynced.

## Dependencies

- Fork worktree `wp-085-tv-app-pipeline` off a freshly fetched
  `origin/scooby-engine` ([wp-lifecycle §5](../reference/wp-lifecycle.md)).
- The Android toolchain from the [smart-TV guide](../reference/scummvm-smart-tv.md#build-our-apk-with-the-terraglyph-engine).
- The TCL 65Q77K over `adb`; a Bluetooth keyboard, mouse and gamepad.
- **Test data, all legally obtained:**
  - *Beneath a Steel Sky*, freeware CD (`bass-cd-1.2.zip`, SHA-256
    `53209b9400eab6fd7fa71518b2f357c8de75cfeaa5ba57024575ab79cc974593`). Its
    license allows free distribution, so it may be a hosted test package.
  - Jeff's own *Showdown in Ghost Town* disc data, for TerraGlyph. Used only
    on Jeff's devices, **never hosted where anyone else can download it**.
- A manifest and package host per D3: a dedicated GitHub repo whose releases
  hold the BASS test package (`barefootbetters/tv-test-packages`, named at
  pre-flight; it's created on Jeff's go, never by a session on its own). Never *Showdown* or any other
  licensed data on GitHub Releases, because they're public.

## Execution

1. Pre-flight: [pre-flight-WP-085-2026-11-26](../reference/pre-flight-WP-085-2026-11-26.md), READY.
2. Milestone 1 → verify on the TCL (EC-008 step 1) → Milestone 2 → verify →
   Milestone 3 → verify → Milestone 4 → verify. Each milestone lands as its
   own commit on the fork branch; a failed verification is fixed before the
   next milestone starts.
3. Write §Result with evidence; open the fork PR.

## Exit criteria

1. [x] D0–D4 answered (2026-11-26; [§Decisions](#decisions-for-jeff)).
2. [ ] Milestone 1: the app installs on the TCL with its own identity, shows
   the library, and launches a game; keyboard, mouse, gamepad and remote
   results recorded.
3. [ ] Milestone 2: at least one import route works on the TCL without a
   computer; the imported game launches, saves and restores (logged). Routes
   that don't work are recorded.
4. [ ] Milestone 3: a test package is listed, downloaded, verified, installed,
   detected, launched and removed on the TCL (logged); a package with a wrong
   SHA-256 is refused (logged).
5. [ ] Milestone 4: an app update keeps games and saves; a game-data update
   installs after verification; an interrupted update leaves the old version
   playable (logged).
6. [ ] No executable code is downloaded by the app (code review note in
   §Result).
7. [ ] Fork PR open with the four milestone commits; §Result written.

## Deliverables

- Fork branch and PR (no game data).
- The manifest format, documented in this repo.
- `pre-flight-WP-085-<date>.md`, EC-008 filled in, §Result.
- Never committed: game data, signing keys, endpoint credentials.

## Notes

- **Evidence discipline.** Every device claim comes from a run that happened
  and was captured (the 2026-11-21 fabrication lesson in
  [DECISIONS](../ai/DECISIONS.md)).
- **Public/private boundary.** No product name, price or Play launch date here,
  per the [2026-11-26 naming decision](../ai/DECISIONS.md#2026-11-26--public-naming-the-packaged-edition-targets-google-tv).
- **What carries over to licensed titles:** all of it. The verified package
  route is how licensed game data could reach a device under a rights holder's
  terms; Play Asset Delivery stays the route for data shipped with the app.
- **This app may become a shared runtime.** A later investigation (the 🔮
  "shared runtime and separate game-data apps" row in
  [WORK_INDEX](WORK_INDEX.md)) looks at games distributed as their own
  data-only apps that hand their data to this app. Nothing in WP-085's scope
  changes for it, but two choices made here should leave it open: a permanent
  package id (D1), and keeping the game-folder access on ScummVM's existing
  `SAFFSTree` path, which can already read a folder another app grants it.
