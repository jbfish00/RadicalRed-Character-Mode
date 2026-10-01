/* ROWE's second guard in the PC, for Radical Red (CFRU, FireRed).
 *
 * Its own compile unit and link address (PC_GUARD_ADDR), like the roster
 * display and the mugshot renderer: the main shim is capped at 1 KB by the
 * roster bitmaps right after it, and this does not fit there.
 *
 * Ported 2026-09-29 from the Seaglass/Lazarus ports (rowe_parity.md §13.53);
 * every address below re-derived from THIS binary (docs/ROUTINE_MAP.md "PC
 * second guard"). The PC-withdraw hook is undo-on-exit, and the sweep's
 * never-empty rule KEEPS an off-roster mon when nothing on the roster is left,
 * so "deposit your only on-roster mon, withdraw an off-roster one" still ended
 * with the off-roster mon. ROWE closes that inside the storage system
 * (IsRemovingLastAllowedPartyMon); this is the same rule here.
 *
 * FireRed keeps IsRemovingLastPartyMon (0x08093900) as a real function, so
 * exactly two calls to CountPartyAliveNonEggMonsExcept are taken over: its
 * one and CanShiftMon's (0x0809393C). Both are BL-retargeted through one
 * trampoline (written over the unused debug routine CheckHeap) to
 * CM_PSSLastMonGuard, which dispatches on its return address:
 *   - IsRemovingLastPartyMon: 0 ("that's your last POKEMON") when the cursor
 *     mon is the last alive, non-egg, on-roster one;
 *   - CanShiftMon: its tail is patched to return this function's answer
 *     directly: vanilla's egg/fainted rule plus ROWE's "don't swap your last
 *     on-roster mon out for an off-roster one".
 * With Character Mode off, both are exactly vanilla.
 *
 * ⚠️ RR's injector keeps ONLY .text: no statics, no string literals.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#ifndef NUM_CHARACTERS
#error "compile with -DNUM_CHARACTERS=<from characters_manifest.json>"
#endif
#ifndef BITMAPS_ADDR
#error "compile with -DBITMAPS_ADDR=0x08xxxxxx"
#endif

/* Restated from src/character_mode.c (same ROM, same values). */
#define FLAG_CHARACTER_MODE 0x18FE
#define VAR_CHARACTER_ID    0x51FD
#define NUM_SPECIES         1376
#define BITMAP_STRIDE       172
#define MON_DATA_SPECIES    11
#define MON_DATA_IS_EGG     45
#define MON_DATA_HP         57      /* CanShiftMon's own GetMonData(moving, 57) @0x08093972 */
#define MON_SIZE            100
#define FlagGet    ((u8  (*)(u16))                 0x0806E6D1)
#define VarGet     ((u16 (*)(u16))                 0x0806E569)
#define GetMonData ((u32 (*)(void *, int, void *)) 0x0803FBE9)
#define gPlayerParty ((u8 *) 0x02024284)

#define CountPartyAliveNonEggMonsExcept ((u8 (*)(u8)) 0x0808C185)
#define PSS_STORAGE            (*(u8 **) 0x020397B0)
#define PSS_MOVING_MON         0x20A0  /* gStorage->movingMon (literal @0x08093994) */
#define PSS_DISPLAY_MON_IS_EGG 0x0CE9  /* gStorage->displayMonIsEgg (literal @0x08093990) */
#define PSS_CANSHIFT_RET       0x0809395A  /* return address of CanShiftMon's call */

static int onRoster(u16 id, u32 species)
{
    const u8 *bm;
    if (species == 0 || species >= NUM_SPECIES)
        return 1;                       /* out of model -> never block */
    bm = (const u8 *) BITMAPS_ADDR + (id - 1) * BITMAP_STRIDE;
    return (bm[species >> 3] & (1 << (species & 7))) != 0;
}

static int removingLastAllowed(u8 slot, u16 id)
{
    const u8 *mon = gPlayerParty + slot * MON_SIZE;
    u32 species;
    int i;

    species = GetMonData((void *) mon, MON_DATA_SPECIES, 0);
    if (species == 0 || GetMonData((void *) mon, MON_DATA_IS_EGG, 0)
        || !onRoster(id, species))
        return 0;
    for (i = 0; i < 6; i++) {
        if (i == slot)
            continue;
        mon = gPlayerParty + i * MON_SIZE;
        species = GetMonData((void *) mon, MON_DATA_SPECIES, 0);
        if (species != 0
            && !GetMonData((void *) mon, MON_DATA_IS_EGG, 0)
            && GetMonData((void *) mon, MON_DATA_HP, 0) != 0
            && onRoster(id, species))
            return 0;
    }
    return 1;
}

u32 CM_PSSLastMonGuard(u8 slot)
{
    u32 ret = (u32) __builtin_return_address(0) & ~1u;
    u8 alive = CountPartyAliveNonEggMonsExcept(slot);
    u16 id = 0;
    int guarded;

    if (FlagGet(FLAG_CHARACTER_MODE) && slot < 6) {
        id = VarGet(VAR_CHARACTER_ID);
        if (id < 1 || id > NUM_CHARACTERS)
            id = 0;
    }
    guarded = id != 0 && removingLastAllowed(slot, id);

    if (ret == PSS_CANSHIFT_RET) {
        u8 *storage = PSS_STORAGE;
        u8 *moving = storage + PSS_MOVING_MON;
        if (alive == 0 && (storage[PSS_DISPLAY_MON_IS_EGG]
                           || GetMonData(moving, MON_DATA_HP, 0) == 0))
            return 0;
        if (guarded && !onRoster(id, GetMonData(moving, MON_DATA_SPECIES, 0)))
            return 0;
        return 1;
    }
    if (alive != 0 && guarded)
        return 0;
    return alive;
}
