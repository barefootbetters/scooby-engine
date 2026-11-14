---
layout: default
title: "WP-019: Sound Archives through the Mixer"
---

# WP-019: Sound archives through `Audio::Mixer` (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 3 (resource loading: audio)
**Depends on:** WP-004 ✅ (audio format), WP-006 ✅ (Phantom's audio is the same), WP-014 ✅ (engine resource pattern)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-019-2026-11-14](../reference/pre-flight-WP-019-2026-11-14.md)

---

## Result (2026-11-14)

| Exit criterion | Result |
|---|---|
| 1. Every clip matches | ✅ At `audio` level 3 the engine logs each clip's file, name, rate, channels, bits, volume, loop flag, data size and PCM MD5, in name order per file. A reference built on `probe_audio.py`'s index reader and data offsets logs the same lines. The logs are identical: Showdown 1,165 clips (316 / 821 / 28), Phantom 1,067 (282 / 768 / 17), 0 bad. |
| 2. Playback through the mixer | ✅ `start_sound=Back_Alley.350A_1_FRED` played on the speech channel. The mixer's elapsed time reached 1,000, 2,000 and 3,000 ms at one-second wall-clock steps, and the clip ended about 3.93 s after it started; its length is 172,288 bytes ÷ 44,100 = 3.91 s. `Chase.Music` played as looping music and kept advancing 1,000 ms per second. |
| 3. Malformed archive rejected | ✅ A scratch game folder had a copied `Sfx.dat` and hard links to the other files. Version 2, and an index offset past the end of the file, are each rejected with `Sfx.dat: bad header (…)`, and the engine stops with "no game data" without crashing. The cached `Sfx.dat` still matches its SHA-256 in `tools/exes/README.md`. |
| 4. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Fork commit [`ac1b4def76`](https://github.com/barefootbetters/scummvm/commit/ac1b4def76) stages its nine files by name, inside `engines/scooby/`, and is pushed. |

**Deviations:**

- **The console wasn't driven.** Keystrokes from a background process never reached the ScummVM window, with either `SendKeys` or `keybd_event`. So the playback test used the pre-flight's fallback, a `start_sound` config key, and `sound_play` was compiled but not run.
- **Order of work.** WP-018 named the exit transition as next. This WP comes first because the transition plays a voice line.

---

## Goal

Read `Sfx.dat`, `Voice.dat` and `Music.dat` in the fork and play any clip,
by name, through ScummVM's mixer.

## Background

[audio-archives](../formats/audio-archives.md) covers the format; WP-004
decoded and verified it. Each file has:

- a 12-byte header (version 1, clip count, index offset);
- clips on 2,048-byte sectors;
- an index of 68-byte records (`u32` offset, NUL-terminated
  `<Section>.<Clip>` name).

A clip has a 16-byte header: data size, rate, channels, bits, pan, volume,
loop flag, and the lip-sync fps and count. The lip-sync bytes follow, and
the **PCM starts on the next sector**. 16-bit samples are signed
little-endian; the single 8-bit clip is unsigned. The engine looks names up
in `Sfx.dat`, then `Voice.dat`, then `Music.dat` (`0x434DC0`).

This comes before the exit transition (WP-020). That transition, reached
from `0x4024C0` through the game's state object, plays a voice line from the
exit's `scene=` section as the gang walks off, so it needs audio.

## Scope

**In scope (fork, `engines/scooby/` only):**

- `SoundArchive` (`sound_archive.{h,cpp}`).
  - It checks the header and index against the file size and builds a
    case-insensitive name map.
  - Each clip's header is checked: the PCM must fit before the next clip
    or the index.
  - A clip opens as an `Audio::SeekableAudioStream` over its PCM, streamed
    from the file.
- `Sound` (`sound.{h,cpp}`) looks names up in the original's file order and
  plays a clip on the mixer channel for its file:
  - `Sfx.dat` as SFX, `Voice.dat` as speech, `Music.dat` as music;
  - the clip's volume byte as the channel volume;
  - looping when the loop flag is set.
- Console commands: `sound_list [prefix]`, `sound_play <name>`, `sound_stop`.
- Checks:
  - `audio` level 3 reads every clip's PCM and logs an MD5;
  - `audio` level 1 logs the mixer's elapsed time once a second while a clip
    plays.

**Out of scope:**

- Which sounds play when: room music, ambient sound and voice lines, which
  come with the transition (WP-020) and room code.
- Lip sync.
- Pan: it is 0 on every clip.

## Exit criteria

1. [x] Every clip in Showdown (1,165) and Phantom (1,067) reads in the engine
   to the same PCM bytes, by MD5, as `probe_audio.py`'s data offset and
   size give. Format fields match too.
2. [x] A clip started from the console plays through the mixer. The elapsed
   time logged once a second advances with wall time, and a non-looping
   clip ends at its length.
3. [x] A malformed archive (bad version, index past the end of the file) is
   rejected with a warning.
4. [x] Scooby-only build: 0 errors and 0 warnings. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §6](../02-SCUMMVM-INTEGRATION.md#6-audio) implementation
  notes.
- [audio-archives](../formats/audio-archives.md) "Next steps" item 1 marked
  done.
