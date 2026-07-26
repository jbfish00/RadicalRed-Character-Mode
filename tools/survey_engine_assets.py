#!/usr/bin/env python3
"""Survey which Character Mode characters already have sprite art IN THE ROM.

Supersedes `survey_engine_ow.py`, which only covered overworld graphics. The
same undercount applied to trainer front pics and back pics: earlier surveys
were built from ROWE's `sprite_report.txt`, which records only art ROWE had
*staged for injection*. Anything added to the roster after that report was
written — the Frontier Brains most obviously — shows as "no art" even when the
base game ships it.

Concrete example: all seven Hoenn Frontier Brains are battleable trainers in
vanilla Emerald, so `TRAINER_PIC_SALON_MAIDEN_ANABEL` and friends exist with
real PNGs in the donor tree. Likewise `TRAINER_BACK_PIC_RIVAL` is Blue/Gary's
back sprite, sitting unused in CFRU.

Engines -> repos:
    firered  (Skeli789/Complete-Fire-Red-Upgrade)   Radical Red, Unbound
    emerald  (rh-hideout/pokeemerald-expansion)     Seaglass, Lazarus
    crystal  (pret/pokecrystal)                     Prism   (overworld only;
                                                     Gen 2 has no trainer pics
                                                     in this sense)

    python3 tools/survey_engine_assets.py           # per-repo report
    python3 tools/survey_engine_assets.py --json    # machine-readable
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

EMERALD = "Seaglass-Character-Mode/tools/pokeemerald_expansion_donor"
FIRERED = "RadicalRed-Character-Mode/tools/cfru_donor"
CRYSTAL = "Prism-Character-Mode/tools/pokecrystal_donor"

# engine -> asset kind -> (file, constant prefix)
TABLES = {
    "emerald": {
        "ow":    (f"{EMERALD}/include/constants/event_objects.h", r"OBJ_EVENT_GFX_"),
        "front": (f"{EMERALD}/include/constants/trainers.h",      r"TRAINER_PIC_"),
        # pokeemerald keeps back-pic symbols in the graphics data file, NOT in
        # include/constants/trainers.h like the front pics. Reading the wrong
        # file here silently reports zero back pics for both Emerald repos.
        # These symbols are CamelCase (gTrainerBackPic_Brendan), unlike every
        # other table here -- an uppercase-only capture matches just the leading
        # letter, so `gTrainerBackPic_None` yields "N" and falsely hands a back
        # sprite to the character N. Marked camel so it gets normalised.
        "back":  (f"{EMERALD}/src/data/graphics/trainers.h", r"gTrainerBackPic_", "camel"),
    },
    "firered": {
        "ow":    (f"{FIRERED}/include/constants/event_objects.h", r"EVENT_OBJ_GFX_"),
        "front": (f"{FIRERED}/include/constants/trainers.h",      r"TRAINER_PIC_"),
        "back":  (f"{FIRERED}/include/constants/trainers.h",      r"TRAINER_BACK_PIC_"),
    },
    "crystal": {
        "ow":    (f"{CRYSTAL}/constants/sprite_constants.asm",    r"SPRITE_"),
    },
}

# Constant names carry trainer-class prefixes the character name does not, e.g.
# TRAINER_PIC_SALON_MAIDEN_ANABEL, TRAINER_PIC_LEADER_ROXANNE. Strip them before
# matching so a character matches its own pic regardless of title.
CLASS_PREFIXES = [
    "SALON_MAIDEN", "DOME_ACE", "PALACE_MAVEN", "ARENA_TYCOON", "FACTORY_HEAD",
    "PIKE_QUEEN", "PYRAMID_KING", "LEADER", "ELITE_FOUR", "CHAMPION",
    "MAGMA_LEADER", "AQUA_LEADER", "TEAM_ROCKET_BOSS", "BOSS", "PROF",
]

ALIAS = {
    "Red": ["RED_NORMAL", "RED", "RED_PLAYER"],
    "Leaf": ["LEAF_NORMAL", "LEAF", "LEAF_PLAYER", "GREEN_NORMAL"],
    "Blue": ["BLUE", "RIVAL"],
    "Gary": ["BLUE", "RIVAL"],
    "Ethan": ["ETHAN_PLAYER", "ETHAN", "CHRIS"],
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
    "Tate": ["TATE", "TATE_AND_LIZA"],
    "Liza": ["LIZA", "TATE_AND_LIZA"],
    "Samson Oak": [],
}

# Constants that exist but denote a same-named engine-custom NPC, not our
# character. CFRU is Unbound's engine, so its MARLON/IVORY are Unbound's own
# protagonists, and it predates Gen 9 entirely.
AMBIGUOUS = {
    ("firered", "Marlon"): "CFRU MARLON is Unbound's own protagonist",
    ("firered", "Penny"):  "CFRU predates Gen 9; this is an Unbound NPC",
    ("firered", "Melony"): "unverified; likely an Unbound NPC",
}


def load(rel, prefix, style="upper"):
    """Collect constant/symbol names following `prefix`.

    style="upper" -> SCREAMING_SNAKE constants (most tables)
    style="camel" -> CamelCase symbols, normalised to UPPER_SNAKE
    """
    path = WS / rel
    if not path.exists():
        print(f"warning: donor missing at {path}", file=sys.stderr)
        return set()
    text = path.read_text(errors="replace")
    if style == "camel":
        raw = re.findall(prefix + r"([A-Za-z0-9_]+)", text)
        return {re.sub(r"(?<!^)(?=[A-Z])", "_", n).upper() for n in raw}
    return set(re.findall(prefix + r"([A-Z0-9_]+)", text))


def strip_class(const):
    """TRAINER_PIC_SALON_MAIDEN_ANABEL -> ANABEL (also yields the raw form)."""
    for pre in CLASS_PREFIXES:
        if const.startswith(pre + "_"):
            return const[len(pre) + 1:]
    return const


def index(consts):
    """Map every constant to itself AND to its class-stripped form."""
    out = {}
    for c in consts:
        out.setdefault(c, c)
        s = strip_class(c)
        out.setdefault(s, c)
    return out


def load_characters(repo):
    path = WS / repo / "tools/character_mode/characters.txt"
    out = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = [p.strip() for p in s.split("|")]
        if len(parts) < 4:
            continue
        out.append(parts[0])
    return out


def stems(name):
    if name in ALIAS:
        return ALIAS[name]
    return [re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    idx = {eng: {kind: index(load(*spec)) for kind, spec in kinds.items()}
           for eng, kinds in TABLES.items()}   # spec may carry a 3rd "style" field

    report = {}
    for key, label, repo, engine in GAMES:
        chars = load_characters(repo)
        found = {}
        for name in chars:
            if (engine, name) in AMBIGUOUS:
                continue
            hit = {}
            for kind, table in idx[engine].items():
                for s in stems(name):
                    if s in table:
                        hit[kind] = table[s]
                        break
            if hit:
                found[name] = hit
        report[key] = {"label": label, "engine": engine,
                       "total": len(chars), "found": found}

    if args.json:
        print(json.dumps(report, indent=1))
        return

    for key, label, repo, engine in GAMES:
        r = report[key]
        f = r["found"]
        counts = {k: sum(1 for v in f.values() if k in v) for k in ("ow", "front", "back")}
        print(f"\n{label}  ({engine})  —  {r['total']} characters")
        print(f"   overworld {counts['ow']:3d}   front pic {counts['front']:3d}   "
              f"back pic {counts['back']:3d}")
        for name, hit in sorted(f.items()):
            bits = "  ".join(f"{k}={v}" for k, v in sorted(hit.items()))
            print(f"     {name:<16} {bits}")
    print("\nAmbiguous name collisions deliberately NOT counted:")
    for (engine, name), why in AMBIGUOUS.items():
        print(f"   {engine}/{name}: {why}")


if __name__ == "__main__":
    main()
