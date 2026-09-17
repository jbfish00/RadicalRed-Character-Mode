#!/usr/bin/env python3
"""Negative test for the PC-exit sweep checks in verify_artifacts.py.

The five checks added for the PC-exit hook (game_plans/rowe_parity.md
§13.24/§13.26c) are worth exactly what they FAIL on. So break the built ROM on
purpose, in each direction the hook can be wrong, and require the matching
check to report FAIL by name -- not merely that the run exits 1, because a
tampered ROM also breaks the BPS round-trip check and that would look like a
catch while proving nothing about these five.

  1. control                    -- the real build passes all five
  2. the goto operand bent      -- the hatch jumps to the wrong tail
  3. the splice reverted        -- the stock tail is back, so the hook is
                                   simply absent while everything else is fine
  4. the callnative target bent -- the tail calls something that is not the
                                   activation sweep (this is the one a "looks
                                   like a callnative" test cannot catch)
  5. the sweep moved BEFORE the -- ordering is load-bearing: run before the
     waitstate                     waitstate the sweep sees an egg, and the
                                   egg exemption then keeps the hatchling
  6. control again

⚠️ The ROM is never modified in place. Each case writes a tampered COPY to a
temporary directory and runs a COPY of verify_artifacts.py pointed at it. The
base ROM under rom/ and the build under build/ are read-only here.
"""
import os
import re
import shutil
import struct
import subprocess
import sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from cm_tally import assert_cases
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "radicalred_cm.gba")

sys.path.insert(0, os.path.join(ROOT, "tools", "character_mode"))
import pc_hook  # noqa: E402

PC_TAIL_OFF = 0x08C8F100 - 0x08000000

CHECKS = {
    # ⚠️ Substrings, not full check names -- the wording differs between ports
    # and matching a whole sentence made the egg version of this test report
    # three MISSES including the control, which is the signature of a broken
    # harness rather than a broken checker.
    "goto": "overlaid with `goto <PC tail>`",
    "shape": "PC tail replays special/waitstate",
    "sweep": "native IS the activation sweep",
}


def _child_env():
    """Environment for a spawned checker, with the tally overrides STRIPPED.

    ⚠️ MEASURED 2026-09-17: subprocess inherits the environment, so running a
    negative test with CM_EXPECT_CHECKS set (as checker_guard_test.sh does to
    checkers) pinned the CHILD to that number too -- and the negative test's
    own CONTROL case, which must see the checker pass on its real literal,
    failed for a reason that had nothing to do with the tamper. A control that
    can be broken by an inherited variable is not a control.
    """
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path, tmp):
    """Run verify_artifacts against `rom_path`; return (rc, stdout)."""
    src = open(VERIFY, encoding="utf-8").read()
    src = src.replace('ROM_OUT = ROOT / "build" / "radicalred_cm.gba"',
                      'ROM_OUT = Path(%r)' % rom_path, 1)
    # ⚠️ The copy must live in tools/tests/, not in the temp directory:
    # verify_artifacts.py resolves the repo root from its OWN __file__, so a
    # copy run from /tmp looks for rom/ and build/ beside /tmp and every check
    # fails for a reason that has nothing to do with the tamper. That is what
    # this test hit on its first run -- all six cases MISSED, control included,
    # which is the signature of a broken harness rather than a broken checker.
    path = os.path.join(HERE, "_negtest_verify_pc.py")
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


def failed(out, key):
    """True if the named check reported FAIL in this run."""
    for line in out.splitlines():
        if line.strip().startswith("[FAIL]") and CHECKS[key] in line:
            return True
    return False


def passed(out, key):
    for line in out.splitlines():
        if line.strip().startswith("[PASS]") and CHECKS[key] in line:
            return True
    return False


# How many tamper cases this negative test must run. A deliberate
# LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 6


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM at %s -- run the injector first"
              % os.path.relpath(BUILT, ROOT))
        return 0
    good = bytearray(open(BUILT, "rb").read())
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append("%s: TAMPER CHANGED NOTHING" % name)
                    return
            rom = os.path.join(tmp, "tampered.gba")
            open(rom, "wb").write(bytes(data))
            _rc, out = run(rom, tmp)
            if want_fail is None:
                ok = all(passed(out, k) for k in CHECKS)
                detail = "all five PC checks pass"
            else:
                ok = failed(out, want_fail)
                detail = "%r reported FAIL" % CHECKS[want_fail]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: the PC-exit sweep checks")
        case("1 control -- the real build", None, None)

        def bend_goto(d):
            struct.pack_into("<I", d, pc_hook.SPLICE_FILE_OFF + 1, 0x08C8F900)
        case("2 the goto operand bent to another address", bend_goto, "goto")

        def revert(d):
            o = pc_hook.SPLICE_FILE_OFF
            d[o:o + len(pc_hook.SPLICE_ORIG)] = pc_hook.SPLICE_ORIG
        case("3 the splice reverted (the hook simply absent)", revert, "goto")

        def bend_native(d):
            # A plausible-looking callnative that is NOT the sweep. This is the
            # one a "looks like a callnative" test cannot catch.
            struct.pack_into("<I", d, PC_TAIL_OFF + 5, 0x08C80201)
        case("4 the callnative target bent off the sweep", bend_native, "sweep")

        def reorder(d):
            # Sweep BEFORE the special/waitstate: same bytes, same length, and
            # every "is there a callnative" test still passes -- but the sweep
            # would run before the storage UI opens, seeing the party the player
            # walked IN with. A silent no-op.
            o = PC_TAIL_OFF
            d[o:o + 9] = (bytes([0x23]) + d[o + 5:o + 9]
                          + bytes([0x25]) + d[o + 1:o + 3] + bytes([0x27]))
        case("5 the sweep moved BEFORE the PC's waitstate", reorder, "shape")

        case("6 control again", None, None)

    print("\n%d/6 negative cases behaved" % passes)
    if fails:
        print("MISSED: " + "; ".join(fails))
        return 1
    print("ALL PASS")
    if assert_cases(passes + len(fails), EXPECT_CASES, 'pc_hook'):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
