<#
.SYNOPSIS
    Create an isolated git worktree of the scummvm fork for one WP, so two
    sessions can't collide in the single C:\dev\scummvm checkout.

.DESCRIPTION
    The fork checkout at C:\dev\scummvm is a SINGLE working copy with no
    per-session worktree. Two Claude sessions that both edit it clobber each
    other (the WP-075 collision, 2026-11-19). This script carves a dedicated
    worktree under C:\claude-worktrees\ on its own branch, forked from a freshly
    fetched origin/scooby-engine. Each worktree is a separate working directory
    on its own branch sharing one object store, so edits, builds and HEAD never
    cross between sessions.

    The branch name doubles as the claim: if the branch already exists locally
    or on origin, another session may hold this WP, and the script refuses
    BEFORE creating anything. Leave C:\dev\scummvm itself clean on scooby-engine
    as the base clone; never work in it directly.

.PARAMETER Branch
    Feature branch for this WP, e.g. 'wp-077-crypt' or 'claude/wp-077'. Created
    fresh off origin/<Base>. Required.

.PARAMETER Base
    Base branch the worktree forks from (default: 'scooby-engine' — the fork's
    integration branch, not 'main'). The script forks from origin/<Base> after
    fetching, so the worktree starts level with the pushed fork.

.PARAMETER ForkPath
    The base scummvm clone (default: C:\dev\scummvm).

.PARAMETER WorktreeRoot
    Where worktrees live (default: C:\claude-worktrees, per the portfolio
    convention). The worktree dir is <WorktreeRoot>\scummvm-<branch-flattened>
    unless -Name overrides the leaf.

.PARAMETER Name
    Override the worktree directory leaf (default: scummvm-<branch-flattened>).
    The 'scummvm-' prefix keeps fork worktrees from colliding with other repos'
    worktrees in the flat C:\claude-worktrees\ (e.g. the docs-repo 'scooby-engine'
    worktree already there).

.PARAMETER Origin
    Fork remote name (default: 'origin').

.PARAMETER NoFetch
    Skip 'git fetch' (offline). The base ref and claim check then use whatever
    origin refs are already local.

.EXAMPLE
    .\New-ForkWorktree.ps1 -Branch wp-077-crypt
    # -> C:\claude-worktrees\scummvm-wp-077-crypt on branch wp-077-crypt,
    #    forked from a fresh origin/scooby-engine.

.EXAMPLE
    .\New-ForkWorktree.ps1 -Branch claude/wp-078 -Base scooby-engine
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [string]$Base         = "scooby-engine",
    [string]$ForkPath     = "C:\dev\scummvm",
    [string]$WorktreeRoot = "C:\claude-worktrees",
    [string]$Name         = "",
    [string]$Origin       = "origin",
    [switch]$NoFetch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg"    -ForegroundColor Green }
function Fail($msg)       { Write-Error $msg; exit 1 }

# Resolve fork path and confirm it's a git work tree.
if (-not (Test-Path $ForkPath)) { Fail "Fork path not found: $ForkPath" }
$ForkPath = (Resolve-Path $ForkPath).Path
git -C $ForkPath rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { Fail "Not a git repository: $ForkPath" }

# Worktree directory leaf.
if ($Name) {
    $leaf = $Name
} else {
    $flat = ($Branch -replace '[/\\]', '-') -replace '[^A-Za-z0-9._-]', '-'
    $leaf = "scummvm-$flat"
}
$dir = Join-Path $WorktreeRoot $leaf
if (Test-Path $dir) { Fail "Worktree directory already exists: $dir`n    (another session may hold this WP; pick a different -Branch/-Name or clean it up with Remove-ForkWorktree.ps1)" }

# Fetch so the base ref and the claim check are current.
if (-not $NoFetch) {
    Write-Step "Fetching $Origin..."
    git -C $ForkPath fetch $Origin --quiet
    if ($LASTEXITCODE -ne 0) { Fail "git fetch $Origin failed." }
    Write-Ok "Fetched."
}

# Claim guard: refuse if the branch already exists (local or remote).
git -C $ForkPath show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -eq 0) { Fail "Branch '$Branch' already exists LOCALLY in $ForkPath.`n    Another session may hold this WP. Coordinate, or pick a different -Branch." }
git -C $ForkPath show-ref --verify --quiet "refs/remotes/$Origin/$Branch"
if ($LASTEXITCODE -eq 0) { Fail "Branch '$Branch' already exists on $Origin.`n    Another session may hold this WP. Coordinate, or pick a different -Branch." }

# Resolve the base ref: prefer origin/<Base>, fall back to a local <Base>.
$baseRef = "$Origin/$Base"
git -C $ForkPath rev-parse --verify --quiet "$baseRef^{commit}" *> $null
if ($LASTEXITCODE -ne 0) {
    git -C $ForkPath rev-parse --verify --quiet "$Base^{commit}" *> $null
    if ($LASTEXITCODE -ne 0) { Fail "Base ref not found: neither '$Origin/$Base' nor local '$Base' resolve. Fetch, or pass -Base." }
    Write-Host "    WARNING: '$Origin/$Base' not found; forking from LOCAL '$Base'." -ForegroundColor Yellow
    $baseRef = $Base
}
$baseSha = (git -C $ForkPath rev-parse --short "$baseRef").Trim()

# Create the worktree + branch.
Write-Step "Adding worktree: $dir  (branch '$Branch' off $baseRef @ $baseSha)"
git -C $ForkPath worktree add -b $Branch $dir $baseRef
if ($LASTEXITCODE -ne 0) { Fail "git worktree add failed." }

Write-Host ""
Write-Ok "Worktree ready."
Write-Host "    Path:   $dir"                                   -ForegroundColor Green
Write-Host "    Branch: $Branch  (forked from $baseRef @ $baseSha)" -ForegroundColor Green
Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "    cd '$dir'"
Write-Host "    # build OUT OF TREE, in a dir of this worktree's own (don't reuse the base checkout's build):"
Write-Host "    #   mkdir build-terraglyph; cd build-terraglyph; ../configure --disable-all-engines --enable-engine=terraglyph && make -j"
Write-Host "    # when done (pushed / merged):"
Write-Host "    #   tools\Remove-ForkWorktree.ps1 -Branch $Branch -DeleteBranch"
