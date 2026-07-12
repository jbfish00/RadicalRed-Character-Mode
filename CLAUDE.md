# CLAUDE.md — Pokemon Radical Red "Character Mode"

Guidance for Claude Code when working in this repo. Keep this file current at every pause — it's the handoff doc for a fresh instance picking this up cold.

## What this project is

Porting the "Character Mode" feature from the Pokemon ROWE project (`/home/jbfish00/Documents/Pokemon Rowe Alteration`) to Pokemon Radical Red v4.1: an opt-in intro-menu choice to play as an iconic Pokemon character, restricted to that character's Bulbapedia-documented roster (evolution families included). Full plan (context, phase breakdown, roster-scope decision, provenance decisions, open risks) at `~/.claude/plans/just-like-with-pokemon-linear-galaxy.md`.

**Sibling project, same workspace, further along**: `../Unbound-Character-Mode/` ported the same feature to Pokemon Unbound and established the binary-ROM-hacking methodology this project reuses. Read its `CLAUDE.md` for the proven technique set, but do not assume its ROM-specific findings (offsets, text conventions, save-flag ranges) transfer — every hack's binary differs.

**Critical difference from ROWE: Radical Red has no public source of its own.** It's a closed binary hack (by soupercell, with koala4 — NOT Skeli789/Unbound's author) built on the open-source Complete FireRed Upgrade (CFRU) engine. Unlike Unbound (which had to approximate its internals via a third-party community fork as a donor), Radical Red's actual upstream engine — CFRU itself (`github.com/Skeli789/Complete-Fire-Red-Upgrade`) — is directly public and cloned locally at `tools/cfru_donor/`. This is a stronger donor situation than Unbound had. Radical Red's own content (maps/story/trainers/balance) remains proprietary — same "open engine, closed content" shape as Unbound, so this is still classic binary ROM hacking: reverse-engineer the compiled ROM, inject new code/data into free space, output a patch (never redistribute the ROM).

## Standing rules (carried over from the ROWE/Unbound projects, user-confirmed pattern)

- **Checkpoint rule**: at every pause, update this file + the plan file for seamless handoff.
- **Ask questions until 95% confident** before making consequential decisions.
- Distribution: patch only (UPS/BPS via `tools/bin/flips`), never a prebuilt/redistributed ROM.
- Every located ROM address is pinned to the exact SHA1 in `rom.sha1`. Re-verify before trusting notes against any other copy.
- Roster scope: **full Gen 1-9** (protagonists/rivals/gym leaders/E4/champions/villains/anime) — user explicitly chose this over matching Unbound's Gen-1-8-only trim, since Radical Red's engine confirms Gen 9 species/moves support (unlike Unbound's ROM, which turned out to lack Gen 9 content entirely).

## Repo layout

- `rom/` — extracted ROM (gitignored, never commit).
- `rom.sha1` — checksum of the source ROM; all findings are pinned to this.
- `docs/ROM_INFO.md` — ROM header/provenance notes.
- `docs/FREE_SPACE.md` — free-space audit results.
- `docs/ROUTINE_MAP.md` — RE findings/anchors (the project's "symbol table").
- `docs/CFRU_CROSSWALK.md` — records whether CFRU-source-as-structural-donor pattern-matching pays off (see Phase 1 notes below).
- `docs/SPRITE_COVERAGE.md` — sprite asset coverage survey (not yet run).
- `tools/scan_free_space.py`, `search_gametext.py`, `decode_gametext.py`, `find_pointer_refs.py`, `dump_all_strings.py` — copied verbatim from `Unbound-Character-Mode/tools/` (game-agnostic; `search_gametext.py`/`decode_gametext.py` default to ROWE's shared `charmap.txt` at `/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt`, same as Unbound uses — no local copy needed).
- `tools/bin/` — convenience copies: `armips` v0.11.0, `flips` (copied from Unbound's already-built binaries, both verified working).
- `tools/cfru_donor/` — fresh shallow clone of `Skeli789/Complete-Fire-Red-Upgrade` (gitignored, third-party) — this project's primary species/structure donor, stronger than Unbound's DPE-fork situation since it's Radical Red's actual upstream engine.
- `tools/ghidra/` — **not yet installed** (deferred until text/pointer-anchor techniques run dry, per Phase 1 priority order; Unbound's Ghidra install + `pudii/gba-ghidra-loader` setup is the template when needed).
- `tools/character_mode/` — roster data pipeline:
  - `characters.txt` (205 lines), `rosters_raw.json` (89,080 bytes) — copied from **ROWE's un-pruned originals** (NOT Unbound's already Gen-9-pruned 199-line/78,343-byte copies), per the full-Gen-9-scope decision.
  - `scrape_rosters.py` — copied from ROWE (game-agnostic; only needed if the seed list changes in a way requiring re-scraping).
  - `cache/` — ROWE's Bulbapedia API disk cache (3,761 files, ~25 MiB), copied alongside the scraper to avoid re-hitting the API. Precedent from Unbound: this cache is **committed to git**, not ignored (matches Unbound's own repo, which tracks 3,837 cache files) — small JSON files, fine to track.
  - `map_species.py`, `emit_characters.py` — **not yet written**. Will be rewritten fresh against the CFRU donor (species mapping) and adapted from Unbound's flat-binary emitter (not ROWE's C-header generator) — see Phase 2 in the plan file.

## Toolchain (confirmed working this session)

- `arm-none-eabi-gcc` (system-installed, 13.2.1) — for new freestanding C, not `~/agbcc`. Same verified flags as Unbound: `-mthumb -mcpu=arm7tdmi -mtune=arm7tdmi -O2 -ffreestanding -fno-builtin`.
- `armips` v0.11.0 — copied from Unbound's already-built binary (`tools/bin/armips`), verified runnable (`--help` prints usage banner correctly).
- `flips` — copied from Unbound's already-built binary (`tools/bin/flips`), verified runnable (prints usage banner).
- `mgba-qt` 0.10.2 (system-installed) — confirmed present via `which`; not yet exercised against this ROM.
- `cmake` — confirmed present via `which` (would be needed only if `armips`/`flips` ever need rebuilding from source rather than reusing Unbound's binaries).
- Ghidra + `pudii/gba-ghidra-loader` — not yet installed for this project; install when Phase 1's text/pointer-anchor techniques run dry (see Unbound's setup as template).

## Free space (resolved — see docs/FREE_SPACE.md)

**5.40 MiB confirmed free** (0xFF-padded, 77 runs >= 0x400 bytes) — over 3.5x what Unbound had (~1.46 MiB), despite Radical Red's denser content (full Gen 1-9 species/moves, Mega/Z-Move/Dynamax/Gigantamax, physical-special split). Two dominant blocks: 1.63 MiB @ 0x00B71D04, ~1.02 MiB @ 0x0085032B. This resolves the plan's open risk #1 favorably — free space is not a bottleneck.

## Status (2026-07-12, v2 — RE session)

**Phase 1 (RE/feasibility): substantial progress, not yet gate-closed.**

**Big win: the CFRU-as-structural-donor bet (Phase 1d) paid off, partially.** Full writeup in `docs/CFRU_CROSSWALK.md`. Key findings:
- CFRU is a hook-and-patch framework over vanilla FireRed binary, NOT a full decompilation — only subsystems it modifies have public source.
- **Catch and gift/static-mon delivery share ONE choke point in CFRU source**: `catching.c`'s `atkF0_givecaughtmon()` (wild catch) and `build_pokemon.c`'s `ScriptGiveMon()` (scripted/static/event mons, likely also Mystery Gift's delivery path) both call `GiveMonToPlayer()`, which already has a `SendMonToPC()` fallback built in. This is a real simplification opportunity for Phase 4 versus ROWE's original 6-separate-hook design — **but** `GiveMonToPlayer` is also used by Battle Frontier/Tower rental-mon delivery, so a naive hook would wrongly roster-gate temporary rental teams. Flagged as a Phase 4 design constraint and a Phase 5 test case.
- Mystery Gift internals (`mevent.h`) and trade internals (`trade.h`) have **no CFRU source at all** — same blind-RE position as Unbound for those two systems specifically.
- Concrete ROM evidence gathered (see `docs/ROUTINE_MAP.md`): found the "Gotcha" catch-message text at `0x3FD7A2`/`0x3FD7C0`, referenced from a large contiguous `gBattleStringsTable`-shaped pointer array at `0x3FE338`+ — same structural shape Unbound found in its own ROM, strong converging evidence the catch-message plumbing is intact. Also confirmed `"Box is full"` and `"sent to [box] PC"` text in the same region, and CFRU's expanded ball roster (`"Beast Ball"`, `"Dream Ball"`) is present in-ROM.
- Found a Mystery Gift tutorial-dialogue anchor (`"Mystery Gift"` text at `0x1A6317`) and `"Wonder Card"` text (17 hits) — not yet decoded into a delivery-relevant routine.
- Tried and ruled out several trade-dialogue leads (Berry Powder shop, Union Room UI text) — no genuine in-game NPC trade anchor confirmed yet, logged in `docs/ROUTINE_MAP.md` so they aren't retried.
- **Not yet done**: XREF-confirming which of the (likely dozens of) call sites referencing the battle-strings table is actually `atkF0_givecaughtmon` — this is the concrete next RE step, mirrors Unbound's own current blocker.

## Status (2026-07-12, initial scaffolding session)

**Phase 0 (scaffolding): COMPLETE.**
- Repo created at `RadicalRed-Character-Mode/`, git initialized (not yet committed — see Next steps).
- ROM extracted from `radicalred 4.1.zip` (workspace root) into `rom/radicalred 4.1.gba` (33,554,432 bytes).
- SHA1 computed and pinned: `964f951a0fdaf209e4ea1344883ef0d557bb3a80` (no published SHA1 for v4.1 existed anywhere — this project owns the canonical pin).
- Header confirmed: `POKEMON FIRE`/`BPRE`/rev 0 — genuinely FireRed-based, consistent with Radical Red being CFRU-derived (same base as Unbound). No watermark/readme in the zip (unlike Unbound's ROMSFUN.COM-watermarked copy).
- `.gitignore` copied from Unbound and extended with `tools/cfru_donor/`.
- `docs/{ROM_INFO,FREE_SPACE,ROUTINE_MAP,CFRU_CROSSWALK,SPRITE_COVERAGE}.md` created (ROM_INFO and FREE_SPACE populated; ROUTINE_MAP has one early finding; CFRU_CROSSWALK and SPRITE_COVERAGE are stubs pending later phases).

**Phase 1 (RE/feasibility): just started.**
- Toolchain verified: `armips`/`flips` binaries copied from Unbound and confirmed runnable; `arm-none-eabi-gcc`/`mgba-qt`/`cmake` confirmed installed system-wide. Ghidra deliberately not yet installed (lowest-priority technique, per the plan's priority order).
- Free-space audit done and resolved favorably (see above).
- CFRU donor repo cloned (`tools/cfru_donor/`, shallow clone) — the Phase 1d "CFRU-as-structural-donor" bet (attempting to pattern-match stock CFRU source/compiled shapes against Radical Red's binary to shortcut hook-site RE) has **not yet been attempted**; this is the single highest-value next step per the plan.
- One real finding via `search_gametext.py`: **Radical Red renders mixed-case text** ("Trainer", "Pokemon"), not vanilla FRLG's ALL-CAPS convention — confirmed by 0 hits for all-caps queries vs. hundreds for mixed-case/`--icase` queries. A `"SAVE"` hit decoded to a genuine RR developer diagnostic string ("WRONG SAVE TYPE! Please change to Flash 128k. Consult the Discord..."), confirming this really is Radical Red's own content. **Always use `--icase` or mixed-case queries on this ROM going forward** — plain all-caps searches (which worked fine on vanilla/Unbound) will silently miss almost everything here. Full detail in `docs/ROUTINE_MAP.md`.
- Not yet attempted: any of the enforcement-hook text/pointer anchor searches (catch, gift, Mystery Gift, trade, PC, starter-selection, intro-menu), the CFRU-crosswalk pattern-matching bet, or any Ghidra work.

**Phase 2 (roster data pipeline): partially started.**
- Seed data sourced: `characters.txt` (205 lines / 182 actual character entries, rest are comments/blank generation separators) and `rosters_raw.json` (89,080 bytes) copied from ROWE's originals — confirmed byte-for-byte match to the plan's pre-verified sizes. `scrape_rosters.py` and its Bulbapedia cache (3,761 files) copied alongside.
- **Seed-list reconciliation DONE — corrects a plan assumption.** Diffed ROWE's 182-character list against Unbound's 156-character list: exactly 26 characters removed, a clean subtraction (no renames — reverse diff is empty). But it's **not purely Gen-9 pruning** as the plan initially assumed — the removed set is: all 15 Gen 9 characters (Geeta, Nemona, Rika, Poppy, Hassel, Katy, Brassius, Iono, Kofu, Larry, Ryme, Tulip, Grusha, Arven, Penny) **plus** Gen 5/6/7 protagonists (Hilbert, Hilda, Nate, Rosa, Calem, Serena, Elio, Selene) **plus** 3 of Gen 7's 4 island kahunas (Hala, Nanu, Hapu — Olivia was kept). So Unbound made a deliberate broader scope cut (no protagonists Gen 5+, partial kahuna trim) specific to that project, not a general/necessary pattern. Since this project targets ROWE's full 182-character breadth (user's explicit full-Gen-1-9 choice), this is moot for what to build — just don't cite "Gen 9 confirmed absent" as the reason Unbound's list is smaller; it's a broader editorial choice than that.
- **Not yet done**: the CFRU-donor species-ID mapping rewrite (`map_species.py`), or the binary emitter adaptation (`emit_characters.py`). These are the next concrete chunks of work — expect real rework here (not a copy), per Unbound's own hard-learned lesson that donor name-table labels don't reliably match species constants and that truncation-convention `NAME_FIXES` need re-deriving per-project.

**Phases 3-6: not started** (sprite pipeline, enforcement logic injection, testing, packaging) — all gated on Phase 1/2 progressing further.

## NEXT

1. ~~Commit initial scaffold~~ DONE. ~~CFRU-as-structural-donor bet~~ DONE (partial win, see above). ~~Seed-list reconciliation~~ DONE (Unbound's cut was broader than Gen-9-only, see Phase 2 status). ~~Enforcement-hook anchor searches~~ done for catch/PC/Mystery-Gift tutorial; trade still open.
2. XREF-confirm which call site referencing the `0x3FE338`+ battle-strings table is `atkF0_givecaughtmon` (needs Ghidra — not yet installed for this project, see Toolchain section — or continued manual disassembly around the ~190+ dumped table entries).
3. Find a genuine in-game NPC trade dialogue anchor (Berry Powder shop and Union Room UI text were false positives, logged in `docs/ROUTINE_MAP.md`) and a Mystery-Gift delivery-relevant anchor (not just the tutorial text found so far).
4. Write `map_species.py` fresh against `tools/cfru_donor/`, expecting to rediscover (not reuse) name-table-position-vs-label-matching behavior and truncation fixes, per Unbound's precedent. This is the next big concrete deliverable — CFRU's `include/species.h`/evolution table are the donor source (need to locate exact paths within `tools/cfru_donor/`).
5. Sprite table locations and intro-menu hook point remain unsearched.
