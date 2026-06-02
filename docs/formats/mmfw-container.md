---
layout: default
title: "Format Spec: MMFW Container"
---

# Format Spec: `MMFW` Container (Gen 2/3 archive format)

**Status:** Container header structure identified — payload format unknown
**Engine generation:** **Gen 2** (Jinx 2001) and **Gen 3** (Case File #1 2002, Case File #2 2003 predicted)
**Sample files:**
- `E:\Mummy.MMF` (57 MB) — Jinx, content type: "Films"
- `E:\Jinx\Mummy_HD.MMF` (10.6 MB) — Jinx, content type: TBD
- `E:\Jinx\HD.MMA` (8.2 MB) — Jinx, audio
- `E:\Jinx\HD.MMP` (11.3 MB) — Jinx, package
- `F:\Scripts and Resources\MuseumCD.MMP` (92 MB) — Case File #1, content type: "Pictures"
- `F:\Scripts and Resources\MuseumCD.MMA` (25 MB) — Case File #1, audio

**Vision doc reference:** [Project Vision](../01-VISION.md) — Engine Lineage section

This is the archive container that **replaced** Gen 1's `TGIFILE.ART`
format starting with Jinx at the Sphinx (Oct 2001). It carries a typed
content tag in its header, then a versioned sub-header, then archive
payload — the payload structure is not yet decoded.

---

## Confirmed structure

### Header layout (first 32 bytes confirmed)

```
Offset  Size  Type        Value (Jinx Mummy.MMF)          Notes
------  ----  ----------  ------------------------------  -----
0x0000     4  ASCII       "MMFW"  (4D 4D 46 57)           Container magic
0x0004    12  ASCII       " Films\0\0\0\0\0\0"            Content-type tag (12 bytes, space-prefixed, null-padded)
0x0010     4  ASCII       "MM\0\x03"  (4D 4D 00 03)       Sub-header — likely version marker
0x0014    12  binary      A6 19 7C 23 0B B8 2E 17 ...     Sub-header data, structure TBD
```

### Confirmed magic bytes across samples

| Sample | Bytes 0-15 (hex) | Content tag |
|---|---|---|
| `Mummy.MMF` (Jinx) | `4D 4D 46 57 20 46 69 6C 6D 73 00 00 00 00 00 00` | "MMFW Films" |
| `MuseumCD.MMP` (Case File #1) | `4D 4D 46 57 20 50 69 63 74 75 72 65 73 00 00 00` | "MMFW Pictures" |

Both share the **identical sub-header bytes at offset 0x10:** `4D 4D 00 03`. This is the strongest signal that Gen 2 and Gen 3 use the same container format — they only differ in which content tags they ship.

### Observed content tags

- `MMFW Pictures` — graphics archive (backgrounds, sprites)
- `MMFW Films` — video / cutscene archive (separate from the disc-root `.avi` files in Gen 3)

Other tags expected but not yet observed (predict from filename patterns): `MMFW Sounds` or `MMFW Audio` for `.MMA` files; possibly `MMFW Package` or `MMFW Project` for `.MMP` files when used as combined containers.

---

## Hypotheses (unverified)

| Hypothesis | Evidence | Confidence |
|---|---|---|
| `MM\x00\x03` is a version-3 marker — implying versions 1 and 2 existed internally before shipping | Standard versioning pattern; Gen 1's `TGIFILE.ART` had no such marker (it was effectively v0 or "untagged") | Medium |
| The 12 bytes after `MMFW` are a space-prefixed ASCII content type, null-padded to fixed width | Both observed samples conform; null padding is consistent | High |
| Sub-header at 0x10 carries entry count + offset table, analogous to `TGIFILE.ART` | Same archive role; engine is a direct descendant | Medium |
| `.MMF`, `.MMA`, `.MMP` extensions encode content category (Film/Audio/Project) and the wrapper tag is redundant | Three-letter extensions correlate but tags duplicate the info | Medium |
| Payload entries are compressed with the same `F0`-opcode encoding as `TGIFILE.ART` (since same engine lineage) | Same C++ codebase per the engine-inheritance finding | Medium |

---

## Unknowns

- Sub-header field layout starting at offset 0x14 (entry count? offset table base?)
- Per-entry record structure
- Whether `.MMA`, `.MMF`, `.MMP` files share an internal payload encoding or have format-specific variations
- Payload compression (likely shared with Gen 1's `TGIFILE.ART` but not verified)
- How `Case File #1.exe` resolves a logical asset ID to an entry within an `MMFW` container

## Investigation plan

1. **Hex inspection of the `0x10`-onwards sub-header** in both samples — identify the entry-count and offset-table fields. The format is almost certainly an evolution of Gen 1's `TGIFILE.ART` structure; expect similar field shapes.
2. **Cross-sample comparison.** Diff the first ~512 bytes of `Mummy.MMF` and `MuseumCD.MMP` — fields that vary identify per-file data (entry count, offset table); fields that match identify shared schema constants.
3. **Probe-script extraction.** Once the sub-header is mapped, port `tools/probe_art.py` to handle `MMFW` containers — likely a thin wrapper that skips the 16-byte tag header before delegating to the existing extraction logic.
4. **Payload decode cross-check.** When a `TGIFILE.ART` payload decodes successfully (WP-002), try the same decoder on an `MMFW` entry. If it works, the engine-inheritance hypothesis extends to the compression layer.

## Success conditions

1. Sub-header field layout fully documented.
2. At least one payload entry extracted from a `MuseumCD.MMP` or `Mummy.MMF`, decoded with the same algorithm as `TGIFILE.ART`, rendered to PNG/BMP matching in-game output.

---

## Engine generation correspondence

| Gen | Title | Archive files | Format spec |
|---|---|---|---|
| 1 | Showdown | `TGIFILE.ART`, `Music.dat`, `Sfx.dat`, `Voice.dat` | [`tgifile-art.md`](tgifile-art.md) (+ [`audio-archives.md`](audio-archives.md) for Gen 1 audio) |
| 1 | Phantom | unverified, predicted same as Showdown | same as Showdown |
| 2 | Jinx | `Mummy*.MMF`, `HD.MMA`, `HD.MMP`, `Mummy_HD.MMF`, `Mummy.mms` | this doc |
| 3 | Case File #1 | `MuseumCD.MMP`, `MuseumCD.MMA` | this doc |
| 3 (predicted) | Case File #2 | TBD | predicted this doc |

---

## References

- Vision doc: [Project Vision](../01-VISION.md) — Engine Lineage section
- Companion specs: [`tgifile-art.md`](tgifile-art.md) (Gen 1 archive format), [`audio-archives.md`](audio-archives.md), [`scooby-exe.md`](scooby-exe.md)
