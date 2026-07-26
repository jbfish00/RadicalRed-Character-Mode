#!/usr/bin/env python3
"""Prove ROSTERS.md describes exactly what the BUILT ROM offers.

`emit_roster_docs.py` generates the docs from `rosters_expanded.bin`, so docs and
build agree by construction -- which means a bug in the generator would make them
agree with each other and still disagree with the game. This check closes that
loop by reading the allow-bitmaps back out of `build/radicalred_cm.gba` at the
address the injector actually wrote them to, and re-deriving every doc row from
those bytes with no reference to the intermediate file.

Checks:
  1. bitmaps in the built ROM == rosters_expanded.bin (the docs' input is real)
  2. every character in ROSTERS.md exists in characters_manifest.json
  3. every character the ROM offers appears in ROSTERS.md, and vice versa
  4. every Pokemon listed under a character is genuinely allowed by that
     character's in-ROM bitmap
  5. every final evolution the in-ROM bitmap allows is actually listed
  6. the sprite pages mirror ROSTERS.md character for character, row for row
  7. the character counts in ROSTERS.md, ROSTERS_SPRITES.md and README.md agree

Exit 1 on any mismatch. Run after emit_roster_docs.py, on a built ROM.
"""
import json
import os
import re
import sys

import emit_roster_docs as erd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BUILT = os.path.join(ROOT, "build", "radicalred_cm.gba")
BITMAPS_ADDR = 0x08C80100          # pinned by tools/inject_character_mode.py
STRIDE = erd.STRIDE
NUM_SPECIES = erd.NUM_SPECIES

REGION_RE = re.compile(r"^(Alolan|Galarian|Hisuian|Paldean)\s+")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_doc(text):
    """{character: [listed Pokemon names]} from a ROSTERS.md-shaped file."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^### (.+?) — ", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
            continue
        m = re.match(r"^\| (.+?) \| (.*?) \|$", line)
        if m and cur and m.group(1) not in ("Pokémon", "---"):
            out[cur].append(m.group(1).strip())
    return out


def main():
    fails = []

    if not os.path.isfile(BUILT):
        print("no built ROM at %s -- run tools/inject_character_mode.py first"
              % os.path.relpath(BUILT, ROOT))
        return 1
    with open(BUILT, "rb") as f:
        rom = f.read()
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    with open(os.path.join(HERE, "rosters_expanded.bin"), "rb") as f:
        staged = f.read()

    n = len(manifest)
    off = BITMAPS_ADDR - 0x08000000
    in_rom = rom[off:off + n * STRIDE]
    if in_rom != staged:
        fails.append("bitmaps in the built ROM differ from rosters_expanded.bin "
                     "-- the docs were generated from data the ROM does not carry")

    species = erd.load_species()
    real_evos = {}
    for sid, info in species.items():
        real_evos[sid] = [e[2] for e in (info.get("evolutions") or [])
                          if len(e) >= 3 and e[0] != erd.EVO_METHOD_MEGA
                          and e[2] in species]
    canonical = {}
    for sid in sorted(species):
        canonical.setdefault(species[sid].get("dexID") or sid, sid)

    def is_final(sid):
        if real_evos.get(sid):
            return False
        base = canonical.get(species[sid].get("dexID") or sid, sid)
        return not real_evos.get(base)

    def row_name(sid):
        region = erd.regional_form(species[sid])
        name = erd.display(species[sid]["name"])
        return "%s %s" % (region, name) if region else name

    # Re-derive, straight from the ROM's own bytes.
    rom_allowed, rom_finals = {}, {}
    for i, rec in enumerate(manifest):
        bits = in_rom[i * STRIDE:(i + 1) * STRIDE]
        allowed = {s for s in range(NUM_SPECIES)
                   if bits[s >> 3] & (1 << (s & 7)) and s in species}
        rom_allowed[rec["character"]] = allowed
        shown = set()
        for s in allowed:
            if not is_final(s):
                continue
            sid = s if erd.regional_form(species[s]) else \
                canonical.get(species[s].get("dexID") or s, s)
            shown.add(row_name(sid))
        rom_finals[rec["character"]] = shown

    doc = parse_doc(read(os.path.join(ROOT, "ROSTERS.md")))
    unselectable = set(erd.load_unselectable())

    for char in doc:
        if char not in rom_allowed:
            fails.append("%s: in ROSTERS.md but not in characters_manifest.json"
                         % char)
    # Selection gating is not injected yet, so the ROM offers every character and
    # the docs must list every character. When bit1=hidden lands, subtract
    # `unselectable` from the expected set here and in emit_roster_docs.
    for char in rom_allowed:
        if char not in doc:
            fails.append("%s: offered by the ROM but missing from ROSTERS.md"
                         % char)

    allowed_name_cache = {}
    for char, listed in doc.items():
        if char not in rom_allowed:
            continue
        names = allowed_name_cache.setdefault(
            char, {erd.display(species[s]["name"]) for s in rom_allowed[char]}
            | {row_name(s) for s in rom_allowed[char]})
        for mon in listed:
            if mon not in names and REGION_RE.sub("", mon) not in names:
                fails.append("%s: doc lists %s, which its in-ROM bitmap does not "
                             "allow" % (char, mon))
        missing = rom_finals[char] - set(listed)
        if missing:
            fails.append("%s: in-ROM bitmap allows %d final evolution(s) the doc "
                         "omits (%s)"
                         % (char, len(missing), ", ".join(sorted(missing)[:6])))

    # --- the sprite pages must mirror ROSTERS.md, cell for cell -------------
    sprite_chars, sprite_rows, missing_src = {}, 0, 0
    sprites_dir = os.path.join(ROOT, "sprites")
    for path in sorted(os.listdir(sprites_dir)):
        if not re.match(r"gen_\d+\.md$", path):
            continue
        cur = None
        for line in read(os.path.join(sprites_dir, path)).splitlines():
            m = re.match(r"^### (.+?) — ", line)
            if m:
                cur = m.group(1).strip()
                sprite_chars[cur] = 0
                continue
            for cell in re.finditer(
                    r"<sub>([^<]+)</sub>(<br><sub><i>([^<]*)</i></sub>)?", line):
                if cur is None:
                    continue
                sprite_chars[cur] += 1
                sprite_rows += 1
                if not cell.group(3):
                    missing_src += 1
    for char in doc:
        if char not in sprite_chars:
            fails.append("%s: in ROSTERS.md but missing from the sprite pages"
                         % char)
        elif sprite_chars[char] != len(doc[char]):
            fails.append("%s: sprite pages show %d Pokemon, ROSTERS.md lists %d"
                         % (char, sprite_chars[char], len(doc[char])))
    for char in sprite_chars:
        if char not in doc:
            fails.append("%s: on a sprite page but not in ROSTERS.md" % char)

    # --- counts must agree across all three docs ---------------------------
    counts = {}
    for path, pat in (("ROSTERS.md", r"\*\*(\d+) characters"),
                      ("ROSTERS_SPRITES.md", r"\*\*(\d+) characters"),
                      # ROWE's pattern was "one of (\d+)", which matches nothing
                      # in this repo's README -- so the check silently did not run
                      # while the README sat at a stale 199.
                      ("README.md", r"(\d+) characters, Generations")):
        full = os.path.join(ROOT, path)
        m = re.search(pat, read(full)) if os.path.isfile(full) else None
        counts[path] = int(m.group(1)) if m else None
    for path, got in counts.items():
        if got is None:
            fails.append("no character count found in %s -- the check that "
                         "would catch drift cannot run" % path)
        elif got != len(doc):
            fails.append("%s says %d characters, ROSTERS.md lists %d"
                         % (path, got, len(doc)))

    rows = sum(len(v) for v in doc.values())
    print("built ROM:    %d bitmaps read at 0x%08X%s"
          % (n, BITMAPS_ADDR, "" if in_rom == staged else "  (MISMATCH)"))
    print("ROSTERS.md:   %d characters, %d Pokemon rows" % (len(doc), rows))
    print("sprite pages: %d characters, %d cells, %d without a source line"
          % (len(sprite_chars), sprite_rows, missing_src))
    print("threshold:    %d characters below six fully-evolved (not gated in this "
          "build, so still documented)" % len(unselectable))
    if fails:
        print("\n%d MISMATCHES:" % len(fails))
        for f in fails[:25]:
            print("   " + f)
        if len(fails) > 25:
            print("   ... and %d more" % (len(fails) - 25))
        return 1
    print("\nOK: the documentation matches what the built ROM offers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
