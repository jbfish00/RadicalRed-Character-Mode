local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- Settle at various x on row y=8, screenshotting once stationary (not
-- mid-walk-animation) to see the true room layout / find the stairs tile.
local STEPS = {
    {moves = {}, tag = "start"},
    {moves = {{K.DOWN,32},{K.DOWN,32}}, tag = "y8_x6"},
    {moves = {{K.LEFT,32},{K.LEFT,32},{K.LEFT,32},{K.LEFT,32},{K.LEFT,32}}, tag = "y8_x1"},
    {moves = {{K.RIGHT,32},{K.RIGHT,32},{K.RIGHT,32},{K.RIGHT,32},{K.RIGHT,32},
              {K.RIGHT,32},{K.RIGHT,32},{K.RIGHT,32},{K.RIGHT,32},{K.RIGHT,32}}, tag = "y8_x11"},
}

local idx = 1
local state = "wait"  -- wait -> move -> settle -> shot
local counter = 0
local function fmt(p) return string.format("x=%d y=%d map=%d.%d", p.x, p.y, p.grp, p.num) end

H.onFrame(function(f)
    if f == 10 then
        for _, m in ipairs(STEPS[idx].moves) do H.press(m[1], m[2], 8) end
        state = "move"
    end
    if state == "move" and #STEPS[idx].moves == 0 then
        state = "settle"; counter = f + 40
    end
    if state == "move" then
        -- crude: assume done once pending queue drains; detect via frame count
        local total = 20
        for _, m in ipairs(STEPS[idx].moves) do total = total + m[2] + 8 end
        if f >= 10 + total then state = "settle"; counter = f + 40 end
    end
    if state == "settle" and f >= counter then
        local p = H.readPos()
        emu:screenshot(string.format("/tmp/rr_e3_%s.png", STEPS[idx].tag))
        if p then H.log(STEPS[idx].tag .. " " .. fmt(p)) end
        idx = idx + 1
        if idx > #STEPS then H.finish(); return end
        state = "wait"
        -- re-queue next step starting now
        for _, m in ipairs(STEPS[idx].moves) do H.press(m[1], m[2], 8) end
        state = "move2"
        local total = f + 20
        for _, m in ipairs(STEPS[idx].moves) do total = total + m[2] + 8 end
        counter = total
    end
    if state == "move2" and f >= counter then
        state = "settle"; counter = f + 40
    end
end)
