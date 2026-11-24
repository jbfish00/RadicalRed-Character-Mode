#!/bin/sh
# LIVE layer (move best-version crit +2, 2026-11-24): the EXP-rate test battle (Pikachu L10 vs a wild Magikarp L2, from
# the bedroom console) with the lead's move 1 forced; a breakpoint right after the battle crit routine's
# CheckTableForMove(move, gHighCriticalChanceMoves) BL (0x09081D4C) reads r0 = the move's list stage. Slash (163, in the
# crit list): 2 on the shipping hook, 1 on the `nocrit` ROM (both BLs back at CheckTableForMove); Tackle (33): 0; and
# the nocrit ROM asked for 2 must FAIL (the negative control).
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_exprate_testrom.py on >/dev/null
python3 tools/tests/build_exprate_testrom.py nocrit >/dev/null
for tag in on nocrit; do
    ss=/tmp/rr_cr_$tag.ss; sav=/tmp/rr_cr_$tag.sav
    rm -f "$ss"; cp "rom/radicalred 4.1.sav" "$sav"
    CHECKPOINT_OUT=$ss CHECKPOINT_SAV=$sav timeout 1200 "$MGBA" \
        --script tools/mgba_scripts/mk_checkpoint_bedroom.lua build/radicalred_cm_exprate_$tag.gba > /tmp/rr_cr_$tag.ckpt.log 2>&1 &
done
wait
EXPECT_CASES=4
pass=0; fail=0
run_case() {  # rom-tag move want label
    log=/tmp/rr_cr_$1_$4.log
    [ -f /tmp/rr_cr_$1.ss ] || { echo "  (no checkpoint for $1)"; return 1; }
    env MGBA_HEADLESS_DEBUGGER=1 CM_EXPECT_CHECKS=3 RATE=0 FORCE_MOVE=$2 WANT_CRIT=$3 CRIT_BP=0x09081D4C timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_exprate_test.lua -t /tmp/rr_cr_$1.ss build/radicalred_cm_exprate_$1.gba > "$log" 2>&1 || true
    grep -ao "CRIT move [0-9]* stage [0-9]*" "$log" | sort -u | tr '\n' ' ' | sed "s/^/  $4: /"; echo
    grep -aq "HARNESS RESULT: PASS" "$log"
}
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
if run_case on 163 2 slash; then ok "Slash: crit stage 2"; else bad "Slash (/tmp/rr_cr_on_slash.log)"; fi
if run_case nocrit 163 1 slash_ctl; then ok "control: Slash keeps CFRU's 1"; else bad "control (/tmp/rr_cr_nocrit_slash_ctl.log)"; fi
if run_case on 33 0 tackle; then ok "Tackle: 0"; else bad "Tackle (/tmp/rr_cr_on_tackle.log)"; fi
if run_case nocrit 163 2 neg; then bad "NEGATIVE CONTROL: nocrit still gave Slash 2"; else ok "negative control: nocrit asked for 2 fails (want FAIL)"; fi
echo "crit +2 live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
