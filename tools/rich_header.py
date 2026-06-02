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

Product ID mappings are sourced from the community-maintained richprint
database (https://github.com/dishather/richprint). Only high-confidence
entries are encoded here; unrecognised IDs print as "unknown 0x..." so
the script never lies confidently.

Build-number annotations were removed in the v2 revision after a false
positive: cvtres build 8447 ships with both VC6 SP5/SP6 AND with standalone
Platform SDK releases, which caused non-VC6 binaries to be falsely
reported as "MSVC 6.0 SP5/SP6 final". The verdict line now reports the
linker product + build without trying to map build numbers to Service
Packs — that interpretation is left to the human reader.
"""

import struct
import sys

# Product ID → human name. High-confidence entries only.
# Anything not listed prints as "unknown 0x..." rather than risk a wrong label.
PRODUCT_IDS = {
    # Generic markers
    0x0000: "Unknown / imported from .obj",
    0x0001: "Imported from .lib",

    # Resource / OMF converters
    0x0004: "cvtres",
    0x000E: "Cvtomf 5.10 (OMF→COFF)",
    0x0010: "Cvtomf 6.00",
    0x0011: "Cvtres 5.00",
    0x0018: "Cvtomf 6.10",
    0x001F: "Cvtomf 7.00",
    0x0020: "Cvtres 7.00",

    # MASM (Microsoft Macro Assembler)
    0x000B: "MASM 6.13",
    0x000C: "MASM 6.14",
    0x0022: "MASM 7.00",

    # Linkers (link.exe variants — see LINKER_IDS below)
    0x0002: "Linker (pre-5.10)",
    0x000A: "Linker 5.10 (VC 5.0)",
    0x000D: "Linker 5.11",
    0x000F: "Linker 6.00 (VC 6.0)",
    0x0017: "Linker 6.10",
    0x0019: "Linker 6.12",
    0x0021: "Linker 7.00 (VS .NET 2002)",

    # MSVC C/C++ compilers (Utc backend, indexed by VS version)
    0x0012: "MSVC 5.0 C (Utc11_C)",
    0x0013: "MSVC 5.0 C++ (Utc11_CPP)",
    0x0015: "MSVC 6.0 C (Utc12_C)",
    0x0016: "MSVC 6.0 C++ (Utc12_CPP)",
    0x001A: "MSVC 6.0 C (Utc12_C_Std)",
    0x001B: "MSVC 6.0 C++ (Utc12_CPP_Std)",
    0x001C: "MSVC 6.0 C (Utc12_C_Book)",
    0x001D: "MSVC 6.0 C++ (Utc12_CPP_Book)",
    0x0023: "MSVC 7.0 C",
    0x0024: "MSVC 7.0 C++",

    # Visual Basic 6
    0x0014: "VB6 compiler (Utc12_Basic)",

    # Implib
    0x001E: "Implib 7.00",
}

# Product IDs that identify an actual linker (link.exe).
# The linker is the last tool to touch the binary and the most direct
# signal of the VS version that produced it — verdict() prefers these.
LINKER_IDS = {0x0002, 0x000A, 0x000D, 0x000F, 0x0017, 0x0019, 0x0021}

# Product IDs that are utility tools (converters, importers, resource
# tools) rather than compilers or linkers. Used by the verdict fallback
# to skip these when looking for the most-used compiler.
UTILITY_IDS = {0x0000, 0x0001, 0x0004, 0x000E, 0x0010, 0x0011,
               0x0018, 0x001E, 0x001F, 0x0020}


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
    """
    Return a one-line toolchain summary suitable for logging.

    Strategy:
      1. Prefer an actual linker entry (product_id in LINKER_IDS) — link.exe
         is the last tool to touch the binary and the cleanest VS version
         signal. Pick the linker with the highest use count if multiple.
      2. Fall back to the most-used compiler entry (skipping utility
         tools — converters, importers, .lib imports).
      3. Final fallback: most-used entry overall.

    No build-number → Service Pack annotation: the same build can appear
    across different products (cvtres 8447 ships with both VC6 SP5 and
    standalone SDKs), and that mapping caused false-positive verdicts in
    v1. Build numbers are reported as-is; interpretation is the reader's.
    """
    linker_entries = [e for e in entries if e[0] in LINKER_IDS]
    if linker_entries:
        prod_id, build, _ = max(linker_entries, key=lambda e: e[2])
    else:
        compiler_entries = [e for e in entries if e[0] not in UTILITY_IDS]
        candidates = compiler_entries if compiler_entries else entries
        prod_id, build, _ = max(candidates, key=lambda e: e[2])

    name = PRODUCT_IDS.get(prod_id, f"unknown product 0x{prod_id:04x}")
    return f"{name}, build {build}"


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
        print(f"   0x{prod_id:04x}   {build:>6}  {count:>6}  {name}")

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
