-- Live test of the in-game roster display in RADICAL RED (2026-09-27).
--
-- Loads the bedroom checkpoint (/tmp/rr_ss_bedroom.ss, made by
-- mk_checkpoint_bedroom.lua: player at (6,6), the console is at (6,5)),
-- presets CM in RAM, faces the console and presses A.
--
--   MODE=roster  CM on as CM_CHAR: "View your Character Mode roster?" -> Yes.
--                Asserts the EXACT rows (read out of the list's own item array,
--                species AND name pointer, against CM_EXPECT_ROOTS from the
--                manifest), the first icon drawn from CFRU's relocated icon
--                table and byte-identical in VRAM, the SECOND root's species
--                after one DOWN ("ID, not index"), and that B tears everything
--                down AND hands the field back (the player can walk again, i.e.
--                the waitstate resumed and the script released).
--   MODE=no      CM on, answer No: the stock console script follows (its own
--                cheat-code yes/no) and reaches the code screen, special 0x12C;
--                the roster never opens.
--   MODE=off     CM off: straight to the stock console script, which reaches
--                special 0x12C; the roster never opens.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY

local MODE = os.getenv("MODE") or "roster"
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "10")
local STATE = "/tmp/rr_ss_bedroom.ss"
local function envaddr(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local ROSTER_OPEN = envaddr("CM_ROSTER_OPEN") & ~1
local ROSTER_MOVE = envaddr("CM_ROSTER_MOVE") & ~1
local EXPECT = {}
for s in (os.getenv("CM_EXPECT_ROOTS") or ""):gmatch("%d+") do EXPECT[#EXPECT + 1] = tonumber(s) end

local CODE_SCREEN = 0x090BBC6C                -- gSpecials[0x12C], the console's code entry
local gTasks, TASK_SIZE = 0x03005090, 0x28
local gSprites, SPRITE_SIZE = 0x0202063C, 0x44
local NAMES = emu:read32(0x08000144)          -- CFRU redirect slot: gSpeciesNames
local ICONS = emu:read32(0x08000138)          -- CFRU redirect slot: mon icon table
local PALIDX = emu:read32(0x0800013C)         -- CFRU redirect slot: icon palette indices
local PALTABLE = emu:read32(0x08000140)       -- icon palette table {ptr, tag, pad}
local HANDLE_INPUT = ROSTER_MOVE              -- replaced below once the task exists

local opened, moves, codeScreen, selSeen = 0, 0, 0, {}
H.breakpoint("roster_open", ROSTER_OPEN, function() opened = opened + 1 end)
H.breakpoint("roster_move", ROSTER_MOVE, function()
    moves = moves + 1
    selSeen[#selSeen + 1] = emu:readRegister("r0")      -- itemId == species
end)
H.breakpoint("code_screen", CODE_SCREEN, function() codeScreen = codeScreen + 1 end)

local function iconSpriteFor(s)
    local img = emu:read32(ICONS + s * 4)
    for i = 0, 63 do
        local b = gSprites + i * SPRITE_SIZE
        if (emu:read8(b + 0x3E) & 1) == 1 and emu:read32(b + 12) == img then return b end
    end
end
local function anyRosterIcon()
    for _, s in ipairs(EXPECT) do if iconSpriteFor(s) then return true end end
    return false
end
-- the roster's input task: the one active task whose func lies in the unit
local function rosterTask()
    for i = 0, 15 do
        local t = gTasks + i * TASK_SIZE
        local fn = emu:read32(t) & ~1
        if emu:read8(t + 4) ~= 0 and fn > ROSTER_OPEN - 0x400 and fn < ROSTER_OPEN + 0x400
           and fn ~= ROSTER_OPEN then return t end
    end
end
local function readRows()
    local t = rosterTask()
    if not t then return nil end
    local items = ((emu:read16(t + 8 + 4 * 2) & 0xFFFF) << 16) | (emu:read16(t + 8 + 5 * 2) & 0xFFFF)
    local ids, namesOk = {}, true
    for i = 0, #EXPECT - 1 do
        local id = emu:read32(items + i * 8 + 4)
        ids[#ids + 1] = tostring(id)
        if emu:read32(items + i * 8) ~= NAMES + id * 11 then namesOk = false end
    end
    return table.concat(ids, ","), namesOk
end
local function iconMatchesRom(b, s)
    local img = emu:read32(ICONS + s * 4)
    local vram = 0x06010000 + (emu:read16(b + 4) & 0x3FF) * 32
    local f0, f1 = true, true
    for k = 0, 511 do
        local v = emu:read8(vram + k)
        if v ~= emu:read8(img + k) then f0 = false end
        if v ~= emu:read8(img + 512 + k) then f1 = false end
    end
    local pal = (emu:read16(b + 4) >> 12) & 15
    local src = emu:read32(PALTABLE + emu:read8(PALIDX + s) * 8)
    local palOk = true
    for k = 0, 15 do
        if emu:read16(0x05000200 + pal * 32 + k * 2) ~= emu:read16(src + k * 2) then palOk = false end
    end
    return (f0 or f1), palOk
end

local step, at = "load", 0
local t = {}
local rows, namesOk, firstIcon, firstVram, firstPal, secondIcon, secondPrio, walked
local function hold(key, n) emu:addKey(key); t.release = { key = key, at = H.frame() + n } end
H.onFrame(function(f)
    if t.release and f >= t.release.at then emu:clearKey(t.release.key); t.release = nil end
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE); step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        if MODE == "off" then H.cmOff() else H.cmOn(); H.setCharId(CM_CHAR) end
        hold(K.UP, 20); step, at = "talk", f
    elseif step == "talk" and f - at == 50 then
        hold(K.A, 12); step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        emu:screenshot(("build/roster_%s_prompt.png"):format(MODE))
        if MODE == "no" then hold(K.B, 12) else hold(K.A, 12) end
        step, at = (MODE == "roster") and "wait_list" or "stock", f
    elseif step == "stock" then
        -- the stock console asks its own yes/no; A answers Yes -> code screen
        if codeScreen > 0 then
            step, at = "stock_shot", f
        elseif f - at > 900 then step = "done"
        elseif (f - at) % 60 == 30 then hold(K.A, 8) end
    elseif step == "stock_shot" and f - at == 60 then
        emu:screenshot(("build/roster_%s_code.png"):format(MODE)); step = "done"
    elseif step == "wait_list" then
        if opened > 0 and moves > 0 then step, at = "list_shot", f
        elseif f - at > 600 then step = "done" end
    elseif step == "list_shot" and f - at == 40 then
        rows, namesOk = readRows()
        local b = iconSpriteFor(EXPECT[1])
        firstIcon = b ~= nil
        if b then firstVram, firstPal = iconMatchesRom(b, EXPECT[1]) end
        emu:screenshot(("build/roster_list_c%d_row0.png"):format(CM_CHAR))
        t.moveBase = moves; step, at = "down", f
    elseif step == "down" then
        if moves > t.moveBase then step, at = "down_shot", f
        elseif f - at > 600 then step, at = "close", f
        elseif (f - at) % 20 == 0 then hold(K.DOWN, 8) end
    elseif step == "down_shot" and f - at == 40 then
        local b = iconSpriteFor(EXPECT[2])
        secondIcon = b ~= nil
        secondPrio = b and ((emu:read8(b + 5) >> 2) & 3)
        emu:screenshot(("build/roster_list_c%d_row1.png"):format(CM_CHAR))
        step, at = "close", f
    elseif step == "close" then
        if rosterTask() == nil then step, at = "walk", f
        elseif f - at > 600 then step = "done"
        elseif (f - at) % 20 == 0 then hold(K.B, 8) end
    elseif step == "walk" and f - at == 60 then
        t.pos = H.readPos(); hold(K.DOWN, 16); step, at = "walked", f
    elseif step == "walked" and f - at == 60 then
        local p = H.readPos()
        walked = p and t.pos and (p.y ~= t.pos.y or p.x ~= t.pos.x)
        emu:screenshot(("build/roster_closed_c%d.png"):format(CM_CHAR))
        step = "done"
    end
    if step == "done" then
        step = "finished"
        local s = {}
        for _, v in ipairs(selSeen) do s[#s + 1] = tostring(v) end
        H.log(("mode=%s char=%d opened=%d moves=%d code=%d sel=[%s] rows=[%s]"):format(
            MODE, CM_CHAR, opened, moves, codeScreen, table.concat(s, ","), tostring(rows)))
        if MODE == "roster" then
            H.assertEq("rows == the character's family roots, in order", rows, table.concat(EXPECT, ","))
            H.assertTrue("every row's name points at gSpeciesNames[species]", namesOk == true)
            H.assertEq("first cursor callback got the first root's SPECIES", selSeen[1], EXPECT[1])
            H.assertTrue("the first root's icon sprite draws from CFRU's icon table", firstIcon == true)
            H.assertTrue("...its VRAM tiles are that icon's frame", firstVram == true)
            H.assertTrue("...and its OBJ palette is the table entry its index names", firstPal == true)
            H.assertEq("after one DOWN, the callback got the SECOND root's species",
                selSeen[#selSeen], EXPECT[2])
            H.assertTrue("the second root's icon replaced it", secondIcon == true)
            H.assertEq("the icon is above the window layer (oam priority)", secondPrio, 0)
            H.assertTrue("B closed it: no roster task, no roster icon", rosterTask() == nil and not anyRosterIcon())
            H.assertTrue("the field is back: the player walked after the close", walked == true)
        else
            H.assertTrue("the stock console reached its code screen (special 0x12C)", codeScreen == 1)
            H.assertTrue("the roster never opened", opened == 0)
        end
        H.finish()
    end
end)
