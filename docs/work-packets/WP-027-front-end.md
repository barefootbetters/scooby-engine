---
layout: default
title: "WP-027: Room classes and the front end"
---

# WP-027: Room classes, and the title, menu, level select and quit screen (Gen 1)

**Status:** 🚧 In progress
**Phase:** 4 (game logic: room classes)
**Depends on:** WP-022 ✅ (movies), WP-023 ✅ (the toolbar's quit button), WP-025 ✅ (menus hide the toolbar), WP-026 ✅ (the profile's level)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** Day
**Pre-flight:** [pre-flight-WP-027-2026-11-14](../reference/pre-flight-WP-027-2026-11-14.md)

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

1. [ ] Both discs match an independent reference line for line:
   - the title's movie steps, its pan and its countdown;
   - every main-menu and level-select button's hit test, steps, frames,
     sound and destination;
   - the quit screen's eyes, lines and endings.
2. [ ] Live, in Showdown:
   - the title after its movies;
   - the toolbar's quit button opening the menu, the menu's Options
     narration, Quit, No and Play back to the game;
   - a level starting movie 1 and Town Center.
3. [ ] Scooby-only build: 0 errors and 0 warnings. The earlier checks and
   the room check are unchanged. The fork diff stays inside
   `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine`.
- [scooby-exe](../formats/scooby-exe.md): room classes, the button and the
  four rooms.
