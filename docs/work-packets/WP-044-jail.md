---
layout: default
title: "WP-044: Showdown's jail"
---

# WP-044: Showdown's jail: the blanket, the bed and the hole under it (Gen 1)

**Status:** ✅ Done (2026-11-15)
**Phase:** 4 (game logic)
**Depends on:** WP-041 ✅ (the dark tunnel), WP-023 ✅ (inventory and requires objects), WP-021 ✅ (clickables), WP-020 ✅ (scenes)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-044-2026-11-15](../reference/pre-flight-WP-044-2026-11-15.md)

---

## Result (2026-11-15)

The reference is `wp044_ref.py`: WP-043's, plus the jail, written from the trace before the engine ran. It reads the following from the art, object.ini and the sound archives' indexes, and never runs the engine:
- the placements, step counts and clickable states;
- the `priority=` keys;
- whether each scene and sound is on the disc.

At `script` level 3 the chase check now logs 131 lines on Showdown: the earlier 122 and 9 for the jail.

The first run matched 130. The one difference was hotspot 3's depth: 0 in the reference, -1 in the engine. The trace bears out -1, since `0x40AD50` gives -1 for an object without `priority=`. It also showed that the class's claim of hotspots 2 and 4 had forced them to 0, and the reference had made the same mistake. With the claim dropped and the reference fixed, the second run matched all 131. On Phantom both print the one line saying there is no chase.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Showdown:<br>**The placements.** The blanket a requires object at depth 1, hidden once taken. The three hotspots clickables at depth -1, with the open hand. The hole and the stool at depths 0 and 500, hidden. No opening.<br>**The hotspots.** The door: `150X2_`, `150X23_`, `150X2_`. The window: `150X3_` on its B, nothing on C, D and A, then `150X3_` on B again. The bed's first click: `150X1_`. Every line held input.<br>**The blanket.** With an item, nothing happens. With the arrow, input is held. On tick 1 Shaggy plays TAKE_BLANKET (24 steps) and the blanket goes. On tick 73 it is in the toolbar, and `150C_` plays, held. Back again, the blanket stays gone.<br>**The bed.** On the second click its hit type goes to 0, its B loops, and input is held. Scooby plays BREAK_BED (22 steps) and asks for `Scooby_Breaks_Bed`, which isn't on the disc. On tick 67 the bed is gone, without its open hand. The hole and the stool show, and `150D_` plays, held.<br>**The drop.** After `150D_`, Shaggy plays LEAVE_JAIL (20 steps) at depth 501, in front of the stool at 500. Scooby is hidden, and `Scooby_Shaggy_Fall_In_Hole` isn't on the disc either. On his step 6 Shaggy is at 499. 60 ticks after he starts, the room goes to the dark tunnel, with Shaggy hidden. Entering the jail again goes straight there, on tick 1.<br>**The keys.** A new game saves `BedBroken=No`. Reading Yes shows the hole and the stool and starts `150D_` on tick 1, and Yes is saved again. A reset and a missing key both read 0.<br>**Leaving.** With the blanket clicked, it goes in the toolbar. With the bed clicked, `BedBroken` is set.<br>**The exit handler** keeps the gang in. It does nothing without the blanket, or while a scene plays. With the blanket in a slot and no scene, Shaggy plays LEAVE_JAIL, and the dark tunnel follows on tick 60. |
| 2. Live, Showdown | ✅ Through `test_script`, minimized, from profiles in the original's form:<br>**The cell.** The door said `150X2_` and the window `150X3_`. On the blanket's click Shaggy took it into the toolbar, with `150C_`. The bed's first click gave `150X1_`. On the second, Scooby broke the bed (ticks 1434 to 1501), and the hole and the stool showed. `150D_` ended on tick 1683; Shaggy started down the hole on the next tick, and on tick 1744 the gang was in the dark tunnel, with its opening `170A_`.<br>**A saved broken bed.** From `BedBroken=Yes` the hole and the stool were there at once. `150D_` played on tick 1, and the two dropped into the dark tunnel on tick 242. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. Phantom's earlier checks are identical to WP-043's run. Showdown's differ in two places. The profile check has the jail's new `BedBroken` key. Its sheriff's clue also differs, but that clue is drawn at random on every run. The room check is identical to WP-020's (69 and 53 rooms). Fork commit [`9cc65df856`](https://github.com/barefootbetters/scummvm/commit/9cc65df856) (5 files staged by name) is pushed. |

**Deviations and gaps:**

- **Entering again after the drop runs the base entry.** The original's entry (`0x413600`) sends the gang to the dark tunnel before the base entry. The fork's class comes after it, so the jail is set up (its characters and its music) for the one tick before the room changes.
- **Clicks act on the press,** like every click in the fork.
- **The hotel room's hotspots 2 and 4** (WP-042) are claimed the way the jail's were. They sit at depth 0, not the -1 the original gives them. That is left for its own fix.

---

## Goal

Make Showdown's jail cell play as the original does. Until now it had the
base class: the blanket couldn't be taken, the bed never broke, and the
gang had no way out of the cell.

## Background

The jail ([scooby-exe](../formats/scooby-exe.md#the-jail-wp-044)) locks
Shaggy and Scooby in a cell with no exit object:
- **The blanket:** clicked with the arrow, Shaggy takes it off the bunk
  and it goes in the toolbar.
- **The bed:** the first click gets a line; the second has Scooby break
  it, which uncovers a hole and a stool.
- **The hole:** after their scene, the two drop through it into the dark
  tunnel. Once they have, the jail leads straight back there.
- **The door and the window** have lines of their own.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`JailRoom`:** the blanket; the bed, the hole and the stool, saved as
  `BedBroken`; the drop into the dark tunnel; the door's and the
  window's lines; the room's leave and its exit handler.
- **A `script` level 3 check** against an independent reference, in the
  chase check.

**Out of scope:**

- **The Sheriff's office,** ROOM_P02_Sheriffs_Office, the way in.
- **The dark tunnel,** done in WP-041.

## Exit criteria

1. [x] Showdown matches an independent reference line for line:
   - the class;
   - the placements, with and without the blanket taken;
   - the door's lines in turn, the window's on its B, the bed's first
     click;
   - the blanket: not with an item; with the arrow, Shaggy, the toolbar
     and 150C_, with their ticks;
   - the bed: Scooby, the sound, the hole and the stool, 150D_, with their
     ticks;
   - the drop: Shaggy's depths by the stool, Scooby gone, the room, and
     the jail again;
   - `BedBroken` saved and read, and a new game's reset;
   - what leaving finishes, and the exit handler.

   Phantom prints that it has no chase, as its reference does.
2. [x] Live, in Showdown, from profiles in the original's form:
   - the door and the window, the blanket, the bed twice, 150D_ and the
     dark tunnel;
   - a saved broken bed: the hole at once, 150D_ and the dark tunnel.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#the-jail-wp-044): the jail.
