# Routine map

RE findings/anchors for this project — the project's "symbol table". Tag every entry CONFIRMED / STRING ANCHOR / LIKELY / UNKNOWN, and record ruled-out false leads explicitly so they aren't re-tried.

## CONFIRMED — text-rendering convention differs from vanilla FireRed/Unbound

Radical Red uses **mixed-case text**, not vanilla FRLG's ALL-CAPS convention:
- `"TRAINER"` (all caps): 0 hits. `"Trainer"` (mixed case, `--icase`): **360 hits**.
- `"POKEMON"` (all caps): 0 hits. `"Pokemon"` (mixed case): 5 hits. `"pokemon"` (lowercase): 1 hit.
- `"SAVE"` (all caps, exact case): 1 hit at file offset `0x0110004E`, decodes to a developer diagnostic string: *"WRONG SAVE TYPE! Please change to Flash 128k. Consult the Discord if you need help."* — confirms this is genuinely Radical Red's own custom content (not vanilla leftover text) and that it targets Flash 128k save type.

**Implication for all future `search_gametext.py` runs on this ROM: always pass `--icase`, or better, search for the expected mixed-case rendering directly** (e.g. `"Trainer"` not `"TRAINER"`) — plain vanilla-style all-caps queries will silently miss almost everything. This is a real divergence from both vanilla FRLG and Unbound's apparent text convention, worth remembering before assuming any porting the Unbound anchors 1:1.

## STRING ANCHOR — catch-message bank / battle strings table

- `"Gotcha"` (mixed-case) found at file offsets `0x3FD7A2` and `0x3FD7C0`, decoding to the expected "Gotcha!\n[name] was caught!" / nickname-prompt text.
- Both offsets are referenced exactly once each, from consecutive pointer-table slots `0x3FE338`/`0x3FE33C`.
- The surrounding region (`0x3FE200`–`0x3FE4FC` and likely beyond in both directions, not yet fully bounded) is an unbroken run of valid `0x08xxxxxx`/`0x09xxxxxx` pointers — the same `gBattleStringsTable`-shaped large contiguous pointer array Unbound found in its own ROM (there at `0x3FDF3C`–`0x3FE514`, ~374 entries).
- Per `docs/CFRU_CROSSWALK.md`, CFRU's public source (`src/catching.c`'s `atkF0_givecaughtmon`) explains exactly what consumes this table and calls `GiveMonToPlayer()` on success — strong converging evidence this is the real catch-completion path, though the exact function address in the compiled RR binary is not yet isolated (needs XREF work on the ~consecutive call sites referencing this table, same next step Unbound is on).
- Not yet bounded: full table start/end offsets (only ~190 entries dumped so far, `0x3FE200`-`0x3FE4FC`), and which of the (likely dozens of) referencing call sites is `atkF0_givecaughtmon` specifically vs. other generic battle-message users.

## CONFIRMED — CFRU's expanded ball roster is present in-ROM

`"Beast Ball"` (2 hits) and `"Dream Ball"` (2 hits) found as mixed-case text — corroborates that Radical Red carries CFRU's Gen 7+ ball additions (`catching.c`'s `GetBaseBallCatchOdds` references `BALL_TYPE_BEAST_BALL`, `BALL_TYPE_DREAM_BALL`, etc.), further supporting the CFRU-lineage hypothesis at the binary level, not just via community/web research.

## STRING ANCHOR — catch/PC message bank further confirmed

Additional hits within the same `0x3FD7xx`–`0x3FD9xx` region already identified above (see the Gotcha table entry):
- `"Box is full"` at `0x3FD87A`, decodes to `"The Box is full!\nYou can't catch any more!"` — the PC-full block ROWE/Unbound's `SendMonToPC`-fallback messaging maps to.
- `"sent to"` at `0x3FD80B`, decodes to `"[mon] was sent to\n[box] PC."` — the standard "party full, mon auto-boxed" message.
Both reinforce that this whole file region is the shared catch/PC battle-string bank (same conclusion as Unbound's, same relative ROM neighborhood — strong signal the underlying vanilla/CFRU battle-message table hasn't moved much across these two FireRed-based hacks).

## STRING ANCHOR — Mystery Gift

`"Mystery Gift"` (mixed-case): 10 hits; first at `0x1A6317` decodes to Mystery-Gift tutorial/explainer dialogue (*"...must know about the Mystery Gift. From now on, you should be receiving Mystery Gifts!"*) — this is NPC/tutorial dialogue, not necessarily the gift-delivery routine itself, but a solid anchor for locating the surrounding script (likely Professor Oak or an equivalent tutorial NPC). `"Wonder Card"` also found, 17 hits, first at `0x41E648` — not yet decoded/investigated further. Per `docs/CFRU_CROSSWALK.md`, the actual Mystery Gift delivery internals (`mevent.h`'s two opaque `sub_XXXXXXX` stubs) have no CFRU source — expect this to require the same blind XREF/pointer work as Unbound's approach once a delivery-relevant (not just tutorial) anchor is found.

## RULED OUT — false leads (don't re-try)

- `"Would you like to trade more Berry Powder for something else?"` (`0x1933BD`) — this is a **Berry Powder shop/exchange NPC**, not a Pokemon trade. Don't treat `"trade"` substring hits as Pokemon-trade-specific without decoding context first.
- `"Take good care of"` (`0x193CAE`) — decoded context mixes with Day Care ("That is merely an Egg!") dialogue; inconclusive whether this is genuine in-game Pokemon trade text or Day Care text reusing similar phrasing. Needs re-verification before treating as a trade anchor.
- `"your trade"` (`0x1BC8FA`) — decodes to Union Room/wireless-adapter trade UI text ("...start your trade... Trainer Card data will be overwritten"), not a standard in-game NPC trade script.
- No definitive in-game NPC-trade dialogue anchor found yet this session (tried "Would you like to trade", "I'll trade you" [apostrophe unsupported by charmap search], "Excellent! Take good care", "linked to trade", "wants to trade" — all misses or false positives above). Needs another pass, possibly searching for specific vanilla FRLG trade NPC names/species pairs once candidate trainers are identified another way (e.g. via `dump_all_strings.py` open-ended scan of a likely map/script region).

## Not yet started

Gift/static-mon handoff routine confirmation (beyond the CFRU-source-level `ScriptGiveMon` lead), genuine in-game trade dialogue, starter-selection dialogue, intro/options-menu wording, sprite/trainer-card/battle-pic tables.
