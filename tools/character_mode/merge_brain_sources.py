#!/usr/bin/env python3
"""Fill in the Battle Frontier Brains' source labels from ROWE's hand-made set.

The Frontier Brains are the one group with no recorded provenance anywhere in the
audit pipeline: their rosters came from a separate research pass that wrote
species names straight into `rosters_raw.json`, so no audit wave and no
`fill_sources.py` run can label them. ROWE's were attributed BY HAND from the
cached Bulbapedia party tables -- the Emerald Silver/Gold Symbol challenges, the
Sinnoh Silver/Gold Print challenges (Dahlia = Battle Arcade, Darach = Battle
Castle, Palmer = Battle Tower), the Battle Tree for Anabel, and the anime Battle
Frontier arc for the rest.

`push_rosters.md` §5 is explicit: copy those labels rather than re-deriving them.
This does that, gap-fill only -- a label this repo's own audit data already
carries always wins, since it has the same provenance and is keyed to this
repo's data.

Idempotent. Run before emit_roster_docs.py; re-running changes nothing.

Usage: merge_brain_sources.py [--dry-run]
"""
import argparse
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
ROWE = Path("/home/jbfish00/Documents/Pokemon Rowe Alteration/tools/character_mode"
            "/roster_sources.json")

# Every Frontier Brain this project carries: Hoenn's seven, Sinnoh's five, plus
# Ingo (a Subway Boss, filed `frontier` here because Legends: Arceus made him a
# warden and the audit's metadata put him with the Brains).
BRAINS = ["Anabel", "Tucker", "Greta", "Spenser", "Noland", "Lucy", "Brandon",
          "Palmer", "Thorton", "Dahlia", "Darach", "Argenta", "Ingo"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    path = HERE / "roster_sources.json"
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    sources = doc["sources"]

    if not ROWE.is_file():
        raise SystemExit("ROWE's roster_sources.json not found at %s -- it is the "
                         "only place these labels exist" % ROWE)
    with open(ROWE, encoding="utf-8") as f:
        donor = json.load(f)["sources"]

    added, kept = 0, 0
    for brain in BRAINS:
        theirs = donor.get(brain)
        if not theirs:
            print("  !! %s absent from ROWE's sources -- nothing to copy" % brain)
            continue
        mine = sources.setdefault(brain, {})
        for sp, info in sorted(theirs.items()):
            if sp in mine and (mine[sp] or {}).get("source"):
                kept += 1
                continue
            mine[sp] = dict(info)
            mine[sp]["derived"] = "rowe-hand-attribution"
            added += 1

    if not args.dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, ensure_ascii=False, sort_keys=True)
            f.write("\n")

    print("Frontier Brains: %d labels copied from ROWE, %d already present"
          % (added, kept))
    for brain in BRAINS:
        n = len(sources.get(brain, {}))
        print("   %-10s %2d labelled species" % (brain, n))
    if args.dry_run:
        print("(dry run -- %s not rewritten)" % os.path.basename(path))


if __name__ == "__main__":
    main()
