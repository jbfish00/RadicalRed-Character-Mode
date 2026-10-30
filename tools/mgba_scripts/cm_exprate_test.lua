-- Live layer (EXP rate, 2026-10-29). On build/radicalred_cm_exprate_<tag>.gba (tools/tests/build_exprate_testrom.py)
-- from that ROM's bedroom checkpoint: RATE goes in gSpecialVar_0x8004 (0x020370C0), the console copies it to var
-- 0x51FC, gives Pikachu L10 + Magikarp L5 (party-wide share flag set) and starts a wild Magikarp L2 battle; move 1 is
-- forced to Tackle and A is mashed until it ends. Logs "GAINS <active> <benched>"; asserts WANT_GAIN0 / WANT_GAIN1
-- when set (the runner derives them from the x1 run).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local RATE = tonumber(os.getenv("RATE") or "0")
-- RR keeps party mons unencrypted (growth substructure first): EXP is the raw u32 at +0x24 (measured: a L10 Pikachu
-- reads 1000 there; the decrypting read gave garbage).
local function exp(i) return emu:read32(0x02024284 + i * 100 + 0x24) end
local battleAt, endAt, e0, e1 = nil, nil, nil, nil
local keys = {}
local function press(k, at) keys[#keys + 1] = {k, at, at + 20} end
press(K.UP, 20); press(K.A, 70); press(K.A, 200); press(K.A, 330)
H.onFrame(function(f)
    if f == 10 then emu:write16(0x020370C0, RATE) end
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    local inb = (emu:read8(0x03003529) >> 1) & 1 == 1
    if not battleAt and f > 400 and inb then battleAt = f end
    if battleAt and not endAt then
        if f == battleAt + 50 then e0 = exp(0); e1 = exp(1) end
        if os.getenv("SHOTS") and (f - battleAt) % 150 == 0 and f < battleAt + 1500 then emu:screenshot(string.format("%s_%05d.png", os.getenv("SHOTS"), f - battleAt)) end
        if f > battleAt + 60 and f < battleAt + 600 then              -- lead move 1 = Tackle (+ PP): a sure KO
            emu:write16(0x02023BE4 + 0x0C, 33); emu:write8(0x02023BE4 + 0x24, 35)
        end
        if (f - battleAt) % 40 == 0 then emu:addKey(K.A) elseif (f - battleAt) % 40 == 8 then emu:clearKey(K.A) end
        if f > battleAt + 120 and not inb then endAt = f; emu:clearKey(K.A) end
    end
    if (endAt and f == endAt + 30) or f == 9000 then
        H.assertTrue("the battle started and ended", battleAt ~= nil and endAt ~= nil and e0 ~= nil)
        local g0, g1 = exp(0) - (e0 or 0), exp(1) - (e1 or 0)
        H.log(string.format("party count %d, battle %s..%s, exp before %s/%s after %d/%d, levels %d/%d",
            emu:read8(0x02024029), tostring(battleAt), tostring(endAt), tostring(e0), tostring(e1), exp(0), exp(1),
            emu:read8(0x02024284 + 0x54), emu:read8(0x02024284 + 100 + 0x54)))
        if os.getenv("SHOTS") then emu:screenshot(os.getenv("SHOTS") .. "_end.png") end
        H.log("GAINS " .. g0 .. " " .. g1)
        H.assertTrue("both mons gained EXP", g0 > 0 and g1 > 0)
        if os.getenv("WANT_GAIN0") then H.assertEq("active mon's EXP gain", g0, tonumber(os.getenv("WANT_GAIN0"))) end
        if os.getenv("WANT_GAIN1") then H.assertEq("benched mon's EXP gain", g1, tonumber(os.getenv("WANT_GAIN1"))) end
        H.finish()
    end
end)
