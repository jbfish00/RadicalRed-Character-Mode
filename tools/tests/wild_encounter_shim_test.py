#!/usr/bin/env python3
"""GDB-driven unit test for the wild-encounter override shim (Phase 7).

Same philosophy as shim_unit_test.py: run the REAL CM_CreateWildMonGated
code in the REAL emulator (mGBA's GDB stub) with controlled register/RAM
state, and observe the decision -- but this shim takes its four arguments
(species, level, monHeaderIndex, purgeParty) directly in r0-r3 (no struct
pointer), so setup is simpler: just set r0-r3 and jump to the entry.

Branch observation point: 0x08CE0052, the single `bl <CreateWildMon thunk>`
tail call every code path funnels through (early-outs AND a successful
override both merge back to this one call site -- see the shim's
disassembly). At the breakpoint, r0 holds the FINAL species about to be
passed to the real CreateWildMon: unchanged from the input if no override
fired, or the picked replacement if one did.

Coverage (the two things the task asked for beyond the static checks
already in verify_artifacts.py):
  RATE: with Character Mode on, run many trials (letting the game's real
    RNG advance naturally between them, exactly like repeated wild
    encounters would) and check the empirical override rate lands near the
    intended 10% (loose bounds -- this is a statistical check, not an exact
    one, and deliberately wide enough not to be flaky).
  EXCLUSIONS: every override result across every trial (for two different
    characters, to also confirm per-character tables differ) must be (a) a
    member of that character's own wild_override table (independently
    re-parsed from wild_override.bin here, not shared code with the shim
    or the emitter) and (b) never a legendary/mythical species.
  Plus the same OFF/unset-char/out-of-range-char pass-through cases as the
  give-mon shim's decision table, adapted to this shim's inputs.

Usage: wild_encounter_shim_test.py <rom.gba>
Starts mgba-qt -g itself; requires DISPLAY. Exit 0 = all pass.
"""
import ast
import json
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

SHIM_ENTRY = 0x08CE0000
BP_CALL = 0x08CE0052   # `bl <CreateWildMon thunk>` -- final species is in r0 here

FLAG_BYTE = 0x0203B373   # gExpandedFlags byte holding flag 0x18FE (same slot shim_unit_test.py uses)
FLAG_MASK = 0x40
VAR_ADDR = 0x0203B76E    # gExpandedVars slot for var 0x51FD
TRAMP_ADDR = 0x0203DF00  # scratch EWRAM for the ARM->Thumb entry trampoline

SENTINEL_SPECIES = 52  # Meowth -- confirmed not on either test character's table below
N_TRIALS_PER_CHAR = 150


def load_wild_table(char_idx):
    wild_data = (ROOT / "tools" / "character_mode" / "wild_override.bin").read_bytes()
    wild_offsets = (ROOT / "tools" / "character_mode" / "wild_override_offsets.bin").read_bytes()
    off = struct.unpack_from("<I", wild_offsets, char_idx * 4)[0]
    p = off
    n_fam = wild_data[p]; p += 1
    sids = set()
    for _ in range(n_fam):
        n_st = wild_data[p]; p += 1
        for _ in range(n_st):
            sid, lo, hi = struct.unpack_from("<HBB", wild_data, p)
            p += 4
            sids.add(sid)
    return sids


def load_legendary_ids():
    with open(ROOT / "tools" / "character_mode" / "rr_pokedex_donor" / "data.js") as f:
        dex = ast.literal_eval(f.read())["species"]
    sys_path_added = str(ROOT / "tools" / "character_mode")
    if sys_path_added not in sys.path:
        sys.path.insert(0, sys_path_added)
    from map_species import LEGENDARY_NAMES  # noqa: E402
    return {sid for sid, info in dex.items() if info["name"] in LEGENDARY_NAMES}


def gdb_script(trials):
    tramp = struct.pack("<III", 0xE59FC000, 0xE12FFF1C, SHIM_ENTRY | 1)
    tramphex = "".join(f"{b:02x}" for b in tramp)
    lines = [
        "set pagination off",
        "set confirm off",
        "target remote :2345",
        f'python gdb.selected_inferior().write_memory({TRAMP_ADDR:#x}, bytes.fromhex("{tramphex}"))',
        f"break *{BP_CALL:#x}",
    ]
    for i, t in enumerate(trials):
        lines += [
            f'echo \\n=== TRIAL {i}: {t["name"]} ===\\n',
            f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if t["flag"] else 0:#x}',
            f'set *(unsigned short*){VAR_ADDR:#x} = {t["char_id"]}',
            f'set $r0 = {t["species"]}',
            f'set $r1 = {t["level"]}',
            f'set $r2 = {t.get("mon_header_index", 0)}',
            f'set $r3 = {1 if t.get("purge_party", True) else 0}',
            'set $sp = 0x03007F00',
            (f'set $pc = {TRAMP_ADDR:#x}' if i == 0 else f'set $pc = {SHIM_ENTRY:#x}'),
            "continue",
            'printf "RESULT_SPECIES=%d\\n", $r0',
        ]
    lines += ["detach", "quit"]
    return "\n".join(lines) + "\n"


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "build" / "radicalred_cm.gba")

    with open(ROOT / "tools" / "character_mode" / "characters_manifest.json") as f:
        manifest = json.load(f)
    chars = [c for c in manifest["characters"] if "roster_species_ids" in c]
    red_idx0 = next(i for i, c in enumerate(chars) if c["character"] == "Red")
    leaf_idx0 = next(i for i, c in enumerate(chars) if c["character"] == "Leaf")
    red_table = load_wild_table(red_idx0)
    leaf_table = load_wild_table(leaf_idx0)
    legendary_ids = load_legendary_ids()
    assert SENTINEL_SPECIES not in red_table and SENTINEL_SPECIES not in leaf_table, (
        "sentinel species picked poorly -- pick one absent from both tables")
    assert not (red_table & legendary_ids), "test fixture bug: Red's own table has a legendary in it"
    assert not (leaf_table & legendary_ids), "test fixture bug: Leaf's own table has a legendary in it"

    trials = []
    trials.append({"name": "flag off -> always passthrough", "flag": 0,
                    "char_id": red_idx0 + 1, "species": SENTINEL_SPECIES, "level": 20})
    trials.append({"name": "char 0 (unset) -> always passthrough", "flag": 1,
                    "char_id": 0, "species": SENTINEL_SPECIES, "level": 20})
    trials.append({"name": "char 185 (out of range) -> always passthrough", "flag": 1,
                    "char_id": 185, "species": SENTINEL_SPECIES, "level": 20})
    n_fixed = len(trials)

    for i in range(N_TRIALS_PER_CHAR):
        trials.append({"name": f"Red rate/exclusion trial {i}", "flag": 1,
                        "char_id": red_idx0 + 1, "species": SENTINEL_SPECIES,
                        "level": 5 + (i % 60)})
    n_red = N_TRIALS_PER_CHAR
    for i in range(N_TRIALS_PER_CHAR):
        trials.append({"name": f"Leaf rate/exclusion trial {i}", "flag": 1,
                        "char_id": leaf_idx0 + 1, "species": SENTINEL_SPECIES,
                        "level": 5 + (i % 60)})

    script = HERE / "wild_encounter_shim_test.gdb"
    script.write_text(gdb_script(trials))

    emu = subprocess.Popen(["mgba-qt", "-g", rom],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)
        r = subprocess.run(["gdb-multiarch", "-nx", "-batch", "-x", str(script)],
                           capture_output=True, text=True, timeout=180)
        out = r.stdout
    finally:
        emu.terminate()
        try:
            emu.wait(timeout=5)
        except subprocess.TimeoutExpired:
            emu.kill()

    results = [int(m) for m in re.findall(r"RESULT_SPECIES=(-?\d+)", out)]
    if len(results) != len(trials):
        print(out[-4000:])
        print(f"FATAL: expected {len(trials)} results, got {len(results)}")
        print(r.stderr[-2000:])
        return 1

    failures = 0

    def check(name, ok, detail=""):
        nonlocal failures
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
        failures += not ok

    print("=== fixed-case results ===")
    for i in range(n_fixed):
        ok = results[i] == SENTINEL_SPECIES
        check(trials[i]["name"], ok, f"got species {results[i]}")

    red_results = results[n_fixed:n_fixed + n_red]
    leaf_results = results[n_fixed + n_red:]

    print("=== Red: rate + exclusions ===")
    red_overrides = [s for s in red_results if s != SENTINEL_SPECIES]
    rate = len(red_overrides) / len(red_results)
    print(f"    override rate: {len(red_overrides)}/{len(red_results)} = {rate:.1%} (target 10%)")
    check("Red override rate within loose statistical bounds [2%, 22%]", 0.02 <= rate <= 0.22, f"{rate:.1%}")
    check("Red: every override is a member of Red's own wild_override table",
          all(s in red_table for s in red_overrides),
          f"bad: {[s for s in red_overrides if s not in red_table][:5]}")
    check("Red: no override is ever a legendary/mythical species",
          not any(s in legendary_ids for s in red_overrides),
          f"bad: {[s for s in red_overrides if s in legendary_ids][:5]}")

    print("=== Leaf: rate + exclusions (different character, different table) ===")
    leaf_overrides = [s for s in leaf_results if s != SENTINEL_SPECIES]
    rate2 = len(leaf_overrides) / len(leaf_results)
    print(f"    override rate: {len(leaf_overrides)}/{len(leaf_results)} = {rate2:.1%} (target 10%)")
    check("Leaf override rate within loose statistical bounds [2%, 22%]", 0.02 <= rate2 <= 0.22, f"{rate2:.1%}")
    check("Leaf: every override is a member of Leaf's own wild_override table",
          all(s in leaf_table for s in leaf_overrides),
          f"bad: {[s for s in leaf_overrides if s not in leaf_table][:5]}")
    check("Leaf: no override is ever a legendary/mythical species",
          not any(s in legendary_ids for s in leaf_overrides),
          f"bad: {[s for s in leaf_overrides if s in legendary_ids][:5]}")
    check("Red and Leaf override sets differ (per-character tables really differ)",
          set(red_overrides) != set(leaf_overrides) or not red_overrides,
          f"both produced {set(red_overrides)}")

    total_checks = n_fixed + 7
    print(f"\n{total_checks - failures}/{total_checks} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
