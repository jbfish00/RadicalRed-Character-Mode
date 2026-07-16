#!/usr/bin/env python3
"""GDB-driven unit test for the Character Mode enforcement shim.

Mirrors ROWE's in-game debug-menu testing philosophy (drive the real code
with controlled state, observe the decision) but adapted to a binary hack:
runs the REAL shim code in the REAL emulator (mGBA's GDB stub), with
synthetic Pokemon structs and flag/var RAM, and checks which branch the
shim takes for every case in the decision table.

Key fact making this safe without booting the game: every function the
shim calls before its branch decision (FlagGet/VarGet via RR's expanded
hooks, GetMonData) reads only fixed EWRAM addresses or the passed struct —
no save-block pointer derefs — so the test runs from reset state.

Branch observation points (from the shim's verified disassembly):
  0x08C80018  = pass-through path (about to call GiveMonToPlayer)
  0x08C80074  = enforcement path (about to call SendMonToPC)
Execution is stopped AT these points; the deep calls never run.

Decision table tested:
  1. flag OFF                                  -> pass-through
  2. flag ON, party empty                      -> pass-through (soft-lock guard)
  3. flag ON, party=1, char=Red, Pikachu(25)   -> pass-through (on-roster)
  4. flag ON, party=1, char=Red, Meowth(52)    -> SendMonToPC  (off-roster)
  5. flag ON, party=1, char=0 (unset)          -> pass-through
  6. flag ON, party=1, char=Red, Meowth EGG    -> pass-through (eggs exempt)
  7. flag ON, party=1, char=185 (out of range) -> pass-through
  8. flag ON, party=1, char=Jessie(?), Meowth  -> pass-through (Meowth IS on
     Team Rocket Jessie's roster... actually Meowth is James/Jessie-adjacent;
     resolved dynamically from the manifest: uses a character that has
     Meowth's family allowed, to prove per-character bitmaps differ)

Usage: shim_unit_test.py <rom.gba>
Starts mgba-qt -g itself; requires DISPLAY. Exit 0 = all pass.
"""
import json
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

SHIM_ENTRY   = 0x08C80000
BP_GIVE      = 0x08C80018   # pass-through branch point
BP_SENDPC    = 0x08C80074   # enforcement branch point

FLAG_BYTE    = 0x0203B373   # gExpandedFlags byte holding flag 0x18FE
FLAG_MASK    = 0x40         # bit 6
VAR_ADDR     = 0x0203B76E   # gExpandedVars slot for var 0x51FD
PARTY_COUNT  = 0x02024029
MON_ADDR     = 0x0203E000   # scratch EWRAM for the synthetic mon
TRAMP_ADDR   = 0x0203DF00   # scratch EWRAM for the ARM->Thumb entry trampoline


def build_mon(species, is_egg=False):
    """Craft a minimal valid BoxPokemon (plaintext: personality=otId=0 ->
    xor key 0, substruct order index 0 = Growth,Attacks,EVs,Misc)."""
    mon = bytearray(100)
    # byte 19 flags: bit0 isBadEgg=0, bit1 hasSpecies=1
    mon[19] = 0x02
    # Growth substruct @32: species u16 at +0
    struct.pack_into("<H", mon, 32, species)
    # Misc substruct @68: IV word at +4 (offset 72), bit30 = isEgg
    ivword = 0x40000000 if is_egg else 0
    struct.pack_into("<I", mon, 72, ivword)
    # checksum @28 = sum of the 24 decrypted substruct u16s
    csum = sum(struct.unpack_from("<24H", mon, 32)) & 0xFFFF
    struct.pack_into("<H", mon, 28, csum)
    return bytes(mon)


def gdb_script(cases):
    # ARM->Thumb entry trampoline in scratch EWRAM: mGBA's stub ignores manual
    # CPSR T-bit writes, so the first shim entry goes through a real BX (which
    # sets Thumb architecturally). Later cases re-enter from Thumb context.
    #   ldr r12, [pc, #0]   ; literal at +8
    #   bx  r12
    #   .word SHIM_ENTRY|1
    tramp = struct.pack("<III", 0xE59FC000, 0xE12FFF1C, SHIM_ENTRY | 1)
    tramphex = "".join(f"{b:02x}" for b in tramp)
    lines = [
        "set pagination off",
        "set confirm off",
        "target remote :2345",
        f'python gdb.selected_inferior().write_memory({TRAMP_ADDR:#x}, bytes.fromhex("{tramphex}"))',
        f"break *{BP_GIVE:#x}",
        f"break *{BP_SENDPC:#x}",
    ]
    for i, c in enumerate(cases):
        mon = build_mon(c["species"], c.get("egg", False))
        monhex = "".join(f"{b:02x}" for b in mon)
        lines += [
            f'echo \\n=== CASE {i}: {c["name"]} ===\\n',
            # write mon struct
            f'restore /dev/stdin binary {MON_ADDR:#x}' if False else
            f'python gdb.selected_inferior().write_memory({MON_ADDR:#x}, bytes.fromhex("{monhex}"))',
            # flag / var / party count
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if c["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {c["char_id"]}',
            f'set *(unsigned char*){PARTY_COUNT:#x} = {c["party"]}',
            # point CPU at shim in Thumb state
            f'set $r0 = {MON_ADDR:#x}',
            'set $sp = 0x03007F00',
            f'set $lr = {SHIM_ENTRY:#x}',   # never returned to; both BPs hit first
            # first case enters via the ARM trampoline (BX establishes Thumb);
            # later cases start from Thumb context and can jump directly
            (f'set $pc = {TRAMP_ADDR:#x}' if i == 0 else f'set $pc = {SHIM_ENTRY:#x}'),
            "continue",
            'printf "STOPPED_AT=%08x\\n", $pc',
        ]
    lines += ["detach", "quit"]
    return "\n".join(lines) + "\n"


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "build" / "radicalred_cm.gba")

    with open(ROOT / "tools" / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = [c for c in manifest["characters"] if "roster_species_ids" in c]
    red_idx = next(i for i, c in enumerate(chars) if c["character"] == "Red") + 1
    # find a character whose expanded bitmap allows Meowth (52): family base is Meowth itself
    bitmaps = (ROOT / "tools" / "character_mode" / "rosters_expanded.bin").read_bytes()
    meowth_ok_idx = None
    meowth_ok_name = None
    for i, c in enumerate(chars):
        bm = bitmaps[i*172:(i+1)*172]
        if bm[52 >> 3] & (1 << (52 & 7)):
            meowth_ok_idx = i + 1
            meowth_ok_name = c["character"]
            break
    assert meowth_ok_idx, "no character allows Meowth?!"

    cases = [
        {"name": "flag off -> give",                       "flag": 0, "char_id": red_idx, "party": 1, "species": 25, "expect": BP_GIVE},
        {"name": "party empty -> give (soft-lock guard)",  "flag": 1, "char_id": red_idx, "party": 0, "species": 52, "expect": BP_GIVE},
        {"name": "Red + Pikachu -> give (on roster)",      "flag": 1, "char_id": red_idx, "party": 1, "species": 25, "expect": BP_GIVE},
        {"name": "Red + Meowth -> PC (off roster)",        "flag": 1, "char_id": red_idx, "party": 1, "species": 52, "expect": BP_SENDPC},
        {"name": "char 0 -> give",                         "flag": 1, "char_id": 0,       "party": 1, "species": 52, "expect": BP_GIVE},
        {"name": "Red + Meowth EGG -> give (eggs exempt)", "flag": 1, "char_id": red_idx, "party": 1, "species": 52, "egg": True, "expect": BP_GIVE},
        {"name": "char 185 out of range -> give",          "flag": 1, "char_id": 185,     "party": 1, "species": 52, "expect": BP_GIVE},
        {"name": f"{meowth_ok_name} + Meowth -> give (their roster differs)",
                                                           "flag": 1, "char_id": meowth_ok_idx, "party": 1, "species": 52, "expect": BP_GIVE},
        {"name": "Red + species 1375 (Chillet, off-roster) -> PC",
                                                           "flag": 1, "char_id": red_idx, "party": 1, "species": 1375, "expect": BP_SENDPC},
    ]

    script = HERE / "shim_test.gdb"
    script.write_text(gdb_script(cases))

    emu = subprocess.Popen(["mgba-qt", "-g", rom],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)  # let the stub come up
        r = subprocess.run(["gdb-multiarch", "-nx", "-batch", "-x", str(script)],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout
    finally:
        emu.terminate()
        try:
            emu.wait(timeout=5)
        except subprocess.TimeoutExpired:
            emu.kill()

    stops = [int(m, 16) for m in re.findall(r"STOPPED_AT=([0-9a-f]+)", out)]
    print(out[-3000:] if len(out) > 3000 else out)
    if len(stops) != len(cases):
        print(f"FATAL: expected {len(cases)} stops, got {len(stops)}")
        print(r.stderr[-2000:])
        return 1

    failures = 0
    print("\n=== RESULTS ===")
    for c, got in zip(cases, stops):
        ok = got == c["expect"]
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {c['name']}: stopped at {got:#x} "
              f"(expected {c['expect']:#x})")
    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
