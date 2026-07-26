#!/usr/bin/env python3
"""Emit per-character "wild encounter override" tables: a 10% chance for a random
non-legendary member of the active character's roster to replace the normal
wild-encounter roll, choosing the evolution stage whose level range best fits the
rolled level -- plus, since 2026-07-26, a separate 1% LEGENDARY table.

The legendary rule (spec: ../../game_plans/legendary_encounters.md, design locked
by the user 2026-07-26):

    roll 1%       -> a legendary from this character's roster
    else roll 10% -> a non-legendary roster member   (unchanged)
    else          -> the game's own wild table

The two rolls are independent and the legendary one goes first, so a character
with no legendary is completely unaffected: its legendary block has zero families
and the shim skips the roll entirely rather than burning an RNG call, which keeps
its encounter stream byte-identical to the pre-2026-07-26 build.

A legendary leaves the pool once CAUGHT -- read from the Pokedex, which costs no
new save state (the only reason this is implementable in a closed binary). The
one exemption: a character with NO non-legendary families at all keeps its
legendaries repeatable forever, or Cogita (whose entire roster is one legendary
family) would catch it once and then be able to catch nothing for the rest of the
run. That condition is known here, at emit time, and is emitted as flags bit0.

⚠️ Tobias no longer has a special case. He used to be hardcoded to a 1%
legendary-inclusive table in three places; the general rule reproduces that
exactly -- his non-legendary pool is empty (so he is also `repeatable`) and his
two legendaries sit in the legendary table at the same 1%. Deleting it was a
single atomic change across this file, inject_character_mode.py's
-DTOBIAS_CHAR_ID, and src/wild_encounter_mode.c; removing only some of the three
would silently reintroduce the divergence.

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
  wild_override_offsets.bin  -- NUM_CHARACTERS * u32, byte offset into
                                 wild_override.bin for character index i
                                 (0-based, i.e. VAR_CHARACTER_ID - 1 -- same
                                 order as characters.bin / rosters_expanded.bin).
  wild_legendary.bin         -- the 1% table, same per-family shape with one
                                 extra header byte:
      u8 flags          -- bit0: repeatable (this character has no non-legendary
                           families, so its legendaries are never retired)
      u8 num_families
      num_families * { u8 num_stages; num_stages * (u16 species, u8 lvlMin, u8 lvlMax) }
  wild_legendary_offsets.bin -- NUM_CHARACTERS * u32, same convention.
"""
import ast
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from map_species import LEGENDARY_NAMES  # noqa: E402  (single source of truth)

MAX_LEVEL = 100

# gSpeciesToNationalPokedexNum, read out of SpeciesToNationalPokedexNum's own
# literal pool at 0x080432B0 (disassembled 2026-07-26, this exact ROM). The dex
# filter at runtime converts species -> national dex number before touching the
# caught flags, and in this FireRed family the two genuinely differ: species 386
# is national dex 313 (Volbeat). Getting it wrong would silently filter the
# wrong species, which looks exactly like the feature not firing.
NATDEX_TABLE_ADDR = 0x098218F0
ROM_PATH = ROOT / "rom" / "radicalred 4.1.gba"

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


def load_natdex():
    """species id -> national dex number, straight from the ROM's own table."""
    rom = ROM_PATH.read_bytes()
    base = NATDEX_TABLE_ADDR - 0x08000000
    return lambda sid: struct.unpack_from("<H", rom, base + (sid - 1) * 2)[0]


def walk_family(base_id, species, allow_legendary=False):
    """Returns [(species_id, level_min, level_max), ...] for every stage
    reachable from base_id (level-gated boundaries where the ROM's own
    evolution data provides one, MAX_LEVEL-open otherwise).

    allow_legendary is for the 1% table only: it walks THROUGH legendary stages
    instead of stopping at them, which is what makes Cosmog -> Cosmoem ->
    Solgaleo/Lunala (the one genuinely multi-stage legendary line) come out as a
    level-banded family rather than a single stage.
    """
    stages = []

    def rec(sid, level_min, visited):
        if sid in visited or sid not in species:
            return
        if not allow_legendary and species[sid]["name"] in LEGENDARY_NAMES:
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
    # DERIVE the count, never hardcode it. This assert used to read
    # `== 210` and it failed the moment the 2026-07-25 roster audit added 28
    # Legends: Arceus characters -- the same trap that has now bitten this project
    # three times (SPRITE_PLAN.md §5). A stale literal here surfaces as an
    # AssertionError if you are lucky and as "wildpool size mismatch" downstream if
    # you are not, never as "the character count changed".
    assert len(chars) == manifest["record_count"], \
        ("manifest lists %d characters but record_count is %d -- re-run "
         "emit_characters.py" % (len(chars), manifest["record_count"]))
    assert all("roster_species_ids" in r for r in chars), \
        "stale manifest shape: an entry has no roster_species_ids"

    natdex = load_natdex()

    def pack_families(stage_lists):
        blocks = []
        for stages in stage_lists:
            if not stages:
                continue
            block = bytearray([min(len(stages), 255)])
            for sid, lo, hi in stages[:255]:
                block += struct.pack("<HBB", sid, lo, hi)
            blocks.append(block)
        return blocks

    data_blob = bytearray()
    offsets = []
    leg_blob = bytearray()
    leg_offsets = []
    report_families = []
    report_empty = []
    report_leg = []
    repeatable_chars = []
    natdex_zero = []

    for rec in chars:
        ids = rec["roster_species_ids"]
        # Filter by name, NOT rec["starter_count"] -- see the module docstring:
        # starter_count exempts a character's own signature mon from the
        # legendary ban (catch-gate semantics), this feature does not exempt
        # anything. The same split feeds BOTH tables, so a species can never end
        # up in neither or in both.
        is_leg = lambda i: species.get(i, {}).get("name") in LEGENDARY_NAMES
        non_legendary_bases = [i for i in ids if not is_leg(i)]
        legendary_bases = [i for i in ids if is_leg(i)]

        offsets.append(len(data_blob))
        fam_blocks = pack_families(
            walk_family(b, species) for b in non_legendary_bases)
        data_blob += bytes([min(len(fam_blocks), 255)])
        for block in fam_blocks:
            data_blob += block

        # --- the 1% legendary table ---
        leg_stage_lists = [walk_family(b, species, allow_legendary=True)
                           for b in legendary_bases]
        leg_blocks = pack_families(leg_stage_lists)
        # §1.2 exemption: no non-legendary families at all -> never retire the
        # legendaries, or this character catches one Pokemon and then nothing for
        # the rest of the run (Cogita, Tobias). Known here, at emit time.
        repeatable = bool(leg_blocks) and not fam_blocks
        if repeatable:
            repeatable_chars.append(rec["character"])
        leg_offsets.append(len(leg_blob))
        leg_blob += bytes([1 if repeatable else 0, min(len(leg_blocks), 255)])
        for block in leg_blocks:
            leg_blob += block

        for stages in leg_stage_lists:
            for sid, _lo, _hi in stages:
                # The runtime dex filter converts species -> national dex number
                # and a 0 there is the unguarded-index hazard RR inherited (see
                # src/wild_encounter_mode.c). Our shim treats natdex 0 as
                # "not caught" rather than calling the dex with it, so this is
                # not a crash risk -- but a legendary that cannot be retired is
                # still worth knowing about, so report it.
                if natdex(sid) == 0:
                    natdex_zero.append((rec["character"], sid))
                # The 1% table must contain ONLY legendaries: the 10% table is
                # what a non-legendary belongs in, and verify_artifacts.py checks
                # both directions against the built ROM.
                assert species[sid]["name"] in LEGENDARY_NAMES, (
                    "%s: non-legendary %s (%d) reached the legendary table"
                    % (rec["character"], species[sid]["name"], sid))

        report_families.append(len(fam_blocks))
        report_leg.append(len(leg_blocks))
        if not fam_blocks and not leg_blocks:
            report_empty.append(rec["character"])

    with open(HERE / "wild_override.bin", "wb") as f:
        f.write(data_blob)
    with open(HERE / "wild_override_offsets.bin", "wb") as f:
        for off in offsets:
            f.write(struct.pack("<I", off))
    with open(HERE / "wild_legendary.bin", "wb") as f:
        f.write(leg_blob)
    with open(HERE / "wild_legendary_offsets.bin", "wb") as f:
        for off in leg_offsets:
            f.write(struct.pack("<I", off))

    print(f"wild_override.bin: {len(data_blob)} bytes")
    print(f"wild_override_offsets.bin: {len(offsets) * 4} bytes ({len(offsets)} entries)")
    print(f"wild_legendary.bin: {len(leg_blob)} bytes")
    print(f"wild_legendary_offsets.bin: {len(leg_offsets) * 4} bytes "
          f"({len(leg_offsets)} entries)")
    print(f"families per character: min {min(report_families)}, "
          f"median {sorted(report_families)[len(report_families)//2]}, "
          f"max {max(report_families)}")
    n_with_leg = sum(1 for n in report_leg if n)
    print(f"legendary pools: {n_with_leg} of {len(chars)} characters "
          f"({100.0 * n_with_leg / len(chars):.0f}%), "
          f"{len({s for r in chars for s in r['roster_species_ids'] if species.get(s, {}).get('name') in LEGENDARY_NAMES})} "
          f"distinct legendary family bases, max {max(report_leg)} on one character")
    if repeatable_chars:
        print(f"  repeatable (no non-legendary families, §1.2 exemption): "
              f"{', '.join(repeatable_chars)}")
    if natdex_zero:
        print(f"  WARNING: {len(natdex_zero)} legendary stage(s) map to national "
              f"dex 0 and can never be retired: {natdex_zero[:6]}")
    if report_empty:
        print(f"WARNING: {len(report_empty)} characters can meet NOTHING in the "
              f"wild (no families in either table): {report_empty}")

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

    # ...and the mirror: Articuno, excluded from Red's 10% table, must be in his
    # 1% table. Without this the two halves could both be "correct" while the
    # legendary simply vanished -- the failure mode the whole legendary feature
    # is most exposed to, because "no legendary appeared" is also what success
    # looks like from the 10% table's side.
    p = leg_offsets[chars.index(red)]
    assert leg_blob[p] == 0, "Red should not be repeatable (he has non-legendaries)"
    n_fam = leg_blob[p + 1]
    p += 2
    red_leg = set()
    for _ in range(n_fam):
        n_st = leg_blob[p]; p += 1
        for _ in range(n_st):
            sid, lo, hi = struct.unpack_from("<HBB", leg_blob, p)
            p += 4
            red_leg.add(sid)
    assert 144 in red_leg, f"Red legendary sanity FAILED: {sorted(red_leg)}"
    assert not (red_leg & red_species), "a species is in BOTH of Red's tables"
    print(f"sanity Red legendary: OK (Articuno present, {len(red_leg)} legendary "
          f"stages, no overlap with the 10% table)")


if __name__ == "__main__":
    main()
