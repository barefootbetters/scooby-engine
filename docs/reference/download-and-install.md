---
layout: default
title: "Download and install the Scooby engine"
---

# Download and install the Scooby engine

How to get our forked ScummVM — the one with the **Scooby** (TerraGlyph) engine —
built and running on your computer, pointed at your own game discs.

> **Windows:** download the ready-to-run preview — see [Download (Windows)](#download-windows)
> below. **Other platforms:** build from source. Either way, the engine is **not**
> in stock/upstream ScummVM (installing ScummVM from a package will not include
> it); it lives on our fork,
> [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm) (branch
> `scooby-engine`).

> **You supply the games.** This project distributes **no** game data. You need
> your own original *Scooby-Doo* CD-ROM (or a copy of its files). ScummVM reads
> the disc you point it at; nothing here ships copyrighted content.

---

## What you can play

| Title | Game id | Status |
|---|---|---|
| *Scooby-Doo! Showdown in Ghost Town* | `showdown` | **Playable** (`ADGF_TESTING`) — complete start-to-credits; still being polished |
| *Scooby-Doo! Phantom of the Knight* | `phantomknight` | In development (`ADGF_UNSTABLE`) — most rooms ported, not yet complete |
| *Jinx at the Sphinx* · *Case File #1* · *Activity Challenge* | — | Detected but **not** playable (Gen 2/3 archive readers not implemented) |

This is a testing-stage engine, not a finished product — expect rough edges.
For the full picture of what works, see the engine's
[status & limitations page](scummvm-wiki-scooby.md), and for why it lives on a
fork rather than upstream ScummVM, see
[Why the engine is a ScummVM fork](why-forked-scummvm.md). To see what it looks
like running, browse the
[Screenshots gallery](https://github.com/barefootbetters/scooby-engine/wiki/Screenshots)
— every room, captured from our engine.

### Required game-data files

Point ScummVM at the disc's **`\scooby\`** folder (or the disc root). The Gen 1
engine reads `TGIFILE.ART`, `object.ini`, `Scooby.eng`, `Music.dat`, `Sfx.dat`,
`Voice.dat`, the `BK.NNN` cutscenes, and uses `Scooby.exe` for detection only
(it is never executed). The disc's `binkw32.dll` is **not** used — ScummVM
decodes Bink itself. Full per-title file and MD5 details are on the
[status page](scummvm-wiki-scooby.md#required-game-data-files).

---

## Download (Windows)

A ready-to-run **64-bit Windows** preview is published on the fork's releases —
no build tools required. It's portable (unzip and run; SDL2 and the runtime DLLs
are bundled) and ships **no game data** (bring your own disc).

**[⬇ Download the latest Windows preview](https://github.com/barefootbetters/scummvm/releases/latest)**

To run it:

1. Unzip the download anywhere.
2. Run `scummvm.exe`.
3. Click **Add Game…** and choose your disc's `\scooby\` folder (or the disc root).
4. Select *Showdown in Ghost Town* and click **Start**.

Only *Showdown* is playable so far ([what you can play](#what-you-can-play)).
Want to build it yourself, or run it on Linux, macOS or a Raspberry Pi? Use
[Build from source](#build-from-source) below.

---

## Build from source

Three platforms below, plus the **Raspberry Pi**, which has its own detailed
page: [Installing ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md)
(use its [Developer build](scummvm-raspberry-pi.md#developer-build-our-fork-from-source)
section). The Scooby engine is declared **disabled by default**, so every build
below passes `--enable-engine=scooby` explicitly.

### Get the source (all platforms)

```bash
git clone https://github.com/barefootbetters/scummvm.git
cd scummvm
git checkout scooby-engine
```

The `scooby-engine` branch is the fork's integration branch; it tracks upstream
ScummVM (kept current by a periodic merge) plus `engines/scooby/`.

### Windows (MSYS2 / UCRT64)

This is the reference toolchain this project builds and tests on (g++ 16.2.0,
SDL2 2.32.10, GNU Make 4.4.1).

1. Install [MSYS2](https://www.msys2.org/) and open the **UCRT64** shell (not
   the plain "MSYS2" shell — the start-menu entry is *"MSYS2 UCRT64"*).
2. Install the toolchain and SDL2:

   ```bash
   pacman -S --needed git make \
       mingw-w64-ucrt-x86_64-gcc \
       mingw-w64-ucrt-x86_64-SDL2 mingw-w64-ucrt-x86_64-SDL2_net
   ```

   A Scooby-only build needs little beyond SDL2 (its audio is PCM and its video
   is Bink, both handled by ScummVM's built-in decoders). For a full-featured
   build, add the optional media libraries from ScummVM's
   [Windows compiling guide](https://wiki.scummvm.org/index.php/Compiling_ScummVM/MSYS2).
3. From the cloned `scummvm` directory, in the UCRT64 shell:

   ```bash
   ./configure --enable-engine=scooby --disable-debug --enable-release
   make -j$(nproc)
   ```

   To build **only** the Scooby engine (fastest), use
   `./configure --disable-all-engines --enable-engine=scooby`.

The build produces `scummvm.exe` in the build directory.

### Linux (Debian / Ubuntu)

```bash
sudo apt update
sudo apt install -y --no-install-recommends \
    build-essential git pkg-config libsdl2-dev libsdl2-net-dev \
    zlib1g-dev libfreetype6-dev
# optional media/feature libraries (see the Pi page's step 1 for the full list):
#   libogg-dev libvorbis-dev libflac-dev libmad0-dev libpng-dev libtheora-dev ...

./configure --enable-engine=scooby --disable-debug --enable-release
make -j"$(nproc)"
```

The full dependency list and feature notes are in the Raspberry Pi page's
[Install the build tools and libraries](scummvm-raspberry-pi.md#1-install-the-build-tools-and-libraries)
step — the same libraries apply to desktop Linux.

### macOS

Install [Homebrew](https://brew.sh/), then:

```bash
brew install sdl2 sdl2_net freetype
./configure --enable-engine=scooby --disable-debug --enable-release
make -j"$(sysctl -n hw.ncpu)"
```

macOS is less exercised than Windows/Linux for this engine; report anything that
doesn't build. ScummVM's [macOS compiling guide](https://wiki.scummvm.org/index.php/Compiling_ScummVM/macOS)
covers bundling into a `.app` if you want one.

---

## Verify the engine is in your build

Launching ScummVM doesn't prove the engine compiled in. Check it (adjust the path
to your built binary):

```bash
./scummvm --list-engines | grep -i scooby
```

It should print the `scooby` engine line. If it prints nothing, the engine wasn't
built — rerun `./configure` with `--enable-engine=scooby` and confirm its engine
summary lists Scooby.

Then point detection at a game folder:

```bash
./scummvm --path=/path/to/your/showdown/disc --detect
```

It should list the game with its Scooby game id (`showdown` / `phantomknight`).

---

## Run a game

1. Start ScummVM, click **Add Game…**, and choose the folder that holds the
   disc's data (the `\scooby\` directory, or the disc root).
2. ScummVM detects the game and opens its options — click **OK** to add it.
3. Select it and click **Start**.

**Seeing the game in the launcher:** *Showdown* (`ADGF_TESTING`) appears normally.
*Phantom* is still in development (`ADGF_UNSTABLE`) and is hidden unless you enable
**Show games marked as unstable** / testing in ScummVM's **Global Options ▸
Miscellaneous** (older builds: *"Show ScummVM in unstable mode"*). You can always
add either title directly from its disc path.

Settings live in ScummVM's usual `scummvm.ini` (e.g.
`%APPDATA%\ScummVM\scummvm.ini` on Windows, `~/.config/scummvm/scummvm.ini` on
Linux). Saves use ScummVM's standard save system.

---

## Keeping your build current

The fork tracks upstream ScummVM. To pull upstream's latest into a build you
maintain, in the fork checkout:

```bash
git checkout scooby-engine
git pull origin scooby-engine
```

(Maintainers syncing the fork itself with upstream use
[`tools/Update-Fork.ps1`](https://github.com/barefootbetters/scooby-engine/blob/main/tools/Update-Fork.ps1)
in the docs repo.)

---

## Reporting problems

File build or gameplay issues on the fork's tracker:
[barefootbetters/scummvm issues](https://github.com/barefootbetters/scummvm/issues).
Include your OS, how you built it (platform + `configure` flags), the title and
game id, and what you expected vs. what happened. Because this is a fork and not
part of upstream ScummVM, do **not** file Scooby-engine issues on scummvm.org.

---

## Sources

- Fork: [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm) (branch `scooby-engine`).
- [Why the engine is a ScummVM fork](why-forked-scummvm.md) — the fork vs. upstream decision.
- [Scooby engine status & limitations](scummvm-wiki-scooby.md) — supported titles, data files, MD5s, known limits.
- [Screenshots gallery](https://github.com/barefootbetters/scooby-engine/wiki/Screenshots) — every room, captured from our engine running.
- [Installing ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md) — the Pi developer build + controllers.
- ScummVM compiling guides: [MSYS2 (Windows)](https://wiki.scummvm.org/index.php/Compiling_ScummVM/MSYS2),
  [macOS](https://wiki.scummvm.org/index.php/Compiling_ScummVM/macOS),
  [general](https://wiki.scummvm.org/index.php/Compiling_ScummVM).
