---
layout: default
title: "Room class audit — Phantom — 2026-11-16"
---

# Room class audit — Phantom — 2026-11-16

> Which rooms in Phantom of the Knight's room factory have a class of their own in the original, and which of those the fork has ported. The companion of [Showdown's audit](room-class-audit-2026-11-15.md), written after WP-056.

---

## Method

As [Showdown's](room-class-audit-2026-11-15.md#method), on Phantom's `Scooby.exe` (SHA-256 `619EA687…07ED`):

1. **The original's classes.** The factory is Phantom's game vtable `+0x14`, `0x42ED60`. For each room name it compares (`0x433360`), find the constructor it calls after the allocation, following the jumps of branches that share one, and the vtable that constructor installs. Then list the slots (`+0x04` to `+0x3C`) that differ from the base room's. Phantom's base room is Showdown's: its constructor `0x40B0F0` installs `0x45E5FC`.
2. **Their size.** Count the decompiled lines of each overridden slot. Phantom's `Scooby.exe` was imported and analyzed in a scratch Ghidra project outside the repo.
3. **The fork's classes.** Read each of the fork's room-class factories and resolve their constants to room names.
4. **Compare.** A room with a class in the original that no factory in the fork answers is unported.

"What it names" lists, from the overridden slots' decompiles, the toolbar items (`OBJ_INV_*`), the camel-case strings (most are the class's profile keys), and the other rooms.

## Result

The factory names all 53 of Phantom's rooms, and every name resolves to a constructor:
- **52 have a class of their own.** Two classes are shared: ROOM_P20_Kings_Armory with its slide, and Brad's three levels.
- **One, ROOM_P26_Castle_Balcony,** has a class whose slots are all the base room's: nothing to port.

The fork's factories answer **10** of the 52 by name: the title, the menus, Sign In, Options, Credits, the suspect chooser, Big Head and the ghost spot. No room-class factory written for Showdown answers a Phantom room: the two titles share no room names beyond those ten. **42 rooms with a class in the original have none in the fork.** They are 39 classes; one, ROOM_Cheat, is a developer room.

| Room | Constructor, vtable | Slots it overrides | Lines | What it names |
|---|---|---|---|---|
| ROOM_P30_WFR | `0x41BEA0`, `0x45EE7C` | tick, enter, leave, claim, exit | 1022 | ROOM_P24_Wizards_Bedroom |
| ROOM_Hedge_Maze | `0x42AA90`, `0x45F3C4` | tick, enter, leave, claim, exit | 912 | `OBJ_INV_MAZE_MAP`; ROOM_Maze_Map, ROOM_P06_Garden, ROOM_P23_Maze_Center, ROOM_P27_Below_Balcony |
| ROOM_P31_KST | `0x419700`, `0x45EDEC` | tick, enter, leave, claim | 671 | ROOM_P12_Dining_Room |
| ROOM_P17_Kitchen_Storage | `0x4139A0`, `0x45E994` | tick, reset, enter, leave, event, claim, save, load | 668 | `OBJ_INV_SCREWDRIVER`, `OBJ_INV_SHIELD`; `DoorClicked` |
| ROOM_P14_Arena2 | `0x40D790`, `0x45E6CC` | tick, reset, enter, leave, event, claim, +28, idle, scene | 637 | `OBJ_INV_MIRROR`, `OBJ_INV_SHIELD`; ROOM_Brad_SPOOKIER, ROOM_Brad_SPOOKTACULAR, ROOM_Brad_SPOOKY, ROOM_P09_Arena1, ROOM_P10_Throne_Room, ROOM_Suspect_Chooser |
| ROOM_P01_Drawbridge | `0x426730`, `0x45F214` | tick, reset, enter, event, claim, save, load, exit, +28 | 534 | `OBJ_INV_1428_SIGN`; `PuzzleDone`; ROOM_P04_Town |
| ROOM_P13_Kitchen | `0x412C90`, `0x45E954` | tick, reset, enter, leave, event, claim, save, load, exit | 478 | `OBJ_INV_BOTTLE_EMPTY`, `OBJ_INV_BOTTLE_FULL`, `OBJ_INV_MIRROR`, `OBJ_INV_SCREWDRIVER`; `EwanIntro`; ROOM_Ewan, ROOM_P12_Dining_Room, ROOM_P17_Kitchen_Storage, ROOM_Suspect_Chooser |
| ROOM_Wizards_Skull | `0x42D7B0`, `0x45F4C4` | tick, reset, enter, leave, event, claim, save, load | 463 | `IntroDone`; ROOM_P08_Magic_Mirror_Room |
| ROOM_Ewan | `0x4109D0`, `0x45E890` | tick, reset, enter, leave, claim, save, load | 430 | `CurrentQuestion`; ROOM_P13_Kitchen |
| ROOM_P11_Room_Of_Doors | `0x415720`, `0x45EA9C` | tick, reset, enter, leave, claim, save, load, exit, idle | 423 | `OBJ_INV_DUSTER`; `JesterIntro`, `ThroneScene`; ROOM_P04_Town, ROOM_P10_Throne_Room, ROOM_P12_Dining_Room, ROOM_P13_Kitchen, ROOM_P20_Kings_Armory, ROOM_P20_Kings_Armory_Slide |
| ROOM_Maria | `0x428770`, `0x45F2C0` | tick, enter, claim | 392 | ROOM_P12_Dining_Room |
| ROOM_P07_Royal_Gallery | `0x416240`, `0x45EADC` | tick, reset, enter, event, claim, exit | 355 | `OBJ_INV_BALL_RED`, `OBJ_INV_MIRROR`; ROOM_P08_Magic_Mirror_Room, ROOM_P12_Dining_Room |
| ROOM_P12_Dining_Room | `0x40FD00`, `0x45E810` | tick, reset, enter, event, claim, save, load, +28, idle | 340 | `OBJ_INV_BURGER`; `MariaMoviePlayed`; ROOM_Maria, ROOM_Suspect_Chooser |
| ROOM_Brad_SPOOKY, ROOM_Brad_SPOOKIER and ROOM_Brad_SPOOKTACULAR | `0x41E9E0`, `0x45EF50` | tick, reset, enter, leave, claim | 335 | ROOM_P14_Arena2 |
| ROOM_P44_Fountain_Closeup | `0x429740`, `0x45F304` | tick, reset, enter, leave, event, claim | 320 | `OBJ_INV_BURGER`, `OBJ_INV_TOKENS`; ROOM_P23_Maze_Center |
| ROOM_P23_Maze_Center | `0x42A090`, `0x45F344` | tick, reset, enter, leave, event, claim, save, load, exit, opening | 281 | `OBJ_INV_RUSTY_SHEARS`, `OBJ_INV_TOKENS`; ROOM_Hedge_Maze, ROOM_P06_Garden, ROOM_P27_Below_Balcony |
| ROOM_P05_Gardeners_House | `0x411BF0`, `0x45E914` | reset, enter, event, claim, arrive | 259 | ROOM_Big_Head, ROOM_Garden_Plaque, ROOM_P04_Town, ROOM_P06_Garden |
| ROOM_P03_Souvenir_Shop | `0x416FE0`, `0x45EB9C` | tick, reset, enter, leave, event, claim, save, load | 247 | `OBJ_INV_BOTTLE_EMPTY`, `OBJ_INV_TOKENS`; `IntroDone`; ROOM_P04_Town |
| ROOM_P20_Kings_Armory and ROOM_P20_Kings_Armory_Slide | `0x40EBC0`, `0x45E710` | tick, reset, enter, leave, event, claim, save, load | 245 | `OBJ_INV_BOTTLE_FULL`, `OBJ_INV_DUSTER`; `IntroDone` |
| ROOM_P10_Throne_Room | `0x417A90`, `0x45EC1C` | tick, reset, enter, event, claim, save, load, opening | 229 | `OBJ_INV_DUSTER`, `OBJ_INV_RUBY`; `JaneMoviePlayed`; ROOM_P09_Arena1, ROOM_P11_Room_Of_Doors, ROOM_P14_Arena2 |
| ROOM_P27_Below_Balcony | `0x40F220`, `0x45E750` | tick, reset, event, claim, save, load | 206 | `OBJ_INV_SHARP_SHEARS`; `PlayBallScene`, `ShowBall`, `VineClicks` |
| ROOM_P25_Wizards_Library | `0x42D1F0`, `0x45F484` | reset, enter, event, claim | 202 | `OBJ_INV_SPELL_BOOK`; ROOM_Big_Head, ROOM_Wizards_Skull |
| ROOM_P22_Well_In_Maze | `0x42C740`, `0x45F404` | tick, reset, enter, event, claim | 193 | `OBJ_INV_BALL_YELLOW`, `OBJ_INV_BOTTLE_FULL`, `OBJ_INV_ROPE`; ROOM_P07_Royal_Gallery |
| ROOM_P24_Wizards_Bedroom | `0x42CCF0`, `0x45F444` | tick, reset, enter, claim | 179 | `OBJ_INV_MAZE_MAP`; ROOM_P30_WFR, ROOM_Suspect_Chooser |
| ROOM_Garden_Plaque | `0x40F840`, `0x45E7D0` | tick, enter, event, claim | 177 | ROOM_P05_Gardeners_House |
| ROOM_P18_Storage | `0x417650`, `0x45EBDC` | tick, reset, enter, leave, event, claim | 147 | `OBJ_INV_ROPE` |
| ROOM_P08_Magic_Mirror_Room | `0x414EC0`, `0x45E9DC` | reset, enter, event, claim | 142 | — |
| ROOM_P28_Veranda | `0x4183B0`, `0x45ECDC` | reset, event, save, load, arrive | 136 | `WellClicks`; ROOM_Big_Head |
| ROOM_P29_Princess_Bedroom | `0x415350`, `0x45EA5C` | tick, enter, leave, event, claim | 133 | `OBJ_INV_SPELL_BOOK` |
| ROOM_P27A_Below_Balcony_Door | `0x4106B0`, `0x45E850` | tick, reset, enter, event, claim | 109 | `OBJ_INV_BALL_BLUE`, `OBJ_INV_BOTTLE_FULL`; ROOM_P07_Royal_Gallery |
| ROOM_P19_Secret_Passage2 | `0x416D10`, `0x45EB5C` | reset, enter, event, claim, save, load | 102 | `GargoyleFlameActive` |
| ROOM_P09_Arena1 | `0x40D4E0`, `0x45E68C` | reset, enter, leave, event | 93 | `OBJ_INV_RUSTY_SHEARS`, `OBJ_INV_SHARP_SHEARS`; ROOM_P10_Throne_Room, ROOM_P14_Arena2 |
| ROOM_Cheat | `0x404490`, `0x45E490` | enter, leave | 83 | `ROOM_NAME` (a developer room) |
| ROOM_P06_Garden | `0x411A20`, `0x45E8D4` | enter, event, claim | 64 | ROOM_P05_Gardeners_House |
| ROOM_P04_Town | `0x4180F0`, `0x45EC5C` | enter | 62 | ROOM_P01_Drawbridge, ROOM_P03_Souvenir_Shop, ROOM_P05_Gardeners_House, ROOM_P11_Room_Of_Doors |
| ROOM_Maze_Map | `0x42A7D0`, `0x45F384` | enter, claim | 57 | — |
| ROOM_P16_Treasury | `0x4182E0`, `0x45EC9C` | tick | 19 | ROOM_Suspect_Chooser |
| ROOM_P15_Secret_Passage1 | `0x416C40`, `0x45EB1C` | enter | 18 | ROOM_P18_Storage, ROOM_P20_Kings_Armory_Slide |
| ROOM_P21_Mermaids_Cavern | `0x415280`, `0x45EA1C` | event | 15 | — |

The slots are named as in Showdown's audit; `+28`, `scene` and `setup` are the vtable's `+0x28`, `+0x38` and `+0x3C`.

## Suggested order

By the story's reach from ROOM_P01_Drawbridge, where a new game starts. The order follows the exits in `object.ini` and the rooms each class names; it isn't from a play-through.

1. **ROOM_P01_Drawbridge** and **ROOM_P04_Town:** the start, the 1428 sign and `PuzzleDone`, and the town's hub.
2. **ROOM_P03_Souvenir_Shop:** the tokens and the empty bottle.
3. **ROOM_P05_Gardeners_House, ROOM_P06_Garden** and **ROOM_Garden_Plaque.**
4. **ROOM_P11_Room_Of_Doors** and the rooms off it:
   - ROOM_P10_Throne_Room;
   - ROOM_P12_Dining_Room with ROOM_Maria;
   - ROOM_P13_Kitchen with ROOM_Ewan and ROOM_P17_Kitchen_Storage;
   - ROOM_P20_Kings_Armory with its slide.
5. **The arenas:** ROOM_P09_Arena1, ROOM_P14_Arena2 and Brad's class.
6. **The passages and the gallery:**
   - ROOM_P15_Secret_Passage1, ROOM_P19_Secret_Passage2 and ROOM_P18_Storage;
   - ROOM_P16_Treasury;
   - ROOM_P07_Royal_Gallery and ROOM_P08_Magic_Mirror_Room;
   - ROOM_P31_KST.
7. **The maze:**
   - ROOM_Hedge_Maze and ROOM_Maze_Map;
   - ROOM_P23_Maze_Center, ROOM_P44_Fountain_Closeup and ROOM_P22_Well_In_Maze;
   - ROOM_P27_Below_Balcony and its door, ROOM_P27A_Below_Balcony_Door.
8. **Upstairs:**
   - ROOM_Wizards_Skull and ROOM_P25_Wizards_Library;
   - ROOM_P29_Princess_Bedroom and ROOM_P21_Mermaids_Cavern;
   - ROOM_P24_Wizards_Bedroom and ROOM_P28_Veranda;
   - ROOM_P30_WFR, the largest class.

ROOM_Cheat is a developer room, as in Showdown.

## Not covered

- **Slot by slot in the ported classes.** The ten ported classes were traced in Showdown. Phantom's are the same code where a WP compared them (the ghost spot, WP-056), but this audit doesn't check the others slot by slot.
- **What Phantom's classes do.** The table measures them; it doesn't trace them.
