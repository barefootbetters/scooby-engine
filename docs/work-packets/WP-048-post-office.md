---
layout: default
title: "WP-048: Showdown's post office"
---

# WP-048: Showdown's post office: the lantern down the hole (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-045 ✅ (the lantern), WP-041 ✅ (the tunnels), WP-023 ✅ (inventory), WP-021 ✅ (clickables)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-048-2026-11-15](../reference/pre-flight-WP-048-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp049_ref.py`: WP-047's, plus the post office, written from the trace before the engine ran. It reads the placements, step counts, clickable states, `priority=` and rollover keys from the art and object.ini, and which scenes and sounds are on the disc from the sound archives' indexes. It never runs the engine. At `script` level 3 the chase check now logs 155 lines on Showdown: the earlier 149 and 6 for the post office. The reference prints the same 155, none different, on the first run. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**Entry.** From Street 1 without the lantern, Velma, Shaggy and Scooby are hidden; with it, no one is. From the dark tunnel, Fred, Daphne and Velma are hidden and hotspots 2 and 3 lose their open hand. From the lit tunnel after that, `OldRoomName` keeps it so. The dark hole is shown and the lit one hidden, the other way round with `TunnelLit`. Hotspots 2 and 3 are clickables at depth -1. The openings are `160A_` while `MoaningActive`, `160D_` from the dark tunnel, and none from the lit tunnel.<br>**The hotspots.** Hotspot 3 gives its three lines in turn. Hotspot 2 gives `160X4_` on its C. All held.<br>**The hole in the dark.** The gang is kept with `160AA_`, `160B2_`, `160B3_`, then `160AA_` again, or `160B_` once Artie has been met. Shaggy and Scooby are kept with one of `380A_` and `380A1_`. With the lantern used the default handler takes it, as it does the way to Street 1.<br>**The lantern.** With the arrow the class doesn't take the click on the hole; with the lantern it does. On tick 1 the lantern is used up, the arrow is back, `TunnelLit` is set and `160C_` plays, held. On tick 2 Fred tosses it (16 steps, `Fred.Tosses.Lantern`). On tick 47, his step 15, the dark hole is hidden, the lit one shown, and the room goes to the lit tunnel.<br>**The keys.** `OldRoomName` is saved and read back. A reset sets it to ROOM_P03_Street1, and a missing key reads empty. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from a profile in the original's form:<br>**The hole in the dark** gave `160AA_`, and the gang stayed.<br>**The lantern.** Taken from the toolbar and clicked on the hole, it gave `160C_`. Fred tossed it, and the gang came down in the lit tunnel. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit and click checks have nothing stuck. Phantom's earlier checks are identical to WP-047's run. Showdown's differ only in the profile check, by the post office's new `OldRoomName` key and the randomly drawn sheriff clue. The original's save has no `OldRoomName`, so it is imported empty, as the original's loader leaves it. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`e1339c631a`](https://github.com/barefootbetters/scummvm/commit/e1339c631a) (5 files staged by name) is pushed. |

**Deviations and gaps:**

- **The lantern on the hole acts on the press,** like every click in the fork; the original reads the release and the hole's clicked flag in its tick. The class takes the click before the inventory, so no "used on nothing" line plays, as in the original, where the room's tick runs before the game's update.

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

1. [x] Showdown matches an independent reference line for line:
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
2. [x] Live, in Showdown, from a profile in the original's form: the hole
   in the dark, then the lantern on it, Fred, and the lit tunnel.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-post-office-wp-048): the post
  office.
