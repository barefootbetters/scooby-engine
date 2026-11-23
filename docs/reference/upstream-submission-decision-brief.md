---
layout: default
title: "Decision brief — upstream ScummVM submission & AI-authorship"
---

# Decision brief: submitting `scooby` to upstream ScummVM

> **Status:** Decision brief for Jeff. Prepared by WP-082 (upstream-submission
> prep). **This document decides nothing** — it lays out the options, their
> mechanics, and an honest read on acceptance, and hands the call back to Jeff.
> Nothing in WP-082 rewrites the fork's history or opens an upstream PR; both
> wait on the decision recorded here.
>
> **Date:** 2026-11-21. **Author:** Jeff (with AI assistance; this brief is a
> draft for his judgment, not a recommendation he is bound to).

---

## 1. The decision in one paragraph

The `scooby` (TerraGlyph) engine is mechanically close to submission-ready for
`scummvm/scummvm` (see [WP-082](../work-packets/WP-082-upstream-submission-prep.md)
for the gate status). But upstream's
[`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md)
imposes an **authorship and maintainership bar**, not just a formatting bar, and
the fork's entire history carries `Co-Authored-By: Claude` trailers that an
upstream CI workflow (`check-commit-authors.yml`) auto-closes on sight. Getting
past the *bot* is trivial (squash to clean, human-authored commits). Getting
past the *policy and the people* is the real question, and it turns on one thing
only you can answer honestly: **are you the engine's author** — able to maintain
it without AI and commit to it as a ScummVM team member — **or was this built
primarily by AI agents you supervised?** The guidelines treat those two very
differently.

## 2. What upstream actually requires (primary source)

From [`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md),
current `master` (quoted, not paraphrased):

- "AI assistance **MUST be disclosed** at least in the PR description. Using AI
  assistance repeatedly without disclosure or with the goal of appearing more
  capable than you actually are **WILL have consequences, up to a permanent ban**
  on the ScummVM project resources."
- "Every commit and PR must be done by humans and with proper scoping. **All
  messages must be written by a human being.**"
- "Code **MUST NOT be authored by an AI agent.** Even with using AI assistance,
  **you are the sole author** of the code you submit. AI agents must never have
  (Co-) authorship of your code."
- "Use of AI-assisted tooling to write **extensive parts of code is reserved for
  established team members** who are experienced with the codebase and its
  conventions."
- On whole engines: "You join the ScummVM Team and become this engine's primary
  maintainer … You have a **deep understanding of the engine internals**, are
  able to **navigate and maintain the engine without AI assistance**, are
  committed to monitoring, engaging with and fixing bug reports."
- And, bluntly: "**Engines fully reversed by a swarm of agents are of no value
  to us. Save your tokens and run the game in DOSBox, Wine, or some kind of an
  emulator or a VM.**"

The CI enforcement: `.github/workflows/check-commit-authors.yml` closes any PR
whose commits carry a `Co-Authored-By:` trailer naming Claude/Copilot/Cursor/
Codex. **Every commit in the fork's history carries one** (the project's own
commit convention), so the branch cannot be submitted as-is.

## 3. The honest read on acceptance

I'm not going to oversell this. Two things are true at once:

1. **Mechanically, the engine is in good shape.** It conforms to ScummVM's
   architecture (the ten acceptance gates — [WP-082](../work-packets/WP-082-upstream-submission-prep.md)),
   it's single-threaded, it uses `Common::File`/`Audio::Mixer`/`Video::BinkDecoder`,
   it has GPL headers, it builds clean. A reviewer looking only at the code would
   find a competently structured engine.

2. **Policy-wise, this project is close to the exact thing the guidelines name as
   unwelcome.** The engine was reverse-engineered and implemented across dozens
   of independent AI work-packet sessions, with per-WP agent traces and at least
   one documented fabrication incident ([DECISIONS.md](../ai/DECISIONS.md)). That
   is much closer to "fully reversed by a swarm of agents" than to "a developer
   who used AI to amplify his own reasoning." Stripping the `Co-Authored-By`
   trailers makes the *bot* pass; it does not make the *authorship claim* true.

So the realistic likelihood of acceptance, **submitted as what it is**, is
**low** — and attempting to pass it off as primarily human-authored work would
run straight into the guidelines' "appearing more capable than you actually are
… up to a permanent ban" clause. That's not a risk worth taking, and it's
contrary to your own truth-discipline standard.

The one path where acceptance is *plausible* is narrow: **you genuinely become
the engine's developer-maintainer.** If you can honestly say you understand the
internals deeply enough to fix bugs and track ScummVM API churn without AI, and
you're willing to join the team and carry that for years, then an honest,
fully-disclosed submission is legitimate and the AI was a tool amplifying you —
which is exactly what the guidelines permit. Only you know whether that's true
today. If it isn't yet but you want it to be, that's a real (large) body of
work, not a formatting pass.

## 4. The options

### Option A — Keep it as a fork (lowest-friction, most honest default)

Ship builds from `barefootbetters/scummvm` directly. No upstream PR. The full
co-authored history stays intact as the honest record of how it was built.

- **Pros:** zero authorship friction; no misrepresentation; you keep full
  control and the honest provenance; players who want it can use your builds.
- **Cons:** no upstream distribution or community maintenance; discoverability is
  on you.
- **Mechanics:** nothing to do — this is the status quo. The WP-082 prep
  (ADGF_TESTING, clean build, wiki page) still improves the fork.

### Option B — Engage upstream transparently *first*, then decide

Before any PR, post to the ScummVM team (Discord `#engine-development` / the
forum / the mailing list): "I've built a TerraGlyph engine (Showdown playable,
Phantom in progress) with heavy AI assistance — here's exactly how. Would you
consider it, and under what conditions re: maintainership?" Let them tell you.

- **Pros:** respects the project's own call instead of surprising them with a
  trailer-stripped PR; cheap; high-information; keeps you on the right side of
  the disclosure rule. If they say no, you've lost nothing and Option A stands.
- **Cons:** the honest answer may well be no (see §3).
- **This is the recommended first step if upstream inclusion matters to you at
  all** — it's the move that's compatible with every other option.

### Option C — Honest disclosed submission, you as genuine maintainer

Only if §3's narrow path is truthfully you. Squash the engine into clean,
human-authored `SCOOBY: <subsystem>: <description>` commits (no AI trailers),
replay onto current master, write the PR and commit messages yourself, disclose
AI assistance fully, join the team as maintainer.

- **Pros:** the legitimate route to upstream if the authorship claim is honest.
- **Cons:** requires the multi-year maintainer commitment and genuine deep
  understanding; even then, "swarm of agents" skepticism may sink it; the squash
  replaces the co-authored history on the submission branch (the fork keeps it).
- **Mechanics:** see §5 — and note the squash *is* the master-rebase, so don't
  do a separate throwaway rebase first.

### Option D — Human re-authorship

A human genuinely re-implements/reworks the engine to the point of true
authorship, then submits clean. Highest effort; only if upstream inclusion is a
hard goal and Option C's honesty test fails today.

## 5. The rebase ↔ authorship coupling (why I did *not* pre-rebase)

The brief's technical-prep step asked for a rebase of `scooby-engine` onto
current master (the pin is 797 commits behind). I deliberately did **not** run a
full 797-commit history replay, because **it's coupled to the authorship
decision and would be thrown away:**

- If you choose **Option C** (squash to clean history), the squash reapplies the
  *final engine tree* onto current master in one operation. A prior commit-by-
  commit rebase of the old co-authored history is discarded by that squash — only
  the *API-drift fixes* survive, and those are captured just as well by building
  the tree against master directly (which WP-082 does — see the build-drift
  result there).
- If you choose **Option A/B**, there's no upstream branch to rebase at all.

So the reusable, decision-independent work is "does the current engine tree build
against current master?" — which I tested directly (WP-082) — **not** a history
rewrite. The history rewrite happens once, as part of whichever submission path
you pick, if any.

## 6. What I recommend you decide between

This is yours. My honest framing:

- If upstream inclusion is a *nice-to-have*: **Option A** (stay a fork). It's the
  honest, zero-risk home for an AI-built preservation engine, and it's where the
  guidelines effectively point work like this.
- If upstream inclusion *matters* to you: **Option B first** (ask them, openly),
  and proceed to **Option C** only if both (a) they're receptive and (b) you can
  stand honestly as the maintainer who can carry it without AI. Do **not** open a
  trailer-stripped PR that leans on the bot while hiding the "how" — that's the
  one move that can actually get you banned and it's beneath the project's and
  your own standards.

Whatever you pick, the WP-082 prep (ADGF_TESTING flip, gate evidence, wiki page,
build-on-master check) is good for the fork regardless and is ready if you ever
get a green light.

---

*Prepared under WP-082. No upstream PR opened, no ScummVM wiki posted, no fork
history rewritten in producing this brief.*
