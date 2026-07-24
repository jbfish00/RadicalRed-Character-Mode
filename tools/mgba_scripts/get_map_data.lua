-- Read the real map header / events / warps for map group 4, map 1
-- (Pallet Town Player's House 2F, our current stuck room) straight out of
-- ROM via the gMapGroups tree (vanilla FireRed 0x3526A8, confirmed already
-- used successfully in this repo per docs/ROUTINE_MAP.md's cheat-console
-- discovery) -- far more reliable than guessing warp tiles by pixel-eye.
local H = dofile("tools/mgba_scripts/harness.lua")

local GROUPS = 0x083526A8

H.onFrame(function(f)
    if f ~= 3 then return end
    local grp, num = 4, 1
    local groupArrPtr = emu:read32(GROUPS + grp * 4)
    H.log(string.format("group[%d] array ptr = %s", grp, H.hex(groupArrPtr)))
    if groupArrPtr < 0x08000000 or groupArrPtr >= 0x0A000000 then
        H.log("groupArrPtr out of ROM range, aborting")
        H.finish(); return
    end
    local headerPtr = emu:read32(groupArrPtr + num * 4)
    H.log(string.format("map[%d][%d] header ptr = %s", grp, num, H.hex(headerPtr)))
    if headerPtr < 0x08000000 or headerPtr >= 0x0A000000 then
        H.log("headerPtr out of ROM range, aborting")
        H.finish(); return
    end
    -- struct MapHeader { mapLayout, events, mapScripts, connections,
    --   u16 music, u16 mapLayoutId, u8 regionMapSectionId, u8 cave,
    --   u8 weather, u8 mapType, ... }
    local eventsPtr = emu:read32(headerPtr + 0x04)
    H.log(string.format("eventsPtr = %s", H.hex(eventsPtr)))
    if eventsPtr < 0x08000000 or eventsPtr >= 0x0A000000 then
        H.log("eventsPtr out of ROM range, aborting")
        H.finish(); return
    end
    -- struct MapEvents { u8 objCount, u8 warpCount, u8 coordCount, u8 bgCount,
    --   objs*, warps*, coords*, bgs* }
    local objCount = emu:read8(eventsPtr + 0)
    local warpCount = emu:read8(eventsPtr + 1)
    local coordCount = emu:read8(eventsPtr + 2)
    local bgCount = emu:read8(eventsPtr + 3)
    H.log(string.format("objCount=%d warpCount=%d coordCount=%d bgCount=%d",
        objCount, warpCount, coordCount, bgCount))
    local warpsPtr = emu:read32(eventsPtr + 8)
    H.log(string.format("warpsPtr = %s", H.hex(warpsPtr)))
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
    local coordsPtr = emu:read32(eventsPtr + 12)
    H.log(string.format("coordsPtr = %s", H.hex(coordsPtr)))
    if coordCount > 0 and coordCount < 20 and coordsPtr >= 0x08000000 and coordsPtr < 0x0A000000 then
        -- struct CoordEvent: s16 x, s16 y, u8 elevation, u8 trigger?, u16 index/var, ...  script ptr near end. Dump raw 16 bytes.
        for i = 0, coordCount - 1 do
            local base = coordsPtr + i * 16
            local bytes = {}
            for j = 0, 15 do bytes[#bytes+1] = string.format("%02X", emu:read8(base+j)) end
            local x = emu:read16(base+0)
            local y = emu:read16(base+2)
            H.log(string.format("COORD %d x=%d y=%d raw: %s", i, x, y, table.concat(bytes, " ")))
        end
    end
    local bgsPtr = emu:read32(eventsPtr + 16)
    H.log(string.format("bgsPtr = %s", H.hex(bgsPtr)))
    if bgCount > 0 and bgCount < 20 and bgsPtr >= 0x08000000 and bgsPtr < 0x0A000000 then
        for i = 0, bgCount - 1 do
            local base = bgsPtr + i * 12
            local bytes = {}
            for j = 0, 11 do bytes[#bytes+1] = string.format("%02X", emu:read8(base+j)) end
            local x = emu:read16(base+0)
            local y = emu:read16(base+2)
            H.log(string.format("BG %d x=%d y=%d raw: %s", i, x, y, table.concat(bytes, " ")))
        end
    end
    local objsPtr = emu:read32(eventsPtr + 4)
    H.log(string.format("objsPtr = %s", H.hex(objsPtr)))
    if objCount > 0 and objCount < 20 and objsPtr >= 0x08000000 and objsPtr < 0x0A000000 then
        -- struct ObjectEventTemplate roughly 24 bytes in vanilla pokefirered:
        -- u8 localId, u16 graphicsId, u8 kind?, s16 x, s16 y, u8 elevation,
        -- u8 movementType, u16 movementRangeX/Y, u16 trainerType, u16 trainerRange,
        -- const u8* script, u16 flagId -- sizes vary by version; just dump raw bytes
        for i = 0, math.min(objCount - 1, 8) do
            local base = objsPtr + i * 24
            local bytes = {}
            for j = 0, 23 do bytes[#bytes+1] = string.format("%02X", emu:read8(base+j)) end
            H.log(string.format("OBJ %d raw: %s", i, table.concat(bytes, " ")))
        end
    end
    H.finish()
end)
