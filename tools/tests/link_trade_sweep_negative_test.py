#!/usr/bin/env python3
"""Negative test for verify_artifacts.py section 19 -- the link-trade sweep
(src/pc_guard.c CM_LinkTradeSweepThenExpand; rowe_parity.md §13.53),
2026-09-30.

Each case breaks a COPY of the built ROM in one way the hook could be wrong and
requires the matching check to report FAIL BY NAME; the other built-ROM
section-19 checks must stay PASS, proving the tamper was precise.

  1. control                          -- every section-19 check passes
  2. the site left calling vanilla     -- StringExpandPlaceholders directly
  3. the site aimed at CheckHeap+0     -- the PC guard's trampoline, a REAL
                                          neighbour: the plausible-wrong shape
  4. the trampoline aimed elsewhere    -- at CM_PSSLastMonGuard, a real entry
  5. the shim's sweep literal bent     -- +4: it would call into the middle of
                                          CM_SweepPartyToPC
  6. control again                     -- proves 2-5 left nothing behind

⚠️ THE ROM IS NEVER MODIFIED IN PLACE.
"""
import os
import re
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_cases  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "radicalred_cm.gba")

_INJ = open(os.path.join(ROOT, "tools", "inject_character_mode.py"), encoding="utf-8").read()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


GUARD_TRAMP = _inj("PSS_GUARD_TRAMPOLINE_ADDR")
LINK_TRAMP = GUARD_TRAMP + 8
SITE = _inj("LINK_TRADE_BL_SITE")
EXPAND = _inj("STRING_EXPAND_PLACEHOLDERS")
PC_GUARD = _inj("PC_GUARD_ADDR") - 0x08000000


def _nm(elf):
    out = subprocess.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", elf)],
                         check=True, capture_output=True, text=True).stdout
    return {m.group(2): int(m.group(1), 16)
            for m in re.finditer(r"^([0-9a-f]+) [Tt] (\w+)$", out, re.M)}


def thumb_bl(src, dst):
    off = ((dst - (src + 4)) >> 1) & 0x3FFFFF
    return struct.pack("<HH", 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


CHECKS = {
    "site": "built: the site calls the link trampoline",
    "tramp": "link trampoline is ldr r3,[pc]; bx r3 -> CM_LinkTradeSweepThenExpand",
    "lits": "compiled link shim (read from the ROM) calls CM_SweepPartyToPC",
}


def _child_env():
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path):
    src = open(VERIFY, encoding="utf-8").read()
    src = src.replace('ROM_OUT = ROOT / "build" / "radicalred_cm.gba"',
                      'ROM_OUT = Path(%r)' % rom_path, 1)
    path = os.path.join(HERE, "_negtest_verify_linksweep.%d.py" % os.getpid())  # unique per run; gitignored
    open(path, "w", encoding="utf-8").write(src)
    try:
        p = subprocess.run([sys.executable, path], capture_output=True,
                           text=True, cwd=ROOT, env=_child_env())
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    return p.returncode, p.stdout + p.stderr


def _hit(out, key, marker):
    return any(line.strip().startswith("[%s]" % marker) and CHECKS[key] in line
               for line in out.splitlines())


# A deliberate LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 6


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    sweep = _nm("character_mode.elf")["CM_SweepPartyToPC"]
    guard = _nm("pc_guard.elf")["CM_PSSLastMonGuard"]
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail, also_pass=()):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append(name)
                    print("  [MISS] %s -- TAMPER CHANGED NOTHING" % name)
                    return
            rom = os.path.join(tmp, "tampered.gba")
            open(rom, "wb").write(bytes(data))
            _rc, out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "PASS") for k in CHECKS)
                detail = "every section-19 check passes"
            else:
                ok = _hit(out, want_fail, "FAIL")
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in also_pass:
                    if not _hit(out, k, "PASS"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts section 19, link-trade sweep")
        case("1 control -- the real build", None, None)

        def leave_site(d):
            d[SITE:SITE + 4] = thumb_bl(0x08000000 + SITE, EXPAND)
        case("2 the site still calls StringExpandPlaceholders", leave_site,
             "site", also_pass=("tramp", "lits"))

        def site_to_guard(d):
            d[SITE:SITE + 4] = thumb_bl(0x08000000 + SITE, GUARD_TRAMP)
        case("3 the site aimed at the PC guard's trampoline", site_to_guard,
             "site", also_pass=("tramp", "lits"))

        def aim_elsewhere(d):
            struct.pack_into("<I", d, LINK_TRAMP - 0x08000000 + 4, guard | 1)
        case("4 the trampoline aimed at CM_PSSLastMonGuard", aim_elsewhere,
             "tramp", also_pass=("site", "lits"))

        def bend_sweep(d):
            code = bytes(d[PC_GUARD:PC_GUARD + 0x1400])
            ks = [k for k in range(0, len(code) - 3, 4)
                  if struct.unpack_from("<I", code, k)[0] == sweep | 1]
            assert len(ks) == 1, f"sweep literal found {len(ks)} times -- re-derive"
            struct.pack_into("<I", d, PC_GUARD + ks[0], (sweep | 1) + 4)
        case("5 the shim's sweep literal bent by +4", bend_sweep,
             "lits", also_pass=("site", "tramp"))

        case("6 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "link_trade_sweep_negative_test")


if __name__ == "__main__":
    sys.exit(main())
