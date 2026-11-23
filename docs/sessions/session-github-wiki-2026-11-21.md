---
layout: default
title: "Session Prompt — build out the GitHub wiki"
---

# Session Prompt — improve the GitHub wiki (screenshots, download/install, landing)

> **Standalone documentation session — not a WP.** No pre-flight/EC. It touches
> no `engines/scooby/**` and no format docs, so it needs no pre-flight gate. Paste
> this as the first message to a fresh session. Keep it leashed: this session does
> the wiki and nothing else; it does not spawn execution sessions, and it verifies
> every empirical claim before writing it (the 2026-11-21 fabrication incident —
> see [DECISIONS.md](../ai/DECISIONS.md) — is why).

## Header

- **Target surface:** the **GitHub wiki** at
  <https://github.com/barefootbetters/scooby-engine/wiki> — its **own** git repo,
  `https://github.com/barefootbetters/scooby-engine.wiki.git`. This is a *fourth*
  public surface, separate from the GitHub Pages site
  (`github.barefootbetters.com/scooby-engine/`), the ewiki
  (`scooby-engine-ewiki.barefootbetters.com`), and the studio site. Edit **only**
  the wiki repo.
- **Audience:** the public — players and curious visitors, not developers.
- **Session date:** fill in `<YYYY-MM-DD>` when run.

## Intent

Build the GitHub wiki into a friendly, visual public landing for the project:
what it is, **screenshots of the engine running**, how to **download and install**
(Windows preview + build-from-source), what's playable, and a short FAQ. The
wiki's unique value is the **welcome + the screenshots** — the other surfaces have
the reference detail. So keep drift-prone facts (install steps, per-title status)
as **links** to the authoritative pages, not copies (the "linked sections to avoid
drift" rule the rest of the docs follow).

**Out of scope (do not do):** editing the main repo, `engines/scooby/**`, the
Pages site, the ewiki, or the studio site; cutting a release; capturing or
inventing anything you can't verify; a from-scratch rewrite of the authoritative
install/status pages (link to them instead).

## Authority chain (read first)

1. `C:\Users\jjensen\.claude\CLAUDE.md` — operator preferences (tone, PowerShell, no busy-body posturing, own mistakes).
2. [docs/01-VISION](../01-VISION.md) — vision, scope, non-goals, the legal/copyright stance.
3. **The authoritative pages the wiki will link to (read, do not copy):**
   - [docs/reference/download-and-install.md](../reference/download-and-install.md) — the canonical install guide (all platforms).
   - [docs/reference/scummvm-wiki-scooby.md](../reference/scummvm-wiki-scooby.md) — live per-title status, data files, MD5s, limitations.
   - [docs/reference/why-forked-scummvm.md](../reference/why-forked-scummvm.md) — the fork decision.
4. [docs/assets/screenshots/showdown-screens/index.md](../assets/screenshots/showdown-screens/index.md) — the existing screenshot library and its **provenance** (see §Screenshots rule below).
5. This prompt.

## Pre-execution checks

- [ ] **Initialize the wiki first (gotcha).** `git ls-remote https://github.com/barefootbetters/scooby-engine.wiki.git` currently returns **"Repository not found"** — GitHub does not create the `.wiki.git` repo until the **first page is saved in the web UI**. Create a `Home` page once at <https://github.com/barefootbetters/scooby-engine/wiki> ("Create the first page" → save anything) — via the built-in browser, or ask Jeff to click it — **then** clone and push the rest. Confirm `ls-remote` succeeds before relying on git.
- [ ] **Release link resolves:** `https://github.com/barefootbetters/scummvm/releases/latest` → 200, and the Windows zip asset is attached.
- [ ] **Raw image URLs resolve** (repo is public): e.g. `https://raw.githubusercontent.com/barefootbetters/scooby-engine/main/docs/assets/screenshots/showdown-screens/ROOM_P01_Town_Center.png` → 200.
- [ ] **Decide the screenshot source** per the rule below before embedding any image.

If the wiki repo can't be initialized this session (no browser, Jeff unavailable), **stop and report** — don't fake the wiki.

## Execution rules

**How to edit the wiki:** after it's initialized, `git clone
https://github.com/barefootbetters/scooby-engine.wiki.git` into a worktrees
folder, edit the `.md` pages, commit, `git push`. Page file names map to wiki
page titles (`Home.md`, `Download-and-Install.md`, `Screenshots.md`,
`_Sidebar.md`, `_Footer.md`). Do this in `C:\claude-worktrees\`, never inside a
project checkout.

**Linked sections, to avoid drift (REQUIRED).** The wiki is the fourth surface for
this content. Do **not** restate install commands or the per-title status table —
they will rot. Link them:
- Install/build detail → `https://github.barefootbetters.com/scooby-engine/docs/reference/download-and-install/`
- Live status / supported titles / data files → `.../scummvm-wiki-scooby/`
- Why it's a fork → `.../why-forked-scummvm/`
The wiki carries the welcome, the screenshots, the one-click download link, and a
short FAQ — the parts the other surfaces lack.

**Screenshots — accuracy rule (REQUIRED; this is the fabrication guard).** Label
every screenshot by what it actually is. The committed
`docs/assets/screenshots/showdown-screens/*.png` (36 of them) are **captures of
the *original* game from a YouTube longplay** (RE reference ground truth — see
their `index.md`), **not** our engine. Do **not** present them as "the Scooby
ScummVM engine running." To show off the port, **capture fresh screenshots of our
engine** this session and label them as such:
- Headless: the engine's `test_script` supports `shot <name>` (saves `<name>.bmp`
  to `test_shots/`) with `start_room` / `start_items` — see
  [02-SCUMMVM-INTEGRATION §9 live tests](../02-SCUMMVM-INTEGRATION.md#9-debug-channels).
  Run the built engine against a mounted *Showdown* disc, capture a few rooms,
  convert to PNG.
- Or, with Jeff, capture a handful of clean frames from the actual GUI he runs.
If neither is possible this session, it is honest to use the YouTube reference
shots **clearly captioned as the original game** ("the original *Showdown*; our
engine reproduces these rooms") and say the port screenshots are pending — but
never imply they came from our engine.

**Copyright / public surface:** these are copyrighted game visuals used for
documentation/commentary (the project's standing posture — [01-VISION](../01-VISION.md)).
Keep it a modest showcase, not an asset dump. Repeat the **bring-your-own-discs /
no game data** line, and that this is a **fork**, not official ScummVM. Choose the
privacy-preserving, honest framing; add no marketing claims you can't back.

**Verify, don't fabricate:** every factual claim (what's playable, the download,
that a screenshot is our engine) is checked against the live source before it goes
on the page. No invented console output, no mocked screenshots, no "it works"
without having seen it.

**Commits** (wiki repo): short imperative subjects; keep the project's
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer (the wiki is part
of this fork's own docs, not the upstream-bound branch).

## Session task

Create these wiki pages (link, don't duplicate; see rules above):

1. **`Home.md`** — one-paragraph intro; a hero screenshot (our engine, or a
   clearly-labeled original-game shot); a short "What you can play" line
   (*Showdown* playable preview; *Phantom* in development) linking to the live
   status page; a prominent **Download** link (`releases/latest`); the
   bring-your-own-discs + fork note; a nav list to the other wiki pages.
2. **`Download-and-Install.md`** — the one-click **Windows** download
   (`releases/latest`) and the four run steps (unzip → run `scummvm.exe` → Add
   Game → pick the disc's `\scooby\` folder → Start). For other platforms / build
   from source, **link** the full install guide. Do not restate the build commands.
3. **`Screenshots.md`** — a captioned gallery embedding images by raw URL
   (`raw.githubusercontent.com/...`) so there's a single source. Label each shot's
   source honestly (our engine vs. original reference).
4. **`FAQ.md`** (or a section on Home) — "Showdown doesn't appear in the launcher"
   (enable *Show testing games*); "where do I point it?" (the `\scooby\` folder);
   "is this official ScummVM?" (no — a fork, link why-forked); "where do I report
   problems?" (`github.com/barefootbetters/scummvm/issues`).
5. **`_Sidebar.md`** + **`_Footer.md`** — simple nav (the pages above) and a footer
   with the trademark/affiliation disclaimer.

**Sprawl guard — do NOT:** rewrite the install or status pages here; add titles
to the playable list beyond what the status page says; build an exhaustive
room-by-room gallery (a handful of representative shots); touch any repo but the
wiki.

## Close ritual

1. **Verify live.** Load each new page on the rendered wiki
   (`github.com/barefootbetters/scooby-engine/wiki/...`); confirm images render and
   every link resolves (the four external links + inter-wiki links). Fix any 404.
2. **Confirm honesty.** Re-check that no screenshot is mislabeled and no claim is
   unverified.
3. **Report** to Jeff: the pages created, the live wiki URLs, which screenshots
   are our-engine vs. reference, and anything deferred (e.g., port screenshots not
   captured). If the wiki couldn't be initialized, say so plainly — don't report a
   wiki that isn't live.

Do not mark anything "done" that you have not loaded and seen on the live wiki.
