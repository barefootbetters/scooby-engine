---
layout: default
title: "Session Prompt — WP-085's four decisions"
---

# Session Prompt — WP-085 decision session (D1–D4)

> **Decision session, not execution.** No pre-flight; nothing is built. This
> session puts WP-085's four open decisions to Jeff with the evidence already
> gathered, records his answers, and updates the docs to match. Pre-flight and
> implementation come after, in their own sessions. Paste this as the first
> message to a fresh session. Keep it leashed: no spawned sessions, and verify
> every factual claim before writing it (the 2026-11-21 fabrication incident in
> [DECISIONS](../ai/DECISIONS.md) is why).

## Header

- **WP:** [WP-085](../work-packets/WP-085-tv-app-pipeline.md), Google TV app
  pipeline (library, import, test packages, updates). Companion
  [EC-008](../execution-checklists/EC-008-tv-app-pipeline.md).
- **Prompt written:** 2026-11-26. **Session date:** fill in when run.
- **Paired pre-flight:** none; this session comes before it.
- **Targets generation(s):** N-A (no engine code).
- **Repos:** `barefootbetters/terraglyph-engine` (public; local checkout
  `C:\dev\scooby-engine`) and `barefootbetters/scooby-engine-private` (private;
  `C:\dev\scooby-engine-private`). Both checkouts are shared with other
  sessions: work in worktrees under `C:\claude-worktrees\`, stage explicit paths.

## Intent

Get Jeff's answers to WP-085's D1–D4 and record them: in WP-085's decision
table, in a DECISIONS entry for the public parts, and on the private strategy
page for the app identity. If an answer changes WP-085's scope (most likely
D2), update WP-085 and EC-008 to match and say so plainly.

**Out of scope:** building anything; pre-flight; creating a Google Play
account, GitHub repo, release, R2 bucket or any other external resource;
uploading game data; contacting Revolution or anyone else; editing the fork.

## Authority chain (read first)

1. `C:\Users\jjensen\.claude\CLAUDE.md` — operator preferences.
2. [WP-085](../work-packets/WP-085-tv-app-pipeline.md) — scope, §Decisions,
   §Notes.
3. [DECISIONS](../ai/DECISIONS.md) — **2026-11-26 "Ship the free Google TV app
   first"** (pipeline first, WP-084 as the Play release) and **2026-11-26
   "Public naming"** (product name, prices and launch dates stay private).
4. [WP-084](../work-packets/WP-084-google-tv-first-release.md) — the Play
   release that follows; its gamepad-required input and Gate 0.
5. [Smart-TV guide §Controls on a TV](../reference/scummvm-smart-tv.md#controls-on-a-tv)
   — what's been tried on the TCL 65Q77K.
6. The ewiki private page **Commercial Strategy**: §"App name and package id
   candidates for WP-085" and §"Lead: one shared runtime" (read in
   `C:\dev\scooby-engine-private\private\commercial-strategy.md`).
7. The 🔮 "Shared runtime and separate game-data apps" row in
   [WORK_INDEX](../work-packets/WORK_INDEX.md).

## Pre-execution checks

- [ ] Both checkouts fetched; `main` in each includes the shared-runtime
      placeholder (public `fa170c8` or later) and the strategy lead (private
      `08e1cca` or later), plus the name-candidates section.
- [ ] WP-085's §Decisions still shows D1–D4 unanswered. If any is already
      answered, record only the rest.

If a check fails, stop and report.

## The four decisions — evidence to present

Put each to Jeff as a short question with the options below, your
recommendation first, then record his answer **in his own words**. Copilot's
2026-11-26 proposals are included as Copilot's, not as decided.

**D1 — App name and package id.** Candidates are on the private page:
the earlier working name, and Copilot's proposal (with its package id). Facts
to state: the package id can't change after the first Play publication; other
apps would detect the runtime by it (shared-runtime lead); "ScummVM" can't be
the product name. **Record the answer only on the private page** and write
"answered; tracked privately" in public WP-085.

**D2 — Input requirement for the Play release.**

| Option | Works today on the TCL? | Google TV review |
|---|---|---|
| **Gamepad required**; keyboard and mouse supported (WP-085's recommendation) | Yes: left stick moves the pointer | Meets TV-GP / TV-DK: a required game controller is the one exemption from D-pad navigation |
| **D-pad required**; keyboard and mouse supported (Copilot's proposal) | **No.** The smart-TV guide records that a plain D-pad can't move ScummVM's pointer, and that remapping it was tried on the TCL and is unreliable | Meets TV-DP, but only once a D-pad pointer exists |
| Mouse required | Yes | **No exemption** in the [TV app quality](https://developer.android.com/docs/quality-guidelines/tv-app-quality) rules; risks review |

Tell Jeff plainly: choosing D-pad pulls the D-pad pointer (currently out of
WP-085's scope) into WP-085 or a new WP before any Play release. Either way the
remote must navigate the library and menus.

**D3 — Where test packages are hosted.**

| Option | Notes |
|---|---|
| **GitHub Releases** (Copilot's proposal) | GitHub's [documented limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases): up to 1,000 assets per release, each under 2 GiB, no total-size or bandwidth limit. **Public** unless the repo is private, so only for data we may redistribute: the *Beneath a Steel Sky* freeware (readme intact). Never *Showdown* or other licensed data |
| Cloudflare behind Access (WP-085's recommendation) | Private to authorized devices; fits licensed data later |

A reasonable combined answer: GitHub Releases for freely redistributable test
packages, an access-controlled host (Cloudflare) for anything licensed, and a
downloader that takes any HTTPS URL from the manifest so the host can change
without a code change (Copilot's point; adopt it in WP-085 either way). Ask
Jeff which repo would hold the releases; a dedicated one keeps game data out of
the engine repos.

**D4 — Does the advanced mode ship in the Play build?**

| Option | Notes |
|---|---|
| Test builds only for v1 (WP-085's recommendation) | Smallest review surface for the first release |
| **In the Play build, behind an Advanced Settings switch** (Copilot's proposal) | Useful to enthusiasts. It downloads data only, which Play's Device and Network Abuse policy allows (interpreted game data is exempt); it must never offer unauthorized games or bypass a purchase |

Facts to state: of Copilot's import routes, USB storage and user-selected
files go through the system file picker (untested on the TCL); "local
network" would need ScummVM's local web server, which the smart-TV guide
records as left out of the fork's Android build.

## Execution rules

**Scope allowlist:**

```
docs/work-packets/WP-085-tv-app-pipeline.md
docs/execution-checklists/EC-008-tv-app-pipeline.md
docs/work-packets/WP-084-google-tv-first-release.md   (only if D2 changes its input)
docs/work-packets/WORK_INDEX.md
docs/ai/DECISIONS.md
private/commercial-strategy.md                          (private repo; D1 only)
```

**Forbidden:** product name, package id or prices in any public file; any
external resource creation; game data anywhere in git; engine or fork code.

**You MUST:**

- Quote Jeff's answers verbatim in the WP and the DECISIONS entry.
- Keep a recommendation a recommendation until Jeff answers.
- Run the ewiki gates with both repos mounted
  (`ewiki/themes/ewiki/tools/Invoke-WikiGates.ps1`, the private worktree
  junctioned as `_private`) and check every link and anchor you add.
- Merge order: public before private when the private page links new public
  anchors.

## Session task

Outputs this session MUST produce:

1. WP-085 §Decisions: D1–D4 marked answered, with Jeff's words (D1 as
   "tracked privately").
2. WP-085 and EC-008 updated where an answer changes scope or checks (D2
   input; D3 manifest and downloader wording, host-independent; D4 whether
   the advanced mode ships).
3. A DECISIONS entry "2026-MM-DD — WP-085 decisions (input, test-package
   hosting, advanced mode)", with the public parts only.
4. The private page's candidates section updated with the chosen name and id.
5. WORK_INDEX's WP-085 row updated; if all four are answered, WP-085 is ready
   for pre-flight.
6. PRs open in both repos, gates green.

Outputs this session MUST NOT produce: the pre-flight, any implementation,
Play or GitHub resources, uploads, or messages to anyone.

## Close ritual

1. Confirm the gates pass and links resolve.
2. Open both PRs; state the merge order.
3. Report to Jeff: each decision and where it's recorded; any scope change it
   caused; that WP-085 is ready for pre-flight (or what's still open). Ask
   before merging or deploying.
