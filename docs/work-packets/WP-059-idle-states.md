---
layout: default
title: "WP-059: Characters' idles"
---

# WP-059: Characters' idles: blink, the two idles and the room's idle line (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-020 ✅ (characters), WP-024 ✅ (the speech lock), WP-057 ✅ (the drawbridge)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** A day
**Pre-flight:** [pre-flight-WP-059-2026-11-16](../reference/pre-flight-WP-059-2026-11-16.md)

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

1. [ ] Both titles match an independent reference line for line:
   - two rooms each, loaded as the base class: each character's cap and
     first countdown;
   - every state change over 1500 and 900 ticks, with its tick, sequence,
     mode, line and next countdown;
   - clicks with the arrow: the second idle, the room's line with the
     speech lock, a click while the lock is held, and characters with no
     idles or no line;
   - Phantom's drawbridge line, before and after the puzzle.
2. [ ] Live, through `test_script`, minimized, in each title: idles start on
   their own; a click plays the second idle or the room's line.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The room check is
   identical to WP-020's. The earlier script checks are identical to the
   fork's before this WP. The fork diff stays inside `engines/scooby/`,
   staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#characters-idles-wp-059): the idles,
  the idle line and both titles' overrides.
