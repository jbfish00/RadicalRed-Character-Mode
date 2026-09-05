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

⭐⭐ AND THE PRIMITIVE WAS WRONG IN THREE MORE WAYS, ALL FOUND 2026-09-04
(../game_plans/rowe_parity.md §13.24). Each is written up beside the code
that fixes it, because each is the same lesson in a new costume:

  1. THE SIZE DOES NOT HAVE TO BE AN IMMEDIATE. The scan accepted only
     `movs r2,#<mon size>`; a compiler may keep the size in a callee-saved
     register and issue `movs r2, r4`. CFRU's CreateShedinja does, so the extra
     Pokemon a Nincada evolution creates -- a genuine acquisition path, written
     straight into gPlayerParty[count] and blessed by a recount -- was invisible
     in BOTH CFRU games. See size_seed().
  2. r2 == THE MON SIZE IS NOT ENOUGH TO MAKE A CALL A COPY.
     `movs r2,#100 ; muls r0,r2` is the party-slot stride multiply and leaves
     r2 holding 100 at the NEXT call, so plain `GetMonData(mon, field, NULL)`
     reads were being inventoried as copies -- two per Emerald game. A copy's
     r1 is a pointer; a field request's r1 is a small immediate.
  3. IN THE CFRU GAMES THE BL TARGET IS A VENEER, not the callee. Everything
     the hack's own high-ROM code calls, it calls through one block of
     `bx r3 / bx r4 / bx r5 / bx r6`. So EXPECT_CALLEES was pinning the veneer,
     and "no new copy primitive is in use" meant only "it still goes through
     the veneer" -- which a call to literally anything satisfies. See
     veneer_reg(); with the register resolved the callee set collapses to the
     real functions (CopyMon, memcpy).

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the set of mon-sized
copies into the party has not changed, and that they all go through known copy
primitives. It does NOT prove each one is harmless -- that is what the verdicts
record. It also does not cover a CreateMon-family call that builds a mon in
place; no such site exists in this ROM's inventory today, and a new one would
appear here as a new callee. And it is a scan for ONE shape: the Emerald pair's
PC-withdraw path does not appear here at all, which is a fact about this scan
and not a clean bill of health for the PC (see the UNGATED verdict in the
FireRed pair, and rowe_parity.md §13.24).

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

EXPECT_CHECKS = 5

# The copy primitives a party write is allowed to go through. A NEW callee here
# means a mon is entering the party by a route nobody has looked at.
EXPECT_CALLEES = frozenset({0x08040b08, 0x081e5e78})

# KNOWN HOLES, listed on purpose. Pinned so a second one cannot arrive silently
# and the first cannot be quietly downgraded to EXEMPT without a decision.
EXPECT_UNGATED = frozenset({0x00092fe2})

# Sites the 2026-09-04 primitive fix removed because they are NOT copies at all.
# Kept here so the site-count change is explained rather than silently absorbed
# -- the sibling inventory (check_acquisition_paths.py) keeps its NOT-A-WRITER
# rows for exactly the same reason.
REMOVED_BY_PRIMITIVE_FIX = {
    0x0011718a: "SendBlock(0, &gPlayerParty[i], 100) at 0x0811718A "
                "(0x0800A448, beside GetMultiplayerId 0x0800A404) -- the "
                "link-cable SEND. A read OUT of the party, reported as a copy "
                "IN because r0 was still marked party-derived after `movs "
                "r0,#0` overwrote it. An immediate is not a pointer",
}

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
    0x000456aa: ("EXEMPT",
                 "DAYCARE WITHDRAW. Identified 2026-09-03: the code just "
                 "above reads field 56 off the stack mon, then "
                 "GetMonData(sp,25) + the daycare struct's stored value at "
                 "r5+0x88 -> SetMonData(sp,25,...) -- it applies the EXP "
                 "the mon earned in the daycare -- and copies it into "
                 "gPlayerParty+500 (the last slot, which this engine family "
                 "uses as scratch). The mon is the player's OWN, deposited "
                 "earlier; nothing new enters"),
    0x00046126: ("EXEMPT",
                 "THE GIFT/DAYCARE EGG GIVE, and the most important entry "
                 "in this file. `SetMonData(sp, MON_DATA_IS_EGG=45, ...)` "
                 "then memcpy into gPlayerParty+500 then `bl "
                 "CalculatePlayerPartyCount 0x08040C3C` -- the LAUNDERING "
                 "PATTERN in the flesh: it writes a mon into the array and "
                 "lets a recount bless it, and it never goes through "
                 "GiveMonToPlayer, so the gate there cannot see it. ⚠️ IT "
                 "IS LIVE, not dead code: CFRU thunks out at 0x08046116 "
                 "(`ldr r0,[pc,#4]; bx r0`) and JUMPS BACK IN -- there are "
                 "thumb pointers to 0x08046121 from the CFRU region. EXEMPT "
                 "because eggs are deliberately exempt from the gate in "
                 "every port (an egg event must never block progress). 🔴 "
                 "BUT THE EXEMPTION HAS A DOWNSTREAM GAP: nothing here "
                 "looks at what the egg HATCHES INTO. Unbound closed "
                 "exactly this with tools/character_mode/egg_hook.py, whose "
                 "own words are that it was 'the one enforcement hole "
                 "reachable in ordinary play' -- breeding cannot reach it "
                 "(rosters store whole evolution families, so offspring are "
                 "on-roster by construction), gift eggs are the way in. See "
                 "game_plans/rowe_parity.md 13.16"),
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
    0x00092fe2: ("UNGATED",
                 "THE PC WITHDRAW, and the most consequential entry in this "
                 "file. 0x08092FD4 is a Pokemon Storage System routine: when "
                 "its first argument is 25 it does "
                 "`memcpy(&gPlayerParty[slot], gPSSData + 0xA0, 100)` -- "
                 "gPSSData is 0x020397B0, named in the CFRU donor's BPRE.ld, "
                 "and +0xA0 is the mon the PC cursor is holding. So this is "
                 "the box -> party move. 5 BL callers, all inside the PSS. "
                 "🔴 WHY IT IS UNGATED RATHER THAN EXEMPT: enforcement "
                 "deliberately ROUTES off-roster mons INTO the PC, and "
                 "nothing re-enforces the roster after the player uses it. "
                 "Measured on the built ROM: CM_SweepPartyToPC is called "
                 "from the selection handlers and the egg-hatch tail and "
                 "NOWHERE ELSE, so an off-roster mon the catch gate just "
                 "boxed can be withdrawn straight back into the party and "
                 "kept for the rest of the run. This needs no exploit -- it "
                 "is what happens if you open the PC and take the mon back. "
                 "⭐ ROWE, the reference implementation, closes it in TWO "
                 "places: `CharacterMode_SweepPartyToPC()` at the top of "
                 "`Cb2_ExitPSS` (src/pokemon_storage_system.c), and "
                 "`IsRemovingLastAllowedPartyMon` -- whose comment describes "
                 "the residual exploit in as many words: withdraw an "
                 "off-roster B, deposit your only on-roster A, exit, and the "
                 "never-empty rule keeps B. \"You could play the whole game "
                 "as your character with an arbitrary Pokemon.\" "
                 "See ../game_plans/rowe_parity.md §13.24"),
    0x000a041a: ("EXEMPT",
                 "inside 0x080A03D8 (4 BL callers): allocates a 300-byte "
                 "(3-mon) buffer, copies party slots out by an order array "
                 "and back. A save/restore of the player's own party for "
                 "the reduced-party link modes"),
    0x000ce786: ("EXEMPT",
                 "DEAD CODE: the orphaned body of stock FireRed "
                 "CreateShedinja. Its entry 0x080CE748 was overwritten with "
                 "the 8-byte thunk `ldr r2,[pc,#0] ; bx r2 ; .word "
                 "0x09093EB9` (CFRU_HOOK_SYMBOLS.txt line 378), and the "
                 "replacement is a complete reimplementation. ⚠️ CHECKED "
                 "RATHER THAN ASSUMED, because \"there is a thunk before "
                 "it\" does NOT mean dead -- CFRU thunks out and often "
                 "jumps back in (see 0x00046126). An unaligned u32 scan of "
                 "the whole ROM finds exactly two words pointing into "
                 "0x080CE750..0x080CE8E0: one aligned literal at 0x080CE0D0 "
                 "-> 0x080CE8DD, which is the NEXT function's entry rather "
                 "than this body, and one unaligned coincidence at "
                 "0x08A5F749 inside compressed graphics. And the "
                 "replacement's own branches all stay inside 0x0909xxxx: it "
                 "never returns into the body"),
    0x001114f2: ("EXEMPT",
                 "LINK/UNION-ROOM PLACEHOLDER PARTY. 0x08111438 allocates "
                 "104 bytes, builds one mon into it with "
                 "`CreateMon(buf, 19, 1, 32, 0,0,0,0)` (0x0803DA54, named in "
                 "BPRE.ld), reads a packed value out of `VarGet(0x4027)` and "
                 "then `CopyMon(&gPlayerParty[i], buf, 100)` for i below its "
                 "top nibble. One BL caller, 0x0805736C, inside a link/"
                 "multiplayer setup sequence (its neighbours in that "
                 "sequence are 0x08111F14 / 0x081113E4 / 0x08110AC8, and the "
                 "adjacent routines in this address range use "
                 "GetMultiplayerId and SendBlock). It writes a FIXED "
                 "template, never a species the player chose, and it "
                 "overwrites the real party wholesale -- so it cannot be a "
                 "route by which a chosen off-roster species enters and "
                 "stays. ⚠️ Residual: nothing here proves it is unreachable "
                 "in single player; if it ever ran there the player would "
                 "lose their team, which is why it reads as link-only"),
    0x0011c08e: ("EXEMPT",
                 "REDUCE-THE-PARTY-FOR-A-LINK-BATTLE. 0x0811C04C copies the "
                 "2 mons named by the selection array at 0x0203C750 out of "
                 "gPlayerParty into gEnemyParty (0x0202402C -- exactly 600 "
                 "bytes below gPlayerParty, which is what makes it this "
                 "engine's party stash), ZeroMonData's all 6 party slots, "
                 "copies the 2 back into slots 0-1, then calls "
                 "CalculatePlayerPartyCount 0x08040C3C. Every mon it writes "
                 "came out of the party a few instructions earlier -- the "
                 "laundering pattern with a benign source"),
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
    0x0108784a: ("EXEMPT",
                 "CFRU's DAYCARE WITHDRAW -- the high-ROM twin of the "
                 "already-EXEMPT vanilla site at 0x000456AA. Named by the six "
                 "vanilla functions it calls through CFRU's register-dispatch "
                 "veneer, all resolved out of its literal pool against the "
                 "donor's BPRE.ld: 0x080453E0 (with gStringVar1), "
                 "GetBoxMonData(mon, 11), BoxMonToMon, then "
                 "memcpy(gPlayerParty + 500, stackMon, 100) -- slot 5, the "
                 "scratch slot this engine family uses -- then ZeroBoxMonData, "
                 "CompactPartySlots and CalculatePlayerPartyCount. The "
                 "laundering pattern again (a direct array write blessed by a "
                 "recount) with a benign source: the mon is the player's own, "
                 "deposited earlier"),
    0x01093f18: ("EXEMPT",
                 "CFRU's LIVE CreateShedinja -- the replacement the vanilla "
                 "body at 0x000CE786 was thunked out to, and a REAL "
                 "acquisition path: a Nincada evolution creates an EXTRA "
                 "Pokemon, copied straight into gPlayerParty[count] and "
                 "blessed by a recount, never touching GiveMonToPlayer. "
                 "\u2b50 IT WAS INVISIBLE TO THIS SCAN UNTIL 2026-09-04, "
                 "because it keeps the mon size in r4 and issues "
                 "`movs r2, r4` -- see size_seed(). \u2705 EXEMPT ON "
                 "MEASUREMENT, not on reasoning: on this game's own "
                 "enforcement data, all 8 characters whose roster allows "
                 "Nincada (301) also allow 302 and 303, so the extra Pokemon "
                 "is on-roster by construction and the family rule is doing "
                 "exactly what it exists for. \u26a0\ufe0f That is a "
                 "property of the DATA: re-check it if the roster pipeline "
                 "ever stops expanding branch evolutions"),
}

WINDOW = 48
BACK = 1024
PRE = 32


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


def veneer_reg(b, target):
    """If `target` is a CFRU register-dispatch veneer (`bx rN`), return N.

    ⚠️ WITHOUT THIS THE CALLEE SET IS A LIE IN THE TWO CFRU GAMES. Everything
    the hack's own high-ROM C code calls, it calls through a four-instruction
    block of `bx r3 / bx r4 / bx r5 / bx r6`, with the real function address
    loaded into that register from a literal pool. So the BL target is the
    veneer, the same veneer for every callee, and "no new copy primitive is in
    use" degrades to "it still goes through the veneer" -- which a call to
    anything at all satisfies. Resolving the register turns the veneer back
    into CopyMon/memcpy.
    """
    off = target - 0x08000000
    if off < 0 or off + 1 >= len(b):
        return None
    v = u16(b, off)
    if (v & 0xFF87) == 0x4700 and 3 <= ((v >> 3) & 0xF) <= 6:
        return (v >> 3) & 0xF
    # The other CFRU shape, and the one 0x0900044A uses: a two-instruction
    # thunk `ldr rN,[pc,#imm] ; bx rN` with the real address in its own literal
    # pool. Returned as a NEGATIVE address so the caller can tell "read this
    # register" from "the answer is this address".
    if (v & 0xF800) == 0x4800 and off + 3 < len(b):
        nxt = u16(b, off + 2)
        if (nxt & 0xFF87) == 0x4700 and ((nxt >> 3) & 0xF) == ((v >> 8) & 7):
            pos = (((target + 4) & ~3) + (v & 0xFF) * 4) - 0x08000000
            if 0 <= pos + 4 <= len(b):
                return -(struct.unpack_from("<I", b, pos)[0] & ~1)
    return None


def size_seed(b, i):
    """Registers r4-r7 holding MON_SIZE on entry to the window at `i`.

    ⭐ THE BLIND SPOT THIS CLOSES. The scan used to accept only the immediate
    form `movs r2,#<mon size>`, and a compiler is free to keep the size in a
    callee-saved register and issue `movs r2, r4` at each call. CFRU's
    CreateShedinja does exactly that, so a mon-sized copy into gPlayerParty --
    the extra Pokemon a Nincada evolution creates -- was invisible to this
    inventory in both CFRU games.

    ⚠️ Only r4-r7, and only on a STRAIGHT-LINE run into the window. r0-r3 are
    the argument registers, and `movs r2,#100 ; muls r0,r2` (a party-slot
    stride multiply) is one of the commonest idioms in these ROMs -- seeding r2
    from it reports every following call as a mon copy. Measured: seeding all
    eight registers turned 1 new site into 20, of which the ones checked by
    hand were all leftovers of that multiply.
    """
    s = set()
    for k in range(max(0, i - PRE * 2), i, 2):
        v = u16(b, k)
        if (v & 0xF800) == 0x2000:                       # movs rD,#imm
            d, imm8 = (v >> 8) & 7, v & 0xFF
            if d >= 4:
                s.add(d) if imm8 == MON_SIZE else s.discard(d)
        elif (v & 0xFFC0) == 0x0000 and v != 0:          # movs rD,rS (lsls #0)
            d, sr = v & 7, (v >> 3) & 7
            if d >= 4:
                s.add(d) if sr in s else s.discard(d)
        elif (v & 0xF800) == 0x4800:                     # ldr rD,[pc,#imm]
            s.discard((v >> 8) & 7)
        elif ((v & 0xF000) == 0xD000 or (v & 0xF800) == 0xE000
              or (v & 0xF800) == 0xF000 or (v & 0xFF00) == 0x4700
              or (v & 0xFF00) == 0xBD00):
            s.clear()          # control can arrive here from anywhere else
    return s


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
            sized = size_seed(b, i)
            r1_is_imm = False
            lit = {}                              # rN -> last pc-relative value
            for k in range(i + 2, min(i + 2 + WINDOW * 2, len(b) - 3), 2):
                v = u16(b, k)
                if v == (0x2200 | MON_SIZE):
                    r2_is_mon = True
                elif (v & 0xFF00) == 0x2200:
                    r2_is_mon = False
                # r1 = a small immediate means this is GetMonData/SetMonData
                # (mon, FIELD, value), not memcpy(dst, src, n). Without this the
                # inventory reports plain reads as copies whenever r2 still
                # holds the stride constant -- measured, 2 per Emerald game.
                if (v & 0xFF00) == 0x2100:
                    r1_is_imm = True
                elif ((v & 0xF807) in (0x0001, 0x1801, 0x1C01, 0x5801, 0x5A01,
                                       0x6801, 0xA901)
                      or (v & 0xFF00) in (0x4900, 0x3100)):
                    r1_is_imm = False
                if (v & 0xF800) == 0x2000:               # movs rD,#imm
                    d, imm8 = (v >> 8) & 7, v & 0xFF
                    sized.add(d) if imm8 == MON_SIZE else sized.discard(d)
                    # An immediate is not a pointer. Without this the scan kept
                    # reporting `SendBlock(0, &gPlayerParty[i], 100)` -- the
                    # link-cable SEND, a read -- as a copy INTO the party,
                    # because r0 was still marked party-derived from before it
                    # was overwritten with 0.
                    tracked.discard(d)
                elif (v & 0xFFC0) == 0x0000 and v != 0:  # movs rD,rS
                    d, sr = v & 7, (v >> 3) & 7
                    sized.add(d) if sr in sized else sized.discard(d)
                    if d == 2:
                        r2_is_mon = 2 in sized
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
                    if r2_is_mon and 0 in tracked and not r1_is_imm:
                        reg = veneer_reg(b, t)
                        if reg is None:
                            found[i].add(t)
                        elif reg < 0:
                            found[i].add(-reg)
                        else:
                            found[i].add(lit.get(reg, t))
                    # A call clobbers r0-r3, so neither the size nor the
                    # destination survives it. Without this every later call in
                    # the window reads as a mon copy.
                    r2_is_mon = False
                    r1_is_imm = False
                    sized -= {0, 1, 2, 3}
                    tracked -= {0, 1, 2, 3}
                    for r in (0, 1, 2, 3):
                        lit.pop(r, None)
                    continue
                if (v & 0xF800) == 0x4800:
                    d = (v >> 8) & 7
                    pos = (((k + 4) & ~3) + (v & 0xFF) * 4)
                    if pos + 4 <= len(b):
                        lit[d] = struct.unpack_from("<I", b, pos)[0] & ~1
                    # Only THIS register is clobbered. Breaking the whole scan
                    # here was a real blind spot: CFRU's GiveMonToPlayer reloads
                    # the register that held gPlayerParty long after the slot
                    # pointer has been computed into r0, so the enforcement copy
                    # itself went unseen.
                    tracked.discard(d)
                    sized.discard(d)
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

    # UNGATED is a KNOWN HOLE, listed on purpose. Pinning the exact set is what
    # stops a second one arriving silently -- and stops the first one being
    # quietly downgraded to EXEMPT without anyone deciding to close it. Same
    # shape as check_gift_eggs.py's UNGATED verdicts and
    # check_acquisition_paths.py's EXPECT_UNGATED.
    ungated = frozenset(o for o in INVENTORY if INVENTORY[o][0] == "UNGATED")
    check("the set of KNOWN-UNGATED party writes is exactly what is expected",
          ungated == EXPECT_UNGATED,
          "expected %s, inventory says %s"
          % (sorted("%#010x" % (0x08000000 + o) for o in EXPECT_UNGATED),
             sorted("%#010x" % (0x08000000 + o) for o in ungated)))

    unver = sorted(o for o in INVENTORY if INVENTORY[o][0] == "UNVERIFIED")
    print("\n  verdicts: %d GATED, %d EXEMPT, %d UNGATED, %d NOT-A-COPY, "
          "%d UNVERIFIED"
          % (sum(1 for v in INVENTORY.values() if v[0] == "GATED"),
             sum(1 for v in INVENTORY.values() if v[0] == "EXEMPT"),
             sum(1 for v in INVENTORY.values() if v[0] == "UNGATED"),
             sum(1 for v in INVENTORY.values() if v[0] == "NOT-A-COPY"),
             len(unver)))
    for o in sorted(o for o in INVENTORY if INVENTORY[o][0] == "UNGATED"):
        print("  \U0001f534 UNGATED %#010x -- a KNOWN hole, not a clean site"
              % (0x08000000 + o))
    if REMOVED_BY_PRIMITIVE_FIX:
        print("  \u2139 %d site(s) the 2026-09-04 primitive fix removed as "
              "NOT-A-COPY (kept here so the count change is explained, not "
              "silently absorbed):" % len(REMOVED_BY_PRIMITIVE_FIX))
        for o in sorted(REMOVED_BY_PRIMITIVE_FIX):
            print("       %#010x" % (0x08000000 + o))
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
