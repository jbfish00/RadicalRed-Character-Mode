/* 100% catch for on-roster species, Radical Red (CFRU, FireRed). User, 2026-10-09.
 *
 * CFRU's atkEF_handleballthrow (0x0907CFF0) builds the capture odds in r4 --
 * GetBaseBallCatchOdds, then the wild-double, low-level, status, SwSh-difficulty
 * and raid modifiers -- and decides at 0x0907D552:
 *     cmp r4, #254 ; bls 0x0907D590        (> 254: caught, three shakes)
 * 0x0907D590 is the not-yet-caught path: FlagGet(0x109D) (RR's own
 * always-catchable flag), then the shake rolls.
 *
 * Those 4 bytes become a BL here (0x08CFE000 is in BL reach). There is no room
 * to keep the `bls`, so the stub takes the branch itself: back to 0x0907D556
 * (caught) when the odds are above 254, else to 0x0907D590 -- exactly where the
 * original pair went. With Character Mode on and the target's species on the
 * active roster the odds become 255. Hooking the FINAL odds, after every
 * modifier, means none of them (the /10 SwSh difficulty, x0.3 wild doubles)
 * can pull a guaranteed catch back under 255.
 *
 * Off-roster species keep their odds; the acquisition gate still sends them to
 * the PC (CM_GiveMonToPlayerGated). The species is the PARTY Pokemon's
 * (gEnemyParty[gBattlerPartyIndexes[gBankTarget]]), not gBattleMons[]:
 * Transform overwrites the battle species (Platinum, 2026-10-08). Addresses
 * are the literals handleballthrow itself loads (0x0907D6FC / D734 / D738).
 * Registers: r0-r3 and r12 are dead at the site (both successors reload them),
 * r4 carries the odds, r6 is preserved.
 *
 * Its own unit and link address (SURE_CATCH_ADDR), like field_moves.c: only
 * .text survives the injector, so no statics, strings or tables.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/* Restated from src/character_mode.c (same ROM, same values). */
#define FLAG_CHARACTER_MODE 0x18FE
#define VAR_CHARACTER_ID    0x51FD
#define NUM_SPECIES         1376
#define BITMAP_STRIDE       172
#define MON_DATA_SPECIES    11
#define FlagGet    ((u8  (*)(u16))                 0x0806E6D1)
#define VarGet     ((u16 (*)(u16))                 0x0806E569)
#define GetMonData ((u32 (*)(void *, int, void *)) 0x0803FBE9)

#ifndef BITMAPS_ADDR
#error "compile with -DBITMAPS_ADDR= and -DNUM_CHARACTERS= (the injector passes both)"
#endif
#ifndef NUM_CHARACTERS
#error "compile with -DNUM_CHARACTERS="
#endif

#define gBankTarget          (*(volatile u8 *) 0x02023D6C)
#define gBattlerPartyIndexes ((volatile u16 *) 0x02023BCE)
#define gEnemyParty          ((u8 *)           0x0202402C)
#define MON_SIZE             100
#define CATCH_ODDS_SURE      255

__attribute__((noinline, used)) u32 CM_CatchOdds(u32 odds)
{
    if (FlagGet(FLAG_CHARACTER_MODE)) {
        u16 id = VarGet(VAR_CHARACTER_ID);
        if (id >= 1 && id <= NUM_CHARACTERS) {
            u8 *mon = gEnemyParty + gBattlerPartyIndexes[gBankTarget] * MON_SIZE;
            u32 species = GetMonData(mon, MON_DATA_SPECIES, 0);
            if (species > 0 && species < NUM_SPECIES) {
                const u8 *bm = (const u8 *) BITMAPS_ADDR + (id - 1) * BITMAP_STRIDE;
                if (bm[species >> 3] & (1 << (species & 7)))
                    return CATCH_ODDS_SURE;
            }
        }
    }
    return odds;
}

__attribute__((naked)) void CM_CatchOddsStub(void)
{
    __asm__ volatile(
        "push {lr}\n\t"
        "mov r0, r4\n\t"
        "bl CM_CatchOdds\n\t"
        "mov r4, r0\n\t"
        "pop {r1}\n\t"          /* 0x0907D557: the caught path, Thumb bit set */
        "cmp r4, #254\n\t"
        "bhi 1f\n\t"
        "add r1, #58\n\t"       /* 0x0907D591: the original bls target */
        "1:\n\t"
        "bx r1\n\t");
}
