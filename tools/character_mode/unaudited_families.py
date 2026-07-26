#!/usr/bin/env python3
"""Which of this repo's roster families has NO audit verdict behind them?

The 2026-07-25 adversarial audit was scoped to the roster data as it stood then.
Every game's `rosters_raw.json` is curated data with its own history, so each one
holds families no wave ever looked at -- ROWE had 156 of them. Those families are
UNVERIFIED, not verified-clean, and the distinction matters at attribution time:
running `fill_sources.py` over them would stamp a source on data nobody checked,
presenting unchecked rows as checked. That is the exact failure the audit exists
to fix, so this script exists to find them before any label is written.

An entry counts as AUDITED if some wave returned a verdict on it for that
character -- a keep, a removal, or an explicit `audit_keeps.json` shield. Family
level, not species level: the audit judged "Ash's Pikachu" and the roster stores
"Pichu", and species-level comparison reports thousands of false positives
because it counts every unexamined stage of an examined family.

Usage: unaudited_families.py [--json out.json]
Reads:  rosters_mapped.json, roster_removals.json, audit_keeps.json,
        ../../../audit_2026-07-25/{final_rosters,audit_compiled}.json
Writes: unaudited_families.json (the wave-5 work list), or --json path
"""
import argparse
import json
import os
from pathlib import Path

from map_species import (build_key_index, build_name_index, load_dex,
                         make_resolver)

HERE = Path(__file__).parent
AUDIT = HERE / "../../../audit_2026-07-25"


def load(path, key=None):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data[key] if key else data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(HERE / "unaudited_families.json"))
    args = ap.parse_args()

    species = load_dex()
    resolve = make_resolver(build_name_index(species), build_key_index(species))

    def base(name):
        sid = resolve(name)
        return None if sid is None else species[sid].get("ancestor", sid)

    mapped = load(HERE / "rosters_mapped.json")
    removals = load(HERE / "roster_removals.json", "removals")
    keeps = load(HERE / "audit_keeps.json", "keeps")
    final = load(AUDIT / "final_rosters.json", "rosters")
    compiled = load(AUDIT / "audit_compiled.json")

    # Every name any wave returned a verdict on, per character. final_rosters is
    # the post-audit keep set; removals and audit_compiled["remove"] are the
    # thrown-out ones (a removal IS a verdict -- the family was examined); keeps
    # is wave 5's explicit shield list.
    verdicts = {}
    for src in (final, keeps, compiled.get("keep", {})):
        for char, rows in src.items():
            if char.startswith("_"):
                continue
            names = rows.keys() if isinstance(rows, dict) else rows
            verdicts.setdefault(char, set()).update(names)
    for src in (removals, compiled.get("remove", {})):
        for char, rows in src.items():
            if char.startswith("_"):
                continue
            verdicts.setdefault(char, set()).update(
                r["species"] if isinstance(r, dict) else r for r in rows)

    audited_bases = {}
    for char, names in verdicts.items():
        audited_bases[char] = {b for b in (base(n) for n in names)
                               if b is not None}

    out, unseen_chars, total = {}, [], 0
    for char, info in sorted(mapped.items()):
        known = audited_bases.get(char)
        if known is None:
            unseen_chars.append(char)
            known = set()
        gap = sorted((s["name"] for s in info["species"]
                      if s["id"] not in known), key=str.lower)
        if gap:
            out[char] = gap
            total += len(gap)

    payload = {
        "_comment": "Roster families in this repo that NO audit wave examined. "
                    "Judge these with audit_2026-07-25/wave5/BRIEF.md before any "
                    "attribution pass labels them -- sourcing an unaudited row "
                    "presents unchecked data as checked.",
        "characters_never_audited": unseen_chars,
        "unaudited": out,
    }
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    covered = sum(len(v["species"]) for v in mapped.values())
    print("families in rosters_mapped.json: %d across %d characters"
          % (covered, len(mapped)))
    print("NEVER AUDITED: %d families across %d characters (%.1f%%)"
          % (total, len(out), 100.0 * total / covered))
    print("characters with no audit verdict at all: %d%s"
          % (len(unseen_chars),
             (" -- " + ", ".join(unseen_chars)) if unseen_chars else ""))
    worst = sorted(out.items(), key=lambda kv: -len(kv[1]))[:12]
    for char, gap in worst:
        print("  %-16s %3d  %s" % (char, len(gap), ", ".join(gap[:8])))
    print("wrote %s" % os.path.relpath(args.json, HERE))


if __name__ == "__main__":
    main()
