#!/usr/bin/env python3
"""GDB-driven unit test for the wild-encounter override shim (Phase 7).

Same philosophy as shim_unit_test.py: run the REAL CM_CreateWildMonGated
code in the REAL emulator (mGBA's GDB stub) with controlled register/RAM
state, and observe the decision -- but this shim takes its four arguments
(species, level, monHeaderIndex, purgeParty) directly in r0-r3 (no struct
pointer), so setup is simpler: just set r0-r3 and jump to the entry.

Branch observation point: CreateWildMon's own entry (0x090C292C). Every code
path -- early-outs and a successful override alike -- tail-calls it, and r0
there holds the FINAL species: unchanged from the input if no override fired,
or the picked replacement if one did. This used to be a hardcoded offset
INSIDE the shim (0x08CE0040), which had already had to be moved once by hand
when the shim was edited and would have had to move again for the legendary
work. CreateWildMon's address is a fixed, independently documented anchor
(docs/ROUTINE_MAP.md), and nothing else executes during these trials because
the harness sets $pc into the shim directly.

Coverage:
  RATE: with Character Mode on, run many trials (letting the game's real
    RNG advance naturally between them, exactly like repeated wild
    encounters would) and check the empirical override rate lands near the
    intended rate (loose bounds -- this is a statistical check, not an exact
    one, and deliberately wide enough not to be flaky).
  EXCLUSIONS: every override result across every trial (for two different
    characters, to also confirm per-character tables differ) must be a member
    of that character's own tables, independently re-parsed from
    wild_override.bin / wild_legendary.bin here -- no shared code with the
    shim or the emitter -- and a legendary may ONLY come from the legendary
    table.
  DETERMINISTIC PICKER (2026-07-26): the statistical blocks above cannot
    prove the 1% legendary path is alive. At 1%, "zero legendaries in 200
    trials" is both what a correctly-suppressed pool looks like AND what a
    completely dead feature looks like -- the trap
    game_plans/legendary_encounters.md §5 calls the biggest risk in this
    change. So CM_PickLegendarySpecies is ALSO called directly, with the
    roll bypassed: it must return a real legendary for a character who has
    one, 0 for a character who does not, and -- after the harness sets the
    Pokedex caught flags for that character's whole pool via the game's own
    GetSetPokedexFlag -- 0 again, while a repeatable character keeps
    returning one. That is the positive direction, and both halves of the
    dex filter, with no reliance on a 1% event.
  Plus the same OFF/unset-char/out-of-range-char pass-through cases as the
  give-mon shim's decision table, adapted to this shim's inputs.

Usage: wild_encounter_shim_test.py <rom.gba>
Starts mgba-qt -g itself; requires DISPLAY. Exit 0 = all pass.
"""
import ast
import json
import os
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent

SHIM_BLOB = 0x08CE0000   # where the blob is injected; NOT the entry point
BP_CALL = 0x090C292C     # CreateWildMon's entry -- see the module docstring for why
                         # this replaced a hand-maintained offset inside the shim

FLAG_BYTE = 0x0203B373   # gExpandedFlags byte holding flag 0x18FE (same slot shim_unit_test.py uses)
FLAG_MASK = 0x40
VAR_ADDR = 0x0203B76E    # gExpandedVars slot for var 0x51FD
TRAMP_ADDR = 0x0203DF00  # scratch EWRAM for the ARM->Thumb entry trampoline
# Direct-call trials return by landing on BP_CALL, the breakpoint that is already
# set. An EWRAM landing pad was tried first and does not work: mGBA's GDB stub
# answers `E07` to a breakpoint insert outside ROM, and gdb reports it only as a
# warning, so the run silently never stops. Reuse the ROM breakpoint instead.

# Verified by disassembly in this ROM, 2026-07-26 (see src/wild_encounter_mode.c).
GETSETPOKEDEXFLAG = 0x08088E74
FLAG_SET_CAUGHT = 3
NATDEX_TABLE = 0x098218F0

SENTINEL_SPECIES = 246  # Larvitar -- confirmed absent from both Red's and Leaf's
                         # (post-2026-07-18 full-roster-rebuild) tables; Meowth(52)
                         # is no longer safe now that Red's roster grew to 71 species
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


def load_legendary_table(char_idx):
    """(repeatable, {species ids}) for the 1% pool. Independently re-parsed."""
    blob = (ROOT / "tools" / "character_mode" / "wild_legendary.bin").read_bytes()
    offs = (ROOT / "tools" / "character_mode" / "wild_legendary_offsets.bin").read_bytes()
    p = struct.unpack_from("<I", offs, char_idx * 4)[0]
    repeatable = bool(blob[p] & 0x1)
    n_fam = blob[p + 1]
    p += 2
    sids = set()
    for _ in range(n_fam):
        n_st = blob[p]; p += 1
        for _ in range(n_st):
            sid, lo, hi = struct.unpack_from("<HBB", blob, p)
            p += 4
            sids.add(sid)
    return repeatable, sids


def natdex_of(rom_path):
    """species id -> national dex number, from the ROM's own conversion table."""
    rom = Path(rom_path).read_bytes()
    base = NATDEX_TABLE - 0x08000000
    return lambda sid: struct.unpack_from("<H", rom, base + (sid - 1) * 2)[0]


def sym_addr(name):
    """A function's link address, from the built ELF. Never assumed.

    This is not defensive style, it is a bug that already bit: the shim entry was
    hardcoded as SHIM_ENTRY = 0x08CE0000 (the blob's base) and held only while
    CM_CreateWildMonGated happened to be emitted first. Adding the legendary
    picker made gcc emit a static helper first, the entry moved to +0x198, and
    every trial then jumped into the middle of CM_MatchStage -- which presented
    as the whole suite hanging until gdb's own timeout, not as a wrong address.
    Statics are local symbols ('t'), so accept either binding.
    """
    elf = ROOT / "build" / "wild_encounter_mode.elf"
    out = subprocess.run(["arm-none-eabi-nm", str(elf)], check=True,
                         capture_output=True, text=True).stdout
    m = re.search(r"^([0-9a-f]+) [tT] %s$" % re.escape(name), out, re.M)
    if not m:
        raise SystemExit("%s not in the ELF -- rebuild:\n%s" % (name, out))
    return int(m.group(1), 16)


def load_legendary_ids():
    with open(ROOT / "tools" / "character_mode" / "rr_pokedex_donor" / "data.js") as f:
        dex = ast.literal_eval(f.read())["species"]
    sys_path_added = str(ROOT / "tools" / "character_mode")
    if sys_path_added not in sys.path:
        sys.path.insert(0, sys_path_added)
    from map_species import LEGENDARY_NAMES  # noqa: E402
    return {sid for sid, info in dex.items() if info["name"] in LEGENDARY_NAMES}


def gdb_script(trials, shim_entry):
    tramp = struct.pack("<III", 0xE59FC000, 0xE12FFF1C, shim_entry | 1)
    tramphex = "".join(f"{b:02x}" for b in tramp)
    lines = [
        "set pagination off",
        "set confirm off",
        "target remote :2345",
        f'python gdb.selected_inferior().write_memory({TRAMP_ADDR:#x}, bytes.fromhex("{tramphex}"))',
        f"break *{BP_CALL:#x}",
    ]
    for i, t in enumerate(trials):
        lines.append(f'echo \\n=== TRIAL {i}: {t["name"]} ===\\n')
        kind = t.get("kind", "shim")
        if kind == "shim":
            lines += [
                f'set *(unsigned char*){FLAG_BYTE:#x} = {FLAG_MASK if t["flag"] else 0:#x}',
                f'set *(unsigned short*){VAR_ADDR:#x} = {t["char_id"]}',
                f'set $r0 = {t["species"]}',
                f'set $r1 = {t["level"]}',
                f'set $r2 = {t.get("mon_header_index", 0)}',
                f'set $r3 = {1 if t.get("purge_party", True) else 0}',
                'set $sp = 0x03007F00',
                # Trial 0 must come in through the ARM->Thumb trampoline: mGBA's
                # GDB stub ignores manual CPSR T-bit writes, so entering Thumb
                # code from an ARM context needs a real BX. Later trials re-enter
                # from the Thumb context the previous stop left behind.
                (f'set $pc = {TRAMP_ADDR:#x}' if i == 0
                 else f'set $pc = {shim_entry:#x}'),
                "continue",
                'printf "RESULT_SPECIES=%d\\n", $r0',
            ]
        else:  # a direct call: bypass the roll and exercise one function
            lines += [
                f'set $r0 = {t["r0"]}',
                f'set $r1 = {t["r1"]}',
                'set $sp = 0x03007F00',
                # Return onto BP_CALL, the breakpoint already set in ROM.
                f'set $lr = {BP_CALL | 1:#x}',
                f'set $pc = {t["func"]:#x}',
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
    red_repeat, red_leg = load_legendary_table(red_idx0)
    leaf_repeat, leaf_leg = load_legendary_table(leaf_idx0)
    assert SENTINEL_SPECIES not in red_table and SENTINEL_SPECIES not in leaf_table, (
        "sentinel species picked poorly -- pick one absent from both tables")
    assert SENTINEL_SPECIES not in red_leg and SENTINEL_SPECIES not in leaf_leg, (
        "sentinel species is in a legendary pool -- pick another")
    assert not (red_table & legendary_ids), "test fixture bug: Red's own table has a legendary in it"
    assert not (leaf_table & legendary_ids), "test fixture bug: Leaf's own table has a legendary in it"
    assert red_leg <= legendary_ids, "test fixture bug: Red's legendary pool has a non-legendary"
    assert red_leg, "test fixture bug: Red has no legendary pool to test the 1% path with"

    # A character with NO legendary at all -- the picker must return 0 for it,
    # and it also proves the shim skips the roll rather than mis-reading a
    # neighbouring block. Derived, never named: the roster audit moves
    # legendaries between characters (it put Mewtwo on Red and inverted three
    # existing fixtures once already).
    noleg_idx0 = next(i for i in range(len(chars)) if not load_legendary_table(i)[1])
    cogita_idx0 = next((i for i, c in enumerate(chars)
                        if load_legendary_table(i)[0]), None)
    assert cogita_idx0 is not None, ("no repeatable (all-legendary) character -- "
                                     "the §1.2 exemption has nothing to test")
    _cog_repeat, cogita_leg = load_legendary_table(cogita_idx0)
    natdex = natdex_of(rom)
    picker = sym_addr("CM_PickLegendarySpecies")
    shim_entry = sym_addr("CM_CreateWildMonGated")
    assert SHIM_BLOB <= shim_entry < SHIM_BLOB + 0x800, hex(shim_entry)
    print(f"shim entry {shim_entry:#x}, picker {picker:#x}")

    trials = []
    trials.append({"name": "flag off -> always passthrough", "flag": 0,
                    "char_id": red_idx0 + 1, "species": SENTINEL_SPECIES, "level": 20})
    trials.append({"name": "char 0 (unset) -> always passthrough", "flag": 1,
                    "char_id": 0, "species": SENTINEL_SPECIES, "level": 20})
    # DERIVED: first index past the table. Hardcoded as 211, this quietly became a
    # REAL character when the 2026-07-25 roster audit took the count to 238, and
    # then failed as "expected passthrough, got species 808" -- indistinguishable
    # from a shim bug at a glance.
    oor = len(chars) + 1
    trials.append({"name": f"char {oor} (out of range, {len(chars)} characters) "
                            "-> always passthrough", "flag": 1,
                    "char_id": oor, "species": SENTINEL_SPECIES, "level": 20})
    n_fixed = len(trials)

    # CM_QUICK=1 keeps the deterministic cases and drops the statistical bulk.
    # The full run is ~520 GDB round-trips and hits gdb's own timeout if anything
    # stalls, which makes it a poor tool for diagnosing a stall. Quick mode is
    # seconds, and covers every check that can fail deterministically.
    quick = os.environ.get("CM_QUICK") == "1"
    per_char = 5 if quick else N_TRIALS_PER_CHAR
    n_tobias = 5 if quick else 200

    for i in range(per_char):
        trials.append({"name": f"Red rate/exclusion trial {i}", "flag": 1,
                        "char_id": red_idx0 + 1, "species": SENTINEL_SPECIES,
                        "level": 5 + (i % 60)})
    n_red = per_char
    for i in range(per_char):
        trials.append({"name": f"Leaf rate/exclusion trial {i}", "flag": 1,
                        "char_id": leaf_idx0 + 1, "species": SENTINEL_SPECIES,
                        "level": 5 + (i % 60)})
    # Tobias: no longer a special case in the C. His roster is entirely
    # legendary, so his non-legendary pool is empty and everything he can meet
    # comes from the 1% table -- which the general rule produces, at the same
    # rate his hand-coded branch used to.
    tobias_idx0 = next(i for i, c in enumerate(chars) if c["character"] == "Tobias")
    _t_repeat, tobias_leg = load_legendary_table(tobias_idx0)
    N_TOBIAS = n_tobias
    for i in range(N_TOBIAS):
        trials.append({"name": f"Tobias 1%-rate trial {i}", "flag": 1,
                        "char_id": tobias_idx0 + 1, "species": SENTINEL_SPECIES,
                        "level": 5 + (i % 60)})

    # --- deterministic picker trials (roll bypassed) ------------------------
    # These come LAST on purpose: they set Pokedex caught flags, which would
    # suppress legendaries in every statistical trial above if they ran first.
    n_stat = len(trials)
    picker_trials = []

    def call(name, func, r0, r1):
        picker_trials.append({"kind": "call", "name": name, "func": func,
                              "r0": r0, "r1": r1})

    call("picker: Red (has a legendary, none caught) -> a real legendary",
         picker, red_idx0, 50)
    call(f"picker: {chars[noleg_idx0]['character']} (no legendary) -> 0",
         picker, noleg_idx0, 50)
    call(f"picker: {chars[cogita_idx0]['character']} (repeatable) -> a legendary",
         picker, cogita_idx0, 50)
    red_leg_dex = sorted({natdex(s) for s in red_leg})
    for d in red_leg_dex:
        call(f"dex: set caught for national dex {d} (Red's pool)",
             GETSETPOKEDEXFLAG, d, FLAG_SET_CAUGHT)
    for d in red_leg_dex:
        call(f"dex: read back caught for national dex {d}",
             GETSETPOKEDEXFLAG, d, 1)
    call("picker: Red again, whole pool now caught -> 0 (dex filter works)",
         picker, red_idx0, 50)
    cog_leg_dex = sorted({natdex(s) for s in cogita_leg})
    for d in cog_leg_dex:
        call(f"dex: set caught for national dex {d} "
             f"({chars[cogita_idx0]['character']}'s pool)",
             GETSETPOKEDEXFLAG, d, FLAG_SET_CAUGHT)
    call(f"picker: {chars[cogita_idx0]['character']} again, pool caught -> STILL "
         "a legendary (§1.2 repeatable exemption)", picker, cogita_idx0, 50)
    trials += picker_trials

    script = HERE / "wild_encounter_shim_test.gdb"
    script.write_text(gdb_script(trials, shim_entry))

    emu = subprocess.Popen(["mgba-qt", "-g", rom],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)
        r = subprocess.run(["gdb-multiarch", "-nx", "-batch", "-x", str(script)],
                           capture_output=True, text=True, timeout=900)
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
    leaf_results = results[n_fixed + n_red:n_fixed + 2 * n_red]
    tobias_results = results[n_fixed + 2 * n_red:n_stat]
    call_results = results[n_stat:]

    def rate_block(label, res, table, leg_pool, target):
        """Shared rate/exclusion checks. A legendary is now a LEGITIMATE override
        -- at 1%, from the legendary pool only -- so the old flat "never a
        legendary" assertion would fail for the wrong reason. What must still
        hold is that a legendary can only come from the legendary pool."""
        print(f"=== {label}: rate + exclusions ===")
        ov = [s for s in res if s != SENTINEL_SPECIES]
        r = len(ov) / len(res)
        print(f"    override rate: {len(ov)}/{len(res)} = {r:.1%} (target ~{target:.0%})")
        lo, hi = (0.0, 0.045) if target <= 0.01 else (0.02, 0.24)
        if quick:
            print(f"    (CM_QUICK: {len(res)} trials, rate bound not asserted)")
        else:
            check(f"{label} override rate within loose statistical bounds "
                  f"[{lo:.0%}, {hi:.1%}]", lo <= r <= hi, f"{r:.1%}")
        check(f"{label}: every override comes from one of this character's own "
              "two tables", all(s in table or s in leg_pool for s in ov),
              f"bad: {[s for s in ov if s not in table and s not in leg_pool][:5]}")
        check(f"{label}: a legendary override only ever comes from the legendary "
              "pool, never the 10% table",
              all(s in leg_pool for s in ov if s in legendary_ids),
              f"bad: {[s for s in ov if s in legendary_ids and s not in leg_pool][:5]}")
        return ov

    red_overrides = rate_block("Red", red_results, red_table, red_leg, 0.11)
    leaf_overrides = rate_block("Leaf", leaf_results, leaf_table, leaf_leg,
                                0.11 if leaf_leg else 0.10)
    check("Red and Leaf override sets differ (per-character tables really differ)",
          set(red_overrides) != set(leaf_overrides) or not red_overrides,
          f"both produced {set(red_overrides)}")

    # Tobias's roster is entirely legendary, so his ONLY pool is the 1% one --
    # the general rule reproducing what a hand-coded branch used to do.
    tobias_ov = rate_block("Tobias", tobias_results, set(), tobias_leg, 0.01)
    check("Tobias: every override is from his legendary pool "
          f"({sorted(tobias_leg)})", all(s in tobias_leg for s in tobias_ov),
          f"bad: {[s for s in tobias_ov if s not in tobias_leg][:5]}")

    # --- the deterministic half -------------------------------------------
    # Everything above is a rate test, and a rate test on a 1% event cannot tell
    # "correctly suppressed" from "never runs". These can.
    print("=== legendary picker: called directly, roll bypassed ===")
    ci = 0

    def nxt():
        nonlocal ci
        v = call_results[ci]
        ci += 1
        return v

    v = nxt()
    check("picker: Red (nothing caught yet) returns a real legendary",
          v in red_leg, f"got {v}, expected one of {sorted(red_leg)}")
    v = nxt()
    check(f"picker: {chars[noleg_idx0]['character']} (no legendary) returns 0",
          v == 0, f"got {v}")
    v = nxt()
    check(f"picker: {chars[cogita_idx0]['character']} returns a legendary",
          v in cogita_leg, f"got {v}, expected one of {sorted(cogita_leg)}")

    red_leg_dex = sorted({natdex(s) for s in red_leg})
    for _ in red_leg_dex:
        nxt()                       # the SET calls; their return value is moot
    readback = [nxt() for _ in red_leg_dex]
    # If gSaveBlock2Ptr were not yet valid this early in boot, the writes would
    # land somewhere harmless and every check below would pass vacuously. The
    # read-back is what makes that impossible.
    check(f"dex: all {len(red_leg_dex)} caught flags read back as set "
          "(the writes really landed)", all(v == 1 for v in readback),
          f"got {readback}")
    v = nxt()
    check("picker: Red returns 0 once his whole pool is caught (dex filter "
          "genuinely suppresses)", v == 0, f"got {v}")

    for _ in sorted({natdex(s) for s in cogita_leg}):
        nxt()
    v = nxt()
    check(f"picker: {chars[cogita_idx0]['character']} STILL returns a legendary "
          "with its whole pool caught (§1.2 repeatable exemption)",
          v in cogita_leg, f"got {v}, expected one of {sorted(cogita_leg)}")

    total_checks = n_fixed + (9 if quick else 12) + 6
    print(f"\n{total_checks - failures}/{total_checks} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
