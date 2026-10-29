#!/bin/sh
# LIVE layer (QoL A3, 2026-10-28): a new game starts with battle animations off. Boot with no save; after FireRed's
# SetDefaultOptions has run, SaveBlock2+0x15 bit 2 must be set. The control is a copy of the built ROM with the base
# byte (movs r0,#3) put back: it must read 0, and must FAIL when asked for 1.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
ROM=${ROM:-build/radicalred_cm.gba}; SITE=${SITE:-0x5499C}; BASE=${BASE:-0x03}
[ -f "$ROM" ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
CTL=/tmp/cm_anim_ctl_$$.gba
python3 -c "import sys; d=bytearray(open(sys.argv[1],'rb').read()); d[int(sys.argv[3],0)]=int(sys.argv[4],0); open(sys.argv[2],'wb').write(d)" "$ROM" "$CTL" "$SITE" "$BASE"
EXPECT_CASES=3; pass=0; fail=0
for c in "$ROM 1 PASS" "$CTL 0 PASS" "$CTL 1 FAIL"; do
    set -- $c
    log=/tmp/cm_anim_$$_$2_$3.log
    WANT=$2 CM_EXPECT_CHECKS=2 MGBA_HEADLESS_DEBUGGER=1 timeout 300 "$MGBA" \
        --script tools/mgba_scripts/cm_anim_default_test.lua "$1" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: $3" "$log"; then echo "[PASS] $(basename $1) WANT=$2 -> $3"; pass=$((pass+1))
    else echo "[FAIL] $(basename $1) WANT=$2 (want $3, see $log)"; fail=$((fail+1)); fi
done
rm -f "$CTL"
echo "anim default: $pass passed, $fail failed (want $EXPECT_CASES)"
[ $fail -eq 0 ] && [ $pass -eq $EXPECT_CASES ]
