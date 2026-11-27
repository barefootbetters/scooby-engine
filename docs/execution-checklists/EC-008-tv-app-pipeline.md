---
layout: default
title: "EC-008: Google TV app pipeline run sheet"
---

# EC-008: Google TV app pipeline — per-milestone device checks

**Paired WP:** [WP-085](../work-packets/WP-085-tv-app-pipeline.md)
**Purpose:** Verify each WP-085 milestone on the TCL 65Q77K before the next one
starts, with evidence. Defects are logged as one-line gaps; fixes go on the WP
branch before moving on.
**Status:** executed 2026-11-26/27. Steps 1, 3 and 4 pass with recorded gaps;
Step 2 is open (no import route without a computer). Results are in
[WP-085 §Result](../work-packets/WP-085-tv-app-pipeline.md#result).

**Evidence rule:** every checked box cites a `logcat` excerpt, a command output
or a screenshot captured during the run. No capture, no check. Jeff's live
confirmations are quoted as his. Quoted output replaces the app's id with
`<app-id>`. Raw captures, which show the TV's address and the id, stay local
(`P:\scooby-engine\wp-085-captures\`).

**How the device was driven:** builds in WSL, and the TV through **Windows**
`adb` (winget platform-tools 37.0.3). WSL runs in NAT mode, where `adb mdns
services` sees nothing, so its `adb` can't find the TV.

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
- [x] Test data staged outside both repos. `Get-FileHash` on the BASS zip:
      `53209B94…C74593`, a match. `P:\scooby-engine\Showdown.iso` is present;
      the copied `Scooby.exe` is `13284543…AF7478`, the WP-079 identity.
      Re-checked 2026-11-26: `platforms` `android-37.0`, NDK `23.2.8568313`,
      armeabi-v7a `liboboe.a` `399a790e…f843dd61`; `getprop
      ro.product.cpu.abilist` = `armeabi-v7a,armeabi`.
- [x] Peripherals (`dumpsys input`, 2026-11-27):
      `Bluetooth 5.1 Keyboard -> KEYBOARD | ALPHAKEY | … | EXTERNAL` and
      `Bluetooth 5.1 Keyboard Mouse -> CURSOR | BATTERY | EXTERNAL`, one
      combo device (Jeff: "the keyboard is combination of mouse pad and
      keyboard - bluetooth"), plus the remote `BT_RC923A_B1`. **No gamepad:**
      the bonded Bluetooth list is the remote and the keyboard only. Jeff
      chose to proceed and record the gamepad as a gap.
- [x] Added at execution: libpng 1.6.59 (from `pnggroup/libpng`, on Jeff's
      go), built static for armeabi-v7a / `android-16` into
      `/opt/build/png-v7a`. Configure: `--with-png-prefix=/opt/build/png-v7a`
      gives `Checking for PNG >= 1.2.8... yes`. Needed by the grid launcher
      (Step 1).

## Step 1 — Milestone 1: app shell (time-box: 1:00)

- [x] Fresh install over `adb`: `adb install -r …` → `Success`;
      `aapt2 dump badging`: `package: name='<app-id>.debug'`,
      `application-label:'<app-label> (debug)'`,
      `leanback-launchable-activity … banner='res/drawable-xhdpi-v4/tvapp_banner.png'`.
      Google TV's Your apps row shows the placeholder icon and the app's name (screenshot `m1-nav-4`; this row uses icons, not banners).
      The same tree built with the properties empty is
      `org.scummvm.scummvm.debug` / "ScummVM (debug)".
- [x] The library opens in the grid view: screenshot `m1-png-launcher-2`
      shows the "Icons per row" slider, and `m1-ours-now` shows the BASS tile
      with its thumbnail. The first build crashed here (`Abort message:
      'ERROR: No PNG support compiled!'`), which was fixed before going on:
      libpng was added, and the grid default now needs `USE_PNG`.
- [x] Each input, pass or gap:
  - **Keyboard: pass.** Typing in the search box works (Jeff, "Typing in
    search"). The F-row sends media keys by default (`getevent`: F5 →
    `KEY_PLAYPAUSE`, Fn+F5 → `KEY_F5`), so in a game it's **Fn+F5** and
    **Ctrl+Fn+F5**. Jeff: "Fn+F5 + save worked".
  - **Touchpad: pointer and click pass, right-click and scroll are a gap.**
    Jeff: "Touchpad: move+click". With two games listed, "right click and
    two-finger scroll still doesn't work".
  - **Gamepad: not tested**, because none was paired. It's required for Play
    (D2), so it's open before WP-084.
  - **Remote: pass.** Jeff: "Remote launches BASS". logcat: `Current activity
    Intent is: scummvm:sky`.

## Step 2 — Milestone 2: import (time-box: 1:30)

- [x] System file picker ("Add game"), **gap: not present.** `cmd package
      query-activities -a android.intent.action.OPEN_DOCUMENT_TREE` lists only
      `com.android.tv.frameworkpackagestubs`, and DocumentsUI isn't installed.
      Jeff, on choosing "Add a new folder": "you dont have an app that can do
      this". logcat: `Warning: resultCode NOT OK for SAF selection!`. USB by
      direct path, **gap:** ScummVM said it "could not find any game in the
      specified directory" (Jeff), and the app gets `ls:
      /storage/A0E2-4288/bass-cd-1.2: Permission denied`.
- [x] Cloud download dialog, **gap, tried with one account only.** The build
      has cloud (`USE_CLOUD`, through Android's HTTP). Connecting Box failed
      at Box's sign-in, "box unexpected system error reference 5253-5020"
      (Jeff). The account is a company Box tenant. A personal account is
      untested.
- [x] `adb push` fallback works. The BASS files were pushed one at a time to
      `Android/data/<app-id>.debug/files/bass-cd-1.2`; a whole-directory push
      from Windows stalled at 76% with no error. **Add Game…** then added it:
      `[sky] path=/storage/emulated/0/Android/data/<app-id>.debug/files/bass-cd-1.2`,
      `description=Beneath a Steel Sky (v0.0372 CD/DOS)`.
- [x] Imported game launches; save, close, reopen and restore pass (Jeff:
      "Fn+F5 + save worked, Restore after reopen"). `saves/SKY-VM.001` was
      written at 10:25. After Quit: `Reloading ScummVM` → `Entering
      scummvm_main` (10:48:57) → `Current activity Intent is: scummvm:sky`
      (10:49:14).
- [ ] **Exit criterion 3, a route that works without a computer: open.**

## Step 3 — Milestone 3: test packages (time-box: 1:30)

- [x] Advanced mode is hidden by default and opens by the gesture: `TVPackages:
      Advanced mode gesture recognized` → `topResumedActivity=…/org.scummvm.scummvm.advanced.PackagesActivity`.
      Release build (D4), SHA-256 `06dd2fe3…1adde`: `apkanalyzer dex packages
      --defined-only` lists `org.scummvm.scummvm`, `.zip` and `.net`, with no
      `.advanced` and no `TestFeatures` class; `PackagesActivity in manifest: 0`;
      `strings | grep -c TVPKG_MANIFEST_URL` → `0`. The debug build shows 23
      advanced classes and `1`. **Gap:** the gesture, as finally changed to up,
      down, up, down, left, right, left, right, opens from the remote's own key
      codes injected over `adb`, but Jeff's entries on the TCL remote didn't
      register. `getevent` shows the remote reports each press twice.
- [x] Manifest fetched over HTTPS; packages listed: `Manifest loaded from
      github.com: 5 package(s)`.
- [x] BASS package from GitHub Releases: `Downloading bass-cd 1.2 from
      github.com` → `Verified bass-cd 1.2: SHA-256 53209b94…c74593, 69377781
      bytes` → `Extracted 4 file(s) to packages/bass-cd/1.2` → `Adding … through
      ScummVM's --add --recursive` → `Installed bass-cd 1.2`, with
      `[sky] path=/data/user/0/<app-id>.debug/files/packages/bass-cd/1.2/bass-cd-1.2`.
      Launched: `Launching target sky` → `Current activity Intent is:
      scummvm:sky`.
- [x] Host independence: after loading `manifest-mirror.json` (manifest from
      `github.com`), `Downloading bass-cd 1.2 from downloads.scummvm.org` →
      `Verified … 69377781 bytes` → `Installed bass-cd 1.2`. Same app build.
- [x] Wrong SHA-256 refused: `REFUSED neg-wrong-hash 1: SHA-256 0d1c9c75…c1d220
      doesn't match the manifest's 0d1c9c75…c1d221`. Also refused: `REFUSED
      neg-zip-slip 1: zip entry rejected: Invalid zip entry path:
      ../../escaped.txt`, `REFUSED neg-elf 1: entry "elf/game.dat" is an ELF
      executable`, and `REFUSED neg-so 1: entry "so/libgame.so" is executable
      code (.so)`. Afterwards, `find . -name escaped.txt -o -name game.dat -o
      -name libgame.so` is empty, and so is `.staging`. The app's own zip-slip
      check (Android 14 pre-empts it on the TV) was run on a desktop JVM
      against the same zips: `REFUSED neg-zip-slip.zip: entry
      "../../escaped.txt" points outside the package folder`, `escaped.txt
      written outside: false`.
- [x] Remove: `Removed target sky from the library (its saves are kept)` →
      `Removed bass-cd`. Then `scummvm.ini` has only `[scummvm]`, `packages/`
      holds only `installed.json` and `store.log`, and `saves/` is unchanged
      (`SKY-VM.001` 12902 bytes, 10:52, before and after).
- [x] Diagnostics: `Engine: 2026.4.1git`, the app version, `Device: TCL Smart TV
      Pro, Android 14 (SDK 34)`, and `bass-cd 1.2 sha256 53209b94… detected:
      target sky, engine sky, game sky, "Beneath a Steel Sky (v0.0372
      CD/DOS)"`, plus the store log. Export: this TV has no share target, so
      the app says so and saves `tv-packages-diagnostics.txt`, which was
      pulled with `adb pull` (3,522 bytes).

## Step 4 — Milestone 4: updates (time-box: 1:30)

- [x] Newer build over the old one: `versionCode=26041000` → `26041001`
      (`versionName=2026.4.1-wp085.2`), `adb install -r` → `Success`. A
      snapshot of the library, `installed.json`, the package files and the
      saves, taken before the update and after its first launch: `identical
      after update + first launch: True`. Then `Current activity Intent is:
      scummvm:sky`.
- [x] Manifest bumps the BASS version: the screen shows `installed 1.2, update
      available`. Then `Downloading bass-cd 1.2.1` → `Verified bass-cd 1.2.1:
      SHA-256 1576aae9…c23197, 69391078 bytes` → `Extracted 5 file(s) to
      packages/bass-cd/1.2.1` → `Switched target sky to
      packages/bass-cd/1.2.1/bass-cd-1.2` → `Removed the old version bass-cd
      1.2` → `Installed bass-cd 1.2.1`. The saves are unchanged, and
      `scummvm.log`: `Found BASS version v0.0372` after the switch.
- [x] Interrupted update: `am force-stop` 1.5 s into the 1.2.1 download, with
      `packages/.staging/bass-cd-1.2.1.zip` at 21,032,640 of 69,391,078 bytes.
      The only difference from the pre-update snapshot is that partial file.
      Relaunched, BASS 1.2 plays (`Current activity Intent is: scummvm:sky`).
      Reopening the advanced mode removed the partial file, and the snapshot
      is identical again. This was a killed app, not "network off": `adb`
      runs over the same network.
- [x] *Showdown* (TerraGlyph) by a non-public route: copied from Jeff's ISO
      (mounted read-only) and pushed over `adb` to the app's own folder, then
      added by Jeff: `[showdown-win] engineid=terraglyph gameid=showdown
      description=Scooby-Doo! Showdown in Ghost Town (Windows/English)`.
      `scummvm.log`: `Running Scooby-Doo! Showdown in Ghost Town
      (Windows/English)` (14:24 and 14:36). Saves `showdown-win.001` and
      `.002`. Jeff: "Showdown added+plays", "Showdown save+load".

## Definition of done

All step outcomes are recorded with captures. WP-085 exit criteria 2 and 4–7
are met; **criterion 3 is open** (Step 2). §Result is written and WORK_INDEX
updated. The WP stays 🚧 until an import route works on the TV without a
computer.

## Out-of-scope captures

- A TV-styled library: not built; ScummVM's launcher is the v1 library.
- A D-pad fine-pointer mode: not built; the remote stays coarse.
- Play listing work and release signing: WP-084.
- Billing: not touched.
- Found during the run: ScummVM's on-screen keyboard opens by itself at
  launcher start on the TV.
- Found during the run: the smart-TV guide needs a libpng step and the
  Windows-`adb` note.
