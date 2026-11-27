---
layout: default
title: "WP-087: Phantom closeout"
---

# WP-087: Phantom closeout — full playthrough and release readiness (Gen 1)

**Status:** 📝 Drafted (2026-11-26) · needs pre-flight.
**Numbering:** WP-086 is held twice by parallel drafts (the Hotspot Magnet research on `docs/wp-086-hotspot-magnet-research`, and a Play internal-testing draft in another worktree), and both also use EC-009. This WP takes WP-087 and EC-010 to stay clear of both ([wp-lifecycle §Supersession check](../reference/wp-lifecycle.md#supersession-check-required-before-reserving-a-number)).
**Phase:** 5 (polish & contribution). It also meets the Phase 3 success criterion for *Phantom* ([01-VISION §Phase 3](../01-VISION.md)).
**Depends on:** every *Phantom* game class ported: the [Phantom room-class audit](../reference/room-class-audit-phantom-2026-11-16.md)'s rooms, WP-057 ✅ … WP-083 ✅ (the last, the Wizard's Rule Room, landed 2026-11-22), and with them the Gen 1 chain WP-014 ✅ … WP-056 ✅; WP-079 ✅ (*Showdown*'s closeout, the model this follows); WP-080 ✅ (the suspect-board fix, shared with *Phantom*)
**Unblocks:** *Phantom* shipping in the fork at `ADGF_TESTING`, and in any packaged edition that carries it
**Companion EC:** [EC-010](../execution-checklists/EC-010-phantom-playthrough.md) (the run sheet)
**Pre-flight:** Required (Yes). This WP claims "*Phantom* (Gen 1) is release-ready", exercises `engines/terraglyph/**` through a full run, and on a GO changes the fork's detection flag for `phantomknight` ([wp-lifecycle §Phase 1 DoD](../reference/wp-lifecycle.md#work_index-row--phase-1-definition-of-done)).
**Targets generation(s):** Gen 1 (*Phantom of the Knight*) only.
**Estimated effort:** 1–2 days. Most of it is the live run, which needs a person at the engine window.

---

## Goal

Prove *Scooby-Doo! Phantom of the Knight* is complete and release-ready as a
Gen 1 TerraGlyph title in the fork. That means one run from an unmodified disc
to the end credits with no missing assets, fatal errors or progression
blockers; save and load working; and each merge-blocking acceptance gate
checked for *Phantom*. The output is a **go/no-go verdict** backed by labelled
evidence, and a gap list. On a GO, `phantomknight` moves from `ADGF_UNSTABLE` to
`ADGF_TESTING` and the wiki-page draft stops calling it "in development".

## Background

Every class in *Phantom*'s room factory now has a port. The audit found 52 of
its 53 rooms with a class of their own (two classes shared), ten of them
already answered by the classes built for *Showdown*. WP-057 to WP-083 ported
the rest, in the audit's suggested order, finishing with `ROOM_P30_WFR`. One
room, `ROOM_P26_Castle_Balcony`, has a class that overrides nothing; one,
`ROOM_Cheat`, is a developer room and is not ported.

What stands between "every class ported" and "*Phantom* is finished" is what
stood in front of *Showdown* at WP-079:

1. **No start-to-credits run.** Each Phantom WP checked its own rooms against an
   independent reference trace and the self-test. The audit's own limit applies:
   it checks that a ported room has a class, not that the class overrides every
   slot the original's does, and the suggested order *"isn't from a play-through"*
   ([audit §Suggested order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order)).
   A missing slot, a bad hand-off between rooms or a dead end shows up only on a
   real run.
2. **The ten shared classes were traced on *Showdown*, not *Phantom*.** The
   title, menus, Sign In, Options, Credits, the suspect chooser, Big Head and the
   ghost spot run on *Phantom* with code traced in *Showdown*'s binary. Only the
   ghost spot (WP-056) and the suspect board (WP-080) were compared on *Phantom*
   ([audit §Not covered](../reference/room-class-audit-phantom-2026-11-16.md#not-covered)).
   The ending is the riskiest of these: it runs the shared accusation, Big Head
   and credits on *Phantom*'s story values.
3. **The release gates and flag.** *Showdown*'s gate walk (WP-079, re-run under
   WP-082) covered the engine as a whole, but gates 3 (detection) and 10 (the
   flag) are per title, and `phantomknight` is still `ADGF_UNSTABLE`. The
   [wiki-page draft](../reference/scummvm-wiki-scooby.md) still lists *Phantom* as
   "In development — room port in progress".
4. **One known deferral.** WP-083 left out a transition-movie variant: leaving
   the Wizard's Rule Room without the wizard's clue sets movie `0xb`, which the
   engine's `leaving()` hook does not expose. The destination and every gameplay
   contract are the same either way
   ([WP-083 §One deferral](WP-083-wfr.md)). The run records whether it is
   visible; the verdict decides whether it blocks.

**On evidence.** WP-079's first §Result reported a live run that never happened
([DECISIONS 2026-11-21](../ai/DECISIONS.md)). This WP labels every piece of
evidence by its source, and nothing in it is claimed without one (see
[§Notes](#notes)).

## Scope

### In scope

**Part A — the playthrough.**

1. Boot *Phantom* in the fork from an unmodified disc mount, start a new game
   through Sign In, and play the story to the end credits. Follow the beat spine
   in EC-010 Step 1, which is the audit's order: the drawbridge and town → the
   souvenir shop → the gardener's house, garden and plaque → the room of doors and
   its rooms (throne room, dining room and Maria, kitchen and Ewan, kitchen
   storage, king's armory) → the arenas and Brad → the passages, treasury, gallery
   and Knights of the Snack Table → the maze → upstairs and the Wizard's Rule Room
   → the final clue, the accusation, Big Head and the credits.
2. At each beat, record the room, its opening, the puzzle, the item or clue
   gained and the exit, with an evidence label (EC-010). Log any missing asset,
   wrong or missing scene, stuck exit, lost item or clue, crash or assertion as a
   one-line gap, and keep playing.
3. Confirm the win condition fires on *Phantom*: the final clue opens the
   accusation (movie 55, WP-071), the wizard's clue arms it (WP-081/WP-083), the
   right suspect is revealed through Big Head, and the credits roll to their end.
4. Run save and load: save before a room change, quit the engine, relaunch,
   load, and confirm the room, inventory and progression restore
   ([02-SCUMMVM-INTEGRATION §8](../02-SCUMMVM-INTEGRATION.md#8-save--load)).
5. Record whether the WP-083 movie `0xb` variant is noticeable when leaving the
   Wizard's Rule Room without the clue.

**Part B — the release gates, for *Phantom*.**

6. Walk the ten merge-blocking gates
   ([02-SCUMMVM-INTEGRATION §Acceptance gates](../02-SCUMMVM-INTEGRATION.md#acceptance-gates-tldr))
   against the fork's current `scooby-engine` tip and record pass or fail with
   evidence. Re-run each mechanical check (gates 1, 2, 3, 4, 5, 6, 7, 9); do not
   quote WP-079 or WP-082. Gate 8 takes WP-082's assessment unless the engine's
   files have changed since.
7. Gate 3 on *Phantom*: `--detect` on the mounted disc returns
   `terraglyph:phantomknight`, the *Showdown* disc still returns `showdown`, and an
   unrelated folder returns nothing. Record *Phantom*'s per-variant MD5s from
   `detection_tables.h` with the full-file SHA-256 locks from
   [tools/exes/README](../../tools/exes/README.md#phantom-gen-1).

**Part C — verdict and, on a GO, release.**

8. Write the **go/no-go verdict** and the gap list in §Result, each gap tagged
   with the WP that owns its fix, or "none — passes".
9. **On a GO only:** in a fork worktree (`tools/New-ForkWorktree.ps1`), change
   `phantomknight` from `ADGF_UNSTABLE` to `ADGF_TESTING` in
   `engines/terraglyph/detection_tables.h`, build, re-run gate 10, and open the
   fork PR. Update the [wiki-page draft](../reference/scummvm-wiki-scooby.md)'s
   *Phantom* row, known limitations and MD5 table to match.

### Out of scope

- **Fixing what the run finds.** Each defect becomes its own scoped follow-up WP
  with a fork branch, as WP-080 was for *Showdown*. The one fork change here is
  the Part C flag, and only on a GO.
- **The upstream `scummvm/scummvm` submission.** Held at the fork (decided
  2026-11-21); [WP-082](WP-082-upstream-submission-prep.md) owns that path.
- **`ROOM_Cheat`.** A developer room; not ported in either title.
- **The Google TV edition.** Whether *Phantom* ships in it is a WP-084/WP-085
  decision; this WP only makes it eligible.
- **Jinx at the Sphinx and the other Gen 2/3 titles.** Phase 5's later tiers.

## Dependencies

- The fork at `C:\dev\scummvm` on `scooby-engine`, built with only this engine
  enabled (`./configure --disable-all-engines --enable-engine=terraglyph`) against
  the pinned ScummVM commit, under MSYS2 UCRT64.
- An unmodified *Phantom of the Knight* disc image
  (`C:\pcloud\scooby-engine\Scooby Doo Phantom of the Knight.iso`), mounted, with
  `Scooby.exe` SHA-256 `619EA687…07ED`
  ([tools/exes/README](../../tools/exes/README.md#phantom-gen-1)). The *Showdown*
  image for gate 3's negative case.
- A person at the engine window for Part A: Jeff, or a session driving the
  window under computer use while it is watched. The headless self-test
  (`test_script`, `--debuglevel=11`, `--logfile`) supplies the logged fragments.

## Execution plan

Follow [EC-010](../execution-checklists/EC-010-phantom-playthrough.md): a
fresh build → gate 3 and boot → the run, beat by beat → the save and load
cycle → the gate walk → the verdict and gap list → on a GO, the flag PR and
the wiki-page update. A run that hits a hard progression blocker stops there:
the blocker is the top gap, the WP stays 🚧, and the blocker's fix WP is the
next step.

## Exit criteria

1. [ ] A run from a mounted, unmodified *Phantom* disc reaches the end credits
   with **no missing asset, fatal error, assertion or progression blocker**, and
   EC-010's beat table is filled in with an evidence label on every row. A row
   with no evidence stays ☐ and the criterion is not met.
2. [ ] The win condition is shown end to end on *Phantom*: final clue →
   accusation → the right suspect through Big Head → credits to the end.
3. [ ] Save before a room change, relaunch, load, and the state restores; the
   `profile read` line is captured in a log, or the row says it is a live visual
   confirmation.
4. [ ] Each of the ten gates is recorded pass or fail with evidence for
   *Phantom*, and every mechanical check was re-run in this WP.
5. [ ] *Phantom*'s per-variant MD5s and SHA-256 locks are recorded in EC-010 and
   the wiki-page draft.
6. [ ] A written **go/no-go verdict** and a gap list, each item tagged with the
   WP that owns its fix (or "none — passes"). The WP-083 movie `0xb` variant has a
   line in the gap list either way.
7. [ ] **On a GO:** `phantomknight` is `ADGF_TESTING` in a merged fork PR, and
   the wiki-page draft's *Phantom* entries are updated. **On a NO-GO:** this
   criterion is "n/a — NO-GO", and the WP stays 🚧 until the blockers' WPs land and
   the run is redone.

## Deliverables

- This WP with its §Result: the verdict, the gap list and the exit-criteria table.
- [EC-010](../execution-checklists/EC-010-phantom-playthrough.md) filled in.
- On a GO, the fork PR for the flag and the updated
  [`scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md).
- WORK_INDEX row and the dashboard's `phantom-port` area updated at close.
- Raw captures (screenshots, logs) stay out of this repo, under the session's
  scratchpad or the verification run's folder, per the
  [copyright posture](../../tools/exes/README.md). §Result names each log file it
  cites.

## Notes

- **Evidence labels.** Each claim in §Result and each EC-010 row carries one
  of: **log** (a named log file, with the quoted line), **self-test** (the
  headless trace, named), **live — Jeff** (Jeff saw it), **live — session**
  (a session drove the window under computer use; screenshots kept), or
  **source** (read in the fork, with file and line). A session never reports a
  live run it did not drive or watch, and never writes Jeff's observations for
  him: it asks, and records his answer as his. This is the WP-079 lesson
  ([DECISIONS 2026-11-21](../ai/DECISIONS.md)).
- **Generation discipline.** Every finding is Gen 1, *Phantom*. A finding about
  a shared class says so, and says whether it was also seen on *Showdown*.
- **A verification WP, kept bounded.** Defects spin out; the exit criteria stay
  checkable and the WP closable.
- **The verdict advises Jeff.** Shipping *Phantom* in a packaged edition is his
  call; a GO makes it eligible.
