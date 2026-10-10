-- Live layer: early party-wide Exp. Share (src/exp_share.c, 2026-10-09).
-- On build/radicalred_cm_expsharetest[_off].gba (tools/tests/build_catch_testrom.py
-- --expshare): the bedroom console sets Character Mode as Red (not in the _off
-- ROM), runs the activation wrapper CM_ActivateSweepAndExpShare, then records
-- flag 0x906 (CFRU FLAG_EXP_SHARE) in var 0x4011 and `checkitem 182` in 0x4012.
--   EXPECT=granted -> both 1 (the Exp. Share is in the bag and switched on)
--   EXPECT=none    -> both 0 (CM off: the wrapper grants nothing)
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local EXPECT = os.getenv("EXPECT") or "granted"
local keys = {}
local function press(k, at) keys[#keys + 1] = {k, at, at + 20} end
local function var(v) return emu:read16(emu:read32(0x03005008) + 0x1000 + 2 * (v - 0x4000)) end
H.onFrame(function(f)
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    if f == 5 then
        emu:write16(emu:read32(0x03005008) + 0x1000 + 2 * (0x4011 - 0x4000), 0xFFFF)
        emu:write16(emu:read32(0x03005008) + 0x1000 + 2 * (0x4012 - 0x4000), 0xFFFF)
        press(K.UP, 20); press(K.A, 70); press(K.A, 200); press(K.A, 330)
    end
    if f == 900 then
        local on, has = var(0x4011), var(0x4012)
        H.log(string.format("flag 0x906 -> %d, checkitem 182 -> %d", on, has))
        local want = (EXPECT == "granted") and 1 or 0
        H.assertEq("Exp. Share switched on (flag 0x906)", on, want)
        H.assertEq("Exp. Share in the bag (checkitem 182)", has, want)
        H.finish()
    end
end)
