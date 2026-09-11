# SPECIES GATES — Radical Red v4.1

**43 `ChoosePartyMon` call sites, 12 classified, 9 of them
real species gates.** Only **20** of the call sites are reachable from a
dialogue anchor, which is why every earlier count of this class was wrong.
Measured 2026-09-11; pinned by `tools/tests/check_species_gates.py` (7 checks,
negative-tested).

A *species gate* is an NPC that wants a Pokémon **shown** rather than traded:
it calls `ChoosePartyMon`, tests what you handed it, and gives something back.

## The verdict

**This game really does cost nothing.** Seven of its nine gates hand over an
item that only works on the species that opened them — a Mega Stone, a Soul
Dew, a Reveal Glass, a Silvally memory, a gender flip — and the two generic
rewards are a **Net Ball** and a **Nest Ball**, both sold in the ball mart at
`0x0816BB74`. Nothing here has no other source.

## Every classified site

| site | what it is | gate species | rewards seen in its window | verdict |
|---|---|---|---|---|
| `0x0816b28f` | Name Rater -- the species in its dialogue are examples | Nidorino (33), Psyduck (54), Cubone (104) | — | `NOT_A_GATE` |
| `0x0816ffb0` | Magikarp size judge -- "That doesn't look much like a Magikarp" | Magikarp (129) | Net Ball ×1 | `ELSEWHERE` |
| `0x081720a0` | Heracross size judge (native test, special 0x78) | Heracross (214) | Nest Ball ×1 | `ELSEWHERE` |
| `0x09047c31` | Latias / Latios researcher | Latias (407), Latios (408) | Soul Dew ×1, Latiasite ×1, Soul Dew ×1, Latiosite ×1 | `SPECIES_LOCKED` |
| `0x090483b5` | form-item collector -- Forces of Nature, Kyurem, Hoopa | Tornadus (694), Thundurus (695), Reshiram (696), Zekrom (697), Landorus (698) +8 | Reveal Glass ×1, DNA Splicers ×1, PrisonBottle ×1 | `SPECIES_LOCKED` |
| `0x0904c37c` | gender swapper (native list, callasm 0x09077B59) | *tested in native code* | — | `SPECIES_LOCKED` |
| `0x0905316c` | Sharpedo -- Sharpedonite | Sharpedo (331) | Sharpedonite ×1 | `SPECIES_LOCKED` |
| `0x0905607c` | form changer -- its neighbouring text is a Rotom/Mimikyu form list | Marshtomp (284), Swampert (285), Rotom (532), Mimikyu (995), Rillaboom (1104) | — | `SPECIES_LOCKED` |
| `0x09057c4e` | Silvally memory swapper | Silvally (990), Silvally (1048), Silvally (1049), Silvally (1050), Silvally (1051) +13 | — | `SPECIES_LOCKED` |
| `0x090582d3` | Mega Evolution researcher -- Kanto starters | *tested in native code* | Venusaurite ×1, CharzarditeX ×1, CharzarditeY ×1, Blastoisnite ×1, Sceptilite ×1, Swampertite ×1, Blazikenite ×1 | `SPECIES_LOCKED` |
| `0x0905994b` | healer -- the Jigglypuff in its text is a battle reference | Jigglypuff (39) | — | `NOT_A_GATE` |
| `0x09059982` | healer -- same NPC family | Jigglypuff (39) | Psychium Z ×1 | `NOT_A_GATE` |

`CANDIDATE` means a species is named in the dialogue or compared in the window
and **nobody has read the script yet**. Rewards are those found between this
call site and the next one; that is a window, not a proof of reachability,
except for the gates whose scripts were decoded by hand (every
`SPECIES_LOCKED`, `ELSEWHERE` and `UNIQUE` row).

## What "UNIQUE" is a floor of, not a proof

`UNIQUE` means: the item appears in **no `pokemart` table in this ROM** and at
**no other site matching the three-command give-item idiom**
(`setorcopyvar 0x8000,item; setorcopyvar 0x8001,qty; callstd 0`). Three sources
are invisible to both scans and would each falsify it — a **ground item**
(the item id lives in the map's object data, not in a script), an item handed
out by **native code**, and **Pickup**. Treat `UNIQUE` as "no cheap source
found", the same way `check_gift_eggs.py` treats its inventory as a floor.

## Why every earlier count of this class was wrong

`rowe_parity.md` §13.28 published **5 / 5 / 2 / 0** species gates for Radical
Red / Unbound / Lazarus / Seaglass. §13.37 then decoded those and concluded the
class costs one TM. Both numbers came from sites reachable by a
**dialogue-anchored walk** — the primitive `check_gift_eggs.py` uses, and the
correct one there. It is the wrong primitive here, measurably:

| game | `ChoosePartyMon` call sites | reachable from a dialogue anchor |
|---|---|---|
| Radical Red | **43** | 20 |
| Unbound | **76** | 26 |
| Lazarus | **19** | 3 |
| Seaglass | **11** | 2 |

⚠️ **And decoding only the reachable subset reproduced the same error one level
down**: §13.37 read the walk-reachable gates, found them all inert or cheap,
and generalised to the class. The sites it never opened contain a Master Ball,
an Eviolite, a Moon Stone, an Air Balloon, a Destiny Knot, a Rare Candy, a
Protein and two Elixirs. **The fix is to enumerate on the call site itself**
(`special <ChoosePartyMon>` followed by `waitstate`), which is what the checker
now pins.

## Two primitives, because each is blind where the other sees

- **A species COMPARE** in the window after the call. Blind whenever the test
  lives in native code — Radical Red's Heracross judge (`special 0x78`) and
  gender swapper (`callasm`), Unbound's Deoxys and Rotom (`callasm`), and
  Seaglass's DEOXYS trick (`special 0x224`) have no species operand at all.
- **A species NAMED in the surrounding dialogue**, matched against this ROM's
  own species-name table. Blind whenever the NPC never says the name, and
  blind to species a curated dex has removed — Lazarus's own big-SEEDOT judge
  is invisible to it, because Seedot is not in Lazarus's dex.

## Four false-positive constants, each of which decodes as a species

- **255** — `PARTY_NOTHING_CHOSEN` in the Emerald pair. Decodes as Torchic.
- **412** — `SPECIES_EGG` in the FireRed pair. Decodes as Bad Egg.
- **`SPECIES_EGG` in the Emerald pair is PER-ROM**, one past that ROM's own
  species table: **1561** in Lazarus, **1524** in Seaglass. The Name Rater and
  the egg kid compare it in both games.
- **A small value after the choice is a PRICE or a SCORE, not a species.**
  Inside a BP facility it is the price in BP (five Unbound sites compare 16, 25
  or 27 — Pidgey, Pikachu, Sandshrew); inside an **IV judge** it is an IV
  total (both Emerald ports compare **120 / 150 / 151** — Staryu, Mewtwo, Mew).

## Re-running it

```bash
python3 tools/tests/check_species_gates.py                   # the inventory
python3 tools/tests/check_species_gates_negative_test.py     # break it on purpose
```

Both read the **base ROM** and this repo's own vendored `tools/charmap.txt`;
they build nothing and change nothing.
