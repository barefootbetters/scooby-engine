---
layout: default
title: "WP-011: Case File #1 decompdecomp Collaboration"
---

# WP-011: Case File #1 executable analysis with decompdecomp (collaboration trial)

**Status:** 🚧 In Progress: repository access and a cooperative room received 2026-11-11; local decompdecomp environment and the capped trial are next (see [§Status and decision log](#status-and-decision-log))
**Phase:** 1 — Format Research (executable-analysis track; runs alongside [WP-001](WP-001-ghidra-session.md), does not replace it)
**Depends on:** Repository access and a room link from the host (external; both received 2026-11-11); a local Case File #1 binary matching the [WP-007 identity lock](../formats/scooby-exe.md#binary-identity-wp-007-baseline)
**Unblocks (recommended, not strict):** [WP-005](WP-005-engine-family-check.md) (function-level engine-family evidence), [MMFW container](../formats/mmfw-container.md) loader questions
**Companion EC:** — (the trial checklist is inline in [§Immediate next actions](#immediate-next-actions); author an EC only if the trial is accepted and continues past it)
**Pre-flight required:** Yes. Execution writes facts into `docs/formats/scooby-exe.md` and may feed a generation classification. Access arrived 2026-11-11; pre-flight runs before the trial writes anything into `scooby-exe.md`.
**Targets generation(s):** Gen 3 (Case File #1) primary. Gen 1 / Gen 2 only through cross-binary matching, opportunistically. Case File #2 is out of scope: WP-005 (2026-11-13) found it runs a different engine.
**Estimated effort:** Trial: half a day of setup plus one capped agent run. Anything past the trial is re-estimated at the decision point.

---

> **Setup guide:** [Setting Up decompdecomp on Windows](../reference/decompdecomp-setup.md) is the step-by-step for this WP: the installs, the spend limit, the build that checks the host's figures, joining the room, and the trial record to fill in.

## Purpose

Evaluate [decompdecomp](https://github.com/n-delic/decompdecomp) as a second, complementary way to analyze the game executables, starting with *Scooby-Doo! Case File #1*. The evaluation is a collaboration with an outside developer who has already begun decompiling that executable. The WP produces a measured answer to one question: does cooperative, AI-assisted, byte-matching decompilation give this project usable evidence faster or more cheaply than focused Ghidra work alone? If it does, the WP also produces a repeatable way to feed that evidence into the format research and, later, into an independently written ScummVM engine.

It does not replace the format-first strategy in the [Vision](../01-VISION.md#game-logic-strategy), and it does not replace [WP-001](WP-001-ghidra-session.md).

## Background

**Contact.** Simeon Armenchev ([monyarm](https://github.com/monyarm)), who goes by Mony, found this repository and got in touch. He has begun decompiling the Case File games with Ghidra, decompdecomp, `m2c`, decomp-permuter and AI coding agents, with manual executable analysis where automated progress stalls. The work lives in his private GitHub repository. This project's account was added as a collaborator on 2026-11-11 and treats the repository as read-only. To set up a machine for the work, follow [Setting Up decompdecomp on Windows](../reference/decompdecomp-setup.md).

**Where the executable analysis stood before this WP.** The [`Scooby.exe` analysis plan](../formats/scooby-exe.md) has one track: focused Ghidra work under [WP-001](WP-001-ghidra-session.md), aimed at the Gen 1 (Showdown) binary and still pending past its Rich Header step. [WP-007](WP-007-strings-and-imports.md) gives a strings and import-table baseline for all four cached binaries, Case File #1 included, with SHA-256 locks.

**What is already known about Case File #1.** It is tagged Gen 3 in the [Engine Lineage](../01-VISION.md#engine-lineage-2026-06-finding) table:

- Its PE Rich Header carries 36 C objects at Jinx's Visual C++ 6.0 compiler build 8168 and the same 17 linker 5.12 import records as Jinx; its own C++ is the VC6 Processor Pack (build 8943) ([cross-title toolchain comparison](../formats/scooby-exe.md#cross-title-toolchain-comparison-engine-generations), corrected 2026-11-14 from a "MSVC 5.0 / Linker 5.10" mislabel).
- Its strings carry the same `MMVisualCursor.cpp` source unit and the same `MMFW` resource labels as Jinx, plus ImageBuilder Software (IBS)–era `PG*`/`SM*`/`IB*` class families ([Case File #1 strings](../formats/scooby-exe.md#case-file-1-gen-3)).
- It uses `MMFW` archives, not `TGIFILE.ART` or the Gen 1 `.dat` audio archives ([cross-title verification](../formats/tgifile-art.md#cross-title-verification-2026-06)).

That evidence is at the toolchain and string level. The overview pages place Case File #1 in the same lineage on that basis, [WP-005](WP-005-engine-family-check.md) closed Phase 1 exit criterion #4 on 2026-11-13: Case File #2 runs a different engine and is excluded. This WP changes no classification. Function-level evidence, for example how many Case File #1 functions match Jinx functions, is one input WP-005 can use later.

**Supersession check (2026-11-11).** No existing WP covers cooperative or automated decompilation. WP-001 is single-operator Ghidra work on the Gen 1 binary, and WP-005 is disc and header comparison. `git log --all --grep=decomp` returns nothing. Every repo hit for "decomp" is the word "decompile" inside WP-001 / EC-001.

## Collaborator-reported starting point

Every figure in this section is **Reported** (see [§Evidence model](#evidence-model)). It was supplied by the collaborator and has not been reproduced locally.

| Item | Reported value |
|---|---|
| Functions identified in the Case File #1 executable | about 3,300 |
| Functions processed so far | about 900, in roughly a day and a half |
| Byte coverage of the processed functions | about 7 % of the executable |
| Why roughly a third of the functions is only 7 % of the bytes | The automated pass took many small functions first |
| Agents used | Agent availability was constrained; much of the run reportedly went through DeepSeek 4.1 |

The report doesn't separate "processed" into matched, near-miss and failed functions. That breakdown is the first thing to measure (see [§Immediate next actions](#immediate-next-actions)).

### Update from the collaborator (2026-11-12)

Also **Reported**: a screenshot of his decompdecomp project, sent 2026-11-12, one day after the figures above.

| Item | Reported value |
|---|---|
| Matched code | 21.7 % of the code, up from about 7 % the day before |
| Functions matched | 1,981 of 3,371 (59 %) |
| Agents running | 7, across several agent tools and models |
| Pace at that moment | 7 matches in the past hour. The app estimated about 25 more hours at that pace. |

The app's "spent" figure is left out. The collaborator reports that it prices his subscription usage as if it were API usage, so it isn't a real cost.

What this means for the WP:

- **The baseline is moving fast.** M0 and M0-R have to name a commit, and the trial result has to subtract any matches he lands while it runs.
- **The trial will start on the hard functions.** 59 % of the functions match but only 21.7 % of the code does, so the matched ones are mostly small. A trial run starts on what's left: the larger functions. Expect its match rate to be lower than his early rate. The two rates aren't comparable.

### Reply from the collaborator (2026-11-13)

Mony answered our questions by email. Everything in this subsection is **Reported**, except the point about how the room credits matches, which comes from decompdecomp's source.

| Item | Reported value |
|---|---|
| Matched code | 28.2 % |
| Functions matched | 2,078 |
| Pace | 1 to 10 matches an hour with one or two Claude instances. He says it doesn't extrapolate well: some functions fall quickly, others slowly. |
| After 50 % | The agents start working out types and names, which he expects to give them new clues |
| Set-aside functions | Functions C can't represent, which decompdecomp sets aside by itself. So far mostly MSVC assembly functions statically linked into the executable. These account for the difference between the 3,376 functions in the tool summary and the 3,371 the app counts. |

Matches by model, from the app's per-model panel (a low-resolution screenshot, so a best reading). The dollar figures are the app's API-equivalent pricing, not what subscriptions actually cost:

| Model (via) | Matches | App-priced cost per match |
|---|---|---|
| DeepSeek V4.1 Flash (opencode) | 1,014 | $0.02 |
| Claude (Claude Code) | 710 | $0.32 |
| Codex, Antigravity, Cursor (free tiers) | 45, 13, 2 | priced in tokens |
| Claude Fable, Gemini 4 Argon, Kimi K3.1 Pro, a local 9B model | 0 each | no match yet |

His notes from his own use: DeepSeek V4.1 Flash is cheap and fast, and several instances at once suit the simpler functions. Claude Opus is very good at this, especially as several instances. Claude Fable used up usage too fast for him to measure it. Free tiers are worth using until they run out. A local model on a GTX 1070 did little.

His answers, and what they change here:

- **No pinned baseline commit.** He says running decompdecomp on our own copy would be redundant: join the room. He pushes the room's progress, ours included, to his repository every day or so, one branch per game. We treat that repository as **read-only**. This replaces the 2026-11-12 point about pinning a commit. **How the trial is measured instead:** the room credits each match to the agent that made it, named `<member>.<agent>` (for example `jeff.claude-1`). This is from decompdecomp's source (`collab.py` `agent_for` and `engine/rooms.py` `apply_remote_match_named`, at commit `9e19b4d`). So the trial's result is the matches credited to our member name. A local build of one of his pushed commits is still what turns his figures into Observed ones, but it's no longer a step before joining.
- **Scope: finish the game.** He proposes finishing Case File #1 fully. After the functions, the agents move on to variable and struct names. Then add the next game, see what it can reuse, and keep going. This WP is still a capped trial; whether to go further is [open question 19](#open-questions).
- **Credit:** by username and GitHub handle, with the repository URL once it's public. He'd make it public after the decompilation is finished. Partly answers [open question 18](#open-questions).
- **Publishing docs, not code.** He's considering using the decompiled code only for research: AI reads it and writes docs, and the docs are what's published. That's the same line this WP draws in [§ScummVM integration boundaries](#scummvm-integration-boundaries).
- **Room:** the same link as before. He'll say when it changes. When he wrote, none of his agents were working, because all had run out of usage.

**For the trial:** DeepSeek Flash did most of the cheap early matching. What's left is the larger functions, where his notes put Claude Opus ahead, so expect the cost per match to rise.

### Tool versions from the collaborator (2026-11-14)

We asked Mony which tool versions he runs, so that our matches build the way his do. His answers are **Reported**; the "Ours" column is **Observed** on this project's PC.

| Tool | His (Reported) | Ours | Same? |
|---|---|---|---|
| decompdecomp | `v1.0.10-alpha.1`; he updates to each new release as it comes out | `v1.0.10-alpha.1` | Yes, today. Both sides track releases, so record the version at the time of each trial session. |
| Visual C++ 6.0 and 7.x | The copies decompdecomp supplies. He hasn't checked the service pack yet and will. | The copies decompdecomp supplies | Same source, so very likely the same build (Inferred). Whether that build matches Case File #1's Processor Pack 8943 is still [open question 7](#open-questions). |
| Ghidra | The copy decompdecomp supplies | 12.1.4, from decompdecomp, on Oracle JDK 27.0.1 | Same source (Inferred). He didn't give a version number. |
| Compiler flags | decompdecomp's detected defaults. It also tries permutations and sets different flags for single functions where needed. | The same app does the same | Yes: the flags are per function and come from the room's project, not from each member's setup. |
| Functions on 7.x | decompdecomp detects which functions were built with a different compiler from the default. About 6 or 7 so far; he'll confirm the count when he next pushes. | — | The [first look](#first-look-at-the-repository-2026-11-11) found one source file pinned to 7.1. Whether that file holds those 6 or 7 functions is to check against his next push. |
| Agents | Mostly DeepSeek and Claude, one instance of each for now. He'll add DeepSeek instances and try other models when his opencode usage resets. | Not chosen yet | — |

**What this changes:** nothing in our setup. The compilers, Ghidra and the flags all come from decompdecomp itself, so matching his tools means running the same decompdecomp release he does. Our trial record already notes the version for each session.

### Progress, libexpat and the compiler build (2026-11-14 to 11-15)

Four short emails from Mony, sent over one evening and the next morning, his time. They are **Reported**, except the rows marked **Observed**.

| Item | Value | Evidence |
|---|---|---|
| Matched code | 30.5 %, pushed to his repository | Reported |
| Functions matched | 2,086 of 3,371 | Reported |
| Near-match tooling | His next commit adds shell scripts that keep permuting near matches past decompdecomp's built-in permutation. The built-in pass is bounded: it allows only so many permutations, styles of change and flags. The scripts submit attempts through the HTTP API decompdecomp uses internally. | Reported |
| `libexpat.dll` | It is the open-source Expat XML parser. He is taking it out of the decompilation project and keeping only the DLL. | Reported |
| Expat version | `expat_1.95.3`, the version string inside this project's copy of `libexpat.dll` (SHA-256 `1B94148C…3CD4`). The DLL has no version resource. | **Observed** |
| decompdecomp | He'll move to the next release. `v1.0.10-alpha.2` came out 2026-11-15 01:42 UTC. Its notes list "bounded deep permutation with focused search", which is the built-in pass his scripts go past. This PC still runs `alpha.1`. | Release: **Observed** on GitHub |
| Compiler | He was wrong about the version. So much was detected as VC6 because the game was built with a beta build that sits between 6 and 7. He is testing which available build is closest. He'll make that one the project's default and keep exceptions for the functions that suit another build. | Reported |

**The compiler point, checked against what this project has observed.** His finding fits the Rich Header:

- **What decompdecomp supplies (Observed on this PC, 2026-11-14).** Its `6.0` compiler is VC6 **RTM, build 8168**: `CL.EXE`, `C1.DLL`, `C1XX.DLL` and `C2.DLL` all report 12.00.8168. Its `7.0` is VS2002 RTM (13.00.9466), and its `7.1` is 13.10.3077.
- **What built Case File #1 (Observed, [scooby-exe §Toolchain](../formats/scooby-exe.md#toolchain)).**
  - The game's own C++, 161 objects: the VC6 **Processor Pack**, build **8943**. It has its own product IDs (`Utc12_2_*`, 0x30/0x31), and richprint labels it "VS6 SP4 PP".
  - 126 C and 8 C++ objects: build 8797. richprint labels it "likely libs", so these are probably the static CRT (Inferred).
  - 36 C objects: build 8168. Only these were built by exactly the compiler decompdecomp calls `6.0`.
  - One object: a pre-release VS2002 compiler, `Utc13_C` build 8830.
- **"Between 6 and 7".** By build number, 8943 falls between VC6 RTM (8168) and VS2002 RTM (9466). So the "beta" he describes is most likely the Processor Pack (Inferred; to confirm with him).
- **Where to get one.** decomp.me's compiler set includes a Processor Pack build, `msvc6.5pp` ([decompme/compilers](https://github.com/decompme/compilers)). *Corrected 2026-11-15:* it isn't build 8943. It is a later Processor Pack, and no decomp.me compiler is exactly 8943. See [§decomp.me's VC6 builds](#decompmes-vc6-builds-2026-11-15).

**What this changes:**

- **The matches so far are real byte matches, made with a different compiler build.** Most of his 2,086 were scored with RTM 8168 against code that build 8943 produced. The score compares bytes, so each one is still byte-identical output. Under [§Evidence and validation requirements](#evidence-and-validation-requirements) they're recorded as matches under a near-equivalent compiler, not under the original toolchain. Once the project's default becomes a Processor Pack build, new matches can be recorded against the original build.
- **The totals will change.** The [first look](#first-look-at-the-repository-2026-11-11) counted 313 of the 3,376 functions in `libexpat.dll`. Dropping them changes the denominator, so a percentage from before the change can't be compared with one from after it. Quote both figures with their date.
- **Research target 4 narrows.** The XML parser is stock Expat 1.95.3, so there's no parser to reverse engineer. What's left is the game's own code: what calls Expat, and the element handlers that read `launch.xml` and the XML inside the `MMFW` archives. ScummVM already has an XML parser of its own (`Common::XMLParser`), so the engine reads those files without Expat (Inferred; to check when the files' schema is known).
- **Progress slowed and moved to bigger functions.** In about a day the count went from 2,078 to 2,086, eight functions, while matched code went from 28.2 % to 30.5 %. That's what [§Update from the collaborator](#update-from-the-collaborator-2026-11-12) predicted: the remaining functions are the large ones.

### Reply on the compiler build (2026-11-15)

We sent Mony the Rich Header's per-object builds and pointed him to decomp.me's Processor Pack compiler. His reply is **Reported**.

| Item | Reported value |
|---|---|
| Build 8943 | He couldn't find it when he searched, so he assumed it was a rare beta. He hadn't thought of decomp.me. |
| Compilers | He'll give the agents decomp.me's compilers at the builds the Rich Header names. He expects that to raise the match rate for quite a few functions. |
| Matched code | 28.4 %, with `libexpat.dll` removed |
| Functions matched | 1,765 of 2,760, with 995 left |
| Last agent attempt | One attempt matched 40 functions at once, just before his usage ran out |
| Status | Out of all AI usage, and in the middle of a lot of work on the decompilation repository. He'll say when it's done. |
| Next games | He'll start decompiling the games this project is working on now "soon". Those are the Gen 1 titles: Showdown and Phantom (WP-020 to WP-036). |

**What this changes:**

- **The "between 6 and 7" build is the Processor Pack.** He took the Rich Header reading. A beta compiler was his guess, made because the build couldn't be found. Case File #1's C++ was built with a released compiler, and decomp.me has it. [Open question 7](#open-questions) now hangs on one measurement: how many functions match once the project uses that build.
- **The new totals aren't comparable with the old ones.** Before: 2,086 of 3,371 and 30.5 %. After: 1,765 of 2,760 and 28.4 %. The total dropped by 611 functions, but the [first look](#first-look-at-the-repository-2026-11-11) counted only 313 in `libexpat.dll`. So something more than Expat also left the count, unless his tool counts differently from that summary. Ask him what else was removed. Matched code fell from 30.5 % to 28.4 %, which suggests the removed code was matched at a higher rate than the rest (Inferred).
- **A Gen 1 project needs the same executables as ours.** This project's Showdown exe is the 2001 `Gold v1.19` patch build ([§Gen 1 discs are 2001 reissues](../formats/scooby-exe.md#gen-1-discs-are-2001-reissues-2026-11-14)). Before he starts, compare his Showdown and Phantom executables with the [WP-007 locks](../formats/scooby-exe.md#binary-identity-wp-007-baseline): Showdown `13284543…7478` (487,473 bytes) and Phantom `619EA687…07ED` (483,377 bytes). If his are another build, function addresses won't line up with this project's notes. That answers [open question 20](#open-questions) in practice: a Showdown project comes now, not after Case File #1.

### decomp.me's VC6 builds (2026-11-15)

We downloaded three of decomp.me's VC6 archives from the release they're served from (`OmniBlade/decomp.me`, release `msvcwin9x`) into scratch space outside this checkout, and read the file versions. The table is **Observed**:

| decomp.me compiler | `CL.EXE` | `C1.DLL` | `C1XX.DLL` | `C2.DLL` (code generator) |
|---|---|---|---|---|
| `msvc6.0` (as installed by decompdecomp) | 12.00.8168 | 12.00.8168 | 12.00.8168 | 12.00.8168 |
| `msvc6.4` (SP4) | 12.00.8804 | 12.00.8867 | 12.00.8867 | 12.00.8799 |
| `msvc6.5` (SP5) | 12.00.8804 | 12.00.8867 | 12.00.8964 | **12.00.8966** |
| `msvc6.5pp` (SP5 + Processor Pack) | 12.00.8804 | 12.00.8867 | 12.00.8964 | **13.00.9044** |

What other decompilation projects have published, and what follows from it:

- **Gen 1 has an exact compiler.** The NOLF2 decompilation (`nolffan/nolf2src`, `progress/COMPILERS.md`) builds Rich Header C++ 8966 objects with VC6 SP5 (`c2.dll` 12.00.8966). Its rebuilt Rich Headers match retail object for object, and thousands of functions match byte for byte. Showdown and Phantom are C++ 8966 ([scooby-exe §Toolchain](../formats/scooby-exe.md#toolchain)), so decomp.me's `msvc6.5` is their compiler (Inferred from that project's proof plus the table above). decompdecomp's own `6.0` is RTM 8168, so a Gen 1 project adds `msvc6.5` through decompdecomp's "your own copy" compiler option.
- **The Processor Pack's code generator is a pre-release VC7 one.** `msvc6.5pp` keeps SP5's front end but swaps in a 13.00 `C2.DLL`, build 9044, older than VS2002's 13.00.9466. So Mony's first reading, a build "between 6 and 7", was close to right. Other projects (`caixax/DeCoF` `docs/toolchains.md`, `nolffan/tools` `richhdr.py`) record that this pack stamps Rich Header entries `Utc12_2_*` build **9044**.
- **Case File #1's Processor Pack is an earlier one.** Its entries are `Utc12_2_CPP` build **8943**, which richprint labels "VS6 SP4 PP": the first Processor Pack, for SP4. decomp.me doesn't ship it. `msvc6.5pp` is the nearest decomp.me has, the same product line one build later. How much 8943 and 9044 differ in output is not known. Functions that fail only under 9044 point to that difference.
- **A quick look at the code generator (Observed).** One documented difference is the x87 compare: the 9044 code generator writes `fnstsw ax; test ah,44h` or `test ah,5`, and plain VC6 writes `test ah,40h` or `test ah,1` (`maci0/rebrew` `toolchain_detect.py`). A whole-file scan of the exes counted Showdown 0 and 63, Phantom 0 and 57, Jinx 0 and 35, and Case File #1 **2 and 29** (Processor Pack style first, plain second). Gen 1 and Jinx are plain throughout. Case File #1 is mixed. The scan doesn't separate the game's own code from the statically linked CRT and the build-8168 C objects. So it can't yet say whether 8943 writes the 9044 idiom; the function map will.

### Library matching, the Processor Pack default and outmatch (2026-11-15)

Four emails from Mony that afternoon and evening, after our reply with the compiler builds and the Gen 1 hashes. Everything below is **Reported**, except the outmatch rows marked **Observed**.

| Item | Value |
|---|---|
| Why the total fell by 611 | Dropping Expat, plus a new script that matches statically linked library functions directly against the `.lib` files and sets them aside. That answers the question in [§Reply on the compiler build](#reply-on-the-compiler-build-2026-11-15). |
| Library matching so far | Run against VC6 RTM's libraries only. Running it on the libraries of the other compiler builds the game used should set aside a few more. |
| Compiler nondeterminism | He has added known ways to steer MSVC's output, from other projects' findings on what changes what, to his scripts. |
| `msvc6.5pp` | Added as a custom compiler and made the project default. All functions are going through it again. **84 new matches** before a quarter of the list was done. |
| Polish mode | While his usage resets, the decompdecomp agents run in polish mode, adding types and names. |
| Repository | Everything so far is committed and pushed. A progress report came with the email; its figures aren't recorded here yet. Next commit expected 2026-11-16, after his usage resets: the interrupted subagents, the other compiler builds and their libraries. |
| Gen 1 hashes | He'll compare his Showdown and Phantom executables with ours when he gets to them. |
| outmatch | He published his tools as [monyarm/outmatch](https://github.com/monyarm/outmatch) and shared them with the decompdecomp developers. |

**outmatch, read from its README (Observed 2026-11-15).** A public repository, created 2026-11-15, in Python with a shell entry point (`outmatch.sh`). It had no license file on 2026-11-15; since commit `89f1c45` it is MIT-licensed, with a NOTICE for the reference notes it bundles from other projects. It runs beside a decompdecomp project while the app is open. It submits every candidate through the app's own `POST /api/try`, so the app compiles, scores and commits each match the same way its **Try** button does. Its commands:

- `loop`: works the whole near-miss queue unattended and keeps a ledger.
- `msvc`, `levers`, `pragma`: catalogues of source changes known to steer MSVC's output.
- `flags`: per-file compiler-flag sweeps.
- `compiler`: tries each function under every installed compiler build.
- `libmatch`: the library matching above. It compares functions with the VC6 libraries' own objects and records the matches as set aside.

Its README paths are Unix-style (`~/Decomp`, `/tmp/outmatch`), so running it on this project's Windows PC is untested.

**What this changes:**

- **The first measurement for [open question 7](#open-questions).** Moving to the Processor Pack added 84 matches early in the pass. Many functions that RTM couldn't match do match under 9044. Whether any still need 8943 is open until the pass ends.
- **The denominator is now game code.** With Expat and identified library code set aside, the remaining count is closer to the game's own functions. That's the set the [research targets](#research-targets) care about. Percentages before 2026-11-15 still aren't comparable with later ones.
- **Better tooling for the trial's large functions.** The trial will start on what's left after outmatch and the Processor Pack pass. That will be the hardest functions, so expect a lower match rate.

### Compiler and library sweeps, and an invitation to join (2026-11-16)

Mony's reply to our notes on the library builds. **Reported**:

| Item | Value |
|---|---|
| Library and compiler sweeps | He ran most of the compilers and libraries through outmatch. The VS2002 pre-release compiler was still downloading. No additional matches. |
| Processor Pack rerun | About 80 more matches after his last email, so about 164 in all. His progress report showed 160 in its last hour. |
| Unit splits | About a dozen more matches from splitting files into single functions and trying different compilers on each one |
| `.lib` files | Confirmed: they only come from the actual service packs |
| outmatch on Windows | Not needed, he says. outmatch finishes what decompdecomp couldn't, and he isn't sure posting to `/api/try` works correctly from a member who has joined a room. |
| What would help | Joining the room with a strong model such as Claude Opus. With the libraries set aside and the right compiler in place, he expects agents to have a much easier time now. |
| His agents now | Claude running outmatch on the set-aside assembly-only functions, mostly small thunks, and on broad attempts that try to match several things at once |
| His plan | A few more things on Case File #1. Then one DeepSeek agent on polishing and one on matching, while he starts decompiling Showdown and Phantom. He expects those to reuse some of what Case File #1 already has. |

**What this changes:**

- **The compiler question is mostly settled.** The Processor Pack added about 164 matches. Other builds and their libraries added none. A dozen more came from per-function compiler choices. Whether the 8943 pack itself would add more is still open, but there isn't much left for it to explain ([open question 7](#open-questions)).
- **The trial is ready to run.** The host has asked for exactly what the trial is: joining the room with Opus-class agents. The setup is done except the agent provider and its cap ([§Immediate next actions](#immediate-next-actions)). We join through the app, not through outmatch, because his doubt about `/api/try` from a joined member applies to us.
- **Expect less reuse from Case File #1 into Gen 1 than he does.** This project's string evidence shows the framework was rewritten between Gen 1 and Gen 2: Showdown and Case File #1 share no engine-surface strings ([scooby-exe §Case File #1](../formats/scooby-exe.md#case-file-1-gen-3)). Reuse into Showdown will most likely be the shared CRT and runtime code. The engine code that carries over sits between Jinx and Case File #1, which is why the [cross-game plan](#cross-game-reuse-strategy) puts Jinx next (Inferred). The Showdown project's value to this project is the game logic, which the engine work in WP-020 onward reads today from the data.

**A standing instruction for the agents (2026-11-16, Reported).** Mony recommends putting one instruction in decompdecomp's agent settings: read the `references` folder of outmatch's `msvc-matching` skill, by full path. Pointing at the skill itself doesn't work, because decompdecomp doesn't load skills well. He says it greatly improves the match rate. The folder holds MSVC matching notes gathered from other decompilation projects. One file is about 335 KB (Observed), so watch what reading it costs per attempt during the capped trial. The steps are in [setup §Give the agents Mony's matching notes](../reference/decompdecomp-setup.md#give-the-agents-monys-matching-notes). The setup page also now covers the `msvc6.5pp` default, which which every member needs installed too (Mony confirmed it 2026-11-16).

### Progress across the games, twin matching and reuse counts (2026-11-18)

Three emails from Mony. **Reported**:

| Item | Value |
|---|---|
| Case File #1 | **37.5 %** matched. Almost every function now has some kind of decomp, even where it doesn't match yet. |
| Real function count | Most functions in the games are thunks and tiny MSVC-generated assembly. Accounting for those and the CRT, the real count is about **1,600**, the same deflation libexpat and the `.lib` set-asides produced for Case File #1. |
| Phantom and Showdown started | Both Gen 1 games are under way, to appear as branches of his decomp repo. DeepSeek agents on Showdown, Claude on Case File #1. |
| Phantom | At **38 %**, pending the batch twin-matching he hasn't run there yet. |
| Twin matching | He's matching twins between the games, and wrote an outmatch command that batch-matches twins faster than decompdecomp does, and attempts a twin even when the compiler differs. |
| Measured reuse | The two Gen 1 games (Showdown, Phantom) share **280 completely identical functions**. Between those and Case File #1, **170 are completely identical**. His caveat: identical means byte-for-byte, so a single change drops a function from the count — these are floors on shared code, not the whole of it. |
| Two questions for Jeff | Whether there are other games he should try beyond Case File #1 and the first two, and whether the decomps have been useful. |

**What this changes:**

- **170 identical functions Gen 1 → Gen 3 is real function-level reuse, but doesn't overturn the rewrite reading.** This project's string evidence shows Showdown and Case File #1 share no engine-surface strings ([scooby-exe §Case File #1](../formats/scooby-exe.md#case-file-1-gen-3)), and the [cross-game plan](#cross-game-reuse-strategy) expected Gen 1 reuse to be mostly CRT and runtime. 170 byte-identical functions is consistent with that: identical matches are exactly where CRT and small runtime helpers land, since those don't change between titles. It does not show the engine carried over — modified engine code wouldn't be byte-identical and so wouldn't be in this count. The number to watch for the engine question is near-matches, not identical ones (Inferred).
- **The 1,600 figure scopes a Showdown project.** Once thunks and CRT are set aside, each Gen 1 game is about 1,600 real functions, not the raw count. A Showdown decompdecomp project ([cross-game plan step 4](#cross-game-reuse-strategy)) is that much smaller than the raw binary suggests.
- **Mony's two questions are Jeff's to answer** (which games, and whether the output is useful). Recorded here; not answered in the repo.

Room links and his email address are not recorded.

### Jinx added, overnight Showdown progress (2026-11-19)

One email from Mony, cross-checked against his pushed branches (fetched read-only into the local clone at `C:\dev\scooby-tlr-decomp`, 2026-11-19).

| Item | Value | Evidence |
|---|---|---|
| "I added sphinx" | He added **Jinx at the Sphinx** — the Gen 2 game this project calls Jinx — as a new decomp target, not an AI agent. Branch `jinx-at-the-sphinx`, first commit 2026-11-19, 190 `.cpp` files. | **Observed** (fetched) |
| Showdown overnight | Agents advanced Showdown overnight. Branch `showdown-at-ghost-town`, first commit 2026-11-18, 419 `.cpp` files, 3,626 functions in `config/scooby/functions.json`. | **Observed** (fetched) |
| Showdown exe identity | His Showdown binary is **byte-identical to this project's**: config `sha1 eb8b5487…9a04` equals our `tools/exes/showdown/Scooby.exe`, whose SHA-256 is the [WP-007 lock](../formats/scooby-exe.md#binary-identity-wp-007-baseline) `1328454334…7478` (487,473 bytes). So every function address in his decomp maps 1:1 onto this project's Ghidra and runtime notes. | **Observed** (hashed locally 2026-11-19) |
| Phantom | Branch `phantom-of-the-knight`, 399 `.cpp` files. | **Observed** (fetched) |
| Case File #1 | Branch `case-file-1` advanced to `0a9268a7`. | **Observed** (fetched) |
| Match rates | Not measured here. Commit and file counts are not match rates; the attached progress report's figures aren't recorded yet, and turning them into Observed numbers needs a local build / objdiff ([setup §6](../reference/decompdecomp-setup.md#6-check-a-build-of-monys-repository)). | Reported (report), not yet measured |
| Usage | Out of both Claude and opencode usage; little further progress for a few days, until they reset. | Reported |
| Request | Read the matched functions for usable information, especially the minigame logic and file formats. | Reported |

What this changes:

- **He's started the Gen 2 game this WP named as the highest-value next target.** [§Cross-game reuse strategy](#cross-game-reuse-strategy) step 2 put Jinx next, because Jinx → Case File #1 is the strongest inheritance evidence, so the `jinx-at-the-sphinx` branch puts that function-level test in progress. It answers his own 2026-11-18 "which games" question by action.
- **All four in-scope engine binaries now have a decomp branch** of `monyarm/scooby-tlr-decomp` (Showdown, Phantom, Jinx, Case File #1). Case File #2/#3 are correctly absent (different engine, [WP-005](WP-005-engine-family-check.md)).
- **The function source is now local and readable** — the clone was stale at the 2026-11-11 first commit until this fetch. The `showdown-at-ghost-town` branch is the one for his minigame-logic / formats request. Findings are **Reported** until reproduced locally; only Observed-or-better goes into `scooby-exe.md` ([§Evidence and validation requirements](#evidence-and-validation-requirements)).
- **For Showdown, most of what he's asking Claude to find is already derived here, from the data and from runtime tracing.** The Gen 1 file formats are solved from the data alone — `TGIFILE.ART` ([WP-002](WP-002-tgifile-art-decoder.md)) and the audio `.dat` archives ([WP-004](WP-004-audio-archive-decode.md)) — and Showdown's minigame and set-piece logic is mapped room by room in Phase 3 (the artifact jigsaw [WP-037](WP-037-artifact.md), the bank-vault clock [WP-039](WP-039-bank.md), the stage levers [WP-043](WP-043-stage.md), and the rest). So the decomp's value on Showdown is corroboration and the few Ghidra unknowns still open (room-block word `0x10` and placement field `+0x88`, from [WP-001](WP-001-ghidra-session.md#result-2026-11-13)), not new formats.
- **First read of the decomp (2026-11-19).** Source is `src/auto/text_<addr>.cpp`, one `func_<addr>` per Ghidra-found function, with structs reconstructed per translation unit as offset-accurate placeholders (`fNN`/`unkNN`, `pad` runs); some runtime types recovered (`CString`, class hierarchies). Corroborations: the per-tick sprite-tree walk (`0x431130`) is a recursive method on a node class (child/sibling pointers at `f38`/`f3c`), matching [WP-017](WP-017-sprite-animation.md); the clickable depth builder (`0x40AD50`) reads an `object.ini` string and `atoi`s it, returning the caller's default when absent, matching the `priority=` reading in [WP-044](WP-044-jail.md). **The two gaps stay open, and the reason is now pinned (traced 2026-11-19).** The runtime *consumer* side is fully decompiled and matches our model — the sprite-node class (`0x45F3DC`: depth-ordered sibling insert `0x430F40`, detach `0x430EE0`, per-tick walk `0x431130`; parent/child/sibling at `f34`/`f3c`/`f38`, depth at `f20`). The *producer* side is not: the `TGIFILE.ART` scene-block parser — the one function that reads the block-header word at `0x10` and each 148-byte placement record (including the `+0x88` constant) and constructs those nodes — has no clean decomp on this branch. The node constructor and `0x430F40` have **no caller anywhere** in `src/`; no scene-id `0x9000` constant, 148-byte (`0x94`) stride, placement `+0x84`/`+0x86` position read, or block-header `0xC0`/`0xC4` pair appears. So the decomp cannot close either gap today — both need that loader decompiled first, which is the concrete, high-value function for Mony's agents to target. **Name caution:** this branch's polish-mode names are unreliable — Gen-2/3 `SM*` class names (`SMAntRoundupScene`, `SMAnimationMolecule`) are stamped on this Gen-1 binary, which has no such minigame, so names here are read as guesses, per [§Evidence model](#evidence-model).
- **His 2026-11-18 questions (which games, whether the output is useful) remain Jeff's.** A reply is drafted 2026-11-19; the answers are recorded here once Jeff sends them.

Room links and his email address are not recorded.

### Reply: name leak fixed, scope questions for Jeff (2026-11-19)

Mony's answer to our 2026-11-19 reply. **Reported.**

| Item | Value |
|---|---|
| Name leak | He confirms the cause of the `SM*`-on-Showdown names: a bug that leaked names across games while twin-matching. He fixed it, but some names got through before the fix. |
| `TGIFILE.ART` fields | When his usage resets, he'll point an agent at the matched and partially-matched functions to try to work out the room-block word at `0x10` and the placement field at `+0x88`. He takes up the one ask. |
| Questions for Jeff | (1) Any plans to handle Case File #2 and #3 once the initial titles are done? (2) Is there any other game on this engine beyond the ones known — he cites "the powerpuff game" and doubts it was the only one. |

What this changes:

- **The name drift is a confirmed, fixed bug, not inference.** Our 2026-11-19 read flagged `SM*` Gen-2/3 class names stamped on the Gen-1 Showdown binary and treated them as guesses ([§Jinx added, overnight Showdown progress](#jinx-added-overnight-showdown-progress-2026-11-19)). Mony confirms the twin-matcher was bleeding names across games and has fixed it. So names on commits before the fix stay **guesses**; names on branches pushed after it should be cleaner, but this project still only takes a name as Observed when reproduced here ([§Evidence model](#evidence-model)).
- **The one ask is accepted.** He'll aim an agent at the scene-block loader's matched/partial functions once usage resets. Both Ghidra gaps stay open until that loader is decompiled and the fields are read ([§Jinx added, overnight Showdown progress](#jinx-added-overnight-showdown-progress-2026-11-19)).
- **His two questions are Jeff's; the documented position the reply draws on:**
  - **Case File #2 and #3 are each a different engine from ours, and from each other.** Case File #2 runs the Trinket / OM++ launcher framework (`R*` classes, `.bul`/`.inx`, LZO), with no code continuity to the TerraGlyph/IBS lineage ([WP-005](WP-005-engine-family-check.md), 2026-11-13; [VISION §Case File #2](../01-VISION.md)). Case File #3 is Macromedia Director (TLC/Broderbund), confirmed out of scope 2026-06-03 ([VISION](../01-VISION.md)). Neither feeds this project's engine, so there's no plan to decomp them here; each would be its own project on its own engine.
  - **The Powerpuff demo is on *Case File #2's* engine, not ours.** The `GroovyGoodies\PPG2Demo\` demo on the Case File #2 disc uses that same Trinket/OM++ framework (`trinket.dll`, 17 shared `R*` classes, same LZO build) — the engine this project *excluded*, not the TerraGlyph engine. So it's "another game on the Case File #2 engine," and a worth-correcting mix-up in his question.
  - **The confirmed TerraGlyph-engine set is the Scooby titles:** Showdown (2000), Phantom (2001), Jinx at the Sphinx (2001) — all TerraGlyph Interactive Studios — plus Activity Challenge (2001, Jinx's Gen-2 engine, [WP-013](WP-013-activity-challenge-engine-check.md)) and Case File #1 (2002, IBS inheriting the engine via embedded `MMFW` objects). That is the five in-scope binaries.
  - **One non-Scooby title found and CONFIRMED on the engine (2026-11-19).** TerraGlyph Interactive Studios shipped about 11 titles 1995–2001 before closing in 2001 (MobyGames, Wikipedia). The one non-Scooby title that shares this PC engine is **Disney's 102 Dalmatians: Activity Center (2000)** — TerraGlyph-developed, Disney-published, Windows + Mac, a point-and-click rendered children's game. A disc image was downloaded from the Internet Archive ([`Disneys102DalmatiansActivityCentreDisneyClassicsCover`](https://archive.org/details/Disneys102DalmatiansActivityCentreDisneyClassicsCover), file `102_Dalmatians.img`, SHA-1 `a84fe50e72ed19cb2ac180401091d4f17ab42370`, 427,805,280 bytes, verified against the Archive's record) and a raw scan of the image is **Observed**: `TGIFILE.ART` is present (the Gen 1 TerraGlyph art container from [WP-002](WP-002-tgifile-art-decoder.md)), with game executables `DALMATIANS.EXE`, `CKTIMEPLAYER.EXE`, `CKSOUND.EXE`. No `trinket`/`RScenePort`/`Crystal`/`EIDOS` strings (not the Case File #2 framework) and no `Macromedia` (not Director). **Verdict: TerraGlyph engine, Gen 1 family — the first confirmed non-Scooby binary on the engine.** It is a hybrid Mac/PC disc (a Roxio Toast HFS partition alongside the PC ISO9660). Confirmation is at the filename/string level; byte-format identity (decoding a `.ART` with the WP-002 decoder) is the deeper check still open, and a full engine-family check (exe hash, import table, RTTI) would be its own WP. The image lives at `C:\pcloud\scooby-engine\102 Dalmatians Activity Center\102_Dalmatians.img` (non-git). **This also makes it a candidate decomp target for Mony**, and a new Gen-1 data point for the lineage work. The studio's console titles (Scooby-Doo! Classic Creep Capers, N64; Tiny Toon and Blue's Clues games, PlayStation) run other engines; its 1995–96 CD-ROM titles predate Gen 1 by five-plus years and are at most an ancestor of the framework (unverified). A separate disc, *102 Dalmatians: Puppies to the Rescue* (archive.org `flt-102d`), is **not** this engine: its image carries Crystal Dynamics / Eidos / Prolific branding and `.RPL` movies, no `TGIFILE.ART` — a different developer's game, ruled out. Secondary wikis disagree on Showdown's developer (Kotaku: TLC; SPONG: Mattel), but the binary's `MMFW`/`TGIFILE.ART` engine and shared RTTI settle the TerraGlyph lineage regardless.
- Recorded here; not answered in the repo. A reply is drafted 2026-11-19, with the catalog finding folded in.

Room links and his email address are not recorded.

### Reply: targets, naming and the Director path (2026-11-20)

Mony's answer to our 2026-11-19 reply. No new question for Jeff this time — he takes the catalog finding, proposes next steps and raises a naming point. **Reported.**

| Item | Value |
|---|---|
| Activity Center and Activity Challenge | Good decomp targets once the current engine is done; failing that, at least document them as sharing the engine so someone else can add support. |
| Older catalog titles | Worth a quick once-over for shared lineage; he'll check some of the console / CD-ROM titles himself for common ground. |
| Case File #3 (Director) | Already partially implemented and supported in ScummVM, so if the other Scooby games are ever done after these, it'd be the good next target — and only then Case File #2. |
| Engine naming | Since the Gen 1 and Gen 2 engines both have non-Scooby games, he suggests a more generic engine name — "Maybe TerraGlyph?" |
| `TGIFILE.ART` fields | Reconfirms he'll point agents at the matched/partial functions once usage resets: Claude on Tuesday, opencode two days after. |

What this changes:

- **The naming suggestion is already this project's convention.** This project calls it the **TerraGlyph engine** throughout — the [VISION lineage](../01-VISION.md#engine-lineage-2026-06-finding) ("the three TerraGlyph titles", the engine "continued through IBS"), this WP, and the user-level repo map. Only the GitHub repo keeps the historical name `scooby-engine`. So Mony's instinct matches the name already in use, and the 102 Dalmatians confirmation ([§Reply: name leak fixed](#reply-name-leak-fixed-scope-questions-for-jeff-2026-11-19)) is exactly why a Scooby-specific name was never right. Nothing to change; independent corroboration of the existing choice.
- **The Director-before-Trinket sequencing is sound and matches our out-of-scope calls.** Case File #3 is Macromedia Director, and ScummVM's Director engine already gives it partial support — so if it were ever pursued it would ride that existing engine, not a TerraGlyph fork. Case File #2 (Trinket / OM++) has no ScummVM support and would be a ground-up engine, so it correctly comes last. Both stay **out of scope for this project** ([WP-005](WP-005-engine-family-check.md); [VISION](../01-VISION.md)); recorded as a forward note for a possible separate project, not a plan here.
  > **Superseded 2026-11-21:** Case File #3 is **Macromedia Flash, not Director** — Mony corrected it and we verified it locally. ScummVM has no Flash engine, so the "#3 could ride ScummVM's Director support, ahead of #2" sequencing no longer holds; #3 is simply out of scope for good (Ruffle plays it). See [§Correction: Case File #3 is Macromedia Flash](#correction-case-file-3-is-macromedia-flash-not-director-2026-11-21).
- **He's volunteering the catalog once-over this project marked unverified.** The 1995–96 TerraGlyph CD-ROM titles (Hansel & Gretel, Rumpelstiltskin, Kidsongs, Tiny Toon: Buster and the Beanstalk) were logged as "at most an ancestor of the framework (unverified)" ([§Reply: name leak fixed](#reply-name-leak-fixed-scope-questions-for-jeff-2026-11-19)), and the console titles as different engines. Mony checking some himself could turn those into Observed on his side; this project takes any such finding as **Reported** until reproduced here.
- **"Document them as sharing the engine" is already done.** WP-011 now records **Activity Center** as confirmed Gen 1 and **Activity Challenge** as the Gen-2 engine ([WP-013](WP-013-activity-challenge-engine-check.md)), so his minimum bar is met; the decomp-target idea is noted for after the current set.
- **The one ask stays in progress, now with a timeline.** He'll aim agents at the scene-block loader's matched/partial functions once usage resets (Claude Tuesday, opencode +2 days). Both Ghidra gaps — room-block word `0x10` and placement field `+0x88` — stay open until that loader is decompiled ([§Jinx added, overnight Showdown progress](#jinx-added-overnight-showdown-progress-2026-11-19)).

Room links and his email address are not recorded.

### Catalog once-over: two more TGIFILE.ART titles and a DOS "TGI" signature (2026-11-20)

Mony took up the catalog once-over he'd offered and went through TerraGlyph's list (MobyGames was down, so via PCGamingWiki and [LaunchBox gamesdb, developer 487](https://gamesdb.launchbox-app.com/developers/games/487-terraglyph-interactive-studios)). All **Reported** — his quick disc / executable look, not reproduced here.

| Title | Mony's finding |
|---|---|
| **Clue Jr.: SpyGlass Mysteries** | `TGIFILE.ART` on the disc — "definitely one of ours." On GOG. Uses DirectX, unlike the later `TGIFILE.ART` titles. |
| **The Little Mermaid II: Return to the Sea** | `TGIFILE.ART` — ours. |
| Hansel & Gretel and the Enchanted Castle (DOS) | No `TGIFILE.ART`. Uses WinG (Microsoft's WinG graphics API — not an engine name; his correction) and carries `TGI_ENGINE` / `TGI_QA` strings. |
| Tiny Toon Adventures: Buster and the Beanstalk (DOS) | Same: WinG + `TGI_ENGINE` / `TGI_QA`. |
| The 1995–96 DOS pair, overall | Likely a *separate, earlier* TerraGlyph engine carrying the studio's "TGI" signature — probably not the `TGIFILE.ART` ancestor — but the two share an engine with each other. |
| Tiny Toon Adventures: The Great Beanstalk (PS1) | Little debug info; file structure suggests bespoke; plays differently on different hardware. Maybe worth a deeper look. |
| Scooby-Doo! Classic Creep Capers | 3D; not examined — unlikely to share a 2D point-and-click engine. |
| Toonenstein, Blue's Big Musical, Kidsongs: Musical Mystery, Rumpelstiltskin's Labyrinth of the Lost | Not our engine (his read). |
| Canceled titles | TerraGlyph has a few; if versions surface, maybe worth a look (ScummVM prototype policy unknown). |
| DOS / Mac variants | Several titles have DOS and Mac releases; supporting them would mean checking version differences and reading both their files. |

What this changes:

- **Two more non-Scooby `TGIFILE.ART` titles, bringing the set to three (Reported).** Activity Center (Observed here, [2026-11-19](#reply-name-leak-fixed-scope-questions-for-jeff-2026-11-19)) + **Clue Jr.: SpyGlass Mysteries** + **The Little Mermaid II: Return to the Sea**. The two new ones are **Reported** until reproduced locally the way Activity Center was (download, scan for `TGIFILE.ART`). Clue Jr. is on GOG, so it's the readily obtainable one for a local check; Little Mermaid II's source is still to find.
- **The DOS titles are a sibling "TGI" engine, not the ancestor the 2026-11-19 note guessed.** That note put the 1995–96 CD-ROM titles as "at most an ancestor of the framework (unverified)". Mony's read refines it: Hansel & Gretel and Buster and the Beanstalk run WinG and carry `TGI_ENGINE` / `TGI_QA` — the studio's signature prefix — but are more likely a *different* TerraGlyph engine than a direct ancestor of `TGIFILE.ART`; they do share an engine with each other. So it's a candidate *second* TerraGlyph engine family (DOS / WinG), separate from the Gen 1–3 `TGIFILE.ART` / `MMFW` lineage this project targets. Out of scope, but "ancestor" becomes "sibling engine."
- **"TGI" is the studio's cross-engine signature — which is the case for the TerraGlyph naming call.** `TGIFILE.ART`, `TGI_ENGINE` and `TGI_QA` all share "TGI" = TerraGlyph Interactive, and the prefix spans at least two distinct engines (DOS / WinG and the Windows `TGIFILE.ART` line). Naming this project's engine generically after the studio (TerraGlyph) rather than after a file signature or Scooby sits at the right altitude — the [2026-11-20 naming point](#reply-targets-naming-and-the-director-path-2026-11-20), now with evidence.
- **Scope is unchanged.** Still five in-scope binaries. Clue Jr. and Little Mermaid II are candidate decomp / support targets and Gen-1 lineage data, not current scope; a full engine-family check on either would be its own WP (as Activity Center would). The PS1 Great Beanstalk (different system) and the DOS pair (different engine) stay out.
- **Platform variants and canceled prototypes parked for any future support work** — DOS / Mac file differences would need the engine to read both; prototypes are a maybe, pending ScummVM's case-by-case policy.

Room links and his email address are not recorded.

### Verified: Clue Jr. and Little Mermaid II confirmed on the engine (2026-11-20)

Followed Activity Center's method on the two new leads: downloaded a disc image for each from the Internet Archive, checked it against the Archive's recorded hash, and scanned it for `TGIFILE.ART` and competing-engine markers. Both **Observed** on this PC. Images live under `C:\pcloud\scooby-engine\` (non-git).

| Title | Image (archive.org) | Size / SHA-1 | Engine evidence (Observed) |
|---|---|---|---|
| **Clue Jr.: SpyGlass Mysteries (1999)** | [`cluejr1999`](https://archive.org/details/cluejr1999) → `CLUEJR.iso` | 565,450,752 B / `6255baef…4772` (verified) | `TGIFILE.ART` loose on the disc (43 `TGIFILE` hits). No `MMFW`, `trinket` / `RScenePort`, `Macromedia` or `EIDOS`. **DirectX-based** — `DDRAW.DLL`, `DINPUT.DLL`, `D3DIM.DLL`, `DSOUND.DLL` all present, confirming Mony's DirectX note. |
| **The Little Mermaid II: Return to the Sea (2000, Russian release)** | [`MERMAID2-RUS`](https://archive.org/details/MERMAID2-RUS) → `MERMAID2.iso` | 604,604,416 B / `368c5c38…4aca` (verified) | Game ships in an InstallShield `data1.cab` (magic `ISc(`); its uncompressed file table lists **`tgifile.art`** and the game exes **`lmii.exe` / `lm2.exe` / `Disney.exe`**. No `trinket`, `Macromedia` or `MMFW`. (A loose `tgifile.001` on the disc is a QuickTime movie — `ftypqt` / `moov` — a name coincidence, not the art container.) |

**Verdict: both are TerraGlyph Gen 1, confirmed.** That makes **three** confirmed non-Scooby `TGIFILE.ART` titles: Activity Center (2000), Clue Jr. (1999) and Little Mermaid II (2000).

- **Clue Jr. (1999) is the earliest confirmed Gen-1 binary — it predates the Scooby Gen-1 titles.** Showdown is 2000; Clue Jr. is 1999. So the `TGIFILE.ART` engine was already shipping a year before Showdown, and its early form is **DirectX-based** (DDraw / DInput / Direct3D / DirectSound), which the 2000–2001 titles dropped. A within-Gen-1 variation to account for if these ever get engine support.
- **Little Mermaid II is confirmed from the InstallShield file table, not a loose file.** `tgifile.art` and `lmii.exe` / `lm2.exe` are named in the cab directory with no competing-engine markers — enough to settle the engine identity. The `.ART` bytes themselves sit inside the compressed cab, so a byte-level decode (the [WP-002](WP-002-tgifile-art-decoder.md) decoder) would need the cab extracted with `unshield` (not available here). This is the Russian localization; the English original wasn't on the Archive as software.
- **No competing engine on either.** Neither shows Case File #2's Trinket / `R*` framework, Macromedia Director, or the Crystal / Eidos *Puppies to the Rescue* markers. Clue Jr.'s high raw "Crystal" string count is bundled third-party audio / video drivers and game demos on the disc (NFS / FIFA / NBA demo exes, ATI / XGI driver DLLs), not the Crystal Dynamics engine.

Byte-format identity (decoding a `.ART` with the WP-002 decoder) and a full engine-family check (exe hash, imports, RTTI) stay open on all three non-Scooby titles, and each would be its own WP. Images: `C:\pcloud\scooby-engine\Clue Jr SpyGlass Mysteries\CLUEJR.iso` and `…\Little Mermaid II Return to the Sea\MERMAID2.iso`.

Room links and his email address are not recorded.

### Localized releases: Norwegian Showdown and Case File #2 for the detection tables (2026-11-20)

A forward-looking note: he owns **Norwegian retail copies of Showdown and Case File #2** (bought thinking they were English). His proposal is that *after* the supported games are done, we scour abandonware sites for other localized releases, add each to the engine's ScummVM detection tables, and check that each still runs. He flags that **the Norwegian Showdown isn't on the abandonware sites** — so his physical disc may be the only accessible source for that release.

| Item (Reported) | Detail |
|---|---|
| Owns | Norwegian Showdown (Gen 1, **in scope**) and Norwegian Case File #2 (Trinket / OM++, **out of scope** — see [§Scope](#scope)). |
| Proposal | After the in-scope games work, collect localized releases, add them to the detection tables, verify each boots. A post-engine task, not now. |
| Preservation flag | The Norwegian Showdown is not on the abandonware sites; his disc may be the only route to its file hashes. |

**What this changes:**

- **This is standard, and correct, ScummVM practice — not scope creep.** ScummVM detects a game by hashing key files, so every localized pressing is its own detection entry (different files → different hashes). A mature engine's detection table carries as many real-world releases as can be legally obtained. So "add the languages to the detection" is just filling out the table once the engine exists; it doesn't touch what the engine has to *do*.
- **Norwegian Showdown is the directly useful one.** Showdown is the primary in-scope Gen 1 target, and a localization we can't otherwise get is exactly the kind of release a detection table would otherwise miss. His owning it — and it being absent from abandonware — makes his copy a genuine preservation asset: the hashes for that entry would have to come from his disc. Worth noting now so it isn't lost, even though the detection work is months out.
- **Norwegian Case File #2 is a preservation note, not an engine input.** Case File #2 runs the excluded Trinket / OM++ framework, so its localizations don't feed this engine's detection table. Good to have mapped (and a nice artifact if #2 is ever revisited), but it changes nothing here.
- **Timing: post-engine, as he framed it.** Nothing to do until the in-scope set detects and runs. Parked as a known follow-up: when the detection table is built, pull localized Showdown releases (his Norwegian disc included) and add an entry per pressing.

Room links and his email address are not recorded.

### MobyGames dev catalog reconciled: 11 titles, two entities, what it misses (2026-11-21)

Jeff found the MobyGames TerraGlyph page, the authoritative developer-credit catalog Mony couldn't reach ("mobygames wouldn't load"). The live site is Cloudflare bot-walled (a "Just a moment…" challenge — the same wall Mony hit, and not one to defeat), so I read it from the **Wayback Machine** instead: the [L.P. page](https://web.archive.org/web/2024/https://www.mobygames.com/company/3679/terraglyph-interactive-studios-lp/) (Moby ID 3679, snapshot 2025-01-16) and the [Productions Limited page](https://web.archive.org/web/2024/https://www.mobygames.com/company/35436/terraglyph-productions-limited/) (Moby ID 35436, snapshot 2025-02-19). **Observed** (catalog read directly); the engine column below is *our* map, not MobyGames'.

**Two TerraGlyph entities.** MobyGames splits the studio in two: **TerraGlyph Interactive Studios, L.P.** (Schaumburg, IL — the game-dev arm, credited on **11 games, 1995–2001**) and **TerraGlyph Productions Limited** (Dublin, IE — a feature-animation house, credited on 4 of those same games for art). The Dublin arm adds no titles of its own; its 4 (Phantom, Activity Center, Showdown, Buster) are a subset of the L.P. list.

The L.P. catalog, against our lineage map:

| MobyGames title (year, platforms) | Where it sits in our map |
|---|---|
| Scooby-Doo!: Show Down in Ghost Town (2000, Win) | **In scope** — Gen 1, primary target |
| Scooby-Doo!: Phantom of the Knight (2001, Win) | **In scope** — Gen 1 |
| Scooby-Doo!: Jinx at the Sphinx (2001, Win) | **In scope** — Gen 2 |
| Disney Activity Center: 102 Dalmatians (2000, Mac/Win) | **Confirmed Gen 1** (Observed, 2026-11-19) |
| Scooby-Doo!: Classic Creep Capers (2000, N64) | Ruled out — 3D console title |
| Tiny Toon Adventures: Toonenstein — Dare to Scare! (1999, PS1) | Ruled out — console |
| Blue's Clues: Blue's Big Musical (2001, PS1) | Ruled out — console; Mony: not our engine |
| Tiny Toon Adventures: Buster and the Beanstalk (1996, Win/PS1/Mac) | Sibling DOS/WinG engine (Mony: `TGI_ENGINE`/`TGI_QA`) |
| Hansel & Gretel and the Enchanted Castle (1995, DOS/Win) | Sibling WinG/`TGI_ENGINE` engine (Mony) |
| Kidsongs: Musical Mystery (1996, DOS/Win/Mac) | Ruled out by Mony |
| Rumpelstiltskin's Labyrinth of the Lost (1995, Win/Mac/DOS) | Ruled out by Mony |

**What this changes:**

- **No new titles — full corroboration.** All 11 were already in our map or Mony's once-over; MobyGames surfaces nothing we hadn't placed. It independently confirms every title Mony flagged is a TerraGlyph *studio* product, which is the premise under the "TGI" signature read.
- **The catalog undercounts the engine. This is the load-bearing point.** Neither TerraGlyph page credits **Clue Jr.: SpyGlass Mysteries** or **The Little Mermaid II: Return to the Sea** — yet we verified both ship `TGIFILE.ART` (Observed, 2026-11-20). So a MobyGames TerraGlyph credit is *not* the boundary of the engine's footprint; the engine appears on titles MobyGames attributes to other developers/publishers. Binary evidence (`TGIFILE.ART` on the disc) outranks a credit list, and this is exactly why Mony's PCGW + LaunchBox route found what MobyGames would have missed anyway.
- **No Case File titles on either page** — both stop at 2001. Consistent with the known 2002+ dev handoff (Case File #1 → IBS), not a contradiction; MobyGames credits the later games elsewhere.
- **Studio shipped across DOS/Win/Mac/PS1/N64 on multiple engines** (1995 Hansel & Gretel through 2001 Jinx). Reinforces that "TerraGlyph" is correctly a **studio-level** name, not an engine-specific one — the naming decision holds.
- **Scope unchanged** — still five in-scope binaries (Showdown, Phantom, Jinx, Activity Challenge, Case File #1).

The live MobyGames pages and Mony's room/email are not recorded.

### Correction: Case File #3 is Macromedia Flash, not Director (2026-11-21)

Mony emailed a correction: Case File #3 isn't Macromedia Director — it's **Flash**. The executable is a Flash player, the game data is a pile of mp3/wav/video and `.swf` files, and **Ruffle** runs it well. His point: worth documenting that you can play #3 on almost anything, and it also means #3 will **never** be a ScummVM title even if #2 ever gets an engine, because ScummVM won't support Flash. **Reported.**

This reverses a prior **Confirmed** reading (VISION and [tools/exes/README](../../tools/exes/README.md): "2026-06-03 — PE version resource confirms Macromedia Director engine"), so I verified it against the disc on hand (`C:\pcloud\scooby-engine\Scooby Doo! #3.iso`, 182,718,464 B, SHA-1 `bc709817…b11`) rather than overwrite one finding with another. **Observed — Mony is right:**

| Check (Observed) | Result |
|---|---|
| Disc exe version resource | `Scooby-Doo!.exe` is a **Windows installer database** — product "Scooby-Doo!(TM)", FileDescription "…installer database…", v4.1.07, **The Learning Company**. Not an engine binary at all. |
| Mounted disc root | Three files only: `AUTORUN.inf`, `scooby_icon.ico`, `Scooby-Doo!.exe` (181,897,154 B). The game payload is packed **inside** the installer. |
| Payload raw scan — Flash | **456 `.swf`** filenames + **6 `.flv`**; **92** `FWS`/`CWS` SWF headers (classic uncompressed + zlib Flash). |
| Payload raw scan — Director | **Zero.** No `.dcr`/`.dxr`/`.dir`/`.cst`, no `MV93`, no `RIFX`, no "Macromedia Director", no "Lingo". |

**What this changes:**

- **The engine is corrected everywhere to Macromedia Flash.** Fixed in [VISION](../01-VISION.md) (five places), [tools/exes/README](../../tools/exes/README.md) (the CF#3 block) and [WP-012](WP-012-detection-table.md). The **out-of-scope conclusion is unchanged** — only the reason moves from "Director" to "Flash."
- **How the 2026-06-03 reading went wrong.** It read the disc's single exe as the engine and took "Director" from its version resource. But that exe is TLC's **installer**, not the game, and its resource says nothing about Director (it's installer metadata). Macromedia shipped *both* Director and Flash, which is how the mistake slipped through. The game's actual content layer — 456 SWF movies — is unambiguously Flash.
- **It kills the 2026-11-20 "#3 before #2" sequencing.** That plan assumed ScummVM's Director engine could pick #3 up. With #3 being Flash and ScummVM having no Flash engine, #3 is simply out of scope for good — no ordering question remains. Marked superseded in [§Reply: targets, naming and the Director path](#reply-targets-naming-and-the-director-path-2026-11-20).
- **Preservation note, as Mony framed it:** #3 plays today under Ruffle on almost anything, so there's nothing for this project to add. Case File #2 (Trinket / OM++) stays the only *remaining* out-of-scope Scooby title that a future engine could ever touch.

The live disc contents and Mony's room/email are not recorded.

### ImageBuilder's MM* format may predate Gen 2; a catalog-sweep proposal (2026-11-21)

Mony's next email, with three threads: the Gen-2/3 `MM*` archive family may not be exclusive to the Scooby Gen-2 engine — he finds the same file extensions on **ImageBuilder's own pre-Scooby titles** (anchor: *Arthur's Thinking Games*, 1999, checked via SteamDB since it's on Steam), so MMFW may be ImageBuilder's house format rather than a TerraGlyph reformat; *Batman: Justice Unbalanced* runs Case File #2's engine; and he proposes automating a catalog-wide engine-fingerprint sweep. All **Reported**, except the catalog grounding, which is **Observed via Wayback** (live MobyGames is Cloudflare bot-walled, same wall as before).

| Item (Reported) | Detail |
|---|---|
| `MM*` not Gen-2-exclusive | *Arthur's Thinking Games* (ImageBuilder, 1999) carries the same `MM*` file extensions. Either the Gen-2 games mix ImageBuilder's engine with TerraGlyph's, or ImageBuilder brought an archive format it already had when it took the engine over. He's looked at only a few titles; wants a thorough pass on ImageBuilder's catalog. |
| Other possible `MM*` titles | Disney's *The Lion King II: Simba's Pride*, *Where in the World Is Carmen Sandiego? Treasures of Knowledge*, *Furby: Big Fun in Furbyland*, "possibly others." |
| *Batman: Justice Unbalanced* | Same engine as Case File #2 (Trinket / OM++). |
| Proposal | Give an agent the MobyGames pages for every company tangentially related to TerraGlyph / ImageBuilder / TLC, plus the Internet Archive and a decompression toolchain (`7z`, `bchunk`, `mdf2iso`, `cabextract`, `unshield`), and have it hunt for which games use which engine — manual sweeping is too tedious. Cited pages: [ImageBuilder (3355)](https://www.mobygames.com/company/3355/imagebuilder-software-inc/), [The Learning Company (40)](https://www.mobygames.com/company/40/the-learning-company/), [Riverdeep (7746)](https://www.mobygames.com/company/7746/riverdeep-interactive-learning-limited/). |

**Catalog grounding — ImageBuilder Software, Inc. (MobyGames Moby ID 3355, read via [Wayback](https://web.archive.org/web/2024/https://www.mobygames.com/company/3355/imagebuilder-software-inc/), snapshot 2024-12-30). Observed** (the credits are read directly; engine columns are still Reported):

| ImageBuilder title (year) | Bearing on the lineage |
|---|---|
| **Scooby-Doo!: Jinx at the Sphinx (2001)** | ImageBuilder is a **credited developer on our Gen-2 game.** MobyGames also credits it to TerraGlyph L.P. ([2026-11-21 reconciliation](#mobygames-dev-catalog-reconciled-11-titles-two-entities-what-it-misses-2026-11-21)) — so Jinx is a TerraGlyph + ImageBuilder co-production. |
| **Scooby-Doo!: Case File #1 (2002)** | ImageBuilder — matches our IBS-inherited Gen-3 reading ([scooby-exe §Case File #1](../formats/scooby-exe.md#case-file-1-gen-3)). |
| **Arthur's Thinking Games (1999)** | Confirms Mony's anchor is an ImageBuilder title, 1999 — two years before the Gen-2 Scooby games. |
| Lion King II: Simba's Pride – Active Play (1998); Carmen Sandiego: Treasures of Knowledge (2001); Furby: Big Fun in Furbyland (2000) | All three of Mony's "possible `MM*`" titles are confirmed ImageBuilder products. |
| Collaborators / lineage | Credited on **31 games, 1995–2002** (Portland, OR). Frequent partners: Learning Company (6), Brøderbund (2), Creative Wonders, Riverdeep (2), Disney Interactive (2) — the TLC / Riverdeep corporate family ImageBuilder sat inside. |

**What this changes:**

- **The MMFW "generations" track ImageBuilder, not a TerraGlyph format evolution — and the credits corroborate it.** Our lineage had Gen 1 = `TGIFILE.ART` (TerraGlyph) → Gen 2/3 = `MMFW`, with IBS (ImageBuilder) inheriting Gen 3. MobyGames credits ImageBuilder as a developer on *both* MMFW Scooby games — Jinx (Gen 2, 2001) and Case File #1 (Gen 3, 2002) — while Gen 1 (Showdown / Phantom, `TGIFILE.ART`) is TerraGlyph-only. So the Gen-1→Gen-2 boundary reads as a **change of tech provider** (TerraGlyph's `TGIFILE.ART` giving way to ImageBuilder's `MM*` engine), not an in-house reformat. Mony's "they brought a format they already had" fits the credits exactly. Reported anchor (Arthur's 1999 `MM*`) + Observed credits (Jinx / CF#1 = ImageBuilder) reinforce each other.
- **It refines the provenance story; it changes no scope and no engine work.** ScummVM still needs a `TGIFILE.ART` reader (Gen 1) and an `MMFW` reader (Gen 2/3); [WP-012](WP-012-detection-table.md)'s per-entry generation flag already draws exactly this format boundary. What it widens is the *potential MMFW corpus*: if `MMFW` is ImageBuilder's house format, their other titles (Arthur's, Carmen Sandiego Treasures, Furby, Lion King II Active Play, the Shrek / Dinotopia / Liberty's Kids activity centers) become candidate `MMFW` titles the same reader might one day open — the Gen-2/3 analogue of the non-Scooby `TGIFILE.ART` set (Activity Center, Clue Jr., Little Mermaid II).
- **Extension match ≠ format identity — the open verification is `MMFW` magic, not filenames.** The ImageBuilder side is all at the "`MM*` extension" / developer-credit level (Reported, from SteamDB filenames + MobyGames credits). `MM*` filenames aren't proof of the `MMFW` container — [WP-012](WP-012-detection-table.md) records our Gen-2 archives as `.MMF`/`.MMA`/`.MMP`/`.mms`, all carrying the `MMFW` magic, but a disc can hold `MM`-prefixed files that aren't that container. Promoting any of these to Observed needs the same disc scan run for the `TGIFILE.ART` titles: obtain an image, scan for the `MMFW` magic, rule out competing markers. None is done yet.
- **Batman: Justice Unbalanced extends the excluded Case File #2 engine, like the Powerpuff demo.** Reported: Mony places it on the Trinket / OM++ framework (Case File #2's engine, [WP-005](WP-005-engine-family-check.md)), not ours — another non-Scooby title on the *excluded* engine, of a piece with the `PPG2Demo` on the CF#2 disc ([2026-11-19](#reply-name-leak-fixed-scope-questions-for-jeff-2026-11-19)). Out of scope; engine identity Reported until a disc is scanned.
- **The catalog-sweep proposal is sound but splits into two jobs that must stay labeled — a decision for Jeff.** (1) *Corpus building* — enumerate the companies' games and which have obtainable images (MobyGames / credits + Internet Archive / GOG / Steam). Safe to automate; its output is leads, all Reported. (2) *Engine fingerprinting* — mount / extract each obtainable disc and scan a fixed marker set (`TGIFILE.ART`; the `MMFW` magic; Trinket `R*` / `.bul` / `.inx` / LZO; Director `MV93` / `RIFX` / "Lingo"; Flash `FWS` / `CWS`), each hit logged with the image's hash and the exact bytes found — never a store page or a filename. The hazard is the one this project already hit once (a scoped session fabricated a live run): an agent told to "look for engine clues" will infer identity from metadata and report it confidently. The guardrail is procedural — web sources build the candidate list; only a magic-byte hit from a verified image promotes a lead to a finding. Framed that way it's worth doing, and the marker set is small enough to hand an agent (or Mony) directly. Whether this project builds that harness, and who runs it, is Jeff's call; the drafted reply puts the engineering shape to Mony without committing the build.

A VISION provenance refinement (noting Jinx's ImageBuilder co-credit and the "`MMFW` = ImageBuilder's format" reading) is **parked** until at least one ImageBuilder non-Scooby title is scanned to Observed `MMFW` magic; VISION stays the settled-evidence layer, this log the developing thread.

The live MobyGames pages and Mony's room/email are not recorded.

### Reply: rename to `terraglyph`, decode review landed (2026-11-22)

Mony's 2026-11-22 email (three threads), the 2026-11-23 follow-ons (his
Norwegian-detection PR and upstream-timing counsel), and his later 2026-11-23
note (a fair catch that replies were being drafted here but not sent, plus an
offer to do a cleanup/refactor PR) — all actionable here:

- **Decode review of `TGIFILE.ART` scene-block / placement (Reported, already
  Observed and merged).** A close read of the room loader and placement walker: the
  close field at `+0x10` is "not read by the engine," `+0x88` is "opaque per-object
  data, not an unrelocated offset" (the placement relocation routine `0x43B940` is a
  `ret 4` no-op), and the `+0xB0`/`+0xB8` tables are never populated — shipped data
  doesn't use them (148-byte placement layout; room loader `0x43B080`, placement
  walker `0x435DC0`; decoded code on his branch `showdown-at-ghost-town`,
  `src/auto/text_0043A460.cpp` and `src/auto/text_00435DC0.cpp`). **Already
  integrated** into [tgifile-art.md](../formats/tgifile-art.md) (cites M. Armenchev
  2026-11-22; closes `+0x10`, `+0x88`, and the never-populated tables). Nothing
  outstanding.
- **"List the other `TGIFILE.ART` games in Target Games" (already satisfied).** The
  [VISION Target Games](../01-VISION.md) section already lists the in-scope set, and
  the non-Scooby Gen-1 confirmations (102 Dalmatians, Clue Jr., Little Mermaid II)
  are recorded in this log. `TGIFILE.ART` is a Gen-1 format — among the Scooby
  titles it is Showdown + Phantom, both already listed. No gap.
- **Rename `scooby` → `terraglyph` (decision taken).** Mony's reason — a WIP engine
  already holds the `scooby` name — checks out: upstream PR
  [#8063](https://github.com/scummvm/scummvm/pull/8063) claims `scooby` for a
  different game (the 1995 Acclaim platformer), and `terraglyph` is free upstream.
  Jeff approved the rename; it is recorded in
  [DECISIONS](../ai/DECISIONS.md#2026-11-22--engine-namespace-rename-scooby--terraglyph)
  and tracked as a fork PR. The prose name was already "TerraGlyph"; this makes the
  engine identifier match.
- **Norwegian Showdown detection (ported, 2026-11-23).** Mony opened fork PR
  [#8](https://github.com/barefootbetters/scummvm/pull/8) adding detection for the
  Norwegian retail Showdown — the localization he flagged on 2026-11-20 as absent
  from the abandonware sites, so his disc is the only source for its hashes. #8 was
  authored against the pre-rename `engines/scooby` path, so it can't merge after the
  `scooby` → `terraglyph` rename. Reviewed (entry correct: `showdown` id, valid
  `Common::NB_NOR`, fields mirror the English entry) and **ported onto
  `engines/terraglyph` as fork PR [#11](https://github.com/barefootbetters/scummvm/pull/11)**,
  Mony kept as the commit author; builds clean (`--enable-engine=terraglyph` links).
  Hashes are Reported (his disc only), corroborated by his "detects and runs" since
  the detector hashes the first 5000 bytes. **Next action: Jeff merges #11 and #8 is
  closed in favor of it** — or, if Mony prefers, he re-pushes #8 onto the rename and
  #11 is dropped (offered in the reply).
- **Upstream-submission timing (agreed, 2026-11-23).** Mony's counsel: hold the
  ScummVM-upstream pitch until the Gen-1 games run end-to-end and the code is cleaned
  up (it's currently one flat folder, no subfolders). Agreed — engine first, upstream
  pitch later. His survey of recently landed AI-assisted engines (and the one bounced
  for unreadable commits / unclear messages) is the groundwork for when we make that
  case. Nothing to action now beyond keeping the pitch parked.
- **Replies drafted-but-not-sent (fair catch, 2026-11-23).** Mony noted the repo
  carried "here's how I'd reply" drafts that never went out as actual emails — a real
  process gap on our side, not a tone problem on his. Fixed by sending the
  consolidated reply below rather than parking another draft.
- **Cleanup/refactor PR offer (accepted, 2026-11-23).** Mony offered a PR for folder
  organization, matching ScummVM's layout, and splitting terraglyph-global vs
  per-game code. Accepted: the folder/style alignment is exactly what's needed before
  any upstream pitch and he's welcome to run with it; the terraglyph-global vs
  per-game **split** is a larger structural call with engine work in flight, so its
  timing is to be coordinated so it doesn't collide. (Jeff's call if he'd rather defer
  the whole thing instead.)

**Reply (Jeff's to send — consolidated, supersedes the earlier unsent draft):**

> Mony — fair hit, and that one's on me. I've been drafting replies into the repo and
> not actually hitting send, which is a dumb way to run a collaboration. Fixed as of
> this email.
>
> Quick on all of it:
>
> - Your Norwegian Showdown detection is in. One wrinkle: #8 was against the old
>   `engines/scooby` path, and the engine got renamed `scooby` → `terraglyph` right
>   after you opened it, so it couldn't merge clean. I rebased your exact entry onto
>   `engines/terraglyph` and kept you as the commit author — it's PR #11, builds
>   clean. Mind closing #8 in favor of it? Or if you'd rather re-push #8 onto the
>   rename yourself, say the word and I'll drop #11 — your call, it's your
>   contribution.
> - Rename's done — you were right, `scooby`'s effectively taken upstream by the
>   Acclaim platformer PR, and `terraglyph` fits the whole Gen-1 catalog anyway.
> - On "the focus's been kinda out there" — agreed. The Warner/licensing material is a
>   parked thinking-out-loud note, not where the work is. The work is the engine.
>   Keeping it that way.
> - The loader/placement decode is already folded into our TGIFILE.ART notes (credited
>   to you): `+0x10` not read at runtime, `+0x88` opaque, `0x43B940` a `ret 4` no-op.
>   That closed the last room-block unknowns — thank you.
>
> And yes, please do the cleanup/refactor PR. Matching ScummVM's folder layout is
> exactly what we'll need before any upstream pitch, and you know that layout better
> than we do — run with the folder/style alignment whenever suits you. The one piece
> I'd want to sync on first is the terraglyph-global vs per-game split: that's a bigger
> structural call and there's engine work in flight, so let's coordinate timing so it
> doesn't collide. Everything else, go for it.
>
> Thanks again — genuinely useful, all of it.

### Reply: refactor plan and merge timing (2026-11-24)

Jeff sent the consolidated reply above (2026-11-24). Mony replied the same day
laying out his refactor plan — and scoping his own restraint, which is the
right instinct:

- **Folder split (doing now).** Keep most things at root; add `format/`,
  `audio/`, `graphics/`; move rooms to `rooms/{game_name}` for single-game
  screens, with shared screens directly in `rooms/`. **Remaining splitting and
  dehardcoding deferred for discussion** — exactly the coordination asked for.
- **Merge handshake.** He keeps his (forthcoming refactor) PR synced to the
  `scooby-engine` branch and waits for Jeff's go to merge.
- **`detection_tables.h` reorg after the refactor merges** — e.g. turning the
  boilerplate into `#define`s (standard ScummVM shape). Fine.
- **Comments.** He notes many are redundant, narrate raw hex addresses, or are
  "clearly for the LLM." He'll trim lightly now, full pass later.

**Timing is the load-bearing call, and the fork state decides it.** A
`rooms/{game_name}` move rewrites include paths tree-wide — maximally
conflict-prone. At the time of reply the fork had **open PR
[#9](https://github.com/barefootbetters/scummvm/pull/9) (WP-083, a Phantom
room)** and a steady room-by-room cadence on `scooby-engine` (WP-080, -081,
-083). Merging the reorg mid-wave conflicts with every open room branch.
**Position: hold the reorg for a deliberate pause — land it _first_ on a quiet
branch and rebase the in-flight room WPs onto the new layout**, rather than
merging it into a moving target. Comments: green-light trimming the
hex-narration / LLM-oriented ones as he goes (a human reader, and eventually a
ScummVM reviewer, gets nothing from them); dedicated pass later. Mony's
now-merged Norwegian entry ([#11](https://github.com/barefootbetters/scummvm/pull/11))
means his **#8 can close**; the refactor is a fresh PR.

**Reply (Jeff's to send):**

> Mony — the split sounds right. `format/` `audio/` `graphics/` at root and
> `rooms/{game_name}` for single-game screens with shared ones in `rooms/` is a
> clean line, and I'm glad you're parking the deeper splitting and dehardcoding
> for us to talk through rather than doing it all at once.
>
> On timing the merge — that's the one piece I want to get right, because the
> folder move rewrites include paths across the whole engine and there's active
> room-by-room work in flight right now (WP-083's open, more Phantom rooms queued
> behind it). If the reorg lands in the middle of that, every open room branch
> conflicts. So rather than merge it into a moving target: keep your PR synced
> like you said, and let's land the reorg at a deliberate pause — ideally it goes
> in first on a quiet branch and the in-flight room WPs rebase onto the new
> layout, not the other way around. I'll give you the go the moment the current
> wave settles.
>
> `detection_tables.h` reorg after that, boilerplate into `#define`s — yep,
> that's the usual ScummVM shape, go for it.
>
> And on the comments: you read that right, and please do trim as you go. The
> ones that just narrate a hex address, or are obviously written at the model,
> are exactly the ones to cut — a human reader (and eventually a ScummVM
> reviewer) gets nothing from them. A dedicated pass later is fine; no need to
> make it a project in itself now.
>
> One housekeeping note: your Norwegian detection entry is already merged (I
> rebased it onto the renamed engine as #11), so #8 is safe to close — the
> refactor will be its own PR.
>
> Thanks — this is the right shape for all of it.

### First look at the repository (2026-11-11)

Read from a fresh clone of the collaborator's private repository (its first commit, `1114c89`), outside this checkout. Nothing was built yet. The evidence column uses the [§Evidence model](#evidence-model).

| Item | Value | Evidence |
|---|---|---|
| Executable identity | The project config pins the game by SHA-1 `dfd47fbdfb87e349dec62524fc79e26d2d88703e`, which equals the SHA-1 of this project's local Case File #1 executable. The size matches too: 786,432 bytes. The local copy's SHA-256 is the WP-007 lock, `9813A3DD…7CF8`. | **Observed**: hashed locally, compared with the config |
| Project type | A decompdecomp PC project created "from scratch", with the game's `libexpat.dll` (at `0x10000000`) as a second program | Read from the project files |
| Compiler | Visual C++ **6.0** by default (`/O2 /GX`). One source file is pinned to 7.1, and many files carry per-file `/O1` or `/Oy-` flags. No file is set to VC 5.0. | Read from the project files |
| Function inventory | 3,376 functions, 455,576 bytes of code: 3,063 in the executable, 313 in `libexpat.dll` | **Reported**, from the tool's own summary in the project files. Consistent with the "about 3,300" above. |
| Source written so far | 150 `.cpp` files covering the whole address range, with about 1,175 C function bodies, plus recovered class declarations and 77 named functions | Counted locally; **match status unknown** |
| Overlap with this repo's research | 11 of the 71 class names in the source are already in [scooby-exe.md](../formats/scooby-exe.md) from the WP-007 strings, among them `MMPictureLoader` and `MMSoundLoader`. Several other resource-file and loader classes are new to this project. | Counted locally |

How many of those C bodies compile to the original bytes is not known yet. The tool's summary in the project files was written when the project was created and counts 0 functions from C, so a local build is the only way to measure the match rate (see [§Immediate next actions](#immediate-next-actions)). Class and function names from the repository stay out of this page until the host's terms on public quoting are known ([open question 18](#open-questions)). The two exceptions are names already public here from the WP-007 strings.

## Toolchain

| Tool | Role here | Notes |
|---|---|---|
| Ghidra | Function boundaries, cross-references, types, naming; the PC-platform function cut-out decompdecomp relies on | Already the project's planned tool ([WP-001](WP-001-ghidra-session.md)) |
| decompdecomp | Desktop app that drives AI agents to write C/C++ per function, builds each attempt with the original compiler, and scores it against the original bytes; also runs the cooperative "room" | AGPL-3.0. A fork of the archived decomp.wtf. Read 2026-11-11 from its [GUIDE](https://github.com/n-delic/decompdecomp/blob/main/docs/GUIDE.md#decompile-together) |
| `m2c` | Draft C from assembly, as a starting point for agents | Bundled by decompdecomp |
| decomp-permuter | Randomized rewrites of near-miss functions toward a byte match | Bundled; the guide limits it to near misses |
| AI coding agents | Write and revise candidate C | The guide lists CLI agents (Claude Code, Codex CLI and others) and any OpenAI-compatible API (DeepSeek, OpenRouter, local models) |
| Manual analysis | Where automation stalls, and for every semantic conclusion | Human work, recorded here |

**Compiler coverage matters for this binary.** *Corrected 2026-11-14:* the project first placed Case File #1 in the Visual C++ 5.0 era, from a product-ID mislabel in `tools/rich_header.py`. Read correctly, Case File #1 is **Visual C++ 6.0**: linker 6.00 in the PE header, its own C++ (161 objects) from the VC6 **Processor Pack** (`Utc12_2_CPP` build 8943, which richprint attributes to SP4 + Processor Pack), plus VC6 C objects at builds 8797 and 8168 ([scooby-exe §Toolchain](../formats/scooby-exe.md#toolchain)). The decompdecomp guide documents Windows compilers from **Visual C++ 6.0** upward, and the host project defaults to VC 6.0 with one file on 7.1 ([§First look at the repository](#first-look-at-the-repository-2026-11-11)). So byte-identical matching is plausible, which fits the collaborator's report of byte matches under VC 6.0. The build is the catch. decompdecomp's VC 6.0 is RTM build 8168 (Observed 2026-11-14), not the Processor Pack's 8943, and the host has since found the same gap from his side. Whether a Processor Pack build reproduces the game's C++ exactly is the next thing to measure ([§Progress, libexpat and the compiler build](#progress-libexpat-and-the-compiler-build-2026-11-14-to-11-15)). Showdown, the next host project, is VC6 build 8966 (richprint: SP5), without the Processor Pack.

## GitHub versus the decompdecomp cooperative room

These are two different systems that complement each other. Cooperative decompilation does not happen by pushing to a shared GitHub repository.

| | GitHub (the collaborator's private repo, and this repo) | decompdecomp cooperative room |
|---|---|---|
| Purpose | Source management, review, documentation, issue and decision tracking, durable history | Coordinating live, parallel decompilation |
| Unit of work | Commits, pull requests, issues | One function at a time, handed out by the host |
| Who does the work | Whoever commits | Each member's own agents, on that member's machine and at that member's expense |
| Game data | Never stored: no binaries, no assets | Each member reads code from their own legally obtained copy. The guide says no game data or assembly passes between machines, and all copies must be identical |
| Verification | Review | The host checks each submitted match against its own copy of the game |
| Access | Repository permissions | An invite link (private room) or an address (public room); the host can approve or remove members |
| Transport | GitHub | Chosen by the host: a Cloudflare quick tunnel, or the host's own address (LAN, Tailscale, a server) |

Per the guide, a member joins with **New project → Join a team's room**, pastes the link, picks a name and points at a local copy of the game. The host hands out functions so no two people work the same one, verifies matches, and shares names, structs and notes back to the team. The guide doesn't describe how a claim expires, how conflicting claims resolve, or exactly how a member's match is merged on the host. Those are [open questions](#open-questions) for the host. **Partly answered from the source (2026-11-13, decompdecomp `9e19b4d`):** members' agents claim functions through the room, the host checks each match against its own copy, and the host records each match against the member's agent that made it (`<member>.<agent>`).

For PC projects the guide says decompdecomp keeps its work in the project's own git repository. That repository is the collaborator's private repo, not this one. We have push access to it but treat it as read-only, at his request (2026-11-13). He pushes the room's progress there. This repo receives only the evidence described in [§Evidence and validation requirements](#evidence-and-validation-requirements).

## Evidence model

This repo has no formal evidence scale. Format specs use "Confirmed", "predicted", "unverified" and High/Medium/Low confidence in their Hypotheses tables. Decompilation output is easy to over-trust, so this WP adds a scale for every finding that comes out of it:

| Level | Meaning | Maps to existing usage |
|---|---|---|
| **Reported** | Supplied by a collaborator; not reproduced locally | A Hypotheses-table row at best |
| **Observed** | Reproduced locally: in the binary, in Ghidra, under a debugger, or in the running game | Eligible for a Findings section, cited with the binary's SHA-256 |
| **Matched** | Candidate C compiles to the original bytes under a recorded compiler and flags | Evidence that the code is equivalent, not that it is understood |
| **Corroborated** | Backed by at least one independent source: asset behavior, runtime tracing, a second executable, existing format research | "Confirmed" |
| **Integrated** | Reimplemented independently and tested in `engines/scooby/` | Phase 2+ |
| **Accepted** | Reviewed and accepted upstream by ScummVM | Phase 5 |

Rules:

- Every figure in [§Collaborator-reported starting point](#collaborator-reported-starting-point), every agent result, and every cross-game expectation in this WP is **Reported** today. The exceptions are the rows the [§First look](#first-look-at-the-repository-2026-11-11) table marks otherwise.
- A finding moves up a level only with a citation: the SHA-256 of the binary, the address, the tool and version, and who reproduced it.
- **Matched is not understood.** A byte-identical function proves the C is equivalent to the original. It does not prove the function name, the struct layout, the high-level meaning, or that the code is readable or suitable for ScummVM. Semantic claims need Observed-level human analysis, and ideally Corroborated.

## Scope

In scope:

1. Getting access to the host's cooperative room and private repository, and recording the terms (not the URLs or credentials) in [§Status and decision log](#status-and-decision-log).
2. Checking that the local Case File #1 binary is byte-identical to the host's, and to the WP-007 lock (SHA-256 `9813A3DDBE58BC9D7CC898030F4A2F93658FD4A69156BA8531C6E4F273E97CF8`, 786,432 bytes).
3. Installing decompdecomp and its prerequisites in an isolated environment, and recording the tool versions.
4. One capped trial run that contributes local agent capacity to the room, with cost, throughput, match rate and failure rate measured.
5. Steering trial work toward the [research targets](#research-targets) where the room allows it.
6. Landing Observed-or-better findings in `docs/formats/scooby-exe.md` (Case File #1, Gen 3) in the [output format](#output-specification), and leaving Reported items labeled as Reported.
7. Taking the [decision](#status-and-decision-log) from Proposed to Accepted or Rejected, with the measurements behind it.

Out of scope:

- Any C++ in `engines/scooby/`. Implementation starts in Phase 2, through [WP-010](WP-010-scummvm-scaffold.md) and later WPs.
- Case File #2. WP-005 (2026-11-13) found it runs a different engine, so it is out of the project's scope.
- Gen 1 `TGIFILE.ART` decode work. That stays with [WP-001](WP-001-ghidra-session.md) and [WP-002](WP-002-tgifile-art-decoder.md). Case File #1 doesn't ship that format.
- Changing any engine-family or generation classification. That belongs to [WP-005](WP-005-engine-family-check.md).
- Committing reconstructed C, generated assembly, or any game data to this repository.

## Local setup prerequisites

Step-by-step instructions are in [Setting Up decompdecomp on Windows](../reference/decompdecomp-setup.md). This list is the summary. The guide was read 2026-11-11 against release `v1.0.10-alpha.1`. Its README and guide disagree on the Windows installer type (MSI or setup `.exe`), so check the release page.

- Windows 10/11 x86-64. The guide says Windows PC games don't need WSL 2.
- decompdecomp from its release installer (it bundles Python and the app), or from source with `uv` and Python 3.12.
- Ghidra, which the guide requires for the PC platform's function cut-out. Record the version.
- The compiler the host project is configured with: Visual C++ 6.0, plus 7.1 for one file. In `v1.0.10-alpha.1` they install from decompdecomp's **Compilers & tools** screen into `%LOCALAPPDATA%\decompnet\toolchains\msvc` (observed 2026-11-11), not from the Setup screen the GUIDE describes.
- To build the host project outside the app: Python, `ninja`, and the configured MSVC toolchain (`tools/configure.py <version> --msvc <folder>`), plus [objdiff](https://github.com/encounter/objdiff) for per-function progress. The game's `libexpat.dll` goes beside the executable in the project's gitignored `orig/` folder.
- An agent provider with a hard spend limit set **on the provider side**. The guide describes usage-limit waits and auto-pause after repeated failures, but no budget cap. `v1.0.10-alpha.2` has one, **Settings → Agents → Budget**, in app-priced dollars (observed 2026-11-16). Set it too.
- A legally obtained Case File #1 disc or ISO. The working copy of the executable lives under the gitignored `tools/exes/casefile1/`, as in [tools/exes/README](../../tools/exes/README.md). The disc filename is `Case File #1.exe`; the local cache renames it `Scooby.exe`.
- Isolation: a dedicated Windows user profile or VM, or at minimum a decompdecomp project directory outside this checkout, or under the gitignored `tools/decomp/`.

## Cooperative connection workflow

1. Get the current invite link from Mony privately, each time. The room runs over a temporary tunnel, so the link changes whenever he restarts decompdecomp; an old link is dead, not a fallback. Never paste a link into this repo, an issue, a commit message or a public page.
2. Confirm with the host which compiler, flags and decompdecomp version the room uses, and which copy of the game they hold. Compare SHA-256 values before joining.
3. In decompdecomp: **New project → Join a team's room**, paste the link, choose a display name, and select the local executable.
4. Set the provider spend cap and the number of helpers before starting any agents. Start small: one or two helpers, not the guide's maximum of 24.
5. Run the trial (see [§Immediate next actions](#immediate-next-actions)). Record results as you go.
6. Stop sharing agent capacity when the cap is reached or the trial time box ends, whichever comes first.

## Research targets

Ordered by value to the ScummVM engine. Gen 3 unless noted. Anchors come from the WP-007 [Case File #1 strings](../formats/scooby-exe.md#case-file-1-gen-3) and imports.

| Priority | Subsystem | Why it matters | Anchors to start from |
|---|---|---|---|
| 1 | File I/O and the `MMFW` archive loader | Answers the [MMFW container](../formats/mmfw-container.md) unknowns: sub-header layout, per-entry records, ID → entry resolution | `CreateFileA` / `ReadFile` call sites; `MMFW Films/Pictures/Scripts/Sounds` labels; `Bad checksum in <category> resource file` error strings; `%s_%s_%04X` key template |
| 2 | Graphics decode for `MMFW` picture entries | Tests the hypothesis in the MMFW spec that payloads share Gen 1's F0-opcode encoding. If they do, it informs WP-002 | Callers of the picture-resource loader; GDI DIB calls |
| 3 | Audio archive indexing and playback (`.MMA`) | The Gen 3 audio path, and an indirect lead on the Gen 1 `.dat` index (see [audio-archives](../formats/audio-archives.md)) | `MMFW Sounds`; dynamic `DSOUND.DLL` / `DirectSoundCreate` load |
| 4 | XML / script loading and interpretation | Gen 3 config and script layer (`launch.xml` via `libexpat.dll`). The parser is stock Expat 1.95.3 (Observed 2026-11-14), so the target is the game's own handlers and the XML schema they read, not the parser | `XML_ParserCreate` / `XML_SetElementHandler` callers |
| 5 | Object initialization and scene / room management | Shared engine core across generations, per the Vision | RTTI classes `PGStageWindow`, `SMMovieScene`, `SMSuspectsAndCluesScene`, `SMGameActFactory` |
| 6 | Input handling and game-state machine | Phase 4 needs these | `IBState`, `IBEvent`, `IBEventHandler`, `IBStateEventThread` (the last one is a threading flag; ScummVM engines are single-threaded) |
| 7 | Save and load | Phase 5 ScummVM save integration | `TLC Case File #1 Users.dat`, `TLC Case File #1 User #%d.dat`, `Scooby 4 Museum Save Data`, `SHFOLDER.DLL` load |
| 8 | Cutscene playback | Gen 3's raw `.avi` path through COM | `CoCreateInstance` callers; `INTRO_0*.avi` and other `.avi` names |
| — | Inherited TerraGlyph units versus IBS-added code | Function-level answer to the engine-family question | Functions matching Jinx (Gen 2) code; the `MM*`/`UU*` class families against `PG*`/`SM*`/`IB*` |

## Evidence and validation requirements

What may land in this public repository, per finding:

- **Identity:** the binary's SHA-256, plus the function's address and size.
- **Name and role:** a proposed name, the subsystem, and a plain-language description of the behavior.
- **Evidence level** from the [scale above](#evidence-model), with **provenance**: who produced it, with which tool and version, the date, and whether it was reproduced locally.
- **Signatures and structs** as needed, with field offsets and types.
- **Pseudocode or short excerpts** where they explain an algorithm, as WP-001 plans for the `TGIFILE.ART` decode function.

What stays out of this repository: whole files of matched C, generated assembly listings, decompdecomp project folders, the executable, extracted assets, and anything else derived wholesale from the binary. They belong in the collaborator's private repository or in gitignored local paths.

Validation before a finding is promoted:

- **Reported → Observed:** reproduce it in local Ghidra against the SHA-locked binary, or in decompdecomp locally.
- **Observed → Corroborated:** check it against existing format research (an `MMFW` header field read by the function matches the hex in [mmfw-container](../formats/mmfw-container.md), for example), against runtime behavior, or against a second executable.
- **Matched code:** record the compiler, the version and the flags. A match under a different compiler than the original (VC 7.1 for VC 6.0 code, or plain VC 6.0 for Processor Pack code, for example) is recorded as a near-equivalent and not called byte-identical to the original toolchain.

## Cross-game reuse strategy

**Reported or expected, not yet demonstrated for these games.** The decompdecomp guide describes:

- trying a matched function on identical functions in the user's other games at no agent cost ("twins"),
- reusing a matched twin's C wherever the same code occurs again,
- and a similarity search over instruction sequences to find copied or inlined code.

Plan:

1. Build a stable Case File #1 baseline first: a known set of Matched and Observed functions with names.
2. Add the **Jinx (Gen 2)** binary next, not Case File #2. WP-007 shows the strongest inheritance evidence is Jinx → Case File #1, so the identical-function count there is the cleanest function-level test of that inheritance.
3. ~~Add Case File #2 after that.~~ Dropped 2026-11-13: WP-005 found Case File #2 runs a different engine (shared with a *Powerpuff Girls* title), so it is out of scope.
4. Gen 1 (Showdown) cross-matching is opportunistic. If Gen 1 shares little code with Gen 3, decompdecomp on Case File #1 will not answer the `TGIFILE.ART` F0-opcode question directly. That still needs WP-001 or a Showdown decompdecomp project. **A Showdown project is the higher-value follow-on for the engine** (Jeff, 2026-11-13): it aims the tool at the Gen 1 binary itself. WP-002 has since decoded `TGIFILE.ART` from the data alone (2026-11-13), so a Showdown project's value is the game logic more than the decoder. Showdown is Visual C++ 6.0 (game C++ build 8966, which richprint attributes to SP5), corrected 2026-11-14 from a VC5 mislabel, so decompdecomp's VC 6.0 is the right compiler family for it too. See [open question 20](#open-questions).

The output of each step is a count of identical, near and unique functions per binary pair, recorded with evidence levels. These counts are evidence for WP-005, not a classification by themselves.

First measured counts (**Reported**, 2026-11-18): the two Gen 1 games share 280 byte-identical functions; Gen 1 ↔ Case File #1 share 170. Byte-identical undercounts shared-but-modified code and is weighted toward CRT and runtime helpers, so it is a floor, not the engine-reuse figure. See [§Progress across the games](#progress-across-the-games-twin-matching-and-reuse-counts-2026-11-18).

## ScummVM integration boundaries

- The decompilation is **research evidence**. The ScummVM engine is an **independent implementation** written to ScummVM's architecture, style and licensing ([02-SCUMMVM-INTEGRATION §11](../02-SCUMMVM-INTEGRATION.md#11-code-style-and-licensing)).
- No reconstructed executable code is imported into `engines/scooby/`, wholesale or by the function. Engine code is written from the documented behavior: names, structs, offsets, algorithms described in prose or pseudocode.
- Byte-matching C is shaped to reproduce 2002 compiler output, not to be maintainable. Even where it is legally usable, it is the wrong shape for ScummVM (single-threaded `Engine::run()`, `Common::File` / `Common::Archive`, no Win32 / DirectX / COM).
- A finding becomes a ScummVM task only when it fills a gap the data-driven path can't, which is the Vision's existing [Game Logic Strategy](../01-VISION.md#game-logic-strategy) rule.

## Legal and repository hygiene

- Never commit game executables, CD images, extracted proprietary assets, copyrighted media, secrets, tokens, or room links and credentials. `.gitignore` already blocks the game data. This WP adds `tools/decomp/`, decompdecomp project files and `.env` files.
- This repository and its GitHub Pages site are **public**. Cooperative connection details (room links, invite tokens, credentials) stay out of every page.
- The collaborator is credited as **Simeon Armenchev (monyarm)**, as he asked on 2026-11-14. His private repository isn't linked until he makes it public. His email and other contact details stay out of every page, as do the repository's contents.
- Review generated C before relying on it. AI-written code that matches bytes can still carry misleading names and comments.
- Keep research artifacts separate from production ScummVM code. Nothing questionable or license-incompatible goes into `engines/scooby/`.
- Record provenance for every major technical conclusion.
- Prefer hashes, offsets, signatures, pseudocode, behavior descriptions and independently written notes over distributing anything binary-derived.
- Use only a legally obtained copy of the game. The project's legal basis is in [Vision §Legal Basis](../01-VISION.md#legal-basis).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Compiler mismatch.** The binary is VC 6.0 with the Processor Pack (C++ build 8943). decompdecomp's `6.0` is VC6 RTM, build 8168 (**Observed** 2026-11-14), so most game functions are being matched with a different build than produced them. Some functions may never match under RTM. (*Corrected 2026-11-14:* this row first read "VC 5.0-era", from a tool mislabel.) | Record the compiler and its build per match. The host is testing which build comes closest, and plans to make it the project default (2026-11-15, Reported); decomp.me's `msvc6.5pp` is the nearest available: the same Processor Pack line, but build 9044, not 8943 ([§decomp.me's VC6 builds](#decompmes-vc6-builds-2026-11-15)). Measure the true byte-identical rate during the trial. |
| **Over-trusting Reported figures** (function counts, coverage, agent results) | Use the evidence scale. Nothing goes into a Findings section below Observed. |
| **Unbounded agent spend.** No budget cap is described in the guide; helpers resume after limit resets. (`v1.0.10-alpha.2` adds **Settings → Agents → Budget**, in app-priced dollars, default 0 = no limit; observed 2026-11-16.) | Set a provider-side spend cap, decompdecomp's **Budget**, and a function-count cap before starting. Use few helpers. Stop at the cap. |
| **Leaking private details into public pages** (room links, credentials, contact details, contents of the private repo) | Hygiene rules above. Review the diff before each commit. Room links never go into files at all. |
| **Proprietary material committed by accident** | `.gitignore` entries for decomp work paths. Keep the decompdecomp project outside this checkout or under `tools/decomp/`. |
| **Byte-matching C mistaken for engine code** | [ScummVM integration boundaries](#scummvm-integration-boundaries). Engine work cites behavior notes, not reconstructed source. |
| **Scope creep away from Phase 1 blockers.** Case File #1 is a Stretch title; Showdown is the primary target. | Keep the WP time-boxed to the trial. The Gen 1 blockers (WP-002, WP-004) keep priority. Gen 3 findings feed Gen 1 only where they actually transfer. |
| **The collaboration ends or stalls** | Only Observed findings, documented here, count toward this project, so they survive without the room. |
| **Tool churn.** decompdecomp is a young fork with self-updating installers. | Pin and record the version used for every finding. |
| **AGPL-3.0 tooling** | The license covers the tool, not its use, and the tool is never distributed or bundled from here. The ScummVM engine never links against it. |

## Open questions

Engine lineage:

1. Are the Case File games built on the TerraGlyph engine used by the Mystery Adventures titles? Toolchain and string evidence for Case File #1 points to inherited Jinx-era code ([Engine Lineage](../01-VISION.md#engine-lineage-2026-06-finding)). That is not yet confirmed at the function level. Case File #2 is answered: WP-005 (2026-11-13) found a different engine.
2. Is each Case File a later revision, a fork, or a separate engine? Answered for Case File #2 by WP-005: a separate engine. Open for Case File #1 at the function level.
3. Which functions are identical or structurally related across the two Case File executables, and between Jinx and Case File #1?
4. Do the Case File games reuse archive formats from the earlier games? Disc evidence says Case File #1 uses `MMFW` like Jinx, and Case File #2 uses `.bul` / `.inx`. Neither uses `TGIFILE.ART`.
5. Are `TGIFILE.ART`, the audio `.dat` archives, `object.ini` or the `Scooby.eng` string-table conventions shared with any Case File? Not as files on the Case File #1 disc. Shared *code* conventions (resource-key templates, error templates) are open.

Toolchain and tooling:

6. Which compiler and settings produced each executable? *Answered in part (2026-11-14, Observed):* all are Visual C++ 6.0 with linker 6.00. Game C++ builds: Showdown and Phantom 8966, Jinx 8168, Case File #1 8943 (Processor Pack). The 2026-06 "VC 5.0" reading was a tool mislabel. Exact flags are unknown.
7. How reliably can decompdecomp reproduce these functions byte for byte? *Partly answered (2026-11-14, Observed):* the VC6 it installs is RTM build 8168, not the Processor Pack's 8943, so only Case File #1's 36 build-8168 C objects were built by exactly that compiler. The host found the same thing from the other side: the game was built with a compiler between 6 and 7, and he's testing which build comes closest (2026-11-15, Reported). *Updated 2026-11-15 (Observed):* decomp.me's `msvc6.5pp` is a later Processor Pack, code generator 13.00.9044, which other projects show stamps build 9044, not 8943. No decomp.me compiler is exactly 8943. *Updated 2026-11-15 (Reported):* with `msvc6.5pp` as the project default, the rerun matched 84 new functions in its first quarter. *Updated 2026-11-16 (Reported):* the rerun added about 164 matches in all. Sweeps of the other compiler builds and their libraries added none, and per-function compiler splits about a dozen. Still open: whether any functions need the 8943 pack itself. Gen 1 (8966) has an exact match in decomp.me's `msvc6.5`. See [§decomp.me's VC6 builds](#decompmes-vc6-builds-2026-11-15).
8. Which functions need manual reconstruction after automated processing stalls, and does that set cluster by subsystem?

Using the results:

9. Which discovered subsystems are useful for the ScummVM implementation?
10. What source-derived material, if any, must stay outside the public repository? The default here: all matched C and generated assembly.
11. How will function identities and discoveries map to clean-room-style ScummVM code? Proposal: a function map in `scooby-exe.md`, with behavior notes as the only input to engine code.
12. Can the decompilation resolve the current audio index-table location? Only indirectly: Case File #1 has no `.dat` audio archives. An `.MMA` loader structurally like the Gen 1 one would be a lead.
13. Can executable analysis confirm the meaning of the F0 opcodes in `TGIFILE.ART`? Only directly from a Gen 1 binary. From Case File #1, only if the MMFW picture decoder turns out to share the algorithm.

For the host, about the room:

14. How are function claims made and expired, and how are conflicts resolved? *Partly answered (source, 2026-11-13):* claims go through the room, so no two agents work the same function. Expiry and conflicts are still open.
15. How does a member's match get merged, and what does the host share back? *Partly answered (source, 2026-11-13):* the host checks the match against its copy, credits it to `<member>.<agent>`, and shares it with the room. The host then pushes the work to the repository every day or so.
16. Does the room check that every member's executable is identical, or is that on each member? *Partly answered:* the project pins the game by SHA-1, and this project's copy matches it. Whether the room enforces it on join is still open.
17. Which compiler and version is the room configured with, and which decompdecomp version? The project files default to VC 6.0 (one file on 7.1). *Answered (2026-11-14, Reported):* decompdecomp `v1.0.10-alpha.1`, updated to each new release; the compilers and Ghidra are the ones decompdecomp supplies; flags are decompdecomp's detected defaults, varied per function where needed; about 6 or 7 functions are detected as built with 7.x. See [§Tool versions from the collaborator](#tool-versions-from-the-collaborator-2026-11-14).
18. What are the terms of the private repository: license, who may read it, what may be quoted publicly, and how the collaborator wants to be credited? *Partly answered (2026-11-13, 2026-11-14):* credit as "Simeon Armenchev (monyarm)", with the repository URL once it's public. The repository stays private until the decompilation is finished, and he may publish AI-written docs instead of the code. License and what may be quoted are still open.

For Jeff:

19. Past the capped trial, does this project commit agent capacity to finishing Case File #1 with the host, as he proposes? The trial's cost per match on the remaining, larger functions is the input to that decision. *Deferred (Jeff, 2026-11-13):* decide after the trial. Until then the host finishes Case File #1 at his own pace, and this project uses what it turns up.
20. Would the host take on Showdown (Gen 1) as the next decompdecomp project, ahead of Case File #2? Showdown is this project's primary target. *Answered (2026-11-14, Reported):* yes. Once Case File #1 is finished, Showdown comes next, before the rest. He questions the VC5 reading of the toolchain: he finds Case File #1 is mostly VC6, and will see when Showdown is imported. He was right: the VC5 reading was a tool mislabel, corrected the same day (see the 2026-11-14 decision-log rows). *Updated 2026-11-15 (Reported):* he'll start on the Gen 1 games "soon", not after Case File #1 is finished ([§Reply on the compiler build](#reply-on-the-compiler-build-2026-11-15)).

## Immediate next actions

Milestones:

- [x] Collaboration repository received (private; access accepted 2026-11-11).
- [x] Case File #1 cooperative decompdecomp session available (2026-11-11). The link is temporary; get the current one from Mony.
- [ ] Inspect the repository and set up a local decompdecomp environment. The repository is inspected ([§First look](#first-look-at-the-repository-2026-11-11)); decompdecomp `v1.0.10-alpha.1` and its Visual C++ 6.0, 7.0 and 7.1 compilers are installed (2026-11-11); its Ghidra 12.1.4 is installed on the Windows JDK route (2026-11-13); the agent provider and the baseline build are next. Follow [Setting Up decompdecomp on Windows](../reference/decompdecomp-setup.md).
- [ ] Join the cooperative session and run a limited initial agent trial.
- [ ] Compare decompilation findings against existing `scooby-engine` research.

Trial checklist. Tick these off in this file as they happen.

- [x] Receive repository access and a room link from Mony, by private channel only.
- [ ] Review the private repository's terms and contents; record the terms in the decision log. Contents reviewed 2026-11-11; terms not yet received ([open question 18](#open-questions)).
- [ ] Read the current decompdecomp cooperative setup instructions and check them against [§Cooperative connection workflow](#cooperative-connection-workflow); correct this page where they differ.
- [ ] Install the prerequisites in an isolated environment (separate profile or VM, project directory outside this checkout or under `tools/decomp/`).
- [ ] Use only a legally obtained local copy of the game.
- [ ] Record the exact executable filename (`Case File #1.exe` on disc), size, version-resource information, and SHA-256 (plus SHA-1 and MD5 if the room uses them). Confirm SHA-256 against the WP-007 lock and against the host's copy. Size and SHA-1 match the host project's pinned copy (2026-11-11); version-resource information is still to record.
- [ ] Confirm that `git status` shows no executable, asset, project folder or credential before every commit.
- [ ] Match tool versions with the host: decompdecomp version, compiler and flags, Ghidra version. Ours: decompdecomp `v1.0.10-alpha.2` (updated from `alpha.1` 2026-11-16), Visual C++ 6.0/7.1, Ghidra 12.1.4 on Oracle JDK 27.0.1. The host's (2026-11-14, Reported): the same decompdecomp release, with the compilers and Ghidra it supplies ([§Tool versions](#tool-versions-from-the-collaborator-2026-11-14)). decompdecomp's `6.0` is VC6 RTM 8168 (Observed 2026-11-14); the host is choosing a closer build for the project default. `v1.0.10-alpha.2` is out; he's moving to it, and ours is updated. Still open: the version at the time of each trial session, since both sides update.
- [ ] Build one of the host's pushed commits locally and measure how many of its C functions match. This turns the Reported progress into a local measurement. Since 2026-11-13 it isn't a step before joining: the room credits our matches by member name ([§Reply from the collaborator](#reply-from-the-collaborator-2026-11-13)).
- [ ] Connect to the cooperative room.
- [ ] Run a limited trial, not open-ended agent use: set the provider spend cap, the helper count and a function cap first (suggested: 2 helpers, 100 functions or a fixed dollar cap Jeff sets, whichever comes first).
- [ ] Measure and record: functions attempted, byte-identical matches (the room's count credited to our member name), near misses, failures, agent cost from the provider's billing, wall time, and the compiler used for the matches.
- [ ] Compare reconstructed functions against existing format research, starting with [mmfw-container](../formats/mmfw-container.md).
- [ ] Steer toward the priority subsystems: file I/O, archive loading, graphics, audio, scripting, object initialization.
- [ ] Document meaningful discoveries in the wiki, following [§Output specification](#output-specification).
- [ ] Start a durable function-name and subsystem map for Case File #1.
- [ ] Compare Case File #1 against Jinx once Case File #1 has a stable baseline ([§Cross-game reuse strategy](#cross-game-reuse-strategy)). (A Case File #2 comparison was dropped 2026-11-13: different engine, per WP-005.)
- [ ] Decide which findings become ScummVM implementation tasks, as rows for the Phase 2–4 WPs in [WORK_INDEX](WORK_INDEX.md).
- [ ] Take the decision below to Accepted or Rejected.

## Output specification

Findings land in [`docs/formats/scooby-exe.md`](../formats/scooby-exe.md) under a new Findings subsection, **Function map — Case File #1 (Gen 3, WP-011)**, created when the first Observed finding exists:

| Address | Size | Proposed name | Subsystem | Evidence | Provenance | Notes |
|---|---|---|---|---|---|---|
| `0x00XXXXXX` | bytes | `MmfwArchive_Open` | Archive I/O | Observed | Ghidra 11.x local, 2026-MM-DD | Reads the 16-byte `MMFW` tag, then … |

Plus a **trial metrics** table: attempted, matched, near miss, failed, cost, wall time, compiler, decompdecomp version. Reported and locally measured values go in separate columns.

## Exit criteria

1. Cooperative access has been obtained, or confirmed unavailable, and recorded in the decision log without URLs or credentials.
2. The local Case File #1 executable's SHA-256 matches the WP-007 lock, and identity with the host's copy has been confirmed.
3. Tool versions (decompdecomp, compiler and flags, Ghidra, agent and provider) are recorded.
4. One capped trial has run, and its metrics table is filled in `scooby-exe.md`.
5. At least one function in research-target priorities 1–4 is in the function map at Observed or above.
6. Every collaborator figure quoted anywhere in the repo is either labeled Reported or backed by a local measurement.
7. The decision below is Accepted or Rejected, with the trial metrics as its rationale.

## Deliverables

- Committed: this WP; updates to `docs/formats/scooby-exe.md` (function map, trial metrics); backlinks from the format specs; the [WORK_INDEX](WORK_INDEX.md) row; `.gitignore` entries.
- Gitignored or kept elsewhere: the executable (`tools/exes/casefile1/`), the decompdecomp project and any exports (`tools/decomp/` or outside the checkout), matched C, generated assembly, room links, credentials.

## Status and decision log

| Date | Entry |
|---|---|
| 2026-11-11 | WP authored. The collaborator reported early decompdecomp progress on Case File #1 (all figures **Reported**). Cooperative access not yet received → ⏸ Blocked. |
| 2026-11-11 | **Decision (Proposed):** see below. |
| 2026-11-11 | Repository access received: the collaborator's private repo, invite accepted and cloned outside this checkout. A Case File #1 cooperative room is open; its link is temporary and is not recorded. ⏸ Blocked → 🚧 In Progress. |
| 2026-11-11 | **Decision (Jeff):** credit the collaborator on these pages by name and GitHub handle, and link his repository (it returns 404 without access). *Superseded 2026-11-14 by his own preference; see below.* His email stays out, because this repository and its Pages site are public. Room links and credentials stay out too. |
| 2026-11-11 | First look at the repository: executable identity confirmed by SHA-1 and size (**Observed**); the project defaults to VC 6.0; the match rate is not measured yet. See [§First look](#first-look-at-the-repository-2026-11-11). |
| 2026-11-11 | Local environment, part 1: decompdecomp `v1.0.10-alpha.1` installed; Visual C++ 6.0, 7.0 and 7.1 installed from its **Compilers & tools** screen into `%LOCALAPPDATA%\decompnet\toolchains\msvc` (**Observed**). The GUIDE's Setup screen isn't in this version; the [setup page](../reference/decompdecomp-setup.md#2-install-the-visual-c-60-compiler) is corrected. |
| 2026-11-11 | decompdecomp's own Ghidra install stopped: with no JDK on the PATH it installs its pinned Temurin 21, which on Windows is a Linux build that needs WSL 2, and this machine has no WSL distribution (**Observed**). Its source (`toolchains.py`, `forks/ghidra.py`) shows that a Windows JDK 21+ on the PATH, with `javac` beside `java`, is used instead, so no WSL is needed. Its docs say none of this. The GUIDE marks Ghidra optional for x86 (it writes agents' drafts). Route being tried: a Windows JDK. [Setup page step 3](../reference/decompdecomp-setup.md#ghidra-inside-decompdecomp-install-a-windows-jdk-first) is updated. |
| 2026-11-12 | Collaborator update: 21.7 % of the code matched, 1,981 functions (**Reported**). See [§Update from the collaborator](#update-from-the-collaborator-2026-11-12). |
| 2026-11-13 | Collaborator reply (**Reported**): 28.2 %, 2,078 functions; no pinned baseline commit; we treat his repository as read-only; he proposes finishing Case File #1 fully ([open question 19](#open-questions)); credit by username and GitHub handle. From decompdecomp's source: the room credits each match to `<member>.<agent>`, so the trial is measured from the room's credits, not by diffing commits. The local build is no longer a step before joining. The Windows JDK install is waiting on IT approval. See [§Reply from the collaborator](#reply-from-the-collaborator-2026-11-13). |
| 2026-11-13 | **Decision (Jeff):** the ScummVM engine stays the deliverable, and decompdecomp stays a research input to it, not a replacement. Matched C rebuilds the original Win32 program and never goes into `engines/scooby/` ([§ScummVM integration boundaries](#scummvm-integration-boundaries)). Case File #1 is a Stretch title (Gen 3), so its decompilation can't answer the Gen 1 blockers. This WP stays a capped trial. Committing agent spend to finishing Case File #1 waits for the trial's cost per match ([open question 19](#open-questions)); the host finishing it at his own pace costs this project nothing. Ask the host about a Showdown project next ([open question 20](#open-questions), [§Cross-game reuse strategy](#cross-game-reuse-strategy)). |
| 2026-11-14 | Collaborator reply (**Reported**). **Credit:** he asked to be credited as "Simeon Armenchev (monyarm)" and for the private repository link to come off these pages; both are done. **Showdown:** next after Case File #1, before the other games ([open question 20](#open-questions)). **Helpers:** all a helper needs is their own copy of the executables and a working decompdecomp, Ghidra and MSVC setup; decompdecomp handles the rest, and more helpers are welcome. **Room:** the link changed after a crash; links aren't recorded. **Toolchain:** he questions the VC5 reading. A check against [richprint](https://github.com/dishather/richprint)'s product-ID database suggested he was right; confirmed the same day (next row). **Future scope:** he proposes looking, after the Scooby-Doo engines are done, for other games on the same engine. |
| 2026-11-14 | **Correction (Observed): the toolchain is Visual C++ 6.0, not 5.0; the collaborator was right.** `tools/rich_header.py` mislabelled Rich Header product IDs: 0x000A (`Utc12_C`, the VC6 C compiler) as "Linker 5.10", 0x000B (`Utc12_CPP`, VC6 C++) as "MASM 6.13", 0x000E (MASM 6.13) as "Cvtomf 5.10", and 0x0013 (`Linker512` import records) as "MSVC 5.0 C++". Checked against three sources: Microsoft's `prodid` enum names (as tabulated in [kirschju/richheader](https://github.com/kirschju/richheader) `prodids.py`), [richprint](https://github.com/dishather/richprint)'s `comp_id.txt`, and the PE optional header, which says linker **6.00** in all five binaries. The script is fixed and rerun on Showdown, Phantom, Jinx and both Case Files. Case File #1's own C++ is the VC6 Processor Pack, build 8943. **Consequences:** byte-identical matching with decompdecomp's VC 6.0 is plausible, with the service-pack level still to check ([open question 7](#open-questions)); the build-number grouping across generations holds; the claim that IBS shipped Jinx's compiled `.obj` files does not (Case File #1 recompiled the `MM*` C++, and only 36 C objects keep Jinx's build). Corrected in [scooby-exe §Toolchain](../formats/scooby-exe.md#toolchain), the VISION lineage table, WP-005, WP-006, EC-001 and this WP. |
| 2026-11-14 | **Finding (Observed): the Showdown exe is a 2001 patch build.** The cached Showdown disc is TLC's August 2001 re-pressing; its `Scooby.exe` is `Gold v1.19`, built 2001-08-23, ten months after the game first shipped. For the Showdown decompdecomp project this is the build in hand; the 2000 release exe and its compiler are unknown. Evidence: [scooby-exe §Gen 1 discs are 2001 reissues](../formats/scooby-exe.md#gen-1-discs-are-2001-reissues-2026-11-14). |
| 2026-11-14 | **Ghidra inside decompdecomp installed on the Windows JDK route (Observed).** With Oracle JDK 27.0.1 on the PATH (`javac` beside `java`, installed 2026-11-13), decompdecomp's **Install** on the Ghidra card fetched only NSA's `ghidra_12.1.4_PUBLIC_20260921.zip` into `%LOCALAPPDATA%\decompnet\toolchains\ghidra` (2026-11-13). Its toolchain manifest records `"wsl": false`; no Temurin or other JDK was downloaded; and `wsl --list --verbose` still reports no installed distribution, although WSL 3.0.5 itself is present. This confirms the 2026-11-11 reading of its source: a Windows JDK 21+ avoids WSL entirely. JDK 27 is newer than the LTS releases the [setup page](../reference/decompdecomp-setup.md#3-install-java) suggests, and works. |
| 2026-11-14 | Collaborator reply on tool versions (**Reported**): the same decompdecomp release as ours (`v1.0.10-alpha.1`), updated to each new release; the compilers and Ghidra decompdecomp supplies; decompdecomp's detected flags, varied per function; about 6 or 7 functions detected as 7.x; mostly DeepSeek and Claude, one instance each for now. His VC6 service pack is still to check ([open question 7](#open-questions)). Open question 17 answered. A current room link came with the reply; links aren't recorded. See [§Tool versions from the collaborator](#tool-versions-from-the-collaborator-2026-11-14). |
| 2026-11-14 | Collaborator emails (**Reported**): 30.5 %, 2,086 of 3,371 functions; scripts that permute near matches past decompdecomp's bounded pass, through its internal HTTP API; `libexpat.dll` comes out of the project because it is open-source Expat; he'll move to the next decompdecomp release; and the game's compiler is a build between 6 and 7, which he's testing for the project default. **Observed the same day:** decompdecomp's `6.0` is VC6 RTM 8168, while Case File #1's C++ is Processor Pack 8943, which fits his finding; the DLL is Expat 1.95.3; decompdecomp `v1.0.10-alpha.2` is out (this PC runs `alpha.1`). [Open question 7](#open-questions) partly answered. See [§Progress, libexpat and the compiler build](#progress-libexpat-and-the-compiler-build-2026-11-14-to-11-15). |
| 2026-11-15 | Collaborator reply (**Reported**): he takes the Processor Pack reading and will give the agents decomp.me's compilers at the Rich Header's builds; 28.4 %, 1,765 of 2,760 functions with `libexpat.dll` removed, 995 left; one agent attempt matched 40 functions at once; out of AI usage for now. He'll start decompiling the Gen 1 games "soon", so their executables need comparing with the WP-007 locks first. The total fell by 611, more than libexpat's 313, which is to ask him about. See [§Reply on the compiler build](#reply-on-the-compiler-build-2026-11-15). |
| 2026-11-15 | **decomp.me's VC6 builds (Observed).** We downloaded `msvc6.4`, `msvc6.5` and `msvc6.5pp` outside this checkout and read their file versions. `msvc6.5` (SP5, `C2.DLL` 12.00.8966) matches Gen 1's C++ 8966. `msvc6.5pp` is SP5 with the Processor Pack's 13.00.9044 code generator, a later pack than Case File #1's 8943 (SP4). So the 2026-11-14 tip to Mony was close but not exact, and the correction goes to him. An x87-idiom scan finds Gen 1 and Jinx plain, and Case File #1 mixed. See [§decomp.me's VC6 builds](#decompmes-vc6-builds-2026-11-15). |
| 2026-11-15 | Collaborator emails (**Reported**). The 611-function drop is Expat plus a script that matches statically linked library code against the `.lib` files and sets it aside. `msvc6.5pp` is now the project default, and the rerun found 84 new matches in its first quarter ([open question 7](#open-questions)). Agents are in polish mode, adding types and names. He'll check the Gen 1 hashes when he gets there. His tools are public as [monyarm/outmatch](https://github.com/monyarm/outmatch) (**Observed**: Python, no license file, submits through decompdecomp's `POST /api/try`). See [§Library matching, the Processor Pack default and outmatch](#library-matching-the-processor-pack-default-and-outmatch-2026-11-15). |
| 2026-11-16 | Collaborator reply (**Reported**). The Processor Pack rerun added about 164 matches. Sweeps of other compiler builds and their libraries added none, and per-function compiler splits about a dozen ([open question 7](#open-questions)). He asks us to join the room with a strong model such as Claude Opus, not to run outmatch, since `/api/try` from a joined member may not work. Next for him: a few more Case File #1 tasks, then DeepSeek agents on polishing and matching while he starts Showdown and Phantom. This project expects that Gen 1 will reuse mostly runtime code from Case File #1, not engine code. See [§Compiler and library sweeps, and an invitation to join](#compiler-and-library-sweeps-and-an-invitation-to-join-2026-11-16). |
| 2026-11-16 | Collaborator note (**Reported**): give the agents a standing instruction to read outmatch's `skills/msvc-matching/references` folder, by full path, not the skill itself. He says it greatly improves the match rate. Added to the [setup page](../reference/decompdecomp-setup.md#give-the-agents-monys-matching-notes), with the `msvc6.5pp` default a member most likely needs too (Inferred; to confirm). |
| 2026-11-16 | **Agent setup on this PC (Observed).** decompdecomp updated to `v1.0.10-alpha.2`, the release the host is moving to. outmatch cloned at commit `89f1c45`, which made it MIT-licensed. The matching-notes line is added to **App instructions** (Agents & models → Agent prompts) as a global custom override, after decompdecomp's built-in text. Still to do before the trial: the agent provider and its cap, `msvc6.5pp` if the room needs it, and a current room link. |
| 2026-11-16 | Collaborator reply (**Reported**): room members need `msvc6.5pp` installed locally too. Matched functions passed **2,000** (of 2,760 after the set-asides). His agents run unattended overnight, and he'll start the Gen 1 decompilations within a day or two. A current room link came with the reply; links aren't recorded. **On this PC (Observed):** `msvc6.5pp` staged at `%USERPROFILE%\Decomp\compilers\msvc6.5pp` from the archive downloaded 2026-11-15 (`C2.DLL` 13.00.9044). decompdecomp's trial stops are set: **Budget** $25, app-priced (Jeff, 2026-11-16), and 8 functions per agent session. Next: add the compiler on the **Microsoft Visual C++ (your own copy)** card, then the agent provider and its own limit. The [setup page](../reference/decompdecomp-setup.md#2-install-the-visual-c-60-compiler) has the steps, and from decompdecomp's source it notes that a member's copy has to be the same build as the host's. |

| 2026-11-18 | Collaborator emails (**Reported**): Case File #1 at **37.5 %**, almost every function with some decomp; real function count ~1,600 after thunks and CRT; Phantom and Showdown both started (DeepSeek on Showdown, Claude on Case File #1), to land as branches of his decomp repo; Phantom at 38 %, pending batch twin-matching; a new outmatch command batch-matches twins across differing compilers. **Measured reuse:** the two Gen 1 games share 280 byte-identical functions; Gen 1 ↔ Case File #1 share 170. He asks Jeff which other games to decomp and whether the output is useful. Links not recorded. See [§Progress across the games](#progress-across-the-games-twin-matching-and-reuse-counts-2026-11-18). |

| 2026-11-19 | Collaborator email (**Reported**), cross-checked against his pushed branches (**Observed**, fetched read-only to `C:\dev\scooby-tlr-decomp` 2026-11-19). "I added sphinx" = he added **Jinx at the Sphinx** (Gen 2) as a new decomp target — branch `jinx-at-the-sphinx`, first commit 2026-11-19 — the game [§Cross-game reuse strategy](#cross-game-reuse-strategy) step 2 named next, not an AI agent. Agents advanced Showdown overnight (`showdown-at-ghost-town`, from 2026-11-18). All four in-scope binaries now have a branch. He's out of Claude/opencode usage for a few days and asks this project's Claude to read the functions for minigame logic and file formats; match rates not yet measured locally. His 2026-11-18 questions remain Jeff's; a reply is drafted 2026-11-19. See [§Jinx added, overnight Showdown progress](#jinx-added-overnight-showdown-progress-2026-11-19). |

| 2026-11-19 | Collaborator reply (**Reported**): the `SM*`-on-Showdown names were a twin-matcher name-leak bug, now fixed, though some leaked through before the fix (confirms the 2026-11-19 name caution); and when his usage resets he'll point an agent at the matched/partial functions to try to resolve the `0x10` and `+0x88` fields (accepts the one ask). Two questions for Jeff: plans for Case File #2/#3, and other games on this engine (he cites the Powerpuff game). Documented position for the reply: #2 is the Trinket/OM++ framework and #3 is Macromedia Director — both out of scope, and the Powerpuff demo rides #2's engine, not the TerraGlyph engine; the in-scope TerraGlyph set is Showdown, Phantom, Jinx, Activity Challenge and Case File #1. Questions remain Jeff's; a reply is drafted. See [§Reply: name leak fixed, scope questions for Jeff](#reply-name-leak-fixed-scope-questions-for-jeff-2026-11-19). |
| 2026-11-19 | **Finding (Observed): Disney's 102 Dalmatians: Activity Center (2000) runs the TerraGlyph Gen 1 engine** — the first confirmed non-Scooby binary on it. Downloaded the Internet Archive disc image (`102_Dalmatians.img`, SHA-1 `a84fe50e…2370`, verified); a raw scan finds `TGIFILE.ART` present and no Trinket/Director/Crystal markers. Confirms the catalog lead from the previous row (was unverified). The *Puppies to the Rescue* disc (`flt-102d`) is a different engine (Crystal/Eidos) and ruled out. Byte-format identity and a full engine-family check remain open; also a candidate decomp target for Mony. See [§Reply: name leak fixed, scope questions for Jeff](#reply-name-leak-fixed-scope-questions-for-jeff-2026-11-19). |

| 2026-11-20 | Collaborator reply (**Reported**): Activity Center + Activity Challenge are good later decomp targets, or at minimum document them as engine-sharing; he'll give some older TerraGlyph console/CD-ROM titles a once-over for shared lineage; Case File #3 (Director) is already partly supported in ScummVM, so it'd be the next target before Case File #2 if the other Scooby games are ever done; and he suggests a generic engine name — "Maybe TerraGlyph?", which is already this project's convention ([VISION](../01-VISION.md)). Reconfirms he'll target the `0x10`/`+0x88` loader fields once usage resets (Claude Tue, opencode +2 days). No new question for Jeff; reply drafted. See [§Reply: targets, naming and the Director path](#reply-targets-naming-and-the-director-path-2026-11-20). *Partly superseded 2026-11-21: the "Case File #3 (Director), supported in ScummVM, next before #2" point is void — #3 is Flash, not Director (verified), and ScummVM has no Flash engine; see the 2026-11-21 correction row.* |

| 2026-11-20 | Collaborator catalog once-over (**Reported**): two more non-Scooby `TGIFILE.ART` titles — **Clue Jr.: SpyGlass Mysteries** (on GOG; uses DirectX) and **The Little Mermaid II: Return to the Sea** — bringing the non-Scooby Gen-1 set to three with Activity Center (the two new ones Reported, not yet reproduced here). The 1995–96 DOS titles (Hansel & Gretel, Buster and the Beanstalk) use WinG and carry `TGI_ENGINE` / `TGI_QA` signature strings — likely a *separate, earlier* TerraGlyph engine sharing the studio's "TGI" prefix, not the `TGIFILE.ART` ancestor the 2026-11-19 note guessed; they share an engine with each other. PS1 Great Beanstalk likely bespoke; Classic Creep Capers (3D), Toonenstein, Blue's Big Musical, Kidsongs, Rumpelstiltskin ruled out by him. Sources: PCGamingWiki, LaunchBox gamesdb (dev 487). Scope unchanged (five in-scope binaries); the two new Gen-1 titles are candidate targets / lineage data, local verification open. See [§Catalog once-over](#catalog-once-over-two-more-tgifileart-titles-and-a-dos-tgi-signature-2026-11-20). |
| 2026-11-20 | **Finding (Observed): Clue Jr.: SpyGlass Mysteries (1999) and The Little Mermaid II: Return to the Sea (2000) both run the TerraGlyph Gen 1 engine** — confirming Mony's catalog leads. Downloaded Internet Archive images (`CLUEJR.iso`, SHA-1 `6255baef…`, verified; `MERMAID2.iso` RUS, SHA-1 `368c5c38…`, verified). Clue Jr. carries a loose `TGIFILE.ART` and is DirectX-based (corroborating Mony's note); Little Mermaid II's InstallShield `data1.cab` file table lists `tgifile.art` + `lmii.exe` / `lm2.exe`. No competing-engine markers on either. Non-Scooby Gen-1 set now three with Activity Center; Clue Jr. (1999) is the earliest confirmed Gen-1 binary, predating Showdown. Byte-format / engine-family checks remain open. See [§Verified: Clue Jr. and Little Mermaid II](#verified-clue-jr-and-little-mermaid-ii-confirmed-on-the-engine-2026-11-20). |
| 2026-11-20 | Collaborator note (**Reported**): he owns **Norwegian retail copies of Showdown and Case File #2**, and proposes that after the in-scope games work, we collect localized releases, add each to the ScummVM detection tables, and verify each boots. The **Norwegian Showdown isn't on abandonware sites**, so his disc may be the only source for that entry's hashes. Standard detection practice, not scope creep; Showdown's localization is the directly useful one (in scope), Case File #2's is a preservation note (Trinket / OM++, out of scope). Parked as a post-engine follow-up. See [§Localized releases](#localized-releases-norwegian-showdown-and-case-file-2-for-the-detection-tables-2026-11-20). |
| 2026-11-21 | **MobyGames dev catalog reconciled (Observed, via Wayback — live site is Cloudflare bot-walled).** Two TerraGlyph entities: **L.P.** (Schaumburg IL, game dev, 11 games 1995–2001) and **Productions Limited** (Dublin IE, animation arm, 4 of the same for art). All 11 L.P. titles already in our map/Mony's once-over — **no new titles**. Key finding: **neither page credits Clue Jr. or Little Mermaid II**, both of which we verified ship `TGIFILE.ART` (2026-11-20) — so MobyGames **undercounts the engine footprint**; a TerraGlyph credit isn't the engine boundary, and binary evidence outranks it (validates Mony's PCGW/LaunchBox route). No Case File titles (both stop at 2001) — consistent with the 2002+ IBS handoff. Studio shipped DOS/Win/Mac/PS1/N64 across multiple engines → reinforces studio-level "TerraGlyph" naming. Scope unchanged. See [§MobyGames dev catalog reconciled](#mobygames-dev-catalog-reconciled-11-titles-two-entities-what-it-misses-2026-11-21). |
| 2026-11-21 | **Correction (Observed): Case File #3 is Macromedia *Flash*, not Director** — reverses the 2026-06-03 "Confirmed Director" reading. Mony reported the engine is Flash (exe is a Flash player, data is `.swf`/mp3/wav/video, Ruffle runs it); verified against the disc on hand (`Scooby Doo! #3.iso`, SHA-1 `bc709817…b11`). The disc's single exe is a **TLC Windows installer** (version resource: "Scooby-Doo!(TM)", v4.1.07, The Learning Company — not an engine binary); the packed payload raw-scans to **456 `.swf` + 6 `.flv`** and 92 `FWS`/`CWS` SWF headers with **zero** Director markers. The 2026-06-03 reading misread the installer's metadata (Macromedia shipped both Director and Flash). Corrected in [VISION](../01-VISION.md) (5 places), [tools/exes/README](../../tools/exes/README.md), [WP-012](WP-012-detection-table.md) and this WP. **Out-of-scope conclusion unchanged** — but #3 is now out of scope *permanently* (ScummVM has no Flash engine; Ruffle already plays it), which voids the 2026-11-20 "#3 before #2" sequencing. See [§Correction: Case File #3 is Macromedia Flash](#correction-case-file-3-is-macromedia-flash-not-director-2026-11-21). |
| 2026-11-21 | Collaborator email (**Reported**) + catalog grounding (**Observed, via Wayback**). Mony finds the Gen-2/3 **`MM*`** archive family on ImageBuilder's own pre-Scooby titles (anchor: *Arthur's Thinking Games*, 1999, via SteamDB), so `MMFW` may be **ImageBuilder's house format**, not a TerraGlyph reformat — either the Gen-2 games mix the two studios' tech or ImageBuilder brought its format when it took the engine over. MobyGames (Moby ID 3355) **credits ImageBuilder as a developer on both MMFW Scooby games — Jinx (Gen 2) and Case File #1 (Gen 3)** — while Gen 1 (`TGIFILE.ART`) is TerraGlyph-only, corroborating the hypothesis at the credit level. His other `MM*` candidates (Lion King II: Simba's Pride – Active Play 1998, Carmen Sandiego: Treasures of Knowledge 2001, Furby: Big Fun in Furbyland 2000) are all confirmed ImageBuilder titles. **Batman: Justice Unbalanced** = Case File #2's Trinket / OM++ engine (Reported) — another non-Scooby title on the *excluded* engine. He proposes an automated catalog-wide engine-fingerprint sweep (agent + MobyGames / Internet Archive + `7z`/`bchunk`/`mdf2iso`/`cabextract`/`unshield`). Extension-match ≠ `MMFW` magic: every ImageBuilder format claim stays **Reported** pending a disc scan; a VISION provenance refinement is parked until then. Scope unchanged. Reply drafted. See [§ImageBuilder's MM* format may predate Gen 2](#imagebuilders-mm-format-may-predate-gen-2-a-catalog-sweep-proposal-2026-11-21). |
| 2026-11-22 | Collaborator email (**Reported**) — three threads, all already actionable. (1) **Decode review of `TGIFILE.ART` scene-block / placement**: close field `+0x10` not read at runtime, `+0x88` opaque (reloc routine `0x43B940` is `ret 4`), `+0xB0`/`+0xB8` tables never populated (148-byte layout; room loader `0x43B080`, walker `0x435DC0`; branch `showdown-at-ghost-town`). **Already integrated** into [tgifile-art.md](../formats/tgifile-art.md) (cites M. Armenchev 2026-11-22). (2) **List the TGIFILE.ART games in Target Games** — already satisfied ([VISION](../01-VISION.md)). (3) **Rename `scooby` → `terraglyph`** — a WIP engine already holds `scooby` upstream; verified (upstream PR [#8063](https://github.com/scummvm/scummvm/pull/8063) claims `scooby`; `terraglyph` free). **Decision taken by Jeff** — see [DECISIONS](../ai/DECISIONS.md#2026-11-22--engine-namespace-rename-scooby--terraglyph) and [§Reply](#reply-rename-to-terraglyph-decode-review-landed-2026-11-22). |
| 2026-11-23 | Collaborator thread follow-ons (**Reported**). (1) **Norwegian Showdown detection PR** — Mony opened fork PR [#8](https://github.com/barefootbetters/scummvm/pull/8) adding detection for the Norwegian retail Showdown (the localization flagged 2026-11-20 as absent from the abandonware sites; his disc is the only hash source). In scope (Showdown is the primary Gen-1 target); **next action: review/merge PR #8** (Jeff's call). (2) **Upstream-submission timing** — his counsel to hold the ScummVM-upstream pitch until the Gen-1 games run end-to-end and the code is cleaned up (one flat folder now); **agreed** — engine first, pitch parked. His AI-assisted-engine precedent survey is groundwork for that case. Reply finalized — see [§Reply](#reply-rename-to-terraglyph-decode-review-landed-2026-11-22). |
| 2026-11-23 | Norwegian detection **ported** + later collaborator note answered. (1) **Fork PR [#11](https://github.com/barefootbetters/scummvm/pull/11)** re-applies Mony's Norwegian Showdown entry onto `engines/terraglyph` (PR #8 was against the pre-rename `engines/scooby` path and couldn't merge); entry reviewed (`showdown` id, valid `Common::NB_NOR`, fields mirror English), Mony kept as commit author, builds clean. **Next: Jeff merges #11, #8 closed in favor of it** — or Mony re-pushes #8 and #11 drops (offered). Hashes Reported (his disc only), corroborated by detect-and-run (first-5000-byte MD5). (2) **Replies drafted-but-not-sent** — Mony's fair catch that the repo carried unsent reply drafts; corrected by actually sending the consolidated reply, not parking another draft. (3) **Cleanup/refactor PR offer accepted** — folder/ScummVM-style alignment welcome anytime; terraglyph-global vs per-game split's timing to be coordinated (engine work in flight). Reply consolidated and sent — see [§Reply](#reply-rename-to-terraglyph-decode-review-landed-2026-11-22). |
| 2026-11-24 | Consolidated reply **sent** by Jeff; collaborator **refactor plan** returned (**Reported**). Mony's plan: folder split now (`format/` `audio/` `graphics/` at root, `rooms/{game_name}` for single-game screens / shared in `rooms/`), **deeper splitting + dehardcoding deferred for discussion**; he keeps his (forthcoming refactor) PR synced to `scooby-engine` and awaits Jeff's merge-go; `detection_tables.h` reorg (boilerplate → `#define`s) after that; light comment trim now (many redundant / hex-narration / "clearly for the LLM"), full pass later. **Position: hold the reorg for a deliberate pause** — the fork has open PR [#9](https://github.com/barefootbetters/scummvm/pull/9) (WP-083) and an active room-by-room cadence, so a tree-wide `rooms/` move collides mid-wave; land it first on a quiet branch and rebase in-flight WPs onto it. Comments: **green-light** trimming hex/LLM-oriented ones as he goes. #8 can **close** (superseded by merged #11). Reply drafted — see [§Reply: refactor plan and merge timing](#reply-refactor-plan-and-merge-timing-2026-11-24). |

**Decision (Proposed, 2026-11-11): Evaluate decompdecomp as a complementary executable-analysis workflow for the Case File games, while keeping focused Ghidra analysis and the existing format-first research strategy.**

- **Rationale:** decompdecomp may speed up function reconstruction, cooperative processing, byte matching and cross-game comparison. Manual Ghidra analysis is still needed for subsystem identification, semantic interpretation, validation, and translation into maintainable ScummVM code.
- **Status:** Proposed. Access to the cooperative environment arrived 2026-11-11; the decision stays Proposed until a local trial establishes its usefulness, cost, reproducibility, and legal and repository boundaries.
- **Revisit:** at exit criterion 7.

## Notes

- **Hand-off to WP-005:** cross-binary identical-function counts (Jinx ↔ Case File #1) are function-level evidence for the lineage. WP-005 closed on 2026-11-13; these counts would strengthen its Case File #1 finding, not reopen it.
- **Hand-off to WP-001:** if Case File #1's `MMFW` loader or picture decoder turns out to be inherited code, its Gen 1 counterpart in Showdown is a concrete Ghidra target. Record any such lead in WP-001 §Background.
- **Generation discipline:** tag every finding Gen 3 unless it was reproduced on another binary.
- **Copyright posture:** same as [tools/samples/README](../../tools/samples/README.md) and [tools/exes/README](../../tools/exes/README.md). Facts, hashes, offsets and descriptions are committed; binaries and binary-derived bulk output are not.
- **Private notes:** contact details, detailed notes on the collaborator's repository, and the M0 → M0-R → M1 baseline plan live on the ewiki's **Private** section. That section is built from the private `barefootbetters/scooby-engine-private` repo and appears only behind Cloudflare Access, never in this repo or on GitHub Pages. Public pages don't link to it, because a build without that repo would fail on the broken link.
