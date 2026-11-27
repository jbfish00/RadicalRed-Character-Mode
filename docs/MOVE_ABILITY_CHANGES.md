# Radical Red: move, ability and stat changes

> **Generated 2026-11-26** from the repo manifests by `make_change_docs.py`. Sections 1-3 are in the shipped release; section 4 (Planned) is **not in any release**.
>
> Status: 13 cards pushed (04e6fa9, build 5e7b19b9).

The change sets here apply with Character Mode on or off (they change the game's move data). Source manifest: `RadicalRed-Character-Mode/tools/character_mode/move_changes.json`.

## 1. Move values

Every move the hack changed is raised to the best value any generation gave it (accuracy, PP, power, effect chance, priority, type). **450 moves changed**: 66 power, 397 pp, 18 accuracy, 41 effect %, 8 priority, 8 type edits. Cells read old → new.

| Move | Power | PP | Accuracy | Effect % | Priority | Type |
|---|---|---|---|---|---|---|
| Comet Punch | 18 → 30 |  |  |  |  |  |
| Fire Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Ice Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Thunder Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Guillotine |  | 5 → 8 |  |  |  |  |
| Swords Dance |  | 20 → 30 |  |  |  |  |
| Cut |  | 25 → 30 |  |  |  | Steel → Normal |
| Whirlwind |  | 5 → 20 |  |  | -6 → 0 |  |
| Fly |  | 15 → 16 |  |  |  |  |
| Mega Kick |  | 5 → 8 |  |  |  |  |
| Jump Kick |  | 10 → 25 |  |  |  |  |
| Horn Drill |  | 5 → 8 |  |  |  |  |
| Tackle | 40 → 50 |  |  |  |  |  |
| Body Slam |  | 15 → 16 |  |  |  |  |
| Thrash |  | 10 → 20 |  |  |  |  |
| Double-Edge |  | 15 → 16 |  |  |  |  |
| Poison Sting | 15 → 30 |  |  | 30 → 50 |  |  |
| Growl |  | 15 → 40 |  |  |  |  |
| Roar |  | 5 → 20 |  |  | -6 → 0 |  |
| Sing |  | 15 → 16 |  |  |  |  |
| Acid |  |  |  | 10 → 33 |  |  |
| Ember |  |  |  | 10 → 30 |  |  |
| Flamethrower | 90 → 95 | 15 → 16 |  | 10 → 20 |  |  |
| Hydro Pump | 110 → 120 | 5 → 8 | 80 → 85 |  |  |  |
| Surf | 90 → 95 | 15 → 16 |  |  |  |  |
| Ice Beam | 90 → 95 | 10 → 12 |  | 10 → 20 |  |  |
| Blizzard | 110 → 120 | 5 → 8 | 70 → 90 | 10 → 30 |  |  |
| Bubble Beam |  |  |  | 10 → 33 |  |  |
| Aurora Beam |  |  |  | 10 → 33 |  |  |
| Hyper Beam |  | 5 → 8 |  |  |  |  |
| Submission |  | 20 → 25 |  |  |  |  |
| Counter |  |  |  |  | -5 → -1 |  |
| Absorb | 25 → 40 |  |  |  |  |  |
| Mega Drain | 60 → 75 |  |  |  |  |  |
| Leech Seed |  | 10 → 12 |  |  |  |  |
| Growth |  | 20 → 40 |  |  |  | Normal → Grass |
| Solar Beam | 120 → 200 | 10 → 12 |  |  |  |  |
| Poison Powder |  |  | 75 → 80 |  |  |  |
| Stun Spore |  |  | 75 → 80 |  |  |  |
| Sleep Powder |  | 15 → 20 | 75 → 80 |  |  |  |
| Petal Dance |  | 10 → 20 |  |  |  |  |
| Fire Spin |  | 15 → 16 |  |  |  |  |
| Thunder Shock |  |  |  | 10 → 30 |  |  |
| Thunderbolt | 90 → 95 | 15 → 16 |  | 10 → 20 |  |  |
| Thunder Wave |  |  | 90 → 100 |  |  |  |
| Thunder | 110 → 120 | 10 → 12 | 70 → 75 |  |  |  |
| Earthquake |  | 10 → 12 |  |  |  |  |
| Spectral Thief |  | 5 → 10 |  |  |  | Psychic → Ghost |
| Dig | 80 → 100 | 10 → 12 |  |  |  |  |
| Toxic |  | 10 → 12 |  |  |  |  |
| Psychic |  | 10 → 12 |  | 10 → 33 |  |  |
| Hypnosis |  |  | 60 → 70 |  |  |  |
| Teleport |  |  |  |  | -6 → 0 |  |
| Night Shade |  | 15 → 16 |  |  |  |  |
| Double Team |  | 15 → 16 |  |  |  |  |
| Recover |  | 5 → 20 |  |  |  |  |
| Minimize |  | 10 → 20 |  |  |  |  |
| Smokescreen |  | 10 → 20 |  |  |  |  |
| Confuse Ray |  | 10 → 12 |  |  |  |  |
| Barrier |  | 20 → 30 |  |  |  |  |
| Haze |  | 5 → 30 |  |  |  |  |
| Self-Destruct | 100 → 200 | 5 → 8 |  |  |  |  |
| Sludge |  |  |  | 30 → 40 |  |  |
| Fire Blast | 110 → 120 | 5 → 8 |  | 10 → 30 |  |  |
| Waterfall |  | 15 → 16 |  |  |  |  |
| Skull Bash | 130 → 150 | 10 → 15 |  |  |  |  |
| Constrict |  |  |  | 10 → 33 |  |  |
| Soft-Boiled |  | 5 → 10 |  |  |  |  |
| High Jump Kick |  | 10 → 20 |  |  |  |  |
| Sky Attack | 140 → 200 | 5 → 8 |  |  |  |  |
| Transform |  | 10 → 12 |  |  |  |  |
| Bubble |  |  |  | 10 → 33 |  |  |
| Flash |  | 10 → 20 |  |  |  | Electric → Normal |
| Acid Armor |  | 20 → 40 |  |  |  |  |
| Crabhammer |  | 10 → 12 | 90 → 95 |  |  |  |
| Explosion | 150 → 250 | 5 → 8 |  |  |  |  |
| Bonemerang | 50 → 55 |  |  |  |  |  |
| Rest |  | 5 → 10 |  |  |  |  |
| Rock Slide |  | 10 → 12 |  | 20 → 30 |  |  |
| Tri Attack |  | 10 → 12 |  | 20 → 30 |  |  |
| Super Fang |  | 10 → 12 |  |  |  |  |
| Slash | 70 → 80 |  |  |  |  |  |
| Substitute |  | 10 → 12 |  |  |  |  |
| Struggle |  | 1 → 10 |  |  |  |  |
| Nightmare |  |  | 100 → 101 |  |  |  |
| Flame Wheel |  |  |  | 10 → 30 |  |  |
| Snore |  | 15 → 16 |  |  |  |  |
| Curse |  | 10 → 12 |  |  |  |  |
| Flail |  | 15 → 16 |  |  |  |  |
| Reversal |  | 15 → 16 |  |  |  |  |
| Spite |  | 10 → 12 |  |  |  |  |
| Powder Snow |  |  |  | 10 → 30 |  |  |
| Scary Face |  | 10 → 12 |  |  |  |  |
| Sweet Kiss |  | 10 → 12 |  |  |  |  |
| Belly Drum |  | 10 → 12 |  |  |  |  |
| Sludge Bomb |  | 10 → 12 |  |  |  |  |
| Mud-Slap |  | 10 → 20 |  |  |  |  |
| Octazooka |  | 10 → 15 |  |  |  |  |
| Zap Cannon |  | 5 → 8 |  |  |  |  |
| Destiny Bond |  | 5 → 8 |  |  |  |  |
| Perish Song |  | 5 → 8 |  |  |  |  |
| Icy Wind | 55 → 60 | 15 → 20 |  |  |  |  |
| Detect |  | 5 → 8 |  |  |  |  |
| Bone Rush | 25 → 30 | 10 → 12 |  |  |  |  |
| Lock-On |  | 5 → 8 |  |  |  |  |
| Outrage |  | 10 → 15 |  |  |  |  |
| Giga Drain |  | 10 → 12 |  |  |  |  |
| Endure |  | 10 → 12 |  |  |  |  |
| Charm |  | 5 → 20 |  |  |  |  |
| Rollout | 30 → 60 |  |  |  |  |  |
| Swagger |  | 15 → 16 |  |  |  |  |
| Milk Drink |  | 5 → 10 |  |  |  |  |
| Mean Look |  | 5 → 8 |  |  |  |  |
| Attract |  | 15 → 16 |  |  |  |  |
| Sleep Talk |  | 10 → 12 |  |  |  |  |
| Heal Bell |  | 5 → 8 |  |  |  |  |
| Dynamic Punch |  | 5 → 8 |  |  |  |  |
| Megahorn |  | 10 → 12 |  |  |  |  |
| Encore |  | 5 → 8 |  |  |  |  |
| Iron Tail |  | 15 → 16 |  |  |  |  |
| Morning Sun |  | 5 → 8 |  |  |  |  |
| Synthesis |  | 5 → 8 |  |  |  |  |
| Moonlight |  | 5 → 8 |  |  |  |  |
| Cross Chop |  | 5 → 8 |  |  |  |  |
| Twister |  | 20 → 25 |  |  |  |  |
| Rain Dance |  | 5 → 8 |  |  |  |  |
| Sunny Day |  | 5 → 8 |  |  |  |  |
| Crunch |  | 15 → 16 |  |  |  |  |
| Mirror Coat |  |  |  |  | -5 → -1 |  |
| Psych Up |  | 10 → 12 |  |  |  |  |
| Extreme Speed |  | 5 → 8 |  |  |  |  |
| Ancient Power |  | 5 → 15 |  | 10 → 20 |  |  |
| Shadow Ball |  | 15 → 16 |  |  |  |  |
| Future Sight |  | 10 → 15 |  |  |  |  |
| Rock Smash |  | 15 → 20 |  |  |  |  |
| Whirlpool |  | 15 → 16 |  |  |  |  |
| Beat Up |  | 10 → 12 |  |  |  |  |
| Fake Out |  | 5 → 12 |  |  |  |  |
| Uproar |  | 10 → 12 |  |  |  |  |
| Spit Up |  | 10 → 12 |  |  |  |  |
| Swallow |  | 10 → 12 |  |  |  |  |
| Heat Wave | 95 → 100 | 10 → 12 |  |  |  |  |
| Torment |  | 15 → 16 |  |  |  |  |
| Flatter |  | 15 → 16 |  |  |  |  |
| Will-O-Wisp |  | 15 → 16 |  |  |  |  |
| Memento |  | 10 → 12 | 100 → 101 |  |  |  |
| Facade | 70 → 75 |  |  |  |  |  |
| Smelling Salts |  |  |  |  |  | Fighting → Normal |
| Follow Me |  |  |  |  | 2 → 3 |  |
| Trick |  | 10 → 12 |  |  |  |  |
| Role Play |  | 10 → 12 |  |  |  |  |
| Superpower |  | 5 → 8 |  |  |  |  |
| Recycle |  | 10 → 12 |  |  |  |  |
| Brick Break |  | 15 → 16 |  |  |  |  |
| Yawn |  | 10 → 12 |  |  |  |  |
| Endeavor |  | 5 → 8 |  |  |  |  |
| Eruption |  | 5 → 8 |  |  |  |  |
| Skill Swap |  | 10 → 12 |  |  |  |  |
| Imprison |  | 10 → 12 |  |  |  |  |
| Dive |  | 10 → 12 |  |  |  |  |
| Feather Dance |  | 5 → 16 |  |  |  |  |
| Blaze Kick |  | 10 → 12 |  |  |  |  |
| Ice Ball | 30 → 40 |  |  |  |  |  |
| Slack Off |  | 5 → 10 |  |  |  |  |
| Hyper Voice |  | 10 → 12 |  |  |  |  |
| Poison Fang |  | 15 → 16 |  |  |  |  |
| Crush Claw |  | 10 → 12 |  |  |  |  |
| Blast Burn |  | 4 → 8 |  |  |  |  |
| Hydro Cannon |  | 4 → 8 |  |  |  |  |
| Meteor Mash | 90 → 100 | 10 → 12 |  |  |  |  |
| Astonish |  | 15 → 25 |  |  |  |  |
| Weather Ball |  | 10 → 12 |  |  |  |  |
| Overheat | 130 → 140 | 5 → 8 |  |  |  |  |
| Rock Tomb |  | 15 → 16 |  |  |  |  |
| Silver Wind |  | 5 → 15 |  | 10 → 20 |  |  |
| Water Spout |  | 5 → 8 |  |  |  |  |
| Extrasensory |  | 20 → 30 |  |  |  |  |
| Sand Tomb |  | 15 → 16 |  |  |  |  |
| Sheer Cold |  | 5 → 8 |  |  |  |  |
| Muddy Water |  | 10 → 12 |  |  |  |  |
| Iron Defense |  | 15 → 20 |  |  |  |  |
| Block |  | 5 → 8 |  |  |  |  |
| Dragon Claw |  | 15 → 16 |  |  |  |  |
| Frenzy Plant |  | 4 → 8 |  |  |  |  |
| Bounce |  | 5 → 8 |  |  |  |  |
| Mud Shot |  | 15 → 16 |  |  |  |  |
| Covet |  | 25 → 40 |  |  |  | Fairy → Normal |
| Volt Tackle |  | 15 → 16 |  | 10 → 30 |  |  |
| Leaf Blade |  | 15 → 16 |  |  |  |  |
| Rock Blast |  | 10 → 12 |  |  |  |  |
| Water Pulse |  |  | 100 → 101 |  |  |  |
| Air Slash |  | 15 → 20 |  |  |  |  |
| Aqua Tail |  | 10 → 12 |  |  |  |  |
| Aura Sphere | 80 → 90 |  |  |  |  |  |
| Avalanche |  | 10 → 12 |  |  |  |  |
| Brave Bird |  | 15 → 16 |  |  |  |  |
| Bug Buzz |  | 10 → 12 |  | 10 → 20 |  |  |
| Charge Beam |  | 10 → 15 |  |  |  |  |
| Close Combat |  | 5 → 8 |  |  |  |  |
| Cross Poison |  |  |  | 10 → 20 |  |  |
| Dark Pulse |  | 15 → 16 | 100 → 101 |  |  |  |
| Discharge |  | 15 → 16 |  |  |  |  |
| Draco Meteor | 130 → 140 | 5 → 8 |  |  |  |  |
| Dragon Pulse | 85 → 90 | 10 → 12 | 100 → 101 |  |  |  |
| Drain Punch |  | 10 → 12 |  |  |  |  |
| Earth Power |  | 10 → 12 |  | 10 → 20 |  |  |
| Energy Ball |  | 10 → 12 |  | 10 → 20 |  |  |
| Focus Blast |  | 5 → 8 |  |  |  |  |
| Giga Impact |  | 5 → 8 |  |  |  |  |
| Gunk Shot |  | 5 → 8 |  |  |  |  |
| Hammer Arm |  | 10 → 12 |  |  |  |  |
| Head Smash |  | 5 → 8 |  |  |  |  |
| Iron Head |  | 15 → 16 |  |  |  |  |
| Lava Plume |  | 15 → 16 |  |  |  |  |
| Magnet Bomb | 60 → 95 |  |  |  |  |  |
| Mud Bomb |  | 10 → 15 |  |  |  |  |
| Night Slash |  | 15 → 20 |  |  |  |  |
| Ominous Wind |  | 5 → 15 |  | 10 → 20 |  |  |
| Power Whip |  | 10 → 12 |  |  |  |  |
| Rock Wrecker |  | 5 → 8 |  |  |  |  |
| Roost |  | 5 → 10 |  |  |  |  |
| Seed Bomb |  | 15 → 16 |  |  |  |  |
| Shadow Claw |  | 15 → 16 |  |  |  |  |
| X-Scissor |  | 15 → 16 |  |  |  |  |
| Zen Headbutt |  | 15 → 16 |  |  |  |  |
| Switcheroo |  | 10 → 12 |  |  |  |  |
| Drill Run |  | 10 → 12 |  |  |  |  |
| Electroweb |  | 15 → 16 |  |  |  |  |
| Frost Breath | 60 → 65 | 10 → 12 |  |  |  |  |
| Horn Leech |  | 10 → 12 |  |  |  |  |
| Hurricane | 110 → 120 | 10 → 12 | 70 → 75 |  |  |  |
| Icicle Crash |  | 10 → 12 |  |  |  |  |
| Low Sweep | 60 → 65 |  |  |  |  |  |
| Snarl | 55 → 60 | 15 → 16 |  |  |  |  |
| Storm Throw | 60 → 65 | 10 → 12 |  |  |  |  |
| Venoshock |  | 10 → 15 |  |  |  |  |
| Wild Charge |  | 15 → 16 |  |  |  |  |
| Fiery Dance |  | 10 → 12 |  |  |  |  |
| Clear Smog |  | 15 → 16 |  |  |  |  |
| Leaf Storm | 130 → 140 | 5 → 8 |  |  |  |  |
| Stone Edge |  | 5 → 8 |  |  |  |  |
| Payback |  | 10 → 12 |  |  |  |  |
| Fire Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Ice Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Thunder Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Flare Blitz |  | 15 → 16 |  | 10 → 20 |  |  |
| Inferno |  | 5 → 8 |  |  |  |  |
| Hex |  | 10 → 15 |  |  |  |  |
| Dual Chop | 40 → 45 |  |  |  |  |  |
| Double Hit | 35 → 50 | 10 → 12 |  |  |  |  |
| Cotton Guard |  | 10 → 12 |  |  |  |  |
| Acrobatics |  | 15 → 16 |  |  |  |  |
| Dragon Tail |  | 10 → 12 |  |  |  |  |
| Circle Throw |  | 5 → 12 |  |  |  |  |
| Wood Hammer |  | 15 → 16 |  |  |  |  |
| Heal Pulse |  | 10 → 12 |  |  |  |  |
| Flash Cannon |  | 10 → 12 |  | 10 → 20 |  |  |
| Shell Smash |  | 15 → 16 |  |  |  |  |
| Rage Powder |  |  |  |  | 2 → 3 |  |
| Razor Shell |  | 10 → 12 |  |  |  |  |
| Sucker Punch | 70 → 80 | 5 → 8 |  |  |  |  |
| Scald |  | 15 → 16 |  |  |  |  |
| Baby-Doll Eyes |  | 10 → 30 |  |  |  |  |
| Play Rough |  | 10 → 12 |  | 10 → 20 |  |  |
| Moonblast |  | 15 → 16 |  |  |  |  |
| Draining Kiss |  | 10 → 15 |  |  |  |  |
| Dazzling Gleam |  | 10 → 12 |  |  |  |  |
| Healing Wish |  | 10 → 12 |  |  |  |  |
| Tailwind |  | 15 → 30 |  |  |  |  |
| Boomburst |  | 10 → 12 |  |  |  |  |
| Worry Seed |  | 10 → 12 |  |  |  |  |
| Gastro Acid |  | 10 → 12 |  |  |  |  |
| Shift Gear |  | 10 → 12 |  |  |  |  |
| Stored Power |  | 10 → 12 |  |  |  |  |
| Assurance |  | 10 → 12 |  |  |  |  |
| Dragon Rush |  | 10 → 12 |  |  |  |  |
| Dark Void |  |  | 80 → 90 |  |  |  |
| Feint | 30 → 50 | 10 → 12 |  |  |  |  |
| Phantom Force |  | 10 → 12 |  |  |  |  |
| Petal Blizzard |  | 15 → 16 |  |  |  |  |
| Play Nice |  | 10 → 20 |  |  |  |  |
| Roar of Time | 80 → 150 |  |  |  | -6 → 0 |  |
| Magma Storm | 100 → 120 |  |  |  |  |  |
| Final Gambit |  | 5 → 8 |  |  |  |  |
| Judgment |  | 5 → 10 |  |  |  |  |
| Psyshock |  | 10 → 12 |  |  |  |  |
| Round |  | 15 → 16 |  |  |  |  |
| Tail Slap |  | 10 → 12 |  |  |  |  |
| Gear Grind | 50 → 60 |  |  |  |  |  |
| Smack Down |  | 15 → 16 |  |  |  |  |
| Gyro Ball |  | 5 → 8 |  |  |  |  |
| Heal Order |  | 5 → 10 |  |  |  |  |
| Defog |  | 15 → 16 |  |  |  |  |
| Guard Swap |  | 10 → 12 |  |  |  |  |
| Metal Burst |  | 10 → 12 |  |  |  |  |
| Power Swap |  | 10 → 12 |  |  |  |  |
| Power Trick |  | 10 → 12 |  |  |  |  |
| King's Shield |  | 5 → 10 |  |  |  |  |
| Sludge Wave |  | 10 → 12 |  |  |  |  |
| Heavy Slam |  | 10 → 12 |  |  |  |  |
| Synchronoise |  | 10 → 15 |  |  |  |  |
| Electro Ball |  | 10 → 12 |  |  |  |  |
| Foul Play |  | 15 → 16 |  |  |  |  |
| Entrainment |  | 15 → 16 |  |  |  |  |
| Night Daze |  | 10 → 12 |  |  |  |  |
| Sacred Sword |  | 15 → 20 |  |  |  |  |
| Heat Crash |  | 10 → 12 |  |  |  |  |
| Mystical Fire |  | 10 → 12 |  |  |  |  |
| Spiky Shield |  | 5 → 10 |  |  |  |  |
| Eerie Impulse |  | 15 → 16 |  |  |  |  |
| Anchor Shot | 80 → 90 |  |  |  |  |  |
| Baneful Bunker |  | 5 → 10 |  |  |  |  |
| Beak Blast | 100 → 120 |  |  |  |  |  |
| Burn Up |  | 5 → 8 |  |  |  |  |
| Clanging Scales |  | 5 → 8 |  |  |  |  |
| Darkest Lariat |  | 10 → 12 |  |  |  |  |
| Fire Lash | 80 → 90 | 15 → 16 |  |  |  |  |
| First Impression | 90 → 100 | 10 → 12 |  |  |  |  |
| High Horsepower |  | 10 → 12 |  |  |  |  |
| Ice Hammer |  | 10 → 12 |  |  |  |  |
| Liquidation |  | 10 → 12 |  |  |  |  |
| Lunge |  | 10 → 16 |  |  |  |  |
| Pollen Puff |  | 15 → 16 |  |  |  |  |
| Power Trip |  | 10 → 12 |  |  |  |  |
| Prismatic Laser |  | 4 → 10 |  |  |  |  |
| Psychic Fangs |  | 10 → 12 |  |  |  |  |
| Shore Up |  | 5 → 10 |  |  |  |  |
| Smart Strike |  | 10 → 12 |  |  |  |  |
| Solar Blade |  | 10 → 12 |  |  |  |  |
| Sparkling Aria |  | 10 → 12 |  |  |  |  |
| Speed Swap |  | 10 → 12 |  |  |  |  |
| Spirit Shackle | 80 → 90 | 10 → 12 |  |  |  |  |
| Stomping Tantrum |  | 10 → 12 |  |  |  |  |
| Strength Sap |  | 5 → 10 |  |  |  |  |
| Throat Chop |  | 15 → 16 |  |  |  |  |
| Trop Kick | 70 → 85 | 10 → 16 |  |  |  |  |
| Zing Zap |  | 10 → 12 |  |  |  |  |
| Electric Terrain |  | 10 → 12 |  |  |  |  |
| Grassy Terrain |  | 10 → 12 |  |  |  |  |
| Misty Terrain |  | 10 → 12 |  |  |  |  |
| Psychic Terrain |  | 10 → 12 |  |  |  |  |
| Trick Room |  | 5 → 8 |  |  |  |  |
| Magic Room |  | 10 → 12 |  |  |  |  |
| Wonder Room |  | 10 → 12 |  |  |  |  |
| Quick Guard |  | 15 → 16 |  |  |  |  |
| Wide Guard |  | 10 → 12 |  |  |  |  |
| Belch |  | 10 → 12 |  |  |  |  |
| Fling |  | 10 → 12 |  |  |  |  |
| Flying Press |  | 10 → 12 |  |  |  |  |
| Gravity |  | 5 → 8 |  |  |  |  |
| Guard Split |  | 10 → 12 |  |  |  |  |
| Magnet Rise |  | 10 → 12 |  |  |  |  |
| Power Split |  | 10 → 12 |  |  |  |  |
| Reflect Type |  | 15 → 16 |  |  |  |  |
| Simple Beam |  | 15 → 16 |  |  |  |  |
| Fairy Lock |  | 10 → 12 |  |  |  |  |
| Light of Ruin |  | 5 → 8 |  |  |  |  |
| After You |  | 15 → 16 |  |  |  |  |
| Instruct |  | 15 → 16 |  |  |  |  |
| Quash |  | 15 → 16 |  |  |  |  |
| Last Resort |  | 5 → 8 |  |  |  |  |
| Snipe Shot | 70 → 85 | 15 → 16 |  |  |  |  |
| Jaw Lock |  | 10 → 12 |  |  |  | Fighting → Dark |
| Stuff Cheeks |  | 10 → 12 |  |  |  |  |
| No Retreat |  | 5 → 8 |  |  |  |  |
| Dragon Darts |  | 10 → 12 |  |  |  |  |
| Teatime |  | 10 → 12 |  |  |  |  |
| Octolock |  | 15 → 16 |  |  |  |  |
| Fishious Rend |  | 5 → 10 |  |  |  |  |
| Court Change |  | 10 → 12 |  |  |  |  |
| Clangorous Soul |  | 5 → 8 |  |  |  |  |
| Body Press |  | 10 → 12 |  |  |  |  |
| Decorate |  | 15 → 16 |  |  |  |  |
| Drum Beating |  | 10 → 12 |  |  |  |  |
| Snap Trap |  | 5 → 16 | 85 → 100 |  |  |  |
| Pyro Ball |  | 5 → 8 |  |  |  |  |
| Aura Wheel |  | 10 → 12 |  |  |  |  |
| Breaking Swipe |  | 10 → 16 |  |  |  |  |
| Overdrive |  | 10 → 12 |  |  |  |  |
| Apple Acid | 80 → 90 | 10 → 12 |  |  |  |  |
| Grav Apple | 80 → 90 | 10 → 12 |  |  |  |  |
| Spirit Break |  | 15 → 16 |  |  |  |  |
| Life Dew |  | 10 → 12 |  |  |  |  |
| Obstruct |  | 5 → 10 |  |  |  |  |
| Meteor Assault | 160 → 170 | 4 → 8 |  |  |  |  |
| Steel Beam |  | 5 → 8 |  |  |  |  |
| Steel Roller |  | 5 → 8 |  |  |  |  |
| Meteor Beam |  | 10 → 12 |  |  |  |  |
| Shell Side Arm |  | 10 → 12 |  | 10 → 20 |  |  |
| Misty Explosion |  | 5 → 8 |  |  |  |  |
| Grassy Glide | 55 → 70 |  |  |  |  |  |
| Terrain Pulse |  | 10 → 12 |  |  |  |  |
| Skitter Smack |  | 10 → 12 |  |  |  |  |
| Burning Jealousy |  | 5 → 8 |  |  |  |  |
| Lash Out |  | 5 → 8 |  |  |  |  |
| Poltergeist |  | 5 → 8 |  |  |  |  |
| Coaching |  | 10 → 12 |  |  |  |  |
| Triple Axel | 20 → 40 | 10 → 12 |  |  |  |  |
| Dual Wingbeat | 40 → 45 | 10 → 12 |  |  |  |  |
| Scorching Sands |  | 10 → 12 |  |  |  |  |
| Jungle Healing |  | 5 → 10 |  |  |  |  |
| Wicked Blow | 75 → 80 |  |  |  |  |  |
| Glacial Lance | 120 → 130 |  |  |  |  |  |
| Stone Axe |  | 15 → 16 |  |  |  |  |
| Headlong Rush |  | 5 → 8 |  |  |  |  |
| Infernal Parade | 60 → 65 | 15 → 16 |  |  |  |  |
| Ceaseless Edge |  | 15 → 16 |  |  |  |  |
| Chloroblast | 120 → 150 |  |  |  |  |  |
| Bitter Malice | 60 → 75 |  |  | 30 → 100 |  |  |
| Dire Claw |  | 15 → 16 |  |  |  |  |
| Mountain Gale |  | 5 → 12 |  |  |  |  |
| Psyshield Bash | 70 → 90 | 10 → 12 |  |  |  |  |
| Flower Trick |  | 10 → 12 |  |  |  |  |
| Torch Song |  | 10 → 12 |  |  |  |  |
| Aqua Step |  | 10 → 12 |  |  |  |  |
| Hyper Drill | 100 → 120 |  |  |  |  |  |
| Armor Cannon |  | 5 → 8 |  |  |  |  |
| Bitter Blade |  | 10 → 12 |  |  |  |  |
| Aqua Cutter |  | 10 → 20 |  |  |  |  |
| Rage Fist |  | 10 → 12 |  |  |  |  |
| Last Respects |  | 10 → 12 |  |  |  |  |
| Shed Tail |  | 10 → 12 |  |  |  |  |
| Jet Punch |  | 15 → 16 |  |  |  |  |
| Gigaton Hammer |  | 5 → 8 |  |  |  |  |
| Raging Bull |  | 10 → 12 |  |  |  |  |
| Twin Beam |  | 10 → 12 |  |  |  |  |
| Kowtow Cleave |  | 10 → 12 |  |  |  |  |
| Double Shock |  | 5 → 8 |  |  |  |  |
| Pounce |  | 10 → 20 |  |  |  |  |
| Make It Rain |  | 5 → 8 |  |  |  |  |
| Population Bomb |  | 10 → 12 |  |  |  |  |
| Lunar Blessing |  | 5 → 10 |  |  |  |  |
| Take Heart |  | 5 → 15 |  |  |  | Fairy → Psychic |
| Silk Trap |  | 5 → 10 |  |  |  |  |
| Axe Kick |  | 10 → 12 |  |  |  |  |
| Lumina Crash |  | 10 → 12 |  |  |  |  |
| Ice Spinner |  | 15 → 16 |  |  |  |  |
| Salt Cure |  | 15 → 16 |  |  |  |  |
| Triple Dive |  |  | 90 → 95 |  |  |  |
| Mortal Spin |  | 15 → 16 |  |  |  |  |
| Chilly Reception |  | 10 → 12 |  |  |  |  |
| Comeuppance |  | 10 → 12 |  |  |  |  |
| Tidy Up |  | 10 → 12 |  |  |  |  |
| Bleakwind Storm |  |  |  | 20 → 30 |  |  |
| Wildbolt Storm |  |  |  | 20 → 30 |  |  |
| Sandsear Storm |  |  |  | 20 → 30 |  |  |
| Matcha Gotcha |  | 5 → 16 |  |  |  |  |
| Electro Shot |  | 10 → 12 |  |  |  |  |
| Psychic Noise |  | 10 → 12 |  |  |  |  |
| Upper Hand |  | 10 → 16 |  |  |  |  |

## 2. Critical hits and move properties

**High critical-hit ratio (+2 stages):** 25 moves: Karate Chop, Razor Wind, Razor Leaf, Sky Attack, Crabhammer, Slash, Aeroblast, Cross Chop, Blaze Kick, Air Cutter, Poison Tail, Leaf Blade, Cross Poison, Night Slash, Psycho Cut, Shadow Claw, Drill Run, Stone Edge, Spacial Rend, Attack Order, Snipe Shot, Triple Arrows, Esper Wing, Aqua Cutter, Ivy Cudgel.

**Properties:**

- **Magic Coat / Magic Bounce no longer reflect it** (16): Defog, Disable, Embargo, Encore, Foresight, Heal Block, Miracle Eye, Odor Sleuth, Roar, Spikes, Spite, Stealth Rock, Taunt, Torment, Toxic Spikes, Whirlwind
- **Mirror Move / Copycat can no longer copy it** (4): Coaching, Feint, Taunt, Teeter Dance
- **Protect / Detect no longer block it** (2): Hyper Drill, Spider Web
- **Snatch no longer steals it** (12): Aqua Ring, Healing Wish, Imprison, Jungle Healing, Lucky Chant, Lunar Dance, Magnet Rise, Power Trick, Recycle, Revival Blessing, Tidy Up, Wish
- **now hits all adjacent foes (doubles)** (1): Surf

## 3. Behaviour changes (moves and abilities)

**committed behaviour_cards.json at HEAD**

| Card | Kind | What it does |
|---|---|---|
| Double-Edge (Gen I) | move | Recoil. Gen I-II: 1/4 of damage dealt (Gen I: none when it breaks a Substitute). Gen III onward: 1/3. Lowest recoil is Gen I-II. (Power 100 in Gen I-III, 120 after, is a separate row.) |
| Astonish (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Substitute (Gen II-V) | move | Gen I: a Substitute blocks sleep, paralysis and Leech Seed less reliably, and a 255+ damage hit always breaks it. Gen II-V: blocks all status and stat drops from others. Gen VI onward: sound moves and Infiltrator go through it, a drawback for the user. |
| Protect / Detect / Endure (Gen IV) | move | Chance when used repeatedly. Gen II: halves each time. Gen III: halves for three uses, then erratic. Gen IV-V: halves each time, floor 1/8. Gen VI onward: drops to 1/3 each time. Gen II and IV-V keep the best odds. Chance when used repeatedly. Gen II: halves each time. Gen III: halves for three uses, then erratic. Gen IV-V: halves each time, floor 1/8. Gen VI onward: drops to 1/3 each time. Gen IV-V keeps the best odds. |
| Aerilate / Pixilate / Refrigerate (Gen VI) | ability | Normal moves become Flying with 1.3x power in Gen VI, 1.2x from Gen VII. Normal moves become Fairy with 1.3x power in Gen VI, 1.2x from Gen VII. Normal moves become Ice with 1.3x power in Gen VI, 1.2x from Gen VII. |
| Parental Bond (Gen VI) | ability | Second hit does 50% damage in Gen VI, 25% from Gen VII. |
| High Jump Kick / Jump Kick (Gen I) | move | Crash damage on a miss. Gen I: 1 HP. Gen II: 1/8 of the damage it would have done. Gen III-IV: half the damage it would have done. Gen V onward: half the user's max HP. Smallest crash is Gen I. |
| Gale Wings (Gen VI) | ability | Gen VI: Flying moves always get +1 priority. Gen VII onward: only at full HP. Gen VI is far stronger. |
| Heal Bell / Soundproof (Gen V) | mixed | Soundproof Pokemon are not cured in Gen III-IV and VI-VII; cured in Gen V. Gen VIII onward: Soundproof party members are skipped but the user is always cured. Gen II and V cure everyone. Whether the holder is cured by an ally's Heal Bell: no in Gen III-IV and VI-VII, yes in Gen V, and Gen VIII onward cured only if it used the move itself. Gen V helps the holder most. |
| Leaf Guard (Gen IV) | ability | Gen IV: in sun blocks status, but the holder can still use Rest. Gen V onward: Rest fails in sun. Gen IV is better for the holder. |
| Parting Shot (Gen VI) | move | Gen VII onward: the user doesn't switch out if neither stat could be lowered. Gen VI always switches. |
| Destiny Bond (Gen III-VI) | move | Gen VII onward: fails if used twice in a row. Earlier: can be used every turn. |
| Disguise (Gen VII) | ability | Gen VIII onward: breaking the disguise also costs Mimikyu 1/8 HP. Gen VII doesn't. |

**Not done yet in this engine:** Brick Break (hook), Disable / Encore / Taunt, Moody, Swallow, Explosion, Anger Point, Magic Guard, trapping abilities, Rapid Spin +1 Speed, Teleport, Healing Wish / Lunar Dance, Howl, Illuminate, Thrash, Moonlight / Morning Sun / Synthesis, Flail / Reversal, Psywave, Sticky Hold, Intrepid Sword / Dauntless Shield (binary arm). (CFRU.md bottom)

## 4. Planned (NOT in any release)

Everything below is the Pokémon Legacy balance pass (`game_plans/legacy_balance_2026-11-26/`): decisions are closed and the manifests are built, but it is not applied in this repo; nothing here ships until the apply step runs.

### Planned: Pokémon Legacy move values (146 moves)

`from` is the value in the release plus the best-version tier above; Legacy values below the hack's are not applied.

| Move | Power | PP | Accuracy | Effect % | Priority | Type |
|---|---|---|---|---|---|---|
| Double Slap | 15 → 20 | 10 → 35 |  |  |  | Normal → Fairy |
| Comet Punch |  | 15 → 25 | 85 → 100 |  |  |  |
| Mega Punch | 80 → 90 |  | 85 → 95 |  |  |  |
| Pay Day | 40 → 60 |  |  |  |  |  |
| Razor Wind |  | 10 → 15 |  |  |  | Normal → Flying |
| Cut |  |  |  |  |  | Normal → Bug |
| Bind | 15 → 35 |  | 85 → 100 |  |  |  |
| Slam |  | 20 → 25 |  |  |  |  |
| Mega Kick |  | 8 → 10 | 75 → 85 |  |  |  |
| Rolling Kick | 60 → 70 | 15 → 25 | 85 → 100 |  |  |  |
| Fury Attack |  | 20 → 35 |  |  |  |  |
| Wrap | 15 → 30 |  | 90 → 100 |  |  |  |
| Take Down | 90 → 95 |  |  |  |  |  |
| Poison Sting | 30 → 35 |  |  |  |  |  |
| Twineedle | 25 → 40 |  |  |  |  |  |
| Pin Missile |  | 20 → 30 |  |  |  |  |
| Supersonic |  |  | 55 → 70 |  |  |  |
| Sonic Boom |  |  | 90 → 100 |  |  |  |
| Acid | 40 → 65 |  |  |  |  |  |
| Hydro Pump |  | 8 → 10 |  |  |  |  |
| Ice Beam |  | 12 → 15 |  |  |  |  |
| Submission | 80 → 90 |  |  |  |  |  |
| Mega Drain |  | 15 → 25 |  |  |  |  |
| Poison Powder |  |  | 80 → 90 |  |  |  |
| Dragon Rage |  | 10 → 20 |  |  |  |  |
| Fire Spin |  |  | 85 → 100 |  |  |  |
| Thunder |  |  | 75 → 85 |  |  |  |
| Rock Throw |  | 15 → 25 |  |  |  |  |
| Dig |  | 12 → 20 |  |  |  |  |
| Psychic |  | 12 → 15 |  |  |  |  |
| Rage | 20 → 60 |  |  |  |  |  |
| Egg Bomb | 100 → 110 | 10 → 15 | 75 → 100 |  |  | Normal → Grass |
| Lick | 30 → 40 |  |  |  |  |  |
| Smog | 30 → 40 |  | 70 → 100 |  |  |  |
| Sludge | 65 → 90 |  |  |  |  |  |
| Bone Club |  | 20 → 25 | 85 → 100 |  |  |  |
| Clamp | 35 → 50 | 15 → 20 | 85 → 100 |  |  |  |
| Spike Cannon | 20 → 30 |  |  |  |  | Normal → Steel |
| Constrict | 10 → 40 |  |  |  |  |  |
| Kinesis |  |  | 80 → 100 |  |  |  |
| Barrage | 15 → 20 |  | 85 → 100 |  |  |  |
| Leech Life |  | 15 → 25 |  |  |  |  |
| Sky Attack |  | 8 → 10 |  |  |  |  |
| Transform |  |  |  |  | 0 → 1 |  |
| Dizzy Punch |  | 10 → 20 |  |  |  |  |
| Crabhammer | 100 → 110 |  | 95 → 100 |  |  |  |
| Fury Swipes | 18 → 20 | 15 → 20 |  |  |  |  |
| Bonemerang |  | 10 → 20 |  |  |  |  |
| Rock Slide | 75 → 80 | 12 → 15 |  |  |  |  |
| Tri Attack |  | 12 → 15 |  |  |  |  |
| Triple Kick | 20 → 30 | 10 → 15 | 90 → 100 |  |  |  |
| Flame Wheel | 60 → 65 |  |  |  |  |  |
| Snore | 50 → 60 | 16 → 20 |  |  |  |  |
| Aeroblast |  | 5 → 10 |  |  |  |  |
| Mach Punch | 40 → 50 |  |  |  |  |  |
| Feint Attack | 60 → 70 |  |  |  |  |  |
| Sludge Bomb | 90 → 95 | 12 → 15 |  |  |  |  |
| Zap Cannon |  | 8 → 10 | 50 → 70 |  |  |  |
| Icy Wind | 60 → 65 |  |  |  |  |  |
| Bone Rush |  | 12 → 20 |  |  |  |  |
| Giga Drain |  | 12 → 15 |  |  |  |  |
| Steel Wing | 70 → 75 |  |  |  |  |  |
| Present |  | 15 → 25 | 90 → 100 |  |  |  |
| Sacred Fire |  | 5 → 10 |  |  |  |  |
| Dynamic Punch |  | 8 → 10 | 50 → 70 |  |  |  |
| Dragon Breath | 60 → 70 |  |  |  |  |  |
| Iron Tail |  |  | 75 → 90 |  |  |  |
| Metal Claw | 50 → 70 |  |  | 10 → 20 |  |  |
| Vital Throw |  | 10 → 20 |  |  |  |  |
| Cross Chop |  | 8 → 10 | 80 → 90 |  |  |  |
| Twister | 40 → 70 |  |  |  |  |  |
| Rain Dance |  | 8 → 10 |  |  |  |  |
| Sunny Day |  | 8 → 10 |  |  |  |  |
| Extreme Speed |  | 8 → 15 |  |  |  |  |
| Whirlpool |  |  | 85 → 100 |  |  |  |
| Uproar |  | 12 → 25 |  |  |  |  |
| Heat Wave |  |  | 90 → 100 |  |  |  |
| Smelling Salts | 70 → 75 | 10 → 15 |  |  |  |  |
| Dive | 80 → 90 | 12 → 15 |  |  |  |  |
| Luster Purge |  | 10 → 15 |  |  |  |  |
| Mist Ball |  | 10 → 15 |  |  |  |  |
| Blaze Kick |  | 12 → 15 |  | 10 → 20 |  |  |
| Needle Arm |  | 15 → 20 |  |  |  |  |
| Hyper Voice | 90 → 100 |  |  |  |  |  |
| Crush Claw | 75 → 80 | 12 → 15 |  |  |  |  |
| Meteor Mash |  |  | 90 → 95 |  |  |  |
| Astonish | 30 → 50 |  |  |  |  |  |
| Weather Ball |  | 12 → 30 |  |  |  |  |
| Air Cutter | 60 → 65 |  |  |  |  |  |
| Rock Tomb |  | 16 → 25 |  |  |  |  |
| Grass Whistle |  |  | 55 → 75 |  |  |  |
| Signal Beam | 75 → 85 |  |  |  |  |  |
| Sky Uppercut | 85 → 90 |  |  |  |  |  |
| Sand Tomb |  |  | 85 → 100 |  |  |  |
| Muddy Water |  | 12 → 15 | 85 → 95 | 40 → 50 |  |  |
| Dragon Claw | 80 → 90 |  |  |  |  |  |
| Bounce |  | 8 → 15 | 85 → 90 |  |  |  |
| Mud Shot |  | 16 → 20 |  |  |  |  |
| Poison Tail | 60 → 80 |  |  |  |  |  |
| Covet |  |  |  |  |  | Normal → Fairy |
| Rock Blast |  | 12 → 15 |  |  |  |  |
| Doom Desire | 140 → 150 |  |  |  |  |  |
| Aqua Tail |  | 12 → 15 |  |  |  |  |
| Cross Poison | 70 → 80 |  |  |  |  |  |
| Dragon Pulse |  | 12 → 15 |  |  |  |  |
| Energy Ball |  | 12 → 15 |  |  |  |  |
| Focus Blast |  | 8 → 10 |  |  |  |  |
| Gunk Shot |  | 8 → 10 | 80 → 85 |  |  |  |
| Mud Bomb | 65 → 70 |  |  |  |  |  |
| Night Slash | 70 → 75 |  |  |  |  |  |
| Psycho Cut | 70 → 75 |  |  |  |  |  |
| Rock Climb | 90 → 100 |  | 85 → 90 |  |  |  |
| X-Scissor | 80 → 85 |  |  |  |  |  |
| Zen Headbutt | 80 → 85 |  |  |  |  |  |
| Drill Run |  | 12 → 15 |  |  |  |  |
| Frost Breath |  | 12 → 15 |  |  |  |  |
| Heart Stamp |  |  |  | 30 → 40 |  |  |
| Horn Leech |  | 12 → 15 |  |  |  |  |
| Steamroller | 65 → 80 |  |  |  |  |  |
| Storm Throw |  | 12 → 15 |  |  |  |  |
| Stone Edge |  | 8 → 10 |  |  |  |  |
| Payback | 50 → 60 |  |  |  |  |  |
| Inferno |  |  | 50 → 60 |  |  |  |
| Double Hit |  | 12 → 20 |  |  |  |  |
| Mirror Shot | 65 → 70 | 10 → 15 |  |  |  |  |
| Flash Cannon | 80 → 90 | 12 → 15 |  |  |  |  |
| Razor Shell | 75 → 80 | 12 → 15 |  |  |  |  |
| Play Rough |  | 12 → 15 |  |  |  |  |
| Dazzling Gleam |  | 12 → 15 |  |  |  |  |
| Dragon Rush |  |  | 75 → 80 |  |  |  |
| Phantom Force |  | 12 → 15 |  |  |  |  |
| Retaliate |  | 5 → 10 |  |  |  |  |
| Psyshock |  | 12 → 15 |  |  |  |  |
| Round | 60 → 65 | 16 → 20 |  |  |  |  |
| Tail Slap |  | 12 → 15 |  |  |  |  |
| Smack Down |  | 16 → 20 |  |  |  |  |
| Gyro Ball |  | 8 → 10 |  |  |  |  |
| Night Daze |  | 12 → 15 |  |  |  |  |
| Head Charge | 120 → 130 |  |  |  |  |  |
| Relic Song | 75 → 85 |  |  |  |  |  |
| Fusion Flare |  | 5 → 10 |  |  |  |  |
| Fusion Bolt |  | 5 → 10 |  |  |  |  |
| Mystical Fire | 75 → 80 | 12 → 15 |  |  |  |  |
| Infestation | 20 → 30 |  |  |  |  |  |
| Flying Press |  | 12 → 15 |  |  |  |  |
| Sky Drop | 60 → 70 |  |  |  |  |  |

**Planned move effects (18; candidates, the apply step checks each hack's current effect first):**

- Vise Grip: stat:Attack-1 20% (emerald L.)
- Razor Wind: one turn + 100% trapping (bind-style), keep power/crit/targeting (user note)
- Razor Wind: status:Capture 100% (xy L.)
- Razor Wind: one-turn (emerald L.)
- Razor Wind: status:Trapped 100% (emerald L.)
- Razor Wind: one-turn (yellow L.)
- Slam: flinch 10% (yellow L.)
- Egg Bomb: category Special (Grass, X&Y L.) where the engine has the split
- Skull Bash: one-turn (yellow L.)
- Sky Attack: one turn (no charge), no retype, keep 200/90 and current flinch/crit (user note)
- Sky Attack: one-turn (emerald L.)
- Sky Attack: one-turn (crystal L.)
- Sky Attack: one-turn (yellow L.)
- Dizzy Punch: status:Confusion 10% (yellow L.)
- Rock Slide: flinch 10% (yellow L.)
- Crunch: defence drop matches Dark's category in this game (user note)
- Hyper Voice: status:Confusion 30% (emerald L.)
- Power Gem: stat:Special Defense-1 20% (xy L.)

**Skipped (1):** Night Shade (power 1 is a placeholder (fixed/variable damage); Legacy yellow power 60 not applied)

### Planned: base stat changes (241 species)

Species Legacy changed get Legacy's per-stat delta on the hack's own line; a hack-customised line keeps the higher of each stat (user ruling 2026-11-26).

<details><summary>Show the stat table</summary>

| Species | Changes |
|---|---|
| Butterfree | HP 60 → 70, Def 50 → 60, SpD 80 → 90 |
| Beedrill | Atk 90 → 100, Spe 75 → 85 |
| Pidgeotto | SpA 50 → 55, SpD 50 → 55 |
| Pidgeot | SpA 70 → 80, SpD 70 → 80 |
| Raticate | Spe 97 → 102 |
| Ekans | HP 35 → 40, Atk 60 → 65, Spe 55 → 60 |
| Arbok | Spe 80 → 90 |
| Sandslash | Spe 65 → 75, SpA 25 → 45 |
| Vulpix | HP 38 → 48, Def 40 → 45, Spe 65 → 75, SpA 50 → 61, SpD 65 → 70 |
| Ninetales | HP 73 → 78, Atk 76 → 71, Def 75 → 80, SpA 81 → 91 |
| Jigglypuff | Def 20 → 30, SpA 45 → 55, SpD 25 → 30 |
| Wigglytuff | Def 45 → 60, SpA 85 → 90, SpD 50 → 60 |
| Oddish | HP 45 → 50 |
| Gloom | HP 60 → 70, Def 70 → 75 |
| Vileplume | HP 75 → 90, Def 85 → 95 |
| Paras | HP 35 → 55, Def 55 → 60, SpD 55 → 60 |
| Parasect | HP 80 → 85, SpD 80 → 90 |
| Venomoth | Atk 65 → 75, Spe 90 → 100 |
| Diglett | Atk 55 → 70 |
| Dugtrio | Atk 100 → 120 |
| Meowth | Atk 45 → 55 |
| Persian | Atk 80 → 85, Spe 115 → 120, SpA 60 → 65 |
| Mankey | HP 40 → 45, Spe 70 → 75 |
| Primeape | HP 65 → 70, Spe 95 → 100 |
| Poliwrath | Atk 95 → 105, SpA 70 → 60 |
| Victreebel | Atk 105 → 120, Spe 70 → 75, SpA 100 → 115 |
| Golem | SpD 65 → 75 |
| Ponyta | Spe 90 → 100 |
| Farfetch’d | Spe 65 → 70 |
| Dodrio | Spe 110 → 120 |
| Seel | Atk 45 → 55 |
| Dewgong | Atk 50 → 80 |
| Grimer | HP 80 → 90, SpD 50 → 75 |
| Muk | HP 105 → 115 |
| Onix | Def 150 → 160, Spe 65 → 70 |
| Drowzee | HP 60 → 70, Spe 42 → 34 |
| Hypno | HP 85 → 100, Spe 67 → 59 |
| Kingler | Atk 130 → 140 |
| Exeggutor | Atk 95 → 85, SpD 75 → 95 |
| Marowak | SpA 30 → 50 |
| Hitmonlee | Atk 120 → 125, Spe 87 → 97 |
| Hitmonchan | Def 79 → 84 |
| Lickitung | Atk 55 → 65, Def 75 → 80, SpD 75 → 80 |
| Weezing | HP 65 → 75 |
| Rhyhorn | HP 80 → 90, SpD 30 → 40 |
| Seaking | Atk 92 → 102, Spe 68 → 78 |
| Jynx | SpD 95 → 100 |
| Flareon | HP 65 → 95, SpD 100 → 110 |
| Omanyte | Atk 40 → 30, SpD 55 → 65 |
| Omastar | Atk 60 → 50, SpD 70 → 80 |
| Articuno | Atk 70 → 75, SpA 95 → 105 |
| Furret | Def 64 → 74 |
| Noctowl | HP 110 → 120, SpA 86 → 96 |
| Ledian | HP 55 → 75, Spe 85 → 95, SpA 35 → 60, SpD 100 → 110 |
| Ariados | HP 70 → 75, Atk 95 → 100, SpA 60 → 70 |
| Chinchou | SpA 56 → 66 |
| Lanturn | SpA 76 → 86 |
| Igglybuff | Def 15 → 20 |
| Togetic | HP 55 → 65 |
| Natu | Spe 70 → 75 |
| Bellossom | HP 75 → 90, SpD 100 → 110 |
| Sudowoodo | SpD 65 → 85 |
| Politoed | SpA 90 → 100 |
| Aipom | Atk 70 → 75 |
| Wooper | SpA 25 → 35, SpD 25 → 35 |
| Quagsire | SpA 65 → 75, SpD 65 → 75 |
| Murkrow | Atk 85 → 90, Spe 91 → 96 |
| Girafarig | SpA 90 → 100 |
| Dunsparce | HP 100 → 110, SpA 65 → 70 |
| Granbull | Atk 120 → 130 |
| Qwilfish | SpA 55 → 65, SpD 55 → 75 |
| Ursaring | Atk 130 → 140, Def 75 → 80, SpA 75 → 55, SpD 75 → 80 |
| Slugma | HP 40 → 50, Atk 40 → 70, Def 40 → 60, SpD 40 → 60 |
| Magcargo | HP 60 → 70, Atk 50 → 80, Def 120 → 130, SpA 90 → 100, SpD 80 → 90 |
| Corsola | Atk 55 → 65, SpA 65 → 75 |
| Remoraid | HP 35 → 45, Atk 65 → 60, SpA 65 → 70 |
| Octillery | HP 75 → 85, SpA 105 → 115 |
| Delibird | HP 45 → 60, Def 45 → 55, SpA 65 → 85, SpD 45 → 55 |
| Stantler | Atk 95 → 105 |
| Hitmontop | Def 95 → 100, Spe 70 → 80 |
| Smoochum | Spe 65 → 70, SpD 65 → 70 |
| Treecko | Atk 45 → 50, SpD 55 → 50 |
| Grovyle | Atk 65 → 70, SpD 65 → 60 |
| Sceptile | SpA 85 → 110 |
| Blaziken | Spe 80 → 85 |
| Mightyena | HP 70 → 75, Def 70 → 75, Spe 70 → 80 |
| Beautifly | Atk 60 → 80 |
| Dustox | Atk 40 → 50, Def 70 → 80, SpD 90 → 100 |
| Ludicolo | HP 80 → 90 |
| Shiftry | Spe 80 → 85 |
| Swellow | SpA 75 → 100 |
| Pelipper | HP 60 → 70, SpA 95 → 105 |
| Kirlia | HP 38 → 43, Atk 35 → 40, Def 35 → 40, SpA 65 → 75, SpD 55 → 65 |
| Shedinja | SpA 30 → 75 |
| Loudred | SpA 71 → 76 |
| Exploud | HP 104 → 114, Atk 81 → 91, Def 63 → 73, SpA 91 → 101 |
| Makuhita | HP 72 → 82, Def 30 → 40, SpD 30 → 40 |
| Nosepass | HP 30 → 45, Atk 45 → 40, Def 135 → 125, SpA 45 → 70, SpD 90 → 105 |
| Skitty | Spe 50 → 60, SpA 35 → 50, SpD 35 → 40 |
| Delcatty | HP 70 → 75, Atk 65 → 70, Def 65 → 75, Spe 90 → 95, SpA 65 → 80, SpD 55 → 70 |
| Sableye | HP 50 → 70, Def 75 → 95, Spe 50 → 40, SpD 65 → 95 |
| Mawile | Atk 85 → 95, Def 85 → 95, SpD 55 → 65 |
| Plusle | Atk 50 → 70, SpA 85 → 95 |
| Minun | HP 60 → 70, Def 75 → 80, SpA 50 → 65, SpD 40 → 95 |
| Volbeat | Atk 47 → 78, SpA 90 → 97 |
| Illumise | SpA 47 → 73, SpD 85 → 90 |
| Gulpin | HP 70 → 85 |
| Swalot | HP 100 → 115, Atk 53 → 73 |
| Carvanha | Spe 65 → 75 |
| Sharpedo | Spe 95 → 115 |
| Wailmer | Spe 60 → 55, SpA 70 → 85 |
| Wailord | HP 150 → 170, Atk 50 → 90, SpA 105 → 115 |
| Numel | HP 60 → 70 |
| Camerupt | Atk 100 → 105, SpA 105 → 110 |
| Torkoal | Atk 75 → 85 |
| Spoink | Def 35 → 40, Spe 60 → 65 |
| Grumpig | Def 65 → 70, Spe 80 → 85 |
| Vibrava | HP 50 → 60, Atk 70 → 80, Def 50 → 60, Spe 70 → 80, SpA 50 → 70, SpD 50 → 60 |
| Cacnea | HP 50 → 60, Atk 85 → 70, Def 40 → 55, Spe 35 → 25, SpD 40 → 45 |
| Cacturne | HP 70 → 100, Def 60 → 90, SpD 60 → 80 |
| Swablu | HP 45 → 60 |
| Altaria | HP 85 → 95 |
| Zangoose | HP 73 → 78, Atk 115 → 120 |
| Seviper | HP 83 → 93 |
| Barboach | SpA 46 → 56 |
| Whiscash | SpA 76 → 91 |
| Corphish | HP 43 → 53, SpA 50 → 60 |
| Crawdaunt | HP 63 → 73, SpA 90 → 100 |
| Armaldo | SpA 45 → 60, SpD 80 → 90 |
| Castform | Spe 85 → 95, SpA 85 → 90 |
| Kecleon | SpA 60 → 70 |
| Banette | HP 64 → 74, SpA 83 → 93 |
| Tropius | HP 99 → 120 |
| Chimecho | SpA 95 → 100 |
| Absol | Spe 75 → 95 |
| Snorunt | HP 50 → 60, Atk 50 → 60, Def 50 → 60, Spe 50 → 60, SpA 50 → 60, SpD 50 → 60 |
| Glalie | HP 80 → 85, Atk 80 → 85, Def 80 → 85, Spe 80 → 85, SpA 80 → 85, SpD 80 → 85 |
| Huntail | Atk 104 → 114, SpA 94 → 84 |
| Relicanth | Atk 105 → 110, Def 115 → 130 |
| Luvdisc | HP 43 → 58, Def 55 → 75, Spe 97 → 102, SpD 65 → 85 |
| Torterra | HP 95 → 100, Atk 109 → 114, SpA 75 → 65 |
| Bibarel | HP 79 → 89, Spe 50 → 71, SpA 55 → 65 |
| Kricketune | SpA 55 → 95 |
| Shinx | HP 45 → 50, Atk 65 → 70, SpA 40 → 30 |
| Luxio | HP 60 → 70, Atk 85 → 90, SpA 60 → 45 |
| Luxray | HP 80 → 90, Atk 120 → 130, SpA 95 → 75 |
| Rampardos | HP 97 → 107, Spe 58 → 63, SpA 65 → 60 |
| Bastiodon | HP 60 → 80, Spe 30 → 20 |
| Vespiquen | Def 102 → 112, SpD 102 → 112 |
| Pachirisu | Spe 95 → 110 |
| Cherubi | Atk 35 → 55 |
| Ambipom | Atk 100 → 105 |
| Drifloon | Atk 50 → 40, SpA 60 → 70 |
| Drifblim | Atk 80 → 60, SpA 90 → 110 |
| Lopunny | Atk 76 → 81, Spe 105 → 130, SpA 54 → 44 |
| Mismagius | Spe 105 → 110, SpA 105 → 110, SpD 105 → 110 |
| Glameow | HP 49 → 59, SpA 42 → 32 |
| Purugly | HP 100 → 103 |
| Chingling | SpA 65 → 70 |
| Bonsly | SpD 45 → 55 |
| Chatot | Def 45 → 60, SpA 92 → 102, SpD 42 → 57 |
| Spiritomb | Atk 92 → 108, Spe 35 → 23, SpA 92 → 108 |
| Croagunk | HP 48 → 58, Atk 61 → 76, Spe 50 → 60, SpA 61 → 66 |
| Toxicroak | Atk 106 → 112, Spe 85 → 90, SpA 86 → 80 |
| Carnivine | HP 89 → 95, Atk 100 → 110, SpA 55 → 75 |
| Lumineon | Spe 101 → 106, SpD 69 → 86 |
| Mantyke | HP 45 → 55 |
| Snover | HP 60 → 70, Spe 40 → 30, SpA 62 → 72 |
| Abomasnow | HP 90 → 110, Spe 60 → 50, SpA 92 → 112, SpD 85 → 75 |
| Lickilicky | Spe 30 → 45 |
| Probopass | HP 65 → 70, SpA 80 → 105 |
| Dusknoir | HP 45 → 65, Atk 100 → 110, Def 135 → 130, Spe 45 → 25, SpD 135 → 130 |
| Froslass | HP 70 → 75, Def 70 → 75, Spe 110 → 115, SpD 70 → 75 |
| Rotom | Def 77 → 87, Spe 91 → 101, SpA 95 → 105, SpD 77 → 87 |
| Phione | HP 80 → 85, Atk 80 → 85, Def 80 → 85, Spe 80 → 85, SpA 80 → 85, SpD 80 → 85 |
| Emboar | Def 65 → 70, SpA 100 → 90, SpD 65 → 70 |
| Dewott | Atk 75 → 86, SpA 83 → 72 |
| Samurott | Atk 108 → 116 |
| Watchog | HP 85 → 87, Def 69 → 74, SpD 69 → 74 |
| Pidove | Atk 55 → 41, SpA 36 → 55 |
| Tranquill | Atk 77 → 55, SpA 50 → 77 |
| Unfezant | SpA 65 → 115 |
| Blitzle | Spe 76 → 81 |
| Zebstrika | Spe 116 → 121 |
| Swoobat | Atk 57 → 67, Spe 114 → 119, SpA 77 → 82, SpD 55 → 65 |
| Audino | Atk 60 → 50, Def 86 → 91, SpA 60 → 70, SpD 86 → 91 |
| Leavanny | Atk 103 → 108, Spe 92 → 102, SpA 70 → 55 |
| Lilligant | HP 70 → 80, SpA 110 → 115 |
| Maractus | HP 75 → 85, Atk 106 → 110, Def 67 → 72, Spe 60 → 76, SpD 67 → 72 |
| Crustle | SpD 75 → 85 |
| Yamask | Def 85 → 95, SpA 55 → 60 |
| Cofagrigus | Def 145 → 155, SpA 95 → 100 |
| Carracosta | Spe 32 → 52, SpA 83 → 73 |
| Garbodor | Spe 60 → 75 |
| Minccino | Spe 75 → 80 |
| Cinccino | Spe 115 → 120 |
| Swanna | Atk 77 → 87 |
| Vanilluxe | SpA 110 → 135 |
| Frillish | HP 55 → 70, SpA 65 → 75 |
| Jellicent | SpA 75 → 95 |
| Galvantula | Spe 108 → 113 |
| Klink | SpA 45 → 55, SpD 60 → 50 |
| Klang | SpA 70 → 80, SpD 85 → 75 |
| Klinklang | SpA 70 → 80, SpD 85 → 75 |
| Tynamo | SpA 45 → 55 |
| Eelektrik | SpA 75 → 85 |
| Eelektross | Atk 105 → 115 |
| Elgyem | Atk 55 → 40, SpA 85 → 100 |
| Beheeyem | SpA 125 → 140 |
| Cubchoo | HP 55 → 65, Spe 40 → 50, SpA 60 → 40 |
| Beartic | HP 95 → 100, Spe 50 → 70 |
| Accelgor | Atk 70 → 60, SpA 100 → 110 |
| Golett | HP 59 → 79, Atk 74 → 94, Def 50 → 55, Spe 35 → 40, SpA 35 → 40, SpD 50 → 55 |
| Golurk | HP 100 → 109, Atk 124 → 134 |
| Heatmor | HP 85 → 95, Def 66 → 76, SpD 66 → 76 |
| Virizion | Spe 108 → 129, SpD 129 → 108 |
| Pyroar | Atk 68 → 78, SpA 109 → 119 |
| Skiddo | HP 66 → 76, Atk 65 → 70, Def 48 → 58, SpA 62 → 37 |
| Gogoat | Atk 100 → 105, Def 72 → 87 |
| Pangoro | HP 95 → 110, Spe 58 → 53, SpA 69 → 59 |
| Aromatisse | HP 101 → 106, Atk 62 → 70, SpA 99 → 104 |
| Swirlix | Atk 48 → 59, Spe 49 → 44, SpA 59 → 53 |
| Slurpuff | SpA 75 → 80 |
| Inkay | HP 53 → 58, Atk 54 → 60, Def 53 → 58, Spe 45 → 50, SpD 46 → 51 |
| Malamar | Atk 92 → 100, Def 88 → 93, SpA 68 → 60, SpD 75 → 80 |
| Binacle | Atk 52 → 62, Def 67 → 77, SpD 56 → 61 |
| Barbaracle | Spe 68 → 78, SpA 54 → 44 |
| Skrelp | HP 50 → 55, SpA 60 → 70, SpD 60 → 75 |
| Dragalge | HP 65 → 76 |
| Clauncher | Def 62 → 67, SpA 58 → 73, SpD 63 → 68 |
| Amaura | HP 77 → 87, Atk 59 → 46, Def 50 → 58, Spe 46 → 26, SpA 67 → 77, SpD 63 → 68 |
| Aurorus | Atk 77 → 57, Def 72 → 92, Spe 58 → 33, SpA 99 → 114, SpD 92 → 102 |
| Dedenne | HP 67 → 82 |
| Sliggoo | Spe 60 → 55, SpA 83 → 88 |
| Goodra | Spe 80 → 70, SpA 110 → 120 |
| Phantump | SpD 60 → 80 |
| Trevenant | SpD 82 → 107 |
| Bergmite | Atk 69 → 74, Def 85 → 90, SpA 32 → 22, SpD 35 → 50 |
| Avalugg | SpA 44 → 34, SpD 46 → 76 |
| Noibat | HP 40 → 55, Atk 30 → 35, Def 35 → 50, Spe 55 → 75, SpA 45 → 65, SpD 40 → 50 |
| Noivern | Spe 123 → 128 |

</details>

Not built yet: 92 Mega / form stat rows.

### Planned: species ability changes (182 slots)

<details><summary>Show the ability table</summary>

| Species | Slot | Old → new |
|---|---|---|
| Caterpie | 2 | (none) → Run Away |
| Butterfree | 2 | (none) → Tinted Lens |
| Butterfree | 3 | Tinted Lens → Overcoat |
| Weedle | 2 | (none) → Run Away |
| Beedrill | 2 | (none) → Sniper |
| Beedrill | 3 | Sniper → Technician |
| Spearow | 3 | Sniper → Anger Point |
| Fearow | 3 | Sniper → Anger Point |
| Sandshrew | 1 | Sand Veil → Sand Rush |
| Sandshrew | 2 | (none) → Tough Claws |
| Sandshrew | 3 | Sand Rush → Sand Veil |
| Sandslash | 1 | Sand Veil → Sand Rush |
| Sandslash | 2 | (none) → Tough Claws |
| Sandslash | 3 | Sand Rush → Sand Veil |
| Vulpix | 2 | (none) → Drought |
| Vulpix | 3 | Drought → Solar Power |
| Ninetales | 2 | (none) → Drought |
| Ninetales | 3 | Drought → Solar Power |
| Jigglypuff | 2 | Competitive → Friend Guard |
| Jigglypuff | 3 | Friend Guard → Competitive |
| Wigglytuff | 2 | Competitive → Magic Bounce |
| Wigglytuff | 3 | Frisk → Competitive |
| Poliwrath | 2 | Damp → Iron Fist |
| Ponyta | 3 | Flame Body → Reckless |
| Seel | 2 | Hydration → Swift Swim |
| Seel | 3 | Ice Body → Simple |
| Dewgong | 3 | Ice Body → Simple |
| Krabby | 3 | Sheer Force → Tough Claws |
| Kingler | 3 | Sheer Force → Tough Claws |
| Lickitung | 2 | Oblivious → Sticky Hold |
| Goldeen | 2 | Water Veil → Lightning Rod |
| Seaking | 2 | Water Veil → Lightning Rod |
| Vaporeon | 2 | Water Absorb → Hydration |
| Vaporeon | 3 | Hydration → Storm Drain |
| Jolteon | 2 | Volt Absorb → Motor Drive |
| Flareon | 2 | Flash Fire → Guts |
| Kabuto | 3 | Swift Swim → Sand Rush |
| Kabutops | 3 | Swift Swim → Sand Rush |
| Chikorita | 3 | Leaf Guard → Sweet Veil |
| Bayleef | 3 | Leaf Guard → Sweet Veil |
| Cyndaquil | 3 | Flash Fire → Unnerve |
| Quilava | 3 | Flash Fire → Unnerve |
| Ledian | 1 | Swarm → Simple |
| Ariados | 1 | Swarm → Poison Touch |
| Igglybuff | 2 | Competitive → Friend Guard |
| Igglybuff | 3 | Friend Guard → Competitive |
| Politoed | 2 | Damp → Drizzle |
| Politoed | 3 | Drizzle → Swift Swim |
| Umbreon | 2 | Synchronize → Pressure |
| Girafarig | 2 | Early Bird → Scrappy |
| Pineco | 2 | (none) → Aftermath |
| Forretress | 2 | (none) → Aftermath |
| Qwilfish | 2 | Swift Swim → Intimidate |
| Qwilfish | 3 | Intimidate → Swift Swim |
| Ursaring | 3 | Unnerve → Defiant |
| Corsola | 3 | Regenerator → Natural Cure |
| Remoraid | 2 | Sniper → Analytic |
| Octillery | 2 | Sniper → Analytic |
| Phanpy | 2 | (none) → Oblivious |
| Donphan | 2 | (none) → Battle Armor |
| Raikou | 1 | Pressure → Volt Absorb |
| Raikou | 2 | (none) → Volt Absorb |
| Entei | 1 | Pressure → Flash Fire |
| Entei | 2 | (none) → Flash Fire |
| Suicune | 1 | Pressure → Water Absorb |
| Suicune | 2 | (none) → Water Absorb |
| Lugia | 1 | Pressure → Multiscale |
| Lugia | 2 | (none) → Multiscale |
| Lugia | 3 | Multiscale → Pressure |
| Ho-Oh | 1 | Pressure → Regenerator |
| Sceptile | 3 | Unburden → Harvest |
| Beautifly | 3 | Rivalry → Defiant |
| Wailmer | 2 | Oblivious → Rain Dish |
| Camerupt | 1 | Magma Armor → Flame Body |
| Camerupt | 3 | Anger Point → Sheer Force |
| Swablu | 2 | (none) → Cloud Nine |
| Swablu | 3 | Cloud Nine → Regenerator |
| Altaria | 2 | (none) → Cloud Nine |
| Altaria | 3 | Cloud Nine → Regenerator |
| Zangoose | 3 | Toxic Boost → Hyper Cutter |
| Seviper | 2 | Shed Skin → Hustle |
| Lileep | 2 | (none) → Rain Dish |
| Cradily | 2 | (none) → Rain Dish |
| Shuppet | 2 | Frisk → Prankster |
| Banette | 2 | Frisk → Prankster |
| Glalie | 1 | Inner Focus → Intimidate |
| Luvdisc | 2 | (none) → Cute Charm |
| Shieldon | 2 | (none) → Bulletproof |
| Drifloon | 2 | Unburden → Flare Boost |
| Drifloon | 3 | Flare Boost → Unburden |
| Drifblim | 2 | Unburden → Flare Boost |
| Drifblim | 3 | Flare Boost → Unburden |
| Spiritomb | 2 | (none) → Infiltrator |
| Carnivine | 2 | (none) → Strong Jaw |
| Finneon | 3 | Water Veil → Wonder Skin |
| Lumineon | 3 | Water Veil → Wonder Skin |
| Leafeon | 3 | Chlorophyll → Sniper |
| Gliscor | 2 | Sand Veil → Sand Rush |
| Gallade | 1 | Steadfast → Justified |
| Gallade | 3 | Justified → Steadfast |
| Dusknoir | 1 | Pressure → Cursed Body |
| Dusknoir | 2 | (none) → Cursed Body |
| Phione | 2 | (none) → Serene Grace |
| Purrloin | 2 | Unburden → Prankster |
| Purrloin | 3 | Prankster → Hustle |
| Liepard | 2 | Unburden → Prankster |
| Liepard | 3 | Prankster → Hustle |
| Pansage | 2 | (none) → Overgrow |
| Pansage | 3 | Overgrow → Sap Sipper |
| Simisage | 2 | (none) → Overgrow |
| Pansear | 2 | (none) → Blaze |
| Pansear | 3 | Blaze → Flash Fire |
| Simisear | 2 | (none) → Blaze |
| Panpour | 2 | (none) → Torrent |
| Panpour | 3 | Torrent → Water Absorb |
| Simipour | 2 | (none) → Torrent |
| Musharna | 2 | (none) → Unaware |
| Unfezant | 3 | Rivalry → Competitive |
| Gigalith | 3 | Sand Force → Sand Stream |
| Woobat | 1 | Unaware → Simple |
| Woobat | 3 | Simple → Unaware |
| Swoobat | 1 | Unaware → Simple |
| Swoobat | 3 | Simple → Unaware |
| Seismitoad | 2 | Poison Touch → Poison Heal |
| Throh | 1 | Guts → Scrappy |
| Maractus | 1 | Water Absorb → Storm Drain |
| Maractus | 2 | Chlorophyll → Sand Rush |
| Garbodor | 2 | Weak Armor → Regenerator |
| Ducklett | 3 | Hydration → Oblivious |
| Vanilluxe | 3 | Weak Armor → Snow Warning |
| Alomomola | 2 | Hydration → Regenerator |
| Alomomola | 3 | Regenerator → Hydration |
| Klink | 2 | Minus → Clear Body |
| Klink | 3 | Clear Body → Flare Boost |
| Klang | 2 | Minus → Clear Body |
| Klang | 3 | Clear Body → Flare Boost |
| Druddigon | 3 | Mold Breaker → Solid Rock |
| Heatmor | 2 | Flash Fire → No Guard |
| Kyurem | 1 | Pressure → Unnerve |
| Kyurem | 2 | (none) → Unnerve |
| Talonflame | 2 | (none) → Gale Wings |
| Pyroar | 2 | Unnerve → Competitive |
| Skiddo | 2 | (none) → Grass Pelt |
| Skiddo | 3 | Grass Pelt → Reckless |
| Gogoat | 2 | (none) → Grass Pelt |
| Gogoat | 3 | Grass Pelt → Reckless |
| Swirlix | 2 | (none) → Unburden |
| Swirlix | 3 | Unburden → Gluttony |
| Slurpuff | 2 | (none) → Unburden |
| Slurpuff | 3 | Unburden → Gluttony |
| Malamar | 3 | Infiltrator → Moxie |
| Skrelp | 2 | Poison Touch → Adaptability |
| Skrelp | 3 | Adaptability → Liquid Ooze |
| Dragalge | 2 | Poison Touch → Adaptability |
| Dragalge | 3 | Adaptability → Liquid Ooze |
| Helioptile | 2 | Sand Veil → Solar Power |
| Helioptile | 3 | Solar Power → Sand Veil |
| Heliolisk | 2 | Sand Veil → Solar Power |
| Heliolisk | 3 | Solar Power → Sand Veil |
| Tyrunt | 2 | (none) → Sturdy |
| Tyrunt | 3 | Sturdy → Intimidate |
| Tyrantrum | 2 | (none) → Rock Head |
| Tyrantrum | 3 | Rock Head → Intimidate |
| Amaura | 2 | (none) → Wonder Skin |
| Aurorus | 2 | (none) → Wonder Skin |
| Sylveon | 2 | Cute Charm → Frisk |
| Goomy | 2 | Hydration → Gooey |
| Goomy | 3 | Gooey → Hydration |
| Sliggoo | 2 | Hydration → Gooey |
| Sliggoo | 3 | Gooey → Hydration |
| Goodra | 2 | Hydration → Gooey |
| Goodra | 3 | Gooey → Hydration |
| Phantump | 1 | Natural Cure → Harvest |
| Phantump | 3 | Harvest → Natural Cure |
| Trevenant | 1 | Natural Cure → Harvest |
| Trevenant | 3 | Harvest → Natural Cure |
| Bergmite | 1 | Own Tempo → Sturdy |
| Bergmite | 3 | Sturdy → Filter |
| Avalugg | 3 | Sturdy → Filter |
| Noibat | 3 | Telepathy → Soundproof |
| Noivern | 2 | Infiltrator → Limber |
| Noivern | 3 | Telepathy → Soundproof |

</details>

135 slots where the hack already holds something other than Legacy's old ability keep the hack's (user ruling).

### Planned: learnset changes (4104 moves added, 3752 moves learned earlier)

Moves this engine lacks (skipped): 69 entries across 8 moves.
<details><summary>Show the learnset changes</summary>

| Species | Added | Earlier |
|---|---|---|
| Bulbasaur | Vine Whip L9, Acid L13, Sweet Scent L16, Body Slam L34, Energy Ball L40, Sludge Bomb L43, Solar Beam L56 | Sleep Powder L13→L11, Poison Powder L13→L11, Seed Bomb L37→L30 |
| Ivysaur | Vine Whip L9, Acid L10, Sweet Scent L16, Razor Leaf L20, Seed Bomb L30, Body Slam L34, Energy Ball L40 | Sleep Powder L13→L11, Poison Powder L13→L11, Growth L28→L27 |
| Venusaur | Acid L10, Sweet Scent L16, Razor Leaf L20, Seed Bomb L30, Body Slam L34, Worry Seed L36, Energy Ball L40, Ancientpower L50, Frenzy Plant L55 | Sleep Powder L13→L11, Poison Powder L13→L11, Growth L28→L27, Synthesis L45→L39, Solarbeam L53→L46 |
| Charmander | Leer L13, Rage L13, Fire Punch L19, Flame Wheel L19, Bite L23, Dragon Claw L38, Body Slam L42, Slam L50, Fire Blast L52 | Fire Spin L43→L15, Slash L34→L29 |
| Charmeleon | Leer L13, Rage L13, Fire Punch L19, Flame Wheel L19, Bite L23, Dragon Claw L38, Body Slam L42, Dragon Rage L43, Slam L48, Fire Blast L52 | Fire Spin L50→L15, Slash L37→L29, Flamethrower L43→L31, Inferno L54→L49 |
| Charizard | Tailwind L1, Rage L13, Fire Punch L19, Flame Wheel L19, Bite L23, Wing Attack L36, Body Slam L42, Slam L48, Outrage L48, Fire Blast L52, Blast Burn L55 | Fire Spin L51→L15, Slash L41→L29, Flamethrower L47→L31, Inferno L56→L49 |
| Squirtle | Withdraw L9, Water Gun L10, Protect L20, Bubblebeam L21, Soak L26, Body Slam L27, Waterfall L33, Ice Beam L45 | Bubble L7→L5, Bite L16→L15, Skull Bash L31→L30, Iron Defense L34→L33 |
| Wartortle | Protect L20, Bubblebeam L21, Soak L26, Body Slam L27, Waterfall L33, Ice Beam L45 | Bite L17→L15, Skull Bash L37→L30, Rain Dance L45→L33, Iron Defense L41→L33, Hydro Pump L49→L47 |
| Blastoise | Dragon Pulse L1, Protect L20, Bubblebeam L21, Soak L26, Body Slam L27, Waterfall L33, Hydro Cannon L55 | Bubble L13→L12, Bite L17→L15, Rapid Spin L20→L17, Water Pulse L25→L22, Skull Bash L40→L30, Rain Dance L54→L33, Iron Defense L47→L33, Hydro Pump L60→L47 |
| Metapod | Tackle L1, String Shot L1 |  |
| Butterfree | Tackle L1, Harden L1, String Shot L1, Leech Life L10, Giga Drain L27, Psychic L32, Signal Beam L37, Synchronoise L42 | Supersonic L23→L17, Whirlwind L29→L21, Captivate L37→L30, Air Slash L43→L32 |
| Kakuna | Poison Sting L1, String Shot L1 |  |
| Beedrill | String Shot L1, Harden L1, Poison Sting L1, Rage L10, Leech Life L10, Acid L21, Sludge L25, Spike Cannon L25, Swords Dance L30, U-turn L30, Drill Run L37 | Pin Missile L32→L10, Focus Energy L20→L12, Toxic Spikes L29→L21, Fell Stinger L44→L23, Poison Jab L35→L32 |
| Pidgey | Sand Attack L4, Twister L16, Wing Attack L19, Mud-Slap L24, Sky Attack L42, Hyper Voice L49, Brave Bird L53 | Gust L9→L6, Quick Attack L13→L10, Whirlwind L17→L13, Agility L29→L28, Air Slash L49→L31, Mirror Move L45→L39 |
| Pidgeotto | Twister L16, Wing Attack L18, Mud-Slap L24, Sky Attack L42, Hyper Voice L49, Brave Bird L53 | Quick Attack L13→L10, Whirlwind L17→L13, Agility L32→L28, Air Slash L37→L31, Mirror Move L40→L39, Tailwind L47→L46 |
| Pidgeot | Feint L1, Twister L16, Wing Attack L18, Mud-Slap L24, Take Down L29, Extremespeed L36, Sky Attack L40, Hyper Voice L49 | Whirlwind L17→L13, Agility L32→L28, Air Slash L38→L31, Mirror Move L44→L39, Tailwind L50→L46 |
| Rattata | Dig L23, Take Down L26 | Assurance L19→L18 |
| Raticate | Ice Fang L1, Fire Fang L1, Thunder Fang L1, Assurance L18, Dig L23, Take Down L26 | Super Fang L34→L28, Endeavor L44→L41 |
| Spearow | Aerial Ace L15, Swift L18, Take Down L21, Sharpen L26, Whirlwind L28, Drill Run L36, Brave Bird L43, Thrash L47 | Focus Energy L29→L7, Fury Attack L15→L10, Drill Peck L36→L24 |
| Fearow | Aerial Ace L15, Swift L18, Take Down L21, Sharpen L26, Whirlwind L28, Thrash L47 | Fury Attack L11→L10, Drill Peck L41→L24, Brave Bird L48→L43 |
| Ekans | Acid L13, Gastro Acid L20, Substitute L22, Acid Spray L24, Sludge L27, Crunch L28, Mud Bomb L30, Poison Jab L33, Sludge Bomb L36, Foul Play L48 | Bite L9→L6, Glare L12→L10, Screech L17→L15, Poison Fang L28→L18, Haze L41→L22, Gunk Shot L49→L45 |
| Arbok | Acid L13, Gastro Acid L20, Substitute L22, Acid Spray L24, Sludge L27, Mud Bomb L30, Sludge Bomb L36, Foul Play L48 | Glare L12→L10, Screech L17→L15, Poison Fang L32→L18, Haze L51→L22, Stockpile L27→L26, Swallow L27→L26, Spit Up L27→L26, Belch L48→L39, Gunk Shot L63→L45 |
| Pikachu | Double Team L16, Headbutt L18, Thunderpunch L20, Iron Tail L44, Volt Tackle L50 | Growl L5→L4, Quick Attack L10→L6, Thunder Wave L18→L10, Spark L26→L13, Discharge L34→L27, Agility L45→L30, Light Screen L53→L40, Thunder L58→L48 |
| Raichu | Growl L1, Thunder Wave L1, Nasty Plot L1, Spark L13, Double Team L15, Headbutt L18, Thunderpunch L20, Slam L20, Electro Ball L21, Nuzzle L23, Discharge L27, Agility L30, Feint L33, Light Screen L40, Thunder L41, Iron Tail L44, Volt Tackle L53 |  |
| Sandshrew | Sand Attack L1, Mud-Slap L9, Metal Claw L16, Cut L28, Drill Run L30, X-Scissor L38, Spike Cannon L46 | Fury Swipes L20→L1, Sand Tomb L23→L5, Magnitude L14→L12, Dig L30→L14, Sandstorm L42→L32, Earthquake L46→L33 |
| Sandslash | Mud-Slap L9, Metal Claw L16, Spike Cannon L24, Cut L28, Drill Run L30, X-Scissor L38 | Fury Swipes L20→L1, Sand Tomb L24→L5, Magnitude L14→L12, Dig L33→L14, Earthquake L53→L30, Sandstorm L48→L32, Swords Dance L43→L42 |
| Nidoran♀ | Dig L26, Headbutt L30, Sludge Bomb L32 | Tail Whip L7→L4, Poison Sting L13→L6, Bite L21→L8, Double Kick L9→L8, Fury Swipes L19→L14, Helping Hand L25→L19, Poison Fang L45→L22, Toxic Spikes L31→L30, Flatter L33→L32 |
| Nidorina | Helping Hand L19, Headbutt L21, Dig L24, Sludge L32, Earthquake L40 | Tail Whip L7→L1, Poison Sting L13→L6, Bite L23→L8, Double Kick L9→L8, Fury Swipes L20→L14, Poison Fang L58→L22, Toxic Spikes L35→L30, Flatter L38→L32, Crunch L43→L41, Captivate L50→L44 |
| Nidoqueen | Dig L1, Growl L1, Fury Swipes L1, Headbutt L8, Bite L17, Helping Hand L19, Poison Fang L22, Magnitude L23, Toxic Spikes L30, Sludge Bomb L32, Flatter L32, Earthquake L40, Crunch L41, Captivate L44 |  |
| Nidoran♂ | Poison Tail L22, Dig L26, Horn Drill L41 | Focus Energy L7→L4, Poison Sting L13→L6, Double Kick L9→L8, Fury Attack L19→L14, Horn Attack L21→L17, Helping Hand L25→L19, Toxic Spikes L31→L30, Flatter L33→L32 |
| Nidorino | Helping Hand L19, Bite L21, Poison Tail L22, Dig L24, Sludge L32, Sludge Bomb L37, Horn Drill L38, Earthquake L40 | Focus Energy L7→L1, Double Kick L9→L8, Poison Sting L13→L11, Fury Attack L20→L14, Horn Attack L23→L17, Toxic Spikes L35→L30, Flatter L38→L32, Captivate L50→L44 |
| Nidoking | Dig L1, Fury Attack L1, Leer L1, Horn Attack L17, Helping Hand L19, Poison Tail L22, Magnitude L26, Toxic Spikes L30, Flatter L32, Earthquake L36, Sludge Bomb L36, Poison Jab L38, Horn Drill L41, Captivate L44 |  |
| Clefairy | Minimize L19, Dazzling Gleam L30, Light Screen L43 | Defense Curl L13→L12, Follow Me L16→L14, Stored Power L28→L27, Metronome L31→L30, Body Slam L40→L35, Gravity L49→L42 |
| Clefable | Growl L1, Pound L1, Encore L1, Defense Curl L12, Follow Me L14, Minimize L19, Bestow L19, Wake-Up Slap L22, Stored Power L27, Dazzling Gleam L30, Cosmic Power L33, Body Slam L35, Moonlight L37, Lucky Chant L37, Light Screen L41, Gravity L42, Meteor Mash L45, Healing Wish L53, After You L55 | Moonblast L51→L48 |
| Vulpix | Flame Wheel L19, Reflect L25, Shadow Ball L36, Night Shade L37, Sunny Day L40, Nasty Plot L51 | Tail Whip L4→L1, Roar L7→L4, Baby-Doll Eyes L9→L6, Quick Attack L10→L7, Fire Spin L15→L11, Feint Attack L23→L17, Flame Burst L28→L19, Hex L26→L25, Safeguard L34→L27, Flamethrower L36→L30, Captivate L47→L37, Fire Blast L42→L40, Inferno L50→L47 |
| Ninetales | Tail Whip L1, Roar L1, Mystical Fire L1, Ember L1, Baby-Doll Eyes L1, Fire Spin L11, Will-O-Wisp L17, Feint Attack L17, Flame Wheel L19, Flame Burst L19, Reflect L25, Hex L25, Extrasensory L32, Shadow Ball L36, Night Shade L37, Captivate L37, Sunny Day L40, Fire Blast L40, Grudge L47, Inferno L47 |  |
| Jigglypuff | Charm L7, Double Slap L8, Fake Tears L17, Encore L33, Play Rough L33, Dazzling Gleam L41, Perish Song L48, Moonblast L51 | Pound L5→L1, Play Nice L9→L5, Disable L14→L10, Rollout L20→L12, Round L22→L15, Lovely Kiss L65→L22, Rest L30→L24, Body Slam L32→L25, Hyper Voice L41→L36, Double-Edge L45→L41 |
| Wigglytuff | Pound L1, Boomburst L1, Play Nice L1, Charm L7, Rollout L12, Round L15, Fake Tears L17, Rest L24, Body Slam L25, Wake-Up Slap L30, Encore L33, Hyper Voice L36, Mimic L39, Dazzling Gleam L41, Perish Song L48 | Lovely Kiss L50→L22 |
| Zubat | Gust L4, Swift L19, Acid L27, Sludge L27, Sludge Bomb L36, Cross Poison L38 | Haze L35→L34 |
| Golbat | Gust L1, Swift L19, Acid L27, Sludge L27, Acrobatics L31, Sludge Bomb L36, Cross Poison L38 | Poison Fang L27→L25, Haze L40→L34, Air Slash L48→L41, Quick Guard L51→L43 |
| Oddish | Tackle L1, Leech Seed L8, Lucky Chant L20, Sludge Bomb L36 | Sweet Scent L5→L4, Poisonpowder L13→L5, Acid L9→L8, Stun Spore L14→L12, Mega Drain L19→L13, Sleep Powder L15→L13, Grassy Terrain L47→L26, Natural Gift L39→L28 |
| Gloom | Tackle L1, Leech Seed L8, Lucky Chant L20, Sludge Bomb L36, Solarbeam L50, Moonblast L51 | Poison Powder L13→L11, Stun Spore L14→L12, Mega Drain L19→L13, Sleep Powder L15→L13, Sludge L24→L23, Grassy Terrain L54→L26, Moonlight L29→L28, Natural Gift L44→L28, Giga Drain L34→L31, Petal Dance L59→L35, Toxic L39→L35 |
| Vileplume | Tackle L1, Absorb L1, Acid L1, Sweet Scent L1, Leech Seed L8, Sleep Powder L13, Lucky Chant L20, Sludge L23, Grassy Terrain L26, Moonlight L28, Natural Gift L28, Giga Drain L31, Toxic L35, Moonblast L51 | Petal Blizzard L49→L1, Petal Dance L59→L40, Solarbeam L69→L50 |
| Paras | Absorb L3, Mega Drain L13, Growth L15, Slash L21, Giga Drain L26, Twineedle L29, Seed Bomb L34, X-Scissor L43, Moonlight L46 | Leech Life L27→L8, Aromatherapy L43→L31, Rage Powder L49→L40 |
| Parasect | Absorb L1, Mega Drain L13, Growth L15, Slash L21, Infestation L24, Giga Drain L26, Twineedle L29, Seed Bomb L34, X-Scissor L43, Moonlight L46 | Aromatherapy L51→L31, Rage Powder L59→L40 |
| Venonat | Infestation L23, Skill Swap L33, Endeavor L38, Sludge Bomb L42, Bug Buzz L48 | Supersonic L5→L4, Confusion L11→L7, Poison Powder L13→L9, Leech Life L35→L12, Poison Fang L41→L16, Stun Spore L23→L18, Sleep Powder L29→L26, Zen Headbutt L37→L30, Psychic L47→L41 |
| Venomoth | Tailwind L1, Acid L25, Skill Swap L33, Air Slash L38, Sludge Bomb L42, Sludge L46 | Confusion L11→L7, Poison Powder L13→L9, Leech Life L37→L12, Poison Fang L47→L16, Stun Spore L23→L18, Sleep Powder L29→L26, Zen Headbutt L41→L30, Psychic L55→L41 |
| Diglett | Rototiller L1, Astonish L5, Pursuit L12, Rock Tomb L18, Rock Slide L33, Screech L35, Sandstorm L35, Night Slash L43 | Growl L4→L3, Mud-Slap L10→L7, Magnitude L14→L10, Bulldoze L18→L15, Slash L35→L21, Dig L31→L24 |
| Dugtrio | Pursuit L12, Rock Tomb L18, Rock Slide L33, Screech L35, Sandstorm L35 | Astonish L7→L5, Mud-Slap L10→L7, Magnitude L14→L10, Bulldoze L18→L15, Slash L41→L21, Dig L35→L24, Earthquake L47→L39 |
| Meowth | Feint Attack L17, Swift L20, Take Down L28, Power Gem L32, Snatch L36, Double-Edge L38, Swagger L40, Knock Off L43, Hyper Beam L45, Trump Card L48 | Bite L6→L1, Fake Out L9→L7, Fury Swipes L14→L8, Pay Day L30→L12, Captivate L46→L15, Taunt L25→L22, Slash L33→L24, Assurance L41→L26, Feint L50→L29, Night Slash L49→L34 |
| Persian | Pay Day L12, Feint Attack L17, Take Down L28, Snatch L36, Double-Edge L38, Swagger L40, Knock Off L43, Trump Card L48, Hyper Beam L50 | Fury Swipes L14→L8, Captivate L56→L15, Taunt L25→L22, Slash L37→L24, Assurance L49→L26, Feint L65→L29, Night Slash L61→L34 |
| Psyduck | Bubblebeam L17, Signal Beam L29, Scald L34, Psychic L37, Power Gem L42 | Tail Whip L4→L1, Water Gun L7→L4, Confusion L10→L7, Disable L19→L10, Fury Swipes L13→L10, Water Pulse L16→L13, Screech L22→L18, Zen Headbutt L25→L21, Aqua Tail L28→L24, Psych Up L34→L26, Amnesia L37→L29 |
| Golduck | Amnesia L1, Bubblebeam L17, Signal Beam L29, Calm Mind L31, Power Gem L42 | Water Gun L7→L1, Confusion L10→L7, Fury Swipes L13→L10, Water Pulse L16→L13, Screech L22→L18, Zen Headbutt L25→L21, Aqua Tail L28→L24, Psych Up L36→L26, Hydro Pump L46→L43, Wonder Room L51→L47 |
| Mankey | Fury Swipes L5, Low Sweep L16, Submission L24, Work Up L26, Mega Punch L30 | Seismic Toss L15→L11, Assurance L26→L14, Screech L37→L19, Cross Chop L47→L33, Close Combat L64→L44, Final Gambit L50→L48 |
| Primeape | Fury Swipes L5, Low Sweep L16, Covet L21, Submission L24, Work Up L26, Mega Punch L30, Thrash L39 | Shadow Punch L35→L1, Seismic Toss L15→L11, Assurance L26→L14, Screech L40→L19, Cross Chop L53→L33, Close Combat L60→L44 |
| Growlithe | Growl L1, Snarl L24, Extreme Speed L49 | Ember L6→L1, Leer L8→L6, Odor Sleuth L10→L8, Helping Hand L12→L10, Flame Wheel L17→L13, Take Down L23→L16, Retaliate L32→L31 |
| Arcanine | Bite L1, Agility L1, Growl L1, Ember L1, Leer L6, Flame Wheel L13, Take Down L16, Reversal L19, Snarl L24, Flame Burst L28, Flamethrower L35, Heat Wave L45, Outrage L50 |  |
| Poliwag | Mind Reader L1, Mist L4, Helping Hand L27, Muddy Water L31, Amnesia L36, Double-Edge L49 | Doubleslap L15→L1, Water Gun L5→L1, Hypnosis L8→L1, Bubble L11→L10, Mud Shot L28→L15, Bubble Beam L25→L18, Wake-Up Slap L35→L34, Mud Bomb L41→L39 |
| Poliwhirl | Mist L1, Mind Reader L1, Karate Chop L25, Helping Hand L27, Ice Punch L30, Muddy Water L31, Amnesia L36, Double-Edge L49 | Doubleslap L15→L10, Bubble L11→L10, Mud Shot L32→L15, Bubble Beam L27→L18, Wake-Up Slap L43→L34, Mud Bomb L53→L39, Hydro Pump L48→L42 |
| Poliwrath | Mist L1, Karate Chop L1, Ice Punch L1, Bubble L1, Mind Reader L1, Hammer Arm L1, Dive L1, Detect L1, Comet Punch L12, Mach Punch L15, Rain Dance L20, Body Slam L24, Muddy Water L31, Bulk Up L36, Hydro Pump L42, Belly Drum L43, Amnesia L48 |  |
| Machop | Focus Energy L3, Foresight L9, Assurance L21, Mega Punch L30, Take Down L33, Counter L37, Double-Edge L54 | Submission L33→L28 |
| Machoke | Assurance L21, Mega Punch L30, Body Slam L33, Counter L37, Double-Edge L54 | Submission L37→L28, Cross Chop L47→L40, Bulk Up L43→L40, Scary Face L53→L43, Dynamic Punch L57→L49 |
| Machamp | Bullet Punch L1, Assurance L21, Mega Punch L30, Take Down L33, Counter L37, Double-Edge L54 | Submission L37→L28, Cross Chop L47→L40, Bulk Up L43→L40, Scary Face L53→L43, Dynamic Punch L57→L49 |
| Bellsprout | Sweet Scent L1, Acid L12, Headbutt L27, Leaf Tornado L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Leaf Blade L40, Leaf Storm L53 | Growth L7→L5, Wrap L11→L8, Poisonpowder L15→L13, Stun Spore L17→L16, Razor Leaf L39→L20, Gastro Acid L35→L32, Wring Out L50→L45 |
| Weepinbell | Sweet Scent L1, Acid L12, Headbutt L27, Leaf Tornado L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Leaf Blade L40, Leaf Storm L53 | Poisonpowder L15→L1, Stun Spore L17→L16, Razor Leaf L44→L20, Gastro Acid L39→L32, Slam L54→L45, Wring Out L58→L45 |
| Victreebel | Growth L1, Wrap L1, Acid L1, Poisonpowder L13, Vine Whip L14, Stun Spore L16, Sludge L25, Headbutt L27, Body Slam L30, Gastro Acid L32, Knock Off L35, Cross Poison L38, Slam L45, Wring Out L45 | Sludge Bomb L44→L32, Leaf Blade L41→L40 |
| Tentacool | Poison Sting L1, Bubble L1, Constrict L3, Whirlpool L9, Wrap L15, Brine L33, Sludge Bomb L34 | Supersonic L4→L1, Acid L10→L6, Water Pulse L16→L13, Acid Spray L19→L18, Bubble Beam L25→L19, Barrier L28→L26, Poison Jab L31→L29, Screech L37→L36, Sludge Wave L43→L40 |
| Tentacruel | Bubble L1, Whirlpool L9, Water Gun L13, Wrap L15, Brine L33, Sludge Bomb L34 | Acid L10→L6, Water Pulse L16→L13, Acid Spray L19→L18, Bubble Beam L25→L19, Sludge L22→L20, Barrier L28→L26, Poison Jab L32→L29, Screech L40→L36, Sludge Wave L48→L40, Hex L44→L43, Hydro Pump L52→L47 |
| Geodude | Mud-Slap L6, Rock Throw L9, Dig L21, Steamroller L36, Rock Slide L40 | Mud Sport L4→L1, Smack Down L18→L16, Self-Destruct L24→L21 |
| Graveler | Mud-Slap L6, Dig L21, Harden L26, Steamroller L36, Rock Slide L40 | Rock Throw L16→L9, Smack Down L18→L16, Self-Destruct L24→L21, Stealth Rock L30→L29, Stone Edge L54→L49 |
| Golem | Mud-Slap L6, Dig L21, Harden L26, Rollout L26, Rock Slide L40 | Rock Throw L16→L9, Smack Down L18→L16, Self-Destruct L24→L21, Stealth Rock L30→L29, Stone Edge L54→L49 |
| Ponyta | Ember L6, Double Kick L14, Sunny Day L25, Blaze Kick L29, Flamethrower L33, High Jump Kick L42, Double-Edge L49 | Fire Spin L25→L1, Flame Charge L21→L12, Take Down L29→L22, Bounce L45→L32, Agility L37→L34 |
| Rapidash | Tackle L1, Double Kick L14, Sunny Day L25, Blaze Kick L29, Flamethrower L33, Hi Jump Kick L40, Double-Edge L49 | Fire Spin L25→L1, Stomp L17→L9, Flame Charge L21→L12, Take Down L29→L22, Bounce L45→L32, Agility L37→L34 |
| Slowpoke | Water Gun L5, Confusion L11, Waterfall L28, Brine L35, Withdraw L36, Aqua Tail L51 | Disable L17→L15, Headbutt L24→L18, Heal Pulse L58→L27, Zen Headbutt L32→L31, Amnesia L41→L39, Psychic L45→L44, Rain Dance L49→L48, Psych Up L54→L53 |
| Slowbro | Water Gun L5, Waterfall L28, Brine L35, Withdraw L36, Aqua Tail L51 | Confusion L14→L11, Disable L17→L15, Headbutt L20→L18, Psybeam L28→L25, Zen Headbutt L32→L31, Amnesia L43→L40, Psychic L49→L45, Rain Dance L55→L48, Psych Up L62→L53 |
| Magnemite | Thundershock L6, Swift L24, Reflect L27, Tri Attack L30, Thunderbolt L33, Electric Terrain L42, Thunder L50 | Sonic Boom L17→L8, Spark L19→L17, Screech L35→L19, Electro Ball L29→L22, Magnet Rise L43→L28, Discharge L37→L36, Gyro Ball L47→L45 |
| Magneton | Swift L24, Reflect L27, Thunderbolt L33, Thunder L50, Refresh L57 | Spark L19→L17, Screech L39→L19, Electro Ball L29→L22, Magnet Rise L53→L28, Discharge L43→L37, Gyro Ball L59→L45 |
| Farfetch'd | Sharpen L9, Air Cutter L17, Wing Attack L18, Baton Pass L28, Leaf Blade L39, Air Slash L41, Body Slam L43 | Knock Off L13→L10, False Swipe L45→L15, Swords Dance L66→L22, Night Slash L33→L25, Drill Peck L72→L31, Acrobatics L37→L31, Feint L43→L33 |
| Doduo | Double Kick L11, Low Kick L23, Bounce L24, Acupressure L27, Tri Attack L39, Double-Edge L50, Mega Kick L52 | Uproar L29→L1, Drill Peck L43→L34, Endeavor L47→L37 |
| Dodrio | Blaze Kick L1, Double Kick L11, Low Kick L23, Bounce L24, Acupressure L27, Mega Kick L52 | Uproar L29→L1, Thrash L56→L1, Endeavor L52→L37, Jump Kick L43→L40 |
| Seel | Whirlpool L1, Powder Snow L1, Water Gun L5, Aqua Ring L15, Bubblebeam L25, Work Up L27, Avalanche L44, Blizzard L50 | Growl L3→L1, Water Sport L7→L3, Aqua Jet L31→L7, Icy Wind L11→L10, Encore L13→L12, Aurora Beam L27→L16, Brine L33→L20, Take Down L37→L24, Dive L41→L30, Ice Beam L47→L32, Safeguard L51→L38, Aqua Tail L43→L41 |
| Dewgong | Water Gun L1, Powder Snow L1, Drill Run L1, Whirlpool L1, Water Sport L1, Aqua Ring L15, Bubblebeam L25, Work Up L27, Avalanche L44, Blizzard L50 | Aqua Jet L31→L7, Encore L13→L12, Brine L33→L20, Aurora Beam L27→L22, Take Down L39→L24, Dive L45→L30, Safeguard L61→L38, Aqua Tail L49→L41 |
| Grimer | Harden L10, Minimize L12, Acid L16, Sludge Wave L22, Toxic L24, Mud Shot L26, Payback L27, Poison Jab L30, Body Slam L37, Pain Split L38, Punishment L45 | Mud-Slap L7→L6, Disable L12→L8, Mud Bomb L18→L14, Fling L26→L17, Screech L37→L19, Acid Armor L43→L24, Belch L46→L35 |
| Muk | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Minimize L12, Acid L16, Sludge Wave L22, Toxic L24, Mud Shot L26, Payback L27, Poison Jab L30, Body Slam L37, Pain Split L38, Punishment L45, Hammer Arm L52 | Disable L12→L1, Sludge L15→L11, Mud Bomb L18→L14, Fling L26→L17, Screech L37→L19, Acid Armor L46→L24, Belch L52→L35, Memento L57→L48 |
| Shellder | Bubble Beam L22, Blizzard L50, Explosion L55 | Withdraw L4→L1, Supersonic L8→L4, Whirlpool L40→L7, Aurora Beam L37→L12, Protect L16→L14, Leer L20→L17, Ice Shard L28→L17, Clamp L25→L22, Razor Shell L32→L31, Iron Defense L49→L33, Ice Beam L52→L35, Brine L44→L35, Hydro Pump L61→L44, Shell Smash L57→L47 |
| Cloyster | Tackle L1, Clamp L1, Whirlpool L1, Water Gun L10, Leer L17, Bubble Beam L22, Icicle Spear L26, Razor Shell L31, Iron Defense L33, Brine L35, Ice Beam L37, Blizzard L50 | Ice Shard L28→L17 |
| Gastly | Smog L4, Psywave L15, Clear Smog L18, Poison Gas L23, Payback L23 | Hex L43→L28 |
| Haunter | Smog L1, Psywave L15, Clear Smog L18, Payback L23 | Hex L55→L28, Dream Eater L39→L35, Destiny Bond L50→L48, Nightmare L61→L51 |
| Gengar | Smog L1, Psywave L1, Clear Smog L18, Payback L23 | Hex L55→L28, Dream Eater L39→L35, Destiny Bond L50→L48, Nightmare L61→L51 |
| Onix | Bulldoze L18 | Rock Throw L7→L4, Rage L13→L6, Slam L28→L13, Stealth Rock L16→L15, Dig L43→L18, Sandstorm L52→L29, Rock Slide L34→L30, Screech L31→L30, Earthquake L57→L40, Stone Edge L46→L43, Double-Edge L49→L46 |
| Drowzee | Dream Eater L24, Payback L27, Skill Swap L35, Foul Play L42 | Disable L5→L4, Confusion L9→L6, Headbutt L13→L9, Poison Gas L17→L11, Meditate L21→L14, Psybeam L25→L17, Psych Up L33→L20, Swagger L45→L30, Psychic L49→L33, Zen Headbutt L41→L38, Future Sight L61→L46, Nasty Plot L53→L49 |
| Hypno | Payback L27, Skill Swap L35, Zen Headbutt L38, Foul Play L42 | Headbutt L13→L9, Poison Gas L17→L11, Meditate L21→L14, Psybeam L25→L17, Psych Up L33→L20, Swagger L45→L30, Psychic L41→L32, Future Sight L54→L45 |
| Krabby | Razor Shell L25, Hone Claws L28, Cut L29, X-Scissor L31, Swords Dance L46 | Harden L11→L1, Leer L9→L7, Bubble Beam L15→L11, Mud Shot L19→L14, Metal Claw L21→L17, Brine L39→L20, Stomp L25→L23, Crabhammer L41→L34 |
| Kingler | Hammer Arm L1, Razor Shell L25, Cut L28, Hone Claws L28, X-Scissor L31, Protect L37, Swords Dance L46 | Harden L11→L1, Bubble Beam L15→L11, Mud Shot L19→L14, Metal Claw L21→L17, Brine L51→L20, Stomp L25→L23, Crabhammer L56→L27, Flail L63→L49 |
| Voltorb | Rapid Spin L1, Spark L9, Thunder Wave L14, Thundershock L19, Electric Terrain L21, Thunderbolt L35, Thunder L40, Signal Beam L40, Rain Dance L42, Nasty Plot L54 | Eerie Impulse L6→L4, Swift L20→L17, Discharge L37→L35 |
| Electrode | Spark L1, Volt Tackle L1, Weather Ball L1, Rapid Spin L1, Thunder Wave L14, Thundershock L19, Electric Terrain L21, Thunderbolt L35, Thunder L40, Signal Beam L40, Rain Dance L42, Nasty Plot L54, Refresh L59 | Eerie Impulse L6→L1, Swift L20→L17, Discharge L41→L35, Mirror Coat L54→L49 |
| Exeggcute | Giga Drain L31, Grassy Terrain L39, Egg Bomb L40, Psychic L45, Soft-Boiled L45 | Reflect L7→L5, Leech Seed L11→L9, Poisonpowder L21→L10, Confusion L27→L13, Sleep Powder L23→L19, Worry Seed L33→L25, Natural Gift L37→L30, Extrasensory L47→L37, Solarbeam L43→L42, Bestow L50→L42 |
| Exeggutor | Reflect L1, Giga Drain L1, Uproar L1, Leech Seed L9, Poisonpowder L10, Bullet Seed L16, Stun Spore L17, Sleep Powder L19, Mega Drain L20, Worry Seed L25, Psybeam L28, Growth L30, Grassy Terrain L39, Solarbeam L42, Psychic L45, Soft-Boiled L45 |  |
| Cubone | Tackle L1, Earthquake L47, Belly Drum L51, Iron Head L53 | Leer L13→L5, Focus Energy L17→L13, False Swipe L27→L15, Rage L23→L17, Fling L33→L27, Bone Rush L51→L33, Endeavor L41→L37, Double-Edge L43→L41, Retaliate L47→L43 |
| Marowak | Tackle L1, Head Smash L1, Earthquake L46, Belly Drum L51, Iron Head L53 | Leer L13→L5, Focus Energy L17→L13, False Swipe L27→L15, Rage L23→L17, Fling L37→L27, Thrash L33→L31, Bone Rush L65→L33, Endeavor L49→L37, Double-Edge L53→L41, Retaliate L59→L43 |
| Hitmonlee | Helping Hand L1, Fake Out L1, Knock Off L27, Bounce L43 | Foresight L37→L1, Feint L25→L10, Focus Energy L21→L14, Mind Reader L33→L23, Wide Guard L41→L36, Blaze Kick L45→L40 |
| Hitmonchan | Helping Hand L1, Fake Out L1, Foresight L1, Power-Up Punch L7, Drain Punch L20, Karate Chop L25, Dynamic Punch L36, Dizzy Punch L39, Submission L42, Shadow Punch L47 | Agility L6→L4, Bullet Punch L16→L14, Feint L21→L17, Mega Punch L46→L23, Ice Punch L36→L27, Thunder Punch L36→L27, Fire Punch L36→L27, Sky Uppercut L41→L30 |
| Lickitung | Pound L1, Headbutt L19, Curse L25, Body Slam L32, Belly Drum L40 | Wrap L17→L1, Disable L25→L1, Defense Curl L9→L8, Stomp L21→L13, Rollout L33→L17, Slam L29→L21, Chip Away L37→L24, Refresh L45→L29, Me First L41→L40, Screech L49→L43, Power Whip L53→L47, Wring Out L57→L52 |
| Koffing | Rapid Spin L1, Smokescreen L15, Acid L23, Venoshock L25, Amnesia L26, Payback L28, Pain Split L49 | Clear Smog L15→L10, Selfdestruct L23→L15, Sludge L18→L16, Haze L26→L22, Memento L45→L30 |
| Weezing | Smokescreen L15, Acid L23, Venoshock L25, Amnesia L26, Payback L28, Pain Split L49 | Clear Smog L15→L10, Sludge L18→L16, Self-Destruct L23→L20, Haze L26→L22, Memento L57→L30, Explosion L40→L39, Destiny Bond L46→L43, Belch L51→L47 |
| Rhyhorn | Rock Throw L12, Magnitude L23, Dig L24, Rock Slide L36, Horn Drill L40, Double-Edge L56 | Stomp L17→L9, Smack Down L13→L9, Bulldoze L21→L16, Chip Away L25→L19, Take Down L37→L29, Earthquake L45→L39, Megahorn L49→L45 |
| Rhydon | Rock Throw L12, Magnitude L23, Dig L24, Rock Slide L36, Double-Edge L56 | Smack Down L13→L1, Bulldoze L21→L16, Chip Away L25→L19, Take Down L37→L29, Earthquake L48→L39, Megahorn L55→L45 |
| Chansey | Echoed Voice L10, Helping Hand L14, Minimize L18, Heal Bell L42, Hyper Voice L46, Mega Punch L50 | Tail Whip L5→L4, Refresh L9→L6, Double Slap L12→L8, Softboiled L16→L10, Bestow L20→L12, Take Down L27→L17, Sing L31→L22, Fling L35→L27, Egg Bomb L44→L28, Heal Pulse L39→L32, Light Screen L50→L37, Healing Wish L57→L49 |
| Tangela | Body Slam L37, Energy Ball L43, Morning Sun L55 | Absorb L10→L1, Poison Powder L14→L10, Bind L17→L13, Growth L20→L16, Mega Drain L23→L19, Knock Off L27→L22, Stun Spore L30→L23, Tickle L44→L28, Natural Gift L33→L28, Giga Drain L36→L31, Ancient Power L38→L34 |
| Kangaskhan | Pound L1, Focus Energy L8, Circle Throw L29, Body Slam L37, Double-Edge L48 | Tail Whip L10→L1, Fake Out L7→L5, Bite L13→L12, Chip Away L31→L15, Mega Punch L25→L24, Dizzy Punch L34→L25, Crunch L37→L36, Endure L43→L41, Reversal L50→L44 |
| Horsea | Smokescreen L5, Aurora Beam L24, Dragon Rage L26, Dragon Breath L28, Waterfall L33, Flail L36 | Leer L9→L7, Water Gun L13→L10, Twister L17→L14, Agility L36→L26 |
| Seadra | Aurora Beam L24, Dragon Rage L26, Dragon Breath L28, Waterfall L33, Flail L38, Slam L41, Body Slam L47 | Twister L17→L14, Agility L38→L26, Dragon Pulse L45→L42, Dragon Dance L58→L50 |
| Goldeen | Bubble L1, Water Gun L3, Water Pulse L16, Fury Attack L19, Drill Peck L27, Swords Dance L30, Rain Dance L32, Horn Drill L34, Aqua Tail L38, Hydro Pump L50 | Waterfall L32→L15, Megahorn L45→L35 |
| Seaking | Bubble L1, Water Gun L1, Drill Run L1, Water Pulse L16, Fury Attack L19, Drill Peck L27, Swords Dance L30, Rain Dance L32, Horn Drill L34, Aqua Tail L38, Hydro Pump L50 | Waterfall L32→L15 |
| Staryu | Water Gun L4, Confusion L10, Swift L15, Psybeam L25, Psyshock L40, Refresh L55 | Camouflage L22→L1, Reflect Type L35→L10, Bubble Beam L18→L16, Gyro Ball L24→L22, Light Screen L46→L27, Confuse Ray L40→L33, Psychic L42→L37, Cosmic Power L49→L41, Hydro Pump L53→L49 |
| Starmie | Confusion L1, Swift L1, Bubblebeam L1, Harden L1, Camouflage L1, Gravity L1, Icy Wind L1, Tackle L1, Reflect Type L10, Psywave L13, Signal Beam L19, Gyro Ball L22, Light Screen L27, Brine L28, Minimize L34, Psychic L37, Power Gem L37, Psyshock L40, Cosmic Power L41, Refresh L55 |  |
| Mr. Mime | Trick L32, Dazzling Gleam L39, Baton Pass L43 | Role Play L43→L3, Meditate L8→L5, Double Slap L11→L10, Encore L18→L12, Reflect L22→L18, Light Screen L22→L18, Psybeam L25→L24, Substitute L29→L27, Recycle L32→L30, Psychic L39→L36, Safeguard L50→L47 |
| Scyther | Cut L15, Double Team L31, Air Slash L35, Twineedle L42, Acrobatics L52, Swords Dance L55 | Fury Cutter L25→L1, Razor Wind L33→L1, Pursuit L9→L8, False Swipe L13→L11, Slash L29→L28, X-Scissor L41→L40, Night Slash L45→L44, Double Hit L49→L48, Feint L61→L57 |
| Jynx | Heart Stamp L10, Confusion L13, Captivate L19, Frost Breath L28, Psychic L38, Body Slam L43 | Double Slap L15→L13, Ice Punch L18→L16, Ice Beam L44→L41, Wring Out L49→L46, Blizzard L60→L54 |
| Electabuzz | Spark L17, Work Up L21, Mega Punch L32, Electric Terrain L44, Cross Chop L48 | Low Kick L8→L6, Shock Wave L15→L9, Thunder Wave L19→L16, Electro Ball L22→L19, Screech L42→L25, Discharge L36→L35, Thunderbolt L49→L42, Thunder L55→L52 |
| Magmar | Smokescreen L6, Flame Wheel L17, Work Up L21, Will-O-Wisp L22, Poison Gas L25, Mega Punch L32, Dark Pulse L48 | Fire Spin L15→L9, Clear Smog L19→L16, Flame Burst L22→L19, Confuse Ray L26→L20, Fire Punch L29→L25, Sunny Day L42→L30, Flamethrower L49→L39, Fire Blast L55→L50 |
| Pinsir | Twineedle L1, Leech Life L1, Bug Bite L16, Guillotine L37 | Seismic Toss L8→L1, Harden L11→L5, Vital Throw L18→L10, Revenge L15→L13, Slash L50→L42, Megahorn L60→L44 |
| Tauros | Refresh L1, Rock Climb L1, Iron Head L1, Outrage L1, Captivate L1, Leer L15, Stomp L19, Headbutt L22, Punishment L29, Take Down L32, Superpower L50 | Tail Whip L3→L1, Rage L5→L4, Horn Attack L8→L7, Rest L19→L18, Work Up L29→L25, Swagger L48→L40, Thrash L55→L45, Double-Edge L63→L50, Giga Impact L71→L60 |
| Gyarados | Tackle L1, Gust L20, Waterfall L25, Slam L48 | Leer L21→L1, Bounce L58→L44, Hyper Beam L54→L50 |
| Lapras | Icy Wind L15, Aurora Beam L23, Waterfall L34, Surf L43, Heal Pulse L46, Blizzard L55 | Brine L37→L29, Safeguard L43→L33 |
| Eevee | Sand Attack L4, Double Kick L14, Focus Energy L30, Baton Pass L30, Wish L35, Jump Kick L36 | Quick Attack L13→L6, Bite L17→L9, Charm L29→L20 |
| Vaporeon | Bubble L1, Growl L1, Icy Wind L1, Jump Kick L1, Sand Attack L4, Mist L12, Double Kick L14, Bite L17, Bubblebeam L26, Rest L47, Ice Beam L52 | Quick Attack L13→L6, Aqua Ring L25→L22 |
| Jolteon | Growl L1, Magnet Rise L1, Jump Kick L1, Sand Attack L4, Charge L12, Bite L17, Eerie Impulse L22, Spark L26, Charge Beam L29, Thunderbolt L36, Electric Terrain L48, Zap Cannon L52 | Quick Attack L13→L6, Double Kick L17→L14 |
| Flareon | Leer L1, Growl L1, Inferno L1, Jump Kick L1, Sand Attack L4, Double Kick L14, Facade L25, Flame Wheel L26, Growth L32, Will-O-Wisp L35, Flamethrower L36, Double-Edge L36, Blaze Kick L37, Play Rough L48, Fire Blast L52, Superpower L52 | Quick Attack L13→L6, Fire Spin L25→L12, Scary Face L29→L22, Lava Plume L37→L29 |
| Porygon | Swift L10, Electroweb L18, Barrier L40, Psyshock L44, Hyper Beam L50 | Psybeam L7→L4, Agility L12→L7, Recover L18→L14, Magnet Rise L23→L21, Signal Beam L29→L24, Tri Attack L50→L28, Recycle L34→L28, Discharge L40→L31, Magic Coat L56→L34, Lock-On L45→L41, Zap Cannon L62→L48 |
| Omanyte | Rock Throw L14, Clamp L14, Bubblebeam L18, Horn Attack L22, Protect L23, Spike Cannon L27, Iron Defense L29, Rock Slide L37, Power Gem L38, Earth Power L45, Spikes L51 | Leer L19→L1, Water Gun L10→L5, Rollout L16→L12, Mud Shot L25→L17, Ancient Power L37→L26, Tickle L43→L35, Hydro Pump L55→L46, Shell Smash L58→L49 |
| Omastar | Stealth Rock L1, Rock Throw L14, Clamp L14, Bubblebeam L18, Protect L23, Iron Defense L29, Rock Slide L37, Power Gem L38, Earth Power L45, Spikes L51 | Leer L19→L1, Water Gun L10→L1, Rollout L16→L12, Mud Shot L25→L17, Ancient Power L37→L26, Tickle L48→L35, Shell Smash L67→L49 |
| Kabuto | Sand Attack L1, Rock Throw L6, Water Gun L11, Smack Down L15, Slash L32, Rock Slide L36, Swords Dance L42, X-Scissor L43, Hydro Pump L48, Stone Edge L53 | Leer L11→L1, Absorb L6→L1, Mega Drain L36→L20, Metal Sound L41→L21, Ancient Power L46→L26, Aqua Jet L31→L28 |
| Kabutops | Rock Throw L1, Sand Attack L1, Water Gun L11, Smack Down L15, Ancient Power L26, Rock Slide L36, Swords Dance L42, X-Scissor L43, Hydro Pump L48, Stone Edge L53, Wring Out L56 | Mega Drain L36→L20, Metal Sound L45→L21, Aqua Jet L31→L28 |
| Aerodactyl | Gust L1, Rock Throw L27, Double-Edge L45, Dragon Claw L50, Stone Edge L60 | Agility L17→L15, Ancient Power L25→L20, Take Down L41→L25, Sky Drop L49→L30, Rock Slide L73→L40, Hyper Beam L65→L50, Giga Impact L81→L65 |
| Snorlax | Harden L33, Hammer Arm L62 | Block L41→L17, Rollout L36→L25, Crunch L49→L44, Heavy Slam L50→L49 |
| Articuno | Extrasensory L1, Heal Bell L1, Defog L1, Air Cutter L15, Drill Peck L40, Air Slash L40, Sky Attack L55 | Mist L8→L5, Ice Shard L15→L10, Mind Reader L22→L20, Ancient Power L29→L25, Agility L36→L35, Reflect L50→L45, Blizzard L78→L70 |
| Zapdos | Wing Attack L1, Extrasensory L1, Metal Sound L1, Eerie Impulse L1, Defog L1, Shock Wave L20, Electro Ball L30, Thunderbolt L45, Sky Attack L55, Baton Pass L61, Tailwind L80 | Thunder Wave L8→L5, Detect L15→L10, Pluck L22→L15, Ancient Power L29→L25, Agility L43→L35, Drill Peck L71→L42, Light Screen L64→L45, Thunder L78→L70 |
| Moltres | Extrasensory L1, Whirlwind L1, Defog L1, Incinerate L15, Growth L20, Flame Burst L30, Drill Peck L40, Fire Blast L51, Tailwind L80 | Fire Spin L8→L5, Endure L22→L10, Ancient Power L29→L25, Air Slash L50→L40, Sky Attack L78→L55, Solar Beam L71→L65 |
| Dratini | Tackle L1, Headbutt L18, Dragon Breath L31, Tri Attack L53, Hyper Beam L54 | Twister L11→L9, Dragon Rage L15→L14, Agility L25→L22, Dragon Tail L31→L27, Safeguard L45→L40, Outrage L55→L45, Dragon Dance L75→L48 |
| Dragonair | Tackle L1, Headbutt L18, Dragon Breath L31, Tri Attack L53, Hyper Beam L61 | Dragon Rage L15→L14, Agility L25→L22, Dragon Tail L33→L27, Aqua Tail L39→L35, Safeguard L53→L40, Dragon Rush L47→L44, Dragon Dance L75→L48, Outrage L67→L50 |
| Dragonite | Tackle L1, Heal Bell L1, Headbutt L18, Dragon Breath L31, Tri Attack L53, Wing Attack L55, Hyper Beam L61 | Dragon Rage L15→L14, Agility L25→L22, Dragon Tail L33→L27, Aqua Tail L39→L35, Safeguard L53→L40, Dragon Rush L47→L44, Dragon Dance L75→L48, Outrage L67→L56 |
| Mew | Sky Attack L1, Superpower L1, Knock Off L1, Iron Tail L1, Icy Wind L1, Soft-Boiled L1, Stealth Rock L1, Helping Hand L1, Trick L1, Defog L1, Psywave L1, Hyper Voice L10, Confusion L15, Psybeam L25, Zen Headbutt L30 |  |
| Chikorita | Leech Seed L9, Mega Drain L21, Giga Drain L26, Seed Bomb L39, Heal Pulse L42, Sunny Day L46 | Razor Leaf L6→L4, Poison Powder L8→L6, Reflect L15→L12, Magical Leaf L20→L15, Natural Gift L23→L20, Light Screen L31→L23, Body Slam L34→L30, Safeguard L39→L34 |
| Bayleef | Leech Seed L9, Giga Drain L26, Seed Bomb L39, Heal Pulse L42, Sunny Day L46 | Reflect L18→L12, Magical Leaf L22→L15, Natural Gift L26→L20, Light Screen L36→L23, Body Slam L40→L30, Safeguard L46→L34, Solarbeam L54→L45 |
| Meganium | Power Whip L1, Weather Ball L1, Leech Seed L9, Mega Drain L21, Giga Drain L26, Heal Pulse L42, Sunny Day L46 | Reflect L18→L12, Magical Leaf L22→L15, Natural Gift L26→L20, Light Screen L40→L23, Body Slam L46→L30, Safeguard L54→L34, Solarbeam L66→L45 |
| Cyndaquil | Work Up L25, Sunny Day L34, Endure L47, Fire Blast L50, Heat Wave L51 | Ember L7→L4, Quick Attack L13→L10, Defense Curl L22→L12, Swift L31→L19, Flame Charge L28→L23, Lava Plume L37→L29, Flamethrower L40→L31, Rollout L49→L31, Inferno L46→L42, Double-Edge L55→L45 |
| Quilava | Flame Charge L23, Work Up L25, Sunny Day L34, Heat Wave L45, Endure L47, Fire Blast L50 | Ember L7→L1, Quick Attack L13→L10, Defense Curl L24→L12, Swift L31→L19, Lava Plume L42→L29, Flamethrower L46→L31, Rollout L57→L31, Inferno L53→L42, Double-Edge L64→L45 |
| Typhlosion | Thunder Punch L1, Work Up L25, Rollout L31, Sunny Day L34, Heat Wave L45, Endure L47, Fire Blast L50 | Quick Attack L13→L10, Defense Curl L24→L12, Flame Wheel L20→L16, Swift L31→L19, Flame Charge L35→L23, Lava Plume L43→L29, Flamethrower L48→L31, Inferno L56→L42, Eruption L100→L60 |
| Totodile | Water Gun L4, Bubble Beam L17, Agility L25, Dive L28 | Bite L13→L11, Scary Face L18→L13, Chip Away L27→L22 |
| Croconaw | Bubble Beam L17, Agility L25, Dive L28 | Water Gun L6→L1, Bite L13→L11, Scary Face L21→L13, Chip Away L30→L22, Aqua Tail L43→L40 |
| Feraligatr | Dynamic Punch L1, Bubble Beam L17, Circle Throw L22, Dive L28, Outrage L47, Hydro Pump L50 | Bite L13→L11, Scary Face L21→L13, Screech L38→L37 |
| Sentret | Thief L9, Fury Swipes L12, Pursuit L16, Dig L20, Coil L22, Baton Pass L28, Extremespeed L30, Double-Edge L43 | Quick Attack L7→L6, Helping Hand L16→L10 |
| Furret | Thief L1, Tackle L1, Hyper Voice L1, Fury Swipes L12, Pursuit L16, Dig L20, Baton Pass L28, Rest L35 | Helping Hand L17→L10, Extremespeed L36→L30, Amnesia L42→L40, Double-Edge L56→L43, Me First L50→L46 |
| Hoothoot | Take Down L18, Psybeam L20, Light Screen L22, Wing Attack L24, Mirror Coat L30, Psychic L40, Hyper Voice L41, Defog L43, Future Sight L50 | Peck L7→L6, Echoed Voice L13→L10, Psycho Shift L19→L16, Roost L37→L29, Dream Eater L46→L45 |
| Noctowl | Future Sight L1, Take Down L18, Psybeam L20, Light Screen L22, Wing Attack L24, Mirror Coat L30, Psychic L40, Hyper Voice L41, Defog L43 | Echoed Voice L13→L10, Psycho Shift L19→L16, Roost L43→L29 |
| Ledyba | Leech Life L6, Silver Wind L18, Baton Pass L20, Work Up L22, Signal Beam L27, Air Slash L32, Giga Drain L36, Barrier L41, Me First L46 | Supersonic L5→L3, Agility L29→L24 |
| Ledian | Leech Life L1, Power Swap L1, Guard Swap L1, Silver Wind L18, Baton Pass L20, Work Up L22, Signal Beam L27, Air Slash L32, Giga Drain L36, Bug Buzz L39, Barrier L41, Double-Edge L44, Me First L46 | Agility L33→L24 |
| Spinarak | Leech Life L5, Poison Fang L13, Twineedle L18, Fell Stinger L22, Giga Drain L25, Megahorn L43, Knock Off L44 | Scary Face L12→L1, Night Shade L15→L8, Fury Swipes L22→L10, Shadow Sneak L19→L15, Spider Web L29→L20, Poison Jab L43→L27, Psychic L40→L30, Pin Missile L36→L35, Sticky Web L50→L38, Cross Poison L47→L41 |
| Ariados | Leech Life L1, Electroweb L1, Fury Swipes L10, Twineedle L18, Giga Drain L25, Psychic L30, Knock Off L44 | Night Shade L15→L8, Poison Fang L22→L13, Shadow Sneak L19→L15, Spider Web L30→L20, Poison Jab L42→L27, Megahorn L49→L43 |
| Crobat | Gust L1, Giga Drain L1, Swift L19, Sludge L27, Acrobatics L31, Sludge Bomb L36, X-Scissor L46, Toxic L50 | Poison Fang L27→L25, Haze L40→L34, Air Slash L48→L41, Quick Guard L51→L43 |
| Chinchou | Flail L1, Water Gun L13, Take Down L15, Thunderbolt L33, Rain Dance L33, Dive L35, Thunder L42 | Thunder Wave L6→L5, Spark L23→L19, Signal Beam L28→L26, Discharge L34→L30, Ion Deluge L47→L38, Charge L50→L44 |
| Lanturn | Flail L1, Water Gun L13, Take Down L15, Thunderbolt L33, Rain Dance L33, Dive L35, Thunder L42 | Spark L23→L19, Signal Beam L29→L26, Discharge L37→L30, Ion Deluge L54→L38, Hydro Pump L51→L41, Charge L58→L44, Aqua Ring L47→L44 |
| Togepi | Helping Hand L1, Fairy Wind L1, Return L10, Swift L25, Dazzling Gleam L35, Tri Attack L43, Soft-Boiled L50 | Sweet Kiss L9→L7, Encore L17→L15, Follow Me L21→L17, Bestow L25→L22, Ancient Power L33→L27, Safeguard L37→L32, Double-Edge L45→L38, After You L53→L47 |
| Togetic | Helping Hand L1, Return L10, Tailwind L22, Wing Attack L24, Air Cutter L25, Dazzling Gleam L35, Tri Attack L39, Defog L47, Soft-Boiled L50 | Fairy Wind L14→L1, Encore L17→L15, Follow Me L21→L17, Ancient Power L33→L27, Safeguard L37→L32 |
| Natu | Morning Sun L1, Teleport L7, Psybeam L21, Recover L30, Baton Pass L30, Air Slash L31, Wing Attack L40, Drill Peck L40 | Confusion L15→L4, Confuse Ray L23→L19, Wish L28→L25, Power Swap L47→L40, Guard Swap L47→L40 |
| Xatu | Teleport L7, Psybeam L21, Recover L30, Baton Pass L30, Wing Attack L40, Drill Peck L40, Morning Sun L49 | Confusion L15→L1, Confuse Ray L23→L19, Wish L29→L25, Psycho Shift L43→L34, Power Swap L53→L40, Guard Swap L53→L40 |
| Mareep | Thundershock L7, Shock Wave L21, Thunderbolt L47, Natural Gift L47, Tail Glow L62 | Cotton Spore L11→L4, Confuse Ray L25→L24 |
| Flaaffy | Shock Wave L21, Thunderbolt L47, Natural Gift L47, Tail Glow L62 | Cotton Spore L11→L1, Charge L16→L15, Take Down L20→L18, Confuse Ray L29→L24, Discharge L38→L37 |
| Ampharos | Shock Wave L21, Thunderbolt L47 | Cotton Spore L11→L1, Charge L16→L15, Take Down L20→L18, Confuse Ray L29→L24, Power Gem L35→L33, Discharge L39→L37, Light Screen L47→L39, Signal Beam L44→L41, Tail Glow L75→L62 |
| Bellossom | Poisonpowder L1, Charm L1, Absorb L1, Sleep Powder L13, Lucky Chant L20, Razor Leaf L23, Grassy Terrain L26, Morning Sun L28, Natural Gift L28, Giga Drain L31, Moonlight L35, Solar Beam L45 | Petal Blizzard L39→L1, Quiver Dance L59→L1, Petal Dance L49→L40 |
| Marill | Bubblebeam L18, Double Slap L19, Take Down L22, Belly Drum L45 | Helping Hand L16→L13, Aqua Ring L28→L24, Rain Dance L31→L28, Superpower L40→L39, Hydro Pump L47→L42 |
| Azumarill | Bounce L1, Bubblebeam L18, Double Slap L19, Take Down L22, Belly Drum L45 | Helping Hand L16→L13, Aqua Ring L31→L24, Rain Dance L35→L28, Superpower L46→L39, Hydro Pump L55→L42 |
| Sudowoodo | Fake Out L1, Submission L28, Curse L37, Thrash L46 | Feint Attack L19→L18, Rock Tomb L26→L20, Block L29→L23, Counter L36→L25, Sucker Punch L40→L34, Head Smash L54→L52 |
| Politoed | Bubble L1, Mist L1, Weather Ball L1, Sweet Kiss L1, Water Gun L1, Water Sport L1, Light Screen L15, Bubblebeam L20, Rain Dance L20, Body Slam L24, Muddy Water L31, Ice Beam L36, Amnesia L36, Hydro Pump L42 | Bounce L37→L34 |
| Hoppip | Gust L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Tackle L8→L1, Synthesis L4→L3, Tail Whip L6→L5, Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L19→L12, Mega Drain L25→L19, Leech Seed L22→L21, Cotton Spore L34→L24, U-turn L37→L26, Giga Drain L43→L30, Worry Seed L40→L38 |
| Skiploom | Gust L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L20→L12, Leech Seed L24→L21, Cotton Spore L40→L24, U-turn L44→L26, Giga Drain L52→L30, Rage Powder L36→L35, Worry Seed L48→L38, Bounce L56→L48, Memento L60→L52 |
| Jumpluff | Gust L1, Encore L1, Protect L24, Giga Drain L30, Seed Bomb L42, Cotton Guard L45 | Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L20→L12, Mega Drain L29→L19, Leech Seed L24→L21, Cotton Spore L44→L24, U-turn L49→L26, Acrobatics L34→L33, Rage Powder L39→L35, Worry Seed L54→L38, Bounce L64→L48, Memento L69→L52 |
| Aipom | Sand Attack L3, Pursuit L17, Low Kick L19, Swift L20, Dizzy Punch L28, Focus Punch L43, Beat Up L50 | Fury Swipes L18→L8, Tickle L15→L14, Fling L36→L35 |
| Sunkern | Grass Whistle L6, Bullet Seed L24, Petal Dance L30, Earth Power L46 | Mega Drain L10→L9, Leech Seed L13→L11, Razor Leaf L16→L14, Worry Seed L19→L16, Endeavor L25→L19, Synthesis L28→L25, Sunny Day L40→L37 |
| Sunflora | Agility L1, Grass Whistle L6, Endeavor L19, Synthesis L25, Earth Power L46, Giga Drain L50 | Ingrain L4→L1, Mega Drain L10→L9, Leech Seed L13→L11, Razor Leaf L16→L14, Worry Seed L19→L16, Bullet Seed L25→L24, Sunny Day L40→L37 |
| Yanma | Leech Life L1, Double Team L7, Twister L12, Signal Beam L24, Twineedle L25, Air Cutter L26, Acrobatics L49 | Quick Attack L6→L4, Sonic Boom L14→L10, Wing Attack L43→L15, Supersonic L22→L20, U-turn L49→L35, Air Slash L54→L38, Bug Buzz L57→L43 |
| Wooper | Mud-Slap L5, Headbutt L10, Bubble Beam L14, Magnitude L20, Body Slam L25, Aqua Tail L31 | Mud Sport L5→L4, Mud Shot L9→L7, Mud Bomb L19→L17, Amnesia L23→L19, Yawn L29→L28, Rain Dance L37→L33, Mist L43→L40, Haze L43→L40, Muddy Water L47→L45 |
| Quagsire | Recover L1, Mud-Slap L5, Headbutt L10, Bubble Beam L14, Magnitude L20, Body Slam L25, Aqua Tail L31 | Mud Shot L9→L1, Mud Bomb L19→L17, Amnesia L24→L19, Yawn L31→L28, Earthquake L36→L33, Rain Dance L41→L33, Mist L48→L40, Haze L48→L40, Muddy Water L53→L45 |
| Espeon | Growl L1, Jump Kick L1, Sand Attack L4, Telekinesis L12, Double Kick L14, Bite L17, Miracle Eye L25, Stored Power L45, Calm Mind L48, Reflect L52, Tri Attack L52 | Quick Attack L13→L6, Power Swap L45→L22, Psychic L37→L36 |
| Umbreon | Growl L1, Curse L1, Jump Kick L1, Sand Attack L4, Torment L12, Double Kick L14, Bite L17, Snarl L20, Dark Pulse L37, Foul Play L52 | Sucker Punch L25→L1, Quick Attack L13→L6, Guard Swap L45→L22 |
| Murkrow | Beat Up L1, Feint Attack L29, Drill Peck L33, Foul Play L41, Sky Attack L53 | Quash L65→L1, Haze L11→L9, Wing Attack L15→L13, Night Shade L21→L17, Assurance L25→L21, Taunt L31→L25, Mean Look L41→L37, Tailwind L50→L45, Sucker Punch L55→L49, Torment L61→L57 |
| Slowking | Heal Block L1, Brine L35, Amnesia L40, Future Sight L50 | Growl L5→L1, Water Gun L9→L1, Confusion L14→L11, Disable L17→L15, Headbutt L24→L18, Psybeam L28→L25, Zen Headbutt L32→L31, Swagger L41→L36, Trump Card L49→L48, Psych Up L54→L53 |
| Misdreavus | Night Shade L4, Ominous Wind L17, Trick L19, Icy Wind L22, Screech L24, Sing L24, Extrasensory L32, Wonder Room L40 | Spite L5→L1, Astonish L10→L4, Confuse Ray L14→L8, Mean Look L19→L10, Psybeam L28→L14, Shadow Ball L41→L27, Pain Split L32→L29, Grudge L50→L35, Perish Song L46→L43, Power Gem L55→L46 |
| Girafarig | Odor Sleuth L4, Bite L8, Zen Headbutt L27, Work Up L29, Baton Pass L33, Tri Attack L40, Body Slam L42, Skill Swap L48 | Psybeam L19→L15, Double Hit L28→L24, Crunch L37→L32, Psychic L50→L38, Nasty Plot L46→L44 |
| Pineco | Harden L1, Pin Missile L7, Mega Drain L15, Steamroller L32 | Rapid Spin L17→L4, Bug Bite L9→L7, Bide L20→L14, Spikes L28→L27, Payback L31→L30 |
| Forretress | Harden L1, Pin Missile L1, Mega Drain L15, Steamroller L32, Spike Cannon L33, Iron Defense L39 | Rapid Spin L17→L1, Bide L20→L14, Spikes L28→L27, Payback L32→L30, Gyro Ball L46→L42, Double-Edge L50→L46 |
| Dunsparce | Tackle L1, Headbutt L10, Endeavor L44 | Rollout L3→L1, Spite L6→L4, Pursuit L8→L6, Yawn L16→L14, Dig L33→L15, Take Down L28→L20, Roost L26→L22, Glare L36→L25, Endure L48→L37, Flail L51→L39 |
| Gligar | Sand Attack L1, Sand Tomb L10, Mud-Slap L16, Wing Attack L18, Air Cutter L24, Screech L24 | Harden L7→L3, Quick Attack L13→L6, Fury Cutter L16→L14, Earthquake L60→L36, Sky Uppercut L45→L38 |
| Steelix | Bulldoze L18 | Rock Slide L34→L1, Rock Throw L7→L4, Rage L13→L6, Slam L28→L13, Stealth Rock L16→L15, Dig L43→L18, Screech L31→L30, Stone Edge L46→L43, Earthquake L54→L45, Double-Edge L49→L46 |
| Snubbull | Lick L10, Double Slap L14, Heal Bell L31, Take Down L32, Super Fang L34, Thrash L44, Double-Edge L47 | Roar L25→L16, Rage L31→L21, Crunch L49→L39 |
| Granbull | Lick L10, Double Slap L14, Heal Bell L31, Take Down L32, Super Fang L34, Thrash L44, Double-Edge L47 | Roar L27→L16, Rage L30→L21, Crunch L59→L39 |
| Qwilfish | Minimize L5, Poison Tail L16, Sludge L20, Brine L28, Bubblebeam L30, Protect L32, Toxic L36, Sludge Bomb L45 | Bubble L13→L1, Harden L9→L5, Revenge L29→L21, Pin Missile L37→L26, Poison Jab L49→L31, Aqua Tail L45→L36 |
| Scizor | Cut L15, Double Team L24, Steel Wing L35, Twineedle L42, Swords Dance L55 | Fury Cutter L25→L1, Razor Wind L33→L1, Pursuit L9→L8, False Swipe L13→L11, Slash L29→L28, Iron Defense L37→L31, X-Scissor L41→L40, Night Slash L45→L44, Double Hit L49→L48 |
| Shuckle | Acid L1, Knock Off L1, Stealth Rock L1, Infestation L12, Defense Curl L18, Sandstorm L24, Acid Armor L31, Protect L35 | Shell Smash L34→L1, Rock Throw L23→L3, Gastro Acid L27→L6, Wrap L9→L7, Encore L36→L13, Safeguard L16→L15, Rock Slide L38→L30, Bug Bite L42→L39, Stone Edge L49→L45 |
| Heracross | Spike Cannon L1, Struggle Bug L1, Work Up L6, Twineedle L34, Cross Chop L38 | Pin Missile L31→L5, Fury Attack L25→L15, Reversal L46→L41 |
| Sneasel | Pursuit L4, Knock Off L12, Assurance L15, Ice Punch L33, Night Slash L39, Icicle Crash L48, Blizzard L50 | Quick Attack L8→L6, Icy Wind L14→L9, Fury Swipes L16→L13, Agility L20→L18, Metal Claw L22→L20, Slash L35→L22, Ice Shard L47→L23, Screech L32→L30 |
| Teddiursa | Sweet Scent L11, Metal Claw L15, Headbutt L24, Captivate L28, Submission L44, Play Rough L50, Yawn L53 | Fury Swipes L8→L6, Rest L43→L29, Snore L43→L34, Charm L36→L35, Thrash L50→L42 |
| Ursaring | Submission L1, Sweet Scent L11, Metal Claw L15, Circle Throw L24, Focus Energy L28, Snore L34, Play Rough L50, Yawn L53, Giga Impact L57 | Fury Swipes L8→L6, Rest L38→L29 |
| Slugma | Flame Wheel L21, Rock Blast L27, Rock Slide L31, Fire Blast L48 | Harden L13→L1, Rock Throw L8→L7, Incinerate L15→L14, Clear Smog L20→L17, Ancient Power L22→L20, Amnesia L36→L22, Body Slam L41→L28, Flamethrower L48→L34, Earth Power L50→L45 |
| Magcargo | Inferno L1, Flame Wheel L21, Rock Blast L27, Rock Slide L31, Fire Blast L48, Earthquake L50 | Harden L13→L1, Incinerate L15→L14, Clear Smog L20→L17, Ancient Power L22→L20, Amnesia L36→L22, Body Slam L43→L28, Flamethrower L54→L34 |
| Swinub | Powder Snow L6, Dig L35 | Mud Sport L5→L3, Mud-Slap L11→L8, Endure L14→L12, Icy Wind L21→L16, Take Down L28→L26, Mist L35→L34, Amnesia L48→L45 |
| Piloswine | Mud Shot L22, Dig L35, Blizzard L50 | Mud-Slap L11→L1, Endure L14→L12, Icy Wind L21→L16, Take Down L28→L26, Mist L37→L34, Earthquake L46→L39, Thrash L41→L40, Icicle Crash L52→L44, Amnesia L58→L45 |
| Corsola | Growth L1, Rock Throw L9, Water Gun L13, Spikes L22, Hydro Pump L43 | Bubble L4→L1, Refresh L13→L7, Lucky Chant L23→L12, Brine L27→L26, Power Gem L41→L31, Aqua Ring L38→L35 |
| Remoraid | Swift L5, Simple Beam L28, Seed Bomb L30, Scald L36, Sludge Bomb L41 | Lock-On L6→L1, Psybeam L10→L8, Bubble Beam L18→L11, Bullet Seed L38→L14, Focus Energy L22→L20, Water Pulse L26→L22, Ice Beam L34→L33 |
| Octillery | Zap Cannon L1, Lock-On L1, Water Pulse L22, Seed Bomb L30, Scald L36, Sludge Bomb L41, Hyper Beam L48, Egg Bomb L53 | Bubble Beam L18→L11, Bullet Seed L46→L14, Focus Energy L22→L20, Ice Beam L40→L33, Signal Beam L34→L33, Hydro Pump L52→L44, Soak L64→L50 |
| Mantine | Gust L1, Scald L33, Mirror Coat L45, Hurricane L52 | Headbutt L16→L7, Water Pulse L19→L18, Wide Guard L23→L21, Take Down L27→L24, Air Slash L36→L28, Aqua Ring L39→L38, Bounce L46→L41, Hydro Pump L49→L45 |
| Skarmory | Whirlwind L1, Sand Attack L8, Spikes L17, Wing Attack L28, Drill Peck L38, Iron Head L50, Iron Defense L52, Defog L55, Brave Bird L59 | Swift L23→L12, Fury Attack L17→L12, Feint L20→L17, Metal Sound L42→L19, Steel Wing L34→L26, Slash L39→L35, Night Slash L53→L43 |
| Houndour | Smog L7, Odor Sleuth L15, Fire Fang L18, Torment L20, Flame Wheel L22, Flame Burst L26, Feint Attack L29, Destiny Bond L56 | Roar L13→L7, Bite L15→L12, Embargo L33→L31, Crunch L49→L35, Flamethrower L44→L38, Nasty Plot L52→L45, Inferno L56→L52 |
| Houndoom | Beat Up L1, Fire Fang L18, Torment L20, Flame Wheel L22, Feint Attack L29, Destiny Bond L56 | Roar L13→L1, Bite L15→L1, Odor Sleuth L20→L15, Embargo L39→L31, Flamethrower L50→L38 |
| Kingdra | Aurora Beam L24, Dragon Breath L28, Flail L38, Body Slam L47, Outrage L56 | Twister L17→L14, Agility L38→L26, Dragon Dance L58→L50 |
| Phanpy | Mud-Slap L5, Mud Sport L7, Natural Gift L12, Bulldoze L27, Knock Off L36, Earthquake L40, Curse L52 | Magnitude L15→L14 |
| Donphan | Mud-Slap L1, Odor Sleuth L1, Magnitude L14, Endure L19, Flail L23, Take Down L25, Body Slam L30, Superpower L44, Double-Edge L48, Curse L52 | Assurance L15→L12, Scary Face L37→L33, Earthquake L43→L40 |
| Porygon2 | Sharpen L1, Curse L1, Imprison L1, Swift L10, Electroweb L18, Psyshock L44 | Psybeam L7→L4, Agility L12→L7, Recover L18→L14, Magnet Rise L23→L21, Signal Beam L29→L24, Recycle L34→L28, Discharge L40→L31, Tri Attack L50→L38, Lock-On L45→L41, Hyper Beam L67→L50 |
| Stantler | Role Play L1, Sand Attack L14, Pursuit L17, Reflect L33, Light Screen L33, Rock Climb L35, Double-Edge L40, Dream Eater L45 | Astonish L7→L6, Hypnosis L10→L9, Stomp L13→L12, Confuse Ray L23→L18, Captivate L50→L20, Zen Headbutt L38→L31, Jump Kick L43→L41, Imprison L49→L46 |
| Hitmontop | Fake Out L1, Helping Hand L1, Foresight L1, Low Kick L9, Low Sweep L15, Seismic Toss L22, Storm Throw L28, Dig L29, Gyro Ball L33, Dynamic Punch L36, Iron Tail L51 | Focus Energy L6→L1, Quick Attack L15→L12, Rapid Spin L19→L18, Agility L37→L30, Wide Guard L46→L39, Quick Guard L46→L39, Triple Kick L55→L45 |
| Smoochum | Powder Snow L1, Heart Stamp L10, Double Slap L13, Frost Breath L28, Ice Punch L30, Ice Beam L41, Nasty Plot L46 | Lick L5→L1, Sweet Kiss L8→L7 |
| Elekid | Spark L17, Work Up L21, Mega Punch L32, Electric Terrain L44, Cross Chop L48 | Thundershock L5→L1, Low Kick L8→L6, Shock Wave L15→L9, Thunder Wave L19→L16, Electro Ball L22→L19, Thunder Punch L29→L25 |
| Magby | Smokescreen L6, Flame Wheel L17, Work Up L21, Poison Gas L25, Will-O-Wisp L28, Mega Punch L32, Dark Pulse L48 | Ember L5→L1, Fire Spin L15→L9, Clear Smog L19→L16, Flame Burst L22→L19, Fire Punch L29→L25 |
| Miltank | Block L1, Iron Head L1, Helping Hand L1, Work Up L1, Refresh L1, Mega Punch L22, Flail L45, Play Rough L50, Double-Edge L55, Last Resort L60 | Growl L3→L1, Defense Curl L5→L4, Stomp L8→L7, Rollout L19→L15, Captivate L35→L25, Wake-Up Slap L50→L29, Heal Bell L48→L40 |
| Raikou | Aura Sphere L1, Charge L12, Extreme Speed L30, Thunderbolt L31, Rain Dance L54, Mind Reader L74, Zap Cannon L80 | Roar L15→L1, Thunder Shock L8→L1, Quick Attack L22→L6, Spark L29→L11, Thunder Fang L50→L18, Reflect L36→L24, Crunch L43→L41, Thunder L85→L60, Calm Mind L78→L68 |
| Entei | Flame Wheel L11, Curse L11, Light Screen L24, Crunch L41, Sunny Day L54, Flare Blitz L60 | Roar L15→L1, Ember L8→L1, Stomp L29→L6, Fire Fang L50→L18, Flamethrower L36→L31, Fire Blast L71→L61, Calm Mind L78→L68 |
| Suicune | Air Slash L1, Whirlpool L1, Aqua Ring L1, Extreme Speed L30, Surf L36, Reflect L41, Light Screen L51, Sheer Cold L80 | Mist L36→L1, Gust L22→L6, Extrasensory L64→L51, Hydro Pump L71→L61, Calm Mind L78→L68 |
| Larvitar | Rock Throw L8, Smack Down L13, Bulldoze L25, Dragon Claw L56 | Screech L10→L9, Payback L37→L21, Thrash L28→L26, Stone Edge L50→L43 |
| Pupitar | Rock Throw L1, Smack Down L13, Bulldoze L25, Dragon Claw L56 | Payback L41→L21, Thrash L28→L26, Stone Edge L60→L43, Earthquake L54→L47, Hyper Beam L67→L61 |
| Tyranitar | Rock Throw L1, Smack Down L13, Bulldoze L25, Dragon Claw L56, Hyper Beam L61 | Payback L41→L21, Thrash L28→L26, Stone Edge L63→L43, Earthquake L54→L47, Giga Impact L82→L67 |
| Lugia | Feather Dance L1, Aqua Tail L1, Defog L1, Whirlpool L10, Future Sight L60, Psycho Boost L66, Tailwind L75 | Gust L9→L1, Safeguard L29→L5, Natural Gift L43→L15, Extrasensory L65→L20, Recover L79→L22, Hydro Pump L57→L35, Aeroblast L71→L40, Ancientpower L85→L44, Calm Mind L93→L65, Sky Attack L99→L70 |
| Ho-Oh | Heat Wave L1, Defog L1, Feather Dance L1, Fire Blast L25, Future Sight L70, Tailwind L75 | Gust L23→L1, Safeguard L43→L5, Fire Spin L15→L10, Natural Gift L29→L15, Extrasensory L57→L20, Recover L65→L22, Sacred Fire L71→L40, Ancientpower L79→L44, Sky Attack L99→L60, Calm Mind L93→L65 |
| Celebi | Helping Hand L1, Mega Drain L20, Zen Headbutt L25, Psybeam L30, Giga Drain L35, Psychic L40, Nasty Plot L60, Earth Power L65 | Heal Block L55→L1, Natural Gift L46→L1, Safeguard L10→L5, Magical Leaf L19→L10, Ancient Power L28→L15, Healing Wish L73→L30, Future Sight L64→L45, Perish Song L91→L50, Leaf Storm L82→L55 |
| Igglybuff | Fairy Wind L7, Double Slap L14, Round L14, Perish Song L25 | Pound L5→L1 |
| Treecko | False Swipe L13, Astonish L16, Growth L18, Dragon Breath L21, Chip Away L29, Fling L41, Solar Beam L46 | Quick Attack L9→L7, Pursuit L17→L10, Energy Ball L37→L33, Endeavor L45→L36 |
| Grovyle | Razor Leaf L15, Growth L18, Dragon Breath L21, Leaf Tornado L24, Focus Energy L26, Slash L29, Dual Chop L36, Extreme Speed L41, Dragon Pulse L54 | Pursuit L18→L10, X-Scissor L43→L41, Leaf Storm L58→L46, Quick Guard L53→L48 |
| Sceptile | Extreme Speed L1, Fake Out L5, Vine Whip L10, Razor Leaf L15, Astonish L16, Growth L18, Dragon Breath L21, Leaf Tornado L24, Focus Energy L26, Slash L29, Dragon Claw L48, Solar Beam L51, Dragon Pulse L54 | Pursuit L18→L10, Detect L39→L38, Quick Guard L57→L48 |
| Torchic | Sand Attack L10, Flame Charge L18, Feather Dance L34, Bounce L44, Overheat L48 | Peck L14→L6, Mirror Move L41→L28, Flamethrower L46→L38 |
| Combusken | Sand Attack L10, Fire Punch L23, Rolling Kick L25, Mach Punch L32, Bounce L44, Overheat L48, High Jump Kick L51, Brave Bird L55 | Peck L14→L7, Flame Charge L20→L18, Mirror Move L47→L28, Sky Uppercut L53→L38 |
| Blaziken | Mach Punch L1, Sand Attack L10, Rolling Kick L25, Mirror Move L28, Bounce L44, Overheat L48 | Thunder Punch L25→L1, Peck L14→L1, Flame Charge L20→L18, Sky Uppercut L47→L38 |
| Mudkip | Foresight L10, Mud Shot L13, Bubble Beam L16, Mud Bomb L23, Aqua Tail L38, Double-Edge L43 | Mud Sport L20→L18, Take Down L36→L26, Whirlpool L33→L28 |
| Marshtomp | Bubble Beam L16, Mud Sport L18, Mud Bomb L23, Dive L28, Hydro Pump L50 | Take Down L42→L26, Earthquake L48→L43, Endeavor L52→L46 |
| Swampert | Earth Power L1, Bubble Beam L16, Mud Sport L18, Dive L28, Endeavor L46, Hydro Pump L50 | Take Down L44→L26, Muddy Water L39→L36, Earthquake L51→L43 |
| Poochyena | Sand Attack L7, Pursuit L8, Thief L15, Super Fang L39, Double-Edge L43, Torment L46 | Odor Sleuth L13→L1, Roar L16→L12, Embargo L28→L22, Take Down L40→L27 |
| Mightyena | Thief L15, Pursuit L18, Take Down L27, Super Fang L39, Double-Edge L43, Torment L46 | Odor Sleuth L13→L1, Roar L16→L12, Embargo L40→L22 |
| Zigzagoon | Sand Attack L7, Fury Swipes L18, Slash L31, Double-Edge L38, Play Rough L42 | Tail Whip L5→L4, Mud Sport L17→L16, Covet L23→L22, Fling L41→L24, Flail L29→L26, Rest L35→L32, Belly Drum L37→L35 |
| Linoone | Sand Attack L1, Pursuit L20, Pin Missile L29, Night Slash L46 | Mud Sport L17→L16, Fury Swipes L19→L18, Covet L24→L22, Fling L48→L24, Slash L32→L26, Rest L40→L32, Belly Drum L43→L35 |
| Silcoon | Tackle L1, String Shot L1, Poison Sting L5 |  |
| Beautifly | String Shot L1, Harden L1, Leech Life L10, Gust L10, Sleep Powder L12, Air Cutter L18, Silver Wind L25, Hurricane L43, Beat Up L45, Defog L47 | Rage L37→L1, Stun Spore L13→L12, Morning Sun L17→L16, Whirlwind L30→L26 |
| Cascoon | Tackle L1, Poison Sting L1, String Shot L1 |  |
| Dustox | Poison Sting L1, String Shot L1, Harden L1, Leech Life L10, Poison Powder L12, Hypnosis L20, Reflect L27, Signal Beam L43, Synchronoise L43, Imprison L45, Sticky Web L47, Psychic L48 | Silver Wind L25→L17, Venoshock L20→L18, Sludge Bomb L32→L30 |
| Lotad | Natural Gift L11, Seed Bomb L30, Worry Seed L32, Tickle L42, Hydro Pump L49 | Bubble L9→L1, Nature Power L24→L12, Bubble Beam L21→L17 |
| Lombre | Fury Swipes L11, Mega Drain L23, Rain Dance L27, Soak L32, Giga Drain L36, Tickle L42 | Bubble L9→L1, Growl L3→L1, Bubble Beam L24→L17, Uproar L32→L30 |
| Ludicolo | Water Gun L1, Bubble L1, Absorb L1, Natural Gift L11, Fury Swipes L14, Fake Out L14, Bubble Beam L17, Water Pulse L18, Petal Dance L26, Rain Dance L27, Water Sport L30, Soak L32, Giga Drain L36, Teeter Dance L38, Zen Headbutt L39, Knock Off L44, Hydro Pump L49 |  |
| Seedot | Tackle L1, Absorb L7, Bullet Seed L8, Leech Seed L14, Headbutt L17, Seed Bomb L30, Self-Destruct L36, Worry Seed L39, Torment L42, Solar Beam L44 | Nature Power L15→L11, Synthesis L21→L19 |
| Nuzleaf | Absorb L7, Knock Off L18, Feint Attack L20, Leaf Tornado L23, Synthesis L26, Sunny Day L27, Leaf Storm L44 | Razor Wind L20→L1, Harden L3→L1 |
| Shiftry | Razor Wind L1, Assurance L1, Absorb L1, Defog L11, Knock Off L18, Torment L25, Synthesis L26, Sunny Day L27, Faint Attack L30, Tailwind L32, Leaf Blade L36, Swagger L37, Extrasensory L39 |  |
| Taillow | Double Team L15, Chip Away L22, Whirlwind L23, Tailwind L28, Air Slash L32, Hyper Voice L39 | Wing Attack L13→L12, Aerial Ace L21→L18 |
| Swellow | Sky Attack L1, Double Team L15, Chip Away L22, Whirlwind L23, Tailwind L28, Hyper Voice L39 | Wing Attack L13→L12, Aerial Ace L21→L18, Quick Guard L27→L25, Brave Bird L51→L48 |
| Wingull | Hydro Pump L42, Tailwind L44, Defog L47 | Mist L12→L11, Quick Attack L19→L18, Air Slash L40→L36 |
| Pelipper | Protect L1, Air Cutter L22, Feather Dance L25, Rain Dance L32, Air Slash L36 | Supersonic L5→L1, Mist L12→L11, Payback L19→L18, Stockpile L33→L25, Swallow L33→L25, Spit Up L33→L25, Hydro Pump L50→L47, Hurricane L55→L51 |
| Kirlia | Fairy Wind L1, Psybeam L18, Wish L42, Stored Power L53, Moonblast L58 | Magical Leaf L17→L1, Charm L40→L16, Imprison L33→L32 |
| Gardevoir | Fairy Wind L1, Lucky Chant L15, Charm L16, Psybeam L18, Psychic L36 | Magical Leaf L17→L1, Captivate L44→L23, Imprison L35→L32, Hypnosis L49→L47, Dream Eater L53→L49 |
| Surskit | Leech Life L5, Infestation L14, Bubble Beam L16, Baton Pass L33, Hydro Pump L37 | Aqua Jet L30→L26 |
| Masquerain | Leech Life L1, Gust L14, Silver Wind L27, Icy Wind L32, Signal Beam L47 |  |
| Shroomish | Synthesis L31 | Mega Drain L12→L11, Poison Powder L19→L18, Growth L29→L21, Toxic L33→L29, Seed Bomb L36→L34 |
| Breloom | Drain Punch L1, Bullet Seed L11, Brick Break L29, Worry Seed L42 | Feint L19→L18, Counter L22→L21, Force Palm L28→L26, Seed Bomb L44→L37, Dynamic Punch L50→L49, Spore L65→L52 |
| Slakoth | Fury Swipes L12, Mega Punch L31, Block L34, Knock Off L38 | Encore L6→L5, Slack Off L9→L8, Covet L22→L21, Chip Away L25→L24, Counter L30→L27 |
| Vigoroth | Yawn L1, Vital Throw L15, Faint Attack L22, Mega Punch L31, Retaliate L38 | Fury Swipes L14→L12, Slash L23→L21, Chip Away L27→L24, Counter L33→L27 |
| Nincada | Sand Attack L1, Silver Wind L28, X-Scissor L30 | Mud-Slap L17→L8, Fury Swipes L13→L11, Mind Reader L25→L15, Metal Claw L21→L18, Dig L37→L22, Bide L29→L27 |
| Ninjask | Gust L8, Silver Wind L28, U-turn L28, Air Cutter L34, Acrobatics L34, Metal Claw L38, Baton Pass L38, Night Slash L46, Quick Guard L50 | Fury Swipes L13→L9, Mind Reader L29→L15, X-Scissor L47→L42 |
| Shedinja | Sand Attack L1, Leech Life L1, Astonish L8, Gust L12, Silver Wind L23, X-Scissor L35, Faint Attack L38, Bug Buzz L44 | Fury Swipes L13→L9, Mind Reader L25→L15, Confuse Ray L29→L26, Shadow Ball L33→L29, Heal Block L41→L32 |
| Whismur | Work Up L22, Flail L29, Boomburst L44, Endeavor L49 | Astonish L8→L1, Howl L11→L6, Supersonic L18→L11, Stomp L22→L18, Roar L29→L26, Hyper Voice L39→L29, Synchronoise L43→L39 |
| Loudred | Work Up L22, Crunch L35, Boomburst L44, Outrage L49, Hyper Beam L50 | Echoed Voice L4→L1, Supersonic L18→L11, Stomp L23→L18, Roar L32→L26, Synchronoise L40→L39 |
| Exploud | Work Up L22, Outrage L49 | Supersonic L18→L11, Stomp L23→L18, Roar L32→L26, Synchronoise L44→L39 |
| Makuhita | Sand Attack L3, Brick Break L30, Body Slam L32, Fling L35, Superpower L38 | Seismic Toss L31→L1, Arm Thrust L7→L5, Fake Out L10→L8, Force Palm L13→L12, Whirlwind L16→L14, Smelling Salts L28→L20, Wake-Up Slap L34→L24, Heavy Slam L46→L41 |
| Hariyama | Bulk Up L1, Brick Break L30, Body Slam L32, Fling L35, Superpower L38, Focus Punch L51 | Seismic Toss L34→L1, Close Combat L46→L1, Fake Out L10→L8, Force Palm L13→L12, Whirlwind L16→L14, Smelling Salts L30→L20, Wake-Up Slap L38→L24, Heavy Slam L54→L41, Reversal L50→L43 |
| Nosepass | Rock Throw L9, Headbutt L11, Shock Wave L17, Ancient Power L20, Spark L22, Smelling Salts L26, Iron Defense L34, Tri Attack L39, Thunderbolt L40, Sleep Talk L45 | Harden L4→L1, Block L7→L5, Sandstorm L34→L33 |
| Skitty | Fury Swipes L9, Double Slap L11, Take Down L23, Encore L32, Hyper Voice L34, Moonblast L42, Mimic L43, Wish L47 | Attract L10→L3, Copycat L19→L6, Covet L34→L11, Assist L31→L16, Wake-Up Slap L28→L20, Charm L25→L23, Play Rough L46→L30 |
| Delcatty | Tackle L1, Tail Whip L1, Helping Hand L1, Follow Me L1, Growl L1, Copycat L6, Fury Swipes L9, Covet L11, Assist L16, Take Down L19, Wake-Up Slap L20, Charm L23, Faint Attack L26, Play Rough L30, Encore L32, Heal Bell L37, Double-Edge L41, Moonblast L42, Mimic L43, Captivate L44, Wish L47 | Hyper Voice L55→L34 |
| Sableye | Taunt L9, Bite L12, Shadow Punch L24, Crunch L27, Pain Split L31, Parting Shot L41, Sucker Punch L45 | Foresight L4→L1, Punishment L24→L1, Quash L44→L1, Astonish L9→L3, Fury Swipes L11→L5, Shadow Sneak L16→L14, Fake Out L21→L17, Knock Off L26→L21, Shadow Claw L29→L24, Confuse Ray L31→L26, Shadow Ball L39→L36 |
| Mawile | Sweet Scent L1, Double Slap L12, Vice Grip L16, Baton Pass L29, Meteor Mash L45, Metal Burst L47, Swords Dance L53 | Swallow L41→L1, Spit Up L41→L1, Fake Tears L5→L3, Bite L9→L6, Iron Defense L33→L27 |
| Aron | Rock Throw L9, Rock Blast L23, Submission L42, Earthquake L51, Head Smash L56 | Iron Defense L37→L15, Roar L19→L16, Take Down L28→L21, Metal Sound L31→L25 |
| Lairon | Rock Throw L9, Rock Blast L23, Submission L42, Earthquake L51, Head Smash L56 | Iron Defense L39→L15, Roar L19→L16, Take Down L28→L21, Metal Sound L31→L25, Double-Edge L43→L41, Autotomize L47→L44, Heavy Slam L51→L47 |
| Aggron | Submission L1, Rock Throw L9, Rock Blast L23, Earthquake L51, Head Smash L56 | Iron Defense L39→L15, Roar L19→L16, Take Down L28→L21, Metal Sound L31→L25, Double-Edge L45→L41, Autotomize L51→L44, Heavy Slam L57→L47, Metal Burst L63→L60 |
| Meditite | Karate Chop L13, Jump Kick L22, Rolling Kick L23, Extrasensory L29, Drain Punch L32, Acupressure L34, Zen Headbutt L44 | Detect L9→L1, Endure L12→L10, Force Palm L15→L12, Feint L17→L15, Psych Up L31→L20, Reversal L39→L38 |
| Medicham | Karate Chop L14, Jump Kick L22, Rolling Kick L23, Extrasensory L29, Drain Punch L32, Acupressure L34 | Endure L12→L10, Force Palm L17→L12, Psych Up L31→L20, Reversal L42→L38 |
| Electrike | Thunder Shock L7, Shock Wave L17, Electric Terrain L29, Snarl L32, Thunderbolt L36, Crunch L40, Rain Dance L46 | Roar L34→L1, Bite L24→L20, Charge L44→L31 |
| Manectric | Thunder Shock L1, Flamethrower L1, Shock Wave L17, Snarl L32, Thunderbolt L36, Crunch L40, Rain Dance L46 | Roar L36→L1, Bite L24→L20, Charge L48→L31, Thunder L54→L50 |
| Plusle | Thunder Shock L1, Magnetic Flux L1, Quick Guard L1, Fake Tears L21, Thunderbolt L28, Fake Out L30, Extreme Speed L37, Baton Pass L40, Volt Tackle L48 | Swift L16→L14, Discharge L31→L26, Agility L37→L33 |
| Minun | Thunder Shock L1, Wide Guard L1, Shock Wave L10, Follow Me L16, Charm L25, Thunderbolt L28, Magnetic Flux L28, Trick L34, Wish L37, Baton Pass L40, Volt Tackle L48 | Charge L28→L1, Swift L16→L14, Discharge L31→L26, Agility L37→L33 |
| Volbeat | Captivate L1, Double Team L6, Leech Life L10, Silver Wind L23, Protect L26, Baton Pass L29, Zen Headbutt L32, U-turn L35, Light Screen L41, Moonblast L45 | Struggle Bug L15→L12, Tail Glow L36→L19, Signal Beam L26→L24 |
| Illumise | Leech Life L10, Struggle Bug L12, Follow Me L16, Silver Wind L23, Signal Beam L24, Extrasensory L32, U-turn L35, Bug Buzz L40, Reflect L41, Moonblast L45 | Flatter L29→L1, Charm L9→L6, Wish L21→L19, Helping Hand L36→L32 |
| Roselia | Sweet Scent L1, Magical Leaf L21, Venoshock L25, Solar Beam L50 | Aromatherapy L43→L22, Ingrain L34→L33, Toxic L40→L37, Petal Dance L50→L40 |
| Gulpin | Body Slam L26, Recover L38 | Yawn L5→L4, Poison Gas L8→L6, Encore L20→L16, Gastro Acid L36→L18, Toxic L25→L24, Gunk Shot L49→L43 |
| Swalot | Recover L38 | Encore L20→L16, Gastro Acid L36→L18, Toxic L25→L24 |
| Carvanha | Water Pulse L18, Dive L28, Slash L30, Taunt L34, Skull Bash L42, Hydro Pump L46 | Poison Fang L28→L26 |
| Sharpedo | Water Pulse L18, Dive L28, Hydro Pump L46 | Poison Fang L34→L26, Taunt L56→L34, Skull Bash L51→L41 |
| Wailmer | Tackle L1, Yawn L21, Body Slam L29, Curse L45, Wide Guard L51 | Growl L4→L3, Water Gun L7→L5, Rollout L10→L8, Whirlpool L13→L11, Astonish L16→L13, Mist L22→L16, Rest L29→L24, Water Spout L33→L32, Bounce L45→L35, Dive L41→L40, Heavy Slam L53→L42 |
| Wailord | Double-Edge L1, Tackle L1, Yawn L21, Body Slam L29, Curse L45, Wide Guard L51 | Whirlpool L13→L11, Astonish L16→L13, Mist L22→L16, Rest L29→L24, Water Spout L33→L32, Bounce L51→L35, Dive L44→L40, Hydro Pump L58→L48 |
| Numel | Mud-Slap L1, Flame Wheel L17, Rock Slide L32, Eruption L45 | Ember L5→L4, Focus Energy L8→L7, Flame Burst L15→L14, Amnesia L19→L17, Take Down L31→L20, Flamethrower L43→L36, Double-Edge L47→L46 |
| Camerupt | Mud-Slap L1, Heat Wave L1, Flame Wheel L17, Flamethrower L36, Double-Edge L46 | Flame Burst L15→L14, Amnesia L19→L17, Take Down L31→L20, Earthquake L46→L40 |
| Torkoal | Smokescreen L1, Clear Smog L14, Yawn L18, Sunny Day L24, Slack Off L33, Heat Crash L46, Overheat L50 | Withdraw L7→L1, Smog L4→L1, Rapid Spin L10→L1, Fire Spin L13→L6, Flame Wheel L18→L17, Body Slam L27→L25, Heat Wave L45→L30, Amnesia L40→L37 |
| Spoink | Tackle L1, Confusion L8, Extrasensory L21, Barrier L23, Sleep Talk L32, Yawn L42, Skill Swap L48 | Psywave L7→L5, Odor Sleuth L10→L7, Psych Up L15→L10, Psybeam L14→L13, Confuse Ray L18→L15, Magic Coat L21→L18, Payback L40→L26, Psyshock L38→L29, Psychic L44→L38, Bounce L50→L40 |
| Grumpig | Headbutt L1, Tackle L1, Confusion L8, Extrasensory L21, Barrier L23, Sleep Talk L32, Yawn L42, Skill Swap L48 | Snore L35→L1, Slack Off L65→L1, Psych Up L15→L10, Confuse Ray L18→L15, Magic Coat L21→L18, Payback L46→L26, Psyshock L42→L29, Rest L35→L32, Psychic L52→L36, Bounce L60→L40 |
| Spinda | Petal Dance L1, Role Play L1, Assist L1, Rapid Spin L1, Play Rough L33, Outrage L39, Dynamic Punch L45 | Copycat L5→L4, Psybeam L14→L13, Hypnosis L19→L16, Dizzy Punch L23→L20, Sucker Punch L28→L23, Teeter Dance L32→L25, Psych Up L41→L27, Thrash L55→L30, Flail L50→L36, Double-Edge L46→L42 |
| Trapinch | Sand Attack L1, Hyper Fang L33, Magnitude L38, Block L39, Screech L43, Bug Bite L43 | Mud-Slap L5→L4, Sandstorm L36→L15 |
| Vibrava | Bite L1, Uproar L20, Crunch L25, Dig L27, Signal Beam L33, Dragon Dance L39, Dragon Rush L55 | Supersonic L19→L1, Sandstorm L36→L15 |
| Flygon | Superpower L1, Bite L1, Crunch L25, Dig L27, Signal Beam L33, Bug Buzz L44, Boomburst L59 | Sandstorm L36→L1, Supersonic L19→L1, Dragon Tail L29→L20, Dragon Dance L60→L39 |
| Cacnea | Sand Attack L7, Pursuit L7, Seed Bomb L24, Giga Drain L34, Dark Pulse L37, Energy Ball L45 | Absorb L4→L1, Growth L7→L4, Needle Arm L42→L14, Ingrain L22→L21, Sucker Punch L32→L27, Spikes L30→L28, Cotton Spore L46→L39, Sandstorm L50→L47, Destiny Bond L54→L48 |
| Cacturne | Spike Cannon L1, Sand Attack L7, Pursuit L7, Seed Bomb L24, Giga Drain L34, Dark Pulse L37, Energy Ball L45 | Needle Arm L41→L14, Ingrain L22→L21, Sucker Punch L34→L27, Spikes L30→L28, Cotton Spore L49→L39, Sandstorm L54→L45 |
| Swablu | Refresh L11, Air Cutter L13, Feather Dance L28, Heal Bell L29, Hyper Voice L33, Sky Attack L45 | Astonish L3→L1, Sing L5→L3, Fury Attack L7→L5, Safeguard L9→L7, Round L17→L16, Take Down L23→L19 |
| Altaria | Dragon Rush L1, Air Cutter L13, Feather Dance L28, Heal Bell L29, Hyper Voice L33 | Fury Attack L7→L5, Safeguard L9→L7, Refresh L26→L11, Round L17→L16, Take Down L23→L19 |
| Zangoose | Metal Claw L24, Feint Attack L34, Double-Edge L40 | False Swipe L29→L1, Pursuit L12→L11, Swords Dance L47→L32 |
| Seviper | Poison Sting L1, Revenge L25, Super Fang L32, Iron Tail L43, Sucker Punch L48 | Lick L6→L3, Haze L34→L5, Poison Fang L21→L10, Screech L14→L12, Glare L19→L17, Coil L44→L23, Poison Jab L31→L30, Crunch L39→L37, Gunk Shot L53→L40 |
| Lunatone | Psywave L1, Icy Wind L12, Calm Mind L21, Ancient Power L28, Heal Block L30, Moonlight L34, Baton Pass L43, Ice Beam L46 |  |
| Solrock | Will-O-Wisp L9, Flame Charge L12, Rock Tomb L19, Curse L21, Psybeam L25, Ancient Power L29, Zen Headbutt L33, Morning Sun L34, Rock Blast L38, Baton Pass L43 | Psywave L13→L1, Heal Block L33→L30 |
| Barboach | Yawn L14, Zen Headbutt L29, Aqua Tail L32, Earth Power L36 | Mud Sport L6→L5, Water Sport L6→L5, Water Gun L9→L8, Mud Bomb L13→L12, Magnitude L20→L13, Muddy Water L35→L29 |
| Whiscash | Yawn L14, Sleep Talk L26, Aqua Tail L32, Earth Power L36 | Mud Bomb L13→L12, Magnitude L20→L13, Muddy Water L39→L29, Future Sight L45→L39 |
| Corphish | Assurance L15, Metal Claw L24 | Taunt L34→L31 |
| Crawdaunt | Assurance L15, Metal Claw L24 | Taunt L36→L31, Crabhammer L48→L36, Crunch L43→L39 |
| Baltoy | Smokescreen L3, Mud-Slap L5, Stealth Rock L8, Psychic L36, Zen Headbutt L41, Earthquake L42, Hyper Beam L48, Recover L53 | Heal Block L10→L1, Rapid Spin L4→L3, Psybeam L16→L11, Self-Destruct L28→L17, Extrasensory L31→L27, Sandstorm L40→L30, Earth Power L37→L33 |
| Claydol | Gravity L1, Smokescreen L3, Mud-Slap L5, Stealth Rock L8, Psychic L36, Zen Headbutt L41, Earthquake L42, Imprison L46, Recover L53 | Heal Block L10→L1, Psybeam L16→L11, Self-Destruct L28→L17, Extrasensory L31→L27, Sandstorm L46→L30, Earth Power L40→L33 |
| Lileep | Rock Throw L7, Mega Drain L12, Rock Blast L33, Stealth Rock L38, Recover L44 | Acid L5→L4, Brine L21→L20, Gastro Acid L31→L22, Stockpile L46→L30, Swallow L46→L30, Spit Up L46→L30, Wring Out L52→L50 |
| Cradily | Rock Throw L1, Leech Seed L1, Mega Drain L12, Rock Blast L33, Stealth Rock L38, Recover L44 | Brine L21→L20, Gastro Acid L31→L22, Energy Ball L44→L42 |
| Anorith | Water Gun L6, Smack Down L8, Rock Throw L15, Hone Claws L25, Twineedle L36, Stone Edge L45, Swords Dance L50 | Mud Sport L4→L1, Metal Claw L17→L14, Ancient Power L21→L17, Brine L29→L20, Bug Bite L25→L23, Crush Claw L36→L28, Rock Blast L45→L32 |
| Armaldo | Iron Tail L1, Smack Down L8, Rock Throw L15, Hone Claws L25, Twineedle L36, Aqua Tail L41, Stone Edge L45, Swords Dance L50 | Metal Claw L17→L14, Ancient Power L21→L17, Brine L29→L20, Bug Bite L25→L23, Rock Blast L48→L32 |
| Milotic | Sing L1, Whirlpool L10, Dragon Breath L30, Dazzling Gleam L37, Light Screen L40, Dragon Pulse L46, Mirror Coat L50 | Attract L34→L1, Water Sport L4→L1, Refresh L7→L4, Safeguard L37→L5, Twister L14→L7, Recover L27→L25, Coil L41→L34 |
| Castform | Water Pulse L10, Flame Wheel L10, Aurora Beam L10, Incinerate L10, Icy Wind L10, Secret Power L15, Muddy Water L30, Heat Wave L30, Freeze-Dry L30, Tri Attack L35 | Water Gun L10→L1, Ember L10→L1, Powder Snow L10→L1, Headbutt L15→L5 |
| Kecleon | Fake Out L1, Swift L20, Swagger L22, Psychic L37, Double-Edge L44 | Feint L10→L7, Psybeam L18→L16, Camouflage L30→L27, Substitute L42→L30, Shadow Claw L33→L32, Sucker Punch L46→L40 |
| Shuppet | Lick L1, Astonish L14, Revenge L25, Substitute L34, Destiny Bond L56 | Screech L4→L3, Spite L10→L9, Shadow Sneak L13→L12, Curse L26→L17, Snatch L42→L41, Grudge L46→L44, Phantom Force L54→L48 |
| Banette | Lick L1, Play Rough L1, Astonish L14, Revenge L25, Substitute L34, Shadow Claw L37, Destiny Bond L50, Trick L51 | Shadow Sneak L13→L12, Snatch L46→L41, Grudge L52→L44 |
| Duskull | Hypnosis L31, Shadow Punch L32, Pain Split L37, Snatch L37, Sucker Punch L44, Phantom Force L53 | Disable L6→L4, Astonish L9→L6, Foresight L14→L8, Pursuit L22→L11, Shadow Sneak L17→L14, Will-O-Wisp L25→L18, Hex L38→L21, Payback L49→L26, Curse L33→L28, Mean Look L46→L34, Shadow Ball L41→L40, Future Sight L54→L48 |
| Dusclops | Hypnosis L31, Pain Split L37, Snatch L37, Sucker Punch L44, Phantom Force L53 | Foresight L14→L8, Pursuit L22→L11, Shadow Sneak L17→L14, Will-O-Wisp L25→L18, Hex L40→L21, Payback L57→L26, Curse L33→L28, Mean Look L52→L34, Shadow Ball L45→L40 |
| Tropius | Outrage L1, Air Cutter L18, Sunny Day L23, Defog L43 | Sweet Scent L6→L5, Stomp L10→L9, Whirlwind L21→L11, Magical Leaf L16→L14, Air Slash L33→L32, Body Slam L37→L35, Solar Beam L48→L38 |
| Chimecho | Follow Me L1, Helping Hand L1, Recover L1, Echoed Voice L6, Psyshock L20, Psychic L38, Wish L38, Magic Room L44, Hyper Voice L47 | Psywave L16→L1, Uproar L32→L10, Yawn L13→L11, Take Down L19→L16, Heal Bell L27→L22, Heal Pulse L47→L27, Safeguard L37→L32 |
| Absol | Double Team L20, Air Cutter L26, Crunch L40, Air Slash L44 | Leer L4→L1, Pursuit L10→L7, Future Sight L53→L26, Psycho Cut L36→L35, Sucker Punch L44→L41, Perish Song L57→L45 |
| Snorunt | Fake Tears L23, Icicle Spear L24, Ice Beam L37, Body Slam L40, Endeavor L43 | Ice Shard L10→L7, Headbutt L28→L18, Ice Fang L23→L21, Frost Breath L37→L26, Crunch L41→L30 |
| Glalie | Ice Ball L1, Super Fang L1, Scary Face L23, Icicle Spear L24, Icicle Crash L37, Body Slam L40, Explosion L47, Wide Guard L49, Sheer Cold L51 | Ice Shard L10→L1, Headbutt L28→L18, Ice Fang L23→L21, Frost Breath L37→L26, Crunch L41→L30, Blizzard L48→L43 |
| Spheal | Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Slack Off L53 | Rollout L5→L4, Ice Ball L13→L11, Brine L17→L15, Body Slam L26→L16, Aurora Beam L21→L18, Rest L31→L25, Snore L31→L25 |
| Sealeo | Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Sheer Cold L50, Slack Off L53 | Rollout L5→L4, Ice Ball L13→L11, Brine L17→L15, Body Slam L26→L16, Aurora Beam L21→L18, Rest L31→L25, Snore L31→L25, Blizzard L45→L43 |
| Walrein | Icicle Spear L1, Super Fang L1, Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Sheer Cold L50, Slack Off L53 | Rollout L7→L4, Ice Ball L13→L11, Brine L19→L15, Body Slam L25→L16, Aurora Beam L19→L18, Rest L31→L25, Snore L31→L25, Blizzard L49→L43 |
| Huntail | Agility L1, Take Down L21, Dragon Dance L29, Baton Pass L40, Double-Edge L43, Hydro Pump L47 | Water Pulse L14→L9, Dive L26→L25, Coil L45→L30, Crunch L47→L35, Aqua Tail L39→L35, Shell Smash L57→L50 |
| Gorebyss | Captivate L5, Psybeam L27, Dazzling Gleam L32, Baton Pass L40, Double-Edge L43 | Agility L9→L1, Water Pulse L14→L9, Amnesia L16→L13, Dive L26→L25, Coil L45→L30, Aqua Tail L39→L35, Hydro Pump L50→L47, Shell Smash L57→L50 |
| Relicanth | Water Pulse L18, Sleep Talk L30, Rock Slide L37, Stealth Rock L46 | Mud Sport L6→L1, Rock Tomb L15→L10, Yawn L31→L13, Take Down L27→L22, Rest L41→L30, Double-Edge L50→L41 |
| Luvdisc | Rain Dance L23, Dive L31, Aqua Ring L39, Dazzling Gleam L47 | Sweet Kiss L31→L1, Agility L7→L3, Heart Stamp L22→L21, Lovely Kiss L40→L32, Safeguard L49→L39 |
| Bagon | Slam L13, Twister L15, Fire Fang L24, Thrash L47, Outrage L64 | Scary Face L39→L33, Zen Headbutt L34→L33 |
| Shelgon | Slam L13, Twister L15, Fire Fang L24, Thrash L47, Outrage L64 | Scary Face L42→L33, Zen Headbutt L35→L33 |
| Salamence | Slam L13, Twister L15, Thrash L47, Outrage L64 | Ember L4→L1, Scary Face L42→L33, Zen Headbutt L35→L33, Double-Edge L63→L61 |
| Metang | Psybeam L30, Gravity L34, Flash Cannon L37, Hammer Arm L49 | Pursuit L23→L22, Scary Face L35→L25, Iron Defense L47→L39 |
| Metagross | Thunder Punch L1, Ice Punch L1, Stealth Rock L1, Refresh L11, Psybeam L30, Gravity L34, Flash Cannon L37 | Pursuit L23→L22, Scary Face L35→L25, Iron Defense L52→L39 |
| Regirock | Gravity L1, Stealth Rock L1, Rapid Spin L1, Thunder Punch L10, Rock Blast L35, Recover L65 | Iron Defense L37→L25, Ancient Power L31→L25 |
| Regice | Gravity L1, Spikes L1, Rapid Spin L1, Shock Wave L10, Water Pulse L15, Ice Beam L35, Blizzard L45, Recover L65 | Amnesia L37→L25, Ancient Power L31→L25 |
| Registeel | Gravity L1, Autotomize L1, Seismic Toss L15, Meteor Mash L45, Heavy Slam L55, Recover L65 | Metal Claw L7→L5, Amnesia L37→L25, Iron Defense L37→L25, Ancient Power L31→L25, Flash Cannon L43→L35 |
| Kyogre | Ancient Power L1, Icy Wind L10, Aqua Tail L15, Surf L40, Calm Mind L45, Sheer Cold L70 | Avalanche L35→L1, Water Spout L82→L65 |
| Groudon | Iron Tail L1, Fire Punch L10, Earth Power L15, Stealth Rock L30, Flamethrower L45, Bulk Up L45, Solar Beam L50, Fire Blast L60 | Ancient Power L60→L1, Rest L30→L25, Eruption L75→L65 |
| Rayquaza | Earth Power L1, Sky Drop L10, Dragon Claw L20, Tailwind L30, Dragon Dance L45, Sky Attack L75 | Ancient Power L20→L1, Extreme Speed L50→L40, Dragon Pulse L65→L50 |
| Deoxys | Fire Punch L1, Thunder Punch L1, Ice Punch L1, Confusion L1, Drain Punch L30, Trick L65 | Night Shade L7→L5, Teleport L13→L10, Pursuit L19→L15, Snatch L37→L20, Zen Headbutt L49→L25, Cosmic Power L55→L35, Recover L61→L55, Psycho Boost L73→L60 |
| Kadabra | Telekinesis L30, Psyshock L36, Power Split L44, Trick L48 | Role Play L41→L38 |
| Alakazam | Telekinesis L30, Power Split L44, Trick L48 | Disable L18→L1, Calm Mind L54→L38 |
| Magikarp | Bounce L35 | Flail L30→L25 |
| Mewtwo | Metronome L1, Zen Headbutt L1, Drain Punch L1, Psybeam L7, Submission L31 | Swift L8→L1, Psych Up L36→L13, Power Swap L43→L37, Guard Swap L43→L37, Recover L50→L49, Barrier L64→L55, Aura Sphere L70→L67, Amnesia L79→L73, Mist L83→L79, Psystrike L86→L85, Me First L93→L91 |
| Pichu | Spark L11, Bestow L18, Electro Ball L22 | Tail Whip L5→L4, Thunder Wave L18→L8 |
| Cleffa | Metronome L24 | Encore L4→L3, Sing L7→L6 |
| Wobbuffet | Tickle L1 |  |
| Delibird | Celebrate L1, Powder Snow L5, Charm L10, Pluck L15, Aurora Beam L25, Blizzard L45, Roost L50, Sky Attack L55 |  |
| Tyrogue | Rock Smash L10 |  |
| Blissey | Wish L1, Recycle L1, Echoed Voice L10, Helping Hand L14, Heal Bell L42, Hyper Voice L46 | Tail Whip L5→L1, Refresh L9→L6, Double Slap L12→L8, Bestow L20→L12, Take Down L27→L17, Sing L31→L22, Fling L34→L27, Egg Bomb L44→L30, Heal Pulse L39→L32, Light Screen L50→L37, Healing Wish L57→L49 |
| Ralts | Fairy Wind L1, Double Team L9, Psybeam L18, Wish L42, Stored Power L53, Moonblast L58 | Charm L34→L23 |
| Slaking | Fury Swipes L12, Mega Punch L31, Block L34, Knock Off L38, Play Rough L45, Giga Impact L65 | Covet L23→L21, Chip Away L27→L24, Counter L33→L27, Double-Edge L66→L50 |
| Azurill | Tackle L7, Double Slap L19 | Helping Hand L16→L13 |
| Feebas | Bounce L35 | Flail L30→L25 |
| Wynaut | Tickle L30 |  |
| Beldum | Iron Defense L25, Zen Headbutt L30, Iron Head L40 |  |
| Latias | Twister L8, Zen Headbutt L35, Tailwind L45, Trick L55 | Mist Ball L35→L25, Psychic L51→L50 |
| Latios | Twister L8, Tailwind L45, Imprison L55 | Luster Purge L35→L25, Zen Headbutt L41→L35, Psychic L51→L50 |
| Jirachi | Ice Punch L1, Thunder Punch L1, Fire Punch L1, Mirror Shot L12, Skill Swap L16, Play Rough L24, Iron Head L32, Moonblast L70 | Refresh L25→L1, Helping Hand L15→L1, Rest L5→L4, Swift L10→L8, Gravity L45→L40, Healing Wish L50→L48, Cosmic Power L60→L56 |
| Turtwig | Absorb L4, Worry Seed L7, Headbutt L13, Seed Bomb L28, Body Slam L30, Natural Gift L45 | Withdraw L5→L1, Bite L21→L20, Mega Drain L25→L22, Leech Seed L29→L25 |
| Grotle | Worry Seed L7, Headbutt L13, Mega Drain L22, Body Slam L30, Natural Gift L45 | Bite L22→L20, Leech Seed L32→L25, Synthesis L37→L34, Crunch L42→L38, Giga Drain L47→L41, Leaf Storm L52→L50 |
| Torterra | Worry Seed L1, Mega Drain L22, Body Slam L30, Shell Smash L60 | Bite L22→L20, Leech Seed L33→L25, Synthesis L39→L34, Crunch L45→L38, Giga Drain L51→L41, Head Smash L63→L45, Leaf Storm L57→L50 |
| Chimchar | Fury Swipes L12, Feint Attack L20, Covet L33, Endeavor L47 | Ember L7→L4, Taunt L9→L8 |
| Monferno | Fury Swipes L12, Wake-Up Slap L24, Covet L33, Endeavor L47 | Taunt L9→L8, Feint L26→L20, Torment L29→L26, Acrobatics L46→L43, Flare Blitz L56→L55 |
| Infernape | Nasty Plot L1, Fury Swipes L12, Wake-Up Slap L24, Torment L26, Heat Wave L40, Focus Punch L47 | Flame Wheel L19→L17, Feint L26→L20, Acrobatics L52→L43, Calm Mind L58→L51 |
| Piplup | Water Sport L7, Peck L9, Icy Wind L15, Defog L33, Chip Away L38, Dive L41 | Growl L4→L1, Bubble L7→L4, Whirlpool L32→L12, Bide L22→L21, Brine L29→L27 |
| Prinplup | Peck L9, Icy Wind L15, Steel Wing L29, Defog L33, Chip Away L38, Dive L41 | Bubble L8→L1, Whirlpool L37→L12, Bide L24→L21, Brine L33→L27 |
| Empoleon | Peck L9, Icy Wind L15, Iron Defense L21, Steel Wing L29, Defog L33, Dive L41, Metal Burst L56 | Swords Dance L11→L1, Whirlpool L39→L12, Brine L33→L27, Flash Cannon L44→L38, Mist L46→L43, Drill Peck L50→L47, Hydro Pump L59→L52 |
| Starly | Double Team L11, Aerial Ace L22, Work Up L28, Pluck L31, Retaliate L36, Double-Edge L49 | Endeavor L17→L15, Whirlwind L21→L18, Take Down L29→L26 |
| Staravia | Double Team L11, Aerial Ace L22, Work Up L28, Pluck L31, Retaliate L36, Double-Edge L49 | Endeavor L18→L15, Whirlwind L23→L18, Take Down L33→L26 |
| Staraptor | Double Team L11, Aerial Ace L22, Work Up L28, Pluck L31, Retaliate L36, Giga Impact L58 | Endeavor L18→L15, Whirlwind L23→L18, Take Down L33→L26, Agility L41→L40, Brave Bird L49→L45, Double-Edge L65→L49, Final Gambit L57→L53 |
| Bidoof | Bide L24, Take Down L31, Natural Gift L38, Double-Edge L49 | Yawn L21→L18, Amnesia L41→L28 |
| Bibarel | Water Pulse L24, Take Down L31, Aqua Tail L38, Double-Edge L49 | Defense Curl L5→L1, Rollout L9→L1, Yawn L23→L18, Amnesia L48→L28, Super Fang L38→L35, Superpower L53→L42, Curse L58→L45 |
| Kricketot | Uproar L18 | Bug Bite L16→L12 |
| Kricketune | Round L10, Focus Energy L11, Snarl L17, Silver Wind L19, Metal Sound L23, X-Scissor L26, Hyper Voice L29, Knock Off L37, Heal Bell L39, Boomburst L42 | Struggle Bug L6→L1, Fell Stinger L36→L13, Sing L18→L15, Screech L34→L23, Taunt L38→L31, Bug Buzz L46→L34, Perish Song L50→L47 |
| Shinx | Howl L19, Facade L28, Sucker Punch L44, Electric Terrain L47, Volt Tackle L52 | Baby-Doll Eyes L13→L9, Roar L21→L16, Thunder Fang L29→L22, Swagger L25→L24, Crunch L33→L31, Wild Charge L45→L34, Discharge L41→L40 |
| Luxio | Baby-Doll Eyes L9, Howl L19, Facade L28, Sucker Punch L44, Electric Terrain L47, Volt Tackle L52 | Charge L9→L1, Spark L13→L11, Roar L23→L16, Thunder Fang L33→L22, Swagger L28→L24, Crunch L38→L31, Wild Charge L53→L34, Scary Face L43→L37, Discharge L48→L40 |
| Luxray | Fire Fang L1, Ice Fang L1, Baby-Doll Eyes L1, Howl L19, Facade L28, Wild Charge L34, Scary Face L37, Discharge L40 | Spark L13→L11, Bite L18→L14, Roar L23→L16, Thunder Fang L35→L22, Swagger L28→L24, Crunch L42→L31, Sucker Punch L49→L44, Volt Tackle L63→L52 |
| Budew | Venoshock L20 |  |
| Roserade | Absorb L1, Growth L1, Stun Spore L10, Leech Seed L16, Aromatherapy L22, Venoshock L25, Giga Drain L28, Toxic Spikes L31, Ingrain L34, Petal Blizzard L37, Toxic L40, Grass Whistle L43, Synthesis L46, Petal Dance L50 |  |
| Cranidos | Smack Down L12, Rock Slide L32, Stealth Rock L38, Iron Head L42, Agility L49 | Focus Energy L6→L5, Pursuit L10→L9, Scary Face L19→L18, Assurance L24→L21, Ancient Power L33→L23, Chip Away L28→L26, Screech L42→L28, Zen Headbutt L37→L35 |
| Rampardos | Superpower L1, Smack Down L12, Stealth Rock L38, Iron Head L42, Agility L49, Head Charge L54 | Scary Face L19→L18, Assurance L24→L21, Ancient Power L36→L23, Chip Away L28→L26, Screech L51→L28, Zen Headbutt L43→L35, Head Smash L54→L46 |
| Shieldon | Smack Down L7, Counter L14, Mirror Shot L19, Endure L27, Stealth Rock L34, Power Split L44 | Taunt L6→L4, Iron Defense L19→L16, Swagger L24→L21, Ancient Power L28→L23, Iron Head L44→L32 |
| Bastiodon | Super Fang L1, Quick Guard L1, Wide Guard L1, Smack Down L1, Counter L14, Mirror Shot L19, Stealth Rock L34, Power Split L44, King’s Shield L52 | Iron Defense L19→L16, Swagger L24→L21, Ancient Power L28→L23, Iron Head L47→L32, Heavy Slam L50→L47 |
| Vespiquen | Bug Buzz L1, Infestation L15, Aromatic Mist L18, Silver Wind L21, Signal Beam L26 | Fury Swipes L13→L12, Swagger L49→L21, Heal Order L29→L24, Attack Order L45→L40 |
| Pachirisu | Endure L15, Volt Switch L25, Lovely Kiss L41, Volt Tackle L49 | Quick Attack L5→L1, Nuzzle L19→L7, Swift L21→L17, Electro Ball L25→L20, Sweet Kiss L29→L22, Super Fang L37→L27, Thunder Wave L33→L30, Discharge L41→L33, Hyper Fang L49→L37 |
| Buizel | Pound L1, Helping Hand L1, Bite L22, Quick Guard L25, Ice Fang L33, Crunch L40, Iron Tail L47 | Growl L4→L1, Water Sport L7→L3, Water Gun L15→L8, Pursuit L18→L14, Swift L21→L17, Aqua Jet L24→L20, Whirlpool L31→L27, Aqua Tail L38→L36 |
| Floatzel | Pound L1, Helping Hand L1, Quick Guard L25, Agility L43, Iron Tail L47 | Water Gun L15→L8, Pursuit L18→L14, Swift L21→L17, Aqua Jet L24→L20, Whirlpool L35→L27, Aqua Tail L46→L36 |
| Cherubi | Petal Dance L25, Natural Gift L30, After You L32, Body Slam L39, Heal Pulse L46 | Helping Hand L13→L1, Growth L7→L5, Leech Seed L10→L8, Magical Leaf L19→L12, Sunny Day L22→L16, Take Down L31→L20, Worry Seed L28→L22, Lucky Chant L40→L27, Petal Blizzard L47→L36 |
| Ambipom | Fire Punch L1, Thunder Punch L1, Ice Punch L1, Pursuit L17, Swift L20, Low Kick L23, Dizzy Punch L28, Focus Punch L43 | Fury Swipes L18→L8, Tickle L15→L14, Fling L36→L35 |
| Drifloon | Whirlwind L1, Tailwind L16, Air Cutter L22, Self-Destruct L32, Air Slash L42, Phantom Force L49 | Gust L8→L7, Focus Energy L13→L11, Payback L16→L14, Swallow L32→L30, Spit Up L32→L30, Amnesia L40→L39 |
| Drifblim | Defog L1, Whirlwind L1, Tailwind L16, Air Cutter L22, Swallow L30, Spit Up L30, Self-Destruct L32, Baton Pass L46 | Focus Energy L13→L11, Payback L16→L14, Shadow Ball L40→L36, Amnesia L46→L39, Explosion L60→L56 |
| Buneary | Rototiller L1, Double Kick L16, Me First L18, Baton Pass L24, Mega Kick L42, High Jump Kick L53 | Endure L6→L5, Baby-Doll Eyes L13→L7, Quick Attack L16→L13, Dizzy Punch L36→L22, Agility L33→L26, After You L43→L32, Charm L46→L35, Entrainment L50→L38, Bounce L56→L45, Healing Wish L63→L49 |
| Lopunny | Last Resort L1, Double Kick L16, Me First L18, Baton Pass L24, Mega Kick L42 | Endure L6→L5, Baby-Doll Eyes L13→L7, Quick Attack L16→L13, Dizzy Punch L36→L22, Agility L33→L26, After You L43→L32, Charm L46→L35, Entrainment L53→L38, High Jump Kick L66→L53 |
| Mismagius | Confuse Ray L8, Mean Look L10, Psybeam L14, Ominous Wind L17, Trick L19, Icy Wind L22, Sing L24, Pain Split L29, Extrasensory L32, Grudge L35, Shadow Ball L38, Wonder Room L40, Perish Song L43 |  |
| Honchkrow | Brave Bird L1, Beat Up L1, Peck L1, Night Shade L17, Assurance L21, Taunt L25, Feint Attack L29, Mean Look L37, Tailwind L45, Sky Attack L53, Torment L57 | Quash L65→L1, Swagger L25→L23, Drill Peck L55→L33, Dark Pulse L75→L55 |
| Glameow | Fury Swipes L13, Slash L25, Night Slash L30, Super Fang L37 | Scratch L5→L1, Growl L8→L3, Hypnosis L13→L10, Charm L25→L19, Assist L29→L22, Hone Claws L48→L27, Play Rough L50→L45 |
| Purugly | Fury Swipes L13, Slash L25, Night Slash L30, Play Rough L45 | Hypnosis L13→L1, Charm L25→L19, Assist L29→L22, Hone Claws L60→L27, Attract L52→L42 |
| Chingling | Psyshock L19, Recover L24 | Growl L4→L1, Astonish L7→L3, Confusion L10→L5, Yawn L13→L8, Entrainment L19→L11, Uproar L32→L15 |
| Stunky | Fury Swipes L9, Pursuit L12, Sludge Bomb L31, Memento L38, Gunk Shot L44 | Screech L7→L6, Acid Spray L19→L17, Toxic L27→L26, Night Slash L31→L29 |
| Skuntank | Fire Fang L1, Fury Swipes L9, Pursuit L12, Sludge Bomb L31, Gunk Shot L44 | Acid Spray L19→L17, Toxic L27→L26, Night Slash L31→L29 |
| Bronzor | Gravity L1, Mirror Shot L16, Stealth Rock L24, Skill Swap L40, Zen Headbutt L52 | Imprison L9→L7, Confuse Ray L11→L10, Psywave L15→L12, Extrasensory L39→L27, Metal Sound L31→L30, Heavy Slam L49→L46 |
| Bronzong | Weather Ball L1, Trick L1, Gravity L1, Mirror Shot L16, Skill Swap L24, Zen Headbutt L52 | Confuse Ray L11→L10, Psywave L15→L12, Extrasensory L42→L27, Metal Sound L31→L30, Gyro Ball L36→L35, Payback L45→L43, Heavy Slam L51→L46 |
| Bonsly | Uproar L28, Curse L37, Stone Edge L43 | Rock Throw L12→L8, Feint Attack L19→L18, Rock Tomb L26→L20, Block L29→L23, Counter L36→L25, Sucker Punch L40→L34 |
| Mime Jr. | Psywave L15, Magical Leaf L21, Trick L32, Dazzling Gleam L39, Baton Pass L43 | Role Play L43→L3, Meditate L8→L5, Double Slap L11→L10, Encore L18→L12, Light Screen L22→L18, Reflect L22→L18, Psybeam L25→L24, Substitute L29→L27, Recycle L32→L30, Psychic L39→L36, Safeguard L50→L47 |
| Happiny | Covet L7, Natural Gift L14, Soft-Boiled L18, Uproar L23, Last Resort L28 | Copycat L5→L3, Refresh L9→L5, Sweet Kiss L12→L10 |
| Chatot | Flatter L1, Uproar L28, Air Slash L33, Nasty Plot L40, Parting Shot L46 | Echoed Voice L35→L1, Growl L5→L4, Mirror Move L9→L7, Round L21→L10, Fury Attack L17→L16, Mimic L32→L30, Feather Dance L54→L35, Synchronoise L49→L44, Boomburst L58→L49 |
| Spiritomb | Ancient Power L1, Switcheroo L20, Revenge L25, Shadow Ball L40, Grudge L55, Phantom Force L60, Outrage L65 | Feint Attack L22→L5, Hypnosis L13→L10, Dream Eater L19→L10, Ominous Wind L28→L15, Sucker Punch L31→L30, Nasty Plot L37→L35 |
| Gible | Slam L7, Dragon Breath L24, Scary Face L40, Rock Climb L45, Earthquake L55 | Sandstorm L13→L10, Sand Tomb L19→L17 |
| Gabite | Slam L1, Scary Face L40, Rock Climb L45, Earthquake L55 | Sandstorm L13→L10, Sand Tomb L19→L17, Dig L40→L36 |
| Garchomp | Earth Power L1, Slam L1, Scary Face L40, Rock Climb L45, Giga Impact L61 | Sand Tomb L19→L17, Dig L40→L36, Dragon Rush L53→L51, Earthquake L57→L55 |
| Munchlax | Slack Off L62 | Screech L20→L17, Rollout L36→L25 |
| Riolu | Vacuum Wave L25, Dizzy Punch L33, Nasty Plot L38 | Feint L11→L10, Force Palm L15→L13, Copycat L19→L17, Screech L24→L21, Final Gambit L50→L44 |
| Lucario | Force Palm L16, Iron Head L47 | Final Gambit L64→L1, Power-Up Punch L15→L1, Counter L6→L1, Feint L11→L10, Me First L37→L13, Heal Pulse L51→L38 |
| Hippopotas | Sandstorm L21, Rest L25, Sleep Talk L25, Bulldoze L28, Roar L34, Slack Off L49 | Bite L7→L6, Sand Tomb L25→L10, Take Down L19→L16 |
| Hippowdon | Sandstorm L21, Rest L25, Sleep Talk L25, Bulldoze L28, Roar L34, Slack Off L49 | Sand Tomb L25→L1, Take Down L19→L16, Double-Edge L50→L44 |
| Skorupi | Acupressure L12, Poison Jab L31, X-Scissor L40 | Pursuit L16→L5, Bug Bite L20→L9, Venoshock L27→L14, Poison Fang L23→L21, Hone Claws L30→L27, Night Slash L38→L37, Cross Poison L49→L46 |
| Drapion | Focus Energy L1, Acupressure L12, Poison Jab L31, X-Scissor L40 | Pursuit L16→L1, Bug Bite L20→L9, Venoshock L27→L14, Poison Fang L23→L21, Hone Claws L30→L27, Night Slash L38→L37, Scary Face L43→L42, Cross Poison L57→L46, Fell Stinger L53→L52 |
| Croagunk | Poison Sting L6, Drain Punch L30, Flatter L37, Cross Chop L48, Gunk Shot L53 | Taunt L10→L8, Pursuit L15→L12, Revenge L22→L15, Venoshock L36→L20, Swagger L24→L23, Mud Bomb L29→L26, Poison Jab L43→L32, Sludge Bomb L45→L40 |
| Toxicroak | Drain Punch L30, Flatter L37, Cross Chop L48, Gunk Shot L53 | Belch L58→L1, Taunt L10→L1, Pursuit L15→L12, Revenge L22→L15, Venoshock L36→L20, Swagger L24→L23, Mud Bomb L29→L26, Poison Jab L49→L32, Sludge Bomb L54→L40 |
| Carnivine | Thunder Fang L1, Acid L1, Razor Leaf L14, Hyper Fang L18, Grass Whistle L27, Poison Fang L30, Seed Bomb L36, Super Fang L45, Energy Ball L52 | Vine Whip L11→L1, Bite L7→L5, Sweet Scent L17→L8, Ingrain L21→L10, Feint Attack L27→L21, Leaf Tornado L31→L24, Crunch L41→L34, Power Whip L50→L42 |
| Finneon | Defog L1, Gust L7, Captivate L21, Air Slash L28, Scald L31, Hydro Pump L44, Tailwind L46, Follow Me L51 | Attract L10→L1, Rain Dance L13→L11, Whirlpool L38→L13, Silver Wind L29→L24, U-turn L42→L40 |
| Lumineon | Quiver Dance L1, Defog L1, Captivate L21, Air Slash L28, Hydro Pump L44, Follow Me L51 | Rain Dance L13→L11, Whirlpool L42→L13, Silver Wind L29→L24, U-turn L48→L40, Bounce L53→L49 |
| Mantyke | Gust L4, Scald L33, Mirror Coat L48, Hurricane L52 | Supersonic L3→L1, Headbutt L16→L7, Water Pulse L19→L18, Wide Guard L23→L21, Take Down L27→L24, Air Slash L36→L28, Aqua Ring L39→L38, Bounce L46→L41, Hydro Pump L49→L45 |
| Snover | Grass Knot L19, Ice Punch L32, Energy Ball L34, Worry Seed L39, Hammer Arm L50 | Mist L21→L11, Ingrain L31→L28 |
| Abomasnow | Leaf Storm L1, Grass Knot L19, Energy Ball L34, Worry Seed L39, Hammer Arm L50, Sheer Cold L55 | Mist L21→L11, Ingrain L31→L28, Blizzard L47→L43 |
| Weavile | Pursuit L1, Slash L33, Ice Punch L35, Beat Up L44, Icicle Crash L48, Knock Off L57 | Icy Wind L14→L9, Fury Swipes L16→L13, Nasty Plot L20→L18, Metal Claw L22→L20, Screech L32→L30 |
| Lickilicky | Belly Drum L1, Drain Punch L1, Pound L1, Curse L27, Body Slam L36 | Supersonic L5→L1, Defense Curl L9→L1, Wrap L17→L12, Stomp L21→L16, Disable L25→L18, Chip Away L37→L24, Refresh L45→L29, Me First L41→L40, Screech L49→L43, Gyro Ball L61→L56 |
| Rhyperior | Stealth Rock L1, Rock Slide L36, Double-Edge L56 | Smack Down L13→L1, Bulldoze L21→L16, Chip Away L25→L19, Take Down L37→L29 |
| Tangrowth | Body Slam L37, Energy Ball L43, Morning Sun L55 | Absorb L10→L1, Sleep Powder L4→L1, Poison Powder L14→L10, Bind L17→L13, Growth L20→L16, Mega Drain L23→L19, Knock Off L27→L22, Stun Spore L30→L25, Natural Gift L33→L28, Giga Drain L36→L31, Ancient Power L40→L34, Tickle L46→L40, Wring Out L49→L46, Grassy Terrain L50→L49, Power Whip L53→L52 |
| Electivire | Ice Punch L1, Work Up L21, Mega Punch L32, Giga Impact L57 | Shock Wave L15→L9, Thunder Wave L19→L16, Electro Ball L22→L19, Thunder Punch L29→L25, Discharge L36→L35, Screech L42→L38, Thunderbolt L49→L42, Thunder L55→L52 |
| Magmortar | Aura Sphere L1, Zap Cannon L1, Work Up L21, Will-O-Wisp L28, Mega Punch L32, Dark Pulse L48, Hyper Beam L57 | Fire Spin L15→L9, Clear Smog L19→L16, Flame Burst L22→L19, Fire Punch L29→L25, Lava Plume L36→L35, Flamethrower L49→L42, Fire Blast L55→L52 |
| Togekiss | Magical Leaf L1, Growl L1, Charm L1, Fairy Wind L1, Metronome L1, Sweet Kiss L7, Return L10, Yawn L13, Encore L15, Follow Me L17, Tailwind L22, Air Cutter L25, Ancient Power L27, Wish L29, Safeguard L32, Dazzling Gleam L35, Baton Pass L41, Tri Attack L45, Defog L47, Soft-Boiled L50 |  |
| Yanmega | Defog L1, Leech Life L1, Twister L12, Wing Attack L15, Signal Beam L24, Air Cutter L26, Acrobatics L49, Dragon Pulse L53 | Feint L38→L1, Sonic Boom L14→L10, Supersonic L22→L20, Slash L43→L28, U-turn L49→L35 |
| Leafeon | Worry Seed L1, Growl L1, Sand Attack L4, Grassy Terrain L12, Double Kick L14, Bite L17, Bullet Seed L29, X-Scissor L48, Solar Beam L52 | Jump Kick L27→L1, Quick Attack L13→L6, Magical Leaf L20→L9, Leaf Blade L44→L37 |
| Glaceon | Sheer Cold L1, Jump Kick L1, Growl L1, Sand Attack L4, Powder Snow L9, Disable L12, Double Kick L14, Haze L22, Frost Breath L29, Yawn L35, Ice Beam L37 | Quick Attack L13→L6 |
| Gliscor | Sand Tomb L10, Wing Attack L18, Screech L24, Sky Attack L59 | Quick Attack L13→L1, Fury Cutter L16→L14, Sky Uppercut L45→L38, Earthquake L70→L44 |
| Mamoswine | Icy Wind L16, Dig L35, Amnesia L51 | Mud-Slap L11→L8, Endure L14→L12, Take Down L28→L26, Thrash L41→L40, Icicle Crash L52→L44 |
| Porygon-Z | Curse L1, Imprison L1, Swift L10, Electroweb L18, Gravity L21, Trick L34, Foul Play L44 | Psybeam L7→L4, Agility L12→L7, Recover L18→L14, Signal Beam L29→L24, Embargo L34→L28, Discharge L40→L31, Tri Attack L50→L38, Lock-On L45→L41, Hyper Beam L67→L52 |
| Gallade | Cross Chop L1, Double Kick L1, Brick Break L28 | Wide Guard L23→L20, Psycho Cut L59→L32, Sacred Sword L72→L39 |
| Probopass | Rock Throw L1, Heavy Slam L11, Shock Wave L17, Ancient Power L20, Flash Cannon L39, Iron Head L54 | Sandstorm L34→L33 |
| Dusknoir | Snatch L37, Sucker Punch L44, Phantom Force L53, Drain Punch L58 | Foresight L14→L8, Pursuit L22→L11, Shadow Sneak L17→L14, Will-O-Wisp L25→L18, Hex L40→L21, Payback L57→L26, Curse L33→L29, Mean Look L52→L34, Shadow Ball L45→L40 |
| Froslass | Trick L1, Icicle Spear L21, Ice Beam L37, Curse L49, Sheer Cold L58 | Ice Shard L10→L1, Captivate L41→L23, Frost Breath L48→L26, Blizzard L52→L47 |
| Rotom | Double Team L10, Eerie Impulse L45, Hyper Voice L55, Shadow Ball L60 | Uproar L8→L5, Shock Wave L22→L15, Ominous Wind L29→L20, Substitute L36→L30, Electro Ball L43→L35, Hex L50→L40 |
| Uxie | Stealth Rock L1, Giga Drain L1, Iron Tail L1, Helping Hand L1, Skill Swap L1, Hex L41, Stored Power L56, Barrier L61, Disable L66 | Swift L21→L11, Extrasensory L50→L21, Yawn L31→L26 |
| Mesprit | Stealth Rock L1, Earth Power L1, Signal Beam L1, Helping Hand L1, Wonder Room L1, Trick L1, Incinerate L6, Fake Tears L16, Knock Off L41, Zen Headbutt L56, Heal Bell L66 | Swift L21→L11, Extrasensory L50→L21, Lucky Chant L31→L26 |
| Azelf | Stealth Rock L1, Fire Punch L1, Outrage L1, Helping Hand L1, Magic Room L1, Spite L1, Tri Attack L41, Final Gambit L46, Psyshock L56, Power Split L66 | Swift L21→L11, Extrasensory L50→L21, Uproar L31→L26 |
| Dialga | Magnet Rise L1, Mirror Shot L15, Heal Block L20, Dragon Claw L25, Stealth Rock L30, Trick Room L55, Dragon Pulse L65, Cosmic Power L75 | Metal Claw L6→L1, Slash L18→L5, Iron Tail L44→L35, Roar of Time L94→L45 |
| Palkia | Brine L15, Heal Block L20, Haze L30, Gravity L55, Dragon Pulse L65, Dragon Dance L75 | Aqua Ring L11→L1, Water Pulse L34→L1, Slash L18→L5, Dragon Claw L44→L25, Spacial Rend L82→L45 |
| Heatran | Mirror Shot L7, Stealth Rock L25, Dragon Pulse L67 | Leer L9→L1, Fire Fang L17→L13, Metal Sound L25→L19, Crunch L33→L31, Lava Plume L49→L37, Stone Edge L88→L79 |
| Regigigas | Dynamic Punch L1, Gravity L1, Stomp L1, Drain Punch L5, Mega Punch L15, Block L45, Superpower L60, Power Split L75, Guard Split L75, Shadow Punch L80 | Wide Guard L40→L20, Zen Headbutt L50→L35, Double-Edge L80→L40, Giga Impact L100→L85 |
| Cresselia | Helping Hand L1, Icy Wind L13, Ice Beam L49 | Safeguard L11→L1, Mist L20→L7, Future Sight L38→L37, Psychic L93→L61, Moonblast L99→L73 |
| Phione | Helping Hand L1, Icy Wind L17, Signal Beam L33, Play Rough L41, Muddy Water L45, Ice Beam L53, Soak L57, Hydro Pump L61, Heal Bell L65 | Charm L9→L5, Whirlpool L39→L9, Supersonic L16→L13, Bubble Beam L24→L21, Aqua Ring L54→L25, Dive L61→L29, Rain Dance L69→L37 |
| Manaphy | Icy Wind L17, Signal Beam L33, Ancient Power L41, Surf L45, Ice Beam L53, Soak L57, Hydro Pump L61 | Charm L9→L5, Whirlpool L39→L9, Supersonic L16→L13, Bubble Beam L24→L21, Aqua Ring L54→L25, Dive L61→L29, Rain Dance L69→L37, Heart Swap L76→L65 |
| Darkrai | Knock Off L1, Trick L1, Double Team L1, Night Shade L1, Pursuit L1, Sucker Punch L43, Nasty Plot L57, Dark Pulse L71 | Nightmare L31→L15, Haze L41→L36, Dark Void L51→L50 |
| Arceus | Iron Head L1, Aqua Tail L1, Phantom Force L1, Heat Wave L1, Giga Drain L1, Dragon Pulse L1, Discharge L1, Icy Wind L1, Defog L1, Tailwind L1, Stealth Rock L1, Outrage L40 |  |
| Victini | Work Up L1, Helping Hand L1, Follow Me L30, Double-Edge L40, Discharge L50, Psychic L65, Volt Tackle L70 | Endure L9→L5, Headbutt L17→L10, Flame Charge L25→L15, Stored Power L89→L20, Flame Burst L41→L25, Zen Headbutt L49→L35, Inferno L57→L45, Final Gambit L81→L75 |
| Snivy | Vine Whip L5, Wrap L8, Glare L21, Synthesis L35, Iron Tail L39, Flail L45 | Leer L4→L1, Growth L13→L10, Slam L25→L13, Gastro Acid L40→L26 |
| Servine | Synthesis L35, Iron Tail L39, Flail L45 | Growth L13→L10, Slam L28→L13, Leech Seed L20→L19, Gastro Acid L48→L26, Leaf Blade L32→L30, Coil L36→L33 |
| Serperior | Noble Roar L1, Synthesis L35, Iron Tail L39, Dragon Pulse L45 | Growth L13→L10, Slam L28→L13, Leech Seed L20→L19, Gastro Acid L56→L26, Leaf Blade L32→L30, Coil L38→L33, Wring Out L50→L49, Leaf Storm L62→L54 |
| Tepig | Odor Sleuth L7, Smog L12, Headbutt L17, Flame Burst L24, Body Slam L36, Double-Edge L46 | Tail Whip L3→L1, Ember L7→L5, Defense Curl L13→L10, Assurance L31→L29, Roar L39→L38 |
| Pignite | Smog L12, Fire Punch L24, Submission L36, Work Up L38, Superpower L46 | Defense Curl L13→L10, Rollout L23→L21, Take Down L28→L27, Assurance L36→L29 |
| Emboar | Smog L12, Fire Punch L24, Submission L36, Work Up L38, Superpower L46 | Defense Curl L13→L10, Rollout L23→L21, Take Down L28→L27, Assurance L38→L29, Flamethrower L43→L42, Flare Blitz L62→L56 |
| Oshawott | Water Gun L5, Focus Energy L11, Slash L29, X-Scissor L41, Knock Off L55 | Tail Whip L5→L1, Water Sport L11→L8, Fury Cutter L19→L14 |
| Dewott | Slash L29, X-Scissor L41 | Fury Cutter L21→L14, Encore L37→L34, Aqua Tail L42→L38, Swords Dance L50→L48 |
| Samurott | Aerial Ace L20, Water Pulse L23, Revenge L26, X-Scissor L41, Horn Drill L55 | Knock Off L18→L1, Focus Energy L13→L11, Fury Cutter L21→L14, Encore L39→L34, Aqua Tail L46→L38, Retaliate L49→L44, Swords Dance L51→L48, Hydro Pump L54→L52 |
| Patrat | Sand Attack L11, Chip Away L14, Bullet Seed L25, Flail L42, Iron Tail L46 | Leer L3→L1, Bite L6→L4, Bide L8→L6, Detect L11→L9, Hypnosis L18→L16, Super Fang L21→L18, Mean Look L36→L27 |
| Watchog | Sand Attack L11, Chip Away L14, Bullet Seed L25, Hyper Fang L30, Lock-On L35, Iron Tail L46 | Bide L8→L1, Detect L11→L9, Super Fang L22→L18, Mean Look L43→L27 |
| Lillipup | Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Odor Sleuth L5→L3, Baby-Doll Eyes L10→L6, Helping Hand L12→L10, Work Up L17→L16 |
| Herdier | Baby-Doll Eyes L6, Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Helping Hand L12→L10, Work Up L19→L16, Roar L29→L27, Reversal L38→L34, Play Rough L52→L49 |
| Stoutland | Baby-Doll Eyes L1, Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Helping Hand L12→L10, Work Up L19→L16, Roar L29→L27, Reversal L42→L34, Last Resort L51→L46, Play Rough L63→L49, Giga Impact L59→L55 |
| Purrloin | U-turn L32, Dark Pulse L38 | Assist L6→L5, Pursuit L15→L8, Torment L19→L14, Assurance L28→L17, Fake Out L21→L19, Slash L30→L22, Night Slash L37→L27, Captivate L33→L30, Snatch L39→L35, Sucker Punch L46→L45, Play Rough L49→L48 |
| Liepard | Copycat L1, Snarl L20, Captivate L30, U-turn L32, Dark Pulse L38 | Pursuit L15→L1, Torment L19→L14, Assurance L31→L17, Fake Out L22→L19, Slash L34→L22, Hone Claws L26→L25, Night Slash L43→L27, Snatch L47→L35, Nasty Plot L50→L42, Play Rough L58→L48 |
| Pansage | Role Play L8, Dizzy Punch L40, Wood Hammer L46, Snatch L49 | Lick L7→L6 |
| Simisage | Work Up L1, Play Nice L1, Scratch L1, Role Play L8, Vine Whip L10, Leech Seed L16, Bite L19, Torment L25, Fling L28, Acrobatics L31, Grass Knot L34, Recycle L37, Dizzy Punch L40, Crunch L43, Wood Hammer L46, Snatch L49, Natural Gift L52 |  |
| Pansear | Role Play L8, Blaze Kick L34, Endeavor L40, Me First L49 | Lick L7→L6 |
| Simisear | Work Up L1, Play Nice L1, Scratch L1, Role Play L8, Incinerate L10, Yawn L16, Bite L19, Amnesia L25, Fling L28, Acrobatics L31, Blaze Kick L34, Recycle L37, Endeavor L40, Crunch L43, Fire Blast L46, Me First L49, Natural Gift L52 |  |
| Panpour | Role Play L8, Hyper Voice L40, Hydro Pump L46, Encore L49 | Lick L7→L6 |
| Simipour | Work Up L1, Play Nice L1, Scratch L1, Role Play L8, Water Gun L10, Water Sport L16, Bite L19, Taunt L25, Fling L28, Acrobatics L31, Brine L34, Recycle L37, Hyper Voice L40, Crunch L43, Hydro Pump L46, Encore L49, Natural Gift L52 |  |
| Munna | Psyshock L25, Telekinesis L27, Dazzling Gleam L30, Heal Bell L42, Moonblast L49 | Lucky Chant L5→L4, Yawn L7→L6, Psybeam L11→L10, Imprison L13→L12, Moonlight L17→L15, Zen Headbutt L23→L17, Nightmare L29→L22, Dream Eater L41→L39 |
| Musharna | Gravity L1, Psywave L1, Yawn L1, Imprison L12, Moonlight L15, Zen Headbutt L17, Nightmare L22, Psyshock L25, Telekinesis L27, Dazzling Gleam L30, Future Sight L34, Calm Mind L37, Dream Eater L39, Heal Bell L42, Psychic L45, Moonblast L49, Stored Power L52 |  |
| Pidove | Air Cutter L12, Echoed Voice L15, Detect L20, Swift L25, Hyper Voice L38 | Growl L4→L3, Leer L6→L5, Razor Wind L32→L22, Feather Dance L36→L34, Tailwind L46→L43, Sky Attack L50→L47 |
| Tranquill | Air Cutter L12, Echoed Voice L15, Swift L25, Air Slash L29, Hyper Voice L38 | Razor Wind L36→L22, Feather Dance L41→L34, Swagger L45→L40, Tailwind L54→L43, Sky Attack L59→L47 |
| Unfezant | Air Cutter L12, Echoed Voice L15, Razor Wind L22, Swift L25, Air Slash L29, Feather Dance L34, Hyper Voice L38 | Swagger L49→L40, Tailwind L60→L43, Sky Attack L66→L47 |
| Blitzle | Double Kick L17, Stomp L25, Blaze Kick L34, Thrash L40, Ion Deluge L42, Jump Kick L46, Volt Tackle L50 | Tail Whip L4→L3, Charge L8→L5, Shock Wave L11→L9, Thunder Wave L15→L11, Flame Charge L18→L15, Spark L25→L20, Discharge L32→L28, Agility L36→L30, Wild Charge L39→L37 |
| Zebstrika | Outrage L1, Double Kick L17, Stomp L25, Blaze Kick L34, Thrash L40, Jump Kick L46, Volt Tackle L50 | Shock Wave L11→L1, Flame Charge L18→L15, Spark L25→L20, Discharge L36→L28, Agility L42→L30, Wild Charge L47→L37 |
| Roggenrola | Mud-Slap L16, Rock Climb L32, Heavy Slam L37, Curse L46 | Iron Defense L20→L19, Smack Down L23→L21, Stealth Rock L30→L23 |
| Boldore | Rock Climb L32, Heavy Slam L37, Curse L46 | Mud-Slap L17→L16, Iron Defense L20→L19, Smack Down L23→L21, Stealth Rock L36→L23, Rock Slide L30→L28, Sandstorm L42→L34, Stone Edge L48→L42, Explosion L55→L52 |
| Gigalith | Rock Climb L32, Heavy Slam L37, Curse L46 | Mud-Slap L17→L16, Iron Defense L20→L19, Smack Down L23→L21, Stealth Rock L36→L23, Rock Slide L30→L28, Sandstorm L42→L34, Stone Edge L48→L42, Explosion L55→L52 |
| Woobat | Simple Beam L22, Extrasensory L26, Roost L35, Hurricane L43 | Odor Sleuth L4→L1, Gust L8→L4, Assurance L12→L8, Heart Stamp L15→L11, Attract L25→L13, Air Cutter L21→L16, Amnesia L29→L28, Air Slash L32→L31, Psychic L41→L38 |
| Swoobat | Trick L1, Simple Beam L22, Extrasensory L26, Roost L35, Hurricane L43 | Heart Stamp L15→L11, Attract L25→L13, Air Cutter L21→L16, Amnesia L29→L28, Air Slash L32→L31, Psychic L41→L38 |
| Drilbur | Rototiller L1, Smack Down L21, Iron Head L43 | Drill Run L40→L33 |
| Excadrill | Smack Down L21, Iron Head L43 | Drill Run L44→L33 |
| Audino | Round L8, Dazzling Gleam L36, Heal Bell L45 | Baby-Doll Eyes L5→L1, Entrainment L29→L18, Heal Pulse L37→L25, Simple Beam L45→L33, Wish L53→L38, Double-Edge L49→L42 |
| Timburr | Work Up L28 |  |
| Gurdurr | Work Up L28 | Rock Slide L33→L31, Dynamic Punch L37→L36, Scary Face L41→L39, Hammer Arm L45→L43, Superpower L57→L56 |
| Conkeldurr | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Work Up L28 | Rock Slide L33→L31, Dynamic Punch L37→L36, Scary Face L41→L39, Hammer Arm L45→L43, Superpower L57→L56 |
| Tympole | Acid L12, Water Pulse L21, Mud Bomb L27, Earth Power L42, Screech L48 | Supersonic L5→L3, Round L9→L6, Bubble Beam L12→L10, Mud Shot L16→L15, Aqua Ring L20→L18, Rain Dance L31→L30 |
| Palpitoad | Acid L12, Water Pulse L21, Mud Bomb L27, Earth Power L42, Screech L48 | Bubble Beam L12→L10, Mud Shot L16→L15, Aqua Ring L20→L18, Rain Dance L33→L30, Echoed Voice L42→L39, Hydro Pump L47→L46 |
| Seismitoad | Ice Punch L1, Gastro Acid L1, Water Pulse L21, Mud Bomb L27, Acid Spray L36, Earth Power L42, Toxic L48, Hyper Voice L51 | Bubble Beam L12→L10, Mud Shot L16→L15, Aqua Ring L20→L18, Rain Dance L33→L30, Echoed Voice L49→L39, Hydro Pump L53→L46 |
| Throh | Ice Punch L1, Thunder Punch L1, Fire Punch L1, Helping Hand L1, Work Up L1, Chip Away L17, Payback L25, Drain Punch L35, Knock Off L54 | Bulk Up L48→L32 |
| Sawk | Ice Punch L1, Thunder Punch L1, Fire Punch L1, Helping Hand L1, Work Up L1, Chip Away L17, Feint Attack L25, Sky Uppercut L35, Dual Chop L54 | Karate Chop L17→L13, Bulk Up L48→L32, Close Combat L65→L47 |
| Sewaddle | Grass Whistle L23, Energy Ball L30 | Struggle Bug L22→L6, Razor Leaf L15→L12, Endure L29→L26, Bug Buzz L36→L35, Flail L43→L40 |
| Swadloon | Struggle Bug L1, Endure L26, Energy Ball L30, Bug Buzz L35, Flail L40, Sticky Web L45 |  |
| Leavanny | Sticky Web L1, Barrier L20, Grass Whistle L23, Knock Off L46 | Struggle Bug L22→L1, Fell Stinger L29→L28, Helping Hand L32→L30, Leaf Blade L36→L34, Entrainment L43→L36, Swords Dance L46→L43 |
| Venipede | Leech Life L6, Protect L9, Poison Jab L33, Pin Missile L39 | Poison Sting L5→L4, Poison Tail L19→L15, Bug Bite L22→L18, Venoshock L26→L24, Steamroller L33→L26, Rock Climb L40→L36 |
| Whirlipede | Leech Life L6, Protect L9, Poison Jab L33, Pin Missile L39 | Poison Tail L19→L15, Bug Bite L23→L18, Venoshock L28→L24, Steamroller L37→L26, Agility L32→L29, Rock Climb L46→L36, Double-Edge L50→L48 |
| Scolipede | Baton Pass L1, Leech Life L1, Protect L9, Poison Jab L33, Pin Missile L39 | Poison Tail L19→L15, Bug Bite L23→L18, Venoshock L28→L24, Steamroller L39→L26, Agility L33→L29, Rock Climb L50→L36, Toxic L44→L42, Venom Drench L47→L44, Double-Edge L55→L48 |
| Cottonee | Gust L15, Tailwind L23, Hurricane L47, Moonblast L50 | Growth L4→L1, Leech Seed L8→L4, Stun Spore L10→L7, Mega Drain L13→L10, Cotton Spore L17→L12, Razor Leaf L19→L18, Poison Powder L22→L20, Endeavor L44→L37, Solar Beam L46→L44 |
| Whimsicott | Fairy Wind L1, Absorb L1, Stun Spore L7, Razor Leaf L18, Poison Powder L20, Giga Drain L26, Charm L28, Helping Hand L31, Energy Ball L35, Endeavor L37, Sunny Day L40, Solar Beam L44 | Tailwind L28→L23 |
| Petilil | Teeter Dance L12, Uproar L23, Petal Dance L31, Quiver Dance L37, Hyper Voice L50 | After You L44→L1, Growth L4→L1, Leech Seed L8→L4, Sleep Powder L10→L7, Mega Drain L13→L10, Synthesis L17→L15, Magical Leaf L19→L18, Stun Spore L22→L20 |
| Lilligant | After You L1, Absorb L1, Magical Leaf L18, Stun Spore L20, Uproar L23, Giga Drain L26, Aromatherapy L28, Helping Hand L35, Sunny Day L40, Entrainment L44, Energy Ball L47, Hyper Voice L50 | Sleep Powder L18→L7, Petal Dance L46→L31 |
| Sandile | Mud-Slap L1 | Torment L10→L7 |
| Krokorok | Mud-Slap L1 | Torment L10→L7 |
| Krookodile | Block L1, Mud-Slap L1 | Torment L10→L7, Foul Play L42→L40, Sandstorm L48→L45, Earthquake L54→L50 |
| Darumaka | Swagger L17, Blaze Kick L39, Zen Headbutt L42 | Rollout L3→L1, Incinerate L6→L4, Rage L9→L7, Uproar L17→L10, Overheat L42→L33 |
| Maractus | Astonish L7, Bullet Seed L10, Acupressure L23, Bounce L27, Teeter Dance L33, Sandstorm L43, Wood Hammer L45, Play Rough L50 | Sweet Scent L3→L1, Growth L6→L3, Cotton Spore L18→L17, Needle Arm L22→L20, Ingrain L33→L25, Petal Blizzard L48→L30, Petal Dance L38→L37 |
| Dwebble | Rock Throw L1, Sharpen L1, Stone Edge L40, Snatch L46 | X-Scissor L35→L34, Flail L41→L37 |
| Crustle | Rock Throw L1, Sharpen L1, Fury Cutter L1, Stone Edge L40, Heavy Slam L46 | X-Scissor L38→L34, Flail L43→L37 |
| Scraggy | Jump Kick L31, Fling L50 | Payback L20→L9, Facade L42→L40 |
| Scrafty | Zen Headbutt L1, Jump Kick L31, Fling L50 | Payback L20→L1, Facade L45→L40, Rock Climb L51→L47, Focus Punch L58→L54, Head Smash L65→L59 |
| Sigilyph | Psycho Shift L44 | Reflect L28→L24, Mirror Move L34→L28, Air Slash L41→L31, Gravity L38→L34, Psychic L44→L38, Cosmic Power L48→L41, Sky Attack L50→L48 |
| Yamask | Role Play L16, Foul Play L32, Earth Power L47, Phantom Force L50 | Disable L5→L4, Night Shade L13→L7, Ominous Wind L25→L13, Will-O-Wisp L21→L19, Curse L29→L26, Power Split L33→L29, Guard Split L33→L29, Grudge L41→L40, Mean Look L45→L43 |
| Cofagrigus | Knock Off L1, Role Play L16, Foul Play L32, Earth Power L47, Phantom Force L50 | Night Shade L13→L1, Ominous Wind L25→L13, Will-O-Wisp L21→L19, Curse L29→L26, Power Split L33→L29, Guard Split L33→L29, Shadow Ball L39→L37, Grudge L45→L40, Mean Look L51→L43, Destiny Bond L57→L54 |
| Tirtouga | Protect L9, Iron Defense L18, Stone Edge L53 | Rollout L5→L4, Bite L8→L7, Aqua Jet L15→L12, Ancient Power L18→L16, Smack Down L31→L21, Brine L28→L24, Curse L35→L26, Aqua Tail L41→L35, Rock Slide L45→L38, Rain Dance L48→L45, Hydro Pump L50→L49 |
| Carracosta | Super Fang L1, Protect L9, Iron Defense L16, Aqua Tail L35, Stone Edge L53 | Bite L8→L7, Aqua Jet L15→L12, Smack Down L31→L21, Brine L28→L24, Curse L35→L26, Rock Slide L47→L38, Rain Dance L56→L45, Hydro Pump L61→L49 |
| Archen | Gust L1, Stone Edge L47, Sky Attack L57 | Ancient Power L18→L16, Dragon Breath L31→L25, Crunch L35→L28, Rock Slide L45→L32, Thrash L50→L37, Dragon Claw L48→L43 |
| Archeops | Defog L1, Gust L1, Stone Edge L47, Sky Attack L57 | Ancient Power L18→L16, Dragon Breath L31→L25, Crunch L35→L28, Rock Slide L51→L32, Thrash L61→L37, Dragon Claw L56→L43 |
| Trubbish | Barrage L13, Poison Fang L16, Poison Jab L32, Dizzy Punch L38, Pain Split L44 | Toxic Spikes L7→L6, Acid Spray L12→L10, Stockpile L23→L20, Swallow L23→L20, Take Down L25→L23, Clear Smog L34→L25, Amnesia L40→L28, Toxic L36→L35 |
| Garbodor | Rock Blast L1, Barrage L13, Poison Fang L16, Poison Jab L32, Dizzy Punch L38, Pain Split L44 | Acid Spray L12→L10, Stockpile L23→L20, Swallow L23→L20, Body Slam L25→L23, Clear Smog L34→L25, Amnesia L46→L28, Toxic L39→L35, Belch L49→L42, Gunk Shot L54→L48, Explosion L59→L53 |
| Zorua | Snarl L15, Dark Pulse L43, Uproar L46 | Pursuit L5→L4, Fake Tears L9→L7, Fury Swipes L13→L11, Scary Face L21→L18, Punishment L45→L28, Torment L33→L32, Agility L37→L35, Embargo L41→L40, Imprison L53→L52, Night Daze L57→L55 |
| Zoroark | Extrasensory L1, Snarl L15, Dark Pulse L43, Crush Claw L46 | Fury Swipes L13→L11, Scary Face L21→L18, Punishment L49→L28, Torment L34→L32, Agility L39→L35, Embargo L44→L40, Nasty Plot L54→L50 |
| Minccino | Fury Swipes L18, Covet L26, Play Rough L47 | Baby-Doll Eyes L3→L1, Helping Hand L7→L3, Echoed Voice L33→L5, Double Slap L13→L8, Swift L19→L13, Charm L27→L23, After You L49→L35, Hyper Voice L43→L38, Last Resort L45→L44 |
| Cinccino | Knock Off L1, Pound L1, Baby-Doll Eyes L1, Echoed Voice L1, Double Slap L8, Swift L13, Encore L15, Fury Swipes L18, Charm L23, Covet L26, Wake-Up Slap L33, After You L35, Hyper Voice L38, Captivate L40, Last Resort L44, Play Rough L47 |  |
| Gothita | Torment L5, Trick Room L29, Dark Pulse L38, Foul Play L49 | Play Nice L8→L1, Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Charm L46→L40 |
| Gothorita | Torment L5, Trick Room L29, Dark Pulse L38, Foul Play L49 | Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Charm L50→L40, Magic Room L53→L52 |
| Gothitelle | Fake Out L1, Torment L1, Trick Room L29, Dark Pulse L38, Foul Play L49 | Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Charm L54→L40, Magic Room L59→L52 |
| Solosis | Snatch L9, Counter L43 | Psybeam L12→L11, Recover L24→L23, Wonder Room L48→L31 |
| Duosion | Counter L43 | Recover L24→L23, Wonder Room L53→L31 |
| Reuniclus | Counter L43, Hammer Arm L57 | Recover L24→L23, Wonder Room L59→L31, Heal Block L54→L52 |
| Ducklett | Razor Wind L23, Brine L30, Acrobatics L36, Scald L41 | Bubble Beam L19→L18, Feather Dance L21→L20, Hurricane L46→L44 |
| Swanna | Razor Wind L23, Brine L30, Acrobatics L36, Scald L41 | Bubble Beam L19→L18, Feather Dance L21→L20, Tailwind L40→L38, Hurricane L47→L44 |
| Vanillite | Recycle L30, Flash Cannon L37, Natural Gift L54 | Harden L4→L3, Astonish L7→L5, Mist L16→L8, Icy Wind L13→L11, Avalanche L19→L18, Taunt L22→L21, Mirror Shot L26→L24, Frost Breath L38→L28 |
| Vanillish | Recycle L30, Flash Cannon L37, Natural Gift L54 | Mist L16→L8, Icy Wind L13→L11, Avalanche L19→L18, Taunt L22→L21, Mirror Shot L26→L24, Frost Breath L39→L28, Blizzard L53→L51 |
| Vanilluxe | Recycle L30, Flash Cannon L37, Belch L54 | Mist L16→L1, Icy Wind L13→L11, Avalanche L19→L18, Taunt L22→L21, Mirror Shot L26→L24, Frost Breath L39→L28, Mirror Coat L50→L47, Blizzard L59→L51 |
| Emolga | Aerial Ace L17, Air Slash L46, Nasty Plot L50, Volt Tackle L55 | Tail Whip L7→L1, Quick Attack L4→L3, Charge L10→L6, Spark L13→L9, Nuzzle L15→L11, Pursuit L16→L14, Encore L38→L25, Volt Switch L42→L38, Agility L46→L40, Discharge L50→L43 |
| Karrablast | Fury Attack L13, Revenge L25, Pin Missile L42, Megahorn L54 | Fury Cutter L13→L9, Headbutt L20→L16, Bug Buzz L28→L20, False Swipe L25→L22, X-Scissor L44→L29, Scary Face L40→L35, Flail L49→L45, Swords Dance L52→L48, Double-Edge L56→L50 |
| Escavalier | Drill Run L1, Fury Attack L13, Mirror Shot L16, Revenge L25, Gyro Ball L50, Megahorn L54 | Bug Buzz L28→L20, False Swipe L25→L22, X-Scissor L44→L29, Iron Defense L40→L35, Reversal L49→L45, Swords Dance L52→L48 |
| Foongus | Astonish L4, Smog L9, Grassy Terrain L25, Protect L34 | Growth L6→L1, Bide L12→L6, Ingrain L18→L11, Mega Drain L15→L14, Sweet Scent L24→L17 |
| Amoonguss | Smog L9, Grassy Terrain L25, Protect L34 | Ingrain L18→L11, Mega Drain L15→L14, Sweet Scent L24→L17, Sludge Bomb L43→L40, Solar Beam L49→L44, Rage Powder L54→L46, Spore L62→L50 |
| Frillish | Astonish L3, Refresh L14, Icy Wind L24, Shadow Ball L45, Pain Split L52 | Night Shade L9→L8, Bubble Beam L13→L12, Ominous Wind L27→L18, Water Pulse L22→L21, Rain Dance L37→L27, Brine L32→L30, Hex L43→L34, Hydro Pump L49→L42, Wring Out L55→L48, Water Spout L61→L57 |
| Jellicent | Giga Drain L1, Astonish L1, Icy Wind L24, Shadow Ball L45, Pain Split L52 | Bubble Beam L13→L12, Ominous Wind L27→L18, Water Pulse L22→L21, Rain Dance L37→L27, Brine L32→L30, Hex L45→L34, Hydro Pump L53→L42 |
| Alomomola | Dive L35, Zen Headbutt L51 | Aqua Jet L9→L8, Double Slap L13→L11, Heal Pulse L17→L15, Protect L21→L18, Water Pulse L25→L21, Wake-Up Slap L29→L28, Soak L33→L31, Safeguard L45→L41 |
| Joltik | Bug Bite L17, Gastro Acid L19, Slash L22, Sticky Web L45, Zap Cannon L50 | Fury Cutter L18→L11, Electroweb L15→L14, Electro Ball L29→L25, Signal Beam L34→L29, Agility L37→L31, Discharge L45→L34, Sucker Punch L40→L37, Bug Buzz L48→L41 |
| Galvantula | Electric Terrain L1, Bug Bite L17, Gastro Acid L19, Slash L22, Zap Cannon L50 | Fury Cutter L12→L11, Electroweb L15→L14, Electro Ball L29→L25, Signal Beam L34→L29, Agility L38→L31, Discharge L47→L34, Sucker Punch L44→L37, Bug Buzz L54→L41 |
| Ferroseed | Bullet Seed L25, Rock Climb L42, Spike Cannon L48, Seed Bomb L51 | Iron Defense L26→L9, Metal Claw L14→L12, Pin Missile L18→L16, Mirror Shot L30→L18, Self-Destruct L38→L30, Ingrain L35→L33, Iron Head L43→L37, Payback L47→L44 |
| Ferrothorn | Bullet Seed L25, Spike Cannon L48, Seed Bomb L51 | Iron Defense L26→L1, Metal Claw L14→L12, Pin Missile L18→L16, Mirror Shot L30→L18, Self-Destruct L38→L30, Ingrain L35→L33, Iron Head L46→L37, Payback L53→L44, Explosion L67→L56 |
| Klink | Magnetic Flux L1, Spark L17, Iron Head L37, Wild Charge L45, Heavy Slam L53 | Charge L6→L1, Thunder Shock L11→L5, Mirror Shot L36→L9, Bind L21→L13, Autotomize L31→L25, Screech L39→L29, Discharge L42→L33, Metal Sound L45→L41 |
| Klang | Magnetic Flux L1, Double Hit L1, Spark L17, Iron Head L37, Wild Charge L45, Heavy Slam L53 | Mirror Shot L36→L9, Bind L21→L13, Autotomize L31→L25, Screech L40→L29, Discharge L44→L33, Metal Sound L48→L41, Shift Gear L52→L49, Zap Cannon L60→L57, Hyper Beam L64→L61 |
| Klinklang | Heat Crash L1, Tri Attack L1, Spark L17, Iron Head L37, Wild Charge L45, Heavy Slam L53 | Mirror Shot L36→L9, Bind L21→L13, Autotomize L31→L25, Screech L40→L29, Discharge L44→L33, Metal Sound L48→L41, Shift Gear L54→L49, Lock-On L60→L57, Hyper Beam L72→L61 |
| Tynamo | Parabolic Charge L45 |  |
| Eelektrik | Mega Drain L15, Thunder Fang L20, Giga Drain L46 | Acid L19→L5, Acid Spray L49→L25, Coil L54→L38, Wild Charge L59→L42, Gastro Acid L64→L50, Thrash L74→L56, Zap Cannon L69→L59 |
| Eelektross | Drain Punch L1, Aqua Tail L1, Thunder Wave L1, Spark L1, Charge Beam L1, Bind L10, Mega Drain L15, Thunder Fang L20, Acid Spray L25, Wild Charge L42, Giga Drain L46, Thunderbolt L53, Superpower L63 |  |
| Elgyem | Psyshock L28, Signal Beam L34, Power Gem L54 | Miracle Eye L11→L1, Growl L4→L1, Heal Block L8→L5, Psybeam L15→L11, Headbutt L18→L14, Hidden Power L22→L17, Imprison L25→L19, Zen Headbutt L32→L22, Simple Beam L29→L24, Psych Up L36→L31, Psychic L39→L38, Calm Mind L43→L41, Guard Split L50→L44, Power Split L50→L44, Synchronoise L53→L48 |
| Beheeyem | Gravity L1, Psyshock L28, Signal Beam L34, Power Gem L54 | Psybeam L15→L11, Headbutt L18→L14, Hidden Power L22→L17, Imprison L25→L19, Zen Headbutt L32→L22, Simple Beam L29→L24, Psych Up L36→L31, Psychic L39→L38, Calm Mind L45→L41, Guard Split L56→L44, Power Split L58→L44 |
| Litwick | Lava Plume L33 | Imprison L24→L23, Hex L28→L26, Pain Split L55→L30, Curse L43→L36, Shadow Ball L49→L40, Overheat L61→L52 |
| Lampent | Lava Plume L33 | Imprison L24→L23, Hex L28→L26, Pain Split L61→L30, Curse L45→L36, Shadow Ball L53→L40, Overheat L69→L52 |
| Chandelure | Hypnosis L1, Ember L1, Astonish L1, Minimize L1, Fire Spin L7, Night Shade L13, Will-O-Wisp L16, Imprison L23, Lava Plume L33, Curse L36, Shadow Ball L40, Inferno L44, Memento L48, Overheat L52 |  |
| Axew | Slam L10, X-Scissor L34, Night Slash L44, Guillotine L48 | False Swipe L24→L16, Taunt L36→L28, Dragon Pulse L41→L31, Swords Dance L46→L41, Outrage L56→L52, Giga Impact L61→L60 |
| Fraxure | Slam L1, X-Scissor L34, Night Slash L44, Guillotine L48 | False Swipe L24→L16, Taunt L36→L28, Dragon Pulse L42→L31, Swords Dance L48→L41, Outrage L60→L52, Giga Impact L66→L60 |
| Haxorus | Slam L1, X-Scissor L34, Night Slash L44, Guillotine L48, Giga Impact L60 | False Swipe L24→L16, Taunt L36→L28, Dragon Pulse L42→L31, Swords Dance L54→L41 |
| Cubchoo | Ice Shard L18, Ice Punch L27, Frost Breath L33, Tickle L51, Sheer Cold L56 | Powder Snow L5→L1, Play Nice L15→L1, Bide L9→L4, Icy Wind L13→L8, Fury Swipes L17→L11, Endure L25→L15, Charm L29→L23, Slash L33→L30, Thrash L53→L49 |
| Beartic | Scary Face L1, Ice Shard L18, Ice Punch L27, Frost Breath L33, Submission L39, Bulk Up L51 | Fury Swipes L17→L11, Endure L25→L15, Swagger L29→L23, Slash L33→L30 |
| Cryogonal | Icy Wind L13, Reflect Type L19, Water Pulse L25, Memento L52, Blizzard L55 | Aurora Beam L24→L22, Freeze-Dry L48→L34 |
| Shelmet | Bug Bite L24, Mud Bomb L30, Signal Beam L33, Metal Sound L38, Wide Guard L41 | Acid L4→L3, Bide L8→L5, Curse L13→L8, Struggle Bug L16→L11, Mega Drain L20→L15, Yawn L25→L18, Protect L28→L21, Acid Armor L32→L26, Giga Drain L37→L36, Recover L49→L47, Guard Swap L50→L49, Final Gambit L56→L54 |
| Accelgor | Mud Bomb L30, Signal Beam L33, Spikes L38, Quick Guard L41 | Struggle Bug L16→L11, Mega Drain L20→L15, Swift L25→L18, Me First L28→L21, U-turn L40→L24, Agility L32→L26, Giga Drain L37→L36, Recover L49→L47 |
| Stunfisk | Revenge L16, Shock Wave L19, Electric Terrain L28, Eerie Impulse L49, Recover L52 | Bide L5→L4, Thunder Shock L9→L7, Mud Shot L13→L10, Camouflage L17→L13, Endure L30→L25, Bounce L35→L34, Earth Power L50→L37 |
| Mienfoo | Vacuum Wave L8, Me First L31, Focus Blast L54 | Meditate L5→L1, Detect L9→L5, Fake Out L13→L12, Swift L21→L15, Quick Guard L45→L23, Drain Punch L33→L29, Jump Kick L37→L35, U-turn L41→L38, Aura Sphere L61→L41, Bounce L49→L47 |
| Mienshao | Vacuum Wave L1, Quick Guard L23, Me First L31, Focus Blast L54 | Wide Guard L45→L1, Swift L21→L15, Drain Punch L33→L29, Jump Kick L37→L35, U-turn L41→L38, Bounce L49→L47, High Jump Kick L56→L50 |
| Druddigon | Hone Claws L1, Slam L8, Metal Claw L16, Dragon Rush L46, Iron Head L49 | Bite L9→L4, Scary Face L13→L11, Chip Away L31→L14, Dragon Tail L45→L22, Revenge L35→L29, Night Slash L40→L31, Rock Climb L49→L39, Superpower L55→L53, Outrage L62→L58 |
| Golett | Power-Up Punch L23, Heavy Slam L37, Phantom Force L41 | Mud-Slap L5→L1, Rollout L9→L8, Night Shade L40→L11, Magnitude L30→L15, Mega Punch L25→L20, Curse L45→L30, Hammer Arm L55→L45, Focus Punch L61→L53 |
| Golurk | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Power-Up Punch L23, Bullet Punch L43, Heat Crash L57, Zap Cannon L64 | Rollout L9→L8, Night Shade L40→L11, Magnitude L30→L15, Mega Punch L25→L20, Curse L47→L30, Hammer Arm L54→L45, Earthquake L51→L48 |
| Pawniard | Pursuit L5, Swords Dance L50, Sucker Punch L53, Guillotine L58 | Leer L6→L1, Torment L14→L12, Metal Claw L25→L16, Scary Face L22→L19, Assurance L33→L22, Metal Sound L38→L24, Slash L30→L28, Embargo L41→L34, Iron Defense L46→L37, Night Slash L49→L41, Iron Head L54→L45 |
| Bisharp | Pursuit L1, Swords Dance L50 | Scary Face L20→L19, Assurance L25→L22, Metal Sound L36→L24, Embargo L41→L34, Iron Defense L46→L37, Night Slash L49→L41 |
| Bouffalant | Work Up L13, Headbutt L17, Endure L45, Zen Headbutt L57 | Rage L6→L1, Horn Attack L16→L5, Fury Attack L11→L9, Revenge L26→L25, Thrash L50→L29, Reversal L46→L45, Swords Dance L55→L49, Giga Impact L61→L53 |
| Rufflet | Rock Smash L15, Aerial Ace L20, Revenge L30, Rock Climb L47, Superpower L51 | Wing Attack L10→L9, Hone Claws L14→L12, Scary Face L19→L17, Slash L28→L24, Defog L32→L26, Sky Drop L50→L33, Crush Claw L46→L37, Whirlwind L55→L41, Brave Bird L59→L55, Thrash L64→L58 |
| Braviary | Zen Headbutt L1, Rock Smash L15, Aerial Ace L20, Revenge L30, Rock Climb L47, Final Gambit L62 | Hone Claws L14→L12, Scary Face L19→L17, Slash L28→L24, Defog L32→L26, Sky Drop L48→L33, Crush Claw L46→L37 |
| Vullaby | Bone Club L15, Air Cutter L24, Bounce L33, Foul Play L47, Bone Rush L51 | Pluck L10→L9, Embargo L50→L12, Flatter L19→L17, Feint Attack L23→L20, Defog L32→L26, Dark Pulse L46→L37, Whirlwind L55→L41, Brave Bird L59→L55 |
| Mandibuzz | Block L1, Bone Club L15, Air Cutter L24, Bounce L33, Foul Play L47, Knock Off L62 | Embargo L50→L12, Flatter L19→L17, Feint Attack L23→L20, Defog L32→L26, Dark Pulse L46→L37 |
| Heatmor | Flame Charge L21, Mega Drain L24, Giga Drain L38, Wring Out L42 | Fire Spin L16→L1, Odor Sleuth L6→L4, Bind L11→L6, Fury Swipes L21→L15, Snatch L26→L17, Bug Bite L36→L26, Stockpile L56→L29, Spit Up L56→L29, Swallow L56→L29, Slash L41→L35, Flamethrower L50→L45 |
| Durant | Leech Life L1, Bug Bite L22, Fell Stinger L46, Beat Up L49 | Fury Cutter L17→L5, Entrainment L36→L29, X-Scissor L41→L37 |
| Deino | Assurance L22, Hyper Fang L26, Dark Pulse L54 | Slam L28→L1, Focus Energy L4→L3, Bite L9→L7, Roar L20→L19, Dragon Pulse L32→L30, Work Up L38→L33, Body Slam L48→L42, Scary Face L50→L49 |
| Zweilous | Assurance L22, Hyper Fang L26, Dark Pulse L54 | Slam L28→L1, Roar L20→L19, Dragon Pulse L32→L30, Work Up L38→L33, Body Slam L48→L42, Scary Face L55→L49, Hyper Voice L64→L58, Outrage L71→L64 |
| Hydreigon | Tailwind L1, Assurance L22, Hyper Fang L26, Dark Pulse L54 | Slam L28→L1, Dragon Breath L17→L16, Roar L20→L19, Dragon Pulse L32→L30, Work Up L38→L33, Body Slam L48→L42, Scary Face L55→L49 |
| Larvesta | Leech Life L5, Fire Spin L15, Sunny Day L35, Rage Powder L40 | Flame Charge L30→L10, Bug Bite L40→L25, Flame Wheel L60→L30, Thrash L90→L45, Bug Buzz L70→L50, Amnesia L80→L55, Flare Blitz L100→L65 |
| Volcarona | Tailwind L1, Flame Burst L30, Sunny Day L35, Air Slash L45 | Fire Spin L30→L15, Whirlwind L40→L20, Silver Wind L50→L25 |
| Cobalion | Night Slash L1, Zen Headbutt L1, Metal Sound L1, Vacuum Wave L11, Thunder Fang L21, Flash Cannon L51 |  |
| Terrakion | Night Slash L1, Zen Headbutt L1, Sandstorm L1, Vacuum Wave L11, Bulldoze L21, Rock Blast L51 |  |
| Virizion | Night Slash L1, Zen Headbutt L1, Grassy Terrain L1, Vacuum Wave L11, Air Slash L21, Horn Leech L51 |  |
| Reshiram | Wish L5, Flame Burst L15, Slash L25, Tailwind L35, Fire Blast L60, Earth Power L65 | Noble Roar L15→L1, Ancient Power L64→L10, Dragon Breath L36→L20, Extrasensory L43→L30, Fusion Flare L71→L40, Dragon Pulse L54→L45, Hyper Voice L92→L50, Outrage L85→L75 |
| Zekrom | Wish L5, Thunder Punch L15, Slash L25, Tailwind L35, Thunder L60, Earth Power L65 | Noble Roar L15→L1, Ancient Power L64→L10, Dragon Breath L36→L20, Zen Headbutt L43→L30, Fusion Bolt L71→L40, Dragon Claw L54→L45, Hyper Voice L92→L55, Outrage L85→L75 |
| Kyurem | Mean Look L1, Snatch L5, Icicle Crash L30, Earth Power L65, Sheer Cold L80 | Ancient Power L15→L10, Dragon Breath L29→L20, Slash L36→L25, Scary Face L43→L35, Glaciate L50→L40, Dragon Pulse L57→L45, Endeavor L71→L50, Hyper Voice L92→L55, Blizzard L78→L60, Outrage L85→L75 |
| Genesect | Electroweb L13, Signal Beam L26, Gravity L35, Iron Head L41, Discharge L48, Blaze Kick L53 | Fury Cutter L7→L4, Lock-On L11→L10, Magnet Bomb L22→L16, Slash L29→L21, Metal Sound L33→L23, Self-Destruct L77→L30, Simple Beam L62→L58, Zap Cannon L66→L65 |
| Chespin | Needle Arm L18, Drain Punch L34 | Leech Seed L15→L14, Mud Shot L35→L23 |
| Quilladin | Vine Whip L1, Needle Arm L18, Drain Punch L34 | Leech Seed L15→L14, Mud Shot L39→L23, Take Down L29→L27, Seed Bomb L35→L32, Bulk Up L44→L40, Body Slam L48→L43, Wood Hammer L56→L48, Pain Split L52→L51 |
| Chesnaught | Spike Cannon L1, Vine Whip L1, Mud Shot L23, Seed Bomb L32, Drain Punch L34 | Leech Seed L15→L14, Take Down L29→L27, Bulk Up L48→L40, Body Slam L54→L43, Wood Hammer L66→L48, Pain Split L60→L51, Giga Impact L78→L61 |
| Fennekin | Howl L7, Flame Charge L12, Hex L45 | Lucky Chant L25→L14, Magic Room L46→L23 |
| Braixen | Howl L7, Flame Charge L12, Hex L45 | Ember L5→L1, Lucky Chant L28→L14, Fire Spin L22→L21, Magic Room L56→L23, Psyshock L36→L33 |
| Delphox | Flame Charge L12, Hex L45, Fire Blast L55 | Lucky Chant L28→L14, Fire Spin L22→L21, Magic Room L68→L23, Psyshock L38→L33, Psychic L57→L48, Sunny Day L62→L52 |
| Froakie | Smokescreen L17, Assurance L23, Dive L27, Feint Attack L33, Muddy Water L42 | Round L21→L20 |
| Frogadier | Smokescreen L17, Assurance L23, Dive L27, Feint Attack L33, Muddy Water L42 | Round L23→L20, Smack Down L33→L30 |
| Greninja | Smokescreen L17, Assurance L23, Dive L27, Muddy Water L42, Double Team L50 | Bubble L5→L1, Shadow Sneak L23→L20, Substitute L42→L38, Extrasensory L49→L45, Hydro Pump L68→L54 |
| Bunnelby | Mud Bomb L26, Hammer Arm L50, Mega Kick L55 | Quick Attack L7→L5, Double Slap L10→L8, Mud-Slap L13→L11, Take Down L15→L14, Dig L33→L17, Odor Sleuth L25→L23, Bounce L38→L33, Facade L47→L37, Earthquake L49→L42 |
| Diggersby | Mud Bomb L26, Mega Kick L55 | Quick Attack L7→L1, Double Slap L13→L8, Mud-Slap L13→L11, Take Down L15→L14, Dig L37→L17, Odor Sleuth L27→L23, Flail L32→L30, Bounce L43→L33, Facade L54→L37, Earthquake L57→L42, Super Fang L48→L46 |
| Fletchling | Pluck L20, Take Down L38, Air Slash L42, Brave Bird L54 | Peck L10→L5, Agility L13→L12, Flail L16→L15, Flame Charge L34→L27, Acrobatics L39→L31, Me First L41→L34 |
| Talonflame | Pluck L20, Heat Wave L38, Air Slash L42 | Agility L13→L12, Flail L16→L15, Roost L25→L24, Flame Charge L31→L27, Acrobatics L39→L31, Me First L49→L34, Tailwind L55→L46, Steel Wing L60→L49 |
| Spewpa | Tackle L1 |  |
| Litleo | Snarl L27, Sunny Day L33 | Noble Roar L15→L14, Fire Fang L23→L17, Echoed Voice L33→L20, Incinerate L46→L23 |
| Pyroar | Captivate L1, Snarl L27, Sunny Day L33 | Ember L5→L1, Noble Roar L15→L14, Fire Fang L23→L17, Echoed Voice L33→L20, Incinerate L51→L23, Flamethrower L38→L37, Crunch L42→L41, Hyper Voice L48→L45, Overheat L57→L50 |
| Skiddo | Grassy Terrain L10, Worry Seed L12, Agility L34, Zen Headbutt L40, Earthquake L51 | Vine Whip L7→L4, Tail Whip L9→L7, Take Down L22→L19, Bulldoze L26→L22, Milk Drink L50→L25, Seed Bomb L30→L28, Horn Leech L42→L37 |
| Gogoat | Rock Climb L1, Grassy Terrain L10, Agility L34, Zen Headbutt L40 | Leech Seed L12→L1, Worry Seed L16→L12, Take Down L22→L19, Bulldoze L26→L22, Milk Drink L58→L25, Seed Bomb L30→L28, Horn Leech L47→L37, Leaf Blade L55→L46 |
| Pancham | Work Up L9, Comet Punch L14, Dizzy Punch L20, Drain Punch L27, Taunt L30 | Arm Thrust L7→L6, Circle Throw L25→L24, Sky Uppercut L48→L37 |
| Pangoro | Comet Punch L14, Dizzy Punch L20, Drain Punch L27, Taunt L30, Night Slash L32 | Circle Throw L25→L24, Body Slam L35→L34, Sky Uppercut L52→L37, Parting Shot L48→L45, Sucker Punch L68→L54 |
| Espurr | Reflect L9, Miracle Eye L20 | Confusion L9→L1, Light Screen L13→L11, Psybeam L16→L15, Fake Out L19→L18 |
| Honedge | Sharpen L1, Metal Claw L20, Shadow Claw L32 | Metal Sound L8→L7, Shadow Sneak L20→L11, Autotomize L18→L17, Slash L29→L26, Iron Defense L32→L29 |
| Doublade | Sharpen L1, Metal Claw L20, Shadow Claw L32 | Metal Sound L8→L7, Shadow Sneak L20→L11, Autotomize L18→L17, Slash L29→L26, Iron Defense L32→L29, Power Trick L41→L40, Iron Head L45→L43 |
| Spritzee | Aromatic Mist L18, Uproar L30, Lovely Kiss L42 | Echoed Voice L13→L11, Misty Terrain L42→L22, Psychic L48→L46 |
| Aromatisse | Uproar L30, Lovely Kiss L42 | Echoed Voice L13→L11, Misty Terrain L42→L22, Psychic L48→L46 |
| Swirlix | Double Slap L16, Zen Headbutt L45, Belly Drum L50 | Aromatherapy L26→L24, Energy Ball L36→L31, Cotton Guard L41→L36, Play Rough L49→L39, Wish L45→L42 |
| Slurpuff | Drain Punch L1, Double Slap L16, Zen Headbutt L45, Belly Drum L50 | Aromatherapy L26→L24, Energy Ball L36→L31, Cotton Guard L41→L36, Play Rough L49→L39, Wish L45→L42 |
| Inkay | Punishment L16, Encore L23, Zen Headbutt L47 | Hypnosis L18→L6, Payback L27→L9, Psybeam L21→L11, Pluck L35→L18, Slash L43→L21, Psycho Cut L39→L32, Night Slash L46→L40, Superpower L48→L44 |
| Malamar | Play Rough L1, Punishment L16, Encore L23, Zen Headbutt L47, Sucker Punch L52 | Hypnosis L18→L6, Payback L27→L9, Psybeam L21→L11, Pluck L35→L18, Slash L42→L21, Psycho Cut L39→L32, Night Slash L45→L40 |
| Binacle | Water Gun L1, Fury Swipes L6, Smack Down L9, Rock Slide L26, Rock Blast L39 | Withdraw L7→L3, Fury Cutter L37→L11, Mud-Slap L18→L16, Clamp L20→L19, Rock Polish L24→L21, Hone Claws L32→L28, Night Slash L41→L36, Cross Chop L49→L46 |
| Barbaracle | Dual Chop L1, Water Gun L1, Fury Swipes L6, Smack Down L9, Rock Blast L39, Dive L50 | Withdraw L7→L1, Fury Cutter L37→L11, Mud-Slap L18→L14, Clamp L20→L19, Rock Polish L24→L21, Hone Claws L32→L28, Night Slash L44→L36, Cross Chop L55→L46 |
| Skrelp | Twister L15, Camouflage L17, Double Team L26, Dragon Tail L29, Gunk Shot L50 | Bubble L12→L1, Tail Whip L9→L5, Acid L15→L8, Water Pulse L25→L21, Aqua Tail L35→L34, Dragon Pulse L49→L41 |
| Dragalge | Foul Play L1, Camouflage L17, Double Team L26, Gunk Shot L50, Outrage L54, Dragon Dance L59, Sludge Wave L63 | Bubble L12→L1, Tail Whip L9→L1, Acid L15→L8, Water Pulse L25→L21, Aqua Tail L35→L34, Dragon Pulse L53→L41 |
| Clauncher | Hone Claws L10, Vacuum Wave L22, Aura Sphere L32, Dragon Pulse L39, Agility L42, Dark Pulse L45 | Water Sport L7→L4, Vice Grip L9→L7, Aqua Jet L43→L12, Flail L16→L15, Bubble Beam L20→L17, Smack Down L39→L20, Water Pulse L34→L28 |
| Clawitzer | Hone Claws L10, Vacuum Wave L22, Agility L42, Hyper Beam L55 | Aqua Jet L49→L12, Flail L16→L15, Bubble Beam L20→L17, Smack Down L42→L20, Water Pulse L34→L28, Muddy Water L54→L49 |
| Helioptile | Electric Terrain L16, Swift L22, Mud Bomb L33, Hyper Voice L38, Eerie Impulse L40 | Charge L11→L4, Mud-Slap L13→L9, Quick Attack L17→L13, Parabolic Charge L25→L20, Thunder Wave L31→L25, Electrify L45→L28, Volt Switch L40→L31, Thunderbolt L49→L43 |
| Heliolisk | Pound L1, Tail Whip L1, Thunder Shock L1, Mud-Slap L9, Electric Terrain L16, Swift L22, Thunder Wave L25, Volt Switch L31, Mud Bomb L33, Hyper Voice L38, Thunderbolt L43, Sunny Day L47, Rain Dance L47, Weather Ball L52 |  |
| Tyrunt | Slam L10, Rock Throw L13, Fire Fang L28, Ice Fang L28, Thunder Fang L28, Rock Slide L31, Hyper Fang L41 | Roar L6→L5, Stomp L10→L8, Charm L20→L15, Ancient Power L26→L21, Dragon Tail L30→L24 |
| Tyrantrum | Dragon Rush L1, Slam L10, Rock Throw L13, Fire Fang L28, Ice Fang L28, Thunder Fang L28, Hyper Fang L41, Horn Drill L51, Outrage L55, Giga Impact L63 | Charm L20→L15, Ancient Power L26→L21, Dragon Tail L30→L24 |
| Amaura | Power Gem L36, Ice Beam L39, Moonlight L45 | Mist L18→L3, Rock Throw L10→L6, Icy Wind L13→L9, Round L30→L16, Aurora Beam L20→L19, Ancient Power L26→L22, Avalanche L34→L30, Encore L44→L32, Blizzard L65→L50, Hyper Beam L57→L55 |
| Aurorus | Wide Guard L1, Power Gem L36, Ice Beam L39, Tri Attack L41, Moonlight L45, Hyper Beam L55, Stone Edge L60 | Mist L18→L1, Icy Wind L13→L9, Round L30→L16, Aurora Beam L20→L19, Ancient Power L26→L22, Avalanche L34→L30, Encore L46→L32, Light Screen L50→L47, Blizzard L74→L50 |
| Sylveon | Lucky Chant L1, Jump Kick L1, Confide L1, Sand Attack L4, Double Kick L14, Bite L17, Wrap L25, Amnesia L32, Dazzling Gleam L37, Encore L48, Hyper Voice L52 | Quick Attack L13→L6, Swift L17→L12, Misty Terrain L29→L22 |
| Hawlucha | Submission L1, Rolling Kick L17, Sky Drop L20, Endure L24, Swords Dance L55 | Encore L20→L1, Wing Attack L8→L1, Aerial Ace L16→L11, Endeavor L36→L14, Bounce L32→L31, Feather Dance L40→L34, High Jump Kick L44→L42 |
| Dedenne | Electric Terrain L25, Dazzling Gleam L33, Recycle L38, Discharge L41, Slack Off L46 | Thunder Wave L23→L1, Thunder Shock L7→L5, Charge L11→L8, Charm L14→L11, Nuzzle L20→L16, Entrainment L39→L19, Snore L31→L30 |
| Carbink | Helping Hand L1, Fairy Wind L9, Dazzling Gleam L28, Power Split L48 | Rock Throw L5→L4, Sharpen L8→L6, Stealth Rock L21→L14, Guard Split L27→L17, Ancient Power L31→L20, Light Screen L60→L24, Flail L35→L30, Power Gem L46→L33, Skill Swap L40→L35, Safeguard L70→L37, Moonblast L50→L40, Recover L65→L43, Stone Edge L49→L46 |
| Goomy | Slam L10, Acid Spray L16, Bubble Beam L18, Acid Armor L32, Recover L52, Outrage L60 | Absorb L5→L4, Bide L13→L6, Dragon Pulse L42→L36 |
| Sliggoo | Slam L10, Acid Spray L16, Bubble Beam L18, Acid Armor L32, Recover L52, Outrage L60 | Bide L13→L6, Dragon Pulse L47→L36 |
| Goodra | Slam L10, Acid Spray L16, Bubble Beam L18, Acid Armor L32, Recover L52 | Bide L13→L1, Dragon Pulse L47→L36 |
| Klefki | Iron Head L40, Swagger L47, Metal Burst L50 | Fairy Wind L5→L4, Astonish L8→L6, Metal Sound L12→L9, Spikes L15→L12, Torment L32→L17, Recycle L40→L21, Imprison L36→L23, Mirror Shot L34→L26, Magic Room L44→L29 |
| Phantump | Vine Whip L3, Mega Drain L15, Echoed Voice L17, Hex L24, Pain Split L53 | Ingrain L40→L11, Forest’s Curse L52→L30, Destiny Bond L48→L38 |
| Trevenant | Drain Punch L1, Vine Whip L1, Mega Drain L15, Revenge L17, Hex L24, Shadow Punch L30, Pain Split L53 | Ingrain L40→L11, Forest’s Curse L52→L30, Destiny Bond L48→L38 |
| Bergmite | Powder Snow L1, Skull Bash L33, Iron Defense L36, Crunch L40, Icicle Crash L45 | Sharpen L20→L7, Ice Ball L30→L14, Curse L22→L21, Ice Fang L26→L24, Rapid Spin L35→L26, Avalanche L39→L30 |
| Avalugg | Block L36, Sheer Cold L60 | Ice Shard L5→L1, Sharpen L20→L7, Ice Ball L30→L14, Curse L22→L21, Ice Fang L26→L24, Rapid Spin L35→L26, Avalanche L42→L30, Recover L51→L48, Double-Edge L56→L51 |
| Noibat | Gust L8, Twister L11, Air Cutter L20, Uproar L37, Boomburst L57 | Whirlwind L40→L23, Hurricane L58→L51 |
| Noivern | Leech Life L1, Twister L11, Air Cutter L20, Uproar L37 | Gust L11→L8, Whirlwind L40→L23 |
| Yveltal | Heal Block L1, Leech Life L1, Chip Away L10, Perish Song L20, Destiny Bond L55, Final Gambit L75 | Sky Attack L93→L1, Snarl L18→L15, Sucker Punch L72→L65, Hyper Beam L88→L70 |
| Zygarde | Dragon Tail L25, Dragon Pulse L45, Pain Split L70 | Safeguard L5→L1, Crunch L44→L35, Extreme Speed L59→L50, Coil L72→L60, Outrage L80→L65, Thousand Arrows L82→L75 |
| Diancie | Play Rough L1, Healing Wish L1, Magic Coat L1, Fairy Wind L9, Mirror Coat L30, Dazzling Gleam L33, Power Split L48 | Ancient Power L27→L12, Stealth Rock L18→L14, Guard Split L21→L17, Light Screen L60→L24, Power Gem L40→L28, Safeguard L70→L37, Stone Edge L49→L40, Trick Room L46→L43, Moonblast L50→L46 |
| Volcanion | Fire Spin L1, Whirlpool L1, Leer L4, Flame Burst L26, Scary Face L28, Lava Plume L40, Soak L55 | Stomp L28→L1, Flame Charge L15→L10, Water Pulse L21→L17, Weather Ball L40→L37, Explosion L76→L46, Overheat L65→L60 |
| Unown |  | Ancientpower L47→L1 |
| Clamperl |  | Shell Smash L57→L40 |
| Magnezone |  | Thunder Shock L5→L1, Spark L19→L17, Screech L39→L19, Electro Ball L29→L22, Magnet Rise L53→L28, Discharge L43→L37, Gyro Ball L59→L45 |
| Scatterbug |  | Stun Spore L6→L5, Bug Bite L15→L8 |

</details>

Engine learnset caps may stop adds short of this list (never overflow); Legacy learnset adds never remove a move.

### Planned: evolution changes (52)

- Poliwag → Poliwhirl: level 25 → 18 (yellow)
- Goldeen → Seaking: level 33 → 26 (xy)
- Pineco → Forretress: level 28 → 25 (crystal)
- Ralts → Kirlia: level 20 → 16 (emerald)
- Aron → Lairon: level 32 → 28 (emerald)
- Meditite → Medicham: level 37 → 33 (emerald)
- Trapinch → Vibrava: level 34 → 30 (xy)
- Vibrava → Flygon: level 44 → 42 (emerald)
- Snorunt → Glalie: level 42 → 36 (emerald)
- Swablu → Altaria: level 35 → 30 (xy)
- Sandile → Krokorok: level 28 → 27 (xy)
- Dwebble → Crustle: level 34 → 32 (xy)
- Vanillite → Vanillish: level 35 → 30 (xy)
- Foongus → Amoonguss: level 36 → 34 (xy)
- Klink → Klang: level 38 → 29 (xy)
- Klang → Klinklang: level 49 → 46 (xy)
- Tynamo → Eelektrik: level 36 → 35 (xy)
- Litwick → Lampent: level 34 → 28 (xy)
- Axew → Fraxure: level 36 → 34 (xy)
- Vullaby → Mandibuzz: level 45 → 42 (xy)
- Deino → Zweilous: level 44 → 35 (xy)
- Larvesta → Volcarona: level 59 → 47 (xy)
- Skrelp → Dragalge: level 44 → 37 (xy)
- Goomy → Sliggoo: level 40 → 30 (xy)
- Kadabra → Alakazam: **added** method level (42) (yellow)
- Machoke → Machamp: **added** method level (38) (yellow)
- Graveler → Golem: **added** method level (38) (yellow)
- Haunter → Gengar: **added** method level (42) (yellow)
- Seadra → Kingdra: **added** method item (Dragon Scale) (crystal)
- Porygon → Porygon2: **added** method item (Up-Grade) (crystal)
- Clamperl → Huntail: **added** method item (Deepseatooth) (emerald)
- Clamperl → Gorebyss: **added** method item (Deepseascale) (emerald)
- Rhydon → Rhyperior: **added** method held_day (Protector) (xy)
- Rhydon → Rhyperior: **added** method held_night (Protector) (xy)
- Electabuzz → Electivire: **added** method held_day (Electirizer) (xy)
- Electabuzz → Electivire: **added** method held_night (Electirizer) (xy)
- Magmar → Magmortar: **added** method held_day (Magmarizer) (xy)
- Magmar → Magmortar: **added** method held_night (Magmarizer) (xy)
- Eevee → Glaceon: **added** method item (Dawn Stone) (xy)
- Murkrow → Honchkrow: **added** method move (Beat Up) (xy)
- Porygon2 → Porygon-Z: **added** method item (Dubious Disc) (xy)
- Nosepass → Probopass: **added** method item (Thunder Stone) (xy)
- Dusclops → Dusknoir: **added** method held_night (Reaper Cloth) (xy)
- Boldore → Gigalith: **added** method level (40) (xy)
- Gurdurr → Conkeldurr: **added** method level (40) (xy)
- Karrablast → Escavalier: **added** method party (Shelmet) (xy)
- Karrablast → Escavalier: **added** method party (Accelgor) (xy)
- Shelmet → Accelgor: **added** method party (Karrablast) (xy)
- Shelmet → Accelgor: **added** method party (Escavalier) (xy)
- Swirlix → Slurpuff: **added** method item (Whipped Dream) (xy)
- Inkay → Malamar: **added** method move (Topsy-Turvy) (xy)
- Phantump → Trevenant: **added** method move (Forest’s Curse) (xy)

Skipped (engine lacks it): Tyrogue -> Hitmontop: item Brick Piece not found in this engine; Lampent -> Chandelure: engine has no "level_night" method (no probe species uses it)
