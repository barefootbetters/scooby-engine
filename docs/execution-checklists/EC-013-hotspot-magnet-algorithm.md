---
layout: default
title: "EC-013: Hotspot Magnet directional algorithm run sheet"
---

# EC-013: Hotspot Magnet directional algorithm — run sheet

**Paired WP:** [WP-091](../work-packets/WP-091-hotspot-magnet-algorithm.md)
**Purpose:** Run WP-091's design work in a fixed order. Write each section
into the [plan](../reference/hotspot-magnet-plan.md) as it's done, so a
stopped session loses nothing.
**Status:** not started.

**Evidence rule:**
- Every fork fact the design relies on cites a file and symbol at the pinned
  commit and goes in the plan's evidence register (E45 onward).
- Every external source goes in Appendix E.
- Every design choice that H1–H16 don't cover is a proposed row in the
  decision register (H17 onward).

The WP body says what each section must answer. This sheet only records
where it was written.

---

## Pre-flight

- [ ] WP-091 is 📝 Drafted on `main` and nobody else holds it. Check that no
      open PR or branch other than the merged draft's names WP-091
      (`gh pr list --search WP-091`, `git ls-remote --heads origin`), and
      that no session's worktree has it.
- [ ] Pre-flight is not required (WP-091 header). The session starts from
      WP-091 and this EC.
- [ ] Check H11, H12 and H13 in plan §10.4. If Jeff has changed any from
      WP-089's proposal, note what this packet must redo:
  - H12 to (b) puts a box or id on the record, so the filter may use extents.
  - H13 rejected removes the menu-room targets from the examples.
  - H11 rejected means no room class takes a direction, so item 13's
    per-direction hook question goes away.
- [ ] Work on a docs branch in its own worktree of this repo, not in
      `C:\dev\scooby-engine`.

## Step 0 — Pin and drift (time-box: 0:30)

- [ ] `git -C C:\dev\scummvm fetch origin`, then record the
      `origin/scooby-engine` commit in plan §3.8 and the Part II status line.
- [ ] `git -C C:\dev\scummvm diff --stat 0d5a69c7694f <pinned>`, and check
      every file listed.
- [ ] Give each room class added since `0d5a69c7694f` its own §6.8 row and
      E45+ row: Wizard's Rule (are the bottles an eligible kind, or do they
      need the class hook?), KST (pointer y and held button), and any later
      one.
- [ ] Confirm which toolbar sprites are on screen with the toolbar closed.

**Outcome:**

## Step 1 — Prior art (time-box: 0:45)

- [ ] Android's D-pad focus search: filter, score, empty direction,
      reachability.
- [ ] The CSS Spatial Navigation draft: the same four.
- [ ] Lab's FOCUS cycle (E17, `processroom.cpp:170`): the same four.
- [ ] Record all three in Appendix E.

**Outcome:**

## Step 2 — The rules (time-box: 1:45)

- [ ] The origin of a press in each case of WP item 3, with who decides each.
      Settle §5.6 against §4.4: §5.1, §5.5, §5.6.
- [ ] The candidate filter, boundaries exact, y down: §5.1.
- [ ] An integer score formula and a total, order-free tie-break: §5.2.
- [ ] Nothing in the direction, and wrap, for a press and a repeat. Name the
      default, fixed or configurable: §5.3, §5.4.
- [ ] Repeat delay and interval in ticks, or never, and double-reported
      presses. Replace the §6.3 sentence that contradicts §4.3: §6.3.
- [ ] Each special case of WP item 9, equal points included: §5.3.
- [ ] Cost per press, the largest Gen 1 list, and no per-frame work: §5.7.

**Outcome:**

## Step 3 — Reachability (time-box: 1:15)

- [ ] One of WP item 7's three outcomes, over presses only and over the
      directions a room leaves to the core: §5.8.
- [ ] A total no-selection rule, and the argument that no selection is never
      a trap.
- [ ] That repeats needn't differ, and the worst-case press count.
- [ ] If the argument fails, go back to Step 2's filter or fallback. Record
      what changed and why.

**Outcome:**

## Step 4 — Navigation examples (time-box: 1:15)

- [ ] Write each layout in WP item 11 in Appendix C, with its cases and
      expected results worked by hand.
- [ ] Map each rule of Step 2 to at least one case, and check it.
- [ ] Optional scratch check (WP Notes): apply the rules as written to the
      examples and to random layouts, in the scratchpad only. Fix any
      disagreement in the plan and record it here. Commit nothing from it.

**Outcome:**

## Step 5 — Tests and the per-room check (time-box: 0:45)

- [ ] Where the core's tests run, with the `test/module.mk` cost weighed
      (§7.1) and what it means for H4: §5.8 or §12.2.
- [ ] The per-room check, written in §5.8 with §12.2 pointed at it and at
      Appendix C. It covers:
  - the graph over the room's directions;
  - the connectivity test;
  - the two-order comparison;
  - the toolbar-open state;
  - the no-selection smoke check;
  - the failure report;
  - the channel and level;
  - what it can't cover.

**Outcome:**

## Step 6 — Register, write-up and close (time-box: 0:45)

- [ ] Add H17 onward to §10.4, each proposed with alternatives and evidence.
      Check by script that each row is cited from §5, §6.3, §6.8 or §12.2,
      and that every "proposed (H*n*)" has a row.
- [ ] Update §14.2's settled items, give §15's C and E rows their links, and
      add Appendix A's "Added by WP-091" table.
- [ ] Mark packet 3 done in §11, update §14.3, and add a revision-history
      row.
- [ ] Update the `tv-dpad` note in `dashboard.json`.
- [ ] Check WP-091's exit criteria one by one, each with its evidence, in a
      WP-091 §Close table.
- [ ] `git diff --name-only main` lists only the five allowed files.
- [ ] The strict wiki build passes.
- [ ] Set WP-091 to ✅ Done in its header and in WORK_INDEX.

**Outcome:**

---

## Definition of done

Every step's outcome is recorded, every WP-091 exit criterion is met with
its evidence, and the WORK_INDEX row is flipped in the close commit.

## Out-of-scope captures

(none yet)
