#!/usr/bin/env python3
"""Generate ROSTERS.md / ROSTERS_SPRITES.md / sprites/gen_*.md from the data
the ROM actually enforces.

Why this exists: these docs used to be hand-maintained, and in the ROWE
reference project that produced a shipped doc promising 194 family bases the
catch gate refused while omitting ~2500 it already allowed. Generating them
from `rosters_expanded.bin` - the very bitmap the enforcement shim tests -
makes that class of drift impossible here.

Source of truth, in order:
  rosters_expanded.bin      the injected allow-bitmaps (bit N = species id N)
  characters_manifest.json  character order, names, generation, category
  rr_pokedex_donor/data.js  names, national dex ids (dexID), evolution graph

"Final evolutions" = allowed species with no real evolution left. Two
subtleties, both learned the hard way:
  * evolution method 254 is MEGA EVOLUTION, not an evolution. Counting it
    would drop every mega-capable species (Venusaur, Charizard, ...) out of
    the list.
  * alt forms share their base's dexID, so they collapse onto the base name
    for display - but a cosmetic form that cannot itself evolve (the cap
    Pikachus) must not be reported as a "final evolution" of a family whose
    base still evolves.

Run after emit_bitmaps.py:
    python3 tools/character_mode/emit_roster_docs.py
"""
import ast
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.path.join(HERE, "..", ".."))

GAME_TITLE = "Pokémon Radical Red v4.1"
NUM_SPECIES = 1376
STRIDE = (NUM_SPECIES + 7) // 8
EVO_METHOD_MEGA = 254

CATEGORY_LABEL = {
    "protagonist": "Protagonist", "rival": "Rival", "gymleader": "Gym Leader",
    "elite4": "Elite Four", "champion": "Champion", "villain": "Villain",
    "anime": "Anime", "professor": "Professor", "frontier": "Frontier Brain",
}

SPRITE_URL = ("https://cdn.jsdelivr.net/gh/PokeAPI/sprites@master"
              "/sprites/pokemon/%d.png")
SPRITES_PER_ROW = 8


def load_species():
    with open(os.path.join(HERE, "rr_pokedex_donor/data.js")) as f:
        return ast.literal_eval(f.read())["species"]


def load_sources():
    """{character: {family-base species: {"source", "owned_form"}}} from the
    adversarial roster audit. Absent file = no Source column content, so the
    docs still generate before/without an audit."""
    path = os.path.join(HERE, "roster_sources.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("sources", {})


def display(name):
    """The donor spells Farfetch'd/Sirfetch'd with a typographic apostrophe;
    every other doc in this repo uses the ASCII one."""
    return name.replace("’", "'")


def source_cell(info, shown_name):
    """"as Bulbasaur — Anime (Indigo League)", or just the source when the
    character owned the final stage itself."""
    src = (info or {}).get("source")
    if not src:
        return "—"
    owned = (info or {}).get("owned_form")
    if owned and owned != shown_name:
        return "as %s — %s" % (owned, src)
    return src


def main():
    species = load_species()
    sources = load_sources()
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    with open(os.path.join(HERE, "rosters_expanded.bin"), "rb") as f:
        bitmaps = f.read()

    if len(bitmaps) != len(manifest) * STRIDE:
        raise SystemExit("rosters_expanded.bin is %d bytes, expected %d for %d "
                         "characters - re-run emit_bitmaps.py"
                         % (len(bitmaps), len(manifest) * STRIDE, len(manifest)))

    # real (non-mega) evolution targets
    evolves_to = {}
    for sid, info in species.items():
        evolves_to[sid] = [e[2] for e in (info.get("evolutions") or [])
                           if len(e) >= 3 and e[0] != EVO_METHOD_MEGA
                           and e[2] in species]

    def dex_of(sid):
        return species[sid].get("dexID") or sid

    # canonical (base-form) entry for a national dex number
    canonical = {}
    for sid in sorted(species):
        canonical.setdefault(dex_of(sid), sid)

    def is_final(sid):
        if evolves_to.get(sid):
            return False
        # a cosmetic form whose base form still evolves is not a final stage
        base = canonical.get(dex_of(sid), sid)
        return not evolves_to.get(base)

    chars = []
    for i, rec in enumerate(manifest):
        bits = bitmaps[i * STRIDE:(i + 1) * STRIDE]
        allowed = [s for s in range(NUM_SPECIES)
                   if bits[s >> 3] & (1 << (s & 7)) and s in species]
        finals = {}
        for s in allowed:
            if not is_final(s):
                continue
            shown = canonical.get(dex_of(s), s)
            # the roster stores evolution-family bases and the audit is keyed by
            # them, so remember which base this row descends from
            finals.setdefault(shown, species[s].get("ancestor") or s)
        ordered = sorted(finals, key=lambda s: (dex_of(s), species[s]["name"]))
        char_sources = sources.get(rec["character"], {})
        rows = []
        for s in ordered:
            base_name = display(species[finals[s]]["name"])
            shown_name = display(species[s]["name"])
            info = char_sources.get(base_name) or char_sources.get(shown_name) or {}
            rows.append((shown_name, dex_of(s), source_cell(info, shown_name)))
        chars.append({
            "name": rec["character"],
            "gen": rec["generation"],
            "label": CATEGORY_LABEL.get(rec["category"], rec["category"].title()),
            "finals": rows,
        })

    by_gen = defaultdict(list)
    for c in chars:
        by_gen[c["gen"]].append(c)
    for g in by_gen:
        by_gen[g].sort(key=lambda c: c["name"])
    gens = sorted(by_gen)

    generated_note = ("GENERATED by `tools/character_mode/emit_roster_docs.py` "
                      "from `rosters_expanded.bin`, the same allow-bitmaps the "
                      "in-ROM enforcement shim tests — do not hand-edit, "
                      "regenerate.")

    out = ["# Character Mode — Final-Evolution Rosters (%s)" % GAME_TITLE, "",
           "Every playable character and the **final evolutions** their complete "
           "roster resolves to, in **National Pokédex order**. Rosters were "
           "researched from Bulbapedia (union of all games, remakes, rematches, "
           "and anime) and cross-checked where possible. Regional/cosmetic forms "
           "show as their base species. Off-roster Pokémon are routed to your PC.",
           "", "**%d characters.** Sprite version: `ROSTERS_SPRITES.md`." % len(chars),
           "", generated_note, "", "## Contents"]
    for g in gens:
        out.append("- [Generation %d](#generation-%d)" % (g, g))
    out.append("")
    for g in gens:
        out += ["", "## Generation %d" % g, ""]
        for c in by_gen[g]:
            out.append("### %s — %s" % (c["name"], c["label"]))
            out.append("**Final evolutions (%d):**" % len(c["finals"]))
            out.append("")
            out.append("| Pokémon | Source |")
            out.append("|---|---|")
            for name, _dex, src in c["finals"]:
                out.append("| %s | %s |" % (name, src))
            out.append("")
    with open(os.path.join(TARGET, "ROSTERS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")

    idx = ["# Character Mode — Roster Sprites (%s)" % GAME_TITLE, "",
           "Each character's **final-evolution** roster, in **National Pokédex "
           "order**, with sprites and names. Split by generation to keep pages "
           "fast. Regional/cosmetic forms show as base species. Sprites via "
           "[PokéAPI](https://github.com/PokeAPI/sprites). Text: `ROSTERS.md`.",
           "", "**%d characters.**" % len(chars), "", generated_note,
           "", "## Generations", ""]
    for g in gens:
        idx.append("- [Generation %d](sprites/gen_%d.md) — %d characters"
                   % (g, g, len(by_gen[g])))
    with open(os.path.join(TARGET, "ROSTERS_SPRITES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(idx).rstrip() + "\n")

    os.makedirs(os.path.join(TARGET, "sprites"), exist_ok=True)
    for g in gens:
        page = ["# %s — Roster Sprites (Generation %d)" % (GAME_TITLE, g), "",
                "Final-evolution rosters in National Pokédex order, sprites with "
                "names. [← back to index](../ROSTERS_SPRITES.md)", ""]
        for c in by_gen[g]:
            page.append("### %s — %s" % (c["name"], c["label"]))
            page.append("<table>")
            row = []
            for name, num, src in c["finals"]:
                note = ("<br><sub><i>%s</i></sub>" % src) if src and src != "—" else ""
                row.append('<td align="center" width="100"><img width="56" src="%s">'
                           "<br><sub>%s</sub>%s</td>" % (SPRITE_URL % num, name, note))
                if len(row) == SPRITES_PER_ROW:
                    page.append("<tr>" + "".join(row) + "</tr>")
                    row = []
            if row:
                page.append("<tr>" + "".join(row) + "</tr>")
            page += ["</table>", ""]
        with open(os.path.join(TARGET, "sprites/gen_%d.md" % g), "w",
                  encoding="utf-8") as f:
            f.write("\n".join(page).rstrip() + "\n")

    print("wrote ROSTERS.md, ROSTERS_SPRITES.md and %d sprites/gen_*.md: "
          "%d characters, %d final-evolution entries"
          % (len(gens), len(chars), sum(len(c["finals"]) for c in chars)))


if __name__ == "__main__":
    main()
