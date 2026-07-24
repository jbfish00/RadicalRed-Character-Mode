local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- Reach (7,2) via the known-good path (press=32 as before, since that
-- worked), then switch to SHORT presses (16f/16f gap) to probe the
-- staircase tile-by-tile without overshooting.
local MOVES = {
    { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
}
local PROBE = {
    { K.DOWN, 16, 16 },
    { K.RIGHT, 16, 16 },
    { K.RIGHT, 16, 16 },
    { K.UP, 16, 16 },
    { K.RIGHT, 16, 16 },
    { K.UP, 16, 16 },
}

local last = nil
local function fmt(p) return string.format("x=%d y=%d map=%d.%d", p.x, p.y, p.grp, p.num) end
local queued = false
local probed = false
H.onFrame(function(f)
    if f == 10 and not queued then
        queued = true
        for _, m in ipairs(MOVES) do H.press(m[1], m[2], 8) end
        local p = H.readPos()
        if p then H.log("START " .. fmt(p)); last = fmt(p) end
    end
    if f == 1000 and not probed then
        probed = true
        for _, m in ipairs(PROBE) do H.press(m[1], m[2], m[3]) end
        H.log("PROBE QUEUED @f=1000")
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f % 30 == 0 and f <= 2000 then
        emu:screenshot(string.format("/tmp/rr_e8_%05d.png", f))
    end
    if f == 2000 then H.finish() end
end)
