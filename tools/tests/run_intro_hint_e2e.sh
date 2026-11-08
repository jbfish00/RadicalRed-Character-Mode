#!/bin/sh
# LIVE layer (QoL B9, 2026-11-08): the wild-intro roster hint in a real battle
# (src/battle_marker.c; tools/mgba_scripts/cm_intro_hint_test.lua). Wild Scyther from the
# catch test ROM's bedroom console. Scyther is on Red's roster (1), off Ash's (16).
#   shipped, Red            -> "destined for RED"
#   shipped, Ash            -> "It is not on your roster."
#   shipped, CM off         -> vanilla
#   CM_NO_OFFROSTER, Ash    -> vanilla (the discriminating control)
#   CM_NO_OFFROSTER, Ash, asked for the off-roster line -> must FAIL (negative control)
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_intro_hint_test.lua
STATE=/tmp/rr_ss_bedroom.ss
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
CM_NO_OFFROSTER=1 python3 tools/inject_character_mode.py >/dev/null
python3 tools/tests/build_catch_testrom.py >/dev/null
cp build/radicalred_cm_catchtest.gba build/radicalred_cm_hinttest_nooff.gba
python3 tools/inject_character_mode.py >/dev/null          # back to the shipping build
python3 tools/tests/build_catch_testrom.py >/dev/null
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro)..."
    cp "rom/radicalred 4.1.sav" /tmp/rr_probe.sav
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_catchtest.gba > /tmp/rr_hint_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
EXPECT_CASES=5
pass=0; fail=0
hint_case() {  # name rom CM_ON CM_CHAR EXPECT
    log=/tmp/rr_hint_$1.log
    MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=2 CM_ON=$3 CM_CHAR=$4 EXPECT=$5 \
        timeout 200 "$MGBA" --script "$SCRIPT" -t "$STATE" "$2" > "$log" 2>&1 || true
    grep -a "intro r0=" "$log" | sed 's/^/  /'
    grep -aq "HARNESS RESULT: PASS" "$log"
}
ok()  { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
if hint_case red build/radicalred_cm_catchtest.gba 1 1 marker; then ok "Red: on-roster Scyther is 'destined for RED'"; else bad "Red marker (/tmp/rr_hint_red.log)"; fi
if hint_case ash build/radicalred_cm_catchtest.gba 1 16 offroster; then ok "Ash: off-roster Scyther says 'It is not on your roster.'"; else bad "Ash off-roster line (/tmp/rr_hint_ash.log)"; fi
if hint_case off build/radicalred_cm_catchtest.gba 0 16 vanilla; then ok "CM off: vanilla intro"; else bad "CM off (/tmp/rr_hint_off.log)"; fi
if hint_case nooff build/radicalred_cm_hinttest_nooff.gba 1 16 vanilla; then ok "CM_NO_OFFROSTER control: Ash gets the vanilla intro"; else bad "control (/tmp/rr_hint_nooff.log)"; fi
if hint_case nooffneg build/radicalred_cm_hinttest_nooff.gba 1 16 offroster; then bad "NEGATIVE CONTROL: CM_NO_OFFROSTER passed 'offroster'"
else ok "negative control: CM_NO_OFFROSTER fails 'offroster' (want FAIL)"; fi
echo "intro hint live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
