---
layout: default
title: "WP-089: Hotspot Magnet interface design"
---

# WP-089: Hotspot Magnet interface design — components, contracts and modes (Gen 1)

**Status:** ✅ Done (2026-11-27). All 17 exit criteria met
([§Close](#close-2026-11-27)); Jeff decided its proposals H9–H16 on 2026-11-27. **Findings
landed in:** the plan's
[Part II](../reference/hotspot-magnet-plan.md#part-ii--technical-design)
(§4.2–4.6, §5.6, §6.1–6.6 and the new §6.8), §7.4, the new
[§12.7](../reference/hotspot-magnet-plan.md#127-test-hooks), the
[evidence register](../reference/hotspot-magnet-plan.md#38-research-evidence-register)
(E27–E44), the
[decision register](../reference/hotspot-magnet-plan.md#104-open-design-decisions)
(H9–H16), and
[Appendices B](../reference/hotspot-magnet-plan.md#appendix-b-interface-declarations)
and [D](../reference/hotspot-magnet-plan.md#appendix-d-terminology).
**Phase:** 5 (polish and accessibility).
**Depends on:** WP-086 ✅ (research, plan §3), and Jeff's decisions H1–H8 in
the plan's [§10.4](../reference/hotspot-magnet-plan.md#104-open-design-decisions)
✅ (2026-11-26 and 27; H4 provisional).
**Unblocks:** the directional algorithm design packet (packet 3 of the
[plan's sequence](../reference/hotspot-magnet-plan.md#11-development-work-packets)),
which needs this packet's hotspot record and core contract, and the
implementation packets 4–8.
**Companion EC:** [EC-012](../execution-checklists/EC-012-hotspot-magnet-interface-design.md).
**Pre-flight required:** **No.** A design packet: it reads the fork's source
and writes only the plan page, this packet's own records and the dashboard
note. It changes nothing under `engines/terraglyph/**`, `docs/formats/**` or
`tools/**`, and classifies no title's generation.
**Targets generation(s):** Gen 1 (*Showdown*, *Phantom*). The shared
navigation core it specifies carries no generation; every TerraGlyph adapter
it specifies is Gen 1.
**Estimated effort:** about one working day (5–7 hours) across the EC's
steps. **Actual:** one session on 2026-11-27. The source reading ran as two
parallel read-only passes (ScummVM's input side, TerraGlyph), and every fact
the design rests on was re-checked against the source before it went in.

---

## Goal

Turn Part II of the [Hotspot Magnet plan](../reference/hotspot-magnet-plan.md)
from design intent into a design the implementation packets can build from,
for the Phase 1 TerraGlyph prototype. The output fixes, in the plan: what
each of the five components (A Provider, B Navigation Core, C Input Adapter,
D Cursor Adapter, E Activation) takes and returns and who owns it; the
hotspot record the core navigates over; how the selection survives a refresh
and when it's dropped; Magnet mode and cursor mode, and how the remote moves
between them; how the rooms that need a held button or a drag are played;
the coordinates each component works in; the per-game setting; and the test
hooks later packets need. Each choice the decisions H1–H8 don't already make
goes to Jeff as a proposed register row.

## Background

- **What's decided** (plan §10.4, Jeff, 2026-11-26 and 27):
  - H1: a game keymap binds `JOY_UP`…`JOY_CENTER` (and `JOY_HAT_*`) while
    Magnet mode is on; turning it off returns the D-pad to the Virtual Mouse.
  - H2: the provider is `Engine::getHotspotPositions()` as is; stable ids
    only if refreshes make the selection unstable.
  - H3: the cursor goes to a validated interaction point, engine-supplied
    when it has one, otherwise the first point on a hit-tested grid, centre
    first; never the box's centre on trust.
  - H4 (provisional): `engines/` is the future shared home, pending
    maintainer feedback; Phase 1 stays inside `engines/terraglyph/`.
  - H5: a TerraGlyph extra option first, default off.
  - H6: hold OK. A short press activates on release; a hold past a threshold
    over 400 ms enters cursor mode and activates nothing; repeated downs while
    OK is held are ignored. The input integration packet confirms the hold's
    event sequence inside ScummVM on the TV (E26's open item).
  - H7: the §3.5 eligibility rule, characters left out at first.
  - H8: refresh on directional input, and drop the selection when game state
    changes; a hotspot that disappears or is disabled is never activatable.
- **What the research established** (plan §3, evidence E1–E26). The ones this
  design rests on:
  - `Graphics::HotspotInfo` is a **point, a name and a type**, with no box
    and no id (E12). H2 keeps it as is, so any identity or geometry the
    design needs lives in the TerraGlyph adapter, or is raised as H2's
    condition (b).
  - Showing all hotspots takes more than implementing
    `getHotspotPositions()`: the engine also calls `drawHotspots()` each frame
    and adds `createHotspotAction` in `initKeymaps()` when `hotspotsEnabled()`
    (E11, E13). One override serves both that display and Magnet.
  - The Virtual Mouse has **no click action**, and `JOY_CENTER` is unbound in
    games (E4, E6). So cursor mode needs its own way to click with OK, or the
    fallback moves the pointer but can't click.
  - TerraGlyph's single click path is `TerraglyphEngine::handleMouse(bool
    click, Point)`, which the `test_script` `click x y` command already drives
    (E20). `Room::hitTest(x, y)` returns a sprite index (E18), and a
    polygon's box is private (E18), so the H3 point search needs an accessor.
  - The remote never repeats a held button, but Android does, 400 ms into a
    hold and then every 50 ms, and ScummVM passes each repeat on as a new
    `JOYBUTTON_DOWN` (E26). The repeat policy for held D-pad presses belongs
    to packet 3 (plan §6.3).
- **Seen while drafting** (fork `origin/scooby-engine` `0d5a69c7694f`, read
  only, checked in a cold review; the EC re-pins and records these as
  E-rows):
  - **TerraGlyph** declares no keymap and doesn't implement
    `getHotspotPositions()`. The screen is 640×480 (`initGraphics(640, 480,
    …)`, `terraglyph.cpp:93`), but a room can be up to 1920 px wide and shows
    only its left edge (`terraglyph.cpp:463-466`). `hitTest()` works in room
    space, so a sprite past x = 639 can be hit but isn't on screen.
  - **What Gen 1 reads.** Mouse movement, the left button's press, and its
    held state: the main loop keeps `_mouseDown` from `EVENT_LBUTTONDOWN` and
    `EVENT_LBUTTONUP` (`terraglyph.cpp:232-237`). Keys go to the room class,
    with Escape and Space as skip. The right button is read only by
    `movie.cpp:120`, to skip a movie, so Gen 1 needs no secondary action.
  - **Rooms that aren't plain clicks.** Several room classes read the held
    button or the pointer directly: the Options knobs
    (`options_rooms.cpp:161-174`, `:208`), Pie Noon (`pienoon_rooms.cpp:729`,
    `:773`), the corral (`corral_rooms.cpp:205`), Brad's game
    (`brad_rooms.cpp:447`), `ButtonRoom::tick` (`room_class.cpp:141`), and
    the chase, Maria's game, the vault and Sign In's list, which read
    `getMousePos()`. A synthetic `handleMouse(true, p)` never sets
    `_mouseDown`, so these can't be played by Magnet's click alone.
  - **Room-class targets.** `handleMouse()` hands a click to the room class's
    `click()` before the kind checks (`terraglyph.cpp:362-363`), and
    `ButtonRoom`'s buttons are found by object name (`room_class.cpp:108-115`).
    H7's rule names exits, clickables, requires and inventory objects and
    toolbar sprites; whether the menu rooms' buttons (Title, Sign In,
    Options, the accusation) are among them is unverified.
  - **Keys.** No room class reads the arrow keys (they carry no ASCII).
    `SignInRoom::key()` queues every ASCII key, Enter included (`'\r'` starts
    play, `signin_room.cpp:326`), and Delete; Escape and an early Space still
    skip. A Windows binding of Enter to OK would take Enter from name entry.
  - **The Keymapper's event shape.** A bound action reaches the engine as
    `EVENT_CUSTOM_ENGINE_ACTION_START` for every incoming down, Android's
    repeats included, and one `_END` on the up (`keymapper.cpp:271-276`,
    `:300-317`, `:377-378`). Keyboard repeats are dropped (`:308`), and a hat
    axis gives one start and one end. So a hold looks different on the
    remote, a gamepad hat and a keyboard. `Keymap::setEnabled()` works on a
    whole keymap (`keymap.h:167-168`), so turning one keymap off would unbind
    OK with the directions.
  - **Nested event loops.** `movie.cpp:116-124` polls events itself and drops
    all but its skip keys, and opening ScummVM's main menu switches to the GUI
    keymaps. An OK pressed before either and released during it would leave a
    hold timer running.
  - **Fork drift since WP-086's pin `ff490ad9449f`:** four WP-085 commits
    (fork PR #13). Besides Android packaging, `android.cpp` gained a
    `gui_launcher_chooser` default (`:366-371`), which moves later lines by
    6, so E3, E8 and E9's line numbers are stale. And
    `ScummVMActivity.java:1287-1296` adds a `dispatchKeyEvent` override that
    runs before `ScummVMEvents`: in **test builds**, `AdvancedMode.onKeyEvent()`
    watches for the D-pad sequence up, down, up, down, left, right, left,
    right within 10 s and, on a match, swallows the last key and opens the
    advanced mode. A player in Magnet mode on a test build (the builds packets
    9–11 test with) could trigger it. Its comment also says the TCL's remote
    sometimes reports one press twice, which E25 and E26 didn't see.
- **Supersession check (2026-11-27).** WORK_INDEX has no other interface or
  navigation design packet; plan §11 names this as packet 2. `git log --all`
  for "interface design", `WP-089` and `EC-012` finds only the plan's own
  mention. WP-088 and EC-011 are held by the Play internal-testing draft in a
  parallel session, so this packet takes 089 and EC-012.

## Scope

### In scope

All reading is at a pinned fork commit, recorded in EC-012 Step 0; the
default is `origin/scooby-engine` at its tip on the execution date.

1. **Re-pin and drift.** Record the pinned fork commit. Compare it with
   WP-086's pin `ff490ad9449f` across every file in the plan's Appendix A and
   every file changed in between (`git diff --stat`), and record each change
   that alters a finding or a citation, including the two Android items
   above. Refresh the stale line numbers in E3, E8 and E9.
2. **Component contracts (plan §4.2, §4.3).** For each of components A–E:
   its inputs, outputs, owner (engine or shared), when it runs, and the
   existing ScummVM or TerraGlyph symbol it builds on or adds. Write the
   contracts as design-level declarations in Appendix B, with no function
   bodies. Components B and C must name no TerraGlyph type or symbol.
3. **The hotspot record and the provider (plan §4.3, §4.6; H2, H3, H7).**
   - Define the record the core navigates over and map it field by field to
     `Graphics::HotspotInfo`. Say whether the core navigates over points only
     or needs a box, and why.
   - Name what the TerraGlyph adapter keeps beside each record (sprite index,
     room) without extending `HotspotInfo`. If the design needs an id on the
     shared record, raise it as H2's condition (b), not design it in.
   - Specify the H3 point search: the box it searches, its grid step, and the
     `Room` accessor it needs for the private polygon box.
   - Specify the provider's filter: H7's rule; dropping any target whose
     interaction point is off screen (outside 0–639 × 0–479); and whether
     targets the room class's `click()` accepts (the menu rooms' buttons)
     are included, as a proposed extension of H7 if they fall outside it.
   - Specify how the one `getHotspotPositions()` override serves both
     ScummVM's show-all display and Magnet's selected-target marker.
4. **Selection lifetime (plan §4.4, §5.6; H2 and H8 conditions).** Define how
   the selection is matched across refreshes using the adapter's identity,
   and what happens when it's gone. List the game-state changes that drop it
   (at least: room change, script start, input blocked, room class busy,
   target hidden, inventory, close-up), each tied to the TerraGlyph symbol
   that detects it, and say how a change is noticed (a hook at the change, or
   a cheap check each tick) without querying the list every frame (H8).
   Specify the activation-time re-check that makes a vanished or disabled
   hotspot impossible to activate.
5. **Modes and input (plan §6.1, §6.2; H1, H6).**
   - Specify Magnet mode and cursor mode as a state machine: every state, the
     events between them, and what each remote input (D-pad, OK short, OK
     held, BACK, MENU) does in each.
   - Specify the keymaps: names, actions, default bindings for the remote
     (`JOY_UP`…`JOY_CENTER`), a gamepad hat (`JOY_HAT_*`) and the Windows
     keyboard (keys that leave Sign In's typing intact), and how each is
     enabled and disabled. Because `setEnabled()` is per keymap, say how OK
     stays bound in cursor mode while the directions go back to the Virtual
     Mouse (for example a second keymap for OK that stays enabled).
   - Answer how OK clicks in cursor mode, and how the rooms that need a held
     button or a drag (Background list) are played: in which mode, and how
     OK gives press, hold and release there without colliding with H6's
     hold-to-switch.
   - Specify the hold timing contract against the Keymapper's event shape:
     timed from the action's first `EVENT_CUSTOM_ENGINE_ACTION_START` to its
     `_END`, repeats ignored, the threshold over 400 ms, no activation on a
     hold, and the same behavior from the remote, a gamepad hat and a
     keyboard. Say whether the switch fires when the threshold passes (a tick
     check) or at release.
   - Specify the hold reset on a nested event loop (a movie), the main menu
     opening, and a room change.
   - Specify where a held D-pad repeat reaches the core (the policy itself is
     packet 3's), and how Magnet mode avoids or handles the test-build D-pad
     gesture.
6. **Coordinates (plan §4.5).** Name the coordinate space each component
   works in (TerraGlyph's 640×480 screen, and room space for wide rooms), how
   the cursor is moved (the ScummVM call, the event it produces, and how
   TerraGlyph's own cursor sprite follows it), and any conversion the hotspot
   display or the Android overlay needs.
7. **Activation (plan §4.2 E).** Specify activation as a synthetic click
   through `handleMouse(false, p)` then `handleMouse(true, p)`, as
   `test_script` does, after the item 4 re-check. Record what blocks it
   (`handleMouse()`'s script, inventory and busy gates) and what the player
   sees when it's blocked.
8. **Configuration (plan §6.6, §7.4; H5).** Specify the extra option: its
   config key, label ("Hotspot Assist"), tooltip, `GAMEOPTION_` GUIO flag,
   default off, which detection entries carry it, and where the engine reads
   it. With it off, Magnet's keymaps aren't registered or stay disabled, and
   behavior is exactly today's.
9. **Feedback (plan §6.5, §12.6).** Specify how the selected target is shown
   in Phase 1 (the cursor's position alone, the hotspot renderer with a
   one-item list, or both), how it coexists with ScummVM's show-all display,
   and how the player can tell which mode they're in.
10. **Test hooks (plan §12).** Specify the self-test hook that lists a room's
    targets, and which room it builds on: `checkAllRooms`'s bare `Room` (no
    room class, toolbar or inventory, `terraglyph.cpp:2003-2010`) or the live
    `showRoom()` path (`:620-640`), which can evaluate H7's toolbar sprites and
    the click gate. Specify the `test_script` verbs a live run needs (a
    directional press, OK short and held, the mode), beside the existing
    `down x y` and `up x y` (`terraglyph.cpp:442-447`). The reachability
    check that uses the hook is packet 3's.
11. **The core's contract for packet 3.** State exactly what the directional
    algorithm receives (targets, current selection or none, the direction,
    whether the press is a repeat) and returns (the new selection or none).
12. **Decision register (plan §10.4).** Add a row, H9 onward, for each choice
    this design makes that H1–H8 don't cover, with alternatives, a
    recommendation and its evidence. Status is **proposed**; Jeff decides
    each. Part II marks each such choice "proposed (H*n*)".

### Out of scope

- **The directional algorithm**: scoring, tie-breaking, wrap-around, the
  reachability guarantee and its per-room check, and the held-D-pad repeat
  policy (plan §5.1–5.5, §5.7–5.8, §6.3). Packet 3. Item 11 fixes only the
  contract it works within, and item 10 only the hook it uses.
- **Any code.** No fork branch, no prototype. Appendix B holds design-level
  declarations; the implementation packets (4–8) write the engine C++ by
  hand and may change them, recording why.
- **Confirming E26's hold sequence inside ScummVM on the TV**, and whether
  the TCL's remote ever reports a press twice. Packet 6 (input integration),
  then packet 10 (Android TV validation).
- **Changing the test-build gesture.** It belongs to WP-085's advanced mode;
  item 5 says how Magnet lives with it, and any change is WP-085's or its
  successor's.
- **SCUMM/HE** (plan §3.6, Phase 2). Packet 12. The contracts must not
  preclude a second engine's provider, but no SCUMM detail is designed here.
- **Shared-code extraction and maintainer contact** (plan §9, §13; H4).
  Packets 13 and 15.
- **Device validation** on the TCL, the Sony Bravia or the Raspberry Pi.
  Packets 9–11.

## Dependencies

- The fork at `C:\dev\scummvm`, read only, through `git show` and `git grep`
  against the pinned commit. Never switch branches in the shared checkout,
  and create no fork branch (exit criterion 15).
- The plan page on `main` after this draft merges (H1–H8 as decided at
  `2bdbe6a`).
- No device. The TV findings needed (E22, E25, E26) are already in.

## Investigation plan

EC-012 runs: pin and drift; the source reads the design rests on; then the
design sections (hotspot record and provider, components, selection lifetime
and activation, modes and input, coordinates, configuration, feedback, test
hooks); then the core's contract once the input path is fixed; then the
register rows; then the write-up and close. Each source fact goes in the
evidence register as E27 onward as it is found.

## Output specification

All output goes into the [plan page](../reference/hotspot-magnet-plan.md),
plus the dashboard note at close:

- **§3.8 evidence register:** E27 onward, and the refreshed E3, E8 and E9.
- **§4.2–4.6:** each component's contract, the hotspot record and the
  provider, replacing the open questions in §4.4 and §4.5 with answers.
- **§5.6:** the selection-lifetime rules. §5.1–5.5 and §5.7–5.8 stay for
  packet 3.
- **§6.1–6.2, §6.5–6.6:** the mode state machine and remote table, the
  keymaps and hold contract, the feedback, and the option.
- **§7.4:** the option's Phase 1 details.
- **§12:** the test hooks and `test_script` verbs.
- **§10.4 decision register:** H9 onward, proposed.
- **Appendix B:** the design-level declarations of item 2.
- **Appendix D:** the terms the design uses (hotspot, target, selection,
  interaction point, Magnet mode, cursor mode, provider, adapter).
- **§11:** packet 2 marked done once this WP closes; **§14.3** next steps.
- **`dashboard.json`:** the `tv-dpad` note, at close.

## Exit criteria

1. The pinned fork commit is recorded in §3.8, with every Appendix A file and
   every file changed since `ff490ad9449f` compared, each change that alters
   a finding or citation named, and E3, E8 and E9 refreshed.
2. Each component A–E has its inputs, outputs, owner and trigger in
   §4.2–4.3, and a declaration in Appendix B with no function bodies.
3. Appendix B's components B and C name no TerraGlyph type or symbol.
4. The hotspot record is mapped field by field to `Graphics::HotspotInfo`,
   with the points-or-box choice argued, and the adapter's identity kept
   outside `HotspotInfo` (or raised as H2 (b)).
5. The provider's filter is specified: H7's rule, the off-screen drop, the
   room-class targets decision, and the H3 point search with its box, grid
   step and accessor.
6. The one-override, two-consumer question (show-all display and Magnet's
   marker) has an answer.
7. The selection-lifetime rules name the identity used across refreshes, list
   at least item 4's game-state changes, each with the symbol that detects it
   and how the change is noticed, and specify the activation re-check (H8).
8. The mode state machine lists every state and transition, and a table gives
   what D-pad, OK short, OK held, BACK and MENU do in each mode, including how
   OK clicks in cursor mode.
9. The keymaps are specified (names, actions, bindings for the remote, a hat
   and the Windows keyboard, enabling), with OK bound in cursor mode and Sign
   In's name entry still receiving every key it reads today.
10. The rooms that need a held button or a drag each have a stated way to be
    played with the remote alone, compatible with H6.
11. The hold timing contract is stated against the Keymapper's event shape
    (first start to end, repeats ignored, threshold over 400 ms, no
    activation on a hold), for the remote, a hat and a keyboard, with when
    the switch fires and the resets on a movie, the main menu and a room
    change.
12. The test-build D-pad gesture has a stated handling, and the point where
    a D-pad repeat reaches the core is named.
13. Each component's coordinate space, the cursor call and how TerraGlyph's
    cursor sprite follows it, activation through `handleMouse()` with what
    blocks it and what the player sees, and the option (key, label, tooltip,
    flag, entries, default, read site, off-state) are specified, each source
    fact cited in the evidence register.
14. The feedback (selected target and mode), the test hooks (which room the
    listing hook builds on, and the `test_script` verbs) and the core's
    contract for packet 3 (inputs and output) are specified.
15. Every Part II statement marked "proposed (H*n*)" has a matching §10.4 row,
    every H9+ row is cited from Part II, and none is marked settled.
16. `git diff --name-only main` lists only the plan page, this WP, EC-012,
    `WORK_INDEX.md` and `dashboard.json`; the fork has no new branch or commit
    from this WP.
17. The wiki's strict build passes
    (`hugo --config ewiki/hugo.toml --minify --panicOnWarning`).

## Deliverables

- **Committed:** the plan page's §3.8, §4, §5.6, §6, §7.4, §10.4, §11, §12,
  §14.3 and Appendices B and D; this WP's status and findings links; EC-012
  with its outcomes; the WORK_INDEX row; the `dashboard.json` note.
- **Local only:** scratch notes.

## Notes

- **Hand-written engine code.** The plan's §14.1 holds that all engine C++ is
  written by hand. Appendix B's declarations are design text, a contract for
  the implementation packets, not code to paste; packets 4–8 write the code
  and record any departure from them.
- **Design, not decisions.** Where the design must choose, it recommends and
  records the choice as a proposed H-row. Part II states the recommendation
  as the design, marked "proposed (H*n*)", until Jeff decides.
- **One engine, two in view.** The contracts serve TerraGlyph only, but
  nothing in components B or C may assume TerraGlyph, so Phase 2 can add a
  SCUMM provider without changing them (plan §4.1).
- **Copyright.** Findings cite ScummVM's GPL source by path and symbol and
  quote only short identifiers.

## Close (2026-11-27)

| # | Exit criterion | Met | Evidence |
|---|---|---|---|
| 1 | Pin, drift, E3/E8/E9 refreshed | ✅ | Plan §3.8: fork `0d5a69c7694f`; `git diff --stat ff490ad9449f` lists 12 files, all WP-085's Android work; `android.cpp` +6 lines at 363, E3/E8/E9 cite new and old lines; the Android key intercept is E33 |
| 2 | Contracts A–E and Appendix B | ✅ | Plan §4.2 contracts table; Appendix B, declarations only |
| 3 | B and C name no TerraGlyph symbol | ✅ | Appendix B: `HotspotMagnet::navigate` and `InputAdapter` use only `Graphics::HotspotInfo`, `Common::Array` and `uint32` |
| 4 | Record mapped to `HotspotInfo`; points or box; identity outside | ✅ | Plan §4.3 (field table, points only); identity (room, sprite index) beside the list; H12 |
| 5 | Provider filter and point search | ✅ | Plan §4.6 (H7, H13, on screen) and §4.5 (box, centre then 4 px rings, `Room::getHitBox()`, cache); E36, E37 |
| 6 | One override, two consumers | ✅ | Plan §6.5: one list serves the show-all display and Magnet; a marker would replace the display while shown (E32); H14 |
| 7 | Selection lifetime and re-check | ✅ | Plan §4.4: identity, the drop table with each signal and how it's noticed (E38), the activation re-check |
| 8 | Mode state machine and per-mode table | ✅ | Plan §6.1 table (D-pad, OK short and held, BACK, MENU per mode) and §6.2 (states, transitions, OK in cursor mode) |
| 9 | Keymaps | ✅ | Plan §6.4: three keymaps with standard action ids, bindings for the remote, hats and the keyboard, enabling; keypad Enter keeps Sign In whole (E43); a raw SDL hat isn't mappable (E44); H16 |
| 10 | Held-button and drag rooms | ✅ (with a gap) | Plan §6.8: each room's input (E35) and how it's played. Six are played in Magnet or cursor mode; the Options knobs, Brad's game and the vault's clock need room assists (H11), which are proposed but not designed or scheduled. Until then they're Phase 1 gaps, playable with a mouse or a gamepad holding `JOY_X` (6.4) |
| 11 | Hold timing contract | ✅ | Plan §6.2: first start to end, repeats ignored, 600 ms (H10), switch at the threshold by tick, resets on room change, movie and pause (E29, E30, E40) |
| 12 | Test-build gesture; repeat entry point | ✅ | Plan §6.3: H15; repeats are the input adapter's own, the same on every device, passed to the core with a flag (§4.3) |
| 13 | Coordinates, cursor, activation, option | ✅ | Plan §4.5 (one space, off-screen drop, warp then push, E31, E37, E39); §4.2 activation, engine-owned so its release can't be lost, and what blocks it (E34, E40, H9); §6.6 option table (E42) |
| 14 | Feedback, test hooks, core contract | ✅ | Plan §6.5 (H14); §12.7 (the listing hook on `showRoom()` after the opening, with unpointed sprites reported; the `test_script` verbs calling the adapter, since pushed events aren't mapped, E41, E44); §4.3 core contract, with the cursor's position |
| 15 | Every "proposed (H*n*)" has a row, every H9+ row cited | ✅ | Checked by script over Part II: rows H9–H16 all cited; no citation without a row |
| 16 | Only the five allowed files; no fork branch | ✅ | `git diff --name-only main` lists the plan page, WP-089, EC-012, `WORK_INDEX.md` and `dashboard.json`; the fork was read through `git show`/`git grep` only |
| 17 | Strict wiki build passes | ✅ | `hugo --config ewiki/hugo.toml --minify --panicOnWarning`, 0 warnings |

**Cold review.** A second read of the design against the source found real holes, all fixed before close: activation now owns its press instead of pushing events (a pushed release can be lost, H9); the click gate and an item in hand are back in the filter (§4.6); repeats are the adapter's own; the core gets the cursor's position; room-class targets have an identity; and off the TV the D-pad doesn't move the Virtual Mouse (§6.1, E44).

**Corrected on the way.** WP-086 recorded that Android gives the D-pad to the
Virtual Mouse in a game. That's true only for an engine whose game keymaps
leave the D-pad unbound. ScummVM's default game keymap, which TerraGlyph has
today, binds it to keypad arrow keys (E27; plan §3.2 carries the correction).
H1 still holds, because TerraGlyph's own keymaps replace the default.

**For the next packets.** H9–H16 are Jeff's to decide. Packet 3 designs the
algorithm against the core's contract (plan §4.3) and the listing hook
(§12.7). If Jeff takes H11, plan §11 gains a packet for the room assists.
Two facts are inferred from source and need the TV (packet 6, then 10): that
the D-pad does nothing in a TerraGlyph game today (E27), and that Android's
warp produces no mouse event (E31).
