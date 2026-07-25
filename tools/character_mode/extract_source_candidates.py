#!/usr/bin/env python3
"""Attribute every rostered species to the Bulbapedia section it was scraped
from, and classify how much that section is worth as evidence of OWNERSHIP.

`scrape_rosters.py` unions species out of every roster-ish section and throws
the provenance away. Its SECTION_HINTS include the bare word "pokemon", which
matches narrative headings like "Pokemon the Series: Ruby and Sapphire" and
"Pokemon Journeys: The Series" -- episode-summary prose that name-drops every
Pokemon in sight, including other trainers'. That is exactly how Tracey (who
tends Professor Oak's lab) picked up Infernape and Gyarados, and how Sabrina
picked up Mewtwo.

This replays the same walk offline (cache only, no network) and records, per
species: which page + section mentioned it, and the KIND of each section:

  ownership  an owned-Pokemon table ("On hand", "Given away", "Released",
             "Status unknown", "In rotation", "Traded away")  -- strong
  game_team  a per-game team section on a game page ("Red, Blue and Yellow")
             -- strong, and names the game
  not_owned  explicitly someone else's ("At Professor Oak's Laboratory",
             "Borrowed", "Rental")                            -- disqualifying
  narrative  episode/era prose ("Pokemon the Series", "History") -- WEAK, a
             mention is not ownership

A species attested ONLY by `narrative` sections is a prime removal candidate.
Nothing here is an assertion: it is the evidence a reviewer (or an adversarial
agent) starts from, and every entry keeps its section list so the call can be
re-checked.

Output: roster_source_candidates.json
"""
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")

NOT_OWNED_HINTS = ("at professor", "laboratory", "borrowed", "rental",
                   "battled", "used by")
OWNERSHIP_HINTS = ("on hand", "in rotation", "released", "traded", "given away",
                   "at home", "status unknown", "temporary", "befriended",
                   "in training", "ride")
NARRATIVE_HINTS = ("the series", "history", "journeys", "chronicles",
                   "pre-series", "original series", "movie", "puzzle league",
                   "character", "biography", "personality")

# Heading (lowercased substring) -> game/medium label. Checked only for
# game_team sections and for narrative sections' era labels.
GAME_LABELS = [
    ("red, blue", "Red/Blue"), ("red and blue", "Red/Blue"), ("yellow", "Yellow"),
    ("gold, silver", "Gold/Silver"), ("gold and silver", "Gold/Silver"),
    ("crystal", "Crystal"),
    ("firered", "FireRed/LeafGreen"), ("leafgreen", "FireRed/LeafGreen"),
    ("ruby, sapphire", "Ruby/Sapphire"), ("ruby and sapphire", "Ruby/Sapphire"),
    ("emerald", "Emerald"),
    ("diamond, pearl", "Diamond/Pearl"), ("diamond and pearl", "Diamond/Pearl"),
    ("platinum", "Platinum"),
    ("heartgold", "HeartGold/SoulSilver"), ("soulsilver", "HeartGold/SoulSilver"),
    ("black 2", "Black 2/White 2"), ("white 2", "Black 2/White 2"),
    ("black and white", "Black/White"), ("black & white", "Black/White"),
    ("x and y", "X/Y"),
    ("omega ruby", "Omega Ruby/Alpha Sapphire"),
    ("alpha sapphire", "Omega Ruby/Alpha Sapphire"),
    ("ultra sun", "Ultra Sun/Ultra Moon"), ("ultra moon", "Ultra Sun/Ultra Moon"),
    ("sun and moon", "Sun/Moon"), ("sun & moon", "Sun/Moon"),
    ("let's go", "Let's Go"),
    ("sword and shield", "Sword/Shield"), ("sword & shield", "Sword/Shield"),
    ("brilliant diamond", "BDSP"), ("shining pearl", "BDSP"),
    ("legends: arceus", "Legends: Arceus"),
    ("scarlet and violet", "Scarlet/Violet"), ("scarlet & violet", "Scarlet/Violet"),
    ("masters", "Masters EX"), ("stadium", "Pokémon Stadium"),
    ("battle subway", "Battle Subway (partner)"), ("world tournament", "PWT"),
    ("battle tree", "Battle Tree (partner)"), ("battle frontier", "Battle Frontier"),
    ("colosseum", "Colosseum"), ("conquest", "Conquest"),
]

ANIME_ERAS = [
    ("chronicles", "Chronicles"), ("origins", "Origins"),
    ("generations", "Generations"), ("evolutions", "Evolutions"),
    ("journeys", "Journeys"), ("horizons", "Horizons"),
    ("orange islands", "Orange Islands"), ("indigo league", "Indigo League"),
    ("ruby and sapphire", "Ruby & Sapphire era"),
    ("diamond and pearl", "Diamond & Pearl era"),
    ("black & white", "Black & White era"), ("black and white", "Black & White era"),
    ("xy", "XY era"), ("sun & moon", "Sun & Moon era"), ("sun and moon", "Sun & Moon era"),
    ("original series", "original series"), ("puzzle league", "Puzzle League"),
    ("movie", "movie"),
]


def clean(heading):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", heading).replace("&amp;", "&")).strip()


def cache_path(key):
    return os.path.join(CACHE, re.sub(r"[^\w.-]", "_", key) + ".json")


def load_scraper():
    spec = importlib.util.spec_from_file_location(
        "scrape_rosters", os.path.join(HERE, "scrape_rosters.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classify(heading, is_anime_page):
    """(kind, label) for one section heading."""
    low = clean(heading).lower()
    if any(h in low for h in NOT_OWNED_HINTS):
        return "not_owned", clean(heading)
    if any(h in low for h in OWNERSHIP_HINTS):
        return "ownership", "Anime" if is_anime_page else "game (unspecified)"
    if any(h in low for h in NARRATIVE_HINTS):
        if is_anime_page:
            era = next((lbl for k, lbl in ANIME_ERAS if k in low), None)
            return "narrative", "Anime — %s" % era if era else "Anime"
        game = next((lbl for k, lbl in GAME_LABELS if k in low), None)
        return "narrative", game or "game (unspecified)"
    game = next((lbl for k, lbl in GAME_LABELS if k in low), None)
    if game:
        return "game_team", game
    return "ownership" if not is_anime_page else "narrative", \
        "Anime" if is_anime_page else "game (unspecified)"


# strongest evidence first. `manga` outranks nothing: manga ownership is out of
# scope by an earlier decision, so it is evidence only in the negative sense.
KIND_RANK = {"game_team": 0, "ownership": 1, "narrative": 2, "manga": 3,
             "not_owned": 4}

MANGA_HINTS = ("manga", "adventures", "pocket monsters", "the electric tale",
               "how i became a pokémon card", "zensho", "battle frontier",
               "pokémon rgb", "pokémon rs", "pokémon dp", "pokémon bw")


def ancestor_headings(sections):
    """section index -> [headings of its ancestors, outermost first].

    The API's "number" field is the ToC path ("5.2.1"), so a section's
    ancestors are the entries whose number is a prefix of it. This is what
    distinguishes an owned-Pokemon table under "In the manga" from the
    identically-titled one under "In the games" -- both are just called
    "Pokemon", which is exactly how Pokemon Adventures teams were scored as
    top-tier ownership evidence in the first pass of this audit.
    """
    by_number = {s.get("number"): clean(s["line"]) for s in sections if s.get("number")}
    out = {}
    for s in sections:
        num = s.get("number") or ""
        parts = num.split(".")
        out[s["index"]] = [by_number[".".join(parts[:i])]
                           for i in range(1, len(parts))
                           if ".".join(parts[:i]) in by_number]
    return out


def is_manga_context(heading, ancestors):
    blob = " ".join([heading] + list(ancestors)).lower()
    return any(h in blob for h in ("manga", "adventures", "pocket monsters",
                                   "electric tale", "zensho"))


def main():
    sr = load_scraper()
    valid = sr.load_valid_names()

    chars = []
    with open(os.path.join(HERE, "characters.txt")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            chars.append((parts[0], [p.strip() for p in parts[1].split("+")]))
    seed_text = open(os.path.join(HERE, "characters.txt")).read()

    out, no_cache = {}, []
    for disp, pages in chars:
        base = disp.split(" (")[0]
        auto = base + " (anime)"
        if auto not in pages:
            pages = pages + [auto]
        found, saw = {}, False
        for page in pages:
            is_auto = (page == auto and auto not in seed_text)
            sections = sr.get_sections(page) if os.path.isfile(cache_path("sections_" + page)) else None
            if sections is None and " (" in page and not is_auto:
                # the scraper's own fallback: "Lorelei (game)" does not exist,
                # the real page is "Lorelei"
                plain = page.split(" (")[0]
                if os.path.isfile(cache_path("sections_" + plain)):
                    sections = sr.get_sections(plain)
                    if sections is not None:
                        page = plain
            if not sections:
                continue
            saw = True
            is_anime_page = page.endswith("(anime)") or "anime" in page.lower()
            ancestors = ancestor_headings(sections)
            for sec in sections:
                heading = sec["line"]
                if not any(h in clean(heading).lower() for h in sr.SECTION_HINTS):
                    continue
                if not os.path.isfile(cache_path("wt_%s_%s" % (page, sec["index"]))):
                    continue
                anc = ancestors.get(sec["index"], [])
                if is_manga_context(clean(heading), anc):
                    kind, label = "manga", "manga (out of scope)"
                else:
                    kind, label = classify(heading, is_anime_page)
                    # an ownership table under "In the anime" is anime ownership
                    # even when the heading itself says nothing
                    anc_blob = " ".join(anc).lower()
                    if kind == "ownership" and label == "game (unspecified)" and "anime" in anc_blob:
                        label = "Anime"
                for species in sr.extract_species(sr.get_section_wikitext(page, sec["index"]), valid):
                    rec = found.setdefault(species, {"evidence": []})
                    rec["evidence"].append({"page": page, "section": clean(heading),
                                            "under": " > ".join(anc) or None,
                                            "kind": kind, "label": label})
        if not saw:
            no_cache.append(disp)
            continue
        for rec in found.values():
            rec["evidence"].sort(key=lambda e: KIND_RANK[e["kind"]])
            best = rec["evidence"][0]
            rec["best_kind"] = best["kind"]
            rec["candidate_source"] = best["label"]
            rec["ownership_evidence"] = any(e["kind"] in ("ownership", "game_team")
                                            for e in rec["evidence"])
            rec["manga_only"] = all(e["kind"] == "manga" for e in rec["evidence"])
        out[disp] = dict(sorted(found.items()))

    path = os.path.join(HERE, "roster_source_candidates.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    total = sum(len(v) for v in out.values())
    weak = sum(1 for c in out.values() for r in c.values() if not r["ownership_evidence"])
    print("wrote %s" % path)
    print("  %d characters, %d attributions" % (len(out), total))
    print("  %d (%.0f%%) rest on NARRATIVE/NOT-OWNED sections only — prime removal candidates"
          % (weak, 100.0 * weak / max(total, 1)))
    if no_cache:
        print("  %d characters have no cached pages (agents must research these "
              "from scratch): %s" % (len(no_cache), ", ".join(no_cache)))


if __name__ == "__main__":
    main()
