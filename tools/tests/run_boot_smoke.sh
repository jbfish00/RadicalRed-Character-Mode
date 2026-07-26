#!/bin/bash
# Boot smoke test (see boot_smoke.gdb). Runs against a given ROM;
# default is the patched build. Run it against rom/*.gba too to get an
# original-ROM baseline for comparison.
#   usage: run_boot_smoke.sh [rom.gba]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ROM="${1:-$ROOT/build/radicalred_cm.gba}"
LOG="$ROOT/build/boot_smoke.$(basename "$ROM" .gba | tr -c 'A-Za-z0-9._-' '_').log"

[ -f "$ROM" ] || { echo "ROM missing: $ROM"; exit 1; }

# Clears a leaked emulator squatting GDB port 2345. It is a BLANKET kill: the
# sibling projects in this workspace (Unbound, Seaglass, Lazarus) run their own
# `mgba-qt -g` suites on the same port, and running this while one of them is
# mid-test kills it. Set CM_NO_PKILL=1 to skip it when you know another session
# is active -- the run then simply fails on a busy port instead of stealing it.
if [ "${CM_NO_PKILL:-0}" != "1" ]; then
    pkill -f "mgba-qt -g" 2>/dev/null && sleep 1
fi

mgba-qt -g "$ROM" >/dev/null 2>&1 &
MGBA_PID=$!
trap 'kill $MGBA_PID 2>/dev/null' EXIT
sleep 5

timeout 90 gdb-multiarch -nx -batch -x "$HERE/boot_smoke.gdb" >"$LOG" 2>&1

kill $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- gdb output ($LOG) ---"
cat "$LOG"
echo "------------------"

python3 - "$LOG" <<'EOF'
import re, sys
fails = 0
checks = 0
for line in open(sys.argv[1]):
    m = re.search(r"\(want (\d+)\): (\d+)", line)
    if m:
        checks += 1
        if m.group(1) != m.group(2):
            print(f"FAIL: {line.strip()}")
            fails += 1
if checks == 0:
    print("NO CHECKS RAN — gdb session failed?")
    sys.exit(2)
print(f"{checks - fails}/{checks} checks passed")
sys.exit(1 if fails else 0)
EOF
