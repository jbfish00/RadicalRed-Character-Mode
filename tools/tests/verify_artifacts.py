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
  6. Script chain walk: from the retargeted goto operand, decode all 202
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
import os
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_tally  # noqa: E402

# faster stat-change battle messages -- (label, script address, string table)
BATTLE_MSG_SITES = (
    ("stat up",   0x081D6BD1, 0x083FE57C),
    ("stat down", 0x081D6C62, 0x083FE588),
)

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

ROM_IN = ROOT / "rom" / "radicalred 4.1.gba"
ROM_OUT = ROOT / "build" / "radicalred_cm.gba"
BPS = ROOT / "build" / "radicalred_cm.bps"
FLIPS = ROOT / "tools" / "bin" / "flips"

ROM_SHA1 = "964f951a0fdaf209e4ea1344883ef0d557bb3a80"
# Character count is derived, not hardcoded: every roster change used to mean
# hunting scattered literals (209 -> 210 for Volo, 2026-07-25). Read it from the
# manifest so the checks below track the build automatically.
_MANIFEST = json.loads((HERE.parent / "character_mode" /
        "characters_manifest.json").read_text())
NUM_CHARS = len(_MANIFEST["characters"])
# Selectable != enforced. Characters below the six-fully-evolved threshold carry
# flags bit1 and get NO check block in the alias chain, so the chain is shorter
# than the table. Everything the ROM indexes by character id (bitmaps, wild
# tables, sprite pointers, the trade wrapper's range guard) still uses NUM_CHARS.
NUM_SELECTABLE = sum(1 for c in _MANIFEST["characters"] if not c.get("hidden"))
SHIM_ADDR = 0x08C80000
# 2026-09-02: was 0x08C80100. The shim outgrew its 256-byte slot when the
# activation party sweep landed, so the bitmaps moved up to 0x400.
BITMAPS_ADDR = 0x08C80400
SCRIPT_ADDR = 0x08C90000  # keep in sync with inject_character_mode.py (2026-07-23 bitmap-overflow move)
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
WILD_LEG_OFFSETS_ADDR = 0x08CEA000  # keep in sync with inject_character_mode.py
WILD_LEG_DATA_ADDR = 0x08CEA400
CM_SPRITE_PTRS_ADDR = 0x08952000   # keep in sync with inject_character_mode.py
CM_SPRITE_BLOBS_ADDR = 0x08952800
CM_SPRITE_SHIM_ADDR = 0x08980000   # mugshot renderer (src/character_sprite.c)
WILD_BL_SITES = (0x10C2FDA, 0x10C30CE, 0x10C3A94, 0x10C3AD0)
CREATEWILDMON_ADDR = 0x090C292C

failures = []
checks_run = 0

# How many checks this layer must run. A deliberate LITERAL, never a total
# recomputed from the data the checks iterate: such a total drifts in lockstep
# with what it is meant to pin and therefore cannot fail. Bump it in the same
# commit that adds or removes a check. See tools/tests/cm_tally.py.
EXPECT_CHECKS = 99   # +1: the activation party sweep (2026-09-02)


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
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


def lz77_decode(buf, off):
    """Independent LZ77 decoder -- deliberately not imported from png_to_gba.py,
    so a bug there cannot make its own output verify as correct."""
    assert buf[off] == 0x10, "no LZ77 header"
    size = buf[off + 1] | (buf[off + 2] << 8) | (buf[off + 3] << 16)
    out = bytearray()
    pos = off + 4
    while len(out) < size:
        flags = buf[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = buf[pos], buf[pos + 1]; pos += 2
                cnt = (b1 >> 4) + 3
                disp = (((b1 & 0xF) << 8) | b2) + 1
                for _ in range(cnt):
                    out.append(out[-disp])
            else:
                out.append(buf[pos]); pos += 1
    return bytes(out[:size])

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
    # Measured, not capped at 0x100: the shim outgrew that on 2026-09-02 and the
    # old generator simply raised StopIteration when it did.
    _so = SHIM_ADDR - 0x08000000
    shim_len = 0
    for _i in range(0, BITMAPS_ADDR - SHIM_ADDR, 4):
        if not all(b == 0xFF for b in patched[_so + _i:_so + _i + 4]):
            shim_len = _i + 4
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
    leg_data = (ROOT / "tools" / "character_mode" / "wild_legendary.bin").read_bytes()
    leg_offsets = (ROOT / "tools" / "character_mode" / "wild_legendary_offsets.bin").read_bytes()
    # Phase 3 character sprites (2026-07-25)
    spr_blobs = (ROOT / "tools" / "character_mode" / "cm_sprite_blobs.bin").read_bytes()
    spr_offs = (ROOT / "tools" / "character_mode" / "cm_sprite_offsets.bin").read_bytes()
    spr_ptrs_expected = bytearray()
    for i in range(len(spr_offs) // 8):
        g, pl = struct.unpack_from("<II", spr_offs, i * 8)
        spr_ptrs_expected += (struct.pack("<II", 0, 0) if g == 0xFFFFFFFF else
                              struct.pack("<II", CM_SPRITE_BLOBS_ADDR + g,
                                                 CM_SPRITE_BLOBS_ADDR + pl))

    wsoff = WILD_SHIM_ADDR - 0x08000000
    wsend = wsoff
    while not all(b == 0xFF for b in patched[wsend:wsend + 64]):
        wsend += 64
    msoff = CM_SPRITE_SHIM_ADDR - 0x08000000
    msend = msoff
    while not all(b == 0xFF for b in patched[msend:msend + 64]):
        msend += 64
    intended = [(SHIM_ADDR - 0x08000000, SHIM_ADDR - 0x08000000 + shim_len),
                (BITMAPS_ADDR - 0x08000000, BITMAPS_ADDR - 0x08000000 + len(bitmaps)),
                (soff, send),
                (woff, wend),
                (wsoff, wsend),
                (msoff, msend),
                (WILD_OFFSETS_ADDR - 0x08000000, WILD_OFFSETS_ADDR - 0x08000000 + len(wild_offsets)),
                (WILD_DATA_ADDR - 0x08000000, WILD_DATA_ADDR - 0x08000000 + len(wild_data)),
                # Registering a new blob here is not optional bookkeeping: an
                # unregistered one fails as "stray bytes in diff containment",
                # which reads like a corrupted build rather than a missing entry.
                (WILD_LEG_OFFSETS_ADDR - 0x08000000,
                 WILD_LEG_OFFSETS_ADDR - 0x08000000 + len(leg_offsets)),
                (WILD_LEG_DATA_ADDR - 0x08000000,
                 WILD_LEG_DATA_ADDR - 0x08000000 + len(leg_data)),
                (CM_SPRITE_PTRS_ADDR - 0x08000000,
                 CM_SPRITE_PTRS_ADDR - 0x08000000 + len(spr_ptrs_expected)),
                (CM_SPRITE_BLOBS_ADDR - 0x08000000,
                 CM_SPRITE_BLOBS_ADDR - 0x08000000 + len(spr_blobs)),
                *[(s, s + 4) for s in BL_SITES],
                *[(s, s + 4) for s in WILD_BL_SITES],
                (GOTO_OPERAND_OFF, GOTO_OPERAND_OFF + 4),
                (TRADE_BG_PTR_OFF, TRADE_BG_PTR_OFF + 4),
                # encounter marker: its shim and the per-character intro
                # strings share one free run low in the ROM, plus the single BL
                # inside the battle-message code that it retargets.
                (0x378CA8, 0x379000 + 238 * 64),
                (0x0D77DE, 0x0D77DE + 4),
                # faster stat-change battle messages: two 15-byte battle-script
                # windows reordered in place (same length, so no pointer moves)
                *[(a - 0x08000000, a - 0x08000000 + 15)
                  for _l, a, _t in BATTLE_MSG_SITES]]
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

    print("== 3b. faster stat-change battle messages ==")
    # Pinned in BOTH directions on purpose. Checking only the patched bytes
    # would pass just as happily if the base ROM had always been in the new
    # order, which would mean the injector was doing nothing.
    for _label, _a, _table in BATTLE_MSG_SITES:
        _o = _a - 0x08000000
        _play = bytes([0x45, 0x02, 0x01]) + struct.pack("<I", 0x02023FD4)
        _prnt = bytes([0x13]) + struct.pack("<I", _table)
        _vanilla = _play + _prnt + bytes([0x12]) + struct.pack("<H", 0x0040)
        _fast = _prnt + _play + bytes([0x12]) + struct.pack("<H", 0x0020)
        check(f"base ROM '{_label}' still has the vanilla order + wait 64",
              bytes(orig[_o:_o + 15]) == _vanilla,
              f"found {bytes(orig[_o:_o + 15]).hex()}")
        check(f"built ROM '{_label}' prints first, then animates, wait 32",
              bytes(patched[_o:_o + 15]) == _fast,
              f"found {bytes(patched[_o:_o + 15]).hex()}")

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
    check(f"{NUM_CHARS} characters in manifest", len(chars) == NUM_CHARS)
    red = next(i for i, c in enumerate(chars) if c["character"] == "Red")
    bm = patched[off + red * STRIDE: off + (red + 1) * STRIDE]
    def has(s): return bool(bm[s >> 3] & (1 << (s & 7)))
    check("Red bitmap (in ROM): allows 25/26/172/1022, rejects 0/27",
          # 52 (Meowth) became a Red roster member on 2026-07-23 (Persian is in
          # the curated research), so the negative fixture moved to 27
          # (Sandshrew, genuinely off-roster).
          has(25) and has(26) and has(172) and has(1022) and not has(0) and not has(27))

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
    with open(_resolve_charmap(), encoding="utf-8") as f:
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
    for i in range(NUM_SELECTABLE + 3):  # 3 debug codes + every SELECTABLE character
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
    check(f"all {NUM_SELECTABLE + 3} check blocks decode (loadword/special 12D/compare/goto_if)",
          chain_ok and len(checks_parsed) == NUM_SELECTABLE + 3)
    # The chain must END here. If a hidden character's block were still emitted,
    # the loop above would simply stop early and every check would still pass --
    # so prove the very next block is NOT another check.
    nxt = rd(p, 20)
    check("no extra check blocks past the last selectable character",
          not (nxt[0] == 0x0F and nxt[6] == 0x25
               and struct.unpack_from("<H", nxt, 7)[0] == 0x12D),
          f"@{p:#x}: {nxt[:10].hex()}")
    tail = rd(p, 5)
    check("chain tail = goto Invalid-code handler",
          tail[0] == 0x05 and struct.unpack_from("<I", tail, 1)[0] == INVALID_CODE_HANDLER)

    # Derived, never hardcoded: this was literally `== 202` (the 199-character
    # era), so from the moment the roster grew to 210 this entire block — debug
    # strings, every alias round-trip, every handler decode — was silently
    # skipped while the suite still reported green. Same trap the count-derivation
    # elsewhere in this file exists to avoid; it just failed by omission here
    # rather than by a wrong-looking error.
    if chain_ok and len(checks_parsed) == NUM_SELECTABLE + 3:
        # debug code strings
        dbg_names = ["CMDbgOff", "CMDbgGive1", "CMDbgGive2"]
        for i, name in enumerate(dbg_names):
            raw = read_text(checks_parsed[i][0])
            decoded = "".join(cmap.get(b, "?") for b in raw) if raw is not None else None
            check(f"debug code {i} string == {name!r}", decoded == name, repr(decoded))

        # character aliases + handlers
        # The chain carries only SELECTABLE characters, in table order, but the
        # setvar operand below must still be the TABLE index -- that is what a
        # save stores. Zipping the two together is the whole point of this walk:
        # a compacted index here would silently select the wrong character.
        selectable = [(i, c) for i, c in enumerate(chars) if not c.get("hidden")]
        hidden_chars = [(i, c) for i, c in enumerate(chars) if c.get("hidden")]
        bad_alias = bad_handler = 0
        show_ops, hide_ops, sweep_ops = set(), set(), set()
        chain_aliases = set()
        for j, (i, c) in enumerate(selectable):
            saddr, haddr = checks_parsed[3 + j]
            raw = read_text(saddr)
            decoded = "".join(cmap.get(b, "?") for b in raw) if raw is not None else None
            if decoded is not None:
                chain_aliases.add(decoded)
            if decoded != alias_for(c["character"]):
                bad_alias += 1
                if bad_alias <= 3:
                    print(f"    alias mismatch [slot {j} / table {i}] "
                          f"{c['character']}: {decoded!r}")
                continue
            # setvar(5) setflag(3) givepokemon(15) callnative(5) callnative(5)
            # loadword(6) callstd(2) callnative(5) release(1) end(1) = 48 bytes
            # The FIRST callnative is the activation party sweep, and its
            # position is the point: it must come after givepokemon. Run before
            # it, a party holding only an off-roster mon hits the never-empty
            # rule and nothing is boxed -- a silent no-op. Decoding positionally
            # is what makes a reordering edit fail here.
            h = rd(haddr, 48)
            ok = (h[0] == 0x16 and struct.unpack_from("<HH", h, 1) == (VAR_ID, i + 1)
                  and h[5] == 0x29 and struct.unpack_from("<H", h, 6)[0] == FLAG_CM
                  and h[8] == 0x79
                  and struct.unpack_from("<H", h, 9)[0] == c["roster_species_ids"][0]
                  and h[11] == 5      # level
                  and h[23] == 0x23   # callnative CM_SweepPartyToPC (AFTER the give)
                  and h[28] == 0x23   # callnative CM_ShowCharacterMugshot
                  and h[33] == 0x0F   # loadword msg
                  and h[39] == 0x09   # callstd (blocks until the box is dismissed)
                  and h[41] == 0x23   # callnative CM_HideCharacterMugshot
                  and h[46] == 0x6C   # release
                  and h[47] == 0x02)  # end
            if ok:
                sweep_ops.add(struct.unpack_from("<I", h, 24)[0])
                show_ops.add(struct.unpack_from("<I", h, 29)[0])
                hide_ops.add(struct.unpack_from("<I", h, 42)[0])
            if not ok:
                bad_handler += 1
                if bad_handler <= 3:
                    print(f"    handler mismatch [slot {j} / table {i}] "
                          f"{c['character']} @{haddr:#x}: {h.hex()}")
        check(f"all {len(selectable)} alias strings decode to expected names",
              bad_alias == 0, f"{bad_alias} mismatches")
        check(f"all {len(selectable)} handlers: setvar TABLE index, setflag, "
              "givepokemon(signature, L5), show-mugshot, msgbox, hide-mugshot",
              bad_handler == 0, f"{bad_handler} mismatches")
        # One sweep native, shared by every handler, inside the shim and not
        # the same address as either mugshot op.
        check(f"every handler calls the same activation sweep, once, after the "
              f"give", len(sweep_ops) == 1
              and SHIM_ADDR < (next(iter(sweep_ops)) & ~1) < BITMAPS_ADDR
              and not (sweep_ops & show_ops) and not (sweep_ops & hide_ops),
              f"sweep={[hex(x) for x in sweep_ops][:4]}")

        # --- the threshold gate, checked in the positive direction ---------
        # "The chain is short" is satisfied by a broken chain just as well as by
        # a gated one, so name the hidden characters and prove each is absent.
        leaked = [c["character"] for _i, c in hidden_chars
                  if alias_for(c["character"]) in chain_aliases]
        check(f"none of the {len(hidden_chars)} hidden characters' codes are in "
              "the chain", not leaked, ", ".join(leaked[:6]))
        # ...and that hiding did not cost anyone else their slot.
        check(f"chain length == selectable count ({len(selectable)}), "
              f"table stays {NUM_CHARS}",
              len(selectable) == NUM_SELECTABLE
              and len(selectable) + len(hidden_chars) == NUM_CHARS)
        # A hidden character's ENFORCEMENT data must be untouched: same bitmap
        # slot, still populated. This is what makes an existing save keep working.
        empty = [c["character"] for i, c in hidden_chars
                 if not any(bitmaps[i * STRIDE:(i + 1) * STRIDE])]
        check("hidden characters keep a populated allow-bitmap (old saves still "
              "enforce)", not empty, ", ".join(empty[:6]))

        # The two callnative operands are re-derived here from the ROM alone --
        # no build artifact says what they should be. Every handler must name
        # the same two entry points, both Thumb, both inside the renderer blob,
        # and they must not be the same function.
        check("every handler calls the same mugshot show/hide pair",
              len(show_ops) == 1 and len(hide_ops) == 1,
              f"show={[hex(x) for x in show_ops]} hide={[hex(x) for x in hide_ops]}")
        if len(show_ops) == 1 and len(hide_ops) == 1:
            show, hide = show_ops.pop(), hide_ops.pop()
            check("mugshot callnative operands are Thumb pointers into the renderer",
                  all(a & 1 and msoff + 0x08000000 <= (a & ~1) < msend + 0x08000000
                      for a in (show, hide)),
                  f"show={show:#x} hide={hide:#x} blob=[{msoff + 0x08000000:#x},"
                  f"{msend + 0x08000000:#x})")
            check("show and hide are distinct entry points", show != hide,
                  f"both {show:#x}")

        # debug handlers
        h = rd(checks_parsed[0][1], 12)
        check("CMDbgOff handler: clearflag CM + setvar 0",
              h[0] == 0x2A and struct.unpack_from("<H", h, 1)[0] == FLAG_CM
              and h[3] == 0x16 and struct.unpack_from("<HH", h, 4) == (VAR_ID, 0))
        # CMDbgGive2's species is DERIVED here from character 0's in-ROM bitmap,
        # independently of the injector. It used to be the literal 52 (Meowth),
        # which joined Red's roster when the roster grew -- so the debug code
        # silently stopped exercising the off-roster path while this check still
        # passed. Re-deriving means the check fails if the two ever disagree,
        # and it also proves the species really is off-roster.
        bm0 = patched[BITMAPS_ADDR - 0x08000000:BITMAPS_ADDR - 0x08000000 + STRIDE]
        on0 = lambda sp: (bm0[sp >> 3] >> (sp & 7)) & 1
        want_give2 = next(sp for sp in range(1, STRIDE * 8) if not on0(sp))
        check(f"CMDbgGive2 species {want_give2} is genuinely off character 0's roster",
              not on0(want_give2))
        for i, species in ((1, 25), (2, want_give2)):
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
          and patched[w+20] == 0x21 and struct.unpack_from("<HH", patched, w+21) == (VAR_ID, NUM_CHARS + 1)
          and patched[w+25] == 0x06 and patched[w+26] == 4 and u32p(w+27) == TRADE_ORIG)
    check("wrapper preamble decodes (flag/char-0/char-range passthroughs)", ok)
    p2 = w + 31
    n_allow = 0
    while patched[p2] == 0x21:
        var, idx = struct.unpack_from("<HH", patched, p2+1)
        good = (var == VAR_ID and 1 <= idx <= NUM_CHARS and patched[p2+5] == 0x06
                and patched[p2+6] == 1 and u32p(p2+7) == TRADE_ORIG)
        if not good:
            break
        # the allowing character's bitmap must actually allow the species
        bmi = (idx-1)*STRIDE
        if not bitmaps[bmi + (TRADE_SPECIES >> 3)] & (1 << (TRADE_SPECIES & 7)):
            break
        n_allow += 1
        p2 += 11
    expected_allow = sum(1 for i in range(NUM_CHARS)
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
    # The entry is NOT the first thing in the blob and must not be assumed to be:
    # gcc reordered it behind a static helper the moment the legendary picker
    # landed. Resolve it from the linked ELF, the same way the mugshot section
    # resolves sMugshotTemplate.
    _wsym = subprocess.run(["arm-none-eabi-nm", str(ROOT / "build" / "wild_encounter_mode.elf")],
                           check=True, capture_output=True, text=True).stdout
    _wm = re.search(r"^([0-9a-f]+) T CM_CreateWildMonGated$", _wsym, re.M)
    check("CM_CreateWildMonGated resolves in the wild shim ELF", bool(_wm))
    wild_entry = int(_wm.group(1), 16) if _wm else WILD_SHIM_ADDR
    check(f"wild shim entry {wild_entry:#x} lies inside the blob",
          wsoff <= wild_entry - 0x08000000 < wsend)
    for site in WILD_BL_SITES:
        tgt = decode_bl(patched[site:site + 4], 0x08000000 + site)
        check(f"wild BL at {site:#x} -> wild shim entry", tgt == wild_entry,
              f"decoded {tgt and hex(tgt)} expected {wild_entry:#x}")
        old = decode_bl(orig[site:site + 4], 0x08000000 + site)
        check(f"wild BL at {site:#x} originally -> CreateWildMon", old == CREATEWILDMON_ADDR,
              f"decoded {old and hex(old)}")
    check("wild shim entry starts with push {..,lr}",
          (struct.unpack_from("<H", patched, wild_entry - 0x08000000)[0] & 0xFF00) == 0xB500)
    off_o = WILD_OFFSETS_ADDR - 0x08000000
    off_d = WILD_DATA_ADDR - 0x08000000
    check("wild_override_offsets.bin in ROM == build artifact",
          patched[off_o:off_o + len(wild_offsets)] == wild_offsets)
    check("wild_override.bin in ROM == build artifact",
          patched[off_d:off_d + len(wild_data)] == wild_data)
    check(f"wild override offsets table has {NUM_CHARS} entries", len(wild_offsets) == NUM_CHARS * 4)

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

    def walk_table(blob, offsets, ci, header=0):
        """Every species id in character ci's block. `header` skips the
        legendary table's extra flags byte."""
        pp = struct.unpack_from("<I", offsets, ci * 4)[0] + header
        out, well_formed = [], True
        nf = blob[pp]; pp += 1
        for _ in range(nf):
            ns = blob[pp]; pp += 1
            for _ in range(ns):
                sid, lo, hi = struct.unpack_from("<HBB", blob, pp)
                pp += 4
                out.append(sid)
                well_formed = well_formed and lo <= hi
        return out, nf, well_formed

    bad_legendary = []
    # NOT range(185): that literal predates the roster growing to NUM_CHARS and
    # made this "exhaustive" scan cover 185/238 while still printing PASS --
    # skipping precisely the newest, least-reviewed rosters. Same bug class as
    # the `== 202` guard fixed above; derive the bound.
    #
    # The Tobias exemption that used to live here is GONE, and its absence is
    # the check: his hand-coded legendary-inclusive 10% table was replaced by the
    # general 1% rule, so the 10% table is now legendary-free for EVERY
    # character with no exceptions at all.
    for ci in range(NUM_CHARS):
        for sid in walk_table(wild_data, wild_offsets, ci)[0]:
            if sid in legendary_ids:
                bad_legendary.append((chars[ci]["character"], sid))
    check(f"wild override: no legendary/mythical in any of the {NUM_CHARS} "
          "characters' 10% tables (no exemptions)",
          not bad_legendary, f"{bad_legendary[:5]}")

    print("== 8b. legendary encounters (1%) ==")
    off_lo = WILD_LEG_OFFSETS_ADDR - 0x08000000
    off_ld = WILD_LEG_DATA_ADDR - 0x08000000
    check("wild_legendary_offsets.bin in ROM == build artifact",
          patched[off_lo:off_lo + len(leg_offsets)] == leg_offsets)
    check("wild_legendary.bin in ROM == build artifact",
          patched[off_ld:off_ld + len(leg_data)] == leg_data)
    check(f"legendary offsets table has {NUM_CHARS} entries",
          len(leg_offsets) == NUM_CHARS * 4)

    # The INVERSE of the scan above, and the one that actually protects this
    # feature. Every existing wild assertion is of the form "a legendary never
    # appeared" -- which, once the dex filter can suppress legendaries, is
    # satisfied just as well by the feature being completely dead. Assert in the
    # positive direction: the 1% table must be non-empty for the characters that
    # should have one, and everything in it must BE a legendary.
    not_legendary, malformed = [], []
    leg_pool, repeatable = {}, set()
    for ci in range(NUM_CHARS):
        base = struct.unpack_from("<I", leg_offsets, ci * 4)[0]
        if leg_data[base] & 0x1:
            repeatable.add(chars[ci]["character"])
        sids, nf, ok = walk_table(leg_data, leg_offsets, ci, header=1)
        if nf:
            leg_pool[chars[ci]["character"]] = sids
        if not ok:
            malformed.append(chars[ci]["character"])
        for sid in sids:
            if sid not in legendary_ids:
                not_legendary.append((chars[ci]["character"], sid))
    check("legendary table contains ONLY legendaries/mythicals",
          not not_legendary, f"{not_legendary[:5]}")
    check("legendary tables well-formed (lvlMin <= lvlMax throughout)",
          not malformed, f"{malformed[:5]}")

    # Re-derive who SHOULD have a pool straight from the rosters, independently
    # of the emitter, and demand an exact match. A silently empty table is the
    # failure this feature is most exposed to.
    with open(ROOT / "tools" / "character_mode" / "characters_manifest.json") as f:
        _mani = json.load(f)["characters"]
    want_pool = {c["character"] for c in _mani
                 if any(dex_species.get(s, {}).get("name") in LEGENDARY_NAMES
                        for s in c["roster_species_ids"])}
    check(f"every character with a legendary on its roster has a 1% pool "
          f"({len(want_pool)} of {NUM_CHARS})",
          set(leg_pool) == want_pool,
          f"missing {sorted(want_pool - set(leg_pool))[:5]} "
          f"extra {sorted(set(leg_pool) - want_pool)[:5]}")

    # §1.2: repeatable exactly when the character has NO non-legendary families,
    # or Cogita catches her one legendary and can then catch nothing all run.
    want_repeat = {chars[ci]["character"] for ci in range(NUM_CHARS)
                   if walk_table(leg_data, leg_offsets, ci, header=1)[1]
                   and not walk_table(wild_data, wild_offsets, ci)[1]}
    check(f"repeatable flag set exactly for the all-legendary characters "
          f"({', '.join(sorted(want_repeat)) or 'none'})",
          repeatable == want_repeat,
          f"flagged {sorted(repeatable)} expected {sorted(want_repeat)}")

    # Nobody may be left unable to catch anything: that is the catch-nothing
    # failure READINESS_PLAN.md flags, and the legendary pool is what fixes it.
    starved = [chars[ci]["character"] for ci in range(NUM_CHARS)
               if not walk_table(wild_data, wild_offsets, ci)[1]
               and not walk_table(leg_data, leg_offsets, ci, header=1)[1]]
    check("no character has an empty pool in BOTH tables", not starved,
          f"{starved[:5]}")

    # Red is the cross-check with a known answer on both sides at once.
    check("legendary: Red's pool holds Articuno, and he is not repeatable",
          144 in leg_pool.get("Red", []) and "Red" not in repeatable)

    # The dex filter converts species -> national dex number before reading the
    # caught flags, and species id != national dex number here. Re-derive the
    # table from the ROM's own literal pool and confirm both the conversion
    # canary and that no legendary in any pool maps to 0 (which the shim treats
    # as "never caught", so such a legendary could never be retired).
    natdex_ptr = struct.unpack_from("<I", orig, 0x432B0)[0]
    check("SpeciesToNationalPokedexNum's literal pool -> gSpeciesToNationalPokedexNum",
          natdex_ptr == 0x098218F0, hex(natdex_ptr))
    nb = natdex_ptr - 0x08000000
    natdex = lambda s: struct.unpack_from("<H", orig, nb + (s - 1) * 2)[0]
    check("species id != national dex number (species 386 -> 313, Volbeat)",
          natdex(386) == 313, str(natdex(386)))
    zero_dex = sorted({s for sids in leg_pool.values() for s in sids if natdex(s) == 0})
    check("no legendary in any pool maps to national dex 0 (would never retire)",
          not zero_dex, f"{zero_dex[:5]}")

    print("== 9. character sprites (Phase 3) ==")
    sp = CM_SPRITE_PTRS_ADDR - 0x08000000
    sb = CM_SPRITE_BLOBS_ADDR - 0x08000000
    check("sprite blobs in ROM == cm_sprite_blobs.bin",
          patched[sb:sb + len(spr_blobs)] == spr_blobs)
    check("sprite pointer table in ROM == recomputed from offsets",
          patched[sp:sp + len(spr_ptrs_expected)] == bytes(spr_ptrs_expected))

    # every wired pointer must land inside the blob region and decode to a real
    # 64x64 4bpp sprite + 16-colour palette. A pointer that merely looks like a
    # ROM address is not evidence of anything.
    n_wired, bad = 0, []
    for i in range(len(chars)):
        g, pl = struct.unpack_from("<II", patched, sp + i * 8)
        if not g and not pl:
            continue
        n_wired += 1
        if not (CM_SPRITE_BLOBS_ADDR <= g < CM_SPRITE_BLOBS_ADDR + len(spr_blobs)
                and CM_SPRITE_BLOBS_ADDR <= pl < CM_SPRITE_BLOBS_ADDR + len(spr_blobs)):
            bad.append((i, "pointer outside blob region")); continue
        try:
            gfx = lz77_decode(patched, g - 0x08000000)
            pal = lz77_decode(patched, pl - 0x08000000)
        except Exception as e:
            bad.append((i, f"decode failed: {e}")); continue
        if len(gfx) != 2048 or len(pal) != 32:
            bad.append((i, f"sizes {len(gfx)}/{len(pal)}"))
    check(f"all {n_wired} wired sprites decode to 64x64 4bpp + 16-colour palette",
          not bad, f"{bad[:5]}")

    # characters.bin must agree with the pointer table about who has art
    cbin = (ROOT / "tools" / "character_mode" / "characters.bin").read_bytes()
    mismatch = []
    for i in range(len(chars)):
        sid = struct.unpack_from("<H", cbin, i * 12 + 8)[0]
        g = struct.unpack_from("<I", patched, sp + i * 8)[0]
        if (sid == 0xFFFF) != (g == 0):
            mismatch.append((i, chars[i]["character"], hex(sid), hex(g)))
    check("characters.bin sprite_asset_id agrees with the in-ROM pointer table",
          not mismatch, f"{mismatch[:5]}")

    print("== 10. mugshot renderer ==")
    ms_bin = ROOT / "build" / "character_sprite.bin"
    if ms_bin.is_file():
        blob = ms_bin.read_bytes()
        check("renderer blob in ROM == build/character_sprite.bin",
              patched[msoff:msoff + len(blob)] == blob, f"{len(blob)} bytes")
    check("renderer starts with push {..,lr}", patched[msoff + 1] == 0xB5)

    # Find the SpriteTemplate inside the blob and check every pointer it hands
    # the engine. A template that assembles cleanly but names a wrong address is
    # the failure mode that would show up on screen as garbage, not as a crash,
    # so it is worth pinning here rather than trusting the compiler.
    #   {u16 tileTag, u16 palTag, u32 oam, u32 anims, u32 images,
    #    u32 affineAnims, u32 callback}
    GDUMMY_ANIM, GDUMMY_AFFINE = 0x08231CF0, 0x08231CFC
    SPRITE_CB_DUMMY = 0x0800760D
    tmpl = None
    for off in range(msoff, msend - 24, 4):
        w = struct.unpack_from("<5I", patched, off + 4)
        if w[1] == GDUMMY_ANIM and w[3] == GDUMMY_AFFINE and w[4] == SPRITE_CB_DUMMY:
            tmpl = off
            break
    check("SpriteTemplate located in the renderer blob", tmpl is not None)
    if tmpl is not None:
        tile_tag, pal_tag = struct.unpack_from("<HH", patched, tmpl)
        oam_ptr, _, images, _, _ = struct.unpack_from("<5I", patched, tmpl + 4)
        check("template tile/palette tags are distinct and non-TAG_NONE",
              tile_tag != pal_tag and 0xFFFF not in (tile_tag, pal_tag),
              f"{tile_tag:#x}/{pal_tag:#x}")
        check("template images == NULL (required when tileTag != TAG_NONE)",
              images == 0, hex(images))
        check("template oam pointer lands inside the renderer blob",
              msoff + 0x08000000 <= oam_ptr < msend + 0x08000000, hex(oam_ptr))
        if msoff + 0x08000000 <= oam_ptr < msend + 0x08000000:
            attr0, attr1, attr2, _ = struct.unpack_from("<4H", patched,
                                                        oam_ptr - 0x08000000)
            # 64x64 = shape square (attr0 bits 14-15 == 0) + size 3 (attr1 bits
            # 14-15 == 3). Getting this wrong renders a corner of the art at the
            # wrong scale rather than failing.
            check("OAM describes a 64x64 4bpp square sprite at priority 0",
                  (attr0 >> 14) == 0 and ((attr0 >> 13) & 1) == 0
                  and (attr1 >> 14) == 3 and ((attr2 >> 10) & 3) == 0,
                  f"attr0={attr0:#06x} attr1={attr1:#06x} attr2={attr2:#06x}")

    # == Species Randomizer exclusion ==
    # Radical Red ships a Species Randomizer whose own description says it
    # "randomizes encounters, trainers, and gifts". CFRU applies it inside
    # CreateBoxMon() via TryRandomizeSpecies() -- DOWNSTREAM of the roster
    # override -- so with it on, a roster species we inject is remapped to an
    # unrelated one and the catch gate then refuses what it was handed:
    # Character Mode degrades to "you can catch almost nothing", silently.
    # Character Mode therefore clears the randomizer flag. ROWE hit the same
    # interaction and made the two modes mutually exclusive.
    #
    # ⚠️ Checked in the BUILT SHIMS, not only in the source. Reading the .c
    # would pass just as happily if the compiler had inlined the guard away or
    # the injector had shipped a stale blob -- this repo's own rule is to
    # verify the constant the compiler baked in.
    print("== 12. Species Randomizer exclusion ==")
    # These shims reach vanilla code through function-pointer constants
    # (-mlong-calls), so the evidence is the LITERAL in the shim's pool, not a
    # BL target. FlagClear is 0x0806E6A8, +1 for Thumb.
    FLAG_CLEAR_LIT = struct.pack("<I", 0x0806E6A9)
    def _blob(base, length):
        b = base - 0x08000000
        return bytes(patched[b:b + length])
    check("the give gate's shim carries FlagClear (randomizer exclusion)",
          FLAG_CLEAR_LIT in _blob(SHIM_ADDR, shim_len))
    check("the wild override's shim carries FlagClear (randomizer exclusion)",
          FLAG_CLEAR_LIT in _blob(WILD_SHIM_ADDR, 0x1000))
    # The flag id has to be in there too, or the guard clears something else.
    # 0x940 is NOT stored as a literal: it exceeds Thumb's 8-bit immediate, so
    # gcc synthesises it as `movs rN,#0x94; lsls rN,#4`. Pin that pair -- the
    # first attempt here looked for a raw 0x0940 halfword and failed for the
    # wrong reason, which is exactly the kind of checker this project keeps
    # having to negative-test.
    _mk940 = bytes.fromhex("94200001")     # movs r0,#0x94 ; lsls r0,r0,#4
    check("the give gate's shim builds flag id 0x940 (movs #0x94; lsls #4)",
          _mk940 in _blob(SHIM_ADDR, shim_len))
    check("the wild override's shim builds flag id 0x940",
          _mk940 in _blob(WILD_SHIM_ADDR, 0x1000))
    for _f in ("src/character_mode.c", "src/wild_encounter_mode.c"):
        _s = (ROOT / _f).read_text()
        check(f"{_f} pins FLAG_POKEMON_RANDOMIZER to 0x940",
              "#define FLAG_POKEMON_RANDOMIZER 0x940" in _s)

    # == 13. Encounter marker ==
    print("== 13. encounter marker ==")
    _MK_SHIM, _MK_ADDR, _MK_STRIDE = 0x08378CA8, 0x08379000, 64
    _MK_BL, _MK_WRAPPER = 0x0D77DE, 0x080D77F4
    _MK_STRS = (0x083FD284, 0x083FD297)
    _mk = (ROOT / "tools" / "character_mode" / "marker_strings.bin").read_bytes()
    _nchars = len(json.loads((ROOT / "tools" / "character_mode" /
                              "characters_manifest.json").read_text())["characters"])
    check("marker_strings.bin is NUM_CHARACTERS x 64",
          len(_mk) == _nchars * _MK_STRIDE, str(len(_mk)))
    check("marker strings in ROM == marker_strings.bin",
          bytes(patched[_MK_ADDR - 0x08000000:
                        _MK_ADDR - 0x08000000 + len(_mk)]) == _mk)
    _want = bytes.fromhex("d1dde0d800fd0600d5e4e4d9d5e6d9d8abfbff")
    for _a in _MK_STRS:
        check(f"wild-intro string intact at {_a:#x}",
              bytes(patched[_a - 0x08000000:
                            _a - 0x08000000 + len(_want)]) == _want)
    _bl_now = decode_bl(bytes(patched[_MK_BL:_MK_BL + 4]), 0x08000000 + _MK_BL)
    check("the intro BL now points into the marker shim",
          _bl_now is not None and _MK_SHIM <= _bl_now < _MK_ADDR,
          hex(_bl_now) if _bl_now else "None")
    check("and originally pointed at the vanilla wrapper",
          decode_bl(bytes(orig[_MK_BL:_MK_BL + 4]),
                    0x08000000 + _MK_BL) == _MK_WRAPPER)
    # The shim and the strings share one free run; prove they do not overlap and
    # that the region really was free before we wrote it.
    check("the marker shim does not run into the string blob",
          _MK_SHIM < _MK_ADDR)
    check("the whole marker region was 0xFF in the original",
          all(b == 0xFF for b in orig[_MK_SHIM - 0x08000000:
                                      _MK_ADDR - 0x08000000 + len(_mk)]))
    _bad = [i for i in range(_nchars)
            if 0xFF not in _mk[i * _MK_STRIDE:(i + 1) * _MK_STRIDE]]
    check("every marker slot is 0xFF-terminated", not _bad, str(len(_bad)))

    if assert_tally(checks_run, EXPECT_CHECKS, "verify_artifacts"):
        return 1
    print(f"\n{'ALL PASS' if not failures else 'FAILURES: ' + ', '.join(failures)}"
          f" -- {checks_run} checks ran")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
