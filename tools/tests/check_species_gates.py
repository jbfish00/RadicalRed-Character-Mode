#!/usr/bin/env python3
"""INVENTORY every ChoosePartyMon call site in this ROM, and decode what the
NPCs behind them GIVE.

⭐ WHY THIS EXISTS. `rowe_parity.md` §13.28 measured a class of NPC that wants
a species SHOWN rather than traded, and reported the raw counts 5/5/2/0 across
the four ports as the mission cost of the PC-withdraw fix -- while stating
plainly that NOBODY HAD DECODED WHAT ANY OF THEM GIVE, so the count was an
upper bound and not a loss. §13.37 decoded them. The answer is that the count
matters to nothing: nine of the fourteen gates hand over an item that only
works on the very species the character cannot own, four more give something
a shop sells, and the last two gate on a species that has to be CAUGHT, which
the catch gate already refuses.

⚠️ THE PRIMITIVE, AND WHY IT IS NOT THE DIALOGUE WALK. `check_gift_eggs.py`
finds its sites by decoding forward from a dialogue anchor. That walk is the
right primitive for `giveegg`, and it is the WRONG one here: measured on these
four ROMs it reaches 20 of 43 ChoosePartyMon sites in this game
(20/43, 26/76, 3/19 and 2/11 across the four). The count §13.28 published was
the walk-reachable subset, so it was never a count of the class. This file
scans for the call site itself -- `special <ChoosePartyMon>` immediately
followed by `waitstate`, which every real site has -- and pins the whole set.

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the set of ChoosePartyMon call
sites has not changed and that the decoded gates still compare the recorded
species and still hand over the recorded items. It does NOT claim every site
in SITES has been decoded: the ones that have are in GATES, and the rest are
pinned by address only. A species test that lives in native code (Radical
Red's `special 0x78`, its gender-swap `callasm`, Unbound's Deoxys and Rotom
callasms, Seaglass's `special 0x224`) is in GATES with an EMPTY species tuple
-- it is there because the DIALOGUE was decoded, and no compare scan can see
it.

⚠️ Three false-positive constants worth pinning, all of which decode as a
plausible species right after a ChoosePartyMon:
  255  PARTY_NOTHING_CHOSEN in the Emerald pair (decodes as Torchic)
  412  SPECIES_EGG in the FireRed pair (decodes as Bad Egg)
  a small value in a BP facility is the PRICE IN BP, not a species -- five
  Unbound sites compare 16, 25 or 27, which decode as Pidgey, Pikachu and
  Sandshrew.

Run:  python3 tools/tests/check_species_gates.py   (0 = ok, 1 = changed)
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from cm_tally import assert_tally          # noqa: E402

GAME = 'Pokémon Radical Red v4.1'
ROM = os.path.join(ROOT, 'rom/radicalred 4.1.gba')
ROM_BASE = 0x08000000
CHARMAP = os.path.join(ROOT, "tools/charmap.txt")

# special id of ChoosePartyMon in this engine family, MEASURED against this
# ROM's own scripts -- the two families do not agree.
CHOOSE_SPECIAL = 0x9f
WAITSTATE = 0x27

# (address of the NAME of id 0, stride) for this ROM's own tables. Measured
# per ROM: all four item tables sit at different addresses and the strides are
# 44 / 44 / 80 / 84. NEVER copy one of these from a sibling port.
ITEM_TABLE = (0x093c0000, 44)
SPECIES_TABLE = (0x094042cc, 11)
# (id, name) pairs read out of those two tables when this file was written.
# ⚠️ At least one probe is deliberately FAR from the base: a wrong STRIDE is
# invisible at id 1 and shows up only at a high index. That is not
# hypothetical -- an early version of this work carried a sibling's stride for
# Seaglass, read ids 1-4 correctly, and decoded item 51 as mojibake.
# Species id 386 is pinned in the FireRed pair on purpose: it is Volbeat, not
# the national-dex 386, which is the trap `CHARACTER_ROSTER_PLAN.md` records.
ITEM_PROBES = ((1, 'Master Ball'), (533, 'Venusaurite'))
SPECIES_PROBES = ((1, 'Bulbasaur'), (386, 'Volbeat'))

# Every ChoosePartyMon call site in the ROM. A site being here is not a claim
# that anyone has looked at it; GATES holds the ones that were decoded.
SITES = (
    0x08168df0,
    0x0816b28f,
    0x0816d8b8,
    0x0816e370,
    0x0816ffb0,
    0x081720a0,
    0x081a8cbd,
    0x08801711,
    0x08801861,
    0x09044fbe,
    0x09046a2d,
    0x09047c31,
    0x090483b5,
    0x0904aba6,
    0x0904ad11,
    0x0904c37c,
    0x0904c3ee,
    0x0904c8f0,
    0x0904c90b,
    0x0904dd38,
    0x090512da,
    0x09051614,
    0x0905164b,
    0x09051716,
    0x0905174d,
    0x09051814,
    0x0905184b,
    0x0905316c,
    0x09053612,
    0x090544aa,
    0x09054900,
    0x09054bf9,
    0x09054cbc,
    0x09055339,
    0x0905607c,
    0x09057c4e,
    0x090582d3,
    0x090597b1,
    0x090597e8,
    0x0905987f,
    0x090598b6,
    0x0905994b,
    0x09059982,
)

# address -> (label, gate species ids, ((give address, item id, qty), ...),
#             verdict, what it actually gives)
#   SPECIES_LOCKED      the reward only works on the species that opens the
#                       gate, so a character who cannot keep that species
#                       loses nothing of value
#   ELSEWHERE           the reward is generic but obtainable another way in
#                       this same ROM (measured, with the other source named)
#   CATCH_ONLY          the reward is generic and has no other source, but
#                       the gate needs a species the catch gate already
#                       refuses. ⚠️ Whether an in-game trade or a computed
#                       gift egg could still deliver that species into the PC
#                       is NOT established here -- so this verdict bounds the
#                       cost, it does not prove it is zero
GATES = {
 0x0816b28f: (
  'Name Rater -- the species in its dialogue are examples',
  (),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x0816ffb0: (
  'Magikarp size judge -- "That doesn\'t look much like a Magikarp"',
  (),
  ((0x0817003c, 6, 1),),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Net Ball x1'),
 0x081720a0: (
  'Heracross size judge (native test, special 0x78)',
  (),
  ((0x0817212c, 8, 1),),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Nest Ball x1'),
 0x09047c31: (
  'Latias / Latios researcher',
  (407, 408),
  ((0x09047c87, 191, 1), (0x09047c93, 571, 1), (0x09047cbe, 191, 1), (0x09047cca, 572, 1)),
  'SPECIES_LOCKED',
  'rewards seen in the window between this site and the next call site:'
  ' Soul Dew x1, Latiasite x1, Soul Dew x1, Latiosite x1'),
 0x090483b5: (
  'form-item collector -- Forces of Nature, Kyurem, Hoopa',
  (694, 695, 696, 697, 698, 699, 754, 755, 756, 828, 829, 1312, 1313),
  ((0x090484b0, 481, 1), (0x090484d2, 480, 1), (0x090484f4, 482, 1)),
  'SPECIES_LOCKED',
  'rewards seen in the window between this site and the next call site:'
  ' Reveal Glass x1, DNA Splicers x1, PrisonBottle x1'),
 0x0904c37c: (
  'gender swapper (native list, callasm 0x09077B59)',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x0905316c: (
  'Sharpedo -- Sharpedonite',
  (331,),
  ((0x090531bb, 563, 1),),
  'SPECIES_LOCKED',
  'rewards seen in the window between this site and the next call site:'
  ' Sharpedonite x1'),
 0x0905607c: (
  'form changer -- its neighbouring text is a Rotom/Mimikyu form list',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09057c4e: (
  'Silvally memory swapper',
  (990, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x090582d3: (
  'Mega Evolution researcher -- Kanto starters',
  (),
  ((0x09058338, 533, 1), (0x09058363, 534, 1), (0x09058374, 535, 1), (0x09058396, 536, 1), (0x090583b8, 554, 1), (0x090583da, 556, 1), (0x090583fc, 555, 1)),
  'SPECIES_LOCKED',
  'rewards seen in the window between this site and the next call site:'
  ' Venusaurite x1, CharzarditeX x1, CharzarditeY x1, Blastoisnite x1,'
  ' Sceptilite x1, Swampertite x1, Blazikenite x1'),
 0x0905994b: (
  'healer -- the Jigglypuff in its text is a battle reference',
  (),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x09059982: (
  'healer -- same NPC family',
  (),
  ((0x09059ac7, 593, 1),),
  'NOT_A_GATE',
  'rewards seen in the window between this site and the next call site:'
  ' Psychium Z x1'),
}

# ---------------------------------------------------------------- non-catch
# ⭐ THE ONLY PART OF THIS CLASS THE PC-WITHDRAW HOOK CAN BE BLAMED FOR.
# Character Mode's catch gate has always refused an off-roster catch, so a gate
# whose species you could only CATCH was already out of reach before the hook
# existed. A gate species that arrives as a GIFT, an EGG or a TRADE lands in the
# party, gets swept into the PC by enforcement -- and before the hook, could be
# withdrawn and shown to the NPC. Measured 2026-09-11; rowe_parity.md §13.42.
#
# (file offset of sInGameTrades, records, species field offset, ((idx, given), ...))
# ⚠️ The 60-byte struct is NOT the same 60 bytes in the two engine families:
# `species` is at +12 in the FireRed pair and +14 in the Emerald pair.
TRADES = (2543500, 9, 12, ((0, 1216), (1, 508), (2, 1167), (3, 1213), (4, 995), (5, 1169), (6, 848), (7, 494), (8, 1153)))
# (rom address of a givemon, species, level) -- only the sites that matter to a
# gate, each hand-decoded.
GIFTS = ((151306470, 129, 5), (151280240, 532, 30))
# gate site -> ((how its species can arrive without a catch, what it costs), ...)
REACHABLE = {
 0x0816ffb0: (
  ('Magikarp via the 0x0904C0E6 gift',
   'ELSEWHERE anyway -- the Net Ball is sold in the ball mart'),
 ),
 0x0905607c: (
  ('Rotom 532 via the 0x09045A70 gift ("This is default Rotom."),'
   ' Mimikyu via trade #4',
   'SPECIES_LOCKED anyway -- a form change is inert without the species'),
 ),
}

EXPECT_CHECKS = 9

failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


def charmap():
    import re
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    for line in open(CHARMAP, encoding="utf-8"):
        m = pat.match(line.rstrip("\n"))
        if m:
            table[int(m.group(2), 16)] = m.group(1)
    table[0x00] = " "
    return table


def name_at(b, cm, addr, limit):
    out = []
    for i in range(limit):
        c = b[addr - ROM_BASE + i]
        if c == 0xFF:
            break
        out.append(cm.get(c, "."))
    return "".join(out).strip()


def item_name(b, cm, n):
    base, stride = ITEM_TABLE
    return name_at(b, cm, base + n * stride, min(stride, 14))


def species_name(b, cm, n):
    base, stride = SPECIES_TABLE
    return name_at(b, cm, base + n * stride, min(stride, 12))


def scan_sites(b):
    """Every `special ChoosePartyMon; waitstate` in the ROM."""
    found = []
    pat = bytes((0x25, CHOOSE_SPECIAL, 0x00))
    i = b.find(pat)
    while i >= 0:
        if i + 3 < len(b) and b[i + 3] == WAITSTATE:
            found.append(ROM_BASE + i)
        i = b.find(pat, i + 1)
    return found


def compares(b, addr, span=0x140):
    """Every compare-var-to-value operand in the window after a site."""
    out = []
    o = addr - ROM_BASE
    for i in range(o, min(len(b) - 5, o + span)):
        if b[i] == 0x21:
            var = struct.unpack_from("<H", b, i + 1)[0]
            if var in (0x8000, 0x8004, 0x8005, 0x8006, 0x800D):
                out.append(struct.unpack_from("<H", b, i + 3)[0])
    return out


def main():
    if not os.path.isfile(ROM):
        print("base ROM not found: %s" % os.path.relpath(ROM, ROOT))
        return 1
    with open(ROM, "rb") as f:
        b = f.read()
    cm = charmap()

    found = scan_sites(b)
    print("%s -- %d ChoosePartyMon (special %#04x) call site(s), "
          "%d inventoried, %d decoded\n"
          % (GAME, len(found), CHOOSE_SPECIAL, len(SITES), len(GATES)))

    # A scanner that resolves nothing finds nothing, and an empty result
    # satisfies every set comparison below. Zero is never a pass.
    check("the scan reached at least one call site", bool(found),
          "no site at all -- the special id or the ROM is wrong, not the data")

    new = sorted(set(found) - set(SITES))
    check("every ChoosePartyMon call site in the ROM is inventoried",
          not new,
          ", ".join("%#010x" % a for a in new)
          + " -- a way to hand a Pokemon to an NPC that nobody has looked at")

    gone = sorted(set(SITES) - set(found))
    check("every inventoried call site is still present in the ROM",
          not gone, ", ".join("%#010x" % a for a in gone))

    bad = []
    for addr, (_label, ids, _rew, _v, _why) in sorted(GATES.items()):
        seen = compares(b, addr)
        missing = [i for i in ids if i not in seen]
        if missing:
            bad.append("%#010x wants %s" % (addr, missing))
    check("every decoded gate still compares its recorded species",
          not bad, "; ".join(bad))

    bad = []
    for addr, (_label, _ids, rew, _v, _why) in sorted(GATES.items()):
        for give, item, qty in rew:
            o = give - ROM_BASE
            ok = (b[o:o + 3] == bytes((0x1A, 0x00, 0x80))
                  and struct.unpack_from("<H", b, o + 3)[0] == item
                  and b[o + 5:o + 8] == bytes((0x1A, 0x01, 0x80))
                  and struct.unpack_from("<H", b, o + 8)[0] == qty
                  and b[o + 10:o + 12] == bytes((0x09, 0x00)))
            if not ok:
                bad.append("%#010x is no longer `give item %d x%d`"
                           % (give, item, qty))
    check("every recorded reward still gives that item, at that address",
          not bad, "; ".join(bad))

    # The two name tables are the reason a reward can be READ at all. If one
    # moves, every verdict above describes the wrong item or the wrong
    # species, and every set check above still passes. The probes are
    # deliberately not empty in any port: a check over GATES alone would be
    # vacuous in the game whose only gate is tested in native code and gives
    # no item.
    bad = ["%d reads %r, recorded %r" % (n, item_name(b, cm, n), want)
           for n, want in ITEM_PROBES if item_name(b, cm, n) != want]
    check("the item-name table still reads what this file recorded",
          ITEM_PROBES and not bad, "; ".join(bad) or "no probe is pinned")

    bad = ["%d reads %r, recorded %r" % (n, species_name(b, cm, n), want)
           for n, want in SPECIES_PROBES if species_name(b, cm, n) != want]
    check("the species-name table still reads what this file recorded",
          SPECIES_PROBES and not bad, "; ".join(bad) or "no probe is pinned")

    # The trade table is the one non-catch route that is pure DATA, so it is
    # pinned by content: a moved table or a changed gift makes the reachability
    # claim above describe a ROM this is not running on.
    toff, tn, tsp, tgives = TRADES
    bad = []
    for idx, want in tgives:
        got = struct.unpack_from("<H", b, toff + idx * 60 + tsp)[0]
        if got != want:
            bad.append("trade #%d gives %d (%s), recorded %d (%s)"
                       % (idx, got, species_name(b, cm, got), want,
                          species_name(b, cm, want)))
    check("every in-game trade still gives the species recorded here",
          tgives and not bad, "; ".join(bad) or "no trade is pinned")

    bad = []
    for addr, species, level in GIFTS:
        o = addr - ROM_BASE
        if not (b[o] == 0x79
                and struct.unpack_from("<H", b, o + 1)[0] == species
                and b[o + 3] == level):
            bad.append("%#010x is no longer `givemon %d, %d`"
                       % (addr, species, level))
    check("every gift Pokemon that opens a gate is still that gift",
          not bad, "; ".join(bad))

    if REACHABLE:
        print("\n  🔴 gate(s) whose species can arrive WITHOUT being caught "
              "-- the PC hook's own cost:")
        for site in sorted(REACHABLE):
            print("     %#010x  %s" % (site, GATES[site][0][:64]))
            for how, cost in REACHABLE[site]:
                print("        %s\n          -> %s" % (how, cost))
    else:
        print("\n  ✅ no gate in this game can be opened with a Pokemon the "
              "player did not catch")

    counts = {}
    for _l, _i, _r, verdict, _w in GATES.values():
        counts[verdict] = counts.get(verdict, 0) + 1
    if counts:
        print("\n  verdicts: " + ", ".join("%d %s" % (counts[k], k)
                                           for k in sorted(counts)))
    for addr in sorted(GATES):
        label, ids, rew, verdict, why = GATES[addr]
        print("\n  %#010x  %s" % (addr, verdict))
        print("     %s" % label)
        if ids:
            print("     gate: %s" % ", ".join(
                "%d %s" % (i, species_name(b, cm, i)) for i in ids[:8])
                + (" (+%d more)" % (len(ids) - 8) if len(ids) > 8 else ""))
        else:
            print("     gate: tested in NATIVE code -- no script operand")
        for give, item, qty in rew:
            print("     gives: %#010x item %d x%d  %s"
                  % (give, item, qty, item_name(b, cm, item)))
        print("     %s" % why)

    if assert_tally(checks_run, EXPECT_CHECKS, "check_species_gates"):
        return 1
    print("\n%s" % ("ALL PASS" if not failures
                     else "FAILURES: " + ", ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
