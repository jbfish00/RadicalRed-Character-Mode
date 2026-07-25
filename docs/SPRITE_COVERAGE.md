# Sprite/asset coverage — Phase 3 planning

Cross-referenced this project's 184-character roster (`tools/character_mode/characters.txt`) against the ROWE Character Mode project's already-built sprite report (`/home/jbfish00/Documents/Pokemon Rowe Alteration/tools/character_mode/sprite_report.txt`), same methodology as `Unbound-Character-Mode/docs/SPRITE_COVERAGE.md` — since this roster's Gen 1-8 slice is largely the same real-world characters ROWE already sourced donor art for.

## Coverage summary

| | count | % of 184 |
|---|---|---|
| Have an overworld sprite candidate | 101 | 55% |
| Have a trainer front-pic candidate | 70 | 38% |
| Have a battle back-pic candidate | 12 | 7% |
| Have AT LEAST ONE asset | 101 | 55% |
| Have NO assets in ROWE's tree | 83 | 45% |

## Pattern (matches Unbound's precedent, plus this project's own Gen 9 addition)

The 83 zero-coverage characters split into three groups:

1. **Gen 6-8 (Kalos/Alola/Galar) game/anime roles** — the same split Unbound found: GBA-style pixel art genuinely doesn't exist anywhere (official or fan-made) for 3D-model-era characters.
2. **A handful of Gen 1-5 anime-only characters** (`Ritchie`, `Tracey`, `Jessie`, `James`, `Lyra`, `Drew`, `Paul`, `Zoey`, `Nando`, `Trip`) — ROWE's own status notes already flagged these as never sourced.
3. **All 15 Gen 9 (Paldea) characters** (`Geeta`, `Nemona`, `Rika`, `Poppy`, `Hassel`, `Katy`, `Brassius`, `Iono`, `Kofu`, `Larry`, `Ryme`, `Tulip`, `Grusha`, `Arven`, `Penny`) — new relative to Unbound's coverage survey, since Unbound's roster excluded Gen 9 entirely (see this project's CLAUDE.md standing-rules note on the full-Gen-1-9 scope decision) but this project's does not. Same underlying reason as group 1: no GBA-style art exists for 3D-only-era characters.

Plus **`Victor` and `Gloria`** (the Sword/Shield protagonists added to this project's `characters.txt` in the v8 session — see `CLAUDE.md`) have **no entry at all** in ROWE's `sprite_report.txt`, since ROWE's own seed list never included them either — same "no assets" outcome as the rest of group 1, just for a different underlying reason (ROWE never looked, not that it looked and found nothing).

This is exactly the split the ROWE/Unbound precedent already established and the user already accepted when scoping the Unbound project: 3D-model-era characters get the lighter-weight trainer-card/menu-portrait-only treatment, not full OW+front+back sprites.

## What this means for Phase 3

- **101 characters (Gen 1-5 + a few Gen 1 anime like Ash/Gary)**: candidate donor PNGs exist in ROWE's `graphics/trainers/front_pics/`, `graphics/trainers/back_pics/`, `graphics/object_events/`. ROWE's `sprite_report.txt` gives *symbol names* (`OBJ_EVENT_GFX_CM_X`, `TRAINER_PIC_X`, `TRAINER_BACK_PIC_X`), not raw file paths — resolving symbol → exact PNG filename needs ROWE's `spritesheet_rules.mk`/`graphics_file_rules.mk` (not yet done; deferred until Phase 3 actually starts, since real injection work is gated on Phase 1 anyway — see below).
- **83 characters (Gen 6-9 + a few anime + Victor/Gloria)**: no GBA-style art exists anywhere. Per the established policy: trainer-card/menu-select portrait only, generic/default costume fallback for their overworld appearance — no bespoke pixel art expected.
- **Actually copying/injecting any of this is blocked on Phase 1 confirming the ROM-side sprite tables.** Checked whether the same CFRU fixed-pointer-redirect technique that solved the species/evolution tables (see `docs/ROUTINE_MAP.md`) would work here first, since it would have been much cheaper than Ghidra: `tools/cfru_donor/include/new/rom_locs.h` only exposes `gBaseStats`/`gEvolutionTable`/`gSpeciesNames`/`gItems`/`gMonIconPaletteIndices` as dynamic pointer-redirect slots. `gTrainerFrontPicTable`/`gTrainerFrontPicPaletteTable`/`gTrainerFrontPicCoords` (`src/defines_battle.h`) are instead **hardcoded compile-time addresses in stock CFRU's own build** (`0x823957C` etc.) — not a redirect slot, so there's no guarantee Radical Red's actual compiled binary has this table at the same address (unlike the redirect-slot tables, whose *slot* address is an engine-level constant regardless of where the hack's own build relocated the *target*). No public CFRU source at all was found for `gObjectEventGraphicsInfoPointers` (the overworld sprite table). Confirming real addresses needs Ghidra's data-type analysis or manual structure hunting, same conclusion Unbound already reached for its own sprite tables — not yet attempted for this project (Ghidra still not installed here, see `CLAUDE.md`/`docs/CFRU_CROSSWALK.md`).

## Reuse mechanics (once unblocked)

Same credits-file discipline as ROWE (`CREDITS_CHARACTER_MODE.md` pattern) — this project will need its own `CREDITS.md` with the same donor list: pret/pokefirered, sinnoh-remakes/pokeemerald-platinum, PokemonHnS-Development/pokemonHnS, DiegoWT's Gen5-in-Gen4-style resource, StreakOfSprites' Ash sheet (same donors Unbound credited, since the underlying art is the same ROWE-sourced set). Injection differs from ROWE's Makefile-automated pipeline: raw tile/palette data needs manual LZ77 compression and free-space injection with hand-patched pointers (see Phase 3 in the plan file), once the real table addresses are confirmed.

## 2026-07-23 — Ash Gray donor sourcing (anime-only gap partially closed)

Pokemon Ash Gray v4.5.3 (metapod23) was built locally — BPS patch (RAPatches
mirror) onto a byte-matching pret/pokefirered build — and its sprites ripped
(`RadicalRed-Character-Mode/tools/rip_frlg_sprites.py`). **19 anime-character
trainer front pics** now staged as verbatim LZ77 blobs in
`sprites/donors/ashgray/` (64x64 4bpp + 32 B palette — the same format this
engine family consumes; see that directory's README for provenance).

Coverage delta for the "never sourced" anime-only list: **Ritchie ✓,
Tracey ✓, Jessie ✓ + James ✓ (as a duo pic)** — plus new-to-us Duplica, Todd,
Giselle, A.J., Otoshi, Samurai, Damian, Gary, Cissy, Danny, Rudy, Jessiebelle,
and anime-style Brock/Misty/Oak/Giovanni alternates. Ash overworld
(walk/bike/fishing) + back-pic sheet also ripped.

**Still missing** (web-archive survey 2026-07-23 found no GBA-style front
pics): Drew, Paul, Zoey, Nando, Trip, Lyra; Gen 6-9 policy unchanged
(portrait-only). Candidate OW-only source if ever needed: spherical-ice's
"Accurate FireRed Overworld Sprite Resource" (DeviantArt) — has some anime OW
sprites; The Spriters Resource search is JS-only (not scriptable).

**Pilot injection result (RadicalRed, 2026-07-23)**: all 19 donors injected
at 0x08CF0000 (15,364 B) by `tools/inject_sprites_pilot.py` (RR repo);
decode-back from the built ROM byte-exact; `gTrainerFrontPicTable`
consumption confirmed (12 literal-pool code refs incl. battle engine); the
all-slots test build boots to free-roam. This project's tables are already CONFIRMED (docs/ROUTINE_MAP.md), so per-character
wiring (which slot each character's mugshot should own, and any menu/OW use)
is the only remaining step here.

### Outstanding (2026-07-24)

1. Per-character wiring design (mugshot use at the console select and/or dedicated slots);
   `sprite_asset_id` still 0xFFFF everywhere.
2. OW sprite table not located (vanilla FRLG candidate 0x39FDB0 — verify + XREF first);
   OW/back-pic injector step not built (front pics only were piloted).
3. In-battle render check of a repointed slot = human playthrough item.
4. Missing art: Drew, Paul, Zoey, Nando, Trip, Lyra; James solo (duo-only). Pipeline reruns in
   minutes on any new donor hack (see sprites/donors/ashgray/README.md recipe).

## 2026-07-24 — CORRECTION: overworld coverage was undercounted (engine-native sprites)

Every previous coverage number in this file came from cross-referencing ROWE's
`sprite_report.txt`, which records only art ROWE had **staged for injection**.
That silently undercounts overworld sprites, because most of these characters are
NPCs in the games themselves — **this engine already ships their overworld
graphics**. Prof. Oak is the clearest case: the old survey listed him with no
overworld art at all, while both engine families define him
(`OBJ_EVENT_GFX_PROF_OAK` / `EVENT_OBJ_GFX_OAK`). Referencing an existing
graphics id is not an injection job.

Re-surveyed against CFRU (`tools/cfru_donor/include/constants/event_objects.h`, `EVENT_OBJ_GFX_*`):

**26 of this repo's 209 characters already have an overworld sprite in the
ROM** and need no art sourced:

Red, Leaf, Blue, Lance, Lorelei, Bruno, Agatha, Koga, Brock, Misty, Lt. Surge,
Erika, Sabrina, Blaine, Giovanni, Gary, Ethan, Lyra, Brendan, May, Lucas,
Dawn, Cynthia, Candice, Oak, Palmer

Cross-repo, counting the engine tables adds **12 characters the old survey called
empty** — Lyra, Oak, Elm, Birch and eight Frontier Brains (Anabel, Tucker, Greta,
Spenser, Noland, Lucy, Brandon, Palmer) — and reclassifies **54 more** from "needs
injecting" to "already there".

Regenerate with `python3 RadicalRed-Character-Mode/tools/survey_engine_ow.py`
(canonical copy lives in the RR repo; it reads every sibling repo's live
`characters.txt`). Visual summary: the "Character Mode — Sprite Coverage by
Character" artifact.

### Three name collisions deliberately NOT counted

CFRU defines `MARLON`, `PENNY` and `MELONY`, but CFRU is Unbound's engine: its
Marlon is Unbound's own protagonist (`MARLON_PLAYER`, `YOUNG_MARLON`,
`MARLON_ARM`), and the engine has no Gen 9 content at all, so its `PENNY` cannot
be the Paldea character. Matching on name alone would have claimed art that does
not depict our character.

### Still open after this correction

1. **The Ash Gray overworld dump is 152 sprites and only 15 were ever
   identified** (`sprites/donors/ashgray/rip/ow/`). Ritchie and Tracey are both
   characters in Ash Gray, so their overworld sprites are very likely already in
   that dump — `ow014` and `ow015` (capless black-haired boys) are the leading
   candidates. Labelling the dump is the cheapest remaining win in Phase 3.
2. **No other anime-based hack has been sourced.** Ash Gray is the only one built
   locally. Drew, Paul, Zoey, Nando and Trip have no art anywhere, and a hack
   covering the Johto/Hoenn/Sinnoh anime arcs is the only plausible source.
3. Back pics remain the real bottleneck: **13 characters across the whole
   workspace**, essentially playable protagonists only.


## 2026-07-25 — CORRECTION 2: "no GBA-style art exists for 3D-era characters" is FALSE

The claim stated above (and in every sibling repo's copy of this file) that GBA-style pixel art
"genuinely doesn't exist anywhere (official or fan-made) for 3D-model-era characters" is **wrong**.
A five-agent search of fan-games and ROM hacks found it, and the format was verified by measuring
pixels rather than trusting page descriptions.

### Primary source: Pokémon Emerald Rogue (open source, drop-in format)

`https://github.com/Pokabbie/pokeemerald-rogue` (branch `vanilla`) — a pret/pokeemerald decomp fork.
Its `graphics/trainers/front_pics/` is split into `kalos/` (13), `alola/` (14), `galar/` (11),
`paldea/` (12) and `rival/` (Gen 6-9 subset), plus Gen 1-5 casts. **Format verified locally: every
sampled front pic is 64x64, 4-bit colormap, exactly 16 palette entries** — stock pokeemerald format,
zero conversion. Back pics are 64x320 5-frame sheets; overworld sets are 144x32 (9 x 16x32 frames).

Cross-matched against this repo's live `characters.txt`: **89 of its characters gain a
trainer front pic they did not have**:

Lyra, Silver, Aaron, Flint, Nate, Rosa, Alder, Iris, Shauntal, Marshal,
Grimsley, Caitlin, Cilan, Chili, Cress, Lenora, Burgh, Elesa, Clay, Skyla,
Brycen, Drayden, Cheren, Roxie, Marlon, Bianca, Hugh, N, Calem, Serena,
Diantha, Malva, Siebold, Wikstrom, Drasna, Viola, Grant, Korrina, Ramos,
Clemont, Valerie, Olympia, Wulfric, Shauna, Lysandre, Elio, Selene, Kukui,
Hau, Molayne, Kahili, Acerola, Hala, Olivia, Nanu, Hapu, Gladion, Sophocles,
Victor, Gloria, Leon, Milo, Nessa, Kabu, Bea, Allister, Opal, Gordie, Melony,
Piers, Raihan, Hop, Bede, Marnie, Geeta, Nemona, Rika, Poppy, Hassel, Katy,
Brassius, Iono, Kofu, Larry, Ryme, Tulip, Grusha, Arven, Penny

Workspace-wide the search takes trainer-pic coverage from 76 to 165 of 236 characters, and the
"nothing at all" group from 92 down to 31.

**Cost: attribution.** The repo has no LICENSE and no CREDITS.md. The only credit trail is its
in-game credits roll (`src/data/credits.h`), which lists ~46 artists under "Additional Sprites"
without saying who drew what — so we can credit the project and that roll, but not per sprite.
Several of those names (Beliot419, princess-phoenix, Zender1752, SageDeoxys) are the same DeviantArt
spriters other searches found independently: the repo is best understood as a pre-converted
aggregation of those galleries.

### Secondary sources worth knowing

- **SwSh Ultimate Plus** (PCL.G -> Jeanstars -> Phantonomy; FireRed + CFRU, BPS-distributed) — the
  "Sword and Shield GBA hack". Real, and our Ash Gray rip recipe would apply unchanged. **Rejected as
  primary**: its own README says *"As a non-original dev, I'm not certain where all of the assets
  came from"*, with exactly one Gen 8 sprite attributed. Correct format, unattributable provenance.
- **darklight177 + RHcks Paldea sheet** (DeviantArt) — 8 Paldea leaders + Geeta, trainer pics AND
  overworld strips, measured GBA-native. Free to use, credit RHcks. Adds overworld art Rogue lacks.
- **RichardPT** (DeviantArt) — the only Alain art anywhere: a complete Gen 3 engine set (front, back,
  walking, running, surfing, fishing, town map, VS Seeker). Free with credit.
- **Kalarie's anime overworlds**, PokéCommunity thread 407124 — includes **Paul**, one of the six
  anime characters previously believed to have no art anywhere. Free with credit; needs a dynamic
  overworld palette patch. NOT yet retrieved or verified.
- **Droid779** (Eevee Expo 284) — Gen III-style overworlds for Mallow, Kiawe, Gladion; author takes
  requests.
- **Beliot419 / mid117 / Zender1752** — broad Gen 7-9 coverage including Sada, Turo, Penny and Arven,
  but DS/Gen 5 style at 80x80. Reference for a redraw, not a drop-in.

### Rejected on measurement (do not re-chase)

- mid117's Scarlet/Violet set: DS/Gen 5 style, not GBA.
- xDracolich's Nemona overworld: genuine Gen 3 art but Essentials scale (30x40 per frame vs GBA's
  16x32).
- PokéCommunity 339994: the Gen 6 block is a to-do list with zero image links.
- PokéCommunity 316888 "Kalos Sprites for GBA": Pokémon species only, and every image is a TinyPic
  link — that domain no longer resolves.
- spherical-ice's "Accurate FireRed Overworld Sprite Resource", referenced in our docs for a year:
  Gen 3 trainer *classes* only, nothing past Gen 3.
- Upstream `rh-hideout/pokeemerald-expansion`: ships no Gen 6-9 human character art at all. Adding
  Gen 9 *species* is not the same as adding Gen 9 *humans* — this distinction is the easiest way to
  get a wrong answer here.

### Still unresolved

1. **31 of this repo's characters still have no art of any kind.** Workspace-wide the 31 are
   the anime cast (Drew, Zoey, Nando, Trip, Alain, Sawyer, Tobias, Goh, Chloe, the Alola anime
   four), the professors (Rowan, Juniper, Sycamore, Burnet, Samson Oak, Magnolia, Sonia, Laventon,
   Cerise, Sada, Turo), and Guzma, Plumeria, Lusamine, Rose, Dahlia, Darach.
2. **The anime-arc search never finished** — that agent hit a usage limit having just surfaced a
   Pokesho 64x64 GBA trainer gallery described as free material. Unverified lead, not a finding.
   The "is there an Ash Gray equivalent for the Hoenn/Sinnoh/Unova arcs" question is still open.
3. **The Ash Gray overworld dump is still unlabelled**: 152 sprites, 15 identified. Ritchie and
   Tracey are both in that game so their overworld art is very likely already ripped —
   `ow014`/`ow015` are the candidates. Confirmed so far: `ow050` Jessie, `ow051`/`ow052` James,
   `ow064` Nurse Joy.
4. **Nothing has been staged or injected.** This is a sourcing finding only; `sprite_asset_id` is
   still `0xFFFF` everywhere.


## 2026-07-25 — CORRECTION 3: the "never sourced" anime characters were sourced all along

Correction 2 closed the Gen 6-9 gap. This closes the anime gap that predates it. The list
"Drew, Paul, Zoey, Nando, Trip, Lyra — no GBA-style art exists anywhere" has been carried in this
file since 2026-07-23. **Five of the six exist.** Only Trip is genuinely missing.

### Pokesho (ポケしょ), by ポケモア / Pokemore — the find

A Japanese fan site that ran two galleries built explicitly to GBA spec. Not a game: a pure sprite
resource. **Both galleries are retired from the live site**; everything below came from the Wayback
capture of **2018-08-15** and was downloaded and format-verified locally.

- **Trainer gallery** (`dot_battle.html`, 68 sprites) — **64x64, <=16 colours = exact GBA trainer
  front-pic format.** Verified: `b_shuu`/`b_shuu2` = **Drew** (two poses), `b_masato` = Max,
  `b_rokettodan` = the Jessie+Meowth+James trio, plus Harley, Tyson, Robert, anime May, Dawn, and
  Ash/Brock/Misty in Kanto, Hoenn and Sinnoh outfits. Measured 64x64 / 16-colour on every sample.
- **Field gallery** (`dot_field.html`, 302 sprites) — **16x22, 16 colours, FRLG-spec, FRONT-FACING
  FRAME ONLY.** Verified: `f_shinji` = **Paul**, `f_nozomi` = **Zoey**, `f_naoshi` = **Nando**
  (carrying his harp), `f_shuu` = Drew, `f_kojirou` = **solo James**, `f_onnanoko_hgss` = **Lyra**.
  Also Ritchie, Tracey, Reggie, Kenny, Ursula, Morrison, Iris, Cilan, Bianca, Cheren, N.
- **Licence, quoted from the gallery header:** 「GBA風トレーナードット絵を展示しています。
  **フリー素材になります**。」 ("GBA-style trainer pixel art is exhibited here. **These are free
  materials.**") and 「すべて64×64サイズ。透明色合わせて最大16色です。**素材としての使用も可能です**。」
  The still-live FAQ answers 「素材もらってもいいですか！？」 with 「**どうぞどうぞ！！**」
  ("Please, go right ahead!!"). Credit as 「ポケしょ / Pokesho（ポケモア）」.
- **Two real caveats.** (1) The field sprites are ONE FRAME — side and back must be drawn before
  they are usable as walking sprites. (2) The galleries are retired and the author states he deletes
  work he considers lower quality; permission was granted while published, so reusing archived
  copies is a judgement call, not a settled one.

### Supporting anime sources

- **kalarie, PokéCommunity thread 407124** — 73 anime overworld sheets, **all imgur links still
  live**, verified **144x32 = the standard FireRed 9-frame NPC sheet of 16x32 frames, GBA-native
  drop-in**. Has **solo James and solo Jessie**, plus Meowth, Butch, Cassidy, Jenny, Joy, Brock,
  Misty, Oak. Kanto/Orange era only. Licence: *"You're free to use any of these sprites in your
  hack... Be sure to give proper credit though."* Needs Navenatox's Dynamic Overworld Palettes patch.
  **This resource is literally Pokesho's front frames animated into full sheets** (its credits say
  so) — which is the proof-of-workflow for doing the same to Paul, Zoey and Nando.
- **aveontrainer (DeviantArt)** — ~480 deviations; posted at 128x192 but that is a clean 2x upscale
  of a native **64x96 = 16 frames of 16x24**, i.e. a full four-direction walk cycle. Has Drew, Lyra,
  Ritchie, Harley, Morrison, **Alain**, Serena, Iris, Bianca, Dawn, Barry, Clemont. No blanket
  licence; takes overworld commissions — the realistic route for Trip/Zoey/Nando walk cycles.
- **Team Aqua's Asset Repo** (`github.com/TeamAquasHideout/Team-Aquas-Asset-Repo`) — **the cleanest
  licence found anywhere**: *"All assets are both free to use and edit by default, but if any assets
  specifically mention not being free to edit, please respect the author's wishes."* Coverage of our
  roster is thin (Lyra, Iris, Serena/Calem, Dawn, Barry + kalarie's Kanto anime fronts) but prefer it
  wherever it overlaps another source.

### CORRECTION to Correction 2: Paul is NOT in kalarie's resource

Correction 2 recorded Paul as available from PokéCommunity 407124. That was wrong. Paul appears in
that thread only as a **rejected submission** (post #20 by *etique*) — the maintainer turned it down
as *"not really FR Style"* — and the attachment measures 32x48 DS-format frames, not GBA. **Paul's
real source is Pokesho's `f_shinji`.**

### The anime-arc hack question: evidenced NEGATIVE

There is **no GBA anime-arc ROM hack for Sinnoh or Unova**, in existence or in development.
*Advanced Generation* (Hoenn, Emerald) stalled at "Beta One Progress: 30%" and its thread is locked.
*Ash Hoenn Version* claims completion but ships as a **pre-patched .gba only**, which fails our
patch-only rule. *Johto League Showdown* is likewise pre-patched-only. *Ash Z* is a 3DS hack with 3D
models. The Sinnoh/Unova cast art exists as standalone resources, not inside any game.
**Pokémon Fire Ash** (RPG Maker XP + Essentials, PC) is the only known thing containing **Trip** —
its walkthrough confirms Trip, Sawyer, Tobias, Paul, Nando and Zoey as battleable trainers — but it
is not a ROM hack, has no stated asset licence, and **nobody has opened its `Graphics/Trainers`
folder to confirm the sprite format.**

### Where this repo now stands

**26 of its characters still have no art of any kind.** Workspace-wide the remaining 26 are
the eleven professors (Rowan, Juniper, Sycamore, Burnet, Samson Oak, Magnolia, Sonia, Laventon,
Cerise, Sada, Turo), the Alola anime four (Lillie, Kiawe, Lana, Mallow), Guzma, Plumeria, Lusamine,
Rose, Goh, Chloe, Tobias, Sawyer, **Trip**, Dahlia and Darach. Several of the artists found here take
commissions and already work natively in our format.

Workspace totals across the three corrections: overworld 103 -> 131 (plus 31 partial), trainer pics
76 -> 168, back pics 13 -> 18, "nothing at all" 92 -> 26.

Nothing is staged or injected. `sprite_asset_id` is still `0xFFFF` everywhere.
