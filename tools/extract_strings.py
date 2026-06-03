"""Extract printable ANSI + UTF-16LE strings (>=6 chars) from a PE binary.

Writes deterministic, sorted, deduplicated lists to <binary_dir>/strings-ansi.txt
and <binary_dir>/strings-wide.txt. Output is byte-identical across runs against
the same input.

Usage:
    python extract_strings.py <path-to-exe>

Used by WP-007 (docs/work-packets/WP-007-strings-and-imports.md). Outputs are
local-only per tools/exes/README.md (gitignored).
"""

import re
import sys
from pathlib import Path

ASCII_RE = re.compile(rb'[\x20-\x7E]{6,}')
UTF16LE_RE = re.compile(rb'(?:[\x20-\x7E]\x00){6,}')


def extract(path):
    data = Path(path).read_bytes()
    ansi = {m.group().decode('ascii').strip() for m in ASCII_RE.finditer(data)}
    wide = {m.group().decode('utf-16le').strip() for m in UTF16LE_RE.finditer(data)}
    return sorted(s for s in ansi if s), sorted(s for s in wide if s)


def main():
    exe = sys.argv[1]
    out_dir = Path(exe).parent
    ansi, wide = extract(exe)
    (out_dir / 'strings-ansi.txt').write_text('\n'.join(ansi), encoding='utf-8')
    (out_dir / 'strings-wide.txt').write_text('\n'.join(wide), encoding='utf-8')
    print(f'{exe}: ansi={len(ansi)} wide={len(wide)}')


if __name__ == '__main__':
    main()
