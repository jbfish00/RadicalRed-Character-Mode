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

from map_species import build_key_index, build_name_index, make_resolver

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
    # the Legends: Arceus cast, added by the 2026-07-25 roster audit. Without
    # these the fallback .title() renders "Galaxy" and "Other", which say
    # nothing about what the character actually is.
    "warden": "Warden", "galaxy": "Galaxy Team", "other": "Other",
}

SPRITE_URL = ("https://cdn.jsdelivr.net/gh/PokeAPI/sprites@master"
              "/sprites/pokemon/%d.png")
SPRITES_PER_ROW = 8


def load_species():
    with open(os.path.join(HERE, "rr_pokedex_donor/data.js")) as f:
        return ast.literal_eval(f.read())["species"]


def rekey_sources_onto_family_base(sources, species, resolve):
    """{character: {family-base name: {owned species name: info}}}.

    THE trap this generator has to survive: the audit recorded the species each
    character actually OWNED ("Charizard", "Greninja"), but a roster stores the
    evolution-family BASE ("Charmander", "Froakie"), and the doc rows are keyed
    by base. Looked up as-recorded, only 37% of this repo's source keys match
    anything and the Source column reads "—" on the other 63%.

    Keeping the owned name inside the inner dict (rather than collapsing to one
    entry per family) is what lets a row say "as Charizard — Anime": a family can
    carry several owned forms, and the row wants the one matching its own final.
    """
    out = {}
    for char, rows in sources.items():
        if char.startswith("_"):
            continue                      # _meta
        per_base = {}
        for owned, info in rows.items():
            sid = resolve(owned)
            if sid is None:
                continue
            base = species[species[sid].get("ancestor") or sid]["name"]
            per_base.setdefault(display(base), {})[display(owned)] = info
        out[char] = per_base
    return out


def pick_source(per_base, base_name, shown_name):
    """The best-matching source entry for one doc row, deterministically.

    Prefer an entry recording the exact species the row shows, then one naming
    the family base, then the alphabetically first -- a family with several owned
    forms must not pick a different one on each run.

    An entry whose `source` is null NEVER wins over a sibling that has one. The
    audit records one entry per owned form, and for the Frontier Brains the final
    form's entry exists with a null source while the family base carries the real
    label (Anabel's Alakazam is null, her Abra says "Emerald"). Taking the first
    match regardless left 23 rows blank while the provenance sat one key away --
    the same shape as the bug where `roster_additions.json` already held a source
    per row and nothing read it.

    The map is keyed by species name with the entry inline, but some rows nest a
    second level (owned form -> entry), so candidates are collected from both
    shapes rather than assuming one.
    """
    candidates = []
    for key in (base_name, shown_name):
        node = per_base.get(key)
        if not isinstance(node, dict):
            continue
        if "source" in node or "owned_form" in node:
            candidates.append(node)          # entry inline
        else:
            for k in (shown_name, base_name):
                if isinstance(node.get(k), dict):
                    candidates.append(node[k])
            candidates += [node[k] for k in sorted(node)
                           if isinstance(node[k], dict)]
    if not candidates:
        return {}
    for entry in candidates:
        if entry.get("source"):
            return entry
    return candidates[0]


def load_sources():
    """{character: {owned species: {"source", "owned_form"}}} -- every provenance
    label this repo holds, from both files that carry one.

    `roster_sources.json` is the audit's own attribution pass. But
    `roster_additions.json` ALSO records a source and owned_form per added
    species, and nothing used to read them, so a family that entered a roster
    through the additions overlay showed a blank Source even though its
    provenance was sitting right there -- that is why only Hilda, of the four
    Battle Subway Multi Train partners, had labels for the shared pool.

    roster_sources.json wins on conflict: it is the audit's considered answer,
    whereas an addition's label is whatever the pass that proposed it wrote down.
    Absent files = no Source column content, so the docs still generate without an
    audit at all.
    """
    merged = {}
    add_path = os.path.join(HERE, "roster_additions.json")
    if os.path.isfile(add_path):
        with open(add_path, encoding="utf-8") as f:
            for char, rows in json.load(f).get("additions", {}).items():
                for row in rows:
                    if not isinstance(row, dict) or not row.get("source"):
                        continue
                    merged.setdefault(char, {})[row["species"]] = {
                        "source": row["source"],
                        "owned_form": row.get("owned_form") or row["species"],
                    }
    path = os.path.join(HERE, "roster_sources.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for char, rows in json.load(f).get("sources", {}).items():
                merged.setdefault(char, {}).update(rows)
    return merged


def load_unselectable():
    """Characters below the six-fully-evolved threshold, from
    character_drops.json (GENERATED by derive_drops.py).

    These are now FILTERED OUT of the docs, because the selection gate is
    injected: `flags` bit1 = hidden (emit_characters.py) makes the injector omit
    their check block from the cheat-code alias chain, so the menu genuinely does
    not offer them. The docs describe what the menu offers.

    They keep their table slot and their allow-bitmap -- a save that already
    selected one still works -- so this filter must never be applied to the
    bitmaps, the wild-override tables or anything else the ROM indexes by
    character id. Docs only.

    The authority for hidden-ness at doc time is the MANIFEST's `hidden` flag --
    the same bit the injector gates on, so docs and ROM cannot disagree. This
    list is read only to name the hidden characters in the header.
    """
    path = os.path.join(HERE, "character_drops.json")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("unselectable", [])


REGION_PREFIX = {"Alola": "Alolan", "Galar": "Galarian", "Hisui": "Hisuian",
                 "Paldea": "Paldean"}


def regional_form(info):
    """The region a species' donor `key` marks it as, or None.

    Regional forms are listed as their own rows (user, 2026-07-25) -- Persian,
    Alolan Persian and Perrserker are three different Pokemon to a player, and
    the ROM allows all three. Mega/Gigantamax/cosmetic keys are NOT forms in
    that sense: they are battle transformations and stay folded into the base.
    """
    key = (info.get("key") or "").replace("’", "'")
    for region, prefix in REGION_PREFIX.items():
        if key.endswith("-" + region):
            return prefix
    return None


def display(name):
    """The donor spells Farfetch'd/Sirfetch'd with a typographic apostrophe;
    every other doc in this repo uses the ASCII one."""
    return name.replace("’", "'")


PLACEHOLDER_FORMS = {"normal", "base", "none", "-", ""}


def source_cell(info, shown_name):
    """"as Bulbasaur — Anime (Indigo League)", or just the source when the
    character owned the final stage itself."""
    src = (info or {}).get("source")
    if not src:
        return "—"
    owned = ((info or {}).get("owned_form") or "").strip()
    if owned and owned.lower() not in PLACEHOLDER_FORMS and owned != shown_name:
        return "as %s — %s" % (owned, src)
    return src


def main():
    species = load_species()
    resolve = make_resolver(build_name_index(species), build_key_index(species))
    sources = rekey_sources_onto_family_base(load_sources(), species, resolve)
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
        # Hidden characters are not offered by the menu, so they are not
        # documented. `i` still indexes the FULL table -- the bitmap slice below
        # must never be compacted, or every character after the first hidden one
        # would be documented with someone else's roster.
        if rec.get("hidden"):
            continue
        bits = bitmaps[i * STRIDE:(i + 1) * STRIDE]
        allowed = [s for s in range(NUM_SPECIES)
                   if bits[s >> 3] & (1 << (s & 7)) and s in species]
        finals = {}
        for s in allowed:
            if not is_final(s):
                continue
            # a regional form keeps its own row; everything else folds into the
            # base form it shares a dex number with
            shown = s if regional_form(species[s]) else canonical.get(dex_of(s), s)
            # the roster stores evolution-family bases and the audit is keyed by
            # them, so remember which base this row descends from
            finals.setdefault(shown, species[s].get("ancestor") or s)
        # The species id is the final tiebreak, and it is not decorative: a
        # regional form shares both its national dex number AND its display name
        # with the base form ("Raichu" / "Raichu"), so without it the two rows
        # sort equal and land in dict-iteration order. Every regeneration then
        # produced a spurious ~190-line diff with no data change.
        ordered = sorted(finals, key=lambda s: (dex_of(s), species[s]["name"], s))
        char_sources = sources.get(rec["character"], {})
        rows = []
        for s in ordered:
            base_name = display(species[finals[s]]["name"])
            region = regional_form(species[s])
            shown_name = display(species[s]["name"])
            if region:
                shown_name = "%s %s" % (region, shown_name)
            info = pick_source(char_sources, base_name, shown_name)
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

    # Coverage, stated rather than implied. Both numbers below have been wrong in
    # a shipped doc before: rows carried no provenance at all, and the character
    # count drifted from the ROM's three times.
    all_rows = [r for c in chars for r in c["finals"]]
    sourced = sum(1 for _n, _d, src in all_rows if src and src != "—")
    thin = [n for n in load_unselectable()]
    coverage = [
        "### Coverage", "",
        "- **%d characters**, **%d final-evolution rows**; every row is derived "
        "from the injected allow-bitmaps, so nothing here is promised that the "
        "ROM refuses." % (len(chars), len(all_rows)),
        "- **%d of %d rows (%.0f%%) carry a Source.** A blank Source means the "
        "provenance is not recorded, not that the entry is unverified — the "
        "2026-07-25 adversarial audit judged every roster in this file."
        % (sourced, len(all_rows), 100.0 * sourced / max(1, len(all_rows))),
    ]
    if thin:
        coverage.append(
            "- **%d characters are hidden from the menu** because they have fewer "
            "than six fully-evolved Pokémon in this game's dex and no legendary to "
            "exempt them (%s). They are **not listed below**, because the patch "
            "genuinely does not offer them — their codes are rejected like any "
            "unknown code. They keep their table slot, so an existing save that "
            "already chose one still works normally."
            % (len(thin), ", ".join(sorted(thin))))

    out = ["# Character Mode — Final-Evolution Rosters (%s)" % GAME_TITLE, "",
           "Every playable character and the **final evolutions** their complete "
           "roster resolves to, in **National Pokédex order**. Rosters were "
           "researched from Bulbapedia (union of all games, remakes, rematches, "
           "and anime) and cross-checked where possible. Regional/cosmetic forms "
           "show as their base species. Off-roster Pokémon are routed to your PC.",
           "", "**%d characters.** Sprite version: `ROSTERS_SPRITES.md`." % len(chars),
           "", generated_note, ""] + coverage + ["", "## Contents"]
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
