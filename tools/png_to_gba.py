#!/usr/bin/env python3
"""Convert indexed PNG sprite art into the exact blobs this engine family injects.

Why this exists
---------------
The Ash Gray donors in `sprites/donors/ashgray/` are verbatim LZ77 streams ripped
straight out of a ROM, so they were injectable as-is. Everything sourced since
(Emerald Rogue, Team Aqua's Asset Repo, pokemonHnS, pokeemerald-platinum,
Pokesho, kalarie, LouLilie) arrives as PNGs from decomp trees and fan galleries.
Those are the right art in the wrong container: a decomp builds them through
`grit` at compile time, and we have no compile step.

This turns a PNG into what `inject_sprites_pilot.py` already knows how to place:

    <name>.4bpp        raw 4bpp tiles, 8x8 tile order  (64x64 -> 2048 B)
    <name>.gbapal      16 colours, BGR555              (32 B)
    <name>.4bpp.lz     LZ77 (BIOS type 0x10) of the above
    <name>.gbapal.lz   LZ77 of the palette

2048 B is not incidental: it is exactly the value CFRU's `MugshotTable.size`
field wants (`64 * 64 / 2`), and what `gTrainerFrontPicTable` entries declare.

Every conversion is round-tripped through the decompressor before being written,
so a blob that cannot be decoded back byte-for-byte is never staged.

    python3 tools/png_to_gba.py IN.png [IN2.png ...] --outdir DIR
    python3 tools/png_to_gba.py --scan HARVEST_DIR --outdir DIR
"""
import argparse
import json
import struct
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("png_to_gba.py needs Pillow (python3 -m pip install Pillow)")


# ---------------------------------------------------------------- LZ77

def lz77_compress(data: bytes) -> bytes:
    """GBA BIOS type-0x10 LZ77.

    Header is 0x10 then a 24-bit little-endian uncompressed length. Then groups
    of 8 items preceded by a flag byte, MSB first: 0 = literal, 1 = backref
    encoded as (len-3)<<12 | (disp-1), big-endian in two bytes.

    The GBA decoder cannot read from displacement 0, and a match must be at
    least 3 bytes to be worth two bytes of encoding -- both enforced below.
    """
    out = bytearray(struct.pack("<I", (len(data) << 8) | 0x10))
    pos = 0
    n = len(data)
    while pos < n:
        flags_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            best_len, best_disp = 0, 0
            # window is 4096 back; matches run 3..18
            start = max(0, pos - 4096)
            max_len = min(18, n - pos)
            if max_len >= 3:
                chunk = data[pos:pos + 3]
                search = data[start:pos]
                idx = search.find(chunk)
                while idx != -1:
                    cand = start + idx
                    ln = 3
                    while ln < max_len and data[cand + ln] == data[pos + ln]:
                        ln += 1
                    if ln > best_len:
                        best_len, best_disp = ln, pos - cand
                        if ln == max_len:
                            break
                    idx = search.find(chunk, idx + 1)
            if best_len >= 3:
                flags |= 0x80 >> bit
                enc = ((best_len - 3) << 12) | (best_disp - 1)
                out += struct.pack(">H", enc)
                pos += best_len
            else:
                out.append(data[pos])
                pos += 1
        out[flags_at] = flags
    return bytes(out)


def lz77_decompress(data: bytes) -> bytes:
    """Mirror of the above, used only to prove a round trip before staging."""
    if not data or data[0] != 0x10:
        raise ValueError("not an LZ77 type-0x10 stream")
    size = struct.unpack("<I", data[:4])[0] >> 8
    out = bytearray()
    pos = 4
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                hi, lo = data[pos], data[pos + 1]
                pos += 2
                ln = ((hi >> 4) & 0xF) + 3
                disp = (((hi & 0xF) << 8) | lo) + 1
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                out.append(data[pos])
                pos += 1
    return bytes(out[:size])


# ---------------------------------------------------------------- graphics

def to_4bpp(im: Image.Image) -> bytes:
    """Linear indexed pixels -> GBA 4bpp, 8x8 tiles in row-major tile order.

    Two pixels per byte, LOW nibble first (left pixel). Getting that backwards
    produces art that looks mirrored within every byte pair -- a classic and
    very visible failure.
    """
    w, h = im.size
    if w % 8 or h % 8:
        raise ValueError(f"dimensions {w}x{h} are not tile-aligned")
    px = im.load()
    out = bytearray()
    for ty in range(h // 8):
        for tx in range(w // 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    lo = px[tx * 8 + x, ty * 8 + y] & 0xF
                    hi = px[tx * 8 + x + 1, ty * 8 + y] & 0xF
                    out.append((hi << 4) | lo)
    return bytes(out)


def to_gbapal(im: Image.Image) -> bytes:
    """16 colours as BGR555, 5 bits per channel, little-endian u16 each."""
    pal = im.getpalette() or []
    entries = len(pal) // 3
    out = bytearray()
    for i in range(16):
        if i < entries:
            r, g, b = pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]
        else:
            r = g = b = 0
        out += struct.pack("<H", ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3))
    return bytes(out)


KIND_BY_SIZE = {
    (64, 64): "front",
    (64, 256): "back4",
    (64, 320): "back5",
    (64, 384): "back6",
}


def classify(w, h):
    if (w, h) in KIND_BY_SIZE:
        return KIND_BY_SIZE[(w, h)]
    if h == 32 and w % 16 == 0:
        return "overworld"
    return "other"


def convert(src: Path, outdir: Path):
    im = Image.open(src)
    if im.mode != "P":
        im = im.convert("P", palette=Image.ADAPTIVE, colors=16)
    colours = len(set(im.getdata()))
    if colours > 16:
        return {"src": str(src), "ok": False,
                "error": f"{colours} distinct indices; needs quantising to 16"}
    w, h = im.size
    kind = classify(w, h)
    try:
        gfx = to_4bpp(im)
    except ValueError as e:
        return {"src": str(src), "ok": False, "error": str(e)}
    pal = to_gbapal(im)
    gfx_lz, pal_lz = lz77_compress(gfx), lz77_compress(pal)

    # never stage a blob we cannot decode back
    if lz77_decompress(gfx_lz) != gfx or lz77_decompress(pal_lz) != pal:
        return {"src": str(src), "ok": False, "error": "LZ77 round-trip mismatch"}

    outdir.mkdir(parents=True, exist_ok=True)
    stem = src.stem
    (outdir / f"{stem}.4bpp").write_bytes(gfx)
    (outdir / f"{stem}.gbapal").write_bytes(pal)
    (outdir / f"{stem}.4bpp.lz").write_bytes(gfx_lz)
    (outdir / f"{stem}.gbapal.lz").write_bytes(pal_lz)
    return {"src": str(src), "name": stem, "kind": kind, "ok": True,
            "width": w, "height": h, "colours": colours,
            "gfx_raw_bytes": len(gfx), "gfx_lz_bytes": len(gfx_lz),
            "pal_raw_bytes": len(pal), "pal_lz_bytes": len(pal_lz)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pngs", nargs="*", type=Path)
    ap.add_argument("--scan", type=Path, help="convert every .png under this directory")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()

    srcs = list(args.pngs)
    if args.scan:
        srcs += sorted(p for p in args.scan.rglob("*.png"))
    if not srcs:
        sys.exit("nothing to convert")

    results = [convert(p, args.outdir) for p in srcs]
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    (args.outdir / "convert_manifest.json").write_text(json.dumps(results, indent=1))

    by_kind = {}
    for r in ok:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    print(f"converted {len(ok)}/{len(results)} -> {args.outdir}")
    for k, v in sorted(by_kind.items()):
        print(f"   {k:<10} {v}")
    if bad:
        print(f"\n{len(bad)} failed:")
        for r in bad[:20]:
            print(f"   {Path(r['src']).name}: {r['error']}")


if __name__ == "__main__":
    main()
