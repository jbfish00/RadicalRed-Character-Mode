-- Sprite pilot: drive the intro but answer "No" at the "simply play
-- without custom options?" prompt to enter RR's character-customization
-- flow, screenshotting it (its player pics come from trainer front pics).
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_cust_"

local loaded = false
local function tap(f, at, key)
    if f == at then emu:addKey(key) end
    if f == at + 10 then emu:clearKey(key) end
end

H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        emu:loadSaveFile(SAV, false)
        emu:reset()
    end
    if f > 30 and f % 20 == 0 and f < 2700 then emu:addKey(H.KEY.A)
    elseif f > 30 and f % 20 == 5 and f < 2700 then emu:clearKey(H.KEY.A) end
    tap(f, 3000, H.KEY.A)      -- dismiss "stop mashing"
    tap(f, 3350, H.KEY.DOWN)   -- move cursor to "No"
    tap(f, 3450, H.KEY.A)      -- confirm No -> custom options flow
    -- click through subsequent prompts slowly; screenshot densely
    for i = 1, 24 do
        tap(f, 3600 + i * 150, H.KEY.A)
    end
    if f % 60 == 0 and f >= 3400 and f <= 7500 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
    end
    if f == 7500 then H.finish() end
end)
