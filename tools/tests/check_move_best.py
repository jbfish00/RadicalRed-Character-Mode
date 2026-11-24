#!/usr/bin/env python3
"""Static check of the move "best version" edits (user 2026-11-23) in build/radicalred_cm.gba.

usage: python3 tools/tests/check_move_best.py [rom] [--no-tamper]
Pass = every applied row of tools/character_mode/move_changes.json reads its new value, no other byte of the move table
changed, and the applied/deferred counts equal the pinned EXPECT. Controls: a reverted edit, a stray table byte and the
unpatched base ROM must each fail the check.
Crit +2 (2026-11-24): both crit routines' CheckTableForMove(move, gHighCriticalChanceMoves) BLs go to CRIT_STUB_ADDR and
the stub there is byte for byte crit_stub(slice crit_list) (inject_character_mode.py). Controls: a BL back at
CheckTableForMove, a list id changed in the stub."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import movepatch
import struct
from inject_character_mode import thumb_bl, crit_stub, CRIT_BL_SITES, CRIT_STUB_ADDR, CHECK_TABLE_FOR_MOVE
STUB = crit_stub(CRIT_STUB_ADDR, json.load((ROOT / "tools/character_mode/move_changes.json").open())["crit_list"]["ids"])

BASE = ROOT / "rom" / "radicalred 4.1.gba"
TABLE = 0x11521D0                 # live gBattleMoves file offset (428 literal refs)
EXPECT = (538 + 34, 0)   # (applied, deferred), pinned 2026-11-23 (cheap + medium flags/target)
SL = json.load((ROOT / "tools/character_mode/move_changes.json").open())
N = max(c["hack_move_id"] for c in SL["changes"])


def check(base, built):
    todo, deferred, _, _ = movepatch.plan(SL, "cfru")
    bad = movepatch.verify(base, built, SL, TABLE, "cfru", N)
    for cs in CRIT_BL_SITES:
        if bytes(built[cs - 0x08000000:cs - 0x08000000 + 4]) != thumb_bl(cs, CRIT_STUB_ADDR):
            bad.append("crit: %#x is not BL -> the crit stub" % cs)
    so = CRIT_STUB_ADDR - 0x08000000
    if bytes(built[so:so + len(STUB)]) != STUB:
        bad.append("crit: the stub at %#x differs from crit_stub(crit_list)" % CRIT_STUB_ADDR)
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
        cm = next(x for x in todo if x.get("tier") == "medium" and x["field"] == "flags")   # a medium-tier row too
        t3 = bytearray(built); o = TABLE + 12 * cm["hack_move_id"] + movepatch.LAYOUTS["cfru"]["fields"]["flags"][0]; t3[o] = base[o]
        t4 = bytearray(built); cs = CRIT_BL_SITES[0] - 0x08000000
        t4[cs:cs + 4] = thumb_bl(CRIT_BL_SITES[0], CHECK_TABLE_FOR_MOVE)
        t5 = bytearray(built); t5[CRIT_STUB_ADDR - 0x08000000 + len(STUB) - 4] ^= 0x01     # a crit_list id
        ok = 0
        for name, t in [("crit: a BL back at CheckTableForMove", t4), ("crit: a list id changed", t5),
                        (f"an applied edit reverted ({c['move']} {c['field']})", t1), ("a stray move-table byte", t2),
                        ("the unpatched base ROM's table", bytearray(base)), (f"a medium flags edit reverted ({cm['move']})", t3)]:
            f = check(base, t)[0]
            print("caught" if f else "MISSED", name, len(f)); ok += bool(f)
        print(f"negative controls: {ok}/6")
        rc |= ok != 6
    sys.exit(rc)


if __name__ == "__main__":
    main()
