-- Sprite-pilot visual check: load the progress save, continue into the
-- overworld, open START menu -> trainer card, screenshotting along the way.
-- Run: mgba-headless --script tools/mgba_scripts/trainer_card_shot.lua <rom>
-- Expects the save at /tmp/rr_sprite_test.sav; shots at /tmp/rr_card_*.png.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local SAV = "/tmp/rr_sprite_test.sav"

local loaded = false
local state = "title"      -- title -> settle -> menu -> done
local stateAt = 0
local shots = 0

local function shot(tag)
    shots = shots + 1
    emu:screenshot(string.format("/tmp/rr_card_%02d_%s.png", shots, tag))
end

H.onFrame(function(f)
    if f == 5 and not loaded then
        loaded = true
        local ok = emu:loadSaveFile(SAV, false)
        H.log("loadSaveFile ok=" .. tostring(ok))
        emu:reset()
        return
    end

    if state == "title" then
        -- mash A/START through logos/title/continue until the overworld loads
        if f > 30 and f % 20 == 0 then
            emu:addKey(K.A); emu:addKey(K.START)
        elseif f > 30 and f % 20 == 5 then
            emu:clearKey(K.A); emu:clearKey(K.START)
        end
        local p = H.readPos()
        if p and p.x ~= 0 and f > 300 then
            H.log(string.format("overworld at f=%d x=%d y=%d map=%d.%d", f, p.x, p.y, p.grp, p.num))
            emu:clearKey(K.A); emu:clearKey(K.START)
            shot("overworld")
            state = "settle"; stateAt = f
        elseif f > 5000 then
            H.log("never reached overworld"); shot("stuck"); H.finish()
        end
    elseif state == "settle" then
        -- close any lingering dialog with B, then open the START menu
        local d = f - stateAt
        if d == 30 or d == 70 or d == 110 then emu:addKey(K.B) end
        if d == 40 or d == 80 or d == 120 then emu:clearKey(K.B) end
        if d == 160 then emu:addKey(K.START) end
        if d == 170 then emu:clearKey(K.START); shot("startmenu_open") end
        if d == 230 then shot("startmenu"); state = "menu"; stateAt = f end
    elseif state == "menu" then
        -- FRLG start menu: Pokedex / Pokemon / Bag / <player card> / Save ...
        local d = f - stateAt
        if d == 20 or d == 60 or d == 100 then emu:addKey(K.DOWN) end
        if d == 30 or d == 70 or d == 110 then emu:clearKey(K.DOWN) end
        if d == 150 then emu:addKey(K.A) end
        if d == 160 then emu:clearKey(K.A) end
        if d == 300 then shot("trainercard"); state = "done"; stateAt = f end
    elseif state == "done" then
        if f - stateAt == 60 then shot("final"); H.finish() end
    end
end)
