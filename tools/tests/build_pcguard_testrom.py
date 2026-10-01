#!/usr/bin/env python3
"""Build a TEST-ONLY ROM for the LIVE PC second-guard e2e (never shipped).

WHAT IT TESTS. CM_PSSLastMonGuard (src/pc_guard.c): the storage system must
refuse to deposit the party's last ON-ROSTER mon when an off-roster one would
be left behind (ROWE's IsRemovingLastAllowedPartyMon). verify_artifacts
section 18 proves the bytes; only a real deposit attempt proves the rule.

THE FIXTURE. The bedroom checkpoint's party is EMPTY. The console runs:

    giveegg 25 (Pikachu) ; giveegg 60 (Poliwag)
    setvar 0x8004, 0 ; <hatch prefix> ; special EggHatch ; waitstate
    setvar 0x8004, 1 ; <hatch prefix> ; special EggHatch ; waitstate
    goto <the PC access script, WITH the shipped splice>

so the party is [Pikachu, Poliwag], both ALIVE, and the real storage system
opens. ⭐ With an alive Poliwag beside it, VANILLA ALLOWS depositing Pikachu
(CountPartyAliveNonEggMonsExcept(0) == 1), so only the guard can refuse -- and
only for a character who has Pikachu but not Poliwag (Red, measured from
rosters_expanded.bin; Misty is the reverse).

The hatch is inline (as in build_pc_testrom.py) because the hatch script ends
in `releaseall; end` and would also fire the EGG hook's sweep. Its prefix is
copied out of this ROM at build time.

`--no-guard` restores the two guard BLs, CanShiftMon's tail and the CheckHeap
trampoline to the BASE ROM's bytes in the test ROM only: the layer's NEGATIVE
CONTROL, which must fail (the deposit goes through).

`--no-link-sweep` restores only the link-trade BL in CB2_SaveAndEndTrade
(LINK_TRADE_BL_SITE): the negative control for the link-trade sweep layer
(tools/mgba_scripts/cm_link_trade_sweep_test.lua), which reuses this fixture.

Usage: python3 tools/tests/build_pcguard_testrom.py [--no-guard | --no-link-sweep]
Writes build/radicalred_cm_pcguard.gba (or ..._noguard / ..._nolinksweep).
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
OUT = BUILD / "radicalred_cm_pcguard.gba"

CONSOLE_SCRIPT_OFF = 0x105006F
GOTO_IF_OPERAND_OFF = CONSOLE_SCRIPT_OFF + 17
CODE_ENTRY_CHAIN = 0x09050086
# Inside the test builders' reserved squat (0x08CF0000-0x08CF3FFF), clear of
# the egg (0x08CF0000), PC (0x08CF1000) and egg-battle (0x08CF2000) scripts.
TEST_SCRIPT_ADDR = 0x08CF3000
SPECIES_ON, SPECIES_OFF = 25, 60     # Pikachu (on Red's roster), Poliwag (off it)

OP_GIVEEGG, OP_SETVAR, OP_GOTO, OP_SPECIAL, OP_WAITSTATE = 0x7A, 0x16, 0x05, 0x25, 0x27
VAR_0x8004 = 0x8004

_INJ = (ROOT / "tools" / "inject_character_mode.py").read_text()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


def main():
    no_guard = "--no-guard" in sys.argv
    no_link_sweep = "--no-link-sweep" in sys.argv
    assert not (no_guard and no_link_sweep), "one negative control at a time"
    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import egg_hook
    import pc_hook

    d = bytearray(SRC.read_bytes())
    base = BASE.read_bytes()

    s = d[CONSOLE_SCRIPT_OFF:CONSOLE_SCRIPT_OFF + 21]
    assert s[0] == 0x6A and s[1] == 0xCA, f"not lock;signmsg: {s[:2].hex()}"
    assert s[15] == 0x06 and s[16] == 0x01, f"not goto_if eq: {s[15:17].hex()}"
    assert struct.unpack_from("<I", d, GOTO_IF_OPERAND_OFF)[0] == CODE_ENTRY_CHAIN

    site_rom, site_off, site_orig = (pc_hook.SPLICE_ROM_ADDR, pc_hook.SPLICE_FILE_OFF,
                                     pc_hook.SPLICE_ORIG)
    assert d[site_off] == OP_GOTO, "the PC splice is NOT in this build -- run the injector"

    pre_lo = egg_hook.SCRIPT_ENTRY - 0x08000000
    pre_hi = egg_hook.SPLICE_FILE_OFF
    hatch_prefix = bytes(d[pre_lo:pre_hi])
    assert hatch_prefix[0] == 0x69, "hatch script does not start with lockall"

    def hatch(slot):
        return (bytes([OP_SETVAR]) + struct.pack("<HH", VAR_0x8004, slot)
                + hatch_prefix
                + bytes([OP_SPECIAL]) + struct.pack("<H", egg_hook.SPECIAL_HATCH)
                + bytes([OP_WAITSTATE]))

    script = (bytes([OP_GIVEEGG]) + struct.pack("<H", SPECIES_ON)
              + bytes([OP_GIVEEGG]) + struct.pack("<H", SPECIES_OFF)
              + hatch(0) + hatch(1)
              + bytes([OP_GOTO]) + struct.pack("<I", site_rom))
    off = TEST_SCRIPT_ADDR - 0x08000000
    assert all(b == 0xFF for b in d[off:off + len(script) + 8]), \
        "test-script free space not clear"
    d[off:off + len(script)] = script
    struct.pack_into("<I", d, GOTO_IF_OPERAND_OFF, TEST_SCRIPT_ADDR)

    out = OUT
    if no_guard:
        body = re.search(r"^PSS_GUARD_BL_SITES\s*=\s*\(([^)]*)\)", _INJ, re.M).group(1)
        sites = [int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", body)]
        sites += [_inj("PSS_CANSHIFT_BL"), _inj("PSS_CANSHIFT_TAIL")]
        t = _inj("PSS_GUARD_TRAMPOLINE_ADDR") - 0x08000000
        regions = [(x, 4) for x in sites] + [(t, 8)]
        for o, n in regions:
            assert d[o:o + n] != base[o:o + n], f"{o:#x} is not patched -- run the injector"
            d[o:o + n] = base[o:o + n]
        out = OUT.with_name(OUT.stem + "_noguard" + OUT.suffix)
        print("NEGATIVE CONTROL: the guard's BLs, tail and trampoline restored to "
              "the base ROM -- the guard is absent here.")

    if no_link_sweep:
        o = _inj("LINK_TRADE_BL_SITE")
        assert d[o:o + 4] != base[o:o + 4], f"{o:#x} is not patched -- run the injector"
        d[o:o + 4] = base[o:o + 4]
        out = OUT.with_name(OUT.stem + "_nolinksweep" + OUT.suffix)
        print("NEGATIVE CONTROL: CB2_SaveAndEndTrade's expand BL restored to the "
              "base ROM -- the link-trade sweep is absent here.")

    restore_stock_console(d)
    out.write_bytes(bytes(d))
    print(f"test ROM: {out.name}: console -> giveegg {SPECIES_ON}+{SPECIES_OFF}, "
          f"hatch both, goto PC script {site_rom:#x}. Never distributed.")


if __name__ == "__main__":
    main()
