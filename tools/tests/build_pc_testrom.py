#!/usr/bin/env python3
"""Build a TEST-ONLY ROM variant for the LIVE PC-exit e2e (never shipped).

WHY THIS EXISTS. ../game_plans/rowe_parity.md §13.33 item 1: the PC-exit hook
shipped in all four GBA games on STATIC evidence alone. Seaglass got the first
live layer on 2026-09-10; this is the port of it. §13.20 is why it matters --
four live layers in three repos were once found dead behind a fully green static
suite, and a hook with no live layer is the same class of claim.

Reaching a PC and a mon worth sweeping means playing most of the game, so --
exactly as build_egg_testrom.py does -- we repoint ONE operand, the bedroom
console's `goto_if eq` target, at a tiny test entry script:

    giveegg <species>          ; becomes the MON UNDER TEST when it hatches
    giveegg <species>          ; the ANCHOR -- stays an egg, see below
    setvar  0x8004, 0          ; the party index EggHatch reads
    <the hatch script's own prefix, copied out of this ROM>
    special <EggHatch> ; waitstate
    goto    0x081A6A22         ; == the PC access script, WITH the shipped splice

⭐ Everything after that `goto` is shipped, unmodified bytes: the overlay, the
replayed `special 0x3C` + `waitstate` that opens the storage system and waits
for the player to close it, and the `callnative CM_SweepPartyToPC` that runs
when it does. build/radicalred_cm.gba is never touched.

⚠️ WHY THE HATCH IS INLINE HERE RATHER THAN A `goto` INTO THE HATCH SCRIPT. The
hatch script ends in `releaseall; end`, so there is no way to reach the PC after
it -- and going through it would ALSO fire the egg hook's sweep, which would box
the mon before the PC ever opened and make this layer test the wrong hook. The
hatch is FIXTURE here, not the thing under test, so it is reproduced inline:
its prefix (lockall, msgbox) is copied verbatim out of this ROM at build time
rather than hardcoded, and the `special`/`waitstate` pair is rebuilt from
egg_hook's own constant. The egg hook's splice is left completely alone.

⚠️⚠️ WHY TWO EGGS, AND WITHOUT THE SECOND ONE THIS LAYER PROVES NOTHING. The
bedroom checkpoint is BEFORE the starter, so the party is empty.
`CM_SweepPartyToPC` never empties the party: its pre-scan sets `kept` only if
some mon is an egg or on the roster, and when nothing qualifies the first
off-roster mon is kept anyway. With one egg, the hatchling would survive for
EVERY character, the "box" and "party" runs would be identical, and the layer
would go green discriminating nothing. The second egg is the anchor -- eggs are
exempt AND set `kept` -- so the hatchling's fate goes back to depending on the
roster. Only slot 0 is hatched; the other stays an egg.

⚠️ WHY `giveegg` RATHER THAN A SYNTHESISED MON. Writing a Pokemon into
gPlayerParty from Lua means reproducing this engine's substruct order, XOR key
and checksum from a donor tree. `giveegg` is the ROM's own constructor. It is
also the only way to get an OFF-ROSTER mon into the party at all: an off-roster
gift is boxed on the way in by the gift gate, while eggs are exempt everywhere
by design and the thing that hatches out of one is never checked on the way in.

Usage: python3 tools/tests/build_pc_testrom.py <species> [--no-hook]
Writes build/radicalred_cm_pctest.gba (or ..._pctest_nohook.gba).

`--no-hook` reverts the PC splice to its stock tail in the test ROM only. That
is the live layer's NEGATIVE CONTROL: cm_pc_exit_test.lua must FAIL on it.
Without it the layer proves the sweep works when it is called and says nothing
about whether CLOSING THE PC calls it -- which is the entire claim.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
OUT = BUILD / "radicalred_cm_pctest.gba"

# Bedroom console script @ 0x0905006F (docs/ROUTINE_MAP.md, map 4.1 BG event
# #0), the same anchor build_egg_testrom.py uses and checked the same way.
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086

# Free space past every injected region, and one page clear of the egg test
# script's 0x08CF0000 so both test ROMs can be built from one tree without one
# silently overwriting the other's entry.
TEST_SCRIPT_ADDR = 0x08CF1000

OP_GIVEEGG = 0x7A
OP_SETVAR  = 0x16
OP_GOTO    = 0x05
OP_SPECIAL = 0x25
OP_WAITSTATE = 0x27
VAR_0x8004 = 0x8004


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_hook = "--no-hook" in sys.argv
    if not argv:
        sys.exit("usage: build_pc_testrom.py <species> [--no-hook]")
    species = int(argv[0], 0)
    assert 0 < species < 0x4000, "species must be a literal id, not a var ref"

    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import egg_hook
    import pc_hook

    d = bytearray(SRC.read_bytes())

    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, f"not lock;signmsg: {s[:2].hex()}"
    assert s[15] == 0x06 and s[16] == 0x01, f"not goto_if eq: {s[15:17].hex()}"
    cur = struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0]
    assert cur == CODE_ENTRY_CHAIN, \
        f"goto_if operand is {cur:#x}, expected {CODE_ENTRY_CHAIN:#x}"

    # The whole point of this ROM is to run the SHIPPED PC hook. If the splice
    # is not in place the run would exercise the stock tail and report a green
    # "the mon stayed in the party" for the control cases while proving nothing
    # -- so refuse to build rather than test the wrong bytes.
    site_rom, site_off, site_orig = (pc_hook.SPLICE_ROM_ADDR,
                                     pc_hook.SPLICE_FILE_OFF,
                                     pc_hook.SPLICE_ORIG)
    spliced = bytes(d[site_off:site_off + len(site_orig)])
    assert spliced[0] == OP_GOTO, (
        "the PC splice is NOT in this build (%s) -- run the injector first"
        % spliced.hex(" "))
    tail = struct.unpack_from("<I", spliced, 1)[0]
    assert 0x08000000 <= tail < 0x0A000000, f"splice goto operand looks wrong: {tail:#x}"

    # The hatch script's prefix -- everything from its entry up to (not
    # including) the bytes the EGG hook overlays. Copied out of the ROM so this
    # fixture cannot drift away from the script it is imitating, and read from
    # before the splice so it is stock bytes even in a hooked build.
    pre_lo = egg_hook.SCRIPT_ENTRY - 0x08000000
    pre_hi = egg_hook.SPLICE_FILE_OFF
    assert pre_lo < pre_hi, "hatch script entry is not before its splice site"
    hatch_prefix = bytes(d[pre_lo:pre_hi])
    assert hatch_prefix[0] == 0x69, (
        "hatch script does not start with lockall (%s)" % hatch_prefix[:1].hex())

    off = TEST_SCRIPT_ADDR - 0x08000000
    egg = bytes([OP_GIVEEGG]) + struct.pack("<H", species)
    script = (egg + egg
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, 0)
              + hatch_prefix
              + bytes([OP_SPECIAL]) + struct.pack("<H", egg_hook.SPECIAL_HATCH)
              + bytes([OP_WAITSTATE])
              + bytes([OP_GOTO]) + struct.pack("<I", site_rom))
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), \
        "test-script free space not clear"
    d[off:off + len(script)] = script

    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    out = OUT
    if no_hook:
        d[site_off:site_off + len(site_orig)] = site_orig
        out = OUT.with_name(OUT.stem + "_nohook" + OUT.suffix)
        print("NEGATIVE CONTROL: the PC splice is reverted to its stock tail "
              f"({site_orig.hex(' ')}) -- the hook is absent here.")

    out.write_bytes(bytes(d))
    print(f"test ROM: {out.name}: bedroom console -> giveegg {species} x2, "
          f"inline hatch, goto PC script {site_rom:#x} "
          + ("(STOCK tail -- no sweep)" if no_hook else f"(spliced -> tail {tail:#x})")
          + f"; script {len(script)} B @ {TEST_SCRIPT_ADDR:#x}. Never distributed.")


if __name__ == "__main__":
    main()
