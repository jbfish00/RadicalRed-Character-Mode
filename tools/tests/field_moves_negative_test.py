#!/usr/bin/env python3
"""Negative test for verify_artifacts.py section 20 -- field moves
(src/field_moves.c; ../game_plans/field_moves.md), 2026-10-07.

Each case breaks a COPY of the built ROM in one way the hooks could be wrong
and requires the matching check to report FAIL BY NAME; the other built-ROM
section-20 checks must stay PASS, proving the tamper was precise.

  1. control                              -- every section-20 check passes
  2. CFRU's site left calling vanilla     -- CanMonLearnTMTutor directly
  3. CFRU's site aimed into the hook      -- CM_FieldMoveCanLearn + 4
  4. checkpartymove left calling vanilla  -- MonKnowsMove directly
  5. checkpartymove aimed at CheckHeap+8  -- the link-trade trampoline, a REAL
                                             neighbour: the plausible-wrong shape
  6. the trampoline aimed elsewhere       -- at CM_FieldMoveCanLearn, a real entry
  7. the hook's fallback literal bent     -- CanMonLearnTMTutor|1 + 4
  8. control again                        -- proves 2-7 left nothing behind

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
FIELD_TRAMP = GUARD_TRAMP + 16
LEARN_SITE = _inj("FIELD_CANLEARN_BL_SITE")
KNOWS_SITE = _inj("FIELD_KNOWS_BL_SITE")
CAN_LEARN = _inj("CAN_MON_LEARN_TM_TUTOR")
KNOWS = _inj("MON_KNOWS_MOVE")
FIELD = _inj("FIELD_MOVES_ADDR") - 0x08000000


def _nm(elf):
    out = subprocess.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", elf)],
                         check=True, capture_output=True, text=True).stdout
    return {m.group(2): int(m.group(1), 16)
            for m in re.finditer(r"^([0-9a-f]+) [Tt] (\w+)$", out, re.M)}


def thumb_bl(src, dst):
    off = ((dst - (src + 4)) >> 1) & 0x3FFFFF
    return struct.pack("<HH", 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


CHECKS = {
    "learn": "built: the field-potential site calls CM_FieldMoveCanLearn",
    "knows": "built: checkpartymove calls the CheckHeap+16 trampoline",
    "tramp": "field trampoline is ldr r3,[pc]; bx r3 -> CM_FieldMoveKnows",
    "lits": "compiled field hooks (read from the ROM) carry CanMonLearnTMTutor",
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
    path = os.path.join(HERE, "_negtest_verify_fieldmoves.%d.py" % os.getpid())  # unique per run; gitignored
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
EXPECT_CASES = 8


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    sym = _nm("field_moves.elf")
    learn = sym["CM_FieldMoveCanLearn"]
    fails, passes = [], 0
    others = lambda k: tuple(x for x in CHECKS if x != k)  # noqa: E731

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
                detail = "every section-20 check passes"
            else:
                ok = _hit(out, want_fail, "FAIL") and _rc != 0
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in others(want_fail):
                    if not _hit(out, k, "PASS"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts section 20, field moves")
        case("1 control -- the real build", None, None)

        def learn_vanilla(d):
            d[LEARN_SITE:LEARN_SITE + 4] = thumb_bl(0x08000000 + LEARN_SITE, CAN_LEARN)
        case("2 CFRU's site still calls CanMonLearnTMTutor", learn_vanilla, "learn")

        def learn_mid(d):
            d[LEARN_SITE:LEARN_SITE + 4] = thumb_bl(0x08000000 + LEARN_SITE, learn + 4)
        case("3 CFRU's site aimed into the middle of the hook", learn_mid, "learn")

        def knows_vanilla(d):
            d[KNOWS_SITE:KNOWS_SITE + 4] = thumb_bl(0x08000000 + KNOWS_SITE, KNOWS)
        case("4 checkpartymove still calls MonKnowsMove", knows_vanilla, "knows")

        def knows_link(d):
            d[KNOWS_SITE:KNOWS_SITE + 4] = thumb_bl(0x08000000 + KNOWS_SITE, LINK_TRAMP)
        case("5 checkpartymove aimed at the link-trade trampoline", knows_link, "knows")

        def tramp_elsewhere(d):
            struct.pack_into("<I", d, FIELD_TRAMP - 0x08000000 + 4, learn | 1)
        case("6 the trampoline aimed at CM_FieldMoveCanLearn", tramp_elsewhere, "tramp")

        def bend_fallback(d):
            code = bytes(d[FIELD:FIELD + 0x400])
            ks = [k for k in range(0, len(code) - 3, 4)
                  if struct.unpack_from("<I", code, k)[0] == CAN_LEARN | 1]
            assert len(ks) == 1, f"fallback literal found {len(ks)} times -- re-derive"
            struct.pack_into("<I", d, FIELD + ks[0], (CAN_LEARN | 1) + 4)
        case("7 the hook's CanMonLearnTMTutor literal bent by +4", bend_fallback, "lits")

        case("8 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "field_moves_negative_test")


if __name__ == "__main__":
    sys.exit(main())
