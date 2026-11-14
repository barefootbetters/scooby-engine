---
layout: default
title: "WP-001: Ghidra Session"
---

# WP-001: Ghidra session — `Scooby.exe` imports + `TGIFILE.ART` decode trace

**Status:** ✅ Done (2026-11-13). Two small residuals are listed under [Result](#result-2026-11-13).
**Phase:** 1 — Format Research
**Depends on:** WP-003 (palette hunt — run first; may eliminate palette-hunt scope from this session), WP-007 (strings dump — recommended; primes Steps 3–4)
**Companion EC:** [EC-001](../execution-checklists/EC-001-ghidra-session.md)
**Estimated effort:** 1 day (Ghidra auto-analysis included). Actual: one session, headless, with auto-analysis taking 107 s.
**Pre-flight:** [pre-flight-WP-001-2026-11-13](../reference/pre-flight-WP-001-2026-11-13.md)

---

## Result (2026-11-13)

Ghidra 12.1.4 ran headless on Java 27 against `Scooby.exe` (SHA-256
`1328454334…F7478`). The binary is not packed. The project is at
`C:\dev\scooby-engine\ghidra\scooby.gpr` (gitignored) with 68 functions
labeled by debug channel. The label list is committed at
[`tools/ghidra-scripts/wp001-labels.txt`](../../tools/ghidra-scripts/wp001-labels.txt)
and re-applied by `ApplyLabels.java`. Because WP-002 had already decoded
the images, the session went after the narrowed Step 5 targets:

| Target (narrowed 2026-11-13) | Result |
|---|---|
| 1. How the 69 room and 453 object descriptors are used | **Resolved.** `start_sector << 14 \| sector_count`; the engine seeks with them. The object table is 453 `u32`, not 8-byte records. That correction moves the name table to `0x834` with 1,788 records. |
| 2. Animation-sequence records (table 0) | **Resolved.** Step = `(0, 0x8000_0000 \| owner << 20 \| frame, polygon)`. The player, its five modes, and the per-step click polygon are traced. ANIM id = `0x3 \| owner & 0xFF \| sequence index`, and the 1,266 ANIMs equal the 1,266 sequences. |
| 3. Room-block words `0x10`, `0x80`, `0xAC` and the tables after the background | **Mostly resolved.** `0x80` holds 10 layer slots (slot 0 = background), `0xAC` the cel table, `0xB0`/`0xB8` two loader-supported tables empty in Showdown, `0xC0` the placements. The placement record is mapped (x, y at `+0x84`). **Open:** word `0x10`, and placement `+0x88`. |
| 4. Roles of the two mask chunks | **Resolved.** A = opaque RGB565 pixels, B = translucent ARGB4444 pixels; everything else transparent. Also found: solid-colour and raw (little-endian) cels. |
| 5. Room names for scenes 18 and 19 | **Resolved.** `ROOM_Artie`, `ROOM_Title_Screen` (name-table records 18, 19). |
| 6. WP-008 leads | **Resolved.** `object.ini` is read live per object (`GetPrivateProfileStringA`); the `ID=` switch is at `0x408F90`. `scrappyid` values are `Voice.dat` clip names, spoken in Scrappy hint mode. Inventory art is sequences of `OBJ_TOOLBAR` / `OBJ_CURSOR`. There is no scripted-room render branch. |

Also found: the engine's own RLE decoder (`0x4398A0`) matches WP-002
exactly, and the `.dat` audio index layout (a lead for WP-004).

Findings live in [tgifile-art.md](../formats/tgifile-art.md) (header,
descriptors, sequences, room blocks, cel flags, masks, name table, decode
path), [scooby-exe.md §Resource loading map](../formats/scooby-exe.md#resource-loading-map)
and [§`object.ini` consumer](../formats/scooby-exe.md#objectini-consumer-wp-001),
and [audio-archives.md](../formats/audio-archives.md#index-records).
`tools/probe_art.py --verify` now checks every data-side claim across the
whole file, and `probe_art.py` renders with the masks.

**Not done:**
- Room-block word `0x10` and placement field `+0x88`: no reader found.
- Object table 2's consumer was not traced.
- Phantom was not loaded (out of scope; WP-005 / EC-002 Phase D).

---

## Goal

Load `Scooby.exe` into Ghidra, identify the function chain that opens and decodes a `TGIFILE.ART` entry, and record enough understanding to reimplement that decode in C++ for the ScummVM engine.

## Background

WP-002 (`TGIFILE.ART` decoder) is the bottleneck for Phase 1 exit. Two paths exist to crack it: blind decode-guessing (`probe_art.py` trying RLE / palette / LZ variants), or tracing the decode function inside the binary that already does it correctly. The binary path is higher-confidence — the decode algorithm is guaranteed to be in there.

`Scooby.exe` is small (476 KB), which supports the hypothesis that it's largely an interpreter over `object.ini` + a thin set of resource loaders. That makes finding the relevant function tractable rather than a multi-week archaeology project.

**WP-003 baseline (2026-06-02) — concrete Ghidra targets unlocked.** [WP-003](WP-003-pre-payload-region.md)
landed the pre-payload region characterization in [tgifile-art.md §Pre-payload region](../formats/tgifile-art.md#pre-payload-region--engine-name-table)
and also corrected the header offsets (`asset_count` is at `0x0118`, not
`0x011C`; whole header shifted +4 in the prior spec). For this Ghidra
session that means four specific function targets to hunt for, on top of
the generic file-I/O surface:

- **Name-table loader.** A routine that reads the 68-byte name records
  (4 B id + 44 B ASCII name + 20 B metadata) from `TGIFILE.ART` into
  memory and populates a lookup structure. Known shape: count probably
  derived from an iterator that runs at least 811 times (the continuous
  block) and likely more (the mixed tail region carries ~600 more
  records on the same stride). Recognizable by the 68-byte stride, the
  `(id >> 24)` type-tag switch, and the ASCII-string-copy pattern.
- **OBJ-id → asset-entry resolver.** WP-003 confirmed that `entry[i]`
  is the payload for `OBJ` id `i` (453 OBJ records, IDs contiguous 0–452,
  matching `asset_count`). This is a one-line indexer — `asset_table[obj_id].start`
  — and the simplest, cleanest landing zone for "find the function that
  resolves a logical asset name to a file offset."
- **20-byte per-record metadata consumers.** WP-003 found one record
  (`ANIM_BIG_HEAD_BG_P09DAPHNE` at file `0xE644`) carrying `(6534, 6078,
  6078, 0, 0)` as `5x uint32LE` in the metadata field; the rest of the
  continuous block has zero metadata. Schema is unresolved — finding
  code that reads offset 48 of name-table records pins it down.
  Plausible candidates: per-frame dimensions, palette index, animation
  duration.
- **69-entry group descriptor table.** The 4-byte records at `0x0004`–`0x0117`
  remain uncharacterized (values are monotonically increasing uint32s
  exceeding file size, so not raw offsets). Ghidra trace may reveal
  whether the engine actually reads this table at runtime, or whether
  it's link-time-only dead weight.

WP-003 also produced a **negative palette finding** — no 256-entry RGB or
RGBA palette exists in the pre-payload region. Palette discovery moved
to WP-002 (per-asset leading bytes or per-record metadata). For this
Ghidra session, that means palette-load code is *not* expected to read
from the pre-payload region; it's expected to read from inside an asset
payload at or after `0x10017E`, or from the 20-byte metadata field on
OBJ records.

**WP-008 baseline (2026-06-03) — four additional Ghidra-session targets.**
The Showdown `object.ini` analysis ([scooby-exe.md §`object.ini`
interpreter behavior](../formats/scooby-exe.md#objectini-interpreter-behavior))
confirmed the engine is name-driven (every reference is a string in the
WP-003 convention) and produced four concrete loose ends that only the
exe can resolve:

- **`object.ini` consumer / loader.** The 215 `[OBJ_*]` sections are
  discriminated by an `ID=` field with 5 values (`exitobject`,
  `clickableobject`, `inventoryobject`, `requiresobject`,
  `simpleobject`). The interpreter almost certainly has a switch on
  this string — find it by xref-ing the `Failed to load room.` error
  string in `strings-ansi.txt`. Adjacent to that switch should be the
  `(name → asset)` hash-table lookup that resolves
  `destinationroom=ROOM_*` and `rolloveranim=ANIM_*` values to runtime
  asset records.
- **`scrappyid` script-table resolver.** `exitobject` entries carry
  `scrappyid=Global.Scrappy.<scene>_<entry>` (e.g.
  `Global.Scrappy.Town_Center_to_Street3`). This is a script-system
  identifier, not an asset name — there's no `Scrappy.*` table in
  `object.ini` or `Scooby.eng`. The store is a new unknown; tracing
  what reads the `scrappyid` value during room-exit handling will
  surface it (most likely embedded in the binary or in a not-yet-found
  data file).
- **Inventory-anim resolution path.** The 11 `OBJ_INV_*` entries each
  reference `ANIM_TOOLBAR<NAME>` + `ANIM_CURSOR<NAME>` (e.g.
  `ANIM_TOOLBARBLANKET`, `ANIM_CURSORBLANKET`) — none of which appear
  in the WP-003 `TGIFILE.ART` name table. System toolbar animations
  (`ANIM_TOOLBARCOMPUTER_IDLE`, `ANIM_TOOLBARSCRAPPY_IDLE`) *do* appear
  in the WP-003 table. So inventory art is in a separate store or is
  composited at runtime from base assets + per-item parameters. Find
  the function that resolves `toolbaranim=`/`usecursor=` for inventory
  objects.
- **Scripted-room background path.** 21 of 37 `destinationroom=` values
  point at rooms with no entry in the WP-003 `TGIFILE.ART` ROOM table
  — including `ROOM_Main_Menu`, `ROOM_P01_Town_Center`,
  `ROOM_P12_Saloon`, `ROOM_P30_Horseshoe_Corral` (the Horseshoe Corral
  minigame), `ROOM_P32_Pie_Noon`. These rooms render via a different
  path — likely procedural / GBH-module code (the source-tree paths
  `\Scooby\GBH\Horseshoe_Corral_Room.cpp` and `Pie_Noon_Room.cpp` in
  the [Showdown strings findings](../formats/scooby-exe.md#showdown-gen-1)
  align with this). Find the room loader's branch between "load from
  `TGIFILE.ART`" and "invoke per-room render function."

All four are name-string xref targets — they should be straightforward
to find once Ghidra has analyzed the binary and the
[scooby-exe.md §Showdown string anchors](../formats/scooby-exe.md#showdown-gen-1)
table is in front of you.

## Scope

In scope:
- PE Rich Header inspection (toolchain identification, 5 min)
- Ghidra project setup at `C:\dev\scooby-engine\ghidra\scooby.gpr`
- Auto-analysis pass
- Imports table review (DirectDraw / DirectSound / DirectInput / Bink / Win32 file I/O)
- Locating and labeling the `TGIFILE.ART` file open call and the function chain it dispatches into
- **Locating and labeling the name-table loader** (per WP-003 baseline — see §Background): the routine that reads the 68-byte records at file offset `≥ 0x0F60` into memory
- **Locating and labeling the OBJ-id → asset-entry resolver** (one-line indexer; cleanest landing zone for asset-name → file-offset resolution)
- **Recording any code accessing offsets 48–67 of name-table records** (resolves the 20-byte metadata schema; the field is non-zero on at least one ANIM record per WP-003)
- **Checking whether the 69-entry group descriptor table (0x0004–0x0117) is read at runtime** (still uncharacterized post-WP-003)
- **Locating and labeling the `object.ini` consumer** — the switch on `ID=` value (5 cases per WP-008) plus the adjacent `(name → asset)` hash-table lookup; xref-anchor the `Failed to load room.` error string
- **Locating and labeling the `scrappyid` script-table resolver** — what reads `Global.Scrappy.*` strings during room-exit handling (new unknown surfaced by WP-008)
- **Locating the inventory-anim resolver** — what handles `ANIM_TOOLBAR<NAME>` / `ANIM_CURSOR<NAME>` lookups for `OBJ_INV_*` objects, since these names don't appear in the WP-003 `TGIFILE.ART` name table
- **Locating the scripted-room render branch** — the room-loader switch between "decode from `TGIFILE.ART`" and "invoke per-room render function" for the 21 rooms with no `TGIFILE.ART` ROOM entry (`ROOM_Main_Menu`, `ROOM_P01_Town_Center`, `ROOM_P12_Saloon`, etc.)
- Decompiling the decode function to readable pseudo-C
- Recording findings into `docs/formats/scooby-exe.md` → Findings section

Out of scope:
- Full disassembly of game logic (puzzle state machines, room transitions) — that's Phase 4 work
- Save-game format reverse engineering — deferred until Phase 4
- Audio archive decode functions — covered by WP-004 if needed
- Cross-title comparison (e.g. analyzing Phantom's exe) — covered by WP-005

## Dependencies

- Ghidra installed locally (any recent version; record version in EC-001 pre-flight)
- `Scooby.exe` extracted from the mounted Showdown ISO to `C:\pcloud\SCOOBY\extracted\showdown\Scooby.exe` (or equivalent local path)
- A PE inspector for the Rich Header check (`CFF Explorer`, `PE-bear`, or `pefile` Python lib)

## Exit criteria

1. `docs/formats/scooby-exe.md` Findings → "Toolchain" populated with confirmed compiler + linker. ✅ (Rich Header step, 2026-06)
2. `docs/formats/scooby-exe.md` Findings → "Imports / runtime surface" populated with the DirectX surfaces in use, Bink integration, and file I/O API set. ✅ (WP-007 import table; cross-checked, no change)
3. `docs/formats/scooby-exe.md` Findings → "Resource loading map" populated with at least the `TGIFILE.ART` open + dispatch path labeled in Ghidra. ✅ 2026-11-13
4. The `TGIFILE.ART` decode function is identified (Ghidra function name + entry address recorded) and its pseudo-C decompilation is captured as a code block in `docs/formats/tgifile-art.md` Findings → "Per-entry payload" → new subsection "Decode algorithm (from `Scooby.exe`)". ✅ 2026-11-13: `graphics_Renderer_GetCelPixels` at `0x4398A0`. The page has no "Per-entry payload" heading any more, so the subsection is [Cel format → Decode path in `Scooby.exe`](../formats/tgifile-art.md#decode-path-in-scoobyexe-wp-001). It is restated pseudo-C, not raw decompiler output.
5. Ghidra project saved at `C:\dev\scooby-engine\ghidra\scooby.gpr` with the labels above intact. ✅ 2026-11-13 (68 labels; list committed under `tools/ghidra-scripts/`)

## Deliverables

- Updated [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) — Findings sections.
- Updated [`docs/formats/tgifile-art.md`](../formats/tgifile-art.md) — decode algorithm sub-section.
- Ghidra project file at `C:\dev\scooby-engine\ghidra\scooby.gpr`.

## Notes

- If Ghidra auto-analysis takes longer than ~45 minutes, queue up WP-003 and the PE Rich Header check in parallel while it runs.
- If the decode function turns out to be inlined or split across many helpers, time-box the trace at 4 hours and fall back to WP-002 with `probe_art.py` — record what was learned so far and what remains unknown.
- If the binary turns out to be packed (UPX or similar), unpack first; record the packer in `scooby-exe.md`.
- This WP is Track A of the [`Scooby.exe` analysis plan](../formats/scooby-exe.md#two-analysis-tracks). Track B, the decompdecomp collaboration on Case File #1, is [WP-011](WP-011-casefile-decompdecomp.md). If WP-011 finds inherited `MMFW`, archive or decoder code in Case File #1, the Gen 1 counterpart here becomes a concrete target. WP-011 doesn't change this WP's scope.
- The PE Rich Header check is cheap enough that it should run before Ghidra (so Ghidra can be told the right calling convention from the start).
