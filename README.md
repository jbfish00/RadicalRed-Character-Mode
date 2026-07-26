# Character Mode for Pokemon Radical Red v4.1

An opt-in game mode where you play as an iconic Pokemon character — a
protagonist, rival, gym leader, Elite Four member, champion, villain, or
anime cast member — and are restricted to catching and keeping only that
character's canon roster (as documented on Bulbapedia, expanded to full
evolution families). 238 characters, Generations 1 through 9.

Ported from the original Character Mode built for Pokemon ROWE.

## What you need

- A **Pokemon Radical Red v4.1** ROM you obtained legally
  (SHA-1 must be `964f951a0fdaf209e4ea1344883ef0d557bb3a80` — see `rom.sha1`).
  This project distributes a patch only, never the ROM.
- [Flips](https://github.com/Alcaro/Flips) (or any BPS patcher).

## Applying the patch

```
flips --apply radicalred_cm.bps "radicalred 4.1.gba" radicalred_cm.gba
```

(Or use Flips' GUI / an online patcher like https://www.marcrobledo.com/RomPatcher.js/ —
select the BPS patch and your v4.1 ROM.)

## Activating Character Mode

Radical Red's cheat codes are entered at the **game console in your
bedroom** (Player's House 2F — where you start a new game). Interact
with it and it asks *"Would you like to put in a cheat code?"* —
Character Mode rides that same system:

1. Say yes and, at the text-entry screen, **type your character's code**
   from the tables below (codes are the character's name with spaces and
   punctuation removed, e.g. `LtSurge` for Lt. Surge).
2. You'll get a confirmation message and your character's starter
   Pokemon at Lv. 5.
3. From then on, catching or receiving any Pokemon **not on your
   character's roster sends it straight to the PC** instead of your
   party. Everything on-roster (including every evolution of a roster
   Pokemon) joins your party normally.

Notes:
- Eggs are always exempt (they join the party; enforcement applies to
  hatched/caught/gifted Pokemon).
- Battle Frontier–style rental Pokemon are never blocked.
- Your first party slot is never blocked (soft-lock protection).
- All of Radical Red's own cheat codes still work unchanged.

### Debug / utility codes

| Code | Effect |
|---|---|
| `CMDbgOff` | Turn Character Mode off (clears the flag and character selection) |
| `CMDbgGive1` | Test code: gives a Lv. 5 Pikachu (on-roster for Red → joins party) |
| `CMDbgGive2` | Test code: gives a Lv. 5 Meowth (off-roster for Red → goes to PC) |

## Known v1 limitations

- Characters keep the normal player sprite (no custom character sprites yet).

(In-game trades ARE enforced: Radical Red v4.1 has exactly one live in-game
trade — the Eternal Flower Floette console — and it politely refuses while
Character Mode is on, since that Floette is not on any character's canon
roster.)

## Character codes

### Generation 1

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Red` | Red | protagonist | Pikachu |
| `Leaf` | Leaf | protagonist | Eevee |
| `Blue` | Blue | champion | Pidgey |
| `Lance` | Lance | champion | Dratini |
| `Lorelei` | Lorelei | elite4 | Lapras |
| `Bruno` | Bruno | elite4 | Machop |
| `Agatha` | Agatha | elite4 | Gastly |
| `Koga` | Koga | elite4 | Koffing |
| `Brock` | Brock | gymleader | Onix |
| `Misty` | Misty | gymleader | Staryu |
| `LtSurge` | Lt. Surge | gymleader | Pikachu |
| `Erika` | Erika | gymleader | Oddish |
| `Sabrina` | Sabrina | gymleader | Abra |
| `Blaine` | Blaine | gymleader | Growlithe |
| `Giovanni` | Giovanni | villain | Rhyhorn |
| `Ash` | Ash | anime | Pikachu |
| `Gary` | Gary | anime | Squirtle |
| `Ritchie` | Ritchie | anime | Pikachu |
| `Tracey` | Tracey | anime | Scyther |
| `Jessie` | Jessie | anime | Ekans |
| `James` | James | anime | Koffing |
| `Oak` | Oak | professor | random from roster |

### Generation 2

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Ethan` | Ethan | protagonist | Cyndaquil |
| `Kris` | Kris | protagonist | Totodile |
| `Lyra` | Lyra | protagonist | Chikorita |
| `Will` | Will | elite4 | Natu |
| `Karen` | Karen | elite4 | Eevee |
| `Janine` | Janine | gymleader | Spinarak |
| `Falkner` | Falkner | gymleader | Hoothoot |
| `Bugsy` | Bugsy | gymleader | Scyther |
| `Whitney` | Whitney | gymleader | Miltank |
| `Morty` | Morty | gymleader | Gastly |
| `Chuck` | Chuck | gymleader | Poliwag |
| `Jasmine` | Jasmine | gymleader | Onix |
| `Pryce` | Pryce | gymleader | Swinub |
| `Clair` | Clair | gymleader | Horsea |
| `Silver` | Silver | rival | Totodile |
| `Archer` | Archer | villain | Houndour |
| `Ariana` | Ariana | villain | Ekans |
| `Elm` | Elm | professor | random from roster |

### Generation 3

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Brendan` | Brendan | protagonist | Treecko |
| `May` | May | protagonist | Torchic |
| `Steven` | Steven | champion | Beldum |
| `Wallace` | Wallace | champion | Feebas |
| `Sidney` | Sidney | elite4 | Absol |
| `Phoebe` | Phoebe | elite4 | Duskull |
| `Glacia` | Glacia | elite4 | Spheal |
| `Drake` | Drake | elite4 | Bagon |
| `Roxanne` | Roxanne | gymleader | Nosepass |
| `Brawly` | Brawly | gymleader | Makuhita |
| `Wattson` | Wattson | gymleader | Electrike |
| `Flannery` | Flannery | gymleader | Torkoal |
| `Norman` | Norman | gymleader | Slakoth |
| `Winona` | Winona | gymleader | Swablu |
| `Tate` | Tate | gymleader | Solrock |
| `Liza` | Liza | gymleader | Lunatone |
| `Juan` | Juan | gymleader | Horsea |
| `Wally` | Wally | rival | Ralts |
| `Maxie` | Maxie | villain | Numel |
| `Archie` | Archie | villain | Carvanha |
| `Drew` | Drew | anime | Budew |
| `Birch` | Birch | professor | random from roster |
| `Anabel` | Anabel | frontier | random from roster |
| `Tucker` | Tucker | frontier | random from roster |
| `Greta` | Greta | frontier | random from roster |
| `Spenser` | Spenser | frontier | random from roster |
| `Noland` | Noland | frontier | random from roster |
| `Lucy` | Lucy | frontier | random from roster |
| `Brandon` | Brandon | frontier | random from roster |

### Generation 4

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Lucas` | Lucas | protagonist | Turtwig |
| `Dawn` | Dawn | protagonist | Piplup |
| `Cynthia` | Cynthia | champion | Gible |
| `Aaron` | Aaron | elite4 | Skorupi |
| `Bertha` | Bertha | elite4 | Hippopotas |
| `Flint` | Flint | elite4 | Chimchar |
| `Lucian` | Lucian | elite4 | Bronzor |
| `Roark` | Roark | gymleader | Cranidos |
| `Gardenia` | Gardenia | gymleader | Budew |
| `Maylene` | Maylene | gymleader | Riolu |
| `CrasherWake` | Crasher Wake | gymleader | Buizel |
| `Fantina` | Fantina | gymleader | Misdreavus |
| `Byron` | Byron | gymleader | Shieldon |
| `Candice` | Candice | gymleader | Snorunt |
| `Volkner` | Volkner | gymleader | Shinx |
| `Barry` | Barry | rival | Piplup |
| `Cyrus` | Cyrus | villain | Sneasel |
| `Mars` | Mars | villain | Glameow |
| `Jupiter` | Jupiter | villain | Stunky |
| `Saturn` | Saturn | villain | Croagunk |
| `Paul` | Paul | anime | Elekid |
| `Zoey` | Zoey | anime | Glameow |
| `Nando` | Nando | anime | Budew |
| `Tobias` | Tobias | anime | Darkrai |
| `Rowan` | Rowan | professor | random from roster |
| `Palmer` | Palmer | frontier | random from roster |
| `Dahlia` | Dahlia | frontier | random from roster |
| `Darach` | Darach | frontier | random from roster |
| `Argenta` | Argenta | frontier | random from roster |
| `Thorton` | Thorton | frontier | random from roster |

### Generation 5

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Hilbert` | Hilbert | protagonist | Oshawott |
| `Hilda` | Hilda | protagonist | Tepig |
| `Nate` | Nate | protagonist | random from roster |
| `Rosa` | Rosa | protagonist | Snivy |
| `Alder` | Alder | champion | Larvesta |
| `Iris` | Iris | champion | Axew |
| `Shauntal` | Shauntal | elite4 | Litwick |
| `Marshal` | Marshal | elite4 | Timburr |
| `Grimsley` | Grimsley | elite4 | Pawniard |
| `Caitlin` | Caitlin | elite4 | Gothita |
| `Cilan` | Cilan | gymleader | Pansage |
| `Chili` | Chili | gymleader | Pansear |
| `Cress` | Cress | gymleader | Panpour |
| `Lenora` | Lenora | gymleader | Patrat |
| `Burgh` | Burgh | gymleader | Sewaddle |
| `Elesa` | Elesa | gymleader | Blitzle |
| `Clay` | Clay | gymleader | Drilbur |
| `Skyla` | Skyla | gymleader | Ducklett |
| `Brycen` | Brycen | gymleader | Cubchoo |
| `Drayden` | Drayden | gymleader | Axew |
| `Cheren` | Cheren | gymleader | Lillipup |
| `Roxie` | Roxie | gymleader | Venipede |
| `Marlon` | Marlon | gymleader | Frillish |
| `Bianca` | Bianca | rival | Tepig |
| `Hugh` | Hugh | rival | random from roster |
| `N` | N | rival | Zorua |
| `Ghetsis` | Ghetsis | villain | Deino |
| `Colress` | Colress | villain | Klink |
| `Trip` | Trip | anime | Snivy |
| `Juniper` | Juniper | professor | random from roster |
| `Ingo` | Ingo | frontier | random from roster |

### Generation 6

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Calem` | Calem | protagonist | random from roster |
| `Serena` | Serena | protagonist | Fennekin |
| `Diantha` | Diantha | champion | Ralts |
| `Malva` | Malva | elite4 | Fletchling |
| `Siebold` | Siebold | elite4 | Clauncher |
| `Wikstrom` | Wikstrom | elite4 | Honedge |
| `Drasna` | Drasna | elite4 | Noibat |
| `Viola` | Viola | gymleader | Scatterbug |
| `Grant` | Grant | gymleader | Tyrunt |
| `Korrina` | Korrina | gymleader | Riolu |
| `Ramos` | Ramos | gymleader | Skiddo |
| `Clemont` | Clemont | gymleader | Helioptile |
| `Valerie` | Valerie | gymleader | Eevee |
| `Olympia` | Olympia | gymleader | Espurr |
| `Wulfric` | Wulfric | gymleader | Bergmite |
| `Shauna` | Shauna | rival | Chespin |
| `Lysandre` | Lysandre | villain | Magikarp |
| `Alain` | Alain | anime | Charmander |
| `Sawyer` | Sawyer | anime | Treecko |
| `Sycamore` | Sycamore | professor | random from roster |

### Generation 7

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Elio` | Elio | protagonist | Popplio |
| `Selene` | Selene | protagonist | Rowlet |
| `Kukui` | Kukui | champion | Litten |
| `Hau` | Hau | champion | Pichu |
| `Molayne` | Molayne | elite4 | Diglett |
| `Kahili` | Kahili | elite4 | Pikipek |
| `Acerola` | Acerola | elite4 | Sandygast |
| `Hala` | Hala | gymleader | Crabrawler |
| `Olivia` | Olivia | gymleader | Rockruff |
| `Nanu` | Nanu | gymleader | Meowth |
| `Hapu` | Hapu | gymleader | Mudbray |
| `Gladion` | Gladion | rival | Type: Null |
| `Guzma` | Guzma | villain | Wimpod |
| `Plumeria` | Plumeria | villain | Salandit |
| `Lusamine` | Lusamine | villain | Stufful |
| `Lillie` | Lillie (anime) | anime | Vulpix |
| `Kiawe` | Kiawe (anime) | anime | Turtonator |
| `Lana` | Lana (anime) | anime | Popplio |
| `Mallow` | Mallow (anime) | anime | Bounsweet |
| `Sophocles` | Sophocles | anime | Togedemaru |
| `Burnet` | Burnet | professor | random from roster |
| `SamsonOak` | Samson Oak | professor | random from roster |

### Generation 8

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Victor` | Victor | protagonist | random from roster |
| `Gloria` | Gloria | protagonist | random from roster |
| `Leon` | Leon | champion | Charmander |
| `Milo` | Milo | gymleader | Gossifleur |
| `Nessa` | Nessa | gymleader | Chewtle |
| `Kabu` | Kabu | gymleader | Sizzlipede |
| `Bea` | Bea | gymleader | Machop |
| `Allister` | Allister | gymleader | Gastly |
| `Opal` | Opal | gymleader | Milcery |
| `Gordie` | Gordie | gymleader | Rolycoly |
| `Melony` | Melony | gymleader | Lapras |
| `Piers` | Piers | gymleader | Zigzagoon |
| `Raihan` | Raihan | gymleader | Duraludon |
| `Hop` | Hop | rival | Wooloo |
| `Bede` | Bede | rival | Hatenna |
| `Marnie` | Marnie | rival | Morpeko |
| `Rose` | Rose | villain | Cufant |
| `Goh` | Goh | anime | Scorbunny |
| `Chloe` | Chloe | anime | Eevee |
| `Magnolia` | Magnolia | professor | random from roster |
| `Sonia` | Sonia | professor | random from roster |
| `Laventon` | Laventon | professor | random from roster |
| `Cerise` | Cerise | professor | random from roster |
| `Volo` | Volo | villain | Togepi |
| `Adaman` | Adaman | rival | random from roster |
| `Akari` | Akari | protagonist | random from roster |
| `Arezu` | Arezu | warden | random from roster |
| `Beni` | Beni | villain | random from roster |
| `Calaba` | Calaba | warden | random from roster |
| `Charm` | Charm | villain | random from roster |
| `Clover` | Clover | villain | random from roster |
| `Cogita` | Cogita | other | random from roster |
| `Coin` | Coin | villain | random from roster |
| `Cyllene` | Cyllene | galaxy | random from roster |
| `Gaeric` | Gaeric | warden | random from roster |
| `Irida` | Irida | rival | random from roster |
| `Iscan` | Iscan | warden | random from roster |
| `Kamado` | Kamado | villain | random from roster |
| `Lian` | Lian | warden | random from roster |
| `Mai` | Mai | warden | random from roster |
| `Melli` | Melli | warden | random from roster |
| `Palina` | Palina | warden | random from roster |
| `Pesselle` | Pesselle | galaxy | random from roster |
| `Rei` | Rei | protagonist | random from roster |
| `Ress` | Ress | galaxy | random from roster |
| `Rye` | Rye | galaxy | random from roster |
| `Sabi` | Sabi | warden | random from roster |
| `Sanqua` | Sanqua | galaxy | random from roster |
| `Zisu` | Zisu | galaxy | random from roster |

### Generation 9

| Type this code | Character | Role | Starter Pokemon |
|---|---|---|---|
| `Geeta` | Geeta | champion | Glimmet |
| `Nemona` | Nemona | champion | Pawmi |
| `Rika` | Rika | elite4 | Wooper |
| `Poppy` | Poppy | elite4 | Tinkatink |
| `Hassel` | Hassel | elite4 | Frigibax |
| `Katy` | Katy | gymleader | Teddiursa |
| `Brassius` | Brassius | gymleader | Bonsly |
| `Iono` | Iono | gymleader | Tadbulb |
| `Kofu` | Kofu | gymleader | Crabrawler |
| `Larry` | Larry | gymleader | Starly |
| `Ryme` | Ryme | gymleader | Toxel |
| `Tulip` | Tulip | gymleader | Flabébé |
| `Grusha` | Grusha | gymleader | Cetoddle |
| `Arven` | Arven | rival | Maschiff |
| `Penny` | Penny | rival | Eevee |
| `Sada` | Sada | professor | random from roster |
| `Turo` | Turo | professor | random from roster |

## For developers

`tools/inject_character_mode.py` rebuilds everything (shim, bitmaps,
selection scripts, patched ROM, BPS) from a pinned v4.1 ROM at
`rom/radicalred 4.1.gba`. Tests live in `tools/tests/`
(`shim_unit_test.py`, `run_boot_smoke.sh`, `verify_artifacts.py`).
See `CLAUDE.md` and `docs/ROUTINE_MAP.md` for the full reverse-engineering
record.
