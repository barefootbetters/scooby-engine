---
layout: default
title: "Pre-Flight Gate — Scooby Engine WP"
---

# Pre-Flight Gate

> **REFERENCE — Reusable readiness gate. Not an execution prompt.**
>
> **Subordination (descending authority):**
> 1. [docs/01-VISION](../01-VISION.md) — vision, goals, scope, decisions log
> 2. [docs/02-SCUMMVM-INTEGRATION](../02-SCUMMVM-INTEGRATION.md) — upstream integration contract
> 3. [docs/work-packets/WORK_INDEX](../work-packets/WORK_INDEX.md) — WP + EC catalog and ordering
>
> If this doc conflicts with any of the above, the higher-authority doc wins.

---

## Purpose

A binary readiness gate that runs **before** a WP execution session is opened. It exists to:

- Confirm prerequisites: every WP this one depends on is `✅ Done` per `WORK_INDEX`
- Lock scope: explicit allowed paths; anything not listed is forbidden
- Surface risk before the Ghidra session, decoder pass, or scaffold edit begins
- Produce a binary **READY** / **NOT READY** verdict

Pre-flight is an audit artifact — fill it in and commit it so a future reader can reconstruct why execution was authorized without re-reading transcripts.

Pre-flight sits inside the broader WP lifecycle. See [wp-lifecycle](wp-lifecycle.md) for the drafting steps that precede this gate and the execution + close steps that follow — including the "stale READY when main moves" pattern and the four-state abandonment ritual.

**Save the filled-in copy as:** `docs/reference/pre-flight-WP-XXX-YYYY-MM-DD.md`
(where `XXX` is the WP number and `YYYY-MM-DD` is today's date). Commit it to `main` before opening the execution session.

---

## When pre-flight is required

**Mandatory** for any WP that touches:

- ScummVM engine source (`engines/scooby/**` once WP-010 lands)
- Format documentation under `docs/formats/**` that locks a fact
- Tool scripts under `tools/**` that produce committed artifacts
- A Ghidra session whose `.gpr` will be re-used by a later WP
- A claim that locks or changes an engine-generation classification (Gen 1 / Gen 2 / Gen 3 per the 2026-06 engine-lineage finding)

**Not required** for WP/EC body edits that don't lock a new fact (rewordings, link fixes, status bumps), typo/link/formatting edits to `docs/**`, or screenshot/reference-image captures.

---

## Template

Replace `WP-XXX` with the actual WP ID. Every section must carry concrete content; placeholder responses ("N/A", "TBD", "none") invalidate the pre-flight.

### Header

- **WP:** `WP-XXX`
- **Title:** `<short>`
- **Pre-flight date:** `<YYYY-MM-DD>`
- **Targets generation(s):** Gen 1 / Gen 2 / Gen 3 / N-A (per [vision §Engine Lineage](../01-VISION.md#engine-lineage-2026-06-finding))
- **Targets disc(s):** Showdown / Phantom / Jinx / Case File #1 / Case File #2 / Case File #3 / N-A

### Pre-flight intent

> Validating readiness for `WP-XXX`. Not implementing, not editing engine code, not annotating Ghidra. Verdict only.

### Dependency check

Confirm every prereq WP listed in `WORK_INDEX` for `WP-XXX` is `✅ Done`. Read the index directly — do not trust memory.

| Prereq | Status in `WORK_INDEX` | Locked on | Notes |
|---|---|---|---|
| WP-AAA | ✅ Done | YYYY-MM-DD | |

**Rule:** any prereq not `✅ Done` → **NOT READY**. Phase ordering is load-bearing; do not start a Phase 2 WP while Phase 1 exit criteria are open.

### Repo + disc state

- [ ] Working tree clean (`git status --short` empty), HEAD on a named branch or `main`
- [ ] Disc-on-hand for each target title is mounted / extracted to a known path; paths recorded below
- [ ] If the WP re-uses a Ghidra `.gpr`: the file exists, the analysis state matches what the WP body assumes, and the file is not open in another Ghidra instance
- [ ] If the WP re-uses prior tool output (e.g., a committed extract under `tools/samples/`): the input hash matches what the WP assumes
- [ ] **If the WP updates an existing `docs/formats/**.md`:** cross-check at least one non-trivial offset cited in the target doc against the actual binary, before the verdict. SHA-256 match confirms binary identity but does **not** catch spec drift (existing doc has wrong offset, future findings silently inherit the error). Decode one cited field (e.g. `uint32LE` count at offset X) and compare against the doc's claimed value. WP-003 closed against `tgifile-art.md` whose `asset_count` offset was off by +4 bytes — caught mid-session by the session prompt's step-1 sanity check, but cheaper to catch at the gate. See [pre-flight-WP-003-2026-06-02 §Lessons learned](pre-flight-WP-003-2026-06-02.md#after-execution--lessons-learned).

ISO / extract paths in use:

```
<title>: <absolute path>
```

### Scope lock

Anything not explicitly allowed is forbidden.

**Allowed paths for `WP-XXX`:**

```
<glob>
<glob>
```

**Forbidden (any change fails the WP):**

- Game data (any binary from the discs) — copyright; **never commit**
- `engines/scooby/**` if this WP is not an engine-code WP
- `docs/formats/**` if this WP is not a format-decode WP
- ScummVM upstream paths outside `engines/scooby/` (`base/`, `engines/scumm/`, etc.) — out of scope; upstream contributions are their own WP

**Exit check (must run before staging a commit):**

```pwsh
# On a feature branch (ScummVM fork, engines/scooby work):
git diff --name-only origin/main..HEAD

# Committing directly to main (docs repo — WP status bumps, format-doc findings):
git diff --cached --name-only
```

Any file in the output that doesn't match the allowed list = scope violation. Remediate with `git restore`, not by widening the allowlist post-hoc.

### Risk review

At least one entry required — "none identified" is not acceptable on a mandatory-pre-flight WP.

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| \<risk\> | low/med/high | low/med/high | \<step or guardrail\> |

Common shapes for scooby WPs:

- **Disc mismatch** — WP cites Showdown evidence but Ghidra session is loaded against Phantom. Mitigation: record exact ISO SHA-256 in §Repo + disc state.
- **Generation conflation** — finding stated as "the engine does X" when X is Gen 2-only. Mitigation: every claim cites the generation it applies to per the 2026-06 lineage finding.
- **Inference vs evidence** — format-doc clause written from analogy ("looks like a standard MMFW header") without byte-citation. Mitigation: every spec clause cites a disc offset + hex window.
- **Ghidra session drift** — re-using a `.gpr` whose annotations have been overwritten since the WP body was drafted. Mitigation: WP body cites the `.gpr` SHA-256 or export-commit SHA.
- **Tool output non-determinism** — a script that depends on dict iteration order, a timestamp, or environment state. Mitigation: run the script twice, compare output hashes, before committing the artifact.
- **Copyright leak** — any disc-extracted binary, screenshot, or audio sample staged for commit. Mitigation: review `git diff --cached --name-only` against the §Scope lock allowlist; nothing under `tools/extracts/` or similar ever commits.
- **ScummVM upstream creep** — the WP "needs one small change" to a core ScummVM file outside `engines/scooby/`. Mitigation: stop; that's its own WP with its own upstream-contribution exit criteria.

### Verdict

- [ ] **READY TO EXECUTE** — every section above carries concrete content; all blockers resolved
- [ ] **NOT READY** — written reason + path to resolution; pre-flight cannot be re-run until cleared

Reviewer: `<name>`
Date: `<YYYY-MM-DD>`

A `READY` verdict authorizes opening the execution session. It does not authorize any code change beyond the §Scope lock allowlist.

A `NOT READY` verdict is itself the audit artifact — keep the saved copy; the next pre-flight cites it.

---

## After execution — lessons learned

If the WP surfaced a preventable gap pre-flight should have caught, record one line in the saved `pre-flight-WP-XXX-YYYY-MM-DD.md` under a "Lessons learned" heading. If the gap is structural (i.e., it would recur on future WPs), amend this template too.

A WP that closes with "No lessons learned" is a complete and valid outcome — write it explicitly rather than leaving the section blank.
