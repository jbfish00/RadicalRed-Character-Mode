#!/usr/bin/env python3
"""Survey which Character Mode characters already have overworld art IN THE ROM.

Why this exists
---------------
Every sprite-coverage survey in this workspace (docs/SPRITE_COVERAGE.md in each
repo) was built by cross-referencing ROWE's `sprite_report.txt`, which records
only art ROWE had *staged for injection*. That silently undercounts overworld
sprites, because most of these characters are NPCs in the games themselves — the
target engines already ship their overworld graphics. Prof. Oak is the clearest
case: `OBJ_EVENT_GFX_PROF_OAK` in pokeemerald-expansion, `EVENT_OBJ_GFX_OAK` in
CFRU. Using him costs a graphics-id reference, not an injection.

This script matches each repo's live `characters.txt` against the three target
engines' own overworld-graphics constant tables and prints, per repo, which
characters need no overworld art sourced at all.

Engines -> repos:
    firered  (Skeli789/Complete-Fire-Red-Upgrade)   Radical Red, Unbound
    emerald  (rh-hideout/pokeemerald-expansion)     Seaglass, Lazarus
    crystal  (pret/pokecrystal)                     Prism

Run from anywhere; paths are derived from this file's location.

    python3 tools/survey_engine_ow.py            # summary per repo
    python3 tools/survey_engine_ow.py --json     # machine-readable
"""
import argparse
import json
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[2]        # .../Character Hacks

GAMES = [
    ("rr",       "Radical Red", "RadicalRed-Character-Mode", "firered"),
    ("seaglass", "Seaglass",    "Seaglass-Character-Mode",   "emerald"),
    ("lazarus",  "Lazarus",     "Lazarus-Character-Mode",    "emerald"),
    ("unbound",  "Unbound",     "Unbound-Character-Mode",    "firered"),
    ("prism",    "Prism",       "Prism-Character-Mode",      "crystal"),
]

ENGINE_TABLES = {
    "emerald": ("Seaglass-Character-Mode/tools/pokeemerald_expansion_donor/"
                "include/constants/event_objects.h", r"OBJ_EVENT_GFX_"),
    "firered": ("RadicalRed-Character-Mode/tools/cfru_donor/"
                "include/constants/event_objects.h", r"EVENT_OBJ_GFX_"),
    "crystal": ("Prism-Character-Mode/tools/pokecrystal_donor/"
                "constants/sprite_constants.asm", r"SPRITE_"),
}

# Character display name -> constant stems that unambiguously denote them.
# Anything not listed falls back to the uppercased/underscored display name.
ALIAS = {
    "Red": ["RED_NORMAL", "RED"],
    "Leaf": ["LEAF_NORMAL", "LEAF", "GREEN_NORMAL"],
    "Blue": ["BLUE", "RIVAL"],
    "Gary": ["BLUE", "RIVAL"],           # Gary is Blue; FRLG calls the slot RIVAL
    "Ethan": ["ETHAN_PLAYER", "ETHAN", "CHRIS"],   # pokecrystal names him CHRIS
    "Kris": ["KRIS"],
    "Lyra": ["LYRA_PLAYER", "LYRA"],
    "Silver": ["SILVER", "OLIVINE_RIVAL"],
    "Brendan": ["BRENDAN", "RUBY"],
    "May": ["MAY", "SAPPHIRE"],
    "Lucas": ["LUCAS_PLAYER", "LUCAS"],
    "Dawn": ["DAWN_PLAYER", "DAWN"],
    "Lt. Surge": ["LT_SURGE", "SURGE"],
    "Crasher Wake": ["CRASHER_WAKE"],
    "Oak": ["PROF_OAK", "OAK"],
    "Elm": ["ELM"],
    "Birch": ["PROF_BIRCH"],
    "Samson Oak": [],                    # distinct from Prof. Oak; no engine sprite
}

# Constants that exist but belong to a same-named engine-custom NPC.
# CFRU is Unbound's engine, so its MARLON is Unbound's own protagonist
# (see MARLON_PLAYER / YOUNG_MARLON / MARLON_ARM), not the Gen 5 gym leader;
# CFRU predates Gen 9 entirely, so its PENNY cannot be the Paldea character.
AMBIGUOUS = {
    ("firered", "Marlon"): "CFRU MARLON is Unbound's own protagonist",
    ("firered", "Penny"):  "CFRU predates Gen 9; this is an Unbound NPC",
    ("firered", "Melony"): "unverified; likely an Unbound NPC",
}


def load_constants(engine):
    rel, prefix = ENGINE_TABLES[engine]
    path = WS / rel
    if not path.exists():
        print(f"warning: {engine} donor missing at {path}", file=sys.stderr)
        return set()
    return set(re.findall(prefix + r"([A-Z0-9_]+)", path.read_text(errors="replace")))


def load_characters(repo):
    """Parse a repo's characters.txt -> [(name, category, generation)].

    Prism's file carries a 5th `source` field; everything else has 4.
    """
    path = WS / repo / "tools/character_mode/characters.txt"
    out = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = [p.strip() for p in s.split("|")]
        if len(parts) < 4:
            continue
        name, _pages, category, generation = parts[:4]
        out.append((name, category, int(generation)))
    return out


def stems(name):
    if name in ALIAS:
        return ALIAS[name]
    return [re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    args = ap.parse_args()

    tables = {eng: load_constants(eng) for eng in ENGINE_TABLES}
    report = {}

    for key, label, repo, engine in GAMES:
        table = tables[engine]
        chars = load_characters(repo)
        native, missing = [], []
        for name, category, generation in chars:
            if (engine, name) in AMBIGUOUS:
                missing.append(name)
                continue
            hit = next((s for s in stems(name) if s in table), None)
            (native if hit else missing).append(name if not hit else (name, hit))
        report[key] = {
            "label": label, "engine": engine, "total": len(chars),
            "native": [n for n, _ in native],
            "native_constants": {n: c for n, c in native},
            "not_native": missing,
        }

    if args.json:
        print(json.dumps(report, indent=1))
        return

    for key, label, repo, engine in GAMES:
        r = report[key]
        print(f"\n{label}  ({engine} engine)  —  {len(r['native'])} of {r['total']} "
              f"characters already have overworld art in the ROM")
        for name in r["native"]:
            print(f"    {name:<16s} {r['native_constants'][name]}")
    print("\nAmbiguous name collisions deliberately NOT counted:")
    for (engine, name), why in AMBIGUOUS.items():
        print(f"    {engine}/{name}: {why}")


if __name__ == "__main__":
    main()
