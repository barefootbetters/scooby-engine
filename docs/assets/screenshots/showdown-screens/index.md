---
layout: default
title: "Showdown Reference Screenshots"
---

# Showdown reference screenshot library

Visual ground truth for the WP-002 *TGIFILE.ART* decoder and the Phase 3
scripted-room reimplementation. One clean stationary frame per distinct
room/scene in *Scooby-Doo! Showdown in Ghost Town* (TLC, 2000), captured
from a YouTube longplay.

Captured per [WP-009](../../../work-packets/WP-009-reference-screenshots.md).
Consumed by [EC-002 pre-flight](../../../execution-checklists/EC-002-probe-art-harness.md)
(decoder visual comparison) and the [WP-001 Ghidra session](../../../work-packets/WP-001-ghidra-session.md)
(scripted-room ground truth for `*_Room.cpp` reimplementation).

## Copyright

These are screen captures taken from publicly available YouTube footage
of gameplay. They are used here for **reverse-engineering reference and
documentation purposes only** — fair use in the context of a ScummVM
engine implementation project, consistent with how ScummVM documents
all supported games. No files extracted directly from the game disc are
stored in this repository.

## Naming convention

File naming is **strictly canonical-first**:

- Canonical IDs use the WP-008 `destinationroom=` values verbatim, e.g.
  `ROOM_P21_Boot_Hill1.png`, `ROOM_P12_Saloon.png`, `ROOM_Main_Menu.png`.
  Source of truth: `tools/samples/asset-catalog.json` `rooms` map
  (gitignored, regenerable per [WP-008 §Notes](../../../work-packets/WP-008-object-ini-catalog.md#notes)).
- If a captured frame can't be confidently canonicalized, save as
  `UNMATCHED_<descriptive-slug>.png` and set Match Status: `Unmatched`
  in the row's table cell, with justification in Notes.
- Character sprite captures (Daphne idle, Scooby walk, etc.) are named
  `OBJ_<NAME>.png` and live under the "Character sprites" section
  below — needed by WP-002's first-decode pass (`entry[0]` is
  `OBJ_DAPHNE_A`).

## Capture rules (binary)

- No transitions (fade, pan, cut) — wait for the room to fully render
  and the camera to settle.
- No motion blur or animation mid-frame.
- Player character allowed in frame but not blocking major background
  geometry.
- UI minimized where possible; if unavoidable, must not obscure key
  background geometry.
- Minimum source quality: 720p. No compression artifacts that obscure
  shapes or colors.
- Cropping allowed ONLY to remove black borders / letterboxing — never
  crop scene content.
- Full-size PNGs committed as-is (typically 1280×720). The gallery
  embeds them at `width="320"` for page weight; the underlying PNG is
  always full resolution.

Once a capture is taken, replace the `*(pending capture)*` cell with:

```markdown
<a href="ROOM_P21_Boot_Hill1.png"><img src="ROOM_P21_Boot_Hill1.png" width="320" alt="ROOM_P21_Boot_Hill1"></a>
```

and fill in the row's Timestamp, Match Status, and Notes columns.

---

## Source video

Single-source YouTube longplay for all captures below:

- **URL:** *(fill in when capture session begins)*
- **Channel / uploader:** *(fill in)*
- **Recorded:** *(fill in)*

Per-row `Source Video` column defaults to this global URL when blank.
If a second longplay is needed (e.g. for a chase sequence the first one
skips), add a second URL block here and link explicitly in affected
rows (e.g. `[YT2](url)`).

---

## Provenance schema

Every gallery row uses this 6-column schema per WP-009 §Deliverables:

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|

- **Match Status** ∈ {`Canonical`, `Unmatched`, `Uncertain`}
  - `Canonical` — filename is an exact WP-008 catalog ID
  - `Unmatched` — `UNMATCHED_`-prefixed filename; justify in Notes
  - `Uncertain` — canonical filename with a capture-to-ID caveat
- **Gap rows** — for canonical IDs not captured in the longplay, leave
  Preview / Timestamp blank, set Match Status: `—`, and use Notes for
  one of: `Not reached in longplay` / `Not observable in source video` /
  `Uncertain match`.

---

## Town & story rooms (P01–P20)

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(pending capture)* | `ROOM_P01_Town_Center` | | | | scripted — no TGIFILE.ART entry |
| *(pending capture)* | `ROOM_P02_Sheriffs_Office` | | | | |
| *(pending capture)* | `ROOM_P03_Street1` | | | | |
| *(pending capture)* | `ROOM_P04_Street2` | | | | |
| *(pending capture)* | `ROOM_P05_Stage` | | | | |
| *(pending capture)* | `ROOM_P06_Stage_Trapdoor` | | | | |
| *(pending capture)* | `ROOM_P07_Jail` | | | | |
| *(pending capture)* | `ROOM_P08_Post_Office` | | | | |
| *(pending capture)* | `ROOM_P09_Railroad_Station` | | | | |
| *(pending capture)* | `ROOM_P10_Front_Of_General_Store` | | | | |
| *(pending capture)* | `ROOM_P11_Street3` | | | | |
| *(pending capture)* | `ROOM_P12_Saloon` | | | | scripted — no TGIFILE.ART entry |
| *(pending capture)* | `ROOM_P13_Bank` | | | | |
| *(pending capture)* | `ROOM_P15_General_Store_Interior` | | | | |
| *(pending capture)* | `ROOM_P16_Bank_Vault` | | | | |
| *(pending capture)* | `ROOM_P17_Hotel_Hall` | | | | |
| *(pending capture)* | `ROOM_P18_Tunnel_Lit` | | | | |
| *(pending capture)* | `ROOM_P19_Back_Alley` | | | | |
| *(pending capture)* | `ROOM_P20_Hotel_Room` | | | | |

## Boot Hill (P21–P23)

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(pending capture)* | `ROOM_P21_Boot_Hill1` | | | | |
| *(pending capture)* | `ROOM_P22_Boot_Hill2` | | | | |
| *(pending capture)* | `ROOM_P23_Boot_Hill3` | | | | |

## Chase sequences (P24–P28, P33–P39)

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(pending capture)* | `ROOM_P24_Chase_B1` | | | | |
| *(pending capture)* | `ROOM_P25_Chase_B2` | | | | |
| *(pending capture)* | `ROOM_P25A_Chase_B2_Closeup` | | | | |
| *(pending capture)* | `ROOM_P27_Chase_B4` | | | | |
| *(pending capture)* | `ROOM_P28_Chase_B5` | | | | |
| *(pending capture)* | `ROOM_P33_Chase_C1` | | | | |
| *(pending capture)* | `ROOM_P34_Chase_C5` | | | | |
| *(pending capture)* | `ROOM_P35_Chase_C6` | | | | |
| *(pending capture)* | `ROOM_P37_Chase_C2` | | | | |
| *(pending capture)* | `ROOM_P38_Chase_C3` | | | | |
| *(pending capture)* | `ROOM_P39_Chase_C4` | | | | |

## Minigames

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(pending capture)* | `ROOM_P30_Horseshoe_Corral` | | | | scripted — `Horseshoe_Corral_Room.cpp` |
| *(pending capture)* | `ROOM_P32_Pie_Noon` | | | | scripted — `Pie_Noon_Room.cpp` |

## Engine / menu rooms

| Preview | Room ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(pending capture)* | `ROOM_Main_Menu` | | | | scripted — no TGIFILE.ART entry |
| *(pending capture)* | `ROOM_Open_Safe` | | | | |

## Character sprites (WP-002 first-decode reference)

`entry[0]` of TGIFILE.ART is `OBJ_DAPHNE_A` — a character sprite, not a
background. At least one clean Daphne capture (idle or walk-cycle) is
needed so WP-002 has a visual comparison target for its first decode
pass. Other character sprites are optional but useful.

| Preview | Object ID | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(pending capture)* | `OBJ_DAPHNE_A` | | | | TGIFILE.ART `entry[0]` — first-decode target |

## Unmatched captures

Add rows here for any `UNMATCHED_*.png` files committed. Each row gets
the same 6-column schema as the canonical tables above; Match Status is
`Unmatched`, and Notes carries the justification (why no canonical ID
applies — frame is between rooms, room not in WP-008 catalog, etc.).

| Preview | Filename | Source Video | Timestamp | Match Status | Notes |
|---|---|---|---|---|---|
| *(none yet)* | | | | | |

---

## Source-of-truth note

The 37 room IDs above were enumerated from `tools/samples/asset-catalog.json`
(`rooms` map) on 2026-06-03. The catalog is regenerable from the
SHA-256-locked source binaries via the command in [WP-008 §Notes](../../../work-packets/WP-008-object-ini-catalog.md#notes).
If `object.ini` is reanalyzed and rooms are added/removed, regenerate
and reconcile this list.
