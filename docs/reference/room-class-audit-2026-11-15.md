---
layout: default
title: "Room class audit — Showdown — 2026-11-15"
---

# Room class audit — Showdown — 2026-11-15

> Which rooms in Showdown's room factory have a class of their own in the original, and which of those the fork has ported. Written after WP-045 and the hotel depth fix.

---

## Method

1. **The original's classes.** For each room name in the factory (`0x42E0E0`), find the constructor it calls and the vtable that constructor installs. Then list the vtable slots (`+0x04` to `+0x3C`) that differ from the base room's (`0x45E5FC`). A room whose vtable is the base's has nothing to port.
2. **Their size.** Count the decompiled lines of each overridden slot, as a rough measure of the work.
3. **The fork's classes.** Read each of the fork's room-class factories (`buildRoomClass` and the `create…Room` functions), resolving their constants and arrays to room names.
4. **Compare.** A room with a class in the original that no factory in the fork answers is unported.

## Result

The factory names 70 rooms:
- **60 have a class of their own,** found through their constructor. Nine of the 60 share one class, the artifact puzzle's.
- **For nine more** the map found no constructor (Boot Hill 1 to 3, Chase B1 to B6). The fork ports those rooms' classes (WP-040, WP-035).
- **One, ROOM_P40_Chase_Start,** has the base class.

So 69 rooms have a class. The fork's factories answer 51 of them: 42 by name, and the nine artifact rooms by their prefix. **Eighteen rooms with a class in the original have none in the fork.** They are 14 classes, since ROOM_SB1 to ROOM_SB5 share one. Two of the 14 are developer rooms.

| Room | Constructor, vtable | Slots it overrides | Lines | What it names |
|---|---|---|---|---|
| ROOM_P12_Saloon | `0x414430`, `0x45E990` | tick, reset, enter, leave, event, claim, save, load, exit, idle | 1276 | `OBJ_INV_NICKEL`, `OBJ_INV_PUMP_HANDLE`; `ArtieChained`, `ArtieMasked`, `BullRidden`, `ShaggyPiano`; ROOM_Artie, ROOM_P05_Stage, ROOM_P11_Street3, ROOM_P17_Hotel_Hall, ROOM_Suspect_Chooser |
| ROOM_P32_Pie_Noon | `0x41B840`, `0x45EC3C` | tick, enter, leave, claim | 602 | ROOM_P12_Saloon |
| ROOM_P09_Railroad_Station | `0x4207C0`, `0x45EE28` | tick, reset, enter, event, claim, arrive | 511 | `OBJ_INV_DENTURES`; ROOM_Gummy, ROOM_P04_Street2, ROOM_Suspect_Chooser |
| ROOM_Gummy | `0x40FC40`, `0x45E7D0` | tick, enter, event, claim | 499 | ROOM_P09_Railroad_Station, ROOM_Quit |
| ROOM_P08_Post_Office | `0x413930`, `0x45E950` | tick, reset, enter, event, claim, save, load, exit, arrive | 401 | `OBJ_INV_LANTERN`; `OldRoomName`; ROOM_P03_Street1, ROOM_P14_Tunnel_Dark, ROOM_P18_Tunnel_Lit |
| ROOM_P02_Sheriffs_Office | `0x4163A0`, `0x45E9D0` | tick, enter, event, claim, exit, opening | 373 | `OBJ_INV_BLANKET`, `OBJ_INV_OILCAN`; ROOM_P07_Jail |
| ROOM_Sheriff | `0x416E20`, `0x45EA10` | tick, reset, enter, leave, claim, save, load | 368 | `CurrentQuestion`; ROOM_P03_Street1 |
| ROOM_P30_Horseshoe_Corral | `0x41DA10`, `0x45ED00` | enter, leave, claim | 249 | ROOM_P28_Chase_B5 |
| ROOM_P19_Back_Alley | `0x40E7A0`, `0x45E70C` | tick, enter, claim, exit | 201 | ROOM_Open_Safe, ROOM_P15_General_Store_Interior, ROOM_P16_Bank_Vault |
| ROOM_Artie | `0x40D4E0`, `0x45E68C` | tick, reset, enter, claim, save, load | 159 | `ChainsLocked`; ROOM_P12_Saloon |
| ROOM_SB1 to ROOM_SB5 | `0x42A340`, `0x45F1A8` | tick, reset, enter, leave, claim | 155 | ROOM_P16_Bank_Vault |
| ROOM_Ghost_Spot | `0x4222E0`, `0x45EEAC` | tick, enter, claim | 128 | — |
| ROOM_Cheat | `0x404490`, `0x45E490` | enter, leave | 85 | `ROOM_NAME` (a developer room) |
| ROOM_Test_Scroll | `0x419250`, `0x45EAD4` | tick, enter, claim | 83 | — (a developer room) |

**What the fork has for these now.** The fork mentions most of them only in four places:
- the toolbar's hidden list (WP-025);
- the music and opening table, `room_setup` (WP-029);
- as another room's exit or its walk-in (Street 1's class also sends the Sheriff's introduction to ROOM_Sheriff);
- for ROOM_Ghost_Spot, the ghost's arrival in `RoomScript` (WP-021).

None has its own tick, events or claims.

**The back alley** builds its hotspots 1 and 3 as WP-044 found the jail's: with `0x408DC0(object, 1, -1)`, the default path's call. A port can leave them to the default path.

## Suggested order

Story rooms first, in the order the story reaches them, then the set pieces they lead to:

1. **ROOM_P02_Sheriffs_Office:** the way into the jail. It names the blanket and the oil can.
2. **ROOM_P19_Back_Alley:** between the vault, the open safe and the General Store.
3. **ROOM_P08_Post_Office:** the lantern and the two tunnels.
4. **ROOM_P09_Railroad_Station** and **ROOM_Gummy:** the dentures, and Gummy's room.
5. **ROOM_P12_Saloon** and **ROOM_Artie:** the largest class. Its story values are `ArtieChained`, `ArtieMasked`, `BullRidden` and `ShaggyPiano`. It may split into two WPs.
6. **ROOM_Sheriff:** `CurrentQuestion`.
7. **ROOM_SB1 to ROOM_SB5:** one class, back to the bank vault.
8. **ROOM_P30_Horseshoe_Corral** and **ROOM_P32_Pie_Noon:** the corral leads to Chase B5, and Pie Noon to the saloon.
9. **ROOM_Ghost_Spot.**

ROOM_Cheat and ROOM_Test_Scroll are developer rooms: no exit object in object.ini leads to either.

## Not covered

- **Phantom of the Knight.** The Ghidra project holds Showdown's `Scooby.exe` only. Phantom's audit, from an import of its own, is [room-class-audit-phantom-2026-11-16](room-class-audit-phantom-2026-11-16.md).
- **Slot by slot in the ported classes.** This audit checks that a ported room has a class at all. It doesn't check that the class overrides every slot the original's does.
