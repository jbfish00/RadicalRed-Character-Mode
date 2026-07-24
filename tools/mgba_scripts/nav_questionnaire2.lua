-- Continue from the "simply play Radical Red without custom options?"
-- Yes/No prompt (cursor default on Yes) -- press A once to confirm Yes,
-- then watch for whatever comes next.
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_q2_"

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
    -- single clean A at the "stop mashing" screen to reveal the real prompt
    if f == 3000 then emu:addKey(H.KEY.A) end
    if f == 3010 then emu:clearKey(H.KEY.A) end
    -- another single clean A once the Yes/No prompt has rendered, to
    -- confirm "Yes" (default cursor position, per screenshot)
    if f == 3400 then emu:addKey(H.KEY.A) end
    if f == 3410 then emu:clearKey(H.KEY.A) end
    if f % 40 == 0 and f >= 3400 and f <= 7000 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
    end
    if f == 7000 then H.finish() end
end)
