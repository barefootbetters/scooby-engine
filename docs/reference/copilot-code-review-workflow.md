---
layout: default
title: "Reviewing engine changes: static checks, Copilot review and testing"
---

# Reviewing engine changes: static checks, Copilot review and testing

How a change to `engines/terraglyph/` gets checked before it merges into the
fork. There are three layers: a PowerShell checker for the rules a machine can
check, GitHub Copilot code review for the rules that need judgment, and
building and playing the game. The developer writes every change and decides
what to do about every finding.

> **Copilot is a reviewer, not an engine developer.** It comments on code. It
> does not write, fix or commit engine code in this workflow.

## Contents

1. [Purpose](#purpose)
2. [Where the engine stands](#where-the-engine-stands)
3. [ScummVM's AI rules](#scummvms-ai-rules)
4. [Prerequisites](#prerequisites)
5. [How Copilot finds its instructions](#how-copilot-finds-its-instructions)
6. [Initial setup](#initial-setup)
7. [Daily workflow](#daily-workflow)
8. [Who checks what](#who-checks-what)
9. [The static checker](#the-static-checker)
10. [Preparing an upstream submission](#preparing-an-upstream-submission)
11. [AI disclosure template](#ai-disclosure-template)
12. [Maintenance](#maintenance)
13. [References](#references)

## Purpose

ScummVM has written rules for formatting, naming, portability and commit
messages. It reviews engine submissions against them, and its AI policy adds
rules about who authors the code. Catching violations in the fork is cheaper
than having an upstream reviewer catch them.

The workflow splits the checking by what each tool is good at:

- **Layer A, the static checker** (`tools/Check-ScummvmStyle.ps1` in this
  repo). It is fast and deterministic, and it covers the rules a script can
  check without false alarms.
- **Layer B, Copilot code review** on a pull request inside the fork. It
  covers what needs judgment: portability, ownership, endianness, naming
  intent, structure and comment quality. Its findings are advice; each one is
  checked by a person.
- **Layer C, building and testing.** Compiling, detection, loading resources
  and playing the game. Neither A nor B replaces it.

Passing all three layers does not guarantee ScummVM will accept the engine.
Upstream reviewers decide that.

## Where the engine stands

The engine code in the fork today was written in AI work-packet sessions;
its commits carry `Co-Authored-By: Claude` trailers. Jeff's recorded decision
is to keep the engine on the fork, with that history intact
([decisions of 2026-11-21 and 2026-11-22](../ai/DECISIONS.md); background in
[why the engine is a ScummVM fork](why-forked-scummvm.md)).

This workflow looks forward. It covers changes written by hand from now on,
including any future hand re-authorship. It does not change where the
existing code came from or the fork decision. Running old code through it
does not make that code hand-written.

## ScummVM's AI rules

From upstream [`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md)
(read 2026-11-26). The fork root carries the same file and an `AGENTS.md`
that points to it.

| Upstream rule | How this workflow meets it |
|---|---|
| All code, AI-assisted or not, must follow the formatting, naming and commit conventions | Layer A checks the mechanical ones; Layer B is pointed at the rest |
| AI assistance must be disclosed, at least in the PR description | The [disclosure template](#ai-disclosure-template) names Copilot review |
| Code must not be authored by an AI agent; AI never has (co-)authorship | Copilot only comments. Its suggested changes are never committed. The checker flags AI co-author trailers |
| Every commit and PR is made by a human; all messages are written by a human | The developer writes commit messages and PR descriptions. Copilot is told not to |
| Lengthy LLM-oriented comments are forbidden | Layer B flags long explanatory comments (`[COMMENT]`) |
| You must test before submitting | Layer C is a required step, not an option |
| A new engine's submitter joins the team as its maintainer and can maintain it without AI | Hand-written changes, reviewed and fixed by hand, are how that ability is built. Copilot's comments don't replace it |
| No AI-generated media | This workflow handles code only; no AI art is produced |

Upstream also closes any PR whose commits carry a `Co-Authored-By:` trailer
naming Claude, Copilot, Cursor or Codex (`.github/workflows/check-commit-authors.yml`).

Three uses of AI are kept apart:

- **AI-assisted review.** Copilot reads a diff and leaves comments; the
  developer decides and writes any fix. This is assistance, and it is
  disclosed.
- **AI-generated code.** Code an AI wrote, including a Copilot "Commit
  suggestion" or a "Fix with Copilot" commit. This workflow does not use it.
- **AI-assisted research outside the engine.** File-format notes, Python
  probes and work packets in this repo. They are not part of a ScummVM
  submission, but the disclosure says they exist.

## Prerequisites

- **A GitHub Copilot plan that includes code review.** Copilot Free does not
  include it; Pro and higher do. Reviews are paid in AI credits ($0.01
  each). GitHub's rough averages per review are $0.25 at Lite, $1.50 at
  Balanced and $10 at Max, and every re-review is a new review. Pro includes
  1,500 credits a month. See
  [Copilot plans](https://docs.github.com/en/copilot/get-started/plans),
  [billing for individuals](https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing)
  and [using code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review).
- **Admin rights on `barefootbetters/scummvm`** to change its Copilot
  settings.
- **The repository setting "Use custom instructions when reviewing pull
  requests" turned on:** Settings → Copilot → Code review.
- **Copilot cloud agent left off.** "Fix with Copilot" needs it, so leaving it
  off means that button can't commit to the PR.
- **PowerShell 7** (`pwsh`). The checker was tested on 7.6.
- **Git** on the `PATH`, a checkout or worktree of the fork, and this repo.
- **The existing ScummVM build environment.** The project's recorded
  toolchain is MSYS2 UCRT64 (see
  [scummvm-smart-tv](scummvm-smart-tv.md) and the WP records).

## How Copilot finds its instructions

The fork holds two instruction files on `scooby-engine`:

- **`.github/copilot-instructions.md`** applies repo-wide. It says Copilot
  reviews only, comments only on `engines/terraglyph/`, reports one problem
  per comment with a category tag (`[FORMAT]`, `[NAMING]`, `[PORTABILITY]`,
  `[ENDIAN]`, `[MEMORY]`, `[STRUCTURE]`, `[COMMENT]`, `[LICENSE]`), and names
  the rule behind each finding. Copilot Chat in Visual Studio reads both
  files too, so the "don't write code" instruction holds there as well.
- **`.github/instructions/scummvm-engine.instructions.md`** applies to the
  engine sources only:

  ```yaml
  ---
  applyTo: "engines/terraglyph/**/*.cpp,engines/terraglyph/**/*.h"
  excludeAgent: "cloud-agent"
  ---
  ```

  It holds the ScummVM rules, each marked upstream rule, upstream pattern or
  project rule. Multiple patterns are separated with commas, the form GitHub
  documents. `excludeAgent: "cloud-agent"` keeps the file for code review only
  (the accepted values are `"code-review"` and `"cloud-agent"`).

What GitHub documents, and what follows from it:

- **Instructions come from the PR's head branch, not its base.** A feature
  branch cut from `scooby-engine` inherits the files. A PR that edits the
  files is reviewed with its own edited copy.
- **Code review also reads `AGENTS.md`.** The fork's copy is upstream's,
  which points the reviewer at `AI-GUIDELINES.md`.
- **The files are instructions, not settings.** GitHub cannot limit code
  review to certain paths on a personal plan; content exclusion is
  Business/Enterprise only. "Comment only on `engines/terraglyph/`" and "don't
  propose code" are requests Copilot usually follows, not guarantees. It can
  still produce a suggested-change block, and there is no setting to turn
  those off.
- **Copilot labels each comment High, Medium or Low** on its own; the
  category tags are added on top.
- **Copilot's review is a "Comment" review.** It does not approve or block
  merging unless Copilot approvals are turned on. They are off by default;
  leave them off.

## Initial setup

1. **Add the two instruction files** in a fork worktree cut from
   `origin/scooby-engine`:

   ```powershell
   .\tools\New-ForkWorktree.ps1 -Branch copilot-review-config
   ```

2. **Commit them on their own**, with no engine changes in the same commit,
   for example `GITHUB: Add Copilot code review instructions`. Keeping fork-only
   configuration in commits of its own is what keeps it out of an upstream
   branch later ([below](#preparing-an-upstream-submission)).
3. **Merge to `scooby-engine`** through a fork PR, so every later feature
   branch has the files.
4. **Check the settings:** repo Settings → Copilot → Code review. Turn on
   "Use custom instructions when reviewing pull requests". Set the default
   effort to **Balanced**, and set the maximum effort to Balanced so a review
   can't run at Max by accident.
5. **Leave automatic review off.** Automatic review (personal Copilot
   settings or a branch ruleset with "Automatically request Copilot code
   review") would also review the upstream-merge PRs into `scooby-engine`.
   Those PRs are large, the review is charged by size, and they hold no
   TerraGlyph code. For a solo developer, asking for a review on the PRs that
   need one costs less and loses nothing. Revisit this if engine PRs start
   outnumbering upstream syncs and you keep forgetting to ask.
6. **Test it on a small PR**: a branch with a one-line, deliberately
   non-compliant engine change (a `std::` use, say). Request a review, check
   that the comments are tagged and describe the problem without code, then
   close the PR without merging.

## Daily workflow

1. **Write the change by hand** in Visual Studio, in a fork worktree on its
   own branch (`tools\New-ForkWorktree.ps1 -Branch <name>`).
2. **Run the static checker:**

   ```powershell
   pwsh -File tools\Check-ScummvmStyle.ps1 -ScummvmPath C:\claude-worktrees\scummvm-<name> -Scope Changed
   ```

3. **Fix every finding by hand.** The checker never edits files.
4. **Build the engine** with the usual Scooby-only configure and make, and
   fix any warnings in `engines/terraglyph/`.
5. **Run what tests exist:** detection, the `--debuglevel` self-check
   channels, and a play-through of the rooms you touched.
6. **Push and open a pull request inside `barefootbetters/scummvm`.**
7. **Target `scooby-engine`.** Never `scummvm/scummvm`, and not the fork's
   `master`, which tracks upstream.
8. **Request a review:** Reviewers → Copilot → Request, at Balanced. Use Lite
   for a small mechanical change.
9. **Judge each finding** against the rule it names. Copilot can be wrong. If
   a finding cites a rule that isn't in the ScummVM sources, dismiss it.
10. **Fix the real ones yourself.** Don't click "Commit suggestion" or "Fix
    with Copilot". Re-type the fix in your editor if you agree with it.
11. **Rebuild, retest and rerun the checker.** Re-request a review only when
    the fix changed something Copilot should look at again; each re-review
    is charged.
12. **Merge the PR** when you are satisfied.

Upstream submission is a separate, later process; nothing in these twelve
steps sends code to `scummvm/scummvm`.

A pull request from a collaborator (for example monyarm's engine
refactor, fork PR #12) goes through the same layers. Its author answers for
its code; the AI rules above bind whoever submits a change upstream.

## Who checks what

| Check | Static checker | Copilot | Compiler / build | Runtime test | Human |
|---|---|---|---|---|---|
| Tabs, trailing whitespace, final newline, LF endings | ✅ | | | | |
| GPL license header, header guards | ✅ | | | | |
| `std::`, STL headers, exceptions | ✅ | | | | |
| `fopen` / `printf` family | ✅ (early) | | ✅ (`common/forbidden.h` makes them compile errors) | | |
| Commit subject prefix, length, blank line, merges, AI trailers | ✅ | | | | |
| Brace style, spacing, `switch` layout | | ✅ | | | ✅ |
| Naming conventions | | ✅ | | | ✅ |
| Global constructors, non-const static locals | | ✅ | clang `-Wglobal-constructors` | | ✅ |
| Endianness, struct packing, fixed-width types | | ✅ | | big-endian testing, where available | ✅ |
| Memory ownership and cleanup | | ✅ | | leak and crash checks | ✅ |
| Comment quality and length | | ✅ | | | ✅ |
| Detection/engine split, `module.mk`, shared-code changes | | ✅ | ✅ (detection-only build) | | ✅ |
| Compiles without warnings | | | ✅ | | |
| Detects the game, loads resources, plays correctly | | | | ✅ | ✅ |
| Commit message in the present tense, scoped sensibly | | | | | ✅ |
| Accept or dismiss each Copilot finding | | | | | ✅ |

## The static checker

`tools/Check-ScummvmStyle.ps1` (in this repo, not the fork) reads
`engines/terraglyph/**/*.cpp` and `*.h` and the commits in
`<BaseRef>..HEAD`. It never writes a file. Run it from any directory:

| Parameter | Default | Meaning |
|---|---|---|
| `-ScummvmPath` | (required) | The fork checkout or worktree. Any folder inside it works |
| `-BaseRef` | `origin/scooby-engine` | Commits after this are checked. Use `upstream/master` to see what an upstream PR would carry |
| `-Scope` | `All` | `Changed`: only engine files changed since the merge base, plus uncommitted and untracked ones |
| `-SkipCommits` | off | Check source files only |
| `-EnginePrefix` | `TERRAGLYPH` | The subsystem a commit touching the engine must use; `''` turns that check off |

Each finding is printed as `<file>(<line>): error <RULE>: <message>`, the
format Visual Studio's Output window turns into a link. Exit code 0 means
clean, 1 means findings, and 2 means a usage or run error (bad path, unknown
`BaseRef`, git failure).

**What it checks, and the source of each rule:**

| Rule | Source |
|---|---|
| `LICENSE-HEADER`: the standard ScummVM GPLv3-or-later comment opens the file | GPLv3+ is required by `AI-GUIDELINES.md`; the header text is the upstream pattern |
| `INDENT-SPACES`, `INDENT-MIXED`: a statement indented with spaces, or a space before a tab | wiki Code Formatting Conventions; `.editorconfig` |
| `TRAILING-WS`, `FINAL-NEWLINE` | `.editorconfig`; upstream pre-commit hooks |
| `EOL-CRLF`: a file stored with CRLF in git | `.gitattributes` (`*.cpp`/`*.h` `eol=lf`) |
| `STD-NAMESPACE`, `STL-HEADER`, `STD-WRAPPER` | wiki Coding Conventions: new engines use `common/` directly; `Std::` is for porting |
| `EXCEPTION`: `throw`, `try`, `catch` | wiki Coding Conventions |
| `FORBIDDEN-BYPASS`: `#define FORBIDDEN_SYMBOL_*` | it turns off `common/forbidden.h` |
| `RAW-FILE-IO`, `PRINT-FUNCTION` | wiki Coding Conventions; also compile errors via `forbidden.h` |
| `HEADER-GUARD`: `TERRAGLYPH_<FILE>_H` or `TERRAGLYPH_<PATH>_H` | upstream pattern (not a written rule). `detection_tables.h` is exempt, as in 60 of 73 upstream engines |
| `COMMIT-PREFIX`: subject starts with a CAPS subsystem | upstream `devtools/check-commit-msg.py` |
| `COMMIT-SUBSYSTEM`: a commit touching the engine uses `TERRAGLYPH:` | project rule |
| `COMMIT-LENGTH` (≤ 50 characters), `COMMIT-BLANK` (blank second line) | wiki Commit Guidelines. A GitHub squash merge adds ` (#NN)`, which counts |
| `COMMIT-MERGE` | wiki Commit Guidelines: linear history only |
| `AI-TRAILER`: a `Co-authored-by` naming an AI tool, or a "Generated with" AI line | `AI-GUIDELINES.md`; `check-commit-authors.yml` |

**What it doesn't check, on purpose:**

- **RTTI.** Upstream engines use `dynamic_cast` (334 files on `master`), and
  ScummVM doesn't turn RTTI off.
- **Present tense.** A regex can't judge grammar.
- **Global constructors and static locals.** A pattern can't tell them from
  valid code, such as a `static` method in a local struct.

Comments and string literals are blanked before the token checks, so "try
to" in a comment or "throw" inside a debug string is not reported. Spaces
that align a continuation line under the line above are allowed.

**Known limits:**

- A line comment continued with a trailing backslash can confuse it.
- So can a method declared with the same name as a C I/O function.
- Prefixed character literals (`L'x'`) are not blanked.

**Tests:** run `pwsh -File tools\tests\Test-CheckScummvmStyle.ps1`. It builds
throwaway git repos under `%TEMP%` and runs 28 cases: clean code, each rule,
commit-range limits, `-Scope Changed`, config errors and running from
another folder. It never touches a real checkout.

**Baseline on 2026-11-26** (fork `scooby-engine` @ `ff490ad944`, 152 engine
files):

- **Sources:** one finding. `story_check.cpp` does not end with a newline.
- **Commits against `upstream/master`:** 87 `AI-TRAILER`, 67 `COMMIT-LENGTH`
  and 5 `COMMIT-MERGE`. That is the existing history described in
  [where the engine stands](#where-the-engine-stands), not new problems.

## Preparing an upstream submission

None of this happens until there is a decision to submit. It is not
automated, and nothing here rewrites history.

**Where the upstream branch comes from.** If a submission ever happens, its
branch is built from `upstream/master`, not by pushing `scooby-engine`. The
[decision brief §5](upstream-submission-decision-brief.md) already plans the
upstream branch as a fresh, squashed series on current `master`. Fork-only
files (the Copilot instructions, anything else under `.github/` that upstream
doesn't have) then stay out as long as they are never added to that branch.

**Removing a file from the diff vs. removing a commit from history:**

- **Removing a file from the diff.** A later commit deletes the file. The
  net diff no longer shows it, but the commits that added and deleted it are
  still in the branch. ScummVM reviews commits one by one, so both would
  still be visible.
- **Removing a commit from history.** The commit is dropped or rewritten
  (rebase, or a fresh cherry-picked series). The file never appears, but the
  branch's history changes. Do that only on a new branch made for the
  submission, never on `scooby-engine`, which others build on.

Building the upstream branch fresh from `upstream/master` avoids both: the
fork-only commits are never picked.

**Before opening the upstream PR, check:**

```powershell
git fetch upstream
git log --oneline upstream/master..<submission-branch>
git diff --stat upstream/master...<submission-branch>
git diff --stat upstream/master...<submission-branch> -- .github
pwsh -File tools\Check-ScummvmStyle.ps1 -ScummvmPath <worktree> -BaseRef upstream/master
```

- The commit list holds only intended commits, with no merges.
- The diff touches only `engines/terraglyph/` and the files a new engine
  must change (credits, and any generated files the PR checklist names).
- The `.github` diff is empty.
- The checker reports nothing. Any `AI-TRAILER` finding means
  `check-commit-authors.yml` will close the PR.

## AI disclosure template

ScummVM requires AI assistance to be disclosed in the PR description.
Upstream's PR template also requires the description to be written by a
human. Use this as a starting point and rewrite it in your own words. Each
bracket has to be true when you submit; if one isn't, change it to what
happened.

```text
AI disclosure:
- Engine code: [written by me / describe what was AI-assisted and how].
  [I am the sole author of the code in this PR.]
- Review: I used GitHub Copilot code review on pull requests in my fork.
  It left comments; I checked each one and made any changes myself. No
  Copilot suggestion was committed.
- Research: [the file-format research, probing scripts and notes in a
  separate repository were made with AI assistance]. None of that is
  part of this PR.
- Art and media: no AI-generated art or media.
```

Do not write "no AI was used." Copilot review alone makes that false.

## Maintenance

Revisit the rules, the instruction files and the checker:

- **Before any upstream submission:** re-read `AI-GUIDELINES.md`, the three
  wiki pages, `.clang-format` and `.editorconfig` on current `master`, and
  rerun the checker against `upstream/master`.
- **When upstream changes `AI-GUIDELINES.md`, `check-commit-authors.yml`,
  `devtools/check-commit-msg.py` or `.pre-commit-config.yaml`.** Check these
  after each upstream sync into the fork.
- **When GitHub changes Copilot code review.** Billing, effort levels and
  instruction handling all changed during 2026. Check the
  [changelog](https://github.blog/changelog/label/copilot/) before relying on
  a detail here.
- **When Copilot keeps getting the same thing wrong:** tighten the instruction
  file, or move the rule into the checker if a script can check it.
- **When the engine layout changes** (subfolders, a new detection file): rerun
  the checker tests and check the header-guard rule.

## References

ScummVM:

- [`AI-GUIDELINES.md`](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md)
  and [`AGENTS.md`](https://github.com/scummvm/scummvm/blob/master/AGENTS.md)
- [`check-commit-authors.yml`](https://github.com/scummvm/scummvm/blob/master/.github/workflows/check-commit-authors.yml)
  and the [PR template](https://github.com/scummvm/scummvm/blob/master/.github/pull_request_template.md)
- [`CONTRIBUTING.md`](https://github.com/scummvm/scummvm/blob/master/CONTRIBUTING.md),
  [`.editorconfig`](https://github.com/scummvm/scummvm/blob/master/.editorconfig),
  [`.clang-format`](https://github.com/scummvm/scummvm/blob/master/.clang-format),
  [`.pre-commit-config.yaml`](https://github.com/scummvm/scummvm/blob/master/.pre-commit-config.yaml)
  and [`devtools/check-commit-msg.py`](https://github.com/scummvm/scummvm/blob/master/devtools/check-commit-msg.py)
- [`common/forbidden.h`](https://github.com/scummvm/scummvm/blob/master/common/forbidden.h)
- Wiki: [Code Formatting Conventions](https://wiki.scummvm.org/index.php/Code_Formatting_Conventions),
  [Coding Conventions](https://wiki.scummvm.org/index.php/Coding_Conventions),
  [Commit Guidelines](https://wiki.scummvm.org/index.php?title=Commit_Guidelines)

GitHub Copilot (read 2026-11-26):

- [Copilot plans](https://docs.github.com/en/copilot/get-started/plans)
- [About Copilot code review](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/code-review)
- [Using Copilot code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review):
  requesting, effort levels and costs, approvals, "Fix with Copilot"
- [Configuring code review](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review):
  automatic review, effort and maximum effort
- [Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions):
  `applyTo`, `excludeAgent`, head-branch reading
- [Custom instructions support by environment](https://docs.github.com/en/copilot/reference/custom-instructions-support)
- [Content exclusion](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/content-exclusion)
- [Usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing)

Project:

- [Why the engine is a ScummVM fork](why-forked-scummvm.md),
  [the upstream-submission decision brief](upstream-submission-decision-brief.md),
  [the decision log](../ai/DECISIONS.md)
- [WP-082: upstream submission prep](../work-packets/WP-082-upstream-submission-prep.md)
  (the earlier style and gate pass)
