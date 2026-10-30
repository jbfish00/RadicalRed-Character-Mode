#!/usr/bin/env python3
"""Negative test for verify_artifacts.py's four EXP rate checks (2026-10-29, src/exp_rate.c).

Each case breaks a COPY of the built ROM in one way and requires the matching check to report FAIL BY NAME; the
other EXP rate checks must stay PASS.

  1. control                                     -- every check passes
  2. getexp's MathMin BL restored                -- the rate is never applied
  3. the exit-append BL restored                 -- no Exp Rate row
  4. CanSetUpSecondaryStartMenu restored         -- the page needs the Dexnav flag again
  5. the callback load back to ldr #64           -- every row would call its neighbour's callback
  6. row 13's callback pointed at Exit           -- the row closes the menu instead
  7. control again                               -- nothing left behind

THE ROM IS NEVER MODIFIED IN PLACE.
"""
import os
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
BASE = os.path.join(ROOT, "rom", "radicalred 4.1.gba")

CHECKS = {
    "min": "EXP rate: atk23_getexp's MathMin BL",
    "row": "EXP rate: SetUpStartMenu's shared exit append BL",
    "block": "EXP rate: START block relocated",
    "script": "EXP rate: the row's script",
}

# A deliberate LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 7


def _child_env():
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path):
    src = open(VERIFY, encoding="utf-8").read()
    assert 'ROM_OUT = ROOT / "build" / "radicalred_cm.gba"' in src
    src = src.replace('ROM_OUT = ROOT / "build" / "radicalred_cm.gba"', 'ROM_OUT = Path(%r)' % rom_path, 1)
    path = os.path.join(HERE, "_negtest_verify_exprate.%d.py" % os.getpid())  # gitignored
    open(path, "w", encoding="utf-8").write(src)
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=ROOT, env=_child_env())
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    return p.stdout + p.stderr


def _hit(out, key, marker):
    return any(line.strip().startswith("[%s]" % marker) and CHECKS[key] in line for line in out.splitlines())


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    base = open(BASE, "rb").read()
    fails, passes = [], 0
    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail):
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
            out = run(rom)
            ok = all(_hit(out, k, "FAIL" if k == want_fail else "PASS") for k in CHECKS)
            print("  [%s] %s" % ("PASS" if ok else "MISS", name))
            if ok:
                passes += 1
            else:
                fails.append(name)

        def restore(a, n):
            def f(d):
                d[a:a + n] = base[a:a + n]
            return f

        def row13_exit(d):
            blk = struct.unpack_from("<I", d, 0x10BE158)[0] - 0x08000000
            struct.pack_into("<I", d, blk + 0x44 + 13 * 8, 0x0806F541)

        print("negative test: verify_artifacts EXP rate checks")
        case("1 control -- the real build", None, None)
        case("2 getexp's MathMin BL restored", restore(0x1094A82, 4), "min")
        case("3 the exit-append BL restored", restore(0x10BE1FC, 4), "row")
        case("4 CanSetUpSecondaryStartMenu restored", restore(0x10BDCEC, 4), "row")
        case("5 the callback load back to ldr #64", restore(0x10BE0D6, 2), "block")
        case("6 row 13's callback pointed at Exit", row13_exit, "block")
        case("7 control again", None, None)
    ran = passes + len(fails)
    if assert_cases(ran, EXPECT_CASES, "exprate_negative_test"):
        return 1
    print("%d/%d negative cases" % (passes, ran) + ("" if not fails else " -- MISSED: " + ", ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
