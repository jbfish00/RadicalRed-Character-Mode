/* Character Mode enforcement shim for Pokemon Radical Red v4.1.
 *
 * Replaces the two BL GiveMonToPlayer call sites (atkF0_givecaughtmon at
 * 0x0907DD84, ScriptGiveMon at 0x090777CE — see docs/ROUTINE_MAP.md) so
 * that, when Character Mode is active, catching or being gifted an
 * off-roster species sends it straight to the PC instead of the party —
 * the same semantics as ROWE's GiveMonToPlayer hook. Both callers already
 * branch on `result != MON_GIVEN_TO_PARTY` and display the correct
 * "sent to Box" messaging, so no message plumbing is needed here.
 *
 * The Battle Frontier rental-mon delivery paths keep their original BLs
 * and are untouched by construction (the ROWE/CFRU rental caveat).
 *
 * Soft-lock guard: never gates while the party is empty, so the player's
 * first mon (their character's signature, delivered by the selection
 * script — or RR's own starter if they somehow skip it) always lands in
 * the party.
 *
 * Eggs are exempt, matching ROWE (`!GetMonData(mon, MON_DATA_IS_EGG)`).
 *
 * All fixed addresses below are CONFIRMED for this exact ROM (rom.sha1);
 * see docs/ROUTINE_MAP.md for the provenance of every one.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FLAG_CHARACTER_MODE 0x18FE

/* Radical Red's own Species Randomizer, which is MUTUALLY EXCLUSIVE with
 * Character Mode. Its in-game description says it "randomizes encounters,
 * trainers, and gifts", and CFRU implements that in CreateBoxMon() via
 * TryRandomizeSpecies() -- i.e. at mon CREATION, downstream of everything we
 * do. With it on, the 10% roster override picks a roster species and
 * CreateBoxMon then remaps it to an unrelated one, so the catch gate rejects
 * what it was handed: Character Mode degrades to "you can catch almost
 * nothing", silently. ROWE hit exactly this and made the two modes exclusive.
 *
 * Flag id cross-validated two ways: CFRU's own config.h carries
 * `//#define FLAG_POKEMON_RANDOMIZER 0x940` as the stock value, and decoding
 * Radical Red's randomizer cheat script gives `29 40 09` (setflag 0x0940) with
 * `2b 40 09` (checkflag 0x0940) at its branch sites. */
#define FLAG_POKEMON_RANDOMIZER 0x940

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
#define NUM_SPECIES         1376
#define BITMAP_STRIDE       172

#define MON_DATA_SPECIES 11
#define MON_DATA_IS_EGG  45

/* Vanilla FRLG functions (CFRU BPRE.ld addresses; expanded flag/var ids are
 * routed by RR's own ExpandedFlagsHook/ExpandedVarsHook transparently). */
#define FlagGet    ((u8  (*)(u16))                 0x0806E6D1)
/* FlagClear: body is byte-identical to FlagSet (0x0806E681) except it uses
   `bics` where FlagSet uses `orrs` -- disassembled in THIS ROM, not taken from
   BPRE.ld. Needed for the Species Randomizer exclusion below. */
#define FlagClear  ((u8  (*)(u16))                 0x0806E6A9)
/* Character Mode wins. Called from the paths that run constantly, so enabling
 * the randomizer mid-run cannot quietly break enforcement either -- the
 * exclusion is a live invariant, not a one-shot at selection. */
static void cmEnforceModeExclusion(void)
{
    if (FlagGet(FLAG_CHARACTER_MODE) && FlagGet(FLAG_POKEMON_RANDOMIZER))
        FlagClear(FLAG_POKEMON_RANDOMIZER);
}
#define VarGet     ((u16 (*)(u16))                 0x0806E569)
#define GetMonData ((u32 (*)(void *, int, void *)) 0x0803FBE9)

/* RR/CFRU functions (confirmed compiled addresses, docs/ROUTINE_MAP.md). */
#define GiveMonToPlayer ((u8 (*)(void *)) 0x0907D791)
#define SendMonToPC     ((u8 (*)(void *)) 0x090B6E39)

#define gPlayerPartyCount (*(volatile u8 *) 0x02024029)

/* Filled in at injection time: the injector compiles this file with
 * -DBITMAPS_ADDR=<address where rosters_expanded.bin was placed>. */
#ifndef BITMAPS_ADDR
#error "compile with -DBITMAPS_ADDR=0x08xxxxxx"
#endif

u8 CM_GiveMonToPlayerGated(void *mon)
{
    cmEnforceModeExclusion();
    if (FlagGet(FLAG_CHARACTER_MODE) && gPlayerPartyCount != 0) {
        u16 id = VarGet(VAR_CHARACTER_ID);

        if (id >= 1 && id <= NUM_CHARACTERS
         && !GetMonData(mon, MON_DATA_IS_EGG, 0)) {
            u32 species = GetMonData(mon, MON_DATA_SPECIES, 0);

            if (species > 0 && species < NUM_SPECIES) {
                const u8 *bm = (const u8 *) BITMAPS_ADDR + (id - 1) * BITMAP_STRIDE;

                if (!(bm[species >> 3] & (1 << (species & 7))))
                    return SendMonToPC(mon);
            }
        }
    }
    return GiveMonToPlayer(mon);
}
