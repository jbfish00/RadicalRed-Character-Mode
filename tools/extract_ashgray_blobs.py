#!/usr/bin/env python3
"""Extract LZ77-compressed trainer-pic blobs (gfx+palette) from Ash Gray,
verbatim, with exact compressed stream lengths — ready for byte-copy
injection into any FRLG-family ROM (e.g. Radical Red).

Outputs per character: <name>_front.lz, <name>_frontpal.lz, <name>_front.png
plus manifest.json with sizes and provenance.
"""
import json, os, struct, sys

ROM_BASE = 0x08000000
FRONT_TBL = 0x23957C
PAL_TBL = 0x239A1C

# pic index -> character key (from gTrainers name dump, ashgray 4.5.3)
PICKS = {
    28: "jessie_james",   # Team Rocket duo pic
    82: "ritchie",
    133: "tracey",
    135: "duplica",
    15: "todd",
    65: "giselle",
    142: "aj",
    47: "otoshi",
    83: "samurai",
    8: "damian",
    25: "cissy",
    62: "danny",
    75: "rudy",
    146: "jessiebelle",
    106: "gary",
    116: "brock_anime",
    117: "misty_anime",
    132: "oak_anime",
    108: "giovanni_anime",
}

def lz77_stream_len(rom, off):
    """Return (decompressed_bytes, compressed_stream_length)."""
    assert rom[off] == 0x10, f"no LZ header at {off:#x}"
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
    return bytes(out), pos - off

def main(rom_path, outdir):
    rom = open(rom_path, "rb").read()
    os.makedirs(outdir, exist_ok=True)
    manifest = {"source": "Pokemon Ash Gray v4.5.3 (metapod23), built locally from BPS patch on byte-matching pret/pokefirered build",
                "format": "GBA LZ77 (BIOS type 0x10); gfx = 64x64 4bpp (0x800 raw), pal = 32 bytes BGR555",
                "tables": {"front": hex(FRONT_TBL), "pal": hex(PAL_TBL)},
                "entries": {}}
    for pic, name in sorted(PICKS.items(), key=lambda kv: kv[1]):
        gfx_ptr = struct.unpack_from("<I", rom, FRONT_TBL + pic*8)[0] - ROM_BASE
        pal_ptr = struct.unpack_from("<I", rom, PAL_TBL + pic*8)[0] - ROM_BASE
        graw, glen = lz77_stream_len(rom, gfx_ptr)
        praw, plen = lz77_stream_len(rom, pal_ptr)
        open(os.path.join(outdir, f"{name}_front.lz"), "wb").write(rom[gfx_ptr:gfx_ptr+glen])
        open(os.path.join(outdir, f"{name}_frontpal.lz"), "wb").write(rom[pal_ptr:pal_ptr+plen])
        manifest["entries"][name] = {
            "ashgray_pic_index": pic,
            "gfx_lz_bytes": glen, "gfx_raw_bytes": len(graw),
            "pal_lz_bytes": plen, "pal_raw_bytes": len(praw),
        }
        print(f"{name:16s} pic {pic:3d}: gfx {glen:5d}B lz ({len(graw)}B raw), pal {plen}B lz")
    json.dump(manifest, open(os.path.join(outdir, "manifest.json"), "w"), indent=2)
    print(f"-> {outdir}/manifest.json")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
