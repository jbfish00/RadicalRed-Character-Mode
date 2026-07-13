# Sprite/asset coverage — Phase 3 planning

Cross-referenced this project's 184-character roster (`tools/character_mode/characters.txt`) against the ROWE Character Mode project's already-built sprite report (`/home/jbfish00/Documents/Pokemon Rowe Alteration/tools/character_mode/sprite_report.txt`), same methodology as `Unbound-Character-Mode/docs/SPRITE_COVERAGE.md` — since this roster's Gen 1-8 slice is largely the same real-world characters ROWE already sourced donor art for.

## Coverage summary

| | count | % of 184 |
|---|---|---|
| Have an overworld sprite candidate | 101 | 55% |
| Have a trainer front-pic candidate | 70 | 38% |
| Have a battle back-pic candidate | 12 | 7% |
| Have AT LEAST ONE asset | 101 | 55% |
| Have NO assets in ROWE's tree | 83 | 45% |

## Pattern (matches Unbound's precedent, plus this project's own Gen 9 addition)

The 83 zero-coverage characters split into three groups:

1. **Gen 6-8 (Kalos/Alola/Galar) game/anime roles** — the same split Unbound found: GBA-style pixel art genuinely doesn't exist anywhere (official or fan-made) for 3D-model-era characters.
2. **A handful of Gen 1-5 anime-only characters** (`Ritchie`, `Tracey`, `Jessie`, `James`, `Lyra`, `Drew`, `Paul`, `Zoey`, `Nando`, `Trip`) — ROWE's own status notes already flagged these as never sourced.
3. **All 15 Gen 9 (Paldea) characters** (`Geeta`, `Nemona`, `Rika`, `Poppy`, `Hassel`, `Katy`, `Brassius`, `Iono`, `Kofu`, `Larry`, `Ryme`, `Tulip`, `Grusha`, `Arven`, `Penny`) — new relative to Unbound's coverage survey, since Unbound's roster excluded Gen 9 entirely (see this project's CLAUDE.md standing-rules note on the full-Gen-1-9 scope decision) but this project's does not. Same underlying reason as group 1: no GBA-style art exists for 3D-only-era characters.

Plus **`Victor` and `Gloria`** (the Sword/Shield protagonists added to this project's `characters.txt` in the v8 session — see `CLAUDE.md`) have **no entry at all** in ROWE's `sprite_report.txt`, since ROWE's own seed list never included them either — same "no assets" outcome as the rest of group 1, just for a different underlying reason (ROWE never looked, not that it looked and found nothing).

This is exactly the split the ROWE/Unbound precedent already established and the user already accepted when scoping the Unbound project: 3D-model-era characters get the lighter-weight trainer-card/menu-portrait-only treatment, not full OW+front+back sprites.

## What this means for Phase 3

- **101 characters (Gen 1-5 + a few Gen 1 anime like Ash/Gary)**: candidate donor PNGs exist in ROWE's `graphics/trainers/front_pics/`, `graphics/trainers/back_pics/`, `graphics/object_events/`. ROWE's `sprite_report.txt` gives *symbol names* (`OBJ_EVENT_GFX_CM_X`, `TRAINER_PIC_X`, `TRAINER_BACK_PIC_X`), not raw file paths — resolving symbol → exact PNG filename needs ROWE's `spritesheet_rules.mk`/`graphics_file_rules.mk` (not yet done; deferred until Phase 3 actually starts, since real injection work is gated on Phase 1 anyway — see below).
- **83 characters (Gen 6-9 + a few anime + Victor/Gloria)**: no GBA-style art exists anywhere. Per the established policy: trainer-card/menu-select portrait only, generic/default costume fallback for their overworld appearance — no bespoke pixel art expected.
- **Actually copying/injecting any of this is blocked on Phase 1 confirming the ROM-side sprite tables.** Checked whether the same CFRU fixed-pointer-redirect technique that solved the species/evolution tables (see `docs/ROUTINE_MAP.md`) would work here first, since it would have been much cheaper than Ghidra: `tools/cfru_donor/include/new/rom_locs.h` only exposes `gBaseStats`/`gEvolutionTable`/`gSpeciesNames`/`gItems`/`gMonIconPaletteIndices` as dynamic pointer-redirect slots. `gTrainerFrontPicTable`/`gTrainerFrontPicPaletteTable`/`gTrainerFrontPicCoords` (`src/defines_battle.h`) are instead **hardcoded compile-time addresses in stock CFRU's own build** (`0x823957C` etc.) — not a redirect slot, so there's no guarantee Radical Red's actual compiled binary has this table at the same address (unlike the redirect-slot tables, whose *slot* address is an engine-level constant regardless of where the hack's own build relocated the *target*). No public CFRU source at all was found for `gObjectEventGraphicsInfoPointers` (the overworld sprite table). Confirming real addresses needs Ghidra's data-type analysis or manual structure hunting, same conclusion Unbound already reached for its own sprite tables — not yet attempted for this project (Ghidra still not installed here, see `CLAUDE.md`/`docs/CFRU_CROSSWALK.md`).

## Reuse mechanics (once unblocked)

Same credits-file discipline as ROWE (`CREDITS_CHARACTER_MODE.md` pattern) — this project will need its own `CREDITS.md` with the same donor list: pret/pokefirered, sinnoh-remakes/pokeemerald-platinum, PokemonHnS-Development/pokemonHnS, DiegoWT's Gen5-in-Gen4-style resource, StreakOfSprites' Ash sheet (same donors Unbound credited, since the underlying art is the same ROWE-sourced set). Injection differs from ROWE's Makefile-automated pipeline: raw tile/palette data needs manual LZ77 compression and free-space injection with hand-patched pointers (see Phase 3 in the plan file), once the real table addresses are confirmed.
