#!/bin/sh
# LIVE PC-exit e2e (../game_plans/rowe_parity.md §13.33 item 1).
#
# The PC-exit hook shipped in all four GBA games on STATIC evidence alone.
# Seaglass got the first live layer on 2026-09-10; this is the port. §13.20 is
# why it matters: four live layers in three repos were once found dead behind a
# fully green static suite, and a hook with no live layer is the same claim.
#
# tools/tests/build_pc_testrom.py repoints the bedroom console's yes-branch at
#   giveegg 60 ; giveegg 60 ; setvar 0x8004,0 ; <inline hatch> ; goto 0x081A6A22
# and everything after that goto is SHIPPED. Poliwag 60 is the same
# discriminator the egg layer uses -- ON Misty's roster, OFF Red's -- so one
# species covers all three cases. The hatch is FIXTURE: it is the only way to
# get an off-roster mon INTO the party, since the gift gate boxes an off-roster
# gift on the way in and eggs are exempt everywhere.
#
# ⚠️ The second egg is an anchor. The bedroom checkpoint is before the starter,
# so the party is empty and the sweep's never-empty rule would keep the
# hatchling for EVERY character -- every run identical, green, proving nothing.
#
# Four runs, and the fourth is the point: with the PC splice reverted the same
# run must FAIL. Exit 0 = all four behaved.
set -e
cd "$(dirname "$0")/../.."

MGBA=../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless
SCRIPT=tools/mgba_scripts/cm_pc_exit_test.lua
STATE=/tmp/rr_ss_bedroom.ss

[ -f "$MGBA" ] || { echo "SKIP: mgba-headless not found at $MGBA"; exit 0; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }

python3 tools/tests/build_pc_testrom.py 60
python3 tools/tests/build_pc_testrom.py 60 --no-hook

if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm_pctest.gba > /tmp/rr_pc_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi

# CM_SweepPartyToPC moves on every shim rebuild; a stale literal would report
# "the PC exit never reached the sweep" on a ROM where it plainly did.
CM_SWEEP_ADDR=$(arm-none-eabi-nm build/character_mode.elf \
    | awk '/ T CM_SweepPartyToPC$/{printf "0x%s\n", toupper($1)}')
[ -n "$CM_SWEEP_ADDR" ] || { echo "  FAIL locating CM_SweepPartyToPC"; exit 1; }

# ⭐ The storage system's own handler, read out of the BUILT ROM's gSpecials
# table. Breakpointing it is what turns "the script ran" into "the PC opened":
# a no-op special would release its waitstate at once and the sweep would still
# fire, green, with no PC ever involved. Derived, never hardcoded.
CM_PSS_ADDR=$(python3 -c "
import sys, struct
sys.path.insert(0, 'tools/character_mode')
import pc_hook
d = open('build/radicalred_cm.gba','rb').read()
off = pc_hook.SPECIALS_TABLE_ADDR - 0x08000000 + pc_hook.SPECIAL_PC * 4
print('0x%08X' % (struct.unpack_from('<I', d, off)[0] & ~1))")
[ -n "$CM_PSS_ADDR" ] || { echo "  FAIL deriving the storage special handler"; exit 1; }
export CM_SWEEP_ADDR CM_PSS_ADDR MGBA_HEADLESS_DEBUGGER=1
echo "  (sweep @ $CM_SWEEP_ADDR, storage special @ $CM_PSS_ADDR)"

fail=0
pc_case() {  # name  CM_ON  CM_CHAR  EXPECT  ROM
    log=/tmp/rr_pc_$1.log
    CM_EXPECT_CHECKS=7 CM_ON=$2 CM_CHAR=$3 EXPECT=$4 CM_SHOT_PREFIX=/tmp/rr_pc_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$5" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] PC exit $1 (7 checks)"
    else
        echo "[FAIL] PC exit $1 (see $log)"; grep -a "HARNESS" "$log" | tail -8
        fail=1
    fi
}
PCROM=build/radicalred_cm_pctest.gba
pc_case red   1 1  box   "$PCROM"   # Poliwag OFF Red's roster   -> boxed on PC exit
pc_case misty 1 10 party "$PCROM"   # Poliwag ON  Misty's roster -> kept
pc_case off   0 1  party "$PCROM"   # CM off                     -> kept

# ⭐ The negative control. No CM_EXPECT_CHECKS: the run must die on the missing
# sweep, not on a tally mismatch, or a future harness change could keep this
# "failing" for the wrong reason and the layer would stop discriminating.
log=/tmp/rr_pc_nohook.log
CM_ON=1 CM_CHAR=1 EXPECT=box CM_SHOT_PREFIX=/tmp/rr_pc_nohook \
    timeout 300 "$MGBA" --script "$SCRIPT" \
    build/radicalred_cm_pctest_nohook.gba > "$log" 2>&1 || true
if grep -aq "HARNESS RESULT: FAIL" "$log" \
   && grep -aq "reached the shipped sweep (timeout)" "$log"; then
    echo "[PASS] PC exit NEGATIVE CONTROL (hook absent -> layer fails)"
else
    echo "[FAIL] negative control did not fail, or failed for another reason (see $log)"
    fail=1
fi
exit $fail
