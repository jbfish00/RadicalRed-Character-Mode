# GIFT EGGS — Radical Red v4.1

**33 `giveegg` sites, all reachable from dialogue, and as of 2026-09-03 all
GATED.** Measured and then closed the same day. Pinned by
`tools/tests/check_gift_eggs.py` (5 checks, negative-tested 7/7); the hook
itself is pinned by five checks in `verify_artifacts.py`, negative-tested 6/6
by `tools/tests/egg_hook_negative_test.py`.

✅ **THE HOOK IS IN** (`tools/character_mode/egg_hook.py`). The hatch script's
tail at `0x081BF54F` is overlaid with a `goto` into an 11-byte replayed tail at
`0x08C8F000` that ends `callnative CM_SweepPartyToPC`, **after** the hatch's
waitstate — so the sweep sees the hatched Pokemon, not the egg, and the egg
exemption inside the sweep no longer applies to it. Build `3354e257`;
`verify_artifacts` **104**, `shim_unit_test` 15/15, boot 4/4.

✅ **AND IT IS NOW PROVEN LIVE, NOT ONLY STATICALLY** (2026-09-04,
`sh tools/tests/run_egg_e2e.sh`, four cases, ~15 s; the PC-exit hook has its
own live layer beside it, `run_pc_e2e.sh`). `build_egg_testrom.py`
repoints the bedroom console at `giveegg 60; giveegg 60; setvar 0x8004,0;
goto <hatch script>` — every byte after the `goto` is shipped — and
`cm_egg_hatch_test.lua` walks the hatch and asserts the **swap**: the egg's own
personality is in the PC (Red, off-roster), or still in the party (Misty,
on-roster; and CM off). A fourth run on a `--no-hook` ROM must **FAIL**, which
is what makes the other three mean anything.

⚠️ **Two eggs, and the second is load-bearing**: the bedroom checkpoint is
before the starter, so with one egg the sweep's never-empty rule would keep the
hatchling and the run would go green having proven nothing. Eggs are exempt from
the sweep, so an unhatched second egg anchors the party without being a roster
decision.

⭐ **The finding that made this cheap: the hatch path is untouched CFRU donor
code, so this ROM's hatch caller (`0x0806D704`) and hatch script (`0x081BF546`)
are BYTE-IDENTICAL to Unbound's, at the same addresses.** Diffed, not assumed.
The only divergence is how the sweep is invoked — Unbound repoints a dead
`gSpecials` slot, this repo emits `callnative` (0x23) directly, which it already
does in its selection script. **Check this first in any other CFRU hack.**

🔴 **This game has an egg ECONOMY, not an egg event.** Two of the three sources
are repeatable purchases, and one of them advertises a random species.

| source | sites | what it gives |
|---|---|---|
| **Shard exchange** | 27 | a starter Egg; the Shard's type picks the pool ("The pool for Fire Starters are Cyndaquil, Chimchar…"), the script picks within it |
| **the ¥5000 Egg vendor** | 6 | *"I have an egg sent to me by a friend. Even he doesn't know where it's from!"* — species 283, 778 and 92 across three branches |
| *(dialogue only)* | — | the same vendor also offers a **"Wonder Egg that just contains a random first form Pokemon"** and a **"Paldean Egg"**; those species are **not** `giveegg` operands and are not visible to this scan |

## How off-roster is it

Measured against `rosters_expanded.bin`, the bitmaps this ROM actually
enforces, over the **210 offered** characters:

- the 29 distinct species across all 33 sites: **median offered character
  finds 97% of them off-roster**; min 45%, max 100%
- **102 of 210 offered characters have NO on-roster outcome at all** — for
  them every egg in this game hatches into a permanent off-roster party member

## How this was measured, and the primitive that does NOT work

`tools/tests/check_gift_eggs.py` is the tool; run it, it is fast and needs
nothing but the base ROM and this repo's own donor tree.

⭐ **The obvious scan is useless, and knowing why is the transferable part.**
`giveegg` is opcode `0x7A` followed by a `u16`. Scanning a ROM for that byte
pattern with a plausible species operand gives, measured on Radical Red,
**3,249 raw candidates**. Filtering on "some aligned ROM word points into the
512 bytes before it, and the script decodes cleanly forward to a terminator"
cuts that to **116** — of which, on inspection, **zero were real**. Script
bytecode is not word-aligned (so an aligned-pointer filter has false negatives
as well as false positives) and one command in isolation is indistinguishable
from data.

✅ **What works is an anchor data cannot cheaply fake**: the byte pair `0F 00`
(`loadword` into destination 0) followed by a ROM pointer whose target decodes
as Gen 3 text. Every dialogue script contains one. Decode linearly from each
anchor, follow `goto`/`call`/`goto_if`/`call_if`, and record every `giveegg`
reached. That is a reachability claim about the script graph, not a byte
pattern. **It was validated on a known positive before it was believed** — the
stock Emerald Lavaridge hot-spring script, which decodes to `giveegg 360`
(Wynaut) in both Emerald ports.

⚠️ **AND THE TEXT SEARCH FOUND WHAT THE OPCODE SCAN CANNOT.** Radical Red's egg
vendor advertises *"a Wonder Egg that just contains a random first form
Pokemon"*; a species that is **computed in native code never appears as a
`giveegg` operand at all**. The inventory is a **floor on the reachable gift
eggs, not a ceiling**. Two independent primitives were used here — decode the
script graph, and read the game's own dialogue — and each found sites the other
did not.

## What this inventory does NOT cover

- **Day Care breeding.** Deliberately out of scope and believed safe: a roster
  stores whole evolution families and only on-roster parents can be kept, so
  offspring are on-roster by construction. Gift eggs are the way in.
- **Eggs whose species is computed in native code** (see above).
- **Whether each script is actually placed on a reachable map.** The scan
  proves the script exists and is entered from dialogue; it does not walk map
  event tables. For the custom content below that is not in doubt (the NPCs
  have their own new dialogue, flags and object removal), but the two stock
  Emerald hot-spring scripts are marked as inherited and their map placement is
  **unverified**.

## How the fix was done

Ported from `Unbound-Character-Mode/tools/character_mode/egg_hook.py`. Unbound's own
summary calls the hole *"the one enforcement hole reachable in ordinary
play"*. Its shape: the overworld step handler calls `ShouldEggHatch` and on a
true result runs a hatch script whose tail is `special <hatch>; waitstate;
release; end`. That tail is overlaid with a `goto` into an injected tail that
replays those commands and then runs the party-sweep special — **after** the
waitstate, so the sweep sees the hatched Pokemon rather than the egg, and the
egg exemption inside the sweep no longer applies to it.

Per-ROM reverse engineering is needed for each port: this ROM's own
`ShouldEggHatch` caller, its hatch script, and free space for the tail. Two
things Unbound checked rather than assumed, and this port must too:

1. **Nothing references the interior of the hatch script**, or the overlay
   lands mid-jump.
2. **Enough displaced bytes are available** for a 5-byte `goto`, with the
   displaced commands replayed rather than shortened.

Both happened together, as the checker requires: the verdicts are GATED **and**
`HATCH_HOOK` is set in `tools/tests/check_gift_eggs.py`. Its fifth check fails
if only one of those two is ever true.

⚠️ **Still not covered, and worth saying plainly:** the sweep boxes an
off-roster hatchling, it does not prevent the egg. That is the deliberate
design — an egg event must never block progress — so the ¥5000 vendor will
still happily sell an egg that boxes itself on hatching.

⬜ **Not yet done: a live egg-hatch test.** Every assertion here is static plus
the existing GDB layers. Unbound's port was live-tested; this one has not been
walked through a hatch in an emulator.
