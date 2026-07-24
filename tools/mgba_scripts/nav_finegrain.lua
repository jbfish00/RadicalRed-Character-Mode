local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_fg_"

local loaded = false
H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        emu:loadSaveFile(SAV, false)
        emu:reset()
    end
    if f > 30 and f % 20 == 0 and f < 2700 then
        emu:addKey(H.KEY.A)
    elseif f > 30 and f % 20 == 5 and f < 2700 then
        emu:clearKey(H.KEY.A)
    end
    if f % 50 == 0 and f >= 2400 and f <= 3400 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
    end
    if f == 3400 then H.finish() end
end)
