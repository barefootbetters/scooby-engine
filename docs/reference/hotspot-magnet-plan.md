---
layout: default
title: "Hotspot Magnet — directional hotspot navigation plan"
---

# Hotspot Magnet: directional hotspot navigation

> **Status:** Planning baseline. The research in [Section 3](#3-existing-scummvm-architecture-research-findings)
> is done for everything except SCUMM/HE
> ([WP-086](../work-packets/WP-086-hotspot-magnet-research.md), 2026-11-26).
> Jeff decided H1–H5, H7 and H8 in [§10.4](#104-open-design-decisions) the
> same day. H6, the cursor fallback, waits on Jeff; the TCL remote capture it
> needed was done on 2026-11-27. The
> design in Part II is still intent only, and nothing here is built.
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

Pinned commits: fork `origin/scooby-engine` **`ff490ad9449f`**; upstream
`scummvm/scummvm` master **`7b6fa644d74a`** (2026-11-26), merge base
`2982fe324b6c`. Paths are in the fork.

| # | Section | Source (file, symbol) | Verified behavior | Implication for Hotspot Magnet | Still unverified |
|---|---|---|---|---|---|
| E1 | 3.1 | `common/events.cpp` `EventDispatcher::dispatch`; `backends/keymapper/keymapper.cpp` `Keymapper::mapEvent`, `getMappedActions`, `executeAction`; `keymap.cpp` `Keymap::getMappedActions`, `loadMappings` | Events map to actions through enabled keymaps; unmapped events pass raw; a match swallows the raw event | Navigation can be Keymapper actions, rebindable like any other | — |
| E2 | 3.1 | `keymapper.cpp:183-199` `Keymapper::mapEvent`; `keymap.cpp:240` | Game/GUI keymaps first; Global only without an exact match; joystick inputs match exactly | An engine keymap wins over the Virtual Mouse for the same buttons | — |
| E3 | 3.1, 3.2 | `backends/platform/android/android.cpp:742-754` `getKeymapperDefaultBindings`; `hardware-input.cpp:266-270` | Android binds `VMOUSE*` to `JOY_UP`…`JOY_RIGHT` in the Global keymap and GUI interact to `JOY_A`, `JOY_CENTER`, `SELECT` | Binding the D-pad in a game keymap takes it from the Virtual Mouse; disabling that keymap gives it back | — |
| E4 | 3.1 | `backends/keymapper/virtual-mouse.cpp` `addActionsToKeymap`, `handleAxisMotion`, `pollEvent`, `computeJoystickMouseSpeedFactor`; `engines/metaengine.cpp:97-101` | Five movement actions, no click; constant velocity every 12 ms; in-game click is `LCLK` on `MOUSE_LEFT`/`JOY_A` | Conventional cursor mode is the Virtual Mouse as it is | — |
| E5 | 3.1 | `backends/events/default/default-events.cpp:57`; `android.cpp:457`, `:364` | The Virtual Mouse is always built on Android; `kbdmouse_speed` defaults to 2 | No enable step needed for the fallback | — |
| E6 | 3.2 | `ScummVMEvents.java:519-545` `onKey`; `events.cpp:1243-1337` (`JE_GAMEPAD`), `:613-617` (`JE_DPAD`), `:1359-1369` (`JE_JOYSTICK`) | D-pad keys become `JOYBUTTON` events; `JOY_CENTER` is unbound in games; hat D-pads are axis events; `JE_DPAD` is dead | Bind `JOY_UP`…`JOY_CENTER` for the remote; a gamepad hat needs `JOY_HAT_*` too | — |
| E7 | 3.2 | `ScummVMEvents.java:446`, `:456-486`, `:593`; `events.cpp:422-424`; `keymapper.cpp:308` | Key repeats are flagged and dropped; gamepad repeats arrive as new presses; long press only for BACK and MENU | A held OK can be timed from `JOYBUTTON_DOWN` to `UP` in the engine | Whether the TCL's remote repeats a held press |
| E8 | 3.2 | `ScummVMEvents.java:238-261`, `:423-441`, `:508-511`; `android.cpp:711`, `:728`, `:733`; `events.cpp:678-718`, `:1261` | BACK, MENU, volume, play/pause and START/SELECT are taken (table in 3.2) | The fallback can't use BACK or MENU without losing skip, the main menu or the keyboard | — |
| E9 | 3.2 | `gui/options.cpp:290`, `:970`, `:1446`; `android.cpp:592`; `virtual-mouse.cpp:204` | Pointer Speed is `kbdmouse_speed`; no acceleration setting | Magnet mode doesn't need to touch pointer settings | — |
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
| E23 | 3.7 | `engines/advancedDetector.h:400-405`, `:715`; `advancedDetector.cpp:333-341`; `engines/metaengine.h:71-78`; `engines/dialogs.cpp:472-495`; `metaengine.cpp:460-468`; `base/main.cpp:225`; `awe/metaengine.cpp:31-75`, `awe/detection_tables.h:40`, `awe/awe.cpp:195` | Declare, tie to entries by GUIO flag, persist per game, read with `ConfMan.getBool` | The Phase 1 setting is a standard extra option | — |
| E24 | 3.7 | `engines/terraglyph/metaengine.h:29-41`; `detection_tables.h:50-123` | No extra options; only `GUIO_NOMIDI` | Where "Hotspot Assist" goes | — |

---

## Part II — Technical design

**Status: design intent only.** The [§10.4](#104-open-design-decisions)
decisions (2026-11-26) bound it; interfaces and algorithms stay provisional
until the interface design packet, which waits on H6.

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

#### 4.3 Proposed interfaces (sketches)

Design-level concepts only, no implementation:

- Hotspot identifier, bounding rectangle (for navigation geometry only),
  interaction point, category, priority.
- Current selection.
- Directional navigation request.
- Selected target result (or "none").

#### 4.4 Data ownership and lifetime

- Who owns the hotspot list?
- When and how is it refreshed (event-driven or polled)?
- How are stale references avoided on room changes, inventory updates,
  dialogs, and cutscenes?
- What happens if the selected hotspot disappears?

#### 4.5 Coordinate systems

- Original game coordinates.
- Logical rendering coordinates.
- Physical display / overlay coordinates.
- Cursor placement policy inside a hotspot (center, nearest point,
  engine-preferred point, and so on).
- Scaling and aspect-ratio correction.

**Interaction point.** The engine hotspot provider may supply a preferred
interaction point independent of the hotspot's bounding rectangle. The
navigation core must not assume the geometric centre is a valid activation
location. In TerraGlyph a valid point is one where `Room::hitTest()` returns
the intended placement (see [3.5](#35-terraglyph-hotspot-data)); a target with
no such point isn't eligible.

#### 4.6 Eligibility

Who decides whether a hotspot is interactive right now? There's a difference
between an object defined in the game data, an object currently visible, an
object currently clickable, and an object currently meaningful to click.

**Requirement:** the engine hotspot provider supplies only targets the engine
currently considers eligible for interaction. Static object definitions
alone aren't enough when game state controls availability. This keeps
engine-specific scripting out of the shared navigation core.

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

- Moving characters, animated objects.
- Objects that appear and disappear.
- Scene transitions, inventory changes, dialog interfaces, cutscenes.
- The policy when the selected target becomes invalid mid-navigation.

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

#### 6.1 Default control scheme (provisional)

| Input | Proposed action |
|---|---|
| D-pad Up | Previous hotspot above |
| D-pad Down | Next hotspot below |
| D-pad Left | Next hotspot left |
| D-pad Right | Next hotspot right |
| OK / Select | Left-click the selected hotspot |
| Secondary button | Right-click / alternate action |
| Long press | Enter conventional cursor mode (candidate only; see 6.2) |

The mapping stays provisional until Android TV remote capabilities and
Keymapper integration are verified. The existing Virtual Mouse bindings must
be considered.

#### 6.2 Cursor-mode fallback requirement

A long press may already mean something on a remote: holding OK might repeat
the click instead of switching modes.

**Requirement:** Hotspot Magnet must provide a reliable way to enter and
leave conventional cursor mode using only the standard TV remote. The method
must not depend on a system-reserved button, need extra hardware, or
unintentionally activate a game object. Device testing on the TV sets the
final mapping. This is a Phase 1 acceptance criterion
([7.6](#76-phase-1-acceptance-criteria)).

#### 6.3 Standard TV remote limitations

- The physical buttons available.
- **Held buttons repeat** (3.2, E26). Android adds a repeated press 400 ms
  into a hold and then every 50 ms, and ScummVM passes each one on as a new
  button press. Holding a D-pad direction would step through hotspots 20
  times a second unless navigation ignores or slows repeats. The navigation
  algorithm packet must decide which.
- Android TV system-reserved buttons.
- Long-press detection reliability.
- Button conflicts.
- Accessibility implications.

#### 6.4 Gamepad and keyboard support

- Configurable actions via the Keymapper.
- Platform-independent navigation behavior.
- Coexistence with existing engine keymaps.

#### 6.5 Visual feedback

- An optional hotspot outline or marker (possibly reusing the existing
  hotspot display renderer).
- Cursor placement.
- Selection indication.
- Avoiding interference with the game's artwork.
- Highlight rendering limitations across engines.

#### 6.6 Parent-friendly configuration

- A single per-game checkbox: "Hotspot Assist" (or similar).
- Disabled by default.
- Saved configuration.
- Clear fallback instructions in the GUI.

#### 6.7 Accessibility considerations

- Reduced fine-motor requirements.
- Predictable navigation.
- Alternative input devices.
- Possible future support for switch-based navigation.
- Complement, not replace, the existing TTS and hotspot display features.

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
decided H1–H5, H7 and H8 on 2026-11-26; H6 waits on the remote capture
([3.2](#32-android-tv-and-gamepad-input)). Status is Jeff's word for each:
Approved, Approved for prototype, Provisional, or Pending.

| # | Question | Alternatives | Recommendation | Evidence | Status | Resolution |
|---|---|---|---|---|---|---|
| H1 | Input integration | (a) a game keymap that binds `JOY_UP`…`JOY_CENTER` while Magnet mode is on; (b) handle raw joystick events in the engine; (c) a new Global keymap | **(a)**: it wins over the Virtual Mouse for those buttons only in games, stays rebindable, and turning it off is the fallback. Add `JOY_HAT_*` for game controllers | E2, E3, E6 | **Approved** (2026-11-26) | (a), a game keymap |
| H2 | Provider interface | (a) `Engine::getHotspotPositions()` as is; (b) it, plus a stable id; (c) a new interface | **(a) first, (b) if keeping the selection across refreshes needs it.** Five engine implementations already fill it, SCUMM's among them; TerraGlyph implementing it also gets the hotspot display | E12, E13, E16 | **Approved for prototype** (2026-11-26) | (a), the existing interface. If refreshing the list makes the selection unstable, investigate stable hotspot ids (b) |
| H3 | Cursor placement | (a) the target's centre; (b) the first point on a small grid, centre first, that hit-tests to the target | **(b)**, as SCUMM does; no such point means not eligible | E16, E18 | **Approved** (2026-11-26) | (b), a validated interaction point. Prefer a point the engine supplies when it has one; otherwise the hit-tested grid. Never assume the rectangle's centre is clickable |
| H4 | Shared-code location | `common/`, `gui/`, `engines/`, `backends/keymapper/`, `graphics/` | **`engines/`**, beside the hotspot display, with the algorithm a standalone class | E11–E15 | **Provisional** (2026-11-26) | `engines/` as the preferred future location, subject to ScummVM maintainer feedback ([13.3](#133-maintainer-feedback-register)). The first implementation stays inside `engines/terraglyph/` |
| H5 | Per-game setting | (a) an engine extra option now, a shared key in Phase 3; (b) a shared key now | **(a)**: a standard option in `TerraglyphMetaEngine`, default off | E14, E23, E24 | **Approved** (2026-11-26) | (a), TerraGlyph-specific at first |
| H6 | Cursor-mode fallback on the remote | (a) hold OK, timed from press to release, with a short press activating on release; (b) BACK or MENU | **(a).** BACK and MENU are taken (skip, main menu, keyboard). The capture supports it: the remote sends one press and one release for a held OK, and Android's repeats (every 50 ms after 400 ms) can be ignored while the button is down. Proposed: a short press activates on release; a hold past a threshold (over 400 ms, so it's a deliberate hold) enters cursor mode, and its release activates nothing | E7, E8, E22, E25, E26 | **Pending**: capture done 2026-11-27, awaiting Jeff | (a), hold OK, if the TCL 65Q77K capture supports it. The test must show short and long OK presses apart; a long press must never activate a hotspot; the fallback must work on the standard remote with no extra hardware |
| H7 | TerraGlyph eligibility | The rule in 3.5, with or without characters | **The rule in 3.5, without characters at first** | E18–E20 | **Approved** (2026-11-26) | The rule in 3.5: only objects that are visible, eligible and hittable now. Characters come later, once their click behavior is verified |
| H8 | Hotspot refresh | (a) query on each press; (b) every frame, as the display does | **(a)**: navigation only needs the targets when a key is pressed | E13 | **Approved** (2026-11-26) | (a), refresh on directional input. Also invalidate the current selection when game state changes: a hotspot that disappears or is disabled must never stay activatable |

### 11. Development work packets

Work packets live in their own `WP-NNN` files under
[work-packets](../work-packets/WORK_INDEX.md). This plan sets only their
sequence and goals; detailed tasks, files touched, and test procedures belong
in the packets. Numbers are assigned when each packet is drafted.

| # | Proposed packet | WP |
|---|---|---|
| 1 | Input and hotspot-feature research (Section 3 except 3.6) | [WP-086](../work-packets/WP-086-hotspot-magnet-research.md) ✅ |
| 2 | Hotspot Magnet interface design | — |
| 3 | Directional algorithm design and test cases (including the reachability check) | — |
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
   [§10.4](#104-open-design-decisions); H6 pending.
3. ~~Capture the TCL remote's buttons~~ ✅ 2026-11-27 (3.2, E26): held OK
   sends one press and one release; Android repeats it. Jeff decides H6 on
   that evidence.
4. Get early maintainer feedback, which also settles H4.
5. Draft the interface design packet from the §10.4 decisions. It doesn't
   start until the remote capture has verified the input assumptions.

### 15. Appendices

| Appendix | Contents |
|---|---|
| A | Source code reference index, [below](#appendix-a-source-code-reference-index) |
| B | Interface sketches (short design-level C++ declarations, no implementation) |
| C | Navigation examples (representative layouts and expected behavior) |
| D | Terminology (hotspot, active target, logical coordinates, engine adapter, cursor fallback, and so on) |
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
| 2026-11-27 | Third remote capture (3.2, E26): D-pad up's code, and held OK, left and right send one press and one release; Android repeats held keys (400 ms, then every 50 ms), and ScummVM turns each repeat into a new press. H6's evidence is in and waits on Jeff; repeating D-pad presses added to the remote limitations (6.3). |
