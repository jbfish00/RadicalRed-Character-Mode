# Routine map

RE findings/anchors for this project — the project's "symbol table". Tag every entry CONFIRMED / STRING ANCHOR / LIKELY / UNKNOWN, and record ruled-out false leads explicitly so they aren't re-tried.

## CONFIRMED — text-rendering convention differs from vanilla FireRed/Unbound

Radical Red uses **mixed-case text**, not vanilla FRLG's ALL-CAPS convention:
- `"TRAINER"` (all caps): 0 hits. `"Trainer"` (mixed case, `--icase`): **360 hits**.
- `"POKEMON"` (all caps): 0 hits. `"Pokemon"` (mixed case): 5 hits. `"pokemon"` (lowercase): 1 hit.
- `"SAVE"` (all caps, exact case): 1 hit at file offset `0x0110004E`, decodes to a developer diagnostic string: *"WRONG SAVE TYPE! Please change to Flash 128k. Consult the Discord if you need help."* — confirms this is genuinely Radical Red's own custom content (not vanilla leftover text) and that it targets Flash 128k save type.

**Implication for all future `search_gametext.py` runs on this ROM: always pass `--icase`, or better, search for the expected mixed-case rendering directly** (e.g. `"Trainer"` not `"TRAINER"`) — plain vanilla-style all-caps queries will silently miss almost everything. This is a real divergence from both vanilla FRLG and Unbound's apparent text convention, worth remembering before assuming any porting the Unbound anchors 1:1.

## STRING ANCHOR — catch-message bank / battle strings table

- `"Gotcha"` (mixed-case) found at file offsets `0x3FD7A2` and `0x3FD7C0`, decoding to the expected "Gotcha!\n[name] was caught!" / nickname-prompt text.
- Both offsets are referenced exactly once each, from consecutive pointer-table slots `0x3FE338`/`0x3FE33C`.
- The surrounding region (`0x3FE200`–`0x3FE4FC` and likely beyond in both directions, not yet fully bounded) is an unbroken run of valid `0x08xxxxxx`/`0x09xxxxxx` pointers — the same `gBattleStringsTable`-shaped large contiguous pointer array Unbound found in its own ROM (there at `0x3FDF3C`–`0x3FE514`, ~374 entries).
- Per `docs/CFRU_CROSSWALK.md`, CFRU's public source (`src/catching.c`'s `atkF0_givecaughtmon`) explains exactly what consumes this table and calls `GiveMonToPlayer()` on success — strong converging evidence this is the real catch-completion path, though the exact function address in the compiled RR binary is not yet isolated (needs XREF work on the ~consecutive call sites referencing this table, same next step Unbound is on).
- Not yet bounded: full table start/end offsets (only ~190 entries dumped so far, `0x3FE200`-`0x3FE4FC`), and which of the (likely dozens of) referencing call sites is `atkF0_givecaughtmon` specifically vs. other generic battle-message users.

## CONFIRMED — CFRU's expanded ball roster is present in-ROM

`"Beast Ball"` (2 hits) and `"Dream Ball"` (2 hits) found as mixed-case text — corroborates that Radical Red carries CFRU's Gen 7+ ball additions (`catching.c`'s `GetBaseBallCatchOdds` references `BALL_TYPE_BEAST_BALL`, `BALL_TYPE_DREAM_BALL`, etc.), further supporting the CFRU-lineage hypothesis at the binary level, not just via community/web research.

## STRING ANCHOR — catch/PC message bank further confirmed

Additional hits within the same `0x3FD7xx`–`0x3FD9xx` region already identified above (see the Gotcha table entry):
- `"Box is full"` at `0x3FD87A`, decodes to `"The Box is full!\nYou can't catch any more!"` — the PC-full block ROWE/Unbound's `SendMonToPC`-fallback messaging maps to.
- `"sent to"` at `0x3FD80B`, decodes to `"[mon] was sent to\n[box] PC."` — the standard "party full, mon auto-boxed" message.
Both reinforce that this whole file region is the shared catch/PC battle-string bank (same conclusion as Unbound's, same relative ROM neighborhood — strong signal the underlying vanilla/CFRU battle-message table hasn't moved much across these two FireRed-based hacks).

## STRING ANCHOR — Mystery Gift

`"Mystery Gift"` (mixed-case): 10 hits; first at `0x1A6317` decodes to Mystery-Gift tutorial/explainer dialogue (*"...must know about the Mystery Gift. From now on, you should be receiving Mystery Gifts!"*) — this is NPC/tutorial dialogue, not necessarily the gift-delivery routine itself, but a solid anchor for locating the surrounding script (likely Professor Oak or an equivalent tutorial NPC). `"Wonder Card"` also found, 17 hits, first at `0x41E648` — not yet decoded/investigated further. Per `docs/CFRU_CROSSWALK.md`, the actual Mystery Gift delivery internals (`mevent.h`'s two opaque `sub_XXXXXXX` stubs) have no CFRU source — expect this to require the same blind XREF/pointer work as Unbound's approach once a delivery-relevant (not just tutorial) anchor is found.

## RULED OUT — false leads (don't re-try)

- `"Would you like to trade more Berry Powder for something else?"` (`0x1933BD`) — this is a **Berry Powder shop/exchange NPC**, not a Pokemon trade. Don't treat `"trade"` substring hits as Pokemon-trade-specific without decoding context first.
- `"Take good care of"` (`0x193CAE`) — decoded context mixes with Day Care ("That is merely an Egg!") dialogue; inconclusive whether this is genuine in-game Pokemon trade text or Day Care text reusing similar phrasing. Needs re-verification before treating as a trade anchor.
- `"your trade"` (`0x1BC8FA`) — decodes to Union Room/wireless-adapter trade UI text ("...start your trade... Trainer Card data will be overwritten"), not a standard in-game NPC trade script.
- No definitive in-game NPC-trade dialogue anchor found yet this session (tried "Would you like to trade", "I'll trade you" [apostrophe unsupported by charmap search], "Excellent! Take good care", "linked to trade", "wants to trade" — all misses or false positives above). Needs another pass, possibly searching for specific vanilla FRLG trade NPC names/species pairs once candidate trainers are identified another way (e.g. via `dump_all_strings.py` open-ended scan of a likely map/script region).

## STRING ANCHOR (promising but UNCONFIRMED positional mapping) — species name table / Pokedex flavor-text region

Found a species-name-containing region starting around file offset `0x014042D7` ("Bulbasaur"), immediately preceded by ~19 KB of Pokédex flavor-text entries (`0x01403B01`–`0x014042CA`, all decode cleanly as genuine dex flavor text, including entries mentioning Paldean lore — e.g. "ancient Paldea", "Pecharunt's control" — confirming Gen 9 Pokédex content really exists in this ROM). Sequential names decode correctly for a short stretch (`Bulbasaur`, `Ivysaur`, `Venusaur`, `Charmander`, `Charmeleon`, `Charizard`, `Squirtle`...), **and Gen 9 species names were independently confirmed present elsewhere in the ROM** (`Sprigatito`/`Floragato`/`Meowscrada`[10-char-truncated]/`Fuecoco`/`Crocalor`/`Skeledirge`/`Quaxly`/`Quaquaval`/`Gholdengo`/`Tinkaton`/`Armarouge`/`Koraidon`/`Miraidon` all found via direct text search, `0x01406xxx`–`0x01407xxx` region) — **this is solid confirmation Radical Red genuinely has the full Gen 1-9 species roster as real content**, not just Gen-9-flavored moves/abilities as the phrasing in earlier web research ambiguously suggested. This validates the user's full-Gen-1-9 roster scope choice.

**However: the simple "table index = species ID" hypothesis that worked for Unbound does NOT hold here on first attempt.** Walking forward from the confirmed `Bulbasaur` entry with naive 0xFF-delimited sequential indexing produces a mismatch almost immediately — variable numbers of blank (empty-string) entries are interspersed between real names in a pattern that doesn't obviously correspond to Dex order gaps (e.g. `Bulbasaur, "", Ivysaur, "", "", "", Venusaur, "", "", Charmander, Charmeleon, Charizard, "", Squirtle, "", "", Wartortle...` — inconsistent blank counts, not a fixed stride). Spot-checking known CFRU-donor indices (25=Pikachu, 150=Mewtwo, 906=Sprigatito, etc.) against this naive walk all mismatched. Possible explanations, not yet investigated: (a) this may not be the actual runtime species-name-by-ID table at all, but some other list (a UI list, a "recently seen" cache, a Pokédex-order-not-ID-order table) that merely happens to contain real species names; (b) the real table interleaves alternate-form name slots per base species inconsistently with what CFRU's own `species.h` ID scheme would predict; (c) the decode script's entry-boundary logic (splitting purely on `0xFF`) may be misinterpreting some other control byte as a boundary. **Do not trust this table for positional species-ID resolution without further work** — needs a next session's focused attention (walk more of the table by hand/script, compare directly against `tools/cfru_donor/include/constants/species.h`'s full ordered list rather than a handful of spot checks, and/or find corroborating evidence like a separate species-ID-indexed base-stats table with a more rigid fixed-size record format that's easier to walk reliably). Raw dump of the first 1400 naive-walk entries saved to scratchpad for reference in a future session (not committed to the repo — regenerate via the same technique if needed, or redo more carefully).

## CONFIRMED — the real base-stats table, found via CFRU's fixed pointer-redirect mechanism, solves species-ID resolution for the ENTIRE roster (Gen 1-9)

**Superseding the two entries below this one (kept for the record, but their table-location conclusions were wrong — see correction).**

CFRU doesn't just leave `gBaseStats`/`gEvolutionTable` as raw symbols — `include/new/rom_locs.h` reveals it accesses them through a **fixed pointer-redirect slot**: `#define gBaseStats ((struct BaseStats*) *((u32*) 0x80001BC))` — i.e. a 4-byte pointer *value* stored at a fixed vanilla ROM address (file offset `0x1BC`), which the compiled game code dereferences to find wherever the real table actually lives (CFRU repoints vanilla tables elsewhere in ROM and just overwrites this one fixed slot to point at the new location). **This is directly readable in the compiled Radical Red binary without any disassembly** — just read 4 bytes at file offset `0x1BC` and subtract `0x08000000`.

Doing exactly that: the pointer at file offset `0x1BC` resolves to file offset `0x17B98EC`. Verified this as the true, code-referenced base-stats table (28-byte stride, same `struct BaseStats` layout as before) exhaustively:

| Index | Species | Result |
|---|---|---|
| 0 | SPECIES_NONE | all-zero record, as expected |
| 1 | Bulbasaur | exact match |
| 2 | Ivysaur | exact match |
| 3 | Venusaur | exact match |
| 4 | Charmander | exact match |
| 7 | Squirtle | exact match |
| 25 | Pikachu | **exact vanilla match** (35,55,40,90,50,50,13,13,190) — this CORRECTS the earlier claim below that RR rebalances Pikachu; that conclusion was drawn from the wrong (decoy/leftover) table. |
| 150 | Mewtwo | exact match |
| 151 | Mew | exact match |
| 1259 | SPECIES_ENAMORUS_THERIAN (stock CFRU's last Gen 8 species) | plausible real stats, table is coherent through the whole stock CFRU range |
| 1293 | SPECIES_URSHIFU_RAPID_GIGA (stock CFRU's `NUM_SPECIES - 1`) | plausible real stats |
| 1294–1375 | **82 additional species beyond stock CFRU's own range** | all plausible, coherent Pokémon-stat-shaped records (real types ≤ ~18-23, sane HP/stat distributions, sane catch rates) — **this is Radical Red's own Gen 9 extension**, appended contiguously right after stock CFRU's species range |
| 1376 | — | all-zero (terminator/reserved slot) |
| 1377+ | — | clearly different, non-stat-shaped data (repeating pointer-like byte patterns) — table has ended |

**Conclusion: `table_base = 0x17B98EC`, `stride = 28` bytes, and Radical Red's `NUM_SPECIES = 1376`** (indices `0`–`1375`), with indices `1294`–`1375` being Radical Red's own 82-entry Gen 9 addition beyond stock CFRU's `NUM_SPECIES` of 1294. This is now a **fully reliable, byte-exact species-ID authority for the entire roster**, Gen 1 through Gen 9 — no need to depend on the ambiguous variable-length name table at all for *existence/index* purposes. `map_species.py` can use `SPECIES_*` constants directly from `tools/cfru_donor/include/constants/species.h` for Gen 1-8 (cross-validated against this table), and can enumerate/validate the 82 Gen-9-range indices (1294-1375) directly via this table once each index is matched to a real species name (still needed — see below).

**Transferable technique, worth reusing on Unbound too**: chasing CFRU's `rom_locs.h` fixed pointer-redirect slots (there are others besides `gBaseStats`) is a much higher-confidence, lower-effort technique than blind byte-pattern search or exhaustive text search — it works because the *slot address* is a CFRU-engine-level constant, not something Radical Red's own content could have moved, whereas the *target* it points to is naturally hack-specific and gets read out directly.

**Still needed**: matching each of the 82 Gen-9-range indices (1294-1375) to a real species name (see OPEN entry below).

## CONFIRMED — evolution table found the same way, EVOS_PER_MON=16 not stock CFRU's 5

The first attempt at `gEvolutionTable`'s fixed-pointer slot (`0x42F6C` per `rom_locs.h`) read all-zero data because it assumed stock CFRU's `EVOS_PER_MON=5` (40-byte block size) — **wrong assumption, not a wrong address**. Radical Red expanded this to **`EVOS_PER_MON=16`** (128-byte blocks, `16 * sizeof(struct Evolution)` where `struct Evolution` is 8 bytes: `u16 method, param, targetSpecies, unknown`) — the same expansion CFRU's own source comment flags DPE as using ("DPE has 16!!!"), so Radical Red apparently adopted the larger table too, likely to support more complex/precise evolution methods added in later generations.

With `table_base = 0x17CD9B0` (same target the pointer slot resolves to) and `stride = 128`, verified against known evolutions:

| Species | Found | Vanilla | Note |
|---|---|---|---|
| Bulbasaur (1) | EVO_LEVEL @ 16 → Ivysaur (2) | EVO_LEVEL @ 16 → Ivysaur | exact match |
| Ivysaur (2) | EVO_LEVEL @ **36** → Venusaur (3) | EVO_LEVEL @ 32 → Venusaur | **RR rebalance** — evolution level bumped from 32 to 36, target species correct. Plausible for a difficulty-focused hack (delayed evolutions are a common kaizo-hack pattern). |
| Charmander (4) | EVO_LEVEL @ 16 → Charmeleon (5) | same | exact match |
| Charmeleon (5) | EVO_LEVEL @ 36 → Charizard (6) | same | exact match |
| Squirtle (7) | EVO_LEVEL @ 16 → Wartortle (8) | same | exact match |
| Pikachu (25) | EVO_ITEM(7) param=96 → Raichu (26); **also** EVO_ITEM(7) param=99 → species **1022** | EVO_ITEM (Thunder Stone) → Raichu | Two evolution paths found — the second (different item param, target species 1022, a high/alt-form-range ID) is plausibly an Alolan Raichu / regional-form evolution path, consistent with Radical Red's confirmed regional-forms content. Not yet confirmed what species 1022 actually is (would need the same "match index to name" work as the Gen-9 range below). |

**This solves evolution-family-root reduction for the whole roster** (the mechanism `IsSpeciesAllowedForCharacter` needs to expand a roster entry to its full evolution family) — walk `gEvolutionTable[species]` (16 entries, 8 bytes each) at `table_base + species*128`, same as ROWE/Unbound's own evolution-walk logic, just with RR's own table location/stride.

## OLD FINDING (SUPERSEDED — kept for the record, do not reuse these conclusions)

<details>
<summary>Original (incorrect) base-stats table finding, based on a decoy/leftover table copy — click to expand</summary>

Following CFRU's `include/pokemon.h:510` `struct BaseStats` definition, searched the RR ROM for the raw byte sequences of several well-known vanilla base-stat records via plain substring search (not the pointer-redirect technique above) and found hits at file offset `0x2547A0` (computed `table_base=0x254784`). This looked plausible for indices 0-4, 7, 150, 151 but showed an apparent "Pikachu rebalance" (Def 30 vs vanilla 40, SpDef 40 vs vanilla 50) and implausible/garbage data starting around index 1290. **Both of those anomalies were artifacts of reading the wrong table** — `0x254784` is some other/leftover data in the ROM that happens to coincidentally match many vanilla base stats, not the table the compiled game code actually reads (confirmed by finding the REAL table via the pointer-redirect slot above, which shows unmodified vanilla Pikachu stats and coherent data all the way to index 1375). Lesson: prefer the fixed-pointer-redirect technique over raw byte-pattern search when both are available — pattern search can find decoy/dead data that happens to match.

</details>

## RESOLVED — all species names solved via an authoritative external donor, "1294-1375 = Gen 9" was WRONG

Species index **1022 confirmed as SPECIES_RAICHU_A (Alolan Raichu)** — cross-checked three ways: its base-stats record exactly matches real Alolan Raichu stats (HP60/Atk85/Def50/Spd110/SpAtk95/SpDef85, Electric/Psychic), CFRU's own `species.h` gives `SPECIES_RAICHU_A = 0x3FE` = 1022 exactly, and it showed up as Pikachu's second evolution target in the evolution-table finding below. This confirms the whole Gen 1-8 + alt-form index range (1-1293) matches CFRU's `species.h` numbering exactly, with no further per-species verification needed.

For the 82-entry "1294-1375" block and the rest of the roster, a background research agent found the authoritative source: **the community Radical Red Pokedex** (`dex.radicalred.net`, backed by `github.com/JwowSquared/Radical-Red-Pokedex`), which ships a full species database (`data.js`) with id, name, stats, type, evolutions, and a precomputed evolution-family-base (`ancestor`) field for every species in the ROM. Its stat/type tuples were cross-checked against all 82 of our independently-extracted 1294-1375 records — **all 82 matched exactly, byte-for-byte** — establishing it as authoritative rather than a guess.

**Important correction: indices 1294-1375 are NOT Radical Red's Gen 9 addition as originally assumed.** They're actually:
- **1294-1313 (20 entries)**: Hisuian forms, Origin formes, and other older-gen alternate forms (Voltorb/Electrode-Hisui, Typhlosion/Samurott/Decidueye-Hisui, Sneasler, Basculegion, Dialga/Palkia-Origin, Enamorus-Therian, Ursaluna, etc.) plus one Radical-Red-original custom form (Dhelmise-Sevii, part of RR's own "Sevii Forms" feature).
- **1314-1374 (60 entries)**: genuine Gen 9 Paldea additions, but only the *later* part of the Paldea dex (early/mid Paldea species like Nymble, Smoliv, Tandemaus, plus the Treasures of Ruin, Loyal Three-era Paradoxes, all four Ogerpon masks, and the Indigo Disk DLC wave).
- **Index 1375**: **"Chillet"** — not a real Pokemon at all, a joke/novelty **Palworld crossover** species Radical Red added (Ice/Dragon type, matching the extracted type bytes 15,16), confirmed via a third-party RR Pokedex mirror's own Chillet page.

**The actual Gen 9 starters and other early/mid-dex Paldea species are interspersed in the "normal" 1-1293 range**, much closer to National-Dex-adjacent order — e.g. **Sprigatito = species 921**, **Fuecoco = 924**, **Quaxly = 927**, **Koraidon = 1193**, **Miraidon = 1194**, **Gholdengo = 852**, **Tinkaton = 842**. This fully explains why the original vanilla-stat-pattern search for these species around index 1294+ found nothing — they were never there.

The full `data.js` donor is now checked into this project (`tools/character_mode/rr_pokedex_donor/data.js`, ~4.4 MB, provenance noted in `PROVENANCE.md` in that directory) and used directly by `map_species.py` as the primary species-ID/name source, superseding the `species.h`-derived-name-matching approach. **Result: 100% of the roster now resolves** (184 characters, 4652 species references, 0 unmatched, 0 empty rosters) — see the map_species.py section of `CLAUDE.md` for the full run summary.

## Not yet started

Gift/static-mon handoff routine confirmation (beyond the CFRU-source-level `ScriptGiveMon` lead), genuine in-game trade dialogue, starter-selection dialogue, intro/options-menu wording, sprite/trainer-card/battle-pic tables, and the Gen 9 species-ID range (see OPEN above).
