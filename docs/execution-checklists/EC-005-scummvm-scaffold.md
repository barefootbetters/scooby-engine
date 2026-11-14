---
layout: default
title: "EC-005: ScummVM Scaffold Checklist"
---

# EC-005: ScummVM fork + `engines/scooby/` scaffold checklist

**Paired WP:** [WP-010](../work-packets/WP-010-scummvm-scaffold.md)
**Purpose:** Step-by-step checklist for forking ScummVM, creating a
compilable empty engine skeleton, and pinning the baseline commit hash.

The ScummVM build system on Windows has more moving parts than most projects —
correct `module.mk` entries, `configure.engine` syntax, and the
detection/engine compilation split all need to be right before a single line
of game code is written. This checklist executes them in an order that catches
each failure as early as possible.

---

## Pre-flight

- [x] Pre-flight verdict: **READY** — complete [docs/reference/pre-flight](../reference/pre-flight.md) and commit the filled-in copy before proceeding; `NOT READY` blocks this session *[pre-flight-WP-010-2026-11-13](../reference/pre-flight-WP-010-2026-11-13.md).*
- [x] Windows build toolchain installed — record which one: __________ *MSYS2 UCRT64, g++ 16.2.0 (installed 2026-11-13, Jeff's choice; kept through Phase 5).*
  - mingw-w64 (most common contributor path): `gcc --version`
  - or MSVC: `cl /?`
- [x] SDL2 development libraries present — confirm `sdl2-config --version` or SDL2 include path *`mingw-w64-ucrt-x86_64-SDL2`, `sdl2-config --version` 2.32.10.*
- [x] git installed and GitHub credentials configured: `git config user.email`
- [x] ScummVM Windows build guide read (in `scummvm/scummvm` repo: `doc/compiling/` or `README.md`) *No MSYS2 guide in the tree at the pin; built with configure/make from the UCRT64 shell.*
- [x] `C:\www\scummvm\` target directory does **not** yet exist (avoids clobber) *Deviation: the clone is `C:\dev\scummvm` (code lives under `C:\dev`, D-24739).*

---

## Step 1 — Fork on GitHub (5 min)

- [x] Navigate to `https://github.com/scummvm/scummvm` *Fork made earlier on 2026-11-13.*
- [x] Click **Fork** → owner: `barefootbetters`, repo name: `scummvm`
- [x] Note the fork's default branch name: __________ (likely `master`) *`master`.*
- [x] Fork URL confirmed: `https://github.com/barefootbetters/scummvm`

---

## Step 2 — Clone fork + add upstream remote (5 min)

```
git clone https://github.com/barefootbetters/scummvm.git C:\www\scummvm
cd C:\www\scummvm
git remote add upstream https://github.com/scummvm/scummvm.git
git fetch upstream --no-tags
```

- [x] Clone succeeded; `C:\www\scummvm\.git` exists *At `C:\dev\scummvm`.*
- [x] `git remote -v` shows both `origin` (fork) and `upstream` (scummvm/scummvm) *`upstream` is a blob-less partial clone.*

---

## Step 3 — Record upstream HEAD commit hash (5 min)

```
git rev-parse upstream/master
```

- [x] Paste the full 40-character hash here: __________ *`c553503d9d433726b22b43b3a6a0a86fd00125e9`.*
- [x] Open `docs/02-SCUMMVM-INTEGRATION.md` → header field "ScummVM version pin" → replace **TBD** with this hash
- [x] Commit that single-line change: `git commit -am "docs: pin ScummVM upstream HEAD at fork time"` *Committed with the rest of the WP-010 doc changes.*

---

## Step 4 — Create working branch

```
git checkout -b scooby-engine
```

- [x] Confirm active branch: `git branch` shows `* scooby-engine`

---

## Step 5 — Create `engines/scooby/` skeleton files

Create the directory and all required files. Copy patterns from an existing
simple engine (e.g. `engines/access/` or `engines/agi/`) for reference on
`module.mk` and `configure.engine` syntax. See
[`docs/02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION.md) §10 for the
exact patterns required.

- [x] `engines/scooby/` directory created *By `devtools/create_engine` (fork commit `8214e448af`), then shaped (`12669217cf`). 12 files.*
- [x] `engines/scooby/configure.engine` created with `default_state = disabled` *`add_engine scooby … no …`, depends on `highres 16bit`.*
- [x] `engines/scooby/module.mk` created; lists all `.cpp` files as `MODULE_OBJS`; includes `$(MODULE)/detection.o` in a separate `DETECT_OBJS` block
- [x] `engines/scooby/scooby.h` created — `ScoobyEngine : Engine` declaration
- [x] `engines/scooby/scooby.cpp` created — `run()` returns `Common::kNoError`; `DebugMan.addDebugChannel()` calls for: `resource`, `graphics`, `audio`, `script`, `input` *Deviation: at the pin channels are a `DebugChannelDef` table returned by `getDebugChannels()` in detection, not `addDebugChannel()` calls; see integration §9.*
- [x] `engines/scooby/detection.h` created — `ScoobyMetaEngineDetection : MetaEngineDetection` declaration *`AdvancedMetaEngineDetection<ADGameDescription>`.*
- [x] `engines/scooby/detection.cpp` created — empty `ADGameDescription` table; `getName()` returns `"scooby"`; `getGameID()` returns `"scooby"` *Table in `detection_tables.h`; game id `showdown`, no entries yet.*
- [x] `engines/scooby/metaengine.h` created — `ScoobyMetaEngine : MetaEngine` declaration
- [x] `engines/scooby/metaengine.cpp` created — `hasFeature()` returns `false` for all flags; `instantiateEngine()` returns `new ScoobyEngine(syst, desc)` *`createInstance()` at the pin, not `instantiateEngine()`.*
- [x] `engines/scooby/` is added to `engines/engines.mk` or `engines/module.mk` (check how the parent list is structured in the target ScummVM version) *Automatic: configure generates `engines/engines.mk` (`MODULES += engines/scooby`).*

---

## Step 6 — First configure + build (time-box: 30 min per attempt)

```
cd C:\www\scummvm
./configure --enable-engine=scooby 2>&1 | tee configure-scooby.log
```

- [x] Configure succeeds with no errors
  - If configure fails: read `configure-scooby.log`; most common issues:
    - Missing SDL2 path → add `--with-sdl-prefix=<path>`
    - Missing zlib → install mingw-w64 zlib dev package
    - Wrong toolchain → verify `CC=` and `CXX=` environment variables
- [x] Record configure flags used: __________ *`--disable-all-engines --enable-engine=scooby`, out of tree.*

```
make -j4 2>&1 | tee build-scooby.log
```

- [x] Build succeeds; zero errors (warnings acceptable) *0 errors; 2 warnings, both upstream (`gob`, `halestorm`), none in `engines/scooby/`.*
  - If build fails: read `build-scooby.log`; most common issues:
    - `module.mk` lists a `.o` that has no corresponding `.cpp` → fix the filename
    - Missing `#include` in stub → add the required ScummVM headers
    - `ScoobyEngine` constructor signature mismatch → check `engines/engine.h` in the target version
- [x] ScummVM binary created (e.g. `scummvm.exe`)

---

## Step 7 — Verify clean omission

```
./configure --disable-engine=scooby && make -j4
```

- [x] Configure and build succeed with scooby disabled *`--disable-engine=scooby`, default engine set, 38 min.*
- [x] `scooby.o` does **not** appear in the build output — engine is cleanly excluded *Only `detection.o` builds (detection for all engines is on by default at the pin).*

---

## Step 8 — Verify debug channels compile

```
./scummvm.exe --list-debug-flags 2>&1 | findstr scooby
```

(or `grep scooby` on the output if using a Unix shell under mingw)

- [x] Output shows the 5 channels: `resource`, `graphics`, `audio`, `script`, `input` *`--list-debugflags=scooby` (the flag's name at the pin).*
- [x] If the channels don't appear: verify `DebugMan.addDebugChannel()` calls are in the `ScoobyEngine` **constructor** body, not a static initializer *N/A.*

---

## Step 9 — Commit and push

```
git add engines/scooby/
git add engines/engines.mk   # or wherever the engine list lives
git commit -m "engines/scooby: add empty compilable engine skeleton

Stub ScoobyEngine, MetaEngineDetection, and MetaEngine. Engine compiles
clean with --enable-engine=scooby and is absent with --disable-engine=scooby.
Debug channels registered: resource, graphics, audio, script, input.
default_state = disabled (ADGF_TESTING).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git push -u origin scooby-engine
```

- [x] `https://github.com/barefootbetters/scummvm/tree/scooby-engine/engines/scooby` shows all 9 files *12 files (template adds `console.*`, `credits.pl`, `detection_tables.h`; `POTFILES` removed).*

---

## Step 10 — Update project docs

- [x] `docs/02-SCUMMVM-INTEGRATION.md` "ScummVM version pin" field confirmed populated (done in Step 3)
- [x] `docs/02-SCUMMVM-INTEGRATION.md` §9 debug channel table verified against actual channel names in `scooby.cpp` — they must match exactly
- [x] WP-010 status updated to ✅ Done in [`WORK_INDEX`](../work-packets/WORK_INDEX.md)

---

## Exit check

- [x] `barefootbetters/scummvm` fork exists on GitHub
- [x] `C:\www\scummvm\` local clone on `scooby-engine` branch *`C:\dev\scummvm`.*
- [x] `engines/scooby/` skeleton: 9 files, all committed *12.*
- [x] `./configure --enable-engine=scooby && make` → clean build ✅
- [x] `./configure --disable-engine=scooby && make` → clean build ✅
- [x] Debug channels visible in `--list-debug-flags` output ✅
- [x] `docs/02-SCUMMVM-INTEGRATION.md` version pin populated ✅
