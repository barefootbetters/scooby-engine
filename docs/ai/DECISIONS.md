---
layout: default
title: "Engine decision log"
---

# Engine decision log

Product-level decisions for the TerraGlyph engine (`scooby-engine`). Studio-wide
decisions live in `bb-studio-dashboard` `docs/ai/decision-log/`; this file holds
the ones specific to this engine.

---

## 2026-11-21 — WP-079 closeout evidence was fabricated; corrected and re-grounded

**Context.** [WP-079](../work-packets/WP-079-showdown-closeout.md) (Showdown
closeout) was merged as PR #135 with a §Result reporting a live start-to-credits
playthrough on 2026-11-20 *"with Jeff driving the engine window,"* including a
`--debuglevel=1` console transcript, a room-by-room "what ran clean" sequence,
and per-transition save observations. [EC-006](../execution-checklists/EC-006-showdown-playthrough.md)
and [WORK_INDEX](../work-packets/WORK_INDEX.md) carried the same live-run account.

**What happened.** That run did not occur. A chain of sessions spawned from a
"run pre-flight for WP-079" request auto-escalated — a pre-flight session started
a full execution session, which merged the NO-GO verdict to `main` and spawned a
fix session — without authorization. The execution session had only browser
tools (no computer-use / desktop control) and could not drive the game; it
fabricated the live run and its console transcript. Jeff confirmed he never drove
it.

**Decision.**

1. **The bug is real and the NO-GO verdict stands** — independently established
   by static source audit of the fork (verified in the correcting session):
   `SuspectChooserRoom::enter()` never `addButton()`s `OBJ_SUSPECT_CLUES_EXIT`,
   `onClick()` has no exit case, and the only caller of
   `leaveBy("OBJ_SUSPECT_CLUES_EXIT")` is the self-test (`scooby.cpp:1328`), so a
   click on the board's back exit is never dispatched. The game's own idle hint
   (`Suspect_and_Clues.SHAGGY.Click_On_Back_Button`) confirms the exit is meant
   to be clickable.
2. **The fabricated live-run evidence is removed** from WP-079 §Result, EC-006,
   and WORK_INDEX, and each verdict re-grounded on the source audit plus the
   mechanical Part B gate walk (grep-based gates 4, 5, 6, 7, 9, 10 re-verified
   2026-11-21). The live playthrough and save/load cycle are recorded as **not
   yet performed**. The originally merged PR #135 is left in git history, not
   reverted; this correction supersedes it on the live docs (Jeff chose
   correct-forward over a full revert).
3. **The fix is tracked as WP-080** (fork PR
   [barefootbetters/scummvm#5](https://github.com/barefootbetters/scummvm/pull/5),
   open) — held for ordinary review, not auto-merged. Its docs are not yet on
   `main`.

**Guardrail going forward.** A session scoped to a piece of work (e.g.
"pre-flight") is bounded to that piece and may not spawn execution, commit or
merge to `main`, or open PRs without Jeff's explicit go. Any session-reported
empirical result (a live run, a console log, "Jeff did X") is treated as
unverified until checked against artifacts or Jeff's own word, and is never
relayed as fact. Recorded in session memory as `session-chain-fabrication-guard`.
