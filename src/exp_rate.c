/* EXP rate (QoL, user 2026-10-29): battle EXP x0.5 / x1 / x1.5 / x2 / x3, every save (Character Mode on or off).
 * game_plans/EXP_RATE_PLAN.md. Storage: expanded var 0x51FC (save-persistent, zero script/literal hits in RR 4.1,
 * like VAR_CHARACTER_ID 0x51FD): 0 = x1 (every existing save), 1 = x1.5, 2 = x2, 3 = x3, 4 = x0.5.
 *
 * Multiply: CFRU's atk23_getexp computes the award with ExpCalculator, then `MathMin(0x190640, exp)` (BL at
 * 0x09094A82) and `MathMax(1, ...)`, and stores the result as both calculatedExp (the "gained N EXP" text) and
 * gBattleMoveDamage (the exp update). The hard-level-cap path (award 1) jumps past the MathMin to the MathMax, so
 * CM_ExpRateMin scales only real awards: min(cap, award * N / 2), never 0. Unbound has the same code at 0x089E2006.
 *
 * Control: RR's START menu keeps its main page at 7 rows (the HELP bar sits under row 7) and puts extras on a
 * second page (RIGHT: Dexnav, PC, Exit <-) that CFRU offers only with the Dexnav flag. The page is now always
 * offered (CanSetUpSecondaryStartMenu -> TRUE) and "Exp Rate" (row 13 of a relocated action table) goes in before
 * its Exit <- (the shared append BL at 0x090BE1FC). Choosing it opens a list over the field with the cursor on the
 * current rate; A stores the row, B keeps the rate.
 *
 * Its own unit at EXP_RATE_ADDR: only .text survives the injector, so constants live in .text (TEXT) and the
 * strings and script are in the injector's data block (addresses passed with -D). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define TEXT __attribute__((section(".text")))

#ifndef EXPRATE_SCRIPT_ADDR
#error "compile with -DEXPRATE_SCRIPT_ADDR= -DEXPRATE_HEADER_ADDR= -DEXPRATE_ITEMS_ADDR= (injector data block)"
#endif
#define EXPRATE_ITEM_STRIDE 6

#define VAR_EXP_RATE        0x51FC
#define STARTMENU_EXIT_LEFT 12
#define STARTMENU_EXPRATE   13

#define VarGet                  ((u16 (*)(u16))      0x0806E569)
#define VarSet                  ((u8 (*)(u16, u16))  0x0806E585)
#define AppendToStartMenuItems  ((void (*)(u8))      0x0806ED95)
#define StartMenuExitCallback   ((u8 (*)(void))      0x0806F541)
#define ScriptContext_SetupScript ((void (*)(const u8 *)) 0x08069AE5)
#define EnableBothScriptContexts ((void (*)(void))   0x08069B35)
#define ResetPaletteFadeControl ((void (*)(void))    0x08070A85)
#define AddWindow               ((u8 (*)(const void *)) 0x08003CE5)
#define RemoveWindow            ((void (*)(u8))      0x08003E3D)
#define DrawStdWindowFrame      ((void (*)(u8, u8))  0x080F6F1D)
#define ClearStdWindowAndFrame  ((void (*)(u8, u8))  0x080F6F9D)
#define FillWindowPixelBuffer   ((void (*)(u8, u8))  0x0800445D)
#define CopyWindowToVram        ((void (*)(u8, u8))  0x08003F21)
#define AddTextPrinterParameterized ((u16 (*)(u8, u8, const u8 *, u8, u8, u8, void *)) 0x08002C49)
#define LoadStdWindowFrameGfx   ((void (*)(void))    0x080F6E9D)
#define ListMenuInit            ((u8 (*)(const void *, u16, u16)) 0x08106FF9)
#define ListMenu_ProcessInput   ((s32 (*)(u8))       0x08107079)
#define DestroyListMenuTask     ((void (*)(u8, u16 *, u16 *)) 0x0810713D)
#define ListMenuDefaultCursorMoveFunc ((void *)      0x08107AED)
#define CreateTask              ((u8 (*)(void (*)(u8), u8)) 0x0807741D)
#define DestroyTask             ((void (*)(u8))      0x08077509)
#define gBattleMoveDamage       (*(s32 *) 0x02023D50)
#define gPlttBufferUnfaded      ((const u32 *) 0x020371F8)
#define gPlttBufferFaded        ((u32 *) 0x020375F8)
#define FONT_NORMAL 2
#define LIST_NOTHING_CHOSEN (-1)

struct Task { void (*func)(u8); u8 isActive, prev, next, priority; s16 data[16]; };
#define gTasks ((struct Task *) 0x03005090)
struct WindowTemplate { u8 bg, tilemapLeft, tilemapTop, width, height, paletteNum; u16 baseBlock; };
struct ListMenuItem { const u8 *name; s32 id; };
struct ListMenuTemplate {
    const struct ListMenuItem *items;
    void *moveCursorFunc;
    void *itemPrintFunc;
    u16 totalItems;
    u16 maxShowed;
    u8 windowId, header_X, item_X, cursor_X;
    u8 upText_Y:4, cursorPal:4;
    u8 fillValue:4, cursorShadowPal:4;
    u8 lettersSpacing:3, itemVerticalPadding:3, scrollMultiple:2;
    u8 fontId:6, cursorKind:2;
};

/* BL at 0x09094A82 (was MathMin 0x090C1858): r0 = the 0x190640 cap, r1 = the award. */
u32 CM_ExpRateMin(u32 cap, u32 exp)
{
#ifndef CM_NO_EXPRATE
    static const u8 sHalves[5] TEXT = { 2, 3, 4, 6, 1 };
    u16 rate = VarGet(VAR_EXP_RATE);

    if (rate >= 1 && rate <= 4 && exp != 0) {
        exp = (exp > 0x190640 ? 0x190640 : exp) * sHalves[rate] >> 1;
        if (exp == 0)
            exp = 1;
    }
#endif
    return exp < cap ? exp : cap;
}

/* BL at 0x090BE1FC (the shared AppendToStartMenuItems call for EXIT / EXIT_RIGHT / EXIT_LEFT; r4 is the callee). */
void CM_StartMenuAppendExit(u8 action)
{
    if (action == STARTMENU_EXIT_LEFT)
        AppendToStartMenuItems(STARTMENU_EXPRATE);
    AppendToStartMenuItems(action);
}

/* Row 13's callback. The START handler began a fade to black before calling a row it does not know (Unbound
 * measured it still at level 0 here): stop it, put the unfaded palettes back, close the menu like Exit and run
 * `lockall; callnative CM_ExpRateOpen; waitstate; releaseall; end`. */
u8 CM_StartMenuExpRate(void)
{
    u32 i;
    u8 r;

    ResetPaletteFadeControl();
    for (i = 0; i < 0x400 / 4; i++)
        gPlttBufferFaded[i] = gPlttBufferUnfaded[i];
    r = StartMenuExitCallback();
    ScriptContext_SetupScript((const u8 *) EXPRATE_SCRIPT_ADDR);
    return r;
}

#define tRateList  data[0]
#define tRateWin   data[1]
#define tRateHead  data[2]
static const struct WindowTemplate sRateHeadWindow TEXT = { 0, 1, 1, 9, 2, 15, 1 };
static const struct WindowTemplate sRateListWindow TEXT = { 0, 1, 5, 9, 10, 15, 1 + 9 * 2 };
/* rows top to bottom: x0.5 x1 x1.5 x2 x3; the item id is the stored value */
static const struct ListMenuItem sRateItems[5] TEXT = {
    { (const u8 *) EXPRATE_ITEMS_ADDR + 0 * EXPRATE_ITEM_STRIDE, 4 },
    { (const u8 *) EXPRATE_ITEMS_ADDR + 1 * EXPRATE_ITEM_STRIDE, 0 },
    { (const u8 *) EXPRATE_ITEMS_ADDR + 2 * EXPRATE_ITEM_STRIDE, 1 },
    { (const u8 *) EXPRATE_ITEMS_ADDR + 3 * EXPRATE_ITEM_STRIDE, 2 },
    { (const u8 *) EXPRATE_ITEMS_ADDR + 4 * EXPRATE_ITEM_STRIDE, 3 },
};
static const u8 sRateRow[5] TEXT = { 1, 2, 3, 4, 0 };   /* stored value -> row */

static void ExpRate_HandleInput(u8 taskId)
{
    s32 r = ListMenu_ProcessInput(gTasks[taskId].tRateList);

    if (r == LIST_NOTHING_CHOSEN)
        return;
    if (r >= 0)
        VarSet(VAR_EXP_RATE, (u16) r);          /* A; B (LIST_CANCEL) keeps the rate */
    DestroyListMenuTask(gTasks[taskId].tRateList, 0, 0);
    ClearStdWindowAndFrame(gTasks[taskId].tRateWin, 1);
    RemoveWindow(gTasks[taskId].tRateWin);
    ClearStdWindowAndFrame(gTasks[taskId].tRateHead, 1);
    RemoveWindow(gTasks[taskId].tRateHead);
    DestroyTask(taskId);
    EnableBothScriptContexts();
}

/* callnative from the row's script. */
void CM_ExpRateOpen(void)
{
    struct ListMenuTemplate t;
    u16 rate = VarGet(VAR_EXP_RATE);
    u8 taskId, win, head;

    LoadStdWindowFrameGfx();
    head = AddWindow(&sRateHeadWindow);
    DrawStdWindowFrame(head, 0);
    FillWindowPixelBuffer(head, 0x11);
    AddTextPrinterParameterized(head, FONT_NORMAL, (const u8 *) EXPRATE_HEADER_ADDR, 0, 1, 0, 0);
    CopyWindowToVram(head, 3);
    win = AddWindow(&sRateListWindow);
    DrawStdWindowFrame(win, 0);
    taskId = CreateTask(ExpRate_HandleInput, 3);
    gTasks[taskId].tRateWin = win;
    gTasks[taskId].tRateHead = head;

    t.items = sRateItems;
    t.moveCursorFunc = ListMenuDefaultCursorMoveFunc;
    t.itemPrintFunc = 0;
    t.totalItems = 5;
    t.maxShowed = 5;
    t.windowId = win;
    t.header_X = 0;
    t.item_X = 8;
    t.cursor_X = 0;
    t.upText_Y = 1;
    t.cursorPal = 2;
    t.fillValue = 1;
    t.cursorShadowPal = 3;
    t.lettersSpacing = 1;
    t.itemVerticalPadding = 0;
    t.scrollMultiple = 0;
    t.fontId = FONT_NORMAL;
    t.cursorKind = 0;
    gTasks[taskId].tRateList = ListMenuInit(&t, 0, sRateRow[rate <= 4 ? rate : 0]);
    CopyWindowToVram(win, 3);
}
