#!/usr/bin/env python3
"""Assemble the PC-exit sweep hook (withdraw-path enforcement).

THE GAP THIS CLOSES. Enforcement deliberately routes off-roster Pokemon INTO
the PC -- the catch gate, the gift routing, the activation sweep and the
egg-hatch hook all box what the roster does not allow. Nothing then looked at
the PC's own WITHDRAW. So a mon the catch gate had just boxed could be taken
straight back out and kept for the rest of the run. No exploit was required:
it is what happens if you open the PC and take the mon back.
../game_plans/rowe_parity.md §13.24 has the measurement; §13.26c has this RE.

⭐ THE FINDING THAT MADE THIS CHEAP, AND IT IS THE EGG HOOK AGAIN. The PC is
opened FROM A SCRIPT, and the special that opens it carries a `waitstate`, so
the script RESUMES after the storage UI closes:

    0x081A6A1A: 0F 00 <0x081A50BE>  loadword 0, "Pokemon Storage System opened."
              +6: 09 04              callstd MSGBOX_DEFAULT
    0x081A6A22: 25 3C 00             special 0x3C   <- opens the storage system
              +3: 27                 waitstate      <- returns here when it closes
              +4: 16 04 80 1B 00     setvar 0x8004, 0x001B
              +9: 25 7D 01           special 0x17D
             +12: 05 <0x081A6998>    goto (back to the PC main menu)

That is the SAME SHAPE as the egg-hatch tail this repo already splices
(egg_hook.py: `25 C2 00 27 6B 02`), so this hook is that technique pointed at a
different script -- already shipped, negative-tested 6/6, and proven live in an
emulator (rowe_parity.md §13.22). ⭐ And there is MORE room here: nine
contiguous replayable bytes where a `goto` needs five; the egg hook had six.

HOW THE SPECIAL ID WAS FOUND (0x3C), and it was NOT guessed. The FireRed pair
has no `specials.inc` to count, so: scan all 444 `gSpecials` entries
(table at 0x0815FD60) for a handler inside the PSS code region
0x0808B000-0x08096000 -- bracketed by `StorageGetCurrentBox` 0x0808B9F4 and
`CompactPartySlots` 0x080937DC, both named in the CFRU donor's BPRE.ld. Three
entries qualify (0x3C, 0x84, 0x85) and only 0x3C is ever followed by a
`waitstate`. ✅ Confirmed by decoding the dialogue immediately above the splice:
"Pokemon Storage System opened."

⚠️ WHAT THIS GIVES, AND WHAT IT DOES NOT. This is ROWE's `Cb2_ExitPSS`
semantics: UNDO ON EXIT, not prevention. The player may withdraw an off-roster
mon and carry it inside the PC UI; it is boxed again the moment the PC closes.
🔴 It does NOT give ROWE's SECOND guard, `IsRemovingLastAllowedPartyMon`. The
sweep's never-empty rule KEEPS an off-roster mon when the roster allows nothing
else, so "deposit your only on-roster mon, withdraw an off-roster one, exit"
still leaves the player holding it. ROWE closes that inside the PSS's own
"can this mon be removed" check, which is a real RE job in a closed binary and
is deliberately NOT attempted here. Do not describe this hook as closing the
withdraw hole completely.

Two facts checked IN THIS ROM before the overlay is applied:

- **Nothing references the interior of the spliced region.** An UNALIGNED u32
  scan of the whole ROM finds ZERO words pointing anywhere into
  0x081A6A22..0x081A6A2A -- the entry included, since the script falls into it
  from the msgbox above rather than being jumped to. (⚠️ The scan MUST be
  unaligned: script pointers in this engine are not word-aligned, and an
  aligned-only scan reports a clean interior it never looked at.)
- **The nine original bytes are asserted byte-for-byte** before anything is
  written, so a wrong ROM, or a re-run over an already-patched build, fails
  loudly instead of writing opcodes into the middle of something else.

Byte grammar (all opcodes confirmed in this ROM):
    23 <u32>   callnative
    25 <u16>   special
    27         waitstate
    16 <u16> <u16>  setvar
    05 <u32>   goto
"""
import struct

# file offset == rom address - 0x08000000 in this region
SPLICE_ROM_ADDR = 0x081A6A22
SPLICE_FILE_OFF = 0x001A6A22
# special 0x3C ; waitstate ; setvar 0x8004, 0x001B
SPLICE_ORIG = bytes.fromhex("253c00271604801b00")
SPECIAL_PC = 0x003C
# gSpecials, the table the id above indexes. Named here because the LIVE layer
# (tools/mgba_scripts/cm_pc_exit_test.lua) breakpoints the storage system's own
# handler -- gSpecials[SPECIAL_PC] -- to prove the UI really opened, rather than
# inferring it from the script having run. Derived, never hardcoded downstream.
SPECIALS_TABLE_ADDR = 0x0815FD60
OPCODE_CALLNATIVE = 0x23
OPCODE_SETVAR = 0x16
# The dialogue that proves this is the PC access script, and its pointer, both
# asserted by the injector so a moved script fails loudly.
PC_TEXT_PTR = 0x081A50BE
PC_TEXT_PTR_OFF = 0x001A6A1C


def build(tail_rom_addr, sweep_thumb_addr):
    """Return (blob, patches): the tail-script blob to place at tail_rom_addr
    and a list of (file_off, orig_bytes, new_bytes) overlay patches.

    sweep_thumb_addr is CM_SweepPartyToPC WITH the Thumb bit, resolved from the
    built shim's own symbol table by the injector -- never hardcoded, because a
    stale address here would call into the middle of another routine every time
    the player closes the PC, and would not fail any static check.
    """
    assert sweep_thumb_addr & 1, (
        "CM_SweepPartyToPC must carry the Thumb bit; %#x does not"
        % sweep_thumb_addr)
    ret = SPLICE_ROM_ADDR + len(SPLICE_ORIG)
    tail = (bytes([0x25]) + struct.pack("<H", SPECIAL_PC)   # replay: open the PC
            + bytes([0x27])                                  # replay: waitstate
            # NEW, and the ORDER IS THE FEATURE: the sweep runs AFTER the
            # waitstate, i.e. after the storage UI has closed and the party is
            # whatever the player left it as. Run before it and the sweep would
            # see the party as it was on the way IN, which is a silent no-op
            # that still passes any "the callnative is present" check.
            + bytes([OPCODE_CALLNATIVE])
            + struct.pack("<I", sweep_thumb_addr)
            + bytes([OPCODE_SETVAR])                         # replay: setvar
            + struct.pack("<HH", 0x8004, 0x001B)
            + bytes([0x05]) + struct.pack("<I", ret))        # rejoin the script
    new = bytes([0x05]) + struct.pack("<I", tail_rom_addr)
    new += b"\x00" * (len(SPLICE_ORIG) - len(new))
    assert len(new) == len(SPLICE_ORIG), (
        "PC splice must be exactly %d bytes, got %d"
        % (len(SPLICE_ORIG), len(new)))
    return tail, [(SPLICE_FILE_OFF, SPLICE_ORIG, new)]


if __name__ == "__main__":
    blob, patches = build(0x08C8F100, 0x08C800D1)
    print("orig: %s" % SPLICE_ORIG.hex(" "))
    print("tail: %d bytes: %s" % (len(blob), blob.hex(" ")))
    for off, orig, new in patches:
        print("patch @%#010x: %s -> %s" % (off, orig.hex(" "), new.hex(" ")))
