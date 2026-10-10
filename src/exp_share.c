/* Early party-wide Exp. Share, Radical Red (CFRU, FireRed). User, 2026-10-09:
 * "make sure for all hacks exp. share is obtained early and applies to the
 * pokemon in the party like for Unbound".
 *
 * RR already has the party-wide device: item 182 (description "Turning on this
 * special device will allow all Pokemon in your party to receive Exp."), whose
 * field use runs the script at 0x088015C8 -- checkflag/setflag/clearflag 0x906
 * (CFRU's FLAG_EXP_SHARE; with it set, exp.c gives every party member a share).
 * RR hands it out only after the first gym (script 0x0905AFEC).
 *
 * CM_ActivateSweepAndExpShare replaces the party sweep's callnative everywhere
 * the scripts run it -- every character handler of the bedroom console, the
 * egg-hatch tail and the PC-exit tail (verify_artifacts requires all three to
 * name the same function). It runs the sweep exactly as before, then, with
 * Character Mode on and no Exp. Share in the bag, adds one and switches it on.
 * The hatch and PC tails run with the mode off too; the flag test keeps them
 * from granting anything then.
 * Only on that first grant -- a player who later turns it off keeps it off,
 * and the gym gift then just adds a second, harmless copy.
 *
 * Its own unit and link address (EXP_SHARE_ADDR): only .text survives the
 * injector, so no statics, strings or tables.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FLAG_CHARACTER_MODE 0x18FE   /* restated from src/character_mode.c */
#define ITEM_EXP_SHARE  182
#define FLAG_EXP_SHARE  0x906
#define FlagGet          ((u8 (*)(u16))      0x0806E6D1)
#define FlagSet          ((u8 (*)(u16))      0x0806E681)
#define CheckBagHasItem  ((u8 (*)(u16, u16)) 0x08099F41)
#define AddBagItem       ((u8 (*)(u16, u16)) 0x0809A085)

#ifndef SWEEP_PARTY
#error "compile with -DSWEEP_PARTY= (CM_SweepPartyToPC|1, from the main shim)"
#endif
#define SweepPartyToPC ((void (*)(void)) SWEEP_PARTY)

void CM_ActivateSweepAndExpShare(void)
{
    SweepPartyToPC();
    if (FlagGet(FLAG_CHARACTER_MODE) && !CheckBagHasItem(ITEM_EXP_SHARE, 1)
        && AddBagItem(ITEM_EXP_SHARE, 1))
        FlagSet(FLAG_EXP_SHARE);
}
