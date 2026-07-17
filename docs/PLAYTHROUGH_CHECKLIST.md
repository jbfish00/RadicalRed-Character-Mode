# Character Mode — Full Playthrough Verification Checklist

Print/keep this open while playing. Every automated layer is green (54 checks
across 4 layers, see `CLAUDE.md` v12–v15) — this playthrough is the one seam
automation can't cover: the real script interpreter, real input, and hours of
ordinary gameplay on the patched ROM.

**How to log a problem**: note the checklist item number, make a savestate
immediately, and record: active character code, the species involved, your
location, party count, and what you expected vs. what happened. Savestate +
those five facts is enough to reproduce and fix anything.

---

## 0. Setup (before starting)

- [ ] Applied `radicalred_cm.bps` to a clean v4.1 ROM (sha1
      `964f951a0fdaf209e4ea1344883ef0d557bb3a80`) — or use the prebuilt
      `build/radicalred_cm.gba` directly.
- [ ] Playing on mGBA (0.10.x) with a fresh `.sav` (don't reuse an old save).
- [ ] Optional but recommended: enable periodic savestates so any crash can be
      rewound and reproduced.

## 1. Boot + activation (first 5 minutes)

- [ ] **1.1** Game boots to title screen, intro plays, New Game starts
      normally (automated boot smoke covers 15 s; you're confirming the rest).
- [ ] **1.2** In your bedroom (new-game start room), interact with the **game
      console at tile (6,5)** → "Would you like to put in a cheat code?" → Yes
      → naming screen opens.
- [ ] **1.3** Type `Red` (codes are exact: case-sensitive, punctuation
      stripped — e.g. Lt. Surge is `LtSurge`, Crasher Wake is `CrasherWake`;
      full list in `README.md`). Expect the Character Mode confirmation msgbox
      **and a Lv5 Pikachu** in your party.
- [ ] **1.4** RR's own native codes still work from the same console (try
      `DexAll` or whichever you'd normally use) — our chain only runs on
      their no-match fallthrough.
- [ ] **1.5** Typing garbage (e.g. `zzzz`) still reaches RR's original
      "Invalid code." handler — no hang, no freeze at the end of our
      184-entry chain.

## 2. Early game — core enforcement (Pallet → first badge)

- [ ] **2.1** Oak's lab starter: as Red, all three Kanto starters are
      on-roster → chosen starter **joins the party** normally.
- [ ] **2.2** Catch an **on-roster** wild mon (as Red: **Caterpie** or
      **Pikachu**, both in Viridian Forest and on his roster) → joins
      party/PC normally, full "Gotcha!" flow, Pokédex registers.
- [ ] **2.3** Catch an **off-roster** wild mon (as Red: **Pidgey** or
      **Rattata** — neither is on his roster) → it is **sent to the PC**
      instead of joining the party, no crash, ball consumed normally,
      Pokédex still registers the catch.
- [ ] **2.4** Confirm the off-roster catch actually IS in the PC box.
- [ ] **2.5** Save, quit the emulator entirely, reload the save:
      **party is intact** (RR rebuilds the party from save via the ungated
      restore path — this is the deliberate 6th-caller exemption) and
      **Character Mode is still active** (catch another off-roster mon → PC).

## 3. Debug-code spot checks (any time, 2 minutes)

- [ ] **3.1** `CMDbgGive1` (gives Pikachu): as Red → **joins party**
      (on-roster gift path).
- [ ] **3.2** `CMDbgGive2` (gives Meowth): as Red → **goes to PC**
      (off-roster gift path).
- [ ] **3.3** `CMDbgOff` → mode off; catch/receive anything → joins party
      ungated. Re-enter `Red` afterwards to resume (note: this re-gifts the
      Lv5 signature — expected).

## 4. Throughout the run — every acquisition channel

Check each of these the first time the playthrough naturally offers one:

- [ ] **4.1** Scripted gift mon (fossil revival, in-game gift NPCs) —
      off-roster → PC; on-roster → party.
- [ ] **4.2** **Egg** received (gift egg or daycare) → egg always enters the
      party even if the species is off-roster — **this is deliberate**
      (eggs exempt), not a bug. Hatching proceeds normally.
- [ ] **4.3** The **Eternal Flower Floette trade console** (the only live
      in-game trade in v4.1, trades your Florges): with Character Mode on it
      must **politely refuse** (sign-style msgbox, no trade, no crash, no
      Florges lost). With `CMDbgOff` it should perform the original trade.
- [ ] **4.4** Battle-facility / rental / boss-preview battles (if you use
      them): temporary battle teams are **unaffected** by roster gating.
- [ ] **4.5** If you use Mystery Gift at all, note what happens — its
      delivery is believed to route through the gated choke point but was
      never directly confirmed. Any mon it delivers should obey the roster;
      log whatever you see either way.

## 5. Stress / edge cases (late game or whenever convenient)

- [ ] **5.1** Off-roster catch with a **full party** → still goes to PC
      cleanly.
- [ ] **5.2** On-roster catch with a full party → normal "sent to PC" vanilla
      flow with correct box messaging.
- [ ] **5.3** (Optional, late) Off-roster catch with **all boxes nearly
      full** → graceful "Box is full" handling, no crash.
- [ ] **5.4** Evolve several party mons (incl. stone/trade-item evolutions) —
      evolution is not an acquisition and must be completely unaffected.
- [ ] **5.5** Entering a **second character's code mid-game** switches
      enforcement to the new roster and gifts their signature — expected
      behavior, but don't do it casually mid-run; if you try it, verify the
      switch takes effect (old-roster species now go to PC).

## 6. General regression watch (passive, whole run)

Nothing here should differ from stock Radical Red — flag anything that does:

- [ ] **6.1** No crashes, freezes, graphical corruption, or garbled text at
      any point — *especially* at the moment of catch resolution and gift
      delivery (the two hooked instants).
- [ ] **6.2** Saving works everywhere, no save corruption across many
      save/reload cycles.
- [ ] **6.3** RR systems untouched by the patch behave normally: level caps,
      boss fights, DexNav/wild encounters, shops, day-care, move relearner.
- [ ] **6.4** Character trainer sprites are **not installed yet**
      (`sprite_asset_id` placeholder) — the player character looks stock.
      Expected; Phase 3 is the remaining cosmetic work.

## 7. Sign-off

- [ ] Full credits roll reached with Character Mode active.
- [ ] Every box above ticked or logged.
- [ ] Report results back → any logged items get fixed, then Phase 3
      (sprites) + `CREDITS.md` close out the project.
