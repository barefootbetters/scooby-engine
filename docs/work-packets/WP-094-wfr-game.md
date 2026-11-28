---
layout: default
title: "WP-094: Phantom's Wizard's Rule Room, the original's game"
---

# WP-094: Phantom's Wizard's Rule Room: the original's game (Gen 1)

**Status:** ✅ Done (2026-11-27). Fork PR [barefootbetters/scummvm#18](https://github.com/barefootbetters/scummvm/pull/18) is open.
**Phase:** 5 (a reconstruction found while searching packets for setup-only checks)
**Depends on:** WP-083 ✅ (the room's claim, entry and exit), WP-081 ✅ (the bedroom the room returns to)
**Companion EC:** none (inline checklist under Exit criteria)
**Pre-flight:** [pre-flight-WP-094-2026-11-27](../reference/pre-flight-WP-094-2026-11-27.md). Required: the packet modifies `engines/terraglyph/**`.
**Targets generation(s):** Gen 1, *Phantom of the Knight* only. Showdown has no such room.
**Estimated effort:** Half a day

---

## Goal

Replace the fork's reconstructed Wizard's Rule Room game (`ROOM_P30_WFR`,
class `0x41BEA0`) with the original's, ported from the decompile, and prove
it by playing it through the engine's tick and live.

## Background

[WP-083](WP-083-wfr.md) ported the room and wrote that "the contract
(classes, clips, claims, music, exit) is what the self-test checks; the feel
of the reconstructed loop is for live play". Its live run watched the wizard
dance and never clicked a bottle. Jeff asked for packets with notes like
that to be searched after WP-090, WP-092 and WP-093 each found gaps behind
them, and this room led the list.

**The fork at `3960fdb`** (source):

- **The wrong game.** It was a Simon run that grew by one colour a round,
  timed on a tick counter. WP-083 chose the counter because "the fork's
  scene player exposes no fractional position". The original's clock,
  though, is the song's play position (`0x4358D0`). That is Showdown's
  `0x434BA0`, which the fork already ports as `Sound::getClipMillis()`.
- **Most of the table missing.** It used the first 48 entries of the table
  at `0x46C5B0`. The original's has 304.
- **Input held.** It returned `isBusy()` while the wizard danced, and the
  engine treats a busy room class as taking every click as a skip, so
  clicks made then were lost. The original never holds input in this room.
- **Wrong anims and lives.** The dancers' anims all looped from step 3, and
  it gave one life fewer than the original.
- **No exit movie.** The movie-`0xB` exit variant was deferred, and it is on
  WP-087's gap list.

## Scope

**In scope:**

1. **Fork, `wfr_rooms.{h,cpp}`:** the tick (`0x41C3A0`), entry (`0x41C0C0`),
   leave (`0x41C350`), claim (`0x41CF50`), the ways out (`0x41BF30`, through
   `exitMovie()`), the dancers (`0x41BAC0`–`0x41BC80`), and the whole table.
2. **Fork, `wfr_check.cpp`:** the game played through the tick, with the
   song's clock set directly, against text written from the trace.
3. **Docs:** this packet, its pre-flight, the WFR section in
   [scooby-exe](../formats/scooby-exe.md#phantoms-wizards-rule-room-wp-083),
   pointers in WP-083 and WP-087, and the index row.

**Out of scope:**

- **The voice channel's volume swap** at entry (`+0x138`): the song ships
  in `Voice.dat`, and the original sets the voice channel's volume to the
  music's. The fork's `Sound` keeps per-file percentages and nothing here
  depends on it.
- **The cursor's "below row 240" condition:** the bottles open the cursor
  wherever they are, through their rollover.

## Exit criteria

1. [x] **Self-test.** The WFR lines match text written from the trace before
   the run. The rest of the self-test matches the `3960fdb` baseline except
   the per-run random keys and a known-flaky arena line. No new warnings.
2. [x] **Live (session).** The beats follow the song. Clicking the beat's
   bottles plays a phrase clean and earns a snack. A missed beat breaks a
   glass and costs a life.
3. [x] **Process.** The fork PR against `scooby-engine` is open, and each claim
   carries its evidence label.

## Result

Every claim is Gen 1, Phantom. Evidence labels: **source** (the decompile),
**self-test**, **log** (the engine's debug log of a live run), **live —
session** (a scripted run this session drove). Nothing here is **live —
Jeff**.

**What the original does (source).** It is written up in full in
[scooby-exe](../formats/scooby-exe.md#phantoms-wizards-rule-room-wp-083),
from `Scooby.exe` (SHA-256 `619EA687…AF807ED`, Ghidra 12.1.4 headless):

- **The clock** is the song's play position at 1.3795 beats a second. A beat
  counts in its first 0.49.
- **A phrase** is 16 beats and eight table entries. On beats 0–7 the wizard
  dances and lights his bottles; on beats 8–15 the player clicks the same
  bottles on the same beats.
- **A missed beat** breaks a glass and costs a life. A phrase played clean
  earns a snack.
- **The end** comes when 5 − difficulty phrases have been missed, or when the
  song is over. The gang goes to the bedroom, through movie `0xB` if the
  wizard's clue isn't owned.
- **The table** holds 38 phrases: six each of 3, 4, 5, 6, 7 and 8 bottles,
  then two empty. The song (418 s, about 577 beats) lasts about 36 of them.

**The port (source).** On `wp-094-wfr-game` (`8bc6cf2994`), the C++ table is
generated from the Ghidra dump of `0x46C5B0`, not typed. A first hand
transcription miscounted, and the generator's checks caught it. Two debug
lines (level 2) log each beat with its bottle and each bottle's box on
screen.

**Self-test (self-test).** The text of each line was written from the trace
before the run; the snack count, cels and sounds follow from `rand()`, pinned
to 1. All seven match:

- **The claim:** the bottles are sprites in layer 0, depth 10, hit 2.
  - Phrase 0: `RED GREEN BLUE - - - - -`, repeated.
  - Phrase 1: `PINK YELLOW RED`, repeated.
  - Bottles a phrase: `3`×6 `4`×6 `5`×6 `6`×6 `7`×6 `8`×6 `0 0`. These were
    computed separately from the dump.
- **Entry:**
  - Lives: 5, 4 and 3 by level.
  - The six bottles: stopped, dark, the cursor open over them, hit by their
    polygon.
  - The counter's cels: 9 9 at no snacks, 0 2 at 13.
  - Both dancers idle, and both skulls found.
- **A clean phrase,** beat by beat:
  - The wizard lights `RED GREEN BLUE`. At beat 0 he's turning to dance and
    Scooby is turning to watch.
  - The player's clicks light `RED GREEN BLUE`. At beat 8 both are turning to
    dance.
  - The snack comes at beat 11, the first gap: snacks 1, cels 9 0, and
    `Wizards_Rule.Correct2_1_NARRATOR`.
  - At beat 16 the wizard lights `PINK`. Late in every beat the bottles are
    dark.
  - The sounds heard are `WFR.Potion_1–3` with their colours.
- **Beat 9 missed:**
  - At beat 10 the phrase is missed: the fifth life is hidden, Scooby goes
    idle, and `Knights.Glass_Breaks.1` and `Wizards_Rule.Incorrect2_1_NARRATOR`
    play.
  - There's no snack at beat 11, and at beat 16 the miss counts.
- **No clicks, level 2:**
  - Three lives, lost at beats 9, 25 and 41.
  - The third miss counts at beat 48, and the gang goes to
    `ROOM_P24_Wizards_Bedroom` with movie 11, since the clue isn't owned.
- **The song over** with the wizard's clue owned: the bedroom, no movie.
- **The sounds:** `WFR.Potion_1–6` and `Correct1–5` all found.

The first run printed movie 11 for "the song over" where the expectation said
−1. The log showed the room's exit never ran in that scenario: my check reused
`next` from the previous scenario, so its loop never ticked. With `next`
cleared, the second run matches.

The rest of the self-test matches the `3960fdb` baseline, from
`C:\dev\scummvm`, run alone. The only differences are:
- the per-run random keys;
- WFR's own lines, where the old setup-only claim line is replaced by the
  seven above;
- the arena pile check's level-0 line, which printed `to -` in this run and
  `ROOM_Brad_SPOOKY` in the baseline. That check is **flaky on unchanged
  code**: it printed `-` in WP-092's baseline too. It waits on a clip's
  playback and doesn't touch this room.

The runtime warnings match, 18 each.

**Build (log).** Terraglyph only, in the fork worktree; no warnings in the
changed files. A shadowed local in the first draft of the check was renamed.

**Live (live — session, with log).** The run used `start_room=ROOM_P30_WFR`
and level 0.

- **The beats follow the song:** `beat 1 at 730 ms`, `beat 8 at 5808 ms, the
  player's, bottle 0`, and so on, 0.72 s apart.
- **Phrase 0, played:**
  - The script clicked the red, green and blue bottles in turn every 60 ms
    through the player's beats. The log shows the clicks landing on sprites
    7, 3 and 4 (red, green, blue). Clicks on the wrong bottle or off the beat
    cost nothing in the original.
  - At beat 11: `wfr: a phrase played clean, 2 snacks`. The screenshot shows
    the counter at 02, Scooby dancing and five lives.
- **Phrase 1, left alone:** at beat 25, `wfr: a beat missed, a glass breaks`.
  The screenshot shows four lives, Scooby idle and the wizard dancing.

**Deviations:**

- **The voice channel's volume swap** isn't reproduced (out of scope).
- **The cursor** opens over a bottle through its rollover, not only below row
  240.
- **The exit's guard:** the room asks for its exit once, when the room script
  isn't busy. The original asks every tick until the exit is under way.

## Deliverables

- Fork: `wp-094-wfr-game`, PR [barefootbetters/scummvm#18](https://github.com/barefootbetters/scummvm/pull/18)
  (`8bc6cf2994`). Staged by name: `wfr_rooms.{h,cpp}` and `wfr_check.cpp`.
- Docs: this packet, its pre-flight, the WFR section in scooby-exe, the
  pointers in WP-083 and WP-087, and the index row.
- Local only: the decompile dumps, the table generator, the self-test and live
  logs, and the screenshots.

## Notes

- **WP-087's gap-list line** for the movie-`0xB` deferral is resolved here.
- **The packet search's next candidates,** from the same search: the wizard's
  skull ([WP-077](WP-077-wizards-skull.md)), whose skull clicks were never
  driven, and the hedge maze ([WP-074](WP-074-maze.md)), whose navigation is
  modelled.
- **The arena pile check's level-0 line is flaky.** Making it independent of
  playback timing would be a small check fix of its own.
