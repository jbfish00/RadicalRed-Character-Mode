local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

-- From 1F checkpoint (10,2): clear Mom's dialogue, go down to y=7 (not 8),
-- slide left to x=5 while still at y=7, then step DOWN into the door at
-- (5,8) so we enter walking south (matches the stairs' direction lesson).
local MOVES = {
    { K.DOWN, 32 }, { K.DOWN, 32 }, { K.DOWN, 32 }, { K.DOWN, 32 }, { K.DOWN, 32 },
    { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 }, { K.LEFT, 32 },
    { K.DOWN, 60 },
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
        for _, m in ipairs(MOVES) do H.press(m[1], m[2], 8) end
        local p = H.readPos()
        if p then H.log("START " .. fmt(p)); last = fmt(p) end
    end
    local p = H.readPos()
    if p then
        local cur = fmt(p)
        if cur ~= last then H.log(string.format("f=%d %s", f, cur)); last = cur end
    end
    if f % 30 == 0 and f <= 2600 then
        emu:screenshot(string.format("/tmp/rr_e13_%05d.png", f))
    end
    if f == 2600 then
        emu:saveStateFile("/tmp/rr_ss_outside.ss")
        H.finish()
    end
end)
