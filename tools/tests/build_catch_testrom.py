#!/usr/bin/env python3
"""TEST-ONLY ROM for the 100% roster catch (2026-10-09): Poke Balls, then a real
wild battle, from the bedroom console.

The bedroom console's yes-branch is repointed at

    additem POKE_BALL 10 ; setwildbattle <wild> <lvl> 0 ; dowildbattle ; end

so a real wild battle starts with no walk to grass. The party lead is written
by the Lua layer (tools/mgba_scripts/cm_sure_catch_test.lua), which also turns
Character Mode on during the battle, before the throw. Optional --no-hook
restores atkEF_handleballthrow's original `cmp r4,#254 ; bls` (the negative
control). Never distributed.
"""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster_console import restore_stock_console  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
OUT = BUILD / "radicalred_cm_catchtest.gba"
OUT_NOHOOK = BUILD / "radicalred_cm_catchtest_nohook.gba"

# Bedroom console script @ 0x0905006F (docs/ROUTINE_MAP.md, map 4.1 BG event #0)
# -- the same anchor build_pc_testrom.py and build_egg_testrom.py use, checked
# the same way, so a ROM whose script layout moved fails loudly here.
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086

# Clear of the other builders' pages (0x08CF0000/1000/2000/3000/3800).
TEST_SCRIPT_ADDR = 0x08CF2800
CATCH_ODDS_SITE = 0x107D552
CATCH_ODDS_ORIG = bytes.fromhex("fe2c1cd9")

OP_ADDITEM = 0x44
ITEM_POKE_BALL = 4
OP_SETWILDBATTLE = 0xB6
OP_DOWILDBATTLE = 0xB7
OP_END = 0x02


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    nohook = "--no-hook" in sys.argv[1:]
    expshare = "--expshare" in sys.argv[1:]
    wild_sp = int(argv[0], 0) if len(argv) > 0 else 123     # Scyther (catch rate 45)
    wild_lv = int(argv[1], 0) if len(argv) > 1 else 30
    assert 0 < wild_sp < 0x4000

    d = bytearray(SRC.read_bytes())

    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, "not lock;signmsg: %s" % s[:2].hex()
    assert s[15] == 0x06 and s[16] == 0x01, "not goto_if eq: %s" % s[15:17].hex()
    cur = struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0]
    assert cur == CODE_ENTRY_CHAIN, \
        "goto_if operand is %#x, expected %#x" % (cur, CODE_ENTRY_CHAIN)

    script = bytearray()
    if expshare:
        # Early Exp. Share (src/exp_share.c): CM on as Red, the activation
        # wrapper, then record what it left behind for the Lua layer:
        #   var 0x4011 <- 1 if flag 0x906 (CFRU FLAG_EXP_SHARE) is set
        #   var 0x4012 <- checkitem 182 (the Exp. Share) result
        import re as _re
        _inj = (ROOT / "tools" / "inject_character_mode.py").read_text()
        wrapper = int(_re.search(r"^EXP_SHARE_ADDR\s*=\s*(0x[0-9A-Fa-f]+)", _inj, _re.M).group(1), 16)
        assert d[wrapper - 0x08000000:wrapper - 0x08000000 + 2] == b"\x10\xb5", "no wrapper at EXP_SHARE_ADDR"
        cm_on = "--cm-off" not in sys.argv[1:]
        if cm_on:
            script += bytes([0x29]) + struct.pack("<H", 0x18FE)           # setflag CM
            script += bytes([0x16]) + struct.pack("<HH", 0x51FD, 1)       # setvar char = Red
        script += bytes([0x16]) + struct.pack("<HH", 0x4011, 0)
        script += bytes([0x23]) + struct.pack("<I", wrapper | 1)          # callnative
        skip = TEST_SCRIPT_ADDR + len(script) + 3 + 6 + 5
        script += bytes([0x2B]) + struct.pack("<H", 0x906)                # checkflag 0x906
        script += bytes([0x06, 0x00]) + struct.pack("<I", skip)           # goto_if unset
        script += bytes([0x16]) + struct.pack("<HH", 0x4011, 1)
        assert TEST_SCRIPT_ADDR + len(script) == skip
        script += bytes([0x47]) + struct.pack("<HH", 182, 1)              # checkitem 182,1
        script += bytes([0x19]) + struct.pack("<HH", 0x4012, 0x800D)      # copyvar
        script += bytes([0x02])
        out_name = "radicalred_cm_expsharetest%s.gba" % ("" if cm_on else "_off")
    else:
        script += bytes([OP_ADDITEM]) + struct.pack("<HH", ITEM_POKE_BALL, 10)
        script += (bytes([OP_SETWILDBATTLE]) + struct.pack("<H", wild_sp)
                   + bytes([wild_lv]) + struct.pack("<H", 0))
        script += bytes([OP_DOWILDBATTLE])
        script += bytes([OP_END])
        out_name = None

    off = TEST_SCRIPT_ADDR - 0x08000000
    region = d[off:off + len(script)]
    assert all(b == 0xFF for b in region), \
        "target %#x is not 0xFF-free -- pick another page" % TEST_SCRIPT_ADDR
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    # Test-only: bypass the roster pre-entry (tools/tests/roster_console.py).
    restore_stock_console(d)
    out = OUT if not out_name else BUILD / out_name
    if nohook:
        cur = bytes(d[CATCH_ODDS_SITE:CATCH_ODDS_SITE + 4])
        assert cur != CATCH_ODDS_ORIG, "the source ROM has no catch hook to remove"
        d[CATCH_ODDS_SITE:CATCH_ODDS_SITE + 4] = CATCH_ODDS_ORIG
        out = OUT_NOHOOK
    out.write_bytes(bytes(d))
    print("test ROM: %s" % out.name)
    if expshare:
        print("  bedroom console -> %sCM_ActivateSweepAndExpShare ; record flag 0x906 / "
              "checkitem 182" % ("setflag CM ; setvar char 1 ; " if "--cm-off" not in sys.argv[1:] else ""))
    else:
        print("  bedroom console -> additem Poke Ball x10 ; setwildbattle %d lv%d ; "
              "dowildbattle ; end%s" % (wild_sp, wild_lv, " (catch hook removed)" if nohook else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
