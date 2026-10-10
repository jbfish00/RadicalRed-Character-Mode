#!/bin/sh
# LIVE layer: 100% catch for on-roster species (src/sure_catch.c; verify section 21).
# The test ROM's bedroom console gives 10 Poke Balls and starts a wild Scyther
# battle (catch rate 45, full HP); one ball is thrown through the real Bag.
# Red (1) has Scyther on his roster, Ash (16) does not. The odds are read at
# the two successors of the hooked decision. A copy with the compare restored
# must FAIL "sure" (the negative control).
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_sure_catch_test.lua
STATE=/tmp/rr_ss_bedroom.ss
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_catch_testrom.py >/dev/null
python3 tools/tests/build_catch_testrom.py --no-hook >/dev/null
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    cp "rom/radicalred 4.1.sav" /tmp/rr_probe.sav
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_catchtest.gba > /tmp/rr_sure_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
fail=0
sure_case() {  # name rom CM_ON CM_CHAR SEED EXPECT
    log=/tmp/rr_sure_$1.log
    MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=3 CM_ON=$3 CM_CHAR=$4 SEED=$5 EXPECT=$6 \
        timeout 150 "$MGBA" --script "$SCRIPT" -t "$STATE" "$2" > "$log" 2>&1 || true
    grep -aq "HARNESS RESULT: PASS" "$log"
}
for seed in 1 2 3; do
    if sure_case red$seed build/radicalred_cm_catchtest.gba 1 1 $seed sure; then
        echo "[PASS] on-roster Scyther caught at full HP (Red, seed $seed)"
    else echo "[FAIL] sure catch, seed $seed (see /tmp/rr_sure_red$seed.log)"; fail=1; fi
done
if sure_case ash build/radicalred_cm_catchtest.gba 1 16 1 vanilla; then
    echo "[PASS] off-roster (Ash) keeps the ball's own odds"
else echo "[FAIL] off-roster odds (see /tmp/rr_sure_ash.log)"; fail=1; fi
if sure_case off build/radicalred_cm_catchtest.gba 0 1 1 miss; then
    echo "[PASS] CM off: the ball's own odds, seed 1 breaks out"
else echo "[FAIL] CM off control (see /tmp/rr_sure_off.log)"; fail=1; fi
if sure_case nohook build/radicalred_cm_catchtest_nohook.gba 1 1 1 sure; then
    echo "[FAIL] NEGATIVE CONTROL: the no-hook ROM passed 'sure'"; fail=1
else echo "[PASS] sure catch NEGATIVE CONTROL (compare restored -> odds below 255)"; fi

# Early party-wide Exp. Share (src/exp_share.c): the activation wrapper puts
# item 182 in the bag and sets flag 0x906 with CM on, and grants nothing off.
python3 tools/tests/build_catch_testrom.py --expshare >/dev/null
python3 tools/tests/build_catch_testrom.py --expshare --cm-off >/dev/null
for pair in "build/radicalred_cm_expsharetest.gba granted" "build/radicalred_cm_expsharetest_off.gba none"; do
    rom=${pair% *}; want=${pair#* }
    log=/tmp/rr_expshare_$want.log
    CM_EXPECT_CHECKS=2 EXPECT=$want timeout 60 "$MGBA" --script tools/mgba_scripts/cm_exp_share_test.lua \
        -t "$STATE" "$rom" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then echo "[PASS] early Exp. Share: $want"
    else echo "[FAIL] early Exp. Share: $want (see $log)"; fail=1; fi
done
exit $fail
