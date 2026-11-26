<#
.SYNOPSIS
    Build, package and publish a portable Windows release of the forked ScummVM
    with the Scooby (TerraGlyph) engine.

.DESCRIPTION
    One command for the whole release flow, the way Update-Fork.ps1 is one command
    for the fork sync. It:

        1. Creates a throwaway worktree of the scummvm fork at the chosen ref
           (default origin/scooby-engine), so the base checkout is untouched.
        2. Builds a TerraGlyph-only RELEASE binary (MSYS2 UCRT64). Fails on any
           warning in engines/terraglyph/.
        3. Runs `make install` to collect the runtime data files (themes, fonts,
           translations, ...).
        4. Assembles a flat, portable folder: scummvm.exe + its full recursive
           UCRT64 DLL closure (discovered with ldd, not hardcoded) + the data
           files + COPYING + a README.
        5. TESTS the portable build on a sanitized PATH (MSYS2 removed): it must
           run, must list the `terraglyph` engine, and — if you pass -DiscPath — must
           detect `terraglyph:showdown`. The script stops if any check fails; no
           untested binary is packaged.
        6. Zips it (top-level folder) and records the SHA-256.
        7. Creates the GitHub Release (a DRAFT by default; pass -Publish to make
           it public) with the zip attached and generated notes.
        8. Removes the worktree and staging dirs.

    Prerequisites: MSYS2 at C:\msys64 with the UCRT64 toolchain (g++, SDL2, make),
    and the GitHub CLI (`gh`) logged in. Run from anywhere.

.PARAMETER Version
    Release version label (default: today's date, yyyy-MM-dd). Drives the tag
    `scooby-preview-<Version>` and the artifact name
    `scummvm-scooby-preview-<Version>-win64`.

.PARAMETER ForkPath
    The base scummvm fork clone (default: C:\dev\scummvm).

.PARAMETER Ref
    Git ref to build (default: origin/scooby-engine). The script fetches first.

.PARAMETER TagTarget
    Branch the release tag points at (default: scooby-engine). Keep it equal to
    the branch in -Ref so the tagged source matches the binary.

.PARAMETER Repo
    GitHub repo for the release (default: barefootbetters/scummvm).

.PARAMETER DiscPath
    Optional path to a mounted Showdown disc (e.g. H:\scooby). If given, the test
    step also asserts detection of terraglyph:showdown.

.PARAMETER Jobs
    Parallel build jobs (default: logical CPU count).

.PARAMETER OutDir
    Where to put the staged folder and zip (default: C:\claude-worktrees).

.PARAMETER Publish
    Publish the release immediately. Default is a DRAFT you review and publish.

.PARAMETER BuildOnly
    Build, bundle, test and zip, but do not create any GitHub release.

.PARAMETER KeepWorktree
    Don't remove the build worktree afterward (for debugging a failed build).

.EXAMPLE
    pwsh -File .\Make-Release.ps1 -DiscPath H:\scooby
    # Build + test (with detection) + zip + create a DRAFT release for review.

.EXAMPLE
    pwsh -File .\Make-Release.ps1 -DiscPath H:\scooby -Publish
    # Same, but publish the release immediately.

.EXAMPLE
    pwsh -File .\Make-Release.ps1 -BuildOnly
    # Just produce and test the zip; no release.
#>
[CmdletBinding()]
param(
    [string]$Version   = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$ForkPath  = 'C:\dev\scummvm',
    [string]$Ref       = 'origin/scooby-engine',
    [string]$TagTarget = 'scooby-engine',
    [string]$Repo      = 'barefootbetters/scummvm',
    [string]$DiscPath,
    [int]   $Jobs      = [Environment]::ProcessorCount,
    [string]$OutDir    = 'C:\claude-worktrees',
    [switch]$Publish,
    [switch]$BuildOnly,
    [switch]$KeepWorktree
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "    $m"   -ForegroundColor Green }
function Write-Warn($m) { Write-Host "    WARNING: $m" -ForegroundColor Yellow }
function Fail($m)       { Write-Host "`nERROR: $m" -ForegroundColor Red; exit 1 }

function ConvertTo-Unix([string]$p) {
    # C:\dev\scummvm -> /c/dev/scummvm
    $d = $p.Substring(0,1).ToLower()
    '/' + $d + ($p.Substring(2) -replace '\\','/')
}

$msys2 = 'C:\msys64\usr\bin\bash.exe'
$name  = "scummvm-scooby-preview-$Version-win64"
$tag   = "scooby-preview-$Version"

# --- Preconditions -------------------------------------------------------------
if (-not (Test-Path $ForkPath))  { Fail "Fork path not found: $ForkPath" }
if (-not (Test-Path $msys2))     { Fail "MSYS2 bash not found at $msys2 (install MSYS2 + the UCRT64 toolchain)." }
if (-not $BuildOnly) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Fail "GitHub CLI (gh) not found. Install it or use -BuildOnly." }
}
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$env:MSYSTEM = 'UCRT64'
$wt        = Join-Path $OutDir "scummvm-release-build-$Version"
$instStage = Join-Path $OutDir "scummvm-release-install-$Version"
$relDir    = Join-Path $OutDir $name
$zipPath   = Join-Path $OutDir "$name.zip"

function Remove-Worktree {
    if (-not $KeepWorktree -and (Test-Path $wt)) {
        git -C $ForkPath worktree remove --force $wt 2>$null
    }
    if (Test-Path $instStage) { Remove-Item $instStage -Recurse -Force -ErrorAction SilentlyContinue }
}

try {
    # --- 1. Fresh worktree at the ref -----------------------------------------
    Write-Step "Fetching origin and creating a build worktree at $Ref..."
    git -C $ForkPath fetch origin --quiet
    if (Test-Path $wt) { git -C $ForkPath worktree remove --force $wt 2>$null; Remove-Item $wt -Recurse -Force -ErrorAction SilentlyContinue }
    git -C $ForkPath worktree add --detach $wt $Ref | Out-Null
    $buildCommit = (git -C $wt rev-parse --short HEAD).Trim()
    Write-Ok "Worktree at $wt (commit $buildCommit)."

    # --- 2. Release build ------------------------------------------------------
    Write-Step "Building TerraGlyph-only RELEASE binary (UCRT64, -j$Jobs)..."
    $wtUnix = ConvertTo-Unix $wt
    $buildCmd = "cd '$wtUnix' && rm -rf build-release && mkdir build-release && cd build-release && " +
                "../configure --disable-all-engines --enable-engine=terraglyph --enable-release --disable-debug > build.log 2>&1 && " +
                "make -j$Jobs >> build.log 2>&1"
    & $msys2 -lc $buildCmd
    if ($LASTEXITCODE -ne 0) {
        Fail "Build failed. See $wt\build-release\build.log"
    }
    $exe = Join-Path $wt 'build-release\scummvm.exe'
    if (-not (Test-Path $exe)) { Fail "Build reported success but scummvm.exe is missing." }
    $engWarn = Select-String -Path (Join-Path $wt 'build-release\build.log') -Pattern 'engines/terraglyph/.*(warning|error):' -ErrorAction SilentlyContinue
    if ($engWarn) {
        $engWarn | ForEach-Object { Write-Warn $_.Line }
        Fail "engines/terraglyph produced warnings/errors — not shipping. Fix them and re-run."
    }
    Write-Ok "Built clean (0 warnings in engines/terraglyph)."

    # --- 3. make install to collect data files --------------------------------
    Write-Step "Collecting runtime data files (make install)..."
    if (Test-Path $instStage) { Remove-Item $instStage -Recurse -Force }
    $instUnix = ConvertTo-Unix $instStage
    & $msys2 -lc "cd '$wtUnix/build-release' && make install DESTDIR='$instUnix' > install.log 2>&1"
    if ($LASTEXITCODE -ne 0) { Fail "make install failed. See $wt\build-release\install.log" }
    $share = Get-ChildItem -Path $instStage -Recurse -Directory -Filter 'scummvm' |
             Where-Object { $_.FullName -match 'share' } | Select-Object -First 1
    if (-not $share) { Fail "Could not locate installed share/scummvm data dir under $instStage." }
    Write-Ok "Data files staged from $($share.FullName)."

    # --- 4. Assemble the portable folder --------------------------------------
    Write-Step "Assembling portable folder..."
    if (Test-Path $relDir) { Remove-Item $relDir -Recurse -Force }
    New-Item -ItemType Directory -Path $relDir | Out-Null
    Copy-Item $exe $relDir

    # Full recursive UCRT64 DLL closure via ldd (robust to new deps).
    $exeUnix = ConvertTo-Unix $exe
    $lddScript = @"
declare -A seen
walk() {
  local f="`$1"
  while read -r _ _ path _; do
    case "`$path" in
      */ucrt64/bin/*)
        local b=`$(basename "`$path")
        if [ -z "`${seen[`$b]:-}" ]; then seen[`$b]=1; cygpath -w "`$path"; walk "`$path"; fi ;;
    esac
  done < <(ldd "`$f" 2>/dev/null)
}
walk "$exeUnix"
"@
    $dllWin = & $msys2 -lc $lddScript
    foreach ($d in $dllWin) {
        if ($d -and (Test-Path $d)) { Copy-Item $d $relDir; Write-Ok "bundled $(Split-Path $d -Leaf)" }
    }

    # Data files + license + authors
    Copy-Item (Join-Path $share.FullName '*') $relDir -Include *.zip,*.dat
    $copying = Join-Path $instStage 'usr\local\share\doc\scummvm\COPYING'
    if (Test-Path $copying) { Copy-Item $copying (Join-Path $relDir 'COPYING.txt') }
    $authors = Join-Path $wt 'AUTHORS'
    if (Test-Path $authors) { Copy-Item $authors $relDir }

    # README.txt
    $readme = @"
ScummVM - Scooby-Doo (TerraGlyph) engine - Windows preview ($Version)
=====================================================================

This is a build of ScummVM that includes the Scooby (TerraGlyph) engine,
which plays The Learning Company's Scooby-Doo! CD-ROM adventures.

Playable in this preview:
  - Scooby-Doo! Showdown in Ghost Town  (complete, testing status)
Phantom of the Knight is in development; other titles are detected only.

YOU SUPPLY THE GAME. This build contains NO game data. You need your own
original Scooby-Doo! disc (or a copy of its files).

How to run:
  1. Unzip this folder anywhere.
  2. Run scummvm.exe.
  3. Click "Add Game..." and choose your disc's \scooby\ folder (or disc root).
  4. Select Showdown and click Start.

This is a FORK of ScummVM, not the official release. Report issues at:
  https://github.com/barefootbetters/scummvm/issues

Full instructions:
  https://github.barefootbetters.com/terraglyph-engine/docs/reference/download-and-install/

ScummVM is licensed under the GNU GPL v3 (see COPYING.txt).
Scooby-Doo is a trademark of Warner Bros. Entertainment Inc. This project is
not affiliated with or endorsed by Warner Bros., The Learning Company, or the
ScummVM project.
"@
    Set-Content -Path (Join-Path $relDir 'README.txt') -Value $readme -Encoding utf8
    Write-Ok "Portable folder ready: $relDir"

    # --- 5. Test on a sanitized PATH (MSYS2 removed) --------------------------
    Write-Step "Testing the portable build on a clean PATH..."
    $testExe = Join-Path $relDir 'scummvm.exe'
    $cleanPath = "$env:SystemRoot\System32;$env:SystemRoot"
    $ver = & cmd /c "set `"PATH=$cleanPath`" && `"$testExe`" --version 2>&1"
    if ($LASTEXITCODE -ne 0 -or -not ($ver -match 'ScummVM')) {
        Fail "Portable build failed to run on a clean PATH (missing a bundled DLL?). Output:`n$ver"
    }
    $engines = & cmd /c "set `"PATH=$cleanPath`" && `"$testExe`" --list-engines 2>&1"
    if (-not ($engines -match 'terraglyph')) { Fail "The terraglyph engine is not in the build (--list-engines)." }
    Write-Ok "Runs on a clean PATH; terraglyph engine present."
    if ($DiscPath) {
        $detect = & cmd /c "set `"PATH=$cleanPath`" && `"$testExe`" --path=`"$DiscPath`" --detect 2>&1"
        if (-not ($detect -match 'terraglyph:showdown')) {
            Fail "Did not detect terraglyph:showdown at $DiscPath. Output:`n$detect"
        }
        Write-Ok "Detects terraglyph:showdown at $DiscPath."
    } else {
        Write-Warn "No -DiscPath given; skipped the detection check."
    }

    # --- 6. Zip + checksum -----------------------------------------------------
    Write-Step "Packaging zip..."
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Compress-Archive -Path $relDir -DestinationPath $zipPath -CompressionLevel Optimal
    $sha = (Get-FileHash $zipPath -Algorithm SHA256).Hash.ToLower()
    $sizeMB = '{0:N1}' -f ((Get-Item $zipPath).Length / 1MB)
    Write-Ok "$zipPath ($sizeMB MB)"
    Write-Ok "SHA-256 $sha"

    if ($BuildOnly) {
        Write-Step "-BuildOnly set: stopping before the GitHub release."
        Write-Ok "Tested zip ready at $zipPath"
        return
    }

    # --- 7. GitHub release -----------------------------------------------------
    Write-Step "Creating GitHub release $tag on $Repo ($(if($Publish){'PUBLISHED'}else{'DRAFT'}))..."
    $notes = @"
**ScummVM with the Scooby (TerraGlyph) engine - Windows preview.**

Plays *Scooby-Doo! Showdown in Ghost Town* start to finish (testing status). *Phantom of the Knight* is in development; the other titles are detected only.

**You supply the game.** This build contains **no** game data - bring your own original *Showdown* disc (or its files).

**Run it:** unzip anywhere, run ``scummvm.exe``, click **Add Game...** -> your disc's ``\scooby\`` folder (or disc root), select *Showdown*, **Start**. Portable/self-contained (SDL2 + runtime DLLs bundled), 64-bit Windows, no install needed.

- Full instructions: https://github.barefootbetters.com/terraglyph-engine/docs/reference/download-and-install/
- Why this is a fork: https://github.barefootbetters.com/terraglyph-engine/docs/reference/why-forked-scummvm/
- Report issues: https://github.com/barefootbetters/scummvm/issues

``$name.zip`` - SHA-256 ``$sha`` - built from ``$TagTarget`` @ ``$buildCommit``.

ScummVM is licensed under the GNU GPL v3. *Scooby-Doo* is a trademark of Warner Bros. Entertainment Inc.; this project is not affiliated with or endorsed by Warner Bros., The Learning Company, or the ScummVM project.
"@
    $notesFile = Join-Path $env:TEMP "scooby-release-notes-$Version.md"
    Set-Content -Path $notesFile -Value $notes -Encoding utf8
    $ghArgs = @('release','create',$tag,$zipPath,'--repo',$Repo,'--target',$TagTarget,
                '--title',"Scooby engine - Windows preview ($Version)",'--notes-file',$notesFile)
    if (-not $Publish) { $ghArgs += '--draft' }
    gh @ghArgs
    if ($LASTEXITCODE -ne 0) { Fail "gh release create failed." }
    Remove-Item $notesFile -ErrorAction SilentlyContinue

    Write-Host ""
    if ($Publish) {
        Write-Ok "Release $tag PUBLISHED on $Repo."
    } else {
        Write-Ok "DRAFT release $tag created on $Repo. Review it, then publish from the Releases page (or re-run with -Publish)."
    }
}
finally {
    Write-Step "Cleaning up..."
    Remove-Worktree
    if (-not $KeepWorktree) { Write-Ok "Worktree and install staging removed. Kept: $relDir and $zipPath" }
}
