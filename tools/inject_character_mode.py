#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Radical Red v4.1.

Pipeline (all addresses CONFIRMED in docs/ROUTINE_MAP.md, pinned to rom.sha1):
  1. Compile src/character_mode.c (the GiveMonToPlayer gate shim) with
     arm-none-eabi-gcc, linked at SHIM_ADDR.
  2. Splice into a ROM copy:
       shim code            @ SHIM_ADDR    (0x08B71D10)
       rosters_expanded.bin @ BITMAPS_ADDR (0x08B72000)
       selection script ext @ SCRIPT_ADDR  (0x08B7A000)
     — all inside the confirmed 1.63 MiB free block at 0xB71D04. The shim
     MUST stay in this block: Thumb BL range is ±4 MB from the two patch
     sites (~0x0907xxxx), and this is the only big free block in range.
  3. Patch:
       - BL at 0x107DD84 (atkF0_givecaughtmon)  -> BL shim
       - BL at 0x10777CE (ScriptGiveMon)        -> BL shim
       - goto operand at 0x10500EF (cheat-code no-match fallthrough)
         -> selection script chain (chain's own fallthrough continues to
            the original "Invalid code." handler at 0x09050811)
  4. Verify expected original bytes before every patch (refuses to run on a
     mismatched ROM), write build/radicalred_cm.gba + build/radicalred_cm.ups.

The selection UI rides RR's own cheat-code entry system: the player talks
to the cheat-code NPC and types a character's name (non-alphanumerics
stripped: "Lt. Surge" -> "LtSurge"). Matching sets VAR_CHARACTER_ID +
FLAG_CHARACTER_MODE and delivers the character's signature mon at Lv 5.
Debug codes (mirroring ROWE's in-game debug-menu test method):
  CMDbgOff    - turn Character Mode off
  CMDbgGive1  - givepokemon Pikachu Lv5  (allowed for Red -> stays in party)
  CMDbgGive2  - givepokemon Meowth Lv5   (off-roster for Red -> sent to PC)
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
CHARMAP = Path("/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt")

# --- confirmed layout constants (docs/ROUTINE_MAP.md) ---
# All three payloads live in the confirmed 1.63 MiB free block
# (0xB71D04-0xD004D7), placed in its upper region because the shim must be
# within Thumb BL range (+/-4 MB) of both patch sites (~0x0907xxxx): the
# reachable window is [0xC7DD88, 0x14777D0), and this block's tail
# [0xC7DD88, 0xD004D7) is comfortably the largest free run inside it.
SHIM_ADDR    = 0x08C80000
BITMAPS_ADDR = 0x08C80100
SCRIPT_ADDR  = 0x08C88000
FREE_BLOCK_END = 0xD004D7  # end of the 1.63MiB free run

BL_SITE_CATCH = 0x107DD84   # inside atkF0_givecaughtmon
BL_SITE_GIFT  = 0x10777CE   # inside ScriptGiveMon
GIVEMON_ADDR  = 0x0907D790  # current BL target at both sites (no Thumb bit)

GOTO_OPERAND_OFF = 0x10500EF          # operand of `goto 0x09050811`
INVALID_CODE_HANDLER = 0x09050811

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
    assert len(chars) == 184, len(chars)
    bitmaps = (HERE / "character_mode" / "rosters_expanded.bin").read_bytes()
    assert len(bitmaps) == 184 * 172, len(bitmaps)

    # --- 1. compile shim ---
    BUILD.mkdir(exist_ok=True)
    obj = BUILD / "character_mode.o"
    elf = BUILD / "character_mode.elf"
    binf = BUILD / "character_mode.bin"
    subprocess.run(["arm-none-eabi-gcc", "-c", "-mthumb", "-mcpu=arm7tdmi",
                    "-mtune=arm7tdmi", "-O2", "-ffreestanding", "-fno-builtin",
                    f"-DBITMAPS_ADDR={BITMAPS_ADDR:#x}",
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

    CHECK_SIZE = len(op_loadword(0) + op_special(0x12D) + op_compare(0x800D, 0) + op_goto_if(1, 0))
    assert CHECK_SIZE == 20
    n_checks = len(debug_codes) + len(chars)
    chain_size = n_checks * CHECK_SIZE + len(op_goto(0))

    # handlers
    H_OFF_SIZE  = len(op_clearflag(0) + op_setvar(0, 0) + op_loadword(0) + op_callstd(6) + op_release() + op_end())
    H_GIVE_SIZE = len(op_givepokemon(0, 5) + op_loadword(0) + op_callstd(6) + op_release() + op_end())
    H_CHAR_SIZE = len(op_setvar(0, 0) + op_setflag(0) + op_givepokemon(0, 5)
                      + op_loadword(0) + op_callstd(6) + op_release() + op_end())

    chain_addr = SCRIPT_ADDR
    handlers_addr = chain_addr + chain_size
    h_addrs = {}
    cur = handlers_addr
    for code, kind in debug_codes:
        h_addrs[code] = cur
        cur += H_OFF_SIZE if kind == "off" else H_GIVE_SIZE
    char_h_addrs = []
    for _ in chars:
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
    add_str("msg:give_bad", "Debug: tried to give Meowth.")
    for i, (c, a) in enumerate(zip(chars, aliases)):
        add_str(f"alias:{i}", a)
        disp = c["character"]
        if disp.endswith(" (anime)"):
            disp = disp[:-len(" (anime)")]
        add_str(f"msg:{i}", f"Character Mode:\nyou are now {disp}!")

    # emit chain
    blob = bytearray()
    for code, kind in debug_codes:
        blob += op_loadword(str_addrs["code:" + code])
        blob += op_special(0x12D)
        blob += op_compare(0x800D, 0)
        blob += op_goto_if(1, h_addrs[code])
    for i in range(len(chars)):
        blob += op_loadword(str_addrs[f"alias:{i}"])
        blob += op_special(0x12D)
        blob += op_compare(0x800D, 0)
        blob += op_goto_if(1, char_h_addrs[i])
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
            species = 25 if kind == "give_ok" else 52  # Pikachu / Meowth
            blob += op_givepokemon(species, 5)
            blob += op_loadword(str_addrs["msg:" + kind])
        blob += op_callstd(6) + op_release() + op_end()
    for i, c in enumerate(chars):
        assert SCRIPT_ADDR + len(blob) == char_h_addrs[i]
        sig = c["roster_species_ids"][0]
        blob += op_setvar(VAR_CHARACTER_ID, i + 1)
        blob += op_setflag(FLAG_CHARACTER_MODE)
        blob += op_givepokemon(sig, 5)
        blob += op_loadword(str_addrs[f"msg:{i}"])
        blob += op_callstd(6) + op_release() + op_end()
    assert SCRIPT_ADDR + len(blob) == strings_addr
    blob += strings
    print(f"script extension: {len(blob)} bytes @ {SCRIPT_ADDR:#x} "
          f"({n_checks} codes: {len(debug_codes)} debug + {len(chars)} characters)")

    # --- 3. splice + patch ---
    def splice(rom_addr, payload, label):
        off = rom_addr - 0x08000000
        assert off + len(payload) <= FREE_BLOCK_END, f"{label} overruns free block"
        seg = data[off:off + len(payload)]
        assert all(b == 0xFF for b in seg), f"{label}: target not 0xFF-free at {rom_addr:#x}"
        data[off:off + len(payload)] = payload

    splice(SHIM_ADDR, shim, "shim")
    splice(BITMAPS_ADDR, bitmaps, "bitmaps")
    splice(SCRIPT_ADDR, blob, "script")

    # BL retargets (verify current bytes first)
    for site in (BL_SITE_CATCH, BL_SITE_GIFT):
        cur_bl = bytes(data[site:site + 4])
        expect = thumb_bl(0x08000000 + site, GIVEMON_ADDR)
        assert cur_bl == expect, (f"BL site {site:#x} bytes {cur_bl.hex()} != expected "
                                  f"BL GiveMonToPlayer {expect.hex()} — wrong ROM or already patched")
        data[site:site + 4] = thumb_bl(0x08000000 + site, SHIM_ADDR)

    # goto retarget
    cur_goto = struct.unpack_from("<I", data, GOTO_OPERAND_OFF)[0]
    assert cur_goto == INVALID_CODE_HANDLER, f"goto operand is {cur_goto:#x}, expected {INVALID_CODE_HANDLER:#x}"
    struct.pack_into("<I", data, GOTO_OPERAND_OFF, SCRIPT_ADDR)

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
    print("  " + ", ".join(aliases[:8]) + ", ...")
    print("Debug codes: " + ", ".join(c for c, _ in debug_codes))


if __name__ == "__main__":
    main()
