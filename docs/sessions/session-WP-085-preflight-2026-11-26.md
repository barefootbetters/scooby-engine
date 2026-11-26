---
layout: default
title: "Session Prompt — WP-085 pre-flight"
---

# Session Prompt — WP-085 pre-flight (Google TV app pipeline)

> **Pre-flight session, not execution.** This session fills in the
> [pre-flight gate](../reference/pre-flight.md) for WP-085, settles the
> questions below with Jeff, and returns a READY or NOT READY verdict. If the
> verdict is READY, it also writes the execution session prompt. Nothing is
> built or installed. Paste this as the first message to a fresh session. Keep it
> leashed: no spawned sessions. Every device or toolchain claim must come from a
> command run in this session (the 2026-11-21 fabrication incident in
> [DECISIONS](../ai/DECISIONS.md) is why).

## Header

- **WP:** [WP-085](../work-packets/WP-085-tv-app-pipeline.md), Google TV app
  pipeline (library, import, test packages, updates). Companion
  [EC-008](../execution-checklists/EC-008-tv-app-pipeline.md).
- **Prompt written:** 2026-11-26. **Pre-flight date:** fill in when run.
- **Follows:** the [decision session](session-WP-085-decisions-2026-11-26.md).
  D0–D4 were answered on 2026-11-26
  ([decision](../ai/DECISIONS.md#2026-11-26--wp-085-decisions-input-test-package-hosting-advanced-mode)).
- **Targets generation(s):** N-A for engine code. TerraGlyph is compiled in and
  smoke-tested with Gen 1 (*Showdown*) data.
- **Repos:**
  - Public docs: `barefootbetters/terraglyph-engine` (`C:\dev\scooby-engine`).
  - The fork: `barefootbetters/scummvm`, **public**, branch `scooby-engine`,
    with its base checkout at `C:\dev\scummvm`.
  - Private: `barefootbetters/scooby-engine-private`
    (`C:\dev\scooby-engine-private`).

  All three checkouts are shared with other sessions. Do docs work in worktrees
  under `C:\claude-worktrees\`, and stage explicit paths only.

## Intent

Produce `docs/reference/pre-flight-WP-085-<date>.md` with every section of the
template filled in and a signed verdict. If it's READY, also produce
`docs/sessions/session-WP-085-<date>.md`, the execution prompt, per
[wp-lifecycle §Session prompt](../reference/wp-lifecycle.md#session-prompt).
Claim the WP by creating its fork worktree.

**Out of scope:**
- Any fork commit, build or install.
- Creating the test-package repo or any other external resource.
- Uploading game data.
- Changing D0–D4.
- Starting Milestone 1.

## Authority chain (read first)

1. `C:\Users\jjensen\.claude\CLAUDE.md`
2. [wp-lifecycle](../reference/wp-lifecycle.md) §Phase 2 and §End-to-end steps
   5–7, and the [pre-flight template](../reference/pre-flight.md).
3. [WP-085](../work-packets/WP-085-tv-app-pipeline.md): every section,
   especially §Decisions, §Scope and §Dependencies.
4. [EC-008](../execution-checklists/EC-008-tv-app-pipeline.md) §Pre-flight.
5. [DECISIONS](../ai/DECISIONS.md), the three 2026-11-26 entries: WP-085
   decisions, ship the free app first, and public naming.
6. [Smart-TV guide](../reference/scummvm-smart-tv.md): the build steps, Oboe
   (including the 32-bit API-16 note), `adb` over the network, the TV smoke
   test, and Controls on a TV.
7. Private: `private/commercial-strategy.md` §"App name and package id
   candidates for WP-085" holds the chosen name and id. **Never copy either one
   into a public file.**

## Pre-execution checks

- [ ] Public `main` includes `e2b0bd5` or later (the D1–D4 record and the D-pad
      correction). WP-085 says "ready for pre-flight".
- [ ] Private `main` includes `b8f2fdc` or later, and the candidates section
      shows the chosen name and id.
- [ ] `origin/scooby-engine` has been fetched. Record its SHA. If it's no longer
      `ff490ad9449f`, re-check WP-085 §Background's Android-port facts against
      the new head before relying on them.
- [ ] No `wp-085-tv-app-pipeline` branch exists locally or on the fork's
      `origin`, and no fork PR mentions WP-085. If either exists, another session
      holds the WP: stop and report.

If a check fails, stop and report.

## What the pre-flight must establish

**Dependency:** WP-079 shows ✅ Done in WORK_INDEX. Read the index; don't go
from memory.

**Claim:** run `tools\New-ForkWorktree.ps1 -Branch wp-085-tv-app-pipeline`.
Record the worktree path and its base SHA. Leave `C:\dev\scummvm` clean.

**Android-port facts:** confirmed in the fork at `ff490ad9449f` on 2026-11-26
while this prompt was written. Re-confirm them in the worktree and cite file
and line:
- `dists/android/build.gradle` sets `applicationId "org.scummvm.scummvm"` and
  `applicationIdSuffix ".debug"`.
- `dists/android/res/values/strings.xml` sets `app_name` to "ScummVM".
- `GAMES_BUNDLE_DIRECTORY` and `androidbundlerelease` (`bundleRelease
  -PsplitAssets`) are in `backends/platform/android/android.mk`.
- `backends/dlc/scummvmcloud.cpp` carries the "temporary mock api" URL, and the
  DLC store is created only in the SDL backend (`backends/platform/sdl/sdl.cpp`).
- `SAFFSTree.java` is present.

**Toolchain** (in the build environment from the smart-TV guide; record each
item's output):
- SDK platform 37.
- NDK `23.2.8568313` exactly.
- Oboe built for each ABI to be tested, with the armeabi-v7a build against
  API 16.

**Device:** `adb connect` to the TCL 65Q77K works, and `getprop
ro.product.cpu.abilist` returns its ABI list (capture both). Jeff confirms the
Bluetooth keyboard, mouse and gamepad are on hand and paired.

**Test data:** staged outside every repo, with paths recorded.
- `bass-cd-1.2.zip` must hash to
  `53209b9400eab6fd7fa71518b2f357c8de75cfeaa5ba57024575ab79cc974593`
  (`Get-FileHash`).
- Jeff's *Showdown* data must be present, and is never hosted.

**Scope lock for execution.** WP-085 changes the fork outside
`engines/terraglyph/`, which the template forbids by default, so list the
allowed fork paths explicitly. Expected, to be confirmed against the code:
- `dists/android/**`
- `backends/platform/android/**`
- `configure` or `ports.mk`, only if the build needs it
- the docs paths in WP-085 §Deliverables (the manifest format doc)

Everything else is forbidden, and so is `engines/terraglyph/**`.

## Questions to put to Jeff

Ask each one as a short question, with your recommendation first, and record
his answer verbatim in the pre-flight.

**Q1. Keeping the package id private on a public fork.** Milestone 1 gives the
app its own `applicationId` and name. The fork is public, so a hard-coded id
pushed to it publishes the name and id before the app is on Play, which goes
against the
[naming decision](../ai/DECISIONS.md#2026-11-26--public-naming-the-packaged-edition-targets-google-tv)
and the private record. Options:

| Option | Notes |
|---|---|
| **Inject at build time** (recommended to evaluate first) | `applicationId`, `app_name` and the icon and banner come from a gitignored local file or `-P` Gradle properties. The fork keeps a neutral default, and the real values live in the private repo |
| Keep the work on an unpushed branch until Play | No public PR or backup, which goes against WP-085's "fork PR open" exit criterion |
| Accept publication | Jeff relaxes the privacy rule for the id; log it in DECISIONS if so |

Check that Gradle's `applicationId` and a resource override can take values
from a property without changing `namespace` (`org.scummvm.scummvm`). If the
first option works, put it in the scope lock and the risks.

**Q2. The test-package repo.** D3 left its name for this pre-flight. Propose a
name that doesn't contain the product name, such as a `barefootbetters/`
repo named for TV test packages. Record Jeff's choice. It's **created on his
go during Milestone 3, not in this session.**

**Q3. Icon and banner for test builds.** D1 left them open. Ask whether
sideloaded test builds may use placeholders until the real art exists.

**Engineering calls (yours to make, with reasoning recorded; not Jeff's):**
- Java-side download, verify and extract (WP-085's preference) versus porting
  `backends/dlc/`. Size both from the code, and pick one.
- How the advanced mode stays out of the Play build (D4): a Gradle product
  flavor, a build-config flag, or a compile-time define. Pick one so a release
  build contains no advanced-mode code path, and say how EC-008 Step 3 will
  check it.
- Where extracted packages live in app-specific storage, outside the
  bundled-assets path that `updateStartSettings` prunes. Cite the code.

## Risk review: seed list (add any others you find)

- Package id or name leaking through the public fork (Q1).
- Downloading executable code: the manifest must allow data zips only. Note
  how the code review will check it (WP-085 exit criterion 6).
- Game data reaching git: confirm `.gitignore` covers the staging paths, and
  check `git diff --cached --name-only` before every commit.
- Collision on the shared checkout: work only in the worktree from the claim.
- The system file picker on the TCL is untested (Milestone 2's first gap).
- The 32-bit Oboe link failure if Oboe is built against an API above 16 (from
  the smart-TV guide).
- Device evidence: no checked EC-008 box without a capture.

## Execution rules for this session

**Scope allowlist:**

```
docs/reference/pre-flight-WP-085-<date>.md
docs/sessions/session-WP-085-<date>.md              (only if READY)
docs/execution-checklists/EC-008-tv-app-pipeline.md (tick the §Pre-flight boxes with evidence)
docs/work-packets/WP-085-tv-app-pipeline.md         (record the Q1–Q3 answers and the engineering calls)
docs/work-packets/WORK_INDEX.md                     (the WP-085 row's status)
private/commercial-strategy.md                      (private repo; only if Q1's answer needs the private values recorded)
```

The fork: the worktree from the claim, read-only apart from creating it.

**Forbidden:**
- The product name or package id in any public file, or in the fork.
- Fork commits.
- External resources.
- Game data in any repo.
- Changing D0–D4.

**You MUST:**
- Fill every template section with concrete content. Placeholders invalidate
  the pre-flight.
- Quote Jeff's answers verbatim.
- Run the ewiki gates with the private worktree junctioned as `_private`, and
  check every link and anchor you add. Remove the junction with
  `(Get-Item _private).Delete()`, never a recursive delete.
- Write the execution prompt (if READY) from the template, filled in against
  the pre-flight. It must not extend the pre-flight.

## Session task

Outputs this session MUST produce:

1. `pre-flight-WP-085-<date>.md`, with a signed verdict against the public
   `main` SHA and the fork SHA.
2. The WP-085 fork worktree, created and recorded.
3. The Q1–Q3 answers and the three engineering calls, recorded in the
   pre-flight and in WP-085.
4. EC-008's §Pre-flight boxes ticked with evidence, or left open with the
   reason.
5. If READY: `session-WP-085-<date>.md`, the execution prompt. If NOT READY:
   §Path to resolution, and WORK_INDEX updated to match.
6. PRs open (public, plus private if it was touched), with the gates green.

## Close ritual

1. Confirm the gates pass and the links resolve.
2. Open the PRs and state the merge order: public before private if the private
   page links new public anchors.
3. Report to Jeff: the verdict and why, the Q1–Q3 answers, the engineering
   calls, the worktree path, and what the execution session will do first. Ask
   before merging.
