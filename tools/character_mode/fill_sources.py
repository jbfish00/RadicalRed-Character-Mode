#!/usr/bin/env python3
"""Attribute a source to rostered Pokemon that don't have one yet.

The docs print, under every Pokemon, where that character's appearance comes
from. Most entries carry a source from the roster audit; species that entered a
roster through an earlier research pass do not. This fetches each character's
Bulbapedia page and reads the source off the SECTION the species appears in,
using the section's heading ancestry -- the same technique that tells a game
team from a Pokemon Adventures table, since both are titled "Pokemon".

Results go back into roster_sources.json tagged `derived: section`, so an
attribution made this way stays distinguishable from one a reviewer checked.

Usage:
    python3 tools/character_mode/fill_sources.py [--dry-run]

Reads sources_needed.json ({character: [species, ...]}) for the worklist.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "raw")
API = "https://bulbapedia.bulbagarden.net/w/index.php"
UA = "character-mode-roster-docs/1.0 (personal ROM hack project; low volume)"

GAME_LABELS = [
    ("red, blue", "Red/Blue"), ("red and blue", "Red/Blue"), ("yellow", "Yellow"),
    ("gold, silver", "Gold/Silver"), ("gold and silver", "Gold/Silver"),
    ("crystal", "Crystal"), ("firered", "FireRed/LeafGreen"),
    ("leafgreen", "FireRed/LeafGreen"), ("ruby, sapphire", "Ruby/Sapphire"),
    ("ruby and sapphire", "Ruby/Sapphire"), ("emerald", "Emerald"),
    ("diamond, pearl", "Diamond/Pearl"), ("diamond and pearl", "Diamond/Pearl"),
    ("platinum", "Platinum"), ("heartgold", "HeartGold/SoulSilver"),
    ("soulsilver", "HeartGold/SoulSilver"), ("black 2", "Black 2/White 2"),
    ("white 2", "Black 2/White 2"), ("black and white", "Black/White"),
    ("black & white", "Black/White"), ("x and y", "X/Y"),
    ("omega ruby", "Omega Ruby/Alpha Sapphire"),
    ("alpha sapphire", "Omega Ruby/Alpha Sapphire"),
    ("ultra sun", "Ultra Sun/Ultra Moon"), ("ultra moon", "Ultra Sun/Ultra Moon"),
    ("sun and moon", "Sun/Moon"), ("sun & moon", "Sun/Moon"),
    ("let's go", "Let's Go"), ("sword and shield", "Sword/Shield"),
    ("sword & shield", "Sword/Shield"), ("brilliant diamond", "BDSP"),
    ("legends: arceus", "Legends: Arceus"), ("scarlet and violet", "Scarlet/Violet"),
    ("masters", "Masters EX"), ("stadium", "Pokémon Stadium"),
    ("battle subway", "Battle Subway (partner)"), ("world tournament", "PWT"),
    ("battle tree", "Battle Tree"), ("battle frontier", "Battle Frontier"),
    ("battle tower", "Battle Tower"), ("battle factory", "Battle Factory"),
    ("battle hall", "Battle Hall"), ("battle castle", "Battle Castle"),
    ("battle arcade", "Battle Arcade"), ("battle chateau", "Battle Chateau"),
    ("battle dome", "Battle Dome"), ("battle pike", "Battle Pike"),
    ("battle palace", "Battle Palace"), ("battle pyramid", "Battle Pyramid"),
]
ANIME_ERAS = [
    ("chronicles", "Anime — Pokémon Chronicles"), ("origins", "Anime — Pokémon Origins"),
    ("generations", "Anime — Pokémon Generations"), ("journeys", "Anime — Journeys"),
    ("horizons", "Anime — Horizons"), ("orange islands", "Anime — Orange Islands"),
    ("indigo league", "Anime — Indigo League"),
    ("ruby and sapphire", "Anime — Ruby & Sapphire era"),
    ("diamond and pearl", "Anime — Diamond & Pearl era"),
    ("black & white", "Anime — Black & White era"),
    ("black and white", "Anime — Black & White era"), ("xy", "Anime — XY era"),
    ("sun & moon", "Anime — Sun & Moon era"), ("sun and moon", "Anime — Sun & Moon era"),
    ("johto", "Anime — Johto"), ("original series", "Anime — original series"),
]
MANGA_HINT = ("manga", "adventures", "pocket monsters", "electric tale", "zensho")


def fetch(page):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, re.sub(r"[^\w.-]", "_", page) + ".wiki")
    if os.path.isfile(path):
        return open(path, encoding="utf-8").read()
    url = "%s?%s" % (API, urllib.parse.urlencode({"title": page, "action": "raw"}))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", "replace")
    except Exception:
        text = ""
    open(path, "w", encoding="utf-8").write(text)
    time.sleep(1.0)                       # be polite to Bulbapedia
    return text


def label_for(headings, is_anime_page):
    """Source label from a section's heading and its ancestors."""
    blob = " ".join(headings).lower()
    if any(h in blob for h in MANGA_HINT):
        for key, lbl in (("adventures", "Manga — Pokémon Adventures"),
                         ("pocket monsters", "Manga — Pocket Monsters"),
                         ("electric tale", "Manga — Electric Tale of Pikachu"),
                         ("zensho", "Manga — Pokémon Zensho")):
            if key in blob:
                return lbl
        return "Manga"
    if "movie" in blob:
        return "Movie"
    for key, lbl in ANIME_ERAS:
        if key in blob:
            return lbl
    for key, lbl in GAME_LABELS:
        if key in blob:
            return lbl
    if "anim" in blob or is_anime_page:
        return "Anime"
    return None


def sections_of(text):
    """[(heading path, body)] for every section of a raw wiki page."""
    out, stack, buf, path = [], [], [], []
    for line in text.splitlines():
        m = re.match(r"^(={2,6})\s*(.*?)\s*\1\s*$", line)
        if m:
            if path:
                out.append((list(path), "\n".join(buf)))
            level = len(m.group(1))
            title = re.sub(r"[\[\]']", "", re.sub(r"<[^>]*>", "", m.group(2))).strip()
            stack = [(lv, t) for lv, t in stack if lv < level] + [(level, title)]
            path = [t for _, t in stack]
            buf = []
        else:
            buf.append(line)
    if path:
        out.append((list(path), "\n".join(buf)))
    return out


def family_names():
    """base species display name -> every display name in that family.

    The worklist holds evolution-family BASES (Abra), but a page names the form
    the character actually used (Alakazam). Searching only for the base misses
    almost every fully-evolved team member.

    Radical Red port: expands through `emit_bitmaps.expand_roster`, the same walk
    that builds the injected allow-bitmaps (forward evolutions plus same-name
    lateral forms), so the names searched for are exactly the ones the ROM lets
    that family reach.
    """
    import emit_bitmaps
    from emit_roster_docs import display as ascii_name

    species = emit_bitmaps.load_species()
    evolves_to, ids_by_name = emit_bitmaps.build_indexes(species)

    out = {}
    for sid, info in species.items():
        name = ascii_name(info["name"])
        if name in out:
            continue                      # lowest id wins, as build_name_index does
        fam = emit_bitmaps.expand_roster([sid], species, evolves_to, ids_by_name)
        out[name] = {ascii_name(species[m]["name"]) for m in fam}
    return out


def main():
    dry = "--dry-run" in sys.argv
    families = family_names()
    src_path = os.path.join(HERE, "roster_sources.json")
    with open(src_path, encoding="utf-8") as f:
        blob = json.load(f)
    sources = blob["sources"]

    pages = {}
    for line in open(os.path.join(HERE, "characters.txt"), encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#"):
            parts = [p.strip() for p in line.split("|")]
            pages[parts[0]] = [p.strip() for p in parts[1].split("+")]

    need = json.load(open(os.path.join(HERE, "sources_needed.json"), encoding="utf-8"))
    filled = unresolved = 0
    misses = []
    for char, species in sorted(need.items()):
        cand = list(pages.get(char, [char]))
        base = char.split(" (")[0]
        # Characters with very large teams have their Pokemon split onto a
        # dedicated list page (Goh, Ash, the Alola captains); without it their
        # rows stay unattributed no matter how many sections we read.
        for extra in (base, base + " (anime)", base + " (game)",
                      "List of %s's Pok\u00e9mon" % base,
                      "%s's Pok\u00e9mon" % base):
            if extra not in cand:
                cand.append(extra)
        found = {}
        for page in cand:
            text = fetch(page)
            if not text or len(text) < 400:
                continue
            is_anime = "(anime)" in page.lower()
            for path, body in sections_of(text):
                lbl = label_for(path, is_anime)
                if not lbl:
                    continue
                for sp in species:
                    if sp in found:
                        continue
                    for member in families.get(sp, {sp}) | {sp}:
                        if re.search(r"\|\s*%s\s*[|}]" % re.escape(member), body) \
                                or re.search(r"\{\{[Pp]\|%s[|}]" % re.escape(member), body):
                            found[sp] = lbl
                            break
        for sp in species:
            if sp in found:
                sources.setdefault(char, {})[sp] = {
                    "source": found[sp], "owned_form": sp, "derived": "section"}
                filled += 1
            else:
                unresolved += 1
                if len(misses) < 20:
                    misses.append("%s/%s" % (char, sp))

    print("filled %d, could not pin %d" % (filled, unresolved))
    if misses:
        print("unpinned sample: %s" % ", ".join(misses))
    if not dry:
        with open(src_path, "w", encoding="utf-8") as f:
            json.dump(blob, f, indent=1, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        print("updated", src_path)


if __name__ == "__main__":
    main()
