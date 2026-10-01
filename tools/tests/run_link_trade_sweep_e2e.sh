#!/bin/sh
# LIVE e2e for the link-trade sweep (src/pc_guard.c CM_LinkTradeSweepThenExpand;
# verify_artifacts section 19; rowe_parity.md §13.53). Reuses the PC-guard test
# ROM's fixture (party [Pikachu, Poliwag]) and runs the REAL
# CB2_SaveAndEndTrade from state 0 up to its hooked BL. A real link trade needs
# two consoles; this is the closest single-console run of the hook.
# ⭐ Asserts WHICH mon moved: Red boxes Poliwag, Misty boxes Pikachu, CM off
# moves nothing, and the --no-link-sweep ROM must fail the Red case.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_link_trade_sweep_test.lua
STATE=/tmp/rr_ss_bedroom.ss
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_pcguard_testrom.py >/dev/null
python3 tools/tests/build_pcguard_testrom.py --no-link-sweep >/dev/null
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_pcguard.gba > /tmp/rr_lts_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
CM_SHIM_ADDR=$(arm-none-eabi-nm build/pc_guard.elf \
    | awk '/ T CM_LinkTradeSweepThenExpand$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_SHIM_ADDR" ] || { echo "  FAIL locating CM_LinkTradeSweepThenExpand"; exit 1; }
CM_PSS_ADDR=$(python3 -c "
import sys, struct
sys.path.insert(0, 'tools/character_mode')
import pc_hook
d = open('build/radicalred_cm.gba','rb').read()
off = pc_hook.SPECIALS_TABLE_ADDR - 0x08000000 + pc_hook.SPECIAL_PC * 4
print('0x%08X' % (struct.unpack_from('<I', d, off)[0] & ~1))")
export CM_PSS_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (sweep shim @ $CM_SHIM_ADDR, storage special @ $CM_PSS_ADDR)"
fail=0
sweep_case() {  # name  CM_ON  CM_CHAR  EXPECT  ROM  SHIM
    log=/tmp/rr_lts_$1.log
    CM_EXPECT_CHECKS=6 CM_ON=$2 CM_CHAR=$3 EXPECT=$4 CM_SHIM_ADDR=$6 \
        CM_SHOT_PREFIX=/tmp/rr_lts_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$5" > "$log" 2>&1 || true
}
ROM=build/radicalred_cm_pcguard.gba
for c in "red 1 1 box1" "misty 1 10 box0" "off 0 1 none"; do
    set -- $c
    sweep_case "$1" "$2" "$3" "$4" "$ROM" "$CM_SHIM_ADDR"
    if grep -aq "HARNESS RESULT: PASS" "/tmp/rr_lts_$1.log"; then
        echo "[PASS] link-trade sweep $1 (6 checks)"
    else
        echo "[FAIL] link-trade sweep $1 (see /tmp/rr_lts_$1.log)"
        grep -a "HARNESS\|RESULT\|fixture" "/tmp/rr_lts_$1.log" | tail -8; fail=1
    fi
done
sweep_case nosweep 1 1 box1 build/radicalred_cm_pcguard_nolinksweep.gba 0
if grep -aq "HARNESS RESULT: FAIL" /tmp/rr_lts_nosweep.log \
   && grep -aq "FAIL Poliwag (off the roster) left the party" /tmp/rr_lts_nosweep.log; then
    echo "[PASS] link-trade sweep NEGATIVE CONTROL (hook absent -> Poliwag stays)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see /tmp/rr_lts_nosweep.log)"
    fail=1
fi
exit $fail
