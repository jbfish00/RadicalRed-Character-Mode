#!/usr/bin/env python3
"""Fold a wave-5 audit's verdicts into this repo's three overlay files.

Wave 5 judges the roster families no earlier audit wave ever examined --
`unaudited_families.py` computes that list per repo, because each game's
`rosters_raw.json` is curated data with its own history. Its verdicts land in
exactly the same overlays the main audit uses, so the pipeline needs no special
case and a re-scrape cannot undo them:

  roster_removals.json  <- every `remove`, with its reason and confidence
  audit_keeps.json      <- every `keep`, as a family-removal shield
  roster_sources.json   <- every `keep`'s source label

Why keeps go into `audit_keeps.json` and not just "nowhere": the family rule says
one canon member makes the whole family canon, and `map_species.py` sweeps
removals at family level. A wave-5 keep on one member has to outrank another
wave's removal of a sibling, or the sweep silently deletes freshly-verified data.

Idempotent: re-running with the same results changes nothing.

Usage: apply_wave5.py <results-dir> [--dry-run]
       (results-dir holds gap_NN_result.json files)
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
TAG = "wave5-radicalred-2026-07-25"


def load(path, key):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return doc, doc.setdefault(key, {})


def save(path, doc, dry):
    if dry:
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(Path(args.results_dir).glob("gap_*_result.json"))
    if not files:
        raise SystemExit("no gap_*_result.json in %s" % args.results_dir)

    verdicts = {}
    for path in files:
        with open(path, encoding="utf-8") as f:
            for char, rows in json.load(f).items():
                if char.startswith("_"):
                    continue
                slot = verdicts.setdefault(char, {"keep": [], "remove": []})
                slot["keep"].extend(rows.get("keep", []))
                slot["remove"].extend(rows.get("remove", []))

    rem_doc, removals = load(HERE / "roster_removals.json", "removals")
    keep_doc, keeps = load(HERE / "audit_keeps.json", "keeps")
    src_doc, sources = load(HERE / "roster_sources.json", "sources")

    n_rem = n_keep = n_src = 0
    for char, rows in sorted(verdicts.items()):
        # --- removals -----------------------------------------------------
        existing = removals.setdefault(char, [])
        have = {r["species"] if isinstance(r, dict) else r for r in existing}
        for r in rows["remove"]:
            if r["species"] in have:
                continue
            existing.append({"species": r["species"],
                             "reason": r.get("reason", ""),
                             "confidence": r.get("confidence", "medium"),
                             "wave": TAG})
            have.add(r["species"])
            n_rem += 1
        if not existing:
            removals.pop(char)

        # --- keeps (the family-removal shield) ----------------------------
        shield = keeps.setdefault(char, [])
        for r in rows["keep"]:
            if r["species"] not in shield:
                shield.append(r["species"])
                n_keep += 1
        keeps[char] = sorted(set(shield))

        # --- sources ------------------------------------------------------
        per_char = sources.setdefault(char, {})
        for r in rows["keep"]:
            src = r.get("source")
            if not src:
                continue
            cur = per_char.get(r["species"]) or {}
            if cur.get("source"):
                continue                  # never overwrite an earlier label
            per_char[r["species"]] = {
                "source": src,
                "owned_form": r.get("owned_form") or r["species"],
                "derived": TAG,
            }
            n_src += 1

    save(HERE / "roster_removals.json", rem_doc, args.dry_run)
    save(HERE / "audit_keeps.json", keep_doc, args.dry_run)
    save(HERE / "roster_sources.json", src_doc, args.dry_run)

    print("%d result files, %d characters judged" % (len(files), len(verdicts)))
    print("  roster_removals.json: +%d species" % n_rem)
    print("  audit_keeps.json:     +%d shields" % n_keep)
    print("  roster_sources.json:  +%d labels" % n_src)
    for char, rows in sorted(verdicts.items()):
        if rows["remove"]:
            print("   - %-16s %s" % (char, ", ".join(r["species"]
                                                     for r in rows["remove"])))
    if args.dry_run:
        print("(dry run -- no file rewritten)")


if __name__ == "__main__":
    main()
