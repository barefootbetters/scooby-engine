---
layout: default
title: "EC-010: Phantom playthrough run sheet"
---

# EC-010: Phantom closeout — playthrough and gate-walk checklist

**Paired WP:** [WP-087](../work-packets/WP-087-phantom-closeout.md)
**Purpose:** Keep the *Phantom* closeout to one start-to-credits run, the save
and load cycle and the gate walk, without it turning into bug-fixing. Each
defect is **logged as a one-line gap and the run goes on**; fixes are
follow-up WPs. Only a hard progression blocker (no legal way forward) stops the
run, and it becomes the top gap.
**Status:** 📝 Not started.

**Evidence labels** (one per row, as WP-087 §Notes defines them): **log**
(named file and quoted line), **self-test** (named trace), **live — Jeff**,
**live — session** (computer use, screenshots kept), **source** (file and
line). A row without one stays ☐.

---

## Pre-flight

- [ ] Pre-flight verdict **READY**: `docs/reference/pre-flight-WP-087-<date>.md`, committed.
- [ ] Fork built with only this engine enabled: `./configure --disable-all-engines --enable-engine=terraglyph && make -j32` under MSYS2 UCRT64. Record the fork commit, the pin as its ancestor, and warnings in `engines/terraglyph/` (gate 1).
- [ ] *Phantom* disc image mounted, unmodified. Record the drive and `Scooby.exe`'s SHA-256; it must be `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED` ([tools/exes/README](../../tools/exes/README.md#phantom-gen-1)).
- [ ] Who drives Part A is recorded: Jeff, or a session under computer use (and who watches).
- [ ] Capture folder set outside this repo (scratchpad or the verification run's folder); nothing from the disc is staged.

---

## Step 0 — Detection and boot (time-box: 15 min)

- [ ] `scummvm.exe --detect --path='<drive>:\scooby'` → `terraglyph:phantomknight` (gate 3). Evidence: the command's output.
- [ ] Title movies play, then Sign In. Evidence:
- [ ] New player → new game; *Phantom*'s story values are set (WP-057): the banner colours, the crest order and the skull combination for this game. Evidence (the `new game` log lines):
- [ ] The first story room, `ROOM_P01_Drawbridge`, opens with its opening and music. Evidence:

**Outcome:**

## Step 1 — Story playthrough (time-box: open; this is the run)

Play straight through. The table is the spine, from the
[Phantom audit](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order)'s
order and the WPs that ported each room; the audit says its order "isn't from a
play-through", so follow the game's own flow and log what really happens.
**Result:** ✅ as expected / ⚠ works, with drift / ✗ blocker or missing asset
(log it in the gap list). Do not fix ✗ inline.

| # | Beat / rooms | Expected | Result | Evidence | Note / gap |
|---|---|---|---|---|---|
| 1 | Drawbridge → Town ([WP-057](../work-packets/WP-057-drawbridge.md)) | four flags set to the banners' colours; the drawbridge comes down; the town opens | ☐ | | |
| 2 | Souvenir shop ([WP-058](../work-packets/WP-058-souvenir-shop.md)) | the tokens buy the empty bottle; Fred puts it in the toolbar | ☐ | | |
| 3 | Gardener's house, garden, plaque ([WP-060](../work-packets/WP-060-gardeners-house.md)) | the crest pressed in this game's order opens the way to the garden | ☐ | | |
| 4 | Room of doors + the Jester ([WP-061](../work-packets/WP-061-room-of-doors.md)) | the locked dining-room door; the Jester's balls, talk and clue | ☐ | | |
| 5 | Throne room ([WP-062](../work-packets/WP-062-throne-room.md)) | Jane's movie; the duster to Jane; the ruby's movie once the balls are found | ☐ | | |
| 6 | Dining room + Maria's game ([WP-063](../work-packets/WP-063-dining-room.md), [WP-064](../work-packets/WP-064-maria-game.md)) | trays balanced → `MariaPuzzle`; her clue, thanks and the burger | ☐ | | |
| 7 | Kitchen + Ewan's quiz ([WP-065](../work-packets/WP-065-kitchen.md), [WP-066](../work-packets/WP-066-ewan-quiz.md)) | the quiz won (level + 3) → `EwanPuzzle`; his clue; the grease fills the bottle | ☐ | | |
| 8 | Kitchen storage ([WP-067](../work-packets/WP-067-kitchen-storage.md)) | Fred takes the screwdriver, Daphne the shield; the door opens (movies 62–64) | ☐ | | |
| 9 | King's armory + slide ([WP-068](../work-packets/WP-068-kings-armory.md)) | the duster; the full bottle → movie 7 into the slide | ☐ | | |
| 10 | Arenas + Brad's game ([WP-069](../work-packets/WP-069-arenas.md), [WP-070](../work-packets/WP-070-brad-game.md)) | the grindstone sharpens the shears (movie 40); Brad rises; the armour in order → `BradPuzzle` | ☐ | | |
| 11 | Secret passages, storage, treasury ([WP-071](../work-packets/WP-071-secret-passages.md)) | the wall of fire takes the level's snacks + 2 (movie 39); Velma takes the rope | ☐ | | |
| 12 | Royal gallery + magic mirror room ([WP-072](../work-packets/WP-072-royal-gallery.md)) | the mirror hung; the red ball; the snack gate to the mirror room | ☐ | | |
| 13 | Knights of the Snack Table ([WP-073](../work-packets/WP-073-kst.md)) | serve to the quota → back to the dining room | ☐ | | |
| 14 | Hedge maze + maze map ([WP-074](../work-packets/WP-074-maze.md)) | the unicycle through the grid; the map's four markers jump | ☐ | | |
| 15 | Maze centre, fountain, well ([WP-075](../work-packets/WP-075-maze-interior.md)) | the token-gated fountain; the well out to the royal gallery; the yellow ball | ☐ | | |
| 16 | Below the balcony + its door ([WP-076](../work-packets/WP-076-below-balcony.md)) | the sharp shears cut the vines; the blue ball to the Jester | ☐ | | |
| 17 | Wizard's skull + library ([WP-077](../work-packets/WP-077-wizards-skull.md)) | the spell book on the shelf shows the combination (movie 61); the skulls set → movie 6 | ☐ | | |
| 18 | Princess's bedroom + Mermaid's cavern ([WP-078](../work-packets/WP-078-princess-bedroom.md)) | Daphne takes the spell book; the cavern echoes the wrong-item lines | ☐ | | |
| 19 | Wizard's bedroom + veranda ([WP-081](../work-packets/WP-081-wizards-bedroom-veranda.md)) | the wizard met; the maze-map scroll; the veranda's well | ☐ | | |
| 20 | Wizard's Rule Room ([WP-083](../work-packets/WP-083-wfr.md)) | back to the bedroom; the wizard's clue; the accusation armed. Note whether the movie `0xb` variant is missed when leaving without the clue | ☐ | | |
| 21 | Ghost spot(s) ([WP-056](../work-packets/WP-056-ghost-spot.md)) | the pan, then on to the Town, not back to the room the ghost came in | ☐ | | |
| 22 | Castle balcony (`ROOM_P26_Castle_Balcony`, base class) | draws and exits like any base room | ☐ | | |
| 23 | Final clue → accusation ([WP-071](../work-packets/WP-071-secret-passages.md), [WP-031](../work-packets/WP-031-accusation.md)) | the Princess clicked with the arrow sets `FinalClue` and opens the accusation (movie 55) | ☐ | | |
| 24 | Big Head + the reveal ([WP-031](../work-packets/WP-031-accusation.md)) | the right suspect for this game revealed | ☐ | | |
| 25 | Credits ([WP-030](../work-packets/WP-030-options-credits.md)) | roll to the end | ☐ | | |

Also note, on the way: the suspect board opened mid-game returns to the room
(the WP-080 fix, shared), and Scrappy's hints and the snack box work in
*Phantom*'s rooms.

- [ ] Every beat reached, with evidence; no missing asset, crash, assertion or dead end.

**Outcome:**

## Step 2 — Save and load (time-box: 20 min)

- [ ] Save mid-run in a *Phantom* room, before a room change. Evidence (the `profile saved` line):
- [ ] Quit the engine fully; relaunch as a new process. Evidence:
- [ ] Load (Sign In's existing player, or ScummVM's load menu); the room, inventory and progression restore. Evidence (the `profile read` line, or "live visual — Jeff"):
- [ ] Optional: the headless `save N` / `load N` verbs in `test_script` on a *Phantom* room. Evidence:

**Outcome:**

## Step 3 — Acceptance-gate walk (time-box: 45 min)

Re-run each check against the fork commit recorded in Pre-flight; do not
quote WP-079 or WP-082.

| Gate | Check | Result | Evidence |
|---|---|---|---|
| 1 | Clean build against the pin; 0 warnings in `engines/terraglyph/` | ☐ | |
| 2 | Registered; `--list-engines` shows `terraglyph` | ☐ | |
| 3 | Detects `phantomknight`; *Showdown*'s disc still `showdown`; an unrelated folder finds nothing | ☐ | |
| 4 | `grep -rnE '(fopen\|std::ifstream\|CreateFile[AW]?)' engines/terraglyph/` → none outside comments | ☐ | |
| 5 | All audio through `Audio::Mixer`; no platform audio calls | ☐ | |
| 6 | Bink through `Video::BinkDecoder`; `grep -rni binkw32 engines/terraglyph/` → none | ☐ | |
| 7 | Single-threaded: `grep -rnE '(pthread_\|std::thread\|CreateThread\|_beginthread)' engines/terraglyph/` → none | ☐ | |
| 8 | Style: WP-082's assessment stands, unless the engine's files changed since | ☐ | |
| 9 | GPL-3.0 header on every `engines/terraglyph/*.{cpp,h}` | ☐ | |
| 10 | `phantomknight` declared `ADGF_TESTING` (expected ✗ until Step 4's GO flip) | ☐ | |

**Per-variant *Phantom* record** (detection MD5 over the first 5000 bytes, from
`detection_tables.h`; SHA-256 from [tools/exes/README](../../tools/exes/README.md#phantom-gen-1)).
Confirm each against the mounted disc:

| File | Size (bytes) | Detection MD5 | Full-file SHA-256 | Confirmed |
|---|---|---|---|---|
| `Scooby.exe` | 483,377 | `c36473c3204c10d75eebf0241e35aee8` | `619EA6871A2FD305CA30814C438F9552DB85FDADB65AD7BE5B82A1656AF807ED` | ☐ |
| `TGIFILE.ART` | 114,386,944 | `a0c28dd3e75241794cb19481496bd919` | `AC24E9AE88CD7D15B1137ADBAA331FD987D8CE54B94A5A808042665BA012BF04` | ☐ |
| `object.ini` | 28,788 | `aafe695ae3f6c2db91858661e28e1c6c` | `67B9EF7967B1EDEB7331D3D41F9EFABC326F4740A6C8D7A8781965CFE9D67870` | ☐ |

**Outcome:**

## Step 4 — Verdict, and on a GO the release (time-box: 45 min)

- [ ] Verdict and gap list written in [WP-087 §Result](../work-packets/WP-087-phantom-closeout.md), each gap tagged with its owner WP; the WP-083 movie `0xb` variant has its line.
- [ ] **GO only:** fork worktree from `tools/New-ForkWorktree.ps1`; `phantomknight` → `ADGF_TESTING` in `engines/terraglyph/detection_tables.h`; build; gate 10 re-run; fork PR opened and merged. Record the PR and squash commit.
- [ ] **GO only:** [`scummvm-wiki-scooby.md`](../reference/scummvm-wiki-scooby.md) — *Phantom*'s row, its known limitations, and the `ADGF` lines updated.

**Outcome:**

---

## Definition of done

- [ ] Steps 0–3 recorded with an evidence label on every filled row.
- [ ] WP-087's exit criteria each marked met, not met or n/a, with the evidence named.
- [ ] Verdict written; on a GO, the flag PR merged and the wiki-page draft updated.
- [ ] WP-087's row in [WORK_INDEX](../work-packets/WORK_INDEX.md) updated.

## Out-of-scope captures

Temptations during the run, logged here as one-liners for later WPs:

-
