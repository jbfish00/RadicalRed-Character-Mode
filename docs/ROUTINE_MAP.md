# Routine map

RE findings/anchors for this project — the project's "symbol table". Tag every entry CONFIRMED / STRING ANCHOR / LIKELY / UNKNOWN, and record ruled-out false leads explicitly so they aren't re-tried.

## CONFIRMED — text-rendering convention differs from vanilla FireRed/Unbound

Radical Red uses **mixed-case text**, not vanilla FRLG's ALL-CAPS convention:
- `"TRAINER"` (all caps): 0 hits. `"Trainer"` (mixed case, `--icase`): **360 hits**.
- `"POKEMON"` (all caps): 0 hits. `"Pokemon"` (mixed case): 5 hits. `"pokemon"` (lowercase): 1 hit.
- `"SAVE"` (all caps, exact case): 1 hit at file offset `0x0110004E`, decodes to a developer diagnostic string: *"WRONG SAVE TYPE! Please change to Flash 128k. Consult the Discord if you need help."* — confirms this is genuinely Radical Red's own custom content (not vanilla leftover text) and that it targets Flash 128k save type.

**Implication for all future `search_gametext.py` runs on this ROM: always pass `--icase`, or better, search for the expected mixed-case rendering directly** (e.g. `"Trainer"` not `"TRAINER"`) — plain vanilla-style all-caps queries will silently miss almost everything. This is a real divergence from both vanilla FRLG and Unbound's apparent text convention, worth remembering before assuming any porting the Unbound anchors 1:1.

## Not yet started

Catch mechanic, Mystery Gift, gift/static-mon handoff, trade dialogue, PC bank text, starter-selection dialogue, intro/options-menu wording, sprite/trainer-card/battle-pic tables — all still to be searched, now that the mixed-case text-rendering convention is known.
