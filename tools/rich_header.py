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

Product IDs are the 16-bit `prodid` values of Microsoft's internal enum.
The names in PRODUCT_IDS are that enum's own (`Utc12_CPP`, `Linker600`, ...),
as tabulated in kirschju/richheader `prodids.py` (2017); the descriptions
follow the community richprint database
(https://github.com/dishather/richprint, `comp_id.txt`), whose empirical
comp.id entries from known Visual Studio builds agree with the enum.
Unrecognised IDs print as "unknown 0x..." so the script never lies
confidently.

v3 (2026-11-14): the v1/v2 table was wrong for most of the IDs these games
use. It called 0x000A (Utc12_C, the VC++ 6.0 C compiler)
"Linker 5.10", 0x000B (Utc12_CPP, VC++ 6.0 C++) "MASM 6.13", 0x000E
(MASM 6.13) "Cvtomf 5.10", 0x000C (AliasObj60) "MASM 6.14", 0x0004
(Linker600 import/export records) "cvtres" and 0x0013 (Linker512
import/export records) "MSVC 5.0 C++". That produced a false "Visual C++
5.0" reading for every Scooby-Doo title. The PE optional header of every
one of them says linker 6.00.

The verdict no longer looks for a linker in the Rich Header. VC6-era
link.exe does not record itself there; the Linker* product IDs that do
appear are import/export records inside the .lib files that were linked
in. The linker version comes from the PE optional header
(MajorLinkerVersion.MinorLinkerVersion), which link.exe writes itself.

Build numbers are reported as-is, with no build-to-Service-Pack mapping:
v1 mapped cvtres build 8447 to "VC6 SP5/SP6", and that build also ships
in standalone Platform SDKs. Interpretation is left to the reader, with
richprint as the reference.
"""

import struct
import sys

# prodid -> "EnumName: description". Names are Microsoft's prodid enum;
# descriptions follow richprint. Low range only (VC5 to VS2003 era).
PRODUCT_IDS = {
    0x0000: "Unknown: unmarked objects (old)",
    0x0001: "Import0: import records with no comp.id (DLL imports from .lib)",
    0x0002: "Linker510: VC++ 5.0 linker 5.10 (import/export records)",
    0x0003: "Cvtomf510: VC++ 5.0 OMF-to-COFF converter",
    0x0004: "Linker600: VC++ 6.0 linker 6.00 (import/export records)",
    0x0005: "Cvtomf600: VC++ 6.0 OMF-to-COFF converter",
    0x0006: "Cvtres500: cvtres 5.00 resource converter (VC5/VC6)",
    0x0007: "Utc11_Basic: VC 5.0 Basic compiler",
    0x0008: "Utc11_C: VC++ 5.0 C compiler",
    0x0009: "Utc12_Basic: VC 6.0 Basic compiler",
    0x000A: "Utc12_C: VC++ 6.0 C compiler",
    0x000B: "Utc12_CPP: VC++ 6.0 C++ compiler",
    0x000C: "AliasObj60: VC 6.0 alias object (OLDNAMES.LIB)",
    0x000D: "VisualBasic60: Visual Basic 6.0",
    0x000E: "Masm613: MASM 6.13",
    0x000F: "Masm710: MASM 7.10",
    0x0010: "Linker511: linker 5.11",
    0x0011: "Cvtomf511: OMF converter 5.11",
    0x0012: "Masm614: MASM 6.14",
    0x0013: "Linker512: linker 5.12 (import/export records)",
    0x0014: "Cvtomf512: OMF converter 5.12",
    0x0015: "Utc12_C_Std: VC++ 6.0 Standard C compiler",
    0x0016: "Utc12_CPP_Std: VC++ 6.0 Standard C++ compiler",
    0x0017: "Utc12_C_Book: VC++ 6.0 Learning Edition C compiler",
    0x0018: "Utc12_CPP_Book: VC++ 6.0 Learning Edition C++ compiler",
    0x0019: "Implib700: VS2002 (7.0) import library records",
    0x001A: "Cvtomf700: VS2002 (7.0) OMF converter",
    0x001B: "Utc13_Basic: VS2002 (7.0) Basic compiler",
    0x001C: "Utc13_C: VS2002 (7.0) C compiler",
    0x001D: "Utc13_CPP: VS2002 (7.0) C++ compiler",
    0x001E: "Linker610: linker 6.10",
    0x001F: "Cvtomf610: OMF converter 6.10",
    0x0020: "Linker601: linker 6.01",
    0x0021: "Cvtomf601: OMF converter 6.01",
    0x0022: "Utc12_1_Basic: VC 6.1 Basic compiler",
    0x0023: "Utc12_1_C: VC++ 6.1 C compiler",
    0x0024: "Utc12_1_CPP: VC++ 6.1 C++ compiler",
    0x0025: "Linker620: linker 6.20",
    0x0026: "Cvtomf620: OMF converter 6.20",
    0x0027: "AliasObj70: VS2002 (7.0) alias object",
    0x0028: "Linker621: linker 6.21",
    0x0029: "Cvtomf621: OMF converter 6.21",
    0x002A: "Masm615: MASM 6.15",
    0x002B: "Utc13_LTCG_C: VS2002 (7.0) LTCG C",
    0x002C: "Utc13_LTCG_CPP: VS2002 (7.0) LTCG C++",
    0x002D: "Masm620: MASM 6.20",
    0x002E: "ILAsm100: .NET 1.0 IL assembler",
    0x002F: "Utc12_2_Basic: VC 6.0 Processor Pack Basic compiler",
    0x0030: "Utc12_2_C: VC++ 6.0 Processor Pack C compiler",
    0x0031: "Utc12_2_CPP: VC++ 6.0 Processor Pack C++ compiler",
    0x0032: "Utc12_2_C_Std: VC++ 6.0 Processor Pack Standard C compiler",
    0x0033: "Utc12_2_CPP_Std: VC++ 6.0 Processor Pack Standard C++ compiler",
    0x0034: "Utc12_2_C_Book: VC++ 6.0 Processor Pack Learning Edition C",
    0x0035: "Utc12_2_CPP_Book: VC++ 6.0 Processor Pack Learning Edition C++",
    0x0036: "Implib622: import library records 6.22",
    0x0037: "Cvtomf622: OMF converter 6.22",
    0x0038: "Cvtres501: cvtres 5.01 resource converter",
    0x0039: "Utc13_C_Std: VS2002 (7.0) Standard C compiler",
    0x003A: "Utc13_CPP_Std: VS2002 (7.0) Standard C++ compiler",
    0x003B: "Cvtpgd1300: VS2002 (7.0) PGD converter",
    0x003C: "Linker622: linker 6.22",
    0x003D: "Linker700: VS2002 (7.0) linker",
    0x003E: "Export622: export records 6.22",
    0x003F: "Export700: VS2002 (7.0) export records",
    0x005D: "Implib710: VS2003 (7.10) import library records",
}

# Product IDs that are compilers (Utc* families): the objects compiled
# from source. The verdict lists these; everything else (import records,
# alias objects, assemblers, converters) is library or tooling residue.
COMPILER_IDS = {0x0007, 0x0008, 0x0009, 0x000A, 0x000B, 0x0015, 0x0016,
                0x0017, 0x0018, 0x001B, 0x001C, 0x001D, 0x0022, 0x0023,
                0x0024, 0x002B, 0x002C, 0x002F, 0x0030, 0x0031, 0x0032,
                0x0033, 0x0034, 0x0035, 0x0039, 0x003A}


def linker_version(data):
    """
    Return "major.minor" from the PE optional header, or None.
    link.exe writes MajorLinkerVersion / MinorLinkerVersion itself, so this
    is the direct signal for which linker produced the image.
    """
    if len(data) < 0x40:
        return None
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if pe + 26 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        return None
    opt = pe + 24
    return f"{data[opt + 2]}.{data[opt + 3]:02d}"


def decode_rich_header(data):
    """
    Return (entries, xor_key, error_str).
    On success entries is a list of (prod_id, build, use_count); error_str is None.
    On failure entries is None; error_str describes the problem.
    """
    if len(data) < 2 or data[:2] != b"MZ":
        return None, None, "Not a PE file (missing MZ magic bytes)."

    rich_pos = data.find(b"Rich")
    if rich_pos == -1:
        return None, None, "No 'Rich' marker: binary may not be MSVC, or header is stripped."

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


def short_name(prod_id):
    name = PRODUCT_IDS.get(prod_id)
    return name.split(":")[0] if name else f"unknown 0x{prod_id:04x}"


def verdict(entries, linker):
    """
    Return a one-line toolchain summary suitable for logging: the PE
    header's linker version, then every compiler entry, most objects first.
    """
    compilers = sorted((e for e in entries if e[0] in COMPILER_IDS),
                       key=lambda e: -e[2])
    parts = [f"{short_name(p)} {b} (x{c})" for p, b, c in compilers]
    head = f"Linker {linker} (PE header)" if linker else "Linker unknown"
    return head + "; compilers: " + (", ".join(parts) if parts else "none recorded")


def report(path):
    with open(path, "rb") as f:
        data = f.read()
    entries, xor_key, err = decode_rich_header(data)
    print(f"\nRich Header: {path}")
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

    print(f"\n  Verdict: {verdict(entries, linker_version(data))}")
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
