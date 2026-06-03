---
layout: default
title: "WP Lifecycle — Drafting, Pre-Flight, Execution, Close"
---

# WP Lifecycle

> **REFERENCE — How a Work Packet moves from idea to ✅ Done. Not an execution prompt.**
>
> **Subordination (descending authority):**
> 1. [docs/01-VISION](../01-VISION.md) — vision, goals, scope, decisions log
> 2. [docs/02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md) — upstream integration contract
> 3. [docs/work-packets/WORK_INDEX](../work-packets/WORK_INDEX.md) — WP + EC catalog and ordering
> 4. [docs/reference/pre-flight](pre-flight.md) — readiness gate
>
> If this doc conflicts with any of the above, the higher-authority doc wins.

---

## Purpose

Pre-flight covers the moment between "WP is drafted" and "execution opens." This doc covers everything around it: how you get **to** a drafted WP, how you get **through** execution after pre-flight clears, and how you cleanly **abandon** work that no longer makes sense.

It exists because the gate (pre-flight) is well-codified but the off-ramps and on-ramps aren't, and the silent failure mode in a small project is *premature WP authoring* — drafting WPs whose work has already shipped via a different commit, or that turn out to belong to a different phase. Catching that at the upstream of pre-flight is cheaper than catching it inside.

This doc is a navigation aid. The operator decides whether to follow each step; if a step blocks progress because it's wrong for the work at hand, route around it and note the bypass.

---

## Status vocabulary

Same closed set as [WORK_INDEX](../work-packets/WORK_INDEX.md):

> ✅ Done · 🚧 In Progress · 📝 Drafted (WP file authored, not yet started) · 📦 Queued (deps met, WP file not yet authored) · ⏸ Blocked (dep unmet) · 🔮 Placeholder (forward-looking, intentionally not authored)

Status flips are governance commits. A WP that quietly slid from 🚧 to ✅ without a `WORK_INDEX.md` edit is a governance gap — the index is the source of truth, not the doc body.

---

## The four-phase lifecycle

| Phase | Output | Gate |
|---|---|---|
| **1. Drafting** | WP file authored, EC file authored (if WP warrants one), `WORK_INDEX.md` row added | — |
| **2. Pre-flight** | `docs/reference/pre-flight-WP-NNN-YYYY-MM-DD.md` with `READY` or `NOT READY` verdict | [pre-flight.md](pre-flight.md) |
| **3. Execution** | Work performed per WP §Scope; findings landed in cited docs; raw outputs in gitignored paths | WP §Exit criteria |
| **4. Close** | WP status flipped to ✅ Done in `WORK_INDEX.md` in a governance commit | — |

A `NOT READY` pre-flight ends the cycle for that attempt — execution does not open. The pre-flight artifact stays on `main` as the audit record; the next attempt cites it in its Header. This is normal; the 2026-06-02 NOT READY artifact for WP-007 is a clean example.

---

## Phase 1 — Drafting

### Supersession check (REQUIRED before reserving a number)

Before authoring `WP-NNN-<slug>.md`, confirm the work hasn't already happened in a different shape. Three quick checks; each is ~15 seconds:

1. **WORK_INDEX scan.** Read [WORK_INDEX](../work-packets/WORK_INDEX.md) end to end. If the proposed work overlaps an existing WP — even one in a different phase — the right move is usually to extend that WP, not draft a new one. The closed-set status vocabulary makes this scan fast.
2. **Format-doc scan.** Read the relevant `docs/formats/*.md` Findings sections. If the fact the WP would lock is already in Findings (with a SHA-256 lock or hex citation), the WP is redundant.
3. **Git log search.** `git log --oneline --all --grep="<slug>"` — has the work shipped under this slug or a near-match on a different branch? `--all` covers branch tips not merged yet, so an in-flight draft surfaces here too.

If any check returns a match, **stop**. The decision is one of: (a) the work is done — abandon the proposed draft; (b) the work is in flight elsewhere — extend the existing WP instead of drafting a parallel one; (c) the match is a false-positive near-collision — note it in the WP's `## Background` and proceed.

**Why this matters at scooby's scale.** Even with ~10 WPs the cost of accidentally drafting "WP-011: cross-title strings comparison" when WP-007 already covers that under its in-scope cross-title runs is non-zero — the index gets a redundant row, the prose duplicates, and the next reader has to reconcile.

### Number reservation

- **WP number** — scan WORK_INDEX for the highest landed `WP-NNN`. New draft = `WP-(N+1)`. Phase 2-5 placeholders (🔮) don't burn numbers; they're explicitly not-yet-authored.
- **EC number** — only if the WP warrants a companion checklist (rule of thumb: estimated effort > 2 hours, or > 5 sequential steps with time-boxing, or sprawl risk). EC numbers track WPs but aren't strictly paired (EC-004 pairs with WP-008; not all WPs have ECs).
- **Pre-flight artifact filename** — `pre-flight-WP-NNN-YYYY-MM-DD.md` per the [pre-flight gate](pre-flight.md) template. Date is reserved at execution time, not draft time.

**Reservation ownership.** A reserved number is owned by the draft branch (or the unstaged file on a working tree, for in-canonical drafts) until the WP+row commit lands on `main`. If the draft is abandoned before merge, the number returns to the free pool. If the draft is abandoned **after** the WORK_INDEX row lands on `main`, the row must be retracted in a follow-up commit before the number can be re-used — see §Abandonment below.

### Required WP file sections

Mirror the structure existing WPs already use ([WP-003](../work-packets/WP-003-pre-payload-region.md) and [WP-007](../work-packets/WP-007-strings-and-imports.md) are good models). In order:

1. **Front matter** — `layout: default`, `title: "WP-NNN: <short>"`
2. **Header block** — Status emoji, Phase, Depends on, Unblocks (if any), Companion EC (or `—`), Pre-flight required (Yes/No with reason), Targets generation(s), Estimated effort
3. **Goal** — one paragraph, what the WP produces
4. **Background** — what's already known and what gap this WP fills; cite the docs that established the gap
5. **Scope (In scope / Out of scope)** — numbered list of what's in; explicit list of what's out, with each "out" line stating where the work belongs instead
6. **Dependencies** — binaries, tools, prior WPs, mounted ISOs
7. **Execution** (for action WPs) or **Investigation plan** (for research WPs)
8. **Output specification** — for WPs that produce structured findings (the [scooby-exe binary identity table](../formats/scooby-exe.md) pattern, etc.)
9. **Exit criteria** — numbered list, each criterion testable. Any criterion not met = WP stays 🚧
10. **Deliverables** — what gets committed, what stays gitignored
11. **Notes** — hand-offs to other WPs, copyright posture, generation discipline reminders

Front-load generation discipline: every Finding subsection should state which generation (Gen 1 / Gen 2 / Gen 3) it applies to. The 2026-06 engine-lineage finding makes this load-bearing — a claim about "the engine" without a generation tag aged badly in practice.

### Companion EC file (if warranted)

EC structure follows [EC-001](../execution-checklists/EC-001-ghidra-session.md) as a model:

- **Paired WP** + **Purpose** header
- **Pre-flight** checkbox block at the top (cite the pre-flight gate doc)
- **Step N — <name> (time-box: HH:MM)** sections, each with checkbox bullets + Outcome
- **Definition of done** — all step outcomes recorded, paired WP exit criteria satisfied, status updated
- **Out-of-scope captures** — sessions sprawl; record temptations as one-line follow-ups for future WPs and move on

Hard rule: ECs are operational, not decision-making. A clause that says "decide whether X" belongs in the WP body, not the EC. ECs that try to make decisions inline produce the WP-007b-style mid-execution amendment spiral that legendary-arena's reference docs cite as the cautionary precedent.

### WORK_INDEX row + Phase 1 Definition of Done

Add the WP's row in the correct Phase section of [WORK_INDEX](../work-packets/WORK_INDEX.md). Status field carries the appropriate emoji from the closed set above.

**Drafting is done when** every box below is checked:

- [ ] WP file exists at `docs/work-packets/WP-NNN-<slug>.md` and renders cleanly under Jekyll (`.md` links resolve)
- [ ] EC file exists at `docs/execution-checklists/EC-NNN-<slug>.md` if warranted
- [ ] WORK_INDEX row added in the correct Phase section, status = 📝 Drafted (or 📦 Queued if WP body is a one-line placeholder)
- [ ] All §Scope (In) bullets are concrete and testable; no "explore," "understand," or "see what's there" verbs
- [ ] §Exit criteria are numbered, each one binary-checkable
- [ ] §Targets generation(s) is filled in; not left at "TBD"
- [ ] §Pre-flight required is answered Yes/No with reason (Yes if writing to `docs/formats/**` that locks a fact, modifying `engines/scooby/**`, committing tool scripts under `tools/**`, or claiming a generation classification)

If any item is unsatisfied, the draft is incomplete. Don't open pre-flight against a half-drafted WP — pre-flight's verdict isn't load-bearing if the WP itself isn't.

---

## Phase 2 — Pre-flight

Covered fully in [pre-flight.md](pre-flight.md). Two reminders that show up at the lifecycle level:

- **Stale READY.** A `READY` verdict ages out when `main` moves. If the WP's pre-flight passed on commit `abc123` and `main` has advanced (other PRs merged, format-doc Findings landed, binaries re-cached with different SHAs), the READY is no longer load-bearing. Re-run pre-flight on a fresh dated artifact. The 2026-06-02 NOT READY → 0da45e3 binary-cache landing pattern is the textbook example: the binaries are now cached and the next pre-flight can verdict READY, but it has to be a *new* artifact citing the prior one — not a retroactive edit to the NOT READY.
- **NOT READY is a complete outcome.** A NOT READY artifact, signed and committed, ends the cycle for that attempt. It's not a failure; it's the audit record of "we checked, here's why execution didn't open." The next pre-flight cites it in its Header.

---

## Phase 3 — Execution

### Session prompt

Execution opens against a READY pre-flight, but the gate verdict is an audit artifact, not a set of instructions. The session prompt is the imperative-form repackaging — what the next Claude session reads as its first message.

- **Location:** `docs/sessions/session-WP-NNN-YYYY-MM-DD.md` (sibling to `docs/reference/`)
- **Naming mirrors pre-flight artifacts** — same date format, paired files sort adjacent. Suffix `-b` for same-day re-runs.
- **Committed**, not gitignored. Same audit-trail discipline as pre-flight artifacts; future readers can reconstruct what was prompted, not just what was decided. At scooby's scale the noise cost is negligible and the reproducibility value is real.
- **Template:** [session-TEMPLATE.md](../sessions/session-TEMPLATE.md) — seven sections: Header / Intent / Authority chain (read order) / Pre-execution checks / Execution rules / Session task / Close ritual. Cap ~200 lines.
- **Source-of-truth boundary:** the prompt operationalizes the WP+EC+pre-flight; it does NOT extend them. If the executing session needs scope beyond what the prompt encodes, it stops and asks. Silent scope expansion is an anti-pattern (§Anti-patterns below).
- **First worked example:** [session-WP-007-2026-06-02.md](../sessions/session-WP-007-2026-06-02.md) instantiated against [pre-flight-WP-007-2026-06-02-b](pre-flight-WP-007-2026-06-02-b.md). Pattern: pre-flight §Repo + disc state → prompt §Pre-execution checks; pre-flight §Scope lock → prompt §Execution rules (imperative); pre-flight §Risk review top mitigations → prompt §Execution rules ("you MUST...").

The pre-flight artifact stays the audit record of why execution was authorized. The session prompt is the operational tool that drives execution. Both are committed; both are dated; both name the other in their respective Header sections.

### Discipline

- **One WP per branch (or per focused session)**, unless the work is small enough to commit straight to `main` (status bumps, link fixes, format-doc text corrections that don't lock new facts). The pre-flight gate's "Allowed paths" list is the scope contract for the duration of the session.
- **Every claim cites its generation.** This is the single discipline that makes findings durable across the engine-lineage split. A finding stated as "the engine loads `TGIFILE.ART` via `CreateFileA`" should read "Gen 1 (Showdown) loads `TGIFILE.ART` via `CreateFileA`" — the Gen 1 qualifier prevents the claim from getting silently mis-applied to Jinx's MMFW pipeline.
- **Raw extracts stay local.** Per the copyright posture in [tools/exes/README](../../tools/exes/README.md) and [tools/samples/README](../../tools/samples/README.md): full strings dumps, decoded image samples, audio clips, and raw archive payloads live under gitignored paths. Only categorized samples + functional/factual identifiers (filenames, function names, SHA-256s, hex citations of small headers) get promoted into `docs/`.
- **Regenerable diagnostic outputs also stay local.** Catalog JSON, name-table dumps, cross-check unmatched-asset lists, and similar tool outputs (`tools/samples/asset-catalog.json`, `tools/samples/wp003-name-table.txt`, `tools/samples/unmatched-assets.txt`) are reproducible from SHA-256-locked source binaries via the tooling under `tools/`; committing them adds noise and drifts from the canonical regeneration. The WP body cites the regeneration command (or names the script that produces the file) so a future reader can rebuild on demand. Findings derived from the file get promoted into `docs/` — the file itself does not.

### Commit hygiene

scooby's commit style is short imperative subject lines with conventional prefixes. The prefixes that have organic precedent in the log:

| Prefix | Used for |
|---|---|
| `docs:` | Documentation changes — most scooby commits. Format-doc Findings, WP body edits, status flips, link fixes |
| `fix:` | Bug fixes in tooling or doc structure (e.g., the `.md` extension sweep) |
| (none) | Pre-prefix commits exist in early history; new commits should pick a prefix |

Title under ~80 chars, body explains the **why** in 1–4 sentences. Co-Author footer for AI-paired commits:

```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

### Two-commit topology for code WPs

When an executing WP both produces code/format-doc changes **and** flips its WORK_INDEX status, split into two commits on the branch:

```
<commit A>  docs: <implementation work>          ← the actual deliverable
<commit B>  docs: close WP-NNN — flip to ✅ Done ← status flip + index hygiene
```

Why split: a single combined commit conflates two different review activities. Reviewing the implementation is "is this finding correct?"; reviewing the close is "did the index row update match the WP's exit criteria, and is the status flip warranted?" The two-commit topology keeps per-commit auditability.

A squash-merge at PR-merge time is fine — the constraint is on the branch state during review, not on `main`'s history afterward.

For docs-only WPs that don't have a meaningful "implementation" step (the [scooby-exe](../formats/scooby-exe.md) Findings sections, the [tools/exes/README](../../tools/exes/README.md) inventories), one commit with both the work and the close is fine — there's no auditable surface to separate.

### Execution Definition of Done

A WP is ready to close when:

- [ ] Every §Exit criterion in the WP body is met, with evidence cited
- [ ] All Findings land in the docs the WP §Deliverables names; nothing important sits in a working tree
- [ ] Raw outputs that shouldn't be committed are confirmed local-only (`git diff --cached --name-only` shows no `tools/exes/**` or `tools/samples/**` content files)
- [ ] WORK_INDEX row updated to ✅ Done in the close commit
- [ ] Downstream WPs that this one unblocks have their `Depends on:` cell on this WP marked Done

---

## Phase 4 — Close

The close commit (`docs: close WP-NNN — flip to ✅ Done`, or folded into the work commit for docs-only WPs) does three things:

1. **Flip the WORK_INDEX row** to ✅ Done. Update the Status column; if the table tracks Date, fill it.
2. **Propagate to dependent rows.** WPs whose `Depends on:` cell named this WP should have that cell visibly updated (the table style varies — sometimes a status icon next to the prereq, sometimes a commit-hash citation, sometimes just removing the strikethrough).
3. **Note the next unblocked WP** in WORK_INDEX's "Current state" section if the close shifts the project's next-step calculus.

The pre-flight artifact stays on `main` permanently. It's the audit record of why execution was authorized; future readers reconstruct authorization from it without re-reading transcripts.

---

## End-to-end operator workflow

Phases 1–4 above describe the discrete artifacts a WP produces. This section strings them together into the actual loop a session runs from "next WP picked off the queue" to "close commit lands on main."

The loop has off-ramps (NOT READY pre-flight → §Abandonment if the blocker doesn't clear) and conditionals (no EC for small WPs, no fork-sync for docs-only WPs, no PR for trivial fixes). Walk the path that fits the work; skipping a step is fine if the rationale is explicit. The order is the order — moving steps around generally means moving review surfaces around, which is what the order is protecting.

### 0. Triage (10 seconds)

- **Trivial fix** — link rot, typo, status flip, docs hygiene that locks no fact: edit + `git commit` + `git push origin main` directly. No branch, no pre-flight, no session prompt, no PR. The "one WP per branch" rule has an explicit carve-out for this; see §Phase 3 Discipline. Forgetting the push is the failure mode here — GitHub Pages builds from `origin/main`, so an unpushed direct-to-main commit looks "done" locally but isn't visible to anyone.
- **Substantive docs-only WP** — fact-locking work that produces no `engines/scooby/**` change. The committed surface is docs (`docs/formats/**`, `docs/work-packets/**`, `docs/reference/**`, `docs/sessions/**`) plus optionally small tool scripts under `tools/*.py` whose outputs are gitignored. Full loop *except* steps 5 (branch), 10 (PR), 11 (squash-merge). Commits go direct to `main` per the two-commit topology, with `git push origin main` after each (or batched at close — but never silently). Pre-flight + session prompt + scope-lock allowlist provide the discipline that branch + PR would otherwise add. WP-007 (four binaries' worth of strings/imports findings + two extraction scripts) and WP-003 (`tgifile-art.md` Findings expansion + spec correction) are this path's precedents.
- **Substantive code WP** — touches `engines/scooby/**`, or commits non-trivial code that benefits from PR-surface review (cumulative architecture changes, binary file additions, > ~100 LOC of new tool code). Full loop including branch + PR + squash-merge.
- **Scope check:** does the WP touch `engines/scooby/**`? If yes, step 1 fires against the scummvm fork. If no (docs-repo-only WP), step 1 is a no-op.

### 1. Sync (conditional)

For WPs touching `engines/scooby/**`: run [`tools/Sync-Fork.ps1`](../../tools/Sync-Fork.ps1) against the scummvm fork to bring local `main` level with `scummvm/scummvm` and rebase the feature branch on top.

For scooby-docs-repo-only WPs (every Phase 0–1 WP to date): `git switch main && git pull --ff-only origin main` against this repo. There is no upstream fork; the script does not apply.

### 2. Draft WP

Per §Phase 1 — Drafting. The supersession check is non-optional — three 15-second checks (WORK_INDEX scan, format-doc scan, `git log --oneline --all --grep=<slug>`); a hit means stop and extend the existing WP rather than draft a parallel one. Reserve the WP number, write `docs/work-packets/WP-NNN-<slug>.md`, add the row to [WORK_INDEX](../work-packets/WORK_INDEX.md) at 📝 Drafted.

### 3. Draft EC (conditional)

Per §Phase 1 — Drafting. Only when estimated effort > 2 hours, > 5 sequential steps with time-boxing, or sprawl risk. ECs are operational, not decision-making — a "decide whether X" clause belongs in the WP body, not the EC.

### 4. Review + revise (one activity, possibly multiple passes)

Self-review first — read the WP + EC end-to-end with fresh eyes against [01-VISION](../01-VISION.md) and [02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md) for alignment, and against [WORK_INDEX](../work-packets/WORK_INDEX.md) for phase fit.

For substantive WPs, spawn an Agent (subagent_type `code-reviewer`) for an independent pass. The agent reads the WP + EC + the authority docs cold and flags inconsistencies the author can't easily see. Apply findings inline; iterate until the WP + EC are internally consistent and don't conflict with the authority docs.

This is one activity, not two ("review" + "apply suggestions"). Real review is iterative.

### 5. Branch (conditional — substantive code WPs only)

`git switch -c wp-NNN-<slug>`. From here, everything lands on the branch, not on `main`. The §Phase 3 "one WP per branch" rule activates here.

**Skip for substantive docs-only WPs** — they commit direct to `main` per the triage path; the §Phase 3 Discipline allowlist + the pre-flight scope-lock + the two-commit topology provide the discipline the branch would otherwise add. Skip for trivial fixes that triage already routed past.

### 6. Pre-flight

Copy [docs/reference/pre-flight.md](pre-flight.md) → `docs/reference/pre-flight-WP-NNN-YYYY-MM-DD.md` (suffix `-b`, `-c`, etc. for same-day re-runs). Fill in every section; verdict at the bottom.

**Off-ramp — NOT READY:** sign and commit the artifact (it stays on `main` as the audit record). Update the WP's WORK_INDEX row to ⏸ Blocked or note the next action in the artifact's §Path to resolution. Workflow ends here for this attempt; the next attempt cites the NOT READY in its Header per §Phase 2.

### 7. Session prompt

Copy [docs/sessions/session-TEMPLATE.md](../sessions/session-TEMPLATE.md) → `docs/sessions/session-WP-NNN-YYYY-MM-DD.md`. Operationalize the pre-flight per §Phase 3 — Session prompt: Repo + disc state → Pre-execution checks; Scope lock → Execution rules; Risk review top mitigations → "you MUST..." rules. Commit pre-flight + session prompt together — one commit on the branch for substantive-code WPs, one commit on `main` (then push) for substantive-docs-only WPs.

### 8. Execute

Pass the session prompt as the first message to a fresh Claude Code session (or run inline in the current one). Commits happen *during* execution per the §Two-commit topology — they are not a separate later step. The session enforces the scope-lock allowlist by running `git diff --cached --name-only` against the allowlist before each commit.

### 9. Close inside the session (still on the working branch — branch for code WPs, `main` for docs-only WPs)

Before opening the PR (substantive code WPs) or pushing the close commit (substantive docs-only WPs), the executing session updates three places — this is §Phase 4 — Close work, executed inside the session that did the implementation:

- **WP-NNN body**: Status → ✅ Done, actual effort recorded, "Findings landed in" links added
- **WORK_INDEX**: row → ✅ Done; downstream `Depends on:` cells annotated ✅; §Current state updated if the project's next-step calculus shifted
- **Pre-flight artifact**: §Lessons learned filled in (one line, or "No lessons learned" explicitly — leaving it blank is a governance gap)

Splitting close into a separate session adds round-trips without separating any review surface; the implementation session has the most context for the close.

### 10. PR (substantive code WPs only)

`gh pr create` from the branch into `main`. Self-review the PR diff in GitHub's UI — it surfaces things the working tree doesn't (large diffs read differently when laid out as a single page; binary file additions are flagged explicitly; the cumulative shape of the change is visible at once instead of file-by-file).

**Skip for substantive docs-only WPs** — the close commit went direct to `main` in step 9; `git push origin main` after that close commit is what step 11 collapses into. Skip for trivial fixes that triage routed past — direct-to-main is fine for the cases the §Phase 3 Discipline carve-out lists.

### 11. Squash-merge + branch cleanup (substantive code WPs only)

`gh pr merge --squash --delete-branch` does merge + push to `main` + delete remote and local branch in one command. Separate "approve", "squash-merge", "push to main", "delete branch" steps describe the same git operation; collapsing them keeps the workflow honest about what's happening.

For solo operation, approval is a self-approval — the discipline is in re-reading the PR diff (step 10), not in the social ritual of clicking Approve.

**For substantive docs-only WPs:** `git push origin main` is the equivalent collapsed step — push every direct-to-main commit produced in steps 7–9 (pre-flight + session prompt + Commit A + Commit B). Failing to push leaves the close trapped locally; GitHub Pages builds from `origin/main`, so an unpushed close looks "done" locally but isn't visible. (This is the same failure mode the trivial-fix path warns about in step 0.)

### 12. Next-WP handoff (usually nothing)

Most cases: no action. §Current state in WORK_INDEX was updated in step 9 and that's the handoff surface; the next session reads it and knows where to start.

Exception: if execution surfaced something the next WP genuinely needs that doesn't fit WORK_INDEX prose — a non-obvious anomaly, a follow-up candidate worth scoping — add it as a one-line heads-up in the next WP's §Background, or spawn a follow-up task via `mcp__ccd_session__spawn_task`. Do **not** write a separate "session context" doc — it duplicates lessons-learned + WORK_INDEX prose and drifts independently from both.

### 13. Tidy (named, not vague)

- `git status --short` after merge — confirms raw extracts under `tools/exes/**` and `tools/samples/**` are still gitignored (zero files staged), and no session-local detritus is left in the working tree
- Drop any session-local stashes (`git stash list` → `git stash drop`) or branches that didn't get cleaned up by `--delete-branch`

That's the scope. Directory-casing normalization, archived logs, cache pruning, etc. are session-level concerns — they ride along inside step 8 if needed, not in workflow-level tidy.

### Off-ramps the loop can take

| Off-ramp | Triggered by | Lands at |
|---|---|---|
| **Triage skip-to-main** | Step 0 — trivial fix, no fact-locking | Direct commit on `main` + `git push origin main`, no branch, no PR |
| **NOT READY** | Step 6 — pre-flight verdicts NOT READY | NOT READY artifact committed; WORK_INDEX row → ⏸ Blocked or next-action noted; workflow ends |
| **Supersession** | Step 2 — supersession check finds the work has shipped or is in flight | Stop drafting; extend the existing WP or close the loop with no new WP |
| **Abandonment** | Any step after the WP+row landed on `main`, where execution stops being viable | §Abandonment ritual below — retraction commit if the WP row is on `main` |

The off-ramps are first-class — taking one is a complete and valid outcome, not a failure. The audit trail (NOT READY artifact, retraction commit, supersession note in WP §Background) is what makes the loop's history reconstructable.

---

## Abandonment

Drafting and execution get interrupted for many reasons — a higher-priority finding lands first, the WP's premise dissolves under inspection, the operator's attention shifts to a different generation. The four states below cover cleanup per state, in ascending order of "how far did this go before abandoning."

### (a) Pre-commit abandonment

WP file exists on disk; nothing committed.

Ritual:
1. `git status` — confirm there's nothing to preserve elsewhere.
2. `git clean -fdn docs/work-packets/` to preview; then `git clean -fd docs/work-packets/` if clean.
3. `git checkout HEAD -- docs/work-packets/WORK_INDEX.md` if the row was already added to the working tree.

The reserved WP/EC numbers return to the free pool automatically — they were never on `main`.

### (b) Committed locally, not pushed

Local commit on a branch; no PR.

Ritual:
1. `git branch -vv` — confirm no upstream tracking.
2. Return to `main`. `git branch -D <branch>` (capital D required; branch isn't merged anywhere).

Same number-reservation rule: nothing on `main`, nothing to retract.

### (c) Pushed; no PR

Branch exists on `origin`.

Ritual:
1. `git push origin --delete <branch>`.
2. Return to `main`. `git branch -D <branch>`.

### (d) PR opened

PR exists, even if not merged.

Ritual:
1. Close the PR with an explanatory comment via `gh pr close <number> --comment "Abandoned: <reason>"`. The comment is **required** — a future reader needs the reason. Common shapes: "Superseded by WP-NNN", "Scope dissolved under inspection", "Work shipped via different commit on main".
2. Apply state (c)'s ritual.

### Retraction commit (REQUIRED if WORK_INDEX row landed on `main`)

Any abandonment that occurs **after** a commit landed the WP row on `main` (typical when the drafting was a clean commit and the abandonment is during execution) needs a retraction:

```
docs: retract WP-NNN — <one-line reason>
```

The retraction commit removes the WORK_INDEX row, removes the WP body file (if it's a stub), removes the EC file (if it exists), and updates any "Depends on: WP-NNN" cells in downstream WPs to drop the dependency.

Without retraction, the WP number is "burnt" — the row sits on `main` but the implementation never lands, and the number can't be re-used without future readers being confused about what WP-NNN was supposed to be.

---

## Anti-patterns

These are the failure modes worth naming so they have something to fail against.

- **Skipping pre-flight to save time.** Pre-flight is ~15–30 minutes; the rewrite a failed pre-flight catches is hours-to-days. Every WP that touches `docs/formats/**` or commits tool scripts should pre-flight. The only WPs that skip pre-flight are link-fixes and text corrections that don't lock new facts.
- **Skipping the supersession check.** Drafting "WP-NNN: cross-title strings comparison" when WP-007 already covers that under cross-title runs costs an index row, redundant prose, and a reconciliation cost for the next reader. 30 seconds of grep upstream is the cheap version.
- **Generation conflation.** Stating "the engine does X" when X is Gen 1-only or Gen 2-only is the single biggest source of finding-rot post-2026-06. Every finding cites its generation; cross-generation claims explicitly span (or explicitly stay scoped to one).
- **Combining implementation + status flip in one code-WP commit.** The status flip is part of Definition of Done but the review surface is different. Separating them keeps per-commit auditability. The exception is docs-only WPs where there's no meaningful "implementation" review separate from the close.
- **Bundling hygiene into unrelated feature commits.** The user-level CLAUDE.md guidance applies in WP context too — papercut fixes ride along on their own branch + commit, not folded into a Findings landing.
- **Letting NOT READY pre-flights linger.** A NOT READY pre-flight artifact is a complete outcome **only** if there's a clear next-action recorded in §Path to resolution. A NOT READY with no follow-up is governance debt — the WP sits 🚧 forever and future readers can't tell whether it's still active. If the path forward is "wait for an external thing," update WORK_INDEX to ⏸ Blocked with the reason.
- **Treating raw extracts as committable.** Strings dumps, decoded image samples, and raw archive payloads sit in gitignored paths for copyright reasons (see [tools/exes/README](../../tools/exes/README.md) and [tools/samples/README](../../tools/samples/README.md)). The discipline isn't optional even for "just one example" cases.
- **Premature WP authoring.** WORK_INDEX's Phase 2–5 sections are deliberately one-line placeholders. Authoring full WP bodies before Phase 1 closes produces churn — the WP body assumes facts that haven't been established and ages badly. The rule from WORK_INDEX is right: "Promote Phase 2-5 entries to authored WPs as Phase 1 closes — not before."
- **Stale-state resumes.** If a draft sat untouched for more than a few days, re-run the supersession check before continuing. The slug may have shipped via a different commit; the format doc the WP would update may already carry the finding the WP was supposed to land. Resuming a stale draft and merging it produces redundant artifacts at PR-open time.

---

## Empirical precedents

Small project, small history — but the patterns are already on the ledger:

- **WP-007 2026-06-02 NOT READY → 0da45e3 binary cache → next pre-flight READY.** The textbook "pre-flight verdict ages with main" pattern. NOT READY artifact committed, binaries cached over the next session with SHA-256s landing in [tools/exes/README](../../tools/exes/README.md), and the next pre-flight will cite the NOT READY in its Header and verdict READY against the cached state. No retroactive edits to the NOT READY artifact; it stays as the audit record.
- **WP-005 engine-family check → engine-lineage finding 2026-06.** WP-005 started as "is this the same engine across Case File titles" and produced a finding (three generations, code-level TerraGlyph→IBS inheritance) load-bearing enough to revise the entire WORK_INDEX Phase 5 scope rule. The WP body stayed scoped, the finding propagated into [01-VISION](../01-VISION.md), and the cross-title runtime-dependencies table moved from "predicted" to "verified" across multiple subsequent WPs. Pattern: WPs whose findings have downstream impact need explicit propagation into the vision-level docs, not just the format-doc Findings.
- **Directory-casing normalization (2026-06-02 single sweep).** Mixed-case cache directories (`Showdown/`, `Phantom/`, `Case File 1/`) drifted in across multiple disc-caching sessions; the cleanup was deferred to a single `Rename-Item` sweep at the end rather than fixed mid-flight. Pattern: small drift accumulated under attention pressure is fine if the normalization plan is explicit — bad if it's "I'll deal with it later" without a recorded plan.

---

## Cross-references

- [pre-flight.md](pre-flight.md) — the readiness gate this doc sits around
- [docs/sessions/session-TEMPLATE.md](../sessions/session-TEMPLATE.md) — fill-in template for the §Session prompt subsection above
- [WORK_INDEX](../work-packets/WORK_INDEX.md) — status vocabulary + phase ordering + the index this doc's status flips update
- [01-VISION](../01-VISION.md) — vision-level authority; finding propagation target
- [02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md) — upstream contract; engine-code WPs cite this
- [tools/exes/README](../../tools/exes/README.md) — cache-state ledger; binary identity source for pre-flights
- [tools/samples/README](../../tools/samples/README.md) — copyright posture for derived artifacts

---

## Authority

This doc INDEXES the lifecycle around the existing pre-flight gate. It does not override the gate or any higher-authority doc; if a step here disagrees with [pre-flight.md](pre-flight.md), [01-VISION](../01-VISION.md), or [02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md), the higher-authority doc wins.

This doc does NOT carry veto authority over WP execution. It's a navigation aid. If a step blocks legitimate progress, route around it and note the bypass in the WP body or the pre-flight artifact's "Lessons learned" tail. Stuck gates are bugs; surface them in WP §Notes so the next operator can correct the doc.
