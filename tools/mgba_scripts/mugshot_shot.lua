-- Live proof that the character mugshot actually renders.
--
-- Runs on build/radicalred_cm_mugshot_test.gba (tools/tests/
-- build_mugshot_testrom.py), where the bedroom console's yes-branch goes
-- straight to a real character handler instead of the code-entry screen.
-- Everything from that point on is the shipped bytecode and the shipped
-- renderer.
--
-- Start from /tmp/rr_ss_bedroom.ss (tools/mgba_scripts/mk_checkpoint_bedroom.lua):
-- player at (6,6) on map 4.1, console at (6,5) directly north.
--
-- This does not just take a picture. It walks gSprites looking for a sprite
-- whose template pointer is our own, so the pass/fail is a memory assertion;
-- the screenshots are evidence for a human, not the test.
--
-- Driven by tools/tests/mugshot_render_test.py, which supplies every parameter
-- through the environment (CM_TEMPLATE_ADDR is read out of the linked ELF, so
-- nothing here hardcodes an address the build could move):
--   CM_TEMPLATE_ADDR  sMugshotTemplate's ROM address
--   CM_CHAR_ID        expected VAR_CHARACTER_ID after selection (1-based)
--   CM_EXPECT_SPRITE  1 if this character has staged art, 0 if not
--   CM_SHOT_PREFIX    where to write the screenshots
--
-- Run: mgba-headless --script tools/mgba_scripts/mugshot_shot.lua <rom>
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"

local TEMPLATE = tonumber(os.getenv("CM_TEMPLATE_ADDR") or "0x0898012C")
local CHAR_ID = tonumber(os.getenv("CM_CHAR_ID") or "1")
local EXPECT_SPRITE = tonumber(os.getenv("CM_EXPECT_SPRITE") or "1")
local PREFIX = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_mugshot"
local gSprites, SPRITE_COUNT, STRIDE = 0x0202063C, 64, 0x44
local OFF_TEMPLATE, OFF_INUSE, OFF_X, OFF_Y = 0x14, 0x3E, 0x20, 0x22

local function s16(v) if v >= 0x8000 then return v - 0x10000 end return v end

-- returns count, x, y, oamPaletteNum of our mugshot sprites currently live
local function findMugshot()
    local n, x, y, pal = 0, nil, nil, nil
    for i = 0, SPRITE_COUNT - 1 do
        local s = gSprites + i * STRIDE
        if (emu:read8(s + OFF_INUSE) & 1) ~= 0
           and emu:read32(s + OFF_TEMPLATE) == TEMPLATE then
            n = n + 1
            x = s16(emu:read16(s + OFF_X))
            y = s16(emu:read16(s + OFF_Y))
            pal = (emu:read16(s + 4) >> 12) & 0xF   -- oam attr2 paletteNum
        end
    end
    return n, x, y, pal
end

local shots = 0
local function shot(tag)
    shots = shots + 1
    local p = string.format("%s_%02d_%s.png", PREFIX, shots, tag)
    emu:screenshot(p)
    H.log("shot " .. p)
end

local step, at = "load", 0
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        local p = H.readPos()
        H.assertEq("start map", p and (p.grp .. "." .. p.num), "4.1")
        H.assertEq("mugshot absent before selection", (findMugshot()), 0)
        shot("00_bedroom")
        emu:addKey(K.UP)            -- turn to face the console at (6,5)
        step, at = "faced", f
    elseif step == "faced" and f - at == 20 then
        emu:clearKey(K.UP)
        step, at = "talk", f
    elseif step == "talk" and f - at == 30 then
        emu:addKey(K.A)             -- interact -> "put in a cheat code?" yes/no
        step, at = "talk2", f
    elseif step == "talk2" and f - at == 12 then
        emu:clearKey(K.A)
        step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        shot("01_yesno")
        emu:addKey(K.A)             -- answer Yes -> the character handler runs
        step, at = "yes2", f
    elseif step == "yes2" and f - at == 12 then
        emu:clearKey(K.A)
        step, at = "confirm", f
    elseif step == "confirm" and f - at == 150 then
        -- the confirm message box is up; callstd 6 blocks here, so the
        -- mugshot must be on screen right now
        local n, x, y, pal = findMugshot()
        shot("02_confirm_mugshot")
        H.assertEq("mugshot sprites while the confirm box is up", n, EXPECT_SPRITE)
        if EXPECT_SPRITE == 1 then
            -- A character with no staged art must reach here with no sprite and
            -- no complaint: the message shows, the selection still works.
            H.assertEq("mugshot x", x, 192)
            H.assertEq("mugshot y", y, 48)
            if pal then H.log("mugshot OBJ palette slot = " .. pal) end
        end
        H.assertEq("character mode flag set by the handler", H.cmIsOn(), true)
        H.assertEq("character id set by the handler", H.getCharId(), CHAR_ID)
        emu:addKey(K.A)             -- dismiss the message
        step, at = "dismiss2", f
    elseif step == "dismiss2" and f - at == 12 then
        emu:clearKey(K.A)
        step, at = "after", f
    elseif step == "after" and f - at == 150 then
        shot("03_after_dismiss")
        H.assertEq("mugshot torn down after the message", (findMugshot()), 0)
        H.assertEq("party has the signature mon", emu:read8(H.gPlayerPartyCount), 1)
        -- Round two: selecting again must not leak OBJ tiles or a palette slot
        -- and must not leave two sprites stacked. This is what the defensive
        -- Hide() call at the top of Show() exists for.
        emu:addKey(K.A)
        step, at = "again2", f
    elseif step == "again2" and f - at == 12 then
        emu:clearKey(K.A)
        step, at = "again3", f
    elseif step == "again3" and f - at == 90 then
        emu:addKey(K.A)             -- answer Yes a second time
        step, at = "again4", f
    elseif step == "again4" and f - at == 12 then
        emu:clearKey(K.A)
        step, at = "again5", f
    elseif step == "again5" and f - at == 150 then
        local n2, _, _, pal2 = findMugshot()
        shot("04_reselect")
        H.assertEq("re-selecting draws exactly one mugshot, not two", n2, EXPECT_SPRITE)
        if EXPECT_SPRITE == 1 then
            H.assertEq("re-selection reuses the same OBJ palette slot", pal2, 1)
        end
        H.finish()
    elseif f > 3000 then
        shot("99_timeout")
        H.log("TIMEOUT at step " .. step)
        H.finish()
    end
end)
