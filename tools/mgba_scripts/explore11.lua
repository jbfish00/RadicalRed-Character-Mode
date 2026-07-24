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
-- reach (11,4) then up to (11,2), then LEFT into (10,2) from the east
local PRECISE = {
    { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 },
    { K.RIGHT, 16, 24 }, { K.RIGHT, 16, 24 }, { K.RIGHT, 16, 24 }, { K.RIGHT, 16, 24 },
    { K.UP, 16, 24 }, { K.UP, 16, 60 },
    { K.LEFT, 60, 120 },  -- enter (10,2) from the EAST
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
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f == 2600 then
        local p2 = H.readPos()
        if p2 then H.log("FINAL " .. fmt(p2)) end
        emu:saveStateFile("/tmp/rr_ss_1f.ss")
        H.log("saved 1F checkpoint")
        H.finish()
    end
end)
