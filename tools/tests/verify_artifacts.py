#!/usr/bin/env python3
"""Independent static verification of the built Character Mode artifacts.

Deliberately does NOT reuse tools/inject_character_mode.py's build-time
assertions — it re-derives everything from the finished artifacts, so a bug
in the injector's own bookkeeping can't hide itself:

  1. rom/ original matches rom.sha1 (all pinned addresses valid).
  2. BPS round-trip: flips-apply build/radicalred_cm.bps onto a fresh copy
     of the original -> byte-identical to build/radicalred_cm.gba.
  3. Patched ROM differs from the original in EXACTLY the 5 intended
     regions (shim, bitmaps, script blob, 2 BLs, 1 goto operand) — nothing
     else moved.
  4. The two patched BL instructions decode (independent decoder) to the
     shim entry; the shim's first instruction is a valid push.
  5. Bitmaps in-ROM == rosters_expanded.bin, and Red's bitmap spot-checks
     (allow 25/26/172/1022, reject 0/52) hold in the ROM copy itself.
  6. Script chain walk: from the retargeted goto operand, decode all 187
     check blocks (3 debug + 184 characters) instruction-by-instruction,
     following every pointer: each alias string is valid text ending 0xFF,
     each handler decodes to the expected opcode sequence with the right
     var/flag ids, givepokemon species == that character's signature
     (roster[0] in characters_manifest.json), and the chain tail gotos the
     original "Invalid code." handler.

Usage: verify_artifacts.py   (exit 0 = all pass)
"""
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

ROM_IN = ROOT / "rom" / "radicalred 4.1.gba"
ROM_OUT = ROOT / "build" / "radicalred_cm.gba"
BPS = ROOT / "build" / "radicalred_cm.bps"
FLIPS = ROOT / "tools" / "bin" / "flips"

ROM_SHA1 = "964f951a0fdaf209e4ea1344883ef0d557bb3a80"
SHIM_ADDR = 0x08C80000
BITMAPS_ADDR = 0x08C80100
SCRIPT_ADDR = 0x08C88000
BL_SITES = (0x107DD84, 0x10777CE)
GOTO_OPERAND_OFF = 0x10500EF
INVALID_CODE_HANDLER = 0x09050811
FLAG_CM = 0x18FE
VAR_ID = 0x51FD
STRIDE = 172

failures = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def decode_bl(halfwords_bytes, site_rom_addr):
    hw1, hw2 = struct.unpack("<HH", halfwords_bytes)
    if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xF800) != 0xF800:
        return None
    off = ((hw1 & 0x7FF) << 11) | (hw2 & 0x7FF)
    if off & 0x200000:
        off -= 0x400000
    return site_rom_addr + 4 + (off << 1)


def main():
    orig = ROM_IN.read_bytes()
    patched = ROM_OUT.read_bytes()

    print("== 1. baseline ==")
    check("original ROM sha1 pinned", hashlib.sha1(orig).hexdigest() == ROM_SHA1)
    check("patched ROM same size as original", len(patched) == len(orig))

    print("== 2. BPS round-trip ==")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "roundtrip.gba"
        r = subprocess.run([str(FLIPS), "--apply", str(BPS), str(ROM_IN), str(out)],
                           capture_output=True, text=True)
        applied = out.read_bytes() if out.exists() else b""
    check("flips applies patch cleanly", b"" != applied, r.stdout + r.stderr)
    check("round-trip byte-identical to built ROM", applied == patched)

    print("== 3. diff confined to intended regions ==")
    shim_len = next(i for i in range(0x100) if all(
        b == 0xFF for b in patched[SHIM_ADDR - 0x08000000 + i:SHIM_ADDR - 0x08000000 + 0x100]))
    bitmaps = (ROOT / "tools" / "character_mode" / "rosters_expanded.bin").read_bytes()
    # script blob length: scan forward from SCRIPT_ADDR to the next 0xFF run
    soff = SCRIPT_ADDR - 0x08000000
    send = soff
    while not all(b == 0xFF for b in patched[send:send + 64]):
        send += 64
    intended = [(SHIM_ADDR - 0x08000000, SHIM_ADDR - 0x08000000 + 0x100),
                (BITMAPS_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000 + len(bitmaps)),
                (soff, send),
                *[(s, s + 4) for s in BL_SITES],
                (GOTO_OPERAND_OFF, GOTO_OPERAND_OFF + 4)]
    stray = []
    i = 0
    n = len(orig)
    while i < n:
        if orig[i] != patched[i]:
            if not any(a <= i < b for a, b in intended):
                stray.append(i)
                if len(stray) > 5:
                    break
            j = i + 1
            while j < n and orig[j] != patched[j]:
                j += 1
            i = j
        else:
            i += 1
    check("no stray modified bytes outside the 6 intended regions",
          not stray, f"first strays at {[hex(x) for x in stray]}")

    print("== 4. BL patches ==")
    for site in BL_SITES:
        tgt = decode_bl(patched[site:site + 4], 0x08000000 + site)
        check(f"BL at {site:#x} -> shim", tgt == SHIM_ADDR, f"decoded {tgt and hex(tgt)}")
        old = decode_bl(orig[site:site + 4], 0x08000000 + site)
        check(f"BL at {site:#x} originally -> GiveMonToPlayer", old == 0x0907D790,
              f"decoded {old and hex(old)}")
    check("shim starts with push {..,lr}",
          (struct.unpack_from("<H", patched, SHIM_ADDR - 0x08000000)[0] & 0xFF00) == 0xB500)

    print("== 5. bitmaps ==")
    off = BITMAPS_ADDR - 0x08000000
    check("bitmaps in ROM == rosters_expanded.bin",
          patched[off:off + len(bitmaps)] == bitmaps)
    with open(ROOT / "tools" / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = [c for c in manifest["characters"] if "roster_species_ids" in c]
    check("184 characters in manifest", len(chars) == 184)
    red = next(i for i, c in enumerate(chars) if c["character"] == "Red")
    bm = patched[off + red * STRIDE: off + (red + 1) * STRIDE]
    def has(s): return bool(bm[s >> 3] & (1 << (s & 7)))
    check("Red bitmap (in ROM): allows 25/26/172/1022, rejects 0/52",
          has(25) and has(26) and has(172) and has(1022) and not has(0) and not has(52))

    print("== 6. script chain walk ==")
    goto_tgt = struct.unpack_from("<I", patched, GOTO_OPERAND_OFF)[0]
    check("cheat fallthrough goto retargeted to chain", goto_tgt == SCRIPT_ADDR)
    check("original goto operand was Invalid-code handler",
          struct.unpack_from("<I", orig, GOTO_OPERAND_OFF)[0] == INVALID_CODE_HANDLER)

    def rd(addr, ln):
        return patched[addr - 0x08000000: addr - 0x08000000 + ln]

    def read_text(addr, maxlen=64):
        raw = rd(addr, maxlen)
        end = raw.find(0xFF)
        return raw[:end] if end >= 0 else None

    # load ROWE charmap to decode alias strings back to ASCII
    cmap = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open("/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                cmap[int(m.group(2), 16)] = m.group(1)

    def alias_for(display):
        if display.endswith(" (anime)"):
            display = display[:-len(" (anime)")]
        return re.sub(r"[^A-Za-z0-9]", "", display)

    p = SCRIPT_ADDR
    checks_parsed = []          # (string_addr, handler_addr)
    chain_ok = True
    for i in range(187):
        blk = rd(p, 20)
        if not (blk[0] == 0x0F and blk[1] == 0x00 and blk[6] == 0x25
                and struct.unpack_from("<H", blk, 7)[0] == 0x12D
                and blk[9] == 0x21
                and struct.unpack_from("<HH", blk, 10) == (0x800D, 0)
                and blk[14] == 0x06 and blk[15] == 1):
            chain_ok = False
            check(f"check block {i} decodes", False, f"@{p:#x}: {blk.hex()}")
            break
        checks_parsed.append((struct.unpack_from("<I", blk, 2)[0],
                              struct.unpack_from("<I", blk, 16)[0]))
        p += 20
    check("all 187 check blocks decode (loadword/special 12D/compare/goto_if)",
          chain_ok and len(checks_parsed) == 187)
    tail = rd(p, 5)
    check("chain tail = goto Invalid-code handler",
          tail[0] == 0x05 and struct.unpack_from("<I", tail, 1)[0] == INVALID_CODE_HANDLER)

    if chain_ok and len(checks_parsed) == 187:
        # debug code strings
        dbg_names = ["CMDbgOff", "CMDbgGive1", "CMDbgGive2"]
        for i, name in enumerate(dbg_names):
            raw = read_text(checks_parsed[i][0])
            decoded = "".join(cmap.get(b, "?") for b in raw) if raw is not None else None
            check(f"debug code {i} string == {name!r}", decoded == name, repr(decoded))

        # character aliases + handlers
        bad_alias = bad_handler = 0
        for i, c in enumerate(chars):
            saddr, haddr = checks_parsed[3 + i]
            raw = read_text(saddr)
            decoded = "".join(cmap.get(b, "?") for b in raw) if raw is not None else None
            if decoded != alias_for(c["character"]):
                bad_alias += 1
                if bad_alias <= 3:
                    print(f"    alias mismatch [{i}] {c['character']}: {decoded!r}")
                continue
            h = rd(haddr, 30)
            ok = (h[0] == 0x16 and struct.unpack_from("<HH", h, 1) == (VAR_ID, i + 1)
                  and h[5] == 0x29 and struct.unpack_from("<H", h, 6)[0] == FLAG_CM
                  and h[8] == 0x79
                  and struct.unpack_from("<H", h, 9)[0] == c["roster_species_ids"][0]
                  and h[11] == 5      # level
                  and h[23] == 0x0F   # loadword msg
                  and h[29] == 0x09)  # callstd
            if not ok:
                bad_handler += 1
                if bad_handler <= 3:
                    print(f"    handler mismatch [{i}] {c['character']} @{haddr:#x}: {h.hex()}")
        check("all 184 alias strings decode to expected names", bad_alias == 0,
              f"{bad_alias} mismatches")
        check("all 184 handlers: setvar id, setflag, givepokemon(signature, L5), msgbox",
              bad_handler == 0, f"{bad_handler} mismatches")

        # debug handlers
        h = rd(checks_parsed[0][1], 12)
        check("CMDbgOff handler: clearflag CM + setvar 0",
              h[0] == 0x2A and struct.unpack_from("<H", h, 1)[0] == FLAG_CM
              and h[3] == 0x16 and struct.unpack_from("<HH", h, 4) == (VAR_ID, 0))
        for i, species in ((1, 25), (2, 52)):
            h = rd(checks_parsed[i][1], 12)
            check(f"CMDbg{'Give1' if i == 1 else 'Give2'} handler: givepokemon {species} L5",
                  h[0] == 0x79 and struct.unpack_from("<H", h, 1)[0] == species and h[3] == 5)

    print(f"\n{'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
