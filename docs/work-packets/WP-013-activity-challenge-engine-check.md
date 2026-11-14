---
layout: default
title: "WP-013: Activity Challenge Engine Check"
---

# WP-013: Engine-family check for *Scooby-Doo! Activity Challenge*

**Status:** ✅ Done (2026-11-14)
**Phase:** 1 — Format Research (follow-on to [WP-005](WP-005-engine-family-check.md), found in passing by [WP-012](WP-012-detection-table.md), the detection table)
**Depends on:** —
**Companion EC:** — (WP-005's method; no checklist needed)
**Estimated effort:** 1–2 hours
**Pre-flight:** [pre-flight-WP-013-2026-11-14](../reference/pre-flight-WP-013-2026-11-14.md)

---

## Result (2026-11-14)

**Verdict: same engine lineage, Gen 2.** *Activity Challenge* runs the
same `MMFW` framework as Jinx, built from the same source tree a day
earlier, with its own game layer on top. VISION's "almost certainly a
different engine" is withdrawn.

| Disc | Code lineage | Formats | Verdict |
|---|---|---|---|
| *Activity Challenge* (2001) | **Same as Jinx.** `__FILE__` path `C:\Projects\Scooby\Bonus\Mmfw\MMVisualCursor.cpp` beside Jinx's `C:\Projects\SCOOBY\mummy\Mmfw\MMVisualCursor.cpp`. All 112 of its `MM*` RTTI classes are Jinx classes. 532 of its 549 engine strings are Jinx's. Linked 2001-09-18, one day before Jinx. | `MMFW` archives (`BONUS.MMF/MMA/MMP`, `Bonus.mms`), with headers laid out like Jinx's | **COMPATIBLE** (WP-005's vocabulary): Gen 2 |

### Evidence

Sources: the disc's `INSTALL\HDINSTALL\Scooby.exe` (794,624 bytes,
cached under `tools/exes/activity/`; see
[tools/exes/README](../../tools/exes/README.md#activity-challenge-gen-2)),
compared with `tools/exes/jinx/Scooby.exe` (847,872 bytes). Full write-up:
[scooby-exe §Activity Challenge](../formats/scooby-exe.md#activity-challenge-wp-013).

1. **Source path.** The one `__FILE__` path in each binary sits in the
   same tree: `C:\Projects\Scooby\Bonus\Mmfw\` (Activity Challenge) and
   `C:\Projects\SCOOBY\mummy\Mmfw\` (Jinx). It is the same project root,
   with a sibling folder per title and the same `Mmfw` framework folder.
   Case File #1's is IBS's `F:\Scooby\Museum\framework\`.
2. **RTTI.** Activity Challenge has 510 distinct RTTI type names, and 323
   of them are in Jinx too.
   - **Framework:** 112 `MM*` classes, all of them in Jinx. Jinx has seven
     more: the bitmap picture collection and manager, two 2D transitions,
     `MMHighlightable` and `MMSingleEventInterpreter`.
   - **Game layer:** `ScoobyCharacter`, `ScoobyGameProgress` and
     `ScoobySnackState` are shared. The title classes run in parallel:
     `BonusApplication`, `BonusStage`, `BonusInteractionScene` and
     `BonusGameProgress` against Jinx's `Mummy*` set.
   - **Activity Challenge only (187 names):** mostly two mini-game
     namespaces, `KnightsTable` (86) and `PieNoon` (74), plus a skiing
     game (`SnowMonster`, `SkiingCharacter`) and a hub scene
     (`SceneCampFire`).
3. **Engine strings.** 532 of the 549 distinct non-RTTI strings of eight
   characters or more are Jinx's. They include the `MMFW Films`/`Pictures`/
   `Scripts`/`Sounds` labels and the resource-file error templates (`Bad
   header in picture resource file '%s'.` and its relatives). The
   differences are the title's own:
   - **Only in Jinx:** the *Jinx At The Sphinx* names and two save-game
     errors.
   - **Only in Activity Challenge:** `The Learning Company\Campfire`
     where Jinx has `The Learning Company\Jinx At The Sphinx` (not a
     registry key: neither binary imports `ADVAPI32`), and
     `Elevator::STATE_*` names.
   - **Left over:** Activity Challenge's binary still carries `Scooby Doo
     -- Jinx At The Sphinx`.
4. **Wide strings.** Jinx names `Mummy*.MM?` and `Hd.mma`/`Hd.mmp`.
   Activity Challenge names `Bonus.MMA`, `Bonus.MMF`, `Bonus.MMP` and
   `Bonus.MMS`, which are the four archives on its disc. It adds
   `SCOOBYDOO`, which matches the disc's volume label.
5. **Imports.** Both import from the same five DLLs (`GDI32`, `KERNEL32`,
   `MSVFW32`, `USER32`, `WINMM`). Activity Challenge imports 206 functions
   and Jinx 204, with 202 shared. Activity Challenge adds `MulDiv`,
   `SetCursorPos` and `ShowCursor` and drops `SetEndOfFile` and `FillRect`.
   Video goes through Video for Windows `DrawDib`, and DirectSound is
   loaded dynamically (`DSOUND.DLL` and `DirectSoundCreate` strings), as in
   Jinx.
6. **Toolchain** (supporting evidence only, per PR #39's correction):
   - **Same as Jinx:** VC6 C build 8168 ×160, MASM 6.13 7299 ×29 and
     `Linker512` 8034 ×17.
   - **Different:** the C++ is mostly build 8447 (×135), plus 8168 (×8),
     where Jinx compiles all 157 C++ objects with 8168. `Cvtres500` is
     build 1735, Jinx's 1720.
   - So the shared C library came over unchanged and the C++ was compiled
     with a later VC6 build. The service pack was not checked.
   - Both are linker 6.00 with the same five sections and no version
     resource.
7. **`MMFW` headers.** Each `Bonus` archive's first 16 bytes equal its
   Jinx counterpart's (`MMFW` and the same content tag). The marker at
   `0x10` is the same too: `4D 4D 00 03` for Films, Sounds and Pictures,
   and `49 49 03 00` for Scripts (`.mms`) in both titles. From `0x14` the
   per-file fields differ. See
   [mmfw-container §Confirmed magic bytes](../formats/mmfw-container.md#confirmed-magic-bytes-across-samples).
8. **Shared disc files.** `IBSlogo.avi`, `TLCLOGO.avi`, `WBLOGO.avi`,
   `PLAY.EXE` and `SETUP.EXE` have the same SHA-256 hashes as Jinx's. 158
   of the 189 files under `INSTALL\` match Jinx's by path and size. The
   layout differs in two places:
   - Activity Challenge keeps its executable in `INSTALL\HDINSTALL\` and
     all four archives at the root. Jinx keeps its executable,
     `Mummy.mms` and the HD archives in `Jinx\`, and its large archives at
     the root.
   - Its disc marker is `INSTALL\TLC\BONUSCD.CD`.

| Exit criterion | Result |
|---|---|
| 1. Verdict on code lineage and on formats, kept separate | ✅ Table above: same code lineage as Jinx; `MMFW` formats |
| 2. Evidence from the executable, not the disc layout | ✅ Source path, RTTI, strings and imports (items 1–5). Disc and toolchain (items 6–8) are supporting evidence. |
| 3. Cache entry with sizes and SHA-256 only | ✅ [tools/exes/README §Activity Challenge](../../tools/exes/README.md#activity-challenge-gen-2). No game data committed. |
| 4. VISION corrected | ✅ The paragraph after the title table, the Engine Lineage Gen 2 row, a confirmed-findings bullet, and the Phase 5 scope rule (Activity Challenge moves from Excluded to Unassigned) |
| 5. ISO dismounted | ✅ `Get-DiskImage` reports `Attached: False` for both `ScoobyDoo.iso` and the Jinx ISO |

### What this does not settle

- **Scope tier.** Activity Challenge is no longer excluded on engine
  grounds, but this WP does not place it in a Phase 5 tier. It is a set of
  real-time mini-games: a skiing game, pie throwing, and a `MovementThread`
  and `PollingMouseInputStrategy` the adventures do not have. A Gen 2
  reader would open its archives, but its game layer would be new work on
  top of Jinx's. VISION lists it as **Unassigned** until that is decided.
- **Payload formats.** As for Jinx, nothing inside an `MMFW` archive is
  decoded yet.
- **Studio.** The source tree and build date put it beside Jinx. No
  developer credit was checked for this title, so none is claimed here.

### Detection (not done here)

The fork's detection table
(`C:\dev\scummvm` `engines/scooby/detection_tables.h`, added by [WP-012](WP-012-detection-table.md))
could take a `kGen2` entry for this disc. Using WP-012's method (size and
MD5 of the first 5,000 bytes; Jinx's `Mummy.mms` reproduces its listed
`17d996eb…`):

| File | Size (bytes) | MD5 (first 5,000 bytes) |
|---|---|---|
| `Bonus.mms` | 289,844 | `b6708dba6c936d5df3355668bca45aa9` |
| `BONUS.MMP` | 68,733,610 | `2a96b23cb24e866d65ea3cd4939c78b1` |
| `BONUS.MMF` | 19,744,128 | `35d13d927badf3d5f6177a003b072ac6` |

The entry would need a game id and a support flag. Like Jinx it would be
`ADGF_UNSUPPORTED`. Until it lands, WP-012's check that Activity
Challenge is not detected stays correct.

---

## Goal

Determine whether *Scooby-Doo! Activity Challenge* (2001,
`ScoobyDoo.iso`) runs the TerraGlyph/IBS engine lineage, and if so, which
generation. Correct VISION either way.

## Background

VISION listed the disc as "almost certainly a different engine" because it
is an edutainment title rather than an adventure. WP-005 left it out of
scope without checking. While testing detection, WP-012 saw Jinx's layout
on the mounted disc: `MMFW` archives at the root, an
`INSTALL\HDINSTALL\Scooby.exe`, and `IBSlogo.avi`. WP-005's lesson applies:
a disc layout is not a lineage verdict, so the executable decides.

## Scope

In scope:
- Mount `ScoobyDoo.iso` with `Mount-DiskImage`, list it, cache the
  executable and the `MMFW` archives under `tools/exes/activity/`
- Compare the executable with Jinx's: Rich Header, strings, imports,
  RTTI, source paths
- Compare `MMFW` header bytes with Jinx's archives
- Record the verdict in VISION, the format docs, the cache README and
  WORK_INDEX

Out of scope:
- Decoding any `MMFW` payload
- Adding a detection entry to the ScummVM fork
- Placing the title in a Phase 5 scope tier

## Exit criteria

1. A verdict on code lineage and one on formats, recorded separately.
2. The verdict rests on executable evidence (RTTI, engine strings, source
   paths, imports). The disc layout and Rich Header support it only.
3. A cache entry in `tools/exes/README.md` with sizes and SHA-256, and no
   game data committed.
4. VISION's paragraph on the disc, its Engine Lineage table and its Phase 5
   scope rule agree with the verdict.
5. The ISO is dismounted at the end.

## Deliverables

- This WP and its [pre-flight](../reference/pre-flight-WP-013-2026-11-14.md)
- [`docs/01-VISION.md`](../01-VISION.md) — Target Games paragraph, Engine
  Lineage, Phase 5 scope rule
- [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) — toolchain
  tables and an Activity Challenge subsection
- [`docs/formats/mmfw-container.md`](../formats/mmfw-container.md) — sample
  headers
- [`tools/exes/README.md`](../../tools/exes/README.md) — cache entry
- [`WORK_INDEX`](WORK_INDEX.md) — row and findings bullet

## Notes

- Both titles' `.mms` scripts archives carry `II 03 00` at `0x10` where
  the other archives carry `MM 00 03`. Read as TIFF-style byte-order marks,
  both say version 3: big-endian for Films, Sounds and Pictures,
  little-endian for Scripts. That is a reading, not a traced fact. It is
  recorded in `mmfw-container.md` as a hypothesis.
