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

## RULED OUT — sprite/trainer-pic tables are NOT reachable via CFRU's fixed-pointer-redirect trick

Checked whether the pointer-redirect technique that solved `gBaseStats`/`gEvolutionTable` (see the CONFIRMED entries above) also applies to sprite tables, since it would be far cheaper than Ghidra. Result: it doesn't, for two different reasons —

- `tools/cfru_donor/include/new/rom_locs.h` only exposes a **small, specific set** of tables as dynamic pointer-redirect slots: `gBaseStats`, `gEvolutionTable`, `gSpeciesNames`, `gItems`, `gMonIconPaletteIndices`, plus a few battle/script one-offs (`gBitTable`, `gGameVersion`/`gGameLanguage`, `SafariZoneEndScript`, `sBasePaletteGammaTypes`, `sTutorLearnsets` (commented out)). No sprite-related table is in this list at all.
- `gTrainerFrontPicTable`/`gTrainerFrontPicPaletteTable`/`gTrainerFrontPicCoords` (`src/defines_battle.h`) exist in CFRU's source, but as **hardcoded compile-time addresses** (e.g. `0x823957C`), not pointer-redirect slots — meaning even stock CFRU doesn't relocate this table dynamically; it's just linked at a fixed spot in CFRU's own build. Radical Red's actual compiled binary has no obligation to have this table at the same address, since (unlike the redirect-slot tables, whose *slot* address is an engine-level constant regardless of where the hack's own build relocated the *target*) this address is purely an artifact of CFRU's own linker layout, which Radical Red's developers may have changed simply by adding enough new content before or after it in the link order.
- No public CFRU source at all references `gObjectEventGraphicsInfoPointers` (the vanilla FireRed overworld-sprite table) — same blind-RE position as Mystery Gift/trade internals.

**Conclusion**: sprite/trainer-pic/OW-graphics table addresses need Ghidra's data-type analysis or manual structure hunting to confirm for real, same conclusion Unbound already reached for its own sprite tables (see `../Unbound-Character-Mode/docs/ROUTINE_MAP.md`). Not worth another blind-pattern-search attempt given the CFRU-crosswalk bet already came up empty for this specific table class. Full asset-coverage planning (which characters have candidate donor art at all, independent of ROM addresses) is done instead — see `docs/SPRITE_COVERAGE.md`.

## CONFIRMED — gBattleStringsTable's real base, via CFRU's own hardcoded compile-time constant (not a redirect slot, but correct anyway)

`src/defines_battle.h` gives `#define gBattleStringsTable ((u8**) 0x83FDF3C)` — a **hardcoded compile-time address**, the same class of constant that turned out NOT to be trustworthy for the sprite tables (see the RULED OUT entry above). Tested it directly anyway, since it costs nothing: `include/battle_string_ids.h` gives `STRINGID_GOTCHAPKMNCAUGHT = 267` and `BATTLESTRINGS_ID_ADDER = 12` (`src/battle_strings.c`: `gBattleStringsTable[stringID - BATTLESTRINGS_ID_ADDER]`), so table index `267 - 12 = 255`, and `table_base(0x3FDF3C) + 255*4 = 0x3FE338` — **exactly** the already-found "Gotcha" table slot. Cross-checked the adjacent slot too: `STRINGID_GOTCHAPKMNCAUGHT2 = 268` → index 256 → `0x3FE33C`, which also holds the exact expected pointer (`0x083FD7C0`, the second Gotcha string). **`table_base = 0x3FDF3C` is now CONFIRMED byte-exact**, not just a plausible string-anchor neighborhood.

**Methodological correction to the sprite-table RULED OUT entry above**: hardcoded CFRU compile-time addresses are NOT uniformly untrustworthy — this one held exactly, while the sprite ones (untested directly, only reasoned about) might too. Worth empirically testing `gTrainerFrontPicTable` (`0x823957C`) and friends the same cheap way (read the bytes, check for a plausible `struct CompressedSpriteSheet`/coords shape) before assuming Ghidra is required — the "compile-time address, not a redirect slot" property alone doesn't predict whether a given hack's build moved it; only checking does.

## CONFIRMED — BattleScript_SuccessBallThrow's real address, and the `catchpoke`/`trysetcaughtmondexflags` opcode-to-mnemonic mapping

`src/catching.c` gives another hardcoded fallback: `#define BattleScript_SuccessBallThrow ((u8*) 0x81D9A42)` (used when `CAPTURE_EXPERIENCE` is *not* defined — stock CFRU's own `src/config.h` *does* define it, which would normally mean stock CFRU itself doesn't use this address, so this could easily have been link-order noise for Radical Red's own build). Tested anyway: read 80 raw bytes at file offset `0x1D9A42` and cross-checked against the annotated stock assembly source (`assembly/battle_scripts/fainting_battle_scripts.s:79`, `BattleScript_SuccessBallThrow`/`BattleScript_PrintCaughtMonInfo`/`BattleScript_CaughtPokemonSkipNewDex` labels). **Two independent byte-exact matches**, at different offsets within the same 80-byte window:
- `printstring 0x10B` (`STRINGID_GOTCHAPKMNCAUGHT`) — raw bytes `10 0B 01` found at script offset `+0xF` (file offset `0x1D9A51`), exactly where the source predicts (right after a `jumpifhalfword`+`incrementgamestat` pair whose own encoded jump target, `50 9A 1D 08` = `0x081D9A50`, correctly points at the very next instruction — the `BattleScript_PrintCaughtMonInfo` label position).
- `printstring 0x10F` (`STRINGID_PKMNDATAADDEDTODEX`) — raw bytes `10 0F 01` found at script offset `+0x16` (file offset `0x1D9A58`), also matching the source's second `printstring` a few instructions later.
- A `trysetcaughtmondexflags` call (opcode `0xF1` + 4-byte target, found via `battle_script_macros.s:1375`: `.macro trysetcaughtmondexflags rom_address` / `.byte 0xf1`) targets `0x081D9A63` — which matches the source's own `goto 0x81D9A63` from the `BattleScript_CaughtPokemonSkipNewDex` label seen a few lines later in the same source file. Third independent confirmation.

**`BattleScript_SuccessBallThrow = file offset 0x1D9A42` is CONFIRMED for this ROM**, three independent ways, despite the `CAPTURE_EXPERIENCE` caveat that should have made this untrustworthy in theory — empirical testing beat reasoning about it in advance, same lesson as the entry above.

**Also confirmed via `battle_script_macros.s`**: the assembly mnemonic that calls `atkF0_givecaughtmon` is `catchpoke` (`.macro catchpoke` / `.byte 0xf0` — single byte, no operand, dispatched through `gBattleScriptingCommandsTable[0xF0]`, matching the `atkF0_` function-naming convention exactly). `assembly/data/battle_script_commands_table.s:257`: `.word atkF0_givecaughtmon @catchpoke` confirms the same mapping from the table-definition side.

**NOT yet confirmed**: exactly where within (or near) `BattleScript_SuccessBallThrow`/`BattleScript_BallThrow` the `catchpoke` (`0xF0`) byte actually sits, or `atkF0_givecaughtmon`'s real compiled ARM/Thumb function address. Two raw `0xF0` bytes were spotted further into the 80-byte dump (script offsets `+0x30`/`+0x3E`), but **do not trust these** — without decoding every preceding instruction's exact operand width, a stray `0xF0` byte is just as likely to be the low byte of some other instruction's 4-byte address operand (very plausible on a GBA ROM, where 4-byte literals are common) as a real standalone opcode. Manually eyeballing bytes without the full opcode table risks exactly this kind of false-positive resync error — didn't chase it further this session. `BattleScript_BallThrow` (`0x81D9A14`, another hardcoded constant, 46 bytes before `SuccessBallThrow`) was also dumped and contains a repeating `printstring`+`0xEF`(single-byte, unknown mnemonic) pattern across 4 messages (`0x0101`, `0x0102`, `0x0173`, `0x0101` again) — very plausibly the classic "Ball shook once/twice/three times..." animation+message loop, but not decoded further.

**Real next step to finish this**: `battle_script_macros.s` (1810 lines) and `assembly/data/battle_script_commands_table.s` (329 lines, ~256-entry `.word` list) together are a *complete* mnemonic-to-opcode-and-operand-width table for this whole scripting ISA — write a small Python decoder from these two files (same spirit as `map_species.py` parsing `species.h`) instead of hand-decoding hex dumps, then walk `BattleScript_BallThrow`→`BattleScript_SuccessBallThrow` properly. That decoder would also directly answer where `gBattleScriptingCommandsTable`'s real address is *if* the script interpreter's dispatch code can be found (still needs Ghidra/XREF for that specific piece — the mnemonic table alone doesn't give the table's ROM address, only the opcode-to-name mapping for reading script bytes once found).

## Ghidra project set up (infrastructure, no analysis run yet)

Copied Unbound's already-built Ghidra 12.0.2 + `pudii/gba-ghidra-loader` install (`tools/ghidra/`, 847 MB, gitignored) rather than reinstalling — same reuse pattern as the `armips`/`flips` binary copies. Imported the ROM headless (`analyzeHeadless ghidra_project RadicalRedCM -import "rom/radicalred 4.1.gba" -noanalysis`): loader correctly auto-detected `GBA Loader` / `ARM:LE:32:v4t:default`, matching Unbound's own result. **Deliberately did not run full-ROM auto-analysis** — Unbound's own experience (see `../Unbound-Character-Mode/docs/ROUTINE_MAP.md`) is that it times out on a 32MB ROM without completing and its `getReferencesTo()` then returns empty for regions it never reached. Copied Unbound's three proven Java scripts instead (`tools/ghidra_scripts/{FindXrefs,InspectRegions,DecompileFunc}.java`, already fixed there for an address-format bug — addresses need the `0x08` ROM-base prefix, e.g. `080CF068` not `000CF068`, or `toAddr()` silently resolves to an unmapped address) — these do targeted, fast, small-window disassembly/decompilation around specific known addresses instead. Not yet run against RadicalRed's own addresses this session (the raw-byte technique above got far enough without needing them yet); ready for a future session to point at `atkF0_givecaughtmon`'s dispatch table once that address is known some other way, or at the script-decoder's findings once written.

## CONFIRMED — gBattleScriptingCommandsTable, atkF0_givecaughtmon, and GiveMonToPlayer all located and verified. THE CATCH-HOOK SEARCH IS CLOSED.

**Technique**: `assembly/data/battle_script_commands_table.s` mixes CFRU-compiled symbols (`.word atkF0_givecaughtmon`) with **hardcoded vanilla handler addresses** (`.word 0x801fd51 @printstring`) for the 108 opcodes CFRU didn't replace. Searched the ROM for a 256-entry pointer table matching all 108 known vanilla values at their exact slot indices. Two candidates found — and the decoy-table lesson from the base-stats work repeated itself exactly:

| candidate | file offset | vanilla slots match | CFRU slots point into | code refs |
|---|---|---|---|---|
| A (decoy) | `0x25011C` | 108/108 | `0x0801-0x0802xxxx` (vanilla region — it's the ORIGINAL vanilla table, left in place, dead) | **0** |
| B (real) | `0x103EF20` | 107/108 | `0x09xxxxxx` (RR's injected-code half of the expanded 32MB ROM) | **5** (literal pools at `0x14C1C`, `0x15A28`, `0x15C6C`, `0x15C98`, `0x1D054` — the vanilla battle-interpreter code region) |

**`gBattleScriptingCommandsTable` (real) = file offset `0x103EF20` (ROM `0x0903EF20`).** Read out the catch-path slots:
- **`atkEF_handleballthrow` = `0x0907CFF1`** (Thumb; function entry file offset `0x107CFF0`)
- **`atkF0_givecaughtmon` = `0x0907DD45`** (file offset `0x107DD44`)
- **`atkF1_trysetcaughtmondexflags` = `0x0907DBD9`** (file offset `0x107DBD8`)

All three start with valid Thumb `push` prologues. **`atkF0_givecaughtmon` decompiled in Ghidra (new script `tools/ghidra_scripts/CreateAndDecompile.java`) and verified structurally against CFRU's `src/catching.c` source — every landmark matches**: the `IsRaidBattle() && FlagGet(0x930) && backupRaidMonItem` intro (so **`FLAG_BATTLE_FACILITY` = `0x930` in this ROM** — add to Phase 4's flag-exclusion list), the `GiveMonToPlayer(mon) != MON_GIVEN_TO_PARTY` gate into the box-full `MULTISTRING_CHOOSER` 0/2/+1 messaging, the `GAME_STAT_CAUGHT_TODAY` (`0x21`) increment-vs-reset branch pair, the `gBattleMons[bank] * 0x58` caught-species read, and the final `++gBattlescriptCurrInstr`.

**`GiveMonToPlayer` = `0x0907D791`** (file offset `0x107D790`) — the call `atkF0` gates on. Decompiled and verified **line-for-line** against CFRU's `src/catching.c:600`: three form-revert calls, `SetMonData` with `MON_DATA_OT_NAME=7`/`MON_DATA_OT_GENDER=0x31`/`MON_DATA_OT_ID=1` (gender/id at `gSaveBlock2+8`/`+10`, matching vanilla layout), the inlined `GetFreeSlotInPartyForMon` 6-slot × 100-byte party loop with `species==0` test at struct offset `0x20`, the `gMain.inBattle` (bit test via `<<0x1E`) `|| gBattleTypeFlags & BATTLE_TYPE_INGAME_PARTNER` (bit 22 via `<<9`) multi-battle PC-redirect, `CopyMon(dest, mon, 100)`, `gPlayerPartyCount = slot+1`, and the party-full fallback `TryRevertOriginFormes(mon, TRUE)` → `return SendMonToPC(mon)`. **This is THE Phase 4 enforcement choke point** (per `docs/CFRU_CROSSWALK.md`, both wild-catch and `ScriptGiveMon` flow through it — remember the Battle-Tower-rental caveat there before hooking naively).

**Byproduct addresses harvested** (from the confirmed decompilations' call sites and literal pools):
- `SendMonToPC` = `0x090B6E39` (tail call from GiveMonToPlayer)
- `LoadTargetPartyData` = `0x0907DBC9` (first call in atkF0)
- `IsRaidBattle` = `0x0908E0A9`
- `TryFormRevert` = `0x09099D8D`, `TryRevertMega` = `0x090A94E1`, `TryRevertGigantamax` = `0x0908D63D`, `TryRevertOriginFormes` = `0x0909A199`
- `CopyMon` = `0x08040B09` (vanilla FRLG address, unchanged)
- **RAM (all exact vanilla FireRed values — RR did NOT relocate the core RAM layout)**: `gPlayerParty` = `0x02024284`, `gPlayerPartyCount` = `0x02024029`, `gSaveBlock2Ptr` = `0x0300500C`, `gMain` = `0x030030F0` (`.inBattle` at `+0x439`), `gBattleTypeFlags` = `0x02022B4C`. **Phase 4's injected C can use pret/pokefirered's documented symbol addresses for these directly.**
- A cluster of what look like long-call trampolines/veneers around `0x0907E498`–`0x0907E4A0` (the decompiler shows `SetMonData`/`FlagGet`/`GetMonData`/`StringCopy`-shaped calls all routing through addresses 2-4 bytes apart there) — NOT yet individually mapped; don't cite specific addresses from this cluster without disassembling it properly first.

The originally-planned "walk the script bytes with a full opcode-width decoder" approach was **not needed** — matching the dispatch table's vanilla-pointer fingerprint was cheaper and gave the compiled function addresses directly (the script-side `catchpoke` position stopped mattering once `atkF0`'s function address was in hand).

## CONFIRMED — ScriptGiveMon located; and the technique that found it generalizes into a 539-entry symbol table

**`ScriptGiveMon` = `0x0907767D`** (Thumb; function entry file offset `0x107767C`). Found via CFRU's own hook-installation record: the `hooks` file in the CFRU source tree lists `ScriptGiveMon 80A011C 3` — CFRU (and RR, which kept the mechanism) installs each of its C functions by overwriting that vanilla address with a Thumb trampoline (`ldr rX,[pc,#0]; bx rX` + literal). Reading the ROM at `0xA011C` shows exactly that shape (`00 4B 18 47` + literal `0x0907767D`). Verified by decompiling the target: matches CFRU's `build_pokemon.c:4007` source structurally — `CreateMon(&mon, species, level, 32, ...)` (the fixed IV `0x20` literal is visible), `SetMonData(..., MON_DATA_HELD_ITEM=0xC, ...)`, the `customGivePokemon` param-gated block, ball-type set, and the tail `GiveMonToPlayer(&mon)` → `if (result < 2) SetMonPokedexFlags` → return. Additionally, one of `GiveMonToPlayer`'s six BL callers (below) sits at `0x090777CE`, *inside* this function — three independent confirmations total.

**`GiveMonToPlayer`'s complete caller inventory** (all six BL sites in the whole ROM, from a full-ROM Thumb-BL-target scan; plus one literal-pool trampoline):
- `0x0907DD84` — inside `atkF0_givecaughtmon` (wild catch — WILL be enforcement-gated)
- `0x090777CE` — inside `ScriptGiveMon` (scripted gifts/static encounters — WILL be gated)
- `0x090791E6`, `0x09079570`, `0x0907A040` — per CFRU `build_pokemon.c` source order, the Battle-Frontier rental-mon givers (`GiveRandomFrontierMonByTier`, `sp06A_GivePlayerFrontierMonByLoadedSpread`, `GivePlayerFrontierMonGivenSpecies`) — **must NOT be gated** (the Phase 4 rental caveat from `docs/CFRU_CROSSWALK.md`, now with concrete addresses). Not individually decompile-verified (identification is by source order within the confirmed build_pokemon.c compile unit — good enough for "don't touch these").
- `0x090BC1BE` — **RESOLVED (testing session): RR's own party-restore-from-save routine — must NOT be gated, and isn't.** The containing function (`0x090BC194`, disassembled via objdump; no CFRU source equivalent — this is RR-specific code) reads `gSaveBlock1Ptr` (`0x03005008`), copies the saved `playerPartyCount` (saveblock `+0x34`) into `gPlayerPartyCount`, then loops all 6 saved party slots (saveblock `+0x38 + 100*i`), memcpy'ing each 100-byte mon to a stack buffer and calling `GiveMonToPlayer` on it — i.e., vanilla `LoadPlayerParty` semantics reimplemented through `GiveMonToPlayer`. Gating it would strip the player's own already-owned party on save load. It also can't bypass enforcement: everything it re-gives was gated when originally acquired. Leaving this BL unpatched is definitively correct.
- Vanilla `GiveMonToPlayer` (`0x08040B15`) is itself a trampoline to the CFRU version (literal at `0x40B18`), so any vanilla-code caller still routes through the same choke point.

**Phase 4 hook design implication**: patch the two BL instructions at `0x0907DD84` and `0x090777CE` to call the injected roster-check shim (which tail-calls the real `GiveMonToPlayer` or reroutes) rather than hooking `GiveMonToPlayer` itself — the rental-mon callers then stay untouched by construction.

**The generalized win — `tools/resolve_cfru_hooks.py` + `docs/CFRU_HOOK_SYMBOLS.txt`**: parsing all 623 entries of CFRU's `hooks` file and reading each recorded vanilla address's trampoline literal resolved **539 CFRU functions to their real RR compiled addresses in one pass** — effectively a symbol table for the whole CFRU layer of this ROM, no disassembly needed. Sanity-checked two ways: `ScriptGiveMon` → `0x0907767D` (matches the decompile-verified address above) and `SendMonToPC` → `0x090B6E39` (independently matches the tail-call address extracted from `GiveMonToPlayer`'s decompilation). The 84 unresolved entries are non-trampoline hook types (mid-function byte patches), listed in the output file for the record. **Check this file FIRST before doing any future function-address RE** — most CFRU-layer functions are already in it.

## CONFIRMED — Radical Red's cheat-code entry system, fully decoded: the Character Mode selection vector

RR's new-game flow includes a **cheat-code NPC**: "Would you like to put in a cheat code?" → yes/no → `special 0x12C` opens a text-entry (naming) screen → an event-script chain compares the entered text against each known code → per-code handler sets a flag. The entire mechanism is plain Gen-3 event-script bytecode, decoded end-to-end:

- **Prompt script** at file `0x1050071`: `loadword 0, "Would you like to put in a cheat code?"; callstd 5` (yes/no); `compare 0x800D, 1; goto_if eq → 0x09050086; release; end`.
- **Entry + check chain** at `0x1050086`: `special 0x12C` (open code-entry screen); `waitstate`; then per code: `loadword 0, <codeString>; special 0x12D` (compare entered text vs loaded string, result → var `0x800D`, 0 = match); `compare 0x800D, 0; goto_if eq → <handler>`. Five codes registered: `Woyaopp` (handler `0x090500F3`, sets flag `0x1040`), `DexAll`, `SO2Toxic`, `TeamPreview`, `EZCatch` (handler `0x09050109`, sets flag `0x109D`).
- **No-match fallthrough**: `goto 0x09050811` at file offset **`0x10500EE`** → "Invalid code." message; release; end. **This 5-byte goto is the Character Mode insertion point**: repoint it into a free-space extension chain that checks 184 character names the exact same way (`loadword`/`special 0x12D`/`compare`/`goto_if` per name), with per-character handlers doing `setvar VAR_CHARACTER_ID, <index>; setflag FLAG_CHARACTER_MODE; <confirm msgbox>; release; end`, and the extension's own fallthrough continuing to the original `0x09050811`. Zero new UI code — the naming screen, comparator special, and message plumbing are all RR's own, already-working machinery.
- Handler shape verified by decoding Woyaopp's: `checkflag 0x1040; goto_if set → "already set" (0x09050135); loadword <"...has been set!">; callstd 6; setflag 0x1040; release; end`.

## CONFIRMED — expanded flag/var ranges, and free IDs chosen for Character Mode

CFRU's `src/save.c` (`GetExpandedFlagPointer`/`GetExpandedVarPointer`): with `SAVE_BLOCK_EXPANSION` (which RR demonstrably has — its cheat flags `0x1040`/`0x109D` are in the expanded range and persist), **flags `0x900`–`0x18FF`** live in `gExpandedFlags` and **vars `0x5000`–`0x51FF`** in `gExpandedVars`, both save-persistent. RR's own hooks (`ExpandedFlagsHook` @ vanilla `0x0806E5C0`, `ExpandedVarsHook` @ vanilla `0x0806E454`, per `docs/CFRU_HOOK_SYMBOLS.txt`) route the vanilla accessors through expanded storage — so injected code just calls vanilla `FlagGet`/`VarGet` and expanded IDs work transparently.

Surveyed actual usage in the ROM (byte-pattern scan for flag opcodes `0x29/0x2A/0x2B` and var opcodes `0x16/0x17/.../0x26` with in-range operands — false positives possible, but zero hits is strong evidence of non-use):
- **`FLAG_CHARACTER_MODE` = `0x18FE`** (zero hits; 115 free candidates existed in `0x1800`–`0x18FF`)
- **`VAR_CHARACTER_ID` = `0x51FD`** (zero hits; 1-based character index, 0 = none — mirrors ROWE's convention)

## Vanilla function addresses for Phase 4 (from CFRU's own `BPRE.ld` linker script — these are what CFRU itself links against, so they're authoritative for any CFRU-based hack)

`GetMonData` = `0x0803FBE9`, `SetMonData` = `0x0804037D`, `ZeroMonData` = `0x0803D995`, `FlagGet` = `0x0806E6D1`, `FlagSet` = `0x0806E681`, `VarGet` = `0x0806E569`, `VarSet` = `0x0806E585`, `CalculatePlayerPartyCount` = `0x08040C3D`, `CompactPartySlots` = `0x080937DD`, `StringCopy` = `0x8008D85` (all Thumb-bit-set). `SendMonToPC` is commented out in BPRE.ld (CFRU replaces it) — use RR's confirmed `0x090B6E39`.

## Phase 4 hook-design summary (all inputs now confirmed)

- **Enforcement semantics ported from ROWE** (`src/character_mode.c` + call sites there): gifts/statics → off-roster non-egg mons redirect to `SendMonToPC`; ROWE additionally ball-blocks wild catches of off-roster species inside `handleballthrow` — for RR v1, catches use the same PC-redirect shim instead (all vanilla "sent to Box" messaging then works automatically, since both `atkF0_givecaughtmon` and `ScriptGiveMon` already branch on `result != MON_GIVEN_TO_PARTY`).
- **Shim**: `CM_GiveMonToPlayerGated(mon)` — if `FlagGet(0x18FE)` and `VarGet(0x51FD)` selects a valid character and mon is non-egg and species bit is NOT set in the character's allowed-species bitmap → `return SendMonToPC(mon)`; else `return GiveMonToPlayer(mon)` (`0x0907D791`).
- **Patch sites**: the two BL instructions at `0x0907DD84` (catch) and `0x090777CE` (scripted gift) retarget to the shim. Thumb BL range is ±4MB: shim must live in the free block at ROM `0x08B71D04`+ (distance ~3.6MB from both sites — in range; the other big block would not be).
- **Allowed-species bitmaps**: 172 bytes × 184 characters (1376 bits each), precomputed by extending `emit_characters.py` — evolution-family-forward expansion over `data.js`'s evolution graph from each roster base id. O(1) lookup at catch time, no runtime evolution walking.

## Not yet started

The sixth-caller, cheat-entry-location, sprite-table, and in-game-trade TODOs are all resolved (see entries above/below). No enforcement gaps remain known.

## CONFIRMED — the in-game trade system, fully mapped; only ONE live trade exists, now gated

The long-open "trade anchor" search is closed. Chain of findings, each cross-verified:
- **`sInGameTrades` table = file `0x26CF8C`** (found by searching FRLG trade-mon nicknames; "Mimien" hit). Nine 60-byte vanilla-struct records, ALL customized by RR (give species / nickname / requested species): 1216 'Mimien'/63, 508 'Aphrodite'/1164, 1167 'ClubPnguin'/811, 1213 'Ch'ding'/948, 995 'spook'/789, 1169 'Gorochu'/810, **848 'Flowre'/779**, 494 'BestBirb'/198, 1153 'Revenant'/1150.
- The vanilla trade specials cluster at gSpecials[0xFC..0xFF] (`gSpecials` = file `0x15FD60`, 444 entries — vanilla address held, RR extended it in place). The script-side trade fingerprint is `specialvar 0x800D, 0x1B8` + `special 0x158` (party-selection UI; 0x158 alone is generic and used 16 places).
- **Only 4 scripts in the whole ROM carry the full trade fingerprint** (trade indices 1, 2, 3, 6 at files `0x161F91`, `0x161504`, `0x16C175`, `0x164B25`) — and a rigorous bounded map-walk (using per-group counts derived from header-array gaps; groups 1/2 are RR-relocated to `0x736E10`/`0x87296C4`) proves **trades 1/2/3's scripts are dead vanilla leftovers with zero real references**. Beware phantom results from unbounded group walks — overruns slide into adjacent groups' header arrays and fabricate convincing-looking maps/objects (this burned several intermediate conclusions this session).
- **The ONLY live trade: index 6** — Eternal Flower Floette (species 848, standalone form, `ancestor: 848`, evolves to nothing) 'Flowre' for the player's Florges (779). Wired as a **BG event** (console/sign-style, like the cheat entry) at tile (0,2) of **map 2.11** (0 objects, 1 warp, 1 BG event; events struct `0x3B4330`, header `0x3500BC`); script entry `0x08164B03`, pointer at **file `0x3B432C`** (BG struct +8).
- **Gated in the build** (`inject_character_mode.py`): the BG script pointer is retargeted to a 90-byte wrapper at `0x08C8E000` — flag off / char 0 / char >184 fall through to the original script; otherwise allowed only for characters whose bitmap permits species 848 (computed at build time — currently **zero** of 184, since Eternal Floette is canon-exclusive to AZ, who isn't a playable character), else a sign msgbox "Character Mode: this trade is not in your roster." Verified by `tools/tests/verify_artifacts.py` section 7 (pointer both directions, full wrapper decode, allow-list re-derived from bitmaps).

## CONFIRMED — the cheat-code entry point is the game console in the player's bedroom

Found by walking the real map-header tree (`gMapGroups` at vanilla `0x3526A8`, 43 groups) and checking every object/coord/BG-event and map-script pointer for targets inside the cheat-script blob: **map 4.1 (Pallet Town — Player's House 2F, the new-game starting room), BG event #0 at tile (6,5), kind 0, script `0x0905006F`**. The script decodes `lock; signmsg; loadword 0 "Would you like to put in a cheat code?"; callstd 5; compare 0x800D,1; goto_if eq -> 0x09050086 (the special-0x12C entry + check chain); release; end` — i.e., it's a sign-type interactable (the bedroom game console), not an NPC. No flag gate before the prompt, so it works any time the player interacts with it. Manual gameplay test path: new game → face the console at (6,5) → A → yes → type a code.

## CONFIRMED — trainer-pic ROM tables ARE at their stock CFRU/vanilla addresses (Phase 3 unblocked)

The v9 session's pessimism ("sprite tables need Ghidra") was wrong — empirical read of the CFRU `BPRE.ld` hardcoded addresses shows all three tables live and well-formed in this ROM:
- **`gTrainerFrontPicTable` = file `0x23957C`** — 148 entries of `{u32 lz-data ptr, u16 size=0x800, u16 tag}` with tags sequential 0..147, all pointers valid. Entry 0 already points into `0x093256A8` (RR's injected-art region) — RR edits this table **in place**, repointing individual slots at new art in free space; the same mechanism works for adding character pics.
- **`gTrainerFrontPicPaletteTable` = file `0x239A1C`** (per `BPRE.ld:381`) — 148 `{u32 pal ptr, u16 tag, u16 0}` entries, tags sequential, entry 0 also into the `0x09` region.
- **`gTrainerBackPicTable` = file `0x239E7C`** — 8+ well-formed entries checked, sequential tags.

(A first probe at `0x23A004` for the palette table read garbage — that address was misremembered, not evidence of relocation. Always pull the address from `tools/cfru_donor/BPRE.ld` rather than memory.)

## CONFIRMED — naming-screen length precedent for the selection codes

RR's own original cheat-code chain (walked backwards from the fallthrough goto at `0x10500EE`) registers exactly five codes: `Woyaopp` (7), `DexAll` (6), `SO2Toxic` (8), `TeamPreview` (11), `EZCatch` (7). **`TeamPreview` at 11 characters proves the `special 0x12C` naming screen accepts 11-char input** — the injected character aliases (asserted ≤11 chars at build time, longest are 11) are within RR's own demonstrated precedent, not an assumption.
