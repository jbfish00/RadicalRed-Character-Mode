#!/bin/sh
# LIVE e2e for the player avatars (tools/character_mode/rr_costumes.py and
# rr_ow_player.py; verify_artifacts "costume characters"). Lucas, whom Radical
# Red's wardrobe ships a costume for, must be drawn in it after the bedroom
# reload, on the same tile. Misty has no costume but has a walk/run sheet: she
# must be drawn in that. Paul has neither: the avatar must not change. The two
# negative controls are Lucas and Misty on ROMs whose handler ends `release;
# end` instead of going to its tail: both must FAIL, or the layer is not testing
# the tails.
set -e
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_costume_test.lua
STATE=/tmp/rr_ss_bedroom.ss
ROM=build/radicalred_cm_mugshot_test.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f build/radicalred_cm.gba ] || { echo "build first: python3 tools/inject_character_mode.py"; exit 1; }
if [ ! -f "$STATE" ]; then
    echo "making the bedroom checkpoint (drives the whole intro, ~10 min)..."
    timeout 1200 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_bedroom.lua \
        build/radicalred_cm.gba > /tmp/rr_costume_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi

env_for() {
    python3 - "$1" <<'EOF2'
import json, struct, sys
name = sys.argv[1]
chars = json.load(open("tools/character_mode/characters_manifest.json"))["characters"]
idx = [c["character"] for c in chars].index(name)
# What the activation is MEANT to wear comes from the injector's manifest; where
# that id's frames live is resolved through the BUILT ROM's own two-level
# overworld lookup (the switcher at 0x091468CC, high byte = table), so a wrong
# table slot or a wrong graphics-info pointer fails here instead of agreeing
# with itself.
want = json.load(open("build/avatar_manifest.json"))[name]
rom = open("build/radicalred_cm.gba", "rb").read()
R = lambda a: a - 0x08000000
def images(gid):
    table = struct.unpack_from("<I", rom, R(0x091468CC) + (gid >> 8) * 4)[0]
    info = struct.unpack_from("<I", rom, R(table) + (gid & 0xFF) * 4)[0]
    return struct.unpack_from("<I", rom, R(info) + 0x1C)[0]
walk = want["walk"]
# With no avatar, assert that nothing draws Lucas's costume -- a sprite nobody
# else on the bedroom map uses, so "0 sprites draw it" is a real assertion.
print(f"CM_CHAR_ID={idx + 1} CM_COSTUME_WALK={walk:#x} "
      f"CM_COSTUME_IMAGES={images(walk or 0x1E1):#x}")
EOF2
}

fail=0
ran=0
costume_case() {  # label character want(PASS|FAIL) [neg]
    ran=$((ran + 1))
    python3 tools/tests/build_mugshot_testrom.py "$2" >/dev/null
    if [ "$4" = neg ]; then
        # Turn the handler's `goto <tail>` back into `release; end` (+3 nops).
        python3 - "$2" <<'EOF'
import json, struct, sys
name = sys.argv[1]
d = bytearray(open("build/radicalred_cm_mugshot_test.gba", "rb").read())
h = struct.unpack_from("<I", d, 0x105006F + 17)[0] - 0x08000000
assert d[h + 46] == 0x05, f"{name}'s handler does not goto a costume tail"
d[h + 46:h + 51] = bytes([0x6C, 0x02, 0x00, 0x00, 0x00])
open("build/radicalred_cm_mugshot_test.gba", "wb").write(bytes(d))
EOF
    fi
    log=/tmp/rr_costume_$1.log
    # shellcheck disable=SC2046
    env $(env_for "$2") CM_EXPECT_CHECKS=10 CM_SHOT_PREFIX=/tmp/rr_costume_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$ROM" > "$log" 2>&1 || true
    if grep -aq "HARNESS RESULT: $3" "$log"; then
        echo "  PASS costume e2e $1 (want $3)"
    else
        echo "  FAIL costume e2e $1 (want $3, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}
costume_case lucas_costume Lucas PASS
costume_case misty_walk_sprite Misty PASS
costume_case paul_no_avatar Paul PASS
costume_case NEGATIVE_CONTROL_tail_skipped Lucas FAIL neg
costume_case NEGATIVE_CONTROL_walk_tail_skipped Misty FAIL neg
# A literal: the case list is pinned, not counted from itself.
[ "$ran" -eq 5 ] || { echo "  FAIL ran $ran costume cases, want 5"; fail=1; }
exit $fail
