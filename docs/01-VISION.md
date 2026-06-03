---
layout: default
title: "Vision — Scooby-Doo ScummVM Engine"
---

# Vision: ScummVM Engine for The Learning Company Scooby-Doo Games

**Project:** `scooby` engine for ScummVM
**Status:** Pre-development — format research
**Started:** 2026-06

---

## Goal

Implement a new ScummVM engine that runs The Learning Company's *Scooby-Doo*
CD-ROM adventure games on modern hardware via
[ScummVM](https://www.scummvm.org/), and contribute the engine upstream.

Once complete, players add these games to ScummVM the same way as any other
supported title — point ScummVM at their disc or ripped ISO, and play.

---

## Non-Goals

- Bundling or redistributing copyrighted game data. Players supply their own discs.
- Modding, rebalancing, or "improving" the games. The goal is faithful playback.
- Supporting platforms ScummVM doesn't already support.
- Standalone reimplementation outside ScummVM (DOSBox shims, custom runtime, etc.). ScummVM is the deliverable.

---

## Target Games

All Scooby-Doo CD-ROM adventure titles published by The Learning Company /
Passport / Knowledge Adventure between 2000 and 2003, plus a 2007 re-release.
Engine sharing across the set is partially confirmed (TerraGlyph trio) and
partially open (Case Files) — see the provenance check below.

| Title | Year | ISO file | Size | Notes |
|---|---|---|---|---|
| *Scooby-Doo! Showdown in Ghost Town* | 2000 | `Scooby Doo Showdown in Ghost Town.iso` | 607 MB | Primary RE target |
| *Scooby-Doo! Phantom of the Knight* | 2001 | `Scooby Doo Phantom of the Knight.iso` | 593 MB | Secondary target |
| *Scooby-Doo! Jinx at the Sphinx* | 2001 | `Scooby Doo Jinx at the Sphinx.iso` | 554 MB | |
| *Scooby-Doo! Case File #1: The Glowing Bug Man* | 2002 | `Case File 1.iso` | 407 MB | |
| *Scooby-Doo! Case File #2: The Scary Stone Dragon* | 2003 | `Case File #2.iso` | 584 MB | |
| *Scooby-Doo! Case File #3: Frights, Camera, Mystery!* | 2003 / 2007 re-release | `Scooby Doo! #3.iso` | 174 MB | Disc on hand is the 2007 Encore Software re-release ([archive.org/details/scooby-doo-3](https://archive.org/details/scooby-doo-3)), reportedly a Macromedia Flash application. Likely a different engine — verify in Phase 1; may be out of scope. |

Also on disk: `ScoobyDoo.iso` (221 MB). Identified via the companion
`archive.org-activity-challenge.url` shortcut (pointing to
`archive.org/details/scooby-dooac2001`) as **Scooby-Doo! Activity Challenge**
(2001). This is an edutainment title rather than a point-and-click
adventure, so it almost certainly uses a different engine — treat as
out of scope unless Phase 1 inspection shows otherwise.

The `C:\pcloud\SCOOBY\` directory also contains `archive.org-*.url`
shortcuts for each disc, recording the provenance of the rips.

**Provenance check (2026-06):** archive.org and MobyGames confirm the five
core ISOs are original Learning Company pressings (only Case File #3 is a
re-release). Developer attribution splits the list into two eras:

- **TerraGlyph Interactive Studios** developed *Showdown* (2000),
  *Phantom of the Knight* (2001), and *Jinx at the Sphinx* (2001). TLC
  published. Confirmed via Wikipedia, MobyGames, and PCGamingWiki.
- **TerraGlyph shut down in 2001** (per Wikipedia). The *Case File* titles
  (#1, 2002; #2, 2003) shipped after that closure, under Riverdeep / The
  Learning Company successor branding. Their actual development studio is
  ambiguous in public sources (ImageBuilder Software has been credited in
  some listings). It is plausible but **not confirmed** that they inherited
  the TerraGlyph engine via IP transfer — TLC was itself acquired by
  Riverdeep around the same time.
- The **Case File #3** disc on hand is the 2007 Encore Flash re-release,
  almost certainly a different engine.

Implication: the "single shared engine" assumption only holds with
confidence for the three TerraGlyph titles. Whether the Case Files share
that engine is a Phase 1 question, answered by mounting the ISOs and
comparing file structures (`TGIFILE.ART`, `Scooby.exe`, `object.ini`).

---

## Engine Lineage (2026-06 finding)

Phase 1 cross-title analysis (Rich Header on each title's main binary +
archive magic-byte inspection — see
[`docs/formats/scooby-exe.md`](formats/scooby-exe.md) Findings) reveals
**one engine lineage across three format generations**:

| Gen | Titles | Toolchain | Archive | Config | Cutscenes |
|---|---|---|---|---|---|
| **1** | Showdown (2000), Phantom (2001) | VC5 + Linker 5.10 build 8047 | `TGIFILE.ART` (raw count + index) | INI text (`object.ini`, `Scooby.eng`) | Bink |
| **2** | Jinx (2001) | VC5 + Linker 5.10 build 8168 | `MMFW` wrapper container | TBD (likely INI) | Bink + Smacker |
| **3** | Case File #1 (2002) | VC5 + Linker 5.10 builds 8168 + 8797 + one VC6 file | `MMFW` continues | XML via `libexpat.dll` | raw `.avi` |

The Gen 1 → Gen 2 jump (mid-2001) coincides with a TerraGlyph build
pipeline upgrade — new linker build, dropped legacy tools (MASM 6.14,
cvtres), cleaner single-environment build. The Gen 2 → Gen 3 jump
(late 2001 / 2002) coincides with the TerraGlyph shutdown and
ImageBuilder Software (IBS) taking over development — confirmed
concretely by:

- IBS shipping Jinx-era compiled object files into Case File #1 (the
  Linker 5.10 build 8168 entries appear in both binaries' Rich Headers)
- IBS adding their own code on top with an updated toolchain (Linker
  5.10 build 8797, plus one VC6-compiled source file)
- IBS introducing XML configuration via `libexpat.dll`
- The Case File #1 disc carrying an `IBSlogo.avi` alongside `TLClogo.avi`

The TerraGlyph engine codebase continued through IBS via **direct code
inheritance** (object files literally embedded), not just architectural
reuse. This is the strongest possible engine-family signal.

**Predictions for unverified titles:**

- Case File #2 (2003): Gen 3 — likely same IBS toolchain mix, MMFW + XML + AVI
- Phantom (2001): currently classified Gen 1 based on toolchain match to Showdown; archive format unverified (could be Gen 1 `TGIFILE.ART` or early Gen 2 `MMFW`). One-minute Format-Hex check next time the disc is mounted will lock it in.
- Case File #3 (2007 Encore Flash re-release) and Activity Challenge: remain out of scope (different engine families entirely).

**Implementation implication:** the `scooby` ScummVM engine covers one
engine lineage with format-version-aware adapters — three archive
parsers, two config parsers, three video paths — not three separate
engines. The detection table (`ADGameDescription`) carries a `gen`
flag per entry; the engine branches at the format-version boundaries.

---

## Why This Is Feasible

Most engine reverse engineering projects start from fully opaque binary
formats. Initial inspection of *Showdown in Ghost Town* found that this
engine is unusually well-structured.

### Verified — human-readable as shipped

- **`object.ini`** — Windows INI file (1,405 lines) defining every interactive
  object, room exit, inventory item, cursor animation, and destination room.
  No decoding required.
- **`Scooby.eng`** — Plain text localized string table using a simple `[NNNN]`
  message ID format. Trivial to parse.

### Verified — handled by existing ScummVM code

- **`BK.XXX`** — Bink video (magic bytes `BIKi`). ScummVM ships a Bink decoder;
  all cutscenes and animations route through it.

### Not yet decoded — reverse engineering required

#### `TGIFILE.ART` — primary risk area

144 MB proprietary archive. Initial hex inspection has confirmed the
two-level index structure; **payload decoding** remains the sole Phase 1
blocker. See `docs/formats/tgifile-art.md` for the full byte-level spec.

**Confirmed structure (Showdown, 2026-06):**
- Offset 0x0000: `uint32LE` = 69 — group count (confirmed, not a hypothesis)
- Offsets 0x0004–0x0117: 69 × 4-byte group descriptor table (values do not
  map to file offsets — meaning TBD; may be packed indices or checksums)
- Offset 0x0118: `uint32LE` = 453 — asset entry count
- Offsets 0x011C–0x0F43: 453 × 8-byte entries, each `(start: uint32LE, end: uint32LE)`
- Offsets 0x0F44–0x10017D: engine resource-name catalog (~1,400 records,
  68-byte stride; the OBJ section is 1:1 with the asset entry table — so
  `entry[i]` is the payload for `OBJ` id `i`)
- First asset payload at file offset 1,048,958 (0x10017E); entry sizes range
  2–9 MB (consistent with full-screen background frames)

**Remaining unknowns:**
- Payload compression: opening bytes `F0 0C 25 5C 12 AE F0 08` match no
  standard codec header; F0 pattern suggests custom opcode-based encoding.
- Pixel format unknown until first successful decode. WP-003 ruled out the
  pre-payload region as the palette location; the palette is either in
  per-asset leading bytes or in the 20-byte per-record metadata field on
  name-table records.

**Remaining investigation:**
1. Decode the F0-opcode payload: attempt RLE with opcode dispatch, then raw
   indexed bitmap, then truecolor — each tested against entry 0 (~6 MB; the
   smallest of the first four documented entries — and per WP-003 it's
   `OBJ_DAPHNE_A`, a character sprite, not a background).
2. Correlate decoded output visually against a known Showdown screenshot.

Execution tracked in
[WP-001](work-packets/WP-001-ghidra-session.md) (Ghidra decode trace),
[WP-002](work-packets/WP-002-tgifile-art-decoder.md) (Python decoder + first
image extraction), and
[WP-003](work-packets/WP-003-pre-payload-region.md) (pre-payload region
characterization, ✅ landed 2026-06-02), with companion checklists
[EC-001](execution-checklists/EC-001-ghidra-session.md) and
[EC-002](execution-checklists/EC-002-probe-art-harness.md).

Success condition: render at least one *Showdown* background or sprite to
PNG/BMP outside the engine, matched visually against the original.

#### Audio archives

`Music.dat`, `Sfx.dat`, `Voice.dat`. Header structure confirmed (2026-06);
index table layout and codec still unresolved.

**Confirmed structure (all three files share the same 12-byte header):**
- Bytes 0x00–0x0B: `version` (= 1, uint32LE), `entry_count` (uint32LE),
  `field3` (uint32LE; sector-aligned quantity, semantics unconfirmed — see
  [`docs/formats/audio-archives.md`](formats/audio-archives.md) for the
  Voice.dat anomaly that rules out a naïve "data size" interpretation)
- Music.dat: 28 entries / 91.7 MB — Sfx.dat: 316 entries / 30.7 MB —
  Voice.dat: 821 entries / 103.8 MB
- Bytes 0x0C–0x4F: all zeros — index table has not been located (may be at
  end-of-file, or the header encodes an index offset not yet read correctly)

**Remaining unknowns:**
- Index table location and per-entry stride.
- Codec: no standard magic bytes (RIFF/WAV, OggS, FLAC) at offset 0.
- Meaning of `field3`.

Execution tracked in
[WP-004](work-packets/WP-004-audio-archive-decode.md).

For Phase 1, codec identification is sufficient — full decode can defer to
Phase 3 if ScummVM already supports the codec.

#### `Scooby.exe`

Main executable. Ghidra analysis needed to map room transitions, puzzle
state, and resource loading — but see **Game Logic Strategy** for how to
keep that scope from spiraling.

---

## Runtime Dependencies (Original Game)

- **DirectX 7.0** — graphics + sound. ScummVM abstracts both away.
- **`binkw32.dll`** — Bink video runtime. ScummVM's built-in decoder replaces it.

---

## Engine Contract (ScummVM Requirements)

The `scooby` engine must conform to ScummVM conventions:

- **Stateless per-frame rendering.** No reliance on OS-managed surfaces; the ScummVM compositor owns the screen.
- **Centralized event loop** via `Engine::run()`. No threaded I/O or hidden update loops.
- **File access via ScummVM abstractions** (`Common::File`, archive members) — no direct filesystem calls.
- **In-engine decoding only.** No external DLLs at runtime; Bink playback uses ScummVM's built-in decoder.
- **Deterministic, platform-independent behavior.** Same input produces the same output across all ScummVM ports.

Implication: anywhere the original engine relied on DirectX surfaces,
threaded resource streams, or implicit Windows-global state, that logic must
be re-expressed in ScummVM-compatible form. Architectural drift here is the
silent way a ScummVM PR gets bounced — keep it tight from Phase 2 onward.

For the concrete API contract (which classes to subclass, which calls to
make, what the upstream PR must satisfy), see
[`docs/02-SCUMMVM-INTEGRATION.md`](02-SCUMMVM-INTEGRATION.md). This vision
doc owns the principles; that doc owns the implementation surface.

---

## Game Logic Strategy

Game logic will be reconstructed via two approaches, in priority order:

**A. Data-driven (preferred).** Behavior inferred from `object.ini`,
`Scooby.eng`, and observed disc layout. Minimal disassembly. If
`object.ini` can describe a behavior — room exits, hotspot actions, cursor
mappings, inventory rules — read it from `object.ini`.

**B. Binary-assisted (fallback).** Where data files don't fully specify
behavior — puzzle state machines, animation timing, save-game format —
trace the relevant subroutine in `Scooby.exe` via Ghidra and reimplement.

**Rule:** disassembly is a last resort. Every Ghidra-derived function adds
Phase 4 scope. Prefer the data-driven path whenever it's feasible. The
1,405-line `object.ini` strongly suggests TerraGlyph already exposed most
behavior as data — exploit that.

---

## Risks & Unknowns

- **Engine architecture mismatch.** ScummVM's conventions assume things like
  fixed palette banks, frame-stepped event loops, room-scoped resources. If
  TLC's engine made very different assumptions (compositing in screen space,
  threaded resource streams, heavy scripting), more glue code is needed and
  some assumptions in this plan break.
- **Audio codec.** If `Music.dat` uses a licensed codec (Miles Sound System,
  patent-encumbered MP3 frames, etc.), playback may not fit ScummVM's existing
  backends cleanly.
- **Cross-title divergence (resolved 2026-06).** Phase 1 cross-title
  analysis confirms one engine lineage spanning three format generations
  (Gen 1 Showdown/Phantom, Gen 2 Jinx, Gen 3 Case Files). IBS inherited
  TerraGlyph's compiled object files into Case File #1, confirming
  code-level continuity. The engine implementation needs format-version-
  aware parsers (one per generation per axis: archive, config, video)
  but is not split across multiple engines. See "Engine Lineage" section
  above for the full table. Residual risk: Case File #2 not yet
  verified; Phantom's archive format not yet locked to Gen 1 vs Gen 2.
- **Schedule realism.** This is a first-time ScummVM engine on an undocumented
  format. The reference engine, [BOLT](https://wiki.scummvm.org/index.php/BOLT),
  took years to get upstream. Phase ordering below is firm; durations are
  deliberately not estimated.

---

## Development Phases

Per-phase work is tracked at the WP level in
[`docs/work-packets/WORK_INDEX.md`](work-packets/WORK_INDEX.md). The phase
prose below sets the scope; the WP files specify the units of work and
their exit criteria. ECs under
[`docs/execution-checklists/`](execution-checklists/) hold step-by-step
playbooks for the WPs most likely to sprawl.

### Phase 1 — Format Research

Work items:
- `TGIFILE.ART` index structure is mapped; **remaining: decode payload and extract a known-good image from *Showdown*** (see `docs/formats/tgifile-art.md` for the probe plan).
- Locate audio archive index table; identify codec(s).
- Load `Scooby.exe` into Ghidra; trace file I/O and resource lookup.
- **Engine-family check:** mount Case File #1 and #2 ISOs; compare disc layouts and file signatures against *Showdown* (same file names, same magic bytes, compatible archive structure?).

Exit criteria (all required):
1. At least one `TGIFILE.ART` entry extracted to PNG or BMP and matched visually against in-game output.
2. `TGIFILE.ART` structure documented in `docs/formats/tgifile-art.md`: header layout (byte offsets, field sizes) and entry table (count, offsets, sizes).
3. At least one audio container inspected; codec identified by name (even if not yet decoded).
4. Engine-family question answered in writing: do Case File #1/#2 share format with *Showdown*, or do they need a separate engine?

Fail condition: inability to extract any visual asset from `TGIFILE.ART` blocks Phase 2 — revisit feasibility before continuing.

### Phase 2 — ScummVM Engine Scaffold

Work items:
- Fork `scummvm/scummvm` into `C:\www\scummvm\`.
- Create `engines/scooby/` from ScummVM's engine template.
- Implement game detection via ScummVM's `ADGameDescription` table.
- Wire up the event loop, graphics surface, and debug logging (define channels for resource loading, rendering, input, and script).

Detection requirements:
- Signature files: `Scooby.exe`, `TGIFILE.ART`, `object.ini`.
- Match on file presence + file size; use MD5 only for version differentiation.
- Detection must distinguish TerraGlyph titles from Case Files (if file structures diverge) and from regional variants.
- Do **not** match on ISO filename or disc directory structure — both are user-controlled.

Exit criteria:
1. Engine compiles cleanly against current ScummVM `master`.
2. Each of the five candidate ISOs is correctly detected or correctly rejected (e.g. Case File #3).
3. Engine launches without crash; at least one debug-channel message appears in the log.

### Phase 3 — Resource Loading

Work items:
- `TGIFILE.ART` parser integrated into the engine; render first background.
- Audio loader for at least one `.dat` archive format.
- `Scooby.eng` string parser.
- `object.ini` parser populating internal game-object structs.

Exit criteria:
1. The Room 1 background of *Showdown* renders correctly via ScummVM's graphics layer.
2. At least one interactive object from `object.ini` is positioned correctly on that background.
3. UI/dialogue strings resolve from `Scooby.eng` and display correctly.
4. One audio clip (music, SFX, or voice) plays through ScummVM's audio mixer.

### Phase 4 — Game Logic

Work items:
- Room/scene management and transitions.
- Cursor system and object interaction.
- Inventory.
- Bink video playback for cutscenes (via ScummVM's built-in decoder).
- Puzzle state machine — `object.ini`-driven first; reach for Ghidra only where data files don't suffice (see **Game Logic Strategy**).

Exit criteria:
1. *Showdown in Ghost Town* is playable end-to-end.
2. No fatal errors or progression blockers across a full playthrough.
3. All cutscenes play through ScummVM's video subsystem with no external Bink runtime.

### Phase 5 — Polish & Contribution

Scope rule (revised per Engine Lineage finding above):
- **Minimum:** full support for *Showdown in Ghost Town* (Gen 1).
- **Extended (high confidence):** Showdown + Phantom (Gen 1 — identical toolchain).
- **Extended (medium confidence):** + Jinx (Gen 2 — requires `MMFW` container parser as a sibling to the Gen 1 `TGIFILE.ART` parser).
- **Stretch:** + Case Files #1 and #2 (Gen 3 — requires Gen 2 MMFW parser, XML config via libexpat, and `.avi` cutscene path alongside the Gen 1 Bink path).
- **Excluded:** Case File #3 (2007 Encore Flash re-release) and Activity Challenge.

Each generation extends the engine with one new adapter per axis; the
shared engine core handles room/scene management, cursor/inventory,
and puzzle state across all generations.

Work items:
- Test in-scope titles; generate `ADGameDescription` entries for each.
- Save/load support if the engine has a meaningful save format; otherwise document as a known limitation.
- ScummVM wiki page covering supported titles, known limitations, and game-data requirements.
- Open PR to `scummvm/scummvm` targeting `ADGF_TESTING`.

Exit criteria:
1. PR opened with at least *Showdown* in `ADGF_TESTING`.
2. ScummVM wiki page published.
3. PR accepted (with or without revisions) into ScummVM mainline.

---

## Success Criteria

All required:
1. *Showdown in Ghost Town* boots from an unmodified ISO mount with no patches to game data.
2. A full playthrough completes to credits with no missing assets, fatal errors, or progression blockers.
3. All cutscenes render through ScummVM's video system (no external Bink runtime).
4. The engine is accepted into ScummVM mainline at `ADGF_TESTING` or higher.

Stretch:
- The TerraGlyph trilogy (Showdown + Phantom + Jinx) runs without per-title engine forks.
- Case File #1 and #2 run if Phase 1 showed engine compatibility.

---

## Tooling

Local working set, established during Phase 1:
- Hex viewer / binary diff tool for archive inspection.
- Ghidra project (`scooby.gpr`) with labeled symbols for `Scooby.exe`.
- Python extractor scripts under `tools/` for repeatable asset dumps from `TGIFILE.ART` and the audio archives.
- ScummVM debug-channel taxonomy defined in the engine (resource, render, input, script).

---

## Legal Basis

Reverse engineering for interoperability is lawful in the US (17 U.S.C. § 107;
*Sega v. Accolade*) and the EU (Software Directive 2009/24/EC, Article 6).
ScummVM has operated under this framework since 2001. Game data is never
bundled with the engine — players supply their own.

---

## File Layout

```
C:\www\scooby\          ← this project (engine research + docs)
C:\www\scummvm\         ← fork of scummvm/scummvm (engine implementation)
C:\pcloud\SCOOBY\       ← ISO images of original game discs (read-only)
```

---

## Key References

- [ScummVM HOWTO: Add a New Engine](https://wiki.scummvm.org/index.php?title=HOWTO-Add_a_new_engine)
- [ScummVM Code Contribution Guidelines](https://wiki.scummvm.org/index.php/Code_Contribution_Guidelines)
- [ScummVM BOLT engine](https://wiki.scummvm.org/index.php/BOLT) — recent example of a newly contributed engine
- [beholdnec/scummvm-funhouse](https://github.com/beholdnec/scummvm-funhouse) — BOLT engine development fork (model to follow)
- [ScummVM Forums](https://forums.scummvm.org/)
