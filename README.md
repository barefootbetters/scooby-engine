# Scooby-Doo ScummVM Engine

Reverse-engineering and engine implementation project to run
[The Learning Company's *Scooby-Doo* CD-ROM adventure games][mobygames]
(2000–2003) in [ScummVM](https://www.scummvm.org/).

**Status: Phase 1 — Format Research** · [Progress site →][pages]

[mobygames]: https://www.mobygames.com/game/scooby-doo-showdown-in-ghost-town/
[pages]: https://github.barefootbetters.com/scooby-engine/

---

## Target games

| Title | Year | Developer | Status |
|---|---|---|---|
| *Scooby-Doo! Showdown in Ghost Town* | 2000 | TerraGlyph | 🔬 Primary RE target |
| *Scooby-Doo! Phantom of the Knight* | 2001 | TerraGlyph | ⏳ Pending Phase 1 |
| *Scooby-Doo! Jinx at the Sphinx* | 2001 | TerraGlyph | ⏳ Pending Phase 1 |
| *Scooby-Doo! Case File #1: The Glowing Bug Man* | 2002 | Unknown | ❓ Engine family TBD |
| *Scooby-Doo! Case File #2: The Scary Stone Dragon* | 2003 | Unknown | ❓ Engine family TBD |

---

## What lives here

```
docs/               Research documentation and format specs
  01-VISION.md      Project vision, phases, feasibility assessment
  02-SCUMMVM-INTEGRATION.md  ScummVM API contract for the engine
  formats/          Reverse-engineered file format specs
    tgifile-art.md    Graphics archive (144 MB, two-level index confirmed)
    audio-archives.md Music / SFX / Voice .dat archives
    scooby-exe.md     Main executable (Ghidra analysis plan)
tools/              Python scripts for format probing and asset extraction
```

Engine code lives in the ScummVM fork at
[barefootbetters/scummvm](https://github.com/barefootbetters/scummvm)
under `engines/scooby/` — created in Phase 2.

---

## Current findings

| File | Status |
|---|---|
| `TGIFILE.ART` | ✅ Two-level index confirmed (69 groups, 453 assets). Payload compression under investigation. |
| `Music.dat` / `Sfx.dat` / `Voice.dat` | ✅ 12-byte header confirmed. Index table + codec TBD. |
| `BK.XXX` | ✅ Bink video — handled by ScummVM's built-in decoder. |
| `object.ini` | ✅ Plain Windows INI (1,405 lines). No decoding needed. |
| `Scooby.eng` | ✅ Plain-text string table. No decoding needed. |
| `Scooby.exe` | 🔬 Ghidra analysis pending. |

---

## Development phases

- **Phase 1 — Format Research** ← *current*
- Phase 2 — ScummVM Engine Scaffold
- Phase 3 — Resource Loading
- Phase 4 — Game Logic
- Phase 5 — Polish & Upstream PR

See [docs/01-VISION.md](docs/01-VISION.md) for full phase exit criteria.

---

## Legal

Reverse engineering for interoperability is lawful under 17 U.S.C. § 107
and EU Software Directive 2009/24/EC Article 6. ScummVM has operated under
this framework since 2001. No copyrighted game data is included here.
Players supply their own discs or legally obtained ISOs.

---

## Contributing

This is a personal research project; not yet accepting contributions.
Once an engine scaffold exists in Phase 2, that will change.
