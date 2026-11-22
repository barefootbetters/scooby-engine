<#
.SYNOPSIS
    Bring the scummvm fork's integration branch (scooby-engine) up to date with
    upstream scummvm/scummvm, verify the engine still compiles, then push.

.DESCRIPTION
    The scooby engine is fully self-contained in engines/scooby/ — it touches no
    shared ScummVM file (configure auto-discovers the engine from the directory).
    So bringing upstream's changes in is a plain MERGE of upstream/master into
    scooby-engine, which is conflict-free in practice. This script does that
    safely:

        1. Verifies the base checkout is clean and on the integration branch.
        2. Fetches upstream + origin; fast-forwards the branch to origin first.
        3. Merges upstream/<UpstreamBranch> into the branch.
             - If the merge hits conflicts, it ABORTS the merge and stops. The
               engine is self-contained, so a conflict means upstream changed
               something the engine *includes* from core — worth a human look.
        4. Smoke-builds Scooby-only (MSYS2 UCRT64) to confirm it still compiles
           against the new upstream. If the build fails, it ROLLS BACK the merge
           (git reset --hard to the pre-merge HEAD) and stops — nothing is pushed.
        5. Pushes the updated branch to origin.

    This replaces Sync-Fork.ps1 for this fork: that script rebases a feature
    branch onto 'main' and force-pushes, which rewrites scooby-engine's merged-PR
    history. A merge keeps the history intact and needs no force-push.

.PARAMETER ForkPath
    The base scummvm clone (default: C:\dev\scummvm). Run this against the base
    checkout, not a worktree.

.PARAMETER Branch
    The fork's integration branch to update (default: scooby-engine).

.PARAMETER UpstreamRemote
    Name of the upstream remote (default: upstream — github.com/scummvm/scummvm).

.PARAMETER OriginRemote
    Name of your fork's remote (default: origin).

.PARAMETER UpstreamBranch
    The upstream branch to merge from (default: master — ScummVM's primary branch).

.PARAMETER Jobs
    Parallel build jobs for the smoke build (default: number of logical CPUs).

.PARAMETER SkipBuild
    Skip the Scooby-only smoke build (merge + push only). Use only if MSYS2/UCRT64
    is unavailable; you then verify the build yourself before relying on the push.

.PARAMETER NoPush
    Do everything except the final push, so you can inspect the merged tree first.

.EXAMPLE
    .\Update-Fork.ps1
    # Fetch upstream, merge master into scooby-engine, smoke-build, push.

.EXAMPLE
    .\Update-Fork.ps1 -NoPush
    # Merge + build locally; review before pushing.
#>
[CmdletBinding()]
param(
    [string]$ForkPath       = "C:\dev\scummvm",
    [string]$Branch         = "scooby-engine",
    [string]$UpstreamRemote = "upstream",
    [string]$OriginRemote   = "origin",
    [string]$UpstreamBranch = "master",
    [int]   $Jobs           = [Environment]::ProcessorCount,
    [switch]$SkipBuild,
    [switch]$NoPush
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg"   -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    WARNING: $msg" -ForegroundColor Yellow }
function Fail($msg)       { Write-Host "`nERROR: $msg" -ForegroundColor Red; exit 1 }

# --- Resolve and enter the fork ------------------------------------------------
if (-not (Test-Path $ForkPath)) { Fail "Fork path not found: $ForkPath" }
Set-Location $ForkPath

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    Fail "Not a git repository: $ForkPath"
}

# Refuse to run inside a linked worktree — this operates on the base integration branch.
$gitDir = (git rev-parse --git-dir)
if ($gitDir -match "worktrees") {
    Fail "This looks like a linked worktree. Run against the base checkout ($ForkPath)."
}

# --- Preconditions -------------------------------------------------------------
$remotes = git remote
if ($remotes -notcontains $UpstreamRemote) {
    Fail "Remote '$UpstreamRemote' not found. Add it:`n  git remote add $UpstreamRemote https://github.com/scummvm/scummvm.git"
}
if ($remotes -notcontains $OriginRemote) {
    Fail "Remote '$OriginRemote' not found."
}

# A merge/rebase already in progress?
if ((Test-Path (Join-Path $gitDir "MERGE_HEAD")) -or (Test-Path (Join-Path $gitDir "rebase-merge")) -or (Test-Path (Join-Path $gitDir "rebase-apply"))) {
    Fail "A merge or rebase is already in progress here. Resolve or abort it first."
}

# Clean working tree?
if (git status --porcelain) {
    Fail "Working tree has uncommitted changes. Commit or stash before syncing (and make sure no other session is mid-work in this checkout)."
}

# --- Get on the branch, level with origin --------------------------------------
Write-Step "Checking out $Branch and fast-forwarding to $OriginRemote/$Branch..."
git fetch $OriginRemote --quiet
git checkout $Branch
git merge --ff-only "$OriginRemote/$Branch"
Write-Ok "$Branch is level with $OriginRemote/$Branch."

$preMerge = (git rev-parse HEAD)

# --- Fetch upstream and merge --------------------------------------------------
Write-Step "Fetching $UpstreamRemote..."
git fetch $UpstreamRemote --quiet
Write-Ok "Fetched $UpstreamRemote/$UpstreamBranch."

$behind = (git rev-list --count "HEAD..$UpstreamRemote/$UpstreamBranch")
if ($behind -eq "0") {
    Write-Ok "Already up to date with $UpstreamRemote/$UpstreamBranch. Nothing to merge."
    exit 0
}
Write-Step "Merging $UpstreamRemote/$UpstreamBranch into $Branch ($behind new upstream commits)..."

git merge --no-edit "$UpstreamRemote/$UpstreamBranch"
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Merge hit conflicts — aborting the merge (nothing changed, nothing pushed)."
    git merge --abort
    Fail "Conflicts merging $UpstreamRemote/$UpstreamBranch. The engine is self-contained, so this is unusual — inspect manually:`n  git merge $UpstreamRemote/$UpstreamBranch"
}
Write-Ok "Merged cleanly."

# --- Smoke build (Scooby-only) -------------------------------------------------
if ($SkipBuild) {
    Write-Warn "-SkipBuild set: NOT verifying the build. Verify it yourself before trusting this push."
} else {
    Write-Step "Smoke-building Scooby-only (MSYS2 UCRT64) to confirm it still compiles..."

    $msys2 = "C:\msys64\usr\bin\bash.exe"
    if (-not (Test-Path $msys2)) {
        git reset --hard $preMerge | Out-Null
        Fail "MSYS2 bash not found at $msys2. Merge rolled back. Re-run with -SkipBuild if you'll build another way."
    }

    # Windows path -> MSYS unix path (C:\dev\scummvm -> /c/dev/scummvm)
    $drive    = $ForkPath.Substring(0,1).ToLower()
    $rest     = ($ForkPath.Substring(2) -replace '\\','/')
    $forkUnix = "/$drive$rest"
    $buildDir = "build-fork-sync"

    $env:MSYSTEM = "UCRT64"
    $bashCmd = "cd '$forkUnix' && rm -rf '$buildDir' && mkdir '$buildDir' && cd '$buildDir' && ../configure --disable-all-engines --enable-engine=scooby > build.log 2>&1 && make -j$Jobs >> build.log 2>&1"
    & $msys2 -lc $bashCmd
    $buildExit = $LASTEXITCODE

    $buildLog = Join-Path $ForkPath "$buildDir\build.log"
    if ($buildExit -ne 0) {
        Write-Warn "Smoke build FAILED (see $buildLog). Rolling back the merge."
        git reset --hard $preMerge | Out-Null
        Fail "Build failed against $UpstreamRemote/$UpstreamBranch — merge rolled back, nothing pushed. Likely upstream API drift touching the engine; inspect build.log, fix engines/scooby, then re-run."
    }

    # Surface any engine warnings (upstream core warnings are expected; engine ones aren't).
    $engineWarn = Select-String -Path $buildLog -Pattern "engines/scooby/.*(warning|error):" -ErrorAction SilentlyContinue
    if ($engineWarn) {
        Write-Warn "Build succeeded but engines/scooby produced warnings:"
        $engineWarn | ForEach-Object { Write-Host "      $($_.Line)" -ForegroundColor Yellow }
    } else {
        Write-Ok "Build clean — 0 warnings in engines/scooby/."
    }
}

# --- Push ----------------------------------------------------------------------
if ($NoPush) {
    Write-Step "-NoPush set: stopping before push."
    Write-Ok  "Merged (and built) locally. Review, then: git push $OriginRemote $Branch"
    exit 0
}

Write-Step "Pushing $Branch to $OriginRemote..."
git push $OriginRemote $Branch
Write-Ok "Done. $OriginRemote/$Branch is updated to upstream $UpstreamBranch ($behind commits merged)."
Write-Host ""
Write-Ok "Tip: worktrees cut after this (New-ForkWorktree.ps1) start from the refreshed branch automatically."
