local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- Known real warp: map 4.1's warp 0 sits at (x=10,y=2) -> map 4.0.
-- Reach (7,2) via the known path, then go down+right+up to land on (10,2).
local MOVES = {
    { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    -- now at (7,2): detour down to y=4, right to x=10, then up onto the warp
    { K.DOWN, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 },
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
    if f % 60 == 0 and f <= 2600 then
        emu:screenshot(string.format("/tmp/rr_e9_%05d.png", f))
    end
    if f == 2600 then
        emu:saveStateFile("/tmp/rr_ss_1f.ss")
        H.finish()
    end
end)
