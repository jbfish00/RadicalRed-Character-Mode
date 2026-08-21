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
  4. flag ON, party=1, char=Red, Sandshrew(27) -> SendMonToPC  (off-roster)
  5. flag ON, party=1, char=0 (unset)          -> pass-through
  6. flag ON, party=1, char=Red, Meowth EGG    -> pass-through (eggs exempt)
  7. flag ON, party=1, char=N+1 (out of range) -> pass-through
     (N = the manifest's character count; derived, never a literal)
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

# ⚠️ BP_GIVE / BP_SENDPC are DERIVED, not hardcoded.
#
# They used to be literal 0x08C80018 and 0x08C80074, and on 2026-08-20 adding
# four instructions to the top of the shim (the Species Randomizer exclusion)
# moved every offset behind them. 0x08C80018 landed inside the new guard, which
# EVERY call passes through -- so all nine cases "stopped at 0x08C80018" and the
# two enforcement cases failed. The give/PC decision was fine; the test had
# simply stopped being able to see it. A hardcoded address in this repo has now
# misled a session four times, and it never presents as a moved address.
#
# The anchor is semantic instead: the single `ldr rX, =GiveMonToPlayer` and the
# single `ldr rX, =SendMonToPC` in the shim. Which of those two the shim
# reaches IS the behaviour under test.
def _derive_branch_points():
    import struct as _s
    rom = (ROOT / "build" / "radicalred_cm.gba").read_bytes()
    def w32(a): return _s.unpack_from("<I", rom, a - 0x08000000)[0]
    def hw(a):  return _s.unpack_from("<H", rom, a - 0x08000000)[0]
    end = SHIM_ENTRY
    while any(b != 0xFF for b in rom[end - 0x08000000:end - 0x08000000 + 0x10]):
        end += 0x10
    out = {}
    for name, target in (("give", 0x0907D791), ("pc", 0x090B6E39)):
        pools = [a for a in range(SHIM_ENTRY, end, 4) if w32(a) == target]
        sites = []
        for a in range(SHIM_ENTRY, end, 2):
            v = hw(a)
            if (v & 0xF800) == 0x4800:            # ldr rX,[pc,#imm8*4]
                if ((a + 4) & ~3) + (v & 0xFF) * 4 in pools:
                    sites.append(a)
        if len(sites) != 1:
            raise SystemExit("shim_unit_test: expected exactly one loader for "
                             "%s, found %d (%s) -- the shim's shape changed"
                             % (name, len(sites), [hex(s) for s in sites]))
        out[name] = sites[0]
    if out["give"] == out["pc"]:
        raise SystemExit("shim_unit_test: give and PC resolve to the same "
                         "address; the test cannot discriminate")
    return out["give"], out["pc"]


BP_GIVE, BP_SENDPC = _derive_branch_points()

FLAG_BYTE    = 0x0203B373   # gExpandedFlags byte holding flag 0x18FE
FLAG_MASK    = 0x40         # bit 6
VAR_ADDR     = 0x0203B76E   # gExpandedVars slot for var 0x51FD
PARTY_COUNT  = 0x02024029
MON_ADDR     = 0x0203E000   # scratch EWRAM for the synthetic mon
TRAMP_ADDR   = 0x0203DF00   # scratch EWRAM for the ARM->Thumb entry trampoline

# --- encounter marker (../../game_plans/rowe_parity.md §3) ---
# Observation point is the small wrapper the intro tail calls, which
# CM_BattleStringGated always tail-calls -- so whatever r0 it is entered with IS
# the shim's decision. The wrapper itself never runs.
MARKER_WRAPPER = 0x080D77F4
MARKER_ADDR    = 0x08379000
MARKER_STRIDE  = 64
TEXT_WILD_A    = 0x083FD284
TEXT_WILD_B    = 0x083FD297
# Something that is NOT a wild intro: the two-wild string. It must pass
# through untouched, or the marker would be rewriting unrelated battle text --
# and it is the string a DOUBLE wild battle uses, which we deliberately leave
# unmarked.
TEXT_TWO_WILD  = 0x083FD2BF
ENEMY_PARTY    = 0x0202402C   # gPlayerParty(0x02024284) - 6*100, = pokefirered's


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


def gdb_script(cases, marker_cases, marker_entry):
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
        f"break *{MARKER_WRAPPER:#x}",
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
    for i, c in enumerate(marker_cases):
        mon = build_mon(c["species"])
        monhex = "".join(f"{b:02x}" for b in mon)
        lines += [
            f'echo \\n=== MARKER {i}: {c["name"]} ===\\n',
            f'python gdb.selected_inferior().write_memory({ENEMY_PARTY:#x}, bytes.fromhex("{monhex}"))',
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if c["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {c["char_id"]}',
            f'set $r0 = {c["src"]:#x}',
            'set $sp = 0x03007F00',
            f'set $lr = {BP_GIVE:#x}',
            f'set $pc = {marker_entry:#x}',
            "continue",
            'printf "MARKER_R0=%08x\\n", $r0',
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
        {"name": "Red + Sandshrew -> PC (off roster)",     "flag": 1, "char_id": red_idx, "party": 1, "species": 27, "expect": BP_SENDPC},  # was Meowth(52) until 2026-07-23: Persian joined Red's curated roster
        {"name": "char 0 -> give",                         "flag": 1, "char_id": 0,       "party": 1, "species": 52, "expect": BP_GIVE},
        {"name": "Red + Meowth EGG -> give (eggs exempt)", "flag": 1, "char_id": red_idx, "party": 1, "species": 52, "egg": True, "expect": BP_GIVE},
        # DERIVED: the first index past the table, not a literal. A hardcoded 211
        # silently became a VALID character when the 2026-07-25 roster audit took
        # the count to 238, and the case then failed as "expected give, got PC" --
        # which looks like a shim bug and is really a stale fixture.
        {"name": f"char {len(chars) + 1} out of range -> give", "flag": 1, "char_id": len(chars) + 1, "party": 1, "species": 52, "expect": BP_GIVE},
        {"name": f"{meowth_ok_name} + Meowth -> give (their roster differs)",
                                                           "flag": 1, "char_id": meowth_ok_idx, "party": 1, "species": 52, "expect": BP_GIVE},
        {"name": "Red + species 1375 (Chillet, off-roster) -> PC",
                                                           "flag": 1, "char_id": red_idx, "party": 1, "species": 1375, "expect": BP_SENDPC},
    ]

    script = HERE / "shim_test.gdb"
    # --- encounter marker (2026-08-21) ---------------------------------------
    # Entry resolved from the SHIPPED ROM's own BL, not assumed: decode the
    # retargeted BL at 0x0D77DE and use exactly what it reaches.
    romdata = open(rom, "rb").read()
    _h1, _h2 = struct.unpack_from("<HH", romdata, 0x0D77DE)
    assert (_h1 & 0xF800) == 0xF000 and (_h2 & 0xF800) == 0xF800, "not a BL"
    _off = ((_h1 & 0x7FF) << 12) | ((_h2 & 0x7FF) << 1)
    if _off & 0x400000:
        _off -= 0x800000
    marker_entry = 0x08000000 + 0x0D77DE + 4 + _off
    assert marker_entry != MARKER_WRAPPER, (
        "the marker BL still points at the vanilla wrapper -- not injected")
    print(f"marker entry (decoded from the shipped BL): {marker_entry:#x}")

    STRIDE = 172

    def allows(ci0, sp):
        return bool(bitmaps[ci0 * STRIDE + (sp >> 3)] & (1 << (sp & 7)))

    red0 = red_idx - 1
    red_on = next(sp for sp in range(1, 1000) if allows(red0, sp))
    red_off = next(sp for sp in range(1, 1000) if not allows(red0, sp))
    # ⚠️ NOT meowth_ok_idx: it resolves to Red himself in this build, which made
    # the "different character" control compare slot 0 against slot 0 and
    # discriminate nothing while reporting PASS. Pick a character that is
    # genuinely a DIFFERENT, OFFERED index, and assert it.
    other0 = next(i for i, c in enumerate(chars)
                  if i != red0 and not c.get("hidden")
                  and any(allows(i, sp) for sp in range(1, 1000)))
    assert other0 != red0, "the discrimination control must use another character"
    other_on = next(sp for sp in range(1, 1000) if allows(other0, sp))

    def marker_for(ci0):
        return MARKER_ADDR + ci0 * MARKER_STRIDE

    marker_cases = [
        # The positive claim. Everything else here is an absence.
        {"name": "CM on, Red, on-roster -> marker", "flag": 1,
         "char_id": red_idx, "species": red_on, "src": TEXT_WILD_A,
         "expect": marker_for(red0)},
        # THE control that matters: a different character must get a DIFFERENT
        # string. A shim that ignored charId and always returned the first
        # character's marker would pass every other case here.
        {"name": f"CM on, {chars[other0]['character']} (char {other0 + 1}) -> its OWN marker",
         "flag": 1,
         "char_id": other0 + 1, "species": other_on, "src": TEXT_WILD_A,
         "expect": marker_for(other0)},
        # The second copy of the string must be matched too -- the whole reason
        # the shim tests both is that they could not be told apart statically.
        {"name": "CM on, on-roster, SECOND string copy -> marker", "flag": 1,
         "char_id": red_idx, "species": red_on, "src": TEXT_WILD_B,
         "expect": marker_for(red0)},
        {"name": "CM on, OFF-roster mon -> vanilla string", "flag": 1,
         "char_id": red_idx, "species": red_off, "src": TEXT_WILD_A,
         "expect": TEXT_WILD_A},
        {"name": "CM off -> vanilla string", "flag": 0,
         "char_id": red_idx, "species": red_on, "src": TEXT_WILD_A,
         "expect": TEXT_WILD_A},
        # The two-wild (double battle) string is deliberately never marked.
        {"name": "the two-wild string is never substituted", "flag": 1,
         "char_id": red_idx, "species": red_on, "src": TEXT_TWO_WILD,
         "expect": TEXT_TWO_WILD},
    ]

    script.write_text(gdb_script(cases, marker_cases, marker_entry))

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
    mresults = [int(m, 16) for m in re.findall(r"MARKER_R0=([0-9a-f]+)", out)]
    print(out[-3000:] if len(out) > 3000 else out)
    if len(stops) != len(cases) or len(mresults) != len(marker_cases):
        print(f"FATAL: expected {len(cases)} stops + {len(marker_cases)} marker "
              f"results, got {len(stops)} + {len(mresults)}")
        print(r.stderr[-2000:])
        return 1

    failures = 0
    print("\n=== RESULTS ===")
    for c, got in zip(cases, stops):
        ok = got == c["expect"]
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {c['name']}: stopped at {got:#x} "
              f"(expected {c['expect']:#x})")
    for c, got in zip(marker_cases, mresults):
        ok = got == c["expect"]
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] marker: {c['name']}: "
              f"r0={got:#010x} (expected {c['expect']:#010x})")
    # Derived from the case lists, NOT hand-summed: the sibling repo's total was
    # a hand-written expression and six new cases ran uncounted for a while.
    total = len(cases) + len(marker_cases)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
