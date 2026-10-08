/* Field moves without a compatible Pokemon, for Radical Red (CFRU, FireRed).
 *
 * User ruling 2026-10-04 (../game_plans/field_moves.md): with Character Mode
 * on, an HM in the bag plus its badge lets ANY party mon use the field move.
 * Its own compile unit and link address (FIELD_MOVES_ADDR), like pc_guard.c:
 * the main shim is capped at 1 KB by the roster bitmaps right after it.
 *
 * RR already needs no Pokemon for most field moves (measured 2026-10-07,
 * docs/ROUTINE_MAP.md "Field moves"): Surf, Waterfall and Flash check only
 * the HM item, Fly is used from the HM02 item, and RR's own Cut / Rock Smash /
 * Strength objects (0x0904DDC8 / 0x0904DE08 / 0x0904DE58) check only the
 * badge and the item. Two gates are left, and both come here:
 *
 *   1. CFRU's PartyHasMonWithFieldMovePotential (0x090B2540) asks
 *      CanMonLearnTMTutor once (bl at 0x090B25BC), after it has seen the HM
 *      in the bag. It decides Dive, Rock Climb and specials 0x10A-0x10C.
 *      CM_FieldMoveCanLearn answers "can learn" for HM01-HM08 with the mode
 *      on, like Unbound's CharacterMode_FieldMoveCanLearn.
 *
 *   2. 67 objects on live maps (9 Cut trees, 34 Rock Smash rocks, 24 Strength
 *      boulders: Viridian City, Sevii) still run FireRed's own scripts, which
 *      check the badge and then `checkpartymove` (a mon must KNOW the move).
 *      ScrCmd_checkpartymove's MonKnowsMove call (bl at 0x0806C0D0) comes here
 *      through a trampoline at CheckHeap+16 (too far for a bl).
 *      CM_FieldMoveKnows also says yes for a non-egg mon when the move is an
 *      HM move and its HM is in the bag. The script has already checked the
 *      badge.
 *
 * With Character Mode off, both return the original function's answer.
 *
 * ⚠️ RR's injector keeps ONLY .text: no statics, no string literals, no
 * lookup tables (hence the if-chain below).
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/* Restated from src/character_mode.c (same ROM, same values). */
#define FLAG_CHARACTER_MODE 0x18FE
#define MON_DATA_IS_EGG     45
#define FlagGet    ((u8  (*)(u16))                 0x0806E6D1)
#define GetMonData ((u32 (*)(void *, int, void *)) 0x0803FBE9)

#define CheckBagHasItem    ((u8 (*)(u16, u16))      0x08099F41)
#define MonKnowsMove       ((u8 (*)(void *, u16))   0x08125AC1)
#define CanMonLearnTMTutor ((u8 (*)(void *, u16, u8)) 0x090A5909)

#define CAN_LEARN_MOVE 0
#define ITEM_HM01      339     /* HM01..HM08 are 339..346 (item table 0x093C0000) */
#define ITEM_HM08      346

/* The HM whose item lets a mon use this move (0 = not a field move).
 * RR's HM05 is Flash; Dive and Rock Climb both use HM08 (RR passes 346 for
 * both in PartyHasMonWithFieldMovePotential's callers). */
static u16 hmForMove(u16 move)
{
    if (move == 15)  return 339;   /* Cut */
    if (move == 19)  return 340;   /* Fly */
    if (move == 57)  return 341;   /* Surf */
    if (move == 70)  return 342;   /* Strength */
    if (move == 148) return 343;   /* Flash */
    if (move == 249) return 344;   /* Rock Smash */
    if (move == 127) return 345;   /* Waterfall */
    if (move == 291) return 346;   /* Dive */
    if (move == 392) return 346;   /* Rock Climb */
    return 0;
}

u8 CM_FieldMoveCanLearn(void *mon, u16 item, u8 tutor)
{
    if (tutor == 0 && item >= ITEM_HM01 && item <= ITEM_HM08
        && FlagGet(FLAG_CHARACTER_MODE)
        && !GetMonData(mon, MON_DATA_IS_EGG, 0))
        return CAN_LEARN_MOVE;
    return CanMonLearnTMTutor(mon, item, tutor);
}

u8 CM_FieldMoveKnows(void *mon, u16 move)
{
    u16 hm;

    if (MonKnowsMove(mon, move))
        return 1;
    hm = hmForMove(move);
    if (hm != 0 && FlagGet(FLAG_CHARACTER_MODE)
        && !GetMonData(mon, MON_DATA_IS_EGG, 0)
        && CheckBagHasItem(hm, 1))
        return 1;
    return 0;
}
