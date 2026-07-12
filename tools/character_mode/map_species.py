#!/usr/bin/env python3
"""Resolve Bulbapedia-scraped species names (rosters_raw.json) to Radical
Red SPECIES_* ids and reduce each to its evolution-family base stage.

Species-ID source: tools/cfru_donor/include/constants/species.h -- verified
byte-exact against the real in-ROM base-stats table (docs/ROUTINE_MAP.md,
"CONFIRMED -- the real base-stats table..."). Evolution-family reduction
uses the real in-ROM evolution table (table_base=0x17CD9B0, stride=128,
16 entries * 8 bytes/entry -- see docs/ROUTINE_MAP.md, "CONFIRMED --
evolution table found the same way, EVOS_PER_MON=16...").

Gen 9 species (Radical Red's own 82-entry extension, indices 1294-1375)
are NOT yet name-resolved (docs/ROUTINE_MAP.md, "OPEN -- Gen 9 species
names...") -- any Bulbapedia name that doesn't match a Gen 1-8/alt-form
SPECIES_* constant falls into unmatched_names.txt for now, expected to
include real Gen 9 species until that gap is closed.

Usage: map_species.py
Reads:  characters.txt, rosters_raw.json
Writes: rosters_mapped.json, roster_review.csv, unmatched_names.txt
"""
import json
import re
import struct
from pathlib import Path

HERE = Path(__file__).parent
CFRU_SPECIES_H = HERE / "../cfru_donor/include/constants/species.h"
ROM_PATH = HERE / "../../rom/radicalred 4.1.gba"
ROSTERS_RAW = HERE / "rosters_raw.json"

BASE_STATS_TABLE_BASE = 0x17B98EC
BASE_STATS_STRIDE = 28
EVO_TABLE_BASE = 0x17CD9B0
EVO_ENTRIES_PER_MON = 16
EVO_ENTRY_SIZE = 8
EVO_BLOCK_SIZE = EVO_ENTRIES_PER_MON * EVO_ENTRY_SIZE

# Legendary/mythical/Ultra-Beast/Paradox base-stage species -- excluded from
# the starter carousel but still catchable, mirrors ROWE/Unbound's
# LEGENDARY_BASES. Gen 9 legends omitted for now (species IDs not resolved).
LEGENDARY_BASES = {
    "SPECIES_ARTICUNO", "SPECIES_ZAPDOS", "SPECIES_MOLTRES", "SPECIES_MEWTWO", "SPECIES_MEW",
    "SPECIES_RAIKOU", "SPECIES_ENTEI", "SPECIES_SUICUNE", "SPECIES_LUGIA", "SPECIES_HO_OH",
    "SPECIES_CELEBI", "SPECIES_REGIROCK", "SPECIES_REGICE", "SPECIES_REGISTEEL", "SPECIES_LATIAS",
    "SPECIES_LATIOS", "SPECIES_KYOGRE", "SPECIES_GROUDON", "SPECIES_RAYQUAZA", "SPECIES_JIRACHI",
    "SPECIES_DEOXYS", "SPECIES_UXIE", "SPECIES_MESPRIT", "SPECIES_AZELF", "SPECIES_DIALGA",
    "SPECIES_PALKIA", "SPECIES_HEATRAN", "SPECIES_REGIGIGAS", "SPECIES_GIRATINA", "SPECIES_CRESSELIA",
    "SPECIES_PHIONE", "SPECIES_MANAPHY", "SPECIES_DARKRAI", "SPECIES_SHAYMIN", "SPECIES_ARCEUS",
    "SPECIES_VICTINI", "SPECIES_COBALION", "SPECIES_TERRAKION", "SPECIES_VIRIZION", "SPECIES_TORNADUS",
    "SPECIES_THUNDURUS", "SPECIES_RESHIRAM", "SPECIES_ZEKROM", "SPECIES_LANDORUS", "SPECIES_KYUREM",
    "SPECIES_KELDEO", "SPECIES_MELOETTA", "SPECIES_GENESECT", "SPECIES_XERNEAS", "SPECIES_YVELTAL",
    "SPECIES_ZYGARDE", "SPECIES_DIANCIE", "SPECIES_HOOPA", "SPECIES_VOLCANION", "SPECIES_TYPE_NULL",
    "SPECIES_SILVALLY", "SPECIES_TAPU_KOKO", "SPECIES_TAPU_LELE", "SPECIES_TAPU_BULU", "SPECIES_TAPU_FINI",
    "SPECIES_COSMOG", "SPECIES_COSMOEM", "SPECIES_SOLGALEO", "SPECIES_LUNALA", "SPECIES_NECROZMA",
    "SPECIES_MAGEARNA", "SPECIES_MARSHADOW", "SPECIES_ZERAORA", "SPECIES_MELTAN", "SPECIES_MELMETAL",
    "SPECIES_ZACIAN", "SPECIES_ZAMAZENTA", "SPECIES_ETERNATUS", "SPECIES_KUBFU", "SPECIES_URSHIFU",
    "SPECIES_ZARUDE", "SPECIES_REGIELEKI", "SPECIES_REGIDRAGO", "SPECIES_GLASTRIER", "SPECIES_SPECTRIER",
    "SPECIES_CALYREX",
}

# Hand-curated fixes for Bulbapedia display-name <-> derived-constant-name
# mismatches. Discovered via unmatched_names.txt review, NOT ported from
# ROWE/Unbound's own dicts (those are for a different name-table convention
# -- CFRU's species.h identifiers have their own quirks). Maps a normalized
# Bulbapedia name to the exact SPECIES_* constant.
NAME_FIXES = {
    "farfetchd": "SPECIES_FARFETCHD",
    "mrmime": "SPECIES_MR_MIME",
    "mimejr": "SPECIES_MIME_JR",
    "hooh": "SPECIES_HO_OH",
    "porygonz": "SPECIES_PORYGON_Z",
    "typenull": "SPECIES_TYPE_NULL",
    "jangmoo": "SPECIES_JANGMO_O",
    "hakamoo": "SPECIES_HAKAMO_O",
    "kommoo": "SPECIES_KOMMO_O",
    "nidoranf": "SPECIES_NIDORAN_F",
    "nidoranm": "SPECIES_NIDORAN_M",
    "mrrime": "SPECIES_MR_RIME",
    "sirfetchd": "SPECIES_SIRFETCHD",
    # Species with no plain base constant in CFRU -- only color/flavor-variant
    # constants exist (these Pokemon are inherently multi-form in-game).
    # Mapped to a representative default form.
    "basculin": "SPECIES_BASCULIN_RED",
    "alcremie": "SPECIES_ALCREMIE_STRAWBERRY",
    "minior": "SPECIES_MINIOR_SHIELD",
    "urshifu": "SPECIES_URSHIFU_SINGLE",
}


def parse_species_h():
    """Returns {SPECIES_CONST_NAME: int_id}."""
    pat = re.compile(r"#define\s+(SPECIES_\w+)\s+(0x[0-9A-Fa-f]+|\d+)")
    out = {}
    with open(CFRU_SPECIES_H) as f:
        for line in f:
            m = pat.match(line.strip())
            if m:
                out[m.group(1)] = int(m.group(2), 0)
    return out


ACCENT_FIXES = str.maketrans({
    "é": "e", "É": "e", "♂": "m", "♀": "f",
})


def normalize(name):
    """Lowercase, fold accents/gender symbols, strip remaining non-alphanumerics."""
    name = name.translate(ACCENT_FIXES)
    return re.sub(r"[^a-z0-9]", "", name.lower())


def derive_display_name(const_name):
    """SPECIES_MR_MIME -> 'mrmime' (normalized), for matching against
    normalized Bulbapedia names. Strips known alt-form suffixes so alt-forms
    match their base display name too (we want the BASE constant to win)."""
    body = const_name[len("SPECIES_"):]
    return normalize(body)


ALT_FORM_SUFFIXES = [
    "_MEGA_X", "_MEGA_Y", "_MEGA", "_GIGA", "_ALOLA", "_GALAR", "_HISUI", "_PALDEA",
    "_A", "_G", "_H", "_P",  # short regional-form suffixes CFRU uses (Alolan/Galarian/Hisuian/Paldean)
    "_THERIAN", "_ORIGIN", "_SKY", "_ZEN", "_PRIMAL", "_ATTACK", "_DEFENSE", "_SPEED",
    "_RAINY", "_SNOWY", "_SUNNY", "_SANDY", "_TRASH",
]


def is_base_form(const_name):
    """Heuristic: does this constant look like a base (non-alt-form) species?"""
    for suf in ALT_FORM_SUFFIXES:
        if const_name.endswith(suf):
            return False
    return True


def build_evolution_parent_map(rom_data, species_by_id, max_id):
    """Walk the confirmed evolution table for every species 1..max_id and
    build {target_species_id: source_species_id} (child -> parent)."""
    parent = {}
    for species_id in range(1, max_id + 1):
        block_off = EVO_TABLE_BASE + species_id * EVO_BLOCK_SIZE
        for i in range(EVO_ENTRIES_PER_MON):
            e_off = block_off + i * EVO_ENTRY_SIZE
            method, param, target, unknown = struct.unpack(
                "<HHHH", rom_data[e_off:e_off + 8]
            )
            if method != 0 and target != 0 and target in species_by_id:
                # First writer wins; don't overwrite an already-known parent
                # (a species should have one canonical evolutionary lineage).
                parent.setdefault(target, species_id)
    return parent


def get_base_form(species_id, parent_map):
    seen = set()
    cur = species_id
    while cur in parent_map and cur not in seen:
        seen.add(cur)
        cur = parent_map[cur]
    return cur


def main():
    species_by_name = parse_species_h()  # SPECIES_X -> id
    species_by_id = {v: k for k, v in species_by_name.items()}
    max_gen8_id = species_by_name["SPECIES_URSHIFU_RAPID_GIGA"]  # 1293, confirmed table upper bound for the known range

    # Build normalized-name -> const-name index, preferring base forms when
    # multiple constants normalize to the same display name.
    name_index = {}
    for const_name in species_by_name:
        norm = derive_display_name(const_name)
        if norm not in name_index or (is_base_form(const_name) and not is_base_form(name_index[norm])):
            name_index[norm] = const_name

    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    parent_map = build_evolution_parent_map(rom_data, species_by_id, max_gen8_id)

    with open(ROSTERS_RAW) as f:
        rosters_raw = json.load(f)

    mapped = {}
    unmatched = []
    review_rows = []

    for char_name, info in rosters_raw.items():
        resolved_bases = set()
        for sp_name in info["species"]:
            norm = normalize(sp_name)
            const_name = NAME_FIXES.get(norm) or name_index.get(norm)
            if const_name is None:
                unmatched.append(f"{char_name}\t{sp_name}")
                continue
            species_id = species_by_name[const_name]
            base_id = get_base_form(species_id, parent_map)
            base_const = species_by_id.get(base_id, const_name)
            resolved_bases.add(base_const)
            review_rows.append((char_name, info["category"], sp_name, const_name, base_const, "Y"))

        mapped[char_name] = {
            "page": info["page"],
            "category": info["category"],
            "gen": info["gen"],
            "species": sorted(resolved_bases),
        }

    with open(HERE / "rosters_mapped.json", "w") as f:
        json.dump(mapped, f, indent=2)

    with open(HERE / "unmatched_names.txt", "w") as f:
        f.write("\n".join(unmatched) + "\n")

    with open(HERE / "roster_review.csv", "w") as f:
        f.write("character,category,scraped_name,species_const,base_form_const,keep\n")
        for row in review_rows:
            f.write(",".join(row) + "\n")

    total_species_refs = sum(len(v["species"]) for v in rosters_raw.values())
    resolved_refs = total_species_refs - len(unmatched)
    empty_rosters = [c for c, v in mapped.items() if not v["species"]]

    print(f"Characters: {len(mapped)}")
    print(f"Species references: {total_species_refs} total, {resolved_refs} resolved, {len(unmatched)} unmatched (PROVISIONAL -- see docs/ROUTINE_MAP.md Gen 9 gap)")
    print(f"Empty rosters after mapping: {len(empty_rosters)} {empty_rosters[:10]}")
    print("Wrote rosters_mapped.json, roster_review.csv, unmatched_names.txt")


if __name__ == "__main__":
    main()
