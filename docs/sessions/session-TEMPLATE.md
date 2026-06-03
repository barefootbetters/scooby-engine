---
layout: default
title: "Session Prompt Template"
---

# Session Prompt — TEMPLATE

> **REFERENCE — Fill-in template. Save instantiated copies as `session-WP-NNN-YYYY-MM-DD.md` in this directory.**
>
> The session prompt is the imperative-form repackaging of a `READY` pre-flight artifact. It's the file you paste as the first message to the next Claude session to drive execution of `WP-NNN`. Cap at ~200 lines — if it grows beyond, the WP+EC isn't pulling its weight.
>
> See [docs/reference/wp-lifecycle](../reference/wp-lifecycle.md) §Session prompt for the convention this template instantiates.

Replace `WP-NNN`, `<slug>`, `<date>`, and every `<...>` placeholder with concrete content. The same "no placeholders" rule that applies to pre-flight artifacts applies here — `TBD`, `N/A`, or `none` invalidate the prompt.

---

## Header

- **WP:** `WP-NNN`
- **Title:** `<short>`
- **Session date:** `<YYYY-MM-DD>`
- **Paired pre-flight:** `docs/reference/pre-flight-WP-NNN-<date>.md` — verdict `READY`, signed against commit `<sha>`
- **Targets generation(s):** Gen 1 / Gen 2 / Gen 3 / N-A (per [vision §Engine Lineage](../01-VISION.md#engine-lineage-2026-06-finding))
- **Targets disc(s):** Showdown / Phantom / Jinx / Case File #1 / Case File #2 / Case File #3 / N-A

## Intent

> One paragraph: what this session accomplishes. Phrase as a deliverable, not a verb. State explicitly what is OUT of scope so the executing session doesn't sprawl.

## Authority chain (read order)

Read these files top-to-bottom before doing any work:

1. `C:\Users\jjensen\.claude\CLAUDE.md` — operator preferences
2. [docs/01-VISION](../01-VISION.md) — vision, goals, scope rules
3. [docs/02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md) — upstream contract (only if the WP touches `engines/scooby/**`)
4. [docs/reference/wp-lifecycle](../reference/wp-lifecycle.md) — drafting / pre-flight / execution / close framework
5. **Paired pre-flight artifact:** `docs/reference/pre-flight-WP-NNN-<date>.md` — scope lock + risk profile
6. **WP body:** `docs/work-packets/WP-NNN-<slug>.md` — exit criteria + output spec
7. **EC body** (if applicable): `docs/execution-checklists/EC-NNN-<slug>.md` — step-by-step checklist
8. **Cited source files** — list every format doc, source binary, cached artifact, or reference image the WP names. Include paths.

## Pre-execution checks

Confirm each before touching files:

- [ ] Working tree clean (`git status --short` empty)
- [ ] HEAD on `main` at or after commit `<sha>` (the pre-flight's signed-against commit). If `main` has moved with substantive changes, STOP and re-run pre-flight per [wp-lifecycle](../reference/wp-lifecycle.md) §Stale READY.
- [ ] Paired pre-flight artifact exists on `main` with verdict `READY`
- [ ] **Binary SHA-256s match the Binary identity table** in the pre-flight artifact:
  - `<title>`: expected `<sha256>`, actual `<verify>` (`Get-FileHash <path> -Algorithm SHA256`)
  - (repeat per binary the WP runs against)
- [ ] Required tools available: `<list — e.g., Python 3.x with pefile, Ghidra X.Y, dumpbin>`
- [ ] Mounted ISOs (if WP re-mounts): `<title>: <expected drive letter or path>`

If any check fails: STOP. Surface the failure; do not proceed with mismatched state.

## Execution rules

**Scope allowlist** (verbatim from pre-flight §Scope lock — any change to files outside this list is a scope violation):

```
<glob>
<glob>
```

**Allowed but local-only** (gitignored; never staged):

```
<glob — e.g., tools/exes/<title>/*>
```

**Forbidden:**

- Game data binaries committed to git (`*.exe`, `*.eng`, `*.dat`, `*.iso`, `*.ART`, `*.MMF`, `*.MMA`, `*.MMP`, `*.MMS`) — copyright; safety-net in `.gitignore`
- `engines/scooby/**` — out of scope unless this is an engine-code WP
- `docs/formats/` files other than those named in the pre-flight §Scope lock
- Any path outside the allowlist above

**Generation discipline (REQUIRED):** every Finding cites the generation it applies to. A claim about "the engine" without a Gen 1/2/3 tag is incomplete. Cross-generation claims explicitly span (e.g., "Gen 1 and Gen 2 both use `CreateFileA`; Gen 3 status TBD").

**Copyright posture:** raw extracts (full strings dumps, decoded image samples, archive payloads) stay under gitignored paths per [tools/exes/README](../../tools/exes/README.md) and [tools/samples/README](../../tools/samples/README.md). Only categorized samples + functional/factual identifiers (filenames, function names, SHA-256s, hex citations of small headers) reach `docs/`.

**Commit conventions:**

- Subject lines under ~80 chars, imperative voice, `docs:` / `fix:` prefix
- Body explains the **why** in 1–4 sentences
- Two-commit topology for code WPs: implementation commit + governance-close commit (`docs: close WP-NNN — flip to ✅ Done`). One-commit fine for docs-only WPs.
- Co-Author footer for AI-paired commits:
  ```
  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
  ```

**Top risks (verbatim from pre-flight §Risk review — re-stated as imperative):**

- `<risk → mitigation as instruction>`
- `<risk → mitigation as instruction>`

## Session task

> The actual work statement. Cite WP-NNN §Execution or §Investigation plan step numbers. State outputs concretely: which files get written, which docs get Findings landed, which structured tables get populated.

Outputs this session MUST produce:

1. `<finding 1 — concrete, testable>`
2. `<finding 2 — concrete, testable>`
3. `<...>`

Outputs this session MUST NOT produce (sprawl guard):

- `<temptation 1 — log as follow-up WP candidate, don't pursue>`
- `<temptation 2>`

## Close ritual

When all §Exit criteria from the WP body are satisfied:

1. **Confirm outputs landed.** Every file in the §Scope lock allowlist either has the expected change or has a deliberate reason for not changing (recorded in WP §Notes).
2. **Confirm raw extracts gitignored.** `git diff --cached --name-only` shows no `tools/exes/**` or `tools/samples/**` content files.
3. **Flip WORK_INDEX status** to ✅ Done in the close commit. Update the Status column; fill Done date if the table tracks it.
4. **Propagate to dependent WPs.** WPs whose `Depends on:` cell named this WP should have that cell visibly updated.
5. **Note the next unblocked WP** in [WORK_INDEX](../work-packets/WORK_INDEX.md) Current state section if the close shifts what's next.
6. **Commit, push, open PR** (if working on a branch). Title matches the close-commit subject. Description references the WP, the EC (if any), and the paired pre-flight artifact.
7. **Report back to operator.** State: outputs landed, exit criteria satisfied, status flipped, PR open (if applicable). Surface any anomalies that came up during execution but didn't fit existing WP/EC scope — these become follow-up WP candidates.

If any §Exit criterion was NOT met: the WP stays 🚧 In Progress. Do not flip to ✅. Document what's open in the WP §Notes and report back honestly.

---

## After the session — operator review

The session prompt is a fixed artifact once the session opens. If the executing session surfaces a need that wasn't in the prompt (new file to touch, new finding type to record), the executing session SHOULD:

1. **Stop the current sub-task.**
2. **Report what it needs and why.**
3. **Wait for operator confirmation** before extending scope.

Silent scope expansion is the failure mode this discipline guards against — see [wp-lifecycle](../reference/wp-lifecycle.md) §Anti-patterns.

If the executing session legitimately needs scope changes, the operator updates the WP body, re-runs pre-flight, and regenerates the session prompt. The old prompt stays on `main` as the audit record of the original intent.
