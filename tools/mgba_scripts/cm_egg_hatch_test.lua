-- LIVE egg-hatch e2e on the TEST-ONLY ROM (build/radicalred_cm_eggtest.gba,
-- built by tools/tests/build_egg_testrom.py).
--
-- ../game_plans/rowe_parity.md §13.21 item 1: the hatch hook was verified
-- statically and by every pre-existing live layer, but no hatch had ever been
-- WALKED in an emulator here. This walks one -- and it matters most in this
-- game, which has 33 reachable gift eggs including a random "Wonder Egg".
--
-- From /tmp/rr_ss_bedroom.ss (the same checkpoint mugshot_shot.lua uses) we
-- face the console at (6,5) and answer Yes. In the test ROM that branch runs
--   giveegg 60 ; giveegg 60 ; setvar 0x8004,0 ; goto <hatch script>
-- and everything from that goto onward is SHIPPED, unmodified: the spliced
-- tail, the replayed special 0xC2 / waitstate / release, and the callnative
-- into CM_SweepPartyToPC.
--
-- ⚠️ TWO eggs, because the bedroom is before the starter and the party is
-- empty: the sweep's never-empty rule would otherwise KEEP the off-roster
-- hatchling, correctly, and prove nothing. The second egg is the anchor -- eggs
-- are exempt from the sweep, so it satisfies that rule without being a roster
-- decision itself.
--
-- ⭐ THE ASSERTION IS A SWAP, NOT A COUNT. We capture the hatching egg's
-- personality before the hatch and afterwards require that exact 32-bit value
-- to be either in the PC (enforced) or still in the party (control). A count
-- alone also holds when neither the give nor the sweep happened.
--
-- Env: CM_ON (1/0), CM_CHAR, EXPECT (box|party), CM_SWEEP_ADDR (derived from
-- build/character_mode.elf by the runner -- never hardcoded: it moves on every
-- shim rebuild, and a stale breakpoint would report "the tail was never
-- reached" on a ROM where it plainly was). Needs MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"

local CM_ON   = (os.getenv("CM_ON") == "1")
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT  = os.getenv("EXPECT") or "box"
local SWEEP   = tonumber(os.getenv("CM_SWEEP_ADDR") or "0")
local PREFIX  = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_egg"

-- gPokemonStoragePtr: the third pointer of FireRed's save-block trio, beside
-- the gSaveBlock1Ptr this harness already anchors on. Read as a pointer and
-- range-checked at runtime rather than trusted, and the scan below is
-- byte-wise, so nothing here depends on where inside struct PokemonStorage the
-- box array starts or how it is strided -- only that a boxed mon still carries
-- its personality as its first four bytes.
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
local swept = nil
if SWEEP ~= 0 then
    -- Prove the SHIPPED tail was reached. The sweep is the last command in it,
    -- so its entry firing means the goto landed, the replayed hatch ran and the
    -- waitstate released -- the whole hook, in order.
    H.breakpoint("sweep", SWEEP, function(fr)
        if swept == nil then
            swept = fr
            H.log(("CM_SweepPartyToPC entered f=%d party=%d"):format(
                fr, emu:read8(H.gPlayerPartyCount)))
        end
    end)
end

local step, at, mashAt, endAt = "load", 0, nil, nil
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
        emu:clearKey(K.A); step, at = "hatching", f
        mashAt = f + 30
    end
end)

-- ⚠️ B, NOT A, from here on. B advances the hatch msgbox just as A does, and --
-- the reason it must be B -- DECLINES the nickname prompt. Mashing A there
-- opens the naming screen and the run wedges in a keyboard it cannot leave.
H.onFrame(function(f)
    if step ~= "hatching" or mashAt == nil then return end
    if f >= mashAt then
        if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
    end
end)

-- Latch the hatching egg (party slot 0) the moment both eggs exist.
H.onFrame(function(f)
    if egg.pers or step ~= "hatching" then return end
    if emu:read8(H.gPlayerPartyCount) == 2 then
        local p = emu:read32(H.gPlayerParty)
        if p ~= 0 then
            egg.pers = p
            egg.sanity = emu:read8(H.gPlayerParty + 19)
            egg.count = 2
            H.log(("eggs latched f=%d slot0 pers=0x%08X sanity=0x%02X"):format(
                f, p, egg.sanity))
        end
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

        H.assertTrue("giveegg put two eggs in the party", egg.count == 2)
        H.assertTrue("the hatching party member IS an egg (sanity bit 2)",
                     (egg.sanity or 0) & 0x04 ~= 0)
        H.assertTrue("the shipped hatch tail reached the sweep", swept ~= nil)
        if EXPECT == "box" then
            H.assertTrue("the hatchling's personality is in the PC", box ~= nil)
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
              .. " egg=" .. tostring(egg.pers))
        H.assertTrue("the shipped hatch tail reached the sweep (timeout)", false)
        H.finish()
    end
end)
