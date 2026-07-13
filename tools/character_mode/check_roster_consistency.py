#!/usr/bin/env python3
"""Sanity-check rosters_mapped.json against rr_pokedex_donor/data.js.

Catches the class of bug found and fixed in map_species.py's
build_name_index (a roster entry that should have reduced further to its
true evolution-family base, but didn't). Run after every map_species.py
re-run before trusting the output for emission.

Usage: check_roster_consistency.py
Exit code 0 if clean, 1 if any check fails.
"""
import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main():
    with open(HERE / "rr_pokedex_donor/data.js") as f:
        species = ast.literal_eval(f.read())["species"]
    with open(HERE / "rosters_mapped.json") as f:
        mapped = json.load(f)

    problems = []
    empty = []
    for char, info in mapped.items():
        if not info["species"]:
            empty.append(char)
        roster_ids = {sp["id"] for sp in info["species"]}
        for sp in info["species"]:
            sp_name, stored_id = sp["name"], sp["id"]
            if stored_id not in species:
                problems.append(f"{char}: {sp_name!r} stored id {stored_id} not present in data.js at all")
                continue
            if species[stored_id]["name"] != sp_name:
                problems.append(
                    f"{char}: stored name {sp_name!r} doesn't match data.js name "
                    f"{species[stored_id]['name']!r} for id {stored_id}"
                )
            # NOTE: do NOT re-derive "the" id for sp_name via canonical_id_by_name and
            # compare -- Radical Red's dex data has genuine same-named regional pairs
            # (e.g. id 83 "Farfetch'd" (Kanto, no evolution) vs id 1213 "Farfetch'd"
            # (Galar, key="Farfetch'd-Galar", evolves into Sirfetch'd) -- both are
            # independently valid evolution-family roots. A name-uniqueness check
            # would false-positive on every such pair; the real invariant is just
            # "is this id its own root", checked below.
            true_root = species[stored_id].get("ancestor")
            if true_root != stored_id:
                root_name = species.get(true_root, {}).get("name", "?")
                problems.append(
                    f"{char}: {sp_name!r} (id {stored_id}) is NOT a true evolution-family root "
                    f"-- should have reduced further to {root_name!r} (id {true_root})"
                )
        sig = info.get("signature")
        if sig and sig["id"] not in roster_ids:
            sig_root = species.get(sig["id"], {}).get("ancestor")
            if sig_root not in roster_ids:
                problems.append(
                    f"{char}: signature {sig['name']!r} (id {sig['id']}) is not present in the "
                    f"character's own roster"
                )

    if empty:
        problems.append(f"{len(empty)} characters have empty rosters: {empty}")

    if problems:
        print(f"FAILED: {len(problems)} issue(s) found")
        for p in problems[:50]:
            print(" -", p)
        sys.exit(1)

    total_refs = sum(len(v["species"]) for v in mapped.values())
    print(f"OK: {len(mapped)} characters, {total_refs} roster entries, all are true evolution-family roots, no empty rosters")


if __name__ == "__main__":
    main()
