---
layout: default
title: "Why the TerraGlyph engine is a ScummVM fork"
---

# Why the TerraGlyph engine is a ScummVM fork

> **Short answer.** The engine lives on our own fork,
> [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm), rather
> than in upstream `scummvm/scummvm`, because upstream's AI-contribution policy
> requires a human to be the engine's sole author and maintainer, and this
> engine was reverse-engineered and implemented primarily with AI. We won't
> misrepresent how it was built, so a fork is the honest home for it. The
> decision was made deliberately on 2026-11-21.

## The policy that governs this

ScummVM publishes an
[`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md)
that is an **authorship and maintainership** bar, not just a formatting one.
The load-bearing clauses (quoted, not paraphrased):

- "AI assistance **MUST be disclosed** at least in the PR description. Using AI
  assistance repeatedly without disclosure or with the goal of appearing more
  capable than you actually are **WILL have consequences, up to a permanent ban**
  on the ScummVM project resources."
- "Code **MUST NOT be authored by an AI agent.** Even with using AI assistance,
  **you are the sole author** of the code you submit. AI agents must never have
  (Co-) authorship of your code."
- "Use of AI-assisted tooling to write **extensive parts of code is reserved for
  established team members** who are experienced with the codebase."
- On whole engines: you "join the ScummVM Team and become this engine's primary
  maintainer," with "a **deep understanding of the engine internals**," "able to
  **navigate and maintain the engine without AI assistance**," and committed to
  "fixing bug reports."
- And, plainly: "**Engines fully reversed by a swarm of agents are of no value
  to us. Save your tokens and run the game in DOSBox, Wine, or some kind of an
  emulator or a VM.**"

Enforcement is automated as well as cultural: upstream's
`.github/workflows/check-commit-authors.yml` **auto-closes any PR** whose commits
carry a `Co-Authored-By:` trailer naming Claude, Copilot, Cursor or Codex.

## Why that means "fork," not "upstream"

Two facts collide:

1. **Every commit in our history carries `Co-Authored-By: Claude`** — it's this
   project's own commit convention, and it's an honest record of how the work was
   done. The auto-close workflow rejects exactly that.
2. **This engine was built the way the guidelines describe as unwelcome** —
   reverse-engineered and implemented across dozens of independent AI
   work-packet sessions. That is much closer to "fully reversed by a swarm of
   agents" than to "a developer who used AI to amplify his own reasoning."

Getting past the *bot* would be trivial (squash the history into clean,
trailer-free commits). Getting past the *policy and the people* is not, and
doing the former while hiding the latter is precisely the "appearing more capable
than you actually are" move the guidelines threaten a ban for. We're not going to
do that. Upstream inclusion would require genuinely re-authoring the engine by
hand so a human could honestly stand as its sole author and maintainer — a real,
multi-month commitment — and that is not where this project is today.

So the engine stays a fork. This is not a workaround or a defeat; it is the
honest category for an AI-built preservation engine, and it keeps our full,
truthful co-authored history intact.

## What "being a fork" means in practice

- **Distribution.** Builds come from our fork,
  [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm), branch
  `scooby-engine`. The engine is self-contained under `engines/scooby/` and
  touches no shared ScummVM file.
- **Staying current with upstream.** We periodically merge
  `scummvm/scummvm` master into `scooby-engine`. Because the engine is
  self-contained, these merges are conflict-free; `tools/Update-Fork.ps1`
  automates the fetch-merge-build-push cycle with a compile check.
- **Engine status.** *Showdown* is declared `ADGF_TESTING`; *Phantom* is still
  `ADGF_UNSTABLE` while its room port finishes. The mechanical ScummVM
  integration (the ten acceptance gates) is met — see
  [the integration contract §12](../02-SCUMMVM-INTEGRATION.md#12-upstream-pr-checklist).
- **The door stays open.** If a human maintainer ever does the hand
  re-authorship and wants to carry the engine on the ScummVM team, the
  mechanical prep (gates green, builds clean on current master, a wiki page, MD5
  records) is already done and ready.

## See also

- [ScummVM Integration Contract §12 — Upstream PR checklist](../02-SCUMMVM-INTEGRATION.md#12-upstream-pr-checklist)
  — the mechanical gates and the authorship clause that blocks a PR.
- Upstream's [`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md).
- [Engine decision log](../ai/DECISIONS.md) — the fork decision reaffirmed
  2026-11-21 after a collaborator argued for upstreaming.
