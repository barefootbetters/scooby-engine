#!/usr/bin/env python3
"""
Rich Header decoder for PE (Windows) binaries.

The Rich Header sits between the DOS stub and the PE signature in
MSVC-built Windows binaries. It records every compiler/linker tool
that contributed to the binary, identified by a 16-bit product ID
plus a 16-bit build number.

For Phase 1 / WP-001 Step 1: identifies the compiler used to build
Scooby.exe (and Phantom.exe, Jinx.exe, etc. for cross-title checks).

Usage:
    python tools/rich_header.py <path-to-PE-file> [<path2> ...]

Pass multiple files to compare toolchains across titles in one run.
Self-contained — no external dependencies (no pefile, no pip install).

The product ID table below covers the MSVC versions plausibly used
by a 2000-era Windows binary. For exhaustive coverage cross-reference
against https://github.com/dishather/richprint — that repo carries
the canonical community-maintained product-ID database.
"""

import struct
import sys

# Product ID -> human name. High-confidence subset; unknowns print as hex.
PRODUCT_IDS = {
    0x0000: "Unknown / imported from .obj",
    0x0001: "Imported from .lib",
    0x0002: "Linker (link.exe)",
    0x0004: "cvtres",
    0x0006: "cvtres (VS 6 era)",
    0x000A: "Linker 5.10",
    0x000B: "MASM 6.13",
    0x000C: "MSVC 5.0 C",
    0x000D: "MSVC 5.0 C++",
    0x000E: "MSVC 5.0 linker",
    0x000F: "VS97 / MSVC 5.0",
    0x0015: "MSVC 6.0 C",
    0x0016: "MSVC 6.0 C++",
    0x0017: "VS98 / MSVC 6.0",
    0x0018: "MSVC 6.0 RC",
    0x0019: "MSVC 6.0 MASM",
    0x001A: "MSVC 6.0 linker",
    0x001B: "MSVC 6.0 implib",
    0x001C: "MSVC 6.0 SP5 update",
    0x005A: "MSVC 7.0 (VS .NET 2002)",
    0x005C: "MSVC 7.0 linker",
    0x005D: "MSVC 7.0 C/C++",
    0x0078: "MSVC 7.1 (VS .NET 2003)",
}

# Build numbers worth annotating when seen.
KNOWN_BUILDS = {
    8168: "MSVC 6.0 SP3 era",
    8447: "MSVC 6.0 SP5/SP6 final",
    9210: "VS .NET 2002 (MSVC 7.0)",
    9466: "VS .NET 2003 (MSVC 7.1)",
}

# Linker product IDs — used to derive the summary verdict.
LINKER_IDS = {0x0002, 0x000E, 0x001A, 0x005C}


def decode_rich_header(path):
    """
    Return (entries, xor_key, error_str).
    On success entries is a list of (prod_id, build, use_count); error_str is None.
    On failure entries is None; error_str describes the problem.
    """
    with open(path, "rb") as f:
        data = f.read()

    if len(data) < 2 or data[:2] != b"MZ":
        return None, None, "Not a PE file (missing MZ magic bytes)."

    rich_pos = data.find(b"Rich")
    if rich_pos == -1:
        return None, None, "No 'Rich' marker — binary may not be MSVC, or header is stripped."

    xor_key = struct.unpack("<I", data[rich_pos + 4: rich_pos + 8])[0]
    dans_marker = struct.pack("<I", 0x536E6144 ^ xor_key)  # "DanS" XOR key
    dans_pos = data.rfind(dans_marker, 0, rich_pos)
    if dans_pos == -1:
        return None, None, "Found 'Rich' but no matching 'DanS' start marker."

    # Skip "DanS" + 3 padding dwords (all encode to zero after XOR).
    pos = dans_pos + 16
    entries = []
    while pos + 8 <= rich_pos:
        a, b = struct.unpack("<II", data[pos: pos + 8])
        comp_id = a ^ xor_key
        use_count = b ^ xor_key
        prod_id = (comp_id >> 16) & 0xFFFF
        build = comp_id & 0xFFFF
        entries.append((prod_id, build, use_count))
        pos += 8

    if not entries:
        return None, None, "DanS and Rich markers found but no entries between them."

    return entries, xor_key, None


def verdict(entries):
    """Return a one-line toolchain summary suitable for logging."""
    # Prefer the linker entry — it most directly names the VS version.
    linker_entries = [(p, b, c) for p, b, c in entries if p in LINKER_IDS]
    candidates = linker_entries if linker_entries else entries

    # Pick the entry whose build number we recognise; fall back to max build.
    known = [(p, b, c) for p, b, c in candidates if b in KNOWN_BUILDS]
    if known:
        prod_id, build, _ = known[0]
    else:
        prod_id, build, _ = max(candidates, key=lambda e: e[1])

    name = PRODUCT_IDS.get(prod_id, f"unknown product 0x{prod_id:04x}")
    build_note = KNOWN_BUILDS.get(build, f"build {build}")
    return f"{name}, build {build} — {build_note}"


def report(path):
    entries, xor_key, err = decode_rich_header(path)
    print(f"\nRich Header — {path}")
    if err:
        print(f"  RESULT: {err}")
        return False

    print(f"  XOR key = 0x{xor_key:08x}  |  {len(entries)} entries")
    print()
    print(f"  {'prod_id':>8}  {'build':>6}  {'count':>6}  description")
    print(f"  {'-'*8}  {'-'*6}  {'-'*6}  {'-'*50}")
    for prod_id, build, count in entries:
        name = PRODUCT_IDS.get(prod_id, f"unknown 0x{prod_id:04x}")
        note = KNOWN_BUILDS.get(build, "")
        desc = name + (f"  [{note}]" if note else "")
        print(f"   0x{prod_id:04x}   {build:>6}  {count:>6}  {desc}")

    print(f"\n  Verdict: {verdict(entries)}")
    return True


def main(paths):
    ok = True
    for path in paths:
        ok = report(path) and ok
    print()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/rich_header.py <path-to-PE-file> [<path2> ...]")
        sys.exit(1)
    main(sys.argv[1:])
