<#
.SYNOPSIS
    Check the TerraGlyph engine sources and branch commits against ScummVM's
    objective coding and commit rules. Read-only: it never modifies a file.

.DESCRIPTION
    Layer A of the code-review workflow (docs/reference/copilot-code-review-workflow.md).
    It catches the rules a machine can check reliably, so Copilot review and
    human review can spend their time on judgment.

    Source checks cover engines/terraglyph/**/*.cpp and *.h only. Comments and
    string literals are blanked before any token check, so "try to" in a
    comment or "throw" in a debug string is not reported.

    Rules and their sources:
      LICENSE-HEADER  Standard ScummVM GPLv3-or-later header at the top of the
                      file (AI-GUIDELINES.md: GPLv3+; header text is the
                      upstream pattern)
      INDENT-SPACES   A statement indented with spaces instead of tabs (wiki
                      Code Formatting Conventions; .editorconfig). Spaces used
                      to align a continuation line are allowed.
      INDENT-MIXED    A space before a tab in the indentation
      TRAILING-WS     Trailing spaces or tabs (.editorconfig)
      FINAL-NEWLINE   File does not end with a newline (.editorconfig)
      EOL-CRLF        A tracked file is stored with CRLF line endings in the
                      index (.gitattributes: *.cpp/*.h eol=lf)
      STD-NAMESPACE   std:: (wiki Coding Conventions: new engines use common/)
      STD-WRAPPER     Std:: or common/std/ (for porting existing code only)
      STL-HEADER      A C++ standard library header
      EXCEPTION       throw, try or catch (wiki Coding Conventions)
      FORBIDDEN-BYPASS  #define FORBIDDEN_SYMBOL_* (turns off common/forbidden.h)
      RAW-FILE-IO     fopen/fread/FILE * and the like (also a compile error via
                      common/forbidden.h; reported here so it shows up first)
      PRINT-FUNCTION  printf/puts family (same)
      HEADER-GUARD    .h file without an #ifndef/#define guard named
                      TERRAGLYPH_<FILE>_H or TERRAGLYPH_<PATH>_H (upstream
                      pattern; detection_tables.h is exempt, as in most
                      upstream engines)

    Commit checks cover the commits in <BaseRef>..HEAD only, so upstream
    history is never inspected:
      COMMIT-MERGE    Merge commit (upstream requires linear history)
      COMMIT-PREFIX   Subject does not start with a CAPS subsystem prefix
                      (upstream devtools/check-commit-msg.py: [A-Z_]+:)
      COMMIT-SUBSYSTEM  A commit touching engines/terraglyph/ does not use the
                      TERRAGLYPH: prefix (project rule; see -EnginePrefix)
      COMMIT-LENGTH   Subject longer than 50 characters (wiki Commit
                      Guidelines). A GitHub squash merge appends " (#NN)",
                      which counts.
      COMMIT-BLANK    Second line of the message is not blank
      AI-TRAILER      A Co-authored-by trailer naming an AI tool, or a
                      "Generated with" AI line (AI-GUIDELINES.md)

    Not checked, on purpose: present tense (left to human review); RTTI
    (upstream engines use dynamic_cast); global constructors and non-const
    static locals (a regex cannot tell them apart from valid code; left to
    Copilot and human review).

    Known limits: a line comment continued with a trailing backslash, and a
    method declared with the same name as a C I/O function, can confuse the
    token checks. Character literals with a prefix (L'x', u8'x') are not
    blanked.

.PARAMETER ScummvmPath
    The ScummVM checkout (the fork, or a worktree of it). Required.

.PARAMETER BaseRef
    The commit the branch starts from. Commits in <BaseRef>..HEAD are checked,
    and -Scope Changed compares against it. Default: origin/scooby-engine, the
    base of an internal review PR. Use upstream/master to check what an
    upstream PR would carry.

.PARAMETER Scope
    All (default): every engine source file. Changed: only engine files
    changed since the merge base with BaseRef, plus uncommitted and untracked
    ones.

.PARAMETER SkipCommits
    Check source files only.

.PARAMETER EnginePrefix
    The subsystem prefix required on commits that touch the engine
    (default TERRAGLYPH). Pass an empty string to turn COMMIT-SUBSYSTEM off.

.OUTPUTS
    One line per finding, in the Visual Studio / MSBuild format
    "<file>(<line>): error <RULE>: <message>", so the Output window links to
    the line. Commit findings read "commit <sha>: error <RULE>: <message>".

    Exit codes: 0 no findings; 1 findings; 2 bad parameters or a failure while
    running (bad path, unknown BaseRef, git error).

.EXAMPLE
    pwsh -File tools\Check-ScummvmStyle.ps1 -ScummvmPath C:\claude-worktrees\scummvm-my-branch

.EXAMPLE
    pwsh -File tools\Check-ScummvmStyle.ps1 -ScummvmPath C:\dev\scummvm -Scope Changed -BaseRef origin/scooby-engine

.EXAMPLE
    pwsh -File tools\Check-ScummvmStyle.ps1 -ScummvmPath C:\dev\scummvm -BaseRef upstream/master -SkipCommits
#>
# why: no Mandatory or ValidateSet. A binding failure exits 1 under
# pwsh -File, which would read as "findings"; validating by hand keeps every
# usage error on exit code 2.
[CmdletBinding()]
param(
    [string]$ScummvmPath = "",
    [string]$BaseRef = "origin/scooby-engine",
    [string]$Scope = "All",
    [switch]$SkipCommits,
    [string]$EnginePrefix = "TERRAGLYPH"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$EngineDir = "engines/terraglyph"

function Exit-WithConfigError([string]$Message) {
    [Console]::Error.WriteLine("Check-ScummvmStyle: $Message")
    exit 2
}

# Run git in the checkout; throw on failure so the outer handler exits 2.
function Invoke-Git([string[]]$GitArgs) {
    $out = & git -C $script:Root @GitArgs 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed (exit $LASTEXITCODE)"
    }
    return @($out)
}

$script:Findings = [System.Collections.Generic.List[string]]::new()

function Add-Finding([string]$Where, [string]$Rule, [string]$Message) {
    $script:Findings.Add("${Where}: error ${Rule}: $Message")
}

# Blank comments and the contents of string and character literals, keeping
# every newline and every column, so a line number or regex position in the
# result is the same as in the source. Returns the blanked text and, for each
# line, whether it starts inside a block comment.
$script:LexRegex = [regex]::new(
    '(?<lc>//[^\n]*)' +
    '|(?<bc>/\*.*?(?:\*/|\z))' +
    '|(?<raw>(?<![A-Za-z0-9_])(?:u8|u|U|L)?R"(?<d>[^()\\\s"]{0,16})\(.*?\)\k<d>")' +
    '|(?<str>"(?:\\.|[^"\\\n])*")' +
    '|(?<chr>(?<![A-Za-z0-9_])''(?:\\.|[^''\\\n])+'')',
    [System.Text.RegularExpressions.RegexOptions]::Singleline)

$script:NotNewline = [regex]::new('[^\n]')

function Get-BlankedSource([string]$Text) {
    $inComment = [System.Collections.Generic.HashSet[int]]::new()
    # Matches arrive in order, so the line count is kept as a running tally.
    $state = @{ Pos = 0; Line = 0 }
    # why: a closure gets its own module scope, where $script: is not this script's.
    $notNewline = $script:NotNewline
    $evaluator = {
        param($m)
        $s = $m.Value
        $state.Line += ($Text.Substring($state.Pos, $m.Index - $state.Pos).Split("`n").Count - 1)
        $extra = $s.Split("`n").Count - 1
        if ($extra -gt 0 -and ($m.Groups['bc'].Success -or $m.Groups['raw'].Success)) {
            # Lines after the first one start inside this comment or raw string.
            for ($k = 1; $k -le $extra; $k++) { [void]$inComment.Add($state.Line + $k) }
        }
        $state.Line += $extra
        $state.Pos = $m.Index + $m.Length
        if ($m.Groups['str'].Success -or $m.Groups['chr'].Success) {
            # Keep the quotes so an #include "..." line still reads as one.
            return $s[0] + (' ' * ($s.Length - 2)) + $s[-1]
        }
        return $notNewline.Replace($s, ' ')
    }.GetNewClosure()
    $blanked = $script:LexRegex.Replace($Text, $evaluator)
    return [pscustomobject]@{ Text = $blanked; InComment = $inComment }
}

$StlHeaders = @(
    'algorithm', 'any', 'array', 'atomic', 'bitset', 'chrono', 'codecvt', 'complex',
    'condition_variable', 'deque', 'exception', 'execution', 'filesystem', 'forward_list',
    'fstream', 'functional', 'future', 'iomanip', 'ios', 'iosfwd', 'iostream', 'istream',
    'iterator', 'list', 'locale', 'map', 'memory', 'mutex', 'numeric', 'optional',
    'ostream', 'queue', 'random', 'ratio', 'regex', 'set', 'shared_mutex', 'sstream',
    'stack', 'stdexcept', 'streambuf', 'string', 'string_view', 'system_error', 'thread',
    'tuple', 'type_traits', 'typeindex', 'typeinfo', 'unordered_map', 'unordered_set',
    'utility', 'valarray', 'variant', 'vector'
)
$CallGuard = '(?<!\.|->|[A-Za-z0-9_]::)\b'
$RawIoRegex = [regex]::new($CallGuard + '(fopen|_wfopen|freopen|fclose|fread|fwrite|fseek|ftell|fgets|fgetc|fputs|fputc|fscanf|tmpfile|CreateFile[AW]?)\s*\(')
$FileStarRegex = [regex]::new('(?<![A-Za-z0-9_:])FILE\s*\*')
$PrintRegex = [regex]::new($CallGuard + '(printf|fprintf|sprintf|vprintf|vfprintf|vsprintf|puts|putchar)\s*\(')
$StdRegex = [regex]::new('(?<![A-Za-z0-9_])std\s*::')
$StdWrapperRegex = [regex]::new('(?<![A-Za-z0-9_])Std\s*::')
$ExceptionRegex = [regex]::new('(?<![A-Za-z0-9_])(throw|try|catch)(?![A-Za-z0-9_])')
$IncludeRegex = [regex]::new('^\s*#\s*include\s*([<"])\s*([^>"]+?)\s*[>"]')
$BypassRegex = [regex]::new('^\s*#\s*define\s+(FORBIDDEN_SYMBOL_\w+)')

$LicenseNeedles = @(
    'ScummVM - Graphic Adventure Engine',
    'GNU General Public License',
    'either version 3 of the License, or',
    '(at your option) any later version'
)

# Does the previous code line end a statement, so that the current line is a
# fresh statement (indentation) rather than a continuation (alignment)?
function Test-StatementBoundary([string[]]$CodeLines, [int]$Index) {
    for ($j = $Index - 1; $j -ge 0; $j--) {
        $p = $CodeLines[$j].Trim()
        if ($p.Length -eq 0) { continue }
        if ($p.StartsWith('#')) { return -not $p.EndsWith('\') }
        if ($p -match '[;{}]$') { return $true }
        if ($p -match '^(public|private|protected)\s*:$' -or $p -match '^(case\b.*|default\s*):$') { return $true }
        if ($p -match '(^|[^A-Za-z0-9_])else$' -or $p -eq 'do') { return $true }
        if ($p.EndsWith(')') -and $p -match '^(\}\s*)?(if|for|while|else\s+if)\s*\(') { return $true }
        return $false
    }
    return $true
}

function Test-SourceFile([string]$FullPath, [string]$RelPath, [hashtable]$IndexCrlf) {
    $where = { param($line) "$FullPath($line)" }.GetNewClosure()
    $text = [System.IO.File]::ReadAllText($FullPath)
    if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) { $text = $text.Substring(1) }

    if ($IndexCrlf.ContainsKey($RelPath)) {
        Add-Finding (& $where 1) 'EOL-CRLF' "stored in git with CRLF line endings; .gitattributes requires LF"
    }
    $norm = $text -replace "`r`n", "`n"
    if ($norm.Length -gt 0 -and -not $norm.EndsWith("`n")) {
        $last = ($norm -split "`n").Count
        Add-Finding (& $where $last) 'FINAL-NEWLINE' "file does not end with a newline"
    }

    # License header: the first comment block, before any code.
    $head = $norm.TrimStart()
    $end = $head.IndexOf('*/')
    if (-not $head.StartsWith('/*') -or $end -lt 0) {
        Add-Finding (& $where 1) 'LICENSE-HEADER' "file does not start with the ScummVM license comment"
    } else {
        $block = $head.Substring(0, $end)
        $missing = @($LicenseNeedles | Where-Object { -not $block.Contains($_) })
        if ($missing.Count -gt 0) {
            Add-Finding (& $where 1) 'LICENSE-HEADER' ("license comment is missing: '" + ($missing -join "', '") + "'")
        }
    }

    $lex = Get-BlankedSource $norm
    $raw = $norm -split "`n"
    $code = $lex.Text -split "`n"

    for ($i = 0; $i -lt $raw.Length; $i++) {
        $n = $i + 1
        $line = $raw[$i]
        $c = $code[$i]

        if ($line -match '[ \t]+$') {
            Add-Finding (& $where $n) 'TRAILING-WS' "trailing whitespace"
        }

        if (-not $lex.InComment.Contains($i) -and $c.Trim().Length -gt 0) {
            $lead = ([regex]::Match($line, '^[ \t]*')).Value
            if ($lead.Contains(" `t")) {
                Add-Finding (& $where $n) 'INDENT-MIXED' "space before a tab in the indentation"
            } elseif ($lead.Length -gt 0 -and $lead -notmatch "`t" -and (Test-StatementBoundary $code $i)) {
                Add-Finding (& $where $n) 'INDENT-SPACES' "indented with spaces; use tabs (spaces are only for aligning continuation lines)"
            }
        }

        $inc = $IncludeRegex.Match($c)
        if ($inc.Success) {
            $rawInc = $IncludeRegex.Match($line)
            $target = if ($rawInc.Success) { $rawInc.Groups[2].Value } else { '' }
            if ($inc.Groups[1].Value -eq '<' -and $StlHeaders -contains $target) {
                Add-Finding (& $where $n) 'STL-HEADER' "#include <$target>: new engines use the common/ classes, not the STL"
            } elseif ($target -like 'common/std/*') {
                Add-Finding (& $where $n) 'STD-WRAPPER' "#include `"$target`": the common/std/ wrappers are for porting existing code, not new engines"
            }
        }

        $byp = $BypassRegex.Match($c)
        if ($byp.Success) {
            Add-Finding (& $where $n) 'FORBIDDEN-BYPASS' "#define $($byp.Groups[1].Value) turns off common/forbidden.h"
        }

        if ($StdRegex.IsMatch($c)) {
            Add-Finding (& $where $n) 'STD-NAMESPACE' "std:: is not used in new engines; use the common/ classes"
        }
        if ($StdWrapperRegex.IsMatch($c)) {
            Add-Finding (& $where $n) 'STD-WRAPPER' "Std:: wrappers are for porting existing code, not new engines"
        }
        $ex = $ExceptionRegex.Match($c)
        if ($ex.Success) {
            Add-Finding (& $where $n) 'EXCEPTION' "'$($ex.Groups[1].Value)': ScummVM code does not use C++ exceptions"
        }
        $io = $RawIoRegex.Match($c)
        if ($io.Success) {
            Add-Finding (& $where $n) 'RAW-FILE-IO' "$($io.Groups[1].Value)(): use Common::File / ScummVM streams"
        } elseif ($FileStarRegex.IsMatch($c)) {
            Add-Finding (& $where $n) 'RAW-FILE-IO' "FILE *: use Common::File / ScummVM streams"
        }
        $pr = $PrintRegex.Match($c)
        if ($pr.Success) {
            Add-Finding (& $where $n) 'PRINT-FUNCTION' "$($pr.Groups[1].Value)(): use debug()/debugC(), warning() or error()"
        }
    }

    if ($RelPath.EndsWith('.h') -and [System.IO.Path]::GetFileName($RelPath) -ne 'detection_tables.h') {
        Test-HeaderGuard $code $RelPath $where
    }
}

function Test-HeaderGuard([string[]]$Code, [string]$RelPath, [scriptblock]$Where) {
    $directives = @()
    for ($i = 0; $i -lt $Code.Length; $i++) {
        $t = $Code[$i].Trim()
        if ($t.StartsWith('#')) { $directives += , @(($i + 1), ($t -replace '^#\s*', '#')) }
    }
    $inner = $RelPath.Substring($EngineDir.Length + 1)
    $fileStem = [System.IO.Path]::GetFileNameWithoutExtension($inner).ToUpperInvariant() -replace '[^A-Z0-9]', '_'
    $pathStem = ($inner -replace '\.h$', '').ToUpperInvariant() -replace '[^A-Z0-9]', '_'
    $expected = @("TERRAGLYPH_${fileStem}_H", "TERRAGLYPH_${pathStem}_H")
    if ($fileStem -eq 'TERRAGLYPH') { $expected += 'TERRAGLYPH_H' }
    $expected = @($expected | Select-Object -Unique)

    if ($directives.Count -eq 0 -or $directives[0][1] -notmatch '^#ifndef\s+(\w+)$') {
        if (@($directives | Where-Object { $_[1] -match '^#pragma\s+once' }).Count -gt 0) {
            Add-Finding (& $Where 1) 'HEADER-GUARD' "#pragma once: use an #ifndef guard named $($expected[0])"
        } else {
            Add-Finding (& $Where 1) 'HEADER-GUARD' "no #ifndef include guard before the first directive; expected $($expected[0])"
        }
        return
    }
    $name = $Matches[1]
    $line = $directives[0][0]
    if ($directives.Count -lt 2 -or $directives[1][1] -notmatch "^#define\s+$([regex]::Escape($name))(\s|$)") {
        Add-Finding (& $Where $line) 'HEADER-GUARD' "#ifndef $name is not followed by #define $name"
    }
    if ($directives[-1][1] -notmatch '^#endif') {
        Add-Finding (& $Where $directives[-1][0]) 'HEADER-GUARD' "the last directive is not the #endif closing the $name guard"
    }
    if ($expected -notcontains $name) {
        Add-Finding (& $Where $line) 'HEADER-GUARD' "guard $name should be $($expected -join ' or ')"
    }
}

$AiTrailerRegex = [regex]::new('^\s*co-authored-by:.*\b(claude|anthropic|copilot|cursor|codex|openai|chatgpt|gemini|devin)\b',
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
$AiNoteRegex = [regex]::new('generated (with|by) .*\b(claude|copilot|chatgpt|codex|cursor|gemini)\b',
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

function Test-Commits {
    $log = Invoke-Git @('log', '--format=%H%x1f%P%x1f%B%x1e', "$BaseRef..HEAD")
    $entries = ($log -join "`n") -split [char]0x1e | Where-Object { $_.Trim().Length -gt 0 }
    $count = 0
    foreach ($entry in $entries) {
        $parts = $entry.TrimStart("`n") -split [char]0x1f, 3
        if ($parts.Count -lt 3) { continue }
        $count++
        $sha = $parts[0].Trim()
        $short = $sha.Substring(0, 10)
        $parents = @($parts[1].Trim() -split '\s+' | Where-Object { $_ })
        $msgLines = @($parts[2].TrimEnd() -split "`n" | ForEach-Object { $_.TrimEnd("`r") })
        $subject = if ($msgLines.Count -gt 0) { $msgLines[0] } else { '' }
        $where = "commit $short"

        if ($parents.Count -gt 1) {
            Add-Finding $where 'COMMIT-MERGE' "merge commit; ScummVM requires linear history ('$subject')"
            continue
        }
        if ($subject -notmatch '^[A-Z_]+:') {
            Add-Finding $where 'COMMIT-PREFIX' "subject must start with a CAPS subsystem, e.g. '${EnginePrefix}: ' ('$subject')"
        } elseif ($EnginePrefix) {
            $files = Invoke-Git @('diff-tree', '--no-commit-id', '--name-only', '-r', $sha)
            if (@($files | Where-Object { $_ -like "$EngineDir/*" }).Count -gt 0 -and -not $subject.StartsWith("${EnginePrefix}:")) {
                Add-Finding $where 'COMMIT-SUBSYSTEM' "touches $EngineDir/ but the subject does not start with '${EnginePrefix}:' ('$subject')"
            }
        }
        if ($subject.Length -gt 50) {
            Add-Finding $where 'COMMIT-LENGTH' "subject is $($subject.Length) characters; the limit is 50 ('$subject')"
        }
        if ($msgLines.Count -gt 1 -and $msgLines[1].Trim().Length -gt 0) {
            Add-Finding $where 'COMMIT-BLANK' "the second line of the message must be blank"
        }
        foreach ($l in $msgLines) {
            if ($AiTrailerRegex.IsMatch($l)) {
                Add-Finding $where 'AI-TRAILER' "AI co-author trailer: '$($l.Trim())'; AI-GUIDELINES.md bars AI (co-)authorship"
            } elseif ($AiNoteRegex.IsMatch($l)) {
                Add-Finding $where 'AI-TRAILER' "AI-generated note in the message: '$($l.Trim())'; messages must be written by a human"
            }
        }
    }
    return $count
}

# ---- main ----------------------------------------------------------------

$savedEncoding = [Console]::OutputEncoding
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    if (-not $ScummvmPath) {
        Exit-WithConfigError "-ScummvmPath is required (the ScummVM checkout to check)"
    }
    if ($Scope -notin @('All', 'Changed')) {
        Exit-WithConfigError "-Scope must be All or Changed, not '$Scope'"
    }
    $Scope = if ($Scope -eq 'All') { 'All' } else { 'Changed' }
    if (-not (Test-Path -LiteralPath $ScummvmPath -PathType Container)) {
        Exit-WithConfigError "ScummvmPath '$ScummvmPath' is not a directory"
    }
    $resolved = (Resolve-Path -LiteralPath $ScummvmPath).ProviderPath
    $top = & git -C $resolved rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $top) {
        Exit-WithConfigError "ScummvmPath '$ScummvmPath' is not a git checkout"
    }
    $script:Root = [System.IO.Path]::GetFullPath(($top | Select-Object -First 1).Trim())
    $engineFull = Join-Path $script:Root ($EngineDir -replace '/', '\')
    if (-not (Test-Path -LiteralPath $engineFull -PathType Container)) {
        Exit-WithConfigError "'$script:Root' has no $EngineDir directory"
    }
    if ($Scope -eq 'Changed' -or -not $SkipCommits) {
        & git -C $script:Root rev-parse --verify --quiet "$BaseRef^{commit}" *> $null
        if ($LASTEXITCODE -ne 0) {
            Exit-WithConfigError "BaseRef '$BaseRef' does not name a commit in '$script:Root' (fetch it, or pass -BaseRef)"
        }
    }

    # Engine source files, as repo-relative forward-slash paths.
    if ($Scope -eq 'All') {
        $rel = @(Get-ChildItem -LiteralPath $engineFull -Recurse -File -Include *.cpp, *.h |
            ForEach-Object { [System.IO.Path]::GetRelativePath($script:Root, $_.FullName) -replace '\\', '/' })
    } else {
        $base = (Invoke-Git @('merge-base', $BaseRef, 'HEAD') | Select-Object -First 1).Trim()
        $rel = @(
            Invoke-Git @('diff', '--name-only', '--diff-filter=ACMR', $base, '--', $EngineDir)
            Invoke-Git @('ls-files', '--others', '--exclude-standard', '--', $EngineDir)
        ) | Where-Object { $_ -match '\.(cpp|h)$' } | Sort-Object -Unique
        $rel = @($rel | Where-Object { Test-Path -LiteralPath (Join-Path $script:Root $_) -PathType Leaf })
    }

    # Tracked files whose index copy has CRLF (the working copy may differ).
    $indexCrlf = @{}
    foreach ($l in (Invoke-Git @('ls-files', '--eol', '--', $EngineDir))) {
        if ($l -match '^i/(crlf|mixed)\s.*\t(.+)$') { $indexCrlf[$Matches[2]] = $true }
    }

    foreach ($r in ($rel | Sort-Object)) {
        Test-SourceFile (Join-Path $script:Root ($r -replace '/', '\')) $r $indexCrlf
    }

    $commitCount = 0
    if (-not $SkipCommits) { $commitCount = Test-Commits }

    foreach ($f in $script:Findings) { Write-Output $f }
    $commitNote = if ($SkipCommits) { "commits skipped" } else { "$commitCount commit(s) in $BaseRef..HEAD" }
    Write-Output ("Check-ScummvmStyle: {0} finding(s); {1} file(s) ({2}), {3}." -f $script:Findings.Count, $rel.Count, $Scope, $commitNote)
    if ($script:Findings.Count -gt 0) { exit 1 }
    exit 0
} catch {
    [Console]::Error.WriteLine("Check-ScummvmStyle: $($_.Exception.Message)")
    exit 2
} finally {
    [Console]::OutputEncoding = $savedEncoding
}
