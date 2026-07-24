#!/usr/bin/env python3
"""Rip trainer pics + overworld sprites from a FireRed-based ROM (vanilla or
old-style binary hack like Ash Gray, which keeps vanilla table addresses).

Outputs indexed PNGs. Trainer front pics are auto-labeled from gTrainers names.
"""
import argparse, os, struct, sys
from PIL import Image

# Vanilla FireRed US 1.0 (from byte-matching pret/pokefirered build .map)
SYM = {
    "gTrainerFrontPicCoords":      0x0823932C,
    "gTrainerFrontPicTable":       0x0823957C,
    "gTrainerFrontPicPaletteTable":0x08239A1C,
    "gTrainerBackPicCoords":       0x08239F8C,
    "gTrainerBackPicTable":        0x08239FA4,
    "gTrainerBackPicPaletteTable": 0x08239FD4,
    "gTrainers":                   0x0823EAC8,
    "gObjectEventGraphicsInfoPointers": 0x0839FDB0,
}
N_FRONT = 148   # (PicPaletteTable - PicTable) / 8
N_BACK = 6
N_TRAINERS = 743
N_OBJ_EVENTS = 240
TRAINER_STRUCT_SIZE = 40
ROM_BASE = 0x08000000

CHARMAP = {}
def _build_charmap():
    # FRLG text encoding, letters/digits/space subset for names
    for i, c in enumerate("0123456789"):
        CHARMAP[0xA1 + i] = c
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        CHARMAP[0xBB + i] = c
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        CHARMAP[0xD5 + i] = c
    CHARMAP[0x00] = " "
    CHARMAP[0xAD] = "."
    CHARMAP[0xB8] = ","
    CHARMAP[0xB4] = "'"
    CHARMAP[0xAE] = "-"
    CHARMAP[0xB0] = "..."
    CHARMAP[0xBA] = "/"
    CHARMAP[0xB1] = '"'
    CHARMAP[0xB2] = '"'
    CHARMAP[0xB3] = "'"
    CHARMAP[0xAB] = "!"
    CHARMAP[0xAC] = "?"
    CHARMAP[0xB5] = "M"   # male sign
    CHARMAP[0xB6] = "F"   # female sign
_build_charmap()

def decode_text(b):
    out = []
    for ch in b:
        if ch == 0xFF:
            break
        out.append(CHARMAP.get(ch, "?"))
    return "".join(out).strip()

def rom_off(ptr):
    if not (ROM_BASE <= ptr < ROM_BASE + 0x02000000):
        raise ValueError(f"not a ROM pointer: {ptr:#x}")
    return ptr - ROM_BASE

def lz77_decompress(rom, off):
    if rom[off] != 0x10:
        raise ValueError(f"no LZ77 header at {off:#x} (byte {rom[off]:#x})")
    size = rom[off+1] | (rom[off+2] << 8) | (rom[off+3] << 16)
    out = bytearray()
    pos = off + 4
    while len(out) < size:
        flags = rom[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = rom[pos], rom[pos+1]; pos += 2
                count = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                for _ in range(count):
                    out.append(out[-disp])
            else:
                out.append(rom[pos]); pos += 1
    return bytes(out)

def bgr555_palette(data):
    pal = []
    for i in range(0, min(len(data), 32), 2):
        v = data[i] | (data[i+1] << 8)
        pal.append(((v & 31) * 255 // 31,
                    ((v >> 5) & 31) * 255 // 31,
                    ((v >> 10) & 31) * 255 // 31))
    while len(pal) < 16:
        pal.append((0, 0, 0))
    return pal

def render_4bpp(tiles, width_px, height_px, pal):
    img = Image.new("P", (width_px, height_px))
    img.putpalette([c for rgb in pal for c in rgb])
    px = img.load()
    tiles_w = width_px // 8
    n = min(len(tiles) // 32, tiles_w * (height_px // 8))
    for t in range(n):
        tx, ty = (t % tiles_w) * 8, (t // tiles_w) * 8
        for row in range(8):
            for col in range(0, 8, 2):
                b = tiles[t * 32 + row * 4 + col // 2]
                px[tx + col, ty + row] = b & 0xF
                px[tx + col + 1, ty + row] = b >> 4
    return img

def u32(rom, off): return struct.unpack_from("<I", rom, off)[0]
def u16(rom, off): return struct.unpack_from("<H", rom, off)[0]

def trainer_names_by_pic(rom):
    """Map pic index -> set of trainer names using it (from gTrainers)."""
    base = rom_off(SYM["gTrainers"])
    names = {}
    for i in range(N_TRAINERS):
        e = base + i * TRAINER_STRUCT_SIZE
        pic = rom[e + 3]
        nm = decode_text(rom[e + 4:e + 16])
        if nm:
            names.setdefault(pic, [])
            if nm not in names[pic]:
                names[pic].append(nm)
    return names

def rip_trainer_pics(rom, outdir, kind="front"):
    tbl = rom_off(SYM[f"gTrainer{kind.capitalize()}PicTable"])
    ptbl = rom_off(SYM[f"gTrainer{kind.capitalize()}PicPaletteTable"])
    n = N_FRONT if kind == "front" else N_BACK
    names = trainer_names_by_pic(rom) if kind == "front" else {}
    os.makedirs(outdir, exist_ok=True)
    ok = 0
    for i in range(n):
        try:
            gfx_ptr = u32(rom, tbl + i * 8)
            size = u16(rom, tbl + i * 8 + 4)
            pal_ptr = u32(rom, ptbl + i * 8)
            goff = rom_off(gfx_ptr)
            if rom[goff] == 0x10:
                tiles = lz77_decompress(rom, goff)
            else:  # FRLG back pics are raw multi-frame 4bpp
                tiles = rom[goff:goff + size]
            poff = rom_off(pal_ptr)
            pal_raw = lz77_decompress(rom, poff) if rom[poff] == 0x10 else rom[poff:poff + 32]
            pal = bgr555_palette(pal_raw)
            side = 64
            h = (len(tiles) // 32 // (side // 8)) * 8
            img = render_4bpp(tiles, side, max(h, 8), pal)
            label = ""
            if i in names:
                label = "_" + "_".join(s.replace(" ", "-") for s in names[i][:3])
            img.save(os.path.join(outdir, f"{kind}_{i:03d}{label}.png"))
            ok += 1
        except Exception as ex:
            print(f"  {kind} {i}: SKIP ({ex})", file=sys.stderr)
    print(f"{kind} pics: {ok}/{n} ripped -> {outdir}")

def rip_object_events(rom, outdir):
    base = rom_off(SYM["gObjectEventGraphicsInfoPointers"])
    os.makedirs(outdir, exist_ok=True)
    ok = 0
    for i in range(N_OBJ_EVENTS):
        try:
            info = rom_off(u32(rom, base + i * 4))
            pal_tag1 = u16(rom, info + 2)
            width = u16(rom, info + 8)
            height = u16(rom, info + 10)
            images_ptr = u32(rom, info + 0x1C)
            frame0 = rom_off(u32(rom, rom_off(images_ptr)))
            frame_size = u16(rom, rom_off(images_ptr) + 4)
            if not (8 <= width <= 128 and 8 <= height <= 128):
                raise ValueError(f"odd dims {width}x{height}")
            tiles = rom[frame0:frame0 + frame_size]
            pal = find_ow_palette(rom, pal_tag1)
            img = render_4bpp(tiles, width, height, pal)
            img.info["transparency"] = 0
            img.save(os.path.join(outdir, f"ow_{i:03d}_pal{pal_tag1:04X}_{width}x{height}.png"),
                     transparency=0)
            ok += 1
        except Exception as ex:
            print(f"  ow {i}: SKIP ({ex})", file=sys.stderr)
    print(f"object events: {ok}/{N_OBJ_EVENTS} ripped -> {outdir}")

_OW_PAL_CACHE = {}
def find_ow_palette(rom, tag):
    """Scan for the SpritePalette table entry {u8* data; u16 tag} by tag.
    FRLG keeps OW palettes uncompressed, 32 bytes, tags 0x11xx.
    We locate sObjectEventSpritePalettes heuristically once."""
    if not _OW_PAL_CACHE:
        # scan ROM for a run of {ptr,u16 tag,u16 0} entries with tags 0x11FF>=tag>=0x1100
        for off in range(0, len(rom) - 8, 4):
            ptr = u32(rom, off)
            tag_v = u16(rom, off + 4)
            if (ROM_BASE <= ptr < ROM_BASE + 0x1000000) and 0x1100 <= tag_v <= 0x11FF:
                # verify a run of >=8 entries
                run = 0
                o = off
                while True:
                    p2, t2 = u32(rom, o), u16(rom, o + 4)
                    if (ROM_BASE <= p2 < ROM_BASE + 0x1000000) and 0x1100 <= t2 <= 0x11FF:
                        run += 1; o += 8
                    else:
                        break
                if run >= 8:
                    o = off
                    for _ in range(run):
                        _OW_PAL_CACHE[u16(rom, o + 4)] = rom_off(u32(rom, o))
                        o += 8
                    break
        if not _OW_PAL_CACHE:
            raise RuntimeError("OW palette table not found")
    poff = _OW_PAL_CACHE.get(tag)
    if poff is None:
        poff = next(iter(_OW_PAL_CACHE.values()))
    return bgr555_palette(rom[poff:poff + 32])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--out", default="ripped")
    ap.add_argument("--front", action="store_true")
    ap.add_argument("--back", action="store_true")
    ap.add_argument("--ow", action="store_true")
    ap.add_argument("--names", action="store_true", help="dump pic->trainer-name map")
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    if a.names:
        for pic, nms in sorted(trainer_names_by_pic(rom).items()):
            print(f"pic {pic:3d}: {', '.join(nms[:8])}")
    if a.front:
        rip_trainer_pics(rom, os.path.join(a.out, "front"), "front")
    if a.back:
        rip_trainer_pics(rom, os.path.join(a.out, "back"), "back")
    if a.ow:
        rip_object_events(rom, os.path.join(a.out, "ow"))

if __name__ == "__main__":
    main()
