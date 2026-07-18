#!/usr/bin/env python3
"""Emit per-character "wild encounter override" tables for the new Phase 7
feature: a 10% chance for a random non-legendary member of the active
character's roster to replace the normal wild-encounter roll, choosing the
evolution stage whose level range best fits the rolled level.

Data source: same rr_pokedex_donor/data.js evolution graph already used by
emit_bitmaps.py (evolutions: [[method, param, targetSpeciesId, extra], ...]),
plus characters_manifest.json's own starter_count split (roster_species_ids
= non-legendary "starters" first, legendary "legends" appended after --
see emit_characters.py) so this script doesn't need to re-derive the
legendary exclusion itself.

Family/stage model
------------------
Each non-legendary roster entry (a family BASE id) is walked forward through
its real evolution graph (excluding EVO_MEGA=254/EVO_GIGANTAMAX=253 -- battle-
only forms, never a wild species) to build every reachable stage. Evolution
branches (e.g. Eevee's stones, Tyrogue's three paths) are walked as a tree,
not flattened. Any stage whose name is in LEGENDARY_NAMES stops the walk on
that branch (a legendary/mythical is never added, and nothing evolving FROM
one is walked further either).

Legendary exclusion is done by NAME (map_species.py's LEGENDARY_NAMES), not
by characters_manifest.json's starter_count split -- those aren't the same
thing. emit_characters.py deliberately exempts a character's SIGNATURE mon
from the legendary ban even when it is one (e.g. Gladion's signature is
Type: Null, a sub-legendary, but it's still counted as one of his
"starters" so it can be his catch-gate starter grant). This feature has no
such exemption -- the task spec says "exclude legendary/mythical roster
members entirely" with no signature carve-out, so Type: Null/Silvally (and
any other signature-legendary) are excluded from the wild-encounter table
even though they appear in roster_species_ids[:starter_count].

Per-stage level range is derived from the ROM's own evolution data:
  - If a stage is reached (or reaches a child) via a level-gated method
    (LEVEL_METHODS below), that level is a hard boundary: a stage's range
    starts at the level it evolved in at (0/1 for the family base) and ends
    one below whatever level its most-restrictive level-gated child needs
    (or MAX_LEVEL if it has no level-gated child).
  - Non-level methods (item/trade/friendship/etc, no level parameter) don't
    supply a boundary; the child simply inherits the parent's current lower
    bound, so both remain "in range" together -- there is no canon level
    data to split them on. This is the documented "nearest-stage fallback"
    case: ties are broken at runtime by picking the CLOSEST range (both
    being equally close when levels agree), then, for exact ties, the
    later/more-evolved stage wins (see CM_PickWildOverrideStage in
    src/character_mode.c) -- a deliberate, documented heuristic, not a
    canon fact, since RR doesn't expose a "canon wild level" for evolutions
    that aren't level-gated.

Output (both consumed directly by the injected shim, no further processing):
  wild_override.bin          -- concatenated per-character blocks:
      u8 num_families
      num_families * { u8 num_stages; num_stages * (u16 species, u8 lvlMin, u8 lvlMax) }
  wild_override_offsets.bin  -- 184 * u32, byte offset into wild_override.bin
                                 for character index i (0-based, i.e.
                                 VAR_CHARACTER_ID - 1 -- same order as
                                 characters.bin / rosters_expanded.bin).
"""
import ast
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from map_species import LEGENDARY_NAMES  # noqa: E402  (single source of truth)

MAX_LEVEL = 100

# struct Evolution.method values that take a LEVEL as their param (see
# tools/cfru_donor/include/pokemon.h "enum EvolutionMethods" -- values are
# the enum's implicit 0-based index, cross-checked against data.js samples,
# e.g. Bulbasaur->Ivysaur is [4, 16, 2, 0] = EVO_LEVEL at level 16).
LEVEL_METHODS = {
    4,   # EVO_LEVEL
    8, 9, 10,          # EVO_LEVEL_ATK_GT_DEF / _EQ_DEF / _LT_DEF
    11, 12, 13, 14,    # EVO_LEVEL_SILCOON/CASCOON/NINJASK/SHEDINJA
    18,                # EVO_TYPE_IN_PARTY ("after given level")
    20, 21,            # EVO_MALE_LEVEL / EVO_FEMALE_LEVEL
    22, 23,            # EVO_LEVEL_NIGHT / EVO_LEVEL_DAY
    28,                # EVO_LEVEL_SPECIFIC_TIME_RANGE
    35,                # EVO_LEVEL_HOLD_ITEM
}
# Battle-only forms -- never a wild species, excluded from the stage walk.
EXCLUDED_METHODS = {0xFD, 0xFE}  # EVO_GIGANTAMAX, EVO_MEGA


def load_species():
    with open(HERE / "rr_pokedex_donor" / "data.js") as f:
        return ast.literal_eval(f.read())["species"]


def walk_family(base_id, species):
    """Returns [(species_id, level_min, level_max), ...] for every stage
    reachable from base_id (level-gated boundaries where the ROM's own
    evolution data provides one, MAX_LEVEL-open otherwise)."""
    stages = []

    def rec(sid, level_min, visited):
        if sid in visited or sid not in species:
            return
        if species[sid]["name"] in LEGENDARY_NAMES:
            return  # never add a legendary/mythical stage, nor walk past one
        visited = visited | {sid}
        evos = [e for e in (species[sid].get("evolutions") or [])
                if len(e) >= 3 and e[0] not in EXCLUDED_METHODS and e[2] in species]
        level_gated = [e[1] for e in evos if e[0] in LEVEL_METHODS]
        level_max = (min(level_gated) - 1) if level_gated else MAX_LEVEL
        level_max = max(level_max, level_min)
        stages.append((sid, level_min, level_max))
        for method, param, target, _extra in evos:
            child_min = param if method in LEVEL_METHODS else level_min
            rec(target, child_min, visited)

    rec(base_id, 1, frozenset())
    return stages


def main():
    with open(HERE / "characters_manifest.json") as f:
        manifest = json.load(f)
    species = load_species()

    chars = manifest["characters"]
    assert len(chars) == 184, len(chars)

    data_blob = bytearray()
    offsets = []
    report_families = []
    report_empty = []

    for rec in chars:
        ids = rec["roster_species_ids"]
        # Filter by name, NOT rec["starter_count"] -- see the module
        # docstring: starter_count exempts a character's own signature mon
        # from the legendary ban (catch-gate semantics), this feature does
        # not exempt anything (task spec: exclude legendary/mythical roster
        # members entirely, no carve-out).
        non_legendary_bases = [i for i in ids if species.get(i, {}).get("name") not in LEGENDARY_NAMES]

        offsets.append(len(data_blob))
        fam_blocks = []
        for base_id in non_legendary_bases:
            stages = walk_family(base_id, species)
            if not stages:
                continue
            block = bytearray([min(len(stages), 255)])
            for sid, lo, hi in stages[:255]:
                block += struct.pack("<HBB", sid, lo, hi)
            fam_blocks.append(block)

        data_blob += bytes([min(len(fam_blocks), 255)])
        for block in fam_blocks:
            data_blob += block

        report_families.append(len(fam_blocks))
        if not fam_blocks:
            report_empty.append(rec["character"])

    with open(HERE / "wild_override.bin", "wb") as f:
        f.write(data_blob)
    with open(HERE / "wild_override_offsets.bin", "wb") as f:
        for off in offsets:
            f.write(struct.pack("<I", off))

    print(f"wild_override.bin: {len(data_blob)} bytes")
    print(f"wild_override_offsets.bin: {len(offsets) * 4} bytes ({len(offsets)} entries)")
    print(f"families per character: min {min(report_families)}, "
          f"median {sorted(report_families)[len(report_families)//2]}, "
          f"max {max(report_families)}")
    if report_empty:
        print(f"WARNING: {len(report_empty)} characters have zero eligible "
              f"(non-legendary) families: {report_empty}")

    # sanity: Red's roster must include a Pichu/Pikachu/Raichu family with a
    # level-gated split (Pichu evolves via friendship, not level -- so Pichu
    # and Pikachu share a range; Pikachu->Raichu(26)/Alolan Raichu(1022) are
    # both EVO_ITEM, also share a range with Pikachu), and must NOT include
    # Articuno (a legendary present on Red's real roster, but excluded here).
    red = next(r for r in chars if r["character"] == "Red")
    red_off = offsets[chars.index(red)]
    p = red_off
    n_fam = data_blob[p]; p += 1
    red_species = set()
    for _ in range(n_fam):
        n_st = data_blob[p]; p += 1
        for _ in range(n_st):
            sid, lo, hi = struct.unpack_from("<HBB", data_blob, p)
            p += 4
            red_species.add(sid)
    assert {172, 25, 26, 1022} <= red_species, f"Red family sanity FAILED: {red_species}"
    assert 144 not in red_species, "Red sanity FAILED: Articuno (legendary) present"
    print("sanity Red: OK (Pichu/Pikachu/Raichu family present, Articuno excluded)")


if __name__ == "__main__":
    main()
