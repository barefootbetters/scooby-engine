# `tools/exes/` — local executable cache

Local copies of `Scooby.exe` (and any other binaries) pulled from mounted
ISOs for analysis with `rich_header.py`, Ghidra, and other tools.

## Why this exists

Mounting and unmounting ISOs to compare binaries across titles is friction.
Copying the EXE out once per disc and keeping it locally means:

- Multi-file `rich_header.py` runs work without juggling drive letters
- Ghidra projects can point at a stable local path
- Disc unmount/re-mount doesn't break in-flight analysis

## Policy: nothing in here gets committed

The repository's `.gitignore` blocks all files in this directory except
this `README.md` and a `.gitkeep` placeholder. `Scooby.exe` and every
other binary here are copyrighted Warner Bros. / Hanna-Barbera material;
they live locally for analysis only.

## Conventional layout

```
tools/exes/
  showdown/Scooby.exe        ← from Scooby Doo Showdown in Ghost Town.iso
  phantom/Scooby.exe         ← from Scooby Doo Phantom of the Knight.iso
  jinx/Scooby.exe            ← from Scooby Doo Jinx at the Sphinx.iso
  casefile1/Scooby.exe       ← from Case File 1.iso
  casefile2/Scooby.exe       ← from Case File #2.iso
```

Per-disc subdirectory + canonical filename means:

- The `.gitignore` rule on `Scooby.exe` (already in place as a safety net)
  catches them even if `tools/exes/*` blocking is bypassed
- Wildcard runs like `tools/exes/*/Scooby.exe` work
- Each subdirectory can also hold the per-title `object.ini`, `Scooby.eng`,
  and any other files pulled from the disc for analysis

## Workflow

```powershell
# Once: create the subdirectories
$dest = "C:\www\scooby\tools\exes"
New-Item -ItemType Directory -Force `
    -Path "$dest\showdown","$dest\phantom","$dest\jinx","$dest\casefile1","$dest\casefile2" `
    | Out-Null

# Per disc: mount via Explorer → right-click → Mount, then:
Copy-Item "<drive>:\scooby\Scooby.exe" "$dest\<title>\Scooby.exe"
# Then right-click drive → Eject. Mount the next disc.
```

After all five are populated, the trio + case-files comparison is one
command — see `tools/rich_header.py` usage in the project README.

## Currently cached

Running ledger of what's in this directory. Update when a new binary lands,
including SHA-256 and a snapshot of the disc inventory so future analysis can
proceed without re-mounting. SHA-256 hashes are factual identifiers, not
copyrighted content — safe to commit here. Used by [WP-007 pre-flights](../../docs/reference/pre-flight.md)
as the Binary identity source.

**Directory casing normalized 2026-06-02** — earlier cache work landed `Showdown/`, `Phantom/`, and `Case File 1/` (mixed case + spaces); a single `Rename-Item` sweep brought them to the canonical lowercase `showdown/`, `phantom/`, `casefile1/` per the [Conventional layout](#conventional-layout) above. The four cached binaries' SHA-256s are unchanged (case-only filesystem rename).

### Jinx (Gen 2)

- **ISO source:** `C:\pcloud\SCOOBY\Scooby Doo Jinx at the Sphinx.iso`
- **Cached EXE:** `tools/exes/jinx/Scooby.exe` (847,872 bytes)
- **Original disc name:** `Scooby.exe` (no rename needed)
- **SHA-256:** `136A276872803AC99B0D050B21CC3A83F8E1608F2394C33865CFFF781FB20271`
- **Additional cached payload files (2026-06-03 — Jinx disc fully cached):** all MMFW-family archives cached under `tools/exes/jinx/`. Sizes match disc inventory exactly. After this cache the Jinx disc never needs to be re-mounted for any drafted Phase 1 WP — the table below is the source-of-truth identity lock.
- **Captured:** 2026-06-02

**Jinx cached-payload identity table** (all gitignored, all on the Jinx disc):

| File | Disc path | Size (bytes) | SHA-256 | Notes |
|---|---|---|---|---|
| `Mummy.MMF` | `E:\Mummy.MMF` | 57,219,822 | `9F173874F0C9FFC0D16B619782DF79B1EA0191093D077586AE05A4C545A0889C` | Gen 2 MMFW base archive |
| `Mummy_01.MMF` | `E:\Mummy_01.MMF` | 97,978,720 | `E0E0A17CDB559FC87F2405C85A93DB074A9E1CA0C5D7152275AE2254EA50126A` | Gen 2 MMFW split archive 1 |
| `Mummy_02.MMF` | `E:\Mummy_02.MMF` | 168,966,920 | `10F41F44C2D6EA00DDEC4F26715E72EABB64578BD799A588581C4D6302EB3836` | Gen 2 MMFW split archive 2 |
| `Mummy.MMA` | `E:\Mummy.MMA` | 34,870,606 | `3DCCA6BBC5C5A83FCD51929D18FF1D26E4495EDEE1688CBF0695CF130A3CE747` | Gen 2 MMFW audio archive |
| `Mummy.MMP` | `E:\Mummy.MMP` | 107,393,012 | `24660C414D2CF1AF23FA2853ABAD9B71A29F14B2EB8AF5B564867B768F1EAA41E` | Gen 2 MMFW primary archive |
| `Mummy.mms` | `E:\Jinx\Mummy.mms` | 887,171 | `9352F9EA5D82155C1731C81A7372D69B5F8A5B9AF12D1A3B02A70A72F969ED14` | Gen 2 engine config/script — Gen 1 `Scooby.eng` analogue |
| `Mummy_HD.MMF` | `E:\Jinx\Mummy_HD.MMF` | 10,557,374 | `419BFA72D413E1FD0C3C1D01521C9DA16CACFF0804A9A7FA18AAE1E526114B10` | HD-install variant |
| `HD.MMA` | `E:\Jinx\HD.MMA` | 8,225,330 | `98BF09C6349AF6F2A78457B4E43A9A5CABFAB2FF5FDEE16CFB76A4E127A094FA` | HD-install audio archive |
| `HD.MMP` | `E:\Jinx\HD.MMP` | 11,264,558 | `4AA0D5EF46F01D0A70E55C15B3716CB31826523F6C7E6CA5178039D1C5B1297B` | HD-install primary archive |

**Skipped this round** (not blocking any drafted WP): `cyber*.bmp` wallpaper installer screens, `IBSlogo.avi`, `TLClogo.AVI`, `WBlogo.AVI`, `Play.exe`, `Setup.exe`, `AUTORUN.INF` — none are engine-relevant. No `BK.*` cutscene files on Jinx (Gen 2 dropped Bink per [scooby-exe cross-title runtime dependencies](../../docs/formats/scooby-exe.md#cross-title-runtime-dependencies)). No `binkw32.dll` either.

**Disc inventory — root (`E:\`):**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           9/27/2001  9:29 AM                INSTALL
d----           9/18/2001  8:28 AM                Jinx
--r--           9/27/2001  9:16 AM            152 AUTORUN.INF
--r--            9/7/2001  5:11 AM        9021440 IBSlogo.avi
--r--           9/11/2001  7:23 AM       97978720 Mummy_01.MMF
--r--           9/18/2001  5:35 AM      168966920 Mummy_02.MMF
--r--           9/14/2001  7:35 AM       34870606 Mummy.MMA
--r--           9/11/2001  9:47 AM       57219822 Mummy.MMF
--r--           9/18/2001  3:11 AM      107393012 Mummy.MMP
--r--           5/16/2001  4:16 AM          45056 Play.exe
--r--           5/16/2001  4:16 AM          45056 Setup.exe
--r--            9/6/2001  6:08 AM        8221184 TLClogo.AVI
--r--           9/18/2001  5:38 AM        2180096 WBlogo.AVI
```

**Disc inventory — `E:\Jinx\`:**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
--r--            9/5/2001  5:53 AM         787510 cyber1024x768.bmp
--r--            9/5/2001  5:54 AM         308278 cyber640x480.bmp
--r--            9/5/2001  5:55 AM         481078 cyber800x600.bmp
--r--            9/7/2001  9:12 AM        8225330 HD.MMA
--r--            9/7/2001 11:45 AM       11264558 HD.MMP
--r--           9/11/2001  9:51 AM       10557374 Mummy_HD.MMF
--r--           9/19/2001  6:42 AM         887171 Mummy.mms
--r--           9/19/2001  6:49 AM         847872 Scooby.exe
```

**Notes:**

- Game files use the working name `Mummy` (the disc's internal codename for
  *Jinx at the Sphinx*). `Mummy_01.MMF`, `Mummy_02.MMF`, `Mummy.MMF`, `Mummy.MMA`,
  `Mummy.MMP`, `Mummy.mms`, `Mummy_HD.MMF` are all Gen 2 MMFW-family archives
  per [mmfw-container](../../docs/formats/mmfw-container.md).
- `Play.exe` / `Setup.exe` (45 KB each, identical size — likely the same stub
  twice) are CD launcher / installer, not the engine.
- `IBSlogo.avi` is unexpected on a TerraGlyph-era title (Jinx predates the
  TerraGlyph → IBS handoff per [scooby-exe](../../docs/formats/scooby-exe.md)).
  May indicate IBS was already involved as publisher/distributor in 2001, or
  the disc was authored later than the binary contents suggest. Worth noting,
  not pursuing now.
- `Mummy.mms` (887 KB) is a strong candidate for the Gen 2 analogue of
  Showdown's `Scooby.eng` — small, plain-data sized, root-level. Cached under
  `tools/exes/jinx/Mummy.mms` for Gen 1↔Gen 2 comparison without re-mounting.

### Showdown (Gen 1)

- **ISO source:** `C:\pcloud\SCOOBY\Scooby Doo Showdown in Ghost Town.iso`
- **Cached EXE:** `tools/exes/showdown/Scooby.exe` (487,473 bytes ≈ 476 KB)
- **Original disc name:** `Scooby.exe` at `E:\scooby\Scooby.exe` (no rename needed)
- **SHA-256:** `1328454334CDDB9518168B78BA7FFEB13BA7B772E6B52F4E2B87098D18AF7478`
- **Additional cached text files:** `tools/exes/showdown/Scooby.eng` (2,823 bytes, the engine error-strings file) and `tools/exes/showdown/object.ini` (25,196 bytes, the interactive-object table — 1,405 lines per [scooby-exe](../../docs/formats/scooby-exe.md)). Both small, both already characterized; cached locally for Gen 1↔Gen 2↔Gen 3 textual diffs without re-mounting. Gitignored.
- **Additional cached payload + runtime files (2026-06-02 — Showdown disc fully cached):** TGIFILE.ART, Music.dat, Sfx.dat, Voice.dat, and binkw32.dll cached under `tools/exes/showdown/`. Sizes match the disc inventory exactly. After this cache the Showdown disc never needs to be re-mounted for any drafted Phase 1 WP — the table below is the source-of-truth identity lock per the same SHA-256 discipline as the cached EXE.
- **Captured:** 2026-06-02

**Showdown cached-payload identity table** (all gitignored, all on the Showdown disc at `E:\scooby\`):

| File | Local path | Size (bytes) | SHA-256 | Unblocks |
|---|---|---|---|---|
| `TGIFILE.ART` | `tools/exes/showdown/TGIFILE.ART` | 144,592,896 | `B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807` | [WP-003](../../docs/work-packets/WP-003-pre-payload-region.md) palette-hunt + [WP-002](../../docs/work-packets/WP-002-tgifile-art-decoder.md) decoder |
| `Music.dat` | `tools/exes/showdown/Music.dat` | 96,182,128 | `43CC40E83F97782BDCFCE4150498BB42399AC8E37FADC0B88CE2E64A1B63EB1E` | [WP-004](../../docs/work-packets/WP-004-audio-archive-decode.md) audio index + codec |
| `Sfx.dat` | `tools/exes/showdown/Sfx.dat` | 32,197,616 | `D6E92447688AA84DA2BC8C22C00F2E0BA5ABAA9FDADFE4E6A7F979C8A924FDCC` | [WP-004](../../docs/work-packets/WP-004-audio-archive-decode.md) |
| `Voice.dat` | `tools/exes/showdown/Voice.dat` | 108,814,868 | `9DB041E42BE3E2C90650829C8FBD8DCA84DF5BC9B7EB46253CA893760761630E` | [WP-004](../../docs/work-packets/WP-004-audio-archive-decode.md) |
| `binkw32.dll` | `tools/exes/showdown/binkw32.dll` | 286,208 | `1FD7EF7873C8A3BE7E2F127B306D0D24D7D88E20CF9188894EFF87B5AF0D495F` | [WP-001](../../docs/work-packets/WP-001-ghidra-session.md) Bink version-string lookup |

**Skipped this round** (not blocking any drafted WP): 43 `BK.*` Bink cutscene files (~140 MB total). These are gameplay video assets, separately addressable via the same workflow when a future WP (Phase 4 cutscene playback verification, or a content-completeness check) needs them. The 0-byte `showdown.cd` disc-presence marker and the AOL/messagemate bundled-software directories are out of scope permanently — bundled retail-promotional content, not engine-relevant.

**Size delta vs Phantom:** Showdown's `Scooby.exe` is **exactly 4,096 bytes larger** than Phantom's (487,473 − 483,377 = 4,096 = 0x1000, one PE section-alignment unit). Suggestive of a single section-size or padding difference between the two Gen 1 binaries — not the "+6 MASM 6.13 (build 8966) compilations" Phantom has over Showdown per the [cross-title toolchain comparison](../../docs/formats/scooby-exe.md#cross-title-toolchain-comparison-engine-generations) (those would tend to *grow* Phantom, not shrink it). Worth a one-line follow-up during WP-001 to characterize what differs; not blocking for WP-007.

**Disc inventory — root (`E:\`):**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           6/18/2001  8:37 AM                AOL
d----           8/24/2001  4:21 AM                INSTALL
d----           6/18/2001  8:40 AM                messagemate
d----           8/24/2001  8:45 AM                scooby
--r--           6/18/2001  7:29 AM            167 AUTORUN.INF
--r--            6/8/2001  4:52 AM          28672 Play.exe
--r--            6/8/2001  4:52 AM          28672 SETUP.EXE
--r--           6/22/2000  4:16 AM              0 showdown.cd
```

**Disc inventory — `E:\scooby\`:**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
--r--           7/11/2000  6:14 AM         286208 binkw32.dll
--r--           8/25/2000  5:06 AM       18968800 BK.001
--r--           8/24/2000  5:32 AM        2332124 BK.002
--r--           8/30/2000  8:05 AM        2732468 BK.003
--r--           8/30/2000  9:34 AM       14212404 BK.004
--r--           8/25/2000  9:48 AM        6620608 BK.005
--r--           8/25/2000  8:15 AM       17053944 BK.006
--r--           8/29/2000  4:19 AM        5062268 BK.007
--r--           8/25/2000 10:31 AM        3537756 BK.008
--r--           8/30/2000  7:44 AM        1744836 BK.009
--r--           8/30/2000  7:49 AM        1670724 BK.010
--r--           8/30/2000  7:41 AM        1807956 BK.011
--r--           8/30/2000  7:45 AM        1816220 BK.012
--r--           8/30/2000  7:53 AM        1806140 BK.013
--r--           8/25/2000  9:34 AM        8685656 BK.014
--r--           8/24/2000  8:05 AM         962060 BK.015
--r--           8/24/2000  8:08 AM         934980 BK.016
--r--           8/24/2000  8:11 AM         977776 BK.017
--r--           8/24/2000  8:17 AM         963788 BK.018
--r--           8/24/2000  8:24 AM         942316 BK.019
--r--           8/24/2000  8:27 AM        1000052 BK.020
--r--           8/24/2000  8:30 AM         950968 BK.021
--r--           8/24/2000 10:49 AM         874440 BK.022
--r--           8/24/2000  8:44 AM         990844 BK.023
--r--           6/19/2001 11:31 AM            276 BK.025
--r--           5/10/2001  5:54 AM        2579044 BK.026
--r--           8/22/2001  3:33 AM         736500 BK.027
--r--           8/31/2000  7:44 AM         847768 BK.028
--r--           8/25/2000 11:16 AM        9340864 BK.029
--r--           8/24/2000  5:13 AM        1469528 BK.030
--r--           8/24/2000  4:59 AM        2214052 BK.031
--r--           8/25/2000 10:19 AM        4276344 BK.032
--r--           8/25/2000  9:36 AM        8544852 BK.033
--r--           8/25/2000  8:57 AM        8517968 BK.034
--r--           8/25/2000  9:12 AM        9129780 BK.035
--r--           8/25/2000  9:59 AM        7528112 BK.036
--r--           8/25/2000  9:12 AM        7625740 BK.037
--r--            8/2/2000  9:19 AM        1425764 BK.038
--r--            8/2/2000  9:22 AM        1191832 BK.039
--r--            8/2/2000 11:14 AM        1308788 BK.040
--r--            8/2/2000 11:18 AM        1349536 BK.041
--r--            8/7/2000 11:41 AM        1349148 BK.042
--r--           8/25/2000  9:43 AM        7966080 BK.058
--r--           8/31/2000 10:41 AM       96182128 Music.dat
--r--            9/1/2000  7:22 AM          25196 object.ini
--r--            6/5/2000  5:15 AM           2823 Scooby.eng
--r--           8/22/2001 11:47 AM         487473 Scooby.exe
--r--            9/1/2000  6:54 AM       32197616 Sfx.dat
--r--           8/24/2001  8:32 AM      144592896 TGIFILE.ART
--r--            9/1/2000  5:55 AM      108814868 Voice.dat
```

**Notes — disc root:**

- `showdown.cd` — 0-byte disc-identifier marker file; common pattern for CD-keyed installs to detect "is the right CD in the drive" without needing to scan archive contents.
- `AOL\` and `messagemate\` — bundled AOL signup software and *MessageMate* (a Hanna-Barbera-themed AIM utility, mid-2001 promotional cross-tie). Period-typical bundling, irrelevant to engine work.
- `Play.exe` / `SETUP.EXE` (28,672 bytes each — same size, likely the same launcher stub twice). Smaller than Jinx's 45 KB equivalents, but same role: CD launcher / installer, not the engine.
- No `IBSlogo.avi` here — Showdown is fully TerraGlyph-era (Aug 2001 disc date), pre-IBS involvement. Consistent with the Jinx note above that IBS appearing on Jinx (Sep 2001) is unexpectedly early.

**Notes — `E:\scooby\` (engine payload directory):**

All five canonical engine data files referenced in [scooby-exe](../../docs/formats/scooby-exe.md) Known facts are present and accounted for: `Scooby.exe`, `Scooby.eng`, `object.ini`, `TGIFILE.ART`, `Music.dat`, `Sfx.dat`, `Voice.dat`. This is the ground-truth confirmation that the file-I/O API surface called out in WP-007 §Background corresponds to actual files on disc.

- **`binkw32.dll`** (286,208 bytes, dated 2000-07-11) — Bink runtime confirmed at static path. Matches the imports-side prediction in [scooby-exe Cross-title runtime dependencies](../../docs/formats/scooby-exe.md#cross-title-runtime-dependencies). Version info from this DLL would let WP-001 pin the exact Bink SDK version Showdown was built against — cheap to capture while disc is mounted.
- **`BK.*` files (43 visible: BK.001–023, 025–042, 058)** — Bink cutscene videos. Numbering has visible gaps at BK.024 and BK.043–057, with BK.058 the last entry. Either gameplay uses sparse indices (likely — engine probably references BK files by ID, not iteration) or there were extra dev-only BK files that didn't ship.
- **`BK.025` is 276 bytes** — tiny vs the other BK files (~1–19 MB range). Almost certainly a stub, placeholder, or marker — not a real Bink stream at that size. Worth a one-line follow-up during WP-001 to verify it's intentional and not a corruption artifact.
- **Date clustering** — most assets carry 2000-08 / 2000-09 timestamps (engine asset build pass). `Scooby.exe` is 2001-08-22 — roughly a year later. Either long QA / localization cycle, or the binary continued iterating while the assets were locked. Phantom's binary will tell us which: if Phantom's `Scooby.exe` timestamp is materially newer with the same asset dates, binary-side iteration; if both ship the same era, shared release cycle.
- **`TGIFILE.ART` (144,592,896 bytes ≈ 138 MB)** — the asset archive at the heart of [WP-002](../../docs/work-packets/WP-002-tgifile-art-decoder.md) and [WP-003](../../docs/work-packets/WP-003-pre-payload-region.md). Size matches the offset arithmetic in WP-003 (asset entry table ends at 0x0F48, first payload starts at 0x10017E, leaving ~1 MB pre-payload region within this 138 MB total).
- **`object.ini`** (25,196 bytes, 1,405 lines per scooby-exe.md) and **`Scooby.eng`** (2,823 bytes) — both cached under `tools/exes/showdown/` per the **Additional cached files** bullet above. Avoids re-mounting for Gen 1↔Gen 2↔Gen 3 textual diffs.
- **No XML files** — consistent with the [Cross-title runtime dependencies](../../docs/formats/scooby-exe.md#cross-title-runtime-dependencies) table's "XML parser: absent" entry for Showdown. Case File #1's `libexpat.dll` will be the contrast.

### Phantom (Gen 1)

- **ISO source:** `C:\pcloud\SCOOBY\Scooby Doo Phantom of the Knight.iso`
- **Cached EXE:** `tools/exes/phantom/Scooby.exe` (483,377 bytes)
- **Original disc name:** `Scooby.exe` at `E:\scooby\Scooby.exe` (no rename needed)
- **SHA-256:** `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED`
- **Additional cached payload + runtime files (2026-06-03 — Phantom disc fully cached):** `TGIFILE.ART`, `MUSIC.DAT`, `SFX.DAT`, `VOICE.DAT`, `BINKW32.DLL`, `SCOOBY.ENG`, `OBJECT.INI` cached under `tools/exes/phantom/`. Sizes match the disc inventory exactly. After this cache the Phantom disc never needs to be re-mounted for any drafted Phase 1 WP — the table below is the source-of-truth identity lock.
- **Captured:** 2026-06-02

**Size sanity check vs Showdown:** 483,377 bytes (Phantom) ≈ ~476 KB (Showdown's reported size in [scooby-exe](../../docs/formats/scooby-exe.md)). Consistent with the Gen 1 prediction — Phantom and Showdown share the same Rich Header (Linker 5.10 build 8047) per the cross-title toolchain comparison, so binary sizes within a few percent are expected.

**Phantom cached-payload identity table** (all gitignored, all on the Phantom disc at `E:\scooby\`):

| File | Local path | Size (bytes) | SHA-256 | Unblocks |
|---|---|---|---|---|
| `TGIFILE.ART` | `tools/exes/phantom/TGIFILE.ART` | 114,386,944 | `AC24E9AE88CD7D15B1137ADBAA331FD987D8CE54B94A5A808042665BA012BF04` | [WP-002](../../docs/work-packets/WP-002-tgifile-art-decoder.md) Gen 1 cross-check |
| `MUSIC.DAT` | `tools/exes/phantom/MUSIC.DAT` | 104,324,228 | `B4EBC5F131A56B853CB76ED3A616869ADD74A1DC737D8857EDD844626CB41538` | [WP-004](../../docs/work-packets/WP-004-audio-archive-decode.md) |
| `SFX.DAT` | `tools/exes/phantom/SFX.DAT` | 30,323,432 | `F410F1BE4583163AF3E2F6ED94B69C634C55293AB4ECF3494AC03F59B8B2C2D8` | [WP-004](../../docs/work-packets/WP-004-audio-archive-decode.md) |
| `VOICE.DAT` | `tools/exes/phantom/VOICE.DAT` | 140,813,312 | `6EE9614081EFACB25A5C16A992716A133B4D9FD9E90CEA541420F949EDAE18F4` | [WP-004](../../docs/work-packets/WP-004-audio-archive-decode.md) |
| `BINKW32.DLL` | `tools/exes/phantom/BINKW32.DLL` | 286,208 | `1FD7EF7873C8A3BE7E2F127B306D0D24D7D88E20CF9188894EFF87B5AF0D495F` | [WP-001](../../docs/work-packets/WP-001-ghidra-session.md) Bink version-string — **identical to Showdown's `binkw32.dll`** |
| `SCOOBY.ENG` | `tools/exes/phantom/SCOOBY.ENG` | 2,823 | `EE9BE93A024FF9B7F5EA1C2445B711FB7C13CEF61A079A4609EDF1201CBAB19B` | Gen 1↔Gen 2 textual diff |
| `OBJECT.INI` | `tools/exes/phantom/OBJECT.INI` | 28,788 | `67B9EF7967B1EDEB7331D3D41F9EFABC326F4740A6C8D7A8781965CFE9D67870` | Gen 1↔Gen 2 textual diff |

**Skipped this round** (not blocking any drafted WP): 52 `BK.*` Bink cutscene files. `phantom.cd` (0-byte disc-presence marker), `AOL\`, `messagemate\`, `INSTALL\`, `Play.exe`, `Setup.exe`, `AUTORUN.INF` — bundled retail/promotional content, out of scope permanently.

**Notable findings from disc inventory:**

- **`BINKW32.DLL` hash is identical to Showdown's** (`1FD7EF7...`) — same Bink SDK build shipped with both Gen 1 titles, consistent with the byte-identical import tables observed in WP-007.
- **`TGIFILE.ART` is 114,386,944 bytes (≈109 MB) vs Showdown's 144,592,896 bytes (≈138 MB)** — ~25 % smaller. Phantom is a different game with a different room/asset count; the format structure should be identical but offsets will differ. WP-002 decoder must not hardcode Showdown-specific sizes.
- **`SCOOBY.ENG` is 2,823 bytes — exact byte-size match with Showdown's** `Scooby.eng`. Strong candidate for identical or near-identical content (shared error-string table across Gen 1 titles). WP-008 textual diff will confirm.
- **`OBJECT.INI` is 28,788 bytes vs Showdown's 25,196 bytes** — Phantom has a larger interactive-object table, consistent with it being a different (possibly larger) game.
- **`Scooby.exe` timestamp is 2001-08-22** — same date as Showdown's binary. Both Gen 1 binaries share a release-window build date, consistent with a shared release cycle rather than long binary-side iteration. Closes the open question from the Showdown notes.
- **BK.025 is again exactly 276 bytes** — confirmed intentional cross-Gen-1 stub/placeholder, not corruption.

**Disc inventory — root (`E:\`):**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           6/18/2001  9:58 AM                AOL
d----           8/15/2001 10:33 AM                INSTALL
d----           6/18/2001  9:48 AM                messagemate
d----           8/24/2001  8:42 AM                scooby
--r--           6/18/2001  7:29 AM            167 AUTORUN.INF
--r--           10/4/2000  9:37 AM              0 phantom.cd
--r--            6/8/2001  4:52 AM          28672 Play.exe
--r--            6/8/2001  4:52 AM          28672 Setup.exe
```

**Disc inventory — `E:\scooby\`:**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
--r--           7/11/2000  6:14 AM         286208 BINKW32.DLL
--r--           9/27/2000 11:06 AM       12150216 BK.001
--r--           10/3/2000 12:00 PM        2307912 BK.002
--r--           10/4/2000  8:39 AM        2210988 BK.003
--r--           10/3/2000 11:54 AM        2226820 BK.004
--r--           8/29/2000  4:33 AM        1963316 BK.005
--r--           9/20/2000  8:56 AM        3420336 BK.006
--r--           9/22/2000  9:10 AM        2593452 BK.007
--r--           9/20/2000  6:22 AM        2765120 BK.008
--r--           9/18/2000  9:14 AM        2148368 BK.009
--r--           9/15/2000  8:16 AM        3993408 BK.010
--r--           9/15/2000 10:52 AM        2226524 BK.011
--r--            9/5/2000  7:38 AM        1115812 BK.013
--r--            9/5/2000  7:26 AM         992792 BK.014
--r--            9/5/2000  7:49 AM        1232140 BK.015
--r--            9/5/2000  7:42 AM        1186856 BK.016
--r--            9/5/2000  7:46 AM         990332 BK.017
--r--           9/28/2000  7:58 AM       10333496 BK.018
--r--           6/19/2001 11:31 AM            276 BK.025
--r--           5/10/2001  5:54 AM        2579044 BK.026
--r--           8/22/2001  3:33 AM         736500 BK.027
--r--           8/31/2000  7:44 AM         847768 BK.028
--r--           8/22/2000 12:22 PM        1266292 BK.029
--r--           8/10/2000  5:25 AM        1589720 BK.030
--r--           8/21/2000 10:02 AM         829840 BK.031
--r--           8/29/2000  8:28 AM        1306836 BK.032
--r--           8/29/2000  8:31 AM        1166796 BK.033
--r--           8/29/2000  8:24 AM        3417132 BK.034
--r--           10/3/2000 12:31 PM        3111740 BK.035
--r--           8/17/2000 11:42 AM        1274604 BK.036
--r--           9/15/2000  8:07 AM        4205532 BK.037
--r--           10/4/2000  8:55 AM        3880560 BK.038
--r--           10/2/2000 12:10 PM        1870680 BK.039
--r--           9/22/2000  6:39 AM        2502104 BK.040
--r--           9/25/2000 10:32 AM        2989760 BK.041
--r--           9/25/2000 10:30 AM        1739316 BK.042
--r--           9/11/2000 10:03 AM        1158436 BK.043
--r--           9/20/2000 11:22 AM        2014008 BK.044
--r--           9/20/2000  6:23 AM        4389220 BK.045
--r--           9/20/2000  3:15 AM        4428044 BK.046
--r--           9/20/2000  3:34 AM        5000012 BK.047
--r--           9/20/2000  5:40 AM        4036864 BK.048
--r--           9/18/2000 11:25 AM        4621648 BK.049
--r--           9/22/2000  6:11 AM        2839972 BK.054
--r--           9/20/2000  5:15 AM        8049992 BK.055
--r--           9/27/2000 12:32 PM        1595332 BK.056
--r--           9/22/2000  6:11 AM        3246420 BK.057
--r--           9/18/2000  8:44 AM        3647232 BK.058
--r--           10/4/2000  8:49 AM        1403276 BK.059
--r--            9/5/2000 10:54 AM        3538336 BK.060
--r--           9/15/2000  9:09 AM        1861040 BK.061
--r--           8/21/2000 11:23 AM         782844 BK.062
--r--           8/21/2000 11:27 AM         914920 BK.063
--r--            9/5/2000  4:52 AM        2027680 BK.064
--r--           8/22/2000 12:19 PM        1067672 BK.065
--r--           10/3/2000 11:55 AM        2331632 BK.066
--r--           10/3/2000 12:04 PM        2284120 BK.067
--r--           10/4/2000 11:40 AM      30323432 SFX.DAT
--r--           9/19/2000 10:44 AM      104324228 MUSIC.DAT
--r--           10/3/2000 12:45 PM          28788 OBJECT.INI
--r--            6/5/2000  5:15 AM           2823 SCOOBY.ENG
--r--           8/22/2001 11:51 AM         483377 Scooby.exe
--r--           8/24/2001  8:19 AM      114386944 TGIFILE.ART
--r--           9/29/2000 10:22 AM      140813312 VOICE.DAT
```

### Case File #1 (Gen 3)

- **ISO source:** `C:\pcloud\SCOOBY\Case File 1.iso`
- **Mount letter at capture:** `F:\` (WP-007 capture 2026-06-02); remounted as `E:\` (payload cache 2026-06-03)
- **Cached EXE:** `tools/exes/casefile1/Scooby.exe` (786,432 bytes ≈ 768 KB)
- **Original disc name:** `Case File #1.exe` at `\MUSEUM\Case File #1.exe` — renamed to `Scooby.exe` per the safety-net policy (the `#` character is fine in a quoted PowerShell path but causes friction in markdown links and URL contexts).
- **SHA-256:** `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8`
- **Additional cached payload files (2026-06-03 — Case File #1 disc fully cached):** all MMFW-family archives cached under `tools/exes/casefile1/`. Sizes match disc inventory exactly. After this cache the Case File #1 disc never needs to be re-mounted for any drafted Phase 1 WP — the table below is the source-of-truth identity lock.
- **Captured:** 2026-06-02

**Case File #1 cached-payload identity table** (all gitignored):

| File | Disc path | Size (bytes) | SHA-256 | Notes |
|---|---|---|---|---|
| `libexpat.dll` | `\MUSEUM\libexpat.dll` | 122,880 | `(captured 2026-06-02 — see WP-007 baseline)` | Gen 3 XML-parser dependency |
| `Museum.MMS` | `\MUSEUM\Scripts and Resources\Museum.MMS` | 787,946 | `87C5AA98854D5A082C1206620F38D954F4DDDF1789451A80246E63E2BF86E8AA` | Gen 3 engine config/script — `.mms` analogue to Jinx's `Mummy.mms` |
| `MuseumHD.MMA` | `\MUSEUM\Scripts and Resources\MuseumHD.MMA` | 4,533,392 | `2791F8D79E6EAAB94A681D265CCA3813901DF6EE2495DB7CF70E9EE71BF84EAD` | HD-install audio archive |
| `MuseumHD.MMP` | `\MUSEUM\Scripts and Resources\MuseumHD.MMP` | 31,949,566 | `5B8D40445D4919F573F1831A380F4505A495943717418A44642E0AF4660807AF` | HD-install primary archive |
| `MuseumCD.MMA` | `\Scripts and Resources\MuseumCD.MMA` | 25,378,516 | `34DBCDEF83279DABBA3C6E1BF09234DAFC6AC6E842BE946D266997D7709DE1ED` | CD-streaming audio archive |
| `MuseumCD.MMP` | `\Scripts and Resources\MuseumCD.MMP` | 91,589,634 | `95C4E72EECC050F73FA7FF68E061BA87D88E20C628DB04F6A3989722903106C2` | CD-streaming primary archive |

**Skipped** (not blocking any drafted WP): `wall.exe` + `wall*.bmp` (wallpaper installer), all `.avi` files (`ExitJoke`, `GhostCapture`, `INTRO_01/02/03`, `IBSlogo`, `TLClogo`, `WBlogo`), `PLAY.EXE`, `AUTORUN.INF`, `User's Guide.pdf`, `Groovy Goodies\`, `PPG Demo\`, `Printables\`, `TLC\`, `HD\`, `INSTALL\` — none are engine-relevant.

**Disc inventory — root (`F:\`):**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           9/26/2002  2:52 PM                Groovy Goodies
d----           9/16/2002  3:53 AM                HD
d----           9/26/2002 11:50 AM                INSTALL
d----           9/27/2002 10:03 AM                MUSEUM
d----           9/25/2002  6:49 AM                PPG Demo
d----           9/26/2002  3:57 AM                Printables
d----           9/27/2002 10:05 AM                Scripts and Resources
d----           9/16/2002  3:57 AM                TLC
--r--           9/12/2002  2:59 AM            152 AUTORUN.INF
--r--           6/12/2002 10:09 PM          45056 PLAY.EXE
--r--           9/27/2002  7:18 AM        2799933 User's Guide.pdf
```

**Notes — disc root:**

- **Disc structure is materially different from Gen 1/2.** Showdown / Phantom put the engine payload in `\scooby\`; Jinx in `\Jinx\`. Case File #1 has no such subdirectory — and no `Case File #1.exe` at root. The binary is in `\MUSEUM\`, consistent with Jinx's `\Jinx\` pattern of using the game's working name.
- **`\MUSEUM\Scripts and Resources\`** holds engine-specific archives (`Museum.MMS`, `MuseumHD.MMA`, `MuseumHD.MMP`); **`\Scripts and Resources\`** (root-level) holds disc-globals (`MuseumCD.MMA`, `MuseumCD.MMP`) and all AVI videos. Both now fully cached.

`F:\MUSEUM\` was the right answer — EXE confirmed at `F:\MUSEUM\Case File #1.exe`. Listing below.

**Disc inventory — `F:\MUSEUM\`:**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           9/27/2002 10:03 AM                Scripts and Resources
--r--           9/27/2002  8:56 AM         786432 Case File #1.exe
--r--            6/3/2002 11:22 AM         122880 libexpat.dll
--r--           9/26/2002  2:28 PM          36864 wall.exe
--r--           9/25/2002  4:58 AM        2359352 wall1024x768.bmp
--r--           9/25/2002  4:59 AM         921656 wall640x480.bmp
--r--           9/25/2002  4:59 AM        1440056 wall800x600.bmp
```

**Disc inventory — `F:\MUSEUM\Scripts and Resources\`** *(nested; engine-specific assets)*:

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
--r--           9/27/2002  8:53 AM         787946 Museum.MMS
--r--           9/27/2002  7:42 AM        4533392 MuseumHD.MMA
--r--           9/27/2002  8:53 AM       31949566 MuseumHD.MMP
```

**Reframe of earlier hypothesis:** I'd predicted `F:\MUSEUM\Scripts and Resources\` would hold loose XML files + plain-text scripts (interpreting the directory name literally). Wrong — it holds three MMFW-family archives. The "Scripts and Resources" name is a *human-readable label for the engine's payload directory*, not a description of file types inside it. The Gen 3 data-pipeline rewrite isn't "plain text → XML files in the open" — it's "many specific named files (object.ini, Scooby.eng, BK.*, Music/Sfx/Voice.dat) → fewer MMFW archives with semantic names". XML lives inside the archives, parsed by `libexpat.dll` at load time.

**Disc inventory — `F:\Scripts and Resources\`** *(root-level; disc-globals — intros, logos, CD-streaming archives)*:

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
--r--           9/27/2002  3:21 AM        8138752 ExitJoke.avi
--r--           9/27/2002  6:35 AM       14055424 GhostCapture.avi
--r--           6/27/2002  4:05 AM        5477674 IBSlogo.avi
--r--           9/27/2002  2:59 AM        8775680 INTRO_01.avi
--r--           9/27/2002  6:16 AM       14376960 INTRO_02.avi
--r--           9/27/2002  3:32 AM       31412224 INTRO_03.avi
--r--           9/27/2002  7:42 AM       25378516 MuseumCD.MMA
--r--           9/27/2002  8:55 AM       91589634 MuseumCD.MMP
--r--           9/26/2002  5:46 AM        2793472 TLClogo.avi
--r--           9/10/2002  6:35 AM        2032832 WBlogo.avi
```

**Notes — Gen 3 architectural shift (load-bearing finding):**

This listing is the **structural payoff** for the [engine lineage finding](../../docs/01-VISION.md#engine-lineage-2026-06-finding). Three concrete Gen 3 shifts vs Gen 1/2, all confirmed disc-side:

1. **Bink → raw AVI for cutscenes.** `F:\Scripts and Resources\` contains seven `.avi` files (`ExitJoke`, `GhostCapture`, `INTRO_01/02/03`, plus three logo videos) and zero `BK.*` files. No `binkw32.dll` anywhere in `MUSEUM\` either. Confirms the [Cross-title runtime dependencies](../../docs/formats/scooby-exe.md#cross-title-runtime-dependencies) table prediction that Gen 3 dropped Bink. ImageBuilder Software switched to whatever Win32 AVI playback path was available (likely `AVIFile`/`MCI` from `winmm.dll` — confirmable in WP-007's import table).
2. **XML parser introduced.** `libexpat.dll` (122,880 bytes, dated 2002-06-03) sits next to `Case File #1.exe`. Static-path Gen 3 dependency — confirms the [Cross-title runtime dependencies](../../docs/formats/scooby-exe.md#cross-title-runtime-dependencies) "XML parser: present" entry. WP-007's import-table extraction will name the libexpat symbols Case File #1 actually calls.
3. **MMFW archive layout changed — `.MMF` retired, `.MMS`/`.mms` retained, CD/HD/base naming pattern carried forward.** Revised from the initial reading after the `F:\MUSEUM\Scripts and Resources\` listing landed:
   - **Jinx (Gen 2) archive surface** (5 files, 4 extensions): `.MMF` + `.MMA` + `.MMP` + `.mms` (lowercase), across `Mummy.*`, `Mummy_01/02.*`, `Mummy_HD.*`, `HD.*`.
   - **Case File #1 (Gen 3) archive surface** (5 files, 3 extensions): `.MMS` (uppercase) + `.MMA` + `.MMP`, across `MuseumCD.*` (root), `Museum.*` and `MuseumHD.*` (nested under `MUSEUM\Scripts and Resources\`).
   - **`.MMF` retired between Gen 2 and Gen 3** — no `.MMF` files appear anywhere on the Case File #1 disc surface examined so far. Its contents either merged into the surviving extensions or migrated to a different format.
   - **`.MMS`/`.mms` retained** (capitalization shifted lowercase → uppercase). Sizes are similar across generations: Jinx's `Mummy.mms` is 887,171 bytes (≈866 KB), Case File #1's `Museum.MMS` is 787,946 bytes (≈770 KB). The size proximity + naming pattern strongly suggests `.MMS` is the Gen 2/3 engine config / scripting archive — the architectural successor to Showdown's `Scooby.eng` (2,823 bytes plain text) scaled up to a packed archive.
   - **CD / HD / base naming pattern carried forward** — Jinx had `Mummy.*` (base) + `Mummy_HD.*` (HD-install variant) + `HD.*` (shared HD assets); Case File #1 has `MuseumCD.*` (CD-streaming variant) + `Museum.*` (base) + `MuseumHD.*` (HD-install variant). Same three-tier architecture; the Gen 3 rename to consistent `<title>CD/<title>/<title>HD` suffixes is just convention-tightening.
   - [mmfw-container](../../docs/formats/mmfw-container.md) needs a Gen 2 vs Gen 3 extension-comparison table that captures these findings.

**Notes — `F:\MUSEUM\` payload directory:**

- **`Case File #1.exe` size (786,432 bytes ≈ 768 KB).** Sits between Showdown/Phantom (476–483 KB) and Jinx (828 KB) — bigger than Gen 1, slightly smaller than Gen 2. Consistent with Case File #1 being inherited Jinx-era code plus IBS additions per the code-level inheritance finding in [scooby-exe](../../docs/formats/scooby-exe.md) (the Linker 5.10 build 8168 entries shared with Jinx).
- **`wall.exe` (36 KB) + `wall*.bmp`** — wallpaper installer, not engine-relevant. The three BMPs (1024x768, 800x600, 640x480) are the same three resolution targets as Jinx's `cyber*.bmp` install splash screens.
- **No `Scooby.eng` / no `object.ini`** at this depth. Gen 1/2's plain-text engine config + interactive-object table are presumably inside `F:\MUSEUM\Scripts and Resources\Museum.MMS` — that archive's 770 KB size lines up with Jinx's `Mummy.mms` (866 KB), and both sit in the same architectural slot. The data-pipeline rewrite is: many specific named files (`object.ini`, `Scooby.eng`, `BK.*`, `Music/Sfx/Voice.dat` on Showdown) → fewer MMFW archives with semantic names, parsed via `libexpat.dll`-driven XML inside. WP-007's strings dump on `Case File #1.exe` should surface the MMFW filenames it opens, confirming this split.
- **Two `Scripts and Resources` directories at different depths** — root (`F:\Scripts and Resources\`) holds disc-globals (intros, logos, CD-streaming archives `MuseumCD.*`); nested (`F:\MUSEUM\Scripts and Resources\`) holds engine-specific archives (`Museum.*` base + `MuseumHD.*` HD-install variant). Both listed below.

**Notes — `F:\Scripts and Resources\` (root):**

- **`IBSlogo.avi` (5.5 MB)** — IBS logo present where expected on a Gen 3 disc, contrast with its anomalous appearance on Jinx (Gen 2, Sep 2001). Two readings still in play: either IBS was already publishing for TerraGlyph in 2001 (so Jinx's IBS logo is normal), or Jinx's disc-author timeline lags its engineering timeline by ~12 months. Cross-title `binkw32.dll` version-string compare during WP-001 may help distinguish.
- **`MuseumCD.MMA` (25 MB) + `MuseumCD.MMP` (92 MB)** — Gen 3 MMFW-family archives. "MuseumCD" is the Case File #1 internal codename, mirroring Jinx's "Mummy" codename. Per-title internal codenames track per-title development branches: TerraGlyph used "Mummy" for Jinx, IBS used "MuseumCD" for Case File #1.
- **Date cluster** — all assets dated 2002-09 except `IBSlogo.avi` (June) and `WBlogo.avi` (also September). Tight ship window for the engine assets, consistent with a late-stage build.

### Case File #2 (Gen 4 — new engine generation)

- **ISO source:** `C:\pcloud\SCOOBY\` (Case File #2 disc)
- **Mount letter at capture:** `E:\` (2026-06-03)
- **Cached EXE:** `tools/exes/casefile2/Scooby.exe` (774,144 bytes) — original disc name `Case File #2.exe` at `E:\HD\Case File #2\Case File #2.exe`, renamed per policy
- **SHA-256:** `AB2B71FEEFF0777B26928E95C99F9936F5C4D87FE321ED4913B8956C83772BC8`
- **Additional cached payload files (2026-06-03 — fully cached):** runtime DLLs, HD bulk archive, all loose scripts, all CD-streaming `.bul` archives, and the CF#1 bonus demo. See identity tables below.
- **Captured:** 2026-06-03

**WP-005 finding — Case File #2 is NOT Gen 3.** The disc structure and runtime dependencies are radically different from Case File #1. This is a new engine generation:

| Signal | Case File #1 (Gen 3) | Case File #2 (Gen 4) |
|---|---|---|
| Archive format | MMFW (`.MMS`/`.MMA`/`.MMP`) | `.bul` bulk archives + `.inx` index |
| Script format | Packed inside MMFW archives | **Loose `.mps` + `.xml` files on disc** |
| Video | Raw AVI (`winmm.dll`/MCI) | **Bink returned** (`binkw32.dll` 375 KB — newer SDK than Gen 1's 286 KB) |
| Audio middleware | DirectSound (dynamic) | **Miles Sound System** (`mss32.dll` 370 KB) — new dependency |
| XML parser | `libexpat.dll` (static path) | XML still present but possibly inlined or via different path |
| Disc layout | `\MUSEUM\` + `\Scripts and Resources\` | `\HD\Case File #2\` (HD install) + `\rsc\` (CD streaming) |
| Date | 2002-09 | **2003-08** (one year later) |

This closes WP-005 Case File #2 verification. Phase 5 scope rule "Extended-medium-confidence (+ Jinx, requires Gen 2 parser)" and "Stretch (+ Case Files, requires Gen 3 adapters)" needs a revision note: Case File #2 requires a **Gen 4 adapter**, not a Gen 3 adapter.

**Case File #2 cached-payload identity table:**

| File | Disc path | Size (bytes) | SHA-256 | Notes |
|---|---|---|---|---|
| `Scooby.exe` | `E:\HD\Case File #2\Case File #2.exe` | 774,144 | `AB2B71FEEFF0777B26928E95C99F9936F5C4D87FE321ED4913B8956C83772BC8` | Gen 4 engine binary |
| `binkw32.dll` | `E:\HD\Case File #2\binkw32.dll` | 375,808 | `2D0AE23A6175DC7B635C402A5E7E9542E923C0D1C376A8C5EF876CA0D5959D23` | Bink runtime — newer SDK (375 KB vs Gen 1's 286 KB); dated 2003-04-16 |
| `mss32.dll` | `E:\HD\Case File #2\mss32.dll` | 370,688 | `7855B8FBAE917CB8449F2D4361AB61B5ECEC4DF0A11130D797CB0AA99B4260EA` | Miles Sound System — new Gen 4 audio dependency; dated 2003-03-17 |
| `TLC.ini` | `E:\HD\Case File #2\TLC.ini` | 29 | `AB7A80B8485D6E47FFC9A01459C1927317788DC318499829C52299D63E48B38C` | Engine config stub |
| `HD.bul` | `E:\HD\Case File #2\rsc\HD.bul` | 81,058,607 | `5E997E6F44D6B904364FC5100DA39DBBD38E1666AD2A19E5756B5E5585953E4D` | HD-install bulk archive (single file replaces multi-file MMFW pattern) |

**Loose scripts** (cached under `tools/exes/casefile2/scripts/` — all from `E:\HD\Case File #2\scripts\`):

These are plain-text `.mps` (script bytecode or source?) and `.xml` (layout/data) files, not packed in archives. 40+ files covering every scene (`S01`–`S07`), every activity (`A01`–`A08`), and global scaffolding. Extremely useful for Gen 4 format research — no unpacking required.

**CD-streaming `.bul` archives** (cached under `tools/exes/casefile2/rsc/`):

| File | Size (bytes) | SHA-256 |
|---|---|---|
| `root.inx` | 226,796 | `653640131F1F950D701033E89AF8A8A0E917DFB33E8014A2B773153AD59EC8DB` |
| `root.txt` | 544,073 | `883CB6EBF8C17685488FC58D7BFB43AE27B487B9784040CAFEE0DEEB486459EB` |
| `Common.bul` | 746,804 | `2BB5F8D1CCB270229E56855540E8E5C41E22DF014C92F16904142220EA9B0D54` |
| `Toolbar.bul` | 11,222,179 | `48575EE086E78CCA0729AEC94D147A9D559118AA86A5B9EF9BD9B166FF3C2F18` |
| `S01Courtyard.bul` | 9,300,387 | `D8E9383DDF9EAEF672190D6B1A250957AB35D1B7817A631063B664C820237FC6` |
| `S02PalaceEntrance.bul` | 3,493,920 | `55FF515368E4F66F275C0015A93356F7AE7322A34FDBC5DA7AC3591D1BE23365` |
| `S03Palace.bul` | 3,180,478 | `1957DC6A1F695C9611B3BBA13FEF0C8347573FFE69C21FEA77CF4F7A7C8ED60F` |
| `S04TreasureRoom.bul` | 7,086,868 | `7B7CFB7967EDC3A90B03AE631CC7BC53DB4104BBB24BFE56F6D43883C973CBAF` |
| `S05Shops.bul` | 6,398,919 | `F26CF594DD14989D702A73F0288794A658877B708DADB5C8807C09B59EECE303` |
| `S06Restaurant.bul` | 5,190,704 | `2B60487FB99E754BEDD7485673396B5FE532816958235A45270DB371B6ABB839` |
| `S07CraftStand.bul` | 6,952,145 | `BDF485B20D39E07B7C52D4A494762B3B949C242D65EE776E0B17B4E9DF70BBBC` |
| `A01MixedUpDoors.bul` | 1,555,674 | `5BD96BC5A0C6168B0F6DE7E2E2A376677F0F0782BA22907554B56F3D3842ECC3` |
| `A02RotatingBricks.bul` | 4,646,891 | `E6BFFED133B2D6C88002A23111E6FB32963844B3E5B714FBD0428ACF2DC17BA7` |
| `A03LamplightMaze.bul` | 13,761,105 | `D1ADFDC0B95F68AC05C3E6BC8E8F2DA41EA76392126B2B87F6DE8F06B6869637` |
| `A04SleepyTiger.bul` | 7,966,916 | `A9E478B0F7D3304961A7A75F2B7696887A5CA4B514D77BCA7350D529FFF0753D` |
| `A05LanternLogic.bul` | 3,628,818 | `47E8DA986F3426E2FD18D371BC10E628C4E684538140A8810ECA4B7097F6F032` |
| `A06WokRecipes.bul` | 10,807,137 | `DAABA36D02E98D39862D233C0569D16A37F5401E7B201CF365E1245B4BD2F7E5` |
| `A07ChineseCostumes.bul` | 1,851,471 | `7EB4D26113AE98C9D9A182F8990BED482BCF2E24220C86DBD1DB4E51BA86B429` |
| `A08Certificate.bul` | 1,790,592 | `05AE08889B8D6D94FBC15E5379E996936E5D127D03D505A0256BB3E2E3EE3BD2` |
| `A08InformationKiosk.bul` | 1,776,583 | `5FEB101DCF3C347342F6E8E0C3B255E40BD906958C55093D09A836C9E4B43462` |
| `SC2Levels.bul` | 682,679 | `17942232F7007EC8A3A2754A545E0D5362C81C3E65CDE8AA9C42AD075F84E284` |
| `SC8Credits.bul` | 5,916,139 | `475DA471B2829DD19946062263024968FF0B1F4204348F3A52CF3AF16E6C722F` |

**Skipped** (not blocking any WP): all `.bik` cutscene videos in `E:\rsc\` (23 files, ~250 MB total), `INSTALL\`, `TLC\`, `GroovyGoodies\PPG2Demo\` (different engine/title entirely), `Play.exe`, `AUTORUN.INF`, `LICENSE.TXT`, `ReadMe.txt`, `User's Guide.pdf`.

**Bonus — Case File #1 demo** (cached under `tools/exes/casefile2/casefile1-demo/`):

Found in `E:\GroovyGoodies\Scooby1Demo\`. A second Gen 3 binary — useful for WP-005 cross-check and as a second data point on the Gen 3 MMFW format.

| File | Disc path | Size (bytes) | SHA-256 | Notes |
|---|---|---|---|---|
| `Scooby-demo.exe` | `E:\GroovyGoodies\Scooby1Demo\Case File #1 Demo.exe` | 675,840 | `140C645E5C5DA5A023459B4247472FC239D5D3F9E7BC68FE0357A08582E30648` | Gen 3 demo binary — smaller than full CF#1 EXE (786,432) |
| `MuseumDemo.MMS` | `...\Scripts and Resources\MuseumDemo.MMS` | 183,532 | `3D343469E14A52C402E93BA0DC46B883CC13AD796B597F5EAB66093D5C0F4524` | Demo engine config — much smaller than full `Museum.MMS` (787,946) |
| `MuseumDemo.MMA` | `...\Scripts and Resources\MuseumDemo.MMA` | 10,791,198 | `3757720996875938C7980E15E92F5B42D9D1E5417887A0AC7F22168278FBB43B` | Demo audio archive |
| `MuseumDemo.MMP` | `...\Scripts and Resources\MuseumDemo.MMP` | 22,964,977 | `2AED5924A936D6894913CE0835C30F5DD6D367E0147A617DB83577E56CEA81C3` | Demo primary archive |

**Disc inventory — root (`E:\`):**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           8/27/2003                          GroovyGoodies
d----           8/27/2003                          HD
d----           8/27/2003                          INSTALL
d----           8/27/2003                          rsc
d----           8/27/2003                          TLC
--r--                                          161 AUTORUN.INF
--r--                                         7715 LICENSE.TXT
--r--                                        45056 Play.exe
--r--                                          281 ReadMe.txt
--r--                                      1466489 User's Guide.pdf
```

**Disc inventory — `E:\HD\Case File #2\`:**

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----                                              rsc
d----                                              scripts
--r--           4/16/2003 12:19 PM         375808 binkw32.dll
--r--           8/27/2003  4:12 AM       81058607 HD.bul   (in rsc\)
--r--           3/17/2003  8:15 AM         370688 mss32.dll
--r--           8/27/2003  5:16 AM         774144 Case File #2.exe
--r--           7/18/2003  4:08 AM             29 TLC.ini
```

---

### Case File #3 (*Frights! Camera! Mystery!*) — OUT OF SCOPE

**⚠️ Not an IBS engine title.** CF#3 was published by **The Learning Company / Broderbund** and authored in
**Macromedia Director** — a completely different engine and publisher from the IBS/Humble lineage. It shares the
Scooby-Doo license but is architecturally unrelated to this project.

- **ISO source:** `C:\pcloud\SCOOBY\Case File 3.iso` (or equivalent)
- **Publisher:** The Learning Company (TLC) / Broderbund
- **Engine:** Macromedia Director (confirmed via `Director` string in PE, TLC version resource)
- **Version resource:** `4.1.07` / `Scooby-Doo! Case File #3 - Frights! Camera! Mystery!.exe`
- **Disc layout:** Single-file installer at disc root — no accessible engine payload without installation

**Disc inventory (`E:\`):**

```
--r--    AUTORUN.inf              87 bytes
--r--    scooby_icon.ico       24,506 bytes
--r--    Scooby-Doo!.exe  181,897,154 bytes  (~174 MB self-contained installer)
```

**Cached for reference only** — installer EXE kept locally as `Scooby-CF3-Installer.exe` to avoid remounting the
disc if the Director projector structure ever becomes useful for comparison or archival context.

**CF#3 cached-payload identity table:**

| File | SHA-256 | Disc source | Size |
|------|---------|-------------|------|
| `Scooby-CF3-Installer.exe` | `22041FF004C4A237833F006571A1EDFC49C7797AEDDAEB91ED2FAAD0F0C4160C` | `E:\Scooby-Doo!.exe` | 181,897,154 |

**Why out of scope:** This project targets the IBS engine family (Gen 1–4 above). Director titles require a
completely separate reverse-engineering approach (Dirapi / ProjectorRays tooling) and would not share any engine
code, asset formats, or scripting surface with the IBS engine reimplementation. If a Director adapter is ever
desired it would be a separate project.

