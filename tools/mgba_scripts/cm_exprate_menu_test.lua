-- Live layer (EXP rate START list, 2026-10-29). From the bedroom checkpoint of build/radicalred_cm_exprate_on.gba:
-- START, RIGHT (RR's second page, now always offered), UP x2 from row 0 (wraps: Exit <-, then Exp Rate), A.
-- Asserts: the second-to-last row is action 13; CM_ExpRateOpen ran (breakpoint at CM_EXPRATE_OPEN); the field is not
-- left faded; LIST_KEYS (comma key names) end in VarSet(0x51FC, WANT_RATE), or no VarSet at all for WANT_RATE=0 with
-- B; START builds the menu again afterwards (the field was released).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local OPEN = tonumber(os.getenv("CM_EXPRATE_OPEN")) & ~1
local WANT = tonumber(os.getenv("WANT_RATE"))
local SHOTS = os.getenv("SHOTS")
local opened, built, setTo = 0, 0, nil
H.breakpoint("CM_ExpRateOpen", OPEN, function() opened = opened + 1 end)
H.breakpoint("SetUpStartMenu", 0x090BE178, function() built = built + 1 end)
H.breakpoint("VarSet", 0x0806E584, function()
    if emu:readRegister("r0") & 0xFFFF == 0x51FC then setTo = emu:readRegister("r1") & 0xFFFF end
end)
local function faded()
    for o = 0, 0x3FC, 4 do if emu:read32(0x020375F8 + o) ~= emu:read32(0x020371F8 + o) then return true end end
    return false
end
local keys = {}
local function press(k, at) keys[#keys + 1] = {k, at, at + 12} end
press(K.START, 30); press(K.RIGHT, 120); press(K.UP, 200); press(K.UP, 240)
press(K.A, 300)
local i = 0
for k in (os.getenv("LIST_KEYS") or ""):gmatch("[^,]+") do press(K[k], 420 + 40 * i); i = i + 1 end
press(K.START, 800)
H.onFrame(function(f)
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    if f == 290 then
        if SHOTS then emu:screenshot(SHOTS .. "_start.png") end
        local n = emu:read8(0x020370F5)
        H.log("second page rows: " .. n .. ", cursor " .. emu:read8(0x020370F4))
        H.assertEq("second-to-last row = Exp Rate (13)", emu:read8(0x020370F6 + n - 2), 13)
    end
    if f == 400 then
        if SHOTS then emu:screenshot(SHOTS .. "_list.png") end
        H.assertEq("the EXP rate list opened", opened, 1)
        H.assertTrue("the field is not faded under the list", not faded())
        built = 0
    end
    if f == 780 then
        if SHOTS then emu:screenshot(SHOTS .. "_after.png") end
        H.assertEq("VarSet(0x51FC) (-1 = none)", setTo or -1, WANT == 0 and -1 or WANT)
        H.assertTrue("the field is not faded after the list", not faded())
    end
    if f == 900 then
        if SHOTS then emu:screenshot(SHOTS .. ".png") end
        H.assertEq("START menu built again (the field was released)", built >= 1 and 1 or 0, 1)
        H.finish()
    end
end)
