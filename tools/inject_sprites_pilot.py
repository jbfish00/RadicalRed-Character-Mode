#!/usr/bin/env python3
"""Phase 3 pilot: inject Ash Gray anime-character trainer front pics into the
Radical Red CM build and repoint gTrainerFrontPicTable slots at them.

Donor blobs are verbatim LZ77 streams ripped from a locally-built Ash Gray
4.5.3 ROM (see sprites/donors/ashgray/manifest.json) — same engine family
(FRLG), same 64x64 4bpp + 32B palette format, so no conversion is needed.

Tables (docs/ROUTINE_MAP.md, CONFIRMED at stock CFRU/vanilla addresses):
  gTrainerFrontPicTable        file 0x23957C  148 x {u32 ptr, u16 0x800, u16 tag}
  gTrainerFrontPicPaletteTable file 0x239A1C  148 x {u32 ptr, u16 tag, u16 0}

Modes:
  default            inject all donor blobs at SPRITES_ADDR + write manifest;
                     no table slots touched (asset staging for later wiring)
  --test-all-slots   ALSO repoint every front pic+palette slot at one donor
                     (throwaway render-proof build; any trainer pic the game
                     draws will show the donor art)

Always verifies by decompressing every injected blob back out of the OUTPUT
ROM and comparing raw bytes against the donor stream's decompressed form.
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent

FRONT_TBL = 0x23957C
PAL_TBL = 0x239A1C
N_SLOTS = 148
ROM_BASE = 0x08000000
SPRITES_ADDR = 0x08CF0000   # inside the 0xB71D04+0x18E7D3 free run, above WILD_* payloads (docs/FREE_SPACE.md)
CM_BUILD_SHA1 = None        # input is our own build; presence-checked, not pinned


def lz77_decompress(data, off=0):
    assert data[off] == 0x10, f"no LZ header at {off:#x}"
    size = data[off+1] | (data[off+2] << 8) | (data[off+3] << 16)
    out = bytearray()
    pos = off + 4
    while len(out) < size:
        flags = data[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = data[pos], data[pos+1]; pos += 2
                count = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                for _ in range(count):
                    out.append(out[-disp])
            else:
                out.append(data[pos]); pos += 1
    return bytes(out), pos - off


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-rom", default=str(ROOT / "build" / "radicalred_cm.gba"))
    ap.add_argument("--out-rom", default=str(ROOT / "build" / "radicalred_cm_sprites.gba"))
    ap.add_argument("--donors", default=str(ROOT / "sprites" / "donors" / "ashgray"))
    ap.add_argument("--test-all-slots", metavar="NAME",
                    help="repoint every front-pic slot at donor NAME (render-proof build)")
    a = ap.parse_args()

    donors = Path(a.donors)
    manifest_in = json.loads((donors / "manifest.json").read_text())
    rom = bytearray(Path(a.in_rom).read_bytes())

    # --- inject blobs ---------------------------------------------------
    cur = SPRITES_ADDR - ROM_BASE
    placed = {}
    for name in sorted(manifest_in["entries"]):
        gfx = (donors / f"{name}_front.lz").read_bytes()
        pal = (donors / f"{name}_frontpal.lz").read_bytes()
        for kind, blob in (("gfx", gfx), ("pal", pal)):
            cur = (cur + 3) & ~3
            region = rom[cur:cur + len(blob)]
            assert region == b"\xFF" * len(blob), \
                f"free-space collision at {cur:#x} for {name}/{kind}"
            rom[cur:cur + len(blob)] = blob
            placed.setdefault(name, {})[kind + "_addr"] = ROM_BASE + cur
            cur += len(blob)
    end_addr = ROM_BASE + cur
    total = cur - (SPRITES_ADDR - ROM_BASE)
    print(f"injected {len(placed)} donors, {total} bytes @ {SPRITES_ADDR:#x}..{end_addr:#x}")

    # --- optional: repoint all slots (render-proof) ----------------------
    if a.test_all_slots:
        d = placed[a.test_all_slots]
        for i in range(N_SLOTS):
            struct.pack_into("<I", rom, FRONT_TBL + i * 8, d["gfx_addr"])
            struct.pack_into("<I", rom, PAL_TBL + i * 8, d["pal_addr"])
        print(f"repointed ALL {N_SLOTS} front pic+palette slots -> {a.test_all_slots}")

    # --- verify by decode-back from the output image ---------------------
    fails = 0
    for name, d in placed.items():
        for kind, srcfile in (("gfx", f"{name}_front.lz"), ("pal", f"{name}_frontpal.lz")):
            want, _ = lz77_decompress((donors / srcfile).read_bytes())
            got, _ = lz77_decompress(rom, d[kind + "_addr"] - ROM_BASE)
            if want != got:
                print(f"VERIFY FAIL {name}/{kind}"); fails += 1
    if a.test_all_slots:
        for i in range(N_SLOTS):
            p = struct.unpack_from("<I", rom, FRONT_TBL + i * 8)[0]
            if p != placed[a.test_all_slots]["gfx_addr"]:
                print(f"VERIFY FAIL slot {i} ptr {p:#x}"); fails += 1
    print("decode-back verify:", "PASS" if fails == 0 else f"{fails} FAILURES")
    if fails:
        sys.exit(1)

    Path(a.out_rom).write_bytes(rom)
    out_manifest = {
        "input_rom": a.in_rom,
        "output_rom": a.out_rom,
        "output_sha1": hashlib.sha1(rom).hexdigest(),
        "sprites_region": [hex(SPRITES_ADDR), hex(end_addr)],
        "test_all_slots": a.test_all_slots,
        "placed": {k: {kk: hex(vv) for kk, vv in v.items()} for k, v in placed.items()},
    }
    mpath = Path(a.out_rom).with_suffix(".sprites.json")
    mpath.write_text(json.dumps(out_manifest, indent=2))
    print(f"wrote {a.out_rom}\n     + {mpath}")


if __name__ == "__main__":
    main()
