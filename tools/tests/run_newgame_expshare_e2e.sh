#!/bin/sh
# LIVE layer: the early party-wide Exp. Share for EVERY new game, Character Mode
# on or off (user, 2026-10-21; src/exp_share.c CM_NewGameExpShare, hooked into
# NewGameInitData's last call). Two test ROMs that differ ONLY in that BL
# (tools/tests/build_catch_testrom.py --newgame-probe [--no-newgame]) each drive
# the whole real intro from an empty save to the bedroom (CM never turned on),
# then the bedroom console records flag 0x906 (FLAG_EXP_SHARE) and checkitem 182:
#   hook kept    -> both 1 (granted)
#   hook removed -> both 0 (none: the discriminating control)
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
python3 tools/tests/build_catch_testrom.py --newgame-probe >/dev/null
python3 tools/tests/build_catch_testrom.py --newgame-probe --no-newgame >/dev/null
EXPECT_CASES=2
pass=0; fail=0
for pair in "ngprobe granted" "ngprobe_nohook none"; do
    tag=${pair% *}; want=${pair#* }
    rom=build/radicalred_cm_$tag.gba; ss=/tmp/rr_ng_$tag.ss; sav=/tmp/rr_ng_$tag.sav
    rm -f "$ss"; cp "rom/radicalred 4.1.sav" "$sav"
    CHECKPOINT_OUT=$ss CHECKPOINT_SAV=$sav timeout 1200 "$MGBA" \
        --script tools/mgba_scripts/mk_checkpoint_bedroom.lua "$rom" > /tmp/rr_ng_$tag.ckpt.log 2>&1 || true
    if [ ! -f "$ss" ]; then echo "[FAIL] new game ($tag): the intro produced no checkpoint"; fail=$((fail+1)); continue; fi
    log=/tmp/rr_ng_$tag.log
    CM_EXPECT_CHECKS=2 EXPECT=$want timeout 60 "$MGBA" --script tools/mgba_scripts/cm_exp_share_test.lua \
        -t "$ss" "$rom" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: PASS" "$log"; then
        echo "[PASS] new game, CM off: Exp. Share $want ($tag)"; pass=$((pass+1))
    else echo "[FAIL] new game, CM off: Exp. Share $want ($tag; see $log)"; fail=$((fail+1)); fi
done
echo "new-game Exp. Share live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
