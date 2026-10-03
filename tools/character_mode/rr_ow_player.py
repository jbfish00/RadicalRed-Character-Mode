#!/usr/bin/env python3
"""Walk/run overworld sprites for characters Radical Red has no costume for.

rr_costumes.py dresses the 11 characters RR's own wardrobe ships. Everyone else
with a player-grade sheet in sprites/ow_player/ (import_rowe_ow.py, copied from
ROWE's build) gets their own sprite for the ON-FOOT state only: CFRU's
GetCustomGraphicsIdByState reads VAR_PLAYER_WALKRUN (0x501F) by itself, so
bike, surf, field move, fishing and underwater keep the gender default. Their
sheets have walk and run frames and nothing else, so no other animation set is
ever handed one.

How the sprites reach the engine, all measured on the base ROM:

  * graphics ids are 16-bit; CFRU's lookup (0x0907E500) uses the HIGH byte to
    pick a table from the switcher at 0x091468CC. Slots 0-2 are RR's; slot 3
    is NULL and becomes ours, so our ids are 0x300 + k and touch nothing else.
  * each id's graphics info is RR's own costume walk struct (Lucas, table 1
    0xE1: anims = FireRed's player walk/run table 0x083A3470, 20 frames) with
    the images and palette tag replaced. Frames 0-17 are the sheet's; RR's
    sheets carry two extra frames (18, 19) in the same down-facing pose, so
    those point at frame 0, and the run frames are REORDERED (FRAME_MAP). A 32x32 sheet takes the oam and subsprite tables
    from RR's 32x32 bike struct (table 1 0xE4) instead.
  * palettes are looked up by tag in sObjectEventSpritePalettes (0x0835CCC8,
    451 {data, tag} entries ending at tag 0x11FF). Exactly three literals read
    it (0x0805F4D8, 0x0805F570, 0x0805F5C8, all in the vanilla palette
    functions). It is copied, our tags 0x1400 + k appended before the
    terminator, and the three literals repointed.

    python3 tools/character_mode/rr_ow_player.py     # print the plan
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHEETS = ROOT / "sprites" / "ow_player"

OW_SWITCHER = 0x091468CC
OW_SLOT = 3
OW_ID_BASE = OW_SLOT << 8
LUCAS_WALK = (0x0934FD7C, 0xE1)        # table 1 entry: a 16x32 player walk struct
LUCAS_BIKE = (0x0934FD7C, 0xE4)        # table 1 entry: a 32x32 player struct
PAL_TABLE = 0x0835CCC8
PAL_TABLE_REFS = (0x0805F4D8, 0x0805F570, 0x0805F5C8)
PAL_TAG_NONE = 0x11FF
PAL_TAG_BASE = 0x1400
INFO_SIZE = 0x24
# RR frame index -> sheet frame. The sheets are pokeemerald's player layout,
# RR's anims are FireRed's, and the two agree on frames 0-8 (stand + walk) but
# NOT on running (decoded from both anim tables, 2026-10-02):
#   FireRed 0x083A3470 [20..22]: south 9,10,9,11  north 12,13,12,14  west 15,16,15,17
#   pokeemerald RunSouth/North/West: south 12,9,13,9  north 14,10,15,10  west 16,11,17,11
# i.e. FireRed groups each direction's stand + two steps, Emerald groups the
# three stands (9-11) and then the steps. Copying 0-17 straight across showed a
# running player's BACK while running sideways (photographed). RR's extra
# frames 18-19 hold the down-facing pose: frame 0.
FRAME_MAP = [0, 1, 2, 3, 4, 5, 6, 7, 8,
             9, 12, 13,        # run south: stand, step, step
             10, 14, 15,       # run north
             11, 16, 17,       # run west (east is west flipped)
             0, 0]
RR_FRAMES = 20
VAR_PLAYER_WALKRUN = 0x501F
# Every var a wardrobe costume sets (rr_costumes.py). A walk-only character
# clears the rest, so a costume worn before activation cannot leave, say,
# Lucas's bike sprite under Misty.
COSTUME_VARS = (0x5020, 0x5021, 0x5022, 0x5023, 0x5024, 0x5025, 0x503D,
                0x5006, 0x5026, 0x5027)


def R(a):
    return a - 0x08000000


def _info(rom, table, idx):
    p = struct.unpack_from("<I", rom, R(table) + idx * 4)[0]
    return p, bytearray(rom[R(p):R(p) + INFO_SIZE])


def sheets():
    """{character: manifest entry} for the staged player-grade sheets."""
    return json.loads((SHEETS / "manifest.json").read_text())["characters"]


def pal_entries(rom):
    out, o = [], R(PAL_TABLE)
    while True:
        p, tag = struct.unpack_from("<IH", rom, o)
        out.append((p, tag))
        if tag == PAL_TAG_NONE:
            return out
        o += 8


def build(rom, characters, base):
    """Lay out every sprite for `characters` (display names, in order) at `base`.

    Returns (blob, ids, patches): the bytes to splice at `base`, {name: id},
    and [(file offset, old u32, new u32)] word patches (the switcher slot and
    the three palette-table literals).
    """
    have = sheets()
    names = [n for n in characters if n in have]
    assert len(names) <= 256, len(names)
    assert struct.unpack_from("<I", rom, R(OW_SWITCHER) + OW_SLOT * 4)[0] == 0, \
        "switcher slot 3 is no longer NULL in the base ROM"
    pals = pal_entries(rom)
    used_tags = {t for _, t in pals}
    assert all(PAL_TAG_BASE + k not in used_tags for k in range(len(names)))
    walk_p, walk = _info(rom, *LUCAS_WALK)
    bike_p, bike = _info(rom, *LUCAS_BIKE)
    # The fields we rely on, checked rather than assumed.
    assert struct.unpack_from("<Hhh", walk, 6) == (256, 16, 32), walk.hex()
    assert struct.unpack_from("<Hhh", bike, 6) == (512, 32, 32), bike.hex()

    n = len(names)
    pal_off = 0
    table_off = pal_off + (len(pals) + n) * 8
    info_off = table_off + 256 * 4
    img_off = info_off + n * INFO_SIZE
    data_off = (img_off + n * RR_FRAMES * 8 + 3) & ~3
    blob = bytearray(data_off)
    ids, cur = {}, data_off

    # palette table copy: RR's entries, ours, then the terminator
    for i, (p, tag) in enumerate(pals[:-1]):
        struct.pack_into("<IHH", blob, pal_off + i * 8, p, tag, 0)
    pal_data = []
    for k, name in enumerate(names):
        pal_data.append((PAL_TAG_BASE + k, (SHEETS / f"{have[name]['stem']}.gbapal").read_bytes()))
    term_at = pal_off + (len(pals) - 1 + n) * 8

    for k, name in enumerate(names):
        e = have[name]
        w, h = e["width"], e["height"]
        fb = w * h // 2
        gfx = (SHEETS / f"{e['stem']}.4bpp").read_bytes()
        assert len(gfx) == 18 * fb, (name, len(gfx))
        gfx_addr = base + cur
        blob += gfx
        cur += len(gfx)
        pal_addr = base + cur
        blob += pal_data[k][1]
        cur += 32
        struct.pack_into("<IHH", blob, pal_off + (len(pals) - 1 + k) * 8,
                         pal_addr, PAL_TAG_BASE + k, 0)
        frames = FRAME_MAP
        img_addr = base + img_off + k * RR_FRAMES * 8
        for f, src in enumerate(frames):
            struct.pack_into("<IHH", blob, img_off + k * RR_FRAMES * 8 + f * 8,
                             gfx_addr + src * fb, fb, 0)
        info = bytearray(walk)
        struct.pack_into("<H", info, 2, PAL_TAG_BASE + k)          # paletteTag
        struct.pack_into("<H", info, 4, PAL_TAG_NONE)               # reflection tag
        if (w, h) == (32, 32):
            struct.pack_into("<Hhh", info, 6, 512, 32, 32)
            info[0x10:0x18] = bike[0x10:0x18]                       # oam, subsprites
        struct.pack_into("<I", info, 0x1C, img_addr)                # images
        blob[info_off + k * INFO_SIZE:info_off + (k + 1) * INFO_SIZE] = info
        struct.pack_into("<I", blob, table_off + k * 4, base + info_off + k * INFO_SIZE)
        ids[name] = OW_ID_BASE + k
    struct.pack_into("<IHH", blob, term_at, pals[-1][0], PAL_TAG_NONE, 0)

    patches = [(R(OW_SWITCHER) + OW_SLOT * 4, 0, base + table_off)]
    for ref in PAL_TABLE_REFS:
        patches.append((R(ref), PAL_TABLE, base + pal_off))
    return bytes(blob), ids, patches


def avatar_sets(gfx_id):
    """The setvar run a walk-only character's activation applies."""
    return [(VAR_PLAYER_WALKRUN, gfx_id)] + [(v, 0) for v in COSTUME_VARS]


if __name__ == "__main__":
    rom = (ROOT / "rom" / "radicalred 4.1.gba").read_bytes()
    names = sorted(sheets())
    blob, ids, patches = build(rom, names, 0x08B72000)
    print(f"{len(ids)} sprites, {len(blob):,} B")
    for off, old, new in patches:
        print(f"  patch file {off:#x}: {old:#x} -> {new:#x}")
