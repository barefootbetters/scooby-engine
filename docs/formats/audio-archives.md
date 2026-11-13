---
layout: default
title: "Format Spec: Audio Archives"
---

# Format Spec: Audio Archives (`Music.dat` / `Sfx.dat` / `Voice.dat`)

**Status:** Header and index layout decoded (index from the WP-001 `Scooby.exe` trace, 2026-11-13). Codec unresolved.  
**Source disc:** *Scooby-Doo! Showdown in Ghost Town* (2000, The Learning Company)  
**Sample files:** `scooby\Music.dat` (91.7 MB), `scooby\Sfx.dat` (30.7 MB), `scooby\Voice.dat` (103.8 MB) on the Showdown disc

**Vision doc reference:** [Project Vision](../01-VISION.md) — Phase 1 work item

For Phase 1, codec identification is sufficient. Full decode integration
can defer to Phase 3 if ScummVM already supports the identified codec.

---

## Findings

### Shared header structure

All three files open with the same three-field 12-byte header:

```
Offset  Size  Type      Notes
------  ----  --------  -----
0x00       4  uint32LE  Version — always 1
0x04       4  uint32LE  Entry count (see table below)
0x08       4  uint32LE  Total data size in bytes (≈ file size; exact match TBD)
```

Confirmed values:

| File       | File size (bytes) | Entry count | Data size field  |
|------------|-------------------|-------------|------------------|
| Music.dat  | 96,182,128        | 28          | 0x05BB9800 (96,180,224) |
| Sfx.dat    | 32,197,616        | 316         | 0x01EAF800 (32,178,176) |
| Voice.dat  | 108,814,868       | 821         | 0x067B8800 (108,822,528) |

The data-size field is within ~20 KB of the actual file size — likely the
payload region size, not counting the header + index.

Entry counts are plausible:
- **28 music tracks** — typical for a full adventure game soundtrack.
- **316 sound effects** — large but credible (footsteps, item sounds, ambient loops, UI).
- **821 voice clips** — Scooby-Doo has extensive spoken dialogue; this matches.

### Index table layout

The 12-byte header is followed by zero-padded bytes through at least offset
79 (confirmed via hex inspection). The index table location is not yet
resolved — candidate positions:

1. **Immediately after the header** at offset 12, but with an entry size
   larger than 8 or 12 bytes (all-zero observations may reflect name/string
   fields before offset data).
2. **Appended at the end of the file**, before or after the audio payloads.
3. **At a fixed offset** specified by a field we haven't yet decoded (e.g.,
   field at 0x08 could be an offset rather than a size).

### Index table (WP-001 lead)

Found while tracing `Scooby.exe` for [WP-001](../work-packets/WP-001-ghidra-session.md)
on 2026-11-13. This is a lead for WP-004, not a WP-004 deliverable. Option 3
above is the answer: **the field at `0x08` is the index offset.**
`audio_SoundFile_ctor` (`0x43C5A0`, `GameSoundFile.cpp`) reads the first
2,048 bytes, requires `u32 1` (else `Invalid sound data file`), seeks to the
offset at `0x08`, and reads `count` records of 68 bytes:

```
Offset  Size  Type      Field
------  ----  --------  -----
0       4     uint32LE  clip offset in the file (2,048-byte aligned, ascending)
4       64    char[64]  NUL-terminated clip name, <Section>.<Clip>
```

It sorts the records by name and finds clips by binary search. The table
ends exactly at end of file in all three Showdown files. (The "data size"
column above is therefore the table offset. Two of its decimal conversions
were also wrong: `0x01EAF800` is 32,176,128 and `0x067B8800` is 108,759,040.)

| File | Entries | Table offset | First clip | Example names |
|---|---|---|---|---|
| `Music.dat` | 28 | `0x05BB9800` | `0x800` | `Artifact.Music`, `Chase.Music` |
| `Sfx.dat` | 316 | `0x01EAF800` | `0x800` | `Artie.Chains_A` |
| `Voice.dat` | 821 | `0x067B8800` | `0x800` | `Back_Alley.350A_1_FRED`, `Global.Scrappy.*` |

Clips are referenced **by name**. The engine's sound id is the file's base
(`0x1000_0000` sfx, `0x2000_0000` voice, `0x3000_0000` music) plus the clip's
index in the name-sorted table. `object.ini`'s `scrappyid=` values are
`Voice.dat` names (see [scooby-exe](scooby-exe.md#objectini-consumer-wp-001)).
A clip's length is presumably the distance to the next offset. The clip
header and codec were not examined.

### Codec

No standard magic bytes at file offset 0 (`RIFF`, `OggS`, `ID3`, `fLaC`).
Codec is unknown until an individual audio entry is located and inspected.
Likely candidates for a year-2000 Windows edutainment title:
- IMA ADPCM (common in mid-2000s game audio)
- Miles Sound System (`MSS` header) — widely licensed in that era
- Uncompressed PCM (WAV-like)

---

## Remaining unknowns

- ~~Location of the index table~~ (header `0x08`; WP-001 lead above).
- ~~Entry record size and field layout~~ (68 bytes: offset + name). Sample
  rate, channels and codec are presumably in each clip's own header (not examined).
- Codec identity — needs at least one clip extracted and inspected.
- ~~Whether clips are referenced by numeric index or by string name~~ (by
  name; WP-001 lead above).
- ~~Whether all three files share an identical index format~~ (they do).

## Next steps

1. Write `tools/probe_audio.py` — scan each `.dat` for codec magic bytes
   (`RIFF`, `OggS`, `MSS`, etc.) at fixed alignment intervals to locate
   individual clips and infer entry stride.
2. Once a clip boundary is found, work backwards to reconstruct the index
   record format.
3. Cross-reference against `object.ini` sound references (e.g. `pickupsfx`)
   to understand the logical ID → archive entry lookup.
4. Map identified codec to ScummVM's `audio/` subsystem — identify any
   decoder work needed.

**Executable analysis.** The index-table location is a question for the
Gen 1 binary's audio loader ([WP-001](../work-packets/WP-001-ghidra-session.md)
and [WP-004](../work-packets/WP-004-audio-archive-decode.md)). The
[WP-011 decompdecomp collaboration](../work-packets/WP-011-casefile-decompdecomp.md)
on Case File #1 can help only indirectly, because that title stores audio
in `MMFW` `.MMA` archives, not `.dat`. If its audio loader turns out to be
inherited code, it gives a structural lead for the Gen 1 index.

## Success condition

Each of `Music.dat`, `Sfx.dat`, `Voice.dat` has its codec named in writing.
At least one clip from one of the three is extracted and plays in an
external player (ffmpeg / VLC).

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Phase 1, audio archives
- ScummVM audio subsystem: `audio/` in the ScummVM tree
- Companion specs: [tgifile-art](tgifile-art.md), [scooby-exe](scooby-exe.md)
