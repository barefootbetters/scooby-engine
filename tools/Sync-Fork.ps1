<#
.SYNOPSIS
    Syncs a forked repo's main branch with upstream, then rebases a feature branch on top of it.

.PARAMETER FeatureBranch
    The branch you're actively working on (e.g. "scooby-port"). Defaults to current branch.

.PARAMETER MainBranch
    The primary branch to sync (default: "main").

.PARAMETER UpstreamRemote
    Name of the upstream remote (default: "upstream").

.PARAMETER OriginRemote
    Name of your fork's remote (default: "origin").

.EXAMPLE
    .\Sync-Fork.ps1 -FeatureBranch scooby-port

.EXAMPLE
    .\Sync-Fork.ps1   # uses current branch as feature branch
#>
param(
    [string]$FeatureBranch   = "",
    [string]$MainBranch      = "main",
    [string]$UpstreamRemote  = "upstream",
    [string]$OriginRemote    = "origin"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    WARNING: $msg" -ForegroundColor Yellow }

# Verify we're inside a git repo
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    Write-Error "Not inside a git repository. cd into your scummvm fork first."
    exit 1
}

# Resolve feature branch — default to current branch
if (-not $FeatureBranch) {
    $FeatureBranch = git rev-parse --abbrev-ref HEAD
    Write-Ok "Using current branch as feature branch: $FeatureBranch"
}

if ($FeatureBranch -eq $MainBranch) {
    Write-Error "Feature branch and main branch are the same ('$MainBranch'). Check out your feature branch first."
    exit 1
}

# Verify upstream remote exists
$remotes = git remote
if ($remotes -notcontains $UpstreamRemote) {
    Write-Error "Remote '$UpstreamRemote' not found. Add it with:`n  git remote add upstream https://github.com/scummvm/scummvm.git"
    exit 1
}

# Abort if working tree is dirty
$dirty = git status --porcelain
if ($dirty) {
    Write-Error "Working tree has uncommitted changes. Stash or commit before syncing."
    exit 1
}

# 1. Fetch upstream
Write-Step "Fetching $UpstreamRemote..."
git fetch $UpstreamRemote
Write-Ok "Fetched."

# 2. Sync local main with upstream/main
Write-Step "Updating $MainBranch from $UpstreamRemote/$MainBranch..."
git checkout $MainBranch
git merge --ff-only "$UpstreamRemote/$MainBranch"
Write-Ok "$MainBranch is now up to date."

# 3. Push updated main to your fork
Write-Step "Pushing $MainBranch to $OriginRemote..."
git push $OriginRemote $MainBranch
Write-Ok "Fork's $MainBranch is current."

# 4. Rebase feature branch onto updated main
Write-Step "Rebasing $FeatureBranch onto $MainBranch..."
git checkout $FeatureBranch
git rebase $MainBranch

Write-Host ""
Write-Ok "Done! $FeatureBranch is rebased on the latest $MainBranch."
Write-Warn "If you've already pushed $FeatureBranch to $OriginRemote, you'll need:"
Write-Host "    git push $OriginRemote $FeatureBranch --force-with-lease" -ForegroundColor DarkYellow
