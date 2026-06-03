#!/usr/bin/env python3
"""Parse Showdown's ``Scooby.eng`` string table into a ``{id: text}`` map.

Encoding observed in the cached file (SHA-256
``EE9BE93A024FF9B7F5EA1C2445B711FB7C13CEF61A079A4609EDF1201CBAB19B``,
2,823 bytes) and confirmed in the file's own self-describing header:

* Pure ASCII (no high-bit bytes).
* Line endings are CRLF.
* Comments: ``^`` starts a comment that runs to end-of-line. Comments
  can appear at the start of a line or after data on the same line.
* Message-ID declarations are bracketed decimal integers: ``[NNNN]``.
  IDs are zero-padded to four digits in this file.
* A ``[`` marks the **end** of the previous message text; a ``]`` marks
  the start of the next message text.
* Whitespace at the start/end of a message (including empty lines) is
  stripped — line breaks **inside** a message are preserved literally.

Usage:
    py -3 tools/parse_eng.py <path-to-Scooby.eng> [--out <path>] [--self-test]

[WP-008]: docs/work-packets/WP-008-object-ini-catalog.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from io import StringIO
from pathlib import Path

ID_RE = re.compile(r"\[\s*(\d+)\s*\]")


class ParseError(Exception):
    pass


def _strip_comments(line: str) -> str:
    """Drop everything from the first ``^`` onward."""
    i = line.find("^")
    return line if i < 0 else line[:i]


def parse_eng(text: str) -> dict[str, str]:
    """Return ``{message_id: text}`` for every ``[NNNN]`` declaration.

    IDs are returned as zero-padded strings preserving the source form so
    downstream tools can round-trip the document. Duplicate IDs are a hard
    error per the WP-008 §Failure handling parallel to ``parse_ini.py``.
    """
    messages: dict[str, str] = {}
    current_id: str | None = None
    current_buf: list[str] = []

    for raw in text.splitlines():
        stripped = _strip_comments(raw)
        m = ID_RE.search(stripped)
        if m:
            before = stripped[: m.start()]
            after = stripped[m.end():]
            if before.strip() and current_id is not None:
                current_buf.append(before)
            if current_id is not None:
                _commit(messages, current_id, current_buf)
            current_id = m.group(1).zfill(4)
            if current_id in messages:
                raise ParseError(f"duplicate message ID [{current_id}]")
            current_buf = []
            if after.strip():
                current_buf.append(after)
            continue
        if current_id is None:
            continue
        current_buf.append(stripped)

    if current_id is not None:
        _commit(messages, current_id, current_buf)
    return messages


def _commit(messages: dict[str, str], mid: str, buf: list[str]) -> None:
    body = "\n".join(buf)
    body = "\n".join(line.rstrip() for line in body.splitlines())
    messages[mid] = body.strip()


def _run_self_tests() -> int:
    failures: list[str] = []

    simple = parse_eng("[0001]\nhello world\n")
    if simple.get("0001") != "hello world":
        failures.append(f"simple parse failed: {simple!r}")

    multi = parse_eng("[0010]\nline one\nline two\n[0011]\nshort\n")
    if multi.get("0010") != "line one\nline two":
        failures.append(f"multi-line message preserved wrongly: {multi.get('0010')!r}")
    if multi.get("0011") != "short":
        failures.append(f"second message wrong: {multi.get('0011')!r}")

    commented = parse_eng("^ comment line\n[0002]\t^inline comment\nactual text\n")
    if commented.get("0002") != "actual text":
        failures.append(f"comment stripping failed: {commented!r}")

    try:
        parse_eng("[0001]\nfirst\n[0001]\nduplicate\n")
        failures.append("duplicate ID did not hard-fail")
    except ParseError:
        pass

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("self-tests OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="path to Scooby.eng")
    ap.add_argument("--out", default=None, help="write JSON to this path instead of stdout")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _run_self_tests()
    if not args.path:
        ap.error("path is required unless --self-test is set")

    text = Path(args.path).read_text(encoding="ascii", errors="replace")
    messages = parse_eng(text)

    if args.out:
        Path(args.out).write_text(json.dumps(messages, indent=2), encoding="utf-8")
        print(f"wrote {args.out}: {len(messages)} messages", file=sys.stderr)
    else:
        json.dump(messages, sys.stdout, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
