---
layout: default
title: "ScummVM Integration Contract"
---

# ScummVM Integration Contract

**Status:** Scaffold — sections populated as Phase 2 implementation lands
**ScummVM version pin:** TBD — set when `scummvm/scummvm` is forked. Record commit hash here so the contract is reproducible.
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

**Implementation notes:** *TBD — populate during WP-002-equivalent (engine scaffold).*

---

## 2. MetaEngine and detection

**Requirement:** Provide both a `MetaEngineDetection` subclass (for game discovery) and a `MetaEngine` subclass (for engine instantiation). These are deliberately split in current ScummVM.

**Upstream reference:** `engines/metaengine.h`, `engines/advancedDetector.h`. Recent example to copy structure from: [BOLT engine](https://wiki.scummvm.org/index.php/BOLT) and [beholdnec/scummvm-funhouse](https://github.com/beholdnec/scummvm-funhouse).

**Acceptance criterion:** The ScummVM launcher's "Add Game" dialog discovers a mounted *Showdown* disc without prompting the user to identify it manually.

**Implementation notes:** *TBD.*

---

## 3. Game detection table (`ADGameDescription`)

**Requirement:** Define an extended `ADGameDescription` array (`AdvancedMetaEngineDetection` with a per-entry `gen` flag — see below). Signature files vary by engine generation per the Phase 1 Engine Lineage finding in [`docs/01-VISION.md`](01-VISION.md#engine-lineage-2026-06-finding):

| Generation | Titles | Signature files |
|---|---|---|
| Gen 1 | Showdown, Phantom | `Scooby.exe`, `TGIFILE.ART`, `object.ini`, `Scooby.eng` |
| Gen 2 | Jinx | `Scooby.exe` (in title-named subdir), `Mummy*.MMF`, `HD.MMA`, `HD.MMP` |
| Gen 3 | Case File #1, Case File #2 | `Case File #N.exe`, `*.MMP`, `*.MMA`, `libexpat.dll`, `*.xml` launcher configs |

Match on file presence + size; MD5 only for version differentiation. Never match on ISO filename or disc directory layout.

**Per-entry generation flag.** Each detection-table row carries a `gen` field (or equivalent flag in the `flags` bitfield) recording which generation the title belongs to. The engine reads this at startup and selects the appropriate archive parser, config parser, and cutscene path. This is the load-bearing piece — without it, the engine would need either runtime format sniffing (slow + brittle) or per-title hardcoded paths (PR-blocking).

**Upstream reference:** `engines/advancedDetector.h`; `engines/<engine>/detection_tables.h` patterns across existing engines. For multi-format engines see existing engines with a `flags` field carrying format-version info (e.g. AGI's `GType_*` field).

**Acceptance criterion:** Each of the five in-scope candidate ISOs is detected with the correct generation flag (Showdown=1, Phantom=1, Jinx=2, Case File #1=3, Case File #2=3 predicted). Case File #3 (Flash re-release) is correctly rejected. No false positives on a directory containing unrelated DOS/Windows-era game files.

**Implementation notes:** *TBD. Cross-reference `docs/formats/tgifile-art.md` (Gen 1) and `docs/formats/mmfw-container.md` (Gen 2/3) for the MD5 / size values to embed here. The `gen` flag is the cleanest extension point — Phase 3 archive code can dispatch on it without expanding the detection table again later.*

---

## 4. Resource access — `Common::File` and `Common::Archive`

**Requirement:** All disc reads go through ScummVM's file abstractions. The engine must not contain `fopen`, `std::ifstream`, `CreateFileA`, or any other direct file API.

**Upstream reference:** `common/file.h`, `common/archive.h`, `common/fs.h`. `SearchMan` for path resolution.

**Acceptance criterion:** A `grep -E '(fopen|std::ifstream|CreateFile[AW]?)' engines/scooby/` returns no matches outside comments. (`Common::File::open()` is permitted — only direct OS file APIs are banned.) The `TGIFILE.ART` parser opens its archive via `Common::File::open(name)` and exposes individual assets as `Common::SeekableReadStream`.

**Implementation notes:** *TBD. The asset entry table from `docs/formats/tgifile-art.md` becomes the index used by a `Common::Archive` subclass that surfaces logical asset IDs.*

---

## 5. Graphics output

**Requirement:** Render through ScummVM's graphics manager (`OSystem::getPaletteManager()`, `OSystem::copyRectToScreen()`, `OSystem::updateScreen()`). No DirectDraw, no Direct3D, no platform surfaces. Palette handling per the `PaletteManager` interface.

**Upstream reference:** `common/system.h` (`OSystem`), `graphics/surface.h`, `graphics/paletteman.h`.

**Acceptance criterion:** Room 1 of *Showdown* renders at the original resolution, with the original palette, in ScummVM's window on Windows, macOS, and Linux without per-platform code paths in the engine.

**Implementation notes:** *TBD. Resolution and palette format determined by Phase 1 `TGIFILE.ART` decode work.*

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

**Requirement:** Register debug channels via `DebugMan.addDebugChannel()` in the engine constructor. Use `debugC(level, channel, ...)` for diagnostic output. No `printf`, no `fprintf(stderr, ...)`, no `std::cout`.

**Upstream reference:** `common/debug.h`, `common/debug-channels.h`.

**Acceptance criterion:** At minimum these channels exist: `resource` (file loading), `graphics` (rendering), `audio` (mixer routing), `script` (`object.ini` interpretation), `input` (event handling). `scummvm --debugflags=resource scooby:showdown` produces meaningful output.

**Implementation notes:** *TBD. Channel taxonomy is owned by this doc — record final names + assigned bits here.*

---

## 10. Build system integration

**Requirement:** Three files in `engines/scooby/` participate in ScummVM's build:

- `module.mk` — make rules listing every `.o` the engine produces; must include both `detection.cpp` and the engine sources as separate compilation units
- `configure.engine` — engine declaration (name, optional dependencies, default state). For a fresh `ADGF_TESTING` engine, default state should be **disabled** — users opt in explicitly. Flipping to default-enabled is a later change once the engine has shipped at least one stable release.
- `POTFILES` — lists source files that contain user-visible translatable strings (e.g. `metaengine.cpp`, `detection.cpp` if they have `_("…")` calls). If the engine has no translatable strings at all (likely for English-only edutainment titles), `POTFILES` can be an empty file or omitted; do not invent placeholder entries.

**Detection/engine split requirement:** Detection code (`MetaEngineDetection`) must live in `detection.cpp` and be linked independently from the engine code (`ScoobyEngine`). This is mandatory in current ScummVM — the detection plugin loads without the full engine at game-scan time. Do not put engine logic in `detection.cpp` and do not put detection table data in `scooby.cpp`.

**Upstream reference:** any existing engine's `module.mk` (e.g. `engines/sci/module.mk`), `configure.engine`. ScummVM's `configure` script picks these up automatically when the directory exists.

**Acceptance criterion:** `./configure --enable-engine=scooby && make` produces a `scummvm` binary that includes the engine. `./configure --disable-engine=scooby && make` produces one that omits it cleanly. No platform-specific build hacks.

**Implementation notes:** *TBD.*

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

---

## References

- [ScummVM HOWTO: Add a New Engine](https://wiki.scummvm.org/index.php?title=HOWTO-Add_a_new_engine)
- [ScummVM Code Contribution Guidelines](https://wiki.scummvm.org/index.php/Code_Contribution_Guidelines)
- [ScummVM Code Formatting Conventions](https://wiki.scummvm.org/index.php/Code_Formatting_Conventions)
- [ScummVM BOLT engine](https://wiki.scummvm.org/index.php/BOLT) — recent newly contributed engine
- [beholdnec/scummvm-funhouse](https://github.com/beholdnec/scummvm-funhouse) — BOLT development fork (model to follow)
- Vision doc: [`docs/01-VISION.md`](01-VISION.md) — high-altitude principles
- Format specs: [`docs/formats/tgifile-art.md`](formats/tgifile-art.md), [`docs/formats/audio-archives.md`](formats/audio-archives.md), [`docs/formats/scooby-exe.md`](formats/scooby-exe.md)
