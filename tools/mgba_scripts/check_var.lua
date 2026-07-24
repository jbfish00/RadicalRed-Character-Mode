local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"

local function tapA(f, at)
    if f == at then emu:addKey(H.KEY.A) end
    if f == at + 10 then emu:clearKey(H.KEY.A) end
end
local loaded = false
H.onFrame(function(f)
    if f == 5 and not loaded then loaded = true; emu:loadSaveFile(SAV, false); emu:reset() end
    if f > 30 and f % 20 == 0 and f < 2700 then emu:addKey(H.KEY.A)
    elseif f > 30 and f % 20 == 5 and f < 2700 then emu:clearKey(H.KEY.A) end
    tapA(f, 3000); tapA(f, 3400)
    for _, t in ipairs({3600,3700,3800,3900,4000,4100,4200,4300,4400,4500,
                         4600,4700,4800,4900,5000,5100,5200,5300,5400,5500}) do
        tapA(f, t)
    end
    if f == 8000 then
        -- var 0x511B address, derived from confirmed VAR_ADDR (0x51FD -> 0x0203B76E)
        local addr = H.VAR_ADDR - (0x51FD - 0x511B) * 2
        H.log(string.format("var 0x511B addr=%s value=%d", H.hex(addr), emu:read16(addr)))
        -- also dump a range of nearby var values for context
        for vid = 0x5100, 0x5120 do
            local a = H.VAR_ADDR - (0x51FD - vid) * 2
            H.log(string.format("  var %s = %d", H.hex(vid,4), emu:read16(a)))
        end
        H.finish()
    end
end)
