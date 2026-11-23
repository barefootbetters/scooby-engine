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
| **Our build** | Compiled from our fork, [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm) (branch `scooby-engine`): standard ScummVM plus the Scooby engine | **Yes** |
| **The standard ScummVM app** | Downloaded from [scummvm.org](https://www.scummvm.org/downloads/) or the Play Store | **No.** It plays the games ScummVM itself supports, but it has no Scooby engine |

We don't publish a ready-made TV download of our build yet (the only download is
the [Windows preview](download-and-install.md#download-windows)). On a Google TV
or other Android TV you **compile it yourself as an Android app (APK)** for the
TV's processor, then install it on the TV. That's the main path on this page:
[Build our APK](#build-our-apk-with-the-scooby-engine).

> **You supply the games.** This project distributes no game data. You point
> ScummVM at files you're entitled to: your own disc, or a legally obtained copy.

> **Checked 2026-11-22.** The build steps come from our fork's own Android build
> files ([Sources](#sources)), which track ScummVM 2026.4. ScummVM has no official
> TV support. On Android TV it was never a Play Store TV app, so every route here
> is a sideload. **No build on this page has been tested on a TV yet.** Run the
> [TV smoke test](#tv-smoke-test) the first time.

---

## Which TV do you have?

| TV platform | How to get the Scooby games on it |
|---|---|
| **Google TV / Android TV / Fire TV** | [Build our APK](#build-our-apk-with-the-scooby-engine) for the TV's processor and sideload it |
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

### Build our APK (with the Scooby engine)

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
- **`git`, `make`, a C++ compiler for the build machine, and `pkg-config`.**

On Ubuntu (in WSL), with the SDK command-line tools unzipped into
`~/android-sdk/cmdline-tools/latest/`:

```bash
sudo apt update
sudo apt install -y --no-install-recommends openjdk-17-jdk git make build-essential pkg-config unzip

export ANDROID_SDK_ROOT="$HOME/android-sdk"
export ANDROID_NDK_ROOT="$ANDROID_SDK_ROOT/ndk/23.2.8568313"
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --licenses
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" \
    "platform-tools" "platforms;android-37" "ndk;23.2.8568313"
```

The command-line tools come from the "Command line tools only" downloads on
[developer.android.com/studio](https://developer.android.com/studio). Put the two
`export` lines in `~/.bashrc` so later shells keep them. `configure` stops with
"Please set ANDROID_SDK_ROOT" (or `ANDROID_NDK_ROOT`) if either is missing.

#### 2. Get the source

```bash
git clone https://github.com/barefootbetters/scummvm.git
cd scummvm
git checkout scooby-engine
```

#### 3. Configure

```bash
./configure --host=android-arm64-v8a --enable-engine=scooby --disable-debug --enable-release
```

Swap the `--host` value for a [different processor](#pick-the-processor-type-abi).
The Scooby engine is off by default, so `--enable-engine=scooby` is required.
Check that `configure`'s engine summary lists Scooby before you build. For a
faster, smaller build with only Scooby in it, add `--disable-all-engines` before
`--enable-engine=scooby`.

#### 4. Build the APK

```bash
make -j"$(nproc)"
make androiddistdebug
```

The APK is `debug/ScummVM-debug.apk`. The first run downloads Gradle and its
plugins, so it takes a while.

The *debug* here is the APK's signing, not the C++ build: Gradle signs it with a
local debug key, so it installs on a TV as it is. That's the right APK for
your own TV.

`make androiddistrelease` makes `release/ScummVM-release-unsigned.apk` instead.
A TV won't install an unsigned APK. Sign it first with your own key (the SDK's
`apksigner`). You only need that to hand the APK to other people.

#### Install conflict with the standard app

Our APK uses the same Android app id as the standard ScummVM app
(`org.scummvm.scummvm`), signed with a different key. If the standard app is
already on the TV, Android refuses to install ours over it. Uninstall the
standard app first. Your ScummVM settings and saves go with it.

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

A sideloaded app may not show on the home row. Look under **Settings → Apps →
See all apps**.

### Add your game data

- **USB stick (simplest):** a **FAT32 or exFAT** stick with the disc's
  `\scooby\` folder (or the whole disc). In ScummVM, choose **Add Game…** and
  pick that folder. Google TV has no file browser of its own, so ScummVM's own
  folder picker on a USB stick is the easy route.
- **Over the network:** ScummVM can run a **local web server** (Global Options →
  Cloud → LAN) that lets you upload files from a browser on your phone or PC.
- The files the Scooby engine reads are listed on the
  [status page](scummvm-wiki-scooby.md#required-game-data-files).

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

It has no Scooby engine. Because it's an SDL2 build, rebuilding it from our fork
with `--enable-engine=scooby` should be possible in principle, but nobody has
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
