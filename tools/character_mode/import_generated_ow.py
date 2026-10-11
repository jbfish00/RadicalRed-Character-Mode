#!/usr/bin/env python3
"""Merge the workspace's GENERATED overworld sheets into sprites/ow_player/.

import_rowe_ow.py copies the player-grade sheets ROWE already had. The
characters ROWE had none for (anime cast, Gen 4-9 NPCs, the protagonists ROWE
drew with its own player graphics) got sheets made in the workspace
(game_plans/ow_generated/: base edits of real Gen 3 sheets, plus Red/Leaf/
Brendan/May/Gary from the official player graphics). They use the same layout
(18 frames, pokeemerald player order, 16x32 or 32x32, one 16-colour palette), so the
build treats them exactly like ROWE's.

Each is staged as gen_<stem>.{4bpp,gbapal,png} and recorded in manifest.json
with "origin": "generated". A character that already has a sheet keeps it.
Re-run this after import_rowe_ow.py (which rewrites the manifest from scratch).

The source directory is an ARGUMENT (the workspace's game_plans/ow_generated/),
never a literal path: check_repo_selfcontained.py forbids a sibling path here.

    python3 tools/character_mode/import_generated_ow.py <ow_generated dir>
"""
import json
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "sprites" / "ow_player"
# Protagonist and rival sheets built from official player graphics (sheets/).
PLAYER_SHEETS = {"Red": "red", "Leaf": "leaf", "Brendan": "brendan", "May": "may", "Gary": "gary"}


def generated(src):
    """{character: source path without extension} for every generated sheet."""
    specs = json.loads((src / "base_edits.json").read_text())
    out = {n: src / "base_edit" / s["stem"] for n, s in specs.items()
           if not n.startswith("_") and n in json.loads((src / "prompts.json").read_text())}
    out.update({n: src / "sheets" / s for n, s in PLAYER_SHEETS.items()})
    return out


def main(src):
    src = Path(src)
    man_path = DEST / "manifest.json"
    man = json.loads(man_path.read_text())
    chars = man["characters"]
    added = []
    for name, base in sorted(generated(src).items()):
        if name in chars and chars[name].get("origin") != "generated":
            continue                                  # an imported sheet wins
        gfx = base.with_suffix(".4bpp").read_bytes()
        pal = base.with_suffix(".gbapal").read_bytes()
        # PNG IHDR: width, height (the sheet is one frame wide, 18 frames tall)
        w, h = struct.unpack(">II", base.with_suffix(".png").read_bytes()[16:24])
        assert (w, h) in ((16, 32 * 18), (32, 32 * 18)), (name, w, h)
        assert len(gfx) == 18 * w * 32 // 2 and len(pal) == 32, (name, len(gfx), len(pal))
        stem = "gen_" + base.name
        for ext in (".4bpp", ".gbapal", ".png"):
            shutil.copy2(base.with_suffix(ext), DEST / f"{stem}{ext}")
        chars[name] = {"stem": stem, "width": w, "height": 32, "origin": "generated"}
        man.get("skipped", {}).pop(name, None)
        added.append(name)
    man["characters"] = dict(sorted(chars.items()))
    if "count" in man:
        man["count"] = len(chars)
    man_path.write_text(json.dumps(man, indent=1) + "\n")
    print(f"{len(added)} generated sheets staged; manifest now {len(chars)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
