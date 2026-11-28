---
layout: default
title: "WP-090: Phantom's Knights of the Snack Table, the serving game"
---

# WP-090: Phantom's Knights of the Snack Table: the serving game (Gen 1)

**Status:** ✅ Done (2026-11-27). Fork PR [barefootbetters/scummvm#15](https://github.com/barefootbetters/scummvm/pull/15) is open.
**Phase:** 5 (a defect found in the Phantom closeout's live play)
**Depends on:** WP-055 ✅ (Pie Noon, the sibling class), WP-057 ✅ (a room's own `Room::Actor` sprites), WP-073 ✅ (the room's claim and entry)
**Companion EC:** none (inline checklist under Exit criteria)
**Pre-flight:** [pre-flight-WP-090-2026-11-27](../reference/pre-flight-WP-090-2026-11-27.md). Required: the packet modifies `engines/terraglyph/**`.
**Targets generation(s):** Gen 1, *Phantom of the Knight* only. Showdown has no such room.
**Estimated effort:** Half a day

---

## Goal

Make `ROOM_P31_KST` (Knights of the Snack Table) playable. Port the
original's serving game from the decompile of class `0x419700` and the
sprite classes it builds, and replace the placeholder that WP-073 left.

## Background

Jeff's live play of Phantom on 2026-11-27 found the room unplayable. Shaggy
stood at his post, no knights appeared, nothing answered the mouse, and the
counter read 13 at Spooky. The fork's `KstRoom` (`engines/terraglyph/kst_rooms.cpp`
at `1c02ca7ecd`) read neither the mouse nor clicks. Its tick spawned knights
on a timer, and each knight slid to a seat and served itself.
[WP-073](WP-073-kst.md) said so under Deviations: the serving loop was
"modelled from the trace, not simulated", and the three sub-controllers were
"not reproduced". Its self-test covered the setup only, so it passed.

WP-073 had also read the room's purpose from marker names, and that reading
was wrong. The decompile shows the room is a bartender game. `+0xE8` holds the
mugs the player has left (five less the difficulty), not knights still to
serve. The counter shows the snacks the player has. The room exits to the
dining room when the mugs run out, not when a quota is met. The three
"sub-controllers" are the lists of full mugs, empty mugs and mugs left. The
packet's brief carried WP-073's model, and the Result below says where the
code differs from it.

## Scope

**In scope:**

1. **Fork, `engines/terraglyph/kst_rooms.{h,cpp}`:** Shaggy (`0x4192F0`,
   update `0x419370`), the knights (`0x418CA0`, `0x418EE0`), the full and
   empty mugs (`0x418710`/`0x418860`, `0x4189B0`/`0x418B10`), the three lists,
   the room's tick (`0x419E40`), a round (`0x41A5C0`), the entry's counter,
   mugs and overlay depths (`0x419A80`), and the cursor rule.
2. **Fork, `room.{h,cpp}`:** `Room::Actor::actorPlays()`, so a class can hold
   a sprite's player while the room pauses, as the original holds the
   knights' and the mugs' players (vtable `+0x08`).
3. **Fork, `kst_check.cpp`:** play the game through the engine's tick with
   the mouse set directly and `rand()` pinned to 1, against an independent
   reference written from the trace.
4. **Docs:** [scooby-exe](../formats/scooby-exe.md#phantoms-knights-of-the-snack-table-the-serving-game-wp-090)
   gains the serving game, with a correction note on WP-073's section; this packet;
   the index row; a pointer in WP-073.

**Out of scope:**

- The sound pan by the knight's x (`0x435850`). The fork's `Sound` has no
  pan, so it belongs with the sound work, not this packet.
- WP-075's well ball game (`+0xB8`, "not reproduced") may be the same kind of
  gap. It is a follow-up for the Phantom closeout ([WP-087](WP-087-phantom-closeout.md)),
  not this packet.
- The checks that end a room visit without `roomLeft()`. They are pre-existing,
  and see Found on the way.

## Exit criteria

1. [x] **Live (session).** A run through `test_script` (`move`, `down`, `up`
   and screenshots) shows the following: knights arrive; the player serves
   them with the mouse; the mugs behave as the code says; the counter shows
   the snacks and the mugs on the counter count down; running out of mugs
   returns to `ROOM_P12_Dining_Room`.
   *The brief asked for "the counter shows the right quota and counts down,
   and meeting the quota returns to the dining room". The code has no quota,
   so this criterion is restated from the decompile (see Background).*
2. [x] **Self-test.** The KST lines match the reference line for line. The
   rest of the self-test matches the `1c02ca7ecd` baseline except the per-run
   random keys. The build of `engines/terraglyph/` has no new warnings.
3. [x] **Process.** The fork PR against `scooby-engine` is open, and this
   packet records each claim with its evidence label.

## Result (2026-11-27)

Every claim is Gen 1, Phantom. Evidence labels: **source** (the decompile),
**self-test**, **log** (the engine's debug log of a live run), **live —
session** (a scripted run this session drove, with screenshots). Nothing here
is **live — Jeff**. The screenshots, logs and the reference stay local, in
this session's scratchpad.

**Decompiler (source).** Ghidra isn't on PATH and `GHIDRA_HOME` isn't set.
decompdecomp's toolchain has Ghidra 12.1.4, at
`%LOCALAPPDATA%\decompnet\toolchains\ghidra`, and that copy runs headless
on Java 27.0.1. The session imported `Scooby.exe` (SHA-256 `619EA687…AF807ED`)
into a scratch project outside the repo and decompiled the room's functions,
vtables and constants with a small post-script.

**What the original does (source).** This is written up in full in
[scooby-exe](../formats/scooby-exe.md#phantoms-knights-of-the-snack-table-the-serving-game-wp-090).
In brief:

- Shaggy follows the mouse to the nearest of three benches, at most 10 a tick.
- A press within 10 of a bench fills a mug. The release slides it. Letting go
  while he is still filling also slides it, because the state falls through.
- A knight walks from the door toward the tap and takes a full mug within 5 of
  him. He drinks while it pushes him back at half his pace. At the door he
  drops an empty mug and either walks again (1 in 3) or leaves.
- The empty mug slides back. Shaggy catches it if he's free at that bench.
- Each of these costs a mug and restarts the round: a full mug past the door
  end, an empty mug off the tap end, or a knight reaching the tap.
- A round served gives a snack, and the next round has one knight more.
- The counter's cels are the snacks, each one back (`(d + 9) % 10`: cel 0
  draws a 1). That is why the old code's "2 to serve" drew "13".

**The port (source).** The fork branch is `wp-090-kst-serving`, commit
`a5829afe4e`, PR [#15](https://github.com/barefootbetters/scummvm/pull/15).
Every state, constant and sound name above is in `kst_rooms.cpp`, with the
address it came from. The lists keep the original's order (newest first), and
`rand()` draws are taken in the original's order.

**Self-test (self-test).** `kst_check.cpp` drives the engine's own tick with
`_mousePos` and `_mouseDown` set directly and the room's `rand()` pinned to 1.
The reference is `wp090_ref.py`, kept local. It was written from the decompile
notes, not from the C++. It reads the placements and the sequences' step
counts from `TGIFILE.ART` and the clip names from the sound indexes. It models
the original's tree walk: children by descending depth, a new child after
every child of at least its depth, and the next sibling read before a child is
walked. The 10 KST lines match it exactly, and checked:

- The markers, and the overlays at depths 200, 285 and 386.
- Entry: 5, 4 and 3 mugs by level, drawn at (410…550, 40) at depth 100.
  Shaggy's offset is 76, and the knights' reaches are 2.45, 2.445 and 2.495.
  The counter's cels are 9 9 for 0 snacks and 0 2 for 13.
- Shaggy walks to the bottom bench (`WALK_FORWARD`, tick 20, x 526) and back
  to the top (`WALK_AWAY`, tick 40, x 488).
- A round served at level 0:
  - the mug slides at tick 15, speed 4.42;
  - the knight takes it at tick 74 (x 152.85) and is at the door at tick 220;
  - the empty mug is caught at tick 320, and the round is served the same
    tick (snacks 1, cels 9 0, a 36-tick pause, `Correct2`).
- Mugs lost at level 2:
  - a mug slid down the middle bench breaks at x 21.52;
  - then a knight reaches the tap twice (x 412.55);
  - "again" after each loss rebuilds 2, 1 and 0 mugs, then the room moves to
    `ROOM_P12_Dining_Room` at tick 627.
- An uncaught empty mug falls at x 464.62 and breaks at y 259, costing a mug.
- The cursor is shown at y 100 and hidden at y 101.
- Every sound name the game plays is found in the indexes.

The rest of the self-test matched the `1c02ca7ecd` baseline built from
`C:\dev\scummvm`: 1815 check lines each. The only differences are the per-run
random keys (the drawbridge's flags, Ewan's `CurrentQuestion`). The runtime
warnings were identical in both runs; see Found on the way.

**Build (log).** Terraglyph-only, out of tree in the fork worktree: 0 errors
and 0 warnings.

**Live (live — session, with log).** All runs used `start_room=ROOM_P31_KST`,
a new game (1 snack, level 0), and the engine's `--debugflags=script,input` log.

- **Run 1 (unserved).** The opening's narrator line held the game until 13 s
  in. Then a knight walked in on the top bench and reached the tap after about
  5 s; the log shows `a mug lost, 4 left`. Screenshot e08 shows five mugs on
  the counter, the knight on the top bench and Shaggy at the tap.
- **Run 2 (served, then out of mugs).** The script moved Shaggy to the bottom
  bench and back (screenshot l02), then pressed and released on the top bench.
  The log reads:
  - `Shaggy slides a full mug down bench 0`, then `the knight on bench 0 takes
    a mug at x 263.1` (screenshots l04 and l05: the mug sliding, the knight
    drinking);
  - `drinks up at the door; the empty mug slides back` (l11);
  - `Shaggy catches the empty mug on bench 0`, then `round 1 served: 2 snacks`
    (l12: the counter reads 02, Shaggy's `SUCCESS`);
  - round 2's two knights walked in on benches 0 and 1 (l17).

  The script then let the mugs go, and the log counts `4 left` … `0 left`,
  then `out of mugs: to ROOM_P12_Dining_Room`, and the dining room loads
  (l30: Maria's dishes).
- **Run 3 (the two breaks).**
  - **A full mug past the door end.** A mug slid down the middle bench, which
    had no knight on it. The log reads `a full mug passes the door end of
    bench 1 and breaks` (b02: the mug at the door end; b03: gone), then `a mug
    lost, 4 left`.
  - **An empty mug off the tap end.** After serving the top bench, the script
    moved the mouse to the bottom bench. The log reads `an empty mug falls off
    the tap end of bench 0 and breaks` (b14: the empty at the tap, Shaggy
    away), then `3 left`.

  In b14 Shaggy stands at the middle bench, not the bottom one the script
  pointed to. The run doesn't log host mouse moves, so the cause is not
  verified; a stray host-mouse event is the likely one. The self-test and run
  2 both walked him to the bottom bench. Either way he had left the top bench,
  which is all this case needs.

**Deviations:**

- **No sound pan.** The original pans each knight's footsteps and gulp by
  his x (`0x435850`). The fork's `Sound` has no pan.
- **The intro hold.** The original holds while the room's scene string is set,
  or while the opening is pending, and then until the narrator's line ends.
  The port reads `RoomScript::isScenePlaying()`, `isOpeningDone()` and
  `Sound::isClipPlaying()`, the same conditions through the fork's own state.
- **The arm.** The original redraws each knight's arm at the body's step every
  frame (`0x419160`). The port does it after the knight's update and at each
  state change. The arm's player stays stopped, as in the original.
- **The toolbar.** `0x407CC0` at entry moves the toolbar away. The fork's
  set-piece framework already hides it (the log reads "toolbar hidden"), so
  the port doesn't repeat it.
- **Entry drops the last visit's sprites.** Some checks end a visit without
  `roomLeft()` (see Found on the way). The freshly loaded room holds none of
  those sprites, so `enter()` forgets them. Without that, the self-test
  crashed when it detached stale sprite indices.

**Found on the way:**

- **WP-073's model was wrong** in its serving loop, quota and counter, which
  it had read from marker names. A correction note now heads its scooby-exe
  section, and WP-073 points here.
- **The pause after a round outlives the visit.** `+0x1A4` (36 ticks) is set
  when a round is served and counted down by the tick. Neither the entry nor
  `0x41A5C0` clears it, so leaving the room within 36 ticks of a round and
  coming back starts the next visit held for the rest of the pause (source).
  The self-test meets this case: its "misses" line starts 35 ticks late, and
  the reference models it.
- **A new game starts with 1 snack** (`Inventory`, `_snacks = 1`), so the
  room's counter reads 01 on a first visit (live — session, screenshot e08).
- **Runtime warnings come from the checks, not the room (log).** In both the
  baseline and the new run, 15 "More than 3 objects…", 2 "Not enough
  character start positions…" and 1 "2 numbers…" warnings appear. They come
  from a self-test path that clears `_roomClass` without calling
  `roomLeft()`, after which KST's markers are claimed twice on the next
  visit. They are pre-existing and harmless. Making those checks call
  `roomLeft()` would be a small check-harness fix of its own.

## Deliverables

- Fork: `wp-090-kst-serving` (`a5829afe4e`), PR [barefootbetters/scummvm#15](https://github.com/barefootbetters/scummvm/pull/15).
  Staged by name: `kst_rooms.{h,cpp}`, `kst_check.cpp`, `room.{h,cpp}`.
- Docs: this packet, its pre-flight, the index row,
  [scooby-exe](../formats/scooby-exe.md#phantoms-knights-of-the-snack-table-the-serving-game-wp-090),
  and the pointer in WP-073.
- Local only: the scratch Ghidra project and decompile dumps, `wp090_ref.py`,
  the self-test and live logs, and the screenshots.

## Notes

- The Phantom closeout ([WP-087](WP-087-phantom-closeout.md)) should replay
  the room live once the fork PR is merged. This packet's live evidence is
  session-driven, not Jeff's.
- WP-075's well ball game (`+0xB8`, "not reproduced") is the next candidate
  for the same kind of check. Its decompile route is now known, and is the
  same as this packet's.
