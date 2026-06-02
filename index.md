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

---

## Documentation

- [Project Vision](docs/01-VISION) — goals, target games, feasibility, development phases
- [ScummVM Integration Contract](docs/02-SCUMMVM-INTEGRATION) — API surface, acceptance gates, PR checklist
- [TGIFILE.ART Format Spec](docs/formats/tgifile-art) — graphics archive reverse engineering
- [Audio Archives Spec](docs/formats/audio-archives) — Music / SFX / Voice .dat format
- [Scooby.exe Analysis Plan](docs/formats/scooby-exe) — Ghidra roadmap

---

## Target Games

| Title | Year | Engine |
|---|---|---|
| *Scooby-Doo! Showdown in Ghost Town* | 2000 | TerraGlyph — primary RE target |
| *Scooby-Doo! Phantom of the Knight* | 2001 | TerraGlyph |
| *Scooby-Doo! Jinx at the Sphinx* | 2001 | TerraGlyph |
| *Scooby-Doo! Case File #1* | 2002 | Engine family TBD |
| *Scooby-Doo! Case File #2* | 2003 | Engine family TBD |

---

## Source

Engine research: [barefootbetters/scooby-engine](https://github.com/barefootbetters/scooby-engine)  
ScummVM fork (Phase 2+): [barefootbetters/scummvm](https://github.com/barefootbetters/scummvm) — `engines/scooby/`
