---
layout: default
title: "Setting Up decompdecomp on Windows"
---

# Setting up decompdecomp on Windows

These steps get a Windows 11 PC ready to join the Case File #1 cooperative decompilation room, which is part of [WP-011](../work-packets/WP-011-casefile-decompdecomp.md). There are four installs, then a baseline measurement, then the join.

**What the trial is for.** Matched C rebuilds the original 2002 Windows program. It isn't a port, and it isn't engine code. The project's deliverable is still an independent ScummVM engine, written from documented behavior. The decompilation is research evidence for that engine ([WP-011 §ScummVM integration boundaries](../work-packets/WP-011-casefile-decompdecomp.md#scummvm-integration-boundaries)). The trial asks a narrower question: does decompdecomp produce that evidence faster or more cheaply than Ghidra work alone? decompdecomp's guide marks its Windows PC support as beta, so expect some friction.

## Where each instruction comes from

The page mixes three kinds of instruction. Each one is tagged with its source:

| Tag | Source | What it covers |
|---|---|---|
| **decompdecomp** | The tool's [README](https://github.com/n-delic/decompdecomp) and [GUIDE](https://github.com/n-delic/decompdecomp/blob/main/docs/GUIDE.md), read 2026-11-11 against release `v1.0.10-alpha.1` | How the tool installs, which compilers it supplies, how rooms and agents work |
| **Case File #1 project** | The collaborator's project files: its README, `tools/configure.py` and config | Which compiler this game is matched with, the build commands, where the game files go |
| **WP-011** | This project's [trial rules](../work-packets/WP-011-casefile-decompdecomp.md) | Spend caps, helper count, the baseline, what gets recorded, hygiene |

decompdecomp is young and self-updates, and its docs leave some screens undescribed. Where they don't cover a step, this page says so, so you know to look and write down what you find.

## Before you start

- Windows 10 or 11, x86-64, with an account that can approve an installer. *decompdecomp:* Windows PC games don't need WSL 2.
- Your own legally obtained Case File #1 files: the executable and `libexpat.dll`. This project keeps them in the gitignored `tools/exes/casefile1/` ([tools/exes/README](../../tools/exes/README.md)). *WP-011:* the executable's SHA-256 must match the [WP-007 lock](../formats/scooby-exe.md#binary-identity-wp-007-baseline). *decompdecomp:* every member of a room needs an identical copy.
- *Case File #1 project:* a local clone of the collaborator's repository, outside this checkout. Ask Mony for access. Put the game files in the clone's gitignored `orig/` folder as `orig/casefile1.exe` and `orig/libexpat.dll`.

## 1. Install decompdecomp

*Source: decompdecomp.*

1. Open the [latest release](https://github.com/n-delic/decompdecomp/releases/latest) and download `decompdecomp-<version>-windows-x64-setup.exe`. The guide also mentions an MSI; use whichever Windows installer the release actually lists.
2. Run it. Setup also installs WebView2 and .NET Framework 4.8 if they're missing. If Windows SmartScreen stops an unsigned installer, choose **More info → Run anyway**. Then start decompdecomp from the Start menu.
3. Record the version you installed. The app offers one-click updates, and *WP-011* records the tool version with every finding.

## 2. Install the Visual C++ 6.0 compiler

*decompdecomp:* the GUIDE's platform table lists, for Windows PC, "Visual C++ 6.0 · 7.0 · 7.1 · 2005 · 2008 · 2010 · 2017", plus any other version "from your own copy" for 32-bit games. Proprietary compilers install only after you accept their licenses in its **Setup** screen. **Compilers & tools** is a different screen, used for extras such as decomp-permuter.

*Case File #1 project:* the game is matched with **Visual C++ 6.0** by default, with one file on 7.1. Those two are the ones you need.

You don't need to install Visual Studio, old or new. decompdecomp's docs don't mention it. What matters is the period compiler that Setup supplies, because every attempt is rebuilt with that compiler and compared byte for byte.

1. Open **Setup** in decompdecomp.
2. Accept the license for the Microsoft compilers and let it download Visual C++ 6.0. If 7.1 is offered on its own, take it too.
3. Write down the folder where the toolchain lands. The docs don't say where that is, so don't guess it: step 5 needs the real path.

## 3. Install Ghidra

*decompdecomp:* the GUIDE names Ghidra as the analysis tool for Windows PC projects started from scratch. It describes no Ghidra configuration step for joining a room.

*Case File #1 project:* the collaborator's function list came from Ghidra. This project also needs Ghidra for [WP-001](../work-packets/WP-001-ghidra-session.md).

1. Install the 64-bit JDK that Ghidra's install guide names for the release you download (JDK 21 for Ghidra 11.x).
2. Download Ghidra from [ghidra-sre.org](https://ghidra-sre.org/) or its [GitHub releases](https://github.com/NationalSecurityAgency/ghidra/releases). Unzip it to a folder with no spaces in the path, such as `C:\tools\ghidra_<version>`, and start it with `ghidraRun.bat`.
3. Record the Ghidra and JDK versions. If decompdecomp asks for Ghidra, point it at that folder.

## 4. Set up an agent provider and a spend limit

*decompdecomp:* the tool has **no budget cap** of its own. When a provider limit is hit, it waits for the limit to reset and then carries on. It pauses only after five fast failures in a row. The guide reports that a small function cost about 8 cents with Claude Code; that figure is the tool's, not ours.

*WP-011:* the spend limit therefore has to come from the provider.

1. Pick a provider.
   - **API key:** DeepSeek, OpenRouter, OpenAI, or any OpenAI-compatible API, including a local model. decompdecomp recommends this route.
   - **CLI agent:** Claude Code, Codex CLI, and others. The app installs the agent and tells you how to sign in.
2. In the provider's console, set the strongest spending limit it offers before creating the key. Providers differ: some have a hard cap, others only prepaid credit or budget alerts. Prepaid credit equal to the trial's dollar cap works as a hard stop.
3. In decompdecomp, open **Agents & models → API key** and paste the key. Don't put it in any file in any repository.

## 5. Record the pre-agent baseline

*WP-011.* Before any agent touches the project, measure where it stands. This baseline is the "before" that the trial is compared against. Without it, the trial can't show what decompdecomp's agents actually added, and the collaborator's progress stays a reported figure.

*Case File #1 project:* the build needs Python 3.12 and `ninja` on the PATH. Make sure `python` is a real Python install, not one bundled inside another app; `py -3.12` avoids the problem. In the clone:

```powershell
py -3.12 tools/configure.py casefile1 --msvc "<Visual C++ 6.0 folder from step 2>"
ninja
ninja rebuild
```

`ninja rebuild` reassembles the whole program from C where the C matches and from your copy's bytes elsewhere, and reports whether the result is byte-identical. `objdiff.json` gives per-function progress in [objdiff](https://github.com/encounter/objdiff).

Record, with the commit hash of the clone:

- Functions with C, matched byte for byte, and not matched
- Whether `ninja rebuild` reports the program byte-identical
- Build warnings or failures, and which files caused them

## 6. Join the cooperative room and run the trial

*decompdecomp* for the mechanics, *WP-011* for the limits.

1. Ask Mony for the **current** invite link, privately. The room runs over a temporary tunnel, so the link changes every time he restarts decompdecomp, and an old one won't work.
2. In decompdecomp, choose **New project → Join a team's room**. Paste the link, type your display name, and pick your copy of the game (`orig/casefile1.exe`).
3. *WP-011:* before pressing **Start agents**, set a small helper count: 2 for the trial. *decompdecomp:* one start can launch up to 24; the docs don't say where the count is set.
4. *WP-011:* stop when the trial cap is reached (100 functions or your dollar cap, whichever comes first), then rerun step 5's measurements.

## Keep each project's material in its place

There are three separate places. Nothing moves between them except what the [Trial record](#trial-record-for-wp-011) below lists.

| Place | What lives there | Rules |
|---|---|---|
| **This repository** (public) | Docs, evidence, the trial record | Never commit a room link, an API key, the game files, a decompdecomp project, or matched C. `.gitignore` blocks `tools/decomp/`, `decompdecomp/`, `.env` files and the game data, but those rules are a backstop, not the process. |
| **The collaborator's repository** (private) | Matched C, project config, the game files in gitignored `orig/` | Its URL and contents stay off this public site until he agrees otherwise ([WP-011 §Legal and repository hygiene](../work-packets/WP-011-casefile-decompdecomp.md#legal-and-repository-hygiene)). Commit there only by his workflow. |
| **decompdecomp's own folder** (`Decomp` under your user folder, `~/Decomp` in its docs) | The app's projects, logs and room state | Already outside both repositories. Leave it there. |

Run `git status` before every commit, in both repositories.

## Trial record for WP-011

Record these in the WP-011 decision log and trial metrics.

**Setup (once):**
- decompdecomp version
- Compiler versions and the toolchain path
- Ghidra and JDK versions
- Provider, model and spending limit

**Pre-agent baseline (step 5):**
- The clone's commit hash
- Functions with C, matched, and not matched
- Rebuild result

**Post-trial (step 6):**
- The same counts as the baseline, rerun
- Functions attempted, matched, near misses and failures
- Helper count, agent cost and wall time
