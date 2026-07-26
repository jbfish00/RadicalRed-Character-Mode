#!/usr/bin/env python3
"""Regenerate README.md's "## Character codes" section from the injected data.

The codes a player types at the bedroom console are derived from the character
name by exactly one rule (see tools/inject_character_mode.py and the
independent re-derivation in tools/tests/audit_conflicts.py): drop a trailing
" (anime)", then strip every non-alphanumeric character. Keeping the tables
hand-written meant they went stale the moment characters were added -- the
2026-07-23 rebuild took the roster from 184 to 199 and the README still listed
184, so Tobias and all 14 professors shipped with no documented code at all.

Everything comes from characters_manifest.json (character order, category,
generation, roster[0] = the granted starter) and the Radical Red pokedex donor
(species names), so this section cannot drift from the patch again.

Run after emit_characters.py:
    python3 tools/character_mode/emit_readme_codes.py
"""
import ast
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.path.join(HERE, "..", ".."))
README = os.path.join(TARGET, "README.md")

SECTION_START = "## Character codes"
SECTION_END = "## For developers"


def alias_for(display):
    """Mirrors tools/inject_character_mode.py exactly."""
    if display.endswith(" (anime)"):
        display = display[:-len(" (anime)")]
    return re.sub(r"[^A-Za-z0-9]", "", display)


def main():
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        chars = json.load(f)["characters"]
    with open(os.path.join(HERE, "rr_pokedex_donor/data.js")) as f:
        species = ast.literal_eval(f.read())["species"]

    by_gen = defaultdict(list)
    for rec in chars:
        by_gen[rec["generation"]].append(rec)

    out = [SECTION_START, ""]
    for gen in sorted(by_gen):
        out += ["### Generation %d" % gen, "",
                "| Type this code | Character | Role | Starter Pokemon |",
                "|---|---|---|---|"]
        for rec in by_gen[gen]:
            ids = rec.get("roster_species_ids") or []
            if not rec.get("has_signature"):
                # No curated signature ace: the selection script rolls a
                # starter from the roster, so naming roster[0] would be a lie.
                starter = "random from roster"
            else:
                starter = species[ids[0]]["name"].replace("’", "'") if ids else "—"
            out.append("| `%s` | %s | %s | %s |"
                       % (alias_for(rec["character"]), rec["character"],
                          rec["category"], starter))
        out.append("")

    text = open(README, encoding="utf-8").read()
    start = text.index(SECTION_START)
    end = text.index(SECTION_END)
    text = text[:start] + "\n".join(out) + "\n" + text[end:]

    # The intro sentence's count is generated too. Rewriting only the tables left
    # it reading "199 characters" through both the Volo build (210) and the
    # 2026-07-25 roster audit (238) -- the same drift this script was written to
    # stop, one paragraph above the part it was fixing. verify_docs.py now checks
    # this number, so a silent miss here becomes a test failure.
    text, n = re.subn(r"\b\d+ characters, Generations 1 through 9\.",
                      "%d characters, Generations 1 through 9." % len(chars),
                      text, count=1)
    if not n:
        print("  !! could not find the intro character-count sentence in "
              "README.md -- check it by hand")
    open(README, "w", encoding="utf-8").write(text)

    print("rewrote README.md's character-code tables: %d characters across "
          "generations %s" % (len(chars), ", ".join(str(g) for g in sorted(by_gen))))


if __name__ == "__main__":
    main()
