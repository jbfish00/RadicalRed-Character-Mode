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
 * rolled (species, level), a roll can override JUST the species (level
 * is left exactly as rolled -- the override instead picks whichever
 * evolution stage of the chosen family fits that level). Two independent
 * rolls, legendary first (spec: ../../game_plans/legendary_encounters.md,
 * design locked by the user 2026-07-26):
 *
 *     1%  -> a legendary from this character's roster
 *     10% -> a non-legendary roster member  (the original feature, unchanged)
 *     else -> the game's own wild table
 *
 * Inert whenever Character Mode is off, no character is selected, or both
 * rolls miss -- falls through to the exact original CreateWildMon call.
 *
 * A character with NO legendary is byte-identical to the pre-legendary build:
 * the legendary roll is skipped on a data check (numFamilies == 0) BEFORE any
 * Random() call, so its RNG stream is untouched. That ordering is deliberate,
 * not incidental -- rolling first and discarding would shift every subsequent
 * encounter for ~62% of the roster.
 *
 * Legendaries are offered until CAUGHT, then retired. "Caught" is read from the
 * Pokedex, which costs zero new save state -- the only reason this is
 * implementable in a closed binary whose save layout cannot grow. The one
 * exemption is flags bit0 (`repeatable`), set at emit time for a character with
 * no non-legendary families at all: without it, Cogita -- whose entire roster is
 * one legendary family -- would catch it once and then be able to catch nothing
 * for the rest of the run.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FLAG_CHARACTER_MODE 0x18FE
#define VAR_CHARACTER_ID    0x51FD
/* The injector passes -DNUM_CHARACTERS, derived from characters_manifest.json.
 * It is NOT hardcoded on purpose: this constant bounds the character-index range
 * the shim accepts, so a stale value makes the shim trust an index past the end
 * of the bitmap table instead of rejecting it -- a silent failure, not a build
 * error. The fallback below only applies to a hand-compile outside the injector.
 * (Was a bare 210 until the 2026-07-25 roster audit took the count to 238.) */
#ifndef NUM_CHARACTERS
#define NUM_CHARACTERS      238
#endif
#define OVERRIDE_CHANCE_PCT  10
#define LEGENDARY_CHANCE_PCT 1
/* Tobias used to be hardcoded here (TOBIAS_CHAR_ID / TOBIAS_CHANCE_PCT, with
 * -DTOBIAS_CHAR_ID derived by the injector) as the one character with a 1%
 * legendary-inclusive table. The general rule above subsumes it exactly: his
 * non-legendary pool is empty and both his legendaries are in the 1% table,
 * marked repeatable. The special case was deleted across all three of its sites
 * at once (here, the injector, and emit_wild_override.py) -- deleting only some
 * would have left two mechanisms disagreeing silently. */

/* Vanilla FRLG functions (CFRU BPRE.ld addresses -- same convention as
 * src/character_mode.c). */
#define FlagGet ((u8  (*)(u16))   0x0806E6D1)
#define VarGet  ((u16 (*)(u16))   0x0806E569)
#define Random  ((u16 (*)(void))  0x08044EC9)

/* Pokedex accessors. Both verified by disassembly in THIS ROM on 2026-07-26,
 * not taken on trust from CFRU's BPRE.ld:
 *   0x08043298  push{lr}; u16 cast; cmp 0 -> return 0; ldr from a literal pool
 *               holding 0x098218F0; [species-1]*2; ldrh   == the real
 *               gSpeciesToNationalPokedexNum lookup.
 *   0x08088E74  push{lr}; u16 cast r0; u8 cast r1; movs r2,#0; bl 0x08104AB0.
 *               That `movs r2,#0` is exactly what makes it take a NATIONAL DEX
 *               NUMBER rather than a species id.
 * The distinction is not academic in this FireRed family: species 386 is
 * national dex 313 (Volbeat). Passing a species id would silently filter the
 * wrong Pokemon, which looks identical to the feature never firing.
 * The call is a bare ldrb + AND + compare out of EWRAM -- no writes, no
 * allocation, no reentrancy -- so it is safe from the encounter hook. */
#define SpeciesToNationalPokedexNum ((u16 (*)(u16))     0x08043299)
#define GetSetPokedexFlag           ((u8  (*)(u16, u8)) 0x08088E75)
#define FLAG_GET_CAUGHT     1
#define LEG_FLAG_REPEATABLE 0x1

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
#ifndef WILD_LEG_OFFSETS_ADDR
#error "compile with -DWILD_LEG_OFFSETS_ADDR=0x08xxxxxx"
#endif
#ifndef WILD_LEG_DATA_ADDR
#error "compile with -DWILD_LEG_DATA_ADDR=0x08xxxxxx"
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
/* Level-match ONE family block. *pp points at its u8 num_stages; on return it
 * points just past the block, so callers can walk a whole character's list.
 * Shared by both tables -- the legendary pool uses exactly the same level
 * matching, per spec §1.4 (no fixed canon levels; a level-70 Mewtwo on route 1
 * would be a different feature). */
static u16 CM_MatchStage(const u8 **pp, u8 level)
{
    const u8 *p = *pp;
    u8 numStages = *p++;
    u8 i;
    u16 best = 0;
    u8 bestDist = 0xFF;

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
    *pp = p;
    return best;
}

static u16 CM_PickWildOverrideSpecies(u16 charIdx, u8 level)
{
    const u8 *p = (const u8 *) WILD_DATA_ADDR
                + *(const u32 *) (WILD_OFFSETS_ADDR + (u32) charIdx * 4);
    u8 numFam = *p++;
    u8 famIdx, i;

    if (numFam == 0)
        return 0;

    famIdx = Random() % numFam;
    for (i = 0; i < famIdx; ++i) {
        u8 n = *p++;
        p += (u32) n * 4;
    }
    return CM_MatchStage(&p, level);
}

/* TRUE once this legendary has been caught, so it can leave the pool.
 *
 * The null guard is mandatory, not defensive. Radical Red inlined
 * GetSetPokedexFlag's body (0x08104AB0) WITHOUT CFRU's
 * FixPokedexCheckNullSpeciesHook, so a national dex number of 0 does
 * `subs r0, r3, #1` -> 0xFFFF, >>3 -> 8191, then a lsls/lsrs #24 truncation
 * makes the byte index 255 -- into a 164-byte array. 32 species ids in this ROM
 * map to national dex 0 (the three Paldean Tauros, three Mega forms, and
 * vanilla's unused 252-276/412 slots); none of them is a legendary today, and
 * emit_wild_override.py reports it if that ever changes.
 *
 * We never hand the dex a 0. Treating it as "not caught" leaves such a legendary
 * permanently offered, which is a much better failure than an out-of-bounds read
 * or a silently empty pool. This guards OUR call site only -- Radical Red's own
 * dex call sites are deliberately left alone (user decision, 2026-07-26: this
 * project has never patched base-game behaviour, and whether the base game can
 * actually reach the bug was not determined).
 */
static u8 CM_LegendaryCaught(u16 species)
{
    u16 dex = SpeciesToNationalPokedexNum(species);

    if (dex == 0)
        return 0;
    return GetSetPokedexFlag(dex, FLAG_GET_CAUGHT);
}

/* A uniformly random ELIGIBLE legendary from this character's 1% table, or 0.
 * Eligible = not yet caught, unless the character is flagged repeatable.
 *
 * noinline is deliberate and load-bearing for the tests, not a performance hint.
 * At -O2 gcc inlined this whole function into CM_CreateWildMonGated and left no
 * symbol behind, and without a symbol the only way to observe the legendary path
 * is to wait for a 1% roll -- at which point "zero legendaries in 200 trials"
 * cannot be told apart from a dead feature (the trap
 * game_plans/legendary_encounters.md §5 names as the biggest risk here).
 * tools/tests/wild_encounter_shim_test.py calls this directly, roll bypassed,
 * and asserts in the positive direction. The cost is one real call per 1% roll.
 */
static u16 __attribute__((noinline)) CM_PickLegendarySpecies(u16 charIdx, u8 level)
{
    const u8 *base = (const u8 *) WILD_LEG_DATA_ADDR
                   + *(const u32 *) (WILD_LEG_OFFSETS_ADDR + (u32) charIdx * 4);
    u8 repeatable = base[0] & LEG_FLAG_REPEATABLE;
    u8 numFam = base[1];
    const u8 *p;
    u8 i, eligible = 0, pick;
    u16 sid;

    if (numFam == 0)
        return 0;

    /* Two passes, because the eligible count is not known up front and there is
     * nowhere to store a list. The test is applied to the stage THIS AREA'S
     * LEVEL would actually produce, not to the family base -- for the one
     * genuinely multi-stage legendary line (Cosmog -> Cosmoem ->
     * Solgaleo/Lunala) that is the difference between "the one you would meet
     * here is already caught" and "somebody in the line is caught". */
    p = base + 2;
    for (i = 0; i < numFam; ++i) {
        sid = CM_MatchStage(&p, level);
        if (sid != 0 && (repeatable || !CM_LegendaryCaught(sid)))
            ++eligible;
    }
    if (eligible == 0)
        return 0;

    pick = Random() % eligible;
    p = base + 2;
    for (i = 0; i < numFam; ++i) {
        sid = CM_MatchStage(&p, level);
        if (sid != 0 && (repeatable || !CM_LegendaryCaught(sid))) {
            if (pick == 0)
                return sid;
            --pick;
        }
    }
    return 0;
}

void CM_CreateWildMonGated(u16 species, u8 level, u8 monHeaderIndex, u8 purgeParty)
{
    if (FlagGet(FLAG_CHARACTER_MODE)) {
        u16 id = VarGet(VAR_CHARACTER_ID);

        if (id >= 1 && id <= NUM_CHARACTERS) {
            const u8 *leg = (const u8 *) WILD_LEG_DATA_ADDR
                          + *(const u32 *) (WILD_LEG_OFFSETS_ADDR
                                            + (u32) (id - 1) * 4);
            u16 replacement = 0;

            /* The data check comes BEFORE the roll on purpose. ~62% of
             * characters have no legendary, and rolling-then-discarding for them
             * would consume an RNG value the pre-legendary build did not,
             * shifting every subsequent encounter. This way they are provably
             * unaffected. */
            if (leg[1] != 0 && (Random() % 100) < LEGENDARY_CHANCE_PCT)
                replacement = CM_PickLegendarySpecies(id - 1, level);

            /* Independent second roll: a missed (or exhausted) legendary roll
             * falls through to the original 10% feature, unchanged. */
            if (replacement == 0 && (Random() % 100) < OVERRIDE_CHANCE_PCT)
                replacement = CM_PickWildOverrideSpecies(id - 1, level);

            if (replacement != 0)
                species = replacement;
        }
    }
    CreateWildMon(species, level, monHeaderIndex, purgeParty);
}
