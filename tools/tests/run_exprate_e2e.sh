#!/bin/sh
# LIVE layer (EXP rate, 2026-10-29, src/exp_rate.c): the same KO (Pikachu L10 active, Magikarp L5 benched through
# the party-wide share, vs Magikarp L2) at every rate. The x1 run's gains give the others: award * N / 2
# (N = 2 3 4 6 1, never 0). The `nohook` ROM (MathMin BL restored) at rate 2 must gain exactly the x1 amounts, and
# asked for the x2 amounts it must FAIL (the negative control). Then the START list layer (cm_exprate_menu_test.lua).
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_exprate_testrom.py on >/dev/null
python3 tools/tests/build_exprate_testrom.py nohook >/dev/null
for tag in on nohook; do
    ss=/tmp/rr_er_$tag.ss; sav=/tmp/rr_er_$tag.sav
    rm -f "$ss"; cp "rom/radicalred 4.1.sav" "$sav"
    CHECKPOINT_OUT=$ss CHECKPOINT_SAV=$sav timeout 1200 "$MGBA" \
        --script tools/mgba_scripts/mk_checkpoint_bedroom.lua build/radicalred_cm_exprate_$tag.gba > /tmp/rr_er_$tag.ckpt.log 2>&1 &
done
wait
EXPECT_CASES=10
pass=0; fail=0
run_case() {  # rom-tag rate label [WANT_GAIN0 WANT_GAIN1]
    log=/tmp/rr_er_$1_$3.log
    [ -f /tmp/rr_er_$1.ss ] || { echo "  (no checkpoint for $1)"; return 1; }
    n=2; [ -n "${4:-}" ] && n=4
    env MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=$n RATE=$2 ${4:+WANT_GAIN0=$4} ${5:+WANT_GAIN1=$5} timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_exprate_test.lua -t /tmp/rr_er_$1.ss build/radicalred_cm_exprate_$1.gba > "$log" 2>&1 || true
    grep -ao "GAINS [0-9]* [0-9]*" "$log" | head -1 | sed "s/^/  $3: /"
    grep -aq "HARNESS RESULT: PASS" "$log"
}
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
if run_case on 0 x1; then ok "x1 baseline"; else bad "x1 baseline (/tmp/rr_er_on_x1.log)"; fi
G0=$(grep -ao "GAINS [0-9]* [0-9]*" /tmp/rr_er_on_x1.log | head -1 | cut -d' ' -f2)
G1=$(grep -ao "GAINS [0-9]* [0-9]*" /tmp/rr_er_on_x1.log | head -1 | cut -d' ' -f3)
[ -n "$G0" ] && [ "$G0" -ge 2 ] && [ "$G1" -ge 2 ] || { echo "no usable x1 gains ($G0 $G1)"; exit 1; }
want() { python3 -I -c "g=$1*$2//2; print(g if g else 1)"; }
for rn in "2 4 x2" "4 1 x0_5" "3 6 x3" "1 3 x1_5"; do
    set -- $rn
    if run_case on $1 $3 $(want $G0 $2) $(want $G1 $2); then ok "$3"; else bad "$3 (/tmp/rr_er_on_$3.log)"; fi
done
if run_case nohook 2 ctl $G0 $G1; then ok "control: no hook at rate 2 gains the x1 amounts"; else bad "control (/tmp/rr_er_nohook_ctl.log)"; fi
if run_case nohook 2 neg $(want $G0 4) $(want $G1 4); then bad "NEGATIVE CONTROL: no hook still gained x2"
else ok "negative control: no hook fails the x2 amounts (want FAIL)"; fi
# START > RIGHT page > Exp Rate (shipping ROM, its own bedroom checkpoint): keys -> var 0x51FC
python3 tools/tests/build_exprate_testrom.py on >/dev/null
for c in "DOWN,DOWN,A 2 down2" "UP,A 4 up" "DOWN,B 0 cancel"; do
    set -- $c; log=/tmp/rr_er_ui_$3.log
    MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=6 CM_EXPRATE_OPEN=$(arm-none-eabi-nm build/exp_rate.elf | sed -n "s/^\([0-9a-f]*\) T CM_ExpRateOpen$/0x\1/p") LIST_KEYS=$1 WANT_RATE=$2 SHOTS=/tmp/rr_er_ui_$3 timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_exprate_menu_test.lua -t /tmp/rr_er_on.ss build/radicalred_cm_exprate_on.gba > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then ok "START list $1 -> $2"; else bad "START list $1 ($log)"; fi
done
echo "EXP rate live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
