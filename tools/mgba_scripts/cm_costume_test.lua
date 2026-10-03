-- Live proof that activating a character Radical Red ships a costume for puts
-- the player IN that costume (2026-10-02; tools/character_mode/rr_costumes.py).
--
-- Runs on build/radicalred_cm_mugshot_test.gba (tools/tests/
-- build_mugshot_testrom.py <name>): the bedroom console's yes-branch goes
-- straight to the named character's real handler, so everything after "Yes"
-- is shipped bytecode -- the handler, its costume tail (RR's own setvar run),
-- getplayerxy and the warpmuted bedroom reload.
--
-- Pass/fail is memory, not pixels: after the reload, the player's sprite must
-- be drawing the costume's graphics (its `images` pointer is the costume's
-- frame table, read from RR's overworld tables by the runner), the walk/run var
-- must hold the costume id, and the player must still be on map 4.1 at the
-- tile they activated from. The screenshots are evidence for a human.
--
-- Environment (tools/tests/run_costume_e2e.sh):
--   CM_CHAR_ID        expected VAR_CHARACTER_ID after selection (1-based)
--   CM_COSTUME_WALK   the costume's walk graphics id, or 0 for "no costume"
--   CM_COSTUME_IMAGES the costume walk sprite's frame-table pointer
--   CM_SHOT_PREFIX    where to write the screenshots
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"

local CHAR_ID = tonumber(os.getenv("CM_CHAR_ID") or "1")
local WALK = tonumber(os.getenv("CM_COSTUME_WALK") or "0")
local IMAGES = tonumber(os.getenv("CM_COSTUME_IMAGES") or "0")
local PREFIX = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_costume"
local gSprites, SPRITE_COUNT, STRIDE = 0x0202063C, 64, 0x44
local OFF_IMAGES, OFF_INUSE = 0x0C, 0x3E
-- CFRU keeps its expanded vars 0x5000.. contiguously; H.VAR_ADDR is 0x51FD's.
local VAR_WALKRUN_ADDR = H.VAR_ADDR - (0x51FD - 0x501F) * 2

local function spritesDrawing(images)
    local n = 0
    for i = 0, SPRITE_COUNT - 1 do
        local s = gSprites + i * STRIDE
        if (emu:read8(s + OFF_INUSE) & 1) ~= 0 and emu:read32(s + OFF_IMAGES) == images then
            n = n + 1
        end
    end
    return n
end

local shots = 0
local function shot(tag)
    shots = shots + 1
    local p = string.format("%s_%02d_%s.png", PREFIX, shots, tag)
    emu:screenshot(p)
    H.log("shot " .. p)
end

local step, at, start = "load", 0, nil
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        start = H.readPos()
        H.assertEq("start map", start and (start.grp .. "." .. start.num), "4.1")
        H.assertEq("walk/run var unset before selection", emu:read16(VAR_WALKRUN_ADDR), 0)
        H.assertEq("nothing draws the costume before selection", spritesDrawing(IMAGES), 0)
        shot("00_before")
        emu:addKey(K.UP)            -- face the console at (6,5)
        step, at = "faced", f
    elseif step == "faced" and f - at == 20 then
        emu:clearKey(K.UP); step, at = "talk", f
    elseif step == "talk" and f - at == 30 then
        emu:addKey(K.A); step, at = "talk2", f
    elseif step == "talk2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        emu:addKey(K.A)             -- Yes -> the character handler
        step, at = "yes2", f
    elseif step == "yes2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "confirm", f
    elseif step == "confirm" and f - at == 150 then
        H.assertEq("character id set by the handler", H.getCharId(), CHAR_ID)
        emu:addKey(K.A)             -- dismiss "you are now ..."
        step, at = "dismiss2", f
    elseif step == "dismiss2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "after", f
    elseif step == "after" and f - at == 300 then
        -- the bedroom reload (a fade out and in) has finished by now
        shot("01_after")
        local p = H.readPos()
        H.assertEq("still on map 4.1 after the reload", p and (p.grp .. "." .. p.num), "4.1")
        H.assertEq("same x after the reload", p and p.x, start.x)
        H.assertEq("same y after the reload", p and p.y, start.y)
        H.assertEq("walk/run var after selection", emu:read16(VAR_WALKRUN_ADDR), WALK)
        H.assertEq("sprites drawing the costume after selection", spritesDrawing(IMAGES),
                   WALK ~= 0 and 1 or 0)
        H.assertEq("character mode flag set", H.cmIsOn(), true)
        step = "done"
        H.finish()
    end
end)
