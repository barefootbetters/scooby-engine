---
layout: default
title: "EC-012: Hotspot Magnet interface design run sheet"
---

# EC-012: Hotspot Magnet interface design — run sheet

**Paired WP:** [WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md)
**Purpose:** Run WP-089's design work in a fixed order, writing each section
into the [plan](../reference/hotspot-magnet-plan.md) as it's done, so a
stopped session loses nothing.
**Status:** not started.

**Evidence rule:** every source fact the design relies on cites a file and
symbol at the pinned commit and goes in the plan's evidence register (E27
onward). Every design choice that H1–H8 don't cover is a proposed row in the
decision register (H9 onward). The WP body says what each section must
answer; this sheet only records where it was written.

---

## Pre-flight

- [ ] WP-089 is 📝 Drafted on `main` and nobody else holds it: no open PR or
      other branch names WP-089 (`gh pr list --search WP-089`,
      `git ls-remote --heads origin`), and no session's worktree has it.
- [ ] Pre-flight not required (WP-089 header). Session starts from WP-089 and
      this EC.
- [ ] Work on a docs branch in its own worktree of this repo, not in
      `C:\dev\scooby-engine`. The branch, pushed, is the claim.

## Step 0 — Pin and drift (time-box: 0:20)

- [ ] `git -C C:\dev\scummvm fetch origin`; record the `origin/scooby-engine`
      commit in plan §3.8.
- [ ] `git -C C:\dev\scummvm diff --stat ff490ad9449f <pinned>`: every file
      changed, not only Appendix A's. Name each change that alters a finding
      or a citation (WP-089 item 1).
- [ ] Refresh E3, E8 and E9's `android.cpp` line numbers.
- [ ] Record the `ScummVMActivity.dispatchKeyEvent` intercept and
      `AdvancedMode`'s D-pad gesture, and its "reported twice" comment, as
      E-rows.

**Outcome:**

## Step 1 — Source reads (time-box: 1:15)

Each read is an E-row with file and symbol.

- [ ] Keymaps: how an engine declares one (`initKeymaps()` on the
      meta-engine), enables and disables it at run time (`setEnabled()`), and
      the action events it delivers (start per down, repeats, end).
- [ ] The cursor: the ScummVM call that moves it, the event it produces, and
      how TerraGlyph's cursor sprite follows the mouse.
- [ ] `handleMouse()`'s gates and the room-class hand-off
      (`RoomClass::click()`, `ButtonRoom`'s buttons), and the game-state
      signals the selection lifetime needs (room change, script, input
      blocked, busy, inventory, close-ups).
- [ ] The held-button and pointer-reading rooms WP-089's Background lists:
      what each reads and when.
- [ ] Nested event loops (`movie.cpp`) and the main menu's keymap switch.
- [ ] Room width and the visible area (`terraglyph.cpp`), and the polygon
      box accessor the H3 search needs (`Room::getPolygon`).
- [ ] The extra-option declaration and its read site (E23, E24) at the pinned
      commit.
- [ ] The self-test's `checkAllRooms` and `showRoom()` paths, and the
      `test_script` parser.
- [ ] `SignInRoom::key()`, for the keyboard binding.

**Outcome:**

## Step 2 — Hotspot record, provider and components (time-box: 1:00)

- [ ] Hotspot record, `HotspotInfo` mapping, adapter identity, point search,
      provider filter and the one-override question written in §4.3 and §4.6
      (WP-089 item 3).
- [ ] Components A–E written in §4.2–4.3 (item 2); declarations in
      Appendix B, no bodies; B and C name no TerraGlyph symbol.

**Outcome:**

## Step 3 — Selection lifetime and activation (time-box: 0:45)

- [ ] Identity across refreshes, the drop list with its detecting symbols and
      how changes are noticed, and the activation re-check written in §4.4
      and §5.6 (item 4).
- [ ] Activation through `handleMouse()`, its blocks and what the player
      sees, written in §4.2 E (item 7).

**Outcome:**

## Step 4 — Modes, input and coordinates (time-box: 1:15)

- [ ] Mode state machine and the per-mode remote table written in §6.1–6.2
      (item 5).
- [ ] Keymaps, bindings and enabling written, with OK bound in cursor mode.
- [ ] The held-button and drag rooms' way of play written.
- [ ] Hold timing contract, when the switch fires, and the resets written.
- [ ] D-pad repeat entry point and the test-build gesture's handling written.
- [ ] Coordinate spaces and the cursor call written in §4.5 (item 6).

**Outcome:**

## Step 5 — Configuration, feedback, test hooks and the core contract (time-box: 0:45)

- [ ] The option written in §6.6 and §7.4 (item 8).
- [ ] Selected-target and mode feedback written in §6.5 (item 9).
- [ ] The listing hook and `test_script` verbs written in §12 (item 10).
- [ ] The core's contract for packet 3 written in §4.3 (item 11).

**Outcome:**

## Step 6 — Register, write-up and close (time-box: 0:45)

- [ ] H9 onward added to §10.4, each proposed with alternatives and
      evidence, and each cited from Part II (item 12).
- [ ] Appendix D terms written; §11 packet 2 marked done; §14.3 updated;
      revision-history row added.
- [ ] The `tv-dpad` note in `dashboard.json` updated.
- [ ] WP-089 exit criteria checked one by one, each with its evidence, in a
      WP-089 §Close table.
- [ ] `git diff --name-only main` lists only the five allowed files.
- [ ] Strict wiki build passes.
- [ ] WP-089 → ✅ Done in its header and WORK_INDEX.

**Outcome:**

---

## Definition of done

Every step's outcome recorded, every WP-089 exit criterion met with its
evidence, and the WORK_INDEX row flipped in the close commit.

## Out-of-scope captures

- *(none yet)*
