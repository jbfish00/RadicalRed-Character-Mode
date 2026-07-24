local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- From 1F checkpoint (10,2): clear Mom, get to (6,8) [one tile east of the
-- door], settle fully idle, then ONE isolated LEFT step onto (5,8) --
-- entering from the EAST, mirroring the technique that worked for the
-- 2F stairs (isolated step after a long idle settle, not mid-sweep).
local PRECISE = {
    { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 }, { K.DOWN, 16, 24 },
    { K.DOWN, 16, 24 },  -- (10,8)
    { K.LEFT, 16, 24 }, { K.LEFT, 16, 24 }, { K.LEFT, 16, 24 }, { K.LEFT, 16, 90 },  -- (6,8), then long settle
    { K.LEFT, 16, 200 },  -- isolated entry into (5,8) from the east, short precise tap
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
        emu:screenshot(string.format("/tmp/rr_e15_%05d.png", f))
    end
    if f == 4000 then
        local p2 = H.readPos()
        if p2 then H.log("FINAL " .. fmt(p2)) end
        emu:saveStateFile("/tmp/rr_ss_outside.ss")
        H.finish()
    end
end)
