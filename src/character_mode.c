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
#define VAR_CHARACTER_ID    0x51FD
#define NUM_CHARACTERS      184
#define NUM_SPECIES         1376
#define BITMAP_STRIDE       172

#define MON_DATA_SPECIES 11
#define MON_DATA_IS_EGG  45

/* Vanilla FRLG functions (CFRU BPRE.ld addresses; expanded flag/var ids are
 * routed by RR's own ExpandedFlagsHook/ExpandedVarsHook transparently). */
#define FlagGet    ((u8  (*)(u16))                 0x0806E6D1)
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
