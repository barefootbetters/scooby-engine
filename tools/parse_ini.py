#!/usr/bin/env python3
"""Parse Showdown's ``object.ini`` into a structured logical asset catalog.

Locked parser mode for Gen 1 (Showdown) per [EC-004] Step 1: **MODE_A** —
every asset reference is a direct TGIFILE name-table string
(``ROOM_*``, ``ANIM_*``); ``OBJ_*`` appears only as section headers.

Schema (v1) is enumerated in [WP-008] §Output schema. Failure handling
policy (warn / preserve / hard-fail) is enumerated in [WP-008] §Failure
handling. Both are enforced literally below.

The ``object.ini`` Showdown ships does not declare top-level ``[ROOM_*]``,
``[CURSOR_*]``, or ``[INVENTORY_*]`` sections: it is a flat list of 215
``[OBJ_*]`` entries discriminated by an ``ID=`` field. The catalog's
``rooms`` / ``cursors`` / ``inventory`` buckets are therefore synthesized
during the post-parse cross-reference pass.

Usage:
    py -3 tools/parse_ini.py <path-to-object.ini> [--out <path>] [--self-test]

[EC-004]: docs/execution-checklists/EC-004-object-ini-catalog.md
[WP-008]: docs/work-packets/WP-008-object-ini-catalog.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from io import StringIO
from pathlib import Path

SECTION_RE = re.compile(r"^\[([^\]]+)\]\s*$")
KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

KNOWN_OBJECT_TYPES = {
    "exitobject",
    "clickableobject",
    "inventoryobject",
    "requiresobject",
    "simpleobject",
}

KNOWN_KEYS_BY_TYPE = {
    "exitobject": {
        "ID", "rolloveranim", "destinationroom", "movie", "scrappyid",
        "scene", "character", "direction",
        "fred", "daphne", "velma", "scooby", "shaggy",
    },
    "clickableobject": {
        "ID", "sequence", "priority", "layer", "rolloveranim", "scrappyid",
    },
    "inventoryobject": {
        "ID", "toolbaranim", "usecursor",
        "pickupanim", "pickupsfx", "pickupmovie",
    },
    "requiresobject": {
        "ID", "requiredanim",
    },
    "simpleobject": {
        "ID", "sequence", "priority", "layer",
    },
}

ASSET_KEYS = {
    "rolloveranim", "destinationroom",
    "toolbaranim", "usecursor", "requiredanim",
    "pickupanim",
}

SENTINEL_VALUES = {"<none>", "-1", ""}

class ParseError(Exception):
    """Raised when ``object.ini`` cannot be parsed safely.

    Per [WP-008] §Failure handling: malformed lines inside known sections,
    duplicate IDs, and section-header lookalikes outside a section are
    hard failures, not warnings.
    """


def parse_object_ini(text: str) -> dict:
    """Parse the raw INI text into the v1 catalog schema."""
    objects: dict[str, dict] = {}
    unknown_sections: list[str] = []
    warnings: list[str] = []

    current_id: str | None = None
    current_entry: dict | None = None
    in_unknown_section = False

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith(";") or line.startswith("#"):
            continue
        m = SECTION_RE.match(line)
        if m:
            sec = m.group(1)
            if not sec.startswith("OBJ_"):
                warnings.append(
                    f"line {lineno}: unknown section [{sec}] (kept under unknown_sections)"
                )
                unknown_sections.append(sec)
                current_id = None
                current_entry = None
                in_unknown_section = True
                continue
            if sec in objects:
                raise ParseError(
                    f"line {lineno}: duplicate section [{sec}] — WP-008 §Failure "
                    f"handling requires hard-fail on duplicate IDs"
                )
            current_id = sec
            current_entry = {
                "id": sec,
                "type": None,
                "raw": {},
                "extra_fields": {},
            }
            objects[sec] = current_entry
            in_unknown_section = False
            continue
        if in_unknown_section:
            continue
        kv = KV_RE.match(line)
        if not kv:
            raise ParseError(
                f"line {lineno}: unparseable line {line!r} — WP-008 §Failure "
                f"handling requires hard-fail inside known sections"
            )
        if current_entry is None:
            raise ParseError(
                f"line {lineno}: key/value {line!r} appears before any section header"
            )
        key, value = kv.group(1), kv.group(2).strip()
        current_entry["raw"][key] = value
        if key == "ID":
            if value not in KNOWN_OBJECT_TYPES:
                warnings.append(
                    f"line {lineno}: [{current_id}] has unknown ID={value!r}"
                )
            current_entry["type"] = value
            continue
        known_keys = KNOWN_KEYS_BY_TYPE.get(current_entry["type"], set())
        if known_keys and key not in known_keys:
            current_entry["extra_fields"][key] = value

    catalog = _build_catalog(objects, unknown_sections, warnings)
    _validate_schema(catalog)
    return catalog


def _build_catalog(
    objects: dict[str, dict],
    unknown_sections: list[str],
    warnings: list[str],
) -> dict:
    rooms: dict[str, dict] = {}
    cursors: dict[str, dict] = {}
    inventory: dict[str, dict] = {}
    final_objects: dict[str, dict] = {}

    for obj_id, entry in objects.items():
        raw = entry["raw"]
        otype = entry["type"]

        room_id = None
        graphics = _collect_assets(raw, ("rolloveranim", "toolbaranim", "pickupanim"))
        sounds = _collect_assets(raw, ("pickupsfx",))
        cursor_ref = raw.get("usecursor") or raw.get("requiredanim")
        if cursor_ref in SENTINEL_VALUES:
            cursor_ref = None

        final_objects[obj_id] = {
            "id": obj_id,
            "type": otype,
            "room": room_id,
            "graphics": graphics,
            "sounds": sounds,
            "cursor": cursor_ref,
            "extra_fields": entry["extra_fields"],
        }

        for anim_key in ("rolloveranim", "toolbaranim", "usecursor", "requiredanim", "pickupanim"):
            ref = raw.get(anim_key)
            if ref and ref not in SENTINEL_VALUES and ref.startswith("ANIM_CURSOR"):
                cursors.setdefault(ref, {"id": ref, "referenced_by": []})
                cursors[ref]["referenced_by"].append(obj_id)

        dest = raw.get("destinationroom")
        if dest and dest not in SENTINEL_VALUES:
            rooms.setdefault(dest, {
                "id": dest,
                "name": None,
                "background_assets": [],
                "objects": [],
                "exits": {},
            })

        if otype == "inventoryobject":
            inventory[obj_id] = {
                "id": obj_id,
                "graphics": graphics,
                "cursor": cursor_ref,
            }

        if dest and dest not in SENTINEL_VALUES and otype == "exitobject":
            rooms[dest]["incoming_exits"] = rooms[dest].get("incoming_exits", [])
            rooms[dest]["incoming_exits"].append(obj_id)

    return {
        "schema_version": "v1",
        "source": {
            "file": "object.ini",
            "title": "Showdown (Gen 1)",
        },
        "counts": {
            "objects": len(final_objects),
            "rooms": len(rooms),
            "cursors": len(cursors),
            "inventory": len(inventory),
            "unknown_sections": len(unknown_sections),
        },
        "rooms": rooms,
        "objects": final_objects,
        "cursors": cursors,
        "inventory": inventory,
        "unknown_sections": unknown_sections,
        "warnings": warnings,
    }


def _collect_assets(raw: dict, keys: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for k in keys:
        v = raw.get(k)
        if v and v not in SENTINEL_VALUES:
            out.append(v)
    return out


def _validate_schema(catalog: dict) -> None:
    required_top = {"rooms", "objects", "cursors", "inventory"}
    missing = required_top - catalog.keys()
    if missing:
        raise ParseError(f"output schema (v1) missing keys: {sorted(missing)}")
    for obj_id, obj in catalog["objects"].items():
        for k in ("id", "type", "room", "graphics", "sounds", "cursor", "extra_fields"):
            if k not in obj:
                raise ParseError(f"object {obj_id} missing required key {k!r}")


def asset_references(catalog: dict) -> list[str]:
    """Return every asset-name reference in the catalog (deduped, sorted).

    Used by the WP-003 name-table cross-check. Skips numeric / sentinel
    values; the ``OBJ_*`` section headers themselves are included since
    they are 1:1 with TGIFILE.ART OBJ name-table entries per WP-003.
    """
    refs: set[str] = set()
    refs.update(catalog["objects"].keys())
    for obj in catalog["objects"].values():
        refs.update(obj["graphics"])
        refs.update(obj["sounds"])
        if obj["cursor"]:
            refs.add(obj["cursor"])
    for room_id in catalog["rooms"]:
        refs.add(room_id)
    for cursor_id in catalog["cursors"]:
        refs.add(cursor_id)
    return sorted(refs)


def load_name_table(path: Path) -> set[str]:
    """Read the WP-003 name-table dump and return the set of names.

    The file is the output of [tools/probe_art_names.py][1] (or its
    equivalent recipe in [tgifile-art.md §Pre-payload region][2]) — a
    columnar listing with a header block of comments and one record per
    line; the trailing whitespace-separated token on each record line is
    the name. ``ROOM_*`` / ``OBJ_*`` / ``ANIM_*`` are the prefixes WP-003
    observed.

    [1]: docs/work-packets/WP-003-pre-payload-region.md
    [2]: docs/formats/tgifile-art.md#pre-payload-region--engine-name-table
    """
    names: set[str] = set()
    for raw in path.read_text(encoding="ascii", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("idx"):
            continue
        tok = line.split()[-1]
        if tok and tok[0].isalpha():
            names.add(tok)
    return names


def cross_check_against_name_table(
    catalog: dict, name_table: set[str]
) -> tuple[dict, list[str]]:
    """Compute the WP-008 §Exit criterion #6 metric.

    Returns ``(metric_dict, sorted_unmatched_list)``. The metric records
    total / matched / unmatched references and the percentage.

    Only asset-name references are counted — sentinels (``-1``, ``<none>``,
    empty) and engine-state numerics (``layer=1``) are excluded by the
    upstream ``asset_references()`` collector.
    """
    refs = asset_references(catalog)
    matched = [r for r in refs if r in name_table]
    unmatched = [r for r in refs if r not in name_table]
    total = len(refs)
    rate = (len(matched) / total * 100.0) if total else 0.0
    metric = {
        "total_references": total,
        "matched": len(matched),
        "unmatched": len(unmatched),
        "match_rate_percent": round(rate, 2),
        "name_table_size": len(name_table),
    }
    return metric, sorted(unmatched)


def _run_self_tests() -> int:
    failures: list[str] = []

    dup = StringIO(
        "[OBJ_A]\nID=clickableobject\nsequence=\n"
        "[OBJ_A]\nID=clickableobject\nsequence=\n"
    ).getvalue()
    try:
        parse_object_ini(dup)
        failures.append("duplicate-ID input did not hard-fail")
    except ParseError:
        pass

    unknown_key = parse_object_ini(
        "[OBJ_X]\nID=clickableobject\nsequence=\nmysteryfield=42\n"
    )
    extra = unknown_key["objects"]["OBJ_X"]["extra_fields"]
    if extra.get("mysteryfield") != "42":
        failures.append(f"unknown key not preserved in extra_fields: got {extra!r}")

    try:
        parse_object_ini("[OBJ_BAD]\nID=clickableobject\nthis line has no equals sign\n")
        failures.append("malformed-line input did not hard-fail")
    except ParseError:
        pass

    unknown_section = parse_object_ini(
        "[GLOBAL]\nsomekey=somevalue\n[OBJ_OK]\nID=simpleobject\n"
    )
    if "GLOBAL" not in unknown_section["unknown_sections"]:
        failures.append(
            f"unknown section did not land in unknown_sections: got "
            f"{unknown_section['unknown_sections']!r}"
        )

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("self-tests OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="path to object.ini")
    ap.add_argument("--out", default=None, help="write JSON to this path instead of stdout")
    ap.add_argument("--self-test", action="store_true", help="run synthetic-input failure-handling checks")
    ap.add_argument("--catalog", action="store_true", help="build the combined catalog (object.ini + Scooby.eng + WP-003 cross-check)")
    ap.add_argument("--eng", default=None, help="path to Scooby.eng (catalog mode)")
    ap.add_argument("--name-table", default=None, help="path to wp003-name-table.txt (catalog mode)")
    ap.add_argument("--unmatched-out", default=None, help="write the unmatched-asset list to this path (catalog mode)")
    args = ap.parse_args()

    if args.self_test:
        return _run_self_tests()

    if not args.path:
        ap.error("path is required unless --self-test is set")

    text = Path(args.path).read_text(encoding="ascii", errors="replace")
    catalog = parse_object_ini(text)

    if args.catalog:
        if not args.eng or not args.name_table:
            ap.error("--catalog requires --eng and --name-table")
        from parse_eng import parse_eng as parse_eng_fn
        eng_text = Path(args.eng).read_text(encoding="ascii", errors="replace")
        messages = parse_eng_fn(eng_text)
        message_id_pattern = re.compile(r"^\d{1,4}$")
        resolved_count = 0
        for obj in catalog["objects"].values():
            for k, v in list(obj["extra_fields"].items()):
                if isinstance(v, str) and message_id_pattern.match(v):
                    mid = v.zfill(4)
                    if mid in messages:
                        obj["extra_fields"][f"{k}__text"] = messages[mid]
                        resolved_count += 1
        catalog["messages"] = messages
        catalog["counts"]["messages"] = len(messages)
        catalog["counts"]["object_ini_to_eng_resolutions"] = resolved_count

        name_table = load_name_table(Path(args.name_table))
        metric, unmatched = cross_check_against_name_table(catalog, name_table)
        catalog["wp003_cross_check"] = metric
        catalog["wp003_unmatched"] = unmatched

        if args.unmatched_out:
            Path(args.unmatched_out).write_text(
                "\n".join(unmatched) + ("\n" if unmatched else ""),
                encoding="utf-8",
            )

    if args.out:
        Path(args.out).write_text(json.dumps(catalog, indent=2), encoding="utf-8")
        print(
            f"wrote {args.out}: {catalog['counts']}",
            file=sys.stderr,
        )
        if args.catalog:
            print(f"cross-check: {catalog['wp003_cross_check']}", file=sys.stderr)
    else:
        json.dump(catalog, sys.stdout, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
