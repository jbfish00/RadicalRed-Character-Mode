#!/usr/bin/env python3
"""Static check of the move "best version" edits (user 2026-11-23) in build/radicalred_cm.gba.

usage: python3 tools/tests/check_move_best.py [rom] [--no-tamper]
Pass = every applied row of tools/character_mode/move_changes.json reads its new value, no other byte of the move table
changed, and the applied/deferred counts equal the pinned EXPECT. Controls: a reverted edit, a stray table byte and the
unpatched base ROM must each fail the check."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import movepatch

BASE = ROOT / "rom" / "radicalred 4.1.gba"
TABLE = 0x11521D0                 # live gBattleMoves file offset (428 literal refs)
EXPECT = (538, 0)         # (applied, deferred), pinned 2026-11-23
SL = json.load((ROOT / "tools/character_mode/move_changes.json").open())
N = max(c["hack_move_id"] for c in SL["changes"])


def check(base, built):
    todo, deferred, _, _ = movepatch.plan(SL, "cfru")
    bad = movepatch.verify(base, built, SL, TABLE, "cfru", N)
    if (len(todo), len(deferred)) != EXPECT:
        bad.append(f"counts {len(todo)}/{len(deferred)} (want {EXPECT})")
    return bad, todo


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    built = bytearray(Path(a[0] if a else ROOT / "build" / "radicalred_cm.gba").read_bytes())
    base = BASE.read_bytes()
    bad, todo = check(base, built)
    for b in bad[:20]:
        print("FAIL", b)
    print(f"move edits checked: {len(todo)} applied, {len(bad)} failures (want 0)")
    rc = 1 if bad else 0
    if "--no-tamper" not in sys.argv:   # the controls always run (the suite runner passes no flags)
        c = todo[len(todo) // 2]
        off, _ = movepatch.LAYOUTS["cfru"]["fields"][c["field"]]
        t1 = bytearray(built); o = TABLE + 12 * c["hack_move_id"] + off; t1[o] = base[o]
        t2 = bytearray(built); t2[TABLE + 12 * 200 + 11] ^= 0x40
        ok = 0
        for name, t in [(f"an applied edit reverted ({c['move']} {c['field']})", t1), ("a stray move-table byte", t2),
                        ("the unpatched base ROM's table", bytearray(base))]:
            f = check(base, t)[0]
            print("caught" if f else "MISSED", name, len(f)); ok += bool(f)
        print(f"negative controls: {ok}/3")
        rc |= ok != 3
    sys.exit(rc)


if __name__ == "__main__":
    main()
