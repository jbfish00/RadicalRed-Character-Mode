#!/usr/bin/env python3
"""TEST-ONLY ROM: two eggs, then a real wild battle, from the bedroom console.

⭐ WHY. rowe_parity.md §13.47 found that CM_SweepPartyToPC counts an EGG as
satisfying its never-empty rule, so the sweep can leave the player with a party
containing nothing but an egg -- a state Gen 3's own storage rules forbid (the
deposit check happens at DEPOSIT time; the sweep acts afterwards and calls
SendMonToPC directly). Reachability is settled. HARM was not, and it cannot be
settled by reading: it is "what does the battle engine do when a wild encounter
starts and the party holds only eggs?"

⚠️ THE MEASUREMENT THAT IS *NOT* ENOUGH, recorded so nobody repeats it: an egg
carries NONZERO HP (measured live: level 1, hp 11/12), so an HP-sum aliveness
test would report "alive". That is true and it is NOT a verdict -- vanilla Gen 3
demonstrably handles a party of [fainted mon, egg] correctly (you black out), so
the engine's egg handling is not a naive HP sum everywhere. Only running the
battle answers the question.

This repoints the bedroom console's yes-branch at:

    giveegg <sp> ; giveegg <sp> ; setwildbattle <wild> <lvl> 0 ; dowildbattle ; end

so the party is [egg, egg] -- an egg-only party built from the ROM's OWN
giveegg, never a synthesised one (§13.22) -- and a real wild battle starts
immediately, with no walking to grass required.

⚠️ NOTHING of Character Mode is under test here. This measures the ENGINE. The
sweep is not involved and the PC hook is not involved; a run of this ROM says
nothing about enforcement, only about what state the engine tolerates.

Never distributed.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
OUT = BUILD / "radicalred_cm_eggbattle.gba"

# Bedroom console script @ 0x0905006F (docs/ROUTINE_MAP.md, map 4.1 BG event #0)
# -- the same anchor build_pc_testrom.py and build_egg_testrom.py use, checked
# the same way, so a ROM whose script layout moved fails loudly here.
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086

# Clear of build_egg_testrom's 0x08CF0000 and build_pc_testrom's 0x08CF1000, so
# all three test ROMs can be built from one tree without clobbering each other.
TEST_SCRIPT_ADDR = 0x08CF2000

OP_GIVEEGG = 0x7A
OP_SETWILDBATTLE = 0xB6
OP_DOWILDBATTLE = 0xB7
OP_END = 0x02


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(argv) < 1:
        sys.exit("usage: build_eggbattle_testrom.py <egg_species> "
                 "[wild_species] [wild_level]")
    egg_sp = int(argv[0], 0)
    wild_sp = int(argv[1], 0) if len(argv) > 1 else 16     # Pidgey
    wild_lv = int(argv[2], 0) if len(argv) > 2 else 3
    for name, v in (("egg", egg_sp), ("wild", wild_sp)):
        assert 0 < v < 0x4000, "%s species must be a literal id" % name

    d = bytearray(SRC.read_bytes())

    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, "not lock;signmsg: %s" % s[:2].hex()
    assert s[15] == 0x06 and s[16] == 0x01, "not goto_if eq: %s" % s[15:17].hex()
    cur = struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0]
    assert cur == CODE_ENTRY_CHAIN, \
        "goto_if operand is %#x, expected %#x" % (cur, CODE_ENTRY_CHAIN)

    script = bytearray()
    script += bytes([OP_GIVEEGG]) + struct.pack("<H", egg_sp)
    script += bytes([OP_GIVEEGG]) + struct.pack("<H", egg_sp)
    script += (bytes([OP_SETWILDBATTLE]) + struct.pack("<H", wild_sp)
               + bytes([wild_lv]) + struct.pack("<H", 0))
    script += bytes([OP_DOWILDBATTLE])
    script += bytes([OP_END])

    off = TEST_SCRIPT_ADDR - 0x08000000
    region = d[off:off + len(script)]
    assert all(b == 0xFF for b in region), \
        "target %#x is not 0xFF-free -- pick another page" % TEST_SCRIPT_ADDR
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    OUT.write_bytes(bytes(d))
    print("test ROM: %s" % OUT.name)
    print("  bedroom console -> giveegg %d x2 ; setwildbattle %d lv%d ; "
          "dowildbattle ; end" % (egg_sp, wild_sp, wild_lv))
    print("  script %d B @ %#x. Engine behaviour only -- no Character Mode "
          "path is exercised. Never distributed." % (len(script),
                                                     TEST_SCRIPT_ADDR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
