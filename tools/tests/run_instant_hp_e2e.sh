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
CM_OLD_HPBAR=1 python3 tools/inject_character_mode.py >/dev/null    # 2026-11-14: the 10-28 scale-0 patch (red bars)
python3 tools/tests/build_hpbar_testrom.py old >/dev/null
python3 tools/inject_character_mode.py >/dev/null           # back to the shipping build
python3 tools/tests/build_hpbar_testrom.py on >/dev/null
EXPECT_CASES=6
pass=0; fail=0
for tag in on nohp old; do
    ss=/tmp/rr_hp_$tag.ss; sav=/tmp/rr_hp_$tag.sav
    rm -f "$ss"; cp "rom/radicalred 4.1.sav" "$sav"
    CHECKPOINT_OUT=$ss CHECKPOINT_SAV=$sav timeout 1200 "$MGBA" \
        --script tools/mgba_scripts/mk_checkpoint_bedroom.lua build/radicalred_cm_hpbar_$tag.gba > /tmp/rr_hp_$tag.ckpt.log 2>&1 || true
done
run_case() {  # rom-tag want-instant [want-full]
    log=/tmp/rr_hp_$1_want$2${3:+_full$3}.log
    if [ ! -f /tmp/rr_hp_$1.ss ]; then echo "  (no checkpoint for $1)"; return 1; fi
    env MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=$([ -n "${3:-}" ] && echo 4 || echo 2) WANT_INSTANT=$2 ${3:+WANT_FULL=$3} SHOT_START=/tmp/rr_hp_$1_start.png timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_instant_hp_test.lua -t /tmp/rr_hp_$1.ss build/radicalred_cm_hpbar_$1.gba > "$log" 2>&1 || true
    grep -a "HP bar\|full-HP" "$log" | sed 's/^/  /'
    grep -aq "HARNESS RESULT: PASS" "$log"
}
if run_case on 1; then echo "[PASS] shipped: the HP bar snaps"; pass=$((pass+1)); else echo "[FAIL] instant (see /tmp/rr_hp_on_want1.log)"; fail=$((fail+1)); fi
if run_case nohp 0; then echo "[PASS] CM_NO_INSTANTHP: the HP bar animates (control)"; pass=$((pass+1)); else echo "[FAIL] control (see /tmp/rr_hp_nohp_want0.log)"; fail=$((fail+1)); fi
if run_case nohp 1; then echo "[FAIL] NEGATIVE CONTROL: CM_NO_INSTANTHP still passed 'instant'"; fail=$((fail+1))
else echo "[PASS] negative control: CM_NO_INSTANTHP fails 'instant' (want FAIL)"; pass=$((pass+1)); fi
# 2026-11-14 (user: bars low and red at battle start): every full-HP bar is drawn 48/48, incl. the L2 Magikarp (max HP < 48)
if run_case on 1 1; then echo "[PASS] shipped: full-HP bars are drawn full"; pass=$((pass+1)); else echo "[FAIL] full bars (see /tmp/rr_hp_on_want1_full1.log)"; fail=$((fail+1)); fi
if run_case old 1 0; then echo "[PASS] CM_OLD_HPBAR: the 10-28 patch draws a short bar (control)"; pass=$((pass+1)); else echo "[FAIL] old-patch control (see /tmp/rr_hp_old_want1_full0.log)"; fail=$((fail+1)); fi
if run_case nohp 0 1; then echo "[PASS] CM_NO_INSTANTHP: vanilla bars are drawn full"; pass=$((pass+1)); else echo "[FAIL] vanilla full bars (see /tmp/rr_hp_nohp_want0_full1.log)"; fail=$((fail+1)); fi
echo "instant HP bar live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
