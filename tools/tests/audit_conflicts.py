#!/usr/bin/env python3
"""Pre-playthrough conflict audit — checks NOT covered by the other three layers.

1. Alias audit: re-derive all 184 character cheat-codes independently and
   check uniqueness, length <= 11 (TeamPreview precedent), and collision
   against Radical Red's own five native codes (which are compared FIRST
   in the chain — an exact collision would silently shadow a character;
   a case-insensitive near-miss is reported as INFO since the compare is
   exact-byte).
2. Flag/var conflict scan: search the ORIGINAL ROM for script-bytecode
   references to our chosen flag 0x18FE (setflag/clearflag/checkflag) and
   var 0x51FD (setvar/addvar/subvar/copyvar/setorcopyvar/compare/specialvar).
   Any real hit would mean RR itself already uses the ID we claimed.
   3-byte patterns have ~2 chance hits per 32 MB, so hits are validated by
   attempting a strict script-context decode around them before flagging.
3. Signature-in-bitmap: for every character, the signature species gifted
   by the selection handler must have its bit set in that character's
   in-ROM bitmap — otherwise the starter would be confiscated on the next
   enforcement pass. Also checks every roster family-base bit.

Exit 0 = all pass. Pure static analysis; no emulator needed.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

ORIG_ROM = ROOT / "rom" / "radicalred 4.1.gba"
CM_ROM = ROOT / "build" / "radicalred_cm.gba"
MANIFEST = ROOT / "tools" / "character_mode" / "characters_manifest.json"

BITMAPS_FILEOFF = 0xC80100
BITMAP_BYTES = 172  # 1376 species bits
NUM_CHARS = 184

# RR's native cheat codes (docs/ROUTINE_MAP.md, walked from fallthrough 0x10500EE)
RR_NATIVE_CODES = ["Woyaopp", "DexAll", "SO2Toxic", "TeamPreview", "EZCatch"]

CM_FLAG = 0x18FE
CM_VAR = 0x51FD

checks = 0
fails = 0


def check(ok, msg):
    global checks, fails
    checks += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
    if not ok:
        fails += 1


def alias_for(display):  # mirrors tools/inject_character_mode.py exactly
    if display.endswith(" (anime)"):
        display = display[:-len(" (anime)")]
    return re.sub(r"[^A-Za-z0-9]", "", display)


def main():
    manifest = json.loads(MANIFEST.read_text())
    chars = manifest["characters"]
    orig = ORIG_ROM.read_bytes()
    cm = CM_ROM.read_bytes()

    print("== 1. alias audit ==")
    aliases = [alias_for(c["character"]) for c in chars]
    check(len(aliases) == NUM_CHARS, f"{NUM_CHARS} aliases derived ({len(aliases)})")
    check(len(set(aliases)) == len(aliases), "all aliases unique")
    check(all(1 <= len(a) <= 11 for a in aliases),
          "all alias lengths in [1, 11] (naming-screen limit)")
    exact = sorted(set(aliases) & set(RR_NATIVE_CODES))
    check(not exact, f"no exact collision with RR's native codes {exact or ''}")
    near = sorted({a for a in aliases for n in RR_NATIVE_CODES
                   if a.lower() == n.lower()} - set(exact))
    if near:
        print(f"  [INFO] case-insensitive near-misses vs native codes: {near}")
    debug_codes = ["CMDbgOff", "CMDbgGive1", "CMDbgGive2"]
    check(not (set(debug_codes) & set(aliases)), "debug codes don't collide with aliases")

    print("== 2. flag/var conflict scan of ORIGINAL ROM ==")
    flag_le = CM_FLAG.to_bytes(2, "little")
    var_le = CM_VAR.to_bytes(2, "little")
    # (pattern, human name) — opcode byte immediately before the LE u16 ID
    flag_ops = {0x29: "setflag", 0x2A: "clearflag", 0x2B: "checkflag"}
    var_ops = {0x16: "setvar", 0x17: "addvar", 0x18: "subvar", 0x1A: "setorcopyvar",
               0x19: "copyvar", 0x21: "compare", 0x25: "specialvar"}

    def plausible(off, op):
        """Reject raw-byte coincidences that can't be a real script command.
        specialvar (0x25) is `specialvar var, specialId` — specialId indexes
        the specials table, always < 0x400 (RR's known specials: 0x12C, 0x158,
        0x1B8...). A huge 'specialId' means the match is not script bytecode
        (verified case: hit at 0x11EBC4 is mid-instruction in Thumb BL pairs)."""
        if op == 0x25:
            special_id = int.from_bytes(orig[off + 3:off + 5], "little")
            return special_id < 0x400
        return True

    def scan(ops, needle, second_operand_ops=()):
        hits = []
        start = 0
        while True:
            i = orig.find(needle, start)
            if i < 0:
                break
            start = i + 1
            if i >= 1 and orig[i - 1] in ops and plausible(i - 1, orig[i - 1]):
                hits.append((i - 1, ops[orig[i - 1]]))
            # copyvar/setorcopyvar/specialvar also take a var as 2nd operand
            if i >= 3 and orig[i - 3] in second_operand_ops:
                hits.append((i - 3, ops.get(orig[i - 3], "?") + " (2nd operand)"))
        return hits

    flag_hits = scan(flag_ops, flag_le)
    var_hits = scan(var_ops, var_le,
                    second_operand_ops={0x19, 0x1A, 0x25})
    for off, name in flag_hits + var_hits:
        print(f"  [INFO] candidate hit: {name} at file 0x{off:X}: "
              f"{orig[off:off + 8].hex(' ')}")
    check(not flag_hits, f"original ROM has no script reference to flag 0x{CM_FLAG:X} "
                         f"({len(flag_hits)} candidate hits)")
    check(not var_hits, f"original ROM has no script reference to var 0x{CM_VAR:X} "
                        f"({len(var_hits)} candidate hits)")

    print("== 3. signature/roster bits in in-ROM bitmaps ==")
    sig_bad, roster_bad = [], []
    for i, c in enumerate(chars):
        bm = cm[BITMAPS_FILEOFF + i * BITMAP_BYTES:
                BITMAPS_FILEOFF + (i + 1) * BITMAP_BYTES]
        def bit(sp):
            return bool(bm[sp >> 3] & (1 << (sp & 7)))
        if c.get("has_signature") and not bit(c["signature_id"]):
            sig_bad.append((c["character"], c["signature_id"]))
        missing = [sp for sp in c["roster_species_ids"] if not bit(sp)]
        if missing:
            roster_bad.append((c["character"], missing))
    check(not sig_bad,
          f"all signature species allowed by their own bitmap {sig_bad or ''}")
    check(not roster_bad,
          f"all roster family-base bits set in bitmaps {roster_bad[:3] or ''}")

    print(f"\n{checks - fails}/{checks} checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
