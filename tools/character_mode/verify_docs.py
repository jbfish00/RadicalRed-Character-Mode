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
  8. ENCOUNTERS.md lists the same characters, and each one's family counts and
     repeatable marking match the wild/legendary tables read back out of the
     BUILT ROM -- not out of the emitted .bin files, which is the same
     closed-loop problem checks 1-5 exist to avoid

Exit 1 on any mismatch. Run after emit_roster_docs.py + emit_encounter_docs.py,
on a built ROM.
"""
import json
import os
import re
import struct
import sys

import emit_roster_docs as erd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BUILT = os.path.join(ROOT, "build", "radicalred_cm.gba")
BITMAPS_ADDR = 0x08C80100          # pinned by tools/inject_character_mode.py
# keep in sync with tools/inject_character_mode.py
WILD_OFFSETS_ADDR = 0x08CE0800
WILD_DATA_ADDR = 0x08CE0C00
WILD_LEG_OFFSETS_ADDR = 0x08CEA000
WILD_LEG_DATA_ADDR = 0x08CEA400
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
    hidden = {rec["character"] for rec in manifest if rec.get("hidden")}

    for char in doc:
        if char not in rom_allowed:
            fails.append("%s: in ROSTERS.md but not in characters_manifest.json"
                         % char)
    # The gate is injected, so the check is "SELECTABLE == documented", not
    # "enforced == documented": a hidden character still has a bitmap in the ROM
    # (that is the point -- old saves keep working) but the menu will not offer it,
    # so documenting it would advertise a code that gets rejected.
    for char in rom_allowed:
        if char in hidden:
            if char in doc:
                fails.append("%s: hidden from the menu but still listed in "
                             "ROSTERS.md -- re-run emit_roster_docs.py" % char)
            continue
        if char not in doc:
            fails.append("%s: offered by the ROM but missing from ROSTERS.md"
                         % char)
    # The manifest bit and the drop list are two different files; if they ever
    # disagree, one of emit_characters.py / derive_drops.py did not run.
    stripped = {re.sub(r"\s*\(anime\)$", "", c) for c in hidden}
    if stripped != unselectable:
        fails.append("manifest hides %d character(s) but character_drops.json "
                     "lists %d (%s) -- re-run derive_drops.py then "
                     "emit_characters.py"
                     % (len(stripped), len(unselectable),
                        ", ".join(sorted(stripped ^ unselectable)[:6])))

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

    # --- 8. ENCOUNTERS.md vs the tables in the BUILT ROM -------------------
    enc_path = os.path.join(ROOT, "ENCOUNTERS.md")
    enc_chars = 0
    if not os.path.isfile(enc_path):
        fails.append("ENCOUNTERS.md is missing -- run emit_encounter_docs.py")
    else:
        def count_families(addr_off, addr_data, idx, header=0):
            offs_base = addr_off - 0x08000000
            off = struct.unpack_from("<I", rom, offs_base + idx * 4)[0]
            p = addr_data - 0x08000000 + off
            flags = rom[p] if header else 0
            p += header
            return flags, rom[p]

        enc = {}
        cur = None
        for line in read(enc_path).splitlines():
            m = re.match(r"^### (.+?) — ", line)
            if m:
                cur = m.group(1).strip()
                enc[cur] = {"leg": 0, "fam": 0, "repeatable": False}
                continue
            if cur is None:
                continue
            m = re.match(r"^\*\*Legendary pool \((\d+) famil\w+, (once each|repeatable)\)", line)
            if m:
                enc[cur]["leg"] = int(m.group(1))
                enc[cur]["repeatable"] = m.group(2) == "repeatable"
            m = re.match(r"^\*\*Roster pool \((\d+) famil", line)
            if m:
                enc[cur]["fam"] = int(m.group(1))
        enc_chars = len(enc)

        if set(enc) != set(doc):
            fails.append("ENCOUNTERS.md lists %d characters, ROSTERS.md %d "
                         "(differences: %s)"
                         % (len(enc), len(doc),
                            ", ".join(sorted(set(enc) ^ set(doc))[:6])))
        by_name = {rec["character"]: i for i, rec in enumerate(manifest)}
        for char, got in enc.items():
            if char not in by_name:
                continue
            i = by_name[char]
            _f, want_fam = count_families(WILD_OFFSETS_ADDR, WILD_DATA_ADDR, i)
            flags, want_leg = count_families(WILD_LEG_OFFSETS_ADDR,
                                             WILD_LEG_DATA_ADDR, i, header=1)
            if got["fam"] != want_fam:
                fails.append("%s: ENCOUNTERS.md says %d roster families, the "
                             "built ROM has %d" % (char, got["fam"], want_fam))
            if got["leg"] != want_leg:
                fails.append("%s: ENCOUNTERS.md says %d legendary families, the "
                             "built ROM has %d" % (char, got["leg"], want_leg))
            if got["leg"] and got["repeatable"] != bool(flags & 0x1):
                fails.append("%s: ENCOUNTERS.md marks it %s, the ROM's flags "
                             "byte says otherwise"
                             % (char, "repeatable" if got["repeatable"]
                                else "once each"))

    rows = sum(len(v) for v in doc.values())
    print("built ROM:    %d bitmaps read at 0x%08X%s"
          % (n, BITMAPS_ADDR, "" if in_rom == staged else "  (MISMATCH)"))
    print("ROSTERS.md:   %d characters, %d Pokemon rows" % (len(doc), rows))
    print("sprite pages: %d characters, %d cells, %d without a source line"
          % (len(sprite_chars), sprite_rows, missing_src))
    print("threshold:    %d of %d characters hidden from the menu (gated in this "
          "build; records kept so old saves still load)" % (len(hidden), n))
    print("ENCOUNTERS.md: %d characters, family counts and repeatable flags "
          "checked against the built ROM's own tables" % enc_chars)
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
