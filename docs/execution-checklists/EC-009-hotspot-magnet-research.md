---
layout: default
title: "EC-009: Hotspot Magnet research run sheet"
---

# EC-009: Hotspot Magnet research — run sheet

**Paired WP:** [WP-086](../work-packets/WP-086-hotspot-magnet-research.md)
**Purpose:** Run WP-086's research in a fixed order, recording each finding in
the [plan's](../reference/hotspot-magnet-plan.md) evidence register as it's
made, so a stopped session loses nothing.
**Status:** done (2026-11-26). Step 3's button capture is a gap.

**Evidence rule:** every checked box cites a file and symbol at the pinned
commit, or (Step 3) a command and its date. No citation, no check. The E- and
H-numbers are rows in the plan's evidence and decision registers.

---

## Pre-flight

- [x] WP-086 is 📝 Drafted on `main` and nobody else holds it: no open PR or
      branch names WP-086 (`gh pr list --search WP-086`,
      `git ls-remote --heads origin`). Checked 2026-11-26: no PR, branch or
      worktree; the fork has no WP-086 branch. The open PRs #223 and #224
      touch only `dashboard.json`. The claim is the branch
      `docs/wp-086-hotspot-magnet-research` (commit `ba0fb80`).
- [x] Pre-flight not required (WP-086 header). Session starts from WP-086 and
      this EC.
- [x] Work on a docs branch in its own worktree of this repo, not in
      `C:\dev\scooby-engine`: `C:\claude-worktrees\scooby-wp086-exec`.

## Step 0 — Pin the commits (time-box: 0:10)

- [x] `git -C C:\dev\scummvm fetch origin`; record the `origin/scooby-engine`
      commit in plan §3.8: `ff490ad9449f`.
- [x] Fetch `scummvm/scummvm` master; record its commit for Step 6:
      `7b6fa644d74a` (2026-11-26), merge base `2982fe324b6c`.

**Outcome:** pinned; recorded in plan §3.8.

## Step 1 — Keymapper and Virtual Mouse (time-box: 1:00)

- [x] Action dispatch: key or button → Keymapper action → event (E1).
- [x] Keymap order when an engine keymap and a global keymap bind the same
      input (E2).
- [x] Virtual Mouse actions, default bindings per platform, and its movement
      and click output (E3, E4, E5).
- [x] Answer WP-086 item 1's question (engine keymap vs Virtual Mouse on the
      D-pad), yes or no, with source: **yes** (E2, E3).

**Outcome:** an enabled game keymap binding `JOY_UP`…`JOY_RIGHT` takes those
buttons from the Virtual Mouse in games; the Virtual Mouse has no click.

## Step 2 — Android input (time-box: 0:45)

- [x] D-pad and OK traced from `ScummVMEvents.java` through
      `backends/platform/android/events.cpp` to the core event (E6).
- [x] Keys or joystick hat events; key repeat on hold; keys the backend
      consumes itself (E6, E7, E8).
- [x] Pointer Speed and acceleration: where they apply (E9).
- [x] Virtual gamepad overlay (`touchcontrols.cpp`): shown or active on a TV
      with no touch screen? No (E10).

**Outcome:** the remote's D-pad arrives as joystick buttons; `JOY_CENTER` is
unbound in games; BACK and MENU are taken; no acceleration setting.

## Step 3 — The remote on the TCL 65Q77K (time-box: 0:30)

- [x] `adb connect` to the TV (smart-TV guide); `adb shell getevent -l`, or
      `dumpsys input` if denied. The TV was already connected; `getevent -lp`
      and `dumpsys input` worked (E22).
- [ ] Each remote button, short and long press: key code, reaches the app or
      reserved, long-press output. **Gap:** a 3-minute `getevent -lt` capture
      on 2026-11-26 had no button presses.
- [x] Raw captures kept local; only codes and behaviors go in the plan.

**Outcome:** gap, recorded in plan §3.2 with the command to fill it.

## Step 4 — The hotspot display and its engines (time-box: 1:15)

- [x] `Graphics::HotspotInfo` fields and `HotspotRenderer` (E12, E15).
- [x] When `getHotspotPositions()`, `drawHotspots()` and `showHotspots()`
      run; hold and toggle key modes and their action (E11, E13, E14).
- [x] `enable_hotspots`: where it's set and how its default resolves (E14).
- [x] What each of `macs2`, `scumm`, `touche` and both `hollywood` games
      returns from `getHotspotPositions()` (E16).
- [x] Answer WP-086 item 4's two questions (provider interface; single
      selected target), with source (plan §3.3).

**Outcome:** the provider interface is usable as is (a stable id may need
adding); the renderer marks one target only as a one-item list.

## Step 5 — Other engine navigation (time-box: 0:30)

- [x] Riven (`engines/mohawk/`), MADS (`engines/mads/`) and a `git grep`
      for cursor cycling between hotspots (E17).

**Outcome:** only Lab's "FOCUS" moves the cursor to the next interactive
item; nothing reusable.

## Step 6 — Upstream drift (time-box: 0:20)

- [x] `git diff <pinned> <upstream master> --stat` for the files read in
      Steps 1, 2 and 4 (E21).

**Outcome:** only `735ad86c21` (Android mouse pointer capture); no finding
changes.

## Step 7 — TerraGlyph targets, Gen 1 (time-box: 1:00)

- [x] Placement fields for kind, hidden, current step, draw order; how to
      list a room's live placements (E18).
- [x] Toolbar rooms, inventory and close-ups: what they do to the clickable
      set (E19).
- [x] Proposed eligibility rule, including characters and simple sprites
      (plan §3.5, H7).
- [x] Proposed interaction-point method verified by `Room::hitTest()`, and
      its behavior for a fully covered placement (plan §3.5, H3).
- [x] Can the headless self-test list a room's eligible placements? **Yes**
      (E20).

**Outcome:** rule and method proposed; activation can reuse
`TerraglyphEngine::handleMouse()`; the polygon box needs a small accessor.

## Step 8 — Configuration and location (time-box: 0:30)

- [x] Extra GUI options: mechanism, example engine (Awe), GUIO flag,
      persistence, run-time read (E23, E24).
- [x] The exact file and symbol for a default-off "Hotspot Assist" option;
      whether the `enable_hotspots` model fits better (E24, H5).
- [x] Shared-location recommendation with reasons (plan §3.4, H4).

**Outcome:** `TerraglyphMetaEngine::getAdvancedExtraGuiOptions()` for Phase
1; `engines/` beside the hotspot display for the shared code.

## Step 9 — Write-up and close (time-box: 0:45)

- [x] Plan §3.1–3.5 and §3.7 rewritten from the findings; §3.8 register,
      §10.4 rows (proposed or unverified only) and Appendix A filled.
- [x] WP-086 exit criteria checked one by one, each with its evidence
      (WP-086 §Close).
- [x] `git diff --name-only main` lists only the four allowed files.
- [x] Strict wiki build passes.
- [x] WP-086 → ✅ Done in its header and WORK_INDEX; plan §11 packet 1 marked
      done.

**Outcome:** closed.

---

## Definition of done

Every step's outcome recorded, every WP-086 exit criterion met with its
evidence, and the WORK_INDEX row flipped in the close commit.

## Out-of-scope captures

- Two small inaccuracies in the fork: the comment at `engines/engine.h:560`
  says hotspot markers are "semi-transparent circles", but the default is a
  crosshair; and `HotspotType` is never used in drawing. Upstream-comment
  material, not ours to fix in WP-086.
- TerraGlyph implementing `getHotspotPositions()` would also give its games
  ScummVM's show-all hotspot display. A candidate for the TerraGlyph hotspot
  provider packet (plan §11, packet 5).
