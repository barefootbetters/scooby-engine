---
layout: default
title: "WP-022: Movies"
---

# WP-022: Movies through `Video::BinkDecoder` (Gen 1)

**Status:** 🚧 In progress
**Phase:** 3 (resource loading: video)
**Depends on:** WP-019 ✅ (sound), WP-020 ✅ (the exit transition, which names a movie)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half-day
**Pre-flight:** [pre-flight-WP-022-2026-11-14](../reference/pre-flight-WP-022-2026-11-14.md)

---

## Goal

Play the Gen 1 movies with ScummVM's own Bink decoder, and play an exit's
`movie=` between its walk-off and the next room, as the original does.

## Background

WP-020's exits log their `movie=` and go on. In `Scooby.exe`:

- **The request** (game vtable `+0x08`, `0x42DE10`). An exit's walk-off
  passes the movie id and the next room. An id outside 0–74 means no
  movie. Ids 0 and 25–28 are title movies, gated by `GBHTitleMovies` in
  `Scooby.ini`. Any other id plays every time. The first viewing can't be
  skipped unless `Settings` / `AbortMovies` in `Scooby.ini` is on; later
  viewings always can (`+0x290`, read through game vtable `+0x3C`).
- **The file** (`0x4362E0`, "Playing movie (%i)"). The name is
  `%sBK.%.3d`: movie 32 is `BK.032` in the game folder, tried on the hard
  disk and then the disc. The engine stops its sounds, clears the
  screen, and hands the file to the Bink manager (`0x4422F0`,
  `BinkOpen`).
- **Skipping.** While a movie plays, input slot 5 or 4, or either mouse
  button, stops it if it may be skipped (`0x4424F0`, `BinkClose`). The
  slots are the input layer's (DirectInput); which keys they hold was
  not traced.
- **Then** the next room loads.

The discs carry 42 movies (Showdown) and 56 (Phantom), all Bink
(`BIKi`), 640 × 480, at 8, 12 or 24 frames per second.

## Scope

**In scope (fork, `engines/scooby/` only):**

- `ScoobyEngine::playMovie(id)`: open `BK.NNN` with
  `Video::BinkDecoder`, decode to the screen's RGB565, play its sound on
  the mixer's SFX channel, and stop on its last frame, on quit, or on a
  skip.
- Skipping: Escape, Space or a mouse click, once the movie has been seen
  this session, or always with an `abort_movies` config key (the
  original's `AbortMovies`).
- An exit with `movie=` plays it after the walk-off, then loads the room.
  The engine's sounds stop first, as the original's do.
- A console command, `movie <id>`, and a `start_movie` config key, for
  testing.
- Checks: `script` level 3 decodes every movie to its last frame and logs
  its frame count, size and length, and the mean colour of its first,
  middle and last frames.
- A movie whose Bink header disagrees with its file size is refused
  before the decoder opens it.

**Out of scope:**

- The title movies (0, 25–28) and the title screen flow.
- `MovieHistory` in the save.
- The input slots 4 and 5: the fork's keys are a stand-in.

## Exit criteria

1. [ ] Every `BK.*` on both discs decodes to its last frame in the
   engine. Frame count, size and rate match `ffprobe`. The mean colour of
   the first, middle and last frames matches `ffmpeg`'s decode to within 2
   levels per channel.
2. [ ] Live, an exit with `movie=` plays the movie with its sound after
   the walk-off, then loads the room; the movie's length matches its frame
   count over its rate. A second viewing can be skipped, the first can't.
3. [ ] A missing or damaged movie file logs a warning and the room loads
   anyway.
4. [ ] Scooby-only build: 0 errors and 0 warnings. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [Integration §7](../02-SCUMMVM-INTEGRATION.md#7-video-playback-bink)
  implementation notes.
- [scooby-exe](../formats/scooby-exe.md): the movie functions.
