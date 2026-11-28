---
layout: default
title: "EC-012: Hotspot Magnet interface design run sheet"
---

# EC-012: Hotspot Magnet interface design — run sheet

**Paired WP:** [WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md)
**Purpose:** Run WP-089's design work in a fixed order, writing each section
into the [plan](../reference/hotspot-magnet-plan.md) as it's done, so a
stopped session loses nothing.
**Status:** done (2026-11-27).

**Evidence rule:** every source fact the design relies on cites a file and
symbol at the pinned commit and goes in the plan's evidence register (E27
onward). Every design choice that H1–H8 don't cover is a proposed row in the
decision register (H9 onward). The WP body says what each section must
answer; this sheet only records where it was written.

---

## Pre-flight

- [x] WP-089 is 📝 Drafted on `main` and nobody else holds it: no open PR or
      other branch names WP-089 (`gh pr list --search WP-089`,
      `git ls-remote --heads origin`), and no session's worktree has it.
      Checked 2026-11-27: none.
- [x] Pre-flight not required (WP-089 header). Session starts from WP-089 and
      this EC.
- [x] Work on a docs branch in its own worktree of this repo, not in
      `C:\dev\scooby-engine`: `C:\claude-worktrees\scooby-wp089-exec`, branch
      `docs/wp-089-hotspot-magnet-interface-exec`, claim commit `00c83ec`.

## Step 0 — Pin and drift (time-box: 0:20)

- [x] `git -C C:\dev\scummvm fetch origin`; record the `origin/scooby-engine`
      commit in plan §3.8: `0d5a69c7694f`.
- [x] `git -C C:\dev\scummvm diff --stat ff490ad9449f <pinned>`: every file
      changed, not only Appendix A's. 12 files, all WP-085's Android work
      (fork PR #13); no keymapper, event, hotspot or TerraGlyph file.
- [x] Refresh E3, E8 and E9's `android.cpp` line numbers (+6 from line 363).
- [x] Record the `ScummVMActivity.dispatchKeyEvent` intercept and
      `AdvancedMode`'s D-pad gesture, and its "reported twice" comment, as
      E-rows (E33).

**Outcome:** pinned; drift changes no finding, only `android.cpp`'s line
numbers.

## Step 1 — Source reads (time-box: 1:15)

Each read is an E-row with file and symbol.

- [x] Keymaps: declaring (`initKeymaps()`), enabling (`setEnabled()`), and
      the action events (E27, E28, E29).
- [x] The cursor: `warpMouse()` and the event it produces, and TerraGlyph's
      cursor sprite (E31, E39).
- [x] `handleMouse()`'s gates and the room-class hand-off, and the
      game-state signals (E34, E36, E38).
- [x] The held-button and pointer-reading rooms (E35).
- [x] Nested event loops and the main menu's keymap switch (E30, E40).
- [x] Room width and the visible area, and the polygon box (E37).
- [x] The extra-option declaration and its read site (E42; E23, E24).
- [x] The self-test's `checkAllRooms` and `showRoom()` paths, and the
      `test_script` parser (E41).
- [x] `SignInRoom::key()` (E43).

**Outcome:** E27–E44. One correction to WP-086: ScummVM's default game
keymap, which TerraGlyph has today, binds the D-pad to keypad keys (E27,
plan §3.2).

## Step 2 — Hotspot record, provider and components (time-box: 1:00)

- [x] Hotspot record, `HotspotInfo` mapping, adapter identity, point search,
      provider filter and the one-override question written in §4.3–4.6 and
      §6.5.
- [x] Components A–E written in §4.2–4.3; declarations in Appendix B, no
      bodies; B and C name no TerraGlyph symbol.

**Outcome:** points only, identity beside the list (H12); room-class
buttons as targets (H13).

## Step 3 — Selection lifetime and activation (time-box: 0:45)

- [x] Identity, the drop table and the activation re-check written in §4.4
      and §5.6.
- [x] Activation, its blocks and what the player sees written in §4.2.

**Outcome:** activation pushes real button events, the release a tick later
(H9).

## Step 4 — Modes, input and coordinates (time-box: 1:15)

- [x] Mode state machine and the per-mode remote table written in §6.1–6.2.
- [x] Keymaps, bindings and enabling written in §6.4, with OK bound in
      cursor mode (H16).
- [x] The held-button and drag rooms written in §6.8 (H11).
- [x] Hold timing contract, when the switch fires, and the resets written in
      §6.2 (H10).
- [x] D-pad repeat entry point and the test-build gesture written in §6.3
      (H15).
- [x] Coordinate spaces and the cursor call written in §4.5.

**Outcome:** three keymaps; the Options knobs, Brad's game and the vault's
clock can't be played on the remote without room assists.

## Step 5 — Configuration, feedback, test hooks and the core contract (time-box: 0:45)

- [x] The option written in §6.6 and §7.4.
- [x] Selected-target and mode feedback written in §6.5 (H14).
- [x] The listing hook and `test_script` verbs written in §12.7.
- [x] The core's contract for packet 3 written in §4.3.

**Outcome:** written.

## Step 6 — Register, write-up and close (time-box: 0:45)

- [x] H9–H16 added to §10.4, each proposed with alternatives and evidence,
      and each cited from Part II (checked by script).
- [x] Appendix D terms written; §11 packet 2 marked done; §14.3 updated;
      revision-history row added.
- [x] The `tv-dpad` note in `dashboard.json` updated.
- [x] WP-089 exit criteria checked one by one, each with its evidence, in
      WP-089 §Close.
- [x] `git diff --name-only main` lists only the five allowed files.
- [x] Strict wiki build passes.
- [x] WP-089 → ✅ Done in its header and WORK_INDEX.

**Outcome:** closed.

---

## Definition of done

Every step's outcome recorded, every WP-089 exit criterion met with its
evidence, and the WORK_INDEX row flipped in the close commit.

## Out-of-scope captures

- **A possible stuck button after a movie.** `movie.cpp`'s own event loop
  discards button releases (E40), so a button held when a movie starts may
  leave TerraGlyph's `_mouseDown` set afterwards. An inference, not seen;
  a candidate engine fix, independent of Magnet.
- **The D-pad in a TerraGlyph game today** sends keypad keys the engine
  ignores (E27). Worth a one-line check on the TV, and a note in the
  smart-TV guide if confirmed.
