---
layout: default
title: "Format Spec: Audio Archives"
---

# Format Spec: Audio Archives (`Music.dat` / `Sfx.dat` / `Voice.dat`)

**Status:** Header structure decoded — codec and index layout unresolved  
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

### Codec

No standard magic bytes at file offset 0 (`RIFF`, `OggS`, `ID3`, `fLaC`).
Codec is unknown until an individual audio entry is located and inspected.
Likely candidates for a year-2000 Windows edutainment title:
- IMA ADPCM (common in mid-2000s game audio)
- Miles Sound System (`MSS` header) — widely licensed in that era
- Uncompressed PCM (WAV-like)

---

## Remaining unknowns

- Location of the index table (offset 12 or elsewhere).
- Entry record size and field layout (offset, size, sample rate, channels, codec flag?).
- Codec identity — needs at least one clip extracted and inspected.
- Whether clips are referenced by numeric index or by string name (affects
  how `Scooby.exe` resolves a logical sound to an archive entry).
- Whether all three files share an identical index format.

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

## Success condition

Each of `Music.dat`, `Sfx.dat`, `Voice.dat` has its codec named in writing.
At least one clip from one of the three is extracted and plays in an
external player (ffmpeg / VLC).

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Phase 1, audio archives
- ScummVM audio subsystem: `audio/` in the ScummVM tree
- Companion specs: [tgifile-art](tgifile-art.md), [scooby-exe](scooby-exe.md)
