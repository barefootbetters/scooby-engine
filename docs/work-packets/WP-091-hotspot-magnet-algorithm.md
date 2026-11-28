---
layout: default
title: "WP-091: Hotspot Magnet directional algorithm"
---

# WP-091: Hotspot Magnet directional algorithm — rules, reachability and test cases

**Status:** 📝 Drafted (2026-11-27).
**Phase:** 5 (polish and accessibility).
**Depends on:** WP-089 ✅ and Jeff's decisions H1–H8 ✅. WP-089 gives the
interface design: the core's contract in the plan's
[§4.3](../reference/hotspot-magnet-plan.md#43-interfaces) and the
target-listing hook in
[§12.7](../reference/hotspot-magnet-plan.md#127-test-hooks). This packet also
builds on WP-089's proposals H9–H16 as written. If Jeff changes H11, H12 or
H13 before it runs, the EC's pre-flight says what to redo.
**Unblocks:**
- packet 4 of the
  [plan's sequence](../reference/hotspot-magnet-plan.md#11-development-work-packets),
  the core's implementation, which writes the C++ by hand from this
  packet's rules and transcribes its test cases;
- the reachability check that packet 5's provider runs.

**Companion EC:** [EC-013](../execution-checklists/EC-013-hotspot-magnet-algorithm.md).
**Pre-flight required:** **No.** A design packet. It reads the fork's source
and published references, and writes only:
- the plan page;
- this packet's own records;
- the dashboard note.

It changes nothing under `engines/terraglyph/**`, `docs/formats/**` or
`tools/**`, and classifies no title's generation.
**Targets generation(s):** none for the core, which carries no generation;
the room layouts it tests against are Gen 1 (*Showdown*, *Phantom*).
**Estimated effort:** about one working day (6–8 hours) across the EC's
steps.

---

## Goal

Design the navigation core: the pure function that picks the next target.
Its inputs are the targets, the current selection, the cursor's position, a
direction, and whether the press is a repeat.

The output is the plan's §5, with rules precise enough that packet 4 can
write the C++ by hand without choosing anything:
- which targets count as lying in a direction;
- how they're scored and tied;
- what happens when none does;
- where navigation starts with no selection;
- how held presses repeat.

It also gives:
- an argument that the rules make **every eligible target reachable from
  every other, with no subset the player can't leave** (Jeff's requirement,
  plan §5.8);
- navigation examples with expected results, which become packet 4's unit
  tests (the plan's Appendix C);
- the design of the per-room reachability check over both Gen 1 titles.

## Background

- **The contract this works within** (plan §4.3, WP-089). One pure function,
  `HotspotMagnet::navigate()` in Appendix B.
  - **It receives:**
    - the target list, as `Graphics::HotspotInfo` entries (a point, a name
      and a type);
    - the current selection's index, or none;
    - the cursor's position;
    - the direction (up, down, left, right);
    - a repeat flag.
  - **It returns** the index to select, or none to stay.
  - **It keeps no state and names no engine type.**
  - **It is called** only in Magnet mode, on a directional press, after the
    provider has rebuilt the list (H8).
- **What the list guarantees** (plan §4.5, §4.6):
  - Every target's point is on screen (0–639 × 0–479).
  - Every **sprite** target's point hit-tests to that sprite. A room-class
    target can have no sprite (Sign In's rows, the jigsaw's places). Its
    validity comes from the class's hook (§4.4).
  - **No two sprite targets share a point.** `Room::hitTest()` returns one
    sprite, the first hit front to back (`room.cpp:886-897`), and §4.5
    re-checks every cached point at each rebuild. A room-class target
    supplies its own point (H11), so it can coincide with another target's.
    Two targets at one point lie in no direction from each other, so a
    points-only rule would strand one of them.
  - The list is empty while a scene runs, input is blocked or the room class
    is busy.
  - §4.5 drops toolbar sprites that are off screen. So while the toolbar is
    closed, its slots probably aren't targets, and the van, which opens it,
    is (`Inventory::clickToolbar()`, `inventory.cpp:452-473`). Which toolbar
    sprites are on screen when it's closed is for the execution to confirm.
  - Its order is the provider's, which nothing yet makes stable across
    rebuilds. **Tie-breaking must not depend on it.**
- **Points only, for now** (proposed H12). The core sees no boxes. Scoring
  that needs a target's extent, such as a beam test, would raise H2's
  condition (b): an id or box on the shared record. The core can't tell
  whether the cursor is *over* a target either, since that takes a hit
  test. This packet decides whether points are enough. If they aren't, it
  says so as a register row rather than designing a box in.
- **Repeats** (plan §4.3, §6.3):
  - The input adapter ignores device repeats. It reports its own while a
    direction is held, from its own clock, at a delay and interval this
    packet sets. "Never" is allowed.
  - Its clock is the engine tick (36 a second), so an interval is a whole
    number of ticks.
  - The flag reaches the core, so a repeat can behave differently, for
    example never wrapping.
  - §6.3 also says the policy must cover the TCL remote occasionally
    reporting one press twice (E33). That is unconfirmed on the TV.
- **Two contradictions in the plan this packet must settle.**
  - **How repeats are detected.** §6.3 still says the adapter marks "a
    start while the direction is already held" as a repeat. §4.3 says device
    starts are ignored and repeats come from the adapter's clock.
  - **What a scene does to the selection.** §5.6 says a running scene, a
    pick-up movie or a busy room class *keeps* the selection. The §4.4
    table *drops* it. This decides where the first press after a scene or a
    dialog starts from.
- **Rooms that take the direction themselves** (proposed H11).
  - A room class may handle a directional press itself (§6.8), and then the
    core isn't called. A knob that takes left and right leaves the core only
    up and down in that room.
  - Everywhere else the core's rules apply. That includes the menu rooms,
    whose `ButtonRoom` buttons are targets under proposed H13.
- **The reachability requirement** (plan §5.8, Jeff, 2026-11-26).
  - **The requirement:**
    - every eligible hotspot is reachable from every other through a finite
      sequence of D-pad inputs, with no trap;
    - the algorithm handles isolated, overlapping and unusually placed
      hotspots.
  - **The plan's notes:**
    - Scoring alone can strand a target, for example the middle one of three
      on a diagonal.
    - A deterministic alternative is acceptable if direction alone can't
      guarantee reachability. One example is a reading-order cycle when
      nothing lies in the pressed direction.
  - **As a graph property** it is **strong connectivity** over one room's
    target list:
    - Each target, under each direction the room leaves to the core, has one
      successor from a press (not a repeat). The successor is itself when
      the press stays.
    - That graph must be strongly connected.
  - **What the graph doesn't cover:**
    - **No selection.** This state is indexed by the cursor's continuous
      position, so it needs its own rule.
    - **A changing graph.** The graph is a snapshot. Moving targets, the
      toolbar opening and a class target's validity all change it between
      presses. Strong connectivity per snapshot doesn't prove reachability
      while it changes. That belongs to the live tests (§12.2).
- **Where the tests can run** (fork `d18cb6688450`, read while drafting):
  - ScummVM's unit tests are CxxTest headers under `test/`.
  - An engine's tests live in `test/engines/<engine>/`. They link against
    the engine's library when the engine is built as a static plugin. See
    the twine, ultima and wintermute blocks in `test/module.mk`, and
    `test/engines/twine/gridtest.h`.
  - `test/module.mk` has no TerraGlyph block, and TerraGlyph is off by
    default (`configure.engine`, `add_engine terraglyph … no`). Running the
    core's cases there means packet 4 adds a block to a shared ScummVM file.
    Plan §7.1 allows that only if the prototype strictly needs it.
  - The per-room check needs the games, so it runs in the engine's self-test
    instead (§12.7).
- **Real layouts aren't available as data yet.**
  - The listing hook (§12.7) is designed, not built, so this packet can't run
    the real check. It designs the check and its synthetic examples, and
    states what packet 5 runs.
  - `tools/probe_art.py` decodes *Showdown*'s room placement lists: a
    148-byte `PLACEMENT` record per placed object, with its position. That
    could give approximate object positions offline as an early read, but it
    has no hit test, eligibility or room class, so it can't stand in for the
    check.
- **Prior art.**
  - **Lab's "FOCUS" cycle** (E17) is the only ScummVM engine that moves the
    cursor between items.
    `LabEngine::setCurrentClose()` (`engines/lab/processroom.cpp:170`) steps
    through close-ups in data order and wraps. With no close-up under the
    cursor, it takes the first.
  - **Android's D-pad focus search** (`FocusFinder`) and the **W3C *CSS
    Spatial Navigation* draft** are named as sources for the execution to
    read. The draft has checked none of their details.
- **Fork drift since WP-089's pin `0d5a69c7694f`.** The tip is now
  `d18cb6688450`, with three merges:
  - **WP-083's *Phantom* Wizard's Rule room.** A new `WizardsRuleRoom`
    class, registered at `room_class.cpp:241`. Its `click(sprite)` and
    `tick()` are at `wfr_rooms.cpp:284` and `:292`. It reads no pointer or
    held button. Its targets are the six `OBJ_WFR_BOTTLES` placements, which
    the class catches through `RoomClass::click()`. If their kind isn't
    eligible under H7, Magnet mode has no targets there unless the class
    adds them through the hook (H11, H13). The room is busy during each
    dance, so the selection drops every round.
  - **A drawbridge flag fix** (`drawbridge_rooms.cpp`, `drawbridge_check.cpp`).
  - **WP-090's *Phantom* Knights of the Snack Table.** A new `KstRoom` that
    reads the pointer's y and the held button (`kst_rooms.cpp:596`, `:614`,
    `:738`), so it's a held-button room for §6.8. It also changes
    `Room::Actor` in `room.cpp` and `room.h`; `hitTest()` is untouched.

  None of the three touches the keymapper, events or hotspot code.
- **Supersession check (2026-11-27).** WORK_INDEX has no other algorithm or
  navigation packet, and plan §11 names this as packet 3. No open PR or other
  branch names WP-091 or EC-013. WP-090 (merged) is Phantom's serving game,
  and WP-088 and EC-011 are still held by the Play internal-testing draft, so
  this packet takes 091 and EC-013.

## Scope

### In scope

All reading is at a pinned fork commit, recorded in EC-013 Step 0. The
default is `origin/scooby-engine` at its tip on the execution date.

1. **Re-pin and drift.**
   - Record the pinned commit in plan §3.8 and the Part II status line.
   - List every file changed since `0d5a69c7694f`, and record each change
     that alters a finding or a citation.
   - Give every room class added since then its own §6.8 row, citing a new
     evidence row (E45 onward) at the new pin: Wizard's Rule, KST and any
     later one. E35 and E36 stay as they are. For Wizard's Rule, the row says
     whether the bottles are an eligible kind or need the class's target
     hook.
2. **Prior art** (plan Appendix E, first filled here). Read Android's focus
   search, the CSS Spatial Navigation draft and Lab's cycle. Record for each:
   - what it filters on;
   - how it scores;
   - what it does with nothing in a direction;
   - whether it claims reachability.

   External sources go in Appendix E, not in the fork evidence register.
3. **The origin of a press** (§5.1, §5.5). Say which point a press measures
   from in each of these cases, and which side decides each, the provider or
   the core:
   - **with a selection:** that target's point;
   - **with a selection but the cursor elsewhere:** after a mouse move on
     Windows, a trip into cursor mode, or a point re-searched after its
     sprite moved. Either drop the selection or measure from the target;
   - **with none:** the cursor's position;
   - **with none, the cursor over a target:** the core can't tell (it
     needs a hit test). Recommended: the provider passes that target as
     `current`;
   - **after a room change, a close-up, a scene, a dialog or the main menu.**
     Settle the §5.6 / §4.4 contradiction, and make §5.5 and §5.6 agree
     with the result.

   Any change to what the provider passes is raised as a row, not made to
   the contract.
4. **The candidate filter** (§5.1). Say which targets lie "in" a direction
   from the origin: a half-plane, a cone of a stated angle, or another rule.
   State the boundary cases (on the axis, on the cone's edge) exactly, with
   the screen's y axis pointing down.
5. **Scoring and tie-breaking** (§5.2).
   - Give the score as a formula over the origin and the candidate's point:
     alignment, distance and their weights.
   - Use **integer arithmetic only** (squared distances, dot and cross
     products). Otherwise near-ties could break differently on x86 and ARM,
     and the 4 px grid makes exact ties common.
   - Say whether `HotspotInfo::type` (exit or object) changes anything.
   - Give a tie-break that is total and independent of list order, for
     example by point (y, then x).
6. **Nothing in the direction, and wrap** (§5.3, §5.4).
   - Say what a press with no candidate does: stay, wrap to the far side, or
     a deterministic fallback.
   - Say whether a repeat does the same.
   - Name the default, and whether it's fixed or configurable.
7. **The reachability guarantee** (§5.8). One of these is required:
   - an argument that items 3–6, applied to any set of distinct on-screen
     points with presses only, always give a strongly connected graph;
   - a deterministic alternative that makes it so, added and argued;
   - a plain statement that points alone can't guarantee it, with H2's
     condition (b) raised as a register row.

   In every case, also state:
   - reachability over **the directions a room leaves to the core**, so a
     room class that takes some (H11) is covered;
   - that **no selection is never a trap**. The no-selection rule must be
     total, so that any press with a non-empty list selects something. Then
     every target is reachable from any cursor position;
   - that a repeat never needs to differ for reachability to hold;
   - the shape of the worst case: the most presses between two targets for
     the list sizes Gen 1 has.
8. **Repeat policy** (§6.3).
   - Give the adapter's repeat delay and interval in ticks, or "never". Say
     how a repeat differs from a press, if it does.
   - Say why, for a child on a remote with no hardware repeat.
   - Say how the policy handles a press reported twice (E33).
   - Replace §6.3's "a start while the direction is already held" sentence,
     so §6.3 agrees with §4.3.
9. **Special cases** (§5.3). Give a rule or a worked answer for each:
   - overlapping and nested sprites (distinct points, close together);
   - a large object represented by one point;
   - closely spaced targets;
   - one target, and none;
   - targets in a row or a column (the menus);
   - targets at equal distance;
   - equal points. Recommended: packet 5's provider guarantees distinct
     points, for example by merging a class target with the room target of
     the same sprite (`ButtonRoom`'s buttons are room sprites). Raised as a
     row rather than handled in the core;
   - targets outside the view. Answered by a cross-reference: §4.5 drops
     them.
10. **Performance** (§5.7).
    - State the core's cost per press in the number of targets.
    - State the largest list Gen 1 can give, from the self-test's room sprite
      counts or `probe_art.py`'s placement counts.
    - Confirm the core does no per-frame work.
11. **Navigation examples** (plan Appendix C). Write a set of named synthetic
    layouts. Each is a list of points (and types where it matters), with
    every (origin, direction, repeat) case worth testing and its expected
    result.
    - **Layouts to include:**
      - the diagonal of three;
      - an isolated target;
      - a dense cluster;
      - a row, a column and a grid;
      - a wide gap;
      - the screen's edges;
      - no selection, from several cursor positions;
      - at least one layout shaped like a real Gen 1 room: the main menu,
        and the open toolbar's row with room objects above it.
    - **Coverage:** together the cases cover each rule of items 3–9.
    - **Form:** written so packet 4 can transcribe them one-to-one into
      CxxTest cases. Expected results are worked by hand from the rules.
12. **Where the core's tests run.** Recommend one of:
    - CxxTest cases under `test/engines/terraglyph/`. This adds a block to
      the shared `test/module.mk`, against §7.1's default. Weigh linking only
      the core's object file against all of `libterraglyph.a`;
    - the engine's self-test;
    - both.

    Say what the choice means for H4's later move of the core to `engines/`.
13. **The per-room reachability check** (§5.8, §12.7). Design the check that
    packet 5 runs on the listing hook's output for every room of both
    titles:
    - **The graph it builds:** each target × each direction the room leaves
      to the core (the class's hook asked per room and direction), from
      presses only.
    - **The connectivity test.**
    - **Order independence:** the graph is built under two list orders (as
      given, and reversed), and the two must be the same.
    - **States checked:** each room as it starts, and again with the toolbar
      open (a UI state, not play progress), or a reason why not.
    - **No selection:** a smoke check from a grid of cursor positions. The
      guarantee itself is item 7's argument.
    - **On failure it reports:** the room, the stranded targets, and the
      presses that reach them or don't.
    - **Where it runs:** the debug channel and level.

    Say what it can't cover (states reached by play, a graph changing
    between presses), and point those at the live tests (§12.2).
14. **Decision register** (plan §10.4). Add a row, H17 onward, for each
    choice this design makes that H1–H16 don't cover. That includes at least
    items 3 (who decides the hovered target), 4, 5, 6, 8, 9 (equal points)
    and 12. Each row has alternatives, a recommendation and its evidence.
    Status is **proposed**; Jeff decides each. The plan marks each such
    choice "proposed (H*n*)" where it's stated.

### Out of scope

- **Any code**, including a reference model or test harness to be
  committed. Packet 4 writes the core and its tests by hand from §5 and
  Appendix C. EC-013 allows a local-only scratch check of the worked
  examples (Notes); nothing from it is committed or handed to packet 4.
- **The provider, the point search and the listing hook** (plan §4.5, §4.6,
  §12.7). Packet 5 builds them and runs item 13's check.
- **The input adapter beyond its repeat timing**, and the keymaps (§6.2,
  §6.4). Packet 6.
- **Room-class direction handling and the room assists** (H11, §6.8). If
  Jeff takes H11, these get their own packet. Item 13 only asks the hook
  which directions a room keeps.
- **Changing the core's contract.** If the design needs more than §4.3 gives
  it (a box, an id, the hovered target, the previous direction), it raises a
  register row and says what would change. It doesn't change the contract
  itself.
- **SCUMM/HE.** The rules must not assume TerraGlyph's 640×480 screen or its
  layouts. Screen size doesn't appear in them; if it must, that's a row.
- **Device validation and the user-experience tests** (§12.6). Packets 9–11.

## Dependencies

- The fork at `C:\dev\scummvm`, read only, through `git show` and `git grep`
  against the pinned commit. Never switch branches in the shared checkout,
  and create no fork branch.
- The plan page on `main` with WP-089's Part II (`fe2b12f`).
- The published prior art of item 2 (web sources).
- No device and no game run.

## Investigation plan

EC-013 runs these steps in order:
1. Pin and drift, including the new room classes' §6.8 rows.
2. The prior art.
3. The rules, in order: origin, filter, score and tie, nothing in the
   direction and wrap, repeats, special cases.
4. The reachability argument. It may send the work back to the filter or the
   fallback.
5. The examples, worked by hand.
6. The per-room check, and where the tests run.
7. The register rows.
8. The write-up and close.

## Output specification

All output goes into the [plan page](../reference/hotspot-magnet-plan.md),
plus the dashboard note at close:

- **§3.8, the evidence register:** the new pin, and E45 onward for each
  fork fact used. That includes the new room classes, `test/module.mk` and
  `configure.engine`, Lab's cycle, and anything item 10 reads.
- **Part II status line:** §5 designed, with the new pin.
- **§5.1–5.5, §5.7, §5.8:** the rules, the reachability argument and the
  per-room check, replacing the intent bullets. **§5.6:** made to agree with
  §4.4.
- **§6.3:** the repeat policy, agreeing with §4.3.
- **§6.8:** the new room classes' rows.
- **§10.4, the decision register:** H17 onward, proposed.
- **§12.2:** the navigation tests pointed at Appendix C and the per-room
  check.
- **§14.2:** the items this packet settles, marked.
- **§15 and the appendices:**
  - §15's rows for C and E get "below" links;
  - Appendix A gets an "Added by WP-091" table;
  - Appendix C holds the navigation examples;
  - Appendix E holds the prior art.
- **Appendix B:** `navigate()`'s declaration only if a row proposes changing
  its parameters. The change is shown as proposed, not made silently.
- **§11:** packet 3 marked done once this WP closes. **§14.3:** next steps.
  **Revision history:** a row.
- **`dashboard.json`:** the `tv-dpad` note, at close.

## Exit criteria

1. The pinned commit is recorded in §3.8 and the Part II status line, and
   every file changed since `0d5a69c7694f` is checked. Each room class added
   since then has a §6.8 row citing an E45+ row, and Wizard's Rule's says
   whether its bottles need the class hook.
2. The prior art (Android's focus search, CSS Spatial Navigation, Lab) is
   cited in Appendix E, with what each does about filtering, scoring, an
   empty direction and reachability.
3. §5 states the origin of a press in each of item 3's cases, says who
   decides each, and makes §5.5, §5.6 and §4.4 agree.
4. The candidate filter is exact, boundaries included, with y pointing down.
5. The score is an integer formula, and the tie-break is total and
   independent of list order.
6. A press with no candidate has one stated result, for a press and for a
   repeat, with the default named and whether it's configurable.
7. §5.8 holds one of item 7's three outcomes, with the graph built from
   presses only, over the directions a room leaves to the core. It shows that
   no selection is never a trap, that repeats needn't differ, and the
   worst-case press count.
8. The repeat delay and interval (in ticks, or "never") are stated, with how
   a repeat differs from a press and how a double-reported press is handled.
   §6.3 agrees with §4.3.
9. Each special case of item 9 has a rule or a worked answer.
10. §5.7 states the cost per press, the largest Gen 1 list it was checked
    against, and that the core does no per-frame work.
11. Appendix C covers every layout item 11 names, and every rule of items
    3–9 is covered by at least one case. Each case has an expected result
    worked by hand, in a form packet 4 can transcribe one-to-one.
12. Where the core's tests run is recommended, with the cost of the shared
    `test/module.mk` change weighed and what it means for H4.
13. The per-room check is designed: the graph over the room's directions,
    the connectivity test, the two-order comparison, the toolbar-open state,
    the no-selection smoke check, the failure report, and the channel and
    level. What it can't cover is stated.
14. Every "proposed (H*n*)" in the plan has a matching §10.4 row, and every
    H17+ row is cited from §5, §6.3, §6.8 or §12.2. None is marked settled.
15. `git diff --name-only main` lists only the plan page, this WP, EC-013,
    `WORK_INDEX.md` and `dashboard.json`. The fork has no new branch or
    commit from this WP.
16. The wiki's strict build passes
    (`hugo --config ewiki/hugo.toml --minify --panicOnWarning`).

## Deliverables

- **Committed:**
  - the plan page's §3.8, Part II status, §5, §6.3, §6.8, §10.4, §11, §12.2,
    §14.2, §14.3, §15, Appendices A, C and E, and the revision history;
  - this WP's status and findings links;
  - EC-013 with its outcomes;
  - the WORK_INDEX row;
  - the `dashboard.json` note.
- **Local only:** scratch notes, and the scratch check of the Notes, if one is
  made.

## Notes

- **Hand-written engine code.** The plan's §14.1 holds that all engine C++ is
  written by hand. This packet's rules and examples are design text, not
  code to paste. Packet 4 writes the core and its CxxTest cases by hand and
  records any departure.
- **A scratch check, local only.** Working the examples by hand can go wrong.
  - **What it is:** the execution may write a throwaway script in the
    session's scratchpad.
  - **What it does:** it applies the rules as written to the examples and to
    random layouts, to catch an arithmetic slip or a counterexample to item
    7's argument.
  - **What it isn't:** it is never committed and never handed to packet 4.
    The plan cites the argument, not the script.

  If Jeff would rather the examples be checked only by hand, strike this
  note before the packet runs.
- **Design, not decisions.** Where the design must choose, it recommends and
  records the choice as a proposed H-row. The plan states the recommendation
  as the design, marked "proposed (H*n*)", until Jeff decides.
- **Copyright.** Prior art is summarized and cited, not quoted beyond short
  identifiers. ScummVM's GPL source is cited by path and symbol.
