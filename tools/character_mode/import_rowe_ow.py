#!/usr/bin/env python3
"""Copy ROWE's player-grade overworld sheets into this repo, for the walk/run avatar.

Radical Red gives a character a full player avatar only when RR itself ships a
wardrobe costume for them (rr_costumes.py, 11 characters). Everyone else can
still have their OWN overworld sprite while walking and running: CFRU's
GetCustomGraphicsIdByState reads VAR_PLAYER_WALKRUN (0x501F) on its own, so
overriding just that state leaves bike, surf, fishing and the rest on the
gender default -- no animation set is ever handed frames it does not have.

ROWE already built the art: 18-frame 16x32 player-grade sheets (walk 0-8,
run 9-17), the exact layout RR's own player sheets use for frames 0-17. This
script copies each sheet's .4bpp and .gbapal into sprites/ow_player/ so the
injector stays self-contained (check_repo_selfcontained forbids reading ROWE
at build time), and writes sprites/ow_player/manifest.json recording, per
character, the ROWE symbol and file it came from and the art's donor set.

Only sheets ROWE itself marks player-safe are taken: its owGfxId must be in
ROWE's imported_ow.txt / imported_ow_donor.txt allowlists or end in _NORMAL
(the same gate ROWE's emit_characters.py applies), and the pic table must have
exactly 18 frames.

    python3 tools/character_mode/import_rowe_ow.py [--rowe PATH]
"""
import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "sprites" / "ow_player"
FRAMES = 18
# ROWE has player-grade sheets in two frame sizes: 16x32 (2x4 tiles) and 32x32
# (4x4 tiles, e.g. the Team Galactic commanders). Both use the same walk/run
# frame order, so both work under RR's player walk animation table.
SIZES = {(2, 4): (16, 32), (4, 4): (32, 32)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rowe", type=Path,
                    default=Path("/home/jbfish00/Documents/Pokemon Rowe Alteration"))
    rowe = ap.parse_args().rowe

    chars_h = (rowe / "src/data/characters.h").read_text()
    names = dict(re.findall(r'static const u8 sName_(\w+)\[\] = _\("([^"]*)"\);', chars_h))
    ow = {}
    for key, body in re.findall(r"\{\s*\.name = sName_(\w+),(.*?)\n    \}", chars_h, re.S):
        m = re.search(r"\.owGfxId = (OBJ_EVENT_GFX_\w+)", body)
        if m:
            ow[names[key]] = m.group(1)
    safe = set()
    for f in ("imported_ow.txt", "imported_ow_donor.txt"):
        safe |= {t for t in (rowe / "tools/character_mode" / f).read_text().split()
                 if t.startswith("OBJ_EVENT_GFX_")}
    ptrs = (rowe / "src/data/object_events/object_event_graphics_info_pointers.h").read_text()
    infos = (rowe / "src/data/object_events/object_event_graphics_info.h").read_text()
    pics = (rowe / "src/data/object_events/object_event_pic_tables.h").read_text()
    gfx = (rowe / "src/data/object_events/object_event_graphics.h").read_text()
    pal_tags = (rowe / "src/event_object_movement.c").read_text()

    rr_chars = {c["character"] for c in json.loads(
        (ROOT / "tools/character_mode/characters_manifest.json").read_text())["characters"]}

    OUT.mkdir(parents=True, exist_ok=True)
    manifest, skipped = {}, {}
    for name, gid in sorted(ow.items()):
        if name not in rr_chars:
            continue
        if not (gid in safe or gid.endswith("_NORMAL")):
            skipped[name] = f"{gid} is not on ROWE's player-safe allowlist"
            continue
        m = re.search(r"\[%s\]\s*=\s*&(\w+)" % gid, ptrs)
        if not m:
            skipped[name] = f"no graphics-info pointer for {gid}"
            continue
        info = re.search(r"const struct ObjectEventGraphicsInfo %s = \{([^}]*)\}" % m.group(1), infos)
        table = re.search(r"\b(gObjectEventPicTable_\w+)\b", info.group(1)) if info else None
        if not table:
            skipped[name] = f"no pic table in {m.group(1)}"
            continue
        rows = re.search(r"%s\[\] = \{(.*?)\};" % table.group(1), pics, re.S)
        frames = re.findall(r"overworld_frame\((\w+), (\d), (\d), (\d+)\)", rows.group(1)) if rows else []
        dims = {(int(w), int(h)) for _, w, h, _ in frames}
        if ([int(k) for *_, k in frames] != list(range(FRAMES))
                or len({f[0] for f in frames}) != 1 or len(dims) != 1 or not dims <= set(SIZES)):
            skipped[name] = f"{table.group(1)} is not one 18-frame 16x32 or 32x32 sheet"
            continue
        width, height = SIZES[dims.pop()]
        frame_bytes = width * height // 2
        sym = frames[0][0]
        pic = re.search(r"const u32 %s\[\] = INCBIN_U32\(\"([^\"]+)\.4bpp\"\)" % sym, gfx)
        pal_sym = re.search(r"\.paletteTag = (\w+)|\{0xFFFF, (\w+),", info.group(0))
        tag = pal_sym.group(1) or pal_sym.group(2)
        pal_name = re.search(r"\{(gObjectEventPal\w*), %s\}" % tag, pal_tags)
        pal = re.search(r"const u16 %s\[\] = INCBIN_U16\(\"([^\"]+)\.gbapal\"\)" % pal_name.group(1), gfx) if pal_name else None
        if not (pic and pal):
            skipped[name] = f"could not resolve the .4bpp/.gbapal for {sym}"
            continue
        src4, srcp = rowe / (pic.group(1) + ".4bpp"), rowe / (pal.group(1) + ".gbapal")
        data = src4.read_bytes()
        assert len(data) == FRAMES * frame_bytes, (name, src4, len(data))
        assert len(srcp.read_bytes()) == 32, (name, srcp)
        stem = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        shutil.copy2(src4, OUT / f"{stem}.4bpp")
        shutil.copy2(srcp, OUT / f"{stem}.gbapal")
        png = rowe / (pic.group(1) + ".png")
        if png.is_file():
            shutil.copy2(png, OUT / f"{stem}.png")
        manifest[name] = {"stem": stem, "width": width, "height": height, "rowe_gfx_id": gid, "rowe_pic": pic.group(1) + ".4bpp",
                          "rowe_palette": pal.group(1) + ".gbapal"}
    (OUT / "manifest.json").write_text(json.dumps(
        {"source": "ROWE (Pokemon Rowe Alteration) built overworld sheets; per-sheet "
                   "donor credits are ROWE's tools/character_mode/donor_ow_backs.txt "
                   "and imported_ow.txt, and this repo's CREDITS.md",
         "frames": FRAMES, "count": len(manifest), "characters": manifest,
         "skipped": skipped}, indent=1))
    print(f"copied {len(manifest)} player-grade sheets to {OUT.relative_to(ROOT)}; "
          f"skipped {len(skipped)}")
    for n, why in sorted(skipped.items()):
        print(f"  skip {n}: {why}")


if __name__ == "__main__":
    main()
