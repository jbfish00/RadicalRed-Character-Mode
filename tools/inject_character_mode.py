#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Radical Red v4.1.

Pipeline (all addresses CONFIRMED in docs/ROUTINE_MAP.md, pinned to rom.sha1):
  1. Compile src/character_mode.c (the GiveMonToPlayer gate shim) with
     arm-none-eabi-gcc, linked at SHIM_ADDR.
  2. Splice into a ROM copy:
       overworld sheets     @ OW_PLAYER_ADDR (0x08B72000, below the shim;
                              rr_ow_player.py, 2026-10-02)
       shim code            @ SHIM_ADDR    (0x08C80000)
       rosters_expanded.bin @ BITMAPS_ADDR (0x08C80400)
       selection script ext @ SCRIPT_ADDR  (0x08C90000)
     — all inside the tail of the confirmed 1.63 MiB free block at
     0xB71D04. The shim MUST stay in [0xC7DD88, 0xD004D7): Thumb BL range
     is ±4 MB from the two patch sites (~0x0907xxxx), and this block's
     tail is the only big free run inside that window.
  3. Patch:
       - BL at 0x107DD84 (atkF0_givecaughtmon)  -> BL shim
       - BL at 0x10777CE (ScriptGiveMon)        -> BL shim
       - goto operand at 0x10500EF (cheat-code no-match fallthrough)
         -> selection script chain (chain's own fallthrough continues to
            the original "Invalid code." handler at 0x09050811)
  4. Verify expected original bytes before every patch (refuses to run on a
     mismatched ROM), write build/radicalred_cm.gba + build/radicalred_cm.bps.

The selection UI rides RR's own cheat-code entry system: the player talks
to the cheat-code NPC and types a character's name (non-alphanumerics
stripped: "Lt. Surge" -> "LtSurge"). Matching sets VAR_CHARACTER_ID +
FLAG_CHARACTER_MODE and delivers the character's signature mon at Lv 5.
Debug codes (mirroring ROWE's in-game debug-menu test method):
  CMDbgOff    - turn Character Mode off
  CMDbgGive1  - givepokemon Pikachu Lv5  (allowed for Red -> stays in party)
  CMDbgGive2  - gives a DERIVED off-roster species Lv5 (-> sent to PC).
                Derived from character 0's own bitmap at build time, never
                hardcoded: the previous literal (Meowth) became on-roster
                when the roster grew and the test quietly stopped testing.
"""
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
ROM_IN = ROOT / "rom" / "radicalred 4.1.gba"
ROM_SHA1 = "964f951a0fdaf209e4ea1344883ef0d557bb3a80"
BUILD = ROOT / "build"

def _resolve_charmap():
    """Path to this repo's vendored game-text charmap (tools/charmap.txt).

    This was a hardcoded absolute path into the unrelated "Pokemon Rowe
    Alteration" working tree, which made this repo unbuildable and
    unverifiable from a fresh clone. The charmap is now vendored here
    (byte-identical, md5 b31d142ca98103d64d707f9894fa42e3). Resolution is
    anchored to this file's own location, never the cwd.

    Override with the CM_CHARMAP environment variable.
    """
    import os
    from pathlib import Path
    override = os.environ.get("CM_CHARMAP")
    if override:
        p = Path(override)
        if not p.is_file():
            raise SystemExit("CM_CHARMAP=%s is not a file" % override)
        return p
    # Walk up to the REPO ROOT only. An unbounded walk would keep climbing past
    # the repo into ~ and could silently pick up an unrelated tools/charmap.txt
    # -- reading the wrong charmap presents as "this game encodes text
    # differently", not as a missing file. Bound it at the .git directory.
    for parent in Path(__file__).resolve().parents:
        cand = parent / "tools" / "charmap.txt"
        if cand.is_file():
            return cand
        if (parent / ".git").exists():
            break
    raise SystemExit(
        "charmap.txt not found. Expected it vendored at <repo>/tools/charmap.txt; "
        "set CM_CHARMAP to override.")

CHARMAP = _resolve_charmap()

# --- confirmed layout constants (docs/ROUTINE_MAP.md) ---
# All three payloads live in the confirmed 1.63 MiB free block
# (0xB71D04-0xD004D7), placed in its upper region because the shim must be
# within Thumb BL range (+/-4 MB) of both patch sites (~0x0907xxxx): the
# reachable window is [0xC7DD88, 0x14777D0), and this block's tail
# [0xC7DD88, 0xD004D7) is comfortably the largest free run inside it.
SHIM_ADDR    = 0x08C80000
# 2026-09-02: 0x100 -> 0x400. The shim outgrew its 256-byte slot when the
# activation party sweep was added (336 -> 664 bytes). The bitmaps are
# 238*172 = 40,936 B and still end well below TRADE_WRAPPER_ADDR.
BITMAPS_ADDR = 0x08C80400
SCRIPT_ADDR  = 0x08C90000  # moved from 0x08C88000 (2026-07-23): 199-char bitmaps (34,228 B) overflow the old 0x08C80100..0x08C88000 window; script chain is goto-retargeted by absolute pointer, no BL-reach constraint
FREE_BLOCK_END = 0xD004D7  # end of the 1.63MiB free run

BL_SITE_CATCH = 0x107DD84   # inside atkF0_givecaughtmon
BL_SITE_GIFT  = 0x10777CE   # inside ScriptGiveMon
GIVEMON_ADDR  = 0x0907D790  # current BL target at both sites (no Thumb bit)

GOTO_OPERAND_OFF = 0x10500EF          # operand of `goto 0x09050811`
INVALID_CODE_HANDLER = 0x09050811

# The ONLY live in-game trade in RR v4.1 (docs/ROUTINE_MAP.md): a BG-event
# console on map 2.11 at tile (0,2) trading the player's Florges (779) for
# Eternal Flower Floette (848). Script pointer lives in the BG event struct;
# wrapper gates it on the character's allowed-species bitmap.
TRADE_BG_SCRIPT_PTR_OFF = 0x3B432C    # BG event struct +8 (script field)
TRADE_ORIG_SCRIPT = 0x08164B03        # lockall; setvar 0x8004,6; ... trade scene
TRADE_GIVEN_SPECIES = 848             # what the player RECEIVES (the gated side)
TRADE_WRAPPER_ADDR = 0x08C8E000

# --- egg-hatch sweep (../game_plans/rowe_parity.md §13.16/§13.18) ---
# The injected tail for the hatch script, 11 bytes. Placed between the trade
# wrapper (which ends by 0x08C8E0C0) and SCRIPT_ADDR; verified 0xFF-free in
# both the base and the built ROM before it was chosen. tools/character_mode/
# egg_hook.py carries the RE and the byte grammar.
EGG_TAIL_ADDR = 0x08C8F000

# --- PC-exit sweep (../game_plans/rowe_parity.md §13.24/§13.26c) ---
# The injected tail for the PC access script, 19 bytes, on the page after the
# egg tail. tools/character_mode/pc_hook.py carries the RE and the grammar.
PC_TAIL_ADDR = 0x08C8F100

# Wild-encounter override (docs/ROUTINE_MAP.md, "CONFIRMED -- wild-encounter
# override hook sites"): the four BL sites calling CreateWildMon
# (0x090C292C, no Thumb bit) from a genuine random-table roll -- primary +
# double-battle calls inside TryGenerateWildMon (land/cave, surfing, rock
# smash/headbutt all share these) and inside FishingWildEncounter (every
# fishing rod tier). Swarms/ghost-battle/raid-scripted/DexNav call
# CreateWildMon too but were verified NOT to be table rolls and are left
# untouched -- see src/wild_encounter_mode.c's header comment.
WILD_SHIM_ADDR    = 0x08CE0000

# --- encounter marker (../game_plans/rowe_parity.md §3) ---
# Low in the ROM ON PURPOSE. The battle-message code is at 0x080D77DE, ~11.9 MB
# from SHIM_ADDR -- far outside the +-4 MB Thumb BL window -- so a marker shim
# placed with the others would need a trampoline. Linked here it is 2.63 MB
# away and the BL is retargeted DIRECTLY at it, no trampoline at all.
# 84,224 bytes verified 0xFF from 0x08378CA8; nothing else in tools/ references
# this region.
MARKER_SHIM_ADDR  = 0x08378CA8
MARKER_ADDR       = 0x08379000     # 238*64 = 15,232 B -> ends 0x0837CC00
MARKER_STRIDE     = 64
# ldr r0,=<string>; b 0x080D77DC ... 0x080D77DC: adds r0,r7,#0 ; bl wrapper
MARKER_BL_SITE    = 0x0D77DE
MARKER_WRAPPER    = 0x080D77F4
# Two byte-identical copies of "Wild {FD}{06} appeared!{FB}"; the shim matches
# both (src/battle_marker.c explains why picking one was not safe).
TEXT_WILD_APPEARED = (0x083FD284, 0x083FD297)
WILD_OFFSETS_ADDR = 0x08CE0800  # shim compiles to ~1KB (needs __aeabi_uidivmod)
WILD_DATA_ADDR    = 0x08CE0C00
# The 1% legendary tables (2026-07-26). They CANNOT share WILD_OFFSETS_ADDR's
# window: that is 952 of 1,024 B used, i.e. 18 more characters from colliding
# with WILD_DATA_ADDR. The spec suggested 0x08CE8200, immediately after
# wild_override.bin -- but measured, that leaves only 250 B of growth room for a
# table that grows with every roster change, so they go further along the same
# verified-0xFF run instead, giving wild_override.bin ~8 KB of headroom. The
# assertions in main() are what actually enforce both gaps.
WILD_LEG_OFFSETS_ADDR = 0x08CEA000
WILD_LEG_DATA_ADDR    = 0x08CEA400

# --- Phase 3 character sprites (2026-07-25) ---
# The 0x08B71D04 block that holds everything above has only ~65 KB left below
# 0x08D00000, and the sprite blobs are ~147 KB. These live in the separate
# 713 KB 0xFF run at 0x08951E14 instead, which nothing else in this project
# touches. Verified free by the 0xFF precondition check in splice().
CM_SPRITE_PTRS_ADDR  = 0x08952000   # NUM_CHARACTERS x {u32 gfx, u32 pal}
CM_SPRITE_BLOBS_ADDR = 0x08952800   # LZ77 gfx+palette streams, concatenated
# The mugshot renderer (src/character_sprite.c). Sits past the ~147 KB of art in
# the same 713 KB 0xFF run; the 0xFF precondition in splice() is what actually
# proves it clear. No BL-reach constraint applies -- every engine call it makes
# goes through a function pointer (ldr/blx), and the script reaches it by an
# absolute `callnative` operand, not a relative branch.
CM_SPRITE_SHIM_ADDR  = 0x08980000
CREATEWILDMON_ADDR = 0x090C292C  # no Thumb bit, current BL target at all 4 sites

# ROWE's second guard in the PC (src/character_mode.c CM_PSSLastMonGuard;
# docs/ROUTINE_MAP.md "PC second guard"; rowe_parity.md §13.53). FireRed keeps
# IsRemovingLastPartyMon as a real function, so exactly two calls to
# CountPartyAliveNonEggMonsExcept (anchor: special 0x85's wrapper calls it) are
# retargeted: its own and CanShiftMon's. Both go through one 8-byte trampoline
# written over CheckHeap, a debug routine vanilla FireRed defines and never
# calls: in this ROM it is byte-identical to vanilla with no BL callers, no
# pointer to its entry and no short branch into it (verify_artifacts re-checks
# all three on the base ROM). 0.6 MB from the sites. ⚠️ NOT a "0xFF run": those
# turned out to be sprite pixels in the Emerald ports.
PSS_COUNT_ALIVE_EXCEPT = 0x0808C184
PSS_GUARD_BL_SITES     = (0x09391A,)        # IsRemovingLastPartyMon: bl Count
PSS_CANSHIFT_BL        = 0x093956           # CanShiftMon: bl Count
PSS_CANSHIFT_TAIL      = 0x09395A           # lsls r0,#24 ; cmp r0,#0 -> b <epilogue 0x0809399A> ; nop
PSS_GUARD_TRAMPOLINE_ADDR = 0x08002BEC      # CheckHeap (unused debug routine)
PC_GUARD_ADDR          = 0x08CFC000         # src/pc_guard.c: its own unit (the main shim is capped at 1 KB)
PSS_DEAD_FN_HEAD       = bytes.fromhex("30b508480468051c")
# Link-trade sweep (src/pc_guard.c CM_LinkTradeSweepThenExpand; rowe_parity.md
# §13.53, the user's "sweep after the trade" choice, 2026-09-30). The one BL to
# StringExpandPlaceholders in CB2_SaveAndEndTrade (0x08053E8C), shared by state
# 0 "Communication standby" and state 2 "Saving", both before LinkFullSave_Init.
# Its trampoline is the second 8 bytes of CheckHeap (still inside the dead
# routine, which ends at 0x08002C1B).
LINK_TRADE_BL_SITE        = 0x0540EC
STRING_EXPAND_PLACEHOLDERS = 0x08008FCC
LINK_TRADE_TRAMPOLINE_ADDR = PSS_GUARD_TRAMPOLINE_ADDR + 8
LINK_TRADE_DEAD_BYTES      = bytes.fromhex("2868211c1031fff7")  # CheckHeap +8..+15
# Field moves (src/field_moves.c; ../game_plans/field_moves.md): with CM on,
# an HM in the bag + its badge lets any party mon use the field move. Two BLs:
# CFRU's PartyHasMonWithFieldMovePotential -> CanMonLearnTMTutor (direct), and
# ScrCmd_checkpartymove -> MonKnowsMove (through a third CheckHeap trampoline).
FIELD_MOVES_ADDR          = 0x08CFD000         # its own unit, after pc_guard.c
# 100% catch for on-roster species (src/sure_catch.c; 2026-10-09). Its own unit
# after field_moves.c, in BL reach of the hook (0x37F552 from 0x0907D552).
SURE_CATCH_ADDR  = 0x08CFE000
# Early party-wide Exp. Share (src/exp_share.c; 2026-10-09). Its own unit.
EXP_SHARE_ADDR   = 0x08CFE800
CATCH_ODDS_SITE  = 0x107D552          # atkEF_handleballthrow: cmp r4,#254 ; bls 0x0907D590
CATCH_ODDS_ORIG  = bytes.fromhex("fe2c1cd9")
FIELD_CANLEARN_BL_SITE    = 0x10B25BC          # in 0x090B2540
CAN_MON_LEARN_TM_TUTOR    = 0x090A5908
FIELD_KNOWS_BL_SITE       = 0x06C0D0           # in ScrCmd_checkpartymove 0x0806C0A8
MON_KNOWS_MOVE            = 0x08125AC0
FIELD_KNOWS_TRAMPOLINE_ADDR = PSS_GUARD_TRAMPOLINE_ADDR + 16
FIELD_KNOWS_DEAD_BYTES    = bytes.fromhex("95ff002808d0e468")  # CheckHeap +16..+23
BL_SITE_LAND_MAIN   = 0x10C2FDA  # inside TryGenerateWildMon (primary)
BL_SITE_LAND_DOUBLE = 0x10C30CE  # inside TryGenerateWildMon (double battle)
BL_SITE_FISH_MAIN   = 0x10C3A94  # inside FishingWildEncounter (primary)
BL_SITE_FISH_DOUBLE = 0x10C3AD0  # inside FishingWildEncounter (double battle)

FLAG_CHARACTER_MODE = 0x18FE

# --- in-game roster display (../game_plans/roster_display.md), 2026-09-27 ---
# FireRed has no dynamic multichoice, so this is ROWE's design (a native task +
# ListMenu + one icon sprite), not the Seaglass/Lazarus callback set. All four
# regions sit in the unused tail of the 1.63 MiB free run (last used byte was
# 0x08CEAA08); splice() proves each clear and non-overlapping.
# ⚠️ 0x08CF0000..0x08CF3FFF is NOT free: the test-ROM builders write their
# scripts there (build_egg_testrom 0x08CF0000, build_pc_testrom 0x08CF1000,
# build_eggbattle_testrom 0x08CF2000). The first layout sat on all three and
# only the egg e2e noticed -- the same trap as Seaglass's 0x08F10000. Asserted
# below against TEST_SCRIPT_SQUAT.
TEST_SCRIPT_SQUAT = (0x08CF0000, 0x08CF4000)
ROSTER_ROOTS_ADDR  = 0x08CF4000   # emit_roster_roots.py blob
ROSTER_NAMES_ADDR  = 0x08CF6000   # NUM_CHARACTERS x 16 B display names (header)
ROSTER_NAME_STRIDE = 16           # longest display name is 12 chars + 0xFF
ROSTER_MENU_ADDR   = 0x08CF8000   # src/roster_display.c
ROSTER_SCRIPT_ADDR = 0x08CFA000   # the console pre-entry + its prompt
# The bedroom console (map 4.1, BG event #0 at (6,5)): the ONLY reference to
# its script in the whole ROM (scanned; asserted below).
CONSOLE_BG_PTR_OFF = 0x721C88
CONSOLE_SCRIPT     = 0x0905006F
VAR_CHARACTER_ID    = 0x51FD
# Overworld sprite (2026-10-02): a character whose costume Radical Red itself
# ships in the bedroom wardrobe gets that costume on activation -- RR's own
# setvar run, read from the base ROM by tools/character_mode/rr_costumes.py, then
# the same bedroom reload RR's wardrobe does (warpmuted 4,1), but to the
# player's OWN tile (warp 0xFF + getplayerxy into 0x8004/0x8005; RR's warpmuted
# VarGets both coordinates) so they stay at the console. Map 4.1 is the only
# place activation runs: the console BG event is the chain's only entry.
BEDROOM_MAP = (4, 1)
# Walk/run sprites for every other character with a player-grade sheet
# (tools/character_mode/rr_ow_player.py): RR's overworld table slot 3, the
# palette table copy and the sheets, in the documented 1.63 MiB free run below
# the CM block (FREE_BLOCK_END).
OW_PLAYER_ADDR = 0x08B72000
OW_PLAYER_END = 0x08C80000           # SHIM_ADDR: the sheets must stop before it
VAR_COSTUME_X, VAR_COSTUME_Y = 0x8004, 0x8005
# --- helpers ---

def load_charmap():
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open(CHARMAP, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                table[m.group(1)] = int(m.group(2), 16)
    return table


def enc_text(s, cm):
    out = bytearray()
    for ch in s:
        if ch == "\n":
            out.append(0xFE)
            continue
        if ch not in cm:
            raise ValueError(f"char {ch!r} not in charmap: {s!r}")
        out.append(cm[ch])
    out.append(0xFF)
    return bytes(out)


def thumb_bl(src_rom_addr, dst_rom_addr):
    off = dst_rom_addr - (src_rom_addr + 4)
    assert -0x400000 <= off < 0x400000, f"BL out of range: {off:#x}"
    off = (off >> 1) & 0x3FFFFF
    hw1 = 0xF000 | ((off >> 11) & 0x7FF)
    hw2 = 0xF800 | (off & 0x7FF)
    return struct.pack("<HH", hw1, hw2)


# --- script assembly (Gen 3 event bytecode) ---

def op_loadword(addr):      return bytes([0x0F, 0x00]) + struct.pack("<I", addr)
def op_special(n):          return bytes([0x25]) + struct.pack("<H", n)
def op_compare(var, val):   return bytes([0x21]) + struct.pack("<HH", var, val)
def op_goto_if(cond, addr): return bytes([0x06, cond]) + struct.pack("<I", addr)
def op_goto(addr):          return bytes([0x05]) + struct.pack("<I", addr)
def op_setvar(var, val):    return bytes([0x16]) + struct.pack("<HH", var, val)
def op_setflag(f):          return bytes([0x29]) + struct.pack("<H", f)
def op_clearflag(f):        return bytes([0x2A]) + struct.pack("<H", f)
def op_callstd(n):          return bytes([0x09, n])
def op_callnative(addr):    return bytes([0x23]) + struct.pack("<I", addr)
def op_release():           return bytes([0x6C])
def op_getplayerxy(vx, vy): return bytes([0x42]) + struct.pack("<HH", vx, vy)
def op_warpmuted(bank, num, warp, x, y):
    return bytes([0x3A, bank, num, warp]) + struct.pack("<HH", x, y)
def op_end():               return bytes([0x02])
def op_givepokemon(species, level, item=0):
    return bytes([0x79]) + struct.pack("<HBH", species, level, item) + bytes(9)


def alias_for(display):
    if display.endswith(" (anime)"):
        display = display[:-len(" (anime)")]
    return re.sub(r"[^A-Za-z0-9]", "", display)


def main():
    data = bytearray(ROM_IN.read_bytes())
    got = hashlib.sha1(data).hexdigest()
    if got != ROM_SHA1:
        raise SystemExit(f"ROM sha1 mismatch: {got} (expected {ROM_SHA1})")

    cm = load_charmap()
    with open(HERE / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = [c for c in manifest["characters"] if "roster_species_ids" in c]
    # DERIVE the character count; never hardcode it. This assert read `== 210`
    # and broke the build the moment the 2026-07-25 roster audit brought the count
    # to 238 -- the third time a stale literal has cost this project a session
    # (SPRITE_PLAN.md §5). The three C shims get it via -DNUM_CHARACTERS below for
    # the same reason: a shim compiled with the wrong count silently accepts an
    # out-of-range character index instead of rejecting it.
    num_chars = len(chars)
    assert num_chars == manifest["record_count"], \
        (f"manifest lists {num_chars} characters but record_count is "
         f"{manifest['record_count']} -- re-run emit_characters.py")
    bitmaps = (HERE / "character_mode" / "rosters_expanded.bin").read_bytes()

    # CMDbgGive2 must give a species that is genuinely OFF the first character's
    # roster, or the debug code stops exercising the enforcement path at all.
    # It was hardcoded to Meowth (52), which joined Red's roster on 2026-07-23
    # via Persian -- so the code silently became a no-op and the shipped
    # playthrough checklist started telling testers to expect a PC transfer that
    # can no longer happen. Derive it, the way Seaglass and Lazarus already do.
    import re as _re
    _shim_src = (ROOT / "src" / "character_mode.c").read_text()
    _stride = int(_re.search(r"#define BITMAP_STRIDE\s+(\d+)", _shim_src).group(1))
    _nspecies = int(_re.search(r"#define NUM_SPECIES\s+(\d+)", _shim_src).group(1))
    assert len(bitmaps) == len(chars) * _stride, (len(bitmaps), _stride)
    _bm0 = bitmaps[0:_stride]
    _on0 = lambda sp: (_bm0[sp >> 3] >> (sp & 7)) & 1
    dbg_give2 = next(sp for sp in range(1, _nspecies) if not _on0(sp))
    print(f"CMDbgGive2 species (off-roster for {chars[0]['character']}): {dbg_give2}")
    assert len(bitmaps) == num_chars * 172, len(bitmaps)
    print(f"character count: {num_chars} (derived from characters_manifest.json)")

    # --- 1. compile shim ---
    BUILD.mkdir(exist_ok=True)
    obj = BUILD / "character_mode.o"
    elf = BUILD / "character_mode.elf"
    binf = BUILD / "character_mode.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    f"-DBITMAPS_ADDR={BITMAPS_ADDR:#x}",
                    f"-DNUM_CHARACTERS={num_chars}",
                    "-o", str(obj), str(ROOT / "src" / "character_mode.c")],
                   check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{SHIM_ADDR:#x}",
                    "--entry", "CM_GiveMonToPlayerGated",
                    "-o", str(elf), str(obj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(elf), str(binf)], check=True)
    shim = binf.read_bytes()
    # entry must be at the very start of .text
    sym = subprocess.run(["arm-none-eabi-nm", str(elf)], check=True,
                         capture_output=True, text=True).stdout
    m = re.search(r"^([0-9a-f]+) T CM_GiveMonToPlayerGated$", sym, re.M)
    assert m and int(m.group(1), 16) == SHIM_ADDR, f"shim entry not at SHIM_ADDR:\n{sym}"
    # The activation sweep, resolved from the same nm output. It is NOT the
    # entry and must not be: the BL patches target SHIM_ADDR directly, so
    # CM_GiveMonToPlayerGated has to stay first in .text.
    _ms = re.search(r"^([0-9a-f]+) T CM_SweepPartyToPC$", sym, re.M)
    assert _ms, f"CM_SweepPartyToPC not found in:\n{sym}"
    SWEEP_PARTY = int(_ms.group(1), 16) | 1
    assert SHIM_ADDR < (SWEEP_PARTY & ~1) < SHIM_ADDR + len(shim), \
        f"CM_SweepPartyToPC at {SWEEP_PARTY:#x} outside the shim blob"
    # --- early party-wide Exp. Share (src/exp_share.c): the activation sweep
    # callnative in every character handler goes through this wrapper. ---
    xobj, xelf, xbin = BUILD / "exp_share.o", BUILD / "exp_share.elf", BUILD / "exp_share.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    "-Wall", "-Wextra", f"-DSWEEP_PARTY={SWEEP_PARTY:#x}",
                    "-o", str(xobj), str(ROOT / "src" / "exp_share.c")], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{EXP_SHARE_ADDR:#x}",
                    "--entry", "CM_ActivateSweepAndExpShare", "-o", str(xelf), str(xobj)],
                   check=True)
    _xsec = subprocess.run(["arm-none-eabi-objdump", "-h", str(xelf)], check=True,
                           capture_output=True, text=True).stdout
    for _sec in (".rodata", ".data", ".bss"):
        assert not re.search(rf"^\s*\d+\s+{re.escape(_sec)}\S*\s+0*[1-9a-f]", _xsec, re.M), (
            f"exp_share.elf has a non-empty {_sec}")
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(xelf), str(xbin)], check=True)
    exp_share = xbin.read_bytes()
    _xs = re.search(r"^([0-9a-f]+) T CM_ActivateSweepAndExpShare$",
                    subprocess.run(["arm-none-eabi-nm", str(xelf)], check=True,
                                   capture_output=True, text=True).stdout, re.M)
    ACTIVATE_SWEEP = int(_xs.group(1), 16) | 1
    # Explicit, because the only thing that caught the overrun was splice()'s
    # 0xFF precondition reporting it as "bitmaps: target not 0xFF", which reads
    # like a wrong base ROM rather than "the shim grew".
    assert len(shim) <= BITMAPS_ADDR - SHIM_ADDR, (
        f"shim too big: {len(shim)} > {BITMAPS_ADDR - SHIM_ADDR} -- it would "
        f"run into BITMAPS_ADDR {BITMAPS_ADDR:#x}")
    print(f"shim: {len(shim)} bytes @ {SHIM_ADDR:#x}")

    # --- 1b. compile the wild-encounter override shim (separate compile
    # unit + link address -- keeps this new feature from disturbing the
    # tightly-packed SHIM_ADDR/BITMAPS_ADDR layout above at all) ---
    wobj = BUILD / "wild_encounter_mode.o"
    welf = BUILD / "wild_encounter_mode.elf"
    wbin = BUILD / "wild_encounter_mode.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    f"-DWILD_OFFSETS_ADDR={WILD_OFFSETS_ADDR:#x}",
                    f"-DNUM_CHARACTERS={num_chars}",
                    # -DTOBIAS_CHAR_ID is gone (2026-07-26). Tobias's hand-coded
                    # 1% legendary-inclusive table was replaced by the general
                    # legendary rule, which reproduces it exactly. The three
                    # sites -- here, the C, and emit_wild_override.py -- were
                    # deleted together on purpose.
                    f"-DWILD_DATA_ADDR={WILD_DATA_ADDR:#x}",
                    f"-DWILD_LEG_OFFSETS_ADDR={WILD_LEG_OFFSETS_ADDR:#x}",
                    f"-DWILD_LEG_DATA_ADDR={WILD_LEG_DATA_ADDR:#x}",
                    "-o", str(wobj), str(ROOT / "src" / "wild_encounter_mode.c")],
                   check=True)
    # Linked via the gcc driver (not raw ld, unlike the shim above) so that
    # libgcc's __aeabi_uidivmod/__aeabi_idivmod get pulled in automatically
    # -- this file uses `%` (Random() % 100, Random() % numFam) where
    # character_mode.c's shim has no division at all. -nostartfiles keeps
    # it freestanding (no crt0/_start requirement); the resulting .text is
    # still a single self-contained relocation-free blob, same as the shim.
    subprocess.run(["arm-none-eabi-gcc", "-mthumb", "-mcpu=arm7tdmi", "-mtune=arm7tdmi",
                    "-nostartfiles", "-Wl,-Ttext," + f"{WILD_SHIM_ADDR:#x}",
                    "-Wl,--entry,CM_CreateWildMonGated",
                    "-o", str(welf), str(wobj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(welf), str(wbin)], check=True)
    wild_shim = wbin.read_bytes()
    wsym = subprocess.run(["arm-none-eabi-nm", str(welf)], check=True,
                          capture_output=True, text=True).stdout
    wm = re.search(r"^([0-9a-f]+) T CM_CreateWildMonGated$", wsym, re.M)
    assert wm, f"CM_CreateWildMonGated not in the wild shim ELF:\n{wsym}"
    # RESOLVED from the ELF, not assumed to be the first thing in the blob. This
    # used to assert `== WILD_SHIM_ADDR` and held only by luck of source order:
    # adding the legendary picker's CM_MatchStage helper made gcc emit THAT
    # first, and the four BL sites would have branched into the middle of a
    # helper. Exactly the trap the mugshot renderer's two entry points already
    # sprang -- gcc orders functions however it likes.
    wild_entry = int(wm.group(1), 16)
    assert WILD_SHIM_ADDR <= wild_entry < WILD_SHIM_ADDR + len(wild_shim), \
        f"entry {wild_entry:#x} outside the shim blob"
    print(f"wild-encounter shim: {len(wild_shim)} bytes @ {WILD_SHIM_ADDR:#x} "
          f"(entry CM_CreateWildMonGated @ {wild_entry:#x})")

    # --- 1b2. compile the encounter-marker shim (fourth compile unit; see
    # MARKER_SHIM_ADDR for why it lives low in the ROM). ---
    mobj = BUILD / "battle_marker.o"
    melf = BUILD / "battle_marker.elf"
    mbin = BUILD / "battle_marker.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    f"-DNUM_CHARACTERS={num_chars}",
                    f"-DNUM_SPECIES={_nspecies}",
                    f"-DBITMAP_STRIDE={_stride}",
                    f"-DBITMAPS_ADDR={BITMAPS_ADDR:#x}",
                    f"-DMARKER_ADDR={MARKER_ADDR:#x}",
                    "-o", str(mobj), str(ROOT / "src" / "battle_marker.c")],
                   check=True)
    subprocess.run(["arm-none-eabi-gcc", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-nostartfiles",
                    "-Wl,-Ttext," + f"{MARKER_SHIM_ADDR:#x}",
                    "-Wl,--entry,CM_BattleStringGated",
                    "-o", str(melf), str(mobj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(melf), str(mbin)], check=True)
    marker_shim = mbin.read_bytes()
    msym = subprocess.run(["arm-none-eabi-nm", str(melf)], check=True,
                          capture_output=True, text=True).stdout
    mm = re.search(r"^([0-9a-f]+) T CM_BattleStringGated$", msym, re.M)
    assert mm, f"CM_BattleStringGated not in the marker ELF:\n{msym}"
    # RESOLVED from the ELF, never assumed to be first in the blob -- gcc orders
    # functions however it likes, and this repo has been bitten twice by
    # assuming otherwise (the wild picker's helper; the mugshot's two entries).
    marker_entry = int(mm.group(1), 16)
    assert MARKER_SHIM_ADDR <= marker_entry < MARKER_SHIM_ADDR + len(marker_shim), \
        f"marker entry {marker_entry:#x} outside its blob"
    assert MARKER_SHIM_ADDR + len(marker_shim) <= MARKER_ADDR, (
        f"marker shim ({len(marker_shim)} B @ {MARKER_SHIM_ADDR:#x}) runs into "
        f"the string blob at {MARKER_ADDR:#x}")
    print(f"encounter-marker shim: {len(marker_shim)} bytes @ "
          f"{MARKER_SHIM_ADDR:#x} (entry @ {marker_entry:#x})")

    # --- 1c. compile the mugshot renderer (third compile unit; see the
    # CM_SPRITE_SHIM_ADDR comment for why it needs no BL-reach window). Both
    # entry points are resolved from the linked ELF rather than assumed to be
    # at a fixed order/offset -- gcc is free to emit them in either order, and
    # the script's `callnative` operands have to be exactly right. ---
    sobj = BUILD / "character_sprite.o"
    selfp = BUILD / "character_sprite.elf"
    sbin = BUILD / "character_sprite.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    f"-DSPRITE_PTRS_ADDR={CM_SPRITE_PTRS_ADDR:#x}",
                    f"-DNUM_CHARACTERS={num_chars}",
                    "-o", str(sobj), str(ROOT / "src" / "character_sprite.c")],
                   check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{CM_SPRITE_SHIM_ADDR:#x}",
                    "--entry", "CM_ShowCharacterMugshot",
                    "-o", str(selfp), str(sobj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(selfp), str(sbin)], check=True)
    sprite_shim = sbin.read_bytes()
    ssym = subprocess.run(["arm-none-eabi-nm", str(selfp)], check=True,
                          capture_output=True, text=True).stdout
    def sprite_sym(name):
        m = re.search(rf"^([0-9a-f]+) [Tt] {name}$", ssym, re.M)
        assert m, f"{name} not found in:\n{ssym}"
        a = int(m.group(1), 16)
        assert CM_SPRITE_SHIM_ADDR <= a < CM_SPRITE_SHIM_ADDR + len(sprite_shim), \
            f"{name} at {a:#x} outside the spliced blob"
        return a | 1                      # callnative operands carry the Thumb bit
    SHOW_MUGSHOT = sprite_sym("CM_ShowCharacterMugshot")
    HIDE_MUGSHOT = sprite_sym("CM_HideCharacterMugshot")
    print(f"mugshot renderer: {len(sprite_shim)} bytes @ {CM_SPRITE_SHIM_ADDR:#x} "
          f"(show {SHOW_MUGSHOT:#x}, hide {HIDE_MUGSHOT:#x})")

    # --- 1d. roster display: native task + list menu (src/roster_display.c) ---
    _roots_manifest = json.loads((HERE / "character_mode" / "roster_roots_manifest.json").read_text())
    assert _roots_manifest["characters"] == num_chars, (
        "roster_roots.bin was emitted for %d characters, this build has %d -- "
        "re-run emit_roster_roots.py" % (_roots_manifest["characters"], num_chars))
    roster_roots = (HERE / "character_mode" / "roster_roots.bin").read_bytes()
    assert len(roster_roots) == _roots_manifest["blob_size_bytes"]
    robj, relf, rbin = BUILD / "roster_display.o", BUILD / "roster_display.elf", BUILD / "roster_display.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    "-Wall", "-Wextra",
                    f"-DNUM_CHARACTERS={num_chars}",
                    f"-DROSTER_ROOTS_ADDR={ROSTER_ROOTS_ADDR:#x}",
                    f"-DROSTER_ROOTS_OFF={_roots_manifest['roots_offset_bytes']}",
                    f"-DROSTER_NAMES_ADDR={ROSTER_NAMES_ADDR:#x}",
                    f"-DROSTER_NAME_STRIDE={ROSTER_NAME_STRIDE}",
                    "-o", str(robj), str(ROOT / "src" / "roster_display.c")], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{ROSTER_MENU_ADDR:#x}",
                    "--entry", "CM_RosterOpen", "-o", str(relf), str(robj)], check=True)
    # Nothing may live outside .text: this injector keeps only that section.
    _rsec = subprocess.run(["arm-none-eabi-objdump", "-h", str(relf)], check=True,
                           capture_output=True, text=True).stdout
    for _sec in (".rodata", ".data", ".bss"):
        assert not re.search(rf"^\s*\d+\s+{re.escape(_sec)}\S*\s+0*[1-9a-f]", _rsec, re.M), (
            f"roster_display.elf has a non-empty {_sec}: objcopy --only-section=.text "
            f"would silently drop it")
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(relf), str(rbin)], check=True)
    roster_menu = rbin.read_bytes()
    _rsym = subprocess.run(["arm-none-eabi-nm", str(relf)], check=True,
                           capture_output=True, text=True).stdout
    _m = re.search(r"^([0-9a-f]+) [Tt] CM_RosterOpen$", _rsym, re.M)
    assert _m, _rsym
    ROSTER_OPEN = int(_m.group(1), 16) | 1
    assert ROSTER_MENU_ADDR < ROSTER_OPEN < ROSTER_MENU_ADDR + len(roster_menu)
    # Display names for the header, fixed stride, indexed by TABLE index.
    roster_names = bytearray()
    assert len(manifest["characters"]) == num_chars
    for c in manifest["characters"]:          # TABLE order, unfiltered
        disp = c["character"]
        if disp.endswith(" (anime)"):
            disp = disp[:-len(" (anime)")]
        enc = enc_text(disp, cm)
        assert len(enc) <= ROSTER_NAME_STRIDE, (disp, len(enc))
        roster_names += enc + b"\xff" * (ROSTER_NAME_STRIDE - len(enc))
    print(f"roster display: {len(roster_menu)} bytes @ {ROSTER_MENU_ADDR:#x} "
          f"(open {ROSTER_OPEN:#x}); roots {len(roster_roots)} B, names {len(roster_names)} B")

    wild_data = (HERE / "character_mode" / "wild_override.bin").read_bytes()
    wild_offsets = (HERE / "character_mode" / "wild_override_offsets.bin").read_bytes()
    assert len(wild_offsets) == len(chars) * 4, len(wild_offsets)
    leg_data = (HERE / "character_mode" / "wild_legendary.bin").read_bytes()
    leg_offsets = (HERE / "character_mode" / "wild_legendary_offsets.bin").read_bytes()
    assert len(leg_offsets) == len(chars) * 4, len(leg_offsets)
    # Both tables grow with the roster and both sit in the same 0xFF run, so the
    # gaps between them are load-bearing. Without these, an overflow surfaces as
    # splice()'s generic "target not 0xFF-free", which reads like a free-space
    # problem rather than "the table outgrew its window".
    assert WILD_SHIM_ADDR + len(wild_shim) <= WILD_OFFSETS_ADDR, (
        f"wild shim is {len(wild_shim)} B, past WILD_OFFSETS_ADDR -- only "
        f"{WILD_OFFSETS_ADDR - WILD_SHIM_ADDR} B of window (it grew from 976 to "
        f"1344 B when the legendary picker landed)")
    assert WILD_OFFSETS_ADDR + len(wild_offsets) <= WILD_DATA_ADDR, (
        f"wild offsets ({len(wild_offsets)} B) overrun WILD_DATA_ADDR -- "
        f"{(WILD_DATA_ADDR - WILD_OFFSETS_ADDR) // 4} characters is the ceiling here")
    assert WILD_DATA_ADDR + len(wild_data) <= WILD_LEG_OFFSETS_ADDR, (
        f"wild_override.bin ({len(wild_data)} B) reaches "
        f"{WILD_DATA_ADDR + len(wild_data):#x}, past WILD_LEG_OFFSETS_ADDR "
        f"{WILD_LEG_OFFSETS_ADDR:#x} -- move the legendary tables further along")
    assert WILD_LEG_OFFSETS_ADDR + len(leg_offsets) <= WILD_LEG_DATA_ADDR, (
        f"legendary offsets ({len(leg_offsets)} B) overrun WILD_LEG_DATA_ADDR")

    # --- 2. build the selection script extension ---
    # Layout inside the script blob (single pass with fixups):
    #   [check chain][handlers][strings]
    # Compute sizes first: every check = 20B; debug handlers and char handlers
    # are fixed-size except trailing strings, so lay out strings last.
    debug_codes = [
        ("CMDbgOff",   "off"),
        ("CMDbgGive1", "give_ok"),
        ("CMDbgGive2", "give_bad"),
    ]
    aliases = []
    seen = {}
    for i, c in enumerate(chars):
        a = alias_for(c["character"])
        assert 1 <= len(a) <= 11, f"alias too long for naming screen: {a!r}"
        assert a not in seen, f"alias collision: {a!r} ({c['character']} vs {seen[a]})"
        seen[a] = c["character"]
        aliases.append(a)
    for code, _ in debug_codes:
        assert code not in seen
    # Aliases are derived for EVERY character, including hidden ones, so the
    # uniqueness and length assertions above still cover a character that a later
    # roster change un-hides. Only the chain below is filtered.

    # --- the threshold gate (push_rosters.md §3) ---------------------------
    # A character below the six-fully-evolved threshold (flags bit1, set by
    # emit_characters.py from character_drops.json) gets NO check block and NO
    # handler: typing its name falls off the end of the chain into Radical Red's
    # own "Invalid code." handler, exactly as any unrecognised code does.
    #
    # What is deliberately NOT filtered: the character's record, its allow-bitmap,
    # its wild-override table and its sprite pointer all stay at the same index.
    # Saves store the character INDEX, so a save that already selected a
    # now-hidden character keeps playing with full enforcement -- only the
    # selection path refuses. Never gate enforcement on this bit.
    selectable = [(i, c) for i, c in enumerate(chars) if not c.get("hidden")]
    hidden = [c["character"] for c in chars if c.get("hidden")]
    assert selectable, "every character is hidden -- character_drops.json is wrong"
    # Character 0 is what CMDbgGive2's off-roster species was derived from and
    # what the debug codes exercise; it must remain reachable.
    assert not chars[0].get("hidden"), \
        f"character 0 ({chars[0]['character']}) is hidden -- the debug codes " \
        "derive their fixtures from it"
    print(f"selection gate: {len(selectable)} selectable, {len(hidden)} hidden "
          f"below threshold" + (f" ({', '.join(hidden[:6])}"
                                f"{', ...' if len(hidden) > 6 else ''})" if hidden else ""))

    CHECK_SIZE = len(op_loadword(0) + op_special(0x12D) + op_compare(0x800D, 0) + op_goto_if(1, 0))
    assert CHECK_SIZE == 20
    n_checks = len(debug_codes) + len(selectable)
    chain_size = n_checks * CHECK_SIZE + len(op_goto(0))

    # handlers
    H_OFF_SIZE  = len(op_clearflag(0) + op_setvar(0, 0) + op_loadword(0) + op_callstd(6) + op_release() + op_end())
    H_GIVE_SIZE = len(op_givepokemon(0, 5) + op_loadword(0) + op_callstd(6) + op_release() + op_end())
    # Character handlers additionally bracket the confirm message with the two
    # mugshot callnatives (callstd 6 blocks until the player dismisses the box,
    # so the sprite stays up for exactly as long as the message does).
    H_CHAR_SIZE = len(op_setvar(0, 0) + op_setflag(0) + op_givepokemon(0, 5)
                      + op_callnative(0)   # the activation party sweep
                      + op_callnative(0) + op_loadword(0) + op_callstd(6)
                      + op_callnative(0) + op_release() + op_end())
    # A costume character's handler ends `goto <its costume tail>` (5 B) in
    # place of `release; end` (2 B); the tails follow the handlers.
    from character_mode.rr_costumes import costumes, costume_for_character
    _costume_table = costumes()
    char_costume = [costume_for_character(c["character"], _costume_table)
                    for _, c in selectable]
    # The rest get their own walk/run sprite where a sheet is staged: the same
    # tail, with a synthetic run (walk/run = the new id, every other costume
    # var cleared to the gender default).
    from character_mode import rr_ow_player
    ow_blob, ow_ids, ow_patches = rr_ow_player.build(
        data, [c["character"] for j, (_, c) in enumerate(selectable) if not char_costume[j]],
        OW_PLAYER_ADDR)
    assert OW_PLAYER_ADDR + len(ow_blob) <= OW_PLAYER_END, (
        f"overworld sheets ({len(ow_blob):,} B) run into the CM block")
    for j, (_, c) in enumerate(selectable):
        if not char_costume[j] and c["character"] in ow_ids:
            gid = ow_ids[c["character"]]
            char_costume[j] = {"walk": gid, "sets": rr_ow_player.avatar_sets(gid),
                               "walk_only": True}
    H_COSTUME_EXTRA = len(op_goto(0)) - len(op_release() + op_end())
    def costume_tail(c):
        b = bytearray()
        for var, val in c["sets"]:
            b += op_setvar(var, val)
        b += op_getplayerxy(VAR_COSTUME_X, VAR_COSTUME_Y)
        b += op_warpmuted(*BEDROOM_MAP, 0xFF, VAR_COSTUME_X, VAR_COSTUME_Y)
        b += op_release() + op_end()
        return bytes(b)

    chain_addr = SCRIPT_ADDR
    handlers_addr = chain_addr + chain_size
    h_addrs = {}
    cur = handlers_addr
    for code, kind in debug_codes:
        h_addrs[code] = cur
        cur += H_OFF_SIZE if kind == "off" else H_GIVE_SIZE
    char_h_addrs = []
    for j in range(len(selectable)):
        char_h_addrs.append(cur)
        cur += H_CHAR_SIZE + (H_COSTUME_EXTRA if char_costume[j] else 0)
    costume_tail_addrs = {}
    for j in range(len(selectable)):
        if char_costume[j]:
            costume_tail_addrs[j] = cur
            cur += len(costume_tail(char_costume[j]))
    strings_addr = cur

    # strings: debug code names + messages, alias names, per-char messages
    strings = bytearray()
    str_addrs = {}
    def add_str(key, text):
        str_addrs[key] = strings_addr + len(strings)
        strings.extend(enc_text(text, cm))

    for code, _ in debug_codes:
        add_str("code:" + code, code)
    add_str("msg:off", "Character Mode is now off.")
    add_str("msg:give_ok", "Debug: tried to give Pikachu.")
    add_str("msg:give_bad", "Debug: off-roster give test.")
    # keyed by CHAIN SLOT j, not table index i -- the two diverge once anyone is
    # hidden, and mixing them up would point a handler at the wrong name.
    for j, (i, c) in enumerate(selectable):
        add_str(f"alias:{j}", aliases[i])
        disp = c["character"]
        if disp.endswith(" (anime)"):
            disp = disp[:-len(" (anime)")]
        add_str(f"msg:{j}", f"Character Mode:\nyou are now {disp}!")

    # emit chain
    blob = bytearray()
    for code, kind in debug_codes:
        blob += op_loadword(str_addrs["code:" + code])
        blob += op_special(0x12D)
        blob += op_compare(0x800D, 0)
        blob += op_goto_if(1, h_addrs[code])
    for j in range(len(selectable)):
        blob += op_loadword(str_addrs[f"alias:{j}"])
        blob += op_special(0x12D)
        blob += op_compare(0x800D, 0)
        blob += op_goto_if(1, char_h_addrs[j])
    blob += op_goto(INVALID_CODE_HANDLER)
    assert len(blob) == chain_size

    # emit handlers
    for code, kind in debug_codes:
        assert SCRIPT_ADDR + len(blob) == h_addrs[code]
        if kind == "off":
            blob += op_clearflag(FLAG_CHARACTER_MODE)
            blob += op_setvar(VAR_CHARACTER_ID, 0)
            blob += op_loadword(str_addrs["msg:off"])
        else:
            species = 25 if kind == "give_ok" else dbg_give2  # Pikachu / derived off-roster
            blob += op_givepokemon(species, 5)
            blob += op_loadword(str_addrs["msg:" + kind])
        blob += op_callstd(6) + op_release() + op_end()
    for j, (i, c) in enumerate(selectable):
        assert SCRIPT_ADDR + len(blob) == char_h_addrs[j]
        sig = c["roster_species_ids"][0]
        # i, the TABLE index, is what the save stores -- not j, the chain slot.
        blob += op_setvar(VAR_CHARACTER_ID, i + 1)
        blob += op_setflag(FLAG_CHARACTER_MODE)
        blob += op_givepokemon(sig, 5)
        # Sweep AFTER the give, never before: beforehand a party holding only an
        # off-roster mon hits the never-empty rule and nothing is boxed.
        blob += op_callnative(ACTIVATE_SWEEP)   # the sweep, then the early Exp. Share
        blob += op_callnative(SHOW_MUGSHOT)
        blob += op_loadword(str_addrs[f"msg:{j}"])
        blob += op_callstd(6)
        blob += op_callnative(HIDE_MUGSHOT)
        if char_costume[j]:
            blob += op_goto(costume_tail_addrs[j])
        else:
            blob += op_release() + op_end()
    for j in sorted(costume_tail_addrs):
        assert SCRIPT_ADDR + len(blob) == costume_tail_addrs[j]
        blob += costume_tail(char_costume[j])
    assert SCRIPT_ADDR + len(blob) == strings_addr
    blob += strings
    # What each activation is meant to wear, for the live layer
    # (tools/tests/run_costume_e2e.sh) -- which resolves the ids through the
    # BUILT ROM's own overworld tables rather than trusting this file for that.
    (BUILD / "avatar_manifest.json").write_text(json.dumps({
        c["character"]: {"walk": char_costume[j]["walk"] if char_costume[j] else 0,
                         "kind": ("none" if not char_costume[j] else
                                  "walk_only" if char_costume[j].get("walk_only") else "costume")}
        for j, (_, c) in enumerate(selectable)}, indent=1))
    _worn = [j for j in sorted(costume_tail_addrs) if not char_costume[j].get("walk_only")]
    print(f"overworld costumes: {len(_worn)} characters wear RR's own "
          f"({', '.join(selectable[j][1]['character'] for j in _worn)}); "
          f"{len(ow_ids)} more get a walk/run sprite ({len(ow_blob):,} B @ {OW_PLAYER_ADDR:#x})")
    print(f"script extension: {len(blob)} bytes @ {SCRIPT_ADDR:#x} "
          f"({n_checks} codes: {len(debug_codes)} debug + {len(selectable)} "
          f"selectable characters; {len(hidden)} hidden)")

    # --- 3. splice + patch ---
    spliced = []
    # the overworld word patches: switcher slot 3 and the palette-table literals
    for _off, _old, _new in ow_patches:
        assert struct.unpack_from("<I", data, _off)[0] == _old, (hex(_off), _old)
        struct.pack_into("<I", data, _off, _new)

    def splice(rom_addr, payload, label):
        off = rom_addr - 0x08000000
        assert off + len(payload) <= FREE_BLOCK_END, f"{label} overruns free block"
        seg = data[off:off + len(payload)]
        assert all(b == 0xFF for b in seg), f"{label}: target not 0xFF-free at {rom_addr:#x}"
        # The 0xFF precondition alone would miss an overlap whose already-written
        # bytes happen to be 0xFF, so check the regions against each other too.
        # A stale hardcoded size elsewhere shows up here as a real error rather
        # than as garbled data several test layers later.
        for o_off, o_len, o_label in spliced:
            assert off >= o_off + o_len or off + len(payload) <= o_off, \
                (f"{label} @ {rom_addr:#x} (+{len(payload)}) overlaps "
                 f"{o_label} @ {o_off + 0x08000000:#x} (+{o_len})")
        spliced.append((off, len(payload), label))
        data[off:off + len(payload)] = payload

    splice(SHIM_ADDR, shim, "shim")
    splice(OW_PLAYER_ADDR, ow_blob, "overworld walk sprites")
    splice(BITMAPS_ADDR, bitmaps, "bitmaps")
    splice(SCRIPT_ADDR, blob, "script")
    splice(WILD_SHIM_ADDR, wild_shim, "wild-encounter shim")
    splice(CM_SPRITE_SHIM_ADDR, sprite_shim, "mugshot renderer")

    # --- roster display: blobs, code, and the console pre-entry ---
    for _lo, _n, _lbl in ((ROSTER_ROOTS_ADDR, len(roster_roots), "roster roots"),
                          (ROSTER_NAMES_ADDR, len(roster_names), "roster names"),
                          (ROSTER_MENU_ADDR, len(roster_menu), "roster code"),
                          (ROSTER_SCRIPT_ADDR, 0x100, "roster pre-entry")):
        assert _lo + _n <= TEST_SCRIPT_SQUAT[0] or _lo >= TEST_SCRIPT_SQUAT[1], (
            f"{_lbl} @ {_lo:#x} lands in the test builders' script squat "
            f"{TEST_SCRIPT_SQUAT[0]:#x}..{TEST_SCRIPT_SQUAT[1]:#x}")
    splice(ROSTER_ROOTS_ADDR, roster_roots, "roster roots")
    splice(ROSTER_NAMES_ADDR, bytes(roster_names), "roster names")
    splice(ROSTER_MENU_ADDR, roster_menu, "roster display code")
    #   checkflag CM; goto_if unset -> the stock console script, unchanged
    #   lock; msgbox yes/no "View your Character Mode roster?"
    #   no  -> the stock console script (which asks about cheat codes)
    #   yes -> closemessage; callnative CM_RosterOpen; waitstate; release; end
    _t_q = enc_text("View your Character Mode roster?", cm)
    _pre = bytearray()
    _pre += bytes([0x2B]) + struct.pack("<H", FLAG_CHARACTER_MODE)   # checkflag
    _pre += op_goto_if(0, CONSOLE_SCRIPT)
    _pre += bytes([0x6A])                                            # lock
    _q_at = len(_pre) + 2
    _pre += op_loadword(0) + op_callstd(5)                           # yes/no
    _pre += op_compare(0x800D, 1) + op_goto_if(5, CONSOLE_SCRIPT)    # != yes
    _pre += bytes([0x68])                                            # closemessage
    _pre += op_callnative(ROSTER_OPEN)
    _pre += bytes([0x27])                                            # waitstate
    _pre += op_release() + op_end()
    struct.pack_into("<I", _pre, _q_at, ROSTER_SCRIPT_ADDR + len(_pre))
    _pre += _t_q
    splice(ROSTER_SCRIPT_ADDR, bytes(_pre), "roster pre-entry")
    _pat = struct.pack("<I", CONSOLE_SCRIPT)
    _refs, _i = [], data.find(_pat)
    _own = range(ROSTER_SCRIPT_ADDR - 0x08000000, ROSTER_SCRIPT_ADDR - 0x08000000 + len(_pre))
    while _i != -1:
        if _i not in _own:
            _refs.append(_i)
        _i = data.find(_pat, _i + 1)
    assert _refs == [CONSOLE_BG_PTR_OFF], (
        f"references to the console script {CONSOLE_SCRIPT:#x} are "
        f"{[hex(a) for a in _refs]}, expected only {CONSOLE_BG_PTR_OFF:#x}")
    struct.pack_into("<I", data, CONSOLE_BG_PTR_OFF, ROSTER_SCRIPT_ADDR)
    print(f"roster display: console BG ptr -> pre-entry @ {ROSTER_SCRIPT_ADDR:#x} ({len(_pre)} B)")
    splice(WILD_OFFSETS_ADDR, wild_offsets, "wild-encounter offsets")

    # --- character sprites: blobs, then a table of absolute ROM pointers ---
    spr_blobs_p = HERE / "character_mode" / "cm_sprite_blobs.bin"
    spr_offs_p = HERE / "character_mode" / "cm_sprite_offsets.bin"
    if spr_blobs_p.is_file() and spr_offs_p.is_file():
        spr_blobs = spr_blobs_p.read_bytes()
        spr_offs = spr_offs_p.read_bytes()
        assert len(spr_offs) == len(chars) * 8, (len(spr_offs), len(chars))
        ptrs = bytearray()
        wired = 0
        for i in range(len(chars)):
            g, pl = struct.unpack_from("<II", spr_offs, i * 8)
            if g == 0xFFFFFFFF:
                ptrs += struct.pack("<II", 0, 0)        # no art for this character
            else:
                ptrs += struct.pack("<II", CM_SPRITE_BLOBS_ADDR + g,
                                           CM_SPRITE_BLOBS_ADDR + pl)
                wired += 1
        splice(CM_SPRITE_BLOBS_ADDR, spr_blobs, "character sprite blobs")
        splice(CM_SPRITE_PTRS_ADDR, bytes(ptrs), "character sprite pointer table")
        print(f"character sprites: {wired}/{len(chars)} wired, "
              f"{len(spr_blobs):,} B of art @ {CM_SPRITE_BLOBS_ADDR:#x}, "
              f"table @ {CM_SPRITE_PTRS_ADDR:#x}")
    splice(MARKER_SHIM_ADDR, marker_shim, "encounter-marker shim")
    marker_blob = (HERE / "character_mode" / "marker_strings.bin").read_bytes()
    assert len(marker_blob) == num_chars * MARKER_STRIDE, (
        f"marker_strings.bin is {len(marker_blob)} B, expected "
        f"{num_chars * MARKER_STRIDE} -- re-run emit_marker_strings.py")
    splice(MARKER_ADDR, marker_blob, "encounter marker strings")
    print(f"encounter marker: {len(marker_blob):,} B @ {MARKER_ADDR:#x}, "
          f"stride {MARKER_STRIDE}")

    splice(WILD_DATA_ADDR, wild_data, "wild-encounter data")
    splice(WILD_LEG_OFFSETS_ADDR, leg_offsets, "legendary-encounter offsets")
    splice(WILD_LEG_DATA_ADDR, leg_data, "legendary-encounter data")

    # --- PC second guard: its own unit, a trampoline over CheckHeap, two BLs,
    # one tail ---
    gobj, gelf, gbin = BUILD / "pc_guard.o", BUILD / "pc_guard.elf", BUILD / "pc_guard.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    "-Wall", "-Wextra",
                    f"-DNUM_CHARACTERS={num_chars}",
                    f"-DBITMAPS_ADDR={BITMAPS_ADDR:#x}",
                    f"-DSWEEP_PARTY_ADDR={SWEEP_PARTY | 1:#x}",
                    "-o", str(gobj), str(ROOT / "src" / "pc_guard.c")], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{PC_GUARD_ADDR:#x}",
                    "--entry", "CM_PSSLastMonGuard", "-o", str(gelf), str(gobj)], check=True)
    _gsec = subprocess.run(["arm-none-eabi-objdump", "-h", str(gelf)], check=True,
                           capture_output=True, text=True).stdout
    for _sec in (".rodata", ".data", ".bss"):
        assert not re.search(rf"^\s*\d+\s+{re.escape(_sec)}\S*\s+0*[1-9a-f]", _gsec, re.M), (
            f"pc_guard.elf has a non-empty {_sec}: objcopy --only-section=.text "
            f"would silently drop it")
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(gelf), str(gbin)], check=True)
    pc_guard = gbin.read_bytes()
    _gsym = subprocess.run(["arm-none-eabi-nm", str(gelf)], check=True,
                           capture_output=True, text=True).stdout
    _mg = re.search(r"^([0-9a-f]+) T CM_PSSLastMonGuard$", _gsym, re.M)
    assert _mg, _gsym
    PSS_GUARD = int(_mg.group(1), 16) | 1
    assert PC_GUARD_ADDR <= (PSS_GUARD & ~1) < PC_GUARD_ADDR + len(pc_guard)
    splice(PC_GUARD_ADDR, pc_guard, "PC second-guard code")
    _t = PSS_GUARD_TRAMPOLINE_ADDR - 0x08000000
    assert bytes(data[_t:_t + 8]) == PSS_DEAD_FN_HEAD, (
        "CheckHeap is not at %#x -- re-derive before overwriting it"
        % PSS_GUARD_TRAMPOLINE_ADDR)
    data[_t:_t + 8] = struct.pack("<HHI", 0x4B00, 0x4718, PSS_GUARD)
    for _site in PSS_GUARD_BL_SITES + (PSS_CANSHIFT_BL,):
        _cur = bytes(data[_site:_site + 4])
        _exp = thumb_bl(0x08000000 + _site, PSS_COUNT_ALIVE_EXCEPT)
        assert _cur == _exp, f"PC guard site {_site:#x}: {_cur.hex()} != {_exp.hex()}"
        data[_site:_site + 4] = thumb_bl(0x08000000 + _site, PSS_GUARD_TRAMPOLINE_ADDR)
    _cur = bytes(data[PSS_CANSHIFT_TAIL:PSS_CANSHIFT_TAIL + 4])
    assert _cur == bytes.fromhex("00060028"), f"CanShiftMon tail: {_cur.hex()}"
    data[PSS_CANSHIFT_TAIL:PSS_CANSHIFT_TAIL + 4] = struct.pack("<HH", 0xE01E, 0x46C0)
    print(f"PC second guard: IsRemovingLastPartyMon + CanShiftMon -> {PSS_GUARD:#x} "
          f"via {PSS_GUARD_TRAMPOLINE_ADDR:#x} (CheckHeap)")

    # --- Link trade: sweep before the post-trade save ---
    _ml = re.search(r"^([0-9a-f]+) T CM_LinkTradeSweepThenExpand$", _gsym, re.M)
    assert _ml, _gsym
    LINK_TRADE_SHIM = int(_ml.group(1), 16) | 1
    assert PC_GUARD_ADDR <= (LINK_TRADE_SHIM & ~1) < PC_GUARD_ADDR + len(pc_guard)
    _t = LINK_TRADE_TRAMPOLINE_ADDR - 0x08000000
    assert bytes(data[_t:_t + 8]) == LINK_TRADE_DEAD_BYTES, (
        "CheckHeap+8 is not the dead routine's bytes -- re-derive")
    data[_t:_t + 8] = struct.pack("<HHI", 0x4B00, 0x4718, LINK_TRADE_SHIM)
    _cur = bytes(data[LINK_TRADE_BL_SITE:LINK_TRADE_BL_SITE + 4])
    _exp = thumb_bl(0x08000000 + LINK_TRADE_BL_SITE, STRING_EXPAND_PLACEHOLDERS)
    assert _cur == _exp, f"link-trade site: {_cur.hex()} != {_exp.hex()}"
    data[LINK_TRADE_BL_SITE:LINK_TRADE_BL_SITE + 4] = thumb_bl(
        0x08000000 + LINK_TRADE_BL_SITE, LINK_TRADE_TRAMPOLINE_ADDR)
    print(f"Link-trade sweep: CB2_SaveAndEndTrade's expand BL -> {LINK_TRADE_SHIM:#x} "
          f"via {LINK_TRADE_TRAMPOLINE_ADDR:#x} (CheckHeap+8)")

    # --- Field moves: any party mon uses an HM in the bag (src/field_moves.c) ---
    fobj, felf, fbin = BUILD / "field_moves.o", BUILD / "field_moves.elf", BUILD / "field_moves.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    "-Wall", "-Wextra",
                    "-o", str(fobj), str(ROOT / "src" / "field_moves.c")], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{FIELD_MOVES_ADDR:#x}",
                    "--entry", "CM_FieldMoveCanLearn", "-o", str(felf), str(fobj)], check=True)
    _fsec = subprocess.run(["arm-none-eabi-objdump", "-h", str(felf)], check=True,
                           capture_output=True, text=True).stdout
    for _sec in (".rodata", ".data", ".bss"):
        assert not re.search(rf"^\s*\d+\s+{re.escape(_sec)}\S*\s+0*[1-9a-f]", _fsec, re.M), (
            f"field_moves.elf has a non-empty {_sec}: objcopy --only-section=.text "
            f"would silently drop it")
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(felf), str(fbin)], check=True)
    field_moves = fbin.read_bytes()
    _fsym = subprocess.run(["arm-none-eabi-nm", str(felf)], check=True,
                           capture_output=True, text=True).stdout
    _fl = re.search(r"^([0-9a-f]+) T CM_FieldMoveCanLearn$", _fsym, re.M)
    _fk = re.search(r"^([0-9a-f]+) T CM_FieldMoveKnows$", _fsym, re.M)
    assert _fl and _fk, _fsym
    FIELD_CANLEARN = int(_fl.group(1), 16) | 1
    FIELD_KNOWS = int(_fk.group(1), 16) | 1
    for _a in (FIELD_CANLEARN, FIELD_KNOWS):
        assert FIELD_MOVES_ADDR <= (_a & ~1) < FIELD_MOVES_ADDR + len(field_moves)
    splice(FIELD_MOVES_ADDR, field_moves, "field-move hooks")
    _cur = bytes(data[FIELD_CANLEARN_BL_SITE:FIELD_CANLEARN_BL_SITE + 4])
    _exp = thumb_bl(0x08000000 + FIELD_CANLEARN_BL_SITE, CAN_MON_LEARN_TM_TUTOR)
    assert _cur == _exp, f"field can-learn site: {_cur.hex()} != {_exp.hex()}"
    data[FIELD_CANLEARN_BL_SITE:FIELD_CANLEARN_BL_SITE + 4] = thumb_bl(
        0x08000000 + FIELD_CANLEARN_BL_SITE, FIELD_CANLEARN & ~1)
    _t = FIELD_KNOWS_TRAMPOLINE_ADDR - 0x08000000
    assert bytes(data[_t:_t + 8]) == FIELD_KNOWS_DEAD_BYTES, (
        "CheckHeap+16 is not the dead routine's bytes -- re-derive")
    data[_t:_t + 8] = struct.pack("<HHI", 0x4B00, 0x4718, FIELD_KNOWS)
    _cur = bytes(data[FIELD_KNOWS_BL_SITE:FIELD_KNOWS_BL_SITE + 4])
    _exp = thumb_bl(0x08000000 + FIELD_KNOWS_BL_SITE, MON_KNOWS_MOVE)
    assert _cur == _exp, f"checkpartymove site: {_cur.hex()} != {_exp.hex()}"
    data[FIELD_KNOWS_BL_SITE:FIELD_KNOWS_BL_SITE + 4] = thumb_bl(
        0x08000000 + FIELD_KNOWS_BL_SITE, FIELD_KNOWS_TRAMPOLINE_ADDR)
    print(f"Field moves: PartyHasMonWithFieldMovePotential -> {FIELD_CANLEARN:#x}; "
          f"checkpartymove -> {FIELD_KNOWS:#x} via {FIELD_KNOWS_TRAMPOLINE_ADDR:#x} (CheckHeap+16)")

    # --- 100% catch for on-roster species (src/sure_catch.c) ---
    sobj, self_, sbin = BUILD / "sure_catch.o", BUILD / "sure_catch.elf", BUILD / "sure_catch.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    "-Wall", "-Wextra", f"-DBITMAPS_ADDR={BITMAPS_ADDR:#x}",
                    f"-DNUM_CHARACTERS={num_chars}",
                    "-o", str(sobj), str(ROOT / "src" / "sure_catch.c")], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext", f"{SURE_CATCH_ADDR:#x}",
                    "--entry", "CM_CatchOddsStub", "-o", str(self_), str(sobj)], check=True)
    _ssec = subprocess.run(["arm-none-eabi-objdump", "-h", str(self_)], check=True,
                           capture_output=True, text=True).stdout
    for _sec in (".rodata", ".data", ".bss"):
        assert not re.search(rf"^\s*\d+\s+{re.escape(_sec)}\S*\s+0*[1-9a-f]", _ssec, re.M), (
            f"sure_catch.elf has a non-empty {_sec}: objcopy --only-section=.text "
            f"would silently drop it")
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=.text", str(self_), str(sbin)], check=True)
    sure_catch = sbin.read_bytes()
    _ssym = subprocess.run(["arm-none-eabi-nm", str(self_)], check=True,
                           capture_output=True, text=True).stdout
    _ss = re.search(r"^([0-9a-f]+) T CM_CatchOddsStub$", _ssym, re.M)
    assert _ss, _ssym
    SURE_STUB = int(_ss.group(1), 16)
    splice(SURE_CATCH_ADDR, sure_catch, "100% roster catch")
    splice(EXP_SHARE_ADDR, exp_share, "early Exp. Share")
    _cur = bytes(data[CATCH_ODDS_SITE:CATCH_ODDS_SITE + 4])
    assert _cur == CATCH_ODDS_ORIG, f"handleballthrow odds compare: {_cur.hex()}"
    data[CATCH_ODDS_SITE:CATCH_ODDS_SITE + 4] = thumb_bl(0x08000000 + CATCH_ODDS_SITE, SURE_STUB)
    print(f"100% roster catch: odds compare @ {0x08000000 + CATCH_ODDS_SITE:#x} -> "
          f"{SURE_STUB:#x} ({len(sure_catch)} B @ {SURE_CATCH_ADDR:#x})")

    # BL retargets (verify current bytes first)
    for site in (BL_SITE_CATCH, BL_SITE_GIFT):
        cur_bl = bytes(data[site:site + 4])
        expect = thumb_bl(0x08000000 + site, GIVEMON_ADDR)
        assert cur_bl == expect, (f"BL site {site:#x} bytes {cur_bl.hex()} != expected "
                                  f"BL GiveMonToPlayer {expect.hex()} — wrong ROM or already patched")
        data[site:site + 4] = thumb_bl(0x08000000 + site, SHIM_ADDR)

    # Prove the strings the shim compares against are still there before moving
    # the BL: if one shifted, the marker would silently never fire.
    _want = bytes.fromhex("d1dde0d800fd0600d5e4e4d9d5e6d9d8abfbff")
    for _a in TEXT_WILD_APPEARED:
        _got = bytes(data[_a - 0x08000000:_a - 0x08000000 + len(_want)])
        assert _got == _want, (f"wild intro at {_a:#x}: {_got.hex()} != "
                               f"{_want.hex()}")
    cur_bl = bytes(data[MARKER_BL_SITE:MARKER_BL_SITE + 4])
    expect = thumb_bl(0x08000000 + MARKER_BL_SITE, MARKER_WRAPPER)
    assert cur_bl == expect, (f"marker BL site {MARKER_BL_SITE:#x} bytes "
                              f"{cur_bl.hex()} != expected {expect.hex()}")
    data[MARKER_BL_SITE:MARKER_BL_SITE + 4] = thumb_bl(
        0x08000000 + MARKER_BL_SITE, marker_entry)

    for site in (BL_SITE_LAND_MAIN, BL_SITE_LAND_DOUBLE, BL_SITE_FISH_MAIN, BL_SITE_FISH_DOUBLE):
        cur_bl = bytes(data[site:site + 4])
        expect = thumb_bl(0x08000000 + site, CREATEWILDMON_ADDR)
        assert cur_bl == expect, (f"wild BL site {site:#x} bytes {cur_bl.hex()} != expected "
                                  f"BL CreateWildMon {expect.hex()} — wrong ROM or already patched")
        data[site:site + 4] = thumb_bl(0x08000000 + site, wild_entry)
    n_leg_chars = sum(1 for i in range(len(chars))
                      if leg_data[struct.unpack_from("<I", leg_offsets, i * 4)[0] + 1])
    n_repeat = sum(1 for i in range(len(chars))
                   if leg_data[struct.unpack_from("<I", leg_offsets, i * 4)[0]] & 1)
    print("wild-encounter override: 4 BL sites retargeted "
          "(1% legendary, then 10% non-legendary roster members)")
    print(f"legendary encounters: {len(leg_data):,} B @ {WILD_LEG_DATA_ADDR:#x}, "
          f"offsets @ {WILD_LEG_OFFSETS_ADDR:#x}; {n_leg_chars}/{len(chars)} "
          f"characters have a legendary pool, {n_repeat} repeatable")

    # goto retarget
    cur_goto = struct.unpack_from("<I", data, GOTO_OPERAND_OFF)[0]
    assert cur_goto == INVALID_CODE_HANDLER, f"goto operand is {cur_goto:#x}, expected {INVALID_CODE_HANDLER:#x}"
    struct.pack_into("<I", data, GOTO_OPERAND_OFF, SCRIPT_ADDR)

    # --- 3b. trade gate: wrap the one live in-game trade ---
    # Wrapper mirrors the shim's semantics: flag off, char unset (0), or char
    # out of range -> original trade runs untouched; otherwise the trade is
    # allowed only for characters whose bitmap permits the received species.
    allowing = [i + 1 for i in range(len(chars))
                if bitmaps[i*172 + (TRADE_GIVEN_SPECIES >> 3)] & (1 << (TRADE_GIVEN_SPECIES & 7))]
    wrapper = bytearray()
    wrapper += bytes([0x2B]) + struct.pack("<H", FLAG_CHARACTER_MODE)   # checkflag
    wrapper += op_goto_if(0, TRADE_ORIG_SCRIPT)                          # unset -> orig
    wrapper += op_compare(VAR_CHARACTER_ID, 0)
    wrapper += op_goto_if(1, TRADE_ORIG_SCRIPT)                          # char 0 -> orig
    wrapper += op_compare(VAR_CHARACTER_ID, len(chars) + 1)
    wrapper += op_goto_if(4, TRADE_ORIG_SCRIPT)                          # >184 -> orig
    for idx in allowing:
        wrapper += op_compare(VAR_CHARACTER_ID, idx)
        wrapper += op_goto_if(1, TRADE_ORIG_SCRIPT)
    msg_addr = TRADE_WRAPPER_ADDR + len(wrapper) + len(op_loadword(0) + op_callstd(3) + op_end())
    wrapper += op_loadword(msg_addr)
    wrapper += op_callstd(3)                                             # sign-style msgbox
    wrapper += op_end()
    wrapper += enc_text("Character Mode:\nthis trade is not in your roster.", cm)
    splice(TRADE_WRAPPER_ADDR, bytes(wrapper), "trade wrapper")
    cur_bg = struct.unpack_from("<I", data, TRADE_BG_SCRIPT_PTR_OFF)[0]
    assert cur_bg == TRADE_ORIG_SCRIPT, f"trade BG script ptr is {cur_bg:#x}, expected {TRADE_ORIG_SCRIPT:#x}"
    struct.pack_into("<I", data, TRADE_BG_SCRIPT_PTR_OFF, TRADE_WRAPPER_ADDR)
    print(f"trade gate: wrapper {len(wrapper)} B @ {TRADE_WRAPPER_ADDR:#x} "
          f"({len(allowing)} characters allow species {TRADE_GIVEN_SPECIES})")


    # --- 3c. egg-hatch sweep ---
    # The one enforcement hole reachable in ordinary play: eggs are exempt
    # everywhere by design so an egg event cannot block progress, and nothing
    # then looked at what the egg HATCHED INTO. This overlays the hatch
    # script's tail with a goto into a replayed tail that ends by calling the
    # activation sweep -- after the hatch's waitstate, so it sees the finished
    # Pokemon rather than the egg. docs/GIFT_EGGS.md has the 33 gift eggs this
    # covers; tools/character_mode/egg_hook.py has the RE.
    sys.path.insert(0, str(Path(__file__).resolve().parent / "character_mode"))
    import egg_hook
    egg_entry = struct.unpack_from("<I", data, 0x0006D71C)[0]
    assert egg_entry == egg_hook.SCRIPT_ENTRY, (
        f"egg-hatch script pointer is {egg_entry:#x}, expected "
        f"{egg_hook.SCRIPT_ENTRY:#x} -- the hatch caller has moved")
    egg_tail, egg_patches = egg_hook.build(EGG_TAIL_ADDR, ACTIVATE_SWEEP)
    splice(EGG_TAIL_ADDR, egg_tail, "egg-hatch tail")
    for off, orig, repl in egg_patches:
        seg = bytes(data[off:off + len(orig)])
        assert seg == orig, (
            f"egg splice site {off + 0x08000000:#x} holds {seg.hex()}, "
            f"expected {orig.hex()} -- wrong ROM, or already patched")
        data[off:off + len(repl)] = repl
    print(f"egg-hatch sweep: tail {len(egg_tail)} B @ {EGG_TAIL_ADDR:#x}, "
          f"splice @ {egg_hook.SPLICE_ROM_ADDR:#x} -> callnative {ACTIVATE_SWEEP:#x}")

    # --- 3d. PC-exit sweep ---
    # Enforcement deliberately routes off-roster mons INTO the PC, and until
    # 2026-09-06 nothing re-enforced the roster afterwards -- so a mon the catch
    # gate had just boxed could be withdrawn straight back and kept, with no
    # exploit required (rowe_parity.md §13.24). The PC is opened from a SCRIPT
    # whose special carries a waitstate, exactly like the egg hatch, so this is
    # the same splice pointed at a different tail: the sweep runs AFTER the
    # waitstate, i.e. once the storage UI has closed and the party is whatever
    # the player left it as.
    # ⚠️ This is ROWE's Cb2_ExitPSS semantics -- UNDO ON EXIT, not prevention --
    # and it deliberately does NOT reproduce ROWE's second guard
    # (IsRemovingLastAllowedPartyMon). See pc_hook.py's docstring.
    import pc_hook
    pc_text = struct.unpack_from("<I", data, pc_hook.PC_TEXT_PTR_OFF)[0]
    assert pc_text == pc_hook.PC_TEXT_PTR, (
        f"PC script's message pointer is {pc_text:#x}, expected "
        f"{pc_hook.PC_TEXT_PTR:#x} -- the PC access script has moved")
    pc_tail, pc_patches = pc_hook.build(PC_TAIL_ADDR, ACTIVATE_SWEEP)
    splice(PC_TAIL_ADDR, pc_tail, "PC-exit tail")
    for off, orig, repl in pc_patches:
        seg = bytes(data[off:off + len(orig)])
        assert seg == orig, (
            f"PC splice site {off + 0x08000000:#x} holds {seg.hex()}, "
            f"expected {orig.hex()} -- wrong ROM, or already patched")
        data[off:off + len(repl)] = repl
    print(f"PC-exit sweep: tail {len(pc_tail)} B @ {PC_TAIL_ADDR:#x}, "
          f"splice @ {pc_hook.SPLICE_ROM_ADDR:#x} -> callnative {ACTIVATE_SWEEP:#x}")


    # --- faster stat-change battle messages (user-approved 2026-09-01) ---
    #
    # Vanilla plays the stat-change animation, THEN prints the message, THEN
    # waits 64 frames. Printing first lets message and animation overlap, and
    # halving the wait removes the dead time after it. This is a pure battle
    # script DATA edit: the 15-byte window is rewritten IN PLACE, same length,
    # so every pointer into it still lands on the same command.
    #
    # Safety, measured 2026-09-02 (game_plans/rowe_parity.md 12.8 item 3):
    #   * `45 02 01 <gBattleAnimArgs>` occurs EXACTLY TWICE in this ROM -- these
    #     two sites -- so the byte pattern identifies them uniquely. The
    #     surrounding idiom `printfromtable <ptr>; waitmessage 0x0040` occurs
    #     242 times, which is what confirms the opcode decode: 0x13 is
    #     printfromtable, 0x12 is waitmessage <u16>, 0x45 is playanimation.
    #   * an UNALIGNED u32 scan of the whole ROM finds every reference to either
    #     window pointing at its FIRST byte. Nothing branches into the middle of
    #     what is being reordered.
    #   * the PRE-CHANGE bytes are asserted below -- against the real binary,
    #     not a synthetic tamper -- so a wrong ROM, a re-run over an already
    #     patched ROM, or a future ROM revision fails loudly instead of
    #     executing wrong opcodes mid-battle.
    #
    # Deliberately only these two sites. The same idiom appears hundreds of
    # times; widening it was never analysed and is not what was approved.
    CM_ANIM_ARGS = 0x02023FD4
    CM_BATTLE_MSG_SITES = (
        ("stat up",   0x081D6BD1, 0x083FE57C),
        ("stat down", 0x081D6C62, 0x083FE588),
    )
    CM_WAIT_OLD, CM_WAIT_NEW = 0x0040, 0x0020
    for _label, _rom_addr, _table in CM_BATTLE_MSG_SITES:
        _o = _rom_addr - 0x08000000
        _play = bytes([0x45, 0x02, 0x01]) + struct.pack("<I", CM_ANIM_ARGS)
        _prnt = bytes([0x13]) + struct.pack("<I", _table)
        _before = _play + _prnt + bytes([0x12]) + struct.pack("<H", CM_WAIT_OLD)
        _after = _prnt + _play + bytes([0x12]) + struct.pack("<H", CM_WAIT_NEW)
        assert len(_after) == len(_before) == 15
        _found = bytes(data[_o:_o + 15])
        assert _found == _before, (
            "battle message '%s' site %#010x: expected %s, found %s -- wrong "
            "ROM or already patched" % (_label, _rom_addr, _before.hex(),
                                        _found.hex()))
        data[_o:_o + 15] = _after
    print("faster battle messages: %d sites reordered, wait %d -> %d frames"
          % (len(CM_BATTLE_MSG_SITES), CM_WAIT_OLD, CM_WAIT_NEW))

    out_rom = BUILD / "radicalred_cm.gba"
    out_rom.write_bytes(data)
    print(f"wrote {out_rom} sha1={hashlib.sha1(data).hexdigest()}")

    # --- 4. BPS patch (flips supports IPS/BPS; BPS is the recommended format) ---
    flips = ROOT / "tools" / "bin" / "flips"
    bps = BUILD / "radicalred_cm.bps"
    r = subprocess.run([str(flips), "--create", "--bps", str(ROM_IN), str(out_rom), str(bps)],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if bps.exists():
        print(f"patch: {bps} ({bps.stat().st_size} bytes)")

    # summary of typed codes for the report
    print("\nSelection codes (type at the cheat-code NPC):")
    print("  " + ", ".join(aliases[i] for i, _ in selectable[:8]) + ", ...")
    print("Debug codes: " + ", ".join(c for c, _ in debug_codes))


if __name__ == "__main__":
    main()
