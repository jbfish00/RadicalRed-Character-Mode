#!/usr/bin/env python3
"""INVENTORY every routine in this ROM that writes gPlayerPartyCount.

⭐ WHY THIS EXISTS, and why it is an inventory rather than a grep.

The workspace's lesson #1 (CLAUDE.md, from Platinum): *a checker that greps the
files which ALREADY contain a hook cannot see a bypass in a file with no hook.*
Platinum's acquisition inventory enumerated `Party_AddPokemon*` repo-wide and
still could not see the link trade or the GTS, because a trade fills the slot
its partner vacated and adds nothing. The fix there was not "search more files"
but "choose a different PRIMITIVE to count".

For a GBA binary hack the primitive that cannot be dodged is the one every
acquisition must eventually touch: **the party count byte itself**. A routine
that hands the player a Pokemon has to increment gPlayerPartyCount, whatever
route it took to get there. So this enumerates every instruction in the ROM
that STORES through a pointer to that byte, and requires each one to carry a
verdict below. A new acquisition path is then a failing check rather than a
silent arrival.

✅ THE METHOD IS VALIDATED ON A KNOWN POSITIVE. Run against Seaglass, it
rediscovers both that game's enforcement choke point AND the give-core bypass
its own ROUTINE_MAP documents as "never BLs GiveMonToPlayer -> bypasses the
injected CM gate" -- a path a caller-of-GiveMonToPlayer scan cannot see, and
the exact shape of the Platinum miss.

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the SET of party-count writers
has not changed. It does NOT prove each one is correctly gated -- that is what
the verdicts record, and several are still UNVERIFIED (they are writers whose
containing routine has not been reverse-engineered here). An UNVERIFIED entry
is a "go look", not a clean bill of health. Recording an absence of
investigation as a negative result is a mistake this workspace has made at
least four times.

Detection: Thumb `ldr rX,[pc,#imm]` puts its literal at ((pc+4) & ~3) + imm*4,
so the loads of a given pool word are found exactly rather than by proximity;
then a store THROUGH that register within the following instructions is a
write. Conservative: it reports WRITE only when it can see the store.

Run:  python3 tools/tests/check_acquisition_paths.py   (0 = ok, 1 = changed)
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from cm_tally import assert_tally          # noqa: E402

GAME = "Pokémon Radical Red v4.1"
ROM = os.path.join(ROOT, 'rom/radicalred 4.1.gba')
PARTY_COUNT = 0x02024029

# How many checks this layer must run. A deliberate LITERAL -- see cm_tally.py.
EXPECT_CHECKS = 3

# ldr site -> (verdict, why). Every writer the scan finds must be listed here.
#   GATED      the project's enforcement covers this path
#   EXEMPT     deliberately not gated, with a reason
#   UNVERIFIED found by the scan, containing routine not yet identified
INVENTORY = {
    0x00040b6c: ("EXEMPT",
                 "DEAD CODE: the orphaned body of stock FireRed "
                 "GiveMonToPlayer. Its entry 0x08040B14 was overwritten "
                 "with a 4-byte thunk (ldr r1,[pc,#0]; bx r1) to "
                 "0x0907D791, the CFRU GiveMonToPlayer that carries the "
                 "GATED writer, so all 3 BL callers are redirected. No BL "
                 "and no branch from outside reaches the orphan; the only "
                 "two ROM words pointing into it (0x08A06D38, 0x08B0B818) "
                 "sit inside sample data, not pointer tables -- measured"),
    0x00040c3e: ("EXEMPT",
                 "CalculatePlayerPartyCount (36 BL callers): "
                 "gPlayerPartyCount = 0, then ++ per slot whose "
                 "MON_DATA_SPECIES is non-zero. A RECOUNT of what the array "
                 "already holds -- it cannot introduce a mon. See the "
                 "LAUNDERING note in docs/PARTY_COUNT_WRITERS.md"),
    0x0004c232: ("EXEMPT",
                 "LoadPlayerParty: gPlayerPartyCount = "
                 "gSaveBlock1Ptr->[0x34], then copies 6 x 100 bytes back "
                 "from the save block. Restores the player's OWN saved "
                 "party (link/facility swap-back); everything it restores "
                 "was gated when first acquired -- same reasoning as the "
                 "existing party-restore EXEMPT"),
    0x00054aee: ("EXEMPT",
                 "new-game init (entry 0x08054A60 thunked to 0x09042E35, "
                 "which re-enters the original body at +0x09): "
                 "gPlayerPartyCount = 0 amid the init BL run. Zeroing "
                 "removes, never adds"),
    0x0008ecc0: ("EXEMPT",
                 "gPlayerPartyCount = CalculatePlayerPartyCount() -- "
                 "literally `bl 0x08040C3C; ldr r1,=count; strb r0,[r1]`. A "
                 "recount after a storage-screen exit"),
    0x0008edf4: ("EXEMPT",
                 "gPlayerPartyCount = CalculatePlayerPartyCount(); "
                 "byte-identical to the site at 0x0008ECC0, the other arm "
                 "of the same screen"),
    0x0012092a: ("NOT-A-WRITER",
                 "FALSE POSITIVE -- not a writer. `ldr r0,=count; ldrb "
                 "r0,[r0]; cmp r4,r0; bcc` is a LOOP BOUND READ. The "
                 "detector's window walked past the loop's unconditional "
                 "branch into the literal pool at 0x08120938 and decoded "
                 "the word 0x020370C2 as `strb r2,[r0,#3]`. See the "
                 "DETECTOR DEFECT note in docs/PARTY_COUNT_WRITERS.md"),
    0x0107d7fa: ("GATED",
                 "inside GiveMonToPlayer 0x0907D791 -- THE enforcement choke point; both wild catches and ScriptGiveMon flow through it (docs/ROUTINE_MAP.md)"),
    0x0109b5c8: ("EXEMPT",
                 "script special (gSpecials entry at 0x0815FF10 = "
                 "0x0909B581): copies party slots 0-2 into a 300-byte stack "
                 "buffer, writes them into slots 3-5, then RECOUNTS (count "
                 "= 0; ++ per non-empty slot). It permutes mons the player "
                 "already owns; no species enters from outside"),
    0x010bc1a2: ("EXEMPT",
                 "inside RR's party-restore-from-save routine 0x090BC194: it re-gives the player's OWN saved party on load. Gating it would strip the party; everything it re-gives was gated when first acquired (docs/ROUTINE_MAP.md:194)"),
}

WINDOW = 60          # instructions to follow after the ldr


def thumb(b, i):
    return struct.unpack_from("<H", b, i)[0]


def writers(b):
    """{ldr file offset: pool offset} for every store through gPlayerPartyCount."""
    pools = []
    p = struct.pack("<I", PARTY_COUNT)
    i = b.find(p)
    while i >= 0:
        if i % 4 == 0:
            pools.append(i)
        i = b.find(p, i + 1)

    found = {}
    for pool in pools:
        for i in range(max(0, pool - 1024), pool, 2):
            w = thumb(b, i)
            if (w & 0xF800) != 0x4800:            # ldr rX,[pc,#imm8]
                continue
            rX, imm = (w >> 8) & 7, w & 0xFF
            if (((i + 4) & ~3) + imm * 4) != pool:
                continue
            for k in range(i + 2, min(i + 2 + WINDOW * 2, len(b) - 1), 2):
                v = thumb(b, k)
                if (v & 0xF800) == 0x7000 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # strb rY,[rX,#imm]
                if (v & 0xFE00) == 0x5400 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # strb rY,[rX,rZ]
                if (v & 0xF800) == 0x6000 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # str  rY,[rX,#imm]
                if (v & 0xF800) == 0x4800 and ((v >> 8) & 7) == rX:
                    break                         # rX reloaded: not ours
                if (v & 0xFF00) in (0x4700, 0xBD00):
                    break                         # bx / pop {..,pc}
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

    found = writers(b)
    rom_addr = {off: 0x08000000 + off for off in found}

    print("%s -- gPlayerPartyCount %#010x" % (GAME, PARTY_COUNT))
    print("  %d writer site(s) found, %d inventoried\n"
          % (len(found), len(INVENTORY)))

    # 1. nothing new arrived
    new = sorted(set(found) - set(INVENTORY))
    check("every party-count writer in the ROM is inventoried",
          not new,
          ", ".join("%#010x" % rom_addr[o] for o in new)
          + " -- a routine that writes the party count and is not on the list "
            "is a possible ungated acquisition path; identify it, then add it "
            "with a verdict")

    # 2. nothing inventoried vanished (the inventory is not describing a
    #    ROM that no longer exists)
    gone = sorted(set(INVENTORY) - set(found))
    check("every inventoried writer is still present in the ROM",
          not gone,
          ", ".join("%#010x" % (0x08000000 + o) for o in gone))

    # 3. the enforcement choke point is actually among the writers -- an
    #    inventory that lists no GATED path would be describing a ROM with no
    #    enforcement at all, and would still pass checks 1 and 2.
    gated = [o for o in INVENTORY if INVENTORY[o][0] == "GATED" and o in found]
    check("at least one GATED writer is present (the enforcement point)",
          bool(gated), "no GATED writer found among %d" % len(found))

    unver = sorted(o for o in INVENTORY if INVENTORY[o][0] == "UNVERIFIED")
    print("\n  verdicts: %d GATED, %d EXEMPT, %d NOT-A-WRITER, %d UNVERIFIED"
          % (sum(1 for v in INVENTORY.values() if v[0] == "GATED"),
             sum(1 for v in INVENTORY.values() if v[0] == "EXEMPT"),
             sum(1 for v in INVENTORY.values() if v[0] == "NOT-A-WRITER"),
             len(unver)))
    print("  NOT-A-WRITER: the scan reports these, and reverse engineering "
          "showed they are\n    reads, not stores. They stay listed on "
          "purpose -- the detector is deliberately\n    conservative, so "
          "dropping them would make check 2 fail. See\n    "
          "docs/PARTY_COUNT_WRITERS.md for the detector defect that "
          "produces them.")
    if unver:
        print("  ⚠️ UNVERIFIED means the containing routine has not been "
              "identified here. It is a 'go look', not a clean bill of health:")
        for o in unver:
            print("       %#010x" % (0x08000000 + o))

    if assert_tally(checks_run, EXPECT_CHECKS, "check_acquisition_paths"):
        return 1
    print("\n%s" % ("ALL PASS" if not failures
                     else "FAILURES: " + ", ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
