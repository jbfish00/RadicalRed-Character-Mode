#!/bin/sh
# LIVE roster-display e2e (../game_plans/roster_display.md), 2026-09-27.
#
# The bedroom console's BG pointer lands on a pre-entry: with CM on it asks
# "View your Character Mode roster?"; Yes runs callnative CM_RosterOpen +
# waitstate (src/roster_display.c: a native task, ListMenu and one icon sprite),
# No and CM-off fall through to the stock console script.
#
# Four runs, and the fourth is the point: on a test-only copy whose console
# pointer is reverted to the stock script, the roster run must FAIL -- or the
# layer only proves the screen works when something calls it.
# Misty (char 10) is deliberately not #1: a per-character test on the first
# record cannot catch an indexing error. Rows come from the manifest.
set -e
cd "$(dirname "$0")/../.."

MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_roster_menu_test.lua
STATE=/tmp/rr_ss_bedroom.ss
ROM=build/radicalred_cm.gba
NEG=build/radicalred_cm_roster_neg.gba

[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }

if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        "$ROM" > /tmp/rr_roster_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi

# Negative-control ROM: the console pointer put back on the stock script.
python3 - <<'EOF'
import re, struct
src = open("tools/inject_character_mode.py").read()
off = int(re.search(r"^CONSOLE_BG_PTR_OFF\s*=\s*(0x[0-9A-Fa-f]+)", src, re.M).group(1), 16)
stock = int(re.search(r"^CONSOLE_SCRIPT\s*=\s*(0x[0-9A-Fa-f]+)", src, re.M).group(1), 16)
d = bytearray(open("build/radicalred_cm.gba", "rb").read())
assert struct.unpack_from("<I", d, off)[0] != stock, "shipped build is not repointed"
struct.pack_into("<I", d, off, stock)
open("build/radicalred_cm_roster_neg.gba", "wb").write(bytes(d))
EOF

eval "$(python3 tools/tests/roster_menu_env.py 10)"
export MGBA_HEADLESS_DEBUGGER=1 CM_CHAR=10

fail=0
run() {  # label mode checks rom want(PASS|FAIL)
    log=/tmp/rr_roster_$1.log
    MODE=$2 CM_EXPECT_CHECKS=$3 timeout 180 "$MGBA" --script "$SCRIPT" "$4" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: $5" "$log"; then
        echo "  PASS roster e2e $1 (want $5)"
    else
        echo "  FAIL roster e2e $1 (want $5, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}
run roster roster 11 "$ROM" PASS
run no     no     2  "$ROM" PASS
run off    off    2  "$ROM" PASS
run NEGATIVE_CONTROL_console_not_repointed roster 11 "$NEG" FAIL
exit $fail
