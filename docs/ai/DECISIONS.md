---
layout: default
title: "Engine decision log"
---

# Engine decision log

Product-level decisions for the TerraGlyph engine (`terraglyph-engine`). Studio-wide
decisions live in `bb-studio-dashboard` `docs/ai/decision-log/`; this file holds
the ones specific to this engine.

---

## 2026-11-26 — WP-085 decisions (input, test-package hosting, advanced mode)

**Context.** [WP-085](../work-packets/WP-085-tv-app-pipeline.md), the Google
TV app pipeline, had four open decisions after D0 ("Pipeline first (a)").
Microsoft Copilot had proposed alternatives for three of them: D-pad-required
input, GitHub Releases hosting, and the advanced mode in the Play build behind
an Advanced Settings switch. Each decision was put to Jeff with WP-085's
recommendation and Copilot's proposal side by side. Jeff picked from the
options offered, so each answer below quotes the label he chose.

**Decisions (Jeff, 2026-11-26).**

- **D1, app identity:** answered; the name and package id are tracked
  privately, under the
  [2026-11-26 naming decision](#2026-11-26--public-naming-the-packaged-edition-targets-google-tv).
- **D2, input for the Play release:** "Gamepad required (Rec)". The app
  declares a game controller required (TV-GP), with keyboard and mouse
  supported. Copilot's D-pad-required proposal wasn't taken. Jeff, on the TCL
  65Q77K: "The D-pad can move the pointer, just that it's missing small fine
  tune movement needed to click a button or object." Until that fine control
  exists, a D-pad-only game isn't playable. The remote still has to navigate
  the library and menus.
- **D3, test-package hosting:** "Split, own repo (Rec)". Freely redistributable
  game data (the *Beneath a Steel Sky* freeware, readme intact) goes on
  **GitHub Releases in a dedicated repo**, not the engine repos. Licensed data
  goes on **Cloudflare behind Access**, never on GitHub Releases, which are
  public. Adopted from Copilot either way: the downloader takes any HTTPS URL
  from the manifest and hard-codes no host.
- **D4, advanced mode:** "Test builds only (Rec)". The package-download mode
  isn't in the v1 Play build.

**Scope boundary.**

- **In:** WP-085's input requirement, test-package hosting and manifest shape,
  and whether the advanced mode ships in the Play build.
- **Out (not decided here):** the dedicated repo's name and its creation (set
  at WP-085's pre-flight, created on Jeff's go); building the Access-protected
  host, which waits until licensed data needs it; the D-pad-only pointer,
  which stays the open remote-first item; the app's icon and banner; and
  WP-084's own D0 and D3–D5.

**Tracked as:** [WP-085 §Decisions](../work-packets/WP-085-tv-app-pipeline.md#decisions-for-jeff)
and [EC-008](../execution-checklists/EC-008-tv-app-pipeline.md). WP-085 is
ready for pre-flight.

## 2026-11-26 — Ship the free Google TV app first

**Context.** The engine's Google TV work has two possible first goals: get an
app onto Google TV, or get a first paying customer. They share the technology
but not necessarily the first game. Licensed TerraGlyph titles are gated on
rights that aren't in hand, and the studio's internal review found no paid
first product that is both lawful and defensible today: the freeware classics
ScummVM distributes (*Beneath a Steel Sky*, *Flight of the Amazon Queen* and
others) may only be distributed free, and the openly licensed candidate
reviewed earlier needed several assets cleared or replaced. Microsoft Copilot
recommended putting the free app first; Jeff relayed that recommendation, and
[WP-084](../work-packets/WP-084-google-tv-first-release.md) was drafted from it.

**Decision (Jeff, 2026-11-26).** "Log the decision to ship the free Google TV
app first." **The first Google TV / Android TV release is a free app built
from the fork, with a freeware classic included;** paid distribution comes
after it.

**Sequencing (Jeff, 2026-11-26, the same day).** Copilot then recommended
proving the delivery pipeline before choosing the first shipped game, and
[WP-085](../work-packets/WP-085-tv-app-pipeline.md) was drafted from it: a
multi-game app with a library, import of legally obtained games, verified
game-data packages, and updates. Asked how WP-085 relates to WP-084, Jeff
answered: "Pipeline first (a)." **WP-085 builds the app first; WP-084 is
re-scoped as that app's free Google Play release,** a multi-game app rather
than a single-game one. **The first bundled game is not decided here:** WP-084
plans *Beneath a Steel Sky*, subject to its Gate 0.

**Scope boundary.**

- **In:** the priority order (free app first, paid later), the sequencing
  (WP-085, then WP-084), and WP-084's re-scope.
- **Out (not decided here):** the first bundled game, and WP-084's Gate 0. Revolution Software's
  confirmation, or Jeff's separate decision to proceed on the freeware license
  alone, is still required before WP-084's implementation starts (WP-085 needs
  no rights holder: it distributes no game). Also out: WP-085's D1–D4 and
  WP-084's remaining decisions (app identity, account type, signing key,
  audience, input requirement), the paid product and its licensing, and any
  Google Play launch date or public promise. The product name and prices stay
  private under the
  [2026-11-26 naming decision](#2026-11-26--public-naming-the-packaged-edition-targets-google-tv).

**Tracked as:** [WP-085](../work-packets/WP-085-tv-app-pipeline.md) with
[EC-008](../execution-checklists/EC-008-tv-app-pipeline.md), then
[WP-084](../work-packets/WP-084-google-tv-first-release.md) with
[EC-007](../execution-checklists/EC-007-google-tv-first-release.md).

## 2026-11-26 — Public naming: the packaged edition targets Google TV

**Context.** The studio's plan for a ready-to-run (packaged) edition of the engine
went TV-first on 2026-11-22: Google TV / Android TV as the primary consumer
platform, Windows as the reference development platform. Until Jeff committed to
it, that platform naming stayed off the public pages. Since then the engine has
reached a real TV: the fork was built as an armeabi-v7a APK, sideloaded onto a
TCL 65Q77K (Google TV, Android 14), and *Showdown in Ghost Town* was played on it
from the TV's own storage on 2026-11-24 ([smart-TV guide §TV smoke test](../reference/scummvm-smart-tv.md#tv-smoke-test)).
*Showdown*'s closeout, [WP-079](../work-packets/WP-079-showdown-closeout.md), has
been **GO** since 2026-11-22.

**Decision (Jeff, 2026-11-26).** Asked whether the public studio site may say the
packaged edition is aimed at Google TV, Jeff answered: "Yes, say Google TV." The
studio's [TerraGlyph page](https://studio.barefootbetters.com/terraglyph-engine/)
may now say the ready-to-run edition is aimed at **Google TV / Android TV**.

**Scope boundary.**

- **In:** naming Google TV / Android TV as the packaged edition's target on public
  surfaces, claimed only as far as the [smart-TV guide](../reference/scummvm-smart-tv.md)
  supports: it has been sideloaded and played on a Google TV, and it is not on
  Google Play.
- **Out (stays private):** prices, the packaged edition's working product name,
  and the deal mechanics (licensing, royalties, economics). No Google Play launch
  date or promise.

**Tracked as:** the studio page update, [barefootbetters/bb-studio-www#7](https://github.com/barefootbetters/bb-studio-www/pull/7), and the
internal commercial strategy's public/private split, updated to match.

## 2026-11-23 — Repo rename: `scooby-engine` → `terraglyph-engine`

**Context.** With the engine identity rename complete and merged (fork
[barefootbetters/scummvm#10](https://github.com/barefootbetters/scummvm/pull/10),
forward docs [#184](https://github.com/barefootbetters/terraglyph-engine/pull/184),
public wiki updated), the GitHub **repo name** `scooby-engine` was the last
`scooby` identity left. The [2026-11-22 namespace-rename entry](#2026-11-22--engine-namespace-rename-scooby--terraglyph)
deliberately held the repo name "out (for now)" as a separate, higher-risk move.
Jeff has now called for it.

**Decision (Jeff).** **Rename the GitHub repo `barefootbetters/scooby-engine` →
`barefootbetters/terraglyph-engine`.** GitHub auto-redirects the old URLs (web,
API, git remotes, raw, Pages path) during a grace period that ends if a new repo
later takes the `scooby-engine` name, so forward-facing references are updated
rather than left on the redirect.

**Scope boundary — "forward-facing + local" (Jeff's choice).**

- **In:** the repo name; the Pages `baseurl` (`/scooby-engine` → `/terraglyph-engine`,
  else the live site's internal links break); forward-facing + operational references
  to this repo's own URLs/paths (README, index, current reference docs, live tooling/
  configs, `C:\dev\scooby-engine` → `C:\dev\terraglyph-engine`); the local checkout
  folder + worktree re-pointing + remotes; and the corporate-memory map.
- **Out / preserved:** the scummvm fork's integration **branch** `scooby-engine`
  (a branch, not this repo); the separate **`scooby-engine-private`** repo; the
  **`scooby-engine-ewiki.barefootbetters.com`** subdomain (a Cloudflare + DNS change,
  same out-of-scope class as the Pages DNS); the **`C:\pcloud\scooby-engine`**
  business-material folder (non-git); and the **historical records** (session logs,
  completed-WP and pre-flight files) — left as the record of what things were called
  at the time, consistent with the namespace-rename entry below.

**Not foreclosed.** The ewiki subdomain and the pCloud folder can follow later if
Jeff wants full consistency; both are deployment/DNS or business-material moves, not
code, and were deliberately left for a separate call.

## 2026-11-22 — Engine namespace rename: `scooby` → `terraglyph`

**Context.** The engine's *prose* name has been "the TerraGlyph engine" since the
2026-06 lineage finding ([VISION](../01-VISION.md)), but the ScummVM engine still
ships under the identifier `scooby`: `engines/scooby/`, `namespace Scooby`, the
plugin symbol `SCOOBY` / `ENABLE_SCOOBY`, `add_engine scooby`, and `scooby`-prefixed
detection game IDs. Mony ([2026-11-22 email](../work-packets/WP-011-casefile-decompdecomp.md#reply-rename-to-terraglyph-decode-review-landed-2026-11-22))
proposed renaming the engine `scooby` → `terraglyph`, noting a WIP engine already
holds the `scooby` name upstream.

**What was checked (Observed, 2026-11-22, via `gh`).**

- Upstream **ScummVM PR [#8063](https://github.com/scummvm/scummvm/pull/8063) —
  "SCOOBY: New engine for Scooby-Doo Mystery"** is open: a *different* game (the
  1995 Acclaim platformer) claiming the `scooby` engine identifier upstream. Our
  `scooby` collides with it in name on any future upstream path and in community /
  search terms now.
- **`terraglyph` is free upstream** — no `engines/terraglyph` on `scummvm/scummvm`
  master, and no open upstream PR mentions it.

**Decision (Jeff).** **Rename the ScummVM engine identity `scooby` → `terraglyph`**
in the fork — directory, `namespace`, plugin / `ENABLE_` symbol, `add_engine` name,
and detection game IDs — and update the forward-facing docs, public site and wiki
to name the `terraglyph` engine. The name is not a Scooby coincidence: the engine
spans the whole TerraGlyph Gen-1 catalog (Showdown, Phantom, 102 Dalmatians, Clue
Jr., Little Mermaid II, …), so `terraglyph` is the accurate family name — and the
one the project's prose already uses.

**Scope boundary.**

- **In:** the fork's engine identity + build / detection hooks; a clean rebuild and
  a green gate walk to prove the rename; the forward-facing docs (VISION,
  SCUMMVM-INTEGRATION, download-and-install, the strategy note, README, WORK_INDEX,
  the ScummVM-wiki page) and the GitHub wiki.
- **Out (for now):** the GitHub **repo name `scooby-engine`** and the Pages URL /
  DNS (`github.barefootbetters.com/scooby-engine`). Those are our own namespace, not
  in collision with upstream, and renaming them is a separate, higher-risk move Jeff
  has not called for. Historical records (pre-flight logs, completed-WP session
  logs) are left as the record of what the directory was called at the time; the
  rename is noted where it load-bears, not retrofitted across the archive.

**Tracked as:** a fork rename PR against `barefootbetters/scummvm` (link on open),
with the docs / site / wiki following in `scooby-engine`. **No upstream action** —
the [fork decision](../reference/why-forked-scummvm.md) is unchanged; this renames
the engine only within the fork.

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
