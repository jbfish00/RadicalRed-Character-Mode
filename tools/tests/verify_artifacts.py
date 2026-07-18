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
  7. Trade gate wrapper decode + allow-list re-derivation.
  8. Wild-encounter override (Phase 7): all 4 BL sites decode to the wild
     shim now / CreateWildMon originally; wild_override.bin/_offsets.bin in
     ROM match the build artifacts; Red's re-derived family/stage table is
     well-formed and matches emit_wild_override.py's own sanity checks; and
     -- checked for EVERY character, not just Red -- no character's table
     contains any legendary/mythical species id at all.

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
TRADE_BG_PTR_OFF = 0x3B432C
TRADE_ORIG = 0x08164B03
TRADE_WRAPPER_ADDR = 0x08C8E000
TRADE_SPECIES = 848

# Wild-encounter override (Phase 7)
WILD_SHIM_ADDR = 0x08CE0000
WILD_OFFSETS_ADDR = 0x08CE0800
WILD_DATA_ADDR = 0x08CE0C00
WILD_BL_SITES = (0x10C2FDA, 0x10C30CE, 0x10C3A94, 0x10C3AD0)
CREATEWILDMON_ADDR = 0x090C292C

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
    woff = TRADE_WRAPPER_ADDR - 0x08000000
    wend = woff
    while not all(b == 0xFF for b in patched[wend:wend + 64]):
        wend += 64
    wild_data = (ROOT / "tools" / "character_mode" / "wild_override.bin").read_bytes()
    wild_offsets = (ROOT / "tools" / "character_mode" / "wild_override_offsets.bin").read_bytes()
    wsoff = WILD_SHIM_ADDR - 0x08000000
    wsend = wsoff
    while not all(b == 0xFF for b in patched[wsend:wsend + 64]):
        wsend += 64
    intended = [(SHIM_ADDR - 0x08000000, SHIM_ADDR - 0x08000000 + 0x100),
                (BITMAPS_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000 + len(bitmaps)),
                (soff, send),
                (woff, wend),
                (wsoff, wsend),
                (WILD_OFFSETS_ADDR - 0x08000000, WILD_OFFSETS_ADDR - 0x08000000 + len(wild_offsets)),
                (WILD_DATA_ADDR - 0x08000000, WILD_DATA_ADDR - 0x08000000 + len(wild_data)),
                *[(s, s + 4) for s in BL_SITES],
                *[(s, s + 4) for s in WILD_BL_SITES],
                (GOTO_OPERAND_OFF, GOTO_OPERAND_OFF + 4),
                (TRADE_BG_PTR_OFF, TRADE_BG_PTR_OFF + 4)]
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
    check(f"no stray modified bytes outside the {len(intended)} intended regions",
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
    # reverse charmap; several chars share a byte (e.g. ' ' and the ideographic
    # space both encode to 0x00) — prefer the ASCII one for round-trip checks
    cmap = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open("/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                b, ch = int(m.group(2), 16), m.group(1)
                if b not in cmap or (not cmap[b].isascii() and ch.isascii()):
                    cmap[b] = ch

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

    print("== 7. trade gate ==")
    check("trade BG script ptr originally -> live trade script",
          struct.unpack_from("<I", orig, TRADE_BG_PTR_OFF)[0] == TRADE_ORIG)
    check("trade BG script ptr retargeted to wrapper",
          struct.unpack_from("<I", patched, TRADE_BG_PTR_OFF)[0] == TRADE_WRAPPER_ADDR)
    # decode the wrapper: checkflag CM; goto_if 0 -> orig; compare var,0;
    # goto_if 1 -> orig; compare var,185; goto_if 4 -> orig; [per-allowing
    # character compare/goto_if pairs]; loadword msg; callstd 3; end
    w = TRADE_WRAPPER_ADDR - 0x08000000
    def u32p(o): return struct.unpack_from("<I", patched, o)[0]
    ok = (patched[w] == 0x2B and struct.unpack_from("<H", patched, w+1)[0] == FLAG_CM
          and patched[w+3] == 0x06 and patched[w+4] == 0 and u32p(w+5) == TRADE_ORIG
          and patched[w+9] == 0x21 and struct.unpack_from("<HH", patched, w+10) == (VAR_ID, 0)
          and patched[w+14] == 0x06 and patched[w+15] == 1 and u32p(w+16) == TRADE_ORIG
          and patched[w+20] == 0x21 and struct.unpack_from("<HH", patched, w+21) == (VAR_ID, 185)
          and patched[w+25] == 0x06 and patched[w+26] == 4 and u32p(w+27) == TRADE_ORIG)
    check("wrapper preamble decodes (flag/char-0/char-range passthroughs)", ok)
    p2 = w + 31
    n_allow = 0
    while patched[p2] == 0x21:
        var, idx = struct.unpack_from("<HH", patched, p2+1)
        good = (var == VAR_ID and 1 <= idx <= 184 and patched[p2+5] == 0x06
                and patched[p2+6] == 1 and u32p(p2+7) == TRADE_ORIG)
        if not good:
            break
        # the allowing character's bitmap must actually allow the species
        bmi = (idx-1)*STRIDE
        if not bitmaps[bmi + (TRADE_SPECIES >> 3)] & (1 << (TRADE_SPECIES & 7)):
            break
        n_allow += 1
        p2 += 11
    expected_allow = sum(1 for i in range(184)
                         if bitmaps[i*STRIDE + (TRADE_SPECIES >> 3)] & (1 << (TRADE_SPECIES & 7)))
    check(f"wrapper allow-list matches bitmaps ({expected_allow} characters)",
          n_allow == expected_allow)
    ok_tail = (patched[p2] == 0x0F and patched[p2+1] == 0
               and patched[p2+6] == 0x09 and patched[p2+7] == 3 and patched[p2+8] == 0x02)
    msg = ""
    if ok_tail:
        ma = u32p(p2+2) - 0x08000000
        raw = patched[ma:ma+80]
        msg = "".join(cmap.get(b, "?") for b in raw[:raw.find(0xFF)])
    check("wrapper tail: msgbox(sign) + end, message decodes",
          ok_tail and msg.startswith("Character Mode:"), repr(msg))

    print("== 8. wild-encounter override ==")
    for site in WILD_BL_SITES:
        tgt = decode_bl(patched[site:site + 4], 0x08000000 + site)
        check(f"wild BL at {site:#x} -> wild shim", tgt == WILD_SHIM_ADDR, f"decoded {tgt and hex(tgt)}")
        old = decode_bl(orig[site:site + 4], 0x08000000 + site)
        check(f"wild BL at {site:#x} originally -> CreateWildMon", old == CREATEWILDMON_ADDR,
              f"decoded {old and hex(old)}")
    check("wild shim starts with push {..,lr}",
          (struct.unpack_from("<H", patched, WILD_SHIM_ADDR - 0x08000000)[0] & 0xFF00) == 0xB500)
    off_o = WILD_OFFSETS_ADDR - 0x08000000
    off_d = WILD_DATA_ADDR - 0x08000000
    check("wild_override_offsets.bin in ROM == build artifact",
          patched[off_o:off_o + len(wild_offsets)] == wild_offsets)
    check("wild_override.bin in ROM == build artifact",
          patched[off_d:off_d + len(wild_data)] == wild_data)
    check("wild override offsets table has 184 entries", len(wild_offsets) == 184 * 4)

    # re-derive Red's family/stage table from the in-ROM bytes and cross-check
    # against the same 4 sanity facts emit_wild_override.py itself checks:
    # Pichu/Pikachu/Raichu/Alolan-Raichu present, Articuno (legendary) absent.
    red_idx = red  # index computed in section 5
    red_off = struct.unpack_from("<I", wild_offsets, red_idx * 4)[0]
    p3 = red_off
    n_fam = wild_data[p3]; p3 += 1
    red_species = set()
    fam_count_ok = n_fam > 0
    for _ in range(n_fam):
        n_st = wild_data[p3]; p3 += 1
        for _ in range(n_st):
            sid, lo, hi = struct.unpack_from("<HBB", wild_data, p3)
            p3 += 4
            red_species.add(sid)
            fam_count_ok = fam_count_ok and lo <= hi
    check("wild override: Red family table well-formed (lvlMin <= lvlMax throughout)", fam_count_ok)
    check("wild override: Red table includes Pichu/Pikachu/Raichu/Alolan-Raichu",
          {172, 25, 26, 1022} <= red_species)
    check("wild override: Red table excludes Articuno (legendary)", 144 not in red_species)
    # cross-character: NO character's table may include ANY legendary id at all
    # (excluded at the family level, not just Red's) — walk every table once.
    with open(ROOT / "tools" / "character_mode" / "rr_pokedex_donor" / "data.js") as f:
        import ast
        dex_species = ast.literal_eval(f.read())["species"]
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    from map_species import LEGENDARY_NAMES  # noqa: E402
    legendary_ids = {sid for sid, info in dex_species.items() if info["name"] in LEGENDARY_NAMES}
    bad_legendary = []
    for ci in range(184):
        o = struct.unpack_from("<I", wild_offsets, ci * 4)[0]
        pp = o
        nf = wild_data[pp]; pp += 1
        for _ in range(nf):
            ns = wild_data[pp]; pp += 1
            for _ in range(ns):
                sid = struct.unpack_from("<H", wild_data, pp)[0]
                pp += 4
                if sid in legendary_ids:
                    bad_legendary.append((ci, sid))
    check("wild override: no character's table contains any legendary/mythical species",
          not bad_legendary, f"{bad_legendary[:5]}")

    print(f"\n{'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
