---
layout: default
title: "ScummVM wiki page — Terraglyph (draft)"
---

# ScummVM `Terraglyph` wiki-page content (draft)

> **What this is.** The content for the ScummVM wiki page
> `https://wiki.scummvm.org/index.php/Terraglyph`, authored here as a committed
> repo doc. It is **not** posted upstream from this WP — publishing it rides
> with the upstream-PR WP ([WP-079 §Out of scope](../work-packets/WP-079-showdown-closeout.md)).
> Produced by [WP-079](../work-packets/WP-079-showdown-closeout.md) /
> [EC-006 Step 4](../execution-checklists/EC-006-showdown-playthrough.md).
> Generation discipline: everything playable here is **Gen 1**; Gen 2/3 are
> detected but not yet supported.

---

## Scooby-Doo (TerraGlyph)

The **terraglyph** engine reimplements the TerraGlyph Interactive Studios
point-and-click adventure engine used by the Scooby-Doo CD-ROM games
(Gen 1). It reads the original discs' data directly — no fan patches, no
re-packed assets — and plays the Bink cutscenes through ScummVM's own
`Video::BinkDecoder` (the disc's `binkw32.dll` is never loaded).

Engine id: `terraglyph`. *Showdown* is declared `ADGF_TESTING` (shown in the
launcher, flagged as needing testing); *Phantom* remains `ADGF_UNSTABLE`
(hidden unless unstable games are enabled) while its room port finishes.

To see it running, browse the
[Screenshots gallery](https://github.com/barefootbetters/scooby-engine/wiki/Screenshots)
— every room, captured from our engine — or the
[screen map](https://github.com/barefootbetters/scooby-engine/wiki/Screenshots#screen-map)
for how the rooms connect, built from the engine's real exits.

## Supported titles

| Title | Game id | Generation | Status |
|---|---|---|---|
| Scooby-Doo! Showdown in Ghost Town | `showdown` | Gen 1 | **Testing** (`ADGF_TESTING`) — all rooms ported; the suspect/clue-board soft-lock is **fixed** (WP-080, fork PR #5 merged 2026-11-21); full release-verification playthrough on the fixed build in progress |
| Scooby-Doo! Phantom of the Knight | `phantomknight` | Gen 1 | In development — room port in progress |
| Scooby-Doo! Jinx at the Sphinx | `jinxsphinx` | Gen 2 | Detected only — unsupported (MMFW archive reader not implemented) |
| Scooby-Doo! Case File #1: The Glowing Bug Man | `casefile1` | Gen 3 | Detected only — unsupported |
| Scooby-Doo! Activity Challenge | `activitychallenge` | Gen 2 | Detected only — unsupported |

Only **Gen 1** (Showdown, Phantom) is playable. Gen 2 and Gen 3 titles are
recognised by the launcher but refuse to start — their archive formats
(MMFW) do not have readers yet. Case File #2 runs a different engine and is
not detected.

## Required game-data files

Point ScummVM at the disc's **`\scooby\`** directory (or the disc root).
The Gen 1 engine needs these files (all in `\scooby\`):

| File | Purpose |
|---|---|
| `TGIFILE.ART` | Art archive — rooms, sprites, cels (all graphics) |
| `object.ini` | Interactive-object / room-script table |
| `Scooby.eng` | Engine error-string table |
| `Music.dat` | Music archive (PCM) |
| `Sfx.dat` | Sound-effects archive (PCM) |
| `Voice.dat` | Voice archive (PCM) |
| `BK.NNN` | Bink cutscenes (sparse numbering; 42 on Showdown) |
| `Scooby.exe` | Used for **detection only** — the engine does not execute it |

`binkw32.dll` ships on the disc but is **not** used — ScummVM decodes Bink
itself. The bundled `AOL\`, `messagemate\`, `INSTALL\`, `Play.exe`,
`SETUP.EXE` and `showdown.cd` marker are not engine data.

## Save-state support

**Supported.** Saves use ScummVM's standard save infrastructure; the payload
is the original game's player-profile INI (the format the retail engine
itself wrote), wrapped with an `SCBY` magic and a version. Keys the engine
does not yet model are preserved verbatim across a save, so nothing is lost.

MetaEngine features declared: `kSupportsListSaves`, `kSupportsDeleteSave`,
`kSupportsLoadingDuringStartup`, `kSavesUseExtendedFormat` (save metadata,
thumbnails, dates, play time). The engine declares
`kSupportsLoadingDuringRuntime` and `kSupportsSavingDuringRuntime` (saving
pauses while a scene or an exit transition is playing).

> Note: the save/load cycle is being release-verified on the fixed build
> (WP-082). The suspect-board soft-lock that previously blocked a full run is
> resolved (WP-080). Save-state support is declared by the MetaEngine as above;
> end-to-end save→quit→reload verification is folded into the fixed-build
> playthrough.

## Known limitations

- **Gen 1 only.** Gen 2 (Jinx, Activity Challenge) and Gen 3 (Case File #1)
  are detected but unsupported.
- **No horizontal scrolling yet.** Rooms wider than the 640×480 screen
  (e.g. 1,920-pixel rooms) currently show only their left 640 pixels.
- **Testing status.** *Showdown* is `ADGF_TESTING` — believed complete and
  playable start to finish (the suspect/clue-board soft-lock that previously
  trapped the player was fixed in WP-080), but still being release-verified by
  full playthrough; expect rough edges. *Phantom* is `ADGF_UNSTABLE` (room port
  in progress).
- **English Windows discs** are what the detection entries cover.

> *Previously-blocking defect, now resolved:* opening the suspects-and-clues
> board from the toolbar magnifier used to trap the player (its back exit was
> never wired to a click). Fixed in WP-080 (fork PR #5, merged 2026-11-21): the
> board's back exit now dispatches to `leaveBy()`.

## Detection — per-variant MD5s

Detection MD5 is over the first 5,000 bytes (the ScummVM advanced-detector
default); sizes are whole-file. From
[`engines/terraglyph/detection_tables.h`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/terraglyph/detection_tables.h).

| Game id | File | Size (bytes) | MD5 (first 5000 B) |
|---|---|---|---|
| `showdown` | `Scooby.exe` | 487,473 | `a7a84eb0e66863bb699bab9fc75fdf2b` |
| `showdown` | `TGIFILE.ART` | 144,592,896 | `ba57da019a38f63b1b85d8cf83457377` |
| `showdown` | `object.ini` | 25,196 | `42db419bd6be75a49552d9e9bdeed880` |
| `phantomknight` | `Scooby.exe` | 483,377 | `c36473c3204c10d75eebf0241e35aee8` |
| `phantomknight` | `TGIFILE.ART` | 114,386,944 | `a0c28dd3e75241794cb19481496bd919` |
| `phantomknight` | `object.ini` | 28,788 | `aafe695ae3f6c2db91858661e28e1c6c` |
| `jinxsphinx` | `Scooby.exe` | 847,872 | `2df7a8e242d525e589abbd2372a80824` |
| `jinxsphinx` | `Mummy.mms` | 887,171 | `17d996eb0ed078a90ce9ab76357e81b9` |
| `jinxsphinx` | `Mummy.MMP` | 107,393,012 | `acd69eec416b74a5f2aade1c06e441ef` |
| `casefile1` | `Case File #1.exe` | 786,432 | `00a2fd4530103cecb0b2f2684ce59129` |
| `casefile1` | `Museum.MMS` | 787,946 | `f92430e7de3242a4fb7b9d8ec2ec6116` |
| `casefile1` | `MuseumCD.MMP` | 91,589,634 | `1a906c898fc25a41c812bafd85f66b5e` |
| `activitychallenge` | `Bonus.mms` | 289,844 | `b6708dba6c936d5df3355668bca45aa9` |
| `activitychallenge` | `BONUS.MMP` | 68,733,610 | `2a96b23cb24e866d65ea3cd4939c78b1` |
| `activitychallenge` | `BONUS.MMF` | 19,744,128 | `35d13d927badf3d5f6177a003b072ac6` |

Full-file SHA-256 identity locks for the Gen 1 discs are in
[`tools/exes/README`](../../tools/exes/README.md). Verified live on
2026-11-19: `--detect` on a mounted Showdown disc (`H:\scooby`) returns
`terraglyph:showdown`, and on a mounted Phantom disc (`G:\scooby`) returns
`terraglyph:phantomknight` — the two Gen 1 discs are discriminated with no false
positive, and an unrelated directory returns no game.
