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

# Known signature/ace Pokemon per character (any stage; reduced to the
# family's evolution-family base below, same as roster species). Copied
# verbatim from ROWE's map_species.py (the reference implementation) --
# ROWE's full 184-character seed list is this project's own, so every key
# here matches a real character; the 5 characters absent (Calem, Gloria,
# Hugh, Nate, Victor -- all late-gen protagonists) get no signature and
# fall back to a random starter, matching ROWE's own documented behavior.
SIGNATURES = {
 "Red":"Pikachu","Leaf":"Eevee","Blue":"Pidgeot","Lance":"Dragonite",
 "Lorelei":"Lapras","Bruno":"Machamp","Agatha":"Gengar","Koga":"Weezing",
 "Brock":"Onix","Misty":"Starmie","Lt. Surge":"Pikachu","Erika":"Vileplume",
 "Sabrina":"Alakazam","Blaine":"Arcanine","Giovanni":"Rhydon","Ash":"Pikachu",
 "Gary":"Blastoise","Ritchie":"Pikachu","Tracey":"Scyther","Jessie":"Ekans",
 "James":"Weezing",
 "Ethan":"Cyndaquil","Kris":"Totodile","Lyra":"Chikorita","Silver":"Totodile",
 "Falkner":"Hoothoot","Bugsy":"Scyther","Whitney":"Miltank","Morty":"Gengar",
 "Chuck":"Poliwrath","Jasmine":"Steelix","Pryce":"Piloswine","Clair":"Kingdra",
 "Will":"Xatu","Karen":"Umbreon","Janine":"Ariados","Archer":"Houndoom",
 "Ariana":"Arbok",
 "Brendan":"Treecko","May":"Blaziken","Wally":"Gallade","Steven":"Metagross",
 "Wallace":"Milotic","Sidney":"Absol","Phoebe":"Dusclops","Glacia":"Walrein",
 "Drake":"Salamence","Roxanne":"Nosepass","Brawly":"Hariyama","Wattson":"Manectric",
 "Flannery":"Torkoal","Norman":"Slaking","Winona":"Altaria","Tate":"Solrock",
 "Liza":"Lunatone","Juan":"Kingdra","Maxie":"Camerupt","Archie":"Sharpedo",
 "Drew":"Roserade",
 "Lucas":"Turtwig","Dawn":"Piplup","Barry":"Empoleon","Cynthia":"Garchomp",
 "Aaron":"Drapion","Bertha":"Hippowdon","Flint":"Infernape","Lucian":"Bronzong",
 "Roark":"Rampardos","Gardenia":"Roserade","Maylene":"Lucario","Crasher Wake":"Floatzel",
 "Fantina":"Mismagius","Byron":"Bastiodon","Candice":"Froslass","Volkner":"Shinx",
 "Cyrus":"Weavile","Mars":"Purugly","Jupiter":"Skuntank","Saturn":"Toxicroak",
 "Paul":"Electivire","Zoey":"Glameow","Nando":"Roserade",
 "Hilbert":"Oshawott","Hilda":"Tepig","Rosa":"Snivy","Cheren":"Stoutland",
 "Bianca":"Emboar","N":"Zorua","Alder":"Volcarona","Iris":"Haxorus",
 "Cilan":"Pansage","Chili":"Pansear","Cress":"Panpour","Lenora":"Watchog",
 "Burgh":"Leavanny","Elesa":"Zebstrika","Clay":"Excadrill","Skyla":"Swanna",
 "Brycen":"Beartic","Drayden":"Haxorus","Roxie":"Whirlipede","Marlon":"Jellicent",
 "Shauntal":"Chandelure","Marshal":"Conkeldurr","Grimsley":"Bisharp","Caitlin":"Gothitelle",
 "Ghetsis":"Hydreigon","Colress":"Klinklang","Trip":"Serperior",
 "Serena":"Fennekin","Shauna":"Chespin","Diantha":"Gardevoir","Malva":"Talonflame",
 "Siebold":"Clawitzer","Wikstrom":"Aegislash","Drasna":"Noivern","Viola":"Vivillon",
 "Grant":"Tyrunt","Korrina":"Lucario","Ramos":"Gogoat","Clemont":"Heliolisk",
 "Valerie":"Sylveon","Olympia":"Meowstic","Wulfric":"Avalugg","Lysandre":"Gyarados",
 "Alain":"Charizard","Sawyer":"Sceptile",
 "Elio":"Popplio","Selene":"Rowlet","Kukui":"Incineroar","Hau":"Raichu",
 "Molayne":"Dugtrio","Kahili":"Toucannon","Acerola":"Palossand","Hala":"Crabominable",
 "Olivia":"Lycanroc","Nanu":"Persian","Hapu":"Mudsdale","Gladion":"Type: Null",
 "Guzma":"Golisopod","Plumeria":"Salazzle","Lusamine":"Bewear","Lillie (anime)":"Vulpix",
 "Kiawe (anime)":"Turtonator","Lana (anime)":"Popplio","Mallow (anime)":"Tsareena",
 "Sophocles":"Togedemaru",
 "Leon":"Charizard","Milo":"Eldegoss","Nessa":"Drednaw","Kabu":"Centiskorch",
 "Bea":"Machamp","Allister":"Gengar","Opal":"Alcremie","Gordie":"Coalossal",
 "Melony":"Lapras","Piers":"Obstagoon","Raihan":"Duraludon","Hop":"Dubwool",
 "Bede":"Hatterene","Marnie":"Morpeko","Rose":"Copperajah","Goh":"Cinderace",
 "Chloe":"Eevee",
 "Geeta":"Glimmora","Nemona":"Pawmot","Rika":"Clodsire","Poppy":"Tinkaton",
 "Hassel":"Baxcalibur","Katy":"Teddiursa","Brassius":"Sudowoodo","Iono":"Bellibolt",
 "Kofu":"Crabominable","Larry":"Staraptor","Ryme":"Toxtricity","Tulip":"Florges",
 "Grusha":"Cetitan","Arven":"Mabosstiff","Penny":"Sylveon",
}

# Signatures used as the EXACT species (not reduced to evolution-family
# base): these characters' partner is famously the mid-stage itself.
SIGNATURES_EXACT = {"Red", "Lt. Surge", "Ash", "Ritchie"}


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
    sig_unresolved = []
    sig_not_on_roster = []

    def resolve(sp_name):
        """Bulbapedia/SIGNATURES display name -> data.js species id, or None."""
        norm = normalize(sp_name)
        fix_name = NAME_FIXES.get(norm)
        if fix_name:
            sid = name_index.get(normalize(fix_name))
            if sid is not None:
                return sid
        return name_index.get(norm)

    for char_name, info in rosters_raw.items():
        resolved_bases = {}  # base_id -> base_name
        for sp_name in info["species"]:
            sid = resolve(sp_name)
            if sid is None:
                unmatched.append(f"{char_name}\t{sp_name}")
                continue
            base_id = species[sid].get("ancestor", sid)
            base_name = species[base_id]["name"]
            resolved_bases[base_id] = base_name
            review_rows.append((char_name, info["category"], sp_name, species[sid]["key"], base_name, "Y"))

        entry = {
            "page": info["page"],
            "category": info["category"],
            "gen": info["gen"],
            "species": [{"id": bid, "name": bname}
                        for bid, bname in sorted(resolved_bases.items(), key=lambda kv: kv[1])],
        }

        ace = SIGNATURES.get(char_name)
        if ace:
            sid = resolve(ace)
            if sid is None:
                sig_unresolved.append(f"{char_name}\t{ace}")
            else:
                base_id = species[sid].get("ancestor", sid)
                sig_id = sid if char_name in SIGNATURES_EXACT else base_id
                if base_id in resolved_bases:
                    entry["signature"] = {"id": sig_id, "name": species[sig_id]["name"]}
                else:
                    sig_not_on_roster.append(f"{char_name}\t{ace}\t{species[base_id]['name']}")

        mapped[char_name] = entry

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

    sig_count = sum(1 for v in mapped.values() if "signature" in v)

    print(f"Characters: {len(mapped)}")
    print(f"Species references: {total_species_refs} total, {resolved_refs} resolved, {len(unmatched)} unmatched")
    print(f"Empty rosters after mapping: {len(empty_rosters)} {empty_rosters[:10]}")
    print(f"Signatures: {sig_count}/{len(SIGNATURES)} resolved and confirmed on-roster")
    if sig_unresolved:
        print(f"  SIGNATURE UNRESOLVED (name didn't match any species): {sig_unresolved}")
    if sig_not_on_roster:
        print(f"  SIGNATURE NOT ON ROSTER (base form not in character's own roster): {sig_not_on_roster}")
    print("Wrote rosters_mapped.json, roster_review.csv, unmatched_names.txt")


if __name__ == "__main__":
    main()
