#!/usr/bin/env python3
"""Build a throwaway ROM that reaches a character handler without the naming screen.

The mugshot renderer is driven from the selection handlers, which normally sit
behind RR's cheat-code text-entry screen. Driving that grid from a headless
emulator means navigating a per-letter cursor -- slow to write, fragile to
maintain, and it would be testing RR's own naming screen rather than anything
this project added.

So: take the built ROM and repoint ONE operand -- the bedroom console script's
`goto_if eq` target, which normally opens the code-entry screen -- straight at a
character's real handler. Everything downstream is then the genuine shipped
bytecode: the same setvar/setflag/givepokemon/callnative/msgbox/callnative
sequence, calling the same renderer, from the same script interpreter.

What this deliberately does NOT cover: the text-entry step itself and the
alias-comparison chain. Both are unchanged by the sprite work and are already
statically verified end-to-end by verify_artifacts.py's chain walk.

Output is build/radicalred_cm_mugshot_test.gba -- a test fixture, never shipped.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
SRC = BUILD / "radicalred_cm.gba"
OUT = BUILD / "radicalred_cm_mugshot_test.gba"

SCRIPT_ADDR = 0x08C90000
CHECK_SIZE = 20
N_DEBUG_CODES = 3

# Bedroom console script @ 0x0905006F (docs/ROUTINE_MAP.md, map 4.1 BG event #0):
#   lock(1) signmsg(1) loadword(6) callstd 5(2) compare 0x800D,1(5) goto_if(6)
# The goto_if's 4-byte operand therefore starts 17 bytes in.
CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086


def main():
    char_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    data = bytearray(SRC.read_bytes())

    # Sanity-check the console script really is what ROUTINE_MAP says before
    # rewriting anything inside it.
    s = data[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, f"not lock;signmsg: {s[:2].hex()}"
    assert s[8] == 0x09 and s[9] == 0x05, f"not callstd 5: {s[8:10].hex()}"
    assert s[10] == 0x21, f"not compare: {s[10]:#x}"
    assert s[15] == 0x06 and s[16] == 0x01, f"not goto_if eq: {s[15:17].hex()}"
    cur = struct.unpack_from("<I", data, GOTO_IF_OPERAND_OFF)[0]
    assert cur == CODE_ENTRY_CHAIN, f"goto_if operand is {cur:#x}, expected {CODE_ENTRY_CHAIN:#x}"

    # The handler address is read out of the built ROM's own check chain rather
    # than recomputed from the injector's layout arithmetic -- if the two ever
    # disagreed, recomputing would hide it.
    blk = SCRIPT_ADDR - 0x08000000 + (N_DEBUG_CODES + char_index) * CHECK_SIZE
    handler = struct.unpack_from("<I", data, blk + 16)[0]
    assert 0x08C90000 <= handler < 0x08CA0000, f"implausible handler {handler:#x}"

    struct.pack_into("<I", data, GOTO_IF_OPERAND_OFF, handler)
    OUT.write_bytes(bytes(data))
    print(f"{OUT.name}: bedroom console -> character[{char_index}] handler {handler:#x}")
    print("  (answer Yes at the console to run the real selection handler)")


if __name__ == "__main__":
    main()
