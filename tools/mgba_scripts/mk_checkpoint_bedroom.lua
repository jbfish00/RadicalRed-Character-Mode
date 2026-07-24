-- Drive the intro (logos -> anti-piracy warning -> "no custom options"
-- questionnaire) to the point of free movement in the bedroom, then save
-- an mGBA savestate + position/party dump so later scripts can start from
-- here instead of re-driving ~8000 frames every time.
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"
local OUT = "/tmp/rr_ss_bedroom.ss"

local loaded = false
local function tapA(f, at)
    if f == at then emu:addKey(H.KEY.A) end
    if f == at + 10 then emu:clearKey(H.KEY.A) end
end

H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        emu:loadSaveFile(SAV, false)
        emu:reset()
    end
    if f > 30 and f % 20 == 0 and f < 2700 then emu:addKey(H.KEY.A)
    elseif f > 30 and f % 20 == 5 and f < 2700 then emu:clearKey(H.KEY.A) end
    tapA(f, 3000)
    tapA(f, 3400)
    for _, t in ipairs({3600, 3700, 3800, 3900, 4000, 4100, 4200, 4300,
                         4400, 4500, 4600, 4700, 4800, 4900, 5000, 5100,
                         5200, 5300, 5400, 5500}) do
        tapA(f, t)
    end
    if f == 8000 then
        local pos = H.readPos()
        if pos then
            H.log(string.format("checkpoint pos x=%d y=%d map=%d.%d party=%d",
                pos.x, pos.y, pos.grp, pos.num, emu:read8(H.gPlayerPartyCount)))
        end
        emu:screenshot("/tmp/rr_ss_bedroom.png")
        emu:saveStateFile(OUT)
        H.log("saved " .. OUT)
        H.finish()
    end
end)
