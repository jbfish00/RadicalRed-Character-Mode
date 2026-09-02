#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Radical Red v4.1.

Pipeline (all addresses CONFIRMED in docs/ROUTINE_MAP.md, pinned to rom.sha1):
  1. Compile src/character_mode.c (the GiveMonToPlayer gate shim) with
     arm-none-eabi-gcc, linked at SHIM_ADDR.
  2. Splice into a ROM copy:
       shim code            @ SHIM_ADDR    (0x08C80000)
       rosters_expanded.bin @ BITMAPS_ADDR (0x08C80100)
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
BITMAPS_ADDR = 0x08C80100
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
BL_SITE_LAND_MAIN   = 0x10C2FDA  # inside TryGenerateWildMon (primary)
BL_SITE_LAND_DOUBLE = 0x10C30CE  # inside TryGenerateWildMon (double battle)
BL_SITE_FISH_MAIN   = 0x10C3A94  # inside FishingWildEncounter (primary)
BL_SITE_FISH_DOUBLE = 0x10C3AD0  # inside FishingWildEncounter (double battle)

FLAG_CHARACTER_MODE = 0x18FE
VAR_CHARACTER_ID    = 0x51FD

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
                      + op_callnative(0) + op_loadword(0) + op_callstd(6)
                      + op_callnative(0) + op_release() + op_end())

    chain_addr = SCRIPT_ADDR
    handlers_addr = chain_addr + chain_size
    h_addrs = {}
    cur = handlers_addr
    for code, kind in debug_codes:
        h_addrs[code] = cur
        cur += H_OFF_SIZE if kind == "off" else H_GIVE_SIZE
    char_h_addrs = []
    for _ in selectable:
        char_h_addrs.append(cur)
        cur += H_CHAR_SIZE
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
        blob += op_callnative(SHOW_MUGSHOT)
        blob += op_loadword(str_addrs[f"msg:{j}"])
        blob += op_callstd(6)
        blob += op_callnative(HIDE_MUGSHOT)
        blob += op_release() + op_end()
    assert SCRIPT_ADDR + len(blob) == strings_addr
    blob += strings
    print(f"script extension: {len(blob)} bytes @ {SCRIPT_ADDR:#x} "
          f"({n_checks} codes: {len(debug_codes)} debug + {len(selectable)} "
          f"selectable characters; {len(hidden)} hidden)")

    # --- 3. splice + patch ---
    spliced = []

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
    splice(BITMAPS_ADDR, bitmaps, "bitmaps")
    splice(SCRIPT_ADDR, blob, "script")
    splice(WILD_SHIM_ADDR, wild_shim, "wild-encounter shim")
    splice(CM_SPRITE_SHIM_ADDR, sprite_shim, "mugshot renderer")
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
