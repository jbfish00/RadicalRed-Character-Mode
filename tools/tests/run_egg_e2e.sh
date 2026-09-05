#!/bin/sh
# LIVE egg-hatch e2e (../game_plans/rowe_parity.md §13.21 item 1).
#
# The hatch hook shipped 2026-09-03 verified statically (five checks in
# verify_artifacts.py, negative-tested 6/6) -- but until this suite no hatch had
# ever been WALKED in an emulator here, so "the hatch calls the sweep" rested
# entirely on reading bytes. It matters most in THIS game: 33 reachable gift
# eggs (docs/GIFT_EGGS.md), including a vendor that sells a random "Wonder Egg".
#
# tools/tests/build_egg_testrom.py repoints the bedroom console's yes-branch at
#   giveegg 60 ; giveegg 60 ; setvar 0x8004,0 ; goto <hatch script>
# and everything after the goto is SHIPPED. Poliwag 60 is deliberate: ON Misty's
# roster, OFF Red's, so one species discriminates all three cases. The second
# egg is an anchor -- the bedroom checkpoint is before the starter, so without
# it the sweep's never-empty rule would keep the hatchling and prove nothing.
#
# Four runs, and the fourth is the point: with the splice reverted the same run
# must FAIL, or the layer only tests that the sweep works when something calls
# it. Exit 0 = all four behaved.
set -e
cd "$(dirname "$0")/../.."

MGBA=../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless
SCRIPT=tools/mgba_scripts/cm_egg_hatch_test.lua
STATE=/tmp/rr_ss_bedroom.ss

[ -f "$MGBA" ] || { echo "SKIP: mgba-headless not found at $MGBA"; exit 0; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }

python3 tools/tests/build_egg_testrom.py 60
python3 tools/tests/build_egg_testrom.py 60 --no-hook

if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_eggtest.gba > /tmp/rr_egg_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi

# CM_SweepPartyToPC moves on every shim rebuild; a stale literal here would
# report "the tail never reached the sweep" on a ROM where it plainly did.
CM_SWEEP_ADDR=$(arm-none-eabi-nm build/character_mode.elf \
    | awk '/ T CM_SweepPartyToPC$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_SWEEP_ADDR" ] || { echo "  FAIL locating CM_SweepPartyToPC"; exit 1; }
export CM_SWEEP_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (sweep @ $CM_SWEEP_ADDR)"

fail=0
egg_case() {  # name  CM_ON  CM_CHAR  EXPECT  ROM
    log=/tmp/rr_egg_$1.log
    CM_EXPECT_CHECKS=5 CM_ON=$2 CM_CHAR=$3 EXPECT=$4 CM_SHOT_PREFIX=/tmp/rr_egg_$1 \
        timeout 260 "$MGBA" --script "$SCRIPT" "$5" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] egg hatch $1 (5 checks)"
    else
        echo "[FAIL] egg hatch $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
EGGROM=build/radicalred_cm_eggtest.gba
egg_case red   1 1  box   "$EGGROM"
egg_case misty 1 10 party "$EGGROM"
egg_case off   0 1  party "$EGGROM"

# ⭐ The negative control. No CM_EXPECT_CHECKS: the run must die on the missing
# sweep, not on a tally mismatch, or a future harness change could keep this
# "failing" for the wrong reason and the layer would stop discriminating.
log=/tmp/rr_egg_nohook.log
CM_ON=1 CM_CHAR=1 EXPECT=box CM_SHOT_PREFIX=/tmp/rr_egg_nohook \
    timeout 260 "$MGBA" --script "$SCRIPT" \
    build/radicalred_cm_eggtest_nohook.gba > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "reached the sweep (timeout)" "$log"; then
    echo "[PASS] egg hatch NEGATIVE CONTROL (hook absent -> layer fails)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
