local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- Reproduce explore5's path to (7,2) [right next to the staircase graphic],
-- then step onto/through the stairs.
local MOVES = {
    { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    -- now push further right/down onto the stairs
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.DOWN, 32 }, { K.DOWN, 32 }, { K.DOWN, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 },
}

local last = nil
local function fmt(p) return string.format("x=%d y=%d map=%d.%d", p.x, p.y, p.grp, p.num) end
local queued = false
H.onFrame(function(f)
    if f == 10 and not queued then
        queued = true
        for _, m in ipairs(MOVES) do H.press(m[1], m[2], 8) end
        local p = H.readPos()
        if p then H.log("START " .. fmt(p)); last = fmt(p) end
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f % 60 == 0 and f <= 4200 then
        emu:screenshot(string.format("/tmp/rr_e6_%05d.png", f))
    end
    if f == 4200 then
        emu:saveStateFile("/tmp/rr_ss_after_stairs.ss")
        H.finish()
    end
end)
