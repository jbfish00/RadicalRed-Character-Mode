-- LIVE e2e for the PC second guard (CM_PSSLastMonGuard, src/pc_guard.c) on the
-- TEST-ONLY ROM build/radicalred_cm_pcguard.gba
-- (tools/tests/build_pcguard_testrom.py). Ported 2026-09-29 from the
-- Seaglass/Lazarus layers.
--
-- From the bedroom checkpoint (empty party): face the console, Yes -> the test
-- script gives Pikachu + Poliwag eggs, hatches BOTH inline, and opens the
-- SHIPPED PC script. Party [Pikachu, Poliwag], both alive. Then: DEPOSIT,
-- slot 0 (Pikachu), STORE, confirm.
--
-- ⭐ With an alive Poliwag beside it VANILLA ALLOWS depositing Pikachu, so only
-- the guard can refuse -- and only for a character with Pikachu but not
-- Poliwag:
--   RED   (1):  Pikachu ON,  Poliwag OFF -> refused ("That's your last POKeMON!")
--   MISTY (10): Pikachu OFF, Poliwag ON  -> deposited (discrimination)
--   CM off                               -> deposited (control)
-- and the --no-guard ROM must FAIL this layer on the deposit.
--
-- ⭐ The swap is asserted (Pikachu's personality, latched when the eggs land),
-- while the PC is still open -- before the exit sweep runs.
--
-- Env: CM_ON 1/0, CM_CHAR, EXPECT refused|deposited, CM_PSS_ADDR,
-- CM_GUARD_ADDR, CM_SHOT_PREFIX. Needs MGBA_HEADLESS_DEBUGGER=1.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"
local CM_ON   = (os.getenv("CM_ON") == "1")
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT  = os.getenv("EXPECT") or "refused"
local PSS     = tonumber(os.getenv("CM_PSS_ADDR") or "0")
local GUARD   = tonumber(os.getenv("CM_GUARD_ADDR") or "0")
local PREFIX  = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_pcguard"
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
local function shot(n) emu:screenshot(("%s_%s.png"):format(PREFIX, n)) end

local pssAt, guardHits, slot0 = nil, 0, nil
H.breakpoint("pss", PSS, function(fr)
    if pssAt == nil then
        pssAt = fr
        H.log(("storage system opened f=%d party=%d"):format(fr, emu:read8(H.gPlayerPartyCount)))
    end
end)
if GUARD ~= 0 then
    H.breakpoint("guard", GUARD, function(fr)
        guardHits = guardHits + 1
        H.log(("CM_PSSLastMonGuard entered f=%d slot(r0)=%d lr=0x%08X"):format(
            fr, emu:readRegister("r0"), emu:readRegister("lr")))
    end)
end

-- The proven console route from cm_pc_exit_test.lua.
local step, at, mashAt = "load", 0, nil
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        if CM_ON then H.cmOn(); H.setCharId(CM_CHAR) else H.cmOff() end
        H.log(("start party=%d cm=%s char=%d"):format(
            emu:read8(H.gPlayerPartyCount), tostring(H.cmIsOn()), H.getCharId()))
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

-- B through both hatch scenes; stops for good once the PC is open.
H.onFrame(function(f)
    if step ~= "running" or mashAt == nil or pssAt then return end
    if not slot0 and emu:read8(H.gPlayerPartyCount) == 2 then
        slot0 = emu:read32(H.gPlayerParty)
        H.log(("eggs landed f=%d slot0 pers=0x%08X"):format(f, slot0))
    end
    if f >= mashAt then
        if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
    end
end)

-- Inside the PC: Withdraw / Deposit / ... -> DOWN, A = Deposit; A = slot 0's
-- action menu; A = the deposit entry; A = confirm the box (or dismiss the
-- refusal).
local STEPS = {
    {60,  nil,    "1_pc_menu"},
    {10,  K.DOWN, nil},
    {40,  K.A,    "2_deposit_mode"},
    {160, K.A,    "3_party"},
    {60,  K.A,    "4_store_menu"},
    {90,  K.A,    "5_after_store"},
    {150, nil,    "6_result"},
}
local stepI, stepAt, done = 1, nil, false
H.onFrame(function(f)
    if not pssAt or done then return end
    if stepAt == nil then emu:clearKey(K.B); stepAt = pssAt end
    local s = STEPS[stepI]
    if s == nil then
        done = true
        local box, slot = inStorage(slot0 or 0), inParty(slot0 or 0)
        H.log(("RESULT slot0 box=%s partySlot=%s guardHits=%d"):format(
            tostring(box), tostring(slot), guardHits))
        H.assertTrue("both eggs landed and the PC opened", slot0 ~= nil and pssAt ~= nil)
        if EXPECT == "refused" then
            H.assertTrue("the deposit reached CM_PSSLastMonGuard", guardHits > 0)
            H.assertTrue("slot 0 (the last on-roster mon) is still in the party", slot ~= nil)
            H.assertTrue("...and NOT in the PC", box == nil)
        else
            H.assertTrue("slot 0 was deposited into the PC", box ~= nil)
            H.assertTrue("...and left the party", slot == nil)
        end
        H.finish()
        return
    end
    if f >= stepAt + s[1] then
        if s[3] then shot(s[3]) end
        if s[2] then H.press(s[2], 8) end
        stepI = stepI + 1; stepAt = f
    end
end)

H.onFrame(function(f)
    if f == 7000 and not done then
        H.log("timeout: step=" .. step .. " pssAt=" .. tostring(pssAt))
        H.assertTrue("reached the deposit (timeout)", false)
        H.finish()
    end
end)
