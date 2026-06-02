# `tools/exes/` — local executable cache

Local copies of `Scooby.exe` (and any other binaries) pulled from mounted
ISOs for analysis with `rich_header.py`, Ghidra, and other tools.

## Why this exists

Mounting and unmounting ISOs to compare binaries across titles is friction.
Copying the EXE out once per disc and keeping it locally means:

- Multi-file `rich_header.py` runs work without juggling drive letters
- Ghidra projects can point at a stable local path
- Disc unmount/re-mount doesn't break in-flight analysis

## Policy: nothing in here gets committed

The repository's `.gitignore` blocks all files in this directory except
this `README.md` and a `.gitkeep` placeholder. `Scooby.exe` and every
other binary here are copyrighted Warner Bros. / Hanna-Barbera material;
they live locally for analysis only.

## Conventional layout

```
tools/exes/
  showdown/Scooby.exe        ← from Scooby Doo Showdown in Ghost Town.iso
  phantom/Scooby.exe         ← from Scooby Doo Phantom of the Knight.iso
  jinx/Scooby.exe            ← from Scooby Doo Jinx at the Sphinx.iso
  casefile1/Scooby.exe       ← from Case File 1.iso
  casefile2/Scooby.exe       ← from Case File #2.iso
```

Per-disc subdirectory + canonical filename means:

- The `.gitignore` rule on `Scooby.exe` (already in place as a safety net)
  catches them even if `tools/exes/*` blocking is bypassed
- Wildcard runs like `tools/exes/*/Scooby.exe` work
- Each subdirectory can also hold the per-title `object.ini`, `Scooby.eng`,
  and any other files pulled from the disc for analysis

## Workflow

```powershell
# Once: create the subdirectories
$dest = "C:\www\scooby\tools\exes"
New-Item -ItemType Directory -Force `
    -Path "$dest\showdown","$dest\phantom","$dest\jinx","$dest\casefile1","$dest\casefile2" `
    | Out-Null

# Per disc: mount via Explorer → right-click → Mount, then:
Copy-Item "<drive>:\scooby\Scooby.exe" "$dest\<title>\Scooby.exe"
# Then right-click drive → Eject. Mount the next disc.
```

After all five are populated, the trio + case-files comparison is one
command — see `tools/rich_header.py` usage in the project README.
