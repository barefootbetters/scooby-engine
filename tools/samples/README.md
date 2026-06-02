# `tools/samples/` — extracted asset policy

This directory holds **decoded sample assets** produced by `tools/probe_*.py`
during Phase 1 format reverse engineering: PNGs of `TGIFILE.ART` entries,
extracted audio clips from `Music.dat` / `Sfx.dat` / `Voice.dat`, raw
palette dumps, and similar artifacts.

## Policy: nothing in here gets committed

The repository's `.gitignore` blocks all files in this directory except this
`README.md` and a `.gitkeep` placeholder.

### Why

Every artifact dropped here is **derived from copyrighted Warner Bros. /
Hanna-Barbera material**. A decoded background frame, even one used solely
to verify that a Python decoder works, is still a copy of a Scooby-Doo
asset. Committing it to a public GitHub repo would:

1. Distribute copyrighted material without authorization — DMCA exposure.
2. Undermine the project's legal posture (`docs/01-VISION.md` → "Legal
   Basis"), which depends on **never distributing game data**.
3. Risk the eventual ScummVM upstream PR. ScummVM's contribution
   guidelines explicitly require engines to ship without game data; a
   repo history full of decoded sprites is a red flag during review.

### What's allowed

- ✅ Local-only sample files in this directory for decoder verification
- ✅ Hex dumps and byte-pattern excerpts in `docs/formats/*.md` (small
  enough to qualify as fair use — typically the first 64 bytes of a header,
  not entire payloads)
- ✅ Algorithmic descriptions, pseudocode, opcode tables — these are
  **uncopyrightable facts** about the format, not the assets themselves

### What's not allowed

- ❌ Decoded image files committed anywhere in the repo
- ❌ Audio clip files committed anywhere in the repo
- ❌ Raw archive payloads committed anywhere in the repo
- ❌ The original `TGIFILE.ART`, `Music.dat`, `Scooby.exe`, etc. — these
  are also blocked by `.gitignore` as a safety net

## If you accidentally commit an asset

1. Do not `git push`.
2. `git rm --cached <file>` and amend (or `git reset` if it's the latest commit).
3. If it already pushed, force-push the corrected history within 24 hours
   and rotate any forks. Notify any cloners.

If a sample is critical to a doc (e.g. "here's what the decoded frame looks
like") — link to an external host instead. Don't commit.
