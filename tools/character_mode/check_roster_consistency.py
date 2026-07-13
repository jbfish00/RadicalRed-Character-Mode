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
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent


def normalize(name):
    name = name.translate(str.maketrans({"é": "e", "É": "e", "♂": "m", "♀": "f"}))
    return re.sub(r"[^a-z0-9]", "", name.lower())


def main():
    with open(HERE / "rr_pokedex_donor/data.js") as f:
        species = ast.literal_eval(f.read())["species"]
    with open(HERE / "rosters_mapped.json") as f:
        mapped = json.load(f)

    # Re-derive the SAME canonical-id-per-name mapping map_species.py's
    # build_name_index computes (min id among same-named candidates) --
    # checking against "is there SOME self-ancestored entry with this name"
    # is not strong enough: cosmetic/event forms (Pikachu costumes, etc.)
    # are self-ancestored by a data quirk despite not being real roots, so
    # that weaker check silently passes exactly the bug this script exists
    # to catch. This must mirror the actual resolution algorithm, not an
    # approximation of it.
    groups = {}
    for sid, info in species.items():
        groups.setdefault(normalize(info["name"]), []).append(sid)
    canonical_id_by_name = {norm: min(ids) for norm, ids in groups.items()}

    problems = []
    empty = []
    for char, info in mapped.items():
        if not info["species"]:
            empty.append(char)
        for sp_name in info["species"]:
            norm = normalize(sp_name)
            canonical_id = canonical_id_by_name.get(norm)
            if canonical_id is None:
                problems.append(f"{char}: {sp_name!r} does not match any known species by name")
                continue
            true_root = species[canonical_id].get("ancestor")
            if true_root != canonical_id:
                root_name = species.get(true_root, {}).get("name", "?")
                problems.append(
                    f"{char}: {sp_name!r} (id {canonical_id}) is NOT a true evolution-family root "
                    f"-- should have reduced further to {root_name!r} (id {true_root})"
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
