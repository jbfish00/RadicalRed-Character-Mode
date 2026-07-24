-- Probe: load the existing progress save, see where we land, and check
-- whether the confirmed flag/var addresses look sane (SB1 pointer value
-- consistent with what the GDB shim tests assumed).
local H = dofile("tools/mgba_scripts/harness.lua")
local SAV = "/tmp/rr_probe.sav"

local loaded = false
H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        local ok = emu:loadSaveFile(SAV, false)
        H.log("loadSaveFile ok=" .. tostring(ok))
        emu:reset()
    end
    if f == 300 then
        local sb1 = H.checkSaveBlockAnchor()
        H.log("gSaveBlock1Ptr = " .. H.hex(sb1))
        local pos = H.readPos()
        if pos then
            H.log(string.format("pos x=%d y=%d map=%d.%d", pos.x, pos.y, pos.grp, pos.num))
        else
            H.log("pos: SB1 ptr out of EWRAM range")
        end
        H.log("party count = " .. emu:read8(H.gPlayerPartyCount))
        H.log("CM flag on? " .. tostring(H.cmIsOn()))
        H.log("char id = " .. H.getCharId())
        emu:screenshot("/tmp/rr_probe_300.png")
    end
    if f == 600 then
        emu:screenshot("/tmp/rr_probe_600.png")
        local pos = H.readPos()
        if pos then
            H.log(string.format("pos@600 x=%d y=%d map=%d.%d", pos.x, pos.y, pos.grp, pos.num))
        end
        H.finish()
    end
end)
