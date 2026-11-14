---
layout: home
title: Scooby-Doo ScummVM Engine
---

# Scooby-Doo ScummVM Engine

Reverse-engineering project to run [The Learning Company's *Scooby-Doo* CD-ROM adventure games](https://www.mobygames.com/game/scooby-doo-showdown-in-ghost-town/) (2000–2003) in [ScummVM](https://www.scummvm.org/).

**Phase 1 — Format Research** is underway. The goal is a contributed engine accepted into ScummVM mainline.

---

## Progress

| Component | Status |
|---|---|
| `TGIFILE.ART` index | ✅ Confirmed — 69 groups, 453 assets, 8-byte `(start, end)` entries |
| `TGIFILE.ART` payload | 🔬 F0-opcode pattern identified; decoder in progress |
| Audio `.dat` header | ✅ Confirmed — 12-byte header; entry counts known |
| Audio index + codec | 🔬 Index table location unresolved |
| `BK.XXX` Bink video | ✅ Handled by ScummVM's built-in decoder |
| `object.ini` | ✅ Plain INI — 1,405 lines of game object definitions |
| `Scooby.eng` | ✅ Plain-text string table |
| `Scooby.exe` | ⏳ Ghidra analysis queued |
| Case File #1 executable (decompdecomp) | 🚧 Access received; executable identity confirmed with the collaborator's copy; local build and capped trial next ([WP-011](docs/work-packets/WP-011-casefile-decompdecomp)) |

Executable analysis now has two complementary tracks: focused Ghidra work on Showdown's `Scooby.exe`, and a decompdecomp-assisted, cooperative decompilation of the Case File #1 executable with an outside collaborator. Progress figures from that collaboration are collaborator-reported and preliminary until reproduced here. Case File #1's place in the lineage rests on string, RTTI and source-path evidence; Case File #2 runs a different engine (WP-005). All five titles' executables are Visual C++ 6.0 builds (corrected 2026-11-14 from an earlier Visual C++ 5.0 reading).

---

## Documentation

- [Project Vision](docs/01-VISION) — goals, target games, feasibility, development phases
- [ScummVM Integration Contract](docs/02-SCUMMVM-INTEGRATION) — API surface, acceptance gates, PR checklist
- [TGIFILE.ART Format Spec](docs/formats/tgifile-art) — graphics archive reverse engineering
- [Audio Archives Spec](docs/formats/audio-archives) — Music / SFX / Voice .dat format
- [Scooby.exe Analysis Plan](docs/formats/scooby-exe) — Ghidra roadmap plus the decompdecomp track
- [Case File #1 decompdecomp Collaboration (WP-011)](docs/work-packets/WP-011-casefile-decompdecomp) — cooperative decompilation trial, evidence model, repository boundaries
- [Setting Up decompdecomp on Windows](docs/reference/decompdecomp-setup) — install, compiler, Ghidra, spend cap, local build check, joining the Case File #1 room
- [Installing ScummVM on the Raspberry Pi](docs/reference/scummvm-raspberry-pi) — the developer build of our fork, plus packaged installs

---

## Target Games

| Title | Year | Engine |
|---|---|---|
| *Scooby-Doo! Showdown in Ghost Town* | 2000 | TerraGlyph — primary RE target |
| *Scooby-Doo! Phantom of the Knight* | 2001 | TerraGlyph |
| *Scooby-Doo! Jinx at the Sphinx* | 2001 | TerraGlyph |
| *Scooby-Doo! Case File #1* | 2002 | Same lineage — Gen 3 (ImageBuilder Software, inherited TerraGlyph code) |
| *Scooby-Doo! Case File #2* | 2003 | Gen 4 format break — engine-family verdict pending (WP-005) |

---

## Source

Engine research: [barefootbetters/scooby-engine](https://github.com/barefootbetters/scooby-engine)  
ScummVM fork (Phase 2+): [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm) — `engines/scooby/`
