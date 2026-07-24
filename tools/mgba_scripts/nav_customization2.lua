-- Sprite pilot attempt 2: intro -> "No" (customize) -> skip difficulty by
-- selecting Done -> continue to appearance/player-sprite selection.
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local DIR = "/tmp/rr_cust2_"

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
    tap(f, 3350, H.KEY.DOWN)   -- Yes/No -> No
    tap(f, 3450, H.KEY.A)      -- confirm No -> "what to customize?" menu
    tap(f, 3700, H.KEY.DOWN)   -- Difficulty Options -> Minimal Grinding
    tap(f, 3780, H.KEY.DOWN)   -- -> Randomizer Options
    tap(f, 3860, H.KEY.DOWN)   -- -> Done
    tap(f, 3940, H.KEY.A)      -- select Done
    -- whatever comes next: slow A taps, dense screenshots
    for i = 1, 14 do
        tap(f, 4100 + i * 200, H.KEY.A)
    end
    if f % 40 == 0 and f >= 3900 and f <= 7000 then
        emu:screenshot(string.format("%s%05d.png", DIR, f))
    end
    if f == 7000 then H.finish() end
end)
