#!/bin/sh
# LIVE e2e for the PC second guard (ROWE's IsRemovingLastAllowedPartyMon;
# src/pc_guard.c; verify_artifacts section 18). The test ROM gives Pikachu and
# Poliwag eggs, hatches both inline and opens the SHIPPED storage system; the
# layer deposits Pikachu. ⭐ With an alive Poliwag beside it VANILLA ALLOWS that
# deposit, so only the guard can refuse -- and only for Red (Pikachu on his
# roster, Poliwag off). The swap is asserted while the PC is still open.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_pc_guard_test.lua
STATE=/tmp/rr_ss_bedroom.ss
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_pcguard_testrom.py >/dev/null
python3 tools/tests/build_pcguard_testrom.py --no-guard >/dev/null
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_pcguard.gba > /tmp/rr_pcg_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
CM_GUARD_ADDR=$(arm-none-eabi-nm build/pc_guard.elf \
    | awk '/ T CM_PSSLastMonGuard$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_GUARD_ADDR" ] || { echo "  FAIL locating CM_PSSLastMonGuard"; exit 1; }
CM_PSS_ADDR=$(python3 -c "
import sys, struct
sys.path.insert(0, 'tools/character_mode')
import pc_hook
d = open('build/radicalred_cm.gba','rb').read()
off = pc_hook.SPECIALS_TABLE_ADDR - 0x08000000 + pc_hook.SPECIAL_PC * 4
print('0x%08X' % (struct.unpack_from('<I', d, off)[0] & ~1))")
export CM_GUARD_ADDR CM_PSS_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (guard @ $CM_GUARD_ADDR, storage special @ $CM_PSS_ADDR)"
fail=0
guard_case() {  # name  CM_ON  CM_CHAR  EXPECT  CHECKS  ROM
    log=/tmp/rr_pcg_$1.log
    CM_EXPECT_CHECKS=$5 CM_ON=$2 CM_CHAR=$3 EXPECT=$4 CM_SHOT_PREFIX=/tmp/rr_pcg_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$6" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] PC guard $1 ($5 checks)"
    else
        echo "[FAIL] PC guard $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
ROM=build/radicalred_cm_pcguard.gba
guard_case red   1 1  refused   4 "$ROM"   # Pikachu ON, Poliwag OFF -> refused
guard_case misty 1 10 deposited 3 "$ROM"   # Pikachu OFF            -> deposited
guard_case off   0 1  deposited 3 "$ROM"   # CM off                 -> deposited
log=/tmp/rr_pcg_noguard.log
CM_ON=1 CM_CHAR=1 EXPECT=refused CM_SHOT_PREFIX=/tmp/rr_pcg_noguard \
    timeout 300 "$MGBA" --script "$SCRIPT" build/radicalred_cm_pcguard_noguard.gba \
    > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "FAIL slot 0 (the last on-roster mon) is still in the party" "$log"; then
    echo "[PASS] PC guard NEGATIVE CONTROL (guard absent -> the deposit goes through)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
