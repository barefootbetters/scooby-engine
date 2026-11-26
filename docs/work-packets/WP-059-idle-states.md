---
layout: default
title: "WP-059: Characters' idles"
---

# WP-059: Characters' idles: blink, the two idles and the room's idle line (Gen 1)

**Status:** ✅ Done (2026-11-16)
**Phase:** 4 (game logic)
**Depends on:** WP-020 ✅ (characters), WP-024 ✅ (the speech lock), WP-057 ✅ (the drawbridge)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-059-2026-11-16](../reference/pre-flight-WP-059-2026-11-16.md)

---

## Result (2026-11-16)

The reference is `idle_ref.py`, written from the trace before the engine
ran.
- **What it reads:** the placements and each sequence's steps from the art,
  and which clips are on the disc from the sound archives' indexes. It never
  runs the engine.
- **How it draws:** it replays ScummVM's `RandomSource`, an xorshift, from
  the check's seed, so every draw lands where the engine's does.
- **The check:** `script` level 3. Two rooms per title, loaded as the base
  class, run for 1500 and 900 ticks with clicks at set ticks.
  - Showdown: the lit tunnel, whose room lines cover the whole gang, and
    Street 2, with Gummy and the donkey.
  - Phantom: the mermaids' cavern, and Arena 2, with both of Brad's sets.

The first run matched: 94 lines on Showdown and 93 on Phantom.

**Exit criteria:**

1. **Against the reference:** ✅ Both titles:
   - **Each character:** its cap (3600, Scooby 108, the narrator `0x2F7600`), its first countdown and the open hand.
   - **Every state change** with its tick, sequence, mode, line and next countdown: blinks, first idles with Velma's `P1` line, Scooby's missing BLINK and the donkey's, each stopped a tick, then back.
   - **Clicks:** the second idle, with Shaggy's `S1` line; the room's line with the speech lock (`P18_Tunnel_Lit.Idle.SCOOBY`, `P21_Mermaids_Cavern.Idle.…`); `Global.Idle.FRED` and `Global.Idle.VELMA` where the room has none; nothing for Gummy, the donkey or Brad, who have no line.
   - **The end:** each character's state and countdown, and the lock let go.
   - **Phantom's drawbridge:** `P01_Drawbridge.Idle.VELMA`, then `Global.Idle.VELMA` with the puzzle done. Fred gets `Global.Idle.FRED`. Showdown prints that it has no drawbridge.
2. **Live:** ✅ Through `test_script`, minimized:
   - **Showdown's lit tunnel:** Scooby's first idle and missing blink, and the others blinking, on their own. The open hand over Velma, Shaggy and Fred; a click on each played their second idle.
   - **Phantom's drawbridge:** five clicks on Velma. Two played her second idle. Three said `P01_Drawbridge.Idle.VELMA` with lip sync, each taking the speech lock and letting it go. Shaggy's first idle and the gang's blinks came on their own.
3. **Build and diff:** ✅ Scooby-only build: 0 errors, 0 warnings.
   - **The room check** is identical to WP-058's run (69 and 53 rooms, 0 bad), and so to WP-020's.
   - **Every script check line** before the idle check is identical to the fork's run before this WP: 1720 on Showdown and 1047 on Phantom. The exceptions are random values that differ between any two runs: Showdown's first imported clue, and the drawbridge's colours in Phantom's profile check.
   - **Fork commit** [`87ef076bd6`](https://github.com/barefootbetters/scummvm/commit/87ef076bd6) (11 files staged by name) is pushed.

**Deviations and gaps:**

- **The earlier checks run without idles,** as they run without the ghost.
  Their references don't have idles, which would move scenes and walks; the
  live game and the idle check have them.
- **The room's idle timer** restarts only for lines said with the speech
  lock. The original restarts it for every line said at once (`0x404DB0`). A
  scene restarts it every tick anyway, and restarting it on every line would
  move every other check's random draws.
- **Phantom's dining room `+0x28`** and the unicycle's open hand wait for
  their room classes.
- **A click** reaches the character on the next tick, as a clickable's does,
  and the cursor is read when the click comes, not in the update.

**Found on the way:**

- **The `Global.IdleN.` clips are never played.** `0x40CB50` builds
  `Global.Idle%d.<NAME>` with `0x431EB0`, which only joins strings. That
  name is never on the disc, so every character's fallback is
  `Global.Idle.<NAME>`. There are 17 such clips on Showdown and 13 on Phantom.
- **Scooby idles every three seconds** (`0x4091FF` caps him at 108 ticks).
  Showdown has no BLINK for him, so two times in three his IDLE_MASTER just
  starts again.
- **State 7 never changes the state** in the original (`0x405190` only sets
  the next one). The fork's `kStateStay` does; not changed here.

---

## Goal

Port the characters' idles to the fork, for both Gen 1 titles. Until now a
character stood in IDLE_MASTER forever:
- **Left alone,** a character blinks, or plays its first idle with its line.
  The original does this every 10–24 seconds; Scooby, every three.
- **Clicked with the arrow,** it plays its second idle, or says the room's
  idle line (room vtable `+0x28`).

## Background

[WP-057](WP-057-drawbridge.md) ported Phantom's drawbridge, whose class
changes Velma's idle line once the puzzle is done. The fork had no state 4 to
ask for it, in any room of either title. The character code
([scooby-exe](../formats/scooby-exe.md#characters-idles-wp-059)) is the
same in both titles, at the same addresses.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`Character`:** states 2–5, the countdown and its cap, a click while
  idle, `say` with the speech lock, Scooby busy in his second idle.
- **`RoomScript`:** the idle random source, the base idle line
  (`0x40CB50`), the hook for `+0x28`, a character's click.
- **`DrawbridgeRoom`:** its `+0x28` (`0x4272D0`).
- **The engine:** a click with the arrow reaches the character under it,
  and a character shows the open hand.
- **A `script` level 3 check** against an independent reference, on both
  titles.

**Out of scope:**

- **Phantom's dining room `+0x28`** (`0x410550`, Maria's lines). It belongs
  to that room's class, which is still in
  [Phantom's audit](../reference/room-class-audit-phantom-2026-11-16.md).
- **The unicycle's open hand,** cleared by a Phantom room class
  (`0x42B8B7`). It belongs with that class too.
- **The room's idle timer restarted by every line** (`0x404DB0`). The fork
  restarts it only for the lines said with the speech lock; a scene starts
  it again every tick it plays.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - two rooms each, loaded as the base class: each character's cap and
     first countdown;
   - every state change over 1500 and 900 ticks, with its tick, sequence,
     mode, line and next countdown;
   - clicks with the arrow: the second idle, the room's line with the
     speech lock, a click while the lock is held, and characters with no
     idles or no line;
   - Phantom's drawbridge line, before and after the puzzle.
2. [x] Live, through `test_script`, minimized, in each title: idles start on
   their own; a click plays the second idle or the room's line.
3. [x] Scooby-only build: 0 errors and 0 warnings. The room check is
   identical to WP-020's. The earlier script checks are identical to the
   fork's before this WP. The fork diff stays inside `engines/scooby/`,
   staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#characters-idles-wp-059): the idles,
  the idle line and both titles' overrides.
