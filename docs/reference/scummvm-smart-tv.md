---
layout: default
title: "Installing ScummVM on a smart TV"
---

# Installing ScummVM on a smart TV

How to get ScummVM running on a smart TV — no console, Raspberry Pi, or mini-PC
attached. As with the [Raspberry Pi page](scummvm-raspberry-pi.md), there are two
different jobs here, and the difference decides what you can play:

- **Play the Scooby games.** The Scooby (TerraGlyph) engine lives only on our
  fork, [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm).
  **No TV build of the fork is published** — only a Windows preview is
  ([Download & install](download-and-install.md#download-windows)) — so playing
  the Scooby titles *directly on a TV* means building the fork's Android package
  yourself, which is advanced and untested here. See
  [Playing the Scooby games on a TV, honestly](#playing-the-scooby-games-on-a-tv-honestly).
- **Play games upstream ScummVM already supports.** Every ready-made TV route
  below — the official Android/Google TV APK, the community LG webOS package, the
  web build — installs **upstream** ScummVM. That plays the ~325 games upstream
  supports, on the screen already under your television. It does **not** include
  the Scooby engine.

> **The Scooby engine is not in any store or package build.** Store, package, and
> sideloaded APK builds are all upstream ScummVM, and none will include the
> Scooby engine before it is merged upstream (the engine is distributed as a
> [fork](why-forked-scummvm.md), not upstreamed). Installing ScummVM on your TV
> from the steps below gets you *upstream* ScummVM. For the Scooby-Doo titles,
> read [the honest section](#playing-the-scooby-games-on-a-tv-honestly) first.

> **You supply the games.** This project distributes **no** game data, and
> neither does ScummVM. You point ScummVM at files you are entitled to — your own
> disc, or a legally obtained copy.

> **Checked 2026-11-22.** The current stable ScummVM is **2026.4.0**. ScummVM has
> no *official* TV support: on Android TV it was never a Play Store category
> (Google's policy blocks APK-packaged apps that declare TV support), so every
> route here is a sideload or a community build. Details drift — the pages under
> [Sources](#sources) are the reference.

---

## Which TV do you have?

| TV platform | How ScummVM gets on it | Plays the Scooby games? |
|---|---|---|
| **Google TV / Android TV / Fire TV** | Sideload the official Android APK ([steps below](#google-tv--android-tv--fire-tv)) | **No** — upstream games only. [Scooby needs the fork](#playing-the-scooby-games-on-a-tv-honestly) |
| **LG webOS** | A community native `.ipk` ([webOS](#lg-webos-community-native-port)) | No — upstream games only |
| **Samsung Tizen** | No maintained native port; a web (Emscripten) build or community sideload ([other TVs](#samsung-tizen-and-other-chromium-tvs)) | No — upstream games only, and limited |
| **Other Chromium-based TVs** | The upstream web/Emscripten build, packaged or hosted | No — upstream games only, and limited |

The most common and best-supported route is the **Android** one, which is also
the one that fits a modern **Google TV** set like the TCL below.

---

## Google TV / Android TV / Fire TV

This is the main route, and the one for the operator's own set
([the TCL 65Q77K](#your-tv-the-tcl-65q77k), a Google TV). ScummVM has an Android
backend and publishes Android APKs; Google TV, Android TV and Fire TV all run
Android, so the same APK sideloads onto any of them. Remember the ceiling: this
is **upstream** ScummVM — great for the hundreds of games upstream supports, but
it does not contain the Scooby engine.

### 1. Enable developer options

On the TV: **Settings → System → About** and click the build row (**"Android TV
OS build"** or similar) seven times, until it says you are a developer.

### 2. Allow installs from your sideload helper

Install a helper from the Play Store first — **Downloader by AFTVnews** (fetch an
APK by URL) or a file manager such as **X-plore** / **File Commander**. Then
**Settings → Apps → Security & restrictions → Unknown sources** (wording varies)
and enable it **for that helper**.

### 3. Get the right APK

Download the official APK from ScummVM's downloads page and **match it to the
TV's processor** — this is the step people get wrong:

- **64-bit TVs (most 2023+ Google TV sets):** try **`arm64-v8a`** first.
- **Older / 32-bit TVs, or if the 64-bit build misbehaves:** use **`armeabi-v7a`**
  (the "32-bit ARM" build). The ScummVM team recommends it for older 32-bit TVs
  and has run it on a Fire TV Stick.

Known gotcha from the ScummVM forums: on some sets the `arm64-v8a` APK refuses to
install, or installs but shows a **white screen** on launch. If that happens,
uninstall and sideload the `armeabi-v7a` build instead.

[⬇ ScummVM downloads](https://www.scummvm.org/downloads/) ·
[ScummVM Android docs](https://docs.scummvm.org/en/latest/other_platforms/android.html)

### 4. Get the APK onto the TV

Any of:

- **Downloader:** type the APK URL and let it download on the TV.
- **Send Files to TV:** push the APK from a phone on the same Wi-Fi.
- **USB stick:** copy the APK on a computer, open it with the TV's file manager.
- **ADB over Wi-Fi:** from a computer, `adb connect <tv-ip>` then `adb install
  scummvm.apk`.

### 5. Install and find it

Open the APK with your helper and install. A sideloaded app often lands under
**Settings → Apps → See all apps** rather than the main home row, so look there if
it is not on the home screen.

### 6. Add your game data

- **USB drive (simplest):** a **FAT32 or exFAT** stick with each game in its own
  folder; point ScummVM at it with **Add Game…**. Note Google TV ships **no
  built-in file browser**, which is exactly why a USB stick (navigated inside
  ScummVM's own file picker) is the path of least resistance.
- **Cloud / web transfer:** ScummVM can also pull from cloud storage (Google
  Drive, etc.) or run a **local web server** so you upload files from a browser on
  your phone or PC.
- Saves and config stay in the app's own storage.

If the on-screen touch control gets in the way of the remote, turn it off under
**Global Options → Backend**.

### Your TV: the TCL 65Q77K

The [TCL 65Q77K](https://www.displayspecifications.com/en/model/8c134688) runs
**Google TV** (Android-based), so the Android steps above apply directly — no
custom port, no external box. Reviews report a **MediaTek Pentonic 700**, a
64-bit SoC, so start with the **`arm64-v8a`** APK and fall back to
**`armeabi-v7a`** if it will not install or shows a white screen (step 3).

A mid-range TV SoC like this runs classic 2D point-and-click games (Monkey
Island, Broken Sword, and the like) comfortably. Heavier OpenGL-era engines are
more variable — try a title and see. The Scooby games themselves are light (2D
art plus Bink cutscenes), so hardware is not the constraint for them —
[availability of a TV build is](#playing-the-scooby-games-on-a-tv-honestly).

---

## LG webOS: community native port

LG TVs run webOS, not Android, so the Android APK does not apply. A
**community** native port exists:
**[RF1705/scummvm-webos](https://github.com/RF1705/scummvm-webos)** — an ARMv7
SDL2 build packaged as a webOS `.ipk`, announced on the ScummVM developer list in
August 2026 (tagged against stable ScummVM 2026.3.0; the author reports testing
on an LG OLED65B19LA on webOS 6.5.3). It installs through **LG Developer Mode**,
the **webOS Dev Manager**, `ares-install`, or the **webOS Homebrew Channel** — no
root required for ScummVM itself.

Caveats: it is community-maintained, not an official ScummVM build, and it is —
again — **upstream** ScummVM, so no Scooby engine. Do not confuse it with
ScummVM's old [WebOS wiki page](https://wiki.scummvm.org/index.php/WebOS), which
covers the long-unmaintained HP/Palm webOS (version 1.7.0), a different thing
entirely.

> A separate, deeper study of shipping *a web app* to LG webOS — Seller Lounge
> policy, 5-way navigation, hosted vs packaged — lives in the Legendary Arena
> ewiki's
> [webOS TV Port](https://ewiki.legendary-arena.com/webos-tv-port/) note. It is
> about a different product (a card-game web client), but the webOS platform
> facts (Magic Remote, `appinfo.json`, the `.ipk` model, Developer Mode) transfer.

---

## Samsung Tizen and other Chromium TVs

Samsung's older native ports (the pre-Tizen SamsungTV port, and Bada/Tizen
builds) were **dropped** and are unmaintained. There is no current native Tizen
port. The practical options on Tizen and on other Chromium-based smart TVs are:

- **The upstream web (Emscripten) build**, packaged as a Tizen `.wgt` via
  Developer Mode, or hosted and opened in the TV's browser. It runs demos and
  freeware well; file access and performance are weaker than a native build.
- Sideloading via the vendor's Developer Mode where the platform allows it.

All of these are upstream ScummVM.

---

## Controls on a TV

- The **stock remote** drives ScummVM's menus with the D-pad and OK.
- A **Bluetooth mouse** (or air-mouse) makes point-and-click games genuinely
  comfortable; an optional keyboard speeds up naming saves. Both pair through the
  TV's own Bluetooth settings.
- ScummVM's **keymapper** (Global Options → Keymaps) assigns remote buttons to
  actions (left click, right click, menu, skip). Per-game maps live under Game
  Options → Keymaps.

Herbs vs. Ailments' ewiki covers the controller side of smart-TV play in more
depth in its
[smart TV platforms](https://ewiki.herbsvsailments.com/research/smart-tv-platforms/)
note; the Scooby games are single-player point-and-click, so one pointer (remote
or mouse) is all you need.

---

## Playing the Scooby games on a TV, honestly

Everything above installs **upstream** ScummVM. The Scooby-Doo titles need our
[fork](why-forked-scummvm.md), and **no TV build of the fork is published** — the
only ready-made binary is the [Windows preview](download-and-install.md#download-windows).
So, to actually play *Showdown in Ghost Town* or *Phantom of the Knight* on a
television today, the realistic routes are:

1. **A small device on the TV's HDMI.** A Raspberry Pi running the fork is the
   documented, tested path — it just happens to sit behind the TV rather than
   inside it. See [Installing ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md).
   (A Windows mini-PC or laptop on HDMI works the same way, with the
   [Windows preview](download-and-install.md#download-windows).)
2. **Build the fork's Android APK yourself (advanced, untested here).** ScummVM
   has an Android backend, so the fork *can* be cross-compiled into an APK with
   the Android NDK and `--enable-engine=scooby`, then sideloaded by the
   [Android steps above](#google-tv--android-tv--fire-tv). This project publishes
   no such build and has not tested one; treat it as a build experiment, and
   report results on the [fork's issues](https://github.com/barefootbetters/scummvm/issues).
   ScummVM's [Android build guide](https://wiki.scummvm.org/index.php/Compiling_ScummVM/Android)
   is the starting point.

This matches the project's [Layer 1 posture](distribution-and-licensing-strategy.md):
"bring your own disc," no license required. A one-tap "buy it, play it on the TV"
install is a Layer 2 (licensed-storefront) goal, not something that exists today.
When a TV build of the fork does get published, it belongs in this section.

---

## Sources

- [ScummVM downloads](https://www.scummvm.org/downloads/) — the current release
  (2026.4.0) and the per-architecture Android APKs.
- [ScummVM docs: Android](https://docs.scummvm.org/en/latest/other_platforms/android.html)
  — Play Store vs. manual APK, unknown-source installs, adding game data.
- [ScummVM wiki: Android](https://wiki.scummvm.org/index.php/Android) — the
  Android port's info page.
- ScummVM forums & tracker on TV use: the
  [TV-support policy removal](https://bugs.scummvm.org/ticket/11932) (Play Store
  TV category dropped in 2.7.1), the
  [arm64 vs armv7a / white-screen reports](https://forums.scummvm.org/viewtopic.php?p=62545),
  and the "not much tested on TV" / no-file-browser notes.
- [RF1705/scummvm-webos](https://github.com/RF1705/scummvm-webos) and its
  [developer-list announcement](https://lists.scummvm.org/pipermail/scummvm-devel/2026-August/013079.html)
  — the community LG webOS `.ipk` (ScummVM 2026.3.0, ARMv7/SDL2, tested on an LG
  OLED on webOS 6.5.3).
- [ScummVM wiki: WebOS](https://wiki.scummvm.org/index.php/WebOS) (old HP/Palm,
  unmaintained) and [SamsungTV](https://wiki.scummvm.org/index.php/SamsungTV)
  (dropped) — the historical ports, for contrast.
- [ScummVM wiki: Compiling ScummVM/Android](https://wiki.scummvm.org/index.php/Compiling_ScummVM/Android)
  — the NDK build route for a from-source fork APK.
- This repo: [Download & install](download-and-install.md),
  [Installing ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md),
  [Why the engine is a ScummVM fork](why-forked-scummvm.md),
  [Distribution & licensing strategy](distribution-and-licensing-strategy.md).
- [Herbs vs. Ailments ewiki: smart TV platforms](https://ewiki.herbsvsailments.com/research/smart-tv-platforms/)
  — sibling-project notes on smart-TV controllers and the browser path.
- [TCL 65Q77K specs](https://www.displayspecifications.com/en/model/8c134688)
  (DisplaySpecifications) — the operator's Google TV set.
