-- Boot the ROM with the existing progress save, mash through logos/title,
-- select CONTINUE, and screenshot periodically so we can see where we land.
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_nav_"

local loaded = false
H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        local ok = emu:loadSaveFile(SAV, false)
        H.log("loadSaveFile ok=" .. tostring(ok))
        emu:reset()
    end
    -- mash A/START periodically through logos + warning + title to reach the menu
    if f > 30 and f % 20 == 0 and f < 6000 then
        emu:addKey(H.KEY.A)
        emu:addKey(H.KEY.START)
    elseif f > 30 and f % 20 == 5 and f < 6000 then
        emu:clearKey(H.KEY.A)
        emu:clearKey(H.KEY.START)
    end
    if f % 300 == 0 and f <= 6000 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
        local pos = H.readPos()
        if pos then
            H.log(string.format("f=%d pos x=%d y=%d map=%d.%d sb1=%s party=%d",
                f, pos.x, pos.y, pos.grp, pos.num, H.hex(H.checkSaveBlockAnchor()),
                emu:read8(H.gPlayerPartyCount)))
        else
            H.log("f=" .. f .. " pos: n/a sb1=" .. H.hex(H.checkSaveBlockAnchor()))
        end
    end
    if f == 6000 then
        H.finish()
    end
end)
