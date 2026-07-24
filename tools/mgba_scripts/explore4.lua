local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- Go down 2 (to y=8), settle, screenshot. Simple single-purpose probe.
local MOVES = { { K.DOWN, 32 }, { K.DOWN, 32 } }

local last = nil
local function fmt(p) return string.format("x=%d y=%d map=%d.%d", p.x, p.y, p.grp, p.num) end
local queued = false
local total = 0
H.onFrame(function(f)
    if f == 10 and not queued then
        queued = true
        for _, m in ipairs(MOVES) do H.press(m[1], m[2], 8) end
        total = f + 10
        for _, m in ipairs(MOVES) do total = total + m[2] + 8 end
        local p = H.readPos()
        if p then H.log("START " .. fmt(p)) end
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f % 30 == 0 and f >= total and f <= total + 400 then
        emu:screenshot(string.format("/tmp/rr_e4_%05d.png", f))
    end
    if f == total + 400 then
        H.finish()
    end
end)
