---
layout: default
title: "WP-075: Phantom's maze interior — the centre, the fountain and the well"
---

# WP-075: Phantom's maze interior — the centre, the fountain and the well (Gen 1)

**Status:** ✅ Done (2026-11-19)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-023 ✅ (the inventory), WP-057 ✅ (Phantom's new game and first room), WP-074 ✅ (the hedge maze and maze map — the hook these connect to)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-075-2026-11-19](../reference/pre-flight-WP-075-2026-11-19.md)

---

## Result (2026-11-19)

The reference is `wp075_ref.py`: WP-074's, plus the maze interior, written from
the trace before the engine ran. It reads the clips from the sound index. It
never runs the engine. At `script` level 3 the chase check now has nine
maze-interior lines on Phantom, and one on Showdown, which has none of the three
rooms. **Every line matched on both titles.**

`ROOM_P23_Maze_Center`, `ROOM_P44_Fountain_Closeup` and `ROOM_P22_Well_In_Maze`
are the audit's group-7 second packet, the maze interior (WP-074 landed the
entry pair). They are **one packet, not split**: the trace shows the centre and
the fountain are coupled (the fountain is a close-up reached only from the
centre, token-gated, and exits back to it) and the well is the most independent
(its own ball/rope/bottle interaction, out to the royal gallery), but all three
are the maze's interiors, delivered together as WP-074's pair was. The last
group-7 packet (`ROOM_P27_Below_Balcony` and its door) stays separate.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**The classes:** `ROOM_P23_Maze_Center` gets `MazeCenterRoom`, `ROOM_P44_Fountain_Closeup` gets `FountainCloseupRoom`, `ROOM_P22_Well_In_Maze` gets `WellInMazeRoom`.<br>**The clips (dotted, prefix for the voice lines):** the centre's water sfx (exact) at volume 90, the shears line (exact), and `Center_of_Maze.250B_`/`250X_`/`250X1_`/`250_`/`250C_` (prefix) found; the fountain's opening `Fountain.250D_`, its cycle, exit line, water, the doubled swim loop, the grab/lunge/eats found; the well's three lines found.<br>**The placements:** the centre's water (sprite, −1500), the shears (requires until taken), the token-gated way to the fountain; the fountain's piranha (idle/full), the tokens (requires), the exit, the grab; the well's yellow ball, the rope-gated climb.<br>**The state:** the centre's start flag from the garden (1) and the balcony (0), the `Entrances` save round-trip; the well's movies (ball 66/4, rope 59, return 54/57).<br>Showdown prints that it has no maze interior. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized:<br>**The centre** loads with the water sprite (`ANIM_P23_MAZE_CENTER_WATERA`, depth −1500) and music group 1; the hotspots, the shears, the token-gated `OBJ_P23_TO_P44` and the hedge-maze exits are all present.<br>**The fountain** plays its opening `Fountain.250D_` at tick 100, music group 1, with the piranha and the tokens placed.<br>**The well** sets `WellVisited` on entry (`well: …, visited`), music group 1, no opening, with the well, the Jester ball-target and the yellow ball present. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The room check is identical to WP-020's (69 and 53 rooms, 0 bad). The other checks match the prior run but for the usual per-run random keys (the imported clue name; the WP-069 arena pile's level-0 line, which is timing-sensitive and flips between runs). Fork commit [`d09a0a2af2`](https://github.com/barefootbetters/scummvm/commit/d09a0a2af2) (8 files staged by name) is pushed. |

**Deviations and gaps:**

- **The piranha eat and the well's ball-game are modelled, not frame-exact.**
  The fountain's tick runs a short lunge/eat/grab sequence that grants the
  tokens; the well holds a ball-game sub-object (`+0xb8`) the fork does not
  reproduce. The deterministic surface the check proves — the classes, the
  clips, the placements and their gating, the save key, the movies — is
  independent of that, and the live run confirms the rooms, the opening, the
  music and the `WellVisited` flag.
- **The numbered scene lines play through the scene player's resolution, not
  `Sound::play`.** They ship with a speaker suffix, so the check probes them by
  prefix; `findClip` is exact and would miss them (the WP-074 trap). Some
  referenced ids ship but go unreferenced by these rooms (`250X2_`, `250A_`,
  the well's `330_`), as `240A3_` did for the hedge maze.
- **The item-use paths are proven deterministically, not live.** Feeding the
  piranha the burger, the rope on the well and the yellow ball are exercised by
  the check (the event and claim logic across inventory states); the live run,
  which did not set up the inventory, confirms reachability, the placements, the
  opening and the music, as WP-074's did.

**Found on the way:**

- **The opening is the fountain's, not the centre's.** The audit tagged
  `ROOM_P23_Maze_Center` with "opening", but the constructor's 4th argument is
  the empty string for the centre (and the well) and `Fountain.250D_` for the
  fountain; the engine's own `room_setup` table already had it right. The live
  run plays `Fountain.250D_` on entering the fountain and nothing on the centre.
- **The clip-name trap recurs**, and is closed the same way: read the string
  bytes and the disc sound index, probe the voice lines by prefix. The centre's
  scene lines, the fountain's and the well's are all dotted.
- **A second independent trace agrees.** Another session traced all three rooms
  in Ghidra independently; its reads match on every clip name, field offset and
  the split decision — the WP-073/074 anti-shared-misreading move at the session
  level, on top of the engine == reference match and the disc probe.

---

## Goal

Port the second of Phantom's group-7 rooms, `ROOM_P23_Maze_Center`,
`ROOM_P44_Fountain_Closeup` and `ROOM_P22_Well_In_Maze`
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 7, the maze). Until now they had the base class: the rooms drew, but the
water did not babble, the piranha did not guard the tokens, and the well did
nothing.

## Background

The maze interior
([scooby-exe](../formats/scooby-exe.md#phantoms-maze-interior--the-centre-the-fountain-and-the-well-wp-075)):
inside the hedge maze (WP-074) the gang reaches the centre, the fountain
close-up off it, and the well. The centre is the hub — its water babbles, the
rusty shears lie there to take, and the way to the fountain opens until the
tokens are grabbed. The fountain's piranha guards the tokens: fed the burger it
eats, and Shaggy grabs them. The well links back to the royal gallery and sets
`WellVisited`.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`MazeCenterRoom`:** the water ambience, the rusty-shears take, the
  token-gated fountain exit, the hotspot lines, the `Entrances` key, and the
  hedge-maze start flag from the garden/balcony.
- **`FountainCloseupRoom`:** the opening, the piranha, the token grab, the
  cycling fountain lines, the exit back to the centre.
- **`WellInMazeRoom`:** the yellow ball, the rope-gated climb, the well lines,
  `WellVisited`, and the return to the royal gallery.
- **A `script` level 3 check** against an independent reference, on both titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes, the clips (dotted, prefix for the voice lines);
   - the placements and their gating, the save key, the movies.

   Showdown prints that it has none of the three rooms.
2. [x] Live, in Phantom: each room is reached and draws its placements; the
   fountain plays its opening; the well sets `WellVisited`.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual random keys. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine` ([`d09a0a2af2`](https://github.com/barefootbetters/scummvm/commit/d09a0a2af2)).
- [scooby-exe](../formats/scooby-exe.md#phantoms-maze-interior--the-centre-the-fountain-and-the-well-wp-075):
  the maze interior.
