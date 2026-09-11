-- LIVE PC-exit e2e on the TEST-ONLY ROM (build/radicalred_cm_pctest.gba, built
-- by tools/tests/build_pc_testrom.py).
--
-- ../game_plans/rowe_parity.md §13.33 item 1. The PC-exit hook shipped in all
-- four GBA games on STATIC evidence alone; Seaglass got the first live layer on
-- 2026-09-10 and this is the port. §13.20 is why it matters: four live layers in
-- three repos were once found dead behind a fully green static suite.
--
-- From /tmp/rr_ss_bedroom.ss (the same checkpoint the egg layer uses) we face
-- the console at (6,5) and answer Yes. In the test ROM that branch runs
--   giveegg 60 ; giveegg 60 ; setvar 0x8004,0 ; <inline hatch> ; goto 0x081A6A22
-- and everything from that goto onward is SHIPPED, unmodified: the overlay, the
-- replayed `special 0x3C` + `waitstate` that opens the storage system and waits
-- for it to close, and the `callnative CM_SweepPartyToPC` that runs when it
-- does. The hatch is fixture, not the thing under test -- it is how an
-- off-roster mon gets into the party at all, since the gift gate boxes an
-- off-roster gift on the way in and eggs are exempt everywhere.
--
-- ⚠️⚠️ TWO eggs, because the bedroom is before the starter and the party is
-- empty: the sweep never empties the party, so with one egg the hatchling would
-- survive for EVERY character and every run would be identical. The second egg
-- is the anchor -- exempt AND a keeper -- which puts the hatchling's fate back
-- on the roster.
--
-- ⭐ THE ASSERTION IS A SWAP, NOT A COUNT. We latch the hatching egg's
-- personality before the hatch and afterwards require that exact 32-bit value to
-- be in the PC (enforced) or still in the party (control). A count alone also
-- holds when neither the give nor the sweep happened.
--
-- ⭐ Poliwag 60 is the same discriminator the egg layer uses: ON Misty's roster,
-- OFF Red's, so one species covers all three cases. ⚠️ Unlike Seaglass, nothing
-- here is inferred from the egg layer's OUTCOME -- that inference is exactly
-- what went wrong there (§13.32); it is the same species chosen for the same
-- measured reason.
--
-- Env: CM_ON (1/0), CM_CHAR, EXPECT (box|party), CM_SWEEP_ADDR (derived from
-- build/character_mode.elf by the runner -- never hardcoded: it moves on every
-- shim rebuild, and a stale breakpoint would report "the PC exit never reached
-- the sweep" on a ROM where it plainly did). Needs MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"

local CM_ON   = (os.getenv("CM_ON") == "1")
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT  = os.getenv("EXPECT") or "box"
local SWEEP   = tonumber(os.getenv("CM_SWEEP_ADDR") or "0")
local PREFIX  = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_pc"

-- ⭐ The storage system's OWN handler, gSpecials[0x3C], passed in by the runner
-- (derived from the built ROM's table -- never hardcoded here). Breakpointing it
-- is what turns "the script ran" into "the PC opened": if `special 0x3C` did
-- nothing, the waitstate would release at once, the sweep would still fire, and
-- the hook would look perfectly green while never having involved a PC at all.
-- It also gives a CLEAN measure of how long the UI was up -- measuring from the
-- hatch instead would fold the whole hatch scene into the number.
local PSS = tonumber(os.getenv("CM_PSS_ADDR") or "0")
local MIN_UI_FRAMES = 60

local gPokemonStoragePtr = 0x03005010
local STORAGE_SCAN_BYTES = 0x8600

local function inStorage(pers)
    local base = emu:read32(gPokemonStoragePtr)
    if base < 0x02000000 or base >= 0x02040000 then return nil end
    for off = 0, STORAGE_SCAN_BYTES - 4 do
        if emu:read8(base + off) == (pers & 0xFF)
            and emu:read8(base + off + 1) == ((pers >> 8) & 0xFF)
            and emu:read8(base + off + 2) == ((pers >> 16) & 0xFF)
            and emu:read8(base + off + 3) == ((pers >> 24) & 0xFF) then
            return off
        end
    end
    return nil
end

local function inParty(pers)
    for i = 0, 5 do
        if emu:read32(H.gPlayerParty + i * H.PARTY_STRIDE) == pers then return i end
    end
    return nil
end

local egg = {}
local swept, sweptParty, pssAt = nil, nil, nil
if PSS ~= 0 then
    H.breakpoint("pss", PSS, function(fr)
        if pssAt == nil then
            pssAt = fr
            H.log(("storage system special entered f=%d"):format(fr))
        end
    end)
end
if SWEEP ~= 0 then
    -- Prove the SHIPPED tail was reached. The sweep sits after the replayed
    -- waitstate, so its entry firing means the overlay's goto landed, the
    -- storage system opened, and it closed again -- the whole hook, in order.
    H.breakpoint("sweep", SWEEP, function(fr)
        if swept == nil then
            swept = fr
            sweptParty = emu:read8(H.gPlayerPartyCount)
            H.log(("CM_SweepPartyToPC entered f=%d party=%d"):format(
                fr, sweptParty))
        end
    end)
end

local step, at, mashAt, endAt, hatchedAt, shotOpen = "load", 0, nil, nil, nil, false
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        if CM_ON then H.cmOn(); H.setCharId(CM_CHAR) else H.cmOff() end
        H.log(("start party=%d cm=%s char=%d"):format(
            emu:read8(H.gPlayerPartyCount), tostring(H.cmIsOn()), H.getCharId()))
        emu:addKey(K.UP)                 -- face the console at (6,5)
        step, at = "faced", f
    elseif step == "faced" and f - at == 20 then
        emu:clearKey(K.UP); step, at = "talk", f
    elseif step == "talk" and f - at == 30 then
        emu:addKey(K.A); step, at = "talk2", f
    elseif step == "talk2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        emu:addKey(K.A)                  -- answer Yes -> the test entry script
        step, at = "yes2", f
    elseif step == "yes2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "running", f
        mashAt = f + 30
    end
end)

-- ⚠️ B, NOT A, from here on, and for TWO reasons now. B advances the hatch
-- msgbox and DECLINES the nickname prompt (A opens the naming screen and the
-- run wedges in a keyboard it cannot leave), and B is also what backs out of the
-- storage system -- where A would dive INTO a box, with no route back out.
--
-- ⭐ AND THE MASH PAUSES WHILE THE PC IS OPEN. Left running, it backs straight
-- out of the storage menu in the same frame it appears -- measured: 29 frames
-- from the special to the sweep, which is real but makes the open window an
-- accident of the mash cadence rather than something the layer controls. Pausing
-- for HOLD_OPEN frames makes "the PC was genuinely open" a deterministic,
-- assertable fact and gives the screenshot something to photograph.
local HOLD_OPEN = 90
H.onFrame(function(f)
    if step ~= "running" or mashAt == nil then return end
    if pssAt and f < pssAt + HOLD_OPEN then emu:clearKey(K.B); return end
    if f >= mashAt then
        if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
    end
end)

-- Latch the hatching egg (party slot 0) the moment both eggs exist, and note
-- when it stops being an egg -- that is the moment the PC script is entered, so
-- it is the baseline the storage-UI gap is measured from.
H.onFrame(function(f)
    if step ~= "running" then return end
    if not egg.pers and emu:read8(H.gPlayerPartyCount) == 2 then
        local p = emu:read32(H.gPlayerParty)
        if p ~= 0 then
            egg.pers = p
            egg.sanity = emu:read8(H.gPlayerParty + 19)
            egg.count = 2
            H.log(("eggs latched f=%d slot0 pers=0x%08X sanity=0x%02X"):format(
                f, p, egg.sanity))
        end
    end
    if egg.pers and hatchedAt == nil
        and emu:read32(H.gPlayerParty) == egg.pers
        and (emu:read8(H.gPlayerParty + 19) & 0x04) == 0 then
        hatchedAt = f
        H.log(("hatched f=%d -- the PC script is entered from here"):format(f))
    end
    if pssAt and os.getenv("CM_PROBE") then
        local d = f - pssAt
        if d == 5 or d == 10 or d == 15 or d == 20 or d == 25 then
            emu:screenshot(("%s_probe_%02d.png"):format(PREFIX, d))
        end
    end
    if pssAt and not shotOpen and f == pssAt + 45 then
        shotOpen = true
        emu:screenshot(PREFIX .. "_" .. EXPECT .. "_open.png")
    end
end)

H.onFrame(function(f)
    if swept and endAt == nil then endAt = f + 90 end
    if endAt and f == endAt then
        emu:screenshot(PREFIX .. "_" .. EXPECT .. ".png")
        local pers = egg.pers or 0
        local box = (pers ~= 0) and inStorage(pers) or nil
        local slot = (pers ~= 0) and inParty(pers) or nil
        H.log(("after: party=%d pers=0x%08X box=%s partySlot=%s"):format(
            emu:read8(H.gPlayerPartyCount), pers, tostring(box), tostring(slot)))
        H.log(("hatched f=%s, storage special f=%s, sweep f=%s -- UI up for %s"):
            format(tostring(hatchedAt), tostring(pssAt), tostring(swept),
                   tostring(swept and pssAt and (swept - pssAt))))

        H.assertTrue("giveegg put two eggs in the party", egg.count == 2)
        H.assertTrue("the hatching party member WAS an egg (sanity bit 2)",
                     (egg.sanity or 0) & 0x04 ~= 0)
        H.assertTrue("closing the PC reached the shipped sweep", swept ~= nil)
        H.assertTrue("the storage system special really ran, BEFORE the sweep",
                     pssAt ~= nil and swept ~= nil and pssAt < swept)
        H.assertTrue("...and the PC stayed open long enough to be real "
                     .. "(not a no-op special)",
                     swept ~= nil and pssAt ~= nil
                     and (swept - pssAt) >= MIN_UI_FRAMES)
        if EXPECT == "box" then
            H.assertTrue("the off-roster hatchling's personality is in the PC",
                         box ~= nil)
            H.assertTrue("...and no longer in the party", slot == nil)
        else
            H.assertTrue("the hatchling's personality is still in the party",
                         slot ~= nil)
            H.assertTrue("...and not in the PC", box == nil)
        end
        H.finish()
    end
    if f == 4000 and endAt == nil then
        emu:screenshot(PREFIX .. "_timeout.png")
        H.log("timeout: step=" .. step .. " swept=" .. tostring(swept)
              .. " egg=" .. tostring(egg.pers)
              .. " hatchedAt=" .. tostring(hatchedAt)
              .. " pssAt=" .. tostring(pssAt))
        H.assertTrue("closing the PC reached the shipped sweep (timeout)", false)
        H.finish()
    end
end)
