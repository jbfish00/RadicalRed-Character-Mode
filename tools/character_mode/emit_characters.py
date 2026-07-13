#!/usr/bin/env python3
"""Generate a flat binary character table from rosters_mapped.json.

Adapted from Unbound's emit_characters.py (itself adapted from ROWE's
C-header generator). Radical Red has no compile step to hook into either
-- this emits raw, position-independent POD data, matching the semantics
of ROWE's `struct CharacterInfo` but as three flat blobs to be injected
into ROM free space and pointer-patched by a later insert script (once
Phase 1 confirms real hook/table addresses):

  characters.bin  - fixed-size records, one per character (layout below)
  rosters.bin     - each character's roster: u16 species ids, SPECIES_NONE-
                    terminated, concatenated back to back
  names.bin       - each character's display name, Gen3-charmap-encoded
                    (reusing the validated charmap from
                    tools/search_gametext.py's technique), 0xFF-terminated,
                    concatenated back to back
  characters_manifest.json - human-readable record of every field + offset,
                    for the later insert step and for debugging

Record layout (12 bytes, native ROM byte order = little-endian), OFFSETS
ARE RELATIVE TO THE START OF THEIR OWN BLOB, not final ROM addresses -- the
insert step (Phase 1-informed) adds each blob's actual injected base address
and writes real 0x08xxxxxx pointers:
    u32 name_offset      -- offset into names.bin
    u32 roster_offset     -- offset into rosters.bin
    u16 sprite_asset_id   -- PLACEHOLDER 0xFFFF ("TBD") until Phase 3 finds
                             Radical Red's OW/trainer-pic tables; asset-none
                             equivalent once real ids exist
    u8  generation
    u8  flags             -- bit0: hasSignature: signature ace is roster[0]

species IDs referenced in rosters.bin are Radical Red's OWN real, ROM-
verified ids (see docs/ROUTINE_MAP.md: gBaseStats pointer-redirect table at
file offset 0x17B98EC, stride 28, indices 1-1375) -- unlike Unbound's
emitter, these are NOT provisional donor ids. rosters_mapped.json's ids
came from rr_pokedex_donor/data.js, cross-checked byte-exact against this
project's own independent ROM extraction (see CLAUDE.md v6/v7 status).
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHARMAP_PATH = "/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt"

sys.path.insert(0, HERE)
from map_species import LEGENDARY_NAMES  # noqa: E402  (single source of truth)

CATEGORIES = ["protagonist", "rival", "gymleader", "elite4", "champion", "villain", "anime"]


def load_charmap(path):
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                table[m.group(1)] = int(m.group(2), 16)
    return table


def encode_text(text, charmap):
    out = bytearray()
    for ch in text:
        if ch not in charmap:
            raise ValueError(f"character {ch!r} not in charmap (name: {text!r})")
        out.append(charmap[ch])
    out.append(0xFF)  # Gen3 string terminator
    return bytes(out)


def display_name(disp):
    if disp.endswith(" (anime)"):
        return disp[: -len(" (anime)")]
    return disp


def main():
    with open(os.path.join(HERE, "rosters_mapped.json")) as f:
        mapped = json.load(f)
    charmap = load_charmap(CHARMAP_PATH)

    order = []
    with open(os.path.join(HERE, "characters.txt")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            disp = line.split("|")[0].strip()
            if disp in mapped:
                order.append(disp)

    names_blob = bytearray()
    rosters_blob = bytearray()
    records = bytearray()
    manifest = []
    skipped = []

    for disp in order:
        info = mapped[disp]
        species = info["species"]
        if not species:
            skipped.append(disp)
            continue

        ids = [s["id"] for s in species]
        name_by_id = {s["id"]: s["name"] for s in species}
        starters = [i for i in ids if name_by_id[i] not in LEGENDARY_NAMES]
        legends = [i for i in ids if name_by_id[i] in LEGENDARY_NAMES]

        sig = info.get("signature")
        has_signature = 0
        if sig and sig.get("id") is not None:
            sig_id = sig["id"]
            if sig_id in starters:
                starters.remove(sig_id)
            elif sig_id in legends:
                legends.remove(sig_id)
            # Signature may not literally be in `ids` if evolution-family
            # reduction folded it elsewhere -- map_species.py's own
            # check_roster_consistency.py already guarantees the signature's
            # base form IS on the roster, so this is always safe.
            starters.insert(0, sig_id)
            has_signature = 1

        ordered_ids = starters + legends
        if not starters:
            manifest.append({"character": disp, "warning": "all-legendary roster, starter fallback needed"})

        name_off = len(names_blob)
        names_blob += encode_text(display_name(disp), charmap)

        roster_off = len(rosters_blob)
        for sid in ordered_ids:
            rosters_blob += struct.pack("<H", sid)
        rosters_blob += struct.pack("<H", 0)  # SPECIES_NONE terminator

        generation = info.get("gen", 0) or 1
        flags = has_signature & 0x1
        sprite_asset_id = 0xFFFF  # TBD -- RR OW/trainer-pic table not yet located (Phase 1/3)

        records += struct.pack("<IIHBB", name_off, roster_off, sprite_asset_id, generation, flags)

        manifest.append({
            "character": disp,
            "category": info.get("category"),
            "generation": generation,
            "name_offset": name_off,
            "roster_offset": roster_off,
            "roster_species_ids": ordered_ids,
            "starter_count": len(starters),
            "has_signature": bool(has_signature),
            "signature_id": sig.get("id") if sig else None,
            "signature_name": sig.get("name") if sig else None,
            "sprite_asset_id": "TBD",
        })

    with open(os.path.join(HERE, "characters.bin"), "wb") as f:
        f.write(records)
    with open(os.path.join(HERE, "rosters.bin"), "wb") as f:
        f.write(rosters_blob)
    with open(os.path.join(HERE, "names.bin"), "wb") as f:
        f.write(names_blob)
    with open(os.path.join(HERE, "characters_manifest.json"), "w") as f:
        json.dump({"record_count": len(order) - len(skipped), "record_size_bytes": 12,
                   "skipped_empty_roster": skipped, "characters": manifest}, f, indent=1)

    print("emitted %d characters (%d skipped empty)" % (len(order) - len(skipped), len(skipped)))
    print("  characters.bin: %d bytes (%d records x 12)" % (len(records), len(records) // 12))
    print("  rosters.bin:    %d bytes" % len(rosters_blob))
    print("  names.bin:      %d bytes" % len(names_blob))
    print("\nsprite_asset_id is a PLACEHOLDER (0xFFFF) for every record -- Phase 3 fills")
    print("this in once Radical Red's OW/trainer-pic tables are located (Phase 1).")
    print("Species ids are the REAL ROM-verified ids (not provisional donor ids).")


if __name__ == "__main__":
    main()
