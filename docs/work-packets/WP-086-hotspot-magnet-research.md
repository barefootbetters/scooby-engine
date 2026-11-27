---
layout: default
title: "WP-086: Hotspot Magnet research"
---

# WP-086: Hotspot Magnet research — input, hotspot features and TerraGlyph targets

**Status:** ✅ Done (2026-11-26). All 14 exit criteria met
([§Close](#close-2026-11-26)); the TCL remote's button capture is recorded
as a gap, as criterion 5 allows. **Findings landed in:** the
[plan's Section 3](../reference/hotspot-magnet-plan.md#3-existing-scummvm-architecture-research-findings),
its [evidence register](../reference/hotspot-magnet-plan.md#38-research-evidence-register),
[decision register](../reference/hotspot-magnet-plan.md#104-open-design-decisions)
(H1–H8, all proposed or unverified) and
[Appendix A](../reference/hotspot-magnet-plan.md#appendix-a-source-code-reference-index).
**Phase:** 5 (polish and accessibility).
**Depends on:** WP-018 ✅ (TerraGlyph hit testing), WP-021 ✅ (clickables),
WP-079 ✅ (the fork's TV build path, proven on the TCL 65Q77K).
**Unblocks:** the Hotspot Magnet interface design packet (packet 2 of the
[plan's sequence](../reference/hotspot-magnet-plan.md#11-development-work-packets)),
and the decisions in the plan's
[§14.2](../reference/hotspot-magnet-plan.md#142-decisions-requiring-research).
**Companion EC:** [EC-009](../execution-checklists/EC-009-hotspot-magnet-research.md).
**Pre-flight required:** **No.** A research packet: it reads the fork's
source and writes only the plan page and this packet's own records. It
changes nothing under `engines/terraglyph/**`, `docs/formats/**` or
`tools/**`, and classifies no title's generation.
**Targets generation(s):** Gen 1 (*Showdown*, *Phantom*) for the TerraGlyph
findings. The ScummVM findings are about shared code and carry no generation.
**Estimated effort:** about one working day (5–7 hours) across the EC's
steps. **Actual:** one session on 2026-11-26. The source reading ran as three
parallel read-only passes, and every finding the write-up relies on was
re-checked against the source before it went in.

---

## Goal

Replace the unverified bullets in Section 3 of the
[Hotspot Magnet plan](../reference/hotspot-magnet-plan.md) with findings
verified in the source. Every finding names its file and symbol at a pinned
fork commit and goes in the plan's evidence register. The output answers
what the design needs to start: how D-pad input reaches the game today, what
ScummVM's existing hotspot feature already provides, which TerraGlyph
placements count as eligible targets and how to find a point that clicks
them, and where a per-game setting and a shared component would live.

## Background

- **The plan.** [Hotspot Magnet](../reference/hotspot-magnet-plan.md) is
  directional, hotspot-to-hotspot navigation for the standard TV remote. Its
  Part II design is provisional until Section 3 is verified. The 2026-11-26
  review folded into it made four requirements explicit that this research
  must inform: a remote-only cursor-mode fallback (§6.2), reachability of
  every target (§5.8), separate selection, positioning and activation with an
  engine-supplied interaction point (§4.2, §4.5), and engine-decided
  eligibility (§4.6). It also merged the plan's two research packets into
  this one.
- **Why now.** [WP-085](WP-085-tv-app-pipeline.md) requires a gamepad for
  the Play release because the D-pad moves ScummVM's pointer but can't click
  a button or object accurately (Jeff on the TCL, 2026-11-26, WP-085 D2).
  WP-085 leaves D-pad-only control out of scope as the open remote-first
  item; Hotspot Magnet is that item. This WP doesn't change WP-085.
- **What's already known about TerraGlyph** (Gen 1, from WP-018 and WP-021):
  hits test the polygon of a placement's current step (exits, clickables,
  requires and inventory objects, simple sprites) or the cel pixels and masks
  (characters). The hit walk is front to back in draw order, skips hidden
  sprites, and the first hit wins; the engine exposes `Room::hitTest(x, y)`.
  Clickables start stopped at step 0 and move to saved states; the ghost is
  hidden. A box's centre is therefore not a safe click point.
- **Leads in the fork, not yet findings** (seen while drafting, at
  `origin/scooby-engine` `ff490ad9449f`; this WP verifies or corrects them):
  - ScummVM has a shared hotspot display. `engines/engine.h` declares
    `Engine::getHotspotPositions(Common::Array<Graphics::HotspotInfo> &)`,
    `drawHotspots()`, `createHotspotRenderer()`, `showHotspots()` and a
    hotspot key mode (hold or toggle). `Graphics::HotspotInfo` and
    `Graphics::HotspotRenderer` are in `graphics/hotspot_renderer.h`. The
    per-game `enable_hotspots` setting is read and written in
    `gui/editgamedialog.cpp`. The latest change to these files on the fork is
    `a11ac4edcc` (2026-11-17).
  - `getHotspotPositions()` is implemented by `hollywood`, `macs2`, `scumm`
    (`engines/scumm/object.cpp`) and `touche`. **TerraGlyph doesn't implement
    it.** If its data is enough, it may be the shared provider interface
    (data reuse, plan §3.3), and SCUMM already fills it (relevant to Phase 2).
  - The Virtual Mouse is `backends/keymapper/virtual-mouse.{h,cpp}`. Android
    input is `backends/platform/android/events.cpp` (native) and
    `backends/platform/android/org/scummvm/scummvm/ScummVMEvents.java`.
- **Supersession check (2026-11-26).** WORK_INDEX has no input-navigation or
  hotspot-navigation packet; WP-084 and WP-085 touch TV input only at the
  app and launcher level. No format doc covers ScummVM's input code. `git log
  --all` for `magnet`, `hotspot nav`, `WP-086` and `EC-009` finds only the
  plan's own commits.

## Scope

### In scope

All reading is at a pinned fork commit, recorded in EC-009 Step 0; the
default is `origin/scooby-engine` at its tip on the execution date.

1. **Keymapper and Virtual Mouse (plan §3.1).** Record how a key or button
   becomes a Keymapper action; how engine keymaps and global keymaps are
   ordered when both bind the same input; the Virtual Mouse's actions and
   default bindings (which hardware inputs, on which platforms); and how it
   emits mouse movement and clicks. Answer: can an engine keymap claim the
   D-pad directions while the Virtual Mouse is bound to them, and what
   happens to the Virtual Mouse when it does?
2. **Android input (plan §3.2).** Trace a remote D-pad press and an OK press
   from `ScummVMEvents.java` to the event ScummVM's core sees: key code
   mapping, whether D-pad keys arrive as keys or as joystick hat events, key
   repeat on hold, and which keys the backend consumes itself (Back, Menu and
   so on). Record how the Pointer Speed and cursor acceleration settings
   apply, and whether the on-screen virtual gamepad overlay
   (`touchcontrols.cpp`) shows or takes input on a TV with no touch screen.
3. **The remote itself (plan §3.2, §6.2–6.3).** On the TCL 65Q77K, record
   each button of the standard remote: its Android key code, whether it
   reaches an app or is reserved by the system, and what a long press
   produces (repeat events, a separate long-press code, or a system action).
   Use `adb shell getevent -l` (or `dumpsys input` if `getevent` is denied);
   if neither works, record the gap and what the source says instead.
4. **The existing hotspot display (plan §3.3).** Record what
   `Graphics::HotspotInfo` holds (every field); how `getHotspotPositions()`,
   `drawHotspots()` and `HotspotRenderer` are called and when; what the hold
   and toggle key modes do and which action triggers them; and how
   `enable_hotspots` is set and defaulted. For `macs2`, `scumm`, `touche` and
   both `hollywood` games, record what each `getHotspotPositions()` returns
   (rectangle, point, label; filtered to interactive objects or not). Answer
   the plan's data-vs-visual question: (a) can `getHotspotPositions()` serve
   as the Hotspot Magnet provider interface as is, with an addition, or not
   at all, and (b) can the renderer draw a single selected target?
5. **Other navigation in engines (plan §3.3).** Record any engine that
   already moves the cursor between hotspots by keyboard or wheel (start
   with Riven in `engines/mohawk/` and `engines/mads/`), with file and
   symbol, and whether its logic is reusable or engine-bound. A search that
   finds none is recorded as such.
6. **Upstream drift.** Compare the files read in items 1, 2 and 4 between
   the pinned fork commit and `scummvm/scummvm` master on the execution date.
   Record any change that alters a finding; upstream is where Phase 3 lands.
7. **Shared-component location (plan §3.4).** For each candidate in the
   plan's table, record what already lives there that Hotspot Magnet would
   sit beside, and recommend one location with reasons. The recommendation
   is a proposal for Jeff, not a decision.
8. **Per-game configuration (plan §3.7).** TerraGlyph declares no extra
   options today: its `metaengine.cpp` has none and `detection_tables.h`
   gives only `GUIO1(GUIO_NOMIDI)`. Record the mechanism from
   `engines/advancedDetector.h` (`ADExtraGuiOptionsMap`,
   `getAdvancedExtraGuiOptions()`) and one engine that uses it, the GUIO flag
   that ties an option to a game entry, how the value persists per game, and
   how an engine reads it at run time. Name the exact place a default-off
   "Hotspot Assist" option would be declared. Also record whether a shared
   per-game option like `enable_hotspots` (an edit-game-dialog checkbox) is
   the better model.
9. **TerraGlyph targets (plan §3.5), Gen 1.** From `room.h`/`room.cpp`,
   `cel.h`, `inventory.cpp` and the room-setup code, record: the placement
   fields that give kind, hidden state, current step and draw order; how a
   room's live placements can be listed; which kinds should count as
   eligible (propose a rule, including whether characters and simple sprites
   are targets); and how the toolbar rooms, the inventory and close-ups
   change what can be clicked. Propose a method for an interaction point that
   `Room::hitTest()` resolves to the intended placement, and say how it
   behaves when a placement is fully covered by another. Record whether a
   room's eligible placements can be listed in the headless self-test, which
   the plan's §5.8 reachability check needs.
10. **Decision register (plan §10.4).** Add a row for each §14.2 decision the
    findings bear on, with alternatives, a recommendation and its evidence.
    Status is **proposed** or **unverified**, never settled: those are
    Jeff's calls.

### Out of scope

- **SCUMM/HE research (plan §3.6).** Packet 12 of the plan. Item 4 records
  only what `engines/scumm/object.cpp`'s `getHotspotPositions()` returns, as
  a lead for packet 12.
- **Any code.** No fork branch, no prototype, no engine or backend change. The
  interface design is packet 2 and the algorithm packets 3 and 4.
- **Choosing the remote mapping.** Item 3 records what the remote can do;
  the mapping is decided in the configuration-and-fallback packet (8) and
  confirmed in Android TV validation (10).
- **Maintainer contact and the community post** (plan §13). Packet 13.
- **The Sony Bravia XBR-75X81CH.** The next test TV, for the validation
  packets.

## Dependencies

- The fork at `C:\dev\scummvm`, read only, through `git show` and `git grep`
  against the pinned commit. Never switch branches in the shared checkout,
  and create no fork branch (exit criterion 10).
- `scummvm/scummvm` master, fetched (item 6).
- The TCL 65Q77K with wireless debugging paired, per the
  [smart-TV guide](../reference/scummvm-smart-tv.md) (item 3).
- WP-018 and WP-021's findings.

## Investigation plan

EC-009 runs the steps in this order: pin the commit; Keymapper and Virtual
Mouse; Android input; the remote on the TV; the hotspot display and its four
engines; other engine navigation; upstream drift; TerraGlyph targets;
configuration and location; then the write-up. Each step records its findings
in the evidence register as it goes, so a stopped session loses nothing.

## Output specification

All findings go into the [plan page](../reference/hotspot-magnet-plan.md):

- **§3.1–3.5 and §3.7:** each bullet becomes a finding, an answered question,
  or an explicit "not found" or "unverified" line. The headings stay.
- **§3.8 evidence register:** a table with one row per finding:

  | # | Section | Source (file, symbol, commit) | Verified behavior | Implication for Hotspot Magnet | Still unverified |
  |---|---|---|---|---|---|

  Device findings (item 3) cite the command and the date instead of a file.
- **§10.4 decision register:** rows per Scope item 10.
- **Appendix A:** the source reference index, one line per file read, with
  the symbols used.
- **§11:** packet 1 marked done once this WP closes.

## Exit criteria

1. The pinned fork commit, and the upstream master commit compared in item 6,
   are recorded in the plan's §3.8.
2. Each of §3.1, 3.2, 3.3, 3.4, 3.5 and 3.7 has no unverified bullets left:
   each is a finding cited in the evidence register, or marked "not found" or
   "unverified" with the reason.
3. The evidence register has a row for every finding, each with a file and
   symbol (or, for the TV, a command and date), and Appendix A lists every
   file read.
4. The Keymapper question in item 1 (can an engine keymap claim the D-pad
   while the Virtual Mouse holds it) has a yes or no with its source.
5. The remote table from item 3 lists every button on the TCL's remote with
   key code, reserved or not, and long-press behavior, or the gap is
   recorded with the commands tried.
6. Item 4's two questions (provider interface: as is, with an addition, or
   not at all; renderer: can or can't draw one selected target) each have an
   answer with its source, and each of the four engines' implementations is
   described.
7. Item 9 gives a proposed eligibility rule and a proposed interaction-point
   method for Gen 1, each citing the TerraGlyph symbols it relies on, and a
   yes or no (with source) on listing eligible placements headlessly.
8. Item 7 gives one recommended location with its reasons.
9. Item 5 lists each engine found that moves the cursor between hotspots,
   with file, symbol and reusable or not, or records that none was found and
   the searches run.
10. Item 6 lists each file that changed between the pinned commit and
    upstream master, and for each, whether a finding changes.
11. Item 8 names the file and symbol where a default-off "Hotspot Assist"
    option would be declared, and says whether the `enable_hotspots` model
    fits better.
12. The §10.4 register has a row for each §14.2 decision the findings bear
    on, none marked settled.
13. `git diff --name-only main` lists only the plan page, this WP, EC-009 and
    `WORK_INDEX.md`; the fork has no new branch or commit from this WP.
14. The wiki's strict build passes
    (`hugo --config ewiki/hugo.toml --minify --panicOnWarning`).

## Deliverables

- **Committed:** the plan page's updated §3, §3.8, §10.4, §11 and Appendix A;
  this WP's status and findings links; EC-009 with its outcomes;
  the WORK_INDEX row.
- **Local only:** raw `getevent` or `dumpsys` captures and any scratch notes.
  Only the key codes and behaviors go into the plan.

## Notes

- **Hand-written engine code.** The plan's §14.1 holds that all engine C++ is
  written by hand. This WP writes none; its findings are the inputs for the
  packets that do.
- **Facts, not designs.** Where the research suggests a design, record it as
  a proposal in §10.4, not in Part II. Part II changes in the interface
  design packet.
- **Copyright.** Findings cite ScummVM's GPL source by path and symbol and
  quote only short identifiers. No game data is involved beyond the room
  layouts WP-018 already characterized.

## Close (2026-11-26)

| # | Exit criterion | Met | Evidence |
|---|---|---|---|
| 1 | Pinned commits recorded | ✅ | Plan §3.8: fork `ff490ad9449f`; upstream master `7b6fa644d74a`, merge base `2982fe324b6c` |
| 2 | §3.1–3.5 and §3.7 have no unverified bullets left | ✅ | Each is a finding with an E-number, or marked unverified with the reason (E7 repeat, E15 TV look, E16, E17, E18, E19) |
| 3 | A register row per finding; Appendix A lists every file read | ✅ | E1–E24; Appendix A |
| 4 | Engine keymap vs the Virtual Mouse on the D-pad | ✅ | **Yes**: E2 (`keymapper.cpp:183-199`), E3 (`android.cpp:742-754`) |
| 5 | The remote table, or the gap with the commands tried | ✅ (gap) | E22: `getevent -lt` (3 min, no presses), `getevent -lp`, `dumpsys input`; devices listed |
| 6 | Item 4's two questions, and the implementations described | ✅ | Plan §3.3: provider usable as is (stable id may need adding); renderer marks one target only as a one-item list; E16 covers scumm, touche, macs2 and both hollywood games |
| 7 | Eligibility rule, interaction-point method, headless listing | ✅ | Plan §3.5 (E18–E20); headless listing **yes** (E20) |
| 8 | One recommended location | ✅ | Plan §3.4: `engines/` (H4) |
| 9 | Other engine navigation | ✅ | E17: Lab's FOCUS only; Riven, MADS, Grim, AGOS, Sword25 described |
| 10 | Upstream drift | ✅ | E21: only `735ad86c21` (mouse pointer capture), no finding changes |
| 11 | Where "Hotspot Assist" is declared; the `enable_hotspots` model | ✅ | E24: `TerraglyphMetaEngine::getAdvancedExtraGuiOptions()` plus a `GAMEOPTION_` flag in `detection_tables.h`; E14 and H5 |
| 12 | Decision register, none settled | ✅ | H1–H8: seven proposed, H6 unverified |
| 13 | Only the four files changed; no fork branch | ✅ | `git diff --name-only main` lists the plan page, WP-086, EC-009 and `WORK_INDEX.md`; the fork was read through `git show`/`git grep` only |
| 14 | Strict wiki build passes | ✅ | `hugo --config ewiki/hugo.toml --minify --panicOnWarning`, 0 warnings |

**For the next packet.** H1–H8 are Jeff's to decide before the interface
design packet is drafted. H6 (the fallback button) also needs the remote
capture: run `adb shell getevent -lt` on the TCL and press each button short,
then held for 2 s.
