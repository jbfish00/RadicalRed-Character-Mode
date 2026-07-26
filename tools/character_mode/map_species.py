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
    # data.js's names match Bulbapedia closely, so this stayed empty for a long
    # time. What refilled it runs the OTHER way: the 2026-07-25 roster audit's
    # data was produced against ROWE, a pokeemerald-expansion fork whose species
    # names are capped at 10 characters, and ROWE's own NAME_FIXES had already
    # rewritten "Iron Valiant" to the in-game "IrnValiant" before the audit saw
    # it. Those truncations arrived here inside roster_additions.json. This is
    # the inverse of ROWE's map -- truncated in-game name back to the full
    # Bulbapedia name that data.js actually uses. Radical Red has no 10-char
    # cap, so nothing here is a Radical Red spelling.
    "irnvaliant": "Iron Valiant",
    "ironjuglis": "Iron Jugulis",
    "stonjourne": "Stonjourner",
    "blacefalon": "Blacephalon",
    "fluttrmane": "Flutter Mane",
    "brutebonet": "Brute Bonnet",
    "gougngfire": "Gouging Fire",
    "roarngmoon": "Roaring Moon",
    "sandyshock": "Sandy Shocks",
    "slithrwing": "Slither Wing",
    "walkngwake": "Walking Wake",
}

# Known signature/ace Pokemon per character (any stage; reduced to the
# family's evolution-family base below, same as roster species). Copied
# verbatim from ROWE's map_species.py (the reference implementation) --
# ROWE's full 184-character seed list is this project's own, so every key
# here matches a real character; the 5 characters absent (Calem, Gloria,
# Hugh, Nate, Victor -- all late-gen protagonists) get no signature and
# fall back to a random starter, matching ROWE's own documented behavior.
SIGNATURES = {
 "Tobias":"Darkrai",
 # Volo shipped (bb66270) with no signature, so his starter fell back to
 # roster[0] -- alphabetically Budew, for the Legends: Arceus final boss. His
 # canon ace is Togekiss (the Togepi line is on his roster).
 "Volo":"Togekiss",
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


def build_key_index(species):
    """data.js `key` -> species id. Unlike `name`, the key disambiguates every
    regional/Mega/Gigantamax variant ("Arcanine-Hisui" vs "Arcanine"), which is
    what regional_fallback() needs to resolve a form by name."""
    return {info["key"]: sid for sid, info in species.items() if info.get("key")}


REGION_SUFFIX = {"Hisuian": "Hisui", "Hisui": "Hisui",
                 "Alolan": "Alola", "Alola": "Alola",
                 "Galarian": "Galar", "Galar": "Galar",
                 "Paldean": "Paldea", "Paldea": "Paldea"}


def regional_fallback(name, name_index, key_index):
    """Resolve "Hisuian Arcanine" -> the Hisuian species id, else plain Arcanine.

    build_name_index() keys on the bare display name and deliberately takes
    min(id), so every regional variant collapses onto its Kanto/base namesake
    and a prefixed name like "Hisuian Arcanine" matches nothing at all. That is
    not cosmetic: it cost Volo his only Fire-type, and Palina — whose whole
    roster is Hisuian forms — mapped to an empty roster.

    The donor's `key` field carries the form ("Arcanine-Hisui"), so try that
    first. If this ROM has no such form, fall back to the plain species: a
    regional variant is still that species, and the project's family rule says a
    family is canon if any member is. Returns None if neither resolves.
    """
    parts = name.split(" ", 1)
    if len(parts) != 2 or parts[0] not in REGION_SUFFIX:
        return None
    suffix, base = REGION_SUFFIX[parts[0]], parts[1]
    sid = key_index.get("%s-%s" % (base, suffix))
    if sid is not None:
        return sid
    return name_index.get(normalize(base))


def make_resolver(name_index, key_index):
    """Bulbapedia/SIGNATURES display name -> data.js species id, or None.

    Module-level so that anything else needing to speak the pipeline's name
    language (unaudited_families.py, derive_drops.py) resolves names EXACTLY as
    the mapping does, instead of reimplementing it and drifting.
    """
    def resolve(sp_name):
        norm = normalize(sp_name)
        fix_name = NAME_FIXES.get(norm)
        if fix_name:
            sid = name_index.get(normalize(fix_name))
            if sid is not None:
                return sid
        sid = name_index.get(norm)
        if sid is None:
            sid = regional_fallback(sp_name, name_index, key_index)
        return sid
    return resolve


def main():
    species = load_dex()
    name_index = build_name_index(species)
    key_index = build_key_index(species)

    with open(ROSTERS_RAW) as f:
        rosters_raw = json.load(f)

    # User-approved roster additions (2026-07-23 Bulbapedia completeness audit;
    # partner pools + edge cases included, manga excluded). Kept as a separate
    # overlay file rather than baked into rosters_raw.json so a future
    # re-scrape can't silently drop them. See roster_additions.json's _comment.
    additions_path = HERE / "roster_additions.json"
    if additions_path.is_file():
        with open(additions_path) as f:
            additions = json.load(f)["additions"]
        added = 0
        for char_name, extra in additions.items():
            if char_name not in rosters_raw:
                print(f"WARNING: roster_additions.json character {char_name!r} "
                      "not in rosters_raw.json — skipped")
                continue
            have = set(rosters_raw[char_name]["species"])
            # Rows are bare species names from the 2026-07-23 pass, or
            # {species, source, owned_form} dicts from the 2026-07-25 audit
            # (which carries each add's provenance alongside it).
            extra_names = {e["species"] if isinstance(e, dict) else e
                           for e in extra}
            new = extra_names - have
            rosters_raw[char_name]["species"] = sorted(have | new)
            added += len(new)
        print(f"roster_additions.json: merged {added} species "
              f"across {len(additions)} characters")

    # Removals from the 2026-07-25 adversarial roster audit. The scraper's
    # section filter matches narrative headings ("Pokemon Journeys: The
    # Series"), so rosters absorbed Pokemon that were merely mentioned in an
    # episode — Professor Oak's lab Pokemon landed on Tracey, Ridley's Golurk
    # on Larry, Red's Clefairy on all three Striaton brothers.
    #
    # An overlay for the same reason as the additions: a re-scrape would
    # reintroduce every one of them, and the file keeps the citation for each.
    #
    # THE FAMILY RULE (user, 2026-07-25): a full evolution family is allowed
    # whenever any single member is canon, forwards and backwards. This pass is
    # only the cheap half — it subtracts the exact NAMES the audit listed, before
    # canonicalization. That is not sufficient by itself; see the family-level
    # sweep further down, which is what actually enforces the rule.
    removals = {}
    removals_path = HERE / "roster_removals.json"
    if removals_path.is_file():
        with open(removals_path) as f:
            removals = json.load(f)["removals"]
        dropped = 0
        for char_name, rows in removals.items():
            if char_name not in rosters_raw:
                print(f"WARNING: roster_removals.json character {char_name!r} "
                      "not in rosters_raw.json — skipped")
                continue
            gone = {r["species"] if isinstance(r, dict) else r for r in rows}
            have = set(rosters_raw[char_name]["species"])
            rosters_raw[char_name]["species"] = sorted(have - gone)
            dropped += len(have & gone)
        print(f"roster_removals.json: dropped {dropped} species "
              f"across {len(removals)} characters")

    mapped = {}
    unmatched = []
    review_rows = []
    sig_unresolved = []
    sig_not_on_roster = []

    resolve = make_resolver(name_index, key_index)

    def family_base(sid):
        return species[sid].get("ancestor", sid)

    # A removal is a verdict on the whole FAMILY, not on the one name the auditor
    # was shown, so the name subtraction above is not enough on its own: the
    # scraper often lists later stages under their own names, and those walk the
    # family straight back in after canonicalization. Leaf's Charmander was
    # removed while "Charizard" stayed in her raw list, and she kept the line.
    # Re-apply the removals here, where an entire family is a single base id.
    #
    # ...but a family a wave explicitly KEPT outranks another wave's removal of a
    # different member, because one canon member makes the family canon (the
    # user's family rule, both directions). Lana's Milotic is another trainer's
    # and her Feebas is her own; unshielded, the Milotic verdict eats the Feebas.
    keeps_path = HERE / "audit_keeps.json"
    audit_keeps = {}
    if keeps_path.is_file():
        with open(keeps_path) as f:
            audit_keeps = json.load(f).get("keeps", {})

    family_removed = {}
    shielded = 0
    for char_name, rows in removals.items():
        kept_bases = set()
        for name in audit_keeps.get(char_name, ()):
            sid = resolve(name)
            if sid is not None:
                kept_bases.add(family_base(sid))
        bases = set()
        for r in rows:
            sid = resolve(r["species"] if isinstance(r, dict) else r)
            if sid is None:
                continue
            base_id = family_base(sid)
            if base_id in kept_bases:
                shielded += 1
                continue
            bases.add(base_id)
        family_removed[char_name] = bases
    swept = 0

    for char_name, info in rosters_raw.items():
        resolved_bases = {}  # base_id -> base_name
        for sp_name in info["species"]:
            sid = resolve(sp_name)
            if sid is None:
                unmatched.append(f"{char_name}\t{sp_name}")
                continue
            base_id = family_base(sid)
            if base_id in family_removed.get(char_name, ()):
                swept += 1
                continue
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

    if swept:
        print(f"roster_removals.json: {swept} more swept at family level")
    if shielded:
        print(f"roster_removals.json: {shielded} held back by an audit keep "
              "on the same family")

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
