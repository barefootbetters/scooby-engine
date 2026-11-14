#!/usr/bin/env python3
"""Decode Gen 1 (Showdown) ``TGIFILE.ART`` sprites and room backgrounds to PNG.

WP-002 deliverable, corrected by the WP-001 ``Scooby.exe`` trace. The format
is documented in ``docs/formats/tgifile-art.md`` (sections "Archive layout",
"Header layout", "Object resources", "Scene blocks", "Cel format"). Summary:

* Header (the engine reads the first 64 sectors, 0x20000 bytes):
  ``u32 room_count`` (69), ``u32[69]`` room descriptors, ``u32 object_count``
  (453), ``u32[453]`` object descriptors, ``u32 name_count`` (1,788) at
  0x830, then 68-byte name records from 0x834. A descriptor is
  ``start_sector << 14 | sector_count`` (2048-byte sectors).
* Object resources start at file offset 0x20000. There are ``object_count``
  of them, packed back to back, each padded to a 2048-byte sector. Resource
  ``i`` is the art for name-table ``OBJ`` id ``i``.
* Room (scene) blocks (backgrounds plus object placement lists) follow the
  last object resource, ``room_count`` of them, each sector padded. Block
  ``i`` is ``ROOM`` id ``i``. The last one ends exactly at end of file.
* Every image (sprite cel or background) is a "cel": a 24-byte header
  ``u32 size, u16 w, u16 h, u32 mask_a, u32 mask_b, u8 solid, u8 rle,
  u16 solid_color, u32 0`` followed by the pixels. With ``rle`` set, byte
  ``0xF0`` starts a run (``F0 count hi lo``) and any other byte starts a
  literal pixel (``hi lo``): big-endian words. With ``rle`` clear, the pixels
  are stored raw, little-endian. With ``solid`` set, the engine paints
  ``solid_color`` instead of the pixels.
* Mask A lists the opaque pixels (RGB565). Mask B lists the translucent
  pixels, whose words are ARGB4444. Every other pixel is transparent.

Outputs go to ``tools/samples/`` by default, which is gitignored: decoded
images are copyrighted derivatives and are never committed (see
``tools/samples/README.md``).

Usage (PowerShell):
    py -3 tools/probe_art.py --list
    py -3 tools/probe_art.py --obj 0                # every cel of OBJ id 0
    py -3 tools/probe_art.py --obj 1 --cel 0
    py -3 tools/probe_art.py --scene 0
    py -3 tools/probe_art.py --room ROOM_P12_Saloon   # background + placed objects
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
NAME_RECORD = 68  # u32 id + char[64] NUL-terminated name
PLACEMENT = 148  # char[64] OBJ name, char[64] ANIM name, u16[4], u32, pad
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


def header() -> tuple[list[int], list[int], int]:
    """Return (room descriptors, object descriptors, offset of name_count).

    Parse order follows ``Scooby.exe``'s art-file constructor (0x43A8B0).
    """
    nr = u32(ART, 0)
    rooms = list(struct.unpack_from(f"<{nr}I", ART, 4))
    p = 4 + 4 * nr
    no = u32(ART, p)
    objs = list(struct.unpack_from(f"<{no}I", ART, p + 4))
    return rooms, objs, p + 4 + 4 * no


def name_table() -> list[tuple[int, str]]:
    """All (id, name) records. The bytes after a name's NUL are not read."""
    _, _, p = header()
    n = u32(ART, p)
    out = []
    for q in range(p + 4, p + 4 + NAME_RECORD * n, NAME_RECORD):
        out.append((u32(ART, q), ART[q + 4 : q + NAME_RECORD].split(b"\0", 1)[0].decode("ascii")))
    return out


def obj_names() -> dict[int, str]:
    """Map OBJ id -> name."""
    return {rid & 0xFFFFFF: name for rid, name in name_table() if rid >> 24 == 0x20}


def descriptor_span(d: int) -> tuple[int, int]:
    """A room/object descriptor -> (file offset, byte length)."""
    return (d >> 14) * SECTOR, (d & 0x3FFF) * SECTOR


def objects() -> list[ObjectResource]:
    count = u32(ART, 4 + 4 * u32(ART, 0))
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
        cel = p + first + PLACEMENT * placements
        out.append(SceneBlock(i, p, size, scene_id, w, h, placements, cel))
        p = align(p + size)
    if p != len(ART):
        raise ValueError(f"scene walk ended at {p:#x}, file is {len(ART):#x}")
    return out


def read_cel(off: int) -> Cel:
    return Cel(off, *struct.unpack_from("<IHHIIII", ART, off))


def is_solid(cel: Cel) -> bool:
    """Cel byte 0x10: the engine paints mask A with ``solid_color`` (0x433AF0)."""
    return cel.flags & 0xFF != 0


def is_rle(cel: Cel) -> bool:
    """Cel byte 0x11: 1 = RLE stream, 0 = raw little-endian words (0x4398A0)."""
    return cel.flags >> 8 & 0xFF != 0


def decode(cel: Cel) -> tuple[list[int], int]:
    """Return (pixel words, pixel bytes consumed)."""
    want = cel.width * cel.height
    q = cel.offset + CEL_HEADER
    if not is_rle(cel):
        return list(struct.unpack_from(f"<{want}H", ART, q)), 2 * want
    px: list[int] = []
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


def mask_spans(off: int, width: int):
    """Yield (start, end) pixel indexes of a span mask's covered pixels.

    Chunk: u32 size, u16 x, u16 y, u16 w, u16 h, then records of
    ``u16 repeat_rows, u16 n, u16[n] runs`` up to the chunk end. Each row
    starts at column x; runs are (skip, covered) pairs, as the engine walks
    them in 0x433AF0 and its blitters.
    """
    size, x, y = struct.unpack_from("<IHH", ART, off)
    q, row = off + 12, y
    while q < off + size:
        rep, n = struct.unpack_from("<HH", ART, q)
        runs = struct.unpack_from(f"<{n}H", ART, q + 4)
        q += 4 + 2 * n
        for _ in range(rep):
            col = x
            for k in range(0, n - 1, 2):
                col += runs[k]
                if runs[k + 1]:
                    yield row * width + col, row * width + col + runs[k + 1]
                col += runs[k + 1]
            row += 1


def rgba(cel: Cel, base: int) -> list[tuple[int, int, int, int]]:
    """Composite one cel the way the engine does: A opaque, B blended, else clear.

    ``base`` is the owning object resource or scene block offset (mask
    offsets are relative to it).
    """
    px, _ = decode(cel)
    out = [(0, 0, 0, 0)] * (cel.width * cel.height)
    if cel.mask_a:
        solid = rgb(cel.flags >> 16) if is_solid(cel) else None
        for s, e in mask_spans(base + cel.mask_a, cel.width):
            out[s:e] = [(*solid, 255)] * (e - s) if solid else [(*rgb(v), 255) for v in px[s:e]]
    if cel.mask_b:
        # ARGB4444: the blend in 0x439170 takes alpha from the top nibble.
        for s, e in mask_spans(base + cel.mask_b, cel.width):
            out[s:e] = [((v >> 8 & 15) * 17, (v >> 4 & 15) * 17, (v & 15) * 17, (v >> 12) * 17)
                        for v in px[s:e]]
    return out


def sequence_frame(o: ObjectResource, seq: int, step: int) -> int:
    """Absolute offset of the frame record a sequence step shows (0x4309C0)."""
    count, table0 = o.tables[0]
    if seq >= count:
        raise ValueError(f"OBJ {o.index} has no sequence {seq}")
    r = o.offset + u32(ART, o.offset + table0 + 4 * seq)
    ref = u32(ART, r + 8 + 12 * step + 4)
    return o.offset + u32(ART, o.offset + o.tables[1][1] + 4 * (ref & 0x3FFFF))


def frame_cels(frame: int, base: int) -> list[tuple[int, int, Cel]]:
    """A frame record's (dx, dy, cel) entries; offsets are relative to ``base``."""
    n = struct.unpack_from("<H", ART, frame + 4)[0]
    out = []
    for k in range(n):
        dx, dy, cel = struct.unpack_from("<hhI", ART, frame + 8 + 8 * k)
        out.append((dx, dy, read_cel(base + cel)))
    return out


# Character actors, from the table at 0x46A720 that 0x4091FF checks.
CHARACTERS = ("NARRATOR", "DAPHNE", "FRED", "SCOOBY", "SHAGGY", "VELMA", "ARTIE", "JENNY",
              "SHERIFF", "ICDOUBLE", "GUMMY", "DONKEY", "BRAD", "EWAN", "MARIA", "JANE",
              "WIZARD", "JESTER", "PRINCESS", "UNICYCLE")


def load_ini(path: Path) -> dict[str, dict[str, str]]:
    """``object.ini`` as {section: {lower-case key: value}} (GetPrivateProfileString rules)."""
    import configparser

    cp = configparser.RawConfigParser(strict=False, interpolation=None)
    cp.read(path, encoding="latin-1")
    return {sec: dict(cp.items(sec)) for sec in cp.sections()}


def ini_int(value: str | None) -> int:
    """0x40AD50: atoi, but a non-numeric (or missing, default "bad") value is -1."""
    value = (value or "bad").strip()
    try:
        return int(value)
    except ValueError:
        return 0 if value[:1] == "0" else -1


class Sprite:
    """A node of the engine's sprite tree (0x430D60 / 0x430F40 / 0x431000)."""

    def __init__(self, depth: int, paint=None, label: str = "") -> None:
        self.depth, self.paint, self.label = depth, paint, label
        self.children: list[Sprite] = []

    def add(self, child: "Sprite") -> "Sprite":
        # 0x430F40: children stay sorted by descending depth; a new child goes
        # after every child whose depth is >= its own.
        k = 0
        while k < len(self.children) and child.depth <= self.children[k].depth:
            k += 1
        self.children.insert(k, child)
        return child

    def front_to_back(self) -> list["Sprite"]:
        # 0x431000: children at or above our depth, then us, then the rest.
        out: list[Sprite] = []
        k = 0
        while k < len(self.children) and self.depth <= self.children[k].depth:
            out += self.children[k].front_to_back()
            k += 1
        out.append(self)
        for c in self.children[k:]:
            out += c.front_to_back()
        return out


def placement_parent_depth(obj: str, y: int, ini: dict[str, dict[str, str]]) -> tuple[int, int, str]:
    """Return (layer slot or -1 for the root, depth, kind) for a default placement.

    Follows 0x4091FF / 0x408F90 / 0x408DC0 / 0x401000. Per-room overrides
    (a room claiming an OBJ by name) are not modelled.
    """
    sec = ini.get(obj, {})
    kind = sec.get("id", "simpleobject").strip().lower()
    if kind == "inventoryobject":
        return 0, -100, kind
    if kind == "requiresobject":
        return 0, 0, kind
    if kind == "exitobject":
        return 0, -1000, kind
    if kind == "clickableobject":
        layer = ini_int(sec.get("layer"))
        return (0 if layer == -1 else layer), ini_int(sec.get("priority")), kind
    stem = obj[:-2] if len(obj) > 2 and obj[-2] == "_" else obj
    if stem in {f"OBJ_{n}" for n in CHARACTERS} or obj == "OBJ_GHOST":
        return 0, y - 200, "character"
    return 1, 0, "sprite"  # parent = layer slot 1, empty in Showdown -> root


def render_room(s: SceneBlock, objs: list[ObjectResource],
                ini: dict[str, dict[str, str]]) -> tuple[object, list[str]]:
    """Composite a room as the engine sets it up on entry (0x435DC0).

    Builds the sprite tree: a root, the room's layer-slot sprites at depth
    -110000 + 10000 x slot, and one sprite per placement at step 0 of its
    sequence, parented and ordered by the default placement rules. Then
    paints the engine's front-to-back draw list from the back.
    """
    from PIL import Image

    ids = {name: rid for rid, name in name_table()}
    im = Image.new("RGBA", (s.width, s.height), (0, 0, 0, 255))
    log: list[str] = []

    def painter(frame: int, base: int, x: int, y: int):
        def paint() -> None:
            for dx, dy, c in frame_cels(frame, base):
                tile = Image.new("RGBA", (c.width, c.height))
                tile.putdata(rgba(c, base))
                _paste_clipped(im, tile, x + dx, y + dy)
        return paint

    root = Sprite(-0x7FFFFFFF, label="root")
    layers: list[Sprite | None] = []
    for slot in range(10):
        off = u32(ART, s.offset + 0x80 + 4 * slot)
        layers.append(root.add(Sprite(-110000 + 10000 * slot, painter(s.offset + off, s.offset, 0, 0),
                                      f"layer {slot}")) if off else None)

    for k in range(s.placements):
        p = s.offset + 0xD8 + PLACEMENT * k
        obj = ART[p : p + 64].split(b"\0", 1)[0].decode("ascii")
        anim = ART[p + 64 : p + 128].split(b"\0", 1)[0].decode("ascii")
        x, y = struct.unpack_from("<hh", ART, p + 0x84)
        slot, depth, kind = placement_parent_depth(obj, y, ini)
        parent = layers[slot] if 0 <= slot < 10 and layers[slot] else root
        o = objs[ids[obj] & 0xFFFFFF]
        frame = sequence_frame(o, ids[anim] & 0x3FFFF, 0)
        n = struct.unpack_from("<H", ART, frame + 4)[0]
        parent.add(Sprite(depth, painter(frame, o.offset, x, y), f"{k:2d} {obj}"))
        log.append(f"{k:2d} {obj:32s} {anim:36s} ({x:4d},{y:4d}) {kind:15s} "
                   f"parent {parent.label:8s} depth {depth:6d} cels {n}")

    order = root.front_to_back()
    for sp in reversed(order):
        if sp.paint:
            sp.paint()
    log.append("draw order, front to back: " + ", ".join(sp.label for sp in order if sp.paint))
    return im, log


def _paste_clipped(im, tile, x: int, y: int) -> None:
    """alpha_composite with a negative destination offset."""
    cx, cy = max(0, -x), max(0, -y)
    if cx >= tile.width or cy >= tile.height:
        return
    im.alpha_composite(tile.crop((cx, cy, tile.width, tile.height)), (x + cx, y + cy))


def save_png(cel: Cel, base: int, path: Path) -> None:
    from PIL import Image

    im = Image.new("RGBA", (cel.width, cel.height))
    im.putdata(rgba(cel, base))
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
            # be carried as a run of length 1. Raw cels have no stream.
            q, n, want = off + CEL_HEADER, 0, c.width * c.height
            while is_rle(c) and n < want:
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
    return verify_engine(objs, scns)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def verify_engine(objs: list[ObjectResource], scns: list[SceneBlock]) -> int:
    """Check the readings WP-001 took from ``Scooby.exe`` against the data."""
    # Descriptors: start_sector << 14 | sector_count (0x43ACE0 / 0x43AED0).
    rooms, odesc, _ = header()
    for kind, descs, blocks in (("room", rooms, scns), ("object", odesc, objs)):
        if len(descs) != len(blocks):
            return fail(f"{len(descs)} {kind} descriptors, {len(blocks)} blocks")
        for i, (d, b) in enumerate(zip(descs, blocks)):
            if descriptor_span(d) != (b.offset, align(b.offset + b.size) - b.offset):
                return fail(f"{kind} descriptor {i} {d:#010x} does not span its block")
    print(f"descriptors: all {len(rooms)} room and {len(odesc)} object descriptors "
          "are (sector << 14 | sectors) spans of their blocks")

    # Name table: ROOM ids 0..n-1, OBJ ids 0..n-1, one ANIM per sequence.
    table = name_table()
    tags: dict[int, list[int]] = {}
    for rid, _ in table:
        tags.setdefault(rid >> 24, []).append(rid & 0xFFFFFF)
    if sorted(tags.get(0x10, [])) != list(range(len(scns))):
        return fail("ROOM ids are not 0..room_count-1")
    if sorted(tags.get(0x20, [])) != list(range(len(objs))):
        return fail("OBJ ids are not 0..object_count-1")
    anims = [(rid, name) for rid, name in table if rid >> 28 == 3]
    if len(anims) + len(tags[0x10]) + len(tags[0x20]) != len(table):
        return fail("name table holds a tag other than ROOM, OBJ, ANIM")
    seqs = sum(o.tables[0][0] for o in objs)
    if len(anims) != seqs:
        return fail(f"{len(anims)} ANIM names but {seqs} sequences")
    # ANIM id = 0x3000_0000 | (owner OBJ id & 0xFF) << 20 | sequence index.
    per_group: dict[int, int] = {}
    for o in objs:
        per_group[o.index & 0xFF] = per_group.get(o.index & 0xFF, 0) + o.tables[0][0]
    groups: dict[int, list[int]] = {}
    for rid, _ in anims:
        groups.setdefault(rid >> 20 & 0xFF, []).append(rid & 0xFFFFF)
    for g, idx in groups.items():
        if len(idx) != per_group.get(g, 0):
            return fail(f"ANIM group {g:#x}: {len(idx)} names, {per_group.get(g, 0)} sequences")
    print(f"name table: {len(table)} records = {len(tags[0x10])} ROOM + {len(tags[0x20])} OBJ "
          f"+ {len(anims)} ANIM; ANIM count equals the sequence count")

    # Sequence steps: (u32 unread, u32 0x8000_0000 | owner << 20 | frame, u32 polygon).
    # The first word is 0 on every Showdown step. Phantom sets it on two
    # steps of OBJ_KST_MUG; no traced reader touches it, so it is reported.
    steps = polys = 0
    unread = []
    for o in objs:
        count, table0 = o.tables[0]
        frames = o.tables[1][0]
        for i in range(count):
            r = o.offset + u32(ART, o.offset + table0 + 4 * i)
            n = struct.unpack_from("<H", ART, r + 4)[0]
            if u32(ART, r) != 8 + 12 * n:
                return fail(f"OBJ {o.index} sequence {i}: size != 8 + 12n")
            for k in range(n):
                first, ref, poly = struct.unpack_from("<III", ART, r + 8 + 12 * k)
                if first:
                    dx, dy = struct.unpack("<hh", struct.pack("<I", first))
                    unread.append(f"OBJ {o.index} seq {i} step {k}: {first:#010x} = i16 ({dx}, {dy})")
                if ref >> 31 != 1 or ref >> 20 & 0x7FF != o.index or ref & 0x3FFFF >= frames:
                    return fail(f"OBJ {o.index} sequence {i} step {k}: frame ref {ref:#010x}")
                if poly:
                    pn = u32(ART, o.offset + poly + 4)
                    if u32(ART, o.offset + poly) != 16 + 4 * pn:
                        return fail(f"OBJ {o.index} sequence {i} step {k}: bad polygon")
                    polys += 1
                steps += 1
    print(f"sequences: {seqs} sequences, {steps} steps; every frame ref names its owner "
          f"and a frame in range; {polys} step polygons parse")
    print(f"sequences: {len(unread)} steps carry a non-zero first word (not read by the player)")
    for line in unread:
        print(f"  {line}")

    # Room blocks: one cel (the background), layer 0 places it at (0, 0);
    # placement (OBJ, ANIM) pairs follow the ANIM ownership rule.
    ids = {name: rid for rid, name in table}
    pairs = 0
    for s in scns:
        b = s.offset
        layers = struct.unpack_from("<10I", ART, b + 0x80)
        if any(layers[1:]) or u32(ART, b + 0xA8) != 1 or u32(ART, b + 0xB0) or u32(ART, b + 0xB8):
            return fail(f"room {s.index}: unexpected header tables")
        if b + u32(ART, b + u32(ART, b + 0xAC)) != s.cel_offset:
            return fail(f"room {s.index}: cel table does not point at the background")
        if struct.unpack_from("<IHHhhI", ART, b + layers[0]) != (16, 1, 0, 0, 0, s.cel_offset - b):
            return fail(f"room {s.index}: layer 0 is not the background at (0, 0)")
        for k in range(s.placements):
            p = b + 0xD8 + PLACEMENT * k
            obj = ART[p : p + 64].split(b"\0", 1)[0].decode("ascii")
            anim = ART[p + 64 : p + 128].split(b"\0", 1)[0].decode("ascii")
            oid, aid = ids[obj] & 0xFFFFFF, ids[anim]
            if aid >> 20 & 0xFF != oid & 0xFF or aid & 0xFFFFF >= objs[oid].tables[0][0]:
                return fail(f"room {s.index}: {anim} is not a sequence of {obj}")
            pairs += 1
    print(f"rooms: every block has one cel table entry and a (0, 0) layer-0 record; "
          f"{pairs} placements name a sequence of their own object")

    # Masks partition each sprite cel: A opaque, B translucent ARGB4444
    # (alpha nibble 1..14), every other pixel 0.
    a_px = b_px = 0
    for o in objs:
        for off in o.cel_offsets:
            c = read_cel(off)
            px, _ = decode(c)
            label = bytearray(len(px))
            nonzero = len(px) - px.count(0)
            covered_nz = 0
            for which, m in ((1, c.mask_a), (2, c.mask_b)):
                if not m:
                    continue
                for s, e in mask_spans(o.offset + m, c.width):
                    if label[s:e].count(0) != e - s:
                        return fail(f"OBJ {o.index} cel {off:#x}: masks overlap")
                    label[s:e] = bytes([which]) * (e - s)
                    seg = px[s:e]
                    covered_nz += len(seg) - seg.count(0)
                    if which == 2:
                        if any(not 1 <= v >> 12 <= 14 for v in seg):
                            return fail(f"OBJ {o.index} cel {off:#x}: mask B pixel alpha 0 or 15")
                        b_px += e - s
                    else:
                        a_px += e - s
            if nonzero != covered_nz:
                return fail(f"OBJ {o.index} cel {off:#x}: non-zero pixel outside both masks")
    print(f"masks: A and B are disjoint in every sprite cel; {a_px} mask-A px, {b_px} mask-B px "
          "(all with alpha 1..14); no non-zero pixel outside them")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--art", type=Path, default=DEFAULT_ART)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--list", action="store_true", help="list object resources and scene blocks")
    ap.add_argument("--obj", type=int, help="decode cels of this OBJ id")
    ap.add_argument("--cel", type=int, help="with --obj: only this cel index")
    ap.add_argument("--scene", type=int, help="decode this scene block's background")
    ap.add_argument("--room", help="composite a room with its placed objects (index or ROOM_ name)")
    ap.add_argument("--ini", type=Path, help="object.ini for --room (default: next to --art)")
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
            save_png(read_cel(cels[k]), o.offset, a.out / f"entry_{o.index:03d}_{name}_cel{k:03d}.png")
    if a.scene is not None:
        s = scns[a.scene]
        save_png(read_cel(s.cel_offset), s.offset, a.out / f"scene_{s.index:02d}_{s.scene_id:04X}.png")
    if a.room is not None:
        rooms = {name: rid & 0xFFFFFF for rid, name in name_table() if rid >> 24 == 0x10}
        idx = int(a.room) if a.room.isdigit() else rooms[a.room]
        name = next(n for n, i in rooms.items() if i == idx)
        ini_path = a.ini or a.art.parent / "object.ini"
        im, log = render_room(scns[idx], objs, load_ini(ini_path))
        print("\n".join(log))
        path = a.out / f"room_{idx:02d}_{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path)
        print(f"wrote {path} ({im.width}x{im.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
