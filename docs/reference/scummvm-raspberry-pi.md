---
layout: default
title: "Installing ScummVM on the Raspberry Pi"
---

# Installing ScummVM on the Raspberry Pi

How to get ScummVM onto a Raspberry Pi. There are two different jobs here:

- **Developer build:** compile our fork,
  [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm), so you
  can run and test the Scooby engine on the Pi.
- **User install:** install stock ScummVM from a package, to play games that
  upstream ScummVM already supports.

> **Checked 2026-11-05.** The current stable ScummVM is **2026.4.0**. Package
> versions below come from Flathub, the Snap Store and Debian on that date, and
> will drift. The scummvm.org pages listed under [Sources](#sources) are the
> reference.

---

## Choose an installation method

| You want to... | Use | Notes |
|---|---|---|
| Develop or test the Scooby engine | [Developer build](#developer-build-our-fork-from-source) | **Recommended for this project.** Pi 4 or 5, 64-bit Raspberry Pi OS |
| Play games upstream ScummVM supports | [Flatpak](#flatpak-recommended) | Newest release (2026.4.0). 64-bit OS only |
| Install quickly and an older version is fine | [`apt`](#apt-simplest) | 2.7.0 on Bookworm, 2.9.0 on Trixie |
| Run a recent release on a 32-bit OS | [Snap](#snap-32-bit-os) | 2026.2.0, `arm64` and `armhf` |
| Build for a Pi too slow to compile on | [Cross-compile (legacy)](scummvm-raspberry-pi-cross-compile.md) | 32-bit only, Buster-era toolchain |

Packages install upstream ScummVM, and none of them will ever include the
Scooby engine before it's merged upstream. To run our engine, you need the
developer build.

scummvm.org's own Pi binaries stopped at 2.7.0 (AppImages for Pi 3, 4 and
400, 2023). They're listed under "Older versions (unsupported)" on the
downloads page.

### Check your OS first

```bash
uname -m                 # aarch64 = 64-bit, armv7l = 32-bit
. /etc/os-release && echo "$VERSION_CODENAME"   # bookworm, trixie, ...
```

The developer build and Flatpak both expect `aarch64`. If the Pi prints
`armv7l`, reinstall it with 64-bit Raspberry Pi OS, or use the Snap for a
user install.

---

## Developer build: our fork from source

Build natively on the Pi. A Pi 4 or 5 is fast enough, and a native build uses
the OS's own compiler and libraries, so you skip the sysroot setup that
cross-compiling needs.

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

### 3. Configure

```bash
mkdir -p "$HOME/scummvm-dist"
./configure --enable-engine=scooby --disable-debug --enable-release \
    --prefix="$HOME/scummvm-dist"
```

New engines are off by default, so `--enable-engine=scooby` is required (see
the [integration contract](../02-SCUMMVM-INTEGRATION.md)). Until
`engines/scooby/` is in the fork (Phase 2), leave that flag off.

For debugging on the Pi, drop `--disable-debug --enable-release` to keep debug
symbols.

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
engine data) into `~/scummvm-dist`.

### 5. Verify the Scooby engine is in the build

Launching ScummVM doesn't prove the engine was compiled in. Check it:

```bash
~/scummvm-dist/bin/scummvm --version
~/scummvm-dist/bin/scummvm --list-engines | grep -i scooby
```

The second command should print the `scooby` engine line. If it prints nothing,
the engine wasn't built. Rerun `./configure` with `--enable-engine=scooby` and
check that `configure`'s engine summary lists it.

Then point detection at a game's data folder:

```bash
~/scummvm-dist/bin/scummvm --path=/path/to/showdown --detect
```

It should list the game with its Scooby game id. If it doesn't, either the path
is wrong or the engine's detection tables don't cover that disc yet.

Finally, start it from the build:

```bash
~/scummvm-dist/bin/scummvm
```

### 6. Optional: text-to-speech

ScummVM's text-to-speech uses speech-dispatcher. Install it with a voice
engine, for example eSpeak NG:

```bash
sudo apt install -y --no-install-recommends speech-dispatcher speech-dispatcher-espeak-ng
```

---

## User install: packaged ScummVM

All three of these install upstream ScummVM, which doesn't include the Scooby
engine.

### Flatpak (recommended)

Flathub's build is the current release and has an `aarch64` build. It has no
32-bit ARM build.

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

### `apt` (simplest)

This installs Debian's version, which lags upstream: 2.7.0 on Bookworm, 2.9.0
on Trixie.

```bash
sudo apt update
sudo apt install -y scummvm
scummvm
```

On the desktop it's also under **Menu > Games > ScummVM**.

### Snap (32-bit OS)

The Snap Store has 2026.2.0 for both `arm64` and `armhf`, which makes it the
newest build for a 32-bit OS. It comes with a few freeware games and demos.

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

---

## Game controllers

ScummVM uses SDL2's game controller support, so a pad Linux recognises usually
works with no setup. Get Linux to see the controller first, then tune it in
ScummVM.

### Connect the controller

**USB:** plug it in. It needs no pairing.

**Bluetooth:** use the Bluetooth icon in the desktop's top bar, or pair from a
terminal. Put the controller in pairing mode, then run:

```bash
bluetoothctl
# inside bluetoothctl:
power on
agent on
scan on            # wait for the controller's MAC address to appear
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
scan off
quit
```

`trust` lets the controller reconnect on its own after a reboot.

### Check that Linux sees it

```bash
ls /dev/input/by-id/ | grep -i joystick
sudo apt install -y joystick evtest
jstest /dev/input/js0      # move sticks and press buttons; values should change
```

Each connected pad shows up as its own `js` device (`js0`, `js1`, ...). If one
is missing, Linux hasn't recognised it, so fix that before you touch ScummVM.
Use `evtest` to see the raw button and axis events.

### Set it up in ScummVM

- **Global Options > Control:** pointer speed (how fast the stick moves the
  cursor) and the analog stick dead zone.
- **Global Options > Keymaps:** map pad buttons to actions such as left click,
  right click, skip, the game menu and the global main menu. **Game Options >
  Keymaps** does the same for one game.
- **Choosing a pad:** with more than one connected, `--joystick=NUM` picks
  which one ScummVM uses, for example `scummvm --joystick=1`.

Point-and-click games use one cursor. A pad drives the virtual mouse, and the
other pads stay idle.

---

## Running games

1. Start ScummVM. Click **Add Game...** and choose the folder that holds a
   game's data files.
2. ScummVM detects the game and opens its options. Click **OK** to add it to
   the launcher.
3. To add a whole folder of games at once, use **Mass Add** (hold Shift and
   click **Add Game...**).

Settings are in `~/.config/scummvm/scummvm.ini` for the developer and `apt`
builds. The Flatpak keeps its own copy inside `~/.var/app/org.scummvm.ScummVM/`.

## Audio

The ScummVM wiki warns that installing PulseAudio can cause bad sound, but that
was written for Raspbian Buster. Bookworm and later use PipeWire by default. If
sound is wrong on a current OS, check the output device (HDMI or headphones) in
the desktop's volume menu before changing anything in ScummVM. FluidSynth and
MT-32 emulation are the most CPU-heavy audio options, so switch to AdLib or a
different MIDI device if audio stutters.

## Cross-compiling (legacy)

The ScummVM wiki's PC cross-compile route builds a 32-bit binary against a copy
of the Pi's libraries. It's only worth doing for a Pi too slow to build on. It's
on its own page:
[Cross-Compiling ScummVM for the Raspberry Pi (Legacy)](scummvm-raspberry-pi-cross-compile.md).

---

## Sources

- [ScummVM docs: Installing ScummVM (Linux)](https://docs.scummvm.org/en/latest/use_scummvm/install_computer.html):
  the Snap, Flatpak and `apt` routes. The ScummVM wiki's Pi page points here.
- [ScummVM docs: Command line interface](https://docs.scummvm.org/en/latest/advanced_topics/command_line.html):
  `--list-engines`, `--detect`, `--path` and `--joystick`.
- ScummVM docs: [Keymaps](https://docs.scummvm.org/en/latest/settings/keymaps.html)
  and [Control](https://docs.scummvm.org/en/latest/settings/control.html) settings.
- [ScummVM wiki: Raspberry Pi](https://wiki.scummvm.org/index.php?title=Raspberry_Pi):
  the port's info page (port maintainer: vanfanel).
- [ScummVM wiki: Compiling ScummVM/RPI](https://wiki.scummvm.org/index.php?title=Compiling_ScummVM/RPI):
  the library list in step 1 and the legacy cross-compile route.
- [ScummVM downloads](https://www.scummvm.org/downloads/): the current release
  and the older Pi AppImages.
- [ScummVM on Flathub](https://flathub.org/apps/org.scummvm.ScummVM) and
  [ScummVM on the Snap Store](https://snapcraft.io/scummvm).
- [ScummVM `configure`](https://github.com/scummvm/scummvm/blob/master/configure):
  the `raspberrypi` host definition (32-bit tuple, `$RPI_ROOT` sysroot, SDL2).
