# CFRU structural-donor crosswalk

Radical Red is built on the open-source Complete FireRed Upgrade (CFRU) engine (`github.com/Skeli789/Complete-Fire-Red-Upgrade`, cloned to `tools/cfru_donor/`), unlike Unbound where the closest available donor was an approximating third-party fork. This doc records whether CFRU's public source can be pattern-matched against Radical Red's compiled binary to shortcut RE.

## Verdict: partial win, real and useful, but not a full shortcut

CFRU is **not** a full pokeemerald-style decompilation. It's a hook-and-patch framework over the vanilla FireRed binary: only the subsystems CFRU specifically modifies have public C source (referencing raw vanilla addresses like `#define BattleScript_TutorialThrow ((u8*) 0x81D9A88)` inline). Subsystems CFRU doesn't touch remain closed vanilla binary with **no public source at all** — for those, this project is in exactly the same blind-RE position Unbound is.

### Where it pays off: catch + gift/static-mon delivery share ONE choke point

Reading `tools/cfru_donor/src/catching.c` and `src/build_pokemon.c` reveals a major structural simplification opportunity, **better than ROWE's original 6-separate-hook-site design**:

- `catching.c`'s `atkF0_givecaughtmon()` — the battle-script command that runs on a successful wild-Pokemon catch — calls `GiveMonToPlayer(mon)`.
- `build_pokemon.c`'s `ScriptGiveMon()` — the general-purpose "give a scripted/static/event Pokemon" function — also calls `GiveMonToPlayer(&mon)`. This is very likely also the Mystery Gift delivery path (Mystery Gift's own internals aren't public source — see below — but it plausibly hands off to this same script-give machinery, matching Unbound's own finding that Mystery Gift is script-triggered).
- Several Battle Frontier/Battle Tower rental-mon functions (`sp06A_GivePlayerFrontierMonByLoadedSpread`, `GivePlayerFrontierMonGivenSpecies`, etc.) *also* funnel through `GiveMonToPlayer`.
- `GiveMonToPlayer()` itself already has a full-party fallback baked in: `SendMonToPC(mon)` — the exact primitive ROWE's `CharacterMode_SweepPartyToPC()` needs, and it's public CFRU source (`pokemon_storage_system.c:403`).

**Implication for Phase 4 (enforcement injection)**: rather than patching separate call sites for catch and gift/static-mon delivery, a single hook inside (or wrapping) `GiveMonToPlayer` — check `IsSpeciesAllowedForCharacter`, call the existing `SendMonToPC` for rejects instead of adding to the party — covers both catch and gift/static/event Pokemon in one place, *if* Radical Red's compiled binary preserves this same centralization (unconfirmed — see caveat below).

**Important caveat / new risk this surfaces**: `GiveMonToPlayer` is also the delivery path for **Battle Frontier/Battle Tower rental mons** — these are temporary loaner teams, not part of the player's own roster, and should almost certainly NOT be roster-gated (a facility that hands out a rental Registeel would break entirely if Character Mode silently PC-boxed it). A naive hook on `GiveMonToPlayer` itself would over-block these. Mitigation options to design around in Phase 4: (a) hook closer to the two specific call sites (`atkF0_givecaughtmon`, `ScriptGiveMon`) rather than `GiveMonToPlayer` itself, or (b) have the hook check for an existing frontier/facility context flag before enforcing (the source already references `FlagGet(FLAG_BATTLE_FACILITY)` and `IsFrontierRaidBattle()` nearby in `catching.c`, suggesting a reusable signal). Record this as an explicit test case for Phase 5 (verify Battle Frontier rentals aren't wrongly roster-gated).

### Where it does NOT pay off: Mystery Gift, trade, and PC-withdraw internals are closed binary even in CFRU

- `include/mevent.h` exists but contains only two opaque stub declarations (`sub_8143D94`, `sub_8143E1C`) with no corresponding `.c` source anywhere in the tree — Mystery Gift's actual internals were never decompiled by CFRU, they're untouched vanilla FRLG binary.
- `include/trade.h` similarly has only commented-out declarations, no `trade.c` exists in `src/`. Link-trade internals are likewise untouched vanilla binary.
- `pokemon_storage_system.c` has full source for box/mon manipulation primitives (`SendMonToPC`, `SendMonToBoxPos`, etc.) but **no PC-withdraw-exit callback** (no `CB2_ExitPSS`-equivalent) — the actual "player exits the PC UI" trigger point isn't reimplemented in C by CFRU.

**Implication**: for Mystery Gift distribution, trade completion, and PC-withdraw-exit, this project is in the same position Unbound is — needs blind text/pointer-anchor RE against the compiled Radical Red ROM, CFRU's source gives no shortcut here.

## Concrete evidence gathered this session (partially bridges the caveat above)

Searched the actual `radicalred 4.1.gba` binary for the vanilla catch-message text ("Gotcha") that `atkF0_givecaughtmon`'s battle script displays:

- `"Gotcha"` (mixed-case; recall Radical Red renders mixed-case text, see `docs/ROUTINE_MAP.md`) found at file offsets `0x3FD7A2` and `0x3FD7C0`, decoding to the expected "Gotcha!\n[name] was caught!" / nickname-prompt text — same relative neighborhood Unbound found its own catch-message bank (`0x3FD790+`).
- `find_pointer_refs.py` on both offsets found exactly one reference each, at consecutive table slots `0x3FE338`/`0x3FE33C` (4 bytes apart — one array entry each).
- Dumping the surrounding region (`0x3FE200`–`0x3FE4FC`, 190+ entries) shows an unbroken run of valid `0x08xxxxxx`/`0x09xxxxxx` ROM pointers — **the same `gBattleStringsTable`-shaped large contiguous pointer array Unbound found** (Unbound's was a ~374-entry table at `0x3FDF3C`–`0x3FE514`; this one is in the same ballpark of both size and absolute location, consistent with both ROMs sharing FireRed/CFRU's underlying battle-message table layout).
- Also confirmed CFRU's expanded ball roster is present in-ROM: `"Beast Ball"` (2 hits) and `"Dream Ball"` (2 hits) both found as mixed-case text — corroborating that Radical Red really does carry CFRU's Gen 7+ ball additions referenced in `catching.c`'s `GetBaseBallCatchOdds`.

**This is real, converging evidence** (text anchor + pointer-table shape + CFRU source explaining exactly what consumes that table) that Radical Red's catch-message/battle-string infrastructure is structurally unchanged from CFRU/vanilla, and that `atkF0_givecaughtmon`/`GiveMonToPlayer` are very likely still the real in-binary catch-completion path — but the **exact function addresses in the compiled RR binary are not yet located** (would need XREF confirmation, e.g. via Ghidra, disassembling around the table's referencing call sites to find which one specifically is the battle-script command dispatcher — the next concrete step, not yet done this session).

## Time-box status

Spent roughly one focused session on this (within the plan's 1-2 session budget). **Net verdict: worth it, don't repeat from scratch** — the source-level insight (single `GiveMonToPlayer` choke point, frontier-rental caveat, Mystery-Gift/trade/PC-withdraw being closed-binary-only) is durable regardless of exact address confirmation, and the text/pointer evidence gathered is a solid head start for the next RE session. Don't re-attempt "read CFRU source cold" again — instead, next session should go straight to XREF-confirming the 26-ish call sites referencing this pointer table (mirroring Unbound's exact next step) to isolate which is `atkF0_givecaughtmon`.
