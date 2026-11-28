---
layout: default
title: "Hotspot Magnet — directional hotspot navigation plan"
---

# Hotspot Magnet: directional hotspot navigation

> **Status:** Planning baseline. The research in [Section 3](#3-existing-scummvm-architecture-research-findings)
> is done for everything except SCUMM/HE
> ([WP-086](../work-packets/WP-086-hotspot-magnet-research.md), 2026-11-26).
> Jeff decided H1–H5, H7 and H8 in [§10.4](#104-open-design-decisions) the
> same day, and H6, the cursor fallback, on 2026-11-27 after the TCL remote
> capture. Part II is designed for the Phase 1 TerraGlyph prototype
> ([WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md),
> 2026-11-27), except the directional algorithm (packet 3); its new choices
> H9–H16 wait on Jeff. Nothing here is built.
> **Date:** 2026-11-26 ([Revision history](#revision-history)). **Author:**
> Jeff (with AI assistance).
>
> **Primary prototype:** the TerraGlyph engine. **Secondary integration:**
> SCUMM / Humongous Entertainment. **Long-term objective:** a shared ScummVM
> accessibility feature (a goal, not a dependency).

**Related pages:** [WP-008 `object.ini` catalog](../work-packets/WP-008-object-ini-catalog.md) ·
[WP-018 hotspots and exits](../work-packets/WP-018-hotspots-and-exits.md) ·
[WP-021 clickable actions](../work-packets/WP-021-clickable-actions.md) ·
[WP-085 Google TV app pipeline](../work-packets/WP-085-tv-app-pipeline.md) ·
[ScummVM on smart TVs](scummvm-smart-tv.md) ·
[ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md) ·
[Upstream submission decision brief](upstream-submission-decision-brief.md)

---

## Part I — Research and requirements

### 1. Executive summary

Conventional D-pad cursor movement on televisions (ScummVM's Virtual Mouse)
is continuous and imprecise. Young children and players with motor
impairments struggle to stop the cursor exactly on small interactive objects.
Jeff saw this on the TCL 65Q77K on 2026-11-26: the D-pad moves ScummVM's
pointer but lacks the fine movement needed to click a button or object
([WP-085 D2](../work-packets/WP-085-tv-app-pipeline.md#decisions-for-jeff)).

**Why it matters for the TV app.** Google's TV app quality rules require an
app to be navigable with a five-way D-pad unless it requires a game controller.
Because the D-pad pointer can't click reliably, WP-085 chose "gamepad required"
for the Play release and left D-pad-only control as its open remote-first
item. Hotspot Magnet is that item: if it makes the games playable with the
standard remote, a later release could reconsider that requirement.

**Hotspot Magnet** is a directional, hotspot-to-hotspot navigation system.
The four D-pad directions move the selection from one currently interactive
hotspot to the next; OK/Select activates it. A clear fallback to conventional
cursor movement stays available at all times.

**Audiences**

- Primary: young children using a standard TV remote.
- Secondary: players with motor impairments.

**Three-phase strategy**

1. A working TerraGlyph prototype (valuable on its own).
2. Reuse of the same navigation core in one SCUMM/HE title.
3. Extraction into shared ScummVM code and an upstream contribution attempt.

Upstream acceptance is an external decision. The project succeeds if Phase 1
(and ideally Phase 2) delivers a reliable, optional feature even if
shared-code integration is declined or delayed.

### 2. Goals, requirements, and scope

#### 2.1 Functional goals

- Navigate between interactive hotspots using four D-pad directions.
- OK/Select activates the selected hotspot (left-click equivalent).
- Support secondary actions (right-click / alternate verb) where the engine
  allows.
- Instant fallback to conventional Virtual Mouse / free-cursor movement,
  reachable with the standard remote alone ([6.2](#62-cursor-mode-fallback-requirement)).
- Every eligible hotspot reachable by directional input
  ([5.8](#58-hotspot-reachability)).
- Work across multiple ScummVM engines via engine-supplied hotspot data.
- Optional visual indication of the selected hotspot.

#### 2.2 User experience goals

- Simple enough for young children.
- No mouse or keyboard required for normal play.
- Predictable, deterministic directional navigation.
- Minimal parent configuration (a single per-game checkbox).
- Impossible to become permanently trapped in Magnet mode.

#### 2.3 Non-functional requirements

- The navigation algorithm is engine-independent.
- Low processing overhead (expected hotspot counts are small).
- Compatible with ScummVM coding conventions and the Keymapper.
- Zero behavior change when the feature is disabled.
- Correct handling of different game resolutions and display scaling.
- Deterministic tie-breaking and scoring.

#### 2.4 Out of scope

- Replacing ScummVM's Keymapper or Virtual Mouse.
- Modifying original game assets.
- Automatic image recognition of clickable objects.
- Requiring every engine to support the feature.
- Rewriting engine-specific interaction systems.
- Guaranteeing upstream acceptance.

### 3. Existing ScummVM architecture: research findings

**Verified by [WP-086](../work-packets/WP-086-hotspot-magnet-research.md)
on 2026-11-26**, except 3.6 (SCUMM/HE, a later packet). Every finding cites
the fork at `origin/scooby-engine` **`ff490ad9449f`**, and each has a row in
the [evidence register](#38-research-evidence-register) (E1, E2, …). Gen 1
means *Showdown* and *Phantom*; the shared-code findings carry no generation.

**What the research changes.** Three findings matter most to the design:

- **The remote's D-pad reaches ScummVM as joystick buttons, and a game can
  take it over** (3.1, 3.2). Android binds those buttons to the Virtual Mouse
  in the Global keymap, and an exact match in the game's keymap is checked
  first, so an engine keymap that binds them gets them instead. Turning that
  keymap off hands the D-pad back to the Virtual Mouse.
- **ScummVM already has an engine hotspot interface,
  `Engine::getHotspotPositions()`, and five engine implementations fill it**
  (3.3), SCUMM's among them. Each returns a point that is checked to hit the
  object, which is the interaction point the design needs. TerraGlyph doesn't
  implement it yet.
- **TerraGlyph already has a single click path,
  `TerraglyphEngine::handleMouse()`, which the test script drives with
  synthetic clicks** (3.5). Activation can go through it unchanged.

#### 3.1 Keymapper and input events

- **Dispatch** (E1). `EventDispatcher::dispatch` passes each event to
  `Keymapper::mapEvent`. That runs `getMappedActions` on the enabled keymaps
  of the current type (Game or GUI), and `Keymapper::executeAction` builds the
  output events. An unmapped event goes through raw, and any match swallows
  the raw event.
- **Priority** (E2). Game (or GUI) keymaps are searched first. The Global
  keymap is searched only when that first pass has no exact match. Joystick
  inputs always match exactly when bound. Game and GUI keymaps are never
  searched together.
- **Can an engine keymap take the D-pad from the Virtual Mouse? Yes** (E2,
  E3). The Virtual Mouse's D-pad bindings live in the Global keymap. While a
  game runs, an enabled game keymap that binds `JOY_UP`/`DOWN`/`LEFT`/`RIGHT`
  matches first, so the Virtual Mouse never sees those presses. Its other
  bindings (the left stick) keep working. In ScummVM's own menus, game keymaps
  aren't searched, so the D-pad moves the pointer there as before.
- **The Virtual Mouse** (E4). Its actions are `VMOUSEUP`, `VMOUSEDOWN`,
  `VMOUSELEFT`, `VMOUSERIGHT` and `VMOUSESLOW`. **It has no click action**: an
  in-game left click is the engine-default `LCLK` on `MOUSE_LEFT`/`JOY_A`. It
  moves the pointer at a constant velocity every 12 ms (no acceleration),
  scaled by `kbdmouse_speed` and `joystick_deadzone`. It is always built on
  Android, with no enable flag (E5).
- **Precedent for an engine-defined action:** the hotspot display's
  "Show/hide hotspots" action is added by each engine through
  `MetaEngine::createHotspotAction()` (E11).

#### 3.2 Android TV and gamepad input

- **D-pad and OK** (E6). `ScummVMEvents.onKey` sends `DPAD_UP`, `DOWN`,
  `LEFT`, `RIGHT` and `CENTER` as `JE_GAMEPAD`. The native side turns them
  into `EVENT_JOYBUTTON_DOWN`/`UP` with `JOYSTICK_BUTTON_DPAD_*`, which are
  the hardware inputs `JOY_UP` … `JOY_CENTER`. They are **not key events, not
  hat axes and not mouse movement**. Android's defaults bind the four
  directions to the Virtual Mouse (Global keymap) and `JOY_CENTER` to
  "interact" in the GUI only. **In a game, `JOY_CENTER` is unbound**, so the
  engine receives it raw. `ENTER` from a keyboard arrives as `KEYCODE_RETURN`.
  **Correction (WP-089, E27):** the Virtual Mouse gets the D-pad in a game
  only if no game keymap binds it. ScummVM's default game keymap does, to
  keypad arrow keys, and it's the keymap TerraGlyph has today, so in a
  TerraGlyph game the D-pad sends keys the engine ignores. *Beneath a Steel
  Sky* declares its own keymap without the D-pad, which is where the pointer
  moves. H1 still holds: TerraGlyph's own keymaps replace the default (6.4).
- **Gamepad hat D-pads** arrive separately, as `EVENT_JOYAXIS_MOTION` on the
  hat axes (E6). A design that binds the remote's buttons doesn't cover a
  game controller's D-pad, which needs its own binding.
- **The old D-pad-to-mouse code is dead** (E6). The native `JE_DPAD` path,
  which emulated the mouse with acceleration, is commented "no longer used",
  and Java never sends that event.
- **Holding a key** (E7). Key events carry a repeat count, and the Keymapper
  drops repeats. `JE_GAMEPAD` ignores the count, so if the remote repeats a
  held D-pad press, each repeat arrives as a fresh `JOYBUTTON_DOWN`. On the
  TCL the remote itself doesn't repeat, but Android does (3.2 remote, below).
  Long-press detection exists only for BACK and MENU.
- **Keys the backend uses itself** (E8):

  | Key | Short press | Long press |
  |---|---|---|
  | BACK | `KEYCODE_AC_BACK`: skip (ESC) in a game, close in the GUI | `KEYCODE_MENU`: ScummVM's main menu |
  | MENU | ScummVM's main menu | Toggles the on-screen keyboard |
  | Volume up/down | Left to Android | — |
  | Play/pause | `VMOUSESLOW` (Virtual Mouse slow) | — |
  | Gamepad START / SELECT | Main menu / virtual keyboard | — |

- **Pointer Speed** is `kbdmouse_speed` (default 2 on Android), read only by
  the Virtual Mouse. There is no cursor-acceleration setting (E9).
- **The on-screen gamepad** (`touchcontrols.cpp`) becomes active only from
  touch input, so on a TV with no touch screen it never shows and never takes
  input (E10).
- **Upstream drift** (E21). Since the fork's base (`2982fe324b6c`),
  `scummvm/scummvm` master (`7b6fa644d74a`, 2026-11-26) changed only
  `735ad86c21` among these files: mouse pointer capture with relative motion.
  It changes no D-pad or key finding.

**The TCL 65Q77K's remote** (E22, E25, E26). Captured with `getevent -lt` on
2026-11-26 and 2026-11-27 (Android 14):

| Button | Kernel key | HID usage (page 0x0C) | Short press | Held 3.4–4.3 s |
|---|---|---|---|---|
| D-pad up | `KEY_UP` | `0x42` | one press, one release | — |
| D-pad down | `KEY_DOWN` | `0x43` | same | — |
| D-pad left | `KEY_LEFT` | `0x44` | same | one press, one release |
| D-pad right | `KEY_RIGHT` | `0x45` | same | one press, one release |
| OK | `KEY_SELECT` | `0x41` | same | one press, one release (three holds) |
| BACK | `KEY_BACK` | `0x224` | same | — |

Short presses last 0.10–0.20 s. **The remote never repeats**: a held button
sends one press and one release, nothing between. **Android does repeat.**
`dumpsys input` shows `HandlesKeyRepeat: false` for every input device, with
`KeyRepeatTimeout: 400ms` and `KeyRepeatDelay: 50ms`, so Android's input
dispatcher adds a repeated key-down 400 ms into a hold and then every 50 ms.
ScummVM's `JE_GAMEPAD` path ignores the repeat count (E7), so **a held OK
reaches the engine as `JOYBUTTON_DOWN`, repeated every 50 ms after 400 ms,
then one `JOYBUTTON_UP`** at release. This is inferred from the kernel
capture, the dispatcher settings and the source, not observed inside
ScummVM. A held D-pad direction does the same, which matters for navigation
([6.3](#63-standard-tv-remote-limitations)).

For H6, a hold of OK can be timed from the first `JOYBUTTON_DOWN` to the
`JOYBUTTON_UP` if the engine ignores repeated downs while the button is
already down. MENU and Home weren't pressed in either capture. MENU is
already taken (E8) and Home never reaches an app, so neither is needed for
H6. The remote was `/dev/input/event7` in the first capture and
`/dev/input/event9` in the second (the TV had restarted), so a tool must find
it by name, not by node. The first 3-minute capture had no presses. What it did show: `getevent`
works over adb without root, and the TV's input devices are the Bluetooth
remote `BT_RC923A_B1 Consumer Control` (`/dev/input/event7`), a
`virtual-remote`, the `MTK Smart TV IR Receiver`, the TV keypad, a
`gIrTouch_Mouse` and a `virtual-search` device. The remote's HID report lists
about 150 possible keys, many more than its buttons, so only presses show
which exist.

#### 3.3 Existing hotspot navigation and display features

- **The data: `Graphics::HotspotInfo` is a point, a name and a type** (E12):
  `Common::Point position` ("in game coordinates"), `Common::U32String name`,
  and `HotspotType type` (default, object, exit or NPC). It has no rectangle
  and no identifier.
- **The engine interface** (E13). `Engine::getHotspotPositions(Common::Array<HotspotInfo> &)`
  is empty by default. `Engine::drawHotspots()`, which each implementing
  engine calls once per frame, asks for positions only when `hotspotDirty()`
  (default: every frame), creates the renderer lazily and draws to the
  overlay. `showHotspots()` turns the display on and off, and pausing or
  opening the GUI suspends it.
- **The key and the setting** (E11, E14). The "Show/hide hotspots" action
  (`HOTS`, key `h`) sends `EVENT_HOTSPOTS_SHOW` on press and `…_HIDE` on
  release. `DefaultEventManager` handles both as hold or toggle (the
  `hotspot_key_mode` setting) and doesn't pass them to the engine. The
  per-game `enable_hotspots` checkbox sits in the edit-game dialog's Misc tab
  for every game, and defaults to **off**. An engine opts in by adding the
  action in its `initKeymaps` only when `hotspotsEnabled(target)`; there is
  no feature flag.
- **The renderer** (E15) draws markers (crosshair, square or point), leader
  lines and labels at the given points, scaled from game to overlay size. It
  draws no outlines, ignores `type`, and always draws the whole list it's
  given. **It can draw one selected target only by being given a one-item
  list**, and it has no selected style. It draws through the generic overlay
  API; no backend has hotspot-specific code.
- **Who fills it** (E16): five engine implementations, each returning only
  interactive things, and each placing the point so it hits the object:

  | Engine | What it returns | How the point is chosen |
  |---|---|---|
  | `scumm` (v0–v8 and HE; the HE sports games, rebel1/2 and moonbase are excluded at the keymap) | Touchable objects in view, and visible actors other than the player | The first point of a 3 × 3 grid over the object where `findObject()` returns that object |
  | `touche` | Hit boxes not locked or hidden, and characters | The rectangle's centre, or the centre of its visible part |
  | `hollywood` (both games) | Named hotspot ids found by scanning the viewport | The bounding box's centre, or the nearest pixel of the region if the centre falls outside |
  | `macs2` | Colour-map regions and scene objects | Each region's centroid, snapped into the region |

- **Data reuse or visual reuse? Both, with limits.** For **data**,
  `getHotspotPositions()` is usable as the Hotspot Magnet provider as it
  stands: its points are hit-checked interaction points, and directional
  navigation can run on points alone. It lacks a stable identifier, which
  keeping a selection across refreshes would want; an addition may be needed
  there. For **visuals**, the renderer can mark one target if given a
  one-item list, but it has no highlight style, and it shares the overlay with
  the show-all display.
- **Other navigation** (E17). **Lab** is the only engine that moves the
  cursor between interactive items: its "FOCUS" action (TAB / `JOY_X`) moves
  the mouse to the centre of the next close-up in its list, wrapping. Its
  logic is tied to Lab's data. Riven's arrow keys run named hotspots
  ("forward", "left") without moving the cursor. MADS's tab swaps the cursor
  between two saved positions. Grim cycles objects through script keys
  (unverified past the key events). AGOS and Sword25 only reveal all
  hotspots. **None is reusable as a navigation core.**
- Two small inaccuracies in the fork, recorded for the record: the comment at
  `engines/engine.h:560` says the markers are "semi-transparent circles", but
  the default is a crosshair, and `HotspotType` is never used in drawing.

#### 3.4 Shared component conventions

What already lives where (E11–E15):

| Location | What's there now | Fit for Hotspot Magnet |
|---|---|---|
| `common/` | General utilities | Could hold a pure point-navigation function, but nothing hotspot-related lives there |
| `gui/` | The `enable_hotspots` checkbox and its sibling options (edit-game dialog) | The shared setting, in Phase 3 |
| `engines/` | `Engine::getHotspotPositions()`, `drawHotspots()`, `showHotspots()`; `MetaEngine::createHotspotAction()` and `hotspotsEnabled()` | **The data source and the action pattern** |
| `backends/keymapper/` | The Virtual Mouse and the Keymapper | Only the bindings; a navigation action is an engine-level action, as `HOTS` is |
| `graphics/` | `HotspotInfo`, `HotspotRenderer` | The selected-target marker |

**Recommendation (proposed):** `engines/`, beside the hotspot display. Its
input is `getHotspotPositions()`, its action follows `createHotspotAction()`,
and its marker can come from `graphics/hotspot_renderer`. Keep the directional
algorithm a standalone class with no engine dependency, so it can be tested
without an engine. Phase 1 still prototypes inside `engines/terraglyph/`
(7.1); this is where the shared extraction would land.

#### 3.5 TerraGlyph hotspot data

From earlier packets, Gen 1: `object.ini` names the objects and their kinds
([WP-008](../work-packets/WP-008-object-ini-catalog.md)), and hits test step
polygons or cel pixels, front to back
([WP-018](../work-packets/WP-018-hotspots-and-exits.md)). In the source:

- **Hit testing** (E18). `Room::hitTest(x, y)` returns a **sprite index**
  into the room's sprites, or −1. It walks the private draw list front to
  back, skips a sprite that is `hidden` or has `hitType` 0, tests the current
  step's polygon (type 2) or the current frame's cels (type 1), and returns
  the first hit. Detached sprites aren't in the list. The cursor is a
  separate sprite and is never hit.
- **The placements** (E18). Each is a private `Room::Sprite` with a `Kind`
  (layer, simple, character, ghost, exit, requires, inventory, clickable,
  engine). A room's class can override the kind. They are listed through
  `getSpriteCount()` and per-index accessors: `getLabel`, `getMode`,
  `getStep`, `isHidden`, `getHitType`, `isDetached`, `getDestination` (an
  exit is a sprite with a destination), `isClickable`, `isInventoryObject`,
  `isRequiresObject`, `isEngineSprite`, `getCharacters()`. Geometry is
  `getFrameRect()` (first cel only) or `getSize()`; **the polygon and its
  bounding box are private** (`getPolygon`), so an interaction-point search
  over a polygon needs a small accessor.
- **One room, gated input** (E19). Play uses a single `Room` object. The
  toolbar's sprites are added to it at depth 5000, so `hitTest()` covers the
  toolbar too, and close-ups and Big Head are rooms loaded into the same
  object. Nothing reroutes input. Instead `TerraglyphEngine::handleMouse()`
  drops clicks while a script runs or the inventory blocks input, and turns a
  click into a skip while the room's class is busy.
- **The click path** (E20). `TerraglyphEngine::handleMouse(bool click, Point)`
  updates the hover through `hitTest()` and then hands the click on, in
  order: character, room class, inventory, hint, then exit or clickable. **The
  `test_script` `click x y` command already calls `handleMouse(false, p)` and
  then `handleMouse(true, p)`**: a synthetic click through the real path.
- **Headless listing: yes** (E20). The self-test's `checkAllRooms` builds a
  bare `Room` (no room class, no toolbar) and hit-tests a 4-pixel grid; other
  checks drive the live room with `hitTest(x, y) == sprite`. The accessors
  above are enough to list each room's sprites headlessly.

**Proposed eligibility rule** (Gen 1, from E18–E20): a sprite is a target
when it is not hidden, not detached, has `hitType` ≠ 0, and is an exit (has a
destination), a clickable, a requires object, an inventory object or a
toolbar sprite; **and** `handleMouse()` would accept a click now (no script
busy, input not blocked, room class not busy). Leave out simple sprites, which
are hittable but do nothing, and the ghost. **Characters:** the engine passes
a click to `clickCharacter()` only with the arrow cursor, and whether that
does something in every room is unverified, so leave them out at first and
revisit.

**Proposed interaction point:** search the sprite's polygon bounding box (or
cel rect) on a small grid, centre first, and keep the first point where
`hitTest()` returns that sprite, as SCUMM does with `findObject()`. A sprite
with no such point (fully covered by another) isn't eligible.

#### 3.6 SCUMM / Humongous Entertainment

Not researched yet (the SCUMM/HE research packet). One lead from 3.3: SCUMM
already implements `getHotspotPositions()` for v0–v8 and HE, with
hit-checked points (E16).

#### 3.7 Per-game configuration

- **The engine mechanism** (E23). An engine declares a per-game checkbox as
  an `ADExtraGuiOptionsMap` entry (a GUIO flag plus an `ExtraGuiOption`:
  label, tooltip, config key, default) returned from
  `getAdvancedExtraGuiOptions()` on its meta-engine. The option shows only for
  detection entries whose GUIO list has the flag (`GUIO_GAMEOPTIONSn`), it's
  saved in the game's own config domain, and `registerDefaultSettings()`
  registers its default, so the engine just calls `ConfMan.getBool(key)`.
  Example: Awe's `copy_protection` (`engines/awe/metaengine.cpp`,
  `detection_tables.h`).
- **TerraGlyph today** (E24). It declares no extra options: its meta-engine
  overrides only `getName`, `createInstance` and `hasFeature`, and every
  detection entry has only `GUIO1(GUIO_NOMIDI)`. A default-off "Hotspot
  Assist" would go in an override of
  `TerraglyphMetaEngine::getAdvancedExtraGuiOptions()`
  (`engines/terraglyph/metaengine.{h,cpp}`), with a `GAMEOPTION_` flag added
  to the entries in `detection_tables.h`.
- **The shared model** (E14). `enable_hotspots` is the other pattern: a
  shared per-game key in the edit-game dialog for every game, with each
  engine opting in through its keymap. **Proposed:** the engine option for
  Phase 1, and a shared key on the `enable_hotspots` model for Phase 3.

#### 3.8 Research evidence register

Pinned commits: fork `origin/scooby-engine` **`ff490ad9449f`** for E1–E26;
upstream `scummvm/scummvm` master **`7b6fa644d74a`** (2026-11-26), merge
base `2982fe324b6c`. E27 onward (WP-089) are at fork **`0d5a69c7694f`**
(2026-11-27). Between the two fork pins only WP-085's four commits landed
(fork PR #13), all Android: no keymapper, event, hotspot or TerraGlyph file
changed. `android.cpp` gained six lines at 363, so E3, E8 and E9 cite the new
line numbers with the old ones beside them. Paths are in the fork.

| # | Section | Source (file, symbol) | Verified behavior | Implication for Hotspot Magnet | Still unverified |
|---|---|---|---|---|---|
| E1 | 3.1 | `common/events.cpp` `EventDispatcher::dispatch`; `backends/keymapper/keymapper.cpp` `Keymapper::mapEvent`, `getMappedActions`, `executeAction`; `keymap.cpp` `Keymap::getMappedActions`, `loadMappings` | Events map to actions through enabled keymaps; unmapped events pass raw; a match swallows the raw event | Navigation can be Keymapper actions, rebindable like any other | — |
| E2 | 3.1 | `keymapper.cpp:183-199` `Keymapper::mapEvent`; `keymap.cpp:240` | Game/GUI keymaps first; Global only without an exact match; joystick inputs match exactly | An engine keymap wins over the Virtual Mouse for the same buttons | — |
| E3 | 3.1, 3.2 | `backends/platform/android/android.cpp:748-760` `getKeymapperDefaultBindings` (`:742-754` at `ff490ad9449f`); `hardware-input.cpp:266-270` | Android binds `VMOUSE*` to `JOY_UP`…`JOY_RIGHT` in the Global keymap and GUI interact to `JOY_A`, `JOY_CENTER`, `SELECT` | Binding the D-pad in a game keymap takes it from the Virtual Mouse; disabling that keymap gives it back | — |
| E4 | 3.1 | `backends/keymapper/virtual-mouse.cpp` `addActionsToKeymap`, `handleAxisMotion`, `pollEvent`, `computeJoystickMouseSpeedFactor`; `engines/metaengine.cpp:97-101` | Five movement actions, no click; constant velocity every 12 ms; in-game click is `LCLK` on `MOUSE_LEFT`/`JOY_A` | Conventional cursor mode is the Virtual Mouse as it is | — |
| E5 | 3.1 | `backends/events/default/default-events.cpp:57`; `android.cpp:457`, `:364` | The Virtual Mouse is always built on Android; `kbdmouse_speed` defaults to 2 | No enable step needed for the fallback | — |
| E6 | 3.2 | `ScummVMEvents.java:519-545` `onKey`; `events.cpp:1243-1337` (`JE_GAMEPAD`), `:613-617` (`JE_DPAD`), `:1359-1369` (`JE_JOYSTICK`) | D-pad keys become `JOYBUTTON` events; `JOY_CENTER` is unbound in games; hat D-pads are axis events; `JE_DPAD` is dead | Bind `JOY_UP`…`JOY_CENTER` for the remote; a gamepad hat needs `JOY_HAT_*` too | — |
| E7 | 3.2 | `ScummVMEvents.java:446`, `:456-486`, `:593`; `events.cpp:422-424`; `keymapper.cpp:308` | Key repeats are flagged and dropped; gamepad repeats arrive as new presses; long press only for BACK and MENU | A held OK can be timed from `JOYBUTTON_DOWN` to `UP` in the engine | Whether the TCL's remote repeats a held press |
| E8 | 3.2 | `ScummVMEvents.java:238-261`, `:423-441`, `:508-511`; `android.cpp:717`, `:734`, `:739` (`:711`, `:728`, `:733` at `ff490ad9449f`); `events.cpp:678-718`, `:1261` | BACK, MENU, volume, play/pause and START/SELECT are taken (table in 3.2) | The fallback can't use BACK or MENU without losing skip, the main menu or the keyboard | — |
| E9 | 3.2 | `gui/options.cpp:290`, `:970`, `:1446`; `android.cpp:598` (`:592` at `ff490ad9449f`); `virtual-mouse.cpp:204` | Pointer Speed is `kbdmouse_speed`; no acceleration setting | Magnet mode doesn't need to touch pointer settings | — |
| E10 | 3.2 | `touchcontrols.cpp:214`, `:241-281`; `ScummVMEvents.java:720-745`; `options.cpp:496-527` | The on-screen gamepad activates only from touch | No conflict on a TV | — |
| E11 | 3.1, 3.3, 3.4 | `engines/metaengine.cpp:73-78` `createHotspotAction`, `:80-85` `hotspotsEnabled`; `standard-actions.cpp:44` | `HOTS` action, key `h`, added by each engine in `initKeymaps` when enabled | The pattern for a shared navigation action | — |
| E12 | 3.3 | `graphics/hotspot_renderer.h:41-60` `HotspotType`, `HotspotInfo` | Position, name, type; no rectangle, no id | Points are enough to navigate; a stable id is missing | — |
| E13 | 3.3 | `engines/engine.h:555-594`, `engine.cpp:751-826` | Default empty; queried when dirty (default every frame) from `drawHotspots()`; suspended on pause and GUI | Hotspot Magnet can query the same interface on each press | — |
| E14 | 3.3, 3.7 | `gui/editgamedialog.cpp:332-372`, `:587-608`; `engines/metaengine.cpp:80-85`; `default-events.cpp:123-142`; `keymapper.cpp:380-381` | Per-game `enable_hotspots`, default off, every game; hold/toggle handled in the event manager | The shared-setting model for Phase 3 | — |
| E15 | 3.3 | `graphics/hotspot_renderer.h:73-133`, `hotspot_renderer.cpp:181-309`, `:322`, `:449`, `:699` | Markers, leader lines, labels for the whole list; no outline; type unused; overlay API | One-item list marks a target; no highlight style | How it looks with one marker on the TV |
| E16 | 3.3, 3.6 | `engines/scumm/object.cpp:559-649`; `scumm/metaengine.cpp:1176-1188`; `touche/touche.cpp:1511-1575`; `hollywood/hotspots.cpp:113-156`, `monsters/hollywood.cpp:404-408`, `runaway/engine.cpp:104-110`; `macs2/macs2.cpp:2202-2386` | Each returns interactive things only, with hit-checked points | The interface is already filled by five engines; SCUMM covers v0–v8 and HE | macs2 map scrolling; touche's player hit box |
| E17 | 3.3 | `engines/lab/metaengine.cpp:284-288`, `lab/engine.cpp:755-762`, `processroom.cpp:170-206`; `mohawk/riven_card.cpp:1174-1244`; `mads/core/game.cpp:997-1001`; `grim/grim.cpp:605-614` | Only Lab moves the cursor to the next interactive item, by its own data | Precedent for a "next object" action; no reusable core | What Grim's scripts do with PageUp/PageDown |
| E18 | 3.5 | `engines/terraglyph/room.h:52-73`, `:108-235`, `:278-356`; `room.cpp:145-255`, `:294-344`, `:563-565`, `:838-898`; `cel.cpp:192` | `hitTest` returns a sprite index; kinds, hidden, hitType, accessors; polygon private | The provider can be built from public accessors plus one polygon-box accessor | Whether a hidden parent hides its children |
| E19 | 3.5 | `terraglyph.cpp:112`, `:125`, `:336-381`, `:471-477`, `:1541-1556`; `inventory.cpp:148`, `:241-242`, `:427`; `inventory.h:165`, `:227` | One room object; toolbar at depth 5000 in it; input gated in `handleMouse` | Eligibility must include the toolbar and follow `handleMouse`'s gates | Whether every close-up is a room like the chase close-up |
| E20 | 3.5 | `terraglyph.cpp:231-237`, `:336-381`, `:414-417`, `:2003-2045`; `chase_check.cpp:259-270` | `handleMouse(false/true, p)` is the click path; the test script already synthesizes clicks; the self-test lists sprites and hit-tests headlessly | Activation reuses `handleMouse`; the reachability check is feasible | — |
| E21 | 3.2 | `git diff 2982fe324b6c 7b6fa644d74a` over the files in E1–E15 | Only `735ad86c21` (Android mouse pointer capture) changed | No finding changes upstream | — |
| E22 | 3.2 | `adb shell getevent -lt`, `getevent -lp`, `dumpsys input` on the TCL 65Q77K, 2026-11-26 | Devices listed; no presses captured | The remote's devices | — |
| E25 | 3.2 | `adb shell "timeout 600 getevent -lt"` on the TCL 65Q77K, 2026-11-26 | Short presses of down, left, right, OK and BACK: kernel keys and HID usages, one press and release each, held 0.10–0.16 s | The D-pad and OK arrive as single key events | — |
| E26 | 3.2 | `adb shell "timeout 600 getevent -lt"` and `dumpsys input` on the TCL 65Q77K, 2026-11-27; `events.cpp:1242-1252` (`JE_GAMEPAD`) | D-pad up is `KEY_UP` (`0x42`). OK held three times (3.4–4.3 s) and left and right held once each: one press and one release, no hardware repeat. Android repeats held keys (400 ms, then every 50 ms); `JE_GAMEPAD` turns each repeat into a new `JOYBUTTON_DOWN` | A held OK can be timed from the first down to the up (H6); held D-pad presses repeat | ScummVM's own event log during a hold (inferred, not observed) |
| E27 | 3.1, 6.4 | `engines/metaengine.cpp:87-177` `MetaEngine::initKeymaps`; `base/main.cpp:312-316`; `engines/terraglyph/metaengine.h:29-41`; `engines/sky/metaengine.cpp:81` | ScummVM's default game keymap ("engine-default") binds `JOY_UP`…`JOY_RIGHT` to keypad 8, 2, 4, 6 key events, `JOY_A` to left click, `JOY_B` to right click and `JOY_Y` to skip. TerraGlyph doesn't override `initKeymaps()`, so it gets this keymap, and in a game the D-pad sends keypad keys the engine ignores instead of moving the Virtual Mouse. Sky (*Beneath a Steel Sky*) declares its own keymap without the D-pad, so there the Virtual Mouse has it | TerraGlyph's own `initKeymaps()` replaces the default; with the option off it must return the default unchanged (6.4) | Seen on the TV in a TerraGlyph game (inferred from source) |
| E28 | 6.2, 6.4 | `engines/touche/metaengine.cpp:115-214`; `backends/keymapper/keymap.h:82-83`, `:167-168`; `keymapper.cpp:142-165`, `:231-246`; `engines/bbvs/bbvs.cpp:244-248` | An engine declares several game keymaps with custom actions (`setCustomEngineActionEvent`, `addDefaultInputMapping`), and toggles one with `setEnabled()` or `setGameKeymapState()`, leaving the others on. Every enabled game keymap with the same match fires together | One keymap for OK, one for the directions; an input bound in two enabled keymaps fires twice | — |
| E29 | 6.2, 6.4 | `keymapper.cpp:257-278`, `:300-318`, `:377-378`; `action.cpp:31`, `action.h:128-132`; `hardware-input.cpp:281-282`, `:498-514`; `keymapper.h:159-160`; `sdl-common-events.cpp:249-277`; `android/events.cpp:1243-1337`, `:1359-1369` | A custom action gets `EVENT_CUSTOM_ENGINE_ACTION_START` for every incoming button down (Android's repeats included; no de-duplication) and one `_END` on release. Keyboard repeats are dropped unless the action allows them. Hats are axes (`JOY_HAT_X`/`Y`, bound as halves `-`/`+`): one start past half travel, one end below a quarter, no repeats; a hat returning to centre ends both halves. Android sends a gamepad hat as axis motion; SDL turns a raw joystick's hat into pushed D-pad button events, which aren't mapped (E44) | OK's hold is timed from the first start to the end, repeats ignored (6.2); the remote binds as `JOY_UP`…, an Android hat as `JOY_HAT_*` | — |
| E30 | 6.2 | `gui/gui-manager.cpp:759-761`, `:771-772`; `engines/engine.cpp:711-724`, `:994-999`; `default-events.cpp:168-170` | Opening the main menu or a dialog pauses the engine and switches the Keymapper to the GUI keymaps; game keymaps aren't consulted, and no end is sent for an action held when it opened | Reset OK's hold at the pause, not at an end that may never come | — |
| E31 | 4.5 | `backends/modular-backend.cpp:282-283`; `backends/graphics/windowed.h:435-452`; `backends/graphics/android/android-graphics.h:47`, `:60`; `default-events.cpp:144-146`; `keymapper.cpp:324-329` | `warpMouse()` purges queued mouse events, then moves the backend's cursor. On SDL it produces a mouse motion event; on Android `setSystemMousePosition()` is empty, so no `EVENT_MOUSEMOVE` arrives and the event manager's mouse position stays where it was | Warp, then push `EVENT_MOUSEMOVE` (4.5) | Run on the TV (inferred from source) |
| E32 | 6.5 | `engines/engine.cpp:774-826`; `engines/metaengine.cpp:73-85`; `engines/touche/touche.cpp:522`; `graphics/hotspot_renderer.cpp:158-236` | The show-all display needs `getHotspotPositions()`, a `drawHotspots()` call each frame and the show-all action in a keymap. The renderer draws any list it's given, one item included, but refuses while another renderer owns the overlay | One list serves the display and Magnet; a selection marker would replace the display while shown | — |
| E33 | 6.3 | `ScummVMActivity.java:1287-1296`; `advanced/…/AdvancedMode.java:24-75`; `advanced-stub/…/TestFeatures.java:21-23`; `dists/android/build.gradle:155`, `:163-172` | In test (debug) builds, up, down, up, down, left, right, left, right within 10 s opens the advanced mode and swallows only the last right's down; release builds compile a stub that does nothing. The code's comment says the TCL's remote sometimes reports one press twice | A Magnet player can trigger it on a test build (H15) | The double report (packet 6, then 10) |
| E34 | 4.2 | `engines/terraglyph/terraglyph.cpp:231-245`, `:336-381` | The main loop passes `EVENT_MOUSEMOVE` and `EVENT_LBUTTONDOWN` to `handleMouse()`, then sets `_mouseDown` on the down and clears it on `EVENT_LBUTTONUP`. `handleMouse()` drops a click while a scene runs or a pick-up movie blocks input, takes it as a skip while the room class is busy, and otherwise hands it to the character, room class, inventory, hint, exit or clickable. A blocked click has no sound or other feedback | Activation pushes real button events (H9) | — |
| E35 | 6.8 | `room_class.cpp:130-165`; `options_rooms.cpp:160-233`; `pienoon_rooms.cpp:726-786`; `corral_rooms.cpp:189-210`; `brad_rooms.cpp:246-255`, `:326-386`, `:447-448`; `chase_rooms.cpp:637-749`; `maria_rooms.cpp:198-208`, `:400-433`; `vault_rooms.cpp:578-644`; `signin_room.cpp:276-281`, `:335-367` | The rooms that read the held button or the pointer, and what each needs (table in 6.8). The Options knobs, Brad's game and the vault's clock need the button held while the pointer moves | Room-class assists (H11) | Kids' play in each (12.6) |
| E36 | 4.6 | `room_class.cpp:82-115`; `room_class.h:97-98`; `room.h:288-298`; `room.cpp:294-343`, `:505-557`; `menu_rooms.cpp:127-134`, `:177-188`, `:216-217`; `signin_room.cpp:92-107`; `accusation_rooms.cpp:141-201` | `ButtonRoom` buttons are placements found by object name or engine sprites, exposed by `getButtonCount()`/`getButtonSprite()`. The menus', Sign In's and the clue book's buttons are these, not exits or clickables; the quit screen's Yes and No are engine sprites | Room-class buttons as targets (H13) | The menu placements' `object.ini` kinds (game data) |
| E37 | 4.5 | `terraglyph.cpp:461-466`; `room.cpp:231-255`, `:819-823`, `:843-848`, `:864-898`, `:990-1012`; `room.h:334-337`; `inventory.cpp:250`, `:309-316` | The screen shows a room's top-left 640×480 with no scrolling; rooms up to 1920 px wide; `hitTest()` in room coordinates, front to back, so a character can cover a target. The polygon box (at +8…+14, relative to the sprite's x and y) is private; `hitsPoint()`, `getFrameRect()` (the first cel only, while a cel hit tests every cel) and `getSize()` are public. The hidden toolbar sits at negative x | Drop off-screen points; add `Room::getHitBox()` | Which rooms are wider than 640 |
| E38 | 4.4 | `terraglyph.cpp:1541-1607` `showRoom`; `room_script.h:267`; `inventory.h:165`; `room_class.h:74-76`; `terraglyph.h:253-259` | Every room change, close-up and Big Head goes through `showRoom()`; `RoomScript::isBusy()`, `Inventory::isInputBlocked()` and `RoomClass::isBusy()` are the click gates | The selection's drop and block rules (4.4) | — |
| E39 | 4.5 | `room.cpp:834-835`, `:1069-1105`; `terraglyph.cpp:342`, `:472`, `:484` | TerraGlyph draws its own cursor sprite, moved only from mouse events through `handleMouse()`/`updateHover()`. It never calls `warpMouse()` or `CursorMan` | The cursor adapter pushes a mouse move (4.5) | — |
| E40 | 5.6, 6.2 | `movie.cpp:116-125` | A movie polls events itself, honours mouse moves and its skip keys and buttons, and discards everything else, button releases included | Reset OK's hold when a movie starts | Whether `_mouseDown` is left set after a movie |
| E41 | 12.7 | `terraglyph.cpp:128-153`, `:383-459`, `:2003-2045` | The self-test runs by debug channel at level 3; `checkAllRooms` builds a bare `Room` with no class, toolbar or inventory. `test_script` runs a step list each frame: `click` calls `handleMouse()` directly, `down`/`up` push real button events | The listing hook uses `showRoom()`; new verbs (12.7) | — |
| E42 | 6.6 | `engines/terraglyph/metaengine.h:26-43`; `detection_tables.h:49`, `:64`, `:78` | `TerraglyphMetaEngine` declares no options or keymaps; every entry is `GUIO1(GUIO_NOMIDI)`; settings are read with plain `ConfMan` calls | "Hotspot Assist" is the engine's first option | — |
| E43 | 6.4 | `signin_room.cpp:306-333`, `:396-409` | Sign In queues every ASCII key (Enter, `'\r'`, starts play) and Delete; Escape and an early Space still skip; arrow keys carry no ASCII and aren't taken | The Windows OK is keypad Enter | — |
| E44 | 6.1, 6.4 | `common/events.h:318-329` (`ArtificialEventSource::allowMapping()` false); `default-events.cpp:272-279`; `backends/keymapper/virtual-mouse.cpp:93`, `:153-180`; `sdl-common-events.cpp:249-272`; `sdl2-events.cpp:880-883`; `backends/keymapper/keymap.cpp:255-272`; `android.cpp:734-735` | Events pushed with `pushEvent()` are never mapped by the Keymapper. SDL pushes a raw joystick hat's D-pad buttons that way, so they never reach a keymap; a recognised game controller's D-pad is mapped. The Virtual Mouse's own defaults are the left stick and right shoulder; only Android (and two handheld ports) bind the D-pad to it. It starts each move from the event manager's mouse position. A backend's standard-action binding (Android: skip on BACK and `JOY_Y`) applies to any keymap's action with that id | Cursor mode's D-pad is Android's; Magnet's actions can't be driven by pushing hardware events (12.7); keep the standard ids (6.4) | Raw-hat and D-pad-only controllers on the Pi (packet 11) |
| E23 | 3.7 | `engines/advancedDetector.h:400-405`, `:715`; `advancedDetector.cpp:333-341`; `engines/metaengine.h:71-78`; `engines/dialogs.cpp:472-495`; `metaengine.cpp:460-468`; `base/main.cpp:225`; `awe/metaengine.cpp:31-75`, `awe/detection_tables.h:40`, `awe/awe.cpp:195` | Declare, tie to entries by GUIO flag, persist per game, read with `ConfMan.getBool` | The Phase 1 setting is a standard extra option | — |
| E24 | 3.7 | `engines/terraglyph/metaengine.h:29-41`; `detection_tables.h:50-123` | No extra options; only `GUIO_NOMIDI` | Where "Hotspot Assist" goes | — |

---

## Part II — Technical design

**Status: designed for the Phase 1 TerraGlyph prototype**
([WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md),
2026-11-27), within Jeff's decisions H1–H8. Choices H1–H8 don't make are
marked **proposed (H*n*)** and wait on Jeff in
[§10.4](#104-open-design-decisions). §5.1–5.5, §5.7 and §5.8 (the
directional algorithm) are still intent, for packet 3. Source facts are E27
onward in [§3.8](#38-research-evidence-register), at fork `0d5a69c7694f`;
everything is Gen 1 except the shared core and input adapter, which carry no
generation. Nothing here is built.

### 4. Proposed software architecture

#### 4.1 Architectural principles

- Separate hotspot discovery from navigation.
- Separate navigation from input mapping.
- Keep engine-specific data outside the shared algorithm.
- Minimize changes to existing engine behavior.
- Prefer composition over deep inheritance.

#### 4.2 Component responsibilities

| Component | Lives in | Responsibility |
|---|---|---|
| **A. Engine Hotspot Provider** | Engine | Supplies only the targets that are eligible right now ([4.6](#46-eligibility)), each with its geometry, metadata and an interaction point; reports availability changes |
| **B. Hotspot Navigation Core** | Shared | **Selection:** holds the active selection, evaluates directional requests, picks the next hotspot, handles unavailable or changing targets |
| **C. Input Adapter** | Shared, or thin engine glue | Turns D-pad / Keymapper events into navigation requests and OK/Select and secondary actions into activation requests; provides the conventional cursor fallback |
| **D. Cursor Adapter** | Engine or shared | **Cursor positioning:** moves the game cursor to the target's interaction point, with coordinate conversion; optionally highlights the selected target (possible reuse of the existing hotspot display) |
| **E. Activation** | Engine | **Activation:** invokes the engine's own interaction behavior at the interaction point, as a real click would. The shared code never triggers game logic directly |

Selection, cursor positioning and activation are separate steps. Moving the
cursor to a target doesn't by itself guarantee the game will accept a click
there, so the engine owns both the point and the click.

**Phase 1 contracts** (WP-089). Declarations are in
[Appendix B](#appendix-b-interface-declarations).

| | Inputs | Outputs | Owner, location | Runs when | Builds on |
|---|---|---|---|---|---|
| **A** | The live room, its room class, the toolbar, the cursor in use | The target list: one `Graphics::HotspotInfo` per target (4.3), with each target's identity kept beside it | TerraGlyph, `TerraglyphEngine` | On each directional press and each OK (H8), and when ScummVM's show-all display asks | `getHotspotPositions()` (H2), `Room::hitTest()`, a new `Room::getHitBox()` (E37), room-class targets (E36, H11, H13) |
| **B** | The target list, the current selection's index or none, the cursor's position, the direction, whether the press is a repeat | The index to select, or none (stay) | Shared, with no engine type; in `engines/terraglyph/` for Phase 1 (H4) | On each directional press in Magnet mode | Nothing; a pure function (4.3) |
| **C** | Magnet's action starts and ends, the clock, each engine tick | One of: navigate (direction, repeat), activate, enter cursor mode, enter Magnet mode, nothing | Shared, with no engine type | On each Magnet action event and each engine tick | Keymapper custom engine actions (E28, E29) |
| **D** | The point to move to | The game cursor at that point, hover and rollover updated | TerraGlyph | When the selection changes | `OSystem::warpMouse()` and a pushed `EVENT_MOUSEMOVE` (E31, E39) |
| **E** | The selected target, or the pointer in cursor mode | A left-button press at the point, released after one game tick has seen it | TerraGlyph | On OK's short press (H6) | `handleMouse(true, p)` and `_mouseDown`, owned by the engine (E34) — proposed (H9) |

**Activation** (E) — proposed (H9). After the re-check (4.4) the engine
sets `_mouseDown`, calls `handleMouse(true, p)` itself, and clears
`_mouseDown` once at least one game tick has run with it set. That is what a
real press does to TerraGlyph's state (the main loop sets `_mouseDown` on a
button down and clears it on the up, E34), so the rooms that read the held
button (the corral, Pie Noon, `ButtonRoom`'s pressed frame) see it. It
doesn't go through the event queue: a pushed release can be lost, because a
movie's own event loop discards releases (E40) and `warpMouse()` purges
queued mouse events (E31), which would leave `_mouseDown` stuck. Ticks run
at 36 a second against 60 frames, so "after one game tick" is counted in the
tick loop, not in frames (E34). Every reset (6.2) also clears a pending
release. What blocks a click, and what the player sees, is today's
`handleMouse()` (E34): a running scene or a pick-up movie drops it with no
sound; a busy room class takes it as a skip (the title, credits, Big Head);
the cursor is already hidden in both cases. Phase 1 adds no feedback of its
own for a blocked click.

#### 4.3 Interfaces

**The hotspot record** is ScummVM's `Graphics::HotspotInfo` unchanged (H2):

| `HotspotInfo` field | Holds for a TerraGlyph target |
|---|---|
| `position` | The interaction point (H3), in game coordinates (4.5) |
| `name` | The target's label (`Room::getLabel()`, or the room class's), for logs and the show-all display |
| `type` | The closest `HotspotType`: an exit is an exit, the rest are objects. Nothing draws by type (E15) |

The provider keeps, in a second array beside the list, each target's
**identity**: its source and index. The source is the room (the index is a
sprite) or the room class (the index is the class's own target number, H11).
With the room, that is the selection (4.4). `HotspotInfo` gets no id, so
H2's condition (b) isn't needed yet. **The core navigates over points
only**: the interaction point is where the player's eye goes and where the
click lands, and a polygon's box can be far bigger than the object it
outlines. If packet 3's scoring needs a box, it raises H2 (b) then —
proposed (H12).

**The navigation core's contract for packet 3.** One pure function: given
the targets, the current selection's index (or none), the cursor's position,
the direction (up, down, left, right) and whether the press is a repeat, it
returns the index to select, or none to stay. It keeps no state and knows no
engine. What it does with no selection, using the cursor's position (5.5),
how it treats a repeat, and how it guarantees reachability (5.8) are all
packet 3's.

**The input adapter** (C) keeps the mode, OK's hold and the directions'
held state, and turns Keymapper events into the five results in the table
above. It's specified in [6.2](#62-cursor-mode-fallback-requirement).
**Repeats are its own**, the same on every device: it ignores the repeated
starts a device sends (Android's, E26) and, while a direction is held,
reports repeats from its own clock on each tick, at a delay and interval
packet 3 sets (which may be "never"). The remote, a hat and a keyboard then
behave alike: a hat never repeats and the Keymapper drops keyboard repeats
(E29).

**Room-class hooks** — proposed (H11). Some rooms aren't sprite clicks
([6.8](#68-rooms-that-arent-plain-clicks)). A room class may add targets of
its own (a point, a label, and a sprite if it has one), say whether each is
still valid, take a directional press for itself, and let OK click with no
target (the corral). `ButtonRoom` implements the target hook with its
visible buttons (H13). A class that does none of this behaves as today.

#### 4.4 Data ownership and lifetime

- **Who owns what.** The engine owns the target list and the selection,
  which it holds as an identity (room, source, index), never as a list
  index. The core owns nothing. The list is rebuilt on each directional press
  and each OK (H8); between presses nothing is queried.
- **Matching across refreshes.** After a rebuild, the selection is the entry
  with the same identity. If it isn't there, the selection is dropped, and
  the next press starts from the cursor's position (5.5).
- **What drops the selection** (H7, H8), each with the TerraGlyph signal
  that shows it (E34, E38):

  | Change | Detected by | Noticed |
  |---|---|---|
  | Room change, a close-up, Big Head | `showRoom()` (the one place a room is entered) | A hook at the change |
  | The target hidden or detached, or a class target no longer valid | `Room::isHidden()`, `isDetached()`; the class's validity hook | A check each tick of the one selected target |
  | A scene or exit running | `RoomScript::isBusy()` | Each tick |
  | A pick-up movie | `Inventory::isInputBlocked()` | Each tick |
  | The room class busy | `RoomClass::isBusy()` | Each tick; OK is then a skip (6.1) |
  | An item taken in hand or put back, when that removes the target (4.6) | `Inventory::isDefaultCursor()` | Each tick |
  | The main menu or another dialog | `pauseEngineIntern()` | A hook at the pause; OK's hold is also reset (6.2) |

  While a scene runs, input is blocked or the class is busy, the list is
  empty (4.6, H7), so dropping the selection loses nothing: the cursor stays
  where it was, and the next press after the scene starts from there. The
  per-tick check reads one target and four flags, not the list, so H8's "no
  query every frame" holds.
- **Occlusion doesn't drop.** A character walking in front of the selected
  target (characters are hittable, E37) blocks activation through the
  re-check but keeps the selection.
- **The activation re-check** (H8). On OK the provider rebuilds the list and
  the engine re-checks the selected target: in the list, and `hitTest(point)`
  still the sprite (or the class's validity hook true). If either fails,
  nothing is clicked. A vanished or disabled hotspot can't be activated.

#### 4.5 Coordinate systems

- **One space.** Gen 1 draws a room's top-left 640×480 at the screen's
  origin, with no scrolling (E37). Room, game and screen coordinates are the
  same, and `hitTest()` works in them. A room can be up to 1920 px wide, and
  the hidden toolbar sits at negative x, so the provider **drops every
  target whose interaction point is outside 0–639 × 0–479**.
- **Moving the cursor** (D). TerraGlyph draws its own cursor sprite and moves
  it only from mouse events (E39). The cursor adapter calls
  `g_system->warpMouse(x, y)`, which moves the host pointer on SDL, and then
  pushes an `EVENT_MOUSEMOVE` at the point. The push is what updates
  TerraGlyph's hover, rollover cursor and `ButtonRoom`'s hover sound, and
  the event manager's mouse position, which the Virtual Mouse starts from in
  cursor mode (E31); Android's warp produces no mouse event at all. Warp
  first: it purges queued mouse events (E31). No warp is made while a
  release is pending (4.2).
- **The overlay.** ScummVM's hotspot renderer takes game coordinates and
  converts them itself (E32); Phase 1 draws no overlay of its own (6.5).
- **The interaction point** (H3). TerraGlyph's data has no preferred point,
  so the provider searches for one. The box is the current step's polygon
  box for a polygon-hit sprite (its offsets are relative to the sprite's x
  and y), and the union of the current frame's cels for a cel-hit one
  (`getFrameRect()` gives the first cel only, but a hit tests every cel,
  E37). The search tries the box's centre, then a 4 px grid in rings outward
  from it, and takes the first point where `hitTest()` returns the sprite and
  that is on screen. No such point: not a target. The polygon box is private
  today, so the search needs a public `Room::getHitBox(sprite)` (E37). A room
  class that knows a better point supplies it through its hook (H11). Points
  are cached per sprite and step, and **each cached point is re-checked with
  one `hitTest()` at every rebuild**; one that fails is searched again.
  Sprites move by offset as well as by step (the jigsaw's pieces, a carried
  item), and characters walk in front of targets, so the step alone isn't
  enough to trust a cache.

#### 4.6 Eligibility

Who decides whether a hotspot is interactive right now? There's a difference
between an object defined in the game data, an object currently visible, an
object currently clickable, and an object currently meaningful to click.

**Requirement:** the engine hotspot provider supplies only targets the engine
currently considers eligible for interaction. Static object definitions
alone aren't enough when game state controls availability. This keeps
engine-specific scripting out of the shared navigation core.

**The Phase 1 filter** (H7, E36, E37). A sprite is a target when all hold:

1. It's not hidden or detached, and its hit type isn't 0.
2. It's one of: an exit, a clickable, a requires object, an inventory
   object, a toolbar sprite (H7); or a target the room class adds through
   its hook, which for a `ButtonRoom` is each visible button
   (`getButtonSprite()`) — proposed (H13). Without this, the main menu,
   level select, quit screen, Sign In and the clue book would have no
   targets: their buttons are room-class buttons and engine sprites, not
   those kinds. `getButtonSprite()` is on `ButtonRoom`, not `RoomClass`, so
   the hook, a `RoomClass` virtual, is how the provider reaches it.
3. With an item in hand (the cursor isn't the default arrow), exits and
   clickables are left out: they answer only the arrow (E34). Requires
   objects, inventory objects and the toolbar stay.
4. `handleMouse()` would accept a click now: no scene running, input not
   blocked, the room class not busy (H7's rule in 3.5). Otherwise the list
   is empty, and OK only skips (6.1).
5. It has an interaction point on screen (4.5).

Characters, simple sprites, layers and the ghost are left out (H7).

### 5. Directional navigation algorithm

#### 5.1 Basic directional selection

1. Filter the candidates that lie in the requested direction.
2. Score them by angular alignment and distance.
3. Apply priority and deterministic tie-breaking.
4. Select the best candidate (or none).

#### 5.2 Selection scoring

- Directional alignment (angle from the current position or previous
  hotspot).
- Distance weighting (prefer nearer, but not exclusively).
- Hotspot priority / category.
- Deterministic tie-breaking (a stable sort key).

#### 5.3 Special cases

- Overlapping and nested hotspots.
- Large interactive regions.
- Closely spaced targets.
- Hotspots outside the current view.
- No hotspot in the requested direction (stay put, wrap, or fall back).

#### 5.4 Wrap-around behavior

- Whether navigation wraps at the screen edges.
- Configurable or fixed.
- The recommended default (likely no wrap, or wrap only for exits).

#### 5.5 Initial selection

- The cursor starts outside all hotspots.
- The cursor already overlaps a hotspot.
- Entering a new room.
- Returning from inventory or a dialog.

#### 5.6 Dynamic hotspots

Designed in WP-089 (Gen 1); the rules are in
[4.4](#44-data-ownership-and-lifetime):

- **Moving and animated objects.** A target's point is recomputed when its
  step changes (4.5), and the selected target is checked each tick against
  its point. Characters aren't targets yet (H7).
- **Objects that appear and disappear.** A hidden or detached target leaves
  the list at the next rebuild; if it was selected, the selection is dropped
  at once.
- **Scene transitions, inventory, dialogs, cutscenes.** A room change drops
  the selection; a running scene, a pick-up movie or a busy room class keeps
  it but blocks activation; a dialog resets OK's hold. Movies play in their
  own event loop (E40), during which Magnet does nothing.
- **A target that becomes invalid mid-navigation** is dropped, never
  activated, and the next directional press starts from no selection (5.5).

#### 5.7 Performance

- Expected hotspot counts: dozens, not hundreds.
- Navigation runs on input, not every frame.
- Hotspot refresh frequency.
- Avoid unnecessary per-frame work.

#### 5.8 Hotspot reachability

The basic requirement isn't that the selection moves intelligently. It's that
a child can reach every interactive object. Scoring alone can leave a target
that is never the preferred candidate from any direction, for example the
middle one of three objects on a diagonal.

- Every eligible hotspot must be reachable from every other through a finite
  sequence of directional inputs.
- Navigation must not trap the player in a subset of hotspots.
- The algorithm must handle isolated, overlapping and unusually placed
  hotspots.
- If directional navigation alone can't guarantee reachability, the design
  adds a deterministic alternative (for example, a fixed reading-order cycle
  when no candidate lies in the pressed direction).

**How to test it.** Reachability is a property of a room's layout, so it can
be checked exhaustively rather than sampled. The headless self-test already
walks every room in both Gen 1 titles (WP-018's grid hit test covers all 69
*Showdown* and 53 *Phantom* rooms). A reachability check can build the
navigation graph for each room's eligible targets (each target × four
directions → the target selected) and confirm it's strongly connected. That
covers each room's starting state; states reached by play (clickables
moved, objects revealed) need the live tests in [12](#12-testing-and-validation-matrix).

### 6. Input and user experience

#### 6.1 Control scheme

With Hotspot Assist on (Gen 1, WP-089). Gen 1 reads no right button except
to skip a movie (E40), so there is no secondary action.

| Input | Magnet mode | Cursor mode |
|---|---|---|
| D-pad up, down, left, right | Select the next target that way (packet 3) | Move the pointer (ScummVM's Virtual Mouse) |
| OK, short (released before the threshold) | Click the selected target. With none: a click at the cursor if the room class is busy (a skip) or lets OK click with no target (the corral, H11); otherwise nothing | Click at the pointer |
| OK, held past the threshold | Switch to cursor mode when the threshold passes; the release clicks nothing | Switch to Magnet mode when the threshold passes; the release clicks nothing |
| BACK | Unchanged: skip in a game; held, the main menu (E8) | Unchanged |
| MENU | Unchanged: the main menu; held, the on-screen keyboard (E8) | Unchanged |

Magnet mode is where a game starts. At each room change the room class says
which mode it starts in: Magnet by default, cursor mode for the rooms 6.8
plays with the pointer, and a close-up or Big Head keeps the mode the player
was in — proposed (H10). A child who drifts into cursor mode is brought back
at the next ordinary room. The threshold is **600 ms**: over Android's
400 ms repeat start (E26), short enough not to feel stuck — proposed (H10),
to be tuned in the user-experience tests (12.6).

**Off the TV.** The D-pad moves the Virtual Mouse only because Android binds
it there (E3); on Windows and the Raspberry Pi the Virtual Mouse's own
defaults are the left stick, so cursor mode moves with the stick or the
mouse, and a D-pad-only controller can't move the pointer unless the player
rebinds it in the Keymaps tab (E44). A raw SDL joystick's hat never reaches
the Keymapper at all (E44); a recognised game controller's D-pad does. Both
are for packet 11 (Raspberry Pi validation).

#### 6.2 Cursor-mode fallback requirement

A long press may already mean something on a remote: holding OK might repeat
the click instead of switching modes.

**Requirement:** Hotspot Magnet must provide a reliable way to enter and
leave conventional cursor mode using only the standard TV remote. The method
must not depend on a system-reserved button, need extra hardware, or
unintentionally activate a game object. Device testing on the TV sets the
final mapping. This is a Phase 1 acceptance criterion
([7.6](#76-phase-1-acceptance-criteria)).

**The design** (H1, H6; WP-089):

- **Two states**, Magnet and cursor, plus OK's hold, which the input adapter
  (C) keeps as the time of OK's first start event, or none.
- **Transitions.** OK's first start records the time; later starts while it's
  held (Android's repeats, E29) are ignored. Each engine tick, if OK is held
  and the threshold has passed, the mode flips and the hold is marked used.
  At OK's end: a used hold does nothing; otherwise it's a short press and
  gives a click (6.1). A room change sets the room class's starting mode
  (6.1).
- **Resets.** The hold is cleared, with no click, and any pending release
  of a click is made (4.2), when the room changes, when a movie starts (it
  runs its own event loop and drops the release, E40), and when the engine
  pauses for the main menu or a dialog (the release then arrives in the GUI
  and the game never sees it, E30).
- **Ends with no start are ignored**, for OK and for the directions alike: a
  hat returning to centre sends an end to both of its halves (E29), and the
  test-build gesture swallows a down but passes its up (E33).
- **The same contract on every device** (E29). The Keymapper sends a start
  for every incoming button down, Android's repeats included, and one end on
  the release; it drops keyboard repeats; and a gamepad hat or stick gives
  one start and one end. Timing from the first start to the end, ignoring
  repeats, gives the same result from the remote, a hat and a keyboard.
- **How cursor mode is entered.** The Magnet direction keymap is disabled,
  so on Android the D-pad falls through to the Global keymap's Virtual Mouse
  (E2, E3; off the TV, see 6.1). OK stays bound, because it's in a second
  keymap that stays enabled: the Virtual Mouse has no click (E4), and
  `setEnabled()` works on a whole keymap (E28). This refines H1, whose
  "turning it off is the fallback" would also unbind OK — proposed (H16).

#### 6.3 Standard TV remote limitations

- The physical buttons available.
- **Held buttons repeat** (3.2, E26). Android adds a repeated press 400 ms
  into a hold and then every 50 ms, and ScummVM passes each one on as a new
  button press. Holding a D-pad direction would step through hotspots 20
  times a second unless navigation ignores or slows repeats. The navigation
  algorithm packet must decide which. The input adapter marks each repeat
  (a start while the direction is already held) and passes it to the core
  with that flag (4.3); the policy is packet 3's.
- **A press reported twice.** WP-085's code says the TCL's remote sometimes
  reports one press twice (E33); the captures (E25, E26) didn't. If it comes
  as two downs before one up, the input adapter sees a repeat; if as two
  full presses, the selection would move twice, which packet 3's repeat and
  rate policy has to cover. Whether and how it happens is checked on the TV
  in packet 6, then 10.
- **A ring press that also presses OK.** The same code says the remote's
  ring often registers OK too when pressed near its edge (E33). In Magnet
  mode that would click the target just selected. Checked on the TV in
  packet 6, then 10; if it happens, the input adapter ignores an OK that
  starts within a short window of a direction.
- **The test-build gesture** (E33). Test builds of the TV app (WP-085) open
  their hidden advanced mode on up, down, up, down, left, right, left, right
  within 10 s, swallowing the last right. A player moving between hotspots
  could make it. Release builds don't have it. Proposed (H15): live with it
  in test builds and tell testers; changing the gesture is WP-085's
  successor's call, not Magnet's.
- Android TV system-reserved buttons.
- Long-press detection reliability.
- Button conflicts.
- Accessibility implications.

#### 6.4 Gamepad and keyboard support

**The keymaps** (H1, WP-089) — the structure is proposed (H16). TerraGlyph
declares no keymap today, so it gets ScummVM's default game keymap, which
binds the D-pad to keypad arrow keys that the engine ignores (E27). Its own
`initKeymaps()` replaces that default, so:

- **Hotspot Assist off:** `initKeymaps()` returns ScummVM's default keymap
  unchanged, so input is exactly today's (plus the show-all action, below).
- **Hotspot Assist on:** three game keymaps.

| Keymap | Actions and default bindings | Enabled |
|---|---|---|
| `terraglyph-default` | The default keymap's actions with the same standard action ids, **without** the four directions, and with `JOY_A` moved to Magnet's OK: left click (mouse left, and `JOY_X`, so a gamepad can still hold the button and drag with the stick), right click (mouse right, `JOY_B`), pause (Space), game menu (F5, left shoulder), skip (Escape, `JOY_Y`), skip line (period only), confirm. Partial matches off, as in the default (E27) | Always |
| `terraglyph-magnet-ok` | OK: `JOY_CENTER` (the remote), `JOY_A` (a gamepad), keypad Enter (Windows) | Always |
| `terraglyph-magnet-dir` | Up, down, left, right: `JOY_UP`…`JOY_RIGHT` (the remote, and a recognised SDL game controller's D-pad), `JOY_HAT_Y-`/`+` and `JOY_HAT_X-`/`+` (an Android gamepad's hat, E29), the arrow keys (Windows) | Magnet mode only |

- The directions must leave the always-on keymap, or in cursor mode an exact
  game match would still win over the Virtual Mouse (E2) and the pointer
  wouldn't move.
- `JOY_A` must be in one keymap only: two enabled game keymaps that bind the
  same input both fire (E28).
- The Windows OK is **keypad Enter**, not Enter: Sign In reads every ASCII
  key, and Enter starts play (E43). The arrow keys carry no ASCII, so Sign
  In loses nothing.
- **The standard action ids matter.** Android binds BACK and `JOY_Y` to
  skip by the standard action id, for every keymap that has an action with
  that id (E44), so `terraglyph-default` keeps `kStandardActionSkip` (and
  the other standard ids) or BACK stops skipping. MENU opens the main menu
  through the Global keymap, which game keymaps don't touch.
- **A gamepad in Magnet mode**: `JOY_A` is OK, so A no longer skips a movie
  (a movie reads only real button presses, E40); `JOY_Y` (skip) and `JOY_B`
  (right click) still do. `JOY_X` was skip line, which TerraGlyph never
  reads, so moving it to left click costs nothing.
- **A raw SDL joystick's hat** isn't bound: SDL pushes its D-pad buttons as
  events the Keymapper never maps (E44). Recorded for packet 11.
- **The show-all action** is added to the game keymap whenever
  `hotspotsEnabled(target)`, with Hotspot Assist on or off, as other engines
  do (E32). With `enable_hotspots` at its default (off) that adds nothing.

#### 6.5 Visual feedback

**Phase 1** (WP-089) — proposed (H14):

- **The selection** is the game's own cursor at the interaction point, with
  its rollover cursor, and a `ButtonRoom` button's hover sound, exactly as
  if a mouse had moved there. No overlay marker.
- **The mode** has no marker of its own in Phase 1, and nothing moves when
  the mode changes: the cursor stays where it is, and the next press shows
  the difference (it jumps to a target, or it glides). That's weak, so
  whether a child can tell the modes apart is a user-experience test (12.6);
  if not, a one-item marker from ScummVM's hotspot renderer is the next step. It can draw any list it's given (E32), but only one renderer
  may own the overlay at a time, so it would replace the show-all display
  while shown.
- **ScummVM's show-all display** comes with `getHotspotPositions()`: the
  same list, so it shows exactly the targets Magnet visits. The engine calls
  `drawHotspots()` each frame and adds the show-all action when
  `enable_hotspots` is on (E32). While it's shown it asks for the list every
  frame (`hotspotDirty()` is true by default), so TerraGlyph overrides
  `hotspotDirty()` to report a change only after a room change, a step
  change or a hide or show, and the point cache keeps the cost down. There's
  no remote button for it.

#### 6.6 Parent-friendly configuration

- A single per-game checkbox: "Hotspot Assist" (or similar).
- Disabled by default.
- Saved configuration.
- Clear fallback instructions in the GUI.

**The option** (H5, WP-089; E42):

| | |
|---|---|
| Config key | `hotspot_assist` |
| Label | "Hotspot Assist" |
| Tooltip | "Move between objects with the arrows; OK clicks. Hold OK for the free pointer." |
| GUIO flag | `GAMEOPTION_HOTSPOT_ASSIST` (`GUIO_GAMEOPTIONS1`) |
| Detection entries | The three Gen 1 entries (*Showdown* English and Norwegian, *Phantom*): `GUIO2(GUIO_NOMIDI, GAMEOPTION_HOTSPOT_ASSIST)`. Gen 2 and 3 stay `GUIO1(GUIO_NOMIDI)` |
| Declared | `TerraglyphMetaEngine::getAdvancedExtraGuiOptions()`, from an `ADExtraGuiOptionsMap` (E23, E24) |
| Default | Off |
| Read | `ConfMan.getBool("hotspot_assist", target)` in `initKeymaps()`, and in the engine at start |
| Off | No Magnet keymap and no Magnet code path runs: input is exactly today's (7.6) |

The option is TerraGlyph's first: today the engine reads its settings with
plain `ConfMan` calls and declares none (E42).

#### 6.7 Accessibility considerations

- Reduced fine-motor requirements.
- Predictable navigation.
- Alternative input devices.
- Possible future support for switch-based navigation.
- Complement, not replace, the existing TTS and hotspot display features.

#### 6.8 Rooms that aren't plain clicks

Some Gen 1 rooms read the held button or the pointer itself (E35). A click
from component E is a real press and release (H9), so a room that needs only
a click, wherever it lands, works in either mode. A room that needs the
button held *while the pointer moves* can't be played on the remote: the OK
button sits inside the D-pad ring, so holding it while pressing a direction
isn't practical (an inference about the remote's layout).

| Room (Gen 1) | What it reads | With the remote, before assists |
|---|---|---|
| Main menu, level select, quit, the clue book (`ButtonRoom`) | Hover, then a click | Magnet mode, once room-class buttons are targets (H13) |
| Sign In's player list | A click inside a row; a second click within 1 s plays | Cursor mode, or a room-class hook adding the rows as targets |
| The artifact jigsaw (*Showdown*) | Click a piece, move it near its place (no button held), it snaps | Cursor mode, or a hook adding the target places |
| Maria's game (*Phantom*) | Click an item, carry it, click to throw | Cursor mode, or a hook adding the pans |
| Pie Noon (*Showdown*) | Scooby follows the pointer's x; a press throws | Cursor mode |
| The corral (*Showdown*) | A press at the right moment, anywhere | Either mode, once its hook lets OK click with no target |
| The Options knobs | Press on a knob, drag along its line, release | **Not playable** on the remote |
| Brad's game (*Phantom*) | Press on a piece, drag it its way more than 60 px, release | **Not playable** on the remote |
| The vault's clock (*Showdown*) | Press on a hand, circle the pointer while held, release | **Not playable** on the remote |

**Proposed (H11):** room-class hooks (4.3), with one assist per room in its
own later packet: the hook adds the room's own targets, and a directional
press in Magnet mode is passed to the class first, so a knob or a clock hand
turns with left and right, and a piece of Brad's armour comes off with the
direction it needs. The assists aren't designed here and no packet is
scheduled for them yet (14.3). Until each lands, that room is played with a
mouse, or a gamepad holding `JOY_X` (left click, 6.4) and steering with the
stick, and the gap is listed in the Phase 1 results.

---

## Part III — Implementation roadmap

### 7. Phase 1: TerraGlyph prototype

**Objective:** demonstrate Hotspot Magnet in a working TerraGlyph game
without modifying the original game assets. Phase 1 is valuable on its own.

#### 7.1 Implementation boundaries

- Prototype primarily within `engines/terraglyph/` in the
  [ScummVM fork](https://github.com/barefootbetters/scummvm).
- Keep the navigation logic as engine-neutral as possible.
- Use the existing TerraGlyph hotspot data.
- No shared ScummVM changes unless the prototype strictly needs them.

#### 7.2 TerraGlyph hotspot provider

- Take the targets from the room's live placements, which the engine already
  built from `object.ini` and the art, not by parsing `object.ini` again.
- Keep only eligible targets ([4.6](#46-eligibility)): an interactive kind,
  not hidden, in the room the player is in.
- Use each target's current step polygon (or cel bounds) for navigation
  geometry, and find an interaction point that `Room::hitTest()` resolves to
  that target.
- Supply normalized hotspot data to the navigation core.

#### 7.3 Cursor and input integration

- Move the cursor to the selected target's interaction point.
- Activate through the game's existing interaction mechanisms.
- Preserve conventional mouse and Virtual Mouse operation.
- Implement the fallback.

#### 7.4 Configuration

- Enable/disable Hotspot Assist.
- Save the per-game setting.
- Zero changes when disabled.

Specified in [6.6](#66-parent-friendly-configuration) (key, flag, entries,
default) and [6.4](#64-gamepad-and-keyboard-support) (what the keymaps are
with it on and off). Phase 1 checks the off state by comparing a run with the
option off against today's build: the same keymaps listed in the Keymapper
tab, and the same self-test results.

#### 7.5 Testing environments

- Windows development (keyboard D-pad simulation).
- Smart TV with its standard remote (setup:
  [ScummVM on smart TVs](scummvm-smart-tv.md)): the TCL 65Q77K (Google TV)
  now, then the Sony Bravia XBR-75X81CH next.
- Raspberry Pi with a D-pad controller (setup:
  [ScummVM on the Raspberry Pi](scummvm-raspberry-pi.md)).

#### 7.6 Phase 1 acceptance criteria

- **Reachability** ([5.8](#58-hotspot-reachability)): every eligible
  interactive hotspot is reachable through a finite sequence of D-pad inputs,
  and the navigation algorithm never traps the player within a subset of
  hotspots. Checked for every room's starting state in both Gen 1 titles.
- A hotspot that disappears or is disabled is never activatable, even while
  selected (H8).
- A long OK press never activates a hotspot (H6).
- Activating a selected hotspot clicks that hotspot: its interaction point
  hit-tests to it.
- Cursor mode can be entered and left with the standard remote alone, with
  no system-reserved button and no accidental click
  ([6.2](#62-cursor-mode-fallback-requirement)).
- Navigation is predictable and repeatable.
- No unintended clicks.
- Dynamic hotspots and room transitions are handled.
- Normal cursor mode remains fully functional.
- Disabling the feature restores the existing behavior exactly.
- No game-specific logic leaks into the navigation core.

### 8. Phase 2: SCUMM / Humongous Entertainment

**Objective:** demonstrate reuse of the navigation core in a second ScummVM
engine.

#### 8.1 Initial game selection

- Putt-Putt is the preferred candidate (exact game and version to be chosen
  after research).
- Establish a reproducible test scenario.

#### 8.2 SCUMM hotspot provider

- Retrieve interactive objects.
- Convert object geometry.
- Determine current availability.
- Handle room transitions.

#### 8.3 Reusing the navigation core

- Reuse directional selection unchanged.
- Keep SCUMM-specific logic in the provider/adapter.
- Don't duplicate the navigation algorithm.

#### 8.4 Compatibility investigation

- Document which HE titles and versions share compatible structures.

#### 8.5 SCUMM maintainer coordination

Questions to ask before deep implementation:

- Does equivalent functionality already exist?
- What is the preferred integration point?
- Which HE versions should be supported first?
- Event-driven or polled hotspot discovery?
- What testing and documentation are expected?
- Where should the reusable component live?

#### 8.6 Phase 2 acceptance criteria

- At least one HE title works.
- The reachability criterion of [7.6](#76-phase-1-acceptance-criteria) holds
  in that title's rooms.
- The same navigation core is reused.
- SCUMM-specific code stays isolated.
- Existing controls are unchanged when the feature is disabled.
- Maintainer feedback is documented.

### 9. Phase 3: shared ScummVM integration (goal)

**Preconditions:** Phases 1 and 2 demonstrated; research complete;
maintainer feedback received.

#### 9.1 Shared code extraction

- Move the reusable navigation logic.
- Preserve the engine adapters.
- Establish stable interfaces.
- Update build integration.

#### 9.2 Shared configuration and input

- Engine capability declarations.
- Per-game settings.
- Keymapper compatibility.
- Platform considerations.

#### 9.3 Upstream contribution strategy

- Early architectural discussion.
- Maintainer review.
- Incremental pull requests.
- Tests and documentation.
- Coding-style compliance.

#### 9.4 Upstream justification

- The user problem and the accessibility benefits.
- Demonstrated reuse across engines.
- Why the existing Virtual Mouse is insufficient for the target audience.
- Why the solution belongs in shared code.
- Maintenance responsibilities and compatibility safeguards.

#### 9.5 Acceptance criteria

- A shared navigation core used by two engines.
- No duplicated navigation algorithm.
- Existing games unaffected when disabled.
- Code meets ScummVM conventions.
- Maintainer review requirements addressed.

> Upstream acceptance is an external decision, not a guaranteed project
> milestone.

### 10. Risks, constraints, and open questions

Rank by severity × likelihood once the research is done.

#### 10.1 Technical risks

- Incomplete or dynamic hotspot data.
- Input event conflicts with the Keymapper / Virtual Mouse.
- Coordinate scaling and overlay rendering.
- Game-specific interaction behavior.
- Stale hotspot references.

#### 10.2 Usability risks

- Unpredictable navigation.
- Too many or too few hotspots.
- Difficulty escaping Magnet mode.
- Too few remote buttons.
- Children getting trapped in inventory/dialog interfaces.

#### 10.3 Integration risks

- SCUMM architectural differences.
- HE version fragmentation.
- Disagreement over the shared-code location.
- Upstream maintenance concerns.

#### 10.4 Open design decisions

A living decision register. The recommendations are WP-086's proposals. Jeff
decided H1–H5, H7 and H8 on 2026-11-26, and H6 on 2026-11-27 after the
remote capture ([3.2](#32-android-tv-and-gamepad-input)). Status is Jeff's word for each:
Approved, Approved for prototype, Provisional, or Pending.

| # | Question | Alternatives | Recommendation | Evidence | Status | Resolution |
|---|---|---|---|---|---|---|
| H1 | Input integration | (a) a game keymap that binds `JOY_UP`…`JOY_CENTER` while Magnet mode is on; (b) handle raw joystick events in the engine; (c) a new Global keymap | **(a)**: it wins over the Virtual Mouse for those buttons only in games, stays rebindable, and turning it off is the fallback. Add `JOY_HAT_*` for game controllers | E2, E3, E6 | **Approved** (2026-11-26) | (a), a game keymap |
| H2 | Provider interface | (a) `Engine::getHotspotPositions()` as is; (b) it, plus a stable id; (c) a new interface | **(a) first, (b) if keeping the selection across refreshes needs it.** Five engine implementations already fill it, SCUMM's among them; TerraGlyph implementing it also gets the hotspot display | E12, E13, E16 | **Approved for prototype** (2026-11-26) | (a), the existing interface. If refreshing the list makes the selection unstable, investigate stable hotspot ids (b) |
| H3 | Cursor placement | (a) the target's centre; (b) the first point on a small grid, centre first, that hit-tests to the target | **(b)**, as SCUMM does; no such point means not eligible | E16, E18 | **Approved** (2026-11-26) | (b), a validated interaction point. Prefer a point the engine supplies when it has one; otherwise the hit-tested grid. Never assume the rectangle's centre is clickable |
| H4 | Shared-code location | `common/`, `gui/`, `engines/`, `backends/keymapper/`, `graphics/` | **`engines/`**, beside the hotspot display, with the algorithm a standalone class | E11–E15 | **Provisional** (2026-11-26) | `engines/` as the preferred future location, subject to ScummVM maintainer feedback ([13.3](#133-maintainer-feedback-register)). The first implementation stays inside `engines/terraglyph/` |
| H5 | Per-game setting | (a) an engine extra option now, a shared key in Phase 3; (b) a shared key now | **(a)**: a standard option in `TerraglyphMetaEngine`, default off | E14, E23, E24 | **Approved** (2026-11-26) | (a), TerraGlyph-specific at first |
| H6 | Cursor-mode fallback on the remote | (a) hold OK, timed from press to release, with a short press activating on release; (b) BACK or MENU | **(a).** BACK and MENU are taken (skip, main menu, keyboard). The capture supports it: the remote sends one press and one release for a held OK, and Android's repeats (every 50 ms after 400 ms) can be ignored while the button is down. Proposed: a short press activates on release; a hold past a threshold (over 400 ms, so it's a deliberate hold) enters cursor mode, and its release activates nothing | E7, E8, E22, E25, E26 | **Approved** (2026-11-27) | (a), hold OK: a short press activates on release; a hold past a threshold over 400 ms enters cursor mode and its release activates nothing; repeated downs while OK is held are ignored. A long press must never activate a hotspot, and the fallback works on the standard remote with no extra hardware. The input integration packet confirms the event sequence inside ScummVM on the TV (E26's open item) |
| H7 | TerraGlyph eligibility | The rule in 3.5, with or without characters | **The rule in 3.5, without characters at first** | E18–E20 | **Approved** (2026-11-26) | The rule in 3.5: only objects that are visible, eligible and hittable now. Characters come later, once their click behavior is verified |
| H8 | Hotspot refresh | (a) query on each press; (b) every frame, as the display does | **(a)**: navigation only needs the targets when a key is pressed | E13 | **Approved** (2026-11-26) | (a), refresh on directional input. Also invalidate the current selection when game state changes: a hotspot that disappears or is disabled must never stay activatable |
| H9 | Activation (4.2 E) | (a) push `EVENT_LBUTTONDOWN` and `EVENT_LBUTTONUP` through the event queue; (b) call `handleMouse(false, p)` then `handleMouse(true, p)`, as `test_script`'s `click`; (c) the engine sets `_mouseDown`, calls `handleMouse(true, p)` itself, and clears `_mouseDown` after one game tick has seen it | **(c)**: it gives the rooms that read the held button (the corral, Pie Noon, `ButtonRoom`'s pressed frame) a real press, which (b) doesn't; and unlike (a) its release can't be lost, since a movie's event loop drops releases and `warpMouse()` purges queued mouse events, which would leave `_mouseDown` stuck. Ticks are counted in the tick loop (36/s), not frames (60/s) | E31, E34, E35, E40, E41 | Proposed (WP-089) | — |
| H10 | Starting mode and hold threshold (6.1) | Mode: (a) the room class says its starting mode, Magnet by default and cursor mode for the pointer rooms of 6.8, with close-ups and Big Head keeping the player's mode; (b) Magnet at every room change; (c) keep the mode across rooms. Threshold: 600 ms, or another value over 400 ms | **(a) and 600 ms**, tuned in the user-experience tests (12.6). (b) would throw a child out of cursor mode at every close-up | E26, E29, E35, E38 | Proposed (WP-089) | — |
| H11 | Rooms that aren't plain clicks (6.8) | (a) room-class hooks (own targets, a direction for the class, a click with no target, a starting mode), with one assist per room in its own later packet; (b) cursor mode only, and the three hold-and-drag rooms left to a mouse or a gamepad; (c) a drag lock in cursor mode | **(a)**: the Options knobs, Brad's game and the vault's clock can't be played on the remote any other way, since OK sits inside the D-pad ring. The assists aren't designed yet and need a packet in §11 (14.3); until each lands, its room is a Phase 1 gap, playable with a mouse or a gamepad holding `JOY_X` | E35 | Proposed (WP-089) | — |
| H12 | Identity and geometry (4.3) | (a) an identity (source, index) beside the list, and points only; (b) an id or a box on the shared record (H2's (b)) | **(a)**: `HotspotInfo` unchanged; packet 3 raises (b) if its scoring needs a box | E12, E18 | Proposed (WP-089) | — |
| H13 | Room-class targets (4.6) | Extend H7's kinds with the targets a room class adds (a `ButtonRoom`'s visible buttons), or keep H7's kinds only | **Extend**: without it the main menu, level select, quit screen, Sign In and the clue book have no targets. H7's click gate and its other conditions still apply | E36 | Proposed (WP-089) | — |
| H14 | Feedback (6.5) | (a) the game's own cursor and rollover, no marker, and the mode shown by behavior; (b) a one-item marker from ScummVM's hotspot renderer in Magnet mode | **(a) for Phase 1**, with (b) next if the user-experience tests show children can't tell the modes apart | E32 | Proposed (WP-089) | — |
| H15 | The test-build gesture (6.3) | Live with it in test builds and tell testers; ask WP-085's successor to change the gesture | **Live with it**: release builds don't have it, and the gesture is WP-085's | E33 | Proposed (WP-089) | — |
| H16 | Keymap structure (6.4); refines H1 | (a) three keymaps: the default without the directions and with `JOY_A` moved to OK and `JOY_X` to left click, OK always on, the directions in Magnet mode only; the default unchanged when the option is off; (b) one Magnet keymap toggled whole, as H1's wording has it | **(a)**: turning one whole keymap off, as H1 says, would also unbind OK in cursor mode, where the Virtual Mouse can't click; and a direction left in an always-on keymap would keep the Virtual Mouse from the D-pad. H1's intent, that the D-pad goes back to the pointer, is kept | E4, E27, E28, E44 | Proposed (WP-089) | — |

### 11. Development work packets

Work packets live in their own `WP-NNN` files under
[work-packets](../work-packets/WORK_INDEX.md). This plan sets only their
sequence and goals; detailed tasks, files touched, and test procedures belong
in the packets. Numbers are assigned when each packet is drafted.

| # | Proposed packet | WP |
|---|---|---|
| 1 | Input and hotspot-feature research (Section 3 except 3.6) | [WP-086](../work-packets/WP-086-hotspot-magnet-research.md) ✅ |
| 2 | Hotspot Magnet interface design | [WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md) ✅ |
| 3 | Directional algorithm design and test cases (including the reachability check) | [WP-091](../work-packets/WP-091-hotspot-magnet-algorithm.md) 📝 |
| 4 | Directional selection implementation (hand-written) | — |
| 5 | TerraGlyph hotspot provider | — |
| 6 | TerraGlyph input integration | — |
| 7 | Dynamic hotspot handling | — |
| 8 | Configuration and fallback | — |
| 9 | Windows validation | — |
| 10 | Android TV validation | — |
| 11 | Raspberry Pi validation | — |
| 12 | SCUMM/HE research | — |
| 13 | SCUMM maintainer consultation | — |
| 14 | SCUMM/HE prototype | — |
| 15 | Shared code proposal | — |

The two research packets of the first draft are one, and the directional
algorithm is split into its design with test cases and its implementation.

Each packet includes: goal, prerequisites, files touched, design constraints,
hand-written implementation tasks, test procedure, done-when criteria, and
documentation updates.

### 12. Testing and validation matrix

#### 12.1 Test environments

- Windows development environment.
- Smart TV: TCL 65Q77K (Google TV) now; Sony Bravia XBR-75X81CH next.
- Raspberry Pi.

#### 12.2 Navigation tests

- All four directions.
- Reachability: from each eligible hotspot, every other one is reachable by
  D-pad presses, with no subset the player can't leave
  ([5.8](#58-hotspot-reachability)).
- Overlapping, sparse, and dense layouts.
- Edge cases and repeatability.

#### 12.3 Interaction tests

- Click, secondary action, inventory, exits, dialog, cutscenes, and the
  free-cursor fallback.

#### 12.4 Regression tests

- Feature disabled.
- Mouse, keyboard, and existing gamepad behavior.
- Save/load and room transitions.

#### 12.5 Evidence collection

Record for each test: environment, game and version, build identification,
steps, expected and actual result, pass/fail.

#### 12.6 User experience validation

The technical criteria can all pass and the feature still feel confusing.
Watch whether a child can:

- tell which object is selected;
- move to another object without being told how;
- activate the object they meant;
- recover from a wrong selection;
- switch to conventional cursor movement when they need it;
- finish a representative game interaction without a mouse.

These are observational tests, recorded as what was seen, not claims that a
given age group will succeed.

#### 12.7 Test hooks

Designed in WP-089 (Gen 1), so packets 3–8 can be tested without a remote
(E41):

- **Listing every room's targets, headless.** A new self-test check, run
  with the other script checks (the `script` debug channel at level 3),
  enters each room of both titles through `showRoom()`, the live path that
  builds the room class, the script, the toolbar and the inventory, and
  skips the room's opening until the script is idle; until then the list is
  empty by design (4.6). The bare `Room` that `checkAllRooms` builds has none
  of these, so it can't see room-class buttons, toolbar sprites or the click
  gate. For each room the check lists every target with its identity, label
  and point, and fails if a point doesn't hit-test to its sprite or is off
  screen. It also lists **every sprite of an eligible kind that got no
  point**: that's the real risk, since a 4 px grid can miss a thin object.
  Packet 3 builds its reachability graph (5.8) on this list.
- **`test_script` verbs** for a live run, beside the existing `down x y` and
  `up x y`. A pushed hardware event is never mapped by the Keymapper (E44),
  so these call the input adapter directly with Magnet's action starts and
  ends; enabling and disabling the keymaps, and the hand-off to the Virtual
  Mouse, are tested with real input on each device (packets 9–11):

  | Verb | Does |
  |---|---|
  | `nav up`, `nav down`, `nav left`, `nav right` | A directional press and release |
  | `ok` | A short OK press |
  | `okhold <ms>` | OK held for that long |
  | `magnet` | Logs the mode, the selected target and its point |

  The verbs log through `debugC` on the input channel, so a run's log shows
  each step's result.

---

## Part IV — Upstream strategy and governance

### 13. ScummVM community engagement

#### 13.1 Early architectural feedback

Introduce the accessibility problem, describe the proposed approach, ask
about existing solutions, and ask for guidance before the SCUMM integration.

#### 13.2 Draft community post

A short, editable draft for Discord or the ScummVM forum, to be written
after the research.

#### 13.3 Maintainer feedback register

| Date | Contributor/maintainer | Feedback | Architectural implications | Decision or follow-up |
|---|---|---|---|---|
| *(none yet)* | | | | |

#### 13.4 Upstream submission readiness

Working demonstrations, code quality, tests, documentation, review feedback,
and licensing and contribution compliance. The engine's own upstream path is
in the [upstream submission decision brief](upstream-submission-decision-brief.md).

### 14. Decisions, dependencies, and next steps

#### 14.1 Settled project direction

- TerraGlyph is the first implementation.
- SCUMM/HE is the proposed second integration.
- A shared ScummVM contribution is the long-term goal, not a hard dependency.
- Implementation stays in the ScummVM fork.
- Research and work packets stay in this repository.
- All engine C++ is written by hand.

Requirements adopted on 2026-11-26 from the review:

- A cursor-mode fallback that works with the standard remote alone
  ([6.2](#62-cursor-mode-fallback-requirement)).
- Every eligible hotspot reachable ([5.8](#58-hotspot-reachability)).
- Selection, cursor positioning and activation kept separate, with the engine
  supplying the interaction point ([4.2](#42-component-responsibilities),
  [4.5](#45-coordinate-systems)).
- The engine supplies only currently eligible targets ([4.6](#46-eligibility)).
- Observational user-experience tests
  ([12.6](#126-user-experience-validation)).

#### 14.2 Decisions requiring research

- Final module interfaces.
- Input integration strategy (Keymapper or direct events).
- Navigation scoring details.
- Hotspot refresh mechanism.
- Shared-code location.
- SCUMM integration point.
- Cursor placement policy.
- Wrap-around default.
- The remote mapping for the cursor-mode fallback.
- Whether reachability needs a deterministic alternative beyond directional
  input.
- Whether the existing hotspot display offers data reuse, visual reuse,
  both or neither.

#### 14.3 Immediate next steps

1. ~~Run WP-086~~ ✅ 2026-11-26: Section 3 is verified except 3.6.
2. ~~Jeff decides H1–H8~~ ✅ 2026-11-26: H1–H5, H7 and H8 decided in
   [§10.4](#104-open-design-decisions); H6 on 2026-11-27.
3. ~~Capture the TCL remote's buttons~~ ✅ 2026-11-27 (3.2, E26): held OK
   sends one press and one release; Android repeats it.
4. Get early maintainer feedback, which also settles H4.
5. ~~Draft the interface design packet~~ 📝 2026-11-27:
   [WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md), from
   the §10.4 decisions and the remote capture.
6. ~~Run WP-089~~ ✅ 2026-11-27: Part II designed except the algorithm;
   evidence E27–E44, proposals H9–H16.
7. Jeff decides H9–H16 in [§10.4](#104-open-design-decisions).
8. ~~Draft the directional algorithm packet~~ 📝 2026-11-27:
   [WP-091](../work-packets/WP-091-hotspot-magnet-algorithm.md) (§11, packet 3), against the core's
   contract ([4.3](#43-interfaces)) and the target-listing hook
   ([12.7](#127-test-hooks)).
9. Add a packet for the room assists of [6.8](#68-rooms-that-arent-plain-clicks)
   to §11, if Jeff takes H11.

### 15. Appendices

| Appendix | Contents |
|---|---|
| A | Source code reference index, [below](#appendix-a-source-code-reference-index) |
| B | Interface declarations, [below](#appendix-b-interface-declarations) (WP-089) |
| C | Navigation examples (representative layouts and expected behavior); packet 3 |
| D | Terminology, [below](#appendix-d-terminology) (WP-089) |
| E | References (ScummVM contribution guidelines, source references, accessibility guidance, maintainer discussions) |

#### Appendix A: source code reference index

Every file WP-086 read, at the fork's `ff490ad9449f`, with the symbols used.

| File | Symbols |
|---|---|
| `common/events.cpp` | `EventDispatcher::dispatch` |
| `backends/keymapper/keymapper.cpp` | `Keymapper::mapEvent`, `getMappedActions`, `executeAction`, `hardcodedEventMapping` |
| `backends/keymapper/keymap.cpp` | `Keymap::getMappedActions`, `loadMappings`, `getActionDefaultMappings` |
| `backends/keymapper/hardware-input.cpp` | `JOY_UP`…`JOY_CENTER` definitions |
| `backends/keymapper/virtual-mouse.cpp`, `.h` | `VirtualMouse::addActionsToKeymap`, `handleAxisMotion`, `pollEvent`, `notifyEvent`, `computeJoystickMouseSpeedFactor` |
| `backends/keymapper/standard-actions.cpp` | `kStandardActionToggleHotspots` |
| `backends/events/default/default-events.cpp` | Virtual Mouse construction; `EVENT_HOTSPOTS_SHOW`/`HIDE` handling; Global keymap |
| `backends/platform/android/android.cpp` | `getKeymapperDefaultBindings`, feature flags, `kbdmouse_speed` default |
| `backends/platform/android/events.cpp` | `OSystem_Android::pushEvent` (`JE_KEY`, `JE_GAMEPAD`, `JE_DPAD`, `JE_JOYSTICK`, `JE_TV_REMOTE`), `pollEvent` |
| `backends/platform/android/jni-android.cpp` | `JNI::pushEvent` |
| `backends/platform/android/touchcontrols.cpp`, `options.cpp` | `TouchControls::draw`, `update`; `applyTouchSettings` |
| `backends/platform/android/org/scummvm/scummvm/ScummVMEvents.java` | `onKey`, `onGenericMotionEvent`, `processJoystickInput`, BACK/MENU long press |
| `gui/editgamedialog.cpp`, `gui/options.cpp` | `enable_hotspots` and sibling options; Pointer Speed |
| `engines/engine.h`, `engine.cpp` | `getHotspotPositions`, `drawHotspots`, `createHotspotRenderer`, `hotspotDirty`, `showHotspots`, `suspendHotspots`, `effectiveHotspotKeyMode` |
| `engines/metaengine.cpp`, `.h` | `createHotspotAction`, `hotspotsEnabled`, `ExtraGuiOption`, `registerDefaultSettings`, engine-default keymap |
| `engines/advancedDetector.h`, `.cpp` | `ADExtraGuiOptionsMap`, `getAdvancedExtraGuiOptions`, `getExtraGuiOptions` |
| `engines/dialogs.cpp` | `ExtraGuiOptionsWidget::load`, `save` |
| `graphics/hotspot_renderer.h`, `.cpp` | `HotspotType`, `HotspotInfo`, `HotspotStyle`, `HotspotRenderer` |
| `engines/scumm/object.cpp`, `scumm/metaengine.cpp` | `ScummEngine::getHotspotPositions`, `findObject`; keymap opt-in |
| `engines/touche/touche.cpp` | `ToucheEngine::getHotspotPositions` |
| `engines/hollywood/hotspots.cpp`, `monsters/hollywood.cpp`, `runaway/engine.cpp` | `HotspotSource::getHotspotPositions` and both games' overrides |
| `engines/macs2/macs2.cpp` | `getHotspotPositions` and its snapshot |
| `engines/lab/metaengine.cpp`, `lab/engine.cpp`, `lab/processroom.cpp` | "FOCUS" action, `setCurrentClose` |
| `engines/mohawk/riven.cpp`, `riven_card.cpp`; `engines/mads/core/game.cpp`; `engines/grim/grim.cpp`; `agos/metaengine.cpp`; `sword25/metaengine.cpp` | Keyboard hotspot actions (none reusable) |
| `engines/awe/metaengine.cpp`, `detection_tables.h`, `awe.cpp` | Extra-option example |
| `engines/terraglyph/room.h`, `room.cpp`, `cel.cpp` | `Room::hitTest`, `Room::Sprite`, `Kind`, sprite accessors, `getPolygon`, `hitPolygon`, `hitCels` |
| `engines/terraglyph/terraglyph.cpp`, `inventory.cpp`, `inventory.h` | `handleMouse`, `updateHover`, `test_script` click, `checkAllRooms`; toolbar sprites |
| `engines/terraglyph/metaengine.h`, `detection_tables.h`; `chase_check.cpp`, `chase_rooms.h`, `accusation_rooms.h` | Meta-engine overrides, GUIO flags; check harness; close-up and Big Head classes |

Added by WP-089, at `0d5a69c7694f`:

| File | Symbols |
|---|---|
| `engines/metaengine.cpp`, `.h`; `base/main.cpp`; `engines/sky/metaengine.cpp` | `MetaEngine::initKeymaps` (the default game keymap); where game keymaps are added; Sky's own keymap |
| `engines/touche/metaengine.cpp`; `engines/bbvs/bbvs.cpp`, `bbvs/metaengine.cpp` | Two game keymaps with custom actions; toggling one keymap during play |
| `backends/keymapper/keymapper.cpp`, `.h`, `keymap.h`, `keymap.cpp`, `action.h`, `action.cpp`, `hardware-input.cpp` | `getMappedActions`, `mapEvent`, `convertStartToEnd`, `setGameKeymapState`, `getKeymap`, `setEnabled`, `allowKbdRepeats`, axis thresholds, `JOY_HAT_X`/`Y` |
| `backends/events/sdl/sdl-common-events.cpp`, `backends/platform/android/events.cpp` | Hat to D-pad buttons (SDL); hat as axis motion (Android) |
| `gui/gui-manager.cpp`, `engines/engine.cpp` | `saveState`, `restoreState`; `runDialog`, `pauseEngine`, `drawHotspots` |
| `backends/modular-backend.cpp`, `backends/graphics/windowed.h`, `backends/graphics/android/android-graphics.h`, `backends/events/default/default-events.cpp` | `warpMouse`, `setSystemMousePosition`; the event manager's mouse position |
| `graphics/hotspot_renderer.cpp` | `setHotspots`, `exchangeHotspots`, `renderOverlay`, overlay ownership |
| `backends/platform/android/org/scummvm/scummvm/ScummVMActivity.java`, `advanced/…/AdvancedMode.java`, `dists/android/build.gradle` | `dispatchKeyEvent`, the test-build gesture, its debug-only source set |
| `engines/terraglyph/terraglyph.cpp`, `.h` | Main loop, `handleMouse`, `showRoom`, `drawRoom`, `checkAllRooms`, `runTestScript`, `isMouseDown`, `getMousePos` |
| `engines/terraglyph/room.cpp`, `room.h`, `room_class.cpp`, `.h`, `room_script.h`, `inventory.cpp`, `.h` | Kinds, polygon box, `hitsPoint`, cursor sprite; `addButton`, `getButtonSprite`, `isBusy`; `RoomScript::isBusy`; `isInputBlocked`, toolbar parking |
| `engines/terraglyph/options_rooms.cpp`, `pienoon_rooms.cpp`, `corral_rooms.cpp`, `brad_rooms.cpp`, `chase_rooms.cpp`, `maria_rooms.cpp`, `vault_rooms.cpp`, `signin_room.cpp`, `menu_rooms.cpp`, `accusation_rooms.cpp`, `movie.cpp` | The held-button, drag and pointer-reading rooms; the menu rooms' buttons; Sign In's keys; the movie's event loop |

#### Appendix B: interface declarations

Design-level declarations for the Phase 1 prototype (WP-089), with no
function bodies. They're a contract for packets 4–8, not code to paste: the
engine C++ is written by hand (14.1), and a packet that departs from these
records why. Names are proposals. B and C use no TerraGlyph type.

```cpp
// --- B. Navigation core (shared; engines/terraglyph/ in Phase 1, H4) ---
namespace HotspotMagnet {

enum Direction { kDirUp, kDirDown, kDirLeft, kDirRight };

// The index of the target to select, or -1 to stay. current is -1 when
// nothing is selected; from is the cursor's position. repeat comes from the
// input adapter's own clock (4.3). Scoring, what to do with no selection,
// the repeat policy and reachability: packet 3.
int navigate(const Common::Array<Graphics::HotspotInfo> &targets,
             int current, const Common::Point &from,
             Direction dir, bool repeat);

// --- C. Input adapter (shared) ---
enum Mode { kModeMagnet, kModeCursor };
enum Action { kActUp, kActDown, kActLeft, kActRight, kActOk };

struct Result {
	enum Kind { kNone, kNavigate, kActivate, kEnterCursor, kEnterMagnet } kind;
	Direction dir;  // for kNavigate
	bool repeat;    // for kNavigate
};

class InputAdapter {
public:
	// holdMillis: OK's threshold, 600 (H10). The repeat delay and interval
	// are packet 3's; 0 means no repeats.
	InputAdapter(uint32 holdMillis, uint32 repeatDelay, uint32 repeatInterval);
	Result actionStart(Action action, uint32 now);  // device repeats ignored
	Result actionEnd(Action action, uint32 now);    // an end with no start ignored
	Result tick(uint32 now);   // the hold threshold, and the adapter's repeats
	void reset();              // room change, movie, pause: no click
	void setMode(Mode mode);   // the room class's starting mode (H10)
	Mode getMode() const;
};

} // namespace HotspotMagnet

// --- A, D, E. TerraGlyph (Gen 1) ---
struct MagnetTarget {           // a target's identity (4.3, 4.4)
	enum Source { kRoom, kRoomClass } source;
	int index;                  // a sprite, or the class's own target number
};

class TerraglyphEngine {
	// A. Every current target (4.6), for Magnet and the show-all display.
	void getHotspotPositions(Common::Array<Graphics::HotspotInfo> &hotspots) override;
	bool hotspotDirty() const override;  // only after a change (6.5)
	// A. The same list, with each target's identity beside it.
	void listTargets(Common::Array<Graphics::HotspotInfo> &targets,
	                 Common::Array<MagnetTarget> &ids);
	// D. Warp, then push EVENT_MOUSEMOVE (4.5); never while a release is pending.
	void moveCursorTo(const Common::Point &p);
	// E. Re-check (4.4); set _mouseDown and call handleMouse(true, p); the
	// release is made after one game tick has run (H9).
	bool activate(const MagnetTarget &target, const Common::Point &p);
	bool _magnetSelected;            // false for none; cleared in showRoom()
	MagnetTarget _magnetSelection;
	int _magnetReleaseTicks;         // ticks until the pending release, or -1
	HotspotMagnet::InputAdapter _magnetInput;
};

class Room {
public:
	// The current step's polygon box, or the union of the current frame's
	// cels for a cel hit (4.5).
	Common::Rect getHitBox(int sprite) const;
};

class RoomClass {  // proposed (H11); ButtonRoom implements addNavTargets (H13)
public:
	struct NavTarget {
		Common::Point point;
		Common::String label;
		int sprite;                // -1 if the target isn't a sprite
	};
	virtual void addNavTargets(Common::Array<NavTarget> &targets) {}
	virtual bool isNavTargetValid(int index) const { return false; }
	// True if the class took the press (a knob, a clock hand).
	virtual bool navigate(HotspotMagnet::Direction dir) { return false; }
	// True if OK may click with no target (the corral).
	virtual bool clicksWithoutTarget() const { return false; }
	// The mode a player starts this room in (H10). A close-up or Big Head
	// keeps the player's mode instead.
	virtual HotspotMagnet::Mode startMode() const { return HotspotMagnet::kModeMagnet; }
	virtual bool keepsMode() const { return false; }
};

class TerraglyphMetaEngine {
	// The three keymaps of 6.4, or ScummVM's default when the option is off.
	Common::KeymapArray initKeymaps(const char *target) const override;
	const ADExtraGuiOptionsMap *getAdvancedExtraGuiOptions() const override;
};
```

#### Appendix D: terminology

| Term | Meaning here |
|---|---|
| Hotspot | Anything a player can click in a room |
| Target | A hotspot the provider lists now: eligible, hittable, on screen (4.6) |
| Selection | The target Magnet's cursor is on, held as (room, sprite index) (4.4) |
| Interaction point | The point the cursor goes to and the click lands on; it hit-tests to its target (4.5, H3) |
| Magnet mode | The D-pad moves between targets; OK clicks the selection |
| Cursor mode | The D-pad moves the free pointer (the Virtual Mouse); OK clicks at it |
| Provider | Component A: the engine code that lists the targets |
| Navigation core | Component B: picks the next target for a direction, with no engine knowledge |
| Input adapter | Component C: turns Magnet's actions into navigate, click and mode changes |
| Adapter (engine) | Components A, D and E together: TerraGlyph's side |
| Assist | A room class's own handling of a direction or an OK, for rooms that aren't plain clicks (6.8, H11) |

---

## Document governance

This page is the authoritative architecture and roadmap for Hotspot Magnet.
Individual work packets govern implementation, testing, and completion.
Source-dependent conclusions rest on the evidence register; one that isn't in
it stays unresolved.

## Revision history

| Date | Change |
|---|---|
| 2026-11-26 | First version, from Jeff's plan. |
| 2026-11-26 | Accepted as the planning baseline after Microsoft Copilot's review, relayed by Jeff. Adopted its four corrections (remote fallback 6.2, reachability 5.8, separate selection, positioning and activation 4.2/4.5, and data vs visual reuse of the hotspot display 3.3), its eligibility requirement (4.6), its packet resequencing (11) and its user-experience tests (12.6). Also added the link to WP-085's gamepad requirement (1), what WP-018 already established about TerraGlyph hit testing (3.5, 7.2), and an exhaustive per-room reachability check (5.8). |
| 2026-11-26 | WP-086's research: Section 3 verified except 3.6, with the evidence register (E1–E24), the decision register's proposals (H1–H8) and Appendix A. The TCL remote's button capture is still a gap. |
| 2026-11-26 | Jeff's decisions on H1–H8 (10.4): H1, H3, H5, H7 and H8 approved, H2 approved for the prototype, H4 provisional, H6 pending remote testing, each with his conditions. Reachability, never activating a vanished hotspot, and no activation on a long OK press added to the acceptance criteria (7.6, 8.6) and navigation tests (12.2). A second remote capture recorded short presses of the D-pad, OK and BACK (3.2, E25); held presses are still a gap. |
| 2026-11-27 | Third remote capture (3.2, E26): D-pad up's code, and held OK, left and right send one press and one release; Android repeats held keys (400 ms, then every 50 ms), and ScummVM turns each repeat into a new press. Repeating D-pad presses added to the remote limitations (6.3). Jeff approved H6, hold OK (10.4). |
| 2026-11-27 | Packet 2 drafted as [WP-089](../work-packets/WP-089-hotspot-magnet-interface-design.md) (11, 14.3). |
| 2026-11-27 | WP-089 run: Part II designed for the Phase 1 TerraGlyph prototype (4.2–4.6, 5.6, 6.1–6.6, the new 6.8 and 12.7, 7.4, Appendices B and D), evidence E27–E44 at fork `0d5a69c7694f`, proposals H9–H16. Corrected 3.2: ScummVM's default game keymap, which TerraGlyph has today, binds the D-pad to keypad keys (E27). A cold review of the design then corrected it before close: activation owns its press (H9), the click gate and an item in hand are in the filter (4.6), repeats are the adapter's own, and off the TV the D-pad doesn't reach the Virtual Mouse (6.1, E44). E3, E8 and E9 cite `android.cpp`'s new line numbers. |
| 2026-11-27 | Packet 3 drafted as [WP-091](../work-packets/WP-091-hotspot-magnet-algorithm.md) (§11, §14.3). |
