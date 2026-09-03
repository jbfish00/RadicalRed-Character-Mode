#!/usr/bin/env python3
"""INVENTORY every mon-sized copy INTO gPlayerParty in this ROM.

⭐ WHY THIS EXISTS, AND WHY IT IS A SECOND INVENTORY.

check_acquisition_paths.py pins every writer of gPlayerPartyCount, on the
reasoning that anything handing the player a Pokemon must increment it. That
caught what it was built for -- but reverse-engineering all 42 of those writers
(2026-09-02, docs/PARTY_COUNT_WRITERS.md) showed the commonest shape by far is
a RECOUNT: `count = 0; ++ per non-empty slot`. A recount introduces nothing,
which is why every one is EXEMPT -- and it is also exactly what makes a DIRECT
write into gPlayerParty legitimate afterwards.

So the count byte is a good primitive for catching a routine that ADDS and a
poor one for catching a routine that writes the array and lets a recount bless
it. That is the workspace's lesson #1 -- *an inventory is only as good as its
choice of PRIMITIVE* -- recurring one level UP rather than one idiom over.
This file is the other half.

⚠️ CHOOSING THE PRIMITIVE TOOK THREE TRIES, and the failures are the useful
part:
  1. "every store through a gPlayerParty-derived pointer" -> 261 write
     candidates. Unusable.
  2. "every function called with a gPlayerParty pointer in r0" -> 171 distinct
     callees, because GetMonData(&gPlayerParty[i], ...) passes the mon in r0
     too. A read looks exactly like a write at that resolution.
  3. What works: a call whose destination register is gPlayerParty-derived AND
     whose r2 is the mon size (100). A species can only enter a party
     slot as a whole-mon copy, and the size argument is what separates the
     copies from the reads. 17 sites, 5 distinct callees.

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the set of mon-sized copies
into the party has not changed, and that they all go through known copy
primitives. It does NOT prove each one is harmless -- that is what the verdicts
record. It also does not cover a CreateMon-family call that builds a mon in
place; no such site exists in this ROM's inventory today, and a new one would
appear here as a new callee.

Run:  python3 tools/tests/check_party_writes.py   (0 = ok, 1 = changed)
"""
import collections
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from cm_tally import assert_tally          # noqa: E402

GAME = "Pokémon Radical Red v4.1"
ROM = os.path.join(ROOT, 'rom/radicalred 4.1.gba')
PLAYER_PARTY = 0x02024284
MON_SIZE = 100

EXPECT_CHECKS = 4

# The copy primitives a party write is allowed to go through. A NEW callee here
# means a mon is entering the party by a route nobody has looked at.
EXPECT_CALLEES = frozenset({0x081e5e78, 0x08040b08, 0x0800a448, 0x0907e498, 0x0900044a})

# ldr site -> (verdict, why).
#   GATED      the project's enforcement covers this path
#   EXEMPT     deliberately not gated, with a reason
#   UNVERIFIED found by the scan, containing routine not yet identified
INVENTORY = {
    0x00040b50: ("EXEMPT",
                 "DEAD CODE: inside the orphaned body of stock FireRed "
                 "GiveMonToPlayer, whose entry 0x08040B14 was overwritten "
                 "with a 4-byte thunk to the CFRU replacement. Proven "
                 "unreachable in docs/PARTY_COUNT_WRITERS.md (entry "
                 "0x00040b6c)"),
    0x000456aa: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x08045608 (1 BL "
                 "caller, 0x080456A6); containing routine not yet "
                 "identified. It reaches the party through a known copy "
                 "primitive, so it cannot be introducing a species by an "
                 "unknown mechanism -- but WHAT it copies is unexamined"),
    0x00046126: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x08046000 (1 BL "
                 "caller, 0x080460DE); containing routine not yet "
                 "identified. It reaches the party through a known copy "
                 "primitive, so it cannot be introducing a species by an "
                 "unknown mechanism -- but WHAT it copies is unexamined"),
    0x0004c240: ("EXEMPT",
                 "inside LoadPlayerParty 0x0804C230: copies 6 x 100 bytes "
                 "back from gSaveBlock1Ptr. Restores the player's OWN saved "
                 "party after a link/facility swap-out; everything it "
                 "restores was gated when first acquired"),
    0x00050828: ("EXEMPT",
                 "inside 0x0805080C (3 BL callers): computes two "
                 "gPlayerParty slot pointers and copies between them -- a "
                 "party SLOT SWAP. It moves mons the player already owns; "
                 "no species enters from outside"),
    0x00092fe2: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x08092FD4 (5 BL "
                 "callers); containing routine not yet identified. It "
                 "reaches the party through a known copy primitive, so it "
                 "cannot be introducing a species by an unknown mechanism "
                 "-- but WHAT it copies is unexamined"),
    0x000a041a: ("EXEMPT",
                 "inside 0x080A03D8 (4 BL callers): allocates a 300-byte "
                 "(3-mon) buffer, copies party slots out by an order array "
                 "and back. A save/restore of the player's own party for "
                 "the reduced-party link modes"),
    0x000ce786: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x080CE72C (no BL "
                 "callers -- reached by pointer or as a task); containing "
                 "routine not yet identified. It reaches the party through "
                 "a known copy primitive, so it cannot be introducing a "
                 "species by an unknown mechanism -- but WHAT it copies is "
                 "unexamined"),
    0x001114f2: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x08111438 (1 BL "
                 "caller, 0x0805736C); containing routine not yet "
                 "identified. It reaches the party through a known copy "
                 "primitive, so it cannot be introducing a species by an "
                 "unknown mechanism -- but WHAT it copies is unexamined"),
    0x0011718a: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x08117130 (no BL "
                 "callers); containing routine not yet identified. It "
                 "reaches the party through a known copy primitive, so it "
                 "cannot be introducing a species by an unknown mechanism "
                 "-- but WHAT it copies is unexamined"),
    0x0011c08e: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x0811C04C (no BL "
                 "callers); containing routine not yet identified. It "
                 "reaches the party through a known copy primitive, so it "
                 "cannot be introducing a species by an unknown mechanism "
                 "-- but WHAT it copies is unexamined"),
    0x00123512: ("EXEMPT",
                 "inside 0x081234EC (1 BL caller, 0x081232D8): allocates a "
                 "600-byte (6-mon) buffer, memcpy's the whole gPlayerParty "
                 "into it, then copies each slot back at a new index -- a "
                 "party REORDER. Verified by disassembly on the 0x08128074 "
                 "twin; all three are the same routine with different order "
                 "functions. Moves owned mons only"),
    0x0012809a: ("EXEMPT",
                 "inside 0x08128074 (5 BL callers): allocates a 600-byte "
                 "(6-mon) buffer, memcpy's the whole gPlayerParty into it, "
                 "then copies each slot back at a new index -- a party "
                 "REORDER. Verified by disassembly on the 0x08128074 twin; "
                 "all three are the same routine with different order "
                 "functions. Moves owned mons only"),
    0x001280ea: ("EXEMPT",
                 "inside 0x081280C4 (1 BL caller, 0x0811FAD2): allocates a "
                 "600-byte (6-mon) buffer, memcpy's the whole gPlayerParty "
                 "into it, then copies each slot back at a new index -- a "
                 "party REORDER. Verified by disassembly on the 0x08128074 "
                 "twin; all three are the same routine with different order "
                 "functions. Moves owned mons only"),
    0x0107d7ce: ("GATED",
                 "inside CFRU's GiveMonToPlayer 0x0907D790 -- THE "
                 "enforcement choke point. It is the memcpy that places the "
                 "mon in gPlayerParty[i], immediately before the count "
                 "write at 0x0107D7FA that check_acquisition_paths.py lists "
                 "as GATED. ⭐ THIS SITE WAS INVISIBLE to the first version "
                 "of this scan: CFRU reloads the register that held "
                 "gPlayerParty long after the slot pointer has been "
                 "computed into r0, and the scanner treated a reload of ANY "
                 "tracked register as the end of the window. It now drops "
                 "just that register and keeps going"),
    0x0108784a: ("UNVERIFIED",
                 "mon-sized copy into a party slot inside 0x09087824 "
                 "(CFRU/RR high-ROM region, no BL callers); containing "
                 "routine not yet identified. It reaches the party through "
                 "a known copy primitive, so it cannot be introducing a "
                 "species by an unknown mechanism -- but WHAT it copies is "
                 "unexamined"),
}

WINDOW = 48
BACK = 1024


def u16(b, i):
    return struct.unpack_from("<H", b, i)[0]


def bl_target(b, k):
    hi, lo = u16(b, k), u16(b, k + 2)
    if (hi & 0xF800) != 0xF000 or (lo & 0xF800) != 0xF800:
        return None
    o = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
    if o & 0x400000:
        o -= 0x800000
    return 0x08000000 + k + 4 + o


def copies(b):
    """{ldr file offset: set(callee ROM addrs)} for every mon-sized copy in."""
    pools = []
    p = struct.pack("<I", PLAYER_PARTY)
    i = b.find(p)
    while i >= 0:
        if i % 4 == 0:
            pools.append(i)
        i = b.find(p, i + 1)

    found = collections.defaultdict(set)
    for pool in pools:
        for i in range(max(0, pool - BACK), pool, 2):
            w = u16(b, i)
            if (w & 0xF800) != 0x4800:            # ldr rX,[pc,#imm8]
                continue
            rX, imm = (w >> 8) & 7, w & 0xFF
            if (((i + 4) & ~3) + imm * 4) != pool:
                continue
            tracked, r2_is_mon = {rX}, False
            for k in range(i + 2, min(i + 2 + WINDOW * 2, len(b) - 3), 2):
                v = u16(b, k)
                if v == (0x2200 | MON_SIZE):
                    r2_is_mon = True
                elif (v & 0xFF00) == 0x2200:
                    r2_is_mon = False
                if (v & 0xFE00) == 0x1C00 and (v >> 3) & 7 in tracked:
                    tracked.add(v & 7); continue          # adds rD,rS,#imm
                if (v & 0xFE00) == 0x1800 and (((v >> 3) & 7) in tracked
                                               or ((v >> 6) & 7) in tracked):
                    tracked.add(v & 7); continue          # adds rD,rS,rT
                if (v & 0xF800) == 0x3000 and ((v >> 8) & 7) in tracked:
                    continue                              # adds rX,#imm
                if (v & 0xFFC0) == 0x1C00 and ((v >> 3) & 7) in tracked:
                    tracked.add(v & 7); continue          # movs rD,rS
                t = bl_target(b, k)
                if t is not None:
                    if r2_is_mon and 0 in tracked:
                        found[i].add(t)
                    # A call clobbers r0-r3, so neither the size nor the
                    # destination survives it. Without this every later call in
                    # the window reads as a mon copy.
                    r2_is_mon = False
                    tracked -= {0, 1, 2, 3}
                    continue
                if (v & 0xF800) == 0x4800:
                    # Only THIS register is clobbered. Breaking the whole scan
                    # here was a real blind spot: CFRU's GiveMonToPlayer reloads
                    # the register that held gPlayerParty long after the slot
                    # pointer has been computed into r0, so the enforcement copy
                    # itself went unseen.
                    tracked.discard((v >> 8) & 7)
                    if not tracked:
                        break
                    continue                                 # rX reloaded
                if (v & 0xFF00) in (0x4700, 0xBD00):
                    break                                 # bx / pop {..,pc}
    return found


failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


def main():
    if not os.path.isfile(ROM):
        print("base ROM not found: %s" % os.path.relpath(ROM, ROOT))
        return 1
    with open(ROM, "rb") as f:
        b = f.read()

    found = copies(b)
    print("%s -- gPlayerParty %#010x, mon size %d" % (GAME, PLAYER_PARTY, MON_SIZE))
    print("  %d mon-sized copy site(s) found, %d inventoried\n"
          % (len(found), len(INVENTORY)))

    new = sorted(set(found) - set(INVENTORY))
    check("every mon-sized copy into gPlayerParty is inventoried",
          not new,
          ", ".join("%#010x" % (0x08000000 + o) for o in new)
          + " -- a routine that copies a whole mon into the party and is not "
            "on the list can introduce a species the count inventory would "
            "then bless on the next recount; identify it, then add a verdict")

    gone = sorted(set(INVENTORY) - set(found))
    check("every inventoried copy is still present in the ROM",
          not gone,
          ", ".join("%#010x" % (0x08000000 + o) for o in gone))

    seen = set()
    for s in found.values():
        seen |= s
    check("no new copy primitive is in use",
          seen <= EXPECT_CALLEES,
          ", ".join("%#010x" % t for t in sorted(seen - EXPECT_CALLEES)))

    # The enforcement choke point must be among them: an inventory listing no
    # GATED copy would describe a ROM where nothing gates the party at all, and
    # would still satisfy the three checks above.
    gated = [o for o in INVENTORY if INVENTORY[o][0] == "GATED" and o in found]
    check("at least one GATED copy is present (the enforcement point)",
          bool(gated), "no GATED copy among %d" % len(found))

    unver = sorted(o for o in INVENTORY if INVENTORY[o][0] == "UNVERIFIED")
    print("\n  verdicts: %d GATED, %d EXEMPT, %d UNVERIFIED"
          % (sum(1 for v in INVENTORY.values() if v[0] == "GATED"),
             sum(1 for v in INVENTORY.values() if v[0] == "EXEMPT"),
             len(unver)))
    if unver:
        print("  ⚠️ UNVERIFIED means the containing routine has not been "
              "identified here. It is a 'go look', not a clean bill of health:")
        for o in unver:
            print("       %#010x" % (0x08000000 + o))

    if assert_tally(checks_run, EXPECT_CHECKS, "check_party_writes"):
        return 1
    print("\n%s" % ("ALL PASS" if not failures
                     else "FAILURES: " + ", ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
