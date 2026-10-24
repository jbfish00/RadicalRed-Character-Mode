#!/usr/bin/env python3
"""Build a TEST-ONLY ROM for the LIVE relearner layer (QoL A2, 2026-10-24; never shipped).

WHAT IT TESTS. inject_character_mode.relearn_any_level: CFRU's relearner list (GetMoveRelearnerMoves) uses level 250, so
every level-up move is relearnable, not only those at or below the mon's level.

THE FIXTURE. The bedroom console (empty party) runs:

    giveegg 129 (Magikarp) ; setvar 0x8004, 0 ; <hatch prefix> ; special EggHatch ; waitstate
    setvar 0x401E, 0x600E                    (marker: the Lua stops pressing B and picks the lead)
    special 0xDB ; waitstate                 (the Move Maniac's own ChooseMonForMoveRelearner)
    copyvar 0x4000, 0x8005                   (the relearnable-move count the party menu computed)
    copyvar 0x4001, 0x8004                   (the slot picked)
    setvar 0x401F, 0x600D ; releaseall ; end

A freshly hatched Magikarp (Lv1: RR hatches at level 1) knows Splash, its only move at or below Lv1, so the level-cut count is 0 and every
counted move is one above its level.

`--no-hook` restores the patched beq to the BASE ROM's bytes in the test ROM only: the layer's NEGATIVE CONTROL (count 0).

Usage: python3 tools/tests/build_relearn_testrom.py [--no-hook]
Writes build/radicalred_cm_reltest.gba (or ..._nohook).
"""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster_console import restore_stock_console  # noqa: E402
from build_field_testrom import (ROOT, SRC, BASE, CONSOLE_SCRIPT_OFF, GOTO_IF_OPERAND_OFF, CODE_ENTRY_CHAIN,  # noqa: E402
                                 SPECIES_MAGIKARP, OP_GIVEEGG, OP_SETVAR, OP_SPECIAL, OP_WAITSTATE, OP_COPYVAR,
                                 VAR_0x8004, _inj)

OUT = ROOT / "build" / "radicalred_cm_reltest.gba"
TEST_SCRIPT_ADDR = 0x08CF3C00          # in the test builders' squat, after the field test (0x08CF3800)
SPECIAL_CHOOSE_RELEARN = 0xDB          # what the Two Island Move Maniac runs
VAR_MARK, MARK = 0x401E, 0x600E
VAR_DONE, DONE = 0x401F, 0x600D


def main():
    no_hook = "--no-hook" in sys.argv
    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import egg_hook

    d = bytearray(SRC.read_bytes())
    base = BASE.read_bytes()
    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, f"not lock;signmsg: {s[:2].hex()}"
    assert struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0] == CODE_ENTRY_CHAIN
    hatch_prefix = bytes(d[egg_hook.SCRIPT_ENTRY - 0x08000000:egg_hook.SPLICE_FILE_OFF])
    assert hatch_prefix[0] == 0x69, "hatch script does not start with lockall"

    script = (bytes([OP_GIVEEGG]) + struct.pack("<H", SPECIES_MAGIKARP)
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, 0)
              + hatch_prefix
              + bytes([OP_SPECIAL]) + struct.pack("<H", egg_hook.SPECIAL_HATCH) + bytes([OP_WAITSTATE])
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_MARK, MARK)
              + bytes([OP_SPECIAL]) + struct.pack("<H", SPECIAL_CHOOSE_RELEARN) + bytes([OP_WAITSTATE])
              + bytes([OP_COPYVAR]) + struct.pack("<HH", 0x4000, 0x8005)
              + bytes([OP_COPYVAR]) + struct.pack("<HH", 0x4001, VAR_0x8004)
              + bytes([OP_SETVAR]) + struct.pack("<HH", VAR_DONE, DONE)
              + b"\x6B\x02")                                    # releaseall ; end
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), "test-script free space not clear"
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    out = OUT
    if no_hook:
        o = _inj("RELEARN_ANYLEVEL_BEQ") - 0x08000000
        assert d[o:o + 2] == b"\xc0\x46" and base[o:o + 2] == b"\x01\xd0", "the relearner beq is not patched"
        d[o:o + 2] = base[o:o + 2]
        out = OUT.with_name(OUT.stem + "_nohook" + OUT.suffix)
        print("NEGATIVE CONTROL: the relearner's level-gate beq restored to the base ROM.")
    restore_stock_console(d)
    out.write_bytes(bytes(d))
    print(f"test ROM: {out.name}: console -> hatch Magikarp, ChooseMonForMoveRelearner, count into 0x4000. "
          "Never distributed.")


if __name__ == "__main__":
    main()
