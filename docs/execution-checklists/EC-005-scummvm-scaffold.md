---
layout: default
title: "EC-005: ScummVM Scaffold Checklist"
---

# EC-005: ScummVM fork + `engines/scooby/` scaffold checklist

**Paired WP:** [WP-010](../work-packets/WP-010-scummvm-scaffold)
**Purpose:** Step-by-step checklist for forking ScummVM, creating a
compilable empty engine skeleton, and pinning the baseline commit hash.

The ScummVM build system on Windows has more moving parts than most projects —
correct `module.mk` entries, `configure.engine` syntax, and the
detection/engine compilation split all need to be right before a single line
of game code is written. This checklist executes them in an order that catches
each failure as early as possible.

---

## Pre-flight

- [ ] Pre-flight verdict: **READY** — complete [docs/reference/pre-flight](../reference/pre-flight) and commit the filled-in copy before proceeding; `NOT READY` blocks this session
- [ ] Windows build toolchain installed — record which one: __________
  - mingw-w64 (most common contributor path): `gcc --version`
  - or MSVC: `cl /?`
- [ ] SDL2 development libraries present — confirm `sdl2-config --version` or SDL2 include path
- [ ] git installed and GitHub credentials configured: `git config user.email`
- [ ] ScummVM Windows build guide read (in `scummvm/scummvm` repo: `doc/compiling/` or `README.md`)
- [ ] `C:\www\scummvm\` target directory does **not** yet exist (avoids clobber)

---

## Step 1 — Fork on GitHub (5 min)

- [ ] Navigate to `https://github.com/scummvm/scummvm`
- [ ] Click **Fork** → owner: `barefootbetters`, repo name: `scummvm`
- [ ] Note the fork's default branch name: __________ (likely `master`)
- [ ] Fork URL confirmed: `https://github.com/barefootbetters/scummvm`

---

## Step 2 — Clone fork + add upstream remote (5 min)

```
git clone https://github.com/barefootbetters/scummvm.git C:\www\scummvm
cd C:\www\scummvm
git remote add upstream https://github.com/scummvm/scummvm.git
git fetch upstream --no-tags
```

- [ ] Clone succeeded; `C:\www\scummvm\.git` exists
- [ ] `git remote -v` shows both `origin` (fork) and `upstream` (scummvm/scummvm)

---

## Step 3 — Record upstream HEAD commit hash (5 min)

```
git rev-parse upstream/master
```

- [ ] Paste the full 40-character hash here: __________
- [ ] Open `docs/02-SCUMMVM-INTEGRATION.md` → header field "ScummVM version pin" → replace **TBD** with this hash
- [ ] Commit that single-line change: `git commit -am "docs: pin ScummVM upstream HEAD at fork time"`

---

## Step 4 — Create working branch

```
git checkout -b scooby-engine
```

- [ ] Confirm active branch: `git branch` shows `* scooby-engine`

---

## Step 5 — Create `engines/scooby/` skeleton files

Create the directory and all required files. Copy patterns from an existing
simple engine (e.g. `engines/access/` or `engines/agi/`) for reference on
`module.mk` and `configure.engine` syntax. See
[`docs/02-SCUMMVM-INTEGRATION.md`](../02-SCUMMVM-INTEGRATION) §10 for the
exact patterns required.

- [ ] `engines/scooby/` directory created
- [ ] `engines/scooby/configure.engine` created with `default_state = disabled`
- [ ] `engines/scooby/module.mk` created; lists all `.cpp` files as `MODULE_OBJS`; includes `$(MODULE)/detection.o` in a separate `DETECT_OBJS` block
- [ ] `engines/scooby/scooby.h` created — `ScoobyEngine : Engine` declaration
- [ ] `engines/scooby/scooby.cpp` created — `run()` returns `Common::kNoError`; `DebugMan.addDebugChannel()` calls for: `resource`, `graphics`, `audio`, `script`, `input`
- [ ] `engines/scooby/detection.h` created — `ScoobyMetaEngineDetection : MetaEngineDetection` declaration
- [ ] `engines/scooby/detection.cpp` created — empty `ADGameDescription` table; `getName()` returns `"scooby"`; `getGameID()` returns `"scooby"`
- [ ] `engines/scooby/metaengine.h` created — `ScoobyMetaEngine : MetaEngine` declaration
- [ ] `engines/scooby/metaengine.cpp` created — `hasFeature()` returns `false` for all flags; `instantiateEngine()` returns `new ScoobyEngine(syst, desc)`
- [ ] `engines/scooby/` is added to `engines/engines.mk` or `engines/module.mk` (check how the parent list is structured in the target ScummVM version)

---

## Step 6 — First configure + build (time-box: 30 min per attempt)

```
cd C:\www\scummvm
./configure --enable-engine=scooby 2>&1 | tee configure-scooby.log
```

- [ ] Configure succeeds with no errors
  - If configure fails: read `configure-scooby.log`; most common issues:
    - Missing SDL2 path → add `--with-sdl-prefix=<path>`
    - Missing zlib → install mingw-w64 zlib dev package
    - Wrong toolchain → verify `CC=` and `CXX=` environment variables
- [ ] Record configure flags used: __________

```
make -j4 2>&1 | tee build-scooby.log
```

- [ ] Build succeeds; zero errors (warnings acceptable)
  - If build fails: read `build-scooby.log`; most common issues:
    - `module.mk` lists a `.o` that has no corresponding `.cpp` → fix the filename
    - Missing `#include` in stub → add the required ScummVM headers
    - `ScoobyEngine` constructor signature mismatch → check `engines/engine.h` in the target version
- [ ] ScummVM binary created (e.g. `scummvm.exe`)

---

## Step 7 — Verify clean omission

```
./configure --disable-engine=scooby && make -j4
```

- [ ] Configure and build succeed with scooby disabled
- [ ] `scooby.o` does **not** appear in the build output — engine is cleanly excluded

---

## Step 8 — Verify debug channels compile

```
./scummvm.exe --list-debug-flags 2>&1 | findstr scooby
```

(or `grep scooby` on the output if using a Unix shell under mingw)

- [ ] Output shows the 5 channels: `resource`, `graphics`, `audio`, `script`, `input`
- [ ] If the channels don't appear: verify `DebugMan.addDebugChannel()` calls are in the `ScoobyEngine` **constructor** body, not a static initializer

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

- [ ] `https://github.com/barefootbetters/scummvm/tree/scooby-engine/engines/scooby` shows all 9 files

---

## Step 10 — Update project docs

- [ ] `docs/02-SCUMMVM-INTEGRATION.md` "ScummVM version pin" field confirmed populated (done in Step 3)
- [ ] `docs/02-SCUMMVM-INTEGRATION.md` §9 debug channel table verified against actual channel names in `scooby.cpp` — they must match exactly
- [ ] WP-010 status updated to ✅ Done in [`WORK_INDEX`](../work-packets/WORK_INDEX)

---

## Exit check

- [ ] `barefootbetters/scummvm` fork exists on GitHub
- [ ] `C:\www\scummvm\` local clone on `scooby-engine` branch
- [ ] `engines/scooby/` skeleton: 9 files, all committed
- [ ] `./configure --enable-engine=scooby && make` → clean build ✅
- [ ] `./configure --disable-engine=scooby && make` → clean build ✅
- [ ] Debug channels visible in `--list-debug-flags` output ✅
- [ ] `docs/02-SCUMMVM-INTEGRATION.md` version pin populated ✅
