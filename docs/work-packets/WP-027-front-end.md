---
layout: default
title: "WP-027: Room classes and the front end"
---

# WP-027: Room classes, and the title, menu, level select and quit screen (Gen 1)

**Status:** ✅ Done (2026-11-14)
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-022 ✅ (movies), WP-023 ✅ (the toolbar's quit button), WP-025 ✅ (menus hide the toolbar), WP-026 ✅ (the profile's level)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-027-2026-11-14](../reference/pre-flight-WP-027-2026-11-14.md)

---

## Result (2026-11-14)

The reference is `wp027_ref.py`, written from the trace. It reads the art and the sound indexes through the repo's probes, and never runs the engine. At `script` level 3 the engine drives the front end through its own room classes and logs 15 lines; the reference prints the same 15 on each title, none different.

| Exit criterion | Result |
|---|---|
| 1. Against the reference | ✅ On both titles:<br>**The title.** It asks for movie 27, then 28, then shows. Layer 0 goes −638, −636, … 0, then −1278 on tick 321; on tick 324 the game goes to Sign In.<br>**The buttons.** Each of the four main-menu and three level-select buttons is hit by its polygon, has 3 steps, and shows frames 0, 1 and 2 at rest, under the mouse and pressed. Options and New Mystery bring the narrator's lines. The level buttons sound Shaggy's `Level_Select` lines.<br>**Where they go.** Play goes back to the game room, or to Sign In from the title. Options, New Mystery and Quit go to their rooms. The level buttons set levels 0–2, then movie 1 and `ROOM_P01_Town_Center` (Phantom: `ROOM_P01_Drawbridge`).<br>**The quit screen.** The eyes look at No (step 1) or Yes (step 2), and Scooby says `Quit_Screen.No_1_SCOOBY` or `…Yes_1_SCOOBY`; then back to the menu, or quit. |
| 2. Live, Showdown | ✅ The input played through `test_script`, minimized.<br>**The title.** A cold start played movies 27 and 28 (3.7 s and 10.0 s), then the panning title. A click skipped it to Sign In.<br>**The menus.** From Town Center, the toolbar's quit button opened the main menu. Options lit up and the narrator explained it, once. Quit opened the quit screen, where No lit up. Scooby's No line ended back in the menu, and Play returned to Town Center.<br>**The level select.** Spooky played movie 1 (55.9 s) and opened Town Center. |
| 3. Build and diff | ✅ Scooby-only build: 0 errors, 0 warnings. The exit, click, inventory, hint and snack checks are identical to WP-026's run, and the room check is identical to WP-020's (69 and 53 rooms). The profile check matches its reference, with the level now written as `Difficulty`. Fork commit [`714e4cd7b7`](https://github.com/barefootbetters/scummvm/commit/714e4cd7b7) stages its 13 files by name, inside `engines/scooby/`, and is pushed. |

**Deviations and gaps:**

- **The buttons keep step 0's shape.** Their hover and pressed steps carry no polygon. Taken literally, the original's hit test would lose a button the tick it lights up, and the first live run did just that: the button flickered, and the narrator restarted every tick. What keeps the original steady isn't traced.
- **Clicks act on the mouse button going down,** as the rest of the fork does; the original acts on its release. A button shows its pressed frame while the button is held.
- **Sign In, Options and Credits** run the base class: the title and New Mystery lead to a Sign In room that does nothing yet.
- **The title's skip key** is a stand-in: Escape, Space or a click for the original's input slot 5.

---

## Goal

Give rooms their own classes, as the original's factory does, and use them
for the front end:
- the game starts at the title;
- the toolbar's quit button opens the main menu;
- the level select starts a game;
- the quit screen quits.

## Background

Until now every room ran the base room class. The original builds one
object per room name, and 47 rooms (Showdown) have a class of their own.
The front end's classes are the menus, built from one kind of button
(details in
[scooby-exe](../formats/scooby-exe.md#room-classes-and-the-front-end-wp-027)):

- **The title** plays title movies 27 and 28, then pans its background for
  nine seconds and goes to Sign In.
- **The main menu** has Play, Options, New Mystery and Quit; the narrator
  explains Options and New Mystery.
- **The level select's** three buttons set the level, then play movie 1
  and open the story's first room.
- **The quit screen** asks Yes or No; Scooby answers, then the game quits
  or goes back.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`RoomClass`.** Entry, tick, click, skip and busy hooks after the base
  behaviour. There is one object per room name, built on first use and kept
  for the game.
- **`ButtonRoom`**, the menus' button: state as its step, a hover sound,
  rollover and click callbacks.
- **The four rooms:** the Title Screen, Main Menu, Difficulty and Quit.
  - The game starts at the title.
  - The title movies can be skipped once seen.
  - The level goes into the profile as `Difficulty`.
- **A `script` level 3 check:** the title's steps, pan and countdown, every
  menu button, and both quit answers.

**Out of scope:**

- **Sign In, Options and Credits**, and the new-game setup (`0x42DBC0`: the
  villain, the clues). The title and New Mystery still lead to the Sign In
  room, which runs the base class for now.
- **The other classes' hooks:** events (`+0x14`), placements (`+0x18`), and
  their profile keys (`+0x1C`/`+0x20`).
- **The story rooms.**

## Exit criteria

1. [x] Both discs match an independent reference line for line:
   - the title's movie steps, its pan and its countdown;
   - every main-menu and level-select button's hit test, steps, frames,
     sound and destination;
   - the quit screen's eyes, lines and endings.
2. [x] Live, in Showdown:
   - the title after its movies;
   - the toolbar's quit button opening the menu, the menu's Options
     narration, Quit, No and Play back to the game;
   - a level starting movie 1 and Town Center.
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): room classes, the button and the
  four rooms.
