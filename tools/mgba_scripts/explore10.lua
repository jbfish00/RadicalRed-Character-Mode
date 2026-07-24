local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local MOVES = {
    { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 }, { K.UP, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.UP, 32 }, { K.UP, 32 },
}
-- from (7,2): short 1-tile taps (16f press / 24f gap, empirically reliable)
local PRECISE = {
    { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 },
    { K.RIGHT, 16, 24 }, { K.RIGHT, 16, 24 }, { K.RIGHT, 16, 24 },
    { K.UP, 16, 60 },   -- (10,4) -> (10,3), long settle
    { K.UP, 60, 60 },  -- (10,3) -> (10,2)
}

local last = nil
local function fmt(p) return string.format("x=%d y=%d map=%d.%d", p.x, p.y, p.grp, p.num) end
local queued, precQueued = false, false
H.onFrame(function(f)
    if f == 10 and not queued then
        queued = true
        for _, m in ipairs(MOVES) do H.press(m[1], m[2], 8) end
        local p = H.readPos()
        if p then H.log("START " .. fmt(p)); last = fmt(p) end
    end
    if f == 900 and not precQueued then
        precQueued = true
        for _, m in ipairs(PRECISE) do H.press(m[1], m[2], m[3]) end
        H.log("PRECISE QUEUED")
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f % 15 == 0 and f >= 1100 and f <= 2600 then
        emu:screenshot(string.format("/tmp/rr_e10e_%05d.png", f))
    end
    if f == 2600 then
        local p = H.readPos()
        if p then H.log("FINAL " .. fmt(p)) end
        emu:saveStateFile("/tmp/rr_ss_1f.ss")
        H.finish()
    end
end)
