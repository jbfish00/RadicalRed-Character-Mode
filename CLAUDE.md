# CLAUDE.md — Pokemon Radical Red "Character Mode"

Guidance for Claude Code when working in this repo. Keep this file current at every pause — it's the handoff doc for a fresh instance picking this up cold.

## What this project is

Porting the "Character Mode" feature from the Pokemon ROWE project (`/home/jbfish00/Documents/Pokemon Rowe Alteration`) to Pokemon Radical Red v4.1: an opt-in intro-menu choice to play as an iconic Pokemon character, restricted to that character's Bulbapedia-documented roster (evolution families included). Full plan (context, phase breakdown, roster-scope decision, provenance decisions, open risks) at `~/.claude/plans/just-like-with-pokemon-linear-galaxy.md`.

**Sibling project, same workspace, further along**: `../Unbound-Character-Mode/` ported the same feature to Pokemon Unbound and established the binary-ROM-hacking methodology this project reuses. Read its `CLAUDE.md` for the proven technique set, but do not assume its ROM-specific findings (offsets, text conventions, save-flag ranges) transfer — every hack's binary differs.

**Critical difference from ROWE: Radical Red has no public source of its own.** It's a closed binary hack (by soupercell, with koala4 — NOT Skeli789/Unbound's author) built on the open-source Complete FireRed Upgrade (CFRU) engine. Unlike Unbound (which had to approximate its internals via a third-party community fork as a donor), Radical Red's actual upstream engine — CFRU itself (`github.com/Skeli789/Complete-Fire-Red-Upgrade`) — is directly public and cloned locally at `tools/cfru_donor/`. This is a stronger donor situation than Unbound had. Radical Red's own content (maps/story/trainers/balance) remains proprietary — same "open engine, closed content" shape as Unbound, so this is still classic binary ROM hacking: reverse-engineer the compiled ROM, inject new code/data into free space, output a patch (never redistribute the ROM).

## Standing rules (carried over from the ROWE/Unbound projects, user-confirmed pattern)

- **Checkpoint rule**: at every pause, update this file + the plan file for seamless handoff.
- **Ask questions until 95% confident** before making consequential decisions.
- Distribution: patch only (UPS/BPS via `tools/bin/flips`), never a prebuilt/redistributed ROM.
- Every located ROM address is pinned to the exact SHA1 in `rom.sha1`. Re-verify before trusting notes against any other copy.
- Roster scope: **full Gen 1-9** (protagonists/rivals/gym leaders/E4/champions/villains/anime) — user explicitly chose this over matching Unbound's Gen-1-8-only trim, since Radical Red's engine confirms Gen 9 species/moves support (unlike Unbound's ROM, which turned out to lack Gen 9 content entirely).

## Repo layout

- `rom/` — extracted ROM (gitignored, never commit).
- `rom.sha1` — checksum of the source ROM; all findings are pinned to this.
- `docs/ROM_INFO.md` — ROM header/provenance notes.
- `docs/FREE_SPACE.md` — free-space audit results.
- `docs/ROUTINE_MAP.md` — RE findings/anchors (the project's "symbol table").
- `docs/CFRU_CROSSWALK.md` — records whether CFRU-source-as-structural-donor pattern-matching pays off (see Phase 1 notes below).
- `docs/SPRITE_COVERAGE.md` — sprite asset coverage survey (not yet run).
- `tools/scan_free_space.py`, `search_gametext.py`, `decode_gametext.py`, `find_pointer_refs.py`, `dump_all_strings.py` — copied verbatim from `Unbound-Character-Mode/tools/` (game-agnostic; `search_gametext.py`/`decode_gametext.py` default to ROWE's shared `charmap.txt` at `/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt`, same as Unbound uses — no local copy needed).
- `tools/bin/` — convenience copies: `armips` v0.11.0, `flips` (copied from Unbound's already-built binaries, both verified working).
- `tools/cfru_donor/` — fresh shallow clone of `Skeli789/Complete-Fire-Red-Upgrade` (gitignored, third-party) — this project's primary species/structure donor, stronger than Unbound's DPE-fork situation since it's Radical Red's actual upstream engine.
- `tools/ghidra/` — **not yet installed** (deferred until text/pointer-anchor techniques run dry, per Phase 1 priority order; Unbound's Ghidra install + `pudii/gba-ghidra-loader` setup is the template when needed).
- `tools/character_mode/` — roster data pipeline:
  - `characters.txt` (205 lines), `rosters_raw.json` (89,080 bytes) — copied from **ROWE's un-pruned originals** (NOT Unbound's already Gen-9-pruned 199-line/78,343-byte copies), per the full-Gen-9-scope decision.
  - `scrape_rosters.py` — copied from ROWE (game-agnostic; only needed if the seed list changes in a way requiring re-scraping).
  - `cache/` — ROWE's Bulbapedia API disk cache (3,761 files, ~25 MiB), copied alongside the scraper to avoid re-hitting the API. Precedent from Unbound: this cache is **committed to git**, not ignored (matches Unbound's own repo, which tracks 3,837 cache files) — small JSON files, fine to track.
  - `map_species.py`, `emit_characters.py` — **not yet written**. Will be rewritten fresh against the CFRU donor (species mapping) and adapted from Unbound's flat-binary emitter (not ROWE's C-header generator) — see Phase 2 in the plan file.

## Toolchain (confirmed working this session)

- `arm-none-eabi-gcc` (system-installed, 13.2.1) — for new freestanding C, not `~/agbcc`. Same verified flags as Unbound: `-mthumb -mcpu=arm7tdmi -mtune=arm7tdmi -O2 -ffreestanding -fno-builtin`.
- `armips` v0.11.0 — copied from Unbound's already-built binary (`tools/bin/armips`), verified runnable (`--help` prints usage banner correctly).
- `flips` — copied from Unbound's already-built binary (`tools/bin/flips`), verified runnable (prints usage banner).
- `mgba-qt` 0.10.2 (system-installed) — confirmed present via `which`; not yet exercised against this ROM.
- `cmake` — confirmed present via `which` (would be needed only if `armips`/`flips` ever need rebuilding from source rather than reusing Unbound's binaries).
- Ghidra + `pudii/gba-ghidra-loader` — not yet installed for this project; install when Phase 1's text/pointer-anchor techniques run dry (see Unbound's setup as template).

## Free space (resolved — see docs/FREE_SPACE.md)

**5.40 MiB confirmed free** (0xFF-padded, 77 runs >= 0x400 bytes) — over 3.5x what Unbound had (~1.46 MiB), despite Radical Red's denser content (full Gen 1-9 species/moves, Mega/Z-Move/Dynamax/Gigantamax, physical-special split). Two dominant blocks: 1.63 MiB @ 0x00B71D04, ~1.02 MiB @ 0x0085032B. This resolves the plan's open risk #1 favorably — free space is not a bottleneck.

## Status (2026-07-12, v2 — RE session)

**Phase 1 (RE/feasibility): substantial progress, not yet gate-closed.**

**Big win: the CFRU-as-structural-donor bet (Phase 1d) paid off, partially.** Full writeup in `docs/CFRU_CROSSWALK.md`. Key findings:
- CFRU is a hook-and-patch framework over vanilla FireRed binary, NOT a full decompilation — only subsystems it modifies have public source.
- **Catch and gift/static-mon delivery share ONE choke point in CFRU source**: `catching.c`'s `atkF0_givecaughtmon()` (wild catch) and `build_pokemon.c`'s `ScriptGiveMon()` (scripted/static/event mons, likely also Mystery Gift's delivery path) both call `GiveMonToPlayer()`, which already has a `SendMonToPC()` fallback built in. This is a real simplification opportunity for Phase 4 versus ROWE's original 6-separate-hook design — **but** `GiveMonToPlayer` is also used by Battle Frontier/Tower rental-mon delivery, so a naive hook would wrongly roster-gate temporary rental teams. Flagged as a Phase 4 design constraint and a Phase 5 test case.
- Mystery Gift internals (`mevent.h`) and trade internals (`trade.h`) have **no CFRU source at all** — same blind-RE position as Unbound for those two systems specifically.
- Concrete ROM evidence gathered (see `docs/ROUTINE_MAP.md`): found the "Gotcha" catch-message text at `0x3FD7A2`/`0x3FD7C0`, referenced from a large contiguous `gBattleStringsTable`-shaped pointer array at `0x3FE338`+ — same structural shape Unbound found in its own ROM, strong converging evidence the catch-message plumbing is intact. Also confirmed `"Box is full"` and `"sent to [box] PC"` text in the same region, and CFRU's expanded ball roster (`"Beast Ball"`, `"Dream Ball"`) is present in-ROM.
- Found a Mystery Gift tutorial-dialogue anchor (`"Mystery Gift"` text at `0x1A6317`) and `"Wonder Card"` text (17 hits) — not yet decoded into a delivery-relevant routine.
- Tried and ruled out several trade-dialogue leads (Berry Powder shop, Union Room UI text) — no genuine in-game NPC trade anchor confirmed yet, logged in `docs/ROUTINE_MAP.md` so they aren't retried.
- **Not yet done**: XREF-confirming which of the (likely dozens of) call sites referencing the battle-strings table is actually `atkF0_givecaughtmon` — this is the concrete next RE step, mirrors Unbound's own current blocker.

## Status (2026-07-12, initial scaffolding session)

**Phase 0 (scaffolding): COMPLETE.**
- Repo created at `RadicalRed-Character-Mode/`, git initialized (not yet committed — see Next steps).
- ROM extracted from `radicalred 4.1.zip` (workspace root) into `rom/radicalred 4.1.gba` (33,554,432 bytes).
- SHA1 computed and pinned: `964f951a0fdaf209e4ea1344883ef0d557bb3a80` (no published SHA1 for v4.1 existed anywhere — this project owns the canonical pin).
- Header confirmed: `POKEMON FIRE`/`BPRE`/rev 0 — genuinely FireRed-based, consistent with Radical Red being CFRU-derived (same base as Unbound). No watermark/readme in the zip (unlike Unbound's ROMSFUN.COM-watermarked copy).
- `.gitignore` copied from Unbound and extended with `tools/cfru_donor/`.
- `docs/{ROM_INFO,FREE_SPACE,ROUTINE_MAP,CFRU_CROSSWALK,SPRITE_COVERAGE}.md` created (ROM_INFO and FREE_SPACE populated; ROUTINE_MAP has one early finding; CFRU_CROSSWALK and SPRITE_COVERAGE are stubs pending later phases).

**Phase 1 (RE/feasibility): just started.**
- Toolchain verified: `armips`/`flips` binaries copied from Unbound and confirmed runnable; `arm-none-eabi-gcc`/`mgba-qt`/`cmake` confirmed installed system-wide. Ghidra deliberately not yet installed (lowest-priority technique, per the plan's priority order).
- Free-space audit done and resolved favorably (see above).
- CFRU donor repo cloned (`tools/cfru_donor/`, shallow clone) — the Phase 1d "CFRU-as-structural-donor" bet (attempting to pattern-match stock CFRU source/compiled shapes against Radical Red's binary to shortcut hook-site RE) has **not yet been attempted**; this is the single highest-value next step per the plan.
- One real finding via `search_gametext.py`: **Radical Red renders mixed-case text** ("Trainer", "Pokemon"), not vanilla FRLG's ALL-CAPS convention — confirmed by 0 hits for all-caps queries vs. hundreds for mixed-case/`--icase` queries. A `"SAVE"` hit decoded to a genuine RR developer diagnostic string ("WRONG SAVE TYPE! Please change to Flash 128k. Consult the Discord..."), confirming this really is Radical Red's own content. **Always use `--icase` or mixed-case queries on this ROM going forward** — plain all-caps searches (which worked fine on vanilla/Unbound) will silently miss almost everything here. Full detail in `docs/ROUTINE_MAP.md`.
- Not yet attempted: any of the enforcement-hook text/pointer anchor searches (catch, gift, Mystery Gift, trade, PC, starter-selection, intro-menu), the CFRU-crosswalk pattern-matching bet, or any Ghidra work.

**Phase 2 (roster data pipeline): partially started.**
- Seed data sourced: `characters.txt` (205 lines / 182 actual character entries, rest are comments/blank generation separators) and `rosters_raw.json` (89,080 bytes) copied from ROWE's originals — confirmed byte-for-byte match to the plan's pre-verified sizes. `scrape_rosters.py` and its Bulbapedia cache (3,761 files) copied alongside.
- **Seed-list reconciliation DONE — corrects a plan assumption.** Diffed ROWE's 182-character list against Unbound's 156-character list: exactly 26 characters removed, a clean subtraction (no renames — reverse diff is empty). But it's **not purely Gen-9 pruning** as the plan initially assumed — the removed set is: all 15 Gen 9 characters (Geeta, Nemona, Rika, Poppy, Hassel, Katy, Brassius, Iono, Kofu, Larry, Ryme, Tulip, Grusha, Arven, Penny) **plus** Gen 5/6/7 protagonists (Hilbert, Hilda, Nate, Rosa, Calem, Serena, Elio, Selene) **plus** 3 of Gen 7's 4 island kahunas (Hala, Nanu, Hapu — Olivia was kept). So Unbound made a deliberate broader scope cut (no protagonists Gen 5+, partial kahuna trim) specific to that project, not a general/necessary pattern. Since this project targets ROWE's full 182-character breadth (user's explicit full-Gen-1-9 choice), this is moot for what to build — just don't cite "Gen 9 confirmed absent" as the reason Unbound's list is smaller; it's a broader editorial choice than that.
- **Not yet done**: the CFRU-donor species-ID mapping rewrite (`map_species.py`), or the binary emitter adaptation (`emit_characters.py`). These are the next concrete chunks of work — expect real rework here (not a copy), per Unbound's own hard-learned lesson that donor name-table labels don't reliably match species constants and that truncation-convention `NAME_FIXES` need re-deriving per-project.

**Phases 3-6: not started** (sprite pipeline, enforcement logic injection, testing, packaging) — all gated on Phase 1/2 progressing further.

## Status (2026-07-12, v3 — species table investigation, IMPORTANT correction)

**Major finding: the CFRU donor's `include/constants/species.h` only covers up to Gen 8** (`NUM_SPECIES_GEN_8`, ends at `SPECIES_ENAMORUS_THERIAN`/`SPECIES_URSHIFU_RAPID_GIGA`) — the mainline `Skeli789/Complete-Fire-Red-Upgrade` repo has no Gen 9 species constants at all. This means the donor alone is **insufficient** for full Gen 1-9 species-ID mapping; Radical Red's own fork must have extended the species table further, and that extension only exists in the compiled RR binary, not in any public source this project has access to.

**Empirically confirmed via direct ROM text search: Radical Red genuinely has the full Gen 1-9 species roster as real, ownable content** — not just Gen-9-flavored moves/abilities as ambiguous web research phrasing suggested. Found `Sprigatito`, `Floragato`, `Meowscrada` (10-char-truncated, matches Unbound's own truncation pattern), `Fuecoco`, `Crocalor`, `Skeledirge`, `Quaxly`, `Quaquaval`, `Gholdengo`, `Tinkaton`, `Armarouge`, and even the box legendaries `Koraidon`/`Miraidon` as real text in the ROM, alongside genuine Gen 9 Pokédex flavor text (mentions of "ancient Paldea", "Pecharunt's control", etc.). **This validates the user's full-Gen-1-9 roster scope decision** — it's achievable, the content is really there.

**However, attempting to resolve species IDs positionally (index = species ID, the technique that worked cleanly for Unbound) did NOT work on first attempt.** Walking forward from a confirmed `Bulbasaur` text anchor produces inconsistent blank-entry padding between real names that doesn't match a simple fixed-stride or Dex-order-gap pattern — spot-checks against known CFRU indices (Pikachu=25, Mewtwo=150, Sprigatito=906, etc.) all mismatched. This is **not yet understood** and is now the critical path blocker for Phase 2 (`map_species.py`). Full detail and hypotheses in `docs/ROUTINE_MAP.md`. This is an honest "not solved yet" — do not build `map_species.py` on top of the naive positional walk without first either (a) figuring out the real indexing scheme, or (b) finding a more rigid fixed-size table (e.g. a base-stats table, which is typically fixed-record-size and much easier to walk reliably than variable-length name strings) to cross-validate against.

## Status (2026-07-12, v4 — species-ID resolution SOLVED)

**Major breakthrough, corrects v3's conclusions.** Found that CFRU accesses `gBaseStats` (and other tables) through a **fixed pointer-redirect slot** (`include/new/rom_locs.h`: `#define gBaseStats ((struct BaseStats*) *((u32*) 0x80001BC))`) — a 4-byte pointer *value* at a fixed vanilla ROM address that the compiled game dereferences to find wherever CFRU/Radical Red actually repointed the real table. Reading this directly (file offset `0x1BC` in the RR ROM) resolves to file offset `0x17B98EC` — the REAL, code-referenced base-stats table, verified byte-exact against known species (Bulbasaur, Ivysaur, Venusaur, Charmander, Squirtle, Pikachu, Mewtwo, Mew — all exact vanilla matches) all the way through **index 1375**, where it terminates (all-zero record at 1376, then clearly different data after).

**This means: `NUM_SPECIES` for Radical Red = 1376, `table_base = 0x17B98EC`, `stride = 28` bytes — a fully reliable, byte-exact species-ID authority for the ENTIRE roster, Gen 1 through Gen 9.** Indices 1294-1375 (82 entries) are Radical Red's own Gen 9 extension beyond stock CFRU's 1294-species range, confirmed via plausible/coherent stat records (not garbage).

**v3's conclusions were wrong and are now corrected**: what v3 found via raw byte-pattern search (table at `0x254784`, showing an apparent "Pikachu rebalance" and "garbage" past index ~1290) was reading a decoy/leftover table copy elsewhere in the ROM, not the one the game actually uses. The real table (found via the pointer-redirect technique above) shows unmodified vanilla Pikachu stats and coherent data throughout. **Lesson for future RE work on this or other hacks: prefer chasing CFRU's `rom_locs.h` fixed-pointer slots over raw byte-pattern search when both are available** — pattern search can and did find decoy data that happened to coincidentally match.

**Still open**: the evolution table's equivalent slot (`gEvolutionTable` at file offset `0x42F6C`) was tried the same way but resolved to a target reading all-zero for the first several species tested — did not pan out on the first attempt, needs another look. Also still open: matching each of the 82 Gen-9-range indices (1294-1375) to an actual species name (the index range is now solid, but names aren't yet attached to specific indices in that range).

Full detail in `docs/ROUTINE_MAP.md`.

## Status (2026-07-12, v5 — map_species.py written and validated for Gen 1-8)

**Evolution table also solved via the same pointer-redirect technique** — the earlier "failed" attempt just assumed stock CFRU's `EVOS_PER_MON=5`; Radical Red actually uses **`EVOS_PER_MON=16`** (128-byte blocks, matching the expansion CFRU's own source comments attribute to DPE). With that corrected, `table_base=0x17CD9B0` verified exactly against known evolutions (Bulbasaur→Ivysaur@16, Charmander→Charmeleon@16, Squirtle→Wartortle@16 all exact vanilla matches; Ivysaur→Venusaur shows a deliberate RR rebalance, level 36 not vanilla's 32). Also found species **1022 = SPECIES_RAICHU_A (Alolan Raichu)** as a second Pikachu evolution path, cross-confirmed three independent ways (base-stats record exactly matches real Alolan Raichu stats, CFRU's own constant is `0x3FE`=1022, and it showed up as an evolution target) — strong proof the whole Gen 1-8 + alt-form index range can be trusted against `species.h` directly.

**`tools/character_mode/map_species.py` written and run.** Parses `species.h` for `SPECIES_*` constants, derives display names from the constant identifiers (de-sanitized + normalized), builds an evolution-family child→parent map by walking the confirmed real evolution table for species 1-1293, and resolves `rosters_raw.json`'s Bulbapedia-scraped names against it. Result: **184 characters, 4652 total species references, 4510 (97.0%) resolved, 0 empty rosters.** Spot-checked correct (Red's roster includes his anime-crossover Pokémon and Articuno; evolution-family reduction correctly folds e.g. Beautifly→Wurmple, Drapion→Skorupi). `NAME_FIXES` needed real curation, as expected — apostrophe/period-stripped names (Farfetch'd, Mr. Mime), Unicode gender symbols (♂/♀) and accents (é) needed explicit normalization handling, and three species (Basculin, Alcremie, Minior, Urshifu) have no bare base constant in CFRU's `species.h` (only color/form-variant constants) and were mapped to a representative default form.

**The remaining 142 unmatched references (76 unique names) are — as expected — entirely genuine Gen 9 species** (Sprigatito, Fuecoco, Quaxly, Tinkaton, Iron Valiant, Great Tusk, etc.), confirming the mapping logic itself has no other gaps; the sole blocker for 100% resolution is the still-open Gen-9-index-to-name matching (see task/OPEN entry in `docs/ROUTINE_MAP.md`). A background research agent was dispatched this session to look for an authoritative Radical Red Gen 9 stats reference (since RR rebalances stats, vanilla-value pattern matching doesn't reliably identify them) — check its result before continuing that thread.

Outputs written: `tools/character_mode/rosters_mapped.json`, `roster_review.csv`, `unmatched_names.txt`.

## Status (2026-07-12, v6 — roster mapping 100% complete)

**The background research agent found the real answer, and it corrects a v4/v5 assumption.** Indices 1294-1375 are NOT Radical Red's Gen 9 addition — they're mostly Hisuian/alternate forms plus the *later* part of the Paldea dex, plus one joke Palworld-crossover species ("Chillet" at 1375). The actual Gen 9 starters and most other Paldea species are interspersed in the "normal" 1-1293 range (Sprigatito=921, Fuecoco=924, Quaxly=927, Koraidon=1193, Miraidon=1194, Gholdengo=852, Tinkaton=842, etc.) — much closer to National-Dex-adjacent order, which is why the original vanilla-stat search for them around index 1294+ never found anything.

The agent found and verified an authoritative source: the community **Radical Red Pokedex** (`dex.radicalred.net` / `github.com/JwowSquared/Radical-Red-Pokedex`), which ships a full per-species database (name, stats, type, evolutions, and a precomputed evolution-family-base `ancestor` field) for the whole ROM. Cross-checked byte-exact against all 82 of this project's own independently-extracted 1294-1375 records before being trusted. Pulled into the project at `tools/character_mode/rr_pokedex_donor/data.js` (~4.4 MB, provenance noted in that directory's `PROVENANCE.md`).

**`map_species.py` rewritten to use this as the primary species-ID/name source** (superseding the `species.h`-derived-name-matching approach — much simpler, since `data.js`'s `ancestor` field gives the evolution-family base directly, even correctly resolving cases like Pikachu→Pichu that the project's own from-scratch ROM evolution-table walk hadn't been verified that deep). **Result: 100% of the roster resolves cleanly — 184 characters, 4652 species references, 0 unmatched, 0 empty rosters.** Spot-checked Arven/Nemona/Geeta/Iono (the Gen-9-heaviest characters) — all correctly show their real Paldea rosters now.

## Status (2026-07-12, v7 — bug hunt found and fixed a real base-form-selection bug)

**Bug found in `build_name_index` and fixed.** The original logic picked, among species sharing a display name, whichever entry was "self-ancestored" (`ancestor == own id`) as the preferred match for a plain Bulbapedia name. This is wrong: Radical Red's dex data defaults `ancestor` to an entry's own id for **cosmetic-only event/costume forms that were never assigned a real pre-evolution** (e.g. all 15 Pikachu cap/costume variants — Cosplay, Libre, PhD, Original, the regional caps, Partner-cap — are self-ancestored, not because they have no pre-evolution in-game, but because the data just didn't bother computing one for promotional forms). The old heuristic would sometimes latch onto one of these decoy self-ancestored entries instead of the true base species (id 25 for Pikachu, which correctly points to Pichu/172), silently breaking evolution-family reduction for any character whose roster included that species. Same bug class hit Greninja, Darmanitan, Aegislash, Cherrim, Silvally, Palafin, and others with similar cosmetic alt-forms.

**Fix**: since every alt/regional/Mega/Gigantamax/costume form in this dataset has a strictly higher species id than its corresponding base form (a structural invariant of how Radical Red's table was built — verified across all groups checked), `build_name_index` now explicitly picks `min(id)` among same-named candidates, rather than relying on the `ancestor`-self-reference heuristic or incidental dict ordering. Re-ran and confirmed: same 100% resolution (184 characters, 4652 refs, 0 unmatched), but now with correct deeper reduction in many places (verified: Ash's roster now correctly shows Pichu instead of un-reduced Pikachu). Diff between before/after was large (~130 lines across the roster) — this was a real, previously-silent correctness bug affecting a meaningful slice of the roster, not a cosmetic change.

Re-ran and re-committed with the fix.

## NEXT

1. ~~Commit initial scaffold~~ DONE. ~~CFRU-as-structural-donor bet~~ DONE. ~~Seed-list reconciliation~~ DONE. ~~Enforcement-hook anchor searches~~ done for catch/PC/Mystery-Gift tutorial; trade still open. ~~Species-ID index range~~ SOLVED. ~~Evolution table~~ SOLVED. ~~map_species.py~~ DONE, 100% resolved, base-form-selection bug found and fixed.
2. Write `emit_characters.py` (adapted from Unbound's flat-binary emitter) to turn `rosters_mapped.json` into `characters.bin`/`rosters.bin`/`names.bin` + manifest. `LEGENDARY_NAMES` set already drafted in `map_species.py` (name-based now, not id-based, since `data.js` is the id source) but not yet cross-checked for completeness against the full Gen 9 legendary/Paradox roster; `ASSET_OVERRIDES` and signature-mon curation not started.
3. XREF-confirm which call site referencing the `0x3FE338`+ battle-strings table is `atkF0_givecaughtmon` (needs Ghidra — not yet installed for this project — or continued manual disassembly).
4. Find a genuine in-game NPC trade dialogue anchor and a Mystery-Gift delivery-relevant anchor (not just the tutorial text found so far).
5. Sprite table locations and intro-menu hook point remain unsearched.
6. Note for Phase 4 (enforcement injection): since `data.js`'s species ids are confirmed to be the exact same numbering as the real ROM's base-stats table index, injected C code can use plain numeric species ids (or a small generated header of `#define`s) without needing CFRU's `species.h` at all for the ~82-entry non-Gen-1-8 range it doesn't cover.
7. Consider auditing `rosters_mapped.json` once more (or writing a small consistency-check script) for other silent-reduction issues of this general shape before trusting it fully for Phase 4/emission — this bug was only caught by manually diffing before/after a refactor, not by an automated check.
