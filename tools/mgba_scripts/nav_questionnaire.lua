-- From the "please stop mashing A" state: press A once cleanly to
-- dismiss, then just watch (no more input) to see what's being asked.
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_q_"

local loaded = false
H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        emu:loadSaveFile(SAV, false)
        emu:reset()
    end
    -- mash A cleanly (32-frame hold, 30-frame gap) up to frame 2700 to get
    -- to the same "stop mashing" state as before, then STOP and do one
    -- single clean press after a long settle.
    if f > 30 and f % 20 == 0 and f < 2700 then
        emu:addKey(H.KEY.A)
    elseif f > 30 and f % 20 == 5 and f < 2700 then
        emu:clearKey(H.KEY.A)
    end
    if f == 3000 then emu:addKey(H.KEY.A) end
    if f == 3010 then emu:clearKey(H.KEY.A) end
    if f % 40 == 0 and f >= 2700 and f <= 5000 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
    end
    if f == 5000 then H.finish() end
end)
