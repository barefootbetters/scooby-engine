---
layout: default
title: "WP-041: Showdown's tunnel"
---

# WP-041: Showdown's tunnel: the crate in the dark, and the lit way (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-040 ✅ (Boot Hill, where the lit tunnel leads), WP-023 ✅ (requires objects), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-041-2026-11-15](../reference/pre-flight-WP-041-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp041_ref.py`: WP-040's, plus the tunnel, written from the trace before the engine ran. It reads the crate and Shaggy's step counts from the art and whether the dark tunnel's opening has a first line from the sound archives' indexes, and never runs the engine. At `script` level 3 the chase check now logs 107 lines on Showdown, the earlier 103 and 4 for the tunnel; the reference prints the same 107, none different. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The dark tunnel.** The crate a requires object; the opening `Tunnel_Dark.170A_`; the way out says `170A2_`, `170A3_`, `170A2_`, not held, and the room never changes.<br>**The crate.** The first try: held, Shaggy's NO_PUSH_CRATE (78 steps) on tick 1 with `Shaggy.Cant.Push.Crate`, nothing hidden; input back on tick 235. The second: PUSH_CRATE (69 steps) with `Shaggy.Scooby.Push.Crate`, the crate and Scooby hidden; the post office on tick 208. A new visit starts with "can't" again.<br>**The lit tunnel.** The way to Boot Hill first says `Tunnel_Light.180A_` and marks it played; again, nothing. Going first by the way with no scene, the way to Boot Hill then says nothing. The key reads back, and a reset clears it. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**The dark tunnel.** The way out said `170A2_` and the gang stayed; the first crate click got Shaggy's "can't"; the second, Shaggy and Scooby pushed it, and the post office loaded.<br>**The lit tunnel.** The way to Boot Hill said `Tunnel_Light.180A_`, then Boot Hill 2 loaded. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings, on `783919255e`. Phantom's earlier checks are identical to WP-040's run; Showdown's differ only by the profile check's `BootHillCommentPlayed`, one key more each way. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`c883a8ebf5`](https://github.com/barefootbetters/scummvm/commit/c883a8ebf5) stages its 5 files by name and is pushed. |

**Deviations and gaps:**

- **Shaggy's last step is a sprite of the engine's own.** The original builds a sprite in layer 0 for it; the fork adds it with the engine's sprites. The room changes on the same tick either way.

---

## Goal

Make Showdown's two tunnel rooms play as the original does. Until now they
had the base class: the dark tunnel's way out simply worked, and its crate
did nothing.

## Background

The tunnel ([scooby-exe](../formats/scooby-exe.md#the-tunnel-wp-041)) has
two rooms:
- **The dark tunnel:** Shaggy and Scooby are trapped. The way out only
  says a line. The crate is the way through: Shaggy can't move it alone,
  but on the next try he and Scooby push it, and the gang comes out in
  the post office.
- **The lit tunnel:** its first way out keeps its scene. The way to Boot
  Hill has a comment, said only if it's the first way the gang takes.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`TunnelDarkRoom`:** the crate; the way out's lines; the two tries and
  the push; the post office.
- **`TunnelLitRoom`:** the first way out's scene, and
  `BootHillCommentPlayed`.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The post office,** ROOM_P08_Post_Office.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the classes;
   - the dark tunnel's crate and opening, and the way out's lines with
     the gang staying;
   - the crate's two tries, Shaggy's sequences and sounds, what hides,
     and the ticks to input coming back and to the post office, again
     on a new visit;
   - the lit tunnel's comment on the first way out only, either way
     round, and its key.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the dark tunnel's way out and the crate pushed on the second try,
     then the post office;
   - the lit tunnel's way to Boot Hill with its comment.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-tunnel-wp-041): the tunnel.
