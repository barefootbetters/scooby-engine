---
layout: default
title: "Setting Up decompdecomp on Windows"
---

# Setting up decompdecomp on Windows

These steps get a Windows 11 PC ready to join the Case File #1 cooperative decompilation room, which is part of [WP-011](../work-packets/WP-011-casefile-decompdecomp.md). There are four installs, one local build check, and then the join.

The decompdecomp details come from its [README](https://github.com/n-delic/decompdecomp) and [GUIDE](https://github.com/n-delic/decompdecomp/blob/main/docs/GUIDE.md), read 2026-11-11 against release `v1.0.10-alpha.1`. The tool is young, self-updates, and its docs leave some screens undescribed. Where the docs don't cover a step, this page says so, so you know to look and write down what you find.

## Before you start

- Windows 10 or 11, x86-64, with an account that can approve an installer. Windows PC games don't need WSL 2.
- Your own legally obtained Case File #1 files: the executable and `libexpat.dll`. This project keeps them in the gitignored `tools/exes/casefile1/` ([tools/exes/README](../../tools/exes/README.md)). The executable's SHA-256 must match the [WP-007 lock](../formats/scooby-exe.md#binary-identity-wp-007-baseline), because every member of a room needs an identical copy.
- A local clone of the collaborator's project repository, **outside this checkout**. Ask Mony for access. Put the game files in the clone's `orig/` folder as `orig/casefile1.exe` and `orig/libexpat.dll`. That folder is gitignored there.

## 1. Install decompdecomp

1. Open the [latest release](https://github.com/n-delic/decompdecomp/releases/latest) and download `decompdecomp-<version>-windows-x64-setup.exe`. The GUIDE also mentions an MSI. Use whichever Windows installer the release actually lists.
2. Run it. Setup also installs WebView2 and .NET Framework 4.8 if they're missing. If Windows SmartScreen stops an unsigned installer, choose **More info → Run anyway**.
3. Record the version you installed. The app offers one-click updates, and WP-011 records the tool version with every finding.

## 2. Install the Visual C++ 6.0 compiler

The collaborator's project builds with **Visual C++ 6.0** by default, and one file with 7.1. decompdecomp supplies Visual C++ 6.0 through 2017 for PC games, but it installs proprietary compilers only after you accept their licenses in its **Setup** screen.

1. Open **Setup** in decompdecomp.
2. Accept the license for the Microsoft compilers and let it download Visual C++ 6.0. If 7.1 is offered on its own, take it too.
3. Write down the folder where the toolchain lands. The docs don't say where that is, and step 5 needs it.

## 3. Install Ghidra

decompdecomp's docs list Ghidra for PC projects started from scratch, and the collaborator's project was built from Ghidra's function list. This project needs Ghidra anyway for [WP-001](../work-packets/WP-001-ghidra-session.md).

1. Install the 64-bit JDK version that Ghidra's install guide names for the release you download (JDK 21 for Ghidra 11.x).
2. Download Ghidra from [ghidra-sre.org](https://ghidra-sre.org/) or its [GitHub releases](https://github.com/NationalSecurityAgency/ghidra/releases). Unzip it to a folder with no spaces in the path, such as `C:\tools\ghidra_<version>`, and start it with `ghidraRun.bat`.
3. Record the version. decompdecomp's docs don't say how the app finds Ghidra. If it asks, point it at that folder.

Keep Ghidra projects out of this checkout, or under the gitignored `ghidra/` folder.

## 4. Set up an agent provider and a spend cap

decompdecomp has **no budget cap** of its own. When a provider limit is hit, it waits for the limit to reset and then carries on. It pauses only after five fast failures in a row. So the only real spend limit is the one you set with the provider.

1. Pick a provider.
   - **API key:** DeepSeek, OpenRouter, OpenAI, or any OpenAI-compatible API, including a local model. decompdecomp recommends this route.
   - **CLI agent:** Claude Code, Codex CLI, and others. The app installs the agent and tells you how to sign in.
2. In the provider's own console, set a **hard monthly spend limit** before creating the key. For the trial, set it to the dollar cap you choose for WP-011.
3. In decompdecomp, open **Agents & models → API key** and paste the key. Don't put it in any file in either repository.

For scale, decompdecomp's guide reports that a small function cost about 8 cents with Claude Code. That figure is decompdecomp's own, not ours.

## 5. Check that the project builds locally (before any agent runs)

This step turns the collaborator's reported progress into a measured number. It needs Python 3.12 and `ninja` on the PATH. Make sure `python` is a real Python install, not one bundled inside another app; `py -3.12` avoids the problem.

In the clone of the collaborator's project:

```powershell
py -3.12 tools/configure.py casefile1 --msvc "<Visual C++ 6.0 folder from step 2>"
ninja
ninja rebuild
```

`ninja rebuild` reassembles the whole program from C where the C matches, and from your copy's bytes elsewhere, and reports whether the result is byte-identical. `objdiff.json` gives the per-function progress in [objdiff](https://github.com/encounter/objdiff). Put the counts (functions from C, matched, not matched) in the trial metrics in WP-011.

## 6. Join the cooperative room

1. Ask Mony for the **current** invite link, privately. The room runs over a temporary tunnel, so the link changes every time he restarts decompdecomp, and an old one won't work.
2. In decompdecomp, choose **New project → Join a team's room**. Paste the link, type your display name, and pick your copy of the game (`orig/casefile1.exe`).
3. Before pressing **Start agents**, set a small helper count: 2 for the trial. One start can launch up to 24. The docs don't say where the helper count is set.
4. Stop when the trial cap is reached (WP-011 suggests 100 functions, or your dollar cap) and record the results.

## Keep it out of the repo

- Never commit a room link, an API key, the game files, a decompdecomp project, or matched C to this repository. `.gitignore` blocks `tools/decomp/`, `decompdecomp/`, `.env` files and the game data, but those rules are a backstop, not the process.
- The collaborator's repository is private. Its URL and contents stay off this public site until he agrees otherwise ([WP-011 §Legal and repository hygiene](../work-packets/WP-011-casefile-decompdecomp.md#legal-and-repository-hygiene)).
- Run `git status` before every commit in both repositories.

## What to record in WP-011

Record these in the WP-011 decision log and trial metrics: the decompdecomp version, the compiler versions and the toolchain path, the Ghidra and JDK versions, the provider, model and spend cap, the helper count, and the build counts from step 5.
