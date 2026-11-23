---
layout: default
title: "Installing ScummVM on a smart TV"
---

# Installing ScummVM on a smart TV

How to run ScummVM on a smart TV itself, with no console, Raspberry Pi or
mini-PC plugged in.

There are two ScummVM builds you could put on a TV, and only one of them plays
the Scooby games:

| Build | Where it comes from | Plays the Scooby games? |
|---|---|---|
| **Our build** | Compiled from our fork, [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm) (branch `scooby-engine`): standard ScummVM plus the TerraGlyph engine | **Yes** |
| **The standard ScummVM app** | Downloaded from [scummvm.org](https://www.scummvm.org/downloads/) or the Play Store | **No.** It plays the games ScummVM itself supports, but it has no TerraGlyph engine |

We don't publish a ready-made TV download of our build yet (the only download is
the [Windows preview](download-and-install.md#download-windows)). On a Google TV
or other Android TV you **compile it yourself as an Android app (APK)** for the
TV's processor, then install it on the TV. That's the main path on this page:
[Build our APK](#build-our-apk-with-the-terraglyph-engine).

> **You supply the games.** This project distributes no game data. You point
> ScummVM at files you're entitled to: your own disc, or a legally obtained copy.

> **Checked 2026-11-22.** The build steps come from our fork's own Android build
> files ([Sources](#sources)), which track ScummVM 2026.4, and were followed end to
> end that day to build an arm64-v8a APK ([build record](#build-record)). ScummVM
> has no official TV support. On Android TV it was never a Play Store TV app, so
> every route here is a sideload. **The APK hasn't been run on a TV yet.** Run the
> [TV smoke test](#tv-smoke-test) the first time.

---

## Which TV do you have?

| TV platform | How to get the Scooby games on it |
|---|---|
| **Google TV / Android TV / Fire TV** | [Build our APK](#build-our-apk-with-the-terraglyph-engine) for the TV's processor and sideload it |
| **LG webOS** | No Scooby build yet. A community webOS package of the standard app exists ([webOS](#lg-webos)) |
| **Samsung Tizen and other browser-only TVs** | No Scooby build. The standard app's web version runs some games ([other TVs](#samsung-tizen-and-other-tvs)) |

---

## Google TV / Android TV / Fire TV

Google TV, Android TV and Fire TV all run Android apps, so one APK built for the
TV's processor installs on any of them.

### Pick the processor type (ABI)

An Android APK is compiled for one processor type. Our build's `configure`
accepts these four:

| `--host=` value | Processor | Use it for |
|---|---|---|
| `android-arm64-v8a` | 64-bit ARM | **Most current TVs**, including the [TCL 65Q77K](#your-tv-the-tcl-65q77k). Start here |
| `android-arm-v7a` | 32-bit ARM | Older or low-end TVs and Fire TV Sticks, or a TV whose Android is 32-bit even on a 64-bit chip |
| `android-x86_64` | 64-bit Intel/AMD | Rare on TVs. Mainly the Android emulator |
| `android-x86` | 32-bit Intel/AMD | Rare on TVs |

If the TV refuses to install the 64-bit APK, or it installs but opens to a white
screen, the TV's Android is probably 32-bit. Rebuild with `android-arm-v7a`. To
check before you build, connect with `adb` ([Prepare the TV](#prepare-the-tv)) and
run `adb shell getprop ro.product.cpu.abilist`. If the list includes
`arm64-v8a`, use the 64-bit build.

### Build our APK (with the TerraGlyph engine)

#### 1. Set up a build machine

The build runs `configure` and `make` in a Unix shell. On Windows, use **WSL 2
with Ubuntu** (`wsl --install -d Ubuntu`) and do every step below inside it.
Linux and macOS work directly. Our `configure` also accepts the NDK's Windows
toolchain, but building from MSYS2 hasn't been tried.

You need:

- **A JDK, 17 or newer.** The Android Gradle Plugin our build uses (9.3.2)
  needs at least Java 17.
- **The Android SDK command-line tools** and, through them, the platform tools,
  the Android 37 platform, and **NDK 23.2.8568313 exactly**. Our `configure`
  compares the NDK version with the one pinned in `dists/android/build.gradle`
  and stops if they differ.
- **Google's [Oboe](https://github.com/google/oboe) audio library, added to the
  NDK.** Our Android audio code includes `oboe/Oboe.h` and links `-loboe`, but
  neither the repo nor the NDK provides it, so `make` stops on that header
  without it. (ScummVM's own release builds use a prebuilt toolchain that already
  has it.) Building it takes about a minute: [step 2](#2-add-oboe-to-the-ndk).
- **`git`, `make`, a C++ compiler for the build machine, `pkg-config`, `cmake`
  and `ninja`.**

On Ubuntu (in WSL), with the SDK command-line tools unzipped into
`~/android-sdk/cmdline-tools/latest/`:

```bash
sudo apt update
sudo apt install -y --no-install-recommends openjdk-17-jdk git make build-essential \
    pkg-config unzip cmake ninja-build

export ANDROID_SDK_ROOT="$HOME/android-sdk"
export ANDROID_NDK_ROOT="$ANDROID_SDK_ROOT/ndk/23.2.8568313"
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" \
    "platform-tools" "platforms;android-37" "ndk;23.2.8568313"
```

The command-line tools come from the "Command line tools only" downloads on
[developer.android.com/studio](https://developer.android.com/studio). Put the two
`export` lines in `~/.bashrc` so later shells keep them. `configure` stops with
"Please set ANDROID_SDK_ROOT" (or `ANDROID_NDK_ROOT`) if either is missing.

Current command-line tools (build 16111833 on 2026-11-22) print a notice that
`sdkmanager` is deprecated in favour of a new `android sdk` command. `sdkmanager`
still works and installs the packages above. It no longer needs a separate
`--licenses` step. If the Android 37 platform doesn't install, Gradle downloads
it during the first build.

#### 2. Add Oboe to the NDK

This builds Oboe as a static arm64-v8a library and copies it into the NDK's
sysroot, where our build looks for it. The 32-bit commands come after it.

```bash
git clone --depth 1 --branch 1.11.0 https://github.com/google/oboe.git ~/oboe
cmake -S ~/oboe -B ~/oboe-build -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake" \
    -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-21 \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF
cmake --build ~/oboe-build

sysroot="$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/sysroot"
mkdir -p "$sysroot/usr/include/oboe"
cp ~/oboe/include/oboe/*.h "$sysroot/usr/include/oboe/"
cp ~/oboe-build/liboboe.a "$sysroot/usr/lib/aarch64-linux-android/"
```

For a 32-bit (`android-arm-v7a`) build, build Oboe a second time for Android
16 and copy it into the 32-bit library folder. Our 32-bit build supports
Android 16 and up, so an Oboe built for Android 21 fails to link with
`undefined symbol: __vsprintf_chk`.

```bash
cmake -S ~/oboe -B ~/oboe-build-v7a -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake" \
    -DANDROID_ABI=armeabi-v7a -DANDROID_PLATFORM=android-16 \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF
cmake --build ~/oboe-build-v7a
cp ~/oboe-build-v7a/liboboe.a "$sysroot/usr/lib/arm-linux-androideabi/"
```

Because it's static, Oboe ends up inside the app. The TV doesn't need anything
extra.

#### 3. Get the source

```bash
git clone https://github.com/barefootbetters/scummvm.git
cd scummvm
git checkout scooby-engine
```

#### 4. Configure

```bash
./configure --host=android-arm64-v8a --disable-all-engines --enable-engine=terraglyph \
    --disable-debug --enable-release
```

Swap the `--host` value for a [different processor](#pick-the-processor-type-abi).
The TerraGlyph engine is off by default, so `--enable-engine=terraglyph` is required.
Check that `configure`'s engine summary lists TerraGlyph before you build. Leaving
out `--disable-all-engines` builds every default engine as well, but see the
next paragraph for why that doesn't get you a full ScummVM.

**This makes a Scooby build, not a full ScummVM.** `configure` looks for about
thirty optional libraries built for Android, and a plain build machine has none
of them: no Ogg Vorbis, FLAC, MP3, JPEG, PNG, FreeType, FluidSynth or SDL_net.
Without them it switches off the engines that need them (26 on 2026-11-22,
including Wintermute, Myst 3, The Longest Journey, Broken Sword 2.5, Nancy Drew
and Thimbleweed Park), and the remaining engines can't play compressed audio or
use TrueType menu fonts. The local web server is left out too. Cloud saves still
work, through Android's own HTTP code.

The Scooby games need none of those libraries: their audio is plain PCM and
their video is Bink, both decoded by ScummVM itself. That's why the command
above builds Scooby only: smaller and faster. Keep the standard ScummVM app for
other games. The
two install side by side ([below](#next-to-the-standard-app-or-instead-of-it)).
ScummVM's own releases get the full feature set from a Docker toolchain that
cross-compiles those libraries
([scummvm/dockerized-bb](https://github.com/scummvm/dockerized-bb)). This page
hasn't used it.

#### 5. Build the APK

```bash
make -j"$(nproc)"
make androiddistdebug
```

The APK is `debug/ScummVM-debug.apk`: about 15 MB for the Scooby-only build
(66 MB with every default engine). The first run downloads Gradle and its
plugins, so it takes a while.

To build the other processor type in the same folder, run `configure` with the
other `--host`, then `make clean` before `make`. Each build overwrites
`debug/ScummVM-debug.apk`, so copy the first APK somewhere else before you start
the second.

The *debug* here is the APK's signing, not the C++ build: Gradle signs it with a
local debug key, so it installs on a TV as it is. That's the right APK for
your own TV.

`make androiddistrelease` makes `release/ScummVM-release-unsigned.apk` instead.
A TV won't install an unsigned APK. Sign it first with your own key (the SDK's
`apksigner`). You only need that to hand the APK to other people.

#### Next to the standard app, or instead of it

The debug APK's app id is **`org.scummvm.scummvm.debug`**: the debug build type
in `dists/android/build.gradle` adds a `.debug` suffix. That's a different app
from the standard ScummVM (`org.scummvm.scummvm`), so both can be installed on
the TV at once, each with its own settings and saves.

The release APK keeps `org.scummvm.scummvm`. Signed with your key, it can't
install over a standard app signed by ScummVM, so uninstall the standard app
first (its settings and saves go with it).

### Prepare the TV

1. **Turn on developer options.** **Settings → System → About**, then click the
   **Android TV OS build** row seven times.
2. **Allow the install.** Either:
   - for `adb` from the build machine: **Settings → System → Developer
     options → USB debugging** (some sets call the network version **Network
     debugging** or **Wireless debugging**), or
   - for a file on the TV: install a file manager such as **X-plore** or
     **Downloader by AFTVnews** from the Play Store, then allow it under
     **Settings → Apps → Security & restrictions → Unknown sources**.

The menu names vary by TV maker and Android version.

### Install it on the TV

From the build machine, on the same network as the TV (the TV's IP address is
under **Settings → Network & Internet**):

```bash
"$ANDROID_SDK_ROOT/platform-tools/adb" connect <tv-ip-address>:5555
"$ANDROID_SDK_ROOT/platform-tools/adb" install -r debug/ScummVM-debug.apk
```

Accept the "Allow debugging?" prompt on the TV the first time. Without `adb`,
copy the APK to a USB stick, or send it with **Send Files to TV**, and open it in
the file manager.

The APK declares a TV launcher entry with its own banner, so it should show in
the TV's apps list like any other TV app. If it doesn't, look under **Settings →
Apps → See all apps**.

### Add your game data

- **USB stick (simplest):** a **FAT32 or exFAT** stick with the disc's
  `\scooby\` folder (or every file on the disc). In ScummVM, choose **Add Game…**
  and pick that folder. Google TV has no file browser of its own, so ScummVM's
  own folder picker on a USB stick is the easy route.

  **Copy the files, not a disc image.** The TerraGlyph engine reads the game's files
  from a plain folder. It can't open an `.iso` (or `.bin`/`.cue`) file, so a
  disc image copied to the stick won't be detected. Unpack it first: on Windows,
  double-click the `.iso` to mount it as a drive, then copy its `scooby` folder
  to the stick. Check that the copy has the 42 `BK.NNN` cutscene files along with
  the files on the [status page](scummvm-wiki-scooby.md#required-game-data-files).

  **Stick size and FAT32.** FAT32 itself allows drives up to 2 TB, but
  File Explorer's Format dialog offers FAT32 only on drives of 32 GB or less,
  which is why bigger sticks usually come as exFAT. Windows 11 Insider builds
  from August 2024 raised the command-line `format` limit to 2 TB, but not every
  Windows install has that change. Where it doesn't, a free tool such as
  [Rufus](https://rufus.ie/) formats a larger drive as FAT32. Any FAT32
  file must be under 4 GB. *Showdown*'s largest file, `TGIFILE.ART`, is 145 MB
  and the whole `\scooby\` folder is about 531 MB, so a 32 GB FAT32 stick is
  plenty. For a larger drive, exFAT has no practical size limit. Google TV sets
  generally read it, but that's not yet checked on the TCL 65Q77K.
- **Over the network:** the standard ScummVM app can run a **local web server**
  (Global Options → Cloud → LAN) for uploading files from a browser. Our APK, as
  built on this page, doesn't include it (no SDL_net). Use a USB stick, or
  [copy the game onto the TV](#keep-the-stick-in-or-copy-the-game-to-the-tv)
  with `adb push`.
- The files the TerraGlyph engine reads are listed on the
  [status page](scummvm-wiki-scooby.md#required-game-data-files).

#### Keep the stick in, or copy the game to the TV

ScummVM doesn't import a game. It reads the art, sound and cutscenes from the
folder you added the whole time you play, so a game added from a USB stick needs
the stick plugged in. Saves and settings are stored inside the app on the TV,
not on the stick, so they survive either way.

To play without the stick, copy the game onto the TV's built-in storage and add
it from there:

1. **Check for room.** The `\scooby\` folder is about 531 MB. Google TV sets have
   fairly small built-in storage, so check **Settings → System → Storage** first.
2. **Copy the folder.** Either:
   - **On the TV:** install a file manager that can copy between folders, such as
     **X-plore** or **File Commander**, from the Play Store. With the stick
     plugged in, copy its `scooby` folder to built-in storage, for example into
     **Download**.
   - **From a PC with `adb`** (set up under [Install it on the TV](#install-it-on-the-tv)):

     ```bash
     adb push scooby /sdcard/Download/scooby
     ```

3. **Add it in ScummVM.** Choose **Add Game…**, go to built-in storage →
   **Download** → `scooby`, and add it. Newer Android versions may ask you to
   allow ScummVM access to the folder the first time. Allow it.
4. **Unplug the stick.** ScummVM now reads the game from the TV.

If you'd added the game from the stick before, remove that launcher entry (select
it, then **Remove Game**) so you don't start the copy that's no longer there.

Not yet tried on a TV. In particular, how ScummVM asks for folder access on the
TCL's Android version is unchecked. If **Add Game…** can't see the Download
folder, play from the stick.

*Showdown in Ghost Town* shows in the launcher normally. *Phantom of the Knight*
is still in development. Turn on **Show games marked as unstable** (Global
Options → Misc) to see it.

If the on-screen touch controls cover the game, turn them off under **Global
Options → Backend**.

### Or: the standard ScummVM app

If you only want the games ScummVM itself supports, skip the build. Download the
standard APK for your processor from
[scummvm.org/downloads](https://www.scummvm.org/downloads/) (`arm64-v8a` or
`armeabi-v7a`), then [prepare the TV](#prepare-the-tv), install it, and add
your games the same way. It won't play the Scooby games.

### Your TV: the TCL 65Q77K

The [TCL 65Q77K](https://www.displayspecifications.com/en/model/8c134688) runs
**Google TV**, so it takes the APK above. Reviews put it on a MediaTek Pentonic
700, a 64-bit chip, so build `android-arm64-v8a` first and fall back to
`android-arm-v7a` if it won't install. `adb shell getprop
ro.product.cpu.abilist` settles it.

The Scooby games are light: 2D art and Bink cutscenes, both decoded by ScummVM.
A TV processor in this class should run them easily. That's an expectation, not
a test result: check it with the smoke test below.

### Build record

The steps above, followed on 2026-11-22. Nothing here has run on a TV yet.

| Item | Result |
|---|---|
| Build machine | Windows 11, WSL 3.0.5 with Ubuntu 26.04.1 LTS (x86_64) |
| Toolchain | OpenJDK 17.0.21, Android command-line tools 16111833, NDK 23.2.8568313 (r23c), Oboe 1.11.0 |
| Source | `barefootbetters/scummvm` branch `scooby-engine`, commit `e52f35c2ffd` (ScummVM 2026.4.1 base) |
| Configure | `--host=android-arm64-v8a --disable-all-engines --enable-engine=scooby --disable-debug --enable-release`. Engine summary: Scooby-Doo (TerraGlyph) only |
| Build time | 41 s for `make` plus `androiddistdebug` on 32 cores, after Gradle's first-run downloads |
| APK | `ScummVM-debug.apk`, 14,738,976 bytes, SHA-256 `f1501a860b3b6d2fb8b926c1cc3bdd59b31fd2a1c6c1707df7ce77b18bc2cf4b` |
| Native code | `lib/arm64-v8a/libscummvm.so` and `libloader.so` only. 64-bit ARM, Android 21+. Oboe and the C++ runtime are linked in; it needs only Android system libraries |
| App | `org.scummvm.scummvm.debug`, version 2026.4.1, target SDK 37, TV launcher entry with banner, touchscreen not required |
| Signature | Android Debug certificate; `apksigner verify` passes |

The 32-bit build, made on 2026-11-23 from the same commit and toolchain (Oboe
built for Android 16 as described in [step 2](#2-add-oboe-to-the-ndk)):

| Item | Result |
|---|---|
| Configure | `--host=android-arm-v7a --disable-all-engines --enable-engine=scooby --disable-debug --enable-release`. Engine summary: Scooby-Doo (TerraGlyph) only |
| Build time | 53 s for `make clean`, `make` and `androiddistdebug` |
| APK | `ScummVM-debug.apk`, 14,537,120 bytes, SHA-256 `59588745bb183bc4cf445f54bb0a2744d1d86035348a89a227b81e4ef9f95607` |
| Native code | `lib/armeabi-v7a/libscummvm.so` and `libloader.so` only. 32-bit ARM with NEON, Android 16+ |
| App | `org.scummvm.scummvm.debug`, version 2026.4.1, target SDK 37 |
| Signature | Android Debug certificate; `apksigner verify` passes |

Both APKs use the same app id, so a TV holds one or the other, not both.

The every-engine build from the same commit was 65,991,765 bytes, with the
optional libraries and 26 engines missing as described in
[step 4](#4-configure).

### TV smoke test

Run this the first time our APK goes on a TV. Each check passes or fails, and TV
support is done only when all of them pass.

| # | Check | Pass when |
|---|---|---|
| 1 | `adb shell getprop ro.product.cpu.abilist` | Lists the ABI you built for |
| 2 | `adb install -r debug/ScummVM-debug.apk` | Prints `Success` |
| 3 | Start ScummVM from **See all apps** | The launcher opens, full screen |
| 4 | **Add Game…** on the USB stick's `\scooby\` folder | Detects *Showdown in Ghost Town* |
| 5 | Start it and play past the intro | Bink video and audio play in sync, without stutter |
| 6 | Use only the remote (or a Bluetooth mouse) | The cursor moves, clicks work, and the ScummVM menu opens |
| 7 | Save, quit ScummVM, start it again, load | The game resumes where it was saved |

Record the TV model, Android version, ABI and results here when it's been run.

---

## LG webOS

LG TVs run webOS, not Android, so an APK doesn't install on them. A community
port, [RF1705/scummvm-webos](https://github.com/RF1705/scummvm-webos), packages
the **standard** app as a webOS `.ipk`: a 32-bit ARM (ARMv7) build on ScummVM's
SDL2 backend, announced on the ScummVM developer list in August 2026 against
ScummVM 2026.3.0. Its author tested it on an LG OLED65B19LA (webOS 6.5.3). It
installs through LG **Developer Mode**, **webOS Dev Manager**, `ares-install`, or
the **webOS Homebrew Channel**. ScummVM itself doesn't need root.

It has no TerraGlyph engine. Because it's an SDL2 build, rebuilding it from our fork
with `--enable-engine=terraglyph` should be possible in principle, but nobody has
tried it. Don't confuse this port with ScummVM's old
[WebOS wiki page](https://wiki.scummvm.org/index.php/WebOS), which is the
long-dead HP/Palm webOS.

> The Legendary Arena ewiki's
> [webOS TV Port](https://ewiki.legendary-arena.com/webos-tv-port/) note covers
> the LG platform in depth (Magic Remote, `appinfo.json`, Developer Mode, the
> store). It's about a different product, a web game, but the LG facts carry
> over.

---

## Samsung Tizen and other TVs

Samsung's old SamsungTV and Tizen ports were dropped, and there's no current
native port. On Tizen and other TVs that only run web apps, the option is
ScummVM's **web (Emscripten) version** of the standard app, opened in the TV's
browser or packaged through the maker's developer mode. It runs demos and
freeware, with weaker file access and speed than a native app, and no Scooby
engine.

---

## Controls on a TV

- The **remote** drives ScummVM's menus with the arrows and OK.
- A **Bluetooth mouse** (or air mouse) is the comfortable way to play
  point-and-click games. A keyboard helps for naming saves. Both pair in the
  TV's Bluetooth settings.
- **Global Options → Keymaps** maps remote buttons to left click, right click,
  skip and the menu. **Game Options → Keymaps** does the same for one game.

The Scooby games are single-player point-and-click, so one pointer is all they
need. Herbs vs. Ailments' ewiki covers TV controllers in its
[smart TV platforms](https://ewiki.herbsvsailments.com/research/smart-tv-platforms/)
note.

---

## Sources

- Our fork's Android build files, branch `scooby-engine` of
  [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm):
  [`configure`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/configure)
  (the four `android-*` hosts, the `ANDROID_SDK_ROOT` / `ANDROID_NDK_ROOT`
  checks, the NDK version check),
  [`backends/platform/android/android.mk`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/backends/platform/android/android.mk)
  (`androiddistdebug`, `androiddistrelease`, the APK names), and
  [`dists/android/build.gradle`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/dists/android/build.gradle)
  (NDK 23.2.8568313, compile SDK 37, Android Gradle Plugin 9.3.2, app id
  `org.scummvm.scummvm`, version 2026.4.1).
- [ScummVM docs: Android](https://docs.scummvm.org/en/latest/other_platforms/android.html):
  installing the standard app, unknown sources, adding games. The ScummVM wiki's
  Android compiling page blocks automated reads, so the build steps above come
  from the build files, not the wiki.
- [ScummVM downloads](https://www.scummvm.org/downloads/): the standard APKs.
- ScummVM tracker and forums on TVs:
  [the dropped Play Store TV listing](https://bugs.scummvm.org/ticket/11932) and
  [64-bit APK install and white-screen reports](https://forums.scummvm.org/viewtopic.php?p=62545).
- [RF1705/scummvm-webos](https://github.com/RF1705/scummvm-webos) and its
  [developer-list announcement](https://lists.scummvm.org/pipermail/scummvm-devel/2026-August/013079.html).
- ScummVM wiki: [WebOS](https://wiki.scummvm.org/index.php/WebOS) (old HP/Palm)
  and [SamsungTV](https://wiki.scummvm.org/index.php/SamsungTV) (dropped).
- This repo: [Download & install](download-and-install.md),
  [Installing ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md),
  [status page](scummvm-wiki-scooby.md),
  [Why the engine is a ScummVM fork](why-forked-scummvm.md).
- [TCL 65Q77K specs](https://www.displayspecifications.com/en/model/8c134688)
  (DisplaySpecifications).
