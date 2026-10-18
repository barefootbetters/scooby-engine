<#
.SYNOPSIS
Runs the engine ewiki's five build gates against a wiki.

.DESCRIPTION
The gates of the engine's wiki-viewer.yml, in its order:

1. Build: `hugo --source <Site> --minify` (plus --config and
   --panicOnWarning when asked), into a fresh output folder.
2. Page count: the content .md count equals the rendered index.html count.
3. Determinism: a second build from scratch hashes identically over every
   *.html and *.css.
4. Pagefind: `npx --yes pagefind@1.5.2 --site <output>`.
5. JS-free: every `<script` in the rendered HTML is the sanctioned
   `<script data-wiki-search` loader, and the Pagefind bundle exists.

It prints each gate's numbers and exits 1 on the first failure.

.PARAMETER Site
The Hugo project directory (`hugo --source`).

.PARAMETER Config
The site config. Defaults to <Site>/hugo.toml. When given, it is passed to
hugo as --config. Its publishDir (default public) is the output folder,
resolved against -Site.

.PARAMETER ContentDir
The folder whose .md files the page-count gate counts. Defaults to
<Site>/content.

.PARAMETER ExpectedPageCount
The page count to expect instead, for a wiki whose content arrives through
mounts. The calling workflow computes it at run time from the mounted
source files; a hard-coded number is a static floor that goes stale.

.PARAMETER PanicOnWarning
Pass --panicOnWarning to hugo, so a warning (a broken link) fails the build.

.EXAMPLE
pwsh -File themes/ewiki/tools/Invoke-WikiGates.ps1 -Site . -PanicOnWarning
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Site,

    [string] $Config,

    [string] $ContentDir,

    [int] $ExpectedPageCount = -1,

    [switch] $PanicOnWarning
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Stop-WithGateFailure {
    <#
    .SYNOPSIS
    Prints a gate failure to stderr and exits 1.
    .PARAMETER Message
    What failed and how to fix it, as full sentences.
    #>
    param([string] $Message)
    [Console]::Error.WriteLine($Message)
    exit 1
}

function Get-PublishPath {
    <#
    .SYNOPSIS
    Returns the output folder: the config's publishDir, against the site.
    .PARAMETER SitePath
    The full site path.
    .PARAMETER ConfigPath
    The full config path.
    #>
    param([string] $SitePath, [string] $ConfigPath)
    $publishDir = 'public'
    foreach ($line in (Get-Content -LiteralPath $ConfigPath)) {
        if ($line -match '^\s*\[') {
            break
        }
        if ($line -match '^\s*publishDir\s*=\s*["''](?<value>[^"'']+)["'']') {
            $publishDir = $Matches['value']
        }
    }
    return [System.IO.Path]::GetFullPath($publishDir, $SitePath)
}

function Invoke-HugoBuild {
    <#
    .SYNOPSIS
    Deletes the output folder and builds the site with hugo --minify.
    .PARAMETER Settings
    The resolved site, config and output paths.
    #>
    param([pscustomobject] $Settings)
    if (Test-Path -LiteralPath $Settings.PublishPath) {
        Remove-Item -LiteralPath $Settings.PublishPath -Recurse -Force
    }
    $arguments = @('--source', $Settings.SitePath, '--minify')
    if ($Config) {
        $arguments += @('--config', $Settings.ConfigPath)
    }
    if ($PanicOnWarning) {
        $arguments += '--panicOnWarning'
    }
    & hugo @arguments
    if ($LASTEXITCODE -ne 0) {
        Stop-WithGateFailure "Build gate failed: hugo exited $LASTEXITCODE for $($Settings.SitePath). Fix the error hugo printed above; a warning fails the build under -PanicOnWarning."
    }
}

function Test-PageCount {
    <#
    .SYNOPSIS
    Gate 2: content pages equal rendered index.html pages.
    .PARAMETER Settings
    The resolved site, config and output paths.
    #>
    param([pscustomobject] $Settings)
    $expected = $ExpectedPageCount
    if ($expected -lt 0) {
        $expected = @(Get-ChildItem -LiteralPath $Settings.ContentPath -Recurse -File -Filter '*.md').Count
    }
    $rendered = @(Get-ChildItem -LiteralPath $Settings.PublishPath -Recurse -File -Filter 'index.html').Count
    Write-Host "Content pages: $expected; rendered HTML pages: $rendered."
    if ($expected -eq 0) {
        Stop-WithGateFailure "Page-count gate failed: found zero content pages for $($Settings.SitePath). Check -ContentDir, or pass -ExpectedPageCount computed from the mounted sources."
    }
    if ($rendered -ne $expected) {
        Stop-WithGateFailure "Page-count gate failed: hugo rendered $rendered pages but the content has $expected, so a page silently failed to render. Compare the content .md files against $($Settings.PublishPath) to find the dropped page."
    }
    Write-Host "Page-count gate passed: all $expected content pages rendered to HTML."
}

function Get-BuildHash {
    <#
    .SYNOPSIS
    Hashes every *.html and *.css in the output, in ordinal path order.
    .PARAMETER PublishPath
    The output folder.
    #>
    param([string] $PublishPath)
    $root = (Resolve-Path -LiteralPath $PublishPath).Path.TrimEnd('\', '/')
    $relativePaths = [string[]] @(Get-ChildItem -LiteralPath $root -Recurse -File |
        Where-Object { $_.Extension -in @('.html', '.css') } |
        ForEach-Object { $_.FullName.Substring($root.Length + 1).Replace('\', '/') })
    [System.Array]::Sort($relativePaths, [System.StringComparer]::Ordinal)
    $lines = foreach ($relativePath in $relativePaths) {
        $hash = (Get-FileHash -LiteralPath (Join-Path $root $relativePath) -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $relativePath"
    }
    $listing = [System.Text.Encoding]::UTF8.GetBytes((@($lines) -join "`n") + "`n")
    return ([System.Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($listing))).ToLowerInvariant()
}

function Test-Determinism {
    <#
    .SYNOPSIS
    Gate 3: a second build from scratch hashes identically.
    .PARAMETER Settings
    The resolved site, config and output paths.
    #>
    param([pscustomobject] $Settings)
    $firstHash = Get-BuildHash $Settings.PublishPath
    Invoke-HugoBuild $Settings
    $secondHash = Get-BuildHash $Settings.PublishPath
    if ($firstHash -ne $secondHash) {
        Stop-WithGateFailure "Determinism gate failed: two consecutive builds differ (first $firstHash, second $secondHash). Look for a clock, random value, GitInfo or map-order dependence in a template."
    }
    Write-Host "Determinism gate passed: $firstHash"
}

function Invoke-PagefindIndex {
    <#
    .SYNOPSIS
    Gate 4: builds the Pagefind search index into the output.
    .PARAMETER Settings
    The resolved site, config and output paths.
    #>
    param([pscustomobject] $Settings)
    & npx --yes pagefind@1.5.2 --site $Settings.PublishPath
    if ($LASTEXITCODE -ne 0) {
        Stop-WithGateFailure "Pagefind gate failed: pagefind exited $LASTEXITCODE for $($Settings.PublishPath). Check that Node 22+ and npx are on PATH, and that some page carries data-pagefind-body."
    }
    Write-Host 'Pagefind gate passed: the search index was built.'
}

function Test-JavaScriptFree {
    <#
    .SYNOPSIS
    Gate 5: every script element in rendered HTML is the Pagefind loader.
    .PARAMETER Settings
    The resolved site, config and output paths.
    #>
    param([pscustomobject] $Settings)
    $total = 0
    $sanctioned = 0
    foreach ($file in (Get-ChildItem -LiteralPath $Settings.PublishPath -Recurse -File -Filter '*.html')) {
        $html = [System.IO.File]::ReadAllText($file.FullName)
        $total += [regex]::Matches($html, '<script').Count
        $sanctioned += [regex]::Matches($html, '<script data-wiki-search').Count
    }
    Write-Host "Rendered HTML script tags: $total; sanctioned data-wiki-search loaders: $sanctioned."
    if ($total -ne $sanctioned) {
        Stop-WithGateFailure "JS-free gate failed: $total script tag(s) in rendered HTML, but only $sanctioned are the data-wiki-search Pagefind loader (D-24293). Remove the other script, or gate it in the wiki's own extension partial."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $Settings.PublishPath 'pagefind/pagefind-ui.js'))) {
        Stop-WithGateFailure "JS-free gate failed: $($Settings.PublishPath)/pagefind/pagefind-ui.js is missing, so the Pagefind gate produced no search bundle. Check that gate's output."
    }
    Write-Host "JS-free gate passed: all $total script tag(s) are the sanctioned Pagefind loader, and the Pagefind bundle is present."
}

function Invoke-WikiGateRun {
    <#
    .SYNOPSIS
    Resolves the paths and runs the five gates in order.
    #>
    $sitePath = [System.IO.Path]::GetFullPath($Site, (Get-Location).Path)
    $configPath = if ($Config) { [System.IO.Path]::GetFullPath($Config, (Get-Location).Path) } else { Join-Path $sitePath 'hugo.toml' }
    if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
        throw "Invoke-WikiGates.ps1: the config $configPath does not exist. Pass -Config with the site's hugo.toml."
    }
    $contentPath = if ($ContentDir) { [System.IO.Path]::GetFullPath($ContentDir, (Get-Location).Path) } else { Join-Path $sitePath 'content' }
    $settings = [pscustomobject]@{
        SitePath    = $sitePath
        ConfigPath  = $configPath
        ContentPath = $contentPath
        PublishPath = Get-PublishPath $sitePath $configPath
    }
    Invoke-HugoBuild $settings
    Write-Host 'Build gate passed: hugo built the site.'
    Test-PageCount $settings
    Test-Determinism $settings
    Invoke-PagefindIndex $settings
    Test-JavaScriptFree $settings
}

Invoke-WikiGateRun
