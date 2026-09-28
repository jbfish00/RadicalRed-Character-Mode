"""Shared by the test-ROM builders: put the bedroom console back on its stock
script in a TEST-ONLY ROM.

Since 2026-09-27 the shipped console BG pointer lands on the roster display's
pre-entry, which with CM ON asks "View your Character Mode roster?" before the
stock console script runs. The egg / PC / egg-battle / mugshot fixtures test
what happens AFTER the console (the hatch, the PC, the handlers), several of
them with CM on, and answering "Yes" there would open the roster instead of
their test script (measured: every CM-on egg run failed until this existed).

This refuses to act unless the pointer really is the roster pre-entry and its
CM-off branch really is the stock script, so it cannot paper over a changed
layout. The pre-entry itself -- including its "No" -> stock path -- is covered
by tools/tests/run_roster_e2e.sh.
"""
import re
import struct
from pathlib import Path

_INJ = (Path(__file__).resolve().parents[1] / "inject_character_mode.py").read_text()


def _inj(name):
    return int(re.search(rf"^{name}\s*=\s*(0x[0-9A-Fa-f]+)", _INJ, re.M).group(1), 16)


CONSOLE_BG_PTR_OFF = _inj("CONSOLE_BG_PTR_OFF")
CONSOLE_SCRIPT = _inj("CONSOLE_SCRIPT")
FLAG_CHARACTER_MODE = _inj("FLAG_CHARACTER_MODE")


def restore_stock_console(d):
    cur = struct.unpack_from("<I", d, CONSOLE_BG_PTR_OFF)[0]
    o = cur - 0x08000000
    assert (d[o] == 0x2B and struct.unpack_from("<H", d, o + 1)[0] == FLAG_CHARACTER_MODE
            and d[o + 3:o + 5] == bytes([0x06, 0x00])
            and struct.unpack_from("<I", d, o + 5)[0] == CONSOLE_SCRIPT), (
        f"console BG ptr {cur:#x} is not the roster pre-entry for {CONSOLE_SCRIPT:#x}")
    struct.pack_into("<I", d, CONSOLE_BG_PTR_OFF, CONSOLE_SCRIPT)
