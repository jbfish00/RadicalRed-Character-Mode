/* Character Mode wild-encounter override for Pokemon Radical Red v4.1.
 *
 * Hooks the four BL sites that call CreateWildMon (0x090C292D) with a
 * concrete (species, level) pair produced by a RANDOM TABLE ROLL -- i.e.
 * every wild-encounter table type that rolls a species when a battle
 * starts (see docs/ROUTINE_MAP.md, "CONFIRMED -- wild-encounter override
 * hook sites", for the full RE trail that identified these four and ruled
 * out the others):
 *   - 0x10C2FDA / 0x10C30CE: inside TryGenerateWildMon (confirmed via its
 *     gSwarmTableLength==0 guard, six-call TYPE/ABILITY ability-influence
 *     chain, and FLAG_DOUBLE_WILD_BATTLE=0x910 gate) -- land/cave, surfing,
 *     and rock smash/headbutt (RockSmashWildEncounter/HeadbuttWildEncounter
 *     both call this same static function with a different area/table) all
 *     funnel through these same two call sites. Primary + double-battle
 *     calls.
 *   - 0x10C3A94 / 0x10C3AD0: inside FishingWildEncounter (GenerateFishing-
 *     WildMon is inlined into it at -O2; confirmed via the FISHING_MONS_
 *     HEADER=2 LoadProperMonsData call and the gFishingByte=TRUE store) --
 *     covers every fishing rod tier, since the rod only selects which row
 *     of the fishing table ChooseWildMonIndex_Fishing reads BEFORE this
 *     call; the call site itself is rod-agnostic. Primary + double-battle
 *     calls.
 *
 * Deliberately NOT hooked (verified by decompiled/disassembled argument
 * shape at each remaining CreateWildMon call site in the ROM):
 *   - TryGenerateSwarmMon's own CreateWildMon call (swarms; not one of the
 *     required table types, left at vanilla behavior).
 *   - sp156_StartGhostBattle (Old Man Marowak) and the sp118_StartRaidBattle-
 *     adjacent scripted encounter -- both read a fixed global/special-var
 *     species with monHeaderIndex hardcoded to 0, the signature of a
 *     scripted encounter, not a table roll.
 *   - Both dexnav.c call sites -- DexNav re-encounters a species the player
 *     already deliberately chose to search for, not a random roll.
 * All of the above keep their original BL straight to CreateWildMon.
 *
 * Semantics: after CreateWildMon would normally run with the table's own
 * rolled (species, level), a 10% roll can override JUST the species (level
 * is left exactly as rolled -- the override instead picks whichever
 * evolution stage of the chosen family fits that level) with a random
 * non-legendary member of the active character's roster, expanded to full
 * evolution families (same data as the catch-gate bitmap). Inert whenever
 * Character Mode is off, no character is selected, or the roll misses --
 * falls through to the exact original CreateWildMon call every time.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FLAG_CHARACTER_MODE 0x18FE
#define VAR_CHARACTER_ID    0x51FD
#define NUM_CHARACTERS      184
#define OVERRIDE_CHANCE_PCT 10

/* Vanilla FRLG functions (CFRU BPRE.ld addresses -- same convention as
 * src/character_mode.c). */
#define FlagGet ((u8  (*)(u16))   0x0806E6D1)
#define VarGet  ((u16 (*)(u16))   0x0806E569)
#define Random  ((u16 (*)(void))  0x08044EC9)

/* RR/CFRU CreateWildMon (confirmed compiled address, docs/ROUTINE_MAP.md). */
#define CreateWildMon ((void (*)(u16, u8, u8, u8)) 0x090C292D)

/* Filled in at injection time: tools/inject_character_mode.py compiles this
 * file with -DWILD_OFFSETS_ADDR=<...> -DWILD_DATA_ADDR=<...>, the addresses
 * where wild_override_offsets.bin / wild_override.bin (both built by
 * tools/character_mode/emit_wild_override.py) are placed in ROM. */
#ifndef WILD_OFFSETS_ADDR
#error "compile with -DWILD_OFFSETS_ADDR=0x08xxxxxx"
#endif
#ifndef WILD_DATA_ADDR
#error "compile with -DWILD_DATA_ADDR=0x08xxxxxx"
#endif

/* wild_override.bin layout per character (see emit_wild_override.py):
 *   u8 num_families
 *   num_families * { u8 num_stages; num_stages * (u16 species, u8 lvlMin, u8 lvlMax) }
 *
 * Picks a random non-legendary family, then the stage within that family
 * whose [lvlMin, lvlMax] best fits `level` (nearest by absolute distance;
 * ties -- only possible where the ROM's own evolution data has no level
 * threshold between two stages -- prefer the LATER/more-evolved stage, a
 * documented heuristic, not canon data; see emit_wild_override.py). Returns
 * 0 (never a real species id) if the character has no eligible family.
 */
static u16 CM_PickWildOverrideSpecies(u16 charIdx, u8 level)
{
    const u8 *p = (const u8 *) WILD_DATA_ADDR
                + *(const u32 *) (WILD_OFFSETS_ADDR + (u32) charIdx * 4);
    u8 numFam = *p++;
    u8 famIdx, i, numStages;
    u16 best = 0;
    u8 bestDist = 0xFF;

    if (numFam == 0)
        return 0;

    famIdx = Random() % numFam;
    for (i = 0; i < famIdx; ++i) {
        u8 n = *p++;
        p += (u32) n * 4;
    }

    numStages = *p++;
    for (i = 0; i < numStages; ++i) {
        u16 sid = p[0] | (p[1] << 8);
        u8 lo = p[2];
        u8 hi = p[3];
        u8 dist;
        p += 4;

        if (level < lo)
            dist = lo - level;
        else if (level > hi)
            dist = level - hi;
        else
            dist = 0;

        if (dist <= bestDist) {
            bestDist = dist;
            best = sid;
        }
    }
    return best;
}

void CM_CreateWildMonGated(u16 species, u8 level, u8 monHeaderIndex, u8 purgeParty)
{
    if (FlagGet(FLAG_CHARACTER_MODE)) {
        u16 id = VarGet(VAR_CHARACTER_ID);

        if (id >= 1 && id <= NUM_CHARACTERS && (Random() % 100) < OVERRIDE_CHANCE_PCT) {
            u16 replacement = CM_PickWildOverrideSpecies(id - 1, level);
            if (replacement != 0)
                species = replacement;
        }
    }
    CreateWildMon(species, level, monHeaderIndex, purgeParty);
}
