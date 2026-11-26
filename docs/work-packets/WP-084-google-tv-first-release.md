---
layout: default
title: "WP-084: First Google TV release (Beneath a Steel Sky)"
---

# WP-084: First Google TV release — a standalone build with *Beneath a Steel Sky*

**Status:** 📝 Drafted · ⏸ **Blocked on Gate 0.** No implementation starts
until Revolution Software has confirmed the distribution, or Jeff has decided
to proceed on the freeware license alone ([§Gate 0](#gate-0--distribution-terms-blocking)).
**Phase:** 5 (polish & distribution).
**Depends on:** WP-079 ✅ (the fork's TV build path proven: an APK built,
sideloaded and played on the TCL 65Q77K, per the
[smart-TV guide](../reference/scummvm-smart-tv.md#tv-smoke-test)); Gate 0.
**Unblocks:** the Google Play publishing path a licensed TerraGlyph title will
reuse: account, signing, App Bundle, the install-time asset pack, TV review and
the GPL source release.
**Companion EC:** [EC-007](../execution-checklists/EC-007-google-tv-first-release.md).
**Pre-flight required:** **Yes.** It changes the fork outside
`engines/terraglyph/` for the first time (the Android backend and build
configuration), and it claims a release-readiness posture.
**Targets generation(s):** none. No TerraGlyph engine code changes; the game
runs on ScummVM's Revolution `sky` engine. TerraGlyph is compiled in, dormant,
only if [D2](#decisions-for-jeff) says so.
**Estimated effort:** about 2–3 working days of build and test, plus the
14-day Play closed test (wall-clock, if the developer account is personal).

---

## Goal

Ship one free, complete, playable adventure as a standalone Google TV / Android
TV app built from our ScummVM fork. The app installs from Google Play, starts
straight into *Beneath a Steel Sky* (BASS), plays end to end with a Bluetooth
gamepad, saves and restores, quits cleanly to the TV home screen, and carries
every license notice and a corresponding-source release. **Done means someone
can find the app on their Google TV, install it and play the game without a
computer.**

## Background

- **Why a freeware classic first.** Licensed TerraGlyph titles are gated on
  rights that aren't in hand. The ScummVM freeware classics let the publishing
  path be built and proven now. The candidate comparison (BASS, *Flight of the
  Amazon Queen*, and an earlier candidate) is in the studio's internal research;
  BASS was chosen because Google Play has no BASS edition, its rights holder is
  a single active studio that already ships on ScummVM, the game needs no asset
  clearance or rebuild, and its engine needs no optional library.
- **The license.** BASS's freeware readme (the text Debian records as
  [Beneath-a-Steel-Sky-License](https://metadata.ftp-master.debian.org/changelogs/main/b/beneath-a-steel-sky/stable_copyright)):
  §1 allows distribution "for free on any medium", provided the readme and all
  notices stay intact; §3 bars charging a fee "for the game itself"; §4 allows
  modification if marked; §5 says all game content is © Revolution Software
  Ltd. Its non-binding preamble asks distributors of commercial collections to
  ask first. **So the app is free of charge, the readme ships unchanged, and
  Revolution is asked before release.**
- **What already exists in the fork** (`origin/scooby-engine` `ff490ad9449f`):
  - `engines/sky`: no required library (`configure.engine` deps empty; Vorbis,
    MP3 and FLAC only for compressed variants). Detection knows the freeware
    CD version (v0.0372; `sky.dsk` 72,395,713 or 73,123,264 bytes). Its keymap
    already maps the gamepad: **A** walk/look/talk, **B** use, **Y**
    skip/close, **X** control panel. `dists/engine-data/sky.cpt` ships with
    the build.
  - **Bundled games:** `backends/platform/android/android.mk` copies
    `GAMES_BUNDLE_DIRECTORY` into the APK's `assets/games/`, and
    `OSystem_Android::updateStartSettings` adds them on the first run after
    each version update.
  - **App Bundle with an install-time asset pack:** `make androidbundlerelease`
    runs `gradlew bundleRelease -PsplitAssets`, which puts the assets (themes,
    engine data, bundled games) in the `mainAssets` install-time asset pack.
    `fatbundle.mk` builds every ABI into one bundle, and upstream's
    `build-release.sh` is the reference recipe. **This path is the same Play
    Asset Delivery route the ~531 MB TerraGlyph data will need.**
  - **TV manifest:** leanback launcher intent, banner, `touchscreen` and
    `gamepad` not required, `minSdkVersion 16`, target SDK 37.
  - **Launch arguments:** `ScummVMActivity` passes the launching intent's data
    as a command-line target; with none, ScummVM opens its launcher.
- **The official ScummVM app on Play** ships no game data ("NO GAME DATA FILES
  ARE INCLUDED"), so a TV app with a complete game included is a distinct
  product, which matters for Play's repetitive-content policy.
- **Play rules as of 2026-11-26** (Google's pages): TV apps target API ≥ 34,
  `minSdkVersion` ≤ 31, ship 32- and 64-bit with 16 KB pages (TV-G6, since
  2026-08-01), App Bundle only, Play App Signing, D-pad navigation unless the
  game requires a controller (TV-DP / TV-DK / TV-GP), Back returns home
  (TV-DB), a 320×180 banner containing the app name (TV-BN), a 1280×720 listing
  banner and at least one real TV screenshot, and an Android TV opt-in with
  review. A personal developer account created after 2023-11-13 needs a closed
  test with 12 testers for 14 consecutive days before production.

## Gate 0 — distribution terms (blocking)

Nothing in §Execution starts until one of these is recorded in
[DECISIONS](../ai/DECISIONS.md):

- **(a)** Revolution Software confirms in writing that bundling the unmodified
  freeware CD version in a free Google TV / Android TV app on Google Play is
  acceptable; **or**
- **(b)** Jeff decides to proceed on the freeware license alone (it permits
  free distribution), with the reason recorded.

**Outreach draft** (Jeff's to send, from his own account; nothing is sent by
this WP):

> Subject: *Beneath a Steel Sky* freeware in a free Google TV app
>
> Hello,
>
> I run Barefoot Betters, a small studio that builds on ScummVM. We'd like to
> publish a free Google TV / Android TV app that includes the unmodified
> freeware CD version of *Beneath a Steel Sky*, so people can play it on their
> television with a game controller, without copying files from a computer.
>
> The app would be free, carry your readme and copyright notices unchanged,
> credit Revolution Software prominently, and say plainly that it is not an
> official Revolution release. It runs on our ScummVM build, whose full source
> we publish under the GPL.
>
> The freeware license allows free distribution, but we'd rather ask than
> assume. Are you happy for us to do this? If you'd like any wording, link or
> credit changed, or would rather we didn't, we'll follow your lead.
>
> Thank you for making the game freely available all these years.

## Scope

### In scope

1. **Build configuration** on a fork branch `wp-084-google-tv-first-release`:
   `--enable-engine=sky` (plus `terraglyph` if D2), `--enable-release`,
   both armeabi-v7a and arm64-v8a in one App Bundle, 16 KB-aligned.
2. **App identity:** our own `applicationId`, app name, launcher icon, the
   320×180 TV banner containing the name, and version code, all per
   [D1](#decisions-for-jeff). No "ScummVM" product name; "Powered by ScummVM"
   in the about text.
3. **Bundled game:** the ScummVM freeware download `bass-cd-1.2.zip`
   (66.2 MiB, SHA-256
   `53209b9400eab6fd7fa71518b2f357c8de75cfeaa5ba57024575ab79cc974593`),
   unmodified, with its readme, under `GAMES_BUNDLE_DIRECTORY`.
4. **Direct launch:** on every start, open BASS directly, not the launcher;
   on the first run after an install or update, add the bundled game and then
   start it (today `updateStartSettings` adds games and stops at the launcher).
   Quitting the game exits the app to the TV home screen.
5. **Single-game posture:** no route to ScummVM's launcher in normal use
   (no "Return to launcher", no add-game UI), so the app is one game, not a
   general ScummVM front end.
6. **Controller-first TV input:** declare the app as requiring a gamepad
   (`android.hardware.gamepad` `required="true"`, TV-GP) and verify that every
   function, including ScummVM's control panel and save/load dialogs, works
   from standard gamepad keys (TV-DK), and that Back reaches the TV home
   screen (TV-DB).
7. **Licenses screen:** GPLv3 text, ScummVM's `COPYING`, `COPYRIGHT` and
   `AUTHORS`, `LICENSES/*` as applicable, Oboe's Apache-2.0, the BASS readme
   verbatim, and the source URL.
8. **Corresponding-source release:** a signed tag on the fork for the exact
   commit built, a source archive, `BUILDING.md` (NDK 23.2.8568313, SDK
   platform 37, the exact `configure` line and make target), and checksums,
   published at a permanent URL linked from the Play description and the app.
9. **Device verification** on the TCL 65Q77K (Google TV) per
   [EC-007](../execution-checklists/EC-007-google-tv-first-release.md):
   install from the bundle, first-run add and launch, full playthrough with a
   Bluetooth gamepad, save → quit → relaunch → restore, Back behaviour.
10. **Google Play preparation:** the app record, Play App Signing (our own
    upload key; D4 covers supplying our own app signing key), the store
    listing (description with license and source notices, 1280×720 banner, TV
    screenshots), privacy policy URL, data safety, content rating
    questionnaire, target audience, ads / health / financial declarations, the
    Android TV form-factor opt-in, and a closed test track.
11. **Production release submission** — only on Jeff's explicit go after
    exit criteria 1–10 are met.

### Out of scope

- **Paid distribution, in-app purchases, Play Billing, a storefront or a
  multi-game launcher.** A later WP, after the commercial licensing route is
  settled; Play Billing can't be linked into the GPL runtime.
- **D-pad-only pointer control** (playing with the TV remote alone). The
  remote-first requirement stays open for a later WP; this release declares a
  gamepad required.
- **Any TerraGlyph / Scooby game data** in the app. Gated on rights.
- **Modifying BASS's data** (upscaling, re-encoding, translations). §4 would
  allow it with a notice; not needed for v1.
- **Compressed-audio variants** (MP3/Vorbis/FLAC) and the libraries they need.
- **Other stores** (Amazon Appstore, Samsung, iOS).
- **Upstreaming the backend changes** to `scummvm/scummvm`. Separate decision
  under the [fork decision](../reference/why-forked-scummvm.md).

## Decisions for Jeff

| # | Decision | Recommendation |
|---|---|---|
| D0 | Gate 0: send the outreach, or proceed on the license alone | Send it; wait a reasonable time for a reply |
| D1 | App name, package id, icon and banner (tracked privately; not in this public WP) | — |
| D2 | Compile TerraGlyph in, dormant? | Yes: it proves the exact release build later TerraGlyph titles ship in, at a cost of a few MB |
| D3 | Personal or organization Play developer account | Organization (D-U-N-S) if the studio account is the long-term publisher; a personal account adds the 12-tester / 14-day closed test |
| D4 | Let Google generate the app signing key, or supply our own | Supply our own, kept offline, so builds published elsewhere can share the signature |
| D5 | Target audience / rating stance | 13+ (the App Store rates BASS 13+); outside Play's Families program |

## Dependencies

- Gate 0 recorded; D1–D5 answered.
- Fork worktree `wp-084-google-tv-first-release` off a freshly fetched
  `origin/scooby-engine` ([wp-lifecycle §5](../reference/wp-lifecycle.md)).
- The Android toolchain from the [smart-TV guide](../reference/scummvm-smart-tv.md#build-our-apk-with-the-terraglyph-engine):
  SDK platform 37, NDK 23.2.8568313 exactly, Oboe built for both ABIs.
- `bundletool` to produce installable APKs from the AAB for sideload testing.
- The TCL 65Q77K with `adb` over the network, and a Bluetooth gamepad.
- A Google Play developer account with a payments-free setup (a free app needs
  no payments profile).

## Execution

1. **Pre-flight** against this WP (`pre-flight-WP-084-<date>.md`).
2. **Fetch and verify the game:** download `bass-cd-1.2.zip` from
   downloads.scummvm.org, check the SHA-256 above, unpack to a staging folder
   outside both repos, and confirm `sky.dsk` / `sky.dnr` match a v0.0372 CD
   detection entry and the readme is present. Never commit game data.
3. **Backend change for direct launch** (Android Java/C++ only): default the
   start target to the bundled game when the launching intent carries none;
   sequence the first-run add before the start; hide the launcher route.
   Smallest change that works; each behaviour covered by a test or a logged
   device check.
4. **App identity and manifest:** `applicationId`, name, icon, banner,
   `gamepad` required.
5. **Build:** `configure` for both ABIs, `make androidfatbundlerelease
   GAMES_BUNDLE_DIRECTORY=<staging>` (or the equivalent sequence from
   `build-release.sh`); confirm 16 KB alignment of the arm64 libraries.
6. **Licenses screen and source release** (scope 7–8).
7. **Device run** per EC-007; every claim backed by a log or a screenshot
   captured in the run.
8. **Play preparation** (scope 10); closed test.
9. **Result** written here; production submission only on Jeff's go.

## Exit criteria

1. [ ] Gate 0 recorded in DECISIONS (Revolution's confirmation, or Jeff's
   decision to proceed on the license).
2. [ ] D1–D5 answered.
3. [ ] The AAB builds from the tagged fork commit, contains armeabi-v7a and
   arm64-v8a, and the arm64 libraries are 16 KB-aligned (checked, output
   recorded).
4. [ ] The bundled game is byte-identical to `bass-cd-1.2.zip` (SHA-256
   recorded) and its readme ships unchanged.
5. [ ] On the TCL, a fresh install from the bundle starts BASS directly on the
   first run and on every later run, with no launcher shown (logged).
6. [ ] A full playthrough reaches the end credits using only a Bluetooth
   gamepad (log plus screenshots from the run).
7. [ ] Save from the control panel → quit → relaunch → restore resumes the
   saved position (logged).
8. [ ] Back from the game reaches the TV home screen; quitting exits the app.
9. [ ] The licenses screen shows every text in scope 7 and the source URL.
10. [ ] The corresponding-source release is published at a permanent URL and
    `BUILDING.md` reproduces the AAB's native libraries from the tag.
11. [ ] Play: listing, declarations and Android TV opt-in complete; closed test
    running (and, for a personal account, 12 testers × 14 days met).
12. [ ] Production release submitted on Jeff's explicit go, and the TV review
    outcome recorded.

## Deliverables

- Fork branch and PR with the backend, manifest and build changes (no game
  data).
- The source release (tag, archive, `BUILDING.md`, checksums).
- `pre-flight-WP-084-<date>.md`, this WP's §Result, EC-007 filled in.
- Play listing text and graphics (kept with the studio's brand assets, not in
  this repo, if they carry the private product name).
- Gitignored / never committed: the BASS data, the signing keys, run captures
  containing personal data.

## Notes

- **Evidence discipline.** Every device claim (launch, playthrough, save/load)
  must come from a run that happened and was captured. Earlier closeout work
  had fabricated a live run ([DECISIONS 2026-11-21](../ai/DECISIONS.md)); this
  WP doesn't repeat that.
- **Public/private boundary.** Per the
  [2026-11-26 naming decision](../ai/DECISIONS.md#2026-11-26--public-naming-the-packaged-edition-targets-google-tv),
  this public WP carries no product name, price or Google Play launch date.
  The app is free because the game's license requires it.
- **What carries over to TerraGlyph titles:** the account, signing, App
  Bundle with an install-time asset pack, TV review, direct launch, the
  licenses screen and the source release. **What doesn't:** game-data rights,
  Bink video and TerraGlyph's own input, and the remote-only pointer.
- **Fork maintenance.** This is the fork's first change outside
  `engines/terraglyph/`; keep it small and isolated so upstream merges stay
  clean.
- **Possible re-scope.** [WP-085](WP-085-tv-app-pipeline.md) (drafted
  2026-11-26) plans a multi-game app: library, import, verified test packages,
  updates. If Jeff picks its D0 option (a), this WP becomes the store release
  of that app, and scope items 4–5 (direct launch, single-game posture) and
  the gamepad-only input give way to WP-085's design.
