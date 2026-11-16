---
layout: default
title: "WP-048: Showdown's post office"
---

# WP-048: Showdown's post office: the lantern down the hole (Gen 1)

**Status:** 🚧 In Progress
**Phase:** 4 (game logic)
**Depends on:** WP-045 ✅ (the lantern), WP-041 ✅ (the tunnels), WP-023 ✅ (inventory), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-048-2026-11-15](../reference/pre-flight-WP-048-2026-11-15.md)

---

## Goal

Make Showdown's post office play as the original does. It is the third
room from the [room class audit](../reference/room-class-audit-2026-11-15.md).
Until now:
- the gang went down the hole in the dark;
- the lantern did nothing there;
- the room didn't know who had come up from the dark tunnel.

## Background

The post office ([scooby-exe](../formats/scooby-exe.md#the-post-office-wp-048)):
- **The hole in the floor:** it leads down to the tunnel, and the gang
  won't go down in the dark. Dropped on the hole, the lantern gets a
  scene, then Fred tosses it in, and the gang goes down to the lit tunnel.
- **Up from the dark tunnel:** Shaggy and Scooby arrive here on their own,
  through the crate.
- **The room come from** is saved as `OldRoomName`.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`PostOfficeRoom`:** the holes and `TunnelLit`; the lantern; the lines
  in the dark; who is here by the room come from; `OldRoomName`; the
  hotspots' lines; the openings.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

## Exit criteria

1. [ ] Showdown matches an independent reference line for line:
   - the class;
   - who is here from Street 1, with and without the lantern, from the
     dark tunnel, and from the lit tunnel after it; the holes with and
     without `TunnelLit`; the hotspots; the openings;
   - hotspot 3's lines in turn and hotspot 2's on its C;
   - the hole in the dark, with the whole gang and with only Shaggy and
     Scooby, and once the lantern is used;
   - the lantern on the hole, Fred, and the lit tunnel, with their ticks;
   - `OldRoomName` saved and read, and a new game's reset.

   Phantom prints that it has no chase, as its reference does.
2. [ ] Live, in Showdown, from a profile in the original's form: the hole
   in the dark, then the lantern on it, Fred, and the lit tunnel.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-post-office-wp-048): the post
  office.
