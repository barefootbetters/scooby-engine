---
layout: default
title: "WP-092: Phantom's well and its Jester"
---

# WP-092: Phantom's well and its Jester (Gen 1)

**Status:** ✅ Done (2026-11-27). Fork PR [barefootbetters/scummvm#16](https://github.com/barefootbetters/scummvm/pull/16) merged on 2026-11-27 (merge commit `8410401169`).
**Phase:** 5 (a gap found while checking WP-075 after WP-090)
**Depends on:** WP-061 ✅ (the room of doors and its Jester, `JesterControl`), WP-072 ✅ (the royal gallery, which keeps him the same way), WP-075 ✅ (the well)
**Companion EC:** none (inline checklist under Exit criteria)
**Pre-flight:** [pre-flight-WP-092-2026-11-27](../reference/pre-flight-WP-092-2026-11-27.md). Required: the packet modifies `engines/terraglyph/**`.
**Targets generation(s):** Gen 1, *Phantom of the Knight* only. Showdown has no such room.
**Estimated effort:** An hour

---

## Goal

Give `ROOM_P22_Well_In_Maze` its Jester. WP-075 left a member of the well's
class at `+0xB8` unported and called it a ball-game sub-object. The decompile
shows it is the shared Jester controller.

## Background

[WP-075](WP-075-maze-interior.md) ported the well and noted, under Deviations,
that "the well holds a ball-game sub-object (`+0xb8`) the fork does not
reproduce". After [WP-090](WP-090-kst-serving.md) found that a similar note
hid an unplayable room, Jeff asked for this one to be looked at next.

The decompile of Phantom's `Scooby.exe` (SHA-256 `619EA687…AF807ED`, Ghidra
12.1.4 headless, scratch project) shows the following (source):

- **The constructor** (`0x42C740`) builds `+0xB8` with `0x4122D0`. That is the
  Jester's constructor, the one the room of doors (`+0xBC`), the royal
  gallery and the balcony's door use.
- **The entry** (`0x42C810`): a queued return bounces to the gallery through
  movie 54 or 57, unless the full bottle has been used. Otherwise it runs the
  base entry, then the Jester's entry (`0x412B80`), then sets `WellVisited`.
- **The tick** (`0x42C7F0`): the base tick, then the Jester's tick
  (`0x4122E0`).
- **The Jester is placed in the well** (`OBJ_JESTER_B`, at 563, 393).

[scooby-exe](../formats/scooby-exe.md#phantoms-room-of-doors-its-jester-and-phantoms-clues-wp-061)
already named the well as one of the four classes that call his tick.

The fork's `WellInMazeRoom` had no Jester, an empty tick and no click
handler, so the Jester stood in the well doing nothing:

- **In every visit,** a click on him gave nothing. Elsewhere it gives his
  introduction or a line, or, after the crest puzzle, the return through
  movie 54 or 57.
- **Once the full bottle has been used,** finding the yellow ball here no
  longer bounces the gang to the gallery. In the original he then takes it
  in the well and, with all three balls found, gives his clue and sends the
  gang to the suspect board. The fork did neither here.

The other Jester rooms still did all of this, so it was a missing behaviour,
not a soft-lock.

## Scope

**In scope:**

1. **Fork, `maze_interior_rooms.{h,cpp}`:** a `JesterControl` member on
   `WellInMazeRoom`. Its entry runs on a visit that doesn't bounce, its tick
   runs after the room's, clicks are passed to it, and `isBusy()` holds input
   while he gives his clue or his thanks, as the gallery does.
2. **Fork, `maze_interior_check.cpp`:** three lines for the well's Jester: a
   click with no ball found; the yellow ball with the full bottle used,
   through the clue to the suspect board; the bounce with no bottle.
3. **Docs:** this packet; the well's section in
   [scooby-exe](../formats/scooby-exe.md#phantoms-maze-interior--the-centre-the-fountain-and-the-well-wp-075);
   a pointer in WP-075; the index row.

**Out of scope:** the Jester's own logic (WP-061's `JesterControl`, unchanged),
and the checks that end a visit without `roomLeft()` (see WP-090).

## Exit criteria

1. [x] **Self-test.** The three new lines match expectations written from
   the trace before the run. The rest of the self-test matches the
   `d18cb66884` baseline except the per-run random keys. The build has no
   new warnings.
2. [x] **Live (session).** In the well, the Jester answers a click.
3. [x] **Process.** A fork PR against `scooby-engine` is open (merged later
   the same day), and each claim here carries its evidence label.

## Result

Every claim is Gen 1, Phantom. Evidence labels: **source** (the decompile),
**self-test**, **log** (the engine's debug log of a live run), **live —
session** (a scripted run this session drove). Nothing here is **live —
Jeff**.

**The port (source).** On `wp-092-well-jester` (`b6c6319dfc`),
`WellInMazeRoom` keeps a `JesterControl` at `+0xB8`, as the gallery keeps one
at `+0xC8`:

- `enter()` runs his entry after the bounce check (only on a visit that
  doesn't bounce), then sets `WellVisited`;
- `tick()` runs his tick;
- `click()` passes the sprite to him;
- `isBusy()` holds input while he gives his clue and his thanks.

**Self-test (self-test).** Three lines were added to the maze interior
check. Their expected text was written from the trace and the shared
controller before the build ran:

- **No ball found:** he is present, and a click gives one of his five lines.
- **The yellow ball shown with the full bottle used:** the return is
  queued, and the well is entered again without bouncing. He plays
  `ANIM_JESTER_BTAKES_YELLOW` and `YellowBallTaken` is set. Then come
  `Global.Jester.Clue_` and `Global.Thank_You_`, the clue is his, and the
  gang goes to `ROOM_Suspect_Chooser`, the same sequence the room of doors'
  check gives.
- **The yellow ball shown with no full bottle:** the visit bounces to
  `ROOM_P07_Royal_Gallery` through movie 57, he takes nothing, and input
  isn't held.

All three match. The first run printed the untouched flag as an empty string
where the expectation had "No"; the check now prints the flag as 0/1, and the
second run matches line for line. The rest of the self-test matches the
`d18cb66884` baseline, built from `C:\dev\scummvm`, with two exceptions:

- the per-run random keys (the drawbridge's flags, Ewan's question);
- the arena pile check's level-0 line, which printed `to -` in the baseline
  run only. That line waits on the pile's click clip (`isClickablePlaying`),
  and the baseline run shared the machine with this one. The new build, the
  WP-090 build and the `1c02ca7ecd` baseline all reach `ROOM_Brad_SPOOKY`. It
  is a pre-existing, timing-sensitive check, unrelated to the well.

Both runs show the same 18 runtime warnings, which are pre-existing (see
WP-090).

**Build (log).** Terraglyph only, in the fork worktree. Neither
`maze_interior_rooms.cpp` nor `maze_interior_check.cpp` raises a warning.

**Live (live — session, with log).** The run used
`start_room=ROOM_P22_Well_In_Maze` and a click at (585, 230) on the Jester:

- **This build:** `click at 585,230 on 5 OBJ_JESTER_B`, then `scene
  Global.1010J1_ starts`, then `JESTER says Global.1010J1_1_JESTER`.
- **`d18cb66884` (unchanged):** the same click lands on `OBJ_JESTER_B` and
  nothing follows.

The clue path wasn't driven live: it needs the full bottle used and all
three balls, which the self-test sets up directly.

## Deliverables

- Fork: `wp-092-well-jester`, PR [barefootbetters/scummvm#16](https://github.com/barefootbetters/scummvm/pull/16) (`b6c6319dfc`), merged on
  2026-11-27 as `8410401169`; the fork worktree is removed, and `C:\dev\scummvm`
  was rebuilt from it. Staged by name: `maze_interior_rooms.{h,cpp}` and
  `maze_interior_check.cpp`.
- Docs: this packet, the well's section in scooby-exe, the pointer in
  WP-075, and the index row.
- Local only: the decompile dump, the self-test logs and the screenshots.

## Notes

- **The bounce guard.** On a visit that bounces to the gallery, the original
  skips the Jester's entry but its tick still runs. The fork rebuilds the
  room's characters on every load, so the controller would then hold the
  previous visit's character until the bounce lands. The port runs his tick
  only on visits where his entry ran. This is a deviation, and harmless: a
  bouncing visit ends at once.
- WP-075's other "modelled, not frame-exact" item, the fountain's piranha,
  hasn't been rechecked against the decompile. It is the next candidate.
