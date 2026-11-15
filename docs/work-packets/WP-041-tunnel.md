---
layout: default
title: "WP-041: Showdown's tunnel"
---

# WP-041: Showdown's tunnel: the crate in the dark, and the lit way (Gen 1)

**Status:** 🔄 In progress
**Phase:** 4 (game logic)
**Depends on:** WP-040 ✅ (Boot Hill, where the lit tunnel leads), WP-023 ✅ (requires objects), WP-020 ✅ (exits)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-041-2026-11-15](../reference/pre-flight-WP-041-2026-11-15.md)

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

1. [ ] Showdown matches an independent reference line for line:
   - the classes;
   - the dark tunnel's crate and opening, and the way out's lines with
     the gang staying;
   - the crate's two tries, Shaggy's sequences and sounds, what hides,
     and the ticks to input coming back and to the post office, again
     on a new visit;
   - the lit tunnel's comment on the first way out only, either way
     round, and its key.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from profiles in the original's form:
   - the dark tunnel's way out and the crate pushed on the second try,
     then the post office;
   - the lit tunnel's way to Boot Hill with its comment.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-tunnel-wp-041): the tunnel.
