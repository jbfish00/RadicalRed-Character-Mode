#!/usr/bin/env python3
"""Generate ENCOUNTERS.md -- what each character can actually meet in the wild.

The deliverable in ../../game_plans/legendary_encounters.md §3. Same principle as
emit_roster_docs.py: derived from the data the ROM itself reads, never
hand-written, so it cannot drift from the patch.

Source is the EMITTED tables -- `wild_override.bin` (the 10% non-legendary pool)
and `wild_legendary.bin` (the 1% pool) plus their offset tables -- deliberately
NOT `rosters_mapped.json`. That file sits upstream of the level-band computation
and of the per-game dex filter, so documenting from it would promise families
this ROM cannot actually spawn.

Hidden characters (flags bit1, below the six-fully-evolved threshold) are
excluded, for the same reason ROSTERS.md excludes them: the menu does not offer
them, so their encounter pools are not something a player can reach.

Run after emit_wild_override.py:
    python3 tools/character_mode/emit_encounter_docs.py
"""
import ast
import json
import os
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "ENCOUNTERS.md")

GAME_TITLE = "Pokémon Radical Red v4.1"
LEGENDARY_CHANCE_PCT = 1     # keep in sync with src/wild_encounter_mode.c
OVERRIDE_CHANCE_PCT = 10

CATEGORY_LABEL = {"protagonist": "Protagonist", "rival": "Rival",
                  "gymleader": "Gym Leader", "elite4": "Elite Four",
                  "champion": "Champion", "villain": "Villain",
                  "anime": "Anime", "professor": "Professor"}


def display(name):
    return name.replace("’", "'")


def read(path):
    with open(os.path.join(HERE, path), "rb") as f:
        return f.read()


def parse_block(blob, offsets, idx, header=0):
    """(flags, [[(species_id, lvl_min, lvl_max), ...], ...]) for character idx."""
    p = struct.unpack_from("<I", offsets, idx * 4)[0]
    flags = blob[p] if header else 0
    p += header
    n_fam = blob[p]
    p += 1
    families = []
    for _ in range(n_fam):
        n_st = blob[p]
        p += 1
        stages = []
        for _ in range(n_st):
            sid, lo, hi = struct.unpack_from("<HBB", blob, p)
            p += 4
            stages.append((sid, lo, hi))
        families.append(stages)
    return flags, families


def stage_cell(stages, species):
    """'Pichu L1–15 → Pikachu L16–99 → Raichu L100' style, in table order."""
    parts = []
    for sid, lo, hi in stages:
        name = display(species.get(sid, {}).get("name", "#%d" % sid))
        parts.append("%s L%d–%d" % (name, lo, hi) if lo != hi
                     else "%s L%d" % (name, lo))
    return " → ".join(parts)


def main():
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    with open(os.path.join(HERE, "rr_pokedex_donor", "data.js")) as f:
        species = ast.literal_eval(f.read())["species"]

    wild = read("wild_override.bin")
    wild_off = read("wild_override_offsets.bin")
    leg = read("wild_legendary.bin")
    leg_off = read("wild_legendary_offsets.bin")
    for name, off in (("wild_override_offsets.bin", wild_off),
                      ("wild_legendary_offsets.bin", leg_off)):
        if len(off) != len(manifest) * 4:
            raise SystemExit("%s has %d entries, manifest has %d -- re-run "
                             "emit_wild_override.py" % (name, len(off) // 4,
                                                        len(manifest)))

    chars = []
    for i, rec in enumerate(manifest):
        if rec.get("hidden"):
            continue
        _f, fams = parse_block(wild, wild_off, i)
        flags, legs = parse_block(leg, leg_off, i, header=1)
        chars.append({
            "name": rec["character"],
            "gen": rec["generation"],
            "label": CATEGORY_LABEL.get(rec["category"], rec["category"].title()),
            "families": fams,
            "legendaries": legs,
            "repeatable": bool(flags & 0x1),
        })

    n_leg = sum(1 for c in chars if c["legendaries"])
    n_repeat = sum(1 for c in chars if c["repeatable"])
    starved = [c["name"] for c in chars if not c["families"] and not c["legendaries"]]

    out = [
        "# Character Mode — Wild Encounters (%s)" % GAME_TITLE, "",
        "What each character can meet **in the wild**, on top of the game's own "
        "encounter tables. Two independent rolls replace the species the area "
        "would normally produce; the level is always the area's own rolled level, "
        "and the evolution stage whose band fits that level is the one you meet.",
        "",
        "```",
        "roll %d%%   -> a legendary from this character's roster" % LEGENDARY_CHANCE_PCT,
        "else roll %d%% -> a non-legendary roster member" % OVERRIDE_CHANCE_PCT,
        "else          -> the game's own wild table",
        "```",
        "",
        "Covers grass/cave, surfing, rock smash, headbutt, sweet scent and every "
        "fishing rod tier — the four `CreateWildMon` call sites that are genuine "
        "table rolls. Scripted, swarm, ghost and DexNav encounters are untouched.",
        "",
        "**Legendaries retire once caught.** A legendary leaves the pool as soon "
        "as its Pokédex *caught* flag is set, so each one can be met once. The "
        "exception is a character whose roster is **entirely** legendary — it "
        "would otherwise be able to catch nothing for the rest of the run — and "
        "those are marked **repeatable** below. Two consequences worth knowing: a "
        "legendary caught before Character Mode was switched on is never offered, "
        "and the flag is per National Dex number, so catching one form of Deoxys, "
        "Giratina, Zygarde, Necrozma, Urshifu or Calyrex retires them all.",
        "",
        "GENERATED by `tools/character_mode/emit_encounter_docs.py` from "
        "`wild_override.bin` and `wild_legendary.bin`, the same tables the "
        "injected shim reads — do not hand-edit, regenerate.",
        "",
        "### Coverage", "",
        "- **%d characters** (the ones the menu offers; characters hidden below "
        "the six-fully-evolved threshold are not listed, same as `ROSTERS.md`)."
        % len(chars),
        "- **%d have a legendary pool** (%.0f%%); **%d** of those are repeatable."
        % (n_leg, 100.0 * n_leg / max(1, len(chars)), n_repeat),
        "- **%d characters can meet nothing at all** — both pools empty."
        % len(starved) + (" (%s)" % ", ".join(starved) if starved else
                          " Every character has something to catch."),
        "", "## Contents",
    ]

    by_gen = defaultdict(list)
    for c in chars:
        by_gen[c["gen"]].append(c)
    for g in by_gen:
        by_gen[g].sort(key=lambda c: c["name"])
    for g in sorted(by_gen):
        out.append("- [Generation %d](#generation-%d)" % (g, g))
    out.append("")

    for g in sorted(by_gen):
        out += ["", "## Generation %d" % g, ""]
        for c in by_gen[g]:
            out.append("### %s — %s" % (c["name"], c["label"]))
            leg_rate = LEGENDARY_CHANCE_PCT if c["legendaries"] else 0
            fam_rate = OVERRIDE_CHANCE_PCT if c["families"] else 0
            out.append("**Effective rates:** %d%% legendary%s · %d%% roster · "
                       "%d%% the game's own tables"
                       % (leg_rate,
                          " (repeatable)" if c["repeatable"] else
                          " (once each)" if leg_rate else "",
                          fam_rate, 100 - leg_rate - fam_rate))
            out.append("")
            if not c["families"] and not c["legendaries"]:
                out += ["> ⚠️ **This character can meet nothing in the wild.**", ""]
                continue

            if c["legendaries"]:
                out += ["**Legendary pool (%d famil%s, %s):**"
                        % (len(c["legendaries"]),
                           "y" if len(c["legendaries"]) == 1 else "ies",
                           "repeatable" if c["repeatable"] else "once each"),
                        "", "| # | Stages by level |", "|---|---|"]
                for n, stages in enumerate(c["legendaries"], 1):
                    out.append("| %d | %s |" % (n, stage_cell(stages, species)))
                out.append("")
            else:
                out += ["**Legendary pool:** none — no legendary on this "
                        "character's roster.", ""]

            if c["families"]:
                out += ["**Roster pool (%d famil%s):**"
                        % (len(c["families"]),
                           "y" if len(c["families"]) == 1 else "ies"),
                        "", "| # | Stages by level |", "|---|---|"]
                for n, stages in enumerate(c["families"], 1):
                    out.append("| %d | %s |" % (n, stage_cell(stages, species)))
                out.append("")
            else:
                out += ["**Roster pool:** none — this character's roster is "
                        "entirely legendary.", ""]

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    total_fams = sum(len(c["families"]) + len(c["legendaries"]) for c in chars)
    print("wrote ENCOUNTERS.md: %d characters, %d families, %d with a legendary "
          "pool (%d repeatable)" % (len(chars), total_fams, n_leg, n_repeat))
    if starved:
        print("  WARNING: %d character(s) can meet nothing: %s"
              % (len(starved), ", ".join(starved)))


if __name__ == "__main__":
    main()
