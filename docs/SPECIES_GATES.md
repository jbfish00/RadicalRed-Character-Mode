# SPECIES GATES — Radical Red v4.1

**5 decoded gate(s) out of 43 ChoosePartyMon call sites** (20
of them reachable from a dialogue anchor). Measured 2026-09-11; pinned by
`tools/tests/check_species_gates.py` (7 checks, negative-tested).

A *species gate* is an NPC that wants a Pokémon **shown** rather than traded:
it calls `ChoosePartyMon`, tests what you handed it, and gives something back.
It matters to Character Mode because the PC-withdraw fix (`rowe_parity.md`
§13.26c, option 1) sweeps an off-roster Pokémon back into the PC the moment
you leave the storage system, so you can no longer carry one to an NPC.
§13.28 counted these NPCs and said plainly that **nobody had decoded what any
of them give**, leaving the cost an upper bound. This is the decode.

## The verdict

**The five gates cost this game nothing.** Four hand over something that
only works on the species that opened the gate — a Mega Stone, a form item, a
Silvally memory, a gender flip — and the fifth gives one Nest Ball, which the
ball mart sells.

## The gates

| site | NPC | gate | what it actually gives | verdict |
|---|---|---|---|---|
| `0x081720A0` | Heracross size judge — *"That's a Heracross! may I measure how big it is?"* | Heracross, tested in **native code** (`special 0x78`) | **one Nest Ball** (item 8 at `0x0817212C`) + flag `0x2D9` | `ELSEWHERE` — Nest Balls are sold at the ball mart (table `0x0816BB74`) |
| `0x090483B5` | form-item collector — *"If you show me one that's compatible, I'll gladly hand it over!"* | Tornadus, Thundurus, Landorus (both formes), Enamorus, Kyurem, Reshiram, Zekrom, Hoopa — 13 ids | **Reveal Glass** (481), **DNA Splicers** (480), **Prison Bottle** (482) | `SPECIES_LOCKED` |
| `0x09057C4E` | Silvally memory swapper | Silvally, 18 form ids | a **form change**, no item at all | `SPECIES_LOCKED` |
| `0x090582D3` | Mega Evolution researcher — *"show me a fully evolved Kanto starter capable of Mega Evolution"* | Venusaur (3), Charizard (6), Blastoise (9) | the **corresponding Mega Stone** — Venusaurite / Charizardite X / Charizardite Y / Blastoisinite, one flag each (`0x966`–`0x968`); the same tail carries Sceptilite / Blazikenite / Swampertite behind `0x969`/`0x97A`/`0x97B` | `SPECIES_LOCKED` |
| `0x0904C37C` | gender swapper | nine species named only in its own dialogue (Snorunt, Ralts, Kirlia, Salandit, Burmy, Combee, Espurr, Basculin, Lechonk); eligibility is a `callasm 0x09077B59` | a **gender flip**, no item | `SPECIES_LOCKED` |

## Why the raw count was never a count

`rowe_parity.md` §13.28 published **5 / 5 / 2 / 0** species gates for Radical
Red / Unbound / Lazarus / Seaglass, found by decoding forward from dialogue
anchors — the same primitive `check_gift_eggs.py` uses, and the right one
there. It is the wrong one here. Measured 2026-09-11, that walk reaches:

| game | ChoosePartyMon call sites in the ROM | reachable from a dialogue anchor |
|---|---|---|
| Radical Red | **43** | 20 |
| Unbound | **76** | 26 |
| Lazarus | **19** | 3 |
| Seaglass | **11** | 2 |

So between 47% and **84%** of the call sites were never seen. The sites the
walk misses are real — Name Rater, move tutors, the *"Hunh? Your BAG is
crammed full."* item NPCs, and in Unbound four more sites of the Deoxys
meteorite and the Rotom appliances, two of the very NPCs §13.28 named. ⭐ **The
better primitive is the call site itself**: `special <ChoosePartyMon>`
immediately followed by `waitstate`, which every real site has and which no
dialogue reachability question can hide. `tools/tests/check_species_gates.py`
pins the whole set that way.

⚠️ **This document does not claim every one of those sites has been decoded.**
The ones that have are in the table above; the rest are pinned by address, so
a new one cannot arrive silently, and a decode of the remainder is open work.

## Three false-positive constants, all of which decode as a species

Each sits immediately after a `ChoosePartyMon` and looks exactly like a
species gate:

- **255** — `PARTY_NOTHING_CHOSEN` in the Emerald pair. Decodes as Torchic.
- **412** — `SPECIES_EGG` in the FireRed pair. Decodes as Bad Egg.
- **a small value inside a BP facility is the PRICE IN BP**, not a species.
  Five Unbound sites compare 16, 25 or 27 right after the choice; those decode
  as Pidgey, Pikachu and Sandshrew, and all five are Battle-Frontier-style
  services whose own dialogue says *"You don't have enough BP"*.

## A species test can be invisible to every compare scan

Four of the gates in this workspace test the species in **native code**, so
the species id never appears as a script operand at all:

| game | NPC | where the test lives |
|---|---|---|
| Radical Red | Heracross size judge | `special 0x78` |
| Radical Red | gender swapper | `callasm 0x09077B59` |
| Unbound | Deoxys meteorite | `callasm 0x088AB3CD` |
| Unbound | Rotom appliances | `callasm 0x088AABB9` / `0x088AACCD` |
| Seaglass | DEOXYS magic trick | `special 0x224` |

They are in the inventory because the **dialogue** was decoded, not because a
scan found them. Any future count of this class is a floor for the same
reason `check_gift_eggs.py` documents for `giveegg`.

## Re-running it

```bash
python3 tools/tests/check_species_gates.py                   # the inventory
python3 tools/tests/check_species_gates_negative_test.py     # break it on purpose
```

The checker reads the **base ROM** and this repo's own vendored
`tools/charmap.txt`; it builds nothing and changes nothing.
