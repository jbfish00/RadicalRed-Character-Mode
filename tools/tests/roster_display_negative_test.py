#!/usr/bin/env python3
"""Negative test for verify_artifacts.py section 16 -- the roster display
(roots blob, header names, code, console pre-entry). 2026-09-27.

Ported from the Lazarus port's roster_display_negative_test.py. Each case
breaks a COPY of the built ROM in one way and requires the matching check to
report FAIL BY NAME (a tampered ROM also fails diff containment, so a bare exit
code proves nothing). Checks that must stay SILENT prove the tamper was
precise -- a checker that fails everything would "catch" every case.

⚠️ THE ROM IS NEVER MODIFIED IN PLACE.
"""
import json
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
CM = os.path.join(ROOT, "tools", "character_mode")
_INJ = open(os.path.join(ROOT, "tools", "inject_character_mode.py"), encoding="utf-8").read()


def inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+|\d+)", _INJ, re.M).group(1), 0)


ROOTS = inj("ROSTER_ROOTS_ADDR") - 0x08000000
NAMES = inj("ROSTER_NAMES_ADDR") - 0x08000000
NAME_STRIDE = inj("ROSTER_NAME_STRIDE")
CODE = inj("ROSTER_MENU_ADDR") - 0x08000000
SCRIPT = inj("ROSTER_SCRIPT_ADDR") - 0x08000000
ROOTS_ADDR = inj("ROSTER_ROOTS_ADDR")
CONSOLE_BG_PTR_OFF = inj("CONSOLE_BG_PTR_OFF")
CONSOLE_SCRIPT = inj("CONSOLE_SCRIPT")
_MAN = json.load(open(os.path.join(CM, "characters_manifest.json")))["characters"]
_RM = json.load(open(os.path.join(CM, "roster_roots_manifest.json")))
ESZ = _RM["entry_size_bytes"]
ROOTS_START = ROOTS + len(_MAN) * ESZ
SPECIES_NAMES, STRIDE = int(_RM["species_table_base"], 16), _RM["species_table_stride"]

CHECKS = {
    "entry": "and root slice re-derive from the manifest",
    "tile": "entries tile roots[] exactly",
    "name": "resolves to a non-empty name in the BUILT ROM",
    "late": "late probe: character #",
    "empty": "characters with zero roots in-ROM ==",
    "header": "every header name in-ROM decodes",
    "code": "roster code in-ROM == roster_display.bin",
    "consts": "compiled code carries the roots blob",
    "console": "console BG ptr -> pre-entry",
    "pre": "pre-entry: CM off -> stock",
    "prompt": "its prompt reads",
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
    path = os.path.join(HERE, "_negtest_verify_roster.%d.py" % os.getpid())  # unique per run; gitignored
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
    return any(line.strip().startswith(marker) and CHECKS[key] in line
               for line in out.splitlines())


def fc(d, ci):
    return struct.unpack_from("<HH", d, ROOTS + ci * ESZ)


EXPECT_CASES = 13


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    late = len(_MAN) - 1
    big = max(ci for ci in range(len(_MAN)) if fc(good, ci)[1] >= 4)
    # A real species SLOT with no name, measured in this ROM (not assumed).
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail, also_pass=()):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append("%s: TAMPER CHANGED NOTHING" % name)
                    print("  [MISS] %s -- TAMPER CHANGED NOTHING" % name)
                    return
            rom = os.path.join(tmp, "tampered.gba")
            open(rom, "wb").write(bytes(data))
            _rc, out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "[PASS]") for k in CHECKS)
                detail = "every section-16 check passes"
            else:
                wants = want_fail if isinstance(want_fail, tuple) else (want_fail,)
                ok = all(_hit(out, k, "[FAIL]") for k in wants)
                detail = " and ".join("%r reported FAIL" % CHECKS[k] for k in wants)
                for k in also_pass:
                    if not _hit(out, k, "[PASS]"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts section 16, roster display")
        case("1 control -- the real build", None, None)

        def blank_name(d):
            # RR's table has no nameless slot to point a root at, so blank the
            # root's OWN name in the copy (the check reads the BUILT ROM's table).
            f, _c = fc(d, big)
            sp, = struct.unpack_from("<H", d, ROOTS_START + f * 2)
            d[SPECIES_NAMES + sp * STRIDE] = 0xFF
        case("2 a root's species name blanked in the built ROM", blank_name, "name",
             also_pass=("entry",))

        def bend_first(d):
            f, c = fc(d, big)
            struct.pack_into("<HH", d, ROOTS + big * ESZ, f + 1, c)
        case("3 a first_root bent into another character's roots (real names)",
             bend_first, "entry", also_pass=("name",))

        def bend_last(d):
            f, c = fc(d, late)
            struct.pack_into("<HH", d, ROOTS + late * ESZ, f, c + 1)
        case("4 the last character's count bent -- roots no longer tile", bend_last, "tile")

        def bend_late(d):
            f, c = fc(d, late)
            if c == 0:      # the last character may be empty: bend the nearest non-empty one
                return
            cur, = struct.unpack_from("<H", d, ROOTS_START + f * 2)
            struct.pack_into("<H", d, ROOTS_START + f * 2, 25 if cur != 25 else 26)
        if fc(good, late)[1]:
            case("5 the LATE probe's own roots bent", bend_late, "late")
        else:
            case("5 the LATE probe's count bent (character #%d is empty)" % (late + 1),
                 bend_last, "late")

        def zero_count(d):
            f, _c = fc(d, big)
            struct.pack_into("<HH", d, ROOTS + big * ESZ, f, 0)
        case("6 a count zeroed -- an empty roster appears", zero_count, "empty")

        def bend_header(d):
            d[NAMES + 9 * NAME_STRIDE] ^= 0x01          # character #10's first letter
        case("7 a header name byte bent", bend_header, "header", also_pass=("entry", "code"))

        def bend_code(d):
            d[CODE + 8] ^= 1
        case("8 roster code bent", bend_code, "code", also_pass=("pre", "header"))

        def bend_roots_lit(d):
            for i in range(CODE, CODE + 0x400, 4):
                if struct.unpack_from("<I", d, i)[0] == ROOTS_ADDR:
                    struct.pack_into("<I", d, i, ROOTS_ADDR + 4)
        case("9 compiled roots literal one entry off", bend_roots_lit, "consts",
             also_pass=("pre", "console"))

        def revert_console(d):
            struct.pack_into("<I", d, CONSOLE_BG_PTR_OFF, CONSOLE_SCRIPT)
        case("10 console BG pointer left on the stock script", revert_console, "console",
             also_pass=("pre", "prompt"))

        def bend_callnative(d):
            o = SCRIPT + 31                             # callnative operand (0x23 at +30)
            assert d[o - 1] == 0x23, "re-derive the callnative offset"
            struct.pack_into("<I", d, o, struct.unpack_from("<I", d, o)[0] + 2)
        case("11 pre-entry callnative aimed 2 B past CM_RosterOpen", bend_callnative, "pre",
             also_pass=("console", "prompt"))

        def bend_prompt(d):
            q = struct.unpack_from("<I", d, SCRIPT + 12)[0] - 0x08000000
            d[q] ^= 0x01
        case("12 prompt text bent", bend_prompt, "prompt", also_pass=("pre", "console"))

        case("13 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "roster_display_negative_test")


if __name__ == "__main__":
    sys.exit(main())
