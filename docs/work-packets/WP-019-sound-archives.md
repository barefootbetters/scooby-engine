---
layout: default
title: "WP-019: Sound Archives through the Mixer"
---

# WP-019: Sound archives through `Audio::Mixer` (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3 (resource loading: audio)
**Depends on:** WP-004 ✅ (audio format), WP-006 ✅ (Phantom's audio is the same), WP-014 ✅ (engine resource pattern)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-019-2026-11-14](../reference/pre-flight-WP-019-2026-11-14.md)

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

1. [ ] Every clip in Showdown (1,165) and Phantom (1,067) reads in the engine
   to the same PCM bytes, by MD5, as `probe_audio.py`'s data offset and
   size give. Format fields match too.
2. [ ] A clip started from the console plays through the mixer. The elapsed
   time logged once a second advances with wall time, and a non-looping
   clip ends at its length.
3. [ ] A malformed archive (bad version, index past the end of the file) is
   rejected with a warning.
4. [ ] Scooby-only build: 0 errors and 0 warnings. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §6](../02-SCUMMVM-INTEGRATION.md#6-audio) implementation
  notes.
- [audio-archives](../formats/audio-archives.md) "Next steps" item 1 marked
  done.
