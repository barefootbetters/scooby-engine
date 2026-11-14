---
layout: default
title: "ScummVM Integration Contract"
---

# ScummVM Integration Contract

**Status:** Scaffold — sections populated as Phase 2 implementation lands
**ScummVM version pin:** `c553503d9d433726b22b43b3a6a0a86fd00125e9` (`scummvm/scummvm` `master`, 2026-11-13, "SCUMM: Hotspot highlighting with object names"). This is the base of the fork's `scooby-engine` branch ([barefootbetters/scummvm](https://github.com/barefootbetters/scummvm/tree/scooby-engine/engines/scooby)), pinned by [WP-010](work-packets/WP-010-scummvm-scaffold.md). Signatures below are checked against this commit.
**Engine location:** `engines/scooby/` (within the ScummVM fork)
**Vision doc reference:** [`docs/01-VISION.md`](01-VISION.md) — "Engine Contract (ScummVM Requirements)" section is the high-altitude principles; this doc owns the concrete API surface.

---

## What this doc is

The `scooby` engine must conform to ScummVM's engine architecture and
integration model — not as a general reimplementation, but as a
ScummVM-compatible engine module. This document enumerates the concrete
integration points: which classes to subclass, which APIs to call, which
files to ship, and what each Phase 2 work item has to satisfy before
upstream will accept the engine.

This doc has its own lifecycle: it tracks ScummVM upstream conventions
(which change between releases) separately from the vision doc (which
tracks the project's evolving understanding of the games themselves).
Pin a ScummVM commit hash in the header above before relying on any
specific signature called out below.

---

## Acceptance gates (TL;DR)

The following are the upstream-merge-blocking items. Phase 5 cannot ship
a PR unless every one of these is true:

1. Engine compiles cleanly against the pinned ScummVM commit.
2. Engine is registered via `MetaEngineDetection` and discovered by ScummVM's launcher.
3. Detection works on at least *Showdown* without false positives on unrelated game files.
4. All file I/O goes through `Common::File` / `Common::Archive` — no `fopen`, no `std::ifstream`, no raw POSIX/Win32 file calls.
5. All audio plays through `Audio::Mixer`; no direct DirectSound or platform audio calls.
6. Bink video plays through ScummVM's built-in `Video::BinkDecoder`; `binkw32.dll` is not loaded.
7. Engine is single-threaded; no `pthread`, no `std::thread`, no worker threads.
8. Code conforms to ScummVM's code style (see §11).
9. All source files carry the GPL-3.0 license header.
10. Engine is declared `ADGF_TESTING` (or higher) in detection.

---

## 1. Engine class

**Requirement:** Implement a subclass of `Engine` providing the main run loop.

**Upstream reference:** `engines/engine.h`, `engines/engine.cpp`. See ScummVM wiki [HOWTO-Add a new engine](https://wiki.scummvm.org/index.php?title=HOWTO-Add_a_new_engine).

**Acceptance criterion:** `ScoobyEngine::run()` drives a cooperative event-pumping loop (calling `_system->getEventManager()->pollEvent()` each frame), returns `Common::kNoError` on clean exit, and contains no platform-specific surfaces or windowing calls. `syncSoundSettings()` is called once on startup (constructor or top of `run()`, per the engine's preference) before any audio plays, so the user's ScummVM volume preferences take effect on the first frame.

**Implementation notes:** WP-010 scaffold (2026-11-13): `ScoobyEngine::run()` sets up 640 × 480 RGB565 with `initGraphics()`, returns `kUnsupportedColorMode` if the backend cannot provide it, calls `syncSoundSettings()`, then pumps events through a `Graphics::FrameLimiter` at 60 fps until `shouldQuit()`.

---

## 2. MetaEngine and detection

**Requirement:** Provide both a `MetaEngineDetection` subclass (for game discovery) and a `MetaEngine` subclass (for engine instantiation). These are deliberately split in current ScummVM.

**Upstream reference:** `engines/metaengine.h`, `engines/advancedDetector.h`. Recent example to copy structure from: [BOLT engine](https://wiki.scummvm.org/index.php/BOLT) and [beholdnec/scummvm-funhouse](https://github.com/beholdnec/scummvm-funhouse).

**Acceptance criterion:** The ScummVM launcher's "Add Game" dialog discovers a mounted *Showdown* disc without prompting the user to identify it manually.

**Implementation notes:** WP-010 and WP-012 (2026-11-14). `ScoobyMetaEngineDetection` derives from `AdvancedMetaEngineDetection<Scooby::ScoobyGameDescription>` and `ScoobyMetaEngine` from `AdvancedMetaEngine<Scooby::ScoobyGameDescription>`, so `createInstance()` receives the extended description (§3) and passes it to the engine. Detection was checked with `scummvm --detect --path=<disc root>` on each mounted ISO. That is the same advanced-detector code the "Add Game" dialog runs, but the dialog itself was not clicked through.

---

## 3. Game detection table (`ADGameDescription`)

**Requirement:** Define an extended `ADGameDescription` array (`AdvancedMetaEngineDetection` with a per-entry `gen` flag — see below). Signature files vary by engine generation per the Phase 1 Engine Lineage finding in [`docs/01-VISION.md`](01-VISION.md#engine-lineage-2026-06-finding):

| Generation | Titles | Signature files |
|---|---|---|
| Gen 1 | Showdown, Phantom | `Scooby.exe`, `TGIFILE.ART`, `object.ini` (all in `\scooby\`) |
| Gen 2 | Jinx | `Scooby.exe`, `Mummy.mms` (in `\Jinx\`), `Mummy.MMP` (disc root) |
| Gen 2 | Activity Challenge | `Bonus.mms`, `BONUS.MMP`, `BONUS.MMF` (all at the disc root; `Scooby.exe` is in `\INSTALL\HDINSTALL\`, so it is not used) |
| Gen 3 | Case File #1 | `Case File #1.exe` (in `\MUSEUM\`), `Museum.MMS` (in `\MUSEUM\Scripts and Resources\`), `MuseumCD.MMP` (in `\Scripts and Resources\`) |

Case File #2 runs a different engine and has no entry ([WP-005](work-packets/WP-005-engine-family-check.md)). Signature files are the ones WP-012 matches. Earlier drafts of this table listed `libexpat.dll` and loose `*.xml` files for Gen 3; the XML is inside the MMFW archives.

Match on file presence, size and MD5. The MD5 covers the first 5,000 bytes, the advanced detector's default, so detection stays fast on 100 MB archives. Never match on ISO filename or disc directory layout.

**Per-entry generation flag.** Each detection-table row carries a `gen` field (or equivalent flag in the `flags` bitfield) recording which generation the title belongs to. The engine reads this at startup and selects the appropriate archive parser, config parser, and cutscene path. This is the load-bearing piece — without it, the engine would need either runtime format sniffing (slow + brittle) or per-title hardcoded paths (PR-blocking).

**Upstream reference:** `engines/advancedDetector.h`; `engines/<engine>/detection_tables.h` patterns across existing engines. For multi-format engines see existing engines with a `flags` field carrying format-version info (e.g. AGI's `GType_*` field).

**Acceptance criterion:** Each of the four in-scope ISOs is detected with the correct generation flag (Showdown=1, Phantom=1, Jinx=2, Case File #1=3). *Activity Challenge* is detected as Gen 2 ([WP-013](work-packets/WP-013-activity-challenge-engine-check.md)); it is not in a Phase 5 tier yet, so it stays `ADGF_UNSUPPORTED`. Case File #2 (a different engine, per WP-005) and Case File #3 (a Director title) are not detected. No false positives on a directory containing unrelated DOS/Windows-era game files. *(Revised 2026-11-14 by WP-012; the original asked for five ISOs with Case File #2 as Gen 3.)*

**Implementation notes:** WP-012 (2026-11-14). `detection.h` declares:

```cpp
enum ScoobyGeneration { kGen1 = 1, kGen2 = 2, kGen3 = 3 };

struct ScoobyGameDescription {
	AD_GAME_DESCRIPTION_HELPERS(desc);

	ADGameDescription desc;
	ScoobyGeneration generation;
};
```

The engine reads it with `ScoobyEngine::getGeneration()`. `detection_tables.h` has five entries (the fifth added after WP-013):

| Game id | Title | Generation | Flag |
|---|---|---|---|
| `showdown` | *Showdown in Ghost Town* | 1 | `ADGF_UNSTABLE` |
| `phantomknight` | *Phantom of the Knight* | 1 | `ADGF_UNSTABLE` |
| `jinxsphinx` | *Jinx at the Sphinx* | 2 | `ADGF_UNSUPPORTED` |
| `casefile1` | *Case File #1: The Glowing Bug Man* | 3 | `ADGF_UNSUPPORTED` |
| `activitychallenge` | *Activity Challenge* | 2 | `ADGF_UNSUPPORTED` |

- **Game ids.** `phantom` and `jinx` are already used by MADS (*Return of the Phantom*) and Glk/Adrift. Two engines with the same id make a bare id on the command line ambiguous, so the entries use `phantomknight` and `jinxsphinx`. `activity` is SCUMM's (*Putt-Putt & Fatty Bear's Activity Pack*), hence `activitychallenge`.
- **Flags.** Gen 1 is `ADGF_UNSTABLE` while it is being built. Gen 2 and Gen 3 are detected but `ADGF_UNSUPPORTED`, so the launcher refuses to start them until their archive readers exist. Moving an entry to a playable flag is a Phase 3 or Phase 5 change, not a table restructure.
- **Directories.** `_maxScanDepth = 3` and `_directoryGlobs` = `scooby`, `jinx`, `museum`, `scripts and resources`. Matching is by base name. The disc root works for all five titles. *Activity Challenge*'s three signature files are at the root, so it needs no glob. For Showdown and Phantom the `\scooby\` directory alone also works. Jinx and Case File #1 keep their signature files in two directories, so they need the root.
- **Values.** Sizes and MD5s are in the fork's [`detection_tables.h`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/detection_tables.h). The sizes match the [`tools/exes/` identity tables](../tools/exes/README.md#currently-cached).

---

## 4. Resource access — `Common::File` and `Common::Archive`

**Requirement:** All disc reads go through ScummVM's file abstractions. The engine must not contain `fopen`, `std::ifstream`, `CreateFileA`, or any other direct file API.

**Upstream reference:** `common/file.h`, `common/archive.h`, `common/fs.h`. `SearchMan` for path resolution.

**Acceptance criterion:** A `grep -E '(fopen|std::ifstream|CreateFile[AW]?)' engines/scooby/` returns no matches outside comments. (`Common::File::open()` is permitted — only direct OS file APIs are banned.) The `TGIFILE.ART` parser opens its archive via `Common::File::open(name)` and exposes individual assets as `Common::SeekableReadStream`.

**Implementation notes:** WP-014 (2026-11-14). `Scooby::ArtArchive` (`engines/scooby/art_archive.{h,cpp}`) is a `Common::Archive` over the Gen 1 `TGIFILE.ART`.

- **Index.** The index is the room and object sector descriptors plus the name table ([tgifile-art §Header layout](formats/tgifile-art.md#header-layout)). The "asset entry table" this note first named turned out not to be offsets.
- **Members.** Room and object names are the members, looked up case-insensitively. Both titles' names are unique even ignoring case.
- **Streams.** `createReadStreamForMember()` opens its own `Common::File` and returns a `SeekableSubReadStream` over the block's whole sector span, which is what the original engine reads.
- **ANIM names** are not members. `findName()` resolves them to their id.
- **Validation.** `open()` checks every count, descriptor span, id and name against the file size and the descriptor arrays. It returns false with a warning rather than indexing bad data.
- **Startup.** The engine adds the disc's `scooby` directory to `SearchMan`, so a game added at the disc root finds the file. Then it opens `TGIFILE.ART` in `run()`, for Gen 1 only.
- **Debugging.** At `resource` level 2 the engine logs every block. At level 3 it also reads each one back through the archive and checks its size word. The console's `art_list` and `art_info` commands show the same index.

The grep in the acceptance criterion finds nothing in `engines/scooby/` at fork commit `155144012a`.

---

## 5. Graphics output

**Requirement:** Render through ScummVM's graphics manager (`OSystem::getPaletteManager()`, `OSystem::copyRectToScreen()`, `OSystem::updateScreen()`). No DirectDraw, no Direct3D, no platform surfaces. Palette handling per the `PaletteManager` interface.

**Upstream reference:** `common/system.h` (`OSystem`), `graphics/surface.h`, `graphics/paletteman.h`.

**Acceptance criterion:** Room 1 of *Showdown* renders at the original resolution in ScummVM's window on Windows, macOS, and Linux without per-platform code paths in the engine. *(Revised 2026-11-14 by WP-015: the original also asked for "the original palette", but there is none. Pixels are RGB565 truecolour, per WP-002 and WP-001.)*

**Implementation notes:** WP-015 (2026-11-14).

- **Screen.** The engine asks for 640 × 480 RGB565 (`initGraphics()`) and returns `kUnsupportedColorMode` if the backend can't provide it. It draws into its own `Graphics::Surface` and hands that to `copyRectToScreen()`. There are no per-platform paths.
- **Decoding.** `Scooby::Cel` (`engines/scooby/cel.{h,cpp}`) decodes one cel from a room or object block into 16-bit words plus a coverage map: transparent, opaque (mask A) or translucent (mask B). It handles RLE (big-endian words), raw (little-endian) and solid cels. Every run, offset and mask span is checked against the block and the image.
- **Drawing.** `drawRoomLayers()` draws each used layer slot's frame record in the opaque pass. Translucent (mask B) blending waits for sprites, since backgrounds have no mask B.
- **Checked on both Gen 1 titles.**
  - Every cel's pixels and coverage match `probe_art.py` (MD5 per cel): 9,111 in Showdown, 5,810 in Phantom.
  - The screen after drawing room 0 matches the probe's composite pixel for pixel.
- **Wide rooms.** Rooms 1,920 pixels wide show their left 640 pixels; scrolling is not done yet.
- **Whole rooms (WP-016, 2026-11-14).** `Scooby::RoomRenderer` (`engines/scooby/room.{h,cpp}`) builds a room as the original sets it up on entry. It creates the layer sprites, then one sprite per placement at step 0 of its sequence, in the traced sprite tree. Placement kinds come from `object.ini`, which is read through `Common::INIFile`. It paints back to front into a room-sized RGB565 surface. `Cel::draw()` copies opaque pixels and blends translucent ones with the original 565 blitter's formula and tables ([tgifile-art §Cel format](formats/tgifile-art.md#cel-format)).
  - For all 69 Showdown and 53 Phantom rooms, the draw order and room surface (MD5) match an exact 565 model.
  - An optional `start_room` key in the game's config domain picks the first room. It is a test convenience to revisit before Phase 5.
- **Animation (WP-017, 2026-11-14).** `Scooby::Room` keeps the sprite tree it builds on entry, and each placed sprite plays its sequence with the original player.
  - The engine loop runs `elapsed_ms × 36 / 1000` game ticks from `OSystem::getMillis()`, as `0x435BC0` does, and redraws when a step changes.
  - Cels are decoded once per room and cached.
  - All 122 rooms match a reference model at tick 0 and tick 37.

---

## 6. Audio

**Requirement:** All audio plays through `Audio::Mixer` via the engine's `_mixer` member. Decoders come from `audio/decoders/` if a standard codec is identified in Phase 1; otherwise a new decoder lives under `audio/decoders/` and is contributed alongside the engine PR (or carried in-engine if it is genuinely Scooby-specific).

**Upstream reference:** `audio/mixer.h`, `audio/audiostream.h`, `audio/decoders/` (raw, ADPCM, MP3, Vorbis, FLAC).

**Acceptance criterion:** Music, SFX, and voice all route through `Audio::Mixer`. Volume sliders in the ScummVM Options dialog control the engine's audio correctly. No direct DirectSound or platform audio calls.

**Implementation notes:** *TBD. Codec identification is owned by `docs/formats/audio-archives.md`. If the codec turns out to be Miles Sound System or another licensed format, an upstream conversation about decoder strategy precedes the PR.*

---

## 7. Video playback (Bink)

**Requirement:** Cutscenes play through ScummVM's built-in `Video::BinkDecoder`. The engine must not load `binkw32.dll` or otherwise depend on the original RAD runtime.

**Upstream reference:** `video/bink_decoder.h`, `video/video_decoder.h`.

**Acceptance criterion:** Every `BK.XXX` cutscene from *Showdown* plays start-to-end in ScummVM with correct audio sync and no fallback to external Bink runtime.

**Implementation notes:** *TBD. Confirm during Phase 4 that ScummVM's decoder handles all Bink variants present on the disc; the older Bink 1 variant is well-supported but the disc may carry edge cases.*

---

## 8. Save / load

**Requirement:** Either implement save/load via ScummVM's `Engine::saveGameState` / `Engine::loadGameState` overrides **and** declare the relevant `MetaEngineFeature` flags consistently in `MetaEngine::hasFeature()`, or explicitly return `false` for those flags and verify the ScummVM GUI correctly hides save/load options. The two must agree — overriding `saveGameState` without also returning `true` from `hasFeature(kSupportsSavingDuringRuntime)` silently breaks the GUI. If the original engine has a save format, prefer reading it for compatibility; if not, document a clean ScummVM-native save format.

**Upstream reference:** `engines/engine.h` (save/load virtuals), `engines/metaengine.h` (`MetaEngineFeature::kSupportsSavingDuringRuntime`, `kSupportsListSaves`, etc.), `common/savefile.h`.

**Acceptance criterion:** Either (a) save/load works through ScummVM's standard dialogs and a state saved before a room transition restores correctly after engine restart, or (b) the engine returns `MetaEngineFeature` flags indicating no save support, and the ScummVM GUI correctly hides save/load options.

**Implementation notes:** *TBD. Original save format is owned by `docs/formats/scooby-exe.md` Findings → "Save-game format" (deferred until Phase 4 per the vision).*

---

## 9. Debug channels

**Requirement:** Declare debug channels as a `DebugChannelDef` table returned from `MetaEngineDetection::getDebugChannels()`; the engine framework registers them. (At the pin, engines no longer call `DebugMan.addDebugChannel()` directly. That was this section's original wording.) Use `debugC(level, channel, ...)` for diagnostic output. No `printf`, no `fprintf(stderr, ...)`, no `std::cout`.

**Upstream reference:** `common/debug.h`, `common/debug-channels.h`.

**Acceptance criterion:** At minimum these channels exist: `resource` (file loading), `graphics` (rendering), `audio` (mixer routing), `script` (`object.ini` interpretation), `input` (event handling). `scummvm --debugflags=resource scooby:showdown` produces meaningful output.

**Implementation notes:** WP-010 (2026-11-13). The channels are declared in `engines/scooby/detection.h` (enum) and `detection.cpp` (table). WP-001 used the same names as Ghidra label prefixes ([`wp001-labels.txt`](../tools/ghidra-scripts/wp001-labels.txt)).

| Id | Enum | Name | Covers |
|---|---|---|---|
| 1 | `kDebugResource` | `resource` | Archive and file loading (`TGIFILE.ART`, `.dat`, `MMFW`) |
| 2 | `kDebugGraphics` | `graphics` | Cel decoding and rendering |
| 3 | `kDebugAudio` | `audio` | Mixer routing and sound archives |
| 4 | `kDebugScript` | `script` | `object.ini` and room logic |
| 5 | `kDebugInput` | `input` | Event handling, hit tests |

At the pin, channel values are ids starting at 1, not bit masks.

---

## 10. Build system integration

**Requirement:** Three files in `engines/scooby/` participate in ScummVM's build:

- `module.mk` — make rules listing every `.o` the engine produces; must include both `detection.cpp` and the engine sources as separate compilation units
- `configure.engine` — engine declaration (name, optional dependencies, default state). For a fresh `ADGF_TESTING` engine, default state should be **disabled** — users opt in explicitly. Flipping to default-enabled is a later change once the engine has shipped at least one stable release.
- `POTFILES` — lists source files that contain user-visible translatable strings (e.g. `metaengine.cpp`, `detection.cpp` if they have `_("…")` calls). If the engine has no translatable strings at all (likely for English-only edutainment titles), `POTFILES` can be an empty file or omitted; do not invent placeholder entries.

**Detection/engine split requirement:** Detection code (`MetaEngineDetection`) must live in `detection.cpp` and be linked independently from the engine code (`ScoobyEngine`). This is mandatory in current ScummVM — the detection plugin loads without the full engine at game-scan time. Do not put engine logic in `detection.cpp` and do not put detection table data in `scooby.cpp`.

**Upstream reference:** any existing engine's `module.mk` (e.g. `engines/sci/module.mk`), `configure.engine`. ScummVM's `configure` script picks these up automatically when the directory exists.

**Acceptance criterion:** `./configure --enable-engine=scooby && make` produces a `scummvm` binary that includes the engine. `./configure --disable-engine=scooby && make` produces one that omits it cleanly. No platform-specific build hacks.

**Implementation notes:** WP-010 (2026-11-13), at the pin, with MSYS2 UCRT64 (g++ 16.2.0, SDL2 2.32.10, GNU Make 4.4.1). The toolchain is chosen for Phase 2–5. Both builds ran out of tree:

- `configure --disable-all-engines --enable-engine=scooby && make -j32`: configure lists only `Scooby-Doo (TerraGlyph)` as builtin, and the four `engines/scooby/*.o` compile with no warnings. `scummvm.exe --list-engines` shows `scooby`, and `--list-debugflags=scooby` shows the five §9 channels.
- `configure --disable-engine=scooby && make -j32` (the default engine set, 38 minutes): configure lists scooby under "Engines Skipped". `scummvm.exe --list-engines` lists 97 engines without it. Only `engines/scooby/detection.o` is compiled, because at the pin configure builds detection for every engine by default ("building detection features for all engines... yes"). That is the detection/engine split working: detection compiles and links without `scooby.o`, `console.o` or `metaengine.o`.

`configure.engine` is `add_engine scooby "Scooby-Doo (TerraGlyph)" no "" "" "highres 16bit" ""`: off by default, and it needs the 640 × 480 and 16-bit features. `module.mk` puts `scooby.o`, `console.o` and `metaengine.o` in `MODULE_OBJS` and `detection.o` in `DETECT_OBJS`. There is no `POTFILES` because there are no translatable strings yet.

---

## 11. Code style and licensing

**Requirement:** Code conforms to ScummVM's house style — based on broadly the Linux kernel style with ScummVM-specific deviations (tabs for indentation, K&R braces, specific naming conventions, no exceptions). Every source file carries the GPL-3.0-or-later header used elsewhere in the tree.

**Upstream reference:** [ScummVM Code Formatting Conventions](https://wiki.scummvm.org/index.php/Code_Formatting_Conventions); license header on any existing engine source file.

**Acceptance criterion:** Files pass ScummVM's `devtools/code_check.sh` (or whatever the current lint script is at the pinned commit) with zero warnings. License headers present on every `.cpp`/`.h` produced by the engine.

**Implementation notes:** *TBD. Add a local pre-commit hook running ScummVM's lint to catch drift early.*

---

## 12. Upstream PR checklist

The PR submitted to `scummvm/scummvm` (Phase 5 deliverable) must satisfy:

- [ ] Engine declared `ADGF_TESTING` (not stable) for initial merge
- [ ] Detection code (`MetaEngineDetection`) is in `detection.cpp`, separate from engine code — confirmed by building detection-only
- [ ] All acceptance gates from "Acceptance gates (TL;DR)" above pass
- [ ] ScummVM wiki page exists at `https://wiki.scummvm.org/index.php/Scooby` describing: supported titles, known limitations, game-data file list, save-state support status
- [ ] Required game data files documented (so players know what to point ScummVM at)
- [ ] MD5 hashes recorded for every detected variant
- [ ] Commit messages follow ScummVM's convention (`SCOOBY: <subsystem>: <description>`)
- [ ] No copyrighted game data, no decoded asset blobs, no `binkw32.dll` in the PR
- [ ] Engine builds on the three reference platforms (Win/macOS/Linux) in ScummVM's CI
- [ ] Complies with upstream's [`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md) (present at the pin; recorded 2026-11-13, WP-010). It requires:
  - AI assistance disclosed in the PR description;
  - no AI (co-)authorship of code;
  - commit and PR messages written by a human;
  - for a whole-engine submission, a human primary maintainer who joins the team and can maintain the engine without AI.

  `.github/workflows/check-commit-authors.yml` closes any PR whose commits carry a `Co-Authored-By:` trailer naming Claude, Copilot, Cursor or Codex. The fork's scaffold commits carry one. How this project meets the policy is an open decision for Jeff, not settled here.

---

## References

- [ScummVM HOWTO: Add a New Engine](https://wiki.scummvm.org/index.php?title=HOWTO-Add_a_new_engine)
- [ScummVM Code Contribution Guidelines](https://wiki.scummvm.org/index.php/Code_Contribution_Guidelines)
- [ScummVM Code Formatting Conventions](https://wiki.scummvm.org/index.php/Code_Formatting_Conventions)
- [ScummVM BOLT engine](https://wiki.scummvm.org/index.php/BOLT) — recent newly contributed engine
- [beholdnec/scummvm-funhouse](https://github.com/beholdnec/scummvm-funhouse) — BOLT development fork (model to follow)
- Vision doc: [`docs/01-VISION.md`](01-VISION.md) — high-altitude principles
- Format specs: [`docs/formats/tgifile-art.md`](formats/tgifile-art.md), [`docs/formats/audio-archives.md`](formats/audio-archives.md), [`docs/formats/scooby-exe.md`](formats/scooby-exe.md)
