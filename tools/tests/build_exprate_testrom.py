#!/usr/bin/env python3
"""TEST-ONLY ROM: a real wild battle from the bedroom console, for the EXP rate layer (2026-10-29, src/exp_rate.c).

The bedroom console's yes-branch runs:

    copyvar 0x51FC, 0x8004 ; setflag 0x906 ; givemon Pikachu L10 ; givemon Magikarp L5 ;
    setwildbattle Magikarp L2 ; dowildbattle ; waitstate ; end

The Lua puts the rate in gSpecialVar_0x8004 first, so one ROM (and one bedroom checkpoint) covers every rate. Flag
0x906 is CFRU's party-wide Exp. Share, so the benched Magikarp gains through the share. Built from whatever
build/radicalred_cm.gba holds; `nohook` restores atk23_getexp's MathMin BL (the control: the rate is ignored).

usage: build_exprate_testrom.py <on|nohook>   -> build/radicalred_cm_exprate_<tag>.gba. Never distributed.
"""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from roster_console import restore_stock_console  # noqa: E402
from inject_character_mode import thumb_bl, EXPRATE_MIN_SITE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086
TEST_SCRIPT_ADDR = 0x08CF3900      # the test builders' 0x08CF0000-0x08CF3FFF page, clear of the hpbar ROM's 0x08CF3800


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("on", "nohook"):
        sys.exit("usage: build_exprate_testrom.py <on|nohook>")
    tag = sys.argv[1]
    d = bytearray(SRC.read_bytes())
    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, "not lock;signmsg: %s" % s[:2].hex()
    assert s[15] == 0x06 and s[16] == 0x01, "not goto_if eq: %s" % s[15:17].hex()
    assert struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0] == CODE_ENTRY_CHAIN
    site, orig = EXPRATE_MIN_SITE
    o = site - 0x08000000
    assert bytes(d[o:o + 4]) != thumb_bl(site, orig), "build/radicalred_cm.gba has no EXP rate hook"
    if tag == "nohook":
        d[o:o + 4] = thumb_bl(site, orig)

    script = b"\x19" + struct.pack("<HH", 0x51FC, 0x8004) + b"\x29" + struct.pack("<H", 0x906)
    script += b"\x79" + struct.pack("<HBH", 25, 10, 0) + b"\0" * 9        # CFRU givemon: + 9 bytes
    script += b"\x79" + struct.pack("<HBH", 129, 5, 0) + b"\0" * 9
    script += b"\xB6" + struct.pack("<HBH", 129, 2, 0) + b"\xB7\x27\x02"
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert all(b == 0xFF for b in d[off:off + len(script)]), "target %#x is not free" % TEST_SCRIPT_ADDR
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)
    restore_stock_console(d)      # test-only: bypass the roster pre-entry (tools/tests/roster_console.py)
    out = BUILD / ("radicalred_cm_exprate_%s.gba" % tag)
    out.write_bytes(bytes(d))
    print("test ROM: %s (rate from 0x8004, Pikachu L10 + Magikarp L5, wild Magikarp L2)" % out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
