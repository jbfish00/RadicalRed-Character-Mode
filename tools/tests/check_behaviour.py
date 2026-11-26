#!/usr/bin/env python3
"""Behaviour cards, CFRU binaries (Radical Red, Unbound): compiled-ROM checker, 2026-11-26.

Master copy: game_plans/move_ability_best_2026-11-22/behaviour_all/gba/check_behaviour_cfru.py; each repo keeps a copy as
tools/tests/check_behaviour.py. It reads the built ROM (not the card file) and decodes what each card does:
  1. bpatch.verify: every card edit reads "to" in the shipped ROM and "from" in the CM_NO_BEHAVIOUR control, and the two
     ROMs differ nowhere else;
  2. one decoder per card, written against the instructions/data themselves (a move list parsed through its literals, a
     script followed through its goto, a branch target computed from its encoding);
  3. controls: the control ROM must fail every decoder; one tamper per decoder must fail that decoder; a pass with zero
     decoders is a failure (pinned count).
usage: check_behaviour.py [shipped.gba] [control.gba]   (defaults: this repo's build/ outputs)
"""
import sys, os, json, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import bpatch  # noqa: E402

GBA = 0x08000000
CARDS = bpatch.load(ROOT / "tools" / "character_mode" / "behaviour_cards.json")
HACK = CARDS["hack"]
OUT = {"radicalred": ("radicalred_cm.gba", "radicalred_cm_nobeh.gba"), "unbound": ("unbound-cm.gba", "unbound-cm_nobeh.gba")}
EXPECT = {"radicalred": 13, "unbound": 15}
G_BATTLE_MOVE_DAMAGE = 0x02023D50


def u8(r, a): return r[a - GBA]
def u16(r, a): return struct.unpack_from("<H", r, a - GBA)[0]
def u32(r, a): return struct.unpack_from("<I", r, a - GBA)[0]


def b_target(r, a):
    h = u16(r, a)
    assert (h & 0xF800) == 0xE000, "not a b.n at %#x" % a
    off = (h & 0x7FF) << 1
    if off & 0x800:
        off -= 0x1000
    return a + 4 + off


def movelist(r, a, limit=64):
    out = []
    while len(out) < limit:
        v = u16(r, a + 2 * len(out))
        if v == 0xFEFE:
            return out
        out.append(v)
    raise AssertionError("no 0xFEFE terminator at %#x" % a)


# ---------------------------------------------------------------- Unbound -------------------------------------------
UB_FLAGS = 0x08A7E266


def ub_bit(r, move, bit):
    return (u8(r, UB_FLAGS + 7 * move + bit // 8) >> (bit % 8)) & 1


def ub_checks():
    c = {}
    c["Double-Edge (Gen I)"] = lambda r: ub_bit(r, 0x26, 39) == 1 and ub_bit(r, 0x26, 40) == 0 and ub_bit(r, 0x26, 41) == 0
    for n, m in (("Astonish (Gen III)", 0x136), ("Extrasensory (Gen III)", 0x146), ("Needle Arm (Gen III)", 0x12E),
                 ("Phantom Force (Gen VI)", 0x1E9)):
        c[n] = (lambda m: lambda r: ub_bit(r, m, 30) == 1)(m)
    # MoveIgnoresSubstitutes: the sound-bit test's bmi is gone, the Infiltrator compare still follows
    c["Substitute (Gen II-V)"] = lambda r: u16(r, 0x089C044E) == 0x06A0 and u16(r, 0x089C0450) == 0x46C0 \
        and u16(r, 0x089C0452) == 0x2966
    c["Protect / Detect / Endure (Gen IV)"] = lambda r: u16(r, 0x089ED314) == 0x2B03 and u16(r, 0x089ED3A6) == 0x2202 \
        and u16(r, 0x089ED3AA) == 0x4351
    c["Parental Bond (Gen VI)"] = lambda r: u16(r, 0x089D27EA) == 0x2B20 and u16(r, 0x089D27EE) == 0x086D
    c["High Jump Kick / Jump Kick (Gen I)"] = lambda r: crash_ok(r, 0x089684EA)
    c["Intimidate (Gen VII)"] = lambda r: u32(r, 0x089A96C8) == 0x47702000
    round2(c, "unbound")
    return c


# ---------------------------------------------------------------- Radical Red ---------------------------------------
def rr_checks():
    c = {}
    lits33 = (0x09073BF8, 0x09081058, 0x090CB5B8)

    def double_edge(r):
        ok = True
        for l in lits33:
            r25, r33 = movelist(r, u32(r, l - 4)), movelist(r, u32(r, l))
            ok &= 0x26 in r25 and 0x26 not in r33 and 0x24 in r25 and 0x169 in r33
        return ok
    c["Double-Edge (Gen I)"] = double_edge

    def minimize(r):
        want = {0x136, 0x146, 0x12E, 0x1E9, 0x17, 0x22}
        return all(want <= set(movelist(r, u32(r, l))) for l in (0x09060C14, 0x090866E0))
    c["Astonish (Gen III)"] = minimize
    c["Substitute (Gen II-V)"] = lambda r: u16(r, 0x09074678) == 0x2800 and u16(r, 0x0907467A) == 0x46C0 \
        and u16(r, 0x0907467C) == 0x2D66
    c["Protect / Detect / Endure (Gen IV)"] = lambda r: u16(r, 0x0909F9BC) == 0x2B03 and u16(r, 0x0909FA66) == 0x2202 \
        and u16(r, 0x0909FA6A) == 0x4351

    def ate(r):
        t = b_target(r, 0x0908558A)              # after `bl AbilityCanChangeTypeAndBoost`
        if not (u16(r, t) == 0x2800 and (u16(r, t + 2) & 0xFF00) == 0xD100):
            return False
        hit = t + 2 + 4 + (((u16(r, t + 2) & 0xFF) ^ 0x80) - 0x80) * 2  # bne target (the bne is at t+2)
        return u16(r, hit) == 0x230D                                  # movs r3,#13 -> x13/10
    c["Aerilate / Pixilate / Refrigerate (Gen VI)"] = ate
    c["Parental Bond (Gen VI)"] = lambda r: u16(r, 0x09086A80) == 0x2B20 and u16(r, 0x09086AC8) == 0x085B
    c["High Jump Kick / Jump Kick (Gen I)"] = lambda r: crash_ok(r, 0x09004429)
    c["Gale Wings (Gen VI)"] = lambda r: u16(r, 0x0906F084) == 0x429A and u16(r, 0x0906F086) == 0x46C0 \
        and u16(r, 0x0906F122) == 0x4287 and u16(r, 0x0906F124) == 0x46C0
    round2(c, "radicalred")
    return c


# ---------------------------------------------------------------- round 2 (both) -----------------------------------
R2 = {"unbound": dict(heal=(0x089EFBBC, 0x089EFC0E, 0x089EFC5E), leaf=0x089EDB42, ps=0x0896964D, db=0x089EF96A,
                      dis=0x089EAFBC),
      "radicalred": dict(heal=(0x090A20C2, 0x090A2116, 0x090A2166), leaf=0x090A0284, ps=0x090056FD, db=0x090A1E8A,
                         dis=0x0909D8E4)}


def round2(c, h):
    a = R2[h]
    # healpartystatus: each `cmp rX,#43 (Soundproof)` is followed by a nop instead of the beq that skips the cure
    c["Heal Bell / Soundproof (Gen V)"] = lambda r: all((u16(r, x) & 0xF8FF) == 0x282B and u16(r, x + 2) == 0x46C0
                                                        for x in a["heal"])
    # trysetrest: `cmp #203` no longer branches; the next compare (#231) and its default arm follow
    c["Leaf Guard (Gen IV)"] = lambda r: (u16(r, a["leaf"]) & 0xF8FF) == 0x28CB and u16(r, a["leaf"] + 2) == 0x46C0 \
        and (u16(r, a["leaf"] + 4) & 0xF8FF) == 0x28E7
    # CheckPartingShotFail: jumpifbyte EQUALS ANIM_TARGETS_HIT <v> BS_MOVE_END with v outside {0, 1}
    c["Parting Shot (Gen VI)"] = lambda r: r[a["ps"] - GBA:a["ps"] + 6 - GBA] == bytes.fromhex("2900dd3f0202") \
        and u8(r, a["ps"] + 6) not in (0, 1) and u8(r, a["ps"] + 11) == 0x2E
    # setdestinybond: after `cmp r3,#0` an unconditional branch to the arm that sets the counter (movs r3,#2)
    c["Destiny Bond (Gen III-VI)"] = lambda r: u16(r, a["db"]) == 0x2B00 and (u16(r, a["db"] + 2) & 0xF800) == 0xE000 \
        and u16(r, b_target(r, a["db"] + 2)) == 0x2302
    # datahpupdate Disguise arm: the HP/8 shift is a movs rD,#0
    c["Disguise (Gen VII)"] = lambda r: (u16(r, a["dis"]) & 0xF8FF) == 0x2014 and u16(r, a["dis"] + 2) in (0x2000, 0x2300)


def crash_ok(r, site):
    """HighJumpKickMiss: `goto S` where S = setword gBattleMoveDamage 1; goto site+5 (graphicalhpupdate attacker)."""
    if u8(r, site) != 0x28:
        return False
    s = u32(r, site + 1)
    if not (GBA <= s < GBA + len(r)):
        return False
    return u8(r, s) == 0xFA and u32(r, s + 1) == G_BATTLE_MOVE_DAMAGE and u32(r, s + 5) == 1 \
        and u8(r, s + 9) == 0x28 and u32(r, s + 10) == site + 5 and r[site + 5 - GBA:site + 7 - GBA] == b"\x0b\x01"


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    ship_n, ctl_n = OUT[HACK]
    shipped = bytearray(Path(a[0] if a else ROOT / "build" / ship_n).read_bytes())
    control = bytearray(Path(a[1] if len(a) > 1 else ROOT / "build" / ctl_n).read_bytes())
    checks = ub_checks() if HACK == "unbound" else rr_checks()
    fails = []
    bad = bpatch.verify(shipped, control, CARDS)
    print(("PASS" if not bad else "FAIL"), "bpatch.verify: %d edits, shipped vs control" % len(CARDS["edits"]))
    fails += bad[:5]
    card_names = []
    for e in CARDS["edits"]:
        if e["card"] not in card_names:
            card_names.append(e["card"])
    for n in card_names:
        if n not in checks:
            fails.append("card %s has no decoder" % n)
    for n, f in checks.items():
        ok = bool(f(shipped))
        print(("PASS" if ok else "FAIL"), n)
        if not ok:
            fails.append(n)
    # controls
    ctl_bad = [n for n, f in checks.items() if f(control)]
    print("control (CM_NO_BEHAVIOUR) fails every decoder: %d/%d" % (len(checks) - len(ctl_bad), len(checks)))
    if ctl_bad:
        fails.append("control passes " + ", ".join(ctl_bad))
    tam = 0
    for n, f in checks.items():
        edits = [e for e in CARDS["edits"] if e["card"] == n] or [e for e in CARDS["edits"] if n.split(" (")[0] in e["card"]]
        caught = False
        for e in edits:                                   # tamper: restore one edit's first CHANGED byte from the control
            f_, t_ = bytes.fromhex(e["from"]), bytes.fromhex(e["to"])
            o = int(e["addr"], 16) - GBA + next(k for k in range(len(f_)) if f_[k] != t_[k])
            t = bytearray(shipped)
            t[o] = control[o]
            if not f(t):
                caught = True
                break
        tam += caught
        if not caught:
            fails.append("tamper of %s not caught" % n)
    print("tampers caught: %d/%d" % (tam, len(checks)))
    if len(checks) != EXPECT[HACK]:
        fails.append("decoder count %d, want %d" % (len(checks), EXPECT[HACK]))
    print("decoders %d (want %d)" % (len(checks), EXPECT[HACK]))
    print("ALL PASS" if not fails else "FAILURES: " + "; ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
