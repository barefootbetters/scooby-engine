---
layout: default
title: "Engine decision log"
---

# Engine decision log

Product-level decisions for the TerraGlyph engine (`scooby-engine`). Studio-wide
decisions live in `bb-studio-dashboard` `docs/ai/decision-log/`; this file holds
the ones specific to this engine.

---

## 2026-11-22 — Merged-PR survey on the precedent question; fork decision unchanged

**Context.** Following up the [2026-11-21 reaffirmation](#2026-11-21--upstream-submission-reconsidered-after-collaborator-pushback-fork-decision-reaffirmed)
(which asked Mony for specifics on accepted engines with genuinely similar
provenance), Mony replied that recent ScummVM merges — "including ones for new
engines" — explicitly mention AI assistance, that the rules are "really more
vague suggestions than anything else," and that wording and framing matter. This
is a checkable claim, so it was checked rather than taken on his word or on our
prior reading.

**Observed** (surveyed 2026-11-22 via `gh` against `scummvm/scummvm` merged PRs):

- **AI _assistance_, disclosed, does merge** — Mony is right on that narrow
  point. PR [#8084](https://github.com/scummvm/scummvm/pull/8084) (nickknissen,
  DIRECTOR fixes, merged 2026-11-18) states plainly: *"I used Claude and Codex to
  investigate the causes … write the patches and prepare the commits. I have
  reviewed every change and tested it."* So AI disclosure is not disqualifying.
  But it is a **bug-fix to an existing engine by a contributor who stands as
  sole author** — the permitted lane — and the disclosure is prose in the PR
  body; no `Co-Authored-By:` AI trailer in the commits.
- **The recently merged _new engines_ are human-authored, not AI.** SNATCHER
  ([#8029](https://github.com/scummvm/scummvm/pull/8029), athrxx, merged
  2026-11-15) advertises *"This engine is completely AI free."* HAROLD/BCB
  ([#7989](https://github.com/scummvm/scummvm/pull/7989), Scorpeg, merged
  2026-10-22) is a human decompilation with no AI mention. Neither carries AI
  co-author trailers.
- **No surveyed merge pairs a _new engine_ with _AI authorship_** — our case.
  The guidelines' distinction (AI-assisted work by a member who authors, vs. an
  engine authored by agents) is holding in practice, not dissolving.

**Bearing on the decision.** This **confirms Hold at fork.** The permissive
precedent is for assisted authorship — a lane this engine is not in; the
comparable precedent (an AI-_authored_ new engine, disclosed and accepted) still
does not appear. "Framing matters" cuts the other way here: framing an
agent-authored engine as member-assisted authorship is exactly the "appearing
more capable than you are" misrepresentation the ban clause targets. The decision
is unchanged and the door stays open on the same terms — a specific merged PR
showing an AI-authored new engine would still reopen it.

**No outward action taken.** The survey was read-only; nothing posted upstream.

## 2026-11-21 — Upstream submission reconsidered after collaborator pushback; fork decision reaffirmed

**Context.** The same day the fork decision was recorded ([why the engine is a
ScummVM fork](../reference/why-forked-scummvm.md); options in
[WP-082's decision brief](../reference/upstream-submission-decision-brief.md)),
collaborator Simeon Armenchev (monyarm) — a ScummVM-community contributor with
his own fork, NovelVM — argued by email for reconsidering upstream submission:
that the engine's clean-room development (docs and observations written, engine
code written from those) is materially different from the full-AI-decomp engines
ScummVM's `AI-GUIDELINES.md` rejects; that the "swarm of agents" line targets
full decomps rather than a clean-room engine; that some engines with similar
development have reportedly been accepted; and that a single-engine fork hurts
discoverability and maintenance. His concrete proposal was Option B from the
brief — ask the ScummVM Discord directly, disclosed.

**What was weighed.** His clean-room point is correct, and it is why the engine's
code is legally clean — but it addresses the wrong bar. The blocker isn't the
clean-room / "swarm" question, nor the CI author-check bot (trivially evaded by
squashing the `Co-Authored-By: Claude` trailers); it is `AI-GUIDELINES.md`'s
**authorship and maintainership** requirement: code must not be AI-authored, a
human must stand as sole author, and the maintainer must be able to navigate and
fix the engine without AI. The engine's honest history — dozens of AI work-packet
sessions authoring it — does not clear that bar, and squashing the trailers to
pass the bot while not volunteering how it was built is the "appearing more
capable than you are" move the guidelines threaten a ban for. His adoption point
(fork = poorer discovery and maintenance) is valid and is already recorded as the
Option A trade-off.

**Decision (Jeff).** **Hold at fork (Option A).** The decision stands as recorded
in [why-forked-scummvm.md](../reference/why-forked-scummvm.md): the fork is the
honest home for an AI-authored preservation engine, with the full co-authored
history intact — no trailer-stripped PR, no misrepresentation. The door stays
open: the mechanical prep (gates green, clean build on current master, wiki page,
MD5 records) is ready should a human ever do the hand re-authorship and choose to
maintain it on the ScummVM team. **Option B (engage the ScummVM team directly,
disclosed) is declined for now, not foreclosed** — it remains the first step if
upstream inclusion later becomes a goal. Mony was asked (by reply) for specifics
on any accepted engines with genuinely similar (AI-authored, disclosed)
provenance; concrete precedent is the input that would reopen the question.

**No outward action taken.** Nothing was posted to ScummVM Discord, the forum or
the mailing list; no upstream PR opened; no fork history rewritten. The reply to
Mony is Jeff's to send.

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
