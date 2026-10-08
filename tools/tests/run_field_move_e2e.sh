#!/bin/sh
# LIVE layer for field moves (src/field_moves.c; verify_artifacts section 20).
# The test ROM hatches a Magikarp (Splash only, learns no HM), sets every badge
# and asks the REAL checkpartymove and specials 0x10A-0x10C for each HM move,
# without and with HM01-HM08 in the bag; then runs FireRed's Cut-tree script
# for a photograph. ../game_plans/field_moves.md.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_field_move_test.lua
STATE=/tmp/rr_ss_bedroom.ss
CHECKS=25    # 1 party + 12 without the HM + 12 with it
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_field_testrom.py >/dev/null
python3 tools/tests/build_field_testrom.py --no-hook >/dev/null
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_fieldtest.gba > /tmp/rr_field_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
fail=0
field_case() {  # name  CM_ON  CM_CHAR
    log=/tmp/rr_field_$1.log
    CM_EXPECT_CHECKS=$CHECKS CM_ON=$2 CM_CHAR=$3 CM_SHOT_PREFIX=/tmp/rr_field_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" build/radicalred_cm_fieldtest.gba > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] field moves $1 ($CHECKS checks)"
    else
        echo "[FAIL] field moves $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
field_case red   1 1     # Red: no Magikarp on his roster
field_case misty 1 10    # a second character (Misty owns the Magikarp line)
field_case off   0 1     # CM off -> the original answer, never a mon
log=/tmp/rr_field_nohook.log
CM_ON=1 CM_CHAR=1 CM_SHOT_PREFIX=/tmp/rr_field_nohook \
    timeout 300 "$MGBA" --script "$SCRIPT" build/radicalred_cm_fieldtest_nohook.gba \
    > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "FAIL checkpartymove Cut with the HM, CM on -> slot 0" "$log" \
   && grep -aq "FAIL special 0x10A (Cut) with the HM, CM on -> slot 0" "$log"; then
    echo "[PASS] field moves NEGATIVE CONTROL (hooks absent -> Magikarp can't Cut)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
