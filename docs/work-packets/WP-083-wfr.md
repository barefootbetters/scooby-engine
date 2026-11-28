---
layout: default
title: "WP-083: Phantom's Wizard's Rule Room"
---

# WP-083: Phantom's Wizard's Rule Room (Gen 1)

**Status:** ✅ Done (2026-11-22)
**Phase:** 4 (game logic)
**Depends on:** WP-018 ✅ (hotspots and exits), WP-021 ✅ (clickables), WP-031 ✅ (the accusation / clues), WP-057 ✅ (Phantom's new game and first room), WP-081 ✅ (the wizard's bedroom — where the WFR returns the gang and the clue is given)
**Companion EC:** none (inline checklist under Exit criteria)
**Estimated effort:** One day (the game's largest class, 1022 lines)
**Pre-flight:** [pre-flight-WP-083-2026-11-22](../reference/pre-flight-WP-083-2026-11-22.md)

---

## Goal

Port the fourth and last of Phantom's group-8 (Upstairs) rooms, `ROOM_P30_WFR`
— the Wizard's Rule Room
([the audit's order](../reference/room-class-audit-phantom-2026-11-16.md#suggested-order),
group 8, Upstairs — the fourth sub-bullet), the game's largest class (1022
lines). Until now it has the base class: the room draws, but the wizard's game
does nothing. With this packet **every game class in Phantom's audit is ported.**

The WFR was split off from WP-081 (the wizard's bedroom and veranda) because it
is a self-contained minigame as large as the two WP-081 rooms together. It took
the next free packet number: WP-082 had meanwhile been claimed by another
session for the upstream-submission-prep decision brief, so the WFR is WP-083.

## Background

The Wizard's Rule Room
([scooby-exe](../formats/scooby-exe.md), extended by this WP) is the wizard's
Simon-says potion game. `ROOM_P30_WFR` (`0x41BEA0`, vtable `0x45EE7C`, 1022
lines, music `Wizards_Rule.Music`, no opening) overrides six vtable slots
against the base room vtable (`0x45E5FC`): the destructor (`0x41BF00`), `tick`
(`0x41C3A0`), `enter` (`0x41C0C0`), `reset` (`0x41C350`), `claim` (`0x41CF50`)
and the leave builder (`0x41BF30`, +0x24).

The mechanic (from the execution trace):

- The wizard sets a **rule**: a number (shown on a two-digit counter) and a run
  of coloured ingredients — **Red, Green, Blue, Pink, Yellow, Brown** — he
  **DANCE**s in turn while the gang **WATCH**es. The player repeats it by
  clicking the ingredients.
- The ingredients, Scooby and the wizard are a WFR animated sub-class
  (`0x41BAC0`, vtable `0x45EE54`) whose mode (`+0x5C`) plays an
  `ANIM_WFR_<name><suffix>` (`0x41BC80`): the idle, `TURN_DANCE`, `TURN_WATCH`,
  `DANCE<n>` or `WATCH`.
- A right run plays `Wizards_Rule.Correct%i_1_NARRATOR` and advances; a wrong
  one plays `Wizards_Rule.Incorrect[/2/3]_1_NARRATOR` (one of three at random)
  and `Knights.Glass_Breaks.1`, and spends a life. The lives
  (`OBJ_WFR_LIVES` / `ANIM_WFR_LIVESA`) are **difficulty-scaled**. Each lit
  colour also plays `Wizards_Rule.<Colour>` and `WFR.Potion_%i`.
- Out of lives, or the run finished, returns the gang to the wizard's bedroom
  (`ROOM_P24_Wizards_Bedroom`), where — on the return from here — the wizard's
  clue is given and the accusation armed (**WP-081**). The leave builder gates a
  transition-movie variant on owning the wizard's clue.
- The original drives the spinner off a lip-sync scene's **fractional playback
  position** (`0x4358D0`) over a position→ingredient table (`0x46C5B0`). The
  fork's scene player exposes no fractional position, so the spinner is ported
  on a tick counter over the same table — the way **Maria's game (WP-064)**
  drives its physics on a tick counter rather than the original's scene clock.

The room already has its `room_setup` entry (music; no opening), so no
`room_setup` edit is expected.

## Scope

**In scope (fork, `engines/scooby/` only):**

- **`WizardsRuleRoom`:** the class, its required placements (six coloured
  ingredients, the wizard, Scooby, two counter numbers), the `OBJ_WFR_*` /
  `ANIM_WFR_*` claims, the difficulty-scaled lives, the counter display, the
  wizard/colour DANCE run, the Simon repeat (clicking the ingredients), the
  Correct/Incorrect/Glass_Breaks/Potion lines, the music, and the return to
  `ROOM_P24_Wizards_Bedroom`.
- **A `script` check** against an independent reference (Showdown has no WFR).

**Out of scope:** no change to a sibling room class is expected (WP-081's
bedroom already reads the return `from == ROOM_P30_WFR`). The leave-transition
movie variant by clue ownership is noted but not reproduced (see Result).

## Exit criteria

1. [x] The title matches an independent reference line for line:
   - the class; the music and the lines (`Wizards_Rule.Music`,
     `Wizards_Rule.Red`/`Green`/`Blue`/`Pink`/`Yellow`/`Brown`, `WFR.Potion_`,
     `Wizards_Rule.Correct`, `Wizards_Rule.Incorrect[/2/3]_1_NARRATOR`,
     `Knights.Glass_Breaks.1`, all probed by prefix); the `OBJ_WFR_BOTTLES`
     clickable claim; the position table; the return to the bedroom.

   Showdown prints that it has no wizard's rule room.
2. [x] Live, in Phantom: the WFR draws (full draw order, a stable 640×480 frame);
   `enter` wires the six bottles, the counter and the difficulty-scaled lives,
   and the wizard dances a run. (The moment-to-moment Simon feel is for a human
   to confirm live.)
3. [x] Scooby-only build: 0 errors and 0 warnings. The earlier checks and the
   room check are unchanged but for the usual per-run random keys. The fork diff
   stays inside `engines/scooby/`, staged by name.

## Deliverables

- Fork commit on `scooby-engine` (files staged by name: the new
  `wfr_rooms.{h,cpp}` and `wfr_check.cpp`, a factory line and include in
  `room_class.cpp`, the two `module.mk` entries, and the check's declaration
  (`scooby.h`) and call (`chase_check.cpp`)).
- [scooby-exe](../formats/scooby-exe.md): the Wizard's Rule Room.
- `WORK_INDEX` row and ledger line flipped to ✅ Done on close; **Phantom's
  audit complete**.

---

## Result (2026-11-22)

`WizardsRuleRoom` in fork commit `ee4da7ea46` (scummvm
[PR #9](https://github.com/barefootbetters/scummvm/pull/9), stacked on WP-081's
[PR #6](https://github.com/barefootbetters/scummvm/pull/6)), files staged by
name: `wfr_rooms.{h,cpp}`, `wfr_check.cpp`, the factory line and include in
`room_class.cpp`, the two `module.mk` entries, the check's declaration
(`scooby.h`) and call (`chase_check.cpp`). No `room_setup` or sibling-room edit —
the room's music is played in `enter`, and WP-081's bedroom already reads the
return `from == ROOM_P30_WFR`.

**Merged 2026-11-27.** This WP closed on 2026-11-22 with PR #9 still open, so
`scooby-engine` had no Wizard's Rule Room until the PR was merged on 2026-11-27
(merge commit `00e3076da7`). A fork build from before that date has no
`WizardsRuleRoom` class.

**Exit criteria.**

1. **Engine == reference (captured).** On Phantom the self-test reports: the
   class (`WFR wfr`); every clip by prefix (`Wizards_Rule.Music`,
   `.Red`/`.Green`/`.Blue`/`.Pink`/`.Yellow`/`.Brown`, `WFR.Potion_`,
   `Wizards_Rule.Correct`, `.Incorrect/2/3_1_NARRATOR`, `Knights.Glass_Breaks.1`);
   the `OBJ_WFR_BOTTLES` **clickable** claim; the position table
   (`0 1 2 6 6 6 6 6 3 4 …`, 6 a gap); the return to `ROOM_P24_Wizards_Bedroom`.
   **Showdown prints it has no wizard's rule room** (`wizard's rule room check:
   no wizard's rule room`).
2. **Live (Phantom, captured).** With `start_room=ROOM_P30_WFR` the room loads
   (`516096 of 516096`) and renders a stable 640×480 frame; the draw order is
   Scooby, the wizard, six `OBJ_WFR_BOTTLES`, the table, the counter, the skulls,
   the lives and the exit; `enter` wires **6 bottles, 4 lives and the counter**
   with no missing-asset warnings, and the wizard dances the run. The
   moment-to-moment Simon loop and the look of the animations are **for a human
   to confirm live.**
3. **Scooby-only build:** `--disable-all-engines --enable-engine=scooby`, **0
   errors, 0 warnings** in `engines/scooby/` (the two pre-existing gob / halestorm
   warnings are not scooby). The fork diff stays inside `engines/scooby/`, staged
   by name.

**The main correction.** The first wiring scanned object names for the colours;
the self-test passed (it calls `claimPlacement("OBJ_WFR_BOTTLES")` directly), but
the live run showed `0 bottles`. The six bottles are one `OBJ_WFR_BOTTLES`
placement each, told apart by the colour in their **ANIM** (`getAnim`), not the
object name; only Scooby and the wizard are the animated sub-class, and the
counter is `OBJ_WFR_COUNTER`. Fixed to wire by object + anim — the live run then
found all six bottles and the counter. (The self-test alone would not have caught
this: the live draw did.)

**One porting judgment.** The original drives the spinner off a lip-sync scene's
fractional playback position (`0x4358D0`); the fork's scene player exposes no
fractional position, so the spinner runs on a tick counter over the same
position table (`0x46C5B0`) — the Maria-game idiom (WP-064). The contract
(classes, clips, claims, music, exit) is what the self-test checks; the feel of
the reconstructed loop is for live play.

**One deferral.** The leave builder (`0x41BF30`) sets a transition-movie variant
(movie `0xb`) when the wizard's clue is not yet owned; the engine's `leaving()`
hook exposes the scene, not that transition movie, and the destination (the
bedroom) and every gameplay contract are the same either way, so the variant is
left to a later pass rather than faked.

See [scooby-exe → the Wizard's Rule Room](../formats/scooby-exe.md#phantoms-wizards-rule-room-wp-083).

## Notes

- The fourth and last packet of the audit's group 8 (Upstairs), and the last
  game class in Phantom's audit — with it, every game class in both titles is
  ported.
- The return to the wizard's bedroom pairs with WP-081: the bedroom gives the
  wizard's clue and arms the accusation on `from == ROOM_P30_WFR`.
