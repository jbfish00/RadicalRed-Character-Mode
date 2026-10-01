-- LIVE e2e for the link-trade sweep (CM_LinkTradeSweepThenExpand, src/pc_guard.c;
-- verify_artifacts section 19; rowe_parity.md §13.53). Added 2026-09-30.
--
-- A real link trade needs two consoles, which headless mGBA can't provide. What
-- CAN be run for real is the code the hook lives in: CB2_SaveAndEndTrade
-- (0x08053E8C), the callback the link trade installs after its animation and
-- evolution. This layer builds the PC-guard fixture (party [Pikachu, Poliwag],
-- both hatched and alive, tools/tests/build_pcguard_testrom.py), then installs
-- that callback at state 0 exactly as CB2_TryLinkTradeEvolution does, and stops
-- at the return of the hooked BL (0x080540F0), before any link traffic.
--
-- ⭐ The SWAP is asserted (which personality went where), and it discriminates:
--   RED   (1):  Pikachu ON,  Poliwag OFF -> Poliwag boxed, Pikachu stays
--   MISTY (10): Pikachu OFF, Poliwag ON  -> Pikachu boxed, Poliwag stays
--   CM off                               -> nothing moves (vanilla)
-- and the --no-link-sweep ROM must FAIL the RED case. The expansion must still
-- happen ("Comm..." in gStringVar4), or the hook broke the screen text.
--
-- Env: CM_ON 1/0, CM_CHAR, EXPECT box1|box0|none, CM_PSS_ADDR, CM_SHIM_ADDR
-- (0 on the no-hook ROM), CM_SHOT_PREFIX. Needs MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"
local CM_ON   = (os.getenv("CM_ON") == "1")
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT  = os.getenv("EXPECT") or "box1"
local PSS     = tonumber(os.getenv("CM_PSS_ADDR") or "0")
local SHIM    = tonumber(os.getenv("CM_SHIM_ADDR") or "0")
local PREFIX  = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_linksweep"

local gMain_callback2    = 0x030030F4
local gMain_state        = 0x030030F0 + 0x438
local CB2_SaveAndEndTrade = 0x08053E8D
local EXPAND_RETURN      = 0x080540F0     -- just after the hooked BL
local gStringVar4        = 0x02021D18
local gPokemonStoragePtr = 0x03005010
local STORAGE_SCAN_BYTES = 0x8600

local function inStorage(pers)
    local base = emu:read32(gPokemonStoragePtr)
    if pers == 0 or base < 0x02000000 or base >= 0x02040000 then return nil end
    for off = 0, STORAGE_SCAN_BYTES - 4 do
        if emu:read32(base + off) == pers then return off end
    end
    return nil
end
local function inParty(pers)
    for i = 0, 5 do
        if emu:read32(H.gPlayerParty + i * H.PARTY_STRIDE) == pers then return i end
    end
    return nil
end

local pssAt, p0, p1, installed, shimHits, done = nil, nil, nil, nil, 0, false
H.breakpoint("pss", PSS, function(fr)
    if pssAt == nil then pssAt = fr end
end)
if SHIM ~= 0 then
    H.breakpoint("shim", SHIM, function() shimHits = shimHits + 1 end)
end
H.breakpoint("expand_return", EXPAND_RETURN, function(fr)
    if done or not installed then return end
    done = true
    emu:screenshot(PREFIX .. "_after.png")
    local s = emu:read8(gStringVar4) .. "," .. emu:read8(gStringVar4 + 1)
              .. "," .. emu:read8(gStringVar4 + 2) .. "," .. emu:read8(gStringVar4 + 3)
    H.log(("RESULT f=%d shimHits=%d party=%d p0 party=%s pc=%s  p1 party=%s pc=%s  str=%s"):format(
        fr, shimHits, emu:read8(H.gPlayerPartyCount),
        tostring(inParty(p0)), tostring(inStorage(p0)),
        tostring(inParty(p1)), tostring(inStorage(p1)), s))
    H.assertTrue("state 0 of CB2_SaveAndEndTrade reached the expand BL", true)
    H.assertTrue("gStringVar4 was still expanded (\"Comm\")",
        emu:read8(gStringVar4) == 0xBD and emu:read8(gStringVar4 + 1) == 0xE3
        and emu:read8(gStringVar4 + 2) == 0xE1 and emu:read8(gStringVar4 + 3) == 0xE1)
    if EXPECT == "box1" then
        H.assertTrue("Pikachu (on the roster) stayed in the party", inParty(p0) ~= nil)
        H.assertTrue("Poliwag (off the roster) left the party", inParty(p1) == nil)
        H.assertTrue("...and is in the PC", inStorage(p1) ~= nil)
    elseif EXPECT == "box0" then
        H.assertTrue("Poliwag (on the roster) stayed in the party", inParty(p1) ~= nil)
        H.assertTrue("Pikachu (off the roster) left the party", inParty(p0) == nil)
        H.assertTrue("...and is in the PC", inStorage(p0) ~= nil)
    else
        H.assertTrue("Pikachu stayed in the party", inParty(p0) ~= nil)
        H.assertTrue("Poliwag stayed in the party", inParty(p1) ~= nil)
        H.assertTrue("party count is still 2", emu:read8(H.gPlayerPartyCount) == 2)
    end
    H.finish()
end)

-- The proven console route from cm_pc_guard_test.lua.
local step, at, mashAt = "load", 0, nil
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        if CM_ON then H.cmOn(); H.setCharId(CM_CHAR) else H.cmOff() end
        emu:addKey(K.UP)
        step, at = "faced", f
    elseif step == "faced" and f - at == 20 then
        emu:clearKey(K.UP); step, at = "talk", f
    elseif step == "talk" and f - at == 30 then
        emu:addKey(K.A); step, at = "talk2", f
    elseif step == "talk2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        emu:addKey(K.A); step, at = "yes2", f
    elseif step == "yes2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "running", f
        mashAt = f + 30
    end
end)

-- B through both hatch scenes until the PC opens; then hand over to the trade
-- ender, the way CB2_TryLinkTradeEvolution does (SetMainCallback2 = state 0).
H.onFrame(function(f)
    if step ~= "running" or mashAt == nil or installed then return end
    if not pssAt then
        if f >= mashAt then
            if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
        end
        return
    end
    emu:clearKey(K.B)
    if f < pssAt + 60 then return end
    p0 = emu:read32(H.gPlayerParty)
    p1 = emu:read32(H.gPlayerParty + H.PARTY_STRIDE)
    H.log(("fixture f=%d party=%d p0=0x%08X p1=0x%08X cm=%s char=%d"):format(
        f, emu:read8(H.gPlayerPartyCount), p0, p1, tostring(H.cmIsOn()), H.getCharId()))
    H.assertTrue("fixture: party of 2 hatched mons, the PC open",
        emu:read8(H.gPlayerPartyCount) == 2 and p0 ~= 0 and p1 ~= 0)
    emu:screenshot(PREFIX .. "_before.png")
    emu:write8(gMain_state, 0)
    emu:write32(gMain_callback2, CB2_SaveAndEndTrade)
    installed = f
end)

H.onFrame(function(f)
    if f == 7000 and not done then
        H.log("timeout: step=" .. step .. " pssAt=" .. tostring(pssAt)
              .. " installed=" .. tostring(installed))
        H.assertTrue("reached CB2_SaveAndEndTrade's expand BL (timeout)", false)
        H.finish()
    end
end)
