#!/usr/bin/env python3
"""Assemble the egg-hatch sweep hook (hatch-path enforcement).

THE GAP THIS CLOSES. Eggs are deliberately exempt from the catch gate, the
gift routing and the activation party sweep, so an egg event can never block
progress -- but nothing looked at what an egg HATCHED INTO. A gift egg of an
off-roster species therefore hatched into a permanent off-roster party member.
Breeding cannot reach that (a roster stores whole evolution families and only
on-roster parents can be kept, so offspring are on-roster by construction);
gift eggs are the way in.

⚠️ AND IN THIS GAME THERE IS AN EGG *ECONOMY*, NOT AN EGG EVENT. Measured
2026-09-03 (docs/GIFT_EGGS.md, ../game_plans/rowe_parity.md §13.18): 33
reachable `giveegg` sites -- 27 of them a Shard->starter-Egg exchange, 6 a
¥5000 vendor that ALSO advertises a "Wonder Egg that just contains a random
first form Pokemon". The median offered character finds 97% of those species
off-roster, and 102 of 210 have no on-roster outcome at all.

RE summary (2026-09-03). ⭐ THE USEFUL FINDING: this path is untouched CFRU
donor code, so Radical Red's hatch caller and hatch script are BYTE-IDENTICAL
to Unbound's, at the same addresses. Measured, not assumed -- both were
diffed. That is what makes this a port rather than a fresh reverse-engineering
job, and it is worth checking first in any other CFRU hack.

Hatching is SCRIPT-DRIVEN. The overworld step handler at 0x0806D704 calls
`ShouldEggHatch` (0x080463B8, the CFRU donor's own address -- the ONLY direct
BL to it in the whole ROM) and on a true result runs a script:

    0806d704: bl   ShouldEggHatch
    0806d70a: cmp  r0, #0
    0806d70c: beq  <no hatch>
    0806d70e: movs r0, #13
    0806d710: bl   0x08054E90
    0806d714: ldr  r0, [pc, #4]      @ 0x081BF546
    0806d716: bl   ScriptContext1_SetupScript

The script at 0x081BF546 decodes to:

    081bf546: 69                 lock-ish (replayed byte-for-byte, unexamined)
    081bf547: 0F 00 <0x081BFB5A> loadword 0, "...hatched!" text
    081bf54d: 09 04              callstd MSGBOX_DEFAULT
    081bf54f: 25 C2 00           special 0xC2   <- performs the hatch
    081bf552: 27                 waitstate
    081bf553: 6B                 release-ish (replayed byte-for-byte)
    081bf554: 02                 end

The tail from `special 0xC2` is overlaid with a `goto` into an injected tail
that replays those four commands and then runs `callnative CM_SweepPartyToPC`.
⭐ That is the one place this port DIVERGES from Unbound, and it is simpler:
Unbound repoints a dead gSpecials slot because it needs one for its trade hook
anyway, while this repo already emits `callnative` (opcode 0x23) in its
selection script, so the sweep can be called directly with no table edit at
all. The sweep runs AFTER the hatch's waitstate, so it sees the finished
Pokemon rather than the egg, and the egg exemption inside the sweep no longer
applies to it. With Character Mode off `CM_SweepPartyToPC` returns immediately,
and the sweep never empties the party.

Two facts that made this safe, both CHECKED IN THIS ROM rather than inherited
from Unbound's write-up:

- **Nothing references the interior of the script.** An UNALIGNED u32 scan of
  the whole ROM finds 0x081BF546 (the entry) twice -- the caller's literal pool
  at 0x0806D71C and a second table at 0x090B1BF0, i.e. a second code path that
  runs the SAME script, so one hook covers both -- and finds ZERO references to
  0x081BF547, 0x081BF54F, 0x081BF552, 0x081BF553 or 0x081BF554. Overlaying the
  tail cannot land mid-jump. (⚠️ The scan must be unaligned: script pointers in
  this engine are not word-aligned, and an aligned-only scan reports a clean
  interior it never actually looked at.)
- **Six bytes are available** (`25 c2 00 27 6b 02`) and a `goto` needs five, so
  the displaced code is replayed rather than shortened. The sixth byte is
  padding that is never executed.

Byte grammar (all opcodes confirmed in this ROM):
    23 <u32>   callnative
    25 <u16>   special
    27         waitstate
    05 <u32>   goto
    02         end
"""
import struct

# file offset == rom address - 0x08000000 in this region
SPLICE_ROM_ADDR = 0x081BF54F
SPLICE_FILE_OFF = 0x001BF54F
SPLICE_ORIG = bytes.fromhex("25c200276b02")   # special 0xC2; waitstate; 6B; end
SCRIPT_ENTRY = 0x081BF546
SPECIAL_HATCH = 0x00C2
OPCODE_RELEASE = 0x6B
OPCODE_CALLNATIVE = 0x23


def build(tail_rom_addr, sweep_thumb_addr):
    """Return (blob, patches): the tail-script blob to place at tail_rom_addr
    and a list of (file_off, orig_bytes, new_bytes) overlay patches.

    sweep_thumb_addr is CM_SweepPartyToPC WITH the Thumb bit, resolved from the
    built shim's own symbol table by the injector -- never hardcoded, because a
    stale address here would call into the middle of another routine on every
    egg hatch and would not fail any static check.
    """
    assert sweep_thumb_addr & 1, (
        "CM_SweepPartyToPC must carry the Thumb bit; %#x does not"
        % sweep_thumb_addr)
    tail = (bytes([0x25]) + struct.pack("<H", SPECIAL_HATCH)   # replay: the hatch
            + bytes([0x27])                                     # replay: waitstate
            + bytes([OPCODE_RELEASE])                           # replay: release-ish
            + bytes([OPCODE_CALLNATIVE])
            + struct.pack("<I", sweep_thumb_addr)               # NEW: sweep to PC
            + bytes([0x02]))                                    # replay: end
    new = bytes([0x05]) + struct.pack("<I", tail_rom_addr) + b"\x00"
    assert len(new) == len(SPLICE_ORIG), (
        "egg splice must be exactly %d bytes, got %d"
        % (len(SPLICE_ORIG), len(new)))
    return tail, [(SPLICE_FILE_OFF, SPLICE_ORIG, new)]


if __name__ == "__main__":
    blob, patches = build(0x08C8F000, 0x08C80101)
    print("tail: %d bytes: %s" % (len(blob), blob.hex(" ")))
    for off, orig, new in patches:
        print("patch @%#010x: %s -> %s" % (off, orig.hex(" "), new.hex(" ")))
