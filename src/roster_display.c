/* Character Mode in-game roster display for Pokemon Radical Red (CFRU, FireRed).
 *
 * ../../game_plans/roster_display.md is the runbook: a read-only list of the
 * ACTIVE character's roster, one row per family ROOT, name + bordered icon.
 *
 * Seaglass and Lazarus draw it with pokeemerald-expansion's dynamic
 * multichoice plus a callback set. FireRed has neither, so this is ROWE's
 * design instead (Pokemon Rowe Alteration src/character_roster_menu.c): a
 * native task owning a header window, a ListMenu window and ONE icon sprite
 * that follows the cursor inside its own framed box. Every engine call is a
 * vanilla FireRed function at its BPRE.ld address (CFRU keeps FireRed's code
 * where it does not hook it); the two tables CFRU relocates -- species names
 * and mon icons -- are reached through CFRU's own redirect slots, never a
 * stock address.
 *
 * Invocation: the bedroom console's pre-entry script runs
 *     closemessage; callnative CM_RosterOpen; waitstate; release; end
 * and the task calls EnableBothScriptContexts() when the list closes, which is
 * what lets the waitstate resume.
 *
 * ⚠️ RR's injector keeps ONLY .text (objcopy --only-section=.text), so every
 * constant here is forced into .text and there are no string literals.
 * ⚠️ No mutable statics: all per-open state lives in the input task's data[].
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;
typedef volatile unsigned short vu16;

#define TEXT __attribute__((section(".text")))

#ifndef NUM_CHARACTERS
#error "compile with -DNUM_CHARACTERS=<from characters_manifest.json>"
#endif
#ifndef ROSTER_ROOTS_ADDR
#error "compile with -DROSTER_ROOTS_ADDR=0x08xxxxxx"
#endif
#ifndef ROSTER_ROOTS_OFF
#error "compile with -DROSTER_ROOTS_OFF=<roots_offset_bytes from the manifest>"
#endif
#ifndef ROSTER_NAMES_ADDR
#error "compile with -DROSTER_NAMES_ADDR=0x08xxxxxx"
#endif
#ifndef ROSTER_NAME_STRIDE
#error "compile with -DROSTER_NAME_STRIDE=<bytes per character name>"
#endif

#define VAR_CHARACTER_ID 0x51FD
#define EOS 0xFF

/* --- CFRU redirect slots (include/new/rom_locs.h) --- */
#define gSpeciesNames ((const u8 *) *(const u32 *) 0x08000144)   /* 11 B per species */
#define SPECIES_NAME_STRIDE 11

/* --- vanilla FireRed, BPRE.ld --- */
#define GetVarPointer        ((u16 *(*)(u16)) 0x0806E455)
#define AddWindow            ((u8 (*)(const void *)) 0x08003CE5)
#define RemoveWindow         ((void (*)(u8)) 0x08003E3D)
#define DrawStdWindowFrame   ((void (*)(u8, u8)) 0x080F6F1D)
#define ClearStdWindowAndFrame ((void (*)(u8, u8)) 0x080F6F9D)
#define FillWindowPixelBuffer ((void (*)(u8, u8)) 0x0800445D)
#define CopyWindowToVram     ((void (*)(u8, u8)) 0x08003F21)
#define AddTextPrinterParameterized ((u16 (*)(u8, u8, const u8 *, u8, u8, u8, void *)) 0x08002C49)
#define LoadStdWindowFrameGfx ((void (*)(void)) 0x080F6E9D)
#define ListMenuInit         ((u8 (*)(const void *, u16, u16)) 0x08106FF9)
#define ListMenu_ProcessInput ((s32 (*)(u8)) 0x08107079)
#define DestroyListMenuTask  ((void (*)(u8, u16 *, u16 *)) 0x0810713D)
#define CreateTask           ((u8 (*)(void (*)(u8), u8)) 0x0807741D)
#define DestroyTask          ((void (*)(u8)) 0x08077509)
#define FindTaskIdByFunc     ((u8 (*)(void (*)(u8))) 0x08077689)
#define Malloc               ((void *(*)(u32)) 0x08002B9D)
#define Free                 ((void (*)(void *)) 0x08002BC5)
#define PlaySE               ((void (*)(u16)) 0x080722CD)
#define EnableBothScriptContexts ((void (*)(void)) 0x08069B35)
#define CreateMonIcon        ((u8 (*)(u16, void *, s16, s16, u8, u32, u32)) 0x08096E19)
#define DestroyMonIcon       ((void (*)(void *)) 0x08097071)
#define LoadMonIconPalette   ((void (*)(u16)) 0x080970E1)
#define FreeMonIconPalette   ((void (*)(u16)) 0x08097169)
#define UpdateMonIconFrame   ((void *) 0x08097229)   /* FireRed's SpriteCB_MonIcon body */

#define gTasks   ((struct Task *) 0x03005090)
#define gMainNewKeys (*(vu16 *) (0x030030F0 + 0x2E))
#define gSprites ((u8 *) 0x0202063C)
#define SPRITE_STRIDE 0x44
#define MAX_SPRITES 64
#define TASK_NONE 0xFF
#define NO_WINDOW 0xFF
#define A_BUTTON 0x0001
#define B_BUTTON 0x0002
#define SE_SELECT 5
#define LIST_NOTHING_CHOSEN (-1)
#define FONT_NORMAL 2

struct Task {
    void (*func)(u8);
    u8 isActive, prev, next, priority;
    s16 data[16];
};

struct WindowTemplate {
    u8 bg, tilemapLeft, tilemapTop, width, height, paletteNum;
    u16 baseBlock;
};

struct ListMenuItem {
    const u8 *name;
    s32 id;
};

struct ListMenuTemplate {
    const struct ListMenuItem *items;
    void (*moveCursorFunc)(s32, u8, void *);
    void (*itemPrintFunc)(u8, s32, u8);
    u16 totalItems;
    u16 maxShowed;
    u8 windowId, header_X, item_X, cursor_X;
    u8 upText_Y:4, cursorPal:4;
    u8 fillValue:4, cursorShadowPal:4;
    u8 lettersSpacing:3, itemVerticalPadding:3, scrollMultiple:2;
    u8 fontId:6, cursorKind:2;
};

/* Geometry: ROWE's, with a wider header (RR names reach 12 characters). */
#define MENU_WIDTH    13
#define MENU_ROWS      6
#define HEADER_WIDTH  18
#define ICON_WIN_LEFT 19
#define ICON_WIN_TOP   8
#define ICON_WIN_SIZE  5
/* 80, not the box's centre 84: icon art is bottom-weighted in its 32x32 frame
 * (ROWE measured it off the rendered screen). */
#define ICON_X 172
#define ICON_Y  80

#define tListTaskId  data[0]
#define tWindowId    data[1]
#define tHeaderId    data[2]
#define tIconSprite  data[3]
#define tItemsHi     data[4]
#define tItemsLo     data[5]
#define tIconWinId   data[6]
#define tIconSpecies data[7]

static const struct WindowTemplate sMenuWindow TEXT = {
    0, 1, 5, MENU_WIDTH, 2 * MENU_ROWS, 15, 1 };
static const struct WindowTemplate sHeaderWindow TEXT = {
    0, 1, 1, HEADER_WIDTH, 2, 15, 1 + MENU_WIDTH * 2 * MENU_ROWS };
static const struct WindowTemplate sIconWindow TEXT = {
    0, ICON_WIN_LEFT, ICON_WIN_TOP, ICON_WIN_SIZE, ICON_WIN_SIZE, 15,
    1 + MENU_WIDTH * 2 * MENU_ROWS + HEADER_WIDTH * 2 };

/* "'s roster" in the game charmap: ' s space r o s t e r */
static const u8 sText_Suffix[] TEXT = { 0xB4, 0xE7, 0x00, 0xE6, 0xE3, 0xE7, 0xE8, 0xD9, 0xE6, EOS };

static void RosterMenu_HandleInput(u8 taskId);

static struct ListMenuItem *GetItems(u8 taskId)
{
    return (struct ListMenuItem *) (((u32) (u16) gTasks[taskId].tItemsHi << 16)
                                    | (u16) gTasks[taskId].tItemsLo);
}

static void DestroyIcon(u8 taskId)
{
    if (gTasks[taskId].tIconSprite != MAX_SPRITES) {
        DestroyMonIcon(gSprites + gTasks[taskId].tIconSprite * SPRITE_STRIDE);
        FreeMonIconPalette((u16) gTasks[taskId].tIconSpecies);
        gTasks[taskId].tIconSprite = MAX_SPRITES;
    }
}

/* ⚠️ THE FIRST PARAMETER IS THE ITEM'S ID, NOT ITS INDEX (ROWE's trap: indexing
 * items[] with it drew Scyther for Pikachu). The id IS the species here. */
static void RosterMenu_MoveCursor(s32 itemId, u8 onInit, void *list)
{
    u8 taskId = FindTaskIdByFunc(RosterMenu_HandleInput);
    u16 species = (u16) itemId;
    u8 id;
    (void) list;

    if (taskId == TASK_NONE || itemId <= 0)
        return;
    if (!onInit)
        PlaySE(SE_SELECT);
    DestroyIcon(taskId);
    /* One palette for the one icon: the field holds most sprite palette slots. */
    LoadMonIconPalette(species);
    id = CreateMonIcon(species, UpdateMonIconFrame, ICON_X, ICON_Y, 0, 0, 0);
    if (id >= MAX_SPRITES) {
        FreeMonIconPalette(species);
        return;
    }
    gSprites[id * SPRITE_STRIDE + 5] &= ~0x0C;   /* oam.priority = 0: above the window */
    gTasks[taskId].tIconSprite = id;
    gTasks[taskId].tIconSpecies = species;
}

static void DrawHeader(u8 windowId, u16 charId)
{
    const u8 *name = (const u8 *) ROSTER_NAMES_ADDR + (u32) (charId - 1) * ROSTER_NAME_STRIDE;
    u8 buf[ROSTER_NAME_STRIDE + sizeof(sText_Suffix)];
    u32 n = 0, k;

    while (n < ROSTER_NAME_STRIDE - 1 && name[n] != EOS) {
        buf[n] = name[n];
        n++;
    }
    for (k = 0; k < sizeof(sText_Suffix); k++)
        buf[n + k] = sText_Suffix[k];
    FillWindowPixelBuffer(windowId, 0x11);
    AddTextPrinterParameterized(windowId, FONT_NORMAL, buf, 0, 1, 0, 0);
    CopyWindowToVram(windowId, 3);
}

/* callnative. Always resumes the script: an out-of-range character or a
 * failed allocation re-enables the contexts immediately instead of wedging
 * the waitstate. */
void CM_RosterOpen(void)
{
    u16 charId = *GetVarPointer(VAR_CHARACTER_ID);
    const u16 *entry, *roots;
    struct ListMenuItem *items;
    struct ListMenuTemplate t;
    u8 windowId, headerId, iconWinId, taskId;
    u32 i, count;

    if (charId < 1 || charId > NUM_CHARACTERS) {
        EnableBothScriptContexts();
        return;
    }
    entry = (const u16 *) ROSTER_ROOTS_ADDR + (u32) (charId - 1) * 2;
    roots = (const u16 *) (ROSTER_ROOTS_ADDR + ROSTER_ROOTS_OFF) + entry[0];
    count = entry[1];
    items = count ? Malloc(count * sizeof(struct ListMenuItem)) : 0;
    if (items == 0) {                 /* no rows, or no memory: nothing to draw */
        EnableBothScriptContexts();
        return;
    }
    for (i = 0; i < count; i++) {
        /* Point straight into the name table: fixed width, 0xFF-terminated. */
        items[i].name = gSpeciesNames + (u32) roots[i] * SPECIES_NAME_STRIDE;
        items[i].id = roots[i];
    }

    LoadStdWindowFrameGfx();
    headerId = AddWindow(&sHeaderWindow);
    DrawStdWindowFrame(headerId, 0);
    DrawHeader(headerId, charId);
    windowId = AddWindow(&sMenuWindow);
    DrawStdWindowFrame(windowId, 0);
    iconWinId = AddWindow(&sIconWindow);
    DrawStdWindowFrame(iconWinId, 0);
    FillWindowPixelBuffer(iconWinId, 0x11);
    CopyWindowToVram(iconWinId, 3);

    /* The task exists BEFORE ListMenuInit: its first moveCursor call (onInit)
     * needs somewhere to keep the sprite id. */
    taskId = CreateTask(RosterMenu_HandleInput, 3);
    gTasks[taskId].tListTaskId = TASK_NONE;
    gTasks[taskId].tWindowId = windowId;
    gTasks[taskId].tHeaderId = headerId;
    gTasks[taskId].tIconSprite = MAX_SPRITES;
    gTasks[taskId].tIconWinId = iconWinId;
    gTasks[taskId].tItemsHi = (s16) ((u32) items >> 16);
    gTasks[taskId].tItemsLo = (s16) ((u32) items & 0xFFFF);

    t.items = items;
    t.moveCursorFunc = RosterMenu_MoveCursor;
    t.itemPrintFunc = 0;
    t.totalItems = count;
    t.maxShowed = count < MENU_ROWS ? count : MENU_ROWS;
    t.windowId = windowId;
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
    gTasks[taskId].tListTaskId = ListMenuInit(&t, 0, 0);
    CopyWindowToVram(windowId, 3);
}

static void RosterMenu_Destroy(u8 taskId)
{
    struct ListMenuItem *items = GetItems(taskId);

    DestroyListMenuTask(gTasks[taskId].tListTaskId, 0, 0);
    DestroyIcon(taskId);
    Free(items);
    ClearStdWindowAndFrame(gTasks[taskId].tWindowId, 1);
    RemoveWindow(gTasks[taskId].tWindowId);
    ClearStdWindowAndFrame(gTasks[taskId].tHeaderId, 1);
    RemoveWindow(gTasks[taskId].tHeaderId);
    ClearStdWindowAndFrame(gTasks[taskId].tIconWinId, 1);
    RemoveWindow(gTasks[taskId].tIconWinId);
    DestroyTask(taskId);
    EnableBothScriptContexts();
}

/* Read-only: A and B both close it (ROWE's rule). */
static void RosterMenu_HandleInput(u8 taskId)
{
    if (ListMenu_ProcessInput(gTasks[taskId].tListTaskId) != LIST_NOTHING_CHOSEN
        || (gMainNewKeys & B_BUTTON))
        RosterMenu_Destroy(taskId);
}
