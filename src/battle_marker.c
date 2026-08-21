/* Radical Red Character Mode -- wild-encounter marker shim.
 *
 * A SEPARATE COMPILE UNIT with its own link address, for the same reason the
 * wild-encounter override and the mugshot renderer are: character_mode.c's
 * entry must sit at exactly SHIM_ADDR (the injector asserts it), so anything
 * added ahead of it in that file would move the entry and break the build.
 * Linking this low in the ROM also puts it within Thumb-BL range of the
 * battle-message code at 0x080D77DE (2.63 MB), so the BL is retargeted
 * DIRECTLY here and no trampoline is needed at all.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FLAG_CHARACTER_MODE 0x18FE
#define VAR_CHARACTER_ID    0x51FD
#define MON_DATA_SPECIES    11

#ifndef NUM_CHARACTERS
#error "compile with -DNUM_CHARACTERS="
#endif
#ifndef NUM_SPECIES
#error "compile with -DNUM_SPECIES="
#endif
#ifndef BITMAP_STRIDE
#error "compile with -DBITMAP_STRIDE="
#endif
#ifndef BITMAPS_ADDR
#error "compile with -DBITMAPS_ADDR=0x08xxxxxx"
#endif

#define FlagGet    ((u8  (*)(u16))                 0x0806E6D1)
#define VarGet     ((u16 (*)(u16))                 0x0806E569)
#define GetMonData ((u32 (*)(void *, int, void *)) 0x0803FBE9)

/* --- wild-encounter marker (../../game_plans/rowe_parity.md §3) ---
 *
 *     Wild GIBLE appeared,
 *     destined for CYNTHIA!
 *
 * WHY. The 10%% roster override hands out a family ROOT, which is
 * indistinguishable from something the map's own table could have produced.
 * ROWE measured the consequence -- the median selectable character matches
 * ~2%% of the game's own wild slots, so the override does nearly all the work
 * of building a team, invisibly -- and Platinum proved the failure mode is
 * real: a playthrough reported as "no on-roster encounters" had no bug at all,
 * and naming the character was the fix. Rates are untouched; this is a message.
 *
 * HOW. BufferStringBattle picks an intro string into r7, moves it to r0 at
 * 0x080D77DC and calls a small wrapper. THAT call, the BL at 0x080D77DE, is
 * what we retarget; the shim adjusts r0 and tail-calls the wrapper. Every
 * other battle message passes through untouched because we substitute only
 * when r0 is one of the two wild-intro pointers.
 *
 * ⚠️ TWO STRINGS, BOTH MATCHED, same as the Emerald ports: this ROM holds
 * "Wild {FD}{06} appeared!{FB}" at 0x083FD284 and again at 0x083FD297, reached
 * from different arms of the compiled switch, and which is the plain intro and
 * which the legendary variant cannot be told apart statically. They are the
 * same sentence and the marker only fires when the mon really is on the
 * roster, so matching both cannot make either say something false.
 *
 * ⚠️ Deviations from ROWE, forced by this being a binary hack: the strings are
 * STATIC, one per character, emitted into ROM (there is no RAM to build one
 * in), and the test is "is the wild mon on the roster" rather than "did the
 * override fire" (no RAM to remember that either). Double battles are left
 * unmarked -- two opponents, only one of which could be the roster mon. */
#ifndef MARKER_ADDR
#error "compile with -DMARKER_ADDR= (marker_strings.bin injection address)"
#endif
#define MARKER_STRIDE 64
#define TEXT_WILD_APPEARED_A ((const u8 *) 0x083FD284)
#define TEXT_WILD_APPEARED_B ((const u8 *) 0x083FD297)
/* The wrapper the intro tail calls; it loads gDisplayedStringBattle and calls
   the real expander. */
#define OrigExpandString ((void (*)(const u8 *)) 0x080D77F5)
/* gEnemyParty. DERIVED, not guessed: this repo's confirmed
   gPlayerParty = 0x02024284 and the vanilla FireRed layout puts the six-slot
   enemy party immediately before it -- 0x02024284 - 6*100 = 0x0202402C, which
   is exactly pokefirered's gEnemyParty. The arithmetic closing on the known
   symbol is the check. */
#define gEnemyParty ((void *) 0x0202402C)

void CM_BattleStringGated(const u8 *src)
{
    if ((src == TEXT_WILD_APPEARED_A || src == TEXT_WILD_APPEARED_B)
        && FlagGet(FLAG_CHARACTER_MODE)) {
        u16 id = VarGet(VAR_CHARACTER_ID);

        if (id >= 1 && id <= NUM_CHARACTERS) {
            u32 species = GetMonData(gEnemyParty, MON_DATA_SPECIES, 0);

            if (species > 0 && species < NUM_SPECIES) {
                const u8 *bm = (const u8 *) BITMAPS_ADDR
                               + (id - 1) * BITMAP_STRIDE;

                if (bm[species >> 3] & (1 << (species & 7)))
                    src = (const u8 *) (MARKER_ADDR
                                        + (u32) (id - 1) * MARKER_STRIDE);
            }
        }
    }
    OrigExpandString(src);
}

