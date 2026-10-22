#!/usr/bin/env python3
"""Negative test for the verify_artifacts.py checks of the new-game Exp. Share
(CM on or off; user, 2026-10-21): NewGameInitData's last BL -> CheckHeap+24
trampoline -> CM_NewGameExpShare (src/exp_share.c).

Each case breaks a COPY of the built ROM in one way and requires the matching
check to report FAIL BY NAME; the other built-ROM checks of this hook must stay PASS.

  1. control                                        -- every check passes
  2. NewGameInitData's BL restored                  -- the hook is gone
  3. the trampoline aimed 2 bytes into the function -- skips its push
  4. the function made CM-gated (0x906 -> 0x18FE)   -- CM-off players get nothing
  5. control again                                  -- nothing left behind

THE ROM IS NEVER MODIFIED IN PLACE.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_cases  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "radicalred_cm.gba")

CHECKS = {
    "site": "built: NewGameInitData calls the CheckHeap+24 trampoline",
    "tramp": "new-game trampoline is ldr r3,[pc]; bx r3 -> CM_NewGameExpShare",
    "fn": "with NO Character Mode test",
}
SITE = 0x054B3E
TRAMP = 0x2C04


def _child_env():
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path):
    src = open(VERIFY, encoding="utf-8").read()
    src = src.replace('ROM_OUT = ROOT / "build" / "radicalred_cm.gba"',
                      'ROM_OUT = Path(%r)' % rom_path, 1)
    path = os.path.join(HERE, "_negtest_verify_ngxs.%d.py" % os.getpid())  # gitignored
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
EXPECT_CASES = 5


def _bl(src, dst):
    off = dst - (src + 4)
    imm = (off >> 1) & 0x3FFFFF
    return ((0xF000 | (imm >> 11)) | ((0xF800 | (imm & 0x7FF)) << 16)).to_bytes(4, "little")


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    out = subprocess.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", "exp_share.elf")],
                         check=True, capture_output=True, text=True).stdout
    fn = int(re.search(r"^([0-9a-f]+) T CM_NewGameExpShare$", out, re.M).group(1), 16)
    end = bytes(good).find(b"\xff" * 16, fn - 0x08000000)
    lit = bytes(good[fn - 0x08000000:end]).find((0x906).to_bytes(4, "little"))
    assert lit > 0 and (fn + lit) % 4 == 0, "0x906 literal not found in CM_NewGameExpShare"
    lit += fn - 0x08000000
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
            _rc, out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "PASS") for k in CHECKS)
                detail = "every new-game Exp. Share check passes"
            else:
                ok = _hit(out, want_fail, "FAIL")
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in CHECKS:
                    if k != want_fail and not _hit(out, k, "PASS"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts, new-game Exp. Share (CM on or off)")
        case("1 control -- the real build", None, None)

        def restore(d):
            d[SITE:SITE + 4] = _bl(0x08000000 + SITE, 0x0815EE0C)
        case("2 NewGameInitData's BL restored", restore, "site")

        def skew(d):
            d[TRAMP + 4:TRAMP + 8] = (fn + 2 | 1).to_bytes(4, "little")
        case("3 the trampoline aimed 2 bytes into the function", skew, "tramp")

        def gate(d):
            d[lit:lit + 4] = (0x18FE).to_bytes(4, "little")
        case("4 the function's 0x906 literal made the CM flag 0x18FE", gate, "fn")

        case("5 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "newgame_exp_share_negative_test")


if __name__ == "__main__":
    sys.exit(main())
