#!/usr/bin/env python3
"""Decode Gen 1 (Showdown) ``TGIFILE.ART`` sprites and room backgrounds to PNG.

WP-002 deliverable. The format is documented in
``docs/formats/tgifile-art.md`` (sections "Archive layout", "Object
resources", "Scene blocks", "Cel format"). Summary:

* Header: ``u32 scene_count`` (69), ``u32[69]`` scene descriptors,
  ``u32 object_count`` (453), ``8-byte[453]`` object descriptors, then the
  name table (0x0F60...). None of the descriptor values are file offsets.
* Object resources start at file offset 0x20000. There are ``object_count``
  of them, packed back to back, each padded to a 2048-byte sector. Resource
  ``i`` is the art for name-table ``OBJ`` id ``i``.
* Scene blocks (room backgrounds plus object placement lists) follow the last
  object resource, ``scene_count`` of them, each sector padded. The last one
  ends exactly at end of file.
* Every image (sprite cel or background) is a "cel": a 24-byte header
  ``u32 size, u16 w, u16 h, u32 mask_a, u32 mask_b, u32 0x100, u32 0``
  followed by an RLE stream of 16-bit pixels. Byte ``0xF0`` starts a run
  (``F0 count hi lo``); any other byte starts a literal pixel (``hi lo``).
  Pixels are RGB565 stored big-endian. In sprites, 0x0000 is transparent.

Outputs go to ``tools/samples/`` by default, which is gitignored: decoded
images are copyrighted derivatives and are never committed (see
``tools/samples/README.md``).

Usage (PowerShell):
    py -3 tools/probe_art.py --list
    py -3 tools/probe_art.py --obj 0                # every cel of OBJ id 0
    py -3 tools/probe_art.py --obj 1 --cel 0
    py -3 tools/probe_art.py --scene 0
    py -3 tools/probe_art.py --verify               # decode every cel in the file

Requires Pillow for PNG output (``--list`` and ``--verify`` do not).
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ART = REPO / "tools" / "exes" / "showdown" / "TGIFILE.ART"
DEFAULT_OUT = REPO / "tools" / "samples"
SHOWDOWN_SHA256 = "B3006E127B4EFA19CF419E92A97A8AA0A565378243CBE396ABA9707F3310C807"

SECTOR = 0x800
OBJECTS_START = 0x20000
NAME_TABLE_START = 0x0F60
NAME_RECORD = 68
CEL_HEADER = 24
RUN_MARKER = 0xF0


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def align(off: int) -> int:
    return (off + SECTOR - 1) // SECTOR * SECTOR


@dataclass
class Cel:
    offset: int  # absolute file offset of the cel header
    size: int
    width: int
    height: int
    mask_a: int
    mask_b: int
    flags: int
    reserved: int


@dataclass
class ObjectResource:
    index: int
    offset: int
    size: int
    tables: list[tuple[int, int]]  # four (count, offset) pairs, offsets resource-relative

    @property
    def cel_offsets(self) -> list[int]:
        count, table = self.tables[3]
        return [self.offset + u32(ART, self.offset + table + 4 * i) for i in range(count)]


@dataclass
class SceneBlock:
    index: int
    offset: int
    size: int
    scene_id: int
    width: int
    height: int
    placements: int  # count of object placement records
    cel_offset: int


ART: bytes = b""


def load(path: Path, check_hash: bool) -> None:
    global ART
    ART = path.read_bytes()
    if check_hash:
        digest = hashlib.sha256(ART).hexdigest().upper()
        if digest != SHOWDOWN_SHA256:
            print(f"warning: SHA-256 {digest} is not the documented Showdown copy", file=sys.stderr)


def obj_names() -> dict[int, str]:
    """Map OBJ id -> name from the 68-byte name-table records (WP-003)."""
    names: dict[int, str] = {}
    p = NAME_TABLE_START
    while p + NAME_RECORD <= OBJECTS_START:
        rid = u32(ART, p)
        raw = ART[p + 4 : p + 48].split(b"\0", 1)[0]
        if not raw or not raw.isascii() or not raw[:1].isalpha():
            break
        if rid >> 24 == 0x20:
            names.setdefault(rid & 0xFFFFFF, raw.decode("ascii"))
        p += NAME_RECORD
    return names


def objects() -> list[ObjectResource]:
    count = u32(ART, 0x118)
    out = []
    p = OBJECTS_START
    for i in range(count):
        v = struct.unpack_from("<9I", ART, p)
        tables = [(v[1 + 2 * k], v[2 + 2 * k]) for k in range(4)]
        # Integrity: the four tables are contiguous u32 arrays ending at size.
        end = tables[0][1]
        for c, o in tables:
            if o != end:
                raise ValueError(f"object {i} at {p:#x}: table chain broken")
            end = o + 4 * c
        if end != v[0]:
            raise ValueError(f"object {i} at {p:#x}: tables end {end:#x} != size {v[0]:#x}")
        out.append(ObjectResource(i, p, v[0], tables))
        p = align(p + v[0])
    return out


def scenes(after: int) -> list[SceneBlock]:
    count = u32(ART, 0)
    out = []
    p = after
    for i in range(count):
        size = u32(ART, p)
        scene_id, w, h = struct.unpack_from("<HHH", ART, p + 10)
        placements, first = struct.unpack_from("<II", ART, p + 0xC0)
        cel = p + first + 148 * placements  # 148-byte placement records
        out.append(SceneBlock(i, p, size, scene_id, w, h, placements, cel))
        p = align(p + size)
    if p != len(ART):
        raise ValueError(f"scene walk ended at {p:#x}, file is {len(ART):#x}")
    return out


def read_cel(off: int) -> Cel:
    return Cel(off, *struct.unpack_from("<IHHIIII", ART, off))


def decode(cel: Cel) -> tuple[list[int], int]:
    """Return (big-endian RGB565 pixel words, RLE bytes consumed)."""
    want = cel.width * cel.height
    px: list[int] = []
    q = cel.offset + CEL_HEADER
    while len(px) < want:
        if ART[q] == RUN_MARKER:
            px.extend([(ART[q + 2] << 8) | ART[q + 3]] * ART[q + 1])
            q += 4
        else:
            px.append((ART[q] << 8) | ART[q + 1])
            q += 2
    if len(px) != want:
        raise ValueError(f"cel at {cel.offset:#x}: run overran image by {len(px) - want} px")
    return px, q - cel.offset - CEL_HEADER


def rgb(v: int) -> tuple[int, int, int]:
    return ((v >> 11 & 31) * 255 // 31, (v >> 5 & 63) * 255 // 63, (v & 31) * 255 // 31)


def save_png(cel: Cel, path: Path, transparent: bool) -> None:
    from PIL import Image

    px, _ = decode(cel)
    if transparent:
        im = Image.new("RGBA", (cel.width, cel.height))
        im.putdata([(*rgb(v), 0 if v == 0 else 255) for v in px])
    else:
        im = Image.new("RGB", (cel.width, cel.height))
        im.putdata([rgb(v) for v in px])
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    print(f"wrote {path} ({cel.width}x{cel.height})")


def safe(name: str) -> str:
    return "".join(c if c.isalnum() or c == "_" else "_" for c in name)


def mask_end(off: int) -> tuple[int, int, int]:
    """Parse a span-mask chunk; return (end offset, chunk end, rows covered).

    Chunk: u32 size, u16 x, u16 y, u16 w, u16 h, then records of
    ``u16 repeat_rows, u16 n, u16[n] runs`` (runs alternate skip/opaque).
    """
    size, _x, _y, w, h = struct.unpack_from("<IHHHH", ART, off)
    q, rows = off + 12, 0
    while rows < h:
        rep, n = struct.unpack_from("<HH", ART, q)
        runs = struct.unpack_from(f"<{n}H", ART, q + 4)
        if rep == 0 or sum(runs) > w:
            break
        rows += rep
        q += 4 + 2 * n
    return q, off + size, rows - h


def verify(objs: list[ObjectResource], scns: list[SceneBlock]) -> int:
    """Decode every cel; check each RLE stream ends where the next part begins."""
    cels = masks = runs = escaped = worst = 0
    for o in objs:
        for off in o.cel_offsets:
            c = read_cel(off)
            _, used = decode(c)
            # Sprite cels: the RLE stream ends just before the first mask
            # chunk (mask offsets are resource-relative; 0 = absent), or at
            # the end of the cel when it has no masks.
            present = [o.offset + m for m in (c.mask_a, c.mask_b) if m]
            stop = min(present) if present else off + c.size
            gap = stop - (off + CEL_HEADER + used)
            if not 0 <= gap < 4:
                print(f"OBJ {o.index} cel {off:#x}: RLE end gap {gap}")
                return 1
            worst = max(worst, gap)
            for m in present:
                end, chunk_end, extra = mask_end(m)
                if end != chunk_end or extra != 0:
                    print(f"OBJ {o.index} cel {off:#x}: mask at {m:#x} does not parse")
                    return 1
                masks += 1
            # Escape check: a literal pixel whose high byte is 0xF0 can only
            # be carried as a run of length 1.
            q, n, want = off + CEL_HEADER, 0, c.width * c.height
            while n < want:
                if ART[q] == RUN_MARKER:
                    runs += 1
                    escaped += ART[q + 1] == 1 and ART[q + 2] == RUN_MARKER
                    if ART[q + 1] == 0:
                        print(f"OBJ {o.index} cel {off:#x}: zero-length run at {q:#x}")
                        return 1
                    n += ART[q + 1]
                    q += 4
                else:
                    n += 1
                    q += 2
            cels += 1
    for s in scns:
        # Scene cels: same layout; mask offsets are relative to the scene block.
        c = read_cel(s.cel_offset)
        _, used = decode(c)
        present = [s.offset + m for m in (c.mask_a, c.mask_b) if m]
        stop = min(present) if present else s.cel_offset + c.size
        gap = stop - (s.cel_offset + CEL_HEADER + used)
        if not 0 <= gap < 4:
            print(f"scene {s.index}: RLE end gap {gap}")
            return 1
        worst = max(worst, gap)
        for m in present:
            end, chunk_end, extra = mask_end(m)
            if end != chunk_end or extra != 0:
                print(f"scene {s.index}: mask at {m:#x} does not parse")
                return 1
            masks += 1
        cels += 1
    print(f"verified {cels} cels ({len(objs)} objects, {len(scns)} scenes); "
          f"{masks} mask chunks parse exactly; max RLE-end gap {worst} bytes")
    print(f"sprite RLE: {runs} runs, none zero-length; {escaped} are 1-runs of an 0xF0xx pixel")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--art", type=Path, default=DEFAULT_ART)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--list", action="store_true", help="list object resources and scene blocks")
    ap.add_argument("--obj", type=int, help="decode cels of this OBJ id")
    ap.add_argument("--cel", type=int, help="with --obj: only this cel index")
    ap.add_argument("--scene", type=int, help="decode this scene block's background")
    ap.add_argument("--verify", action="store_true", help="decode every cel and check stream bounds")
    ap.add_argument("--no-hash", action="store_true", help="skip the SHA-256 identity check")
    a = ap.parse_args()

    load(a.art, not a.no_hash)
    names = obj_names()
    objs = objects()
    scns = scenes(align(objs[-1].offset + objs[-1].size))

    if a.list:
        for o in objs:
            seq, frm, t3, cel = (c for c, _ in o.tables)
            print(f"OBJ {o.index:3d} @{o.offset:#010x} size {o.size:8d} seq {seq:3d} frames {frm:3d} "
                  f"t3 {t3:2d} cels {cel:3d}  {names.get(o.index, '?')}")
        for s in scns:
            print(f"SCENE {s.index:2d} @{s.offset:#010x} size {s.size:8d} id {s.scene_id:#06x} "
                  f"{s.width}x{s.height} placements {s.placements:3d} cel @{s.cel_offset:#010x}")
    if a.verify:
        return verify(objs, scns)
    if a.obj is not None:
        o = objs[a.obj]
        name = safe(names.get(o.index, "UNNAMED"))
        cels = o.cel_offsets
        picks = range(len(cels)) if a.cel is None else [a.cel]
        for k in picks:
            save_png(read_cel(cels[k]), a.out / f"entry_{o.index:03d}_{name}_cel{k:03d}.png", True)
    if a.scene is not None:
        s = scns[a.scene]
        save_png(read_cel(s.cel_offset), a.out / f"scene_{s.index:02d}_{s.scene_id:04X}.png", False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
