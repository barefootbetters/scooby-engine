---
layout: default
title: "Cross-Compiling ScummVM for the Raspberry Pi (Legacy)"
---

# Cross-Compiling ScummVM for the Raspberry Pi (Legacy)

This route builds a **32-bit (armhf)** ScummVM on a Linux PC, against libraries
copied off the Pi's SD card. It comes from the ScummVM wiki's
[Compiling ScummVM/RPI](https://wiki.scummvm.org/index.php?title=Compiling_ScummVM/RPI)
page, which was written for Raspbian Buster (2020), and the official toolchain
it uses has an old GCC.

For a Pi 4 or 5, build on the Pi itself. See
[Installing ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md#developer-build-our-fork-from-source).
Only use this page when the Pi is too slow to build on, such as a Pi Zero or
Pi 2.

---

## 1. Toolchain

Clone the official tools and put the cross-compiler on `PATH`:

```bash
git clone https://github.com/raspberrypi/tools.git
export PATH=$PATH:$HOME/tools/arm-bcm2708/arm-linux-gnueabihf/bin
```

To test it, run `arm-linux-gnueabihf-gcc` with no input files. You should get a
"no input files" error.

For a newer GCC, the wiki suggests
[Stefan Profanter's raspi-toolchain](https://github.com/Pro/raspi-toolchain).
It has to be installed in `/opt/cross-pi-gcc`.

## 2. Libraries on the Pi

On the Pi, install the same `-dev` packages as the native build's
[step 1](scummvm-raspberry-pi.md#1-install-the-build-tools-and-libraries). Only
libraries installed there end up in the copy, so a feature whose library is
missing on the Pi is left out of the build.

## 3. Sysroot on the PC

Install `make` and `pkg-config`, then copy `/usr`, `/lib` and `/opt` from the
Pi's SD card. Any folder your user can write to works. This example uses
`/opt/rpi_root`:

```bash
sudo apt install -y make pkg-config
mkdir -p /opt/rpi_root
export RPI_ROOT=/opt/rpi_root
cd <sd-card-mount-point>
cp -R usr lib opt $RPI_ROOT
```

## 4. Fix absolute symlinks

The copy breaks every symlink that points to an absolute path. Repair them with
the `sysroot-relativelinks.py` script, which needs Python 3:

```bash
wget https://raw.githubusercontent.com/riscv/riscv-poky/master/scripts/sysroot-relativelinks.py
python3 ./sysroot-relativelinks.py $RPI_ROOT
```

Then put `$RPI_ROOT` at the front of `PATH`. `configure` looks there for
libcurl's files:

```bash
export PATH=$RPI_ROOT:$PATH
```

## 5. Configure and build

From the ScummVM source folder:

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

`--host=raspberrypi` is the cross-compile target in ScummVM's `configure`. It
sets the `arm-linux-gnueabihf` tuple, links against `$RPI_ROOT`, and always
uses SDL2.

With the old official toolchain, `configure` may not detect FluidSynth.
FluidSynth and MT-32 emulation are CPU-heavy on a Pi anyway, so it's fine to
leave them out.

## 6. Copy to the Pi

Copy the contents of `scummvmDist` to the SD card, for example into
`~/scummvm`, along with your games. `make install` with `--prefix` already put
the themes, translations and engine data files there.

For text-to-speech, install speech-dispatcher on the Pi as described in the
native build's
[text-to-speech step](scummvm-raspberry-pi.md#6-optional-text-to-speech).

---

## Sources

- [ScummVM wiki: Compiling ScummVM/RPI](https://wiki.scummvm.org/index.php?title=Compiling_ScummVM/RPI)
- [Official Raspberry Pi toolchain](https://github.com/raspberrypi/tools)
- [raspi-toolchain by Stefan Profanter](https://github.com/Pro/raspi-toolchain)
- [ScummVM `configure`](https://github.com/scummvm/scummvm/blob/master/configure):
  the `raspberrypi` host definition
