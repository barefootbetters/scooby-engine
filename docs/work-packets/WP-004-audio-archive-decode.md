# WP-004: Audio archive index + codec identification

**Status:** 📝 Drafted
**Phase:** 1 — Format Research
**Depends on:** —
**Companion EC:** — (single afternoon's work; no checklist needed)
**Estimated effort:** Half-day to 1 day

---

## Goal

Locate the index table inside `Music.dat`, `Sfx.dat`, and `Voice.dat`; identify the codec used for individual audio clips; extract at least one clip and verify it plays in an external player (ffmpeg / VLC). Satisfies Phase 1 exit criterion #3.

## Background

Shared 12-byte header structure is understood (version=1, entry_count, data_size — see [`docs/formats/audio-archives.md`](../formats/audio-archives.md)). Bytes `0x0C`–`0x4F` are zero in all three files. The actual index table has not been located.

Open questions about the third header field:

| File | File size | Field value | Δ (field − file) |
|---|---|---|---|
| Music | 96,182,128 | 96,180,224 | −1,904 |
| Sfx | 32,197,616 | 32,178,176 | −19,440 |
| Voice | 108,814,868 | 108,822,528 | **+7,660** |

Voice.dat's field exceeds file size, ruling out "payload bytes." All three end in `0x800` (= 2048, CD-ROM sector size), suggesting some sector-aligned quantity rather than a byte count of contents.

## Scope

In scope:
- `tools/probe_audio.py` — Python harness that scans each `.dat` for codec magic bytes at various alignments (header start, sector boundaries, end-of-file walking backward)
- Locating the index table — three candidate positions per `docs/formats/audio-archives.md`
- Once a candidate clip boundary is found, extract one clip and identify codec by external play
- Resolving the third header field's meaning (sector-aligned what?)
- Recording findings into `docs/formats/audio-archives.md`

Out of scope:
- Implementing a ScummVM-compatible audio decoder (Phase 3, WP-021 equivalent)
- Decoding more than one clip per archive — codec identification is sufficient for Phase 1 exit
- Cross-title verification across Phantom / Jinx (covered by WP-005 file-name-and-size diff)

## Dependencies

- Python 3.x
- `ffmpeg` or VLC for playback verification of extracted clips
- Optional: `binwalk` for automated magic-byte scanning

## Exit criteria

1. The codec used by `Music.dat`, `Sfx.dat`, and `Voice.dat` is identified by name (IMA ADPCM, Miles MSS, raw PCM, Vorbis, MP3 frames, etc.). Single name acceptable if all three share a codec; otherwise per-file names.
2. At least one clip from one archive is extracted and plays in an external player.
3. Index table location and per-entry record format documented in `docs/formats/audio-archives.md` Findings.
4. The third header field's meaning is either resolved (with a confirmed interpretation) or explicitly listed in `docs/formats/audio-archives.md` as "remains unknown, candidate hypotheses tested were …".
5. ScummVM codec coverage assessed: if the codec is already supported by ScummVM's `audio/decoders/`, note which decoder. If not, this becomes a known item for Phase 3 (WP-021 will need a new decoder or wrap an existing library).

## Deliverables

- [`tools/probe_audio.py`](../../tools/probe_audio.py) — extraction + scanning harness
- At least one extracted clip at `tools/samples/audio-clip-0.<ext>` (extension reflecting identified codec)
- Updated [`docs/formats/audio-archives.md`](../formats/audio-archives.md) — Findings

## Notes

- Parallel-safe with WP-001, WP-002, WP-003, WP-005.
- The `0x800` (2048-byte) trailing pattern in the third header field strongly suggests sector alignment — worth specifically testing whether the field × 1 byte = sector-aligned payload end, or whether it's an offset to the index table aligned to sectors.
- If the codec turns out to be Miles Sound System, flag for `02-SCUMMVM-INTEGRATION.md` §6 — Miles licensing is a known sensitive area for upstream contribution and merits a pre-PR discussion with ScummVM maintainers.
- The very-low-confidence hypothesis from `docs/formats/audio-archives.md` is that voice clips are referenced by string name (via `object.ini`); this WP doesn't need to resolve that but should note any name-table-shaped structures encountered.
