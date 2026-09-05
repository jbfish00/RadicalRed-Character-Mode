#!/usr/bin/env python3
"""Build a TEST-ONLY ROM variant for the LIVE egg-hatch e2e (never shipped).

WHY THIS EXISTS. ../game_plans/rowe_parity.md §13.20 closed the egg-hatch hole
here -- the hatch script's tail is overlaid with a `goto` into an injected tail
that replays the hatch and then runs `callnative CM_SweepPartyToPC`, so a gift
egg of an off-roster species can no longer hatch into a permanent off-roster
party member. That matters more in this game than in any sibling: there are
**33 reachable gift eggs** (docs/GIFT_EGGS.md), including a ¥5000 vendor that
sells a *random* "Wonder Egg". The hook is verified statically (five checks in
verify_artifacts.py, negative-tested 6/6) -- but **no hatch had ever been walked
in an emulator here**, which was §13.21's top open item.

Reaching a real gift egg means playing most of the game, so -- exactly as
build_mugshot_testrom.py does for the selection handlers -- we repoint ONE
operand, the bedroom console's `goto_if eq` target, at a tiny test entry script:

    giveegg <species>          ; hatched: the mon under test
    giveegg <species>          ; NOT hatched: see below
    setvar  0x8004, 0          ; the party index EggHatch reads
    goto    0x081BF546         ; == the hatch script, WITH the shipped splice

⭐ Everything after the `goto` is shipped, unmodified bytes: the spliced tail,
the replayed `special 0xC2`/`waitstate`/release, and the `callnative` into the
sweep. build/radicalred_cm.gba is never touched.

⚠️ WHY TWO EGGS. The bedroom checkpoint is BEFORE the starter, so the party is
empty, and `CM_SweepPartyToPC`'s never-empty rule would then KEEP the off-roster
hatchling -- correctly, and the test would prove nothing. The second egg is the
anchor: eggs are exempt from the sweep, so it satisfies the never-empty rule
without itself being a roster decision. One egg hatches, the other stays an egg.
(Seaglass and Lazarus need no such trick; their fixtures already hold a mon.)

⚠️ WHY `giveegg` RATHER THAN A SYNTHESISED EGG. Writing an egg into gPlayerParty
from Lua means reproducing this engine's substruct order, XOR key and checksum
from a donor tree. `giveegg` is the ROM's own constructor, so the egg under test
is by construction the same object a real gift egg produces.

Usage: python3 tools/tests/build_egg_testrom.py <species> [--no-hook]
Writes build/radicalred_cm_eggtest.gba (or ..._eggtest_nohook.gba).

`--no-hook` reverts the splice to the stock tail in the test ROM only. That is
the live layer's NEGATIVE CONTROL: cm_egg_hatch_test.lua must FAIL on it.
Without it the layer proves the sweep works when it is called and says nothing
about whether the hatch calls it -- which is the entire claim being made.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
OUT = BUILD / "radicalred_cm_eggtest.gba"

# Bedroom console script @ 0x0905006F (docs/ROUTINE_MAP.md, map 4.1 BG event
# #0), same anchor build_mugshot_testrom.py uses and checked the same way.
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086

# Free space past every injected region (the last is the egg tail at
# 0x08C8F000 and the wild tables through 0x08CEA400).
TEST_SCRIPT_ADDR = 0x08CF0000

OP_GIVEEGG = 0x7A
OP_SETVAR  = 0x16
OP_GOTO    = 0x05
VAR_0x8004 = 0x8004


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_hook = "--no-hook" in sys.argv
    if not argv:
        sys.exit("usage: build_egg_testrom.py <species> [--no-hook]")
    species = int(argv[0], 0)
    assert 0 < species < 0x4000, "species must be a literal id, not a var ref"

    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import egg_hook

    d = bytearray(SRC.read_bytes())

    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, f"not lock;signmsg: {s[:2].hex()}"
    assert s[15] == 0x06 and s[16] == 0x01, f"not goto_if eq: {s[15:17].hex()}"
    cur = struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0]
    assert cur == CODE_ENTRY_CHAIN, \
        f"goto_if operand is {cur:#x}, expected {CODE_ENTRY_CHAIN:#x}"

    # The whole point of this ROM is to run the SHIPPED hook. If the splice is
    # not in place the run would exercise the stock tail and report a green
    # "the mon stayed in the party" for the control cases while proving nothing.
    spliced = bytes(d[egg_hook.SPLICE_FILE_OFF:
                      egg_hook.SPLICE_FILE_OFF + len(egg_hook.SPLICE_ORIG)])
    assert spliced[0] == OP_GOTO, (
        "the egg-hatch splice is NOT in this build (%s) -- run the injector first"
        % spliced.hex(" "))
    tail = struct.unpack_from("<I", spliced, 1)[0]
    assert 0x08000000 <= tail < 0x0A000000, f"splice goto operand looks wrong: {tail:#x}"

    off = TEST_SCRIPT_ADDR - 0x08000000
    egg = bytes([OP_GIVEEGG]) + struct.pack("<H", species)
    script = (egg + egg
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, 0)
              + bytes([OP_GOTO]) + struct.pack("<I", egg_hook.SCRIPT_ENTRY))
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), \
        "test-script free space not clear"
    d[off:off + len(script)] = script

    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    out = OUT
    if no_hook:
        o = egg_hook.SPLICE_FILE_OFF
        d[o:o + len(egg_hook.SPLICE_ORIG)] = egg_hook.SPLICE_ORIG
        out = OUT.with_name(OUT.stem + "_nohook" + OUT.suffix)
        print("NEGATIVE CONTROL: splice reverted to the stock tail "
              f"({egg_hook.SPLICE_ORIG.hex(' ')}) -- the hook is absent here.")

    out.write_bytes(bytes(d))
    print(f"test ROM: {out.name}: bedroom console -> giveegg {species} x2, "
          f"setvar 0x8004=0, goto hatch script {egg_hook.SCRIPT_ENTRY:#x} "
          + ("(STOCK tail -- no sweep)" if no_hook else f"(spliced -> tail {tail:#x})")
          + ". Never distributed.")


if __name__ == "__main__":
    main()
