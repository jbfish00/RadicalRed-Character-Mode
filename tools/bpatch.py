"""Behaviour-card ROM patcher for the closed GBA binaries (move/ability "best version", item 1; 2026-11-25).

Master copy: game_plans/move_ability_best_2026-11-22/behaviour_all/gba/bpatch.py. Each repo/kit keeps a copy next to its
build script and its own card list as tools/character_mode/behaviour_cards.json (written by the workspace generator
behaviour_all/gba/make_<engine>.py, which finds every site by byte pattern in the BASE rom and asserts it is unique).

Card file: {"hack", "engine", "edits": [{"card", "kind", "addr" ("0x08......"), "from" (hex), "to" (hex), "why"}]}
kind is one of data / imm / inplace / repoint / script / hook / blob (blob = new bytes in free space; its "from" is the
free-space bytes it replaces).

apply(rom, cards) writes every edit after asserting the bytes it replaces (a wrong address or a hack that differs from
the generator's base fails the build instead of writing garbage). It refuses overlapping edits.
verify(shipped, control, cards) is the static check: every edit reads "to" in the shipped ROM and "from" in the control
(CM_NO_BEHAVIOUR=1) ROM, and the two ROMs differ nowhere else. Returns a list of failures (empty = pass).
"""
import json

GBA = 0x08000000


def _edits(cards):
    out = []
    for e in cards["edits"]:
        a = int(e["addr"], 16) - GBA
        f, t = bytes.fromhex(e["from"]), bytes.fromhex(e["to"])
        assert len(f) == len(t) and f != t, "edit %s at %s: from/to sizes differ or equal" % (e["card"], e["addr"])
        out.append((a, f, t, e))
    out.sort(key=lambda x: x[0])
    for (a1, f1, _, e1), (a2, _, _, e2) in zip(out, out[1:]):
        assert a1 + len(f1) <= a2, "overlapping edits: %s @%s and %s @%s" % (e1["card"], e1["addr"], e2["card"], e2["addr"])
    return out


def apply(rom, cards):
    """rom: bytearray (patched in place). Returns {card: n_edits}."""
    done = {}
    for a, f, t, e in _edits(cards):
        cur = bytes(rom[a:a + len(f)])
        assert cur == f, "%s @%s: ROM has %s, card file says %s (wrong address or a different base)" % (
            e["card"], e["addr"], cur.hex(), f.hex())
        rom[a:a + len(t)] = t
        done[e["card"]] = done.get(e["card"], 0) + 1
    return done


def verify(shipped, control, cards):
    bad = []
    covered = set()
    for a, f, t, e in _edits(cards):
        if bytes(shipped[a:a + len(t)]) != t:
            bad.append("%s @%s: shipped has %s, want %s" % (e["card"], e["addr"], bytes(shipped[a:a + len(t)]).hex(), t.hex()))
        if bytes(control[a:a + len(f)]) != f:
            bad.append("%s @%s: control has %s, want %s" % (e["card"], e["addr"], bytes(control[a:a + len(f)]).hex(), f.hex()))
        covered.update(range(a, a + len(t)))
    if len(shipped) != len(control):
        bad.append("size differs: shipped %d, control %d" % (len(shipped), len(control)))
    else:
        stray = []
        if shipped != control:
            for k in range(0, len(shipped), 4096):          # chunked: only differing 4 KB blocks are walked byte by byte
                if shipped[k:k + 4096] != control[k:k + 4096]:
                    stray += [i for i in range(k, min(k + 4096, len(shipped))) if shipped[i] != control[i] and i not in covered]
        if stray:
            bad.append("%d stray bytes outside the card edits, first at %#x" % (len(stray), stray[0] + GBA))
    return bad


def load(path):
    return json.load(open(path))
