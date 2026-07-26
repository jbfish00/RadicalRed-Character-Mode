#!/usr/bin/env python3
"""Fill this repo's remaining unsourced families from ROWE's hand-made labels.

`fill_sources.py` pinned the 85 families whose provenance could be derived
mechanically; the residue -- 81 families across 10 characters, concentrated in
Goh, Red and the Gen 5/8 protagonists -- needs judgement, and that judgement was
already made by hand in the reference project. ROWE reached 100% source coverage,
and every one of the 81 is labelled there, so porting beats re-deriving: the
labels are specific ("Anime — Pokemon Origins PO04 (Cerulean Cave)", "Games —
Sword and Shield (post-game, Sordward & Shielbert)"), which is not something a
scraper would reconstruct. Same call the Frontier Brains got, for the same reason.

What this deliberately does NOT do:
  - invent a label for anything ROWE does not have (it reports those instead);
  - overwrite a source this repo already carries -- RR's own audit may have made
    a different, per-game call, and a bulk import must never quietly win over it;
  - touch `rosters_raw.json`. Sources are an overlay, merged at doc time, so a
    re-scrape cannot undo them.

Run before emit_roster_docs.py:
    python3 tools/character_mode/needed_sources.py      # refresh the residue list
    python3 tools/character_mode/port_sources_from_rowe.py
    python3 tools/character_mode/emit_roster_docs.py
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROWE = "/home/jbfish00/Documents/Pokemon Rowe Alteration/tools/character_mode/roster_sources.json"
MINE = os.path.join(HERE, "roster_sources.json")
NEEDED = os.path.join(HERE, "sources_needed.json")


def load_sources(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("sources", d), d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(ROWE):
        raise SystemExit("ROWE's roster_sources.json not found at %s -- this "
                         "script is the only thing that reads outside the repo, "
                         "and it is read-only" % ROWE)
    if not os.path.isfile(NEEDED):
        raise SystemExit("sources_needed.json missing -- run needed_sources.py")

    rowe, _ = load_sources(ROWE)
    mine, mine_doc = load_sources(MINE)
    with open(NEEDED, encoding="utf-8") as f:
        needed = json.load(f)

    added, already, unavailable = 0, 0, []
    for char, families in sorted(needed.items()):
        for fam in families:
            if mine.get(char, {}).get(fam, {}).get("source"):
                already += 1
                continue
            src = rowe.get(char, {}).get(fam)
            if not src or not src.get("source"):
                unavailable.append("%s/%s" % (char, fam))
                continue
            entry = mine.setdefault(char, {}).setdefault(fam, {})
            # Keep ROWE's owned_form only where we have none: the owned form is
            # the species the character actually had, and RR's own audit may have
            # recorded a different one for the same family.
            entry.setdefault("owned_form", src.get("owned_form", fam))
            entry["source"] = src["source"]
            entry["source_ported_from"] = "ROWE"
            added += 1

    if not args.dry_run:
        mine_doc["sources"] = mine
        with open(MINE, "w", encoding="utf-8") as f:
            json.dump(mine_doc, f, indent=1, sort_keys=True, ensure_ascii=False)
            f.write("\n")

    print("%d families labelled from ROWE, %d already had a source, %d "
          "unavailable" % (added, already, len(unavailable)))
    if unavailable:
        print("  still need judgement (ROWE has no label either):")
        for k in unavailable[:20]:
            print("    " + k)
    if args.dry_run:
        print("(dry run -- roster_sources.json not rewritten)")


if __name__ == "__main__":
    main()
