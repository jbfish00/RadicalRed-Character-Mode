local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- Reach (7,2) via the known-good path, then probe the staircase approach
-- carefully: down 1, then right several times (to go around/under the
-- railing), then try up onto the steps.
local MOVES = {
    { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    -- now at (7,2). Probe: down 1, right x5, up x2
    { K.DOWN, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
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
    if f % 60 == 0 and f <= 3600 then
        emu:screenshot(string.format("/tmp/rr_e7_%05d.png", f))
    end
    if f == 3600 then H.finish() end
end)
