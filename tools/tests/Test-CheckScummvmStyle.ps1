<#
.SYNOPSIS
    Tests for tools/Check-ScummvmStyle.ps1.

.DESCRIPTION
    Builds throwaway git repositories under $env:TEMP, each holding a small
    engines/terraglyph/ tree, runs the checker against them in a child pwsh,
    and checks the exit code and the rules reported. It never touches a real
    ScummVM checkout. Plain PowerShell, no Pester.

    Run: pwsh -NoProfile -File tools\tests\Test-CheckScummvmStyle.ps1
    Exit code 0 when every case passes, 1 otherwise.
#>
[CmdletBinding()]
param(
    [switch]$KeepFixtures
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Checker = Join-Path (Split-Path -Parent $PSScriptRoot) 'Check-ScummvmStyle.ps1'
$WorkRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("check-scummvm-style-tests-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $WorkRoot | Out-Null

$License = @'
/* ScummVM - Graphic Adventure Engine
 *
 * ScummVM is the legal property of its developers, whose names
 * are too numerous to list here. Please refer to the COPYRIGHT
 * file distributed with this source distribution.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
'@ -replace "`r`n", "`n"

# Clean sources that exercise the cases a naive regex gets wrong: exception
# and std words in comments and strings, member calls named like C I/O
# functions, space-aligned continuation lines, dynamic_cast.
$CleanCpp = $License + @'

#include "common/file.h"
#include "terraglyph/clean.h"

namespace Terraglyph {

/*
 * A block comment: try to throw std::vector at it.
 * printf("not code");
 */
bool Clean::load(Common::File &file, Room *room) {
	// Don't try to catch anything; std::string is not used.
	const char *msg = "throw std::vector fopen( printf(";
	char quote = '"';
	if (!file.open("data.bin"))
		return false;
	uint32 size = file.readUint32LE();
	_stream->fread(msg, size);
	Special *s = dynamic_cast<Special *>(room);
	int total = addValues(size,
                          quote,
	                      s ? 1 : 0);
	switch (total) {
	case 1:
		total++;
		// fall through
	default:
		break;
	}
	return total > 0;
}

} // End of namespace Terraglyph

'@ -replace "`r`n", "`n"

$CleanH = $License + @'

#ifndef TERRAGLYPH_CLEAN_H
#define TERRAGLYPH_CLEAN_H

#include "common/file.h"

namespace Terraglyph {

class Clean {
public:
	bool load(Common::File &file, Room *room);

private:
	Common::SeekableReadStream *_stream;
};

} // End of namespace Terraglyph

#endif

'@ -replace "`r`n", "`n"

$script:Failures = 0
$script:Passes = 0

function Write-Source([string]$Repo, [string]$RelPath, [string]$Text) {
    $full = Join-Path $Repo $RelPath
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $full) | Out-Null
    [System.IO.File]::WriteAllText($full, $Text, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-FixtureGit([string]$Repo, [string[]]$GitArgs) {
    $out = & git -C $Repo -c user.name=Fixture -c user.email=fixture@example.invalid -c core.autocrlf=false -c commit.gpgsign=false @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) { throw "fixture git $($GitArgs -join ' ') failed: $out" }
}

function Commit-All([string]$Repo, [string]$Message) {
    Invoke-FixtureGit $Repo @('add', '-A')
    $msgFile = Join-Path $WorkRoot ("msg-" + [guid]::NewGuid().ToString('N') + ".txt")
    [System.IO.File]::WriteAllText($msgFile, $Message, [System.Text.UTF8Encoding]::new($false))
    Invoke-FixtureGit $Repo @('commit', '-q', '--allow-empty', '-F', $msgFile)
}

# A repo whose base commit (tagged 'base') holds the clean sources.
function New-Fixture([string]$Name) {
    $repo = Join-Path $WorkRoot $Name
    New-Item -ItemType Directory -Path $repo | Out-Null
    Invoke-FixtureGit $repo @('init', '-q', '-b', 'main')
    Write-Source $repo 'engines/terraglyph/clean.cpp' $CleanCpp
    Write-Source $repo 'engines/terraglyph/clean.h' $CleanH
    Commit-All $repo "TERRAGLYPH: Add the clean fixture"
    Invoke-FixtureGit $repo @('tag', 'base')
    return $repo
}

function Invoke-Checker([string[]]$CheckerArgs, [string]$WorkingDirectory = $WorkRoot) {
    Push-Location $WorkingDirectory
    try {
        $out = & pwsh -NoProfile -NonInteractive -File $Checker @CheckerArgs 2>&1 | ForEach-Object { "$_" }
        return [pscustomobject]@{ Exit = $LASTEXITCODE; Output = @($out) }
    } finally {
        Pop-Location
    }
}

function Get-Rules($Result) {
    return @($Result.Output | ForEach-Object { if ($_ -match ': error ([A-Z-]+):') { $Matches[1] } })
}

function Assert-Case([string]$Name, $Result, [int]$ExpectExit, [string[]]$ExpectRules = @(), [string[]]$ForbidRules = @(), [string]$ExpectText = '') {
    $rules = Get-Rules $Result
    $problems = @()
    if ($Result.Exit -ne $ExpectExit) { $problems += "exit $($Result.Exit), expected $ExpectExit" }
    foreach ($r in $ExpectRules) { if ($rules -notcontains $r) { $problems += "missing $r" } }
    foreach ($r in $ForbidRules) { if ($rules -contains $r) { $problems += "unexpected $r" } }
    if ($ExpectText -and -not ($Result.Output -join "`n").Contains($ExpectText)) { $problems += "output lacks '$ExpectText'" }
    if ($problems.Count -eq 0) {
        $script:Passes++
        Write-Host "PASS  $Name"
    } else {
        $script:Failures++
        Write-Host "FAIL  $Name : $($problems -join '; ')"
        $Result.Output | ForEach-Object { Write-Host "        $_" }
    }
}

$AllSourceRules = @('LICENSE-HEADER', 'INDENT-SPACES', 'INDENT-MIXED', 'TRAILING-WS', 'FINAL-NEWLINE',
    'EOL-CRLF', 'STD-NAMESPACE', 'STD-WRAPPER', 'STL-HEADER', 'EXCEPTION', 'FORBIDDEN-BYPASS',
    'RAW-FILE-IO', 'PRINT-FUNCTION', 'HEADER-GUARD')

try {
    # 1. Clean source and a clean commit: nothing to report.
    $repo = New-Fixture 'clean'
    Write-Source $repo 'engines/terraglyph/rooms/hall.h' ($CleanH -replace 'TERRAGLYPH_CLEAN_H', 'TERRAGLYPH_ROOMS_HALL_H')
    Commit-All $repo "TERRAGLYPH: Add the hall room"
    $before = Get-ChildItem $repo -Recurse -File -Force | Where-Object { $_.FullName -notmatch '\\\.git\\' } |
        ForEach-Object { "$($_.FullName)=$((Get-FileHash $_.FullName).Hash)" }
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-BaseRef', 'base')
    Assert-Case 'clean source and commit pass' $res 0 -ForbidRules $AllSourceRules -ExpectText '0 finding(s)'
    $after = Get-ChildItem $repo -Recurse -File -Force | Where-Object { $_.FullName -notmatch '\\\.git\\' } |
        ForEach-Object { "$($_.FullName)=$((Get-FileHash $_.FullName).Hash)" }
    $same = @(Compare-Object $before $after).Count -eq 0
    Assert-Case 'checker leaves files unchanged' ([pscustomobject]@{ Exit = [int](-not $same); Output = @() }) 0

    # 2. Missing license header.
    $repo = New-Fixture 'license'
    Write-Source $repo 'engines/terraglyph/nolicense.cpp' ($CleanCpp.Substring($License.Length))
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'missing license header' $res 1 -ExpectRules @('LICENSE-HEADER') -ExpectText 'nolicense.cpp(1): error LICENSE-HEADER'

    # 3. License header for another licence version.
    $repo = New-Fixture 'license-v2'
    Write-Source $repo 'engines/terraglyph/gplv2.cpp' (($CleanCpp -replace 'either version 3 of the License, or', 'version 2 of the License.') -replace '\(at your option\) any later version\.', '')
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'wrong license wording' $res 1 -ExpectRules @('LICENSE-HEADER')

    # 4. Trailing whitespace, final newline.
    $repo = New-Fixture 'whitespace'
    Write-Source $repo 'engines/terraglyph/ws.cpp' (($CleanCpp -replace 'return total > 0;', "return total > 0;  ").TrimEnd("`n"))
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'trailing whitespace and final newline' $res 1 -ExpectRules @('TRAILING-WS', 'FINAL-NEWLINE')

    # 5. Space indentation, and mixed indentation; continuation alignment stays clean.
    $repo = New-Fixture 'indent'
    Write-Source $repo 'engines/terraglyph/indent.cpp' (($CleanCpp -replace "`tuint32 size = file", '    uint32 size = file') -replace "`treturn total > 0;", " `treturn total > 0;")
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'space and mixed indentation' $res 1 -ExpectRules @('INDENT-SPACES', 'INDENT-MIXED')
    $lines = @($res.Output | Where-Object { $_ -match 'INDENT-SPACES' })
    Assert-Case 'continuation alignment not flagged' ([pscustomobject]@{ Exit = $lines.Count; Output = $lines }) 1

    # 5b. A file committed with CRLF line endings.
    $repo = New-Fixture 'crlf'
    Write-Source $repo 'engines/terraglyph/crlf.cpp' ($CleanCpp -replace "`n", "`r`n")
    Commit-All $repo "TERRAGLYPH: Add a CRLF file"
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'CRLF stored in git' $res 1 -ExpectRules @('EOL-CRLF') -ForbidRules @('TRAILING-WS', 'INDENT-SPACES')

    # 6. STL usage, Std:: wrappers.
    $repo = New-Fixture 'stl'
    Write-Source $repo 'engines/terraglyph/stl.cpp' ($CleanCpp -replace '#include "common/file.h"', "#include `"common/file.h`"`n#include <vector>`n#include `"common/std/map.h`"" -replace "`tuint32 size = file.readUint32LE\(\);", "`tuint32 size = file.readUint32LE();`n`tstd::vector<int> v;`n`tStd::map<int, int> m;")
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'STL header, std:: and Std::' $res 1 -ExpectRules @('STL-HEADER', 'STD-NAMESPACE', 'STD-WRAPPER')

    # 7. Exceptions, raw I/O, printing, forbidden-symbol bypass.
    $repo = New-Fixture 'forbidden'
    Write-Source $repo 'engines/terraglyph/forbidden.cpp' ($CleanCpp -replace '#include "common/file.h"', "#define FORBIDDEN_SYMBOL_ALLOW_ALL`n#include `"common/file.h`"" -replace "`tuint32 size = file.readUint32LE\(\);", "`tuint32 size = file.readUint32LE();`n`tFILE *f = fopen(`"x`", `"rb`");`n`tprintf(`"%d`", size);`n`ttry {`n`t`tthrow 1;`n`t} catch (...) {`n`t}")
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'exceptions, raw I/O, printf, bypass' $res 1 -ExpectRules @('EXCEPTION', 'RAW-FILE-IO', 'PRINT-FUNCTION', 'FORBIDDEN-BYPASS')

    # 8. Header guards: wrong name, #pragma once, missing; detection_tables.h exempt.
    $repo = New-Fixture 'guards'
    Write-Source $repo 'engines/terraglyph/wrong.h' ($CleanH -replace 'TERRAGLYPH_CLEAN_H', 'WRONG_H')
    Write-Source $repo 'engines/terraglyph/pragma.h' (($CleanH -replace '#ifndef TERRAGLYPH_CLEAN_H\n#define TERRAGLYPH_CLEAN_H', '#pragma once') -replace '\n#endif\n$', "`n")
    Write-Source $repo 'engines/terraglyph/detection_tables.h' ($License + "`nnamespace Terraglyph {`n} // End of namespace Terraglyph`n")
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'invalid header guards' $res 1 -ExpectRules @('HEADER-GUARD') -ExpectText 'guard WRONG_H should be TERRAGLYPH_WRONG_H'
    Assert-Case '#pragma once reported' $res 1 -ExpectText 'pragma.h(1): error HEADER-GUARD: #pragma once'
    $dt = @($res.Output | Where-Object { $_ -match 'detection_tables' })
    Assert-Case 'detection_tables.h exempt' ([pscustomobject]@{ Exit = $dt.Count; Output = $dt }) 0

    # 9. Commit subjects: no prefix, too long, wrong subsystem, no blank line, merge.
    $repo = New-Fixture 'commits'
    Write-Source $repo 'engines/terraglyph/a.cpp' $CleanCpp
    Commit-All $repo "fixed the thing that was broken in the engine yesterday"
    Write-Source $repo 'engines/terraglyph/b.cpp' $CleanCpp
    Commit-All $repo "SCOOBY: Add b`nno blank line here"
    Invoke-FixtureGit $repo @('switch', '-q', '-c', 'side', 'base')
    Write-Source $repo 'engines/terraglyph/c.cpp' $CleanCpp
    Commit-All $repo "TERRAGLYPH: Add c"
    Invoke-FixtureGit $repo @('switch', '-q', 'main')
    Invoke-FixtureGit $repo @('merge', '-q', '--no-ff', '-m', 'Merge branch side', 'side')
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-BaseRef', 'base')
    Assert-Case 'invalid commit messages' $res 1 -ExpectRules @('COMMIT-PREFIX', 'COMMIT-LENGTH', 'COMMIT-SUBSYSTEM', 'COMMIT-BLANK', 'COMMIT-MERGE') -ForbidRules $AllSourceRules

    # 10. AI co-author trailer and AI-generated note; lower-case trailer too.
    $repo = New-Fixture 'trailer'
    Write-Source $repo 'engines/terraglyph/d.cpp' $CleanCpp
    Commit-All $repo "TERRAGLYPH: Add d`n`nBody text.`n`nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    Write-Source $repo 'engines/terraglyph/e.cpp' $CleanCpp
    Commit-All $repo "TERRAGLYPH: Add e`n`nco-authored-by: Copilot <123+Copilot@users.noreply.github.com>"
    Write-Source $repo 'engines/terraglyph/f.cpp' $CleanCpp
    Commit-All $repo "TERRAGLYPH: Add f`n`nCo-authored-by: Jane Human <jane@example.invalid>"
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-BaseRef', 'base')
    $ai = @($res.Output | Where-Object { $_ -match 'AI-TRAILER' })
    Assert-Case 'AI co-author trailers' $res 1 -ExpectRules @('AI-TRAILER')
    Assert-Case 'two AI trailers, human trailer ignored' ([pscustomobject]@{ Exit = $ai.Count; Output = $ai }) 2

    # 11. Commits before BaseRef are not inspected.
    $repo = New-Fixture 'range'
    Commit-All $repo "bad subject before the base, much longer than fifty characters"
    Invoke-FixtureGit $repo @('tag', '-f', 'base')
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-BaseRef', 'base')
    Assert-Case 'commits before BaseRef ignored' $res 0 -ExpectText '0 commit(s)'

    # 12. Scope Changed checks only files changed since BaseRef.
    $repo = New-Fixture 'changed'
    Write-Source $repo 'engines/terraglyph/old_bad.cpp' "no license`n"
    Commit-All $repo "TERRAGLYPH: Add old bad file"
    Invoke-FixtureGit $repo @('tag', '-f', 'base')
    Write-Source $repo 'engines/terraglyph/new_bad.cpp' "no license either`n"
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-BaseRef', 'base', '-Scope', 'Changed', '-SkipCommits')
    $txt = $res.Output -join "`n"
    Assert-Case 'Scope Changed reports the new file only' ([pscustomobject]@{ Exit = $res.Exit; Output = $res.Output }) 1 -ExpectRules @('LICENSE-HEADER')
    Assert-Case 'Scope Changed skips the old file' ([pscustomobject]@{ Exit = [int]$txt.Contains('old_bad.cpp'); Output = $res.Output }) 0

    # 13. Files outside engines/terraglyph/ are never checked.
    $repo = New-Fixture 'outside'
    Write-Source $repo 'engines/other/bad.cpp' "std::vector<int> v;   `n"
    Write-Source $repo 'common/bad.h' "no guard`n"
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-SkipCommits')
    Assert-Case 'other engines and common code ignored' $res 0

    # 14. Configuration errors exit 2.
    $res = Invoke-Checker @('-ScummvmPath', (Join-Path $WorkRoot 'does-not-exist'))
    Assert-Case 'invalid repository path' $res 2 -ExpectText 'is not a directory'
    $res = Invoke-Checker @()
    Assert-Case 'missing -ScummvmPath' $res 2 -ExpectText 'is required'
    $plain = Join-Path $WorkRoot 'not-a-repo'
    New-Item -ItemType Directory -Path $plain | Out-Null
    $res = Invoke-Checker @('-ScummvmPath', $plain)
    Assert-Case 'directory that is not a git checkout' $res 2 -ExpectText 'not a git checkout'
    $noEngine = Join-Path $WorkRoot 'no-engine'
    New-Item -ItemType Directory -Path $noEngine | Out-Null
    Invoke-FixtureGit $noEngine @('init', '-q')
    $res = Invoke-Checker @('-ScummvmPath', $noEngine, '-SkipCommits')
    Assert-Case 'checkout without engines/terraglyph' $res 2 -ExpectText 'has no engines/terraglyph'
    $repo = New-Fixture 'badref'
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-BaseRef', 'no-such-ref')
    Assert-Case 'unknown BaseRef' $res 2 -ExpectText "BaseRef 'no-such-ref'"
    $res = Invoke-Checker @('-ScummvmPath', $repo, '-Scope', 'Some')
    Assert-Case 'invalid -Scope' $res 2 -ExpectText '-Scope must be'

    # 15. Invoked from another directory, with a relative -ScummvmPath.
    $elsewhere = Join-Path $WorkRoot 'elsewhere'
    New-Item -ItemType Directory -Path $elsewhere | Out-Null
    $res = Invoke-Checker @('-ScummvmPath', '..\clean', '-BaseRef', 'base') $elsewhere
    Assert-Case 'run from another directory, relative path' $res 0 -ExpectText '0 finding(s)'
    $res = Invoke-Checker @('-ScummvmPath', (Join-Path $WorkRoot 'clean\engines\terraglyph'), '-BaseRef', 'base') $elsewhere
    Assert-Case 'path inside the checkout resolves to its root' $res 0 -ExpectText '0 finding(s)'
} finally {
    if ($KeepFixtures) {
        Write-Host "Fixtures kept in $WorkRoot"
    } else {
        Remove-Item -LiteralPath $WorkRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "$script:Passes passed, $script:Failures failed"
if ($script:Failures -gt 0) { exit 1 }
exit 0
