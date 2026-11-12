-- Live layer (Extras: heal + PC anywhere, QoL round 2 item 3, 2026-11-11; src/exp_rate.c CM_ExtrasOpen).
-- From the bedroom checkpoint: make sure there is a lead Pokemon (RR party mons are unencrypted; a Pikachu is written
-- if the party is empty) at 1 HP + poison, then START, RIGHT (second page), UP x2 (Exit <-, then Extras), A.
-- EXTRAS_KEYS (comma key names) act in the Extras list:
--   DOWN,A      -> Heal party: WANT_HEAL=1 (full HP, no status)
--   DOWN,DOWN,A -> PC: WANT_PC=1 (gSpecials[0x3C] ran once)
--   B           -> nothing
--   A           -> Exp. Rate: WANT_RATEOPEN=1
-- NO_PARTY=1: the party is left empty -> the row opens the rate list at once (WANT_RATEOPEN=1, WANT_EXTRAS=1: the
-- callnative still runs). Afterwards START builds the menu again (the field was released).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local function a(n) return tonumber(os.getenv(n)) & ~1 end
local WANT_HEAL, WANT_PC, WANT_RATEOPEN = tonumber(os.getenv("WANT_HEAL") or "0"), tonumber(os.getenv("WANT_PC") or "0"), tonumber(os.getenv("WANT_RATEOPEN") or "0")
local SHOTS = os.getenv("SHOTS")
local PARTY, COUNT = 0x02024284, 0x02024029
local exOpened, rateOpened, pcHits, built = 0, 0, 0, 0
H.breakpoint("CM_ExtrasOpen", a("CM_EXTRAS_OPEN"), function() exOpened = exOpened + 1 end)
H.breakpoint("CM_ExpRateOpen", a("CM_EXPRATE_OPEN"), function() rateOpened = rateOpened + 1 end)
H.breakpoint("special 0x3C", emu:read32(0x0815FD60 + 0x3C * 4) & ~1, function() pcHits = pcHits + 1 end)
H.breakpoint("SetUpStartMenu", 0x090BE178, function() built = built + 1 end)
local keys = {}
local function press(k, at) keys[#keys + 1] = {k, at, at + 12} end
press(K.START, 30); press(K.RIGHT, 120); press(K.UP, 200); press(K.UP, 240)
press(K.A, 300)
local i = 0
for k in (os.getenv("EXTRAS_KEYS") or ""):gmatch("[^,]+") do press(K[k], 420 + 40 * i); i = i + 1 end
press(WANT_HEAL == 1 and K.A or K.B, 760); press(K.B, 820)
press(K.START, 940)
H.onFrame(function(f)
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    if f == 10 then
        if os.getenv("NO_PARTY") == "1" then
            emu:write8(COUNT, 0)
        else
            if emu:read8(COUNT) == 0 then
                for o = 0, 99, 4 do emu:write32(PARTY + o, 0) end
                emu:write16(PARTY + 0x20, 25); emu:write8(PARTY + 0x54, 20); emu:write16(PARTY + 0x58, 40)
                emu:write8(COUNT, 1)
            end
            emu:write16(PARTY + 0x56, 1); emu:write32(PARTY + 0x50, 8)
            H.assertTrue("lead hurt for the test (1 HP of more)", emu:read16(PARTY + 0x56) == 1 and emu:read16(PARTY + 0x58) > 1)
        end
    end
    if f == 290 then
        local n = emu:read8(0x020370F5)
        H.assertEq("second-to-last row = Extras (13)", emu:read8(0x020370F6 + n - 2), 13)
    end
    if f == 400 then
        if SHOTS then emu:screenshot(SHOTS .. "_list.png") end
        H.assertEq("CM_ExtrasOpen ran", exOpened, 1)
        built = 0
    end
    if f == 750 then
        if SHOTS then emu:screenshot(SHOTS .. "_after.png") end
        if os.getenv("NO_PARTY") ~= "1" then
            local healed = emu:read16(PARTY + 0x56) == emu:read16(PARTY + 0x58) and emu:read32(PARTY + 0x50) == 0
            H.log(("lead hp %d/%d status %d"):format(emu:read16(PARTY + 0x56), emu:read16(PARTY + 0x58), emu:read32(PARTY + 0x50)))
            H.assertEq("lead healed (full HP, no status)", healed and 1 or 0, WANT_HEAL)
        end
        H.assertEq("the storage special (0x3C) ran", pcHits, WANT_PC)
        H.assertEq("the EXP rate list opened", rateOpened, WANT_RATEOPEN)
    end
    if f == 1040 then
        if SHOTS then emu:screenshot(SHOTS .. ".png") end
        H.assertEq("START menu built again (the field was released)", built >= 1 and 1 or 0, 1)
        H.finish()
    end
end)
