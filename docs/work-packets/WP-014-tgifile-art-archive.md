---
layout: default
title: "WP-014: TGIFILE.ART Archive Reader"
---

# WP-014: `TGIFILE.ART` reader as a `Common::Archive` (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3 (resource loading)
**Depends on:** WP-012 ✅ (detection and generation flag), WP-001 ✅ (header and descriptors traced), WP-006 ✅ (Phantom uses the same format)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-014-2026-11-14](../reference/pre-flight-WP-014-2026-11-14.md)

---

## Goal

Add the first piece of Phase 3 to the fork: a `Common::Archive` subclass
that opens a Gen 1 `TGIFILE.ART` and returns any room or object block, by
name, as a `Common::SeekableReadStream`. The engine opens it at startup for
Gen 1 games.

## Background

[tgifile-art](../formats/tgifile-art.md) documents the layout, and its
"Next steps" item 1 says the reader can be written from that page. The parts
the reader needs are:

- **Header.** It is count-driven: a room count and the room descriptors,
  then an object count and the object descriptors, then a name count and
  68-byte name records (`u32 id`, then a NUL-terminated name).
- **Descriptors.** `start_sector = d >> 14`, `sector_count = d & 0x3FFF`,
  with 2,048-byte sectors.
- **Ids.** The top nibble of a name's id is its type: 1 = ROOM, 2 = OBJ,
  3 = ANIM. For ROOM and OBJ, `id & 0x0FFFFFFF` indexes the descriptor array.

`Scooby.exe` loads by name: it binary-searches the name table and seeks with
the descriptor (`0x43B080`, `0x43B3D0`). The reader does the same; walking
the blocks is only a cross-check. Showdown and Phantom differ only in their
counts (WP-006).

## Scope

**In scope (fork, `engines/scooby/` only):**

- `ArtArchive` in `art_archive.{h,cpp}`:
  - Reads and validates the header.
  - Indexes ROOM and OBJ names, case-insensitively, as archive members. Each
    member's stream is the descriptor's sector span, as the engine reads it.
  - Keeps the full name table, so ANIM ids can be resolved by name.
- **Startup:** for Gen 1, the engine adds the `scooby` disc directory to the
  search path, opens `TGIFILE.ART` and logs the counts on the `resource`
  channel. At debug level 2 it also logs every member's offset and size, for
  checking against `probe_art.py`.
- **Console:** `art_list [prefix]` and `art_info <name>`.

**Out of scope:**

- Cel decoding (graphics).
- Parsing object resources or room blocks.
- `object.ini`, audio, and Gen 2/3 archives.

## Exit criteria

1. [ ] Showdown and Phantom: the engine's member list (name, offset, size)
   matches one computed by `probe_art.py`'s parser, for every room and
   object.
2. [ ] The name-table count and type counts match (Showdown 69 / 453 /
   1,266; Phantom 53 / 433 / 1,148).
3. [ ] A malformed or truncated file is rejected with an error instead of a
   crash. Tested with a truncated copy.
4. [ ] `grep -E '(fopen|std::ifstream|CreateFile[AW]?)' engines/scooby/`
   finds nothing (integration §4).
5. [ ] Scooby-only build: 0 errors and 0 warnings in `engines/scooby/`.
   The fork diff stays inside `engines/scooby/`.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §4](../02-SCUMMVM-INTEGRATION.md#4-resource-access--commonfile-and-commonarchive)
  implementation notes.
