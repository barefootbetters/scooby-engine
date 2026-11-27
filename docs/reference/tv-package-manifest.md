---
layout: default
title: "TV package manifest format"
---

# TV package manifest format

The test build of the studio's Google TV app ([WP-085](../work-packets/WP-085-tv-app-pipeline.md))
installs **authorized game-data packages** from a manifest: a JSON file fetched
over HTTPS that lists each package's id, version, size, SHA-256 and download
URL. This page is that format, and the rules the app enforces when it installs
a package.

The manifest and its packages are **data only**. The app never loads or runs
anything from a package. That's what Google Play's
[Device and Network Abuse policy](https://support.google.com/googleplay/android-developer/answer/16559646)
allows: game data interpreted by ScummVM's engines, never downloaded native code
or bytecode.

## Where it's used

Only in **test builds** (the debug build type), through a hidden advanced mode.
The release build, which is the one that goes to Google Play, compiles a stub
instead and contains none of this code ([WP-085 D4](../work-packets/WP-085-tv-app-pipeline.md#decisions-for-jeff)).

The advanced mode opens from ScummVM's library with a D-pad sequence: **up,
down, up, down, left, right, left, right** within ten seconds. A gamepad's
D-pad and a keyboard's arrow keys send it, and so does a TV remote. No key
follows itself in the sequence and a repeated key is ignored, because the TCL
65Q77K's remote reports each press twice. Other keys, such as a stray OK from
the remote's ring, don't break it. Entering it by hand on the TCL's remote
hasn't worked yet ([WP-085 §Result](../work-packets/WP-085-tv-app-pipeline.md#result)).
The mode asks for the manifest's URL; there's no built-in one.

## The format

```json
{
  "format": 1,
  "packages": [
    {
      "id": "bass-cd",
      "title": "Beneath a Steel Sky (CD, freeware)",
      "version": "1.2",
      "size": 69377781,
      "sha256": "53209b9400eab6fd7fa71518b2f357c8de75cfeaa5ba57024575ab79cc974593",
      "url": "https://github.com/barefootbetters/tv-test-packages/releases/download/packages-2026-11-26/bass-cd-1.2.zip"
    }
  ]
}
```

| Field | Required | Rule |
|---|---|---|
| `format` | yes | `1`. Any other value refuses the whole manifest |
| `packages` | yes | An array of package entries |
| `id` | yes | `[a-z0-9][a-z0-9._-]{0,63}`. Stable across versions: it's the package's folder name, and how an update finds the installed version |
| `title` | no | Shown in the list. Defaults to the id |
| `version` | yes | `[A-Za-z0-9][A-Za-z0-9._-]{0,31}`. Compared part by part, numerically where both parts are numbers (`1.2.1` is newer than `1.2`) |
| `size` | yes | The zip's exact size in bytes. A download larger than this is stopped; a different final size is refused |
| `sha256` | yes | The zip's SHA-256, 64 hex digits. A mismatch is refused |
| `url` | yes | Any **HTTPS** URL. The app holds no host: moving a package to another host is a manifest change, not an app change. A redirect may change host but not leave HTTPS |

An entry that breaks a rule is skipped and listed as skipped; the rest of the
manifest still loads. The manifest itself must be HTTPS and at most 1 MB.

## The package

A package is a **zip of game data**, laid out as the game's folder (or a folder
holding it). ScummVM detects the game anywhere inside it.

The app refuses the whole package, and keeps nothing from it, if any entry:

- ends in `.so`, `.dex`, `.jar`, `.apk`, `.odex`, `.oat` or `.vdex` (any case);
- is a file that starts with the ELF (`7F 45 4C 46`) or dex (`dex\n`) magic
  number, whatever its name;
- resolves, after `..` and the like, to a path outside the package's folder
  (zip-slip);
- would take the extracted total past 8 GB.

An empty zip is refused too.

## What the app does with it

1. **Download** to `files/packages/.staging/` in the app's private storage.
2. **Verify** the size and SHA-256 against the manifest. Refuse on any mismatch.
3. **Extract** to a staging folder under the rules above, then move it to
   `files/packages/<id>/<version>/`. That folder survives app updates (only
   `assets/` and `doc/` are re-synced on an update) and is deleted on uninstall.
4. **Add** it through ScummVM's own detection: the app restarts the ScummVM
   thread with `--add --path=<folder> --recursive --no-exit`, which adds what it
   detects and stays in the library.
5. **Update**: a newer `version` of an installed `id` is downloaded, verified and
   extracted beside the old one. Only then does the app point the game's
   library entry at the new folder and delete the old one. A failed or
   interrupted update leaves the old version in place and playable.
6. **Remove** deletes the package's folder and its library entries. Saves are
   kept: they belong to the library entry's name, so re-adding the game finds
   them.

ScummVM's `--add` skips a game whose usual target name (for example `sky`) is
already in the library. Remove an earlier entry for the same game before
installing it as a package.

## Hosting

Per [WP-085 D3](../work-packets/WP-085-tv-app-pipeline.md#decisions-for-jeff):
freely redistributable packages go on GitHub Releases in a dedicated repo,
[barefootbetters/tv-test-packages](https://github.com/barefootbetters/tv-test-packages),
which keeps game data out of the engine repos. Anything licensed is hosted
behind access control, not on a public release.
