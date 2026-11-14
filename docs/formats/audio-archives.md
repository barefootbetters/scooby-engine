---
layout: default
title: "Format Spec: Audio Archives"
---

# Format Spec: Audio Archives (`Music.dat` / `Sfx.dat` / `Voice.dat`)

**Status:** Decoded (WP-004, 2026-11-13). All three files are a name-indexed set of clips, and every clip is **uncompressed PCM** with a small header and, for voice, a lip-sync track. Layout traced in `Scooby.exe` and checked on all 1,165 clips.  
**Engine generation:** Gen 1 (Showdown; Phantom unverified)  
**Source disc:** *Scooby-Doo! Showdown in Ghost Town* (2000, The Learning Company)  
**Sample files:** `scooby\Music.dat` (91.7 MB), `scooby\Sfx.dat` (30.7 MB), `scooby\Voice.dat` (103.8 MB) on the Showdown disc  
**Source SHA-256s:** `Music.dat` `43CC40E8…EB1E`, `Sfx.dat` `D6E92447…FDCC`, `Voice.dat` `9DB041E4…630E` (full values in [tools/exes/README §Showdown](../../tools/exes/README.md#showdown-gen-1))  
**Tool:** [`tools/probe_audio.py`](../../tools/probe_audio.py) (`--list`, `--verify`, `--extract`)

**Vision doc reference:** [Project Vision](../01-VISION.md) — Phase 1 work item

---

## Findings

### File layout

```
Offset          Size          Content
--------------  ------------  ------------------------------------------------
0x0000          12            Header: u32 version (1), u32 count, u32 index_offset
0x000C–0x07FF                 Zero
0x0800          var           Clips, each starting on a 2,048-byte sector, ascending
index_offset    68 × count    Index; ends exactly at end of file
```

| File | Clips | Index offset | First clip |
|---|---|---|---|
| `Music.dat` | 28 | `0x05BB9800` | `0x800` |
| `Sfx.dat` | 316 | `0x01EAF800` | `0x800` |
| `Voice.dat` | 821 | `0x067B8800` | `0x800` |

`audio_SoundFile_ctor` (`0x43C5A0`, `GameSoundFile.cpp`) reads the first
2,048 bytes and requires version 1, failing with `Invalid sound data file`
otherwise. It then seeks to `index_offset` and reads the records.

**Correction (WP-001/WP-004, 2026-11-13).** This page used to call the
third header field a "total data size", and the WP-004 body read it as
larger than `Voice.dat` itself. It is the index offset, and two of its
decimal conversions were wrong: `0x01EAF800` is 32,176,128, not 32,178,176;
`0x067B8800` is 108,759,040, not 108,822,528.

### Index records

```
Offset  Size  Type      Field
------  ----  --------  -----
0       4     uint32LE  clip offset in the file
4       64    char[64]  NUL-terminated clip name, <Section>.<Clip>
```

The engine sorts the records by name and finds clips by binary search.
Clips are referenced **by name**, for example `Artie.Chains_A`,
`Back_Alley.350A_1_FRED`, `Chase.Music` or `Global.Scrappy.Help.Wiggle`.
A numeric sound id is the file's base (`0x1000_0000` sfx, `0x2000_0000`
voice, `0x3000_0000` music) plus the clip's index in its name-sorted
table. Lookups search `Sfx.dat`, `Voice.dat` and `Music.dat` in that order
(`0x434DC0`). `object.ini`'s `scrappyid=` values are `Voice.dat` names (see
[scooby-exe](scooby-exe.md#objectini-consumer-wp-001)). On each room load
the engine preloads the `sfx.dat` clips of the `Global` section and of the
room's own section.

### Clip format

`SoundStream::Open` (`0x446010`, labelled `audio_SoundStream_Open`) reads
the clip's first sector and parses a 16-byte header:

```
Offset  Size  Type      Field                     Values in Showdown
------  ----  --------  ------------------------  ------------------------------
0x00    4     uint32LE  data_size (PCM bytes)     whole samples on every clip
0x04    4     uint32LE  sample rate               22050 (1,161 clips), 44100 (4)
0x08    1     uint8     channels                  1 or 2
0x09    1     uint8     bits per sample           16 (1,164 clips), 8 (1)
0x0A    1     uint8     pan (× 100 → SetPan)      0 on every clip
0x0B    1     uint8     volume, percent           80–100
0x0C    1     uint8     loop flag                 1 on 10 music tracks and 3 sfx
0x0D    1     uint8     lip-sync frames/second    12 or 30 when a block is present, else 0
0x0E    2     uint16LE  lip-sync byte count       0 when absent
0x10    var             lip-sync bytes, then zero padding to the next sector
next sector             data_size bytes of PCM
```

The engine builds a `WAVEFORMATEX` with **`wFormatTag = 1` (PCM)**. It
takes the channels from `0x08`, the bits from `0x09` and the rate from
`0x04`, and sets `nBlockAlign = channels × bits / 8`. It then creates a
DirectSound buffer in that format (`0x445550`; the stream thread logs
`Buffer format = %d channels, %d bits, %d`). There is no decoder: the
bytes go to DirectSound as they are. So 16-bit samples are signed
little-endian, and the one 8-bit clip (`Shaggy.Oils.Door`) is unsigned,
following the DirectSound convention; its bytes average about 125. The
engine passes the volume byte to the buffer's `SetVolume` (at full volume
the result is `v × 100 − 10000`) and the pan byte to `SetPan(pan × 100)`.
The flag at `0x0C` sets a bit on the stream. Reading it as looping is an
inference: 10 of the 28 music tracks carry it, along with 3 ambient
sfx such as `Back_Alley.Snakes_Distant`.

**PCM starts on the sector after the header.** The open reads the header
sector, plus more sectors if `16 + lip-sync count` exceeds 2,048, frees
that buffer, and streams from the next file position. On every clip in all
three files, the bytes between the end of the lip-sync block and the next
sector are zero, and `sector + data_size` fits before the next clip. Read
from that sector, the samples are clean audio. Read from just after the
lip-sync block instead, every voice clip with an odd-length block comes out
as noise.

**Lip sync.** `0x442FB0` keeps the block as `(count, fps, bytes)` for the
character code. There is one byte per frame. For 677 of the 706 voice clips
that carry a block, `count` is within 1.5 frames of the clip's duration ×
fps. The values are mouth shapes 0–6, some with the high bits set
(`0x70`–`0x76`, `0x80`–`0x86`). What the high bits do was not traced; that
belongs to the character-animation work. Twelve `Sfx.dat` clips also carry
blocks, for character actions such as `Gummy.Whistle1a`–`3c`.

**Checks** (`py -3 tools/probe_audio.py --verify`). For all 1,165 clips it
confirms:
- the index ends at EOF and every clip is sector-aligned;
- the padding before the PCM is zero, and the PCM fits its slot;
- each clip's data size is whole samples.

It also runs a signal check: mean |Δsample| / mean |sample| at mid-clip.
Read correctly, the median is 0.29–0.33 in each file. Misaligned or
byte-swapped reads give about 1.1 or more, as noise does. Clips scoring
higher are mostly noisy effects (chains, crashes) and near-silence.

**Extraction.** `--extract <name>` writes a WAV (local `tools/samples/`,
gitignored). Checked on four clips:

| Clip | ffprobe | Level |
|---|---|---|
| `Back_Alley.350A_1_FRED` (voice) | `pcm_s16le`, 22050 Hz, mono, 3.91 s | mean −16.8 dB, peak −1.0 dB |
| `Global.Scrappy.Help.Wiggle` (sfx) | `pcm_s16le`, 22050 Hz, mono, 0.97 s | mean −17.2 dB, peak −1.0 dB |
| `Artie.Chains_A` (sfx) | `pcm_s16le`, 22050 Hz, mono, 1.29 s | mean −28.3 dB, peak −4.0 dB |
| `Chase.Music` (music) | `pcm_s16le`, 22050 Hz, stereo, 78.28 s | mean −13.9 dB, peak −0.6 dB |

### ScummVM coverage

No new decoder is needed. ScummVM's raw PCM stream plays these clips
directly: `Audio::makeRawStream` (`audio/decoders/raw.h`) with
`FLAG_16BITS | FLAG_LITTLE_ENDIAN` (plus `FLAG_STEREO`), or
`FLAG_UNSIGNED` for the 8-bit clip. Looping clips wrap in
`Audio::makeLoopingAudioStream`. Volume and pan map to the mixer's channel
volume and balance. Miles Sound System is not involved, so the
`02-SCUMMVM-INTEGRATION.md` §6 licensing flag in WP-004 §Notes does not
apply.

---

## Remaining unknowns

- The meaning of the lip-sync bytes' high bits (`0x70`, `0x80`), and how
  the character code maps shapes 0–6 (up to 8 in `Sfx.dat`) to mouth frames.
- Where in-game dialogue *text* lives, if anywhere. No text sits alongside
  the clips. The names identify the line and speaker
  (`Back_Alley.350A_1_FRED`), but not the words.
- Phantom's `.dat` files: same layout predicted (same engine), not checked.

## Next steps

1. Phase 3: an `Audio` loader that reads the index into a name map and
   opens clips as raw PCM streams from the sector after the header.
2. Lip sync: trace the consumer of the `(count, fps, bytes)` block alongside
   the character actor (`0x4048E0` family) in Phase 4.
3. Run `probe_audio.py --verify --dir <Phantom folder>` when the disc is
   mounted.

## Success condition

Each of `Music.dat`, `Sfx.dat`, `Voice.dat` has its codec named in writing.
At least one clip from one of the three is extracted and plays in an
external player (ffmpeg / VLC). **Met (WP-004, 2026-11-13):** all three
are uncompressed PCM, and clips from all three extract to WAV files that
ffmpeg decodes with normal levels.

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Phase 1, audio archives
- Work packet: [WP-004](../work-packets/WP-004-audio-archive-decode.md)
- ScummVM audio subsystem: `audio/decoders/raw.h` in the ScummVM tree
- Companion specs: [tgifile-art](tgifile-art.md), [scooby-exe](scooby-exe.md)
