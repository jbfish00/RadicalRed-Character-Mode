local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_q3_"

local loaded = false
local function tapA(f, at)
    if f == at then emu:addKey(H.KEY.A) end
    if f == at + 10 then emu:clearKey(H.KEY.A) end
end

H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        emu:loadSaveFile(SAV, false)
        emu:reset()
    end
    if f > 30 and f % 20 == 0 and f < 2700 then emu:addKey(H.KEY.A)
    elseif f > 30 and f % 20 == 5 and f < 2700 then emu:clearKey(H.KEY.A) end
    tapA(f, 3000)   -- dismiss "stop mashing"
    tapA(f, 3400)   -- confirm Yes (no custom options)
    -- now single, well-spaced A taps (every 60 frames) to click through
    -- any remaining message boxes, without mashing (guard-safe)
    for i, t in ipairs({3600, 3700, 3800, 3900, 4000, 4100, 4200, 4300,
                         4400, 4500, 4600, 4700, 4800, 4900, 5000, 5100,
                         5200, 5300, 5400, 5500}) do
        tapA(f, t)
    end
    if f % 40 == 0 and f >= 3400 and f <= 8000 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
    end
    if f == 8000 then H.finish() end
end)
