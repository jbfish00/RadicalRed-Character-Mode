#!/usr/bin/env python3
"""Emit per-character allowed-species bitmaps for the Phase 4 enforcement shim.

For each character (order = characters_manifest.json, same order as
characters.bin records), expands every roster base-form id forward through
the full evolution graph (rr_pokedex_donor/data.js `evolutions` field:
[[method, param, targetSpeciesId, extra], ...]) and sets one bit per
allowed species id.

Output: rosters_expanded.bin — NUM_CHARACTERS x 172-byte records
(1376 bits each, bit N = species id N allowed, LSB-first within each byte).
The shim tests `bitmap[species >> 3] & (1 << (species & 7))`.

Bitmap size/stride and NUM_SPECIES=1376 are pinned by the base-stats table
finding in docs/ROUTINE_MAP.md.
"""
import ast
import json
from pathlib import Path

HERE = Path(__file__).parent
NUM_SPECIES = 1376
STRIDE = (NUM_SPECIES + 7) // 8  # 172


def main():
    with open(HERE / "rr_pokedex_donor/data.js") as f:
        species = ast.literal_eval(f.read())["species"]
    with open(HERE / "characters_manifest.json") as f:
        manifest = json.load(f)

    # forward evolution adjacency
    evolves_to = {}
    for sid, info in species.items():
        targets = [e[2] for e in (info.get("evolutions") or []) if len(e) >= 3]
        evolves_to[sid] = [t for t in targets if t in species]

    out = bytearray()
    report = []
    for rec in manifest["characters"]:
        if "warning" in rec and "character" in rec and "roster_species_ids" not in rec:
            continue  # warning-only entries
        ids = rec["roster_species_ids"]
        allowed = set()
        stack = [i for i in ids if 0 < i < NUM_SPECIES]
        while stack:
            s = stack.pop()
            if s in allowed:
                continue
            allowed.add(s)
            stack.extend(evolves_to.get(s, []))
        bm = bytearray(STRIDE)
        for s in allowed:
            bm[s >> 3] |= 1 << (s & 7)
        out += bm
        report.append((rec["character"], len(ids), len(allowed)))

    with open(HERE / "rosters_expanded.bin", "wb") as f:
        f.write(out)

    n = len(report)
    print(f"emitted {n} bitmaps x {STRIDE} bytes = {len(out)} bytes -> rosters_expanded.bin")
    # sanity: Red's roster must allow Pikachu(25), Raichu(26), Alolan Raichu(1022)
    # via the Pichu(172) family, and must NOT allow Meowth(52).
    red_i = next(i for i, r in enumerate(report) if r[0] == "Red")
    bm = out[red_i*STRIDE:(red_i+1)*STRIDE]
    def has(s): return bool(bm[s >> 3] & (1 << (s & 7)))
    checks = [("Pichu 172", has(172), True), ("Pikachu 25", has(25), True),
              ("Raichu 26", has(26), True), ("Alolan Raichu 1022", has(1022), True),
              ("Meowth 52", has(52), False), ("SPECIES_NONE 0", has(0), False)]
    ok = True
    for name, got, want in checks:
        status = "OK" if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  sanity Red/{name}: {status}")
    if not ok:
        raise SystemExit("sanity checks FAILED")
    sizes = sorted(r[2] for r in report)
    print(f"  expanded roster sizes: min {sizes[0]}, median {sizes[n//2]}, max {sizes[-1]}")


if __name__ == "__main__":
    main()
