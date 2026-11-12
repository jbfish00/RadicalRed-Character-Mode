#!/bin/sh
# LIVE layer (Extras: heal + PC anywhere, 2026-11-11, src/exp_rate.c): START > RIGHT page > Extras from the bedroom
# checkpoint. Heal (lead at 1 HP + poison -> full, no status), PC (special 0x3C runs once), cancel, Exp. Rate through
# the list, and with no Pokemon the row opens the rate list at once. The CM_NO_EXTRAS build (control) asked for the
# heal must FAIL on the heal assert.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
sym() { arm-none-eabi-nm "$1" | sed -n "s/^\([0-9a-f]*\) T $2$/0x\1/p"; }
mk() {  # tag: build_exprate_testrom "on" from the current build -> its own ROM, ELF and bedroom checkpoint
    python3 tools/tests/build_exprate_testrom.py on >/dev/null
    cp build/radicalred_cm_exprate_on.gba build/radicalred_cm_extras_$1.gba; cp build/exp_rate.elf build/exp_rate_extras_$1.elf
    rm -f /tmp/rr_ex_$1.ss; cp "rom/radicalred 4.1.sav" /tmp/rr_ex_$1.sav
    CHECKPOINT_OUT=/tmp/rr_ex_$1.ss CHECKPOINT_SAV=/tmp/rr_ex_$1.sav timeout 1200 "$MGBA" \
        --script tools/mgba_scripts/mk_checkpoint_bedroom.lua build/radicalred_cm_extras_$1.gba > /tmp/rr_ex_$1.ckpt.log 2>&1 || true   # the checkpoint script asserts nothing: its exit status is not the result
    [ -f /tmp/rr_ex_$1.ss ] || { echo "no checkpoint for $1"; exit 1; }
}
CM_NO_EXTRAS=1 python3 tools/inject_character_mode.py >/dev/null; mk ctl
python3 tools/inject_character_mode.py >/dev/null; mk on
EXPECT_CASES=6
pass=0; fail=0
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
run_case() {  # tag label checks env...
    tag=$1; label=$2; n=$3; shift 3; log=/tmp/rr_ex_$label.log
    env MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=$n CM_EXTRAS_OPEN=$(sym build/exp_rate_extras_$tag.elf CM_ExtrasOpen) \
        CM_EXPRATE_OPEN=$(sym build/exp_rate_extras_$tag.elf CM_ExpRateOpen) SHOTS=/tmp/rr_ex_$label "$@" timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_extras_menu_test.lua -t /tmp/rr_ex_$tag.ss build/radicalred_cm_extras_$tag.gba > "$log" 2>&1 || true
    grep -aq "HARNESS RESULT: PASS" "$log"
}
if run_case on heal 7 EXTRAS_KEYS=DOWN,A WANT_HEAL=1; then ok "Extras > Heal party heals the lead"; else bad "heal (/tmp/rr_ex_heal.log)"; fi
if run_case on pc 7 EXTRAS_KEYS=DOWN,DOWN,A WANT_PC=1; then ok "Extras > PC opens the storage system"; else bad "pc (/tmp/rr_ex_pc.log)"; fi
if run_case on cancel 7 EXTRAS_KEYS=B; then ok "B in Extras: nothing healed, no PC"; else bad "cancel (/tmp/rr_ex_cancel.log)"; fi
if run_case on rate 7 EXTRAS_KEYS=A WANT_RATEOPEN=1; then ok "Extras > Exp. Rate opens the rate list"; else bad "rate (/tmp/rr_ex_rate.log)"; fi
if run_case on nomon 5 NO_PARTY=1 WANT_RATEOPEN=1; then ok "no Pokemon: the row opens the rate list at once"; else bad "nomon (/tmp/rr_ex_nomon.log)"; fi
if run_case ctl NEG_heal 7 EXTRAS_KEYS=DOWN,A WANT_HEAL=1 WANT_RATEOPEN=1; then bad "NEGATIVE CONTROL: CM_NO_EXTRAS still healed"
elif grep -aq "FAIL lead healed" /tmp/rr_ex_NEG_heal.log; then ok "negative control: CM_NO_EXTRAS asked for the heal fails on the heal (want FAIL)"
else bad "negative control failed for another reason (/tmp/rr_ex_NEG_heal.log)"; fi
echo "Extras live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
