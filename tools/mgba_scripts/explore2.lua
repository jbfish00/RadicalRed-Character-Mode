local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- from (6,8), stuck moving down further. Try scanning: a few more downs,
-- then sweep right and left at this row to find a gap/stairs.
local MOVES = {
    { K.DOWN, 32 }, { K.DOWN, 32 },
    { K.RIGHT, 32 }, { K.RIGHT, 32 }, { K.RIGHT, 32 },
    { K.DOWN, 32 }, { K.DOWN, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.DOWN, 32 }, { K.DOWN, 32 },
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
    if f % 40 == 0 and f <= 3000 then
        emu:screenshot(string.format("/tmp/rr_e2_%05d.png", f))
    end
    if f == 3000 then H.finish() end
end)
