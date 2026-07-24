-- General map-data dumper: pass grp/num via globals set before dofile isn't
-- possible with dofile caching, so just hardcode per invocation (edit GRP/NUM).
local H = dofile("tools/mgba_scripts/harness.lua")
local GROUPS = 0x083526A8
local GRP, NUM = 4, 0   -- EDIT PER RUN

H.onFrame(function(f)
    if f ~= 3 then return end
    local groupArrPtr = emu:read32(GROUPS + GRP * 4)
    local headerPtr = emu:read32(groupArrPtr + NUM * 4)
    H.log(string.format("map[%d][%d] header ptr = %s", GRP, NUM, H.hex(headerPtr)))
    if headerPtr < 0x08000000 or headerPtr >= 0x0A000000 then H.finish(); return end
    local eventsPtr = emu:read32(headerPtr + 0x04)
    if eventsPtr < 0x08000000 or eventsPtr >= 0x0A000000 then H.log("bad eventsPtr"); H.finish(); return end
    local objCount = emu:read8(eventsPtr + 0)
    local warpCount = emu:read8(eventsPtr + 1)
    local coordCount = emu:read8(eventsPtr + 2)
    local bgCount = emu:read8(eventsPtr + 3)
    H.log(string.format("objCount=%d warpCount=%d coordCount=%d bgCount=%d",
        objCount, warpCount, coordCount, bgCount))
    local warpsPtr = emu:read32(eventsPtr + 8)
    if warpCount > 0 and warpCount < 20 and warpsPtr >= 0x08000000 and warpsPtr < 0x0A000000 then
        for i = 0, warpCount - 1 do
            local base = warpsPtr + i * 8
            local x = emu:read16(base + 0)
            local y = emu:read16(base + 2)
            local elevation = emu:read8(base + 4)
            local warpId = emu:read8(base + 5)
            local destMapNum = emu:read8(base + 6)
            local destMapGrp = emu:read8(base + 7)
            H.log(string.format("WARP %d: x=%d y=%d elev=%d warpId=%d -> map %d.%d",
                i, x, y, elevation, warpId, destMapGrp, destMapNum))
        end
    end
    local connPtr = emu:read32(headerPtr + 0x0C)
    H.log("connectionsPtr = " .. H.hex(connPtr))
    if connPtr >= 0x08000000 and connPtr < 0x0A000000 then
        local count = emu:read32(connPtr + 0)
        local listPtr = emu:read32(connPtr + 4)
        H.log(string.format("connection count=%d listPtr=%s", count, H.hex(listPtr)))
        if count > 0 and count < 10 and listPtr >= 0x08000000 and listPtr < 0x0A000000 then
            for i = 0, count - 1 do
                local base = listPtr + i * 12
                local direction = emu:read32(base + 0)
                local offset = emu:read32(base + 4)
                local mapGroup = emu:read8(base + 8)
                local mapNum = emu:read8(base + 9)
                H.log(string.format("CONN %d dir=%d offset=%d -> map %d.%d",
                    i, direction, offset, mapGroup, mapNum))
            end
        end
    end
    H.finish()
end)
