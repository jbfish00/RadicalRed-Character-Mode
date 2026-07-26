/* Character Mode mugshot renderer for Pokemon Radical Red v4.1.
 *
 * Phase 3's missing half. 164 character front pics are already injected as an
 * additive blob region + pointer table (see tools/character_mode/
 * emit_sprite_table.py), but until now nothing on screen read them. This is the
 * render surface: two `callnative`-able functions that draw the selected
 * character's 64x64 mugshot beside the selection confirm message, then tear it
 * down again.
 *
 * Why a sprite we draw ourselves, rather than an engine table entry: RR's
 * trainer card and new-game intro do NOT render gTrainerFrontPicTable (the card
 * goes through RR's own customization system, the intro uses dedicated BG
 * tiles), so only real opponent battles draw that table. Repointing its slots
 * would swap a real opponent's art mid-playthrough. This path touches no engine
 * table at all -- it allocates OBJ tiles and a palette by tag, creates one
 * sprite, and frees all three again.
 *
 * Called from the selection script chain, which the injector emits as:
 *      setvar / setflag / givepokemon
 *      callnative CM_ShowCharacterMugshot
 *      loadword <msg>; callstd 6      <- blocks until the player presses A
 *      callnative CM_HideCharacterMugshot
 *      release; end
 *
 * Every fixed address below was verified byte-exact in THIS ROM (rom.sha1), not
 * merely copied from BPRE.ld -- see docs/ROUTINE_MAP.md's sprite-renderer entry
 * for the disassembly that pins each one:
 *   - gSprites 0x0202063C, stride 0x44, inUse at +0x3E bit 0, template at +0x14
 *     (read straight out of CreateSprite/CreateSpriteAt's own code)
 *   - LoadCompressedSpriteSheet/-SpritePalette's struct layouts, ditto
 *
 * Failure is always silent and safe: no character selected, no art staged for
 * that character, or no free OBJ palette slot -> the confirm message simply
 * appears without a mugshot, exactly as it did before this file existed.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;

#define FLAG_CHARACTER_MODE 0x18FE
#define VAR_CHARACTER_ID    0x51FD
#define NUM_CHARACTERS      210

/* Filled in at injection time (-DSPRITE_PTRS_ADDR=<CM_SPRITE_PTRS_ADDR>): a
 * NUM_CHARACTERS-entry table of {u32 gfx, u32 pal} absolute ROM pointers, in
 * character-index order, {0,0} for a character with no staged art. */
#ifndef SPRITE_PTRS_ADDR
#error "compile with -DSPRITE_PTRS_ADDR=0x08xxxxxx"
#endif

/* Our OBJ tile / palette tags. Arbitrary but deliberately far from the small
 * sequential values the engine's own templates use; they are live only for the
 * few seconds the confirm message is up, and both are freed in Hide(). */
#define CM_TILE_TAG    0xC0DE
#define CM_PALETTE_TAG 0xC0DF

/* 64x64 4bpp = 64 tiles = 2048 bytes uncompressed. LoadCompressedSpriteSheet
 * wants the DEcompressed size, not the stream length. */
#define MUGSHOT_GFX_SIZE 2048

/* Screen position of the sprite's CENTRE (CreateSprite applies the
 * centre-to-corner vector itself): top-right, clear of the message box, which
 * occupies roughly y >= 112. */
#define MUGSHOT_X 192
#define MUGSHOT_Y 48

/* Vanilla FRLG (CFRU BPRE.ld addresses, each re-verified in this ROM). */
#define FlagGet ((u8 (*)(u16))  0x0806E6D1)
#define VarGet  ((u16 (*)(u16)) 0x0806E569)
#define LoadCompressedSpriteSheet   ((u16 (*)(const void *)) 0x0800EBCD)
#define LoadCompressedSpritePalette ((u8  (*)(const void *)) 0x0800EC29)
#define CreateSprite  ((u8 (*)(const void *, s16, s16, u8)) 0x08006F8D)
#define DestroySprite ((void (*)(void *))                   0x08007281)
#define FreeSpriteTilesByTag   ((void (*)(u16)) 0x0800874D)
#define FreeSpritePaletteByTag ((void (*)(u16)) 0x08008A31)

#define gSprites            ((u8 *)   0x0202063C)
#define SPRITE_COUNT        64
#define SPRITE_STRIDE       0x44
#define SPRITE_OFF_TEMPLATE 0x14
#define SPRITE_OFF_INUSE    0x3E   /* bit 0 */

#define gDummySpriteAnimTable       ((const void *) 0x08231CF0)
#define gDummySpriteAffineAnimTable ((const void *) 0x08231CFC)
#define SpriteCallbackDummy         ((void (*)(void *)) 0x0800760D)

#define MAX_SPRITES_RETURN 64   /* CreateSprite's "no free slot" return */
#define PALETTE_ALLOC_FAIL 0xFF

struct CompressedSpriteSheet {
    const void *data;
    u16 size;      /* decompressed */
    u16 tag;
};

struct CompressedSpritePalette {
    const void *data;
    u16 tag;
};

struct SpriteTemplate {
    u16 tileTag;
    u16 paletteTag;
    const void *oam;
    const void *anims;
    const void *images;
    const void *affineAnims;
    void (*callback)(void *);
};

/* The injector extracts only .text, so every const below must live there or it
 * would be silently dropped and the template would read as garbage. */
#define IN_TEXT __attribute__((section(".text"), used, aligned(4)))

/* struct OamData, hand-encoded: attr0 = 0 (square, 4bpp, normal), attr1 =
 * 0xC000 (size 3 -> 64x64 with shape square), attr2 = 0 (priority 0; CreateSprite
 * fills tileNum and paletteNum from the tags). */
static const u32 sMugshotOam[2] IN_TEXT = { 0xC0000000, 0x00000000 };

static const struct SpriteTemplate sMugshotTemplate IN_TEXT = {
    CM_TILE_TAG,
    CM_PALETTE_TAG,
    sMugshotOam,
    gDummySpriteAnimTable,
    0,                              /* images: unused when tileTag != TAG_NONE */
    gDummySpriteAffineAnimTable,
    SpriteCallbackDummy,
};

void CM_HideCharacterMugshot(void);

void CM_ShowCharacterMugshot(void)
{
    struct CompressedSpriteSheet sheet;
    struct CompressedSpritePalette pal;
    const u32 *entry;
    u16 id;

    if (!FlagGet(FLAG_CHARACTER_MODE))
        return;

    id = VarGet(VAR_CHARACTER_ID);
    if (id < 1 || id > NUM_CHARACTERS)
        return;

    /* character index is 1-based in the var, 0-based in the table */
    entry = (const u32 *) SPRITE_PTRS_ADDR + (u32) (id - 1) * 2;
    if (entry[0] == 0 || entry[1] == 0)
        return;                     /* no front pic staged for this character */

    /* Never leave a previous mugshot's tags allocated: selecting twice in one
     * session would otherwise leak OBJ tiles until a screen transition. */
    CM_HideCharacterMugshot();

    pal.data = (const void *) entry[1];
    pal.tag = CM_PALETTE_TAG;
    if (LoadCompressedSpritePalette(&pal) == PALETTE_ALLOC_FAIL)
        return;                     /* all 16 OBJ palette slots in use */

    sheet.data = (const void *) entry[0];
    sheet.size = MUGSHOT_GFX_SIZE;
    sheet.tag = CM_TILE_TAG;
    LoadCompressedSpriteSheet(&sheet);

    if (CreateSprite(&sMugshotTemplate, MUGSHOT_X, MUGSHOT_Y, 0) == MAX_SPRITES_RETURN) {
        /* no free OAM slot -- don't strand the allocations */
        FreeSpriteTilesByTag(CM_TILE_TAG);
        FreeSpritePaletteByTag(CM_PALETTE_TAG);
    }
}

void CM_HideCharacterMugshot(void)
{
    u8 *s = gSprites;
    u32 i;

    /* Identify our own sprite by template pointer rather than by a remembered
     * id: that needs no new save-block var and no scratch RAM, and it stays
     * correct even if the sprite was never created. */
    for (i = 0; i < SPRITE_COUNT; i++, s += SPRITE_STRIDE) {
        if (!(s[SPRITE_OFF_INUSE] & 1))
            continue;
        if (*(const void **) (s + SPRITE_OFF_TEMPLATE) == (const void *) &sMugshotTemplate)
            DestroySprite(s);
    }

    FreeSpriteTilesByTag(CM_TILE_TAG);
    FreeSpritePaletteByTag(CM_PALETTE_TAG);
}
