"""Extract the PE import table from a binary, normalized to DLL::Function lines.

Writes a deterministic, sorted, deduplicated list to <binary_dir>/imports.txt.
Ordinal-only entries appear as DLL::ord#N. Sort is case-insensitive, by
(DLL name, function name).

Usage:
    python extract_imports.py <path-to-exe>

Requires: pip install pefile

Used by WP-007 (docs/work-packets/WP-007-strings-and-imports.md). Outputs are
local-only per tools/exes/README.md (gitignored).
"""

import sys
from pathlib import Path

import pefile


def extract(exe):
    pe = pefile.PE(exe)
    lines = set()
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode(errors='ignore')
        for imp in entry.imports:
            name = imp.name.decode(errors='ignore') if imp.name else f'ord#{imp.ordinal}'
            lines.add(f'{dll}::{name}')
    return sorted(lines, key=lambda s: (s.split('::', 1)[0].lower(), s.split('::', 1)[1].lower()))


def main():
    exe = sys.argv[1]
    out = Path(exe).parent / 'imports.txt'
    lines = extract(exe)
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{exe}: {len(lines)} imports -> {out}')


if __name__ == '__main__':
    main()
