---
layout: default
title: "WP-091: Hotspot Magnet directional algorithm"
---

# WP-091: Hotspot Magnet directional algorithm — rules, reachability and test cases

**Status:** 📝 Drafted (2026-11-27).
**Phase:** 5 (polish and accessibility).
**Depends on:** WP-089 ✅ (the interface design: the core's contract in the
plan's [§4.3](../reference/hotspot-magnet-plan.md#43-interfaces) and the
target-listing hook in
[§12.7](../reference/hotspot-magnet-plan.md#127-test-hooks)), and Jeff's
decisions H1–H8 ✅. It builds on the WP-089 proposals H9–H16 as written; if
Jeff changes H11, H12 or H13 before this runs, the EC's pre-flight says what
to redo.
**Unblocks:** the implementation of the core (packet 4 of the
[plan's sequence](../reference/hotspot-magnet-plan.md#11-development-work-packets)),
which writes the C++ by hand from this packet's rules and transcribes its
test cases, and the reachability check that packet 5's provider runs.
**Companion EC:** [EC-013](../execution-checklists/EC-013-hotspot-magnet-algorithm.md).
**Pre-flight required:** **No.** A design packet: it reads the fork's source
and published references and writes only the plan page, this packet's own
records and the dashboard note. It changes nothing under
`engines/terraglyph/**`, `docs/formats/**` or `tools/**`, and classifies no
title's generation.
**Targets generation(s):** none for the core, which carries no generation;
the room layouts it tests against are Gen 1 (*Showdown*, *Phantom*).
**Estimated effort:** about one working day (5–7 hours) across the EC's
steps.

---

## Goal

Design the navigation core: the pure function that, given the targets, the
current selection, the cursor's position, a direction and whether the press
is a repeat, picks the next target. The output fixes, in the plan's §5,
rules precise enough that packet 4 can write the C++ by hand without
choosing anything: which targets count as lying in a direction, how they're
scored and tied, what happens when none does, where navigation starts with no
selection, and how held presses repeat. It also gives an argument that the
rules make **every eligible target reachable from every other, with no
subset the player can't leave** (Jeff's requirement, plan §5.8), a set of
navigation examples with expected results that become packet 4's unit tests
(the plan's Appendix C), and the design of the per-room reachability check
over both Gen 1 titles.

## Background

- **The contract this works within** (plan §4.3, WP-089). One pure function,
  `HotspotMagnet::navigate()` in Appendix B. It receives the target list
  (`Graphics::HotspotInfo`: a point, a name and a type), the current
  selection's index or none, the cursor's position, the direction (up, down,
  left, right) and a repeat flag. It returns the index to select, or none to
  stay. It keeps no state and names no engine type. It is called only in
  Magnet mode, on a directional press, after the provider has rebuilt the
  list (H8).
- **What the list guarantees** (plan §4.5, §4.6):
  - Every target's point is on screen (0–639 × 0–479) and hit-tests to that
    target.
  - Since `Room::hitTest()` returns one sprite, **no two sprite targets share
    a point**. Room-class targets supply their own points (H11), so this
    packet checks whether it can rely on distinct points or must handle
    equal ones.
  - The list is empty while a scene runs, input is blocked or the room class
    is busy.
  - Its order is the provider's, which nothing yet makes stable across
    rebuilds. Tie-breaking must not depend on it.
- **Points only, for now** (proposed H12). The core sees no boxes. Scoring
  that needs a target's extent, such as a beam test, would raise H2's
  condition (b), an id or box on the shared record. This packet decides
  whether points are enough and, if they aren't, says so as a register row
  rather than designing a box in.
- **Repeats** (plan §4.3, §6.3). The input adapter ignores device repeats and
  reports its own while a direction is held, from its own clock, at a delay
  and interval this packet sets. "Never" is allowed. The flag reaches the core
  so a repeat can behave differently, for example never wrapping.
- **Rooms that take the direction themselves** (proposed H11). A room class
  may handle a directional press itself (6.8), and then the core isn't called.
  The core's rules apply everywhere else, the menu rooms included, whose
  `ButtonRoom` buttons are targets under proposed H13.
- **The reachability requirement** (plan §5.8, Jeff, 2026-11-26): every
  eligible hotspot reachable from every other through a finite sequence of
  D-pad inputs, with no trap, and the algorithm must handle isolated,
  overlapping and unusually placed hotspots. The plan notes that scoring alone
  can strand a target, for example the middle one of three on a diagonal, and
  that a deterministic alternative (such as a reading-order cycle when nothing
  lies in the pressed direction) is acceptable if direction alone can't
  guarantee it. As a graph property it is **strong connectivity**: each
  target, under each of the four directions, has one successor (itself when
  the press stays), and the graph must be strongly connected.
- **Where the tests can run** (fork `1c02ca7ecdb5`, read while drafting).
  ScummVM's unit tests are CxxTest headers under `test/`. Engine tests live
  in `test/engines/<engine>/` and are linked against the engine's library
  when the engine is built as a static plugin (`test/module.mk`, the twine,
  ultima and wintermute blocks; `test/engines/twine/gridtest.h` is one). The
  core has no engine type, so its examples can run there as `make test` cases
  without a game. The per-room check needs the games and runs in the engine's
  self-test instead (§12.7).
- **Real layouts aren't available as data yet.** The listing hook (§12.7) is
  designed, not built, so this packet can't run the real check. It designs
  the check and its synthetic examples, and states what packet 5 runs.
  `tools/probe_art.py` decodes *Showdown*'s room placement lists (a 148-byte
  record per placed object, `PLACEMENT`), which may give approximate object
  positions offline as an early read. That is unverified, and it can't stand
  in for the check: it has no hit test, eligibility or room class.
- **Prior art to read, not yet read.** These are named here only as sources
  for the execution to read and cite. The draft has checked no detail of
  them:
  - Android's D-pad focus search (`FocusFinder`, the "beam" rules).
  - The W3C *CSS Spatial Navigation* draft.
  - Lab's "FOCUS" cycle (E17), the only ScummVM engine that moves the cursor
    between items. It is a fixed order with wrap, and the only one that
    guarantees reachability.
- **Fork drift since WP-089's pin `0d5a69c7694f`.** The tip is now
  `1c02ca7ecdb5`. It brings two merges: WP-083's *Phantom* Wizard's Rule
  room, a new `WizardsRuleRoom` class with `click(sprite)` and `tick()`
  (`wfr_rooms.cpp:284`, `:292`, registered in `room_class.cpp`), and a
  drawbridge flag fix (`drawbridge_rooms.cpp`). Neither touches the
  keymapper, events or hotspot code. The new room class needs a line in plan
  §6.8 (and E36) saying whether it's a plain click.
- **Supersession check (2026-11-27).** WORK_INDEX has no other algorithm or
  navigation packet, and plan §11 names this as packet 3. There are no open
  PRs or branches naming WP-091 or EC-013. WP-090 is Phantom's
  serving-game packet, on branch `claude/wp-090-kst-serving`. WP-088 and
  EC-011 are still held by the Play internal-testing draft, so this packet
  takes 091 and EC-013.

## Scope

### In scope

All reading is at a pinned fork commit, recorded in EC-013 Step 0; the
default is `origin/scooby-engine` at its tip on the execution date.

1. **Re-pin and drift.** Record the pinned commit in plan §3.8. List every
   file changed since `0d5a69c7694f`, record each change that alters a
   finding or citation, and add the Wizard's Rule room to §6.8 and E36.
2. **Prior art** (plan Appendix E). Read Android's focus search, the CSS
   Spatial Navigation draft and Lab's cycle. Record for each what it filters
   on, how it scores, what it does with nothing in a direction, and whether
   it claims reachability. Cite them in Appendix E, which is first filled
   here. External sources go there, not in the fork evidence register.
3. **The origin of a press** (§5.1, §5.5). Say which point a press measures
   from:
   - with a selection, that target's point;
   - with none, the cursor's position.

   And what the first press does when the cursor is already over a target:
   select that target, or move from it.
4. **The candidate filter** (§5.1). Say which targets lie "in" a direction
   from the origin: a half-plane, a cone of a stated angle, or another rule.
   State the boundary cases (on the axis, on the cone's edge) exactly, with
   the screen's y axis pointing down.
5. **Scoring and tie-breaking** (§5.2). Give the score as a formula over the
   origin and the candidate's point: alignment, distance and their weights.
   Say whether `HotspotInfo::type` (exit or object) changes anything. Give a
   tie-break that is total and independent of list order, for example by
   point (y, then x). The list index is the last resort only if points can
   be equal (item 9).
6. **Nothing in the direction, and wrap** (§5.3, §5.4). Say what a press with
   no candidate does: stay, wrap to the far side, or a deterministic
   fallback. Say whether a repeat does the same, and the recommended default.
7. **The reachability guarantee** (§5.8). Do one of these:
   - give an argument that items 3–6, applied to any set of distinct on-screen
     points, always yield a strongly connected graph;
   - add the deterministic alternative that makes it so, and argue that.

   Also state:
   - that every target can be reached from **no selection**, from any cursor
     position;
   - the shape of the worst case (the most presses between two targets) for
     the room sizes Gen 1 has.

   If no rule over points alone can guarantee it, say so, and raise H2's
   condition (b) as a register row.
8. **Repeat policy** (§6.3). Give the adapter's repeat delay and interval, or
   "never", and how a repeat differs from a press, if it does. Say why, for a
   child on a remote with no hardware repeat.
9. **Special cases** (§5.3). Give a rule or a worked answer for each:
   - overlapping and nested sprites (distinct points, close together);
   - a large object represented by one point;
   - closely spaced targets;
   - one target, and none;
   - targets in a row or a column (the menus);
   - targets at equal distance;
   - equal points from room-class targets, if item 1's reading finds them
     possible.
10. **Performance** (§5.7). State the core's cost per press in the number of
    targets, the largest list Gen 1 can give (from the self-test's room
    sprite counts or the drafts' layouts), and confirm it does no per-frame
    work.
11. **Navigation examples** (plan Appendix C). A set of named synthetic
    layouts, each a list of points (and types where it matters), with every
    (origin, direction, repeat) case worth testing and its expected result.
    Together they must cover each rule of items 3–9, the diagonal of three,
    an isolated target, a dense cluster, a row, a column, a grid, a wide gap,
    the screen's edges, no selection from several cursor positions, and at
    least one layout shaped like a real Gen 1 room (the main menu, a toolbar
    row with room objects above it). Write them in a form packet 4 can
    transcribe one-to-one into CxxTest cases. Work the expected results by
    hand from the rules.
12. **Where the core's tests run.** Recommend whether the examples run as
    CxxTest cases under `test/engines/terraglyph/` (built when TerraGlyph is a
    static plugin, `test/module.mk`), in the engine's self-test, or both, and
    what that means for H4's later move of the core to `engines/`.
13. **The per-room reachability check** (§5.8, §12.7). Design the check
    packet 5 runs on the listing hook's output for every room of both titles:
    - the graph it builds (each target × four directions, plus each target
      reached from no selection at a grid of cursor positions);
    - the connectivity test;
    - what it reports on failure (the room, the stranded targets, the
      presses that reach them or don't);
    - the debug channel and level it runs at.

    Say what it can't cover (states reached by play) and point those at the
    live tests (§12.2).
14. **Decision register** (plan §10.4). Add a row, H17 onward, for each choice
    this design makes that H1–H16 don't cover (at least items 4, 5, 6, 8 and
    12), with alternatives, a recommendation and its evidence. Status is
    **proposed**; Jeff decides each. §5 marks each such choice
    "proposed (H*n*)".

### Out of scope

- **Any code**, including the reference model or test harness that would
  later be committed. Packet 4 writes the core and its tests by hand from
  §5 and Appendix C. EC-013 allows a local-only scratch check of the worked
  examples (Notes); nothing from it is committed or handed to packet 4.
- **The provider, the point search and the listing hook** (plan §4.5, §4.6,
  §12.7). Packet 5 builds them and runs item 13's check.
- **The input adapter beyond its repeat timing**, and the keymaps (§6.2,
  §6.4). Packet 6.
- **Room-class direction handling and the room assists** (H11, §6.8). If Jeff
  takes H11, these get their own packet.
- **Changing the core's contract.** If the design needs more than §4.3 gives
  it (a box, an id, the previous direction), it raises a register row and
  says what changes. It doesn't change the contract itself.
- **SCUMM/HE.** The rules must not assume TerraGlyph's 640×480 screen or its
  layouts. Screen size is a parameter or doesn't appear.
- **Device validation and the user-experience tests** (§12.6). Packets 9–11.

## Dependencies

- The fork at `C:\dev\scummvm`, read only, through `git show` and `git grep`
  against the pinned commit. Never switch branches in the shared checkout,
  and create no fork branch.
- The plan page on `main` with WP-089's Part II (`fe2b12f`).
- The published prior art of item 2 (web sources).
- No device and no game run.

## Investigation plan

EC-013 runs:
1. pin and drift;
2. the prior art;
3. the rules in order (origin, filter, score and tie, nothing-in-direction
   and wrap, repeats, special cases);
4. the reachability argument, which may send it back to the filter or the
   fallback;
5. the examples, worked by hand;
6. the per-room check and where the tests run;
7. the register rows;
8. the write-up and close.

## Output specification

All output goes into the [plan page](../reference/hotspot-magnet-plan.md),
plus the dashboard note at close:

- **§3.8 evidence register:** the new pin, and E45 onward for each fork fact
  used (the Wizard's Rule room, `test/module.mk`, and anything item 10
  reads).
- **§5.1–5.5, §5.7, §5.8:** the rules, the reachability argument and the
  per-room check, replacing the intent bullets.
- **§6.3:** the repeat policy. **§6.8:** the Wizard's Rule room.
- **§10.4 decision register:** H17 onward, proposed.
- **§12.2:** the navigation tests pointed at Appendix C and the per-room
  check.
- **Appendix C:** the navigation examples. **Appendix E:** the prior art.
- **Appendix B:** `navigate()`'s declaration only if its parameters change
  (raised as a row, not changed silently).
- **§11:** packet 3 marked done once this WP closes; **§14.3** next steps.
- **`dashboard.json`:** the `tv-dpad` note, at close.

## Exit criteria

1. The pinned fork commit is recorded in §3.8, every file changed since
   `0d5a69c7694f` is checked, and the Wizard's Rule room is in §6.8 and E36.
2. The prior art (Android's focus search, CSS Spatial Navigation, Lab) is
   cited in Appendix E with what each does about filtering, scoring, an empty
   direction and reachability.
3. §5 states the origin of a press, with and without a selection, and the
   first press over a target.
4. The candidate filter is exact, boundaries included, with y pointing down.
5. The score is a formula, and the tie-break is total and independent of list
   order.
6. A press with no candidate has one stated result, for a press and a repeat,
   with the default named.
7. §5.8 holds an argument that the rules give a strongly connected graph for
   any set of distinct on-screen points, and that every target is reachable
   from no selection. Or it says plainly that points can't guarantee it, and
   raises H2 (b). It also states the worst-case press count.
8. The repeat delay and interval (or "never") are stated, with how a repeat
   differs from a press.
9. Each special case of item 9 has a rule or a worked answer.
10. §5.7 states the cost per press and the largest Gen 1 list it was checked
    against.
11. Appendix C covers every layout item 11 names. Each case has an expected
    result worked by hand, in a form packet 4 can transcribe one-to-one.
12. Where the core's tests run is recommended, with what it means for H4.
13. The per-room check is designed (graph, test, failure report, channel and
    level), with what it can't cover.
14. Every "proposed (H*n*)" in §5 and §6.3 has a matching §10.4 row, every
    H17+ row is cited, and none is marked settled.
15. `git diff --name-only main` lists only the plan page, this WP, EC-013,
    `WORK_INDEX.md` and `dashboard.json`. The fork has no new branch or
    commit from this WP.
16. The wiki's strict build passes
    (`hugo --config ewiki/hugo.toml --minify --panicOnWarning`).

## Deliverables

- **Committed:**
  - the plan page's §3.8, §5, §6.3, §6.8, §10.4, §11, §12.2, §14.3 and
    Appendices C and E;
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
- **A scratch check, local only.** Working the examples by hand can be wrong.
  The execution may write a throwaway script in the session's scratchpad that
  applies the rules as written to the examples and to random layouts, to
  catch an arithmetic slip or a counterexample to item 7's argument. It is
  never committed, never handed to packet 4, and the plan cites the argument,
  not the script. If Jeff would rather the examples be checked only by hand,
  strike this note before the packet runs.
- **Design, not decisions.** Where the design must choose, it recommends and
  records the choice as a proposed H-row. §5 states the recommendation as the
  design, marked "proposed (H*n*)", until Jeff decides.
- **Copyright.** Prior art is summarized and cited, not quoted beyond short
  identifiers. ScummVM's GPL source is cited by path and symbol.
