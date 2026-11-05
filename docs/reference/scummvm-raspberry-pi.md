---
layout: default
title: "Installing ScummVM on the Raspberry Pi"
---

# Installing ScummVM on the Raspberry Pi

How to get ScummVM running on a Raspberry Pi: install a ready-made package for
playing, or build from source to run our fork with the Scooby engine in it.

> **Checked 2026-11-05.** The current stable ScummVM is **2026.4.0**. Versions
> below come from Flathub, the Snap Store and Debian on that date. The
> scummvm.org pages listed under [Sources](#sources) are the reference. The
> ScummVM wiki's Raspberry Pi pages date from the Raspbian Buster era (2020),
> so this page updates their commands for Raspberry Pi OS Bookworm and Trixie.

---

## Pick a route

| Route | Version you get | Needs | Use it when |
|---|---|---|---|
| [Flatpak (Flathub)](#option-a-flatpak-newest-release) | **2026.4.0** (current) | 64-bit OS (`aarch64`) | You want the newest release with no build |
| [Snap](#option-b-snap) | 2026.2.0 | 64-bit (`arm64`) or 32-bit (`armhf`) OS | You're on a 32-bit OS and want a recent build |
| [Raspberry Pi OS repository (`apt`)](#option-c-the-os-package-apt) | 2.7.0 on Bookworm, 2.9.0 on Trixie | Any Raspberry Pi OS | Simplest install, an older version is fine |
| [Build on the Pi](#option-d-build-from-source-on-the-pi) | Whatever you check out | Any Raspberry Pi OS, time | You need our fork or the Scooby engine |
| [Cross-compile on a PC](#option-e-cross-compile-on-a-pc-legacy) | Whatever you check out | Linux PC, a copy of the Pi's libraries | Legacy 32-bit route from the ScummVM wiki |

scummvm.org's own Pi binaries stopped at 2.7.0 (AppImages for Pi 3, 4 and
400, 2023). They're under "Older versions (unsupported)" on the downloads page,
so use one of the routes above instead.

### First, check which OS you're on

```bash
uname -m                 # aarch64 = 64-bit, armv7l = 32-bit
. /etc/os-release && echo "$VERSION_CODENAME"   # bookworm, trixie, ...
```

The Flatpak needs `aarch64`. On a 32-bit OS, use the Snap, `apt`, or a source
build.

---

## Option A: Flatpak (newest release)

Flathub's ScummVM build is the current release and has an `aarch64` build. It
has no 32-bit ARM build.

```bash
sudo apt update
sudo apt install -y flatpak
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
sudo reboot
```

After the reboot:

```bash
flatpak install -y flathub org.scummvm.ScummVM
flatpak run org.scummvm.ScummVM
```

Command-line arguments go after the `run` command, for example
`flatpak run org.scummvm.ScummVM --list-games`.

Flatpak apps run in a sandbox. ScummVM's docs say to copy games into
`~/Documents` so the app can see them. The current Flathub manifest grants home
directory access, so any folder under `/home/<you>` should work. Keep games
there, not on other mounts, unless you add permissions with
`flatpak override`.

## Option B: Snap

The Snap Store has 2026.2.0 for both `arm64` and `armhf`, so it's the newest
build for a 32-bit OS. It comes with a few freeware games and demos.

```bash
sudo apt update
sudo apt install -y snapd
sudo reboot
```

After the reboot:

```bash
sudo snap install scummvm
scummvm
```

## Option C: The OS package (`apt`)

This is the simplest route, but you get Debian's version: 2.7.0 on Bookworm,
2.9.0 on Trixie. Newer engines and fixes won't be there.

```bash
sudo apt update
sudo apt install -y scummvm
scummvm
```

On the desktop it's also under **Menu > Games > ScummVM**.

---

## Option D: Build from source on the Pi

Use this for our fork, [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm).
A Pi 4 or 5 is fast enough to build natively. Native builds use the OS's own
compiler and libraries, so you don't need the cross-compile setup in
[Option E](#option-e-cross-compile-on-a-pc-legacy).

### 1. Install the build tools and libraries

This is the ScummVM wiki's library list plus the build basics. Each library
turns on a feature or engine, such as FLAC, MP3, Theora video, FluidSynth MIDI,
text-to-speech or cloud saves. `configure` skips any library it can't find.

```bash
sudo apt update
sudo apt install -y --no-install-recommends \
    build-essential git pkg-config \
    libsdl2-dev libsdl2-net-dev \
    liba52-0.7.4-dev libjpeg62-turbo-dev libmpeg2-4-dev \
    libogg-dev libvorbis-dev libflac-dev libmad0-dev \
    libpng-dev libtheora-dev libfaad-dev libfluidsynth-dev \
    libfreetype6-dev libcurl4-openssl-dev libspeechd-dev \
    zlib1g-dev libfribidi-dev libglew-dev
```

If `apt` can't find a package on a newer OS release, drop it and rerun. The
build still works without that feature.

### 2. Get the source

```bash
git clone https://github.com/barefootbetters/scummvm.git
cd scummvm
```

For upstream ScummVM, clone `https://github.com/scummvm/scummvm.git` instead.

### 3. Configure

```bash
mkdir -p "$HOME/scummvm-dist"
./configure --disable-debug --enable-release --prefix="$HOME/scummvm-dist"
```

Once `engines/scooby/` is in the fork (Phase 2), add `--enable-engine=scooby`.
New engines are off by default, per the
[integration contract](../02-SCUMMVM-INTEGRATION.md).

Don't pass `--host=raspberrypi` on a native build. In ScummVM's `configure`,
that host is the cross-compile target. It assumes the 32-bit
`arm-linux-gnueabihf` toolchain and a copied Pi sysroot in `$RPI_ROOT`. A plain
`./configure` detects the Pi's own compiler and SDL2.

**Low memory:** the final link can run out of RAM on smaller Pis. If you use
GNU ld, run this before `./configure` to make the linker use less memory:

```bash
export LDFLAGS="-Wl,--no-keep-memory"
```

### 4. Build and install

```bash
make clean
make -j"$(nproc)"
make install
```

If the build gets killed partway (out of memory), rerun with `make -j2`.
`make install` copies the binary and its data files (themes, translations,
engine data) into `~/scummvm-dist`. Run it with:

```bash
~/scummvm-dist/bin/scummvm
```

### 5. Optional: text-to-speech

ScummVM's text-to-speech uses speech-dispatcher. Install it with a voice
engine, for example eSpeak NG:

```bash
sudo apt install -y --no-install-recommends speech-dispatcher speech-dispatcher-espeak-ng
```

---

## Option E: Cross-compile on a PC (legacy)

This is the ScummVM wiki's route. It builds a **32-bit (armhf)** binary on a
Linux PC, against libraries copied off the Pi's SD card. The wiki wrote it for
Raspbian Buster (2020), and the official toolchain it uses has an old GCC.
Build on the Pi ([Option D](#option-d-build-from-source-on-the-pi)) unless the
Pi is too slow to build on, such as a Pi Zero or Pi 2.

1. **Toolchain.** Clone the official tools and put the cross-compiler on `PATH`:

   ```bash
   git clone https://github.com/raspberrypi/tools.git
   export PATH=$PATH:$HOME/tools/arm-bcm2708/arm-linux-gnueabihf/bin
   ```

   For a newer GCC, the wiki suggests
   [Stefan Profanter's raspi-toolchain](https://github.com/Pro/raspi-toolchain).
   It has to be installed in `/opt/cross-pi-gcc`.

2. **Libraries on the Pi.** On the Pi, install the same `-dev` packages as
   [Option D step 1](#1-install-the-build-tools-and-libraries). Only libraries
   installed there end up in the copy.

3. **Sysroot on the PC.** Install `make` and `pkg-config`, then copy `/usr`,
   `/lib` and `/opt` from the Pi's SD card:

   ```bash
   sudo apt install -y make pkg-config
   mkdir -p /opt/rpi_root
   export RPI_ROOT=/opt/rpi_root
   cd <sd-card-mount-point>
   cp -R usr lib opt $RPI_ROOT
   ```

4. **Fix absolute symlinks.** The copy breaks every symlink that points to an
   absolute path. Repair them with the `sysroot-relativelinks.py` script, which
   needs Python 3:

   ```bash
   wget https://raw.githubusercontent.com/riscv/riscv-poky/master/scripts/sysroot-relativelinks.py
   python3 ./sysroot-relativelinks.py $RPI_ROOT
   export PATH=$RPI_ROOT:$PATH      # configure looks here for libcurl's files
   ```

5. **Configure and build** from the ScummVM source folder:

   ```bash
   mkdir -p ./scummvmDist
   PKG_CONFIG_SYSROOT_DIR=$RPI_ROOT \
   PKG_CONFIG_LIBDIR=$RPI_ROOT/usr/lib/arm-linux-gnueabihf/pkgconfig \
   ./configure --host=raspberrypi \
     --with-sdl-prefix=$RPI_ROOT/usr --with-png-prefix=$RPI_ROOT/usr \
     --disable-debug --enable-release --prefix=$(pwd)/scummvmDist
   make clean
   make -j$(nproc)
   make install
   ```

   With the old official toolchain, `configure` may not detect FluidSynth.
   FluidSynth and MT-32 emulation are CPU-heavy on a Pi anyway, so it's fine to
   leave them out.

6. **Copy to the Pi.** Copy the contents of `scummvmDist` to the SD card, for
   example into `~/scummvm`, along with your games.

---

## Running games

1. Start ScummVM. Click **Add Game...** and choose the folder that holds a
   game's data files.
2. ScummVM detects the game and opens its options. Click **OK** to add it to
   the launcher.
3. To add a whole folder of games at once, use **Mass Add** (hold Shift and
   click **Add Game...**).

Settings are in `~/.config/scummvm/scummvm.ini` for the `apt` and source
builds. The Flatpak keeps its own copy inside `~/.var/app/org.scummvm.ScummVM/`.

### Audio

The wiki's note about bad sound when PulseAudio is installed is from Raspbian
Buster. Bookworm and later use PipeWire by default. If sound is wrong on a
current OS, check the output device in the desktop's volume menu before
changing anything in ScummVM. FluidSynth and MT-32 emulation are the most
CPU-heavy audio options, so switch to AdLib or a different MIDI device if
audio stutters.

---

## Sources

- [ScummVM docs: Installing ScummVM (Linux)](https://docs.scummvm.org/en/latest/use_scummvm/install_computer.html):
  the Snap, Flatpak and `apt` routes. The ScummVM wiki's Pi page points here.
- [ScummVM wiki: Raspberry Pi](https://wiki.scummvm.org/index.php?title=Raspberry_Pi):
  the port's info page (port maintainer: vanfanel).
- [ScummVM wiki: Compiling ScummVM/RPI](https://wiki.scummvm.org/index.php?title=Compiling_ScummVM/RPI):
  the cross-compile walkthrough behind Option E and the library list in Option D.
- [ScummVM downloads](https://www.scummvm.org/downloads/): the current release
  and the older Pi AppImages.
- [ScummVM on Flathub](https://flathub.org/apps/org.scummvm.ScummVM) and
  [ScummVM on the Snap Store](https://snapcraft.io/scummvm).
- [ScummVM `configure`](https://github.com/scummvm/scummvm/blob/master/configure):
  the `raspberrypi` host definition (32-bit tuple, `$RPI_ROOT` sysroot, SDL2).
