#!/usr/bin/env python3
"""Build a TEST-ONLY ROM for the LIVE field-move layer (never shipped).

WHAT IT TESTS. src/field_moves.c (verify_artifacts section 20): with Character
Mode on, an HM in the bag lets ANY party mon pass the two Pokemon checks RR
still has: FireRed's `checkpartymove` (the vanilla Cut / Rock Smash / Strength
objects) and CFRU's PartyHasMonWithFieldMovePotential (specials 0x10A-0x10C,
Dive, Rock Climb). verify proves the bytes; only the real engine proves the rule.

THE FIXTURE. The bedroom checkpoint's party is EMPTY. The console runs:

    giveegg 129 (Magikarp) ; setvar 0x8004, 0 ; <hatch prefix> ; special EggHatch
    setflag 0x820..0x827                    (every badge)
    phase A, no HM in the bag:
        checkpartymove <m> ; copyvar 0x4000+i, 0x800D     for the 9 HM moves
        special 0x10A/B/C  ; copyvar 0x4009+j, 0x8004     Cut / Rock Smash / Strength
    additem 339..346                         (HM01..HM08)
    phase B: the same into 0x400C..0x4017
    setvar 0x401F, 0x600D                    (done)
    goto 0x081BDF13                          (FireRed's own Cut-tree script)

A hatched Magikarp knows only Splash and learns no HM, so every slot 0 in
phase B can only come from the hooks. Phase A must be all 6 (none) in every
mode: the hook never answers without the HM.

`--no-hook` restores the two hooked BLs and CheckHeap+16 to the BASE ROM's
bytes in the test ROM only: the layer's NEGATIVE CONTROL, which must fail.

Usage: python3 tools/tests/build_field_testrom.py [--no-hook]
Writes build/radicalred_cm_fieldtest.gba (or ..._nohook).
"""
import re
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster_console import restore_stock_console  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
BASE = ROOT / "rom" / "radicalred 4.1.gba"
OUT = BUILD / "radicalred_cm_fieldtest.gba"

CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086
# Inside the test builders' reserved squat (0x08CF0000-0x08CF3FFF), clear of
# the egg (0x08CF0000), PC (0x08CF1000), egg-battle (0x08CF2000) and PC-guard
# (0x08CF3000) scripts.
TEST_SCRIPT_ADDR = 0x08CF3800
SPECIES_MAGIKARP = 129
CUT_TREE_SCRIPT = 0x081BDF13          # FireRed's EventScript_CutTree (verify §20 pins it)

# Order matters: the Lua layer reads the vars in this order.
FIELD_MOVES = [(15, "Cut"), (19, "Fly"), (57, "Surf"), (70, "Strength"),
               (148, "Flash"), (249, "Rock Smash"), (127, "Waterfall"),
               (291, "Dive"), (392, "Rock Climb")]
FIELD_SPECIALS = [0x10A, 0x10B, 0x10C]   # Cut / Rock Smash / Strength
HM_ITEMS = range(339, 347)               # HM01..HM08
VAR_RESULTS = 0x4000
VAR_DONE, DONE = 0x401F, 0x600D

OP_GIVEEGG, OP_SETVAR, OP_GOTO, OP_SPECIAL, OP_WAITSTATE = 0x7A, 0x16, 0x05, 0x25, 0x27
OP_SETFLAG, OP_ADDITEM, OP_CHECKPARTYMOVE, OP_COPYVAR = 0x29, 0x44, 0x7C, 0x19
VAR_0x8004, VAR_RESULT = 0x8004, 0x800D

_INJ = (ROOT / "tools" / "inject_character_mode.py").read_text()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


def phase(first_var):
    out, v = b"", first_var
    for move, _ in FIELD_MOVES:
        out += bytes([OP_CHECKPARTYMOVE]) + struct.pack("<H", move)
        out += bytes([OP_COPYVAR]) + struct.pack("<HH", v, VAR_RESULT)
        v += 1
    for sp in FIELD_SPECIALS:
        out += bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, 0x77)
        out += bytes([OP_SPECIAL]) + struct.pack("<H", sp)
        out += bytes([OP_COPYVAR]) + struct.pack("<HH", v, VAR_0x8004)
        v += 1
    return out


def main():
    no_hook = "--no-hook" in sys.argv
    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import egg_hook

    d = bytearray(SRC.read_bytes())
    base = BASE.read_bytes()

    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, f"not lock;signmsg: {s[:2].hex()}"
    assert s[15] == 0x06 and s[16] == 0x01, f"not goto_if eq: {s[15:17].hex()}"
    assert struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0] == CODE_ENTRY_CHAIN

    pre_lo = egg_hook.SCRIPT_ENTRY - 0x08000000
    pre_hi = egg_hook.SPLICE_FILE_OFF
    hatch_prefix = bytes(d[pre_lo:pre_hi])
    assert hatch_prefix[0] == 0x69, "hatch script does not start with lockall"

    n = len(FIELD_MOVES) + len(FIELD_SPECIALS)
    script = (bytes([OP_GIVEEGG]) + struct.pack("<H", SPECIES_MAGIKARP)
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, 0)
              + hatch_prefix
              + bytes([OP_SPECIAL]) + struct.pack("<H", egg_hook.SPECIAL_HATCH)
              + bytes([OP_WAITSTATE])
              + b"".join(bytes([OP_SETFLAG]) + struct.pack("<H", 0x820 + i) for i in range(8))
              + phase(VAR_RESULTS)
              + b"".join(bytes([OP_ADDITEM]) + struct.pack("<HH", it, 1) for it in HM_ITEMS)
              + phase(VAR_RESULTS + n)
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_DONE, DONE)
              + bytes([OP_GOTO]) + struct.pack("<I", CUT_TREE_SCRIPT))
    assert VAR_RESULTS + 2 * n <= VAR_DONE
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert len(script) < 0x800, len(script)
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), \
        "test-script free space not clear"
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    out = OUT
    if no_hook:
        t = _inj("PSS_GUARD_TRAMPOLINE_ADDR") - 0x08000000 + 16
        regions = [(_inj("FIELD_CANLEARN_BL_SITE"), 4), (_inj("FIELD_KNOWS_BL_SITE"), 4),
                   (t, 8)]
        for o, k in regions:
            assert d[o:o + k] != base[o:o + k], f"{o:#x} is not patched -- run the injector"
            d[o:o + k] = base[o:o + k]
        out = OUT.with_name(OUT.stem + "_nohook" + OUT.suffix)
        print("NEGATIVE CONTROL: both field-move BLs and CheckHeap+16 restored to the "
              "base ROM -- the hooks are absent here.")

    restore_stock_console(d)
    out.write_bytes(bytes(d))
    print(f"test ROM: {out.name}: console -> hatch Magikarp, badges, "
          f"{n} checks without and with HM01-HM08 into vars {VAR_RESULTS:#x}.., "
          f"then the Cut-tree script. Never distributed.")


if __name__ == "__main__":
    main()
