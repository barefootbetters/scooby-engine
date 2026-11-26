---
layout: default
title: "WP-074: Phantom's hedge maze and maze map"
---

# WP-074: Phantom's hedge maze and maze map: ride the unicycle, read the map (Gen 1)

**Status:** ✅ Done (2026-11-19)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-023 ✅ (the inventory, for the maze map item), WP-057 ✅ (Phantom's new game and first room)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-074-2026-11-19](../reference/pre-flight-WP-074-2026-11-19.md)

---

## Result (2026-11-19)

The reference is `wp074_ref.py`: WP-073's, plus the maze, written from the
trace before the engine ran. It reads the clips from the sound index and the
cell tables from the binary's resolved constants. It never runs the engine. At
`script` level 3 the chase check now has 10 maze lines on Phantom, and one on
Showdown, which has neither room. Every line matched on both titles.

`ROOM_Hedge_Maze` and `ROOM_Maze_Map` open the audit's group 7, the maze. They
are **one packet, not split**: the map is the maze map item's close-up, reached
by using `OBJ_INV_MAZE_MAP` inside the maze, and its markers jump to the maze
rooms — the two are meaningless apart. The later group-7 rooms
(`ROOM_P23_Maze_Center`, `ROOM_P44_Fountain_Closeup`, `ROOM_P22_Well_In_Maze`,
`ROOM_P27_Below_Balcony` and its door) stay separate later packets.

**Exit criteria:**

1. **Against the reference:** ✅ Phantom:
   - **The classes:** `ROOM_Hedge_Maze` gets `HedgeMazeRoom`, `ROOM_Maze_Map` gets `MazeMapRoom`.
   - **The clips:** `Hedge_Maze.Music` and the nine `Hedge_Maze.Unicycle_*` sfx found; the idle `Hedge_Maze.240A_`/`240A1_` found (by prefix), `240A2_` not.
   - **The moves:** back/front/R/L with their dir code, step, Start/End clips and passage/wall anims.
   - **The grid:** the per-level cell tables (20, 32 and 60 cells), the path tables, the `+0x440` patch cell.
   - **The starts:** the start cell from the garden, below the balcony and the centre (two cases), and the garden-exit cells.
   - **The map:** the four markers jump to the garden, well, centre and below the balcony.
   - Showdown prints that it has no hedge maze.
2. **Live, Phantom:** ✅ Through `test_script`, minimized:
   - **The maze** draws with the unicycle and the current cell's passages (cell 24 mask 15, all four open); `Hedge_Maze.Music` loops.
   - **Riding** a direction rode to the adjacent cell and played the Start/End unicycle clips (back → cell 23, left → cell 13).
   - **The map** draws its four location markers; clicking the garden marker jumped to `ROOM_P06_Garden`.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings. The room check is identical to WP-020's (69 and 53 rooms, 0 bad).
   - The other checks match the prior run but for the usual per-run random keys (the drawbridge's crest, Ewan's `CurrentQuestion`).
   - Fork commit [`9a0897017d`](https://github.com/barefootbetters/scummvm/commit/9a0897017d) (9 files staged by name) is pushed.

**Deviations and gaps:**

- **The cell tables are a transcription of binary code constants.** The maze
  layout is written as a run of immediate stores in `enter`, not a data table
  the art or the sound index supplies — so there is no independent source for
  it. The tables were derived **mechanically from the decompile** (one parse
  emits both the reference's Python and the engine's C++), so the two carry the
  same constants rather than a hand-copy; their meaning (the index formula and
  the bit per direction) is read from the trace, independent of the values.
- **The idle mutterings do not play live.** The tick requests `Hedge_Maze.240A_`
  by its id, but the fork's `Sound::play` is exact-match and does not do the
  original's speaker resolution, so the rare muttering is a no-op (the voice
  clip ships as `…240A_1_SHAGGY`). The deterministic check confirms the lines
  ship, by prefix. The unicycle sfx and the music resolve exactly and play.
- **The navigation is modelled, not frame-exact.** The original re-enters the
  room on each move; the fork updates the position and redraws the cell. The
  deterministic surface the check proves (the classes, the clips, the moves,
  the tables, the starts, the map) is independent of that; the live run
  confirms the ride and the map jump.

**Found on the way:**

- **Read the string bytes, not Ghidra's labels.** The music and the nine
  unicycle clips are `Hedge_Maze.Music` and `Hedge_Maze.Unicycle_*` with a
  **dot**; Ghidra's symbol labels (`s_Hedge_Maze_Unicycle_*`) underscore them.
  A first pass used the underscored labels, and the reference and the engine
  agreed on "found 0" while both were wrong — caught by reading the disc's
  sound index, which has the dotted names. The string bytes (`StrAt`) confirmed
  the dots.
- **`240A2_` is referenced but not shipped; `240A3_` ships but is not
  referenced** — the exe's idle list names `240A_`, `240A1_`, `240A2_`, while
  the disc has `240A_`, `240A1_`, `240A3_`.
- **The two titles share no maze room**, as with KST: Showdown has neither
  class.

---

## Goal

Port the first of Phantom's group-7 rooms, `ROOM_Hedge_Maze` and
`ROOM_Maze_Map`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 7, the maze). Until now they had the base class: the maze drew, but no
walls or passages, no riding between cells, and the map's markers did nothing.

## Background

The maze ([scooby-exe](../formats/scooby-exe.md#phantoms-hedge-maze-and-maze-map-wp-074)):
the gang rides a unicycle through a grid of hedge cells, each cell opening on
some of its four sides; the maze map item shows a close-up whose markers jump
straight to the garden, the well, the centre or below the balcony.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`HedgeMazeRoom`:** the per-level cell tables and the start cells; the four
  direction buttons drawn as passages or walls; riding to the adjacent cell
  with the unicycle clips; the exit to the garden.
- **`MazeMapRoom`:** the four location markers and their jumps.
- **A `script` level 3 check** against an independent reference, on both titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes, the clips, the moves;
   - the per-level cell and path tables, the patch cell;
   - the start cells and the garden-exit cells;
   - the map's markers.

   Showdown prints that it has neither room.
2. [x] Live, in Phantom: the maze draws its cell; riding a direction moves to
   the adjacent cell; the map's garden marker jumps to the garden.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual random keys. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-hedge-maze-and-maze-map-wp-074):
  the maze.
