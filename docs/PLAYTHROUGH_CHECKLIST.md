# Character Mode — Full Playthrough Verification Checklist

Print/keep this open while playing. **Every automated layer is green — 8 of them,
all observed on this exact ROM** (verify_artifacts ALL PASS, audit_conflicts 9/9,
verify_docs OK, consistency clean, boot smoke 4/4, shim unit 9/9, wild encounter
21/21, mugshot render 4/4). This playthrough is the one seam automation cannot
cover: the real script interpreter, real input, and hours of ordinary gameplay.

**Build under test:** `build/radicalred_cm.bps` (168,606 B) over a clean v4.1 ROM,
sha1 `964f951a0fdaf209e4ea1344883ef0d557bb3a80`.
**238 characters in the table, 210 offered by the menu, 28 hidden below the
playability threshold.** The code chain holds 213 entries (3 debug + 210).

**How to log a problem**: note the checklist item number, make a savestate
immediately, and record: active character code, the species involved, your
location, party count, and what you expected vs. what happened. Savestate + those
five facts is enough to reproduce and fix anything.

> ⚠️ **Fixtures in this file are DERIVED from the built ROM, not remembered.** An
> earlier revision told testers Caterpie was on Red's roster and Pidgey/Rattata
> were off — both backwards after the roster audit, which would have produced two
> false bug reports. If you rebuild with a changed roster, re-derive §3's lists
> before using them (`tools/character_mode/rosters_expanded.bin` is the authority).

---

## 0. Setup (before starting)

- [ ] Applied `radicalred_cm.bps` to a clean v4.1 ROM — or use the prebuilt
      `build/radicalred_cm.gba` directly.
- [ ] Playing on mGBA (0.10.x) with a fresh `.sav` (don't reuse an old save).
- [ ] Optional but recommended: enable periodic savestates so any crash can be
      rewound and reproduced.

## 1. Boot + activation (first 5 minutes)

- [ ] **1.1** Game boots to title screen, intro plays, New Game starts normally
      (automated boot smoke covers 15 s; you're confirming the rest).
- [ ] **1.2** In your bedroom (new-game start room), interact with the **game
      console at tile (6,5)** → "Would you like to put in a cheat code?" → Yes →
      naming screen opens.
- [ ] **1.3** Type `Red` (codes are exact: case-sensitive, punctuation stripped —
      e.g. Lt. Surge is `LtSurge`, Crasher Wake is `CrasherWake`; full list in
      `README.md`). Expect the Character Mode confirmation msgbox **and a Lv5
      Pikachu** in your party.
- [ ] **1.4** **A 64×64 mugshot of Red is drawn beside that confirmation message**,
      and disappears when you dismiss the box. Select again → still exactly **one**
      mugshot, not two stacked.
- [ ] **1.5** Pick a character with **no staged art** (e.g. `Ash`, `Kris`, `Maxie`,
      `Paul`) → the message shows with **no mugshot and no glitch**. 54 of the 210
      offered characters take this path; silence is the designed behaviour.
- [ ] **1.6** RR's own native codes still work from the same console (try `DexAll`
      or whichever you'd normally use) — our chain only runs on their no-match
      fallthrough.
- [ ] **1.7** Typing garbage (e.g. `zzzz`) still reaches RR's original "Invalid
      code." handler — no hang, no freeze at the end of the 213-entry chain.

## 2. Threshold gating — hidden characters (NEW, 2 minutes)

28 characters have fewer than six fully-evolved Pokémon in this game's dex and no
legendary to exempt them, so the menu does not offer them. They keep their table
slot, because saves store the character **index**.

- [ ] **2.1** Type `Tracey` → must be **rejected exactly like an unknown code**
      ("Invalid code."), with no Character Mode message and no gift. Same for
      `Drew` and `Viola`.
- [ ] **2.2** Immediately after a rejection, type a valid code (`Red`) → works
      normally. (Confirms the rejection did not leave the script stuck.)
- [ ] **2.3** None of the 28 appear in `README.md`'s code tables or in
      `ROSTERS.md`. Spot-check two.
- [ ] **2.4** **The important one — hidden ≠ broken.** If you have a save made
      *before* this build in which a now-hidden character was active, load it: the
      game must run and **still enforce that character's roster**. Only *selection*
      is gated, never enforcement. If you have no such save, skip and note it.

## 3. Early game — core enforcement (Pallet → first badge)

Red's real roster status, read out of the injected bitmaps:

| on-roster (should join the party) | off-roster (should go to the PC) |
|---|---|
| Pikachu, Pidgey, Rattata, Spearow, Nidoran♂, Nidoran♀, Gastly, Magikarp, and all three Kanto starters | Caterpie, Weedle, Sandshrew, Zubat, Oddish, Abra, Geodude |

Radical Red's encounter tables are heavily rebalanced, so catch whichever of these
you actually meet rather than going to a vanilla location for it.

- [ ] **3.1** Oak's lab starter: all three Kanto starters are on-roster → the one
      you choose **joins the party** normally.
- [ ] **3.2** Catch an **on-roster** wild mon (Pikachu / Pidgey / Rattata) → joins
      party or PC normally, full "Gotcha!" flow, Pokédex registers.
- [ ] **3.3** Catch an **off-roster** wild mon (Caterpie / Weedle / Sandshrew) →
      **sent to the PC** instead of the party, no crash, ball consumed normally,
      Pokédex still registers the catch.
- [ ] **3.4** Confirm the off-roster catch actually IS in the PC box.
- [ ] **3.5** Save, quit the emulator entirely, reload: **party is intact** (RR
      rebuilds the party from save through the deliberately ungated restore path)
      and **Character Mode is still active** (catch another off-roster mon → PC).

## 4. Wild encounters — the roster override and legendaries

Two independent rolls replace the species the area would normally give: **1%
legendary**, else **10% a non-legendary roster member**, else the game's own
table. The level is always the area's own; the evolution stage is matched to it.
`ENCOUNTERS.md` lists every character's exact pools.

- [ ] **4.1** As Red, over an hour or so of grass/surf/fishing, you should see
      roughly **1 in 10** encounters be something from his roster that the area
      would not normally produce, at a sensible level for the area (his pool has
      33 families). Flag anything wildly off-level.
- [ ] **4.2** These override encounters are **catchable and on-roster**, so they
      join the party normally.
- [ ] **4.3** **Legendaries — passive watch, ~1 in 100 encounters.** Red's pool is
      Articuno, Entei, Mewtwo, Moltres, Raikou, Suicune, Zapdos, **once each**.
      Do not grind for this; the mechanism is proven deterministically by the
      automated suite. Just note it if one appears, and that it appears at the
      area's level, not level 70.
- [ ] **4.4** If you do catch a wild legendary, it should **stop appearing** from
      then on (the pool is filtered on the Pokédex *caught* flag).
- [ ] **4.5** *(Optional, and the fastest way to actually see §4.3.)* Start a
      throwaway save as `Cogita` (roster = Enamorus only, **repeatable**) or
      `Tobias` (Darkrai + Latios, repeatable). They have no non-legendary pool at
      all, so every override they get is a legendary and it never retires. This is
      also the check that **Cogita is no longer able to catch nothing all run** —
      the bug this feature was written to fix.

## 5. Debug-code spot checks (any time, 2 minutes)

- [ ] **5.1** `CMDbgGive1` (gives Pikachu): as Red → **joins party** (on-roster
      gift path).
- [ ] **5.2** `CMDbgGive2` → **goes to PC** (off-roster gift path). **Do not expect
      a specific species**: the build derives it from character 0's own bitmap and
      prints it at build time (currently Caterpie). It used to be hardcoded to
      Meowth, which later joined Red's roster — so the code silently became a
      no-op while this step still told testers to expect a PC transfer.
- [ ] **5.3** `CMDbgOff` → mode off; catch/receive anything → joins party ungated.
      Re-enter `Red` afterwards to resume (note: this re-gifts the Lv5 signature —
      expected).

## 6. Throughout the run — every acquisition channel

Check each the first time the playthrough naturally offers one:

- [ ] **6.1** Scripted gift mon (fossil revival, in-game gift NPCs) — off-roster →
      PC; on-roster → party.
- [ ] **6.2** **Egg** received (gift egg or daycare) → an egg always enters the
      party even if the species is off-roster — **deliberate** (eggs exempt), not a
      bug. Hatching proceeds normally.
- [ ] **6.3** The **Eternal Flower Floette trade console** (the only live in-game
      trade in v4.1): as Red it must **politely refuse** (sign-style msgbox, no
      trade, no crash, nothing lost). Only Shauna, Lysandre, Goh and Tulip may take
      it. With `CMDbgOff` it should perform the original trade.
- [ ] **6.4** Battle-facility / rental / boss-preview battles: temporary battle
      teams are **unaffected** by roster gating.
- [ ] **6.5** If you use Mystery Gift at all, note what happens — its delivery is
      believed to route through the gated choke point but was never directly
      confirmed. Log whatever you see either way.

## 7. Stress / edge cases (late game or whenever convenient)

- [ ] **7.1** Off-roster catch with a **full party** → still goes to PC cleanly.
- [ ] **7.2** On-roster catch with a full party → normal "sent to PC" vanilla flow
      with correct box messaging.
- [ ] **7.3** *(Optional, late)* Off-roster catch with **all boxes nearly full** →
      graceful "Box is full" handling, no crash.
- [ ] **7.4** Evolve several party mons (incl. stone/trade-item evolutions) —
      evolution is not an acquisition and must be completely unaffected.
- [ ] **7.5** Entering a **second character's code mid-game** switches enforcement
      to the new roster and gifts their signature — expected, but don't do it
      casually mid-run. If you try it, verify the switch took (old-roster species
      now go to PC) and that the new character's mugshot is the one drawn.

## 8. General regression watch (passive, whole run)

Nothing here should differ from stock Radical Red — flag anything that does:

- [ ] **8.1** No crashes, freezes, graphical corruption or garbled text at any
      point — *especially* at catch resolution, gift delivery, and the moment a
      mugshot is drawn or torn down (the hooked instants).
- [ ] **8.2** Saving works everywhere, no save corruption across many save/reload
      cycles.
- [ ] **8.3** RR systems untouched by the patch behave normally: level caps, boss
      fights, DexNav, shops, day-care, move relearner.
- [ ] **8.4** **Character mugshots are installed** (156 of the 210 offered
      characters have one) and appear **only** at the selection console. The
      player's overworld sprite and trainer card are **stock** — the patch
      deliberately touches no engine art table, so real opponents' sprites must be
      unchanged all run. A wrong trainer sprite in any battle is a serious bug.

## 9. Sign-off

- [ ] Full credits roll reached with Character Mode active.
- [ ] Every box above ticked or logged.
- [ ] Report results back → any logged items get fixed, then `CREDITS.md` and the
      remaining sprite work (overworld sheets, back pics) close the project out.
