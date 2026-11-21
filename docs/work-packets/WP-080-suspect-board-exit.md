---
layout: default
title: "WP-080: Suspect-board back-exit soft-lock fix"
---

# WP-080: Suspect/clue board back-exit soft-lock fix (Gen 1)

**Status:** ✅ Done (2026-11-21) — soft-lock fixed; self-test green on both titles; live re-verified by Jeff (board exit returns, run reaches credits, save/load restores). *Showdown* closeout flips to **GO**. Engine fix in [barefootbetters/scummvm#5](https://github.com/barefootbetters/scummvm/pull/5) — **ready for merge, not yet merged** (Jeff's call). See §Result.
**Phase:** 5 (polish & contribution). The fix for [WP-079](WP-079-showdown-closeout.md)'s NO-GO blocker; unblocks the *Showdown* release-readiness verdict.
**Depends on:** [WP-079](WP-079-showdown-closeout.md) 🚧 (the closeout that found the blocker — the NO-GO verdict and the root-cause lead; its §Result and [EC-006](../execution-checklists/EC-006-showdown-playthrough.md) hold the live evidence), [WP-031](WP-031-accusation.md) ✅ (the `SuspectChooserRoom` port this corrects)
**Unblocks:** a re-run of the WP-079 playthrough from the board forward to the credits + the save/load cycle, and with it the *Showdown* **go** verdict; Gate 10 (`showdown` `ADGF_UNSTABLE` → `ADGF_TESTING`), which WP-079 left explicitly blocked on this fix ("the flag cannot be promoted while the game is soft-lockable")
**Companion EC:** — (the live re-verify reuses [EC-006 Part A](../execution-checklists/EC-006-showdown-playthrough.md) from the board forward; the code change is a single focused edit)
**Pre-flight:** Required (Yes). Modifies `engines/scooby/**` (`accusation_rooms.cpp`, `accusation_rooms.h`, `scooby.cpp`). Per [wp-lifecycle §Phase 1 DoD](../reference/wp-lifecycle.md#work_index-row--phase-1-definition-of-done), engine-code changes need pre-flight.
**Targets generation(s):** Gen 1 (*Showdown in Ghost Town* and *Phantom of the Knight* — both share `SuspectChooserRoom`).
**Estimated effort:** ~1 hour for the code + rebuild + unit trace; the live re-verify (board → credits + save/load) is a bounded interactive run with Jeff.

---

## Goal

Close the release-blocking soft-lock [WP-079](WP-079-showdown-closeout.md) found:
the suspect-and-clues board's on-screen back exit (`OBJ_SUSPECT_CLUES_EXIT`)
receives clicks with the correct exit cursor but is never dispatched to
`leaveBy()`, so any player who opens the board from the toolbar magnifier — in
every room — is trapped, and the game cannot be finished from that state. Wire a
click on the exit through to `leaveBy()` in `SuspectChooserRoom`, matching the
original TerraGlyph behaviour, and add a regression test that drives the
**click → exit** path (the gap the existing self-test missed by calling
`leaveBy()` directly). The fix is in the shared `SuspectChooserRoom`, so it covers
both Gen 1 titles; the WP verifies Phantom's board is not separately broken.

## Background

[WP-079](WP-079-showdown-closeout.md) closed **NO-GO** on 2026-11-20 after a live
interactive playthrough (Jeff driving, the executing session reading the
`--debugflags=script,input` console) hit a hard progression blocker at the
suspect-and-clues board opened from `ROOM_P12_Saloon`. The live evidence
(WP-079 §Result, [EC-006 Step 2](../execution-checklists/EC-006-showdown-playthrough.md)):
entering the board logs `suspects: 0 clues, back to ROOM_P12_Saloon` (so the
return room `_from` is set), hovering the star logs `cursor ANIM_CURSORER` (the
correct exit cursor), and clicking logs only `click … on 5 OBJ_SUSPECT_CLUES_EXIT`
with **no** following `exit … clicked: going to …` and no room change — unlike
every working exit (e.g. `OBJ_P01_TO_P04` → `ROOM_P04_Street2`). The click
reaches the exit sprite but is never dispatched.

Reading the fork source (`scooby-engine`) confirms and sharpens the root cause:

- `SuspectChooserRoom` is a `ButtonRoom`. Every other interactive element — the
  suspect pictures, the clue buttons, the hotspots, the final clue — is
  registered with `addButton()` in `enter()` and dispatched through `onClick()`.
  The exit object is the one interactive element never added as a button.
- In `enter()` the placement loop has a branch per object name, ending with
  `else if (final && anim.hasSuffix("EXITICON")) setHidden(s)` — which only hides
  the exit **once the final clue is found** (the original's "the exit gone once it
  is"). When the clue is **not** final, the exit matches no branch and stays a
  plain sprite.
- It loaded from the room as an exit-kind sprite (hence the `ANIM_CURSORER`
  rollover), but its `object.ini` `destinationroom` is **empty**: the board's
  return target is the dynamic `_from` (wherever it was opened from), not a fixed
  room. The engine's generic exit dispatch
  ([`scooby.cpp` clickExit path](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/scooby.cpp))
  only fires `if (!getDestination(sprite).empty())` — an empty destination means
  that path is skipped too. So the click hits neither the button handler (not a
  button) nor the exit handler (no destination).
- `leaveBy()` itself is correct — it returns the gang to `_from`. The accusation
  self-test's "The way back" block
  ([`scooby.cpp:1322`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/scooby.cpp))
  calls `sc->leaveBy("OBJ_SUSPECT_CLUES_EXIT")` **directly**, never the
  click → `leaveBy()` wiring the real game depends on. That is exactly why the
  defect shipped: the self-test exercised `leaveBy()` but not the dispatch to it.

The *endgame* accusation leaves the board by a different path (`accuse()` →
`requestRoom()` → villain movie → verdict → credits), so the final accusation is
not blocked; only the always-available review-and-return exit is a dead end.

## Scope

### In scope

1. **Wire the exit's click to `leaveBy()`** in `SuspectChooserRoom`
   (`engines/scooby/accusation_rooms.cpp`): when the board is not showing the
   final clue, register `OBJ_SUSPECT_CLUES_EXIT` as a button (its anim ends
   `EXITICON`) so a click reaches the room class's `onClick()`, and route that
   click to `leaveBy("OBJ_SUSPECT_CLUES_EXIT")`. Keep the existing behaviour of
   hiding the exit once the final clue is found. The exit's rollover cursor is
   already correct and is left unchanged.
2. **Add an `_exit` button index + accessor** to `SuspectChooserRoom`
   (`accusation_rooms.h`), reset in `enter()` alongside the other button indexes.
3. **Add a regression test for the click → exit path** by rewriting the "The way
   back" block in `ScoobyEngine::checkAccusation()` (`engines/scooby/scooby.cpp`)
   to drive a **click** on the exit button (`sc->click(sc->getButtonSprite(
   sc->getExitButton()))`) and confirm the room changes to `_from` — not a direct
   `leaveBy()` call. The trace line reports the exit button index and the
   destination room, so a regression (exit not a button) shows as
   `button -1 … to -`.
4. **Rebuild Scooby-only and run the unit trace.** Fresh
   `./configure --disable-all-engines --enable-engine=scooby && make -j32` under
   MSYS2 UCRT64 with zero warnings in `engines/scooby/`; launch the built engine
   with `--debugflags=script --debuglevel=3` and confirm the `accusation check
   exit:` line shows the click routing to the return room, for both `showdown`
   and `phantomknight` game ids.
5. **Phantom check.** Confirm by code (the shared class) and by the self-test
   trace under `phantomknight` that Phantom's board takes the same fix and is not
   separately broken.
6. **Live re-verify (needs Jeff, interactive desktop).** From a mounted
   *Showdown* ISO, open the board, click the exit, confirm the gang returns to the
   room it was opened from; then play from the board forward to the end credits
   (the beats WP-079 did not reach), and run one explicit save → quit → relaunch →
   load cycle. This is the evidence that flips WP-079's exit-criterion 1 from
   NO-GO.

### Out of scope

- **Gate 10 (`ADGF_UNSTABLE` → `ADGF_TESTING`).** WP-079 left this as its own
  one-line `detection_tables.h` follow-up, blocked on this fix. Promoting the
  flag is a separate WP once the live re-verify passes — not folded in here.
- **The rest of the WP-079 gap list** (Gate 8's absent style/lint tool) and the
  upstream `scummvm/scummvm` PR — later WPs per WP-079.
- **Any other defect a fuller playthrough turns up.** This WP fixes the one
  blocker; a new defect spins to its own WP per the
  [one-WP-per-branch discipline](../reference/wp-lifecycle.md#discipline).

## Dependencies

- The fork at `C:\dev\scummvm` on `scooby-engine`, built Scooby-only against the
  pinned ScummVM commit (`c553503d9d`, [WP-010](WP-010-scummvm-scaffold.md)),
  worked in a dedicated fork worktree (`tools\New-ForkWorktree.ps1 -Branch
  wp-080-suspect-board-exit`) per the
  [collision discipline](../reference/wp-lifecycle.md#5-branch--a-fork-worktree-conditional--substantive-code-wps-only).
- An unmodified *Showdown in Ghost Town* ISO, mounted, for the live re-verify;
  *Phantom of the Knight* for the Phantom trace check (the self-test needs only
  the disc mounted for detection, not a full run).

## Execution plan

1. `tools\New-ForkWorktree.ps1 -Branch wp-080-suspect-board-exit` (the branch name
   is the claim; the script refuses if it already exists).
2. Edit `accusation_rooms.h`: add `int _exit = -1;` and
   `int getExitButton() const { return _exit; }`.
3. Edit `accusation_rooms.cpp`: reset `_exit = -1` in `enter()`; change the
   `EXITICON` branch to register the exit as a button when not final; add the exit
   route at the top of `onClick()`.
4. Edit `scooby.cpp`: rewrite the "The way back" self-test block to click the exit
   button and assert the room change.
5. Rebuild Scooby-only; confirm a clean build (0 warnings in `engines/scooby/`).
6. Run the unit trace under both game ids; confirm `accusation check exit:` shows
   the click routing to the return room.
7. Coordinate the live re-verify with Jeff (board → exit → credits + save/load).
8. Two-commit topology on the fork branch (the fix, then — once verified — the
   closeout note); PR the fork branch. Separately, PR the WP doc + WORK_INDEX row
   + pre-flight on the scooby-engine docs branch.

## Exit criteria

1. [x] A click on `OBJ_SUSPECT_CLUES_EXIT` in `SuspectChooserRoom` returns the
   gang to the room the board was opened from, in code: the exit is registered as
   a button and `onClick()` routes it to `leaveBy()`. — done (fork `45a7d71de7`).
2. [x] The accusation self-test drives the **click → exit** path (not a direct
   `leaveBy()`), and the `accusation check exit:` trace shows a valid exit button
   index and the destination room, for both `showdown` and `phantomknight`. — done
   (`button 3, click to ROOM_P01_Town_Center` / `ROOM_P01_Drawbridge`).
3. [x] A fresh Scooby-only build links clean with zero warnings in
   `engines/scooby/`. — done (`make -j32`, EXIT 0, 0 warnings in `engines/scooby/`).
4. [x] Phantom's board is confirmed to take the same fix (shared class) and is not
   separately broken. — done (shared `SuspectChooserRoom`; self-test trace green
   under `phantomknight`).
5. [x] **Live re-verify:** on a mounted *Showdown* ISO, opening the board and
   clicking the exit returns to the opening room; the run then reaches the end
   credits (final clue → accusation → Big Head → credits) and one explicit
   save → quit → relaunch → load cycle restores state. — **confirmed by Jeff live**
   (exit returns to Town Center; end-credits screenshot; save → quit → relaunch →
   load slot 0 restored to his save point). Evidence detail and its honest limits
   in §Result. This clears WP-079 exit-criterion 1.

## Deliverables

- The engine fix on the fork branch `wp-080-suspect-board-exit`
  (`accusation_rooms.cpp`, `accusation_rooms.h`, `scooby.cpp`), with its §Result
  recorded in this WP body and the fork commit SHA cited.
- This WP body + the [WORK_INDEX](WORK_INDEX.md) row + the pre-flight artifact on
  the scooby-engine docs branch.
- No game data committed; raw captures from the live re-verify stay in gitignored
  paths per the [copyright posture](../../tools/exes/README.md).

## Notes

- **Generation discipline.** The fix is in the shared `SuspectChooserRoom`, so it
  is Gen 1 for both *Showdown* and *Phantom*. The live re-verify is *Showdown*
  (the title WP-079 blocked); Phantom's coverage here is the code guarantee plus
  the self-test trace, not a full Phantom playthrough (that rides with Phantom's
  own future closeout).
- **Why a click-path test, not another `leaveBy()` call.** The existing self-test
  called `leaveBy()` directly and passed, which is precisely why the shipped build
  soft-locked. The regression test must exercise the dispatch the real game uses,
  or it re-opens the same blind spot.
- **Dependency timing.** WP-079's NO-GO verdict and its WORK_INDEX changes are in
  flight ([PR #135](https://github.com/barefootbetters/scooby-engine/pull/135)),
  not yet on `main`; this WP's WORK_INDEX edit may need a trivial rebase once
  #135 merges.

---

## Execution (in flight, 2026-11-21)

The engine fix landed on fork branch `wp-080-suspect-board-exit`
(`barefootbetters/scummvm@45a7d71de7`, [PR #5](https://github.com/barefootbetters/scummvm/pull/5)
into `scooby-engine`), scoped to the three allowed files:

- `accusation_rooms.cpp` — `enter()` registers `OBJ_SUSPECT_CLUES_EXIT` as a
  button (`_exit = addButton(s)`) while the board is non-final (still hidden once
  the final clue is found); `onClick()` routes `button == _exit` to
  `leaveBy("OBJ_SUSPECT_CLUES_EXIT")`; `_exit` reset in `enter()`.
- `accusation_rooms.h` — `_exit` member + `getExitButton()` accessor.
- `scooby.cpp` — the accusation self-test's back-exit check now drives a **click**
  on `getExitButton()` instead of a direct `leaveBy()`.

**Evidence:**

- Scooby-only build clean (incremental `make -j32`, EXIT 0; 0 warnings in `engines/scooby/`).
- Self-test trace (`--debuglevel=11`, which bypasses the per-channel gate in
  `debugChannelSet`), both titles that share `SuspectChooserRoom`:
  - Showdown: `accusation check exit: button 3, click to ROOM_P01_Town_Center`
  - Phantom:  `accusation check exit: button 3, click to ROOM_P01_Drawbridge`
  - The probes also confirm the exit shows on a non-final board and is hidden on
    the final board. Pre-fix, the regression reads `button -1 ... to -`.

---

## Result (2026-11-21)

**Verdict: fix works; *Showdown* closeout flips NO-GO → GO.** The suspect-board
back-exit soft-lock is closed in the shared `SuspectChooserRoom`; the live
re-verify passed on Jeff's desktop. Evidence below is labelled by how it was
captured — what is log-verified, what is Jeff's own live visual confirmation, and
what was not captured — so the close is honest about its receipts.

### Evidence of record

- **Exit fix (EC-1, EC-2, EC-3, EC-4) — code + self-test, log-verified.** Clean
  Scooby-only build (`make -j32`, EXIT 0, 0 warnings in `engines/scooby/`). The
  rewritten click-path self-test prints, under `--debuglevel=11`:
  - Showdown: `accusation check exit: button 3, click to ROOM_P01_Town_Center`
  - Phantom:  `accusation check exit: button 3, click to ROOM_P01_Drawbridge`

  Probes also confirm the exit shows on a non-final board and is hidden on the
  final board; pre-fix the regression read `button -1 … to -`.
- **Suspect-board exit (EC-5, part 1) — confirmed by Jeff live.** On a mounted
  *Showdown* disc, opening the board from the toolbar magnifier and clicking the
  back exit returned the gang to the room it was opened from (Town Center). This
  is the exact interaction WP-079 found soft-locked; it now works.
- **Reaches credits (EC-5, part 2) — confirmed by Jeff's end-credits screenshot.**
  The run played forward from the board to the end credits. *That run was not
  debug-logged* — the evidence is Jeff's screenshot of the end-credits screen, not
  a `credits check` trace line.
- **Save / load (EC-5, part 3) — confirmed by Jeff live; log-level corroboration
  not captured.** Jeff saved, quit, relaunched, loaded slot 0, and the game
  restored to his save point. The save file `showdown-win.000` (slot 0) is
  verified present on disk. **This is Jeff's own live visual confirmation, not a
  log verification** — the engine's `profile read: StartRoom …` restore receipt
  was *not* captured in a debug log and is not claimed here.

### Honest limits / context (not blockers)

- The attempt to log-capture the restore via `--save-slot=0 --debuglevel=11` is a
  clumsy combination: at `--debuglevel=11` the engine runs its full in-`run()`
  self-test (including `checkAllMovies`, which decodes every `BK.*` movie
  synchronously and freezes the window for minutes) *before* it applies
  `--save-slot` at [`scooby.cpp:172-173`](https://github.com/barefootbetters/scummvm/blob/scooby-engine/engines/scooby/scooby.cpp).
  The restore receipt would only land after that long self-test, so it was not
  worth waiting out; the save/load is recorded as Jeff's visual confirmation
  instead. Noted for future verification tooling, not a WP-080 defect.
- The save used for the restore test was a **mid-chase** save (slot 0's StartRoom
  was a Chase room). That is context on which save was exercised, not a limitation
  of the fix.

### Lifecycle state

- Engine fix: fork branch `wp-080-suspect-board-exit`,
  commit [`barefootbetters/scummvm@45a7d71de7`](https://github.com/barefootbetters/scummvm/pull/5),
  base `scooby-engine`. **[PR #5](https://github.com/barefootbetters/scummvm/pull/5)
  is ready for merge but NOT yet merged** — the squash-merge is Jeff's call. The
  §Result SHA is the branch commit; it will be the squash SHA once Jeff merges.
- Docs: this WP body + [WORK_INDEX](WORK_INDEX.md) row + pre-flight on
  `claude/wp-080-suspect-board-exit`
  ([PR #136](https://github.com/barefootbetters/scooby-engine/pull/136)).
- **Gate 10** (`showdown` `ADGF_UNSTABLE` → `ADGF_TESTING`), which WP-079 left
  blocked on this fix, is now **unblocked** — the game is no longer soft-lockable.
  Promoting the flag remains its own one-line `detection_tables.h` follow-up WP
  (out of scope here, per §Scope).

---

*Drafted 2026-11-20. Executed and live re-verified 2026-11-21; closed ✅ Done.
Engine [PR #5](https://github.com/barefootbetters/scummvm/pull/5) and docs
[PR #136](https://github.com/barefootbetters/scooby-engine/pull/136) ready for
Jeff's review/merge — nothing merged by the session.*
