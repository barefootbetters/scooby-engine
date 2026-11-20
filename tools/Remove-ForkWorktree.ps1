<#
.SYNOPSIS
    Tear down a scummvm-fork worktree created by New-ForkWorktree.ps1, and
    optionally delete its branch.

.DESCRIPTION
    Removes the worktree directory, prunes the fork's worktree registry, and
    (with -DeleteBranch) deletes the local branch. Run it once a WP's branch is
    pushed and merged, so fork worktrees and stale local branches don't pile up
    in the single C:\dev\scummvm checkout.

.PARAMETER Branch
    The worktree's branch, e.g. 'wp-077-crypt'. Used to derive the directory
    (<WorktreeRoot>\scummvm-<branch-flattened>) when -Path isn't given, and it's
    the branch -DeleteBranch removes. Give -Branch, -Path, or -Name.

.PARAMETER Path
    The worktree directory to remove, when it isn't the derived default.

.PARAMETER Name
    The worktree directory leaf (default derivation: scummvm-<branch-flattened>).

.PARAMETER ForkPath
    The base scummvm clone the worktree belongs to (default: C:\dev\scummvm).

.PARAMETER WorktreeRoot
    Where worktrees live (default: C:\claude-worktrees).

.PARAMETER DeleteBranch
    Also delete the local branch after removing the worktree. Safe delete
    ('git branch -d') unless -Force (then 'git branch -D').

.PARAMETER Force
    Remove the worktree even with uncommitted changes ('git worktree remove
    --force'), and force the branch delete ('-D'). Destructive — only when you
    mean to discard that worktree's uncommitted work.

.EXAMPLE
    .\Remove-ForkWorktree.ps1 -Branch wp-077-crypt -DeleteBranch

.EXAMPLE
    .\Remove-ForkWorktree.ps1 -Path C:\claude-worktrees\scummvm-wp-077-crypt
#>
[CmdletBinding()]
param(
    [string]$Branch       = "",
    [string]$Path         = "",
    [string]$Name         = "",
    [string]$ForkPath     = "C:\dev\scummvm",
    [string]$WorktreeRoot = "C:\claude-worktrees",
    [switch]$DeleteBranch,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg"    -ForegroundColor Green }
function Fail($msg)       { Write-Error $msg; exit 1 }

if (-not $Branch -and -not $Path -and -not $Name) { Fail "Give -Branch, -Path, or -Name." }

if (-not (Test-Path $ForkPath)) { Fail "Fork path not found: $ForkPath" }
$ForkPath = (Resolve-Path $ForkPath).Path
git -C $ForkPath rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { Fail "Not a git repository: $ForkPath" }

# Resolve the worktree directory.
if ($Path) {
    $dir = $Path
} else {
    if ($Name) { $leaf = $Name }
    else {
        $flat = ($Branch -replace '[/\\]', '-') -replace '[^A-Za-z0-9._-]', '-'
        $leaf = "scummvm-$flat"
    }
    $dir = Join-Path $WorktreeRoot $leaf
}

# If we'll delete the branch but weren't told which, read it from the worktree.
if ($DeleteBranch -and -not $Branch -and (Test-Path $dir)) {
    $Branch = (git -C $dir rev-parse --abbrev-ref HEAD 2>$null)
    if ($Branch) { $Branch = $Branch.Trim() }
}

# Remove the worktree.
if (Test-Path $dir) {
    Write-Step "Removing worktree: $dir"
    if ($Force) { git -C $ForkPath worktree remove --force $dir }
    else        { git -C $ForkPath worktree remove $dir }
    if ($LASTEXITCODE -ne 0) { Fail "git worktree remove failed (uncommitted changes? re-run with -Force to discard them)." }
    Write-Ok "Removed."
} else {
    Write-Host "    Worktree directory not present: $dir (nothing to remove)" -ForegroundColor Yellow
}

Write-Step "Pruning worktree registry..."
git -C $ForkPath worktree prune
Write-Ok "Pruned."

# Delete the branch.
if ($DeleteBranch) {
    if (-not $Branch) { Fail "-DeleteBranch given but no branch resolved. Pass -Branch." }
    Write-Step "Deleting branch '$Branch'..."
    if ($Force) { git -C $ForkPath branch -D $Branch }
    else        { git -C $ForkPath branch -d $Branch }
    if ($LASTEXITCODE -ne 0) { Fail "git branch delete failed (branch not merged? re-run with -Force to force-delete)." }
    Write-Ok "Deleted."
}

Write-Host ""
Write-Ok "Done."
