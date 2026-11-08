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
 * CM_NewGameExpShare (user, 2026-10-21: the early party-wide Exp. Share with
 * Character Mode OFF too; the catch rules stay CM-only): NewGameInitData's last
 * call (bl ResetTrainerTowerResults @ 0x08054B3E, after ClearBag and the map-flag
 * reset) goes through a CheckHeap+24 trampoline to here. It runs that call, then
 * gives every new game -- CM on or off -- one Exp. Share, switched on. Existing
 * saves are untouched (they never run NewGameInitData again); a CM player who
 * activates later already has it, so the activation grant above adds nothing.
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
#define ResetTrainerTowerResults ((void (*)(void)) 0x0815EE0D)

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

/* QoL C11 + C16 (2026-11-07, the same new-game call, CM on or off): Running Shoes (FLAG_SYS_B_DASH 0x82F), the
 * Bicycle (360) with the Cerulean bike shop's own flag (0x271: its vanilla script at 0x0816AC30 gives 360 and sets
 * it, so the shop then says it was handed out), and the Shiny (471) + Oval (470) Charms -- RR's CFRU code asks the bag
 * for both (CheckBagHasItem(471) at 0x0907785A, (470) at 0x090884AA). Written out call by call: this unit keeps
 * only .text, no tables. CM_NO_STARTKIT builds the control. */
#define FLAG_SYS_B_DASH 0x82F
#define FLAG_GOT_BICYCLE 0x271
#define ITEM_BICYCLE 360
#define ITEM_OVAL_CHARM 470
#define ITEM_SHINY_CHARM 471

void CM_NewGameExpShare(void)
{
    ResetTrainerTowerResults();
    if (!CheckBagHasItem(ITEM_EXP_SHARE, 1) && AddBagItem(ITEM_EXP_SHARE, 1))
        FlagSet(FLAG_EXP_SHARE);
#ifndef CM_NO_STARTKIT
    FlagSet(FLAG_SYS_B_DASH);
    if (!FlagGet(FLAG_GOT_BICYCLE) && !CheckBagHasItem(ITEM_BICYCLE, 1))
        AddBagItem(ITEM_BICYCLE, 1);
    FlagSet(FLAG_GOT_BICYCLE);
    if (!CheckBagHasItem(ITEM_SHINY_CHARM, 1))
        AddBagItem(ITEM_SHINY_CHARM, 1);
    if (!CheckBagHasItem(ITEM_OVAL_CHARM, 1))
        AddBagItem(ITEM_OVAL_CHARM, 1);
#endif
}
