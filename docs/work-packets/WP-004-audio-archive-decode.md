---
layout: default
title: "WP-004: Audio Archive Decode"
---

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
- **Architectural prior from [WP-003](WP-003-pre-payload-region.md):** `TGIFILE.ART` uses a `header + name-table + payload` layout with 68-byte name records (4 B `uint32LE` id + 44 B zero-padded ASCII name + 20 B metadata; type-tag in id high byte: `0x10` = ROOM, `0x20` = OBJ, `0x3x` = ANIM). The Gen 1 engine uses this exact pattern for image / animation resources; it's plausible (not proven) that `Music.dat`/`Sfx.dat`/`Voice.dat` follow the same shape, with type-tagged audio resource names. When scanning the unaccounted bytes `0x0C`–`0x4F` and the regions immediately after the 12-byte header, watch specifically for 68-byte-stride records or any contiguous block of type-tagged uint32 + ASCII string pairs. A name-table hit there would also resolve the "string-name vs numeric index" question for audio resource resolution.
- **`Scooby.eng` is NOT in-game dialogue** ([WP-008 finding](../formats/scooby-exe.md#objectini-interpreter-behavior), 2026-06-03). The file carries 10 system-error/init messages (DirectDraw failure, CD-ROM access, out-of-memory, etc.) loaded by `Scooby.exe`'s boot path — all 5 spot-checked strings appear in the binary's strings dump. **In-game dialogue text is therefore in a different store** — most likely `Voice.dat` (per-clip text alongside the audio?), inside `Scooby.exe`'s embedded strings, or in a not-yet-identified file. Watch for ASCII-shaped runs alongside the audio clips during the index-table scan — a `(clip_id, text, audio_offset)` shape would resolve both this WP's dialogue-text question and the "voice clips referenced by string name" hypothesis at once.
- **Audio cue references in `object.ini` are sparse** (WP-008 baseline). Only `pickupsfx=<none>` appears on the 11 `OBJ_INV_*` entries; no other audio key is observed across 215 OBJ sections. Either audio cues are triggered by code (referenced by `scrappyid=Global.Scrappy.*` script handlers — see [WP-001 §Background](WP-001-ghidra-session.md#background)), or they're co-located with dialogue inside `Voice.dat`. The data-driven hypothesis "voice clips are referenced by name from `object.ini`" gets weaker evidence from WP-008, but the script-system path is now an explicit suspect.
