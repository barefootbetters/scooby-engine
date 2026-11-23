---
layout: default
title: "Engine screenshots (our engine running)"
---

# Engine screenshots — the TerraGlyph engine running

These are screen captures of **our `terraglyph` ScummVM engine actually running**
*Scooby-Doo! Showdown in Ghost Town* — not the original game. Each is the
engine's own 640×480 output: a decoded `TGIFILE.ART` background with the gang and
room objects composited as sprites, exactly as the engine draws them.

This covers the game's **story, location and chase rooms** — every playable
place in *Showdown*, captured straight from the running engine. Filenames use the
canonical `ROOM_*` IDs, so this gallery lines up with the
[`showdown-screens/`](../showdown-screens/index.md) reference library (and fills
the rooms that library left as gaps — the longplay never reached them, but our
engine renders them: `ROOM_P27_Chase_B4`, and the full `B3`/`B6` track-fork and
`Chase_Start` rooms). The engine's menu, suspect-chooser and artifact-overlay
screens aren't rooms, so they sit apart from the gallery.

> **Provenance — why these are our engine, not reference frames.** Unlike the
> `showdown-screens/` library (which is captures of the *original* retail game
> from a YouTube longplay, used as RE ground truth), every image here was
> produced by the engine itself and verified by eye before committing. Keep the
> two sets distinct: these are the port; those are the reference.

## How these were captured (2026-11-22)

Captured headlessly with the engine's built-in `test_script` harness
(see [02-SCUMMVM-INTEGRATION §9](../../../02-SCUMMVM-INTEGRATION.md#9-debug-channels)),
so no live mouse was needed:

- **Build:** the fork engine `barefootbetters/scummvm` (branch `scooby-engine`,
  commit `d1a26e7`), built on MSYS2 UCRT64.
- **Data:** a mounted *Showdown* disc (detected as `terraglyph:showdown`).
- **Method:** the engine was launched once per room with a game-domain config of
  `start_room=<ROOM>` plus `test_script=wait 6000; shot <ROOM>; quit`, which dumps
  the engine's screen surface to `test_shots/<ROOM>.bmp`. Each BMP was converted
  to PNG losslessly and checked by eye against the room before committing. No
  "Cannot go to" warning fired for any room in the set.

No image here was retouched, composited, or sourced from anything but the running
engine.

## Rooms

### Town & story (P01–P20)

| File | Room |
|---|---|
| `ROOM_P01_Town_Center.png` | Ghost Town hub — the gang, the POPULATION signpost |
| `ROOM_P02_Sheriffs_Office.png` | Sheriff's office |
| `ROOM_P03_Street1.png` | Street 1 — sheriff's office frontage |
| `ROOM_P04_Street2.png` | Street 2 — general-store frontage |
| `ROOM_P05_Stage.png` | The theatre stage |
| `ROOM_P06_Stage_Trapdoor.png` | The stage with the trapdoor |
| `ROOM_P07_Jail.png` | The jail |
| `ROOM_P08_Post_Office.png` | The post office |
| `ROOM_P09_Railroad_Station.png` | The R.R. depot |
| `ROOM_P10_Front_Of_General_Store.png` | Outside the general store |
| `ROOM_P11_Street3.png` | Street 3 — saloon / bank |
| `ROOM_P12_Saloon.png` | The saloon interior |
| `ROOM_P13_Bank.png` | The bank |
| `ROOM_P15_General_Store_Interior.png` | The general-store interior |
| `ROOM_P16_Bank_Vault.png` | The bank vault |
| `ROOM_P17_Hotel_Hall.png` | The hotel hall |
| `ROOM_P18_Tunnel_Lit.png` | The lit tunnel |
| `ROOM_P19_Back_Alley.png` | The back alley |
| `ROOM_P20_Hotel_Room.png` | The hotel room |

### Boot Hill (P21–P23)

| File | Room |
|---|---|
| `ROOM_P21_Boot_Hill1.png` | Boot Hill 1 |
| `ROOM_P22_Boot_Hill2.png` | Boot Hill 2 — the signpost |
| `ROOM_P23_Boot_Hill3.png` | Boot Hill 3 |

### Chase sequences

In chase order. The B-leg runs `Chase_Start` → `B1`–`B6`; the C-leg runs
`C1`–`C6`. Two of the B rooms are **track forks** where the rails split: `B3`
(the Dig Site fork) and `B6` (whose switch sends one track to `C4`, an oil-can
room that's easy to miss).

| File | Room |
|---|---|
| `ROOM_P40_Chase_Start.png` | Chase start — the locomotive at the depot |
| `ROOM_P24_Chase_B1.png` | Chase B1 — the runaway mine cart |
| `ROOM_P25_Chase_B2.png` | Chase B2 |
| `ROOM_P25A_Chase_B2_Closeup.png` | Chase B2 — character close-up |
| `ROOM_P26_Chase_B3.png` | Chase B3 — the Dig Site track fork |
| `ROOM_P27_Chase_B4.png` | Chase B4 — the canyon trestle |
| `ROOM_P28_Chase_B5.png` | Chase B5 — the ranch turn |
| `ROOM_P29_Chase_B6.png` | Chase B6 — the track-switch fork to C4 |
| `ROOM_P33_Chase_C1.png` | Chase C1 |
| `ROOM_P37_Chase_C2.png` | Chase C2 |
| `ROOM_P38_Chase_C3.png` | Chase C3 |
| `ROOM_P39_Chase_C4.png` | Chase C4 — the oil can on the track |
| `ROOM_P34_Chase_C5.png` | Chase C5 — the spiral butte |
| `ROOM_P35_Chase_C6.png` | Chase C6 |

### Minigames

| File | Room |
|---|---|
| `ROOM_P30_Horseshoe_Corral.png` | The horseshoe-toss minigame |
| `ROOM_P32_Pie_Noon.png` | Pie Noon — the town square |

### Other

| File | Room |
|---|---|
| `ROOM_Open_Safe.png` | The open safe |

## Title & menu screens

The engine also renders the game's front-end. These are UI screens, not rooms, so
they sit apart from the gallery above:

| File | Screen |
|---|---|
| `ROOM_Title_Screen.png` | The *Showdown in Ghost Town* title card |
| `ROOM_Main_Menu.png` | The main menu (New Mystery / Sound / Quit / Play) |

These feed the public [GitHub wiki Screenshots page](https://github.com/barefootbetters/terraglyph-engine/wiki/Screenshots).
