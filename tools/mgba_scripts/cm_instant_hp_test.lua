-- Live layer (QoL A3 instant HP bar, 2026-10-28). On build/radicalred_cm_hpbar_<tag>.gba (tools/tests/build_hpbar_testrom.py)
-- from that ROM's bedroom checkpoint: the console gives a Pikachu L10 and starts a wild Magikarp L2 battle; move 1 is
-- forced to Tackle and A is mashed until the battle ends. Every MoveBattleBar(HEALTH_BAR) call (0x08049FD8, r2 == 0)
-- is counted, with the distinct frames they fall on and the bar updates they belong to (an update starts while
-- gBattleSpritesDataPtr->battleBars[b].currValue holds -32768).
--   WANT_INSTANT=1 -> at most 4 frames an update (the bar snaps: the shipped ROM)
--   WANT_INSTANT=0 -> more than 4 frames an update (CFRU's own bar, 1/48 of it a frame below 48 max HP: the control)
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local WANT = tonumber(os.getenv("WANT_INSTANT") or "1")
local calls, updates, battleAt, endAt = 0, 0, nil, nil
local frames, lastFrame = 0, -1     -- distinct frames with a health-bar call: an instant bar may loop within one frame
local keys = {}
local function press(k, at) keys[#keys + 1] = {k, at, at + 20} end
H.breakpoint("MoveBattleBar", 0x08049FD8, function()
    if emu:readRegister("r2") & 0xFF ~= 0 then return end
    local bars = emu:read32(emu:read32(0x02024018) + 12)
    calls = calls + 1
    if H.frame() ~= lastFrame then frames = frames + 1; lastFrame = H.frame() end
    if emu:read32(bars + (emu:readRegister("r0") & 0xFF) * 20 + 16) == 0xFFFF8000 then updates = updates + 1 end
end)
press(K.UP, 20); press(K.A, 70); press(K.A, 200); press(K.A, 330)
H.onFrame(function(f)
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    local inb = (emu:read8(0x03003529) >> 1) & 1 == 1
    if not battleAt and f > 400 and inb then battleAt = f end
    if battleAt and not endAt then
        if f > battleAt + 60 and f < battleAt + 600 then              -- lead move 1 = Tackle (+ PP): a sure KO
            emu:write16(0x02023BE4 + 0x0C, 33); emu:write8(0x02023BE4 + 0x24, 35)
        end
        if os.getenv("SHOTS") and (f - battleAt) % tonumber(os.getenv("SHOT_EVERY") or "200") == 0 and f < battleAt + 1200 then emu:screenshot(string.format("%s_%05d.png", os.getenv("SHOTS"), f)) end
        if (f - battleAt) % 40 == 0 then emu:addKey(K.A) elseif (f - battleAt) % 40 == 8 then emu:clearKey(K.A) end
        if f > battleAt + 120 and not inb then endAt = f; emu:clearKey(K.A) end
    end
    if (endAt and f == endAt + 30) or f == 8000 then
        H.log(string.format("HP bar: %d MoveBattleBar calls on %d frames over %d updates (battle %s..%s)", calls, frames,
            updates, tostring(battleAt), tostring(endAt)))
        H.assertTrue("the battle started and ended", battleAt ~= nil and endAt ~= nil)
        if WANT == 1 then
            H.assertTrue("instant HP bar: at most 4 frames per update", updates > 0 and frames <= 4 * updates)
        else
            H.assertTrue("animated HP bar: more than 4 frames per update", updates > 0 and frames > 4 * updates)
        end
        H.finish()
    end
end)
