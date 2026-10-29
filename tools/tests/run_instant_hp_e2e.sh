#!/bin/sh
# LIVE layer (QoL A3, 2026-10-28): the instant HP bar (tools/inject_character_mode.py instant_hp: CFRU's MoveBattleBar
# tail passes scale 0 / toAdd 255) in a real battle, against a CM_NO_INSTANTHP=1 build of the same tree.
#   shipped              -> instant (<= 4 frames of MoveBattleBar calls an update)
#   CM_NO_INSTANTHP      -> animated (the discriminating control)
#   CM_NO_INSTANTHP, asked for instant -> must FAIL (the negative control)
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
CM_NO_INSTANTHP=1 python3 tools/inject_character_mode.py >/dev/null
python3 tools/tests/build_hpbar_testrom.py nohp >/dev/null
python3 tools/inject_character_mode.py >/dev/null           # back to the shipping build
python3 tools/tests/build_hpbar_testrom.py on >/dev/null
EXPECT_CASES=3
pass=0; fail=0
for tag in on nohp; do
    ss=/tmp/rr_hp_$tag.ss; sav=/tmp/rr_hp_$tag.sav
    rm -f "$ss"; cp "rom/radicalred 4.1.sav" "$sav"
    CHECKPOINT_OUT=$ss CHECKPOINT_SAV=$sav timeout 1200 "$MGBA" \
        --script tools/mgba_scripts/mk_checkpoint_bedroom.lua build/radicalred_cm_hpbar_$tag.gba > /tmp/rr_hp_$tag.ckpt.log 2>&1 || true
done
run_case() {  # rom-tag want label
    log=/tmp/rr_hp_$1_want$2.log
    if [ ! -f /tmp/rr_hp_$1.ss ]; then echo "  (no checkpoint for $1)"; return 1; fi
    MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=2 WANT_INSTANT=$2 timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_instant_hp_test.lua -t /tmp/rr_hp_$1.ss build/radicalred_cm_hpbar_$1.gba > "$log" 2>&1 || true
    grep -a "HP bar:" "$log" | sed 's/^/  /'
    grep -aq "HARNESS RESULT: PASS" "$log"
}
if run_case on 1; then echo "[PASS] shipped: the HP bar snaps"; pass=$((pass+1)); else echo "[FAIL] instant (see /tmp/rr_hp_on_want1.log)"; fail=$((fail+1)); fi
if run_case nohp 0; then echo "[PASS] CM_NO_INSTANTHP: the HP bar animates (control)"; pass=$((pass+1)); else echo "[FAIL] control (see /tmp/rr_hp_nohp_want0.log)"; fail=$((fail+1)); fi
if run_case nohp 1; then echo "[FAIL] NEGATIVE CONTROL: CM_NO_INSTANTHP still passed 'instant'"; fail=$((fail+1))
else echo "[PASS] negative control: CM_NO_INSTANTHP fails 'instant' (want FAIL)"; pass=$((pass+1)); fi
echo "instant HP bar live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
