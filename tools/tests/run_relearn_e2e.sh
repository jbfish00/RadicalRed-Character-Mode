#!/bin/sh
# LIVE layer for the any-level relearner (QoL A2, 2026-10-24; inject_character_mode.relearn_any_level).
# The test ROM hatches a Magikarp (Lv1, Splash) and runs the Move Maniac's ChooseMonForMoveRelearner with Character
# Mode off; the count must be > 0. The --no-hook ROM (the level-gate beq restored) must count 0.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_relearn_test.lua
STATE=/tmp/rr_ss_bedroom.ss
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_relearn_testrom.py >/dev/null
python3 tools/tests/build_relearn_testrom.py --no-hook >/dev/null
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_reltest.gba > /tmp/rr_relearn_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
fail=0
rel_case() {  # rom WANT label
    log=/tmp/rr_relearn_$2.log
    CM_EXPECT_CHECKS=2 WANT=$2 timeout 300 "$MGBA" --script "$SCRIPT" "build/$1" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] relearner $3 ($(grep -ao 'RELEARN count=[0-9]*' "$log" | tail -1))"
    else
        echo "[FAIL] relearner $3 (see $log)"; grep -a "HARNESS" "$log" | tail -6
        fail=1
    fi
}
rel_case radicalred_cm_reltest.gba pos "any level, CM off"
rel_case radicalred_cm_reltest_nohook.gba zero "NEGATIVE CONTROL (level gate restored -> 0)"
exit $fail
