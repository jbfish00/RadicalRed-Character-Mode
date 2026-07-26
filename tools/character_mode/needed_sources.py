#!/usr/bin/env python3
"""Build fill_sources.py's worklist: the roster families whose doc row has no
Source yet.

Derived from `rosters_mapped.json` and the same source lookup
`emit_roster_docs.py` performs, so the worklist is exactly the set of rows that
currently print "—" -- not a guess, and not the full roster.

SAFETY: a family that no audit wave examined is EXCLUDED and reported. Attaching
a mechanically-derived label to unaudited data would present unchecked rows as
checked, which is the precise failure the 2026-07-25 audit exists to correct.
Run `unaudited_families.py`, judge what it finds with
`audit_2026-07-25/wave5/BRIEF.md`, and apply the verdicts with `apply_wave5.py`
BEFORE running this.

Usage: needed_sources.py
Writes: sources_needed.json
"""
import json
from pathlib import Path

import emit_roster_docs as erd
from map_species import build_key_index, build_name_index, make_resolver

HERE = Path(__file__).parent


def main():
    species = erd.load_species()
    resolve = make_resolver(build_name_index(species), build_key_index(species))
    sources = erd.rekey_sources_onto_family_base(erd.load_sources(), species,
                                                 resolve)
    with open(HERE / "rosters_mapped.json") as f:
        mapped = json.load(f)

    unaudited = {}
    path = HERE / "unaudited_families.json"
    if path.is_file():
        with open(path, encoding="utf-8") as f:
            unaudited = json.load(f).get("unaudited", {})

    need, skipped = {}, 0
    for char, info in sorted(mapped.items()):
        per_base = sources.get(char, {})
        blocked = set(unaudited.get(char, ()))
        gaps = []
        for entry in info["species"]:
            name = erd.display(entry["name"])
            if per_base.get(name):
                continue
            if name in blocked:
                skipped += 1
                continue
            gaps.append(name)
        if gaps:
            need[char] = sorted(gaps)

    with open(HERE / "sources_needed.json", "w", encoding="utf-8") as f:
        json.dump(need, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    total = sum(len(v) for v in need.values())
    print("%d families need a source, across %d characters"
          % (total, len(need)))
    for char, gaps in sorted(need.items(), key=lambda kv: -len(kv[1]))[:12]:
        print("   %-16s %3d  %s" % (char, len(gaps), ", ".join(gaps[:6])))
    if skipped:
        print("EXCLUDED %d families that no audit wave examined -- judge them "
              "first (see this script's docstring)" % skipped)
    print("wrote sources_needed.json")


if __name__ == "__main__":
    main()
