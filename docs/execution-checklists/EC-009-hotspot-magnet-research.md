---
layout: default
title: "EC-009: Hotspot Magnet research run sheet"
---

# EC-009: Hotspot Magnet research — run sheet

**Paired WP:** [WP-086](../work-packets/WP-086-hotspot-magnet-research.md)
**Purpose:** Run WP-086's research in a fixed order, recording each finding in
the [plan's](../reference/hotspot-magnet-plan.md) evidence register as it's
made, so a stopped session loses nothing.
**Status:** not started.

**Evidence rule:** every checked box cites a file and symbol at the pinned
commit, or (Step 3) a command and its date. No citation, no check.

---

## Pre-flight

- [ ] WP-086 is 📝 Drafted on `main` and nobody else holds it: no open PR or
      branch names WP-086 (`gh pr list --search WP-086`,
      `git ls-remote --heads origin`).
- [ ] Pre-flight not required (WP-086 header). Session starts from WP-086 and
      this EC.
- [ ] Work on a docs branch in its own worktree of this repo, not in
      `C:\dev\scooby-engine`.

## Step 0 — Pin the commits (time-box: 0:10)

- [ ] `git -C C:\dev\scummvm fetch origin`; record the `origin/scooby-engine`
      commit in plan §3.8.
- [ ] Fetch `scummvm/scummvm` master; record its commit for Step 6.

**Outcome:**

## Step 1 — Keymapper and Virtual Mouse (time-box: 1:00)

- [ ] Action dispatch: key or button → Keymapper action → event
      (`backends/keymapper/keymapper.cpp`, `keymap.cpp`, `action.h`).
- [ ] Keymap order when an engine keymap and a global keymap bind the same
      input.
- [ ] Virtual Mouse actions, default bindings per platform, and its movement
      and click output (`backends/keymapper/virtual-mouse.{h,cpp}`,
      `keymapper-defaults.h`).
- [ ] Answer WP-086 item 1's question (engine keymap vs Virtual Mouse on the
      D-pad), yes or no, with source.

**Outcome:**

## Step 2 — Android input (time-box: 0:45)

- [ ] D-pad and OK traced from `ScummVMEvents.java` through
      `backends/platform/android/events.cpp` to the core event.
- [ ] Keys or joystick hat events; key repeat on hold; keys the backend
      consumes itself.
- [ ] Pointer Speed and acceleration: where they apply.
- [ ] Virtual gamepad overlay (`touchcontrols.cpp`): shown or active on a TV
      with no touch screen?

**Outcome:**

## Step 3 — The remote on the TCL 65Q77K (time-box: 0:30)

- [ ] `adb connect` to the TV (smart-TV guide); `adb shell getevent -l`, or
      `dumpsys input` if denied.
- [ ] Each remote button, short and long press: key code, reaches the app or
      reserved, long-press output. Table in plan §3.2.
- [ ] Raw captures kept local; only codes and behaviors go in the plan.

**Outcome:**

## Step 4 — The hotspot display and its engines (time-box: 1:15)

- [ ] `Graphics::HotspotInfo` fields and `HotspotRenderer`
      (`graphics/hotspot_renderer.h` and its `.cpp`).
- [ ] When `getHotspotPositions()`, `drawHotspots()` and `showHotspots()`
      run; hold and toggle key modes and their action (`engines/engine.{h,cpp}`;
      the keys are handled in `backends/events/default/default-events.cpp`).
- [ ] `enable_hotspots`: where it's set (`gui/editgamedialog.cpp`) and how
      its default resolves (`engines/metaengine.cpp`).
- [ ] What each of `macs2`, `scumm`, `touche` and both `hollywood` games
      returns from `getHotspotPositions()`.
- [ ] Answer WP-086 item 4's two questions (provider interface; single
      selected target), with source.

**Outcome:**

## Step 5 — Other engine navigation (time-box: 0:30)

- [ ] Riven (`engines/mohawk/`), MADS (`engines/mads/`) and a `git grep`
      for cursor cycling between hotspots: file, symbol, reusable or not. None
      found is a valid outcome.

**Outcome:**

## Step 6 — Upstream drift (time-box: 0:20)

- [ ] `git diff <pinned> <upstream master> --stat` for the files read in
      Steps 1, 2 and 4; for each changed file, does a finding change?

**Outcome:**

## Step 7 — TerraGlyph targets, Gen 1 (time-box: 1:00)

- [ ] Placement fields for kind, hidden, current step, draw order
      (`engines/terraglyph/room.h`, `cel.h`); how to list a room's live
      placements.
- [ ] Toolbar rooms, inventory and close-ups: what they do to the clickable
      set (`inventory.cpp`, `room_setup.cpp`).
- [ ] Proposed eligibility rule, including characters and simple sprites.
- [ ] Proposed interaction-point method verified by `Room::hitTest()`, and
      its behavior for a fully covered placement.
- [ ] Can the headless self-test list a room's eligible placements (for the
      plan's §5.8 reachability check)? Yes or no, with source.

**Outcome:**

## Step 8 — Configuration and location (time-box: 0:30)

- [ ] Extra GUI options: `ADExtraGuiOptionsMap` and
      `getAdvancedExtraGuiOptions()` (`engines/advancedDetector.h`), one engine
      that uses them, the GUIO flag in `detection_tables.h`; persistence;
      run-time read. TerraGlyph declares none today.
- [ ] The exact file and symbol for a default-off "Hotspot Assist" option;
      whether the `enable_hotspots` model fits better.
- [ ] Shared-location recommendation with reasons (plan §3.4).

**Outcome:**

## Step 9 — Write-up and close (time-box: 0:45)

- [ ] Plan §3.1–3.5 and §3.7 rewritten from the findings; §3.8 register,
      §10.4 rows (proposed or unverified only) and Appendix A filled.
- [ ] WP-086 exit criteria checked one by one, each with its evidence.
- [ ] `git diff --name-only main` lists only the four allowed files.
- [ ] Strict wiki build passes.
- [ ] WP-086 → ✅ Done in its header and WORK_INDEX; plan §11 packet 1 marked
      done.

**Outcome:**

---

## Definition of done

Every step's outcome recorded, every WP-086 exit criterion met with its
evidence, and the WORK_INDEX row flipped in the close commit.

## Out-of-scope captures

Record temptations here as one line each, for later packets, and move on.

-
