#!/usr/bin/env python3
"""Radical Red's own player costumes, read out of the BASE ROM.

RR's bedroom wardrobe ("Which costume would you like to change into?") offers
twelve costumes besides the default. Each one is a full player avatar: CFRU's
GetCustomGraphicsIdByState reads one var per avatar state (walk/run 0x501F,
bike 0x5020, surf 0x5021, field move 0x5022, fishing 0x5023, Vs Seeker on bike
0x5024, underwater 0x5025, Vs Seeker 0x503D), and a non-zero var replaces the
gender default for that state. A costume also sets the battle back sprite
(VAR_BACKSPRITE_SWITCH 0x5006) and the trainer card (0x5026). Character Mode
gives a character whose costume RR already ships that exact costume
(../../../game_plans/radical_red.md, overworld sprites).

Nothing here is restated by hand. The wardrobe script is decoded from the ROM:

  * each menu option is `compare 0x501F, W; call_if == A; compare 0x501F, W;
    call_if != B; return`, where B is `loadpointer <name>; special ...` -- so W
    (the costume's walk graphics id) is tied to its displayed NAME;
  * each "selected" block is a run of `setvar` starting `setvar 0x501F, W` and
    ending `warpmuted 4,1,2; release; end` (reload the bedroom so the avatar
    redraws).

A costume's assignments are that setvar run, verbatim.

    python3 tools/character_mode/rr_costumes.py     # print the table
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_ROM = ROOT / "rom" / "radicalred 4.1.gba"
CHARMAP = ROOT / "tools" / "charmap.txt"

VAR_PLAYER_WALKRUN = 0x501F
# The states CFRU's GetCustomGraphicsIdByState reads (its literal pool at
# 0x0907E4E4 holds exactly these, plus 0x5024 read by the Vs-Seeker-on-bike
# path). A parsed costume must set every one of them or it is not a costume.
AVATAR_STATE_VARS = (0x501F, 0x5020, 0x5021, 0x5022, 0x5023, 0x5024, 0x5025, 0x503D)
# The wardrobe's option labels live in one string pool; the walk ids it
# compares against are the costumes. Region bounds are the menu script's.
WARDROBE_SCRIPT = (0x01051E8D, 0x01052A00)

# RR's costume name -> the Character Mode character it is. Only names that
# differ need an entry: RR calls Ethan by his Japanese-release name.
CHARACTER_FOR_COSTUME = {"Gold": "Ethan"}


def _charmap():
    cm = {}
    for line in CHARMAP.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$", line.strip())
        if m:
            cm.setdefault(int(m.group(2), 16), m.group(1))
    cm[0x00] = " "
    return cm


def _text(rom, ptr, cm):
    o = ptr - 0x08000000
    if not 0 <= o < len(rom):
        return None
    e = rom.find(b"\xff", o, o + 40)
    if e < 0:
        return None
    return "".join(cm.get(b, "\x00") for b in rom[o:e])


def costumes(rom=None):
    """{costume name: {"walk": W, "sets": [(var, value), ...]}}, read from the ROM."""
    if rom is None:
        rom = BASE_ROM.read_bytes()
    cm = _charmap()
    lo, hi = WARDROBE_SCRIPT

    # 1. menu options: walk id -> name
    names = {}
    for o in range(lo, hi - 23):
        if rom[o] != 0x21 or struct.unpack_from("<H", rom, o + 1)[0] != VAR_PLAYER_WALKRUN:
            continue
        w = struct.unpack_from("<H", rom, o + 3)[0]
        a = o + 5
        if (rom[a] != 0x07 or rom[a + 1] != 1 or rom[a + 6] != 0x21
                or struct.unpack_from("<HH", rom, a + 7) != (VAR_PLAYER_WALKRUN, w)
                or rom[a + 11] != 0x07 or rom[a + 12] != 5):
            continue
        b = struct.unpack_from("<I", rom, a + 13)[0] - 0x08000000
        if not (0 <= b < len(rom)) or rom[b] != 0x0F:
            continue
        name = _text(rom, struct.unpack_from("<I", rom, b + 2)[0], cm)
        if w and name and name.isprintable() and "\x00" not in name:
            names[w] = name

    # 2. selected blocks: the setvar run that starts `setvar 0x501F, W`
    out = {}
    for w, name in names.items():
        start = bytes([0x16]) + struct.pack("<HH", VAR_PLAYER_WALKRUN, w)
        hits = [m.start() for m in re.finditer(re.escape(start), rom[lo:hi])]
        assert len(hits) == 1, f"costume {name} ({w:#x}): {len(hits)} setvar blocks"
        o = lo + hits[0]
        sets = []
        while rom[o] == 0x16:
            sets.append(struct.unpack_from("<HH", rom, o + 1))
            o += 5
        assert rom[o:o + 3] == bytes([0x3A, 0x04, 0x01]), (
            f"costume {name}: block does not end in warpmuted 4,1 ({rom[o:o + 3].hex()})")
        got = {v for v, _ in sets}
        missing = [hex(v) for v in AVATAR_STATE_VARS if v not in got]
        assert not missing, f"costume {name} leaves avatar states unset: {missing}"
        out[name] = {"walk": w, "sets": sets}
    return out


def costume_for_character(character, table=None):
    """The costume a Character Mode character wears, or None."""
    table = costumes() if table is None else table
    for name, c in table.items():
        if CHARACTER_FOR_COSTUME.get(name, name) == character:
            return c
    return None


if __name__ == "__main__":
    for name, c in sorted(costumes().items(), key=lambda kv: kv[1]["walk"]):
        who = CHARACTER_FOR_COSTUME.get(name, name)
        print(f"{name:8} walk {c['walk']:#06x} -> {who:8} "
              + " ".join(f"{v:#06x}={x:#x}" for v, x in c["sets"]))
