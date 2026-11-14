#!/usr/bin/env python3
"""List, verify and extract clips from Gen 1 (Showdown) ``Music.dat`` / ``Sfx.dat`` / ``Voice.dat``.

WP-004 deliverable. The format is documented in
``docs/formats/audio-archives.md``; the layout comes from ``Scooby.exe``
(``audio_SoundFile_ctor`` 0x43C5A0 for the index, ``SoundStream::Open``
0x446010 for the clip). Summary:

* File header: ``u32 version`` (1), ``u32 count``, ``u32 index_offset``.
* Index at ``index_offset``: ``count`` × 68-byte records,
  ``u32 clip_offset`` + ``char[64]`` NUL-terminated name ``<Section>.<Clip>``.
  It ends exactly at end of file. Clips are sector-aligned (2048) from 0x800.
* Clip: a 16-byte header, ``extra`` bytes of lip-sync data, zero padding to
  the next 2048-byte sector, then ``data_size`` bytes of uncompressed PCM
  (``wFormatTag`` 1), little-endian, signed for 16-bit::

      u32 data_size, u32 sample_rate, u8 channels, u8 bits, u8 pan,
      u8 volume (percent), u8 loop flag, u8 lip_fps, u16 extra

  The engine reads the header sector(s), then streams PCM from the next
  sector. The lip-sync block is one byte per frame at ``lip_fps`` frames a
  second.

Outputs (WAV files) go to ``tools/samples/`` by default, which is
gitignored: extracted audio is a copyrighted derivative and is never
committed (see ``tools/samples/README.md``).

Usage (PowerShell):
    py -3 tools/probe_audio.py --list Voice.dat
    py -3 tools/probe_audio.py --verify
    py -3 tools/probe_audio.py --extract Global.Scrappy.Help.Wiggle
"""

from __future__ import annotations

import argparse
import struct
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO / "tools" / "exes" / "showdown"
DEFAULT_OUT = REPO / "tools" / "samples"
FILES = ("Sfx.dat", "Voice.dat", "Music.dat")  # the engine's search order (0x434DC0)
SECTOR = 0x800
RECORD = 68
CLIP_HEADER = 16


@dataclass
class Clip:
    name: str
    offset: int  # absolute offset of the clip header
    slot: int  # bytes up to the next clip (or the index)
    data_size: int
    rate: int
    channels: int
    bits: int
    pan: int
    volume: int
    loop: int
    lip_fps: int
    extra: int

    @property
    def data_offset(self) -> int:
        """PCM starts at the first sector boundary after header + lip-sync (0x446010)."""
        head = CLIP_HEADER + self.extra
        return self.offset + (head + SECTOR - 1) // SECTOR * SECTOR

    @property
    def seconds(self) -> float:
        return self.data_size / (self.rate * self.channels * self.bits // 8)


def read_index(path: Path) -> tuple[bytes, list[Clip]]:
    data = path.read_bytes()
    version, count, index = struct.unpack_from("<III", data, 0)
    if version != 1:
        raise ValueError(f"{path.name}: version {version}, expected 1")
    entries = []
    for i in range(count):
        q = index + RECORD * i
        offset = struct.unpack_from("<I", data, q)[0]
        name = data[q + 4 : q + RECORD].split(b"\0", 1)[0].decode("ascii")
        entries.append((offset, name))
    entries.sort()
    clips = []
    for k, (offset, name) in enumerate(entries):
        end = entries[k + 1][0] if k + 1 < len(entries) else index
        fields = struct.unpack_from("<IIBBBBBBH", data, offset)
        clips.append(Clip(name, offset, end - offset, *fields))
    return data, clips


def verify(paths: list[Path]) -> int:
    """Check every clip header against the rules the engine applies."""
    for path in paths:
        data, clips = read_index(path)
        _, count, index = struct.unpack_from("<III", data, 0)
        if index + RECORD * count != len(data):
            print(f"FAIL {path.name}: index does not end at end of file")
            return 1
        formats: dict[tuple[int, int, int], int] = {}
        pans: dict[int, int] = {}
        ratios: list[float] = []
        lip = near = 0
        for c in clips:
            if c.offset % SECTOR:
                print(f"FAIL {path.name} {c.name}: clip not sector-aligned")
                return 1
            if any(data[c.offset + CLIP_HEADER + c.extra : c.data_offset]):
                print(f"FAIL {path.name} {c.name}: non-zero bytes between header and PCM")
                return 1
            pans[c.pan] = pans.get(c.pan, 0) + 1
            if c.channels not in (1, 2) or c.bits not in (8, 16):
                print(f"FAIL {path.name} {c.name}: {c.channels} ch, {c.bits} bits")
                return 1
            if c.data_size % (c.channels * c.bits // 8):
                print(f"FAIL {path.name} {c.name}: data size not whole samples")
                return 1
            if c.data_offset - c.offset + c.data_size > c.slot:
                print(f"FAIL {path.name} {c.name}: clip overruns its slot")
                return 1
            formats[(c.rate, c.channels, c.bits)] = formats.get((c.rate, c.channels, c.bits), 0) + 1
            if c.bits == 16 and c.data_size >= 40000:
                ratios.append(smoothness(data, c))
            if c.extra:
                lip += 1
                near += abs(c.extra - c.seconds * c.lip_fps) <= 1.5
        fmt = ", ".join(f"{n} x {r} Hz/{ch} ch/{b}-bit" for (r, ch, b), n in sorted(formats.items()))
        print(f"{path.name}: {len(clips)} clips, index ends at EOF; {fmt}; "
              f"PCM starts on the sector after the header and fits its slot; pan values {sorted(pans)}")
        if ratios:
            ratios.sort()
            print(f"  signal check on {len(ratios)} 16-bit clips: median |dx|/|x| {ratios[len(ratios) // 2]:.2f} "
                  f"(noise is about 1.1+); {sum(r < 0.8 for r in ratios)} below 0.8")
        if lip:
            print(f"  {lip} clips carry lip-sync data; {near} have one byte per frame (+/-1.5)")
    return 0


def smoothness(data: bytes, c: Clip) -> float:
    """Mean |sample delta| / mean |sample| over 4,000 frames mid-clip, first channel.

    Band-limited audio read correctly scores well below 1; a wrong byte
    order or a one-byte misalignment turns it into noise (about 1.1 and up).
    """
    frame = c.channels * 2
    start = c.data_offset + (c.data_size // 2) // frame * frame
    n = min(4000, (c.data_offset + c.data_size - start) // frame)
    x = struct.unpack_from(f"<{n * c.channels}h", data, start)[:: c.channels]
    mag = sum(abs(v) for v in x) or 1
    return sum(abs(x[i + 1] - x[i]) for i in range(len(x) - 1)) / mag


def extract(paths: list[Path], name: str, out: Path) -> int:
    for path in paths:
        data, clips = read_index(path)
        for c in clips:
            if c.name == name:
                out.mkdir(parents=True, exist_ok=True)
                dest = out / f"{name}.wav"
                with wave.open(str(dest), "wb") as w:
                    w.setnchannels(c.channels)
                    w.setsampwidth(c.bits // 8)
                    w.setframerate(c.rate)
                    w.writeframes(data[c.data_offset : c.data_offset + c.data_size])
                print(f"wrote {dest} ({path.name}, {c.rate} Hz, {c.channels} ch, {c.bits}-bit, "
                      f"{c.seconds:.2f} s, volume {c.volume}%, loop {c.loop}, lip-sync {c.extra} B)")
                return 0
    print(f"no clip named {name}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="folder holding the .dat files")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--list", metavar="FILE", help="list the clips of one .dat file")
    ap.add_argument("--verify", action="store_true", help="check every clip header in all three files")
    ap.add_argument("--extract", metavar="NAME", help="write one clip as a WAV file")
    a = ap.parse_args()
    paths = [a.dir / f for f in FILES]

    if a.list:
        _, clips = read_index(a.dir / a.list)
        for c in clips:
            print(f"{c.offset:#010x} {c.rate:5d} Hz {c.channels} ch {c.bits:2d}-bit {c.seconds:7.2f} s "
                  f"vol {c.volume:3d} loop {c.loop} lip {c.extra:4d}  {c.name}")
    if a.verify:
        return verify(paths)
    if a.extract:
        return extract(paths, a.extract, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
