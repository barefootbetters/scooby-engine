---
layout: default
title: "Hotspot Magnet — directional hotspot navigation plan"
---

# Hotspot Magnet: directional hotspot navigation

> **Status:** Planning baseline. The research in [Section 3](#3-existing-scummvm-architecture-research-findings)
> isn't done, so the design in Part II is intent only and nothing here is
> built. The first work packet, [WP-086](../work-packets/WP-086-hotspot-magnet-research.md),
> is that research. **Date:** 2026-11-26, revised the same day after a review
> ([Revision history](#revision-history)). **Author:** Jeff (with AI
> assistance).
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

**This section must be completed from actual source-code inspection before
Sections 4–6 are finalized.** The findings below are unverified assumptions
or high-level observations, except where 3.5 cites an earlier work packet.
[WP-086](../work-packets/WP-086-hotspot-magnet-research.md) does the research
for 3.1–3.5 and 3.7; 3.6 (SCUMM/HE) is a later packet.

#### 3.1 Keymapper and input events

- Keymapper architecture and engine-specific actions.
- The Virtual Mouse implementation (`backends/keymapper/virtual-mouse.*`) and
  its default D-pad / joystick bindings.
- Mouse movement and click emulation paths.
- Opportunities for reuse versus conflicts with existing arrow-key / D-pad
  bindings.

#### 3.2 Android TV and gamepad input

- Android backend D-pad handling (mapped to the Virtual Mouse by default).
- The difference between remote D-pad button events and gamepad HAT/axis
  events.
- Cursor acceleration and the Pointer Speed setting.
- Long-press detection and system-reserved buttons.
- Virtual gamepad overlay behavior.

#### 3.3 Existing hotspot navigation and display features

- The recent shared "Enable hotspot display" feature (visual markers and
  labels, configurable style).
- Engines with hotspot highlighting or object cycling (Riven keyboard
  navigation, MADS, others).
- Mouse-wheel cursor-cycling implementations.
- Existing keyboard navigation that could be reused or conflict.

Two different kinds of reuse, which the research keeps apart:

- **Visual reuse:** Hotspot Magnet draws the selected target with the
  existing hotspot display's renderer.
- **Data reuse:** Hotspot Magnet gets hotspot geometry through an existing
  shared interface that engines already fill.

Find out whether the hotspot display exposes reusable hotspot geometry or
only draws it. Don't assume the display system can serve as a hotspot
provider until the source shows it.

#### 3.4 Shared component conventions

Evaluate the candidate locations and recommend one, with reasoning:

| Location | Evaluation |
|---|---|
| `common/` | General-purpose navigation logic |
| `gui/` | User interface integration |
| `engines/` | Engine-facing helper |
| `backends/keymapper/` | Input mapping integration |
| `graphics/` | Possible synergy with the hotspot display renderer |

#### 3.5 TerraGlyph hotspot data

Already established (Gen 1: *Showdown* and *Phantom*):

- **`object.ini` names the objects and their kinds, not their shapes.** It
  is catalogued in [WP-008](../work-packets/WP-008-object-ini-catalog.md).
  The kinds that matter here are `exitobject`, `clickableobject`,
  `requiresobject` and `inventoryobject`; simple sprites and characters can
  also be hit.
- **Hits are polygons and pixels, not rectangles**
  ([WP-018](../work-packets/WP-018-hotspots-and-exits.md)). Exits,
  clickables, requires and inventory objects test the polygon of their
  *current animation step*. Characters test their cel pixels and masks. The
  hit walk goes front to back in draw order, skips hidden sprites, and the
  first hit wins. The engine exposes this as `Room::hitTest(x, y)`.
- **So a shape's bounding box isn't a click target.** The box's centre can
  fall outside a concave polygon, or under a sprite drawn in front, and a
  hotspot's shape changes as its animation steps.
- **Availability is runtime state.** Clickables start stopped at step 0 and
  move to saved states ([WP-021](../work-packets/WP-021-clickable-actions.md)).
  The ghost is hidden. Rooms, the toolbar rooms and close-ups change what can
  be clicked.

For WP-086 to answer: which placements count as *eligible* (an
interactive kind, not hidden, not under the toolbar or a dialog), whether
characters are interaction targets, and how to find an interaction point that
`Room::hitTest()` resolves to the intended placement.

#### 3.6 SCUMM / Humongous Entertainment

- Object storage, coordinates, and bounding boxes.
- Room transitions and interactive object availability.
- Differences between HE game versions.
- Candidate integration points.

#### 3.7 Per-game configuration

- The `ExtraGuiOptions` pattern.
- Configuration persistence.
- Engine-specific feature availability declarations.
- Default-disabled behavior.

#### 3.8 Research evidence register

For every finding, record:

- Source file path and the relevant class/method.
- Verified behavior.
- Implications for Hotspot Magnet.
- Remaining unverified assumptions.

---

## Part II — Technical design

**Status: design intent only.** Interfaces and algorithms are provisional
until Section 3 is complete.

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

- Every eligible hotspot can be reached and selected ([5.8](#58-hotspot-reachability)),
  checked for every room's starting state in both Gen 1 titles.
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

A living decision register. Mark each row settled, proposed, or unverified.

| Question | Alternatives | Recommendation | Evidence | Status | Resolution |
|---|---|---|---|---|---|
| *(none yet)* | | | | | |

### 11. Development work packets

Work packets live in their own `WP-NNN` files under
[work-packets](../work-packets/WORK_INDEX.md). This plan sets only their
sequence and goals; detailed tasks, files touched, and test procedures belong
in the packets. Numbers are assigned when each packet is drafted.

| # | Proposed packet | WP |
|---|---|---|
| 1 | Input and hotspot-feature research (Section 3 except 3.6) | [WP-086](../work-packets/WP-086-hotspot-magnet-research.md) 📝 |
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

1. Run [WP-086](../work-packets/WP-086-hotspot-magnet-research.md): the
   source-code research for Section 3 (except 3.6), with every finding in the
   evidence register.
2. Resolve the architecture decisions it makes answerable.
3. Get early maintainer feedback.
4. Draft the interface design packet.

### 15. Appendices

| Appendix | Contents |
|---|---|
| A | Source code reference index (verified paths, classes, methods) |
| B | Interface sketches (short design-level C++ declarations, no implementation) |
| C | Navigation examples (representative layouts and expected behavior) |
| D | Terminology (hotspot, active target, logical coordinates, engine adapter, cursor fallback, and so on) |
| E | References (ScummVM contribution guidelines, source references, accessibility guidance, maintainer discussions) |

---

## Document governance

This page is the authoritative architecture and roadmap for Hotspot Magnet.
Individual work packets govern implementation, testing, and completion.
Source-dependent conclusions stay unresolved until the ScummVM source is
inspected.

## Revision history

| Date | Change |
|---|---|
| 2026-11-26 | First version, from Jeff's plan. |
| 2026-11-26 | Accepted as the planning baseline after Microsoft Copilot's review, relayed by Jeff. Adopted its four corrections (remote fallback 6.2, reachability 5.8, separate selection, positioning and activation 4.2/4.5, and data vs visual reuse of the hotspot display 3.3), its eligibility requirement (4.6), its packet resequencing (11) and its user-experience tests (12.6). Also added the link to WP-085's gamepad requirement (1), what WP-018 already established about TerraGlyph hit testing (3.5, 7.2), and an exhaustive per-room reachability check (5.8). |
