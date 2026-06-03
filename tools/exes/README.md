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
- **Captured:** 2026-06-02

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
  Showdown's `Scooby.eng` — small, plain-data sized, root-level. Not in WP-007
  scope but flagged for future Gen 2 format research.

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
- **Captured:** 2026-06-02

**Size sanity check vs Showdown:** 483,377 bytes (Phantom) ≈ ~476 KB (Showdown's reported size in [scooby-exe](../../docs/formats/scooby-exe.md)). Consistent with the Gen 1 prediction — Phantom and Showdown share the same Rich Header (Linker 5.10 build 8047) per the cross-title toolchain comparison, so binary sizes within a few percent are expected.

**Disc inventory — root (`E:\`):**

```
(pending — run `dir E:` while disc is mounted)
```

**Disc inventory — `E:\scooby\`:**

```
(pending — run `dir E:\scooby` while disc is mounted)
```

### Case File #1 (Gen 3)

- **ISO source:** `C:\pcloud\SCOOBY\Case File 1.iso`
- **Mount letter at capture:** `F:\` (not `E:\` like the Gen 1/2 discs above — Jeff had Showdown still mounted on `E:\` when Case File #1 was mounted)
- **Cached EXE:** `tools/exes/casefile1/Scooby.exe` (786,432 bytes ≈ 768 KB)
- **Original disc name:** `Case File #1.exe` at `F:\MUSEUM\Case File #1.exe` — renamed to `Scooby.exe` per the safety-net policy (the `#` character is fine in a quoted PowerShell path but causes friction in markdown links and URL contexts).
- **SHA-256:** `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8`
- **Additional cached file:** `tools/exes/casefile1/libexpat.dll` (122,880 bytes, dated 2002-06-03) — the Gen 3 XML-parser dependency. Cached for cheap version-string lookup during WP-001 without re-mounting; also gitignored.
- **Captured:** 2026-06-02

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

- **Disc structure is materially different from Gen 1/2.** Showdown / Phantom put the engine payload in `\scooby\`; Jinx in `\Jinx\`. Case File #1 has no such subdirectory — and no `Case File #1.exe` at root. The binary is presumably in one of the engine-looking subdirectories below; `\MUSEUM\` is the strongest candidate (Case File #1's plot — "The Glowing Bug Man" — is set in a museum, and the casing matches Jinx's `\Jinx\` pattern of using the game's working name).
- **Date cluster** — everything is 2002-09. ImageBuilder Software era; consistent with the [engine lineage finding](../../docs/01-VISION.md#engine-lineage-2026-06-finding) (Gen 3 = post-TerraGlyph IBS continuation).
- **`PLAY.EXE` is 45 KB** — exact match for Jinx's `Play.exe` size. Same launcher stub binary carried forward through the engine generations.
- **No `IBSlogo.avi` at root** — likely lives in a subdirectory now (the `TLC` and `INSTALL` dirs are candidates), unlike Jinx which had it at root.
- **`User's Guide.pdf`** — the only user-facing PDF on any disc surveyed so far. Period-typical for boxed retail product; consistent with Case File #1 being the most polished/late-era of the four titles.
- **Subdirectory inventory needed to locate the EXE:**
  - `F:\MUSEUM\` — strongest candidate (matches the `\<gamename>\` convention)
  - `F:\Scripts and Resources\` — secondary candidate (the name itself is interesting for Gen 3 — implies a more data-driven, script-resource-separated architecture than Gen 1/2; this is also where `libexpat.dll` and XML files might live per the [Cross-title runtime dependencies](../../docs/formats/scooby-exe.md#cross-title-runtime-dependencies) "XML parser: present" entry for Case File #1)
  - `F:\HD\` — possibly hard-drive install staging
  - `F:\INSTALL\` — installer-side, less likely to hold the runtime EXE

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

### Case File #2 (Gen 3, predicted)

*Not yet cached.*

