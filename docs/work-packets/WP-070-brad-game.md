---
layout: default
title: "WP-070: Phantom's Brad game"
---

# WP-070: Phantom's Brad game: the armour pile, piece by piece (Gen 1)

**Status:** ✅ Done (2026-11-17)
**Phase:** 4 (game logic)
**Depends on:** WP-069 ✅ (the arena's pile leads here; his clue follows the win), WP-064 ✅ (a set piece's hidden cursor and timed way back), WP-057 ✅ (sprites' own updates), WP-039 ✅ (a drag)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Half a day
**Pre-flight:** [pre-flight-WP-070-2026-11-17](../reference/pre-flight-WP-070-2026-11-17.md)

---

## Result (2026-11-17)

The reference is `wp071_ref.py`: WP-069's, plus Brad's game, written from the trace before the engine ran. It reads the placements from the art and the way out from `object.ini`. It plays the game itself: springs, pushes, drags and flights, in single precision where the original stores a value. It never runs the engine. At `script` level 3 the chase check now has 8 Brad lines on Phantom (110 in all), and one on Showdown, which has no such rooms (227 in all).

The first run matched all 110 lines on Phantom and all 227 on Showdown, with no warnings.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ Phantom:<br>**The classes:** all three rooms get Brad's game.<br>**Placements:** 6, 8 and 10 pieces by level, each where it hangs, at its depth in the order, under the root, with the open hand. The body, heads and mouths are at -10, -9 and -8, the mouths stopped. Another level's game in a room builds none of its pieces.<br>**Links:** every piece's neighbours, in the order its list runs.<br>**Entry:** the order; each piece's way out, to a tenth of a degree, and its share; the introduction playing with the cursor hidden; the hour. With the introduction over, the cursor is back.<br>**Left alone,** nothing moves for 300 ticks. A click on a piece is the game's; on the body, not.<br>**The spring:** the next piece set 30 right of its place is at (28.62, 0.04) a tick later. Each neighbour is pushed to the hundredth, a rattle plays, and the pile settles in 21 ticks.<br>**Out of turn:** a piece is held at 20.03, and every fourth time the heads get excited. The complaints run 1, 2, 3, then 2, none while a line still plays; another piece starts over at 1. The heads calm 71 ticks on.<br>**The game:** each piece in turn is dragged out its way at 2 a tick until it breaks loose (24 to 35 ticks), then left to fly off the screen (19 to 28 ticks). After the last, `BradPuzzle` is set, input is held, the cursor is hidden, and the game returns to the arena 73 ticks later, at every level.<br>Showdown prints that it has no Brad game. |
| 2. Live, Phantom | ✅ Through `test_script`, minimized, at the easy level:<br>**The introduction** (about 7 s) and the cursor back.<br>**Six pulls,** with `down`, moves and `up`, each piece's way taken from the reference's own play. Every piece broke loose (61 to 63 out) and flew off in order. Then the game was won, it went back to the arena, and Brad gave his clue (`180B_`). |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit, click, inventory and hint checks have nothing stuck. The room check is identical to WP-020's (69 and 53 rooms). Showdown's other checks are identical to WP-069's run. Phantom's differ only in random keys: the drawbridge's, and Ewan's `CurrentQuestion`.<br>Fork commit [`9da0dba7e2`](https://github.com/barefootbetters/scummvm/commit/9da0dba7e2) (8 files staged by name) is pushed. |

**Deviations and gaps:**

- **The cursor's fades** (`0x435E80`, `0x435EF0`) are taken as hidden or shown; the fork has no fade, as in Maria's game ([WP-064](WP-064-maria-game.md)).
- **The rattle's play call** passes a second argument, 500, whose use wasn't traced; the fork plays the clip.
- **Arithmetic:** the original's floats pass through the x87's wider registers; the fork computes in doubles and stores floats. The check's tick counts and two-place positions match the reference.
- **The heads' excitement timer** (`+0x128`) isn't set by the class's reset or entry, and the base constructor wasn't traced for it. The fork starts it at 0, so it only reaches 0 again after a complaint.

**Found on the way:**

- **The pile can't be taken apart out of order:** a piece out of turn is held within 20 of its place, and the next one breaks only when pulled near its own way.
- **Pulling the right piece moves the others:** each pushes its neighbours by how far it is out. The original uses the x distance for both terms, so the push leans along the diagonal.
- **The ways are worked out again after each piece goes,** from where the rest are then, so the pull for a later piece depends on the earlier ones.
- **The sound names have dots** (`Brad.ARMOR_INTRO_1`); Ghidra's labels show underscores.

---

## Goal

Port Phantom's Brad game, the three rooms the arena's pile leads to by
level, split off from [WP-069](WP-069-arenas.md). Until now the rooms had
the base class: the armour sat still, and only their way out worked.

## Background

Brad's game ([scooby-exe](../formats/scooby-exe.md#phantoms-brad-game-wp-070)):
- **A pile of armour** on Brad, its pieces on springs, taken off one at a
  time in the level's order by dragging each out its way.
- **His complaints** when the wrong piece is tugged.
- **The win** sets `BradPuzzle`, which the arena reads for his clue.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`BradGameRoom`,** for the three rooms: the placements, the order and
  links, the pieces' own update, the complaints, the introduction, the
  rattles, the win and the hour.
- **A `script` level 3 check** against an independent reference, on both
  titles.

## Exit criteria

1. [x] Both titles match an independent reference line for line:
   - the classes, placements and links;
   - entry: the order, ways, shares, the introduction, the cursor;
   - the pile left alone; clicks;
   - the spring, the pushes and the rattle;
   - the complaints;
   - the game at each level, to the win and the way back.

   Showdown prints that it has no Brad game, as its reference does.
2. [x] Live, in Phantom: the game played through and won, and his clue.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged but for random keys. The fork diff stays
   inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md#phantoms-brad-game-wp-070):
  Brad's game.
