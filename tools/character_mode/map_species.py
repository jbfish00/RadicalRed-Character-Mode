#!/usr/bin/env python3
"""Resolve Bulbapedia-scraped species names (rosters_raw.json) to Radical
Red species ids and reduce each to its evolution-family base stage.

Species-ID/name source: tools/character_mode/rr_pokedex_donor/data.js --
a full species database (name, stats, type, evolutions, and a precomputed
`ancestor` = evolution-family base id) pulled from the community Radical
Red Pokedex (github.com/JwowSquared/Radical-Red-Pokedex, dex.radicalred.net).
Cross-validated byte-exact against our own ROM extraction (28-byte
base-stats records at file offset 0x17B98EC -- see docs/ROUTINE_MAP.md,
"CONFIRMED -- the real base-stats table...") for all 82 species we
independently extracted, so this is treated as authoritative rather than
a guess. It also resolves the earlier "OPEN -- Gen 9 species names" gap
directly (e.g. Sprigatito turned out to be species 921, not in the
1294-1375 range we'd been assuming -- that range is actually Hisuian/
alt-form species, see docs/ROUTINE_MAP.md for the full story).

Usage: map_species.py
Reads:  rosters_raw.json, rr_pokedex_donor/data.js
Writes: rosters_mapped.json, roster_review.csv, unmatched_names.txt
"""
import ast
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DEX_DATA = HERE / "rr_pokedex_donor/data.js"
ROSTERS_RAW = HERE / "rosters_raw.json"

# Legendary/mythical/Ultra-Beast/Paradox base-stage species -- excluded from
# the starter carousel but still catchable, mirrors ROWE/Unbound's
# LEGENDARY_BASES. Matched by name (not id) since data.js is the id source.
LEGENDARY_NAMES = {
    "Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune", "Lugia",
    "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre",
    "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf", "Dialga",
    "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy",
    "Darkrai", "Shaymin", "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion",
    "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo",
    "Meloetta", "Genesect", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa",
    "Volcanion", "Type: Null", "Silvally", "Tapu Koko", "Tapu Lele", "Tapu Bulu",
    "Tapu Fini", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Necrozma", "Magearna",
    "Marshadow", "Zeraora", "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus",
    "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier",
    "Calyrex", "Enamorus", "Wo-Chien", "Chien-Pao", "Ting-Lu", "Chi-Yu", "Koraidon",
    "Miraidon", "Walking Wake", "Iron Leaves", "Fezandipiti", "Munkidori", "Okidogi",
    "Ogerpon", "Terapagos", "Pecharunt", "Raging Bolt", "Iron Crown", "Iron Boulder",
    "Gouging Fire",
}

ACCENT_FIXES = str.maketrans({"é": "e", "É": "e", "♂": "m", "♀": "f"})


def normalize(name):
    """Lowercase, fold accents/gender symbols, strip remaining non-alphanumerics."""
    name = name.translate(ACCENT_FIXES)
    return re.sub(r"[^a-z0-9]", "", name.lower())


# Hand-curated fixes for Bulbapedia display-name <-> Radical-Red-Pokedex
# name mismatches. Discovered via unmatched_names.txt review.
NAME_FIXES = {
    # (currently empty after switching to the authoritative dex data source
    # -- data.js's names match Bulbapedia far more closely than
    # species.h-derived names did. Re-populate from unmatched_names.txt
    # if new mismatches turn up.)
}


def load_dex():
    with open(DEX_DATA) as f:
        data = ast.literal_eval(f.read())
    return data["species"]  # {id: {name, key, ancestor, stats, type, ...}}


def build_name_index(species):
    """normalized display name -> preferred species id, when multiple ids
    share a display name (e.g. Venusaur vs Venusaur-Mega; or Rattata vs
    Rattata-Alola, where BOTH are self-ancestored -- regional variants
    don't evolve from each other, so "is this a base form" alone can't
    disambiguate them). Radical Red's species ids append every alt/regional/
    Mega/Gigantamax form at a HIGHER id than its corresponding base species
    (verified: every Mega/Alola/Galar/Hisui/Paldea-regional/Gigantamax
    variant checked in this dataset has a strictly higher id than its base
    -- see docs/ROUTINE_MAP.md), so the lowest id among same-named
    candidates is always the intended match for a plain Bulbapedia name.
    Picking explicitly by min(id) rather than relying on dict insertion
    order keeps this correct even if data.js's key order ever changes."""
    groups = {}
    for sid, info in species.items():
        groups.setdefault(normalize(info["name"]), []).append(sid)
    return {norm: min(ids) for norm, ids in groups.items()}


def main():
    species = load_dex()
    name_index = build_name_index(species)

    with open(ROSTERS_RAW) as f:
        rosters_raw = json.load(f)

    mapped = {}
    unmatched = []
    review_rows = []

    for char_name, info in rosters_raw.items():
        resolved_bases = set()
        for sp_name in info["species"]:
            norm = normalize(sp_name)
            sid = None
            fix_name = NAME_FIXES.get(norm)
            if fix_name:
                sid = name_index.get(normalize(fix_name))
            if sid is None:
                sid = name_index.get(norm)
            if sid is None:
                unmatched.append(f"{char_name}\t{sp_name}")
                continue
            base_id = species[sid].get("ancestor", sid)
            base_name = species[base_id]["name"]
            resolved_bases.add(base_name)
            review_rows.append((char_name, info["category"], sp_name, species[sid]["key"], base_name, "Y"))

        mapped[char_name] = {
            "page": info["page"],
            "category": info["category"],
            "gen": info["gen"],
            "species": sorted(resolved_bases),
        }

    with open(HERE / "rosters_mapped.json", "w") as f:
        json.dump(mapped, f, indent=2)

    with open(HERE / "unmatched_names.txt", "w") as f:
        f.write("\n".join(unmatched) + ("\n" if unmatched else ""))

    with open(HERE / "roster_review.csv", "w") as f:
        f.write("character,category,scraped_name,species_key,base_form_name,keep\n")
        for row in review_rows:
            f.write(",".join(row) + "\n")

    total_species_refs = sum(len(v["species"]) for v in rosters_raw.values())
    resolved_refs = total_species_refs - len(unmatched)
    empty_rosters = [c for c, v in mapped.items() if not v["species"]]

    print(f"Characters: {len(mapped)}")
    print(f"Species references: {total_species_refs} total, {resolved_refs} resolved, {len(unmatched)} unmatched")
    print(f"Empty rosters after mapping: {len(empty_rosters)} {empty_rosters[:10]}")
    print("Wrote rosters_mapped.json, roster_review.csv, unmatched_names.txt")


if __name__ == "__main__":
    main()
