#!/usr/bin/env python3
"""TEST-ONLY ROM: a real wild battle from the bedroom console, for the instant HP bar layer (QoL A3, 2026-10-28).

The bedroom console's yes-branch runs:

    givemon Pikachu L10 ; setwildbattle Magikarp L2 ; dowildbattle ; waitstate ; end

(L10 obeys with no badges; a L50 Pikachu disobeyed and the battle never ended.) Built from whatever
build/radicalred_cm.gba holds, so the runner makes one from the shipping build and one from a CM_NO_INSTANTHP=1 build.

usage: build_hpbar_testrom.py <tag>   -> build/radicalred_cm_hpbar_<tag>.gba. Never distributed.
"""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster_console import restore_stock_console  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"

# Bedroom console script @ 0x0905006F (docs/ROUTINE_MAP.md), the anchor every console test ROM checks.
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086
TEST_SCRIPT_ADDR = 0x08CF3800      # inside the test builders' 0x08CF0000-0x08CF3FFF page, clear of the others

OP_GIVEMON = 0x79
OP_SETWILDBATTLE, OP_DOWILDBATTLE, OP_WAITSTATE, OP_END = 0xB6, 0xB7, 0x27, 0x02


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isalnum():
        sys.exit("usage: build_hpbar_testrom.py <tag>")
    tag = sys.argv[1]
    d = bytearray(SRC.read_bytes())
    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, "not lock;signmsg: %s" % s[:2].hex()
    assert s[15] == 0x06 and s[16] == 0x01, "not goto_if eq: %s" % s[15:17].hex()
    assert struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0] == CODE_ENTRY_CHAIN

    script = bytes([OP_GIVEMON]) + struct.pack("<HBH", 25, 10, 0) + b"\0" * 9      # CFRU givemon: + 9 bytes
    script += bytes([OP_SETWILDBATTLE]) + struct.pack("<HBH", 129, 2, 0)
    script += bytes([OP_DOWILDBATTLE, OP_WAITSTATE, OP_END])
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert all(b == 0xFF for b in d[off:off + len(script)]), "target %#x is not free" % TEST_SCRIPT_ADDR
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)
    restore_stock_console(d)      # test-only: bypass the roster pre-entry (tools/tests/roster_console.py)
    out = BUILD / ("radicalred_cm_hpbar_%s.gba" % tag)
    out.write_bytes(bytes(d))
    print("test ROM: %s (givemon Pikachu L10, wild Magikarp L2)" % out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
