local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- From 1F checkpoint (10,2), after Mom's dialogue: short (16f/24g) precise
-- single-tile steps down to (10,7) then left to (5,7), then settle fully
-- idle, then ONE isolated door-entry step down onto (5,8) -- matching the
-- pattern that worked for the 2F stairs (isolated step from idle, long
-- gap after).
local PRECISE = {
    { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 },
    { K.LEFT, 16, 24 }, { K.LEFT, 16, 24 }, { K.LEFT, 16, 24 }, { K.LEFT, 16, 24 }, { K.LEFT, 16, 60 },
    { K.DOWN, 40, 90 },
    { K.DOWN, 40, 150 },
    { K.DOWN, 40, 150 },
}

local last = nil
local function fmt(p) return string.format("x=%d y=%d map=%d.%d", p.x, p.y, p.grp, p.num) end
local queued = false
local function tapA(f, at)
    if f == at then emu:addKey(H.KEY.A) end
    if f == at + 10 then emu:clearKey(H.KEY.A) end
end
H.onFrame(function(f)
    for _, t in ipairs({40, 140, 240, 340, 440, 540, 640, 740, 840}) do
        tapA(f, t)
    end
    if f == 900 and not queued then
        queued = true
        for _, m in ipairs(PRECISE) do H.press(m[1], m[2], m[3]) end
        local p = H.readPos()
        if p then H.log("START " .. fmt(p)); last = fmt(p) end
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f % 30 == 0 and f <= 4000 then
        emu:screenshot(string.format("/tmp/rr_e14_%05d.png", f))
    end
    if f == 4000 then
        local p2 = H.readPos()
        if p2 then H.log("FINAL " .. fmt(p2)) end
        emu:saveStateFile("/tmp/rr_ss_outside.ss")
        H.finish()
    end
end)
