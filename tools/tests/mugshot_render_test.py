#!/usr/bin/env python3
"""Live render test for the character mugshot (Phase 3 render surface).

The other layers prove the data is correct and the bytecode is well-formed.
This one proves something is actually on screen: it boots the real ROM in
mgba-headless, runs a real selection handler through the real script
interpreter, and then walks gSprites looking for a sprite whose template
pointer is our own. Pass/fail is that memory assertion -- the screenshots it
leaves in /tmp are evidence for a human, not the test.

Characters are chosen to cover the cases that fail differently:
  - three different donor sets, so a hardcoded "always draws the same art" bug
    cannot pass
  - one character with no staged front pic, which must render nothing and still
    complete the selection normally

Prerequisites (both built automatically if missing):
  build/radicalred_cm.gba        python3 tools/inject_character_mode.py
  /tmp/rr_ss_bedroom.ss          mk_checkpoint_bedroom.lua on the test ROM

Run: python3 tools/tests/mugshot_render_test.py
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
MGBA = ROOT.parent / "Seaglass-Character-Mode" / "tools" / "mgba_src" / "build" / "mgba-headless"
TEST_ROM = BUILD / "radicalred_cm_mugshot_test.gba"
STATE = Path("/tmp/rr_ss_bedroom.ss")

# (character name, has staged front pic). Names, not indices: indices shift
# every time the roster changes, and a stale index would silently test the
# wrong character rather than erroring.
CASES = [
    ("Red", True),        # rogue/     -- the reference case
    ("Jessie", True),     # pokesho/   -- a different donor set entirely
    ("Cynthia", True),    # rogue/     -- far down the table, not index 0
    ("Ash", False),       # no front pic staged -> must draw nothing, cleanly
]


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def template_addr():
    """sMugshotTemplate's ROM address, read from the linked ELF."""
    out = sh(["arm-none-eabi-nm", str(BUILD / "character_sprite.elf")]).stdout
    m = re.search(r"^([0-9a-f]+) [tT] sMugshotTemplate$", out, re.M)
    assert m, f"sMugshotTemplate not in the ELF:\n{out}"
    return int(m.group(1), 16)


def main():
    if not MGBA.is_file():
        print(f"SKIP: mgba-headless not found at {MGBA}")
        return 0
    if not (BUILD / "radicalred_cm.gba").is_file():
        print("building ROM first...")
        sh([sys.executable, "tools/inject_character_mode.py"], check=True)

    manifest = json.loads((ROOT / "tools" / "character_mode" /
                           "characters_manifest.json").read_text())["characters"]
    chars = [c["character"] for c in manifest]
    tmpl = template_addr()
    print(f"sMugshotTemplate @ {tmpl:#x}")

    failures = []
    for name, expect_sprite in CASES:
        assert name in chars, f"{name} is no longer in the roster -- update CASES"
        idx = chars.index(name)
        assert not manifest[idx].get("hidden"), \
            f"{name} is now hidden below the threshold and has no handler -- update CASES"
        # The fixture builder takes the NAME and resolves the chain slot itself;
        # the chain skips hidden characters, so slot != table index.
        sh([sys.executable, "tools/tests/build_mugshot_testrom.py", name]).check_returncode()

        if not STATE.is_file():
            print("making the bedroom checkpoint (this drives the whole intro)...")
            sh([str(MGBA), "--script", "tools/mgba_scripts/mk_checkpoint_bedroom.lua",
                str(TEST_ROM)], timeout=900)
            assert STATE.is_file(), "checkpoint script did not produce the savestate"

        env = dict(os.environ,
                   CM_TEMPLATE_ADDR=hex(tmpl),
                   CM_CHAR_ID=str(idx + 1),
                   CM_EXPECT_SPRITE="1" if expect_sprite else "0",
                   CM_SHOT_PREFIX=f"/tmp/rr_mugshot_{name.lower()}")
        r = subprocess.run([str(MGBA), "--script", "tools/mgba_scripts/mugshot_shot.lua",
                            str(TEST_ROM)], cwd=ROOT, capture_output=True, text=True,
                           env=env, timeout=600)
        log = [l.split("HARNESS ", 1)[1] for l in r.stdout.splitlines() if "HARNESS " in l]
        ok = any(l.startswith("RESULT: PASS") for l in log)
        art = "with art" if expect_sprite else "no art staged"
        print(f"\n=== {name} (index {idx}, {art}) ===")
        for l in log:
            if l.startswith(("PASS", "FAIL", "mugshot OBJ")):
                print("  " + l)
        if not ok:
            failures.append(name)
            print("  " + "\n  ".join(l for l in log if l.startswith("FAIL")) or "  no RESULT line")

    print(f"\n{len(CASES) - len(failures)}/{len(CASES)} characters rendered as expected")
    if failures:
        print("FAILURES: " + ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
