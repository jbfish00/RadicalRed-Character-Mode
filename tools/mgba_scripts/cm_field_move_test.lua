-- LIVE layer for field moves (src/field_moves.c; verify_artifacts section 20)
-- on the TEST-ONLY ROM build/radicalred_cm_fieldtest.gba
-- (tools/tests/build_field_testrom.py). 2026-10-07.
--
-- From the bedroom checkpoint (empty party): face the console, Yes -> the test
-- script hatches a Magikarp (knows only Splash, learns no HM), sets every
-- badge and asks the REAL engine, for each HM move, `checkpartymove` (FireRed's
-- Cut / Rock Smash / Strength objects) and specials 0x10A-0x10C (CFRU's
-- PartyHasMonWithFieldMovePotential), first with no HM in the bag, then with
-- HM01-HM08. Results land in vars 0x4000.. (6 = no mon, 0 = slot 0).
--
--   CM on : no HM -> 6 everywhere ; HM -> 0 everywhere
--   CM off: 6 everywhere (the original answer: Magikarp knows and learns none)
-- and the --no-hook ROM (CM on) must FAIL, on "checkpartymove Cut with the HM".
--
-- Then the script runs FireRed's own Cut-tree script; the layer presses A once
-- and photographs it (the "use Cut?" prompt only appears if the check passed).
--
-- Env: CM_ON 1/0, CM_CHAR, CM_SHOT_PREFIX.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"
local CM_ON   = (os.getenv("CM_ON") == "1")
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local PREFIX  = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_field"

-- Vars 0x4000.. are FireRed's own: gSaveBlock1Ptr (0x03005008) + 0x1000.
-- (VAR_CHARACTER_ID 0x51FD is a CFRU expanded var stored elsewhere.)
local function varAddr(v) return emu:read32(0x03005008) + 0x1000 + 2 * (v - 0x4000) end
local function var(v) return emu:read16(varAddr(v)) end
local VAR_DONE, DONE = 0x401F, 0x600D

local MOVES = {"Cut", "Fly", "Surf", "Strength", "Flash", "Rock Smash",
               "Waterfall", "Dive", "Rock Climb"}
local SPECIALS = {"special 0x10A (Cut)", "special 0x10B (Rock Smash)",
                  "special 0x10C (Strength)"}
local N = #MOVES + #SPECIALS

local function shot(n) emu:screenshot(("%s_%s.png"):format(PREFIX, n)) end

local step, at, mashAt, doneAt = "load", 0, nil, nil
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        if CM_ON then H.cmOn(); H.setCharId(CM_CHAR) else H.cmOff() end
        emu:write16(varAddr(VAR_DONE), 0)
        H.log(("start party=%d cm=%s char=%d"):format(
            emu:read8(H.gPlayerPartyCount), tostring(H.cmIsOn()), H.getCharId()))
        emu:addKey(K.UP)
        step, at = "faced", f
    elseif step == "faced" and f - at == 20 then
        emu:clearKey(K.UP); step, at = "talk", f
    elseif step == "talk" and f - at == 30 then
        emu:addKey(K.A); step, at = "talk2", f
    elseif step == "talk2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        emu:addKey(K.A); step, at = "yes2", f
    elseif step == "yes2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "running", f
        mashAt = f + 30
    end
end)

-- B through the hatch scene until the script reports done.
H.onFrame(function(f)
    if step ~= "running" or mashAt == nil or doneAt then return end
    if var(VAR_DONE) == DONE then
        emu:clearKey(K.B)
        doneAt = f
        H.log(("done f=%d party=%d"):format(f, emu:read8(H.gPlayerPartyCount)))
        return
    end
    if f >= mashAt then
        if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
    end
end)

local finished = false
H.onFrame(function(f)
    if not doneAt or finished then return end
    if f == doneAt + 90 then shot("1_cut_tree_text") ; H.press(K.A, 8) end
    if f == doneAt + 160 then
        shot("2_after_A")
        finished = true
        local without, with = {}, {}
        for i = 0, N - 1 do
            without[i + 1] = var(0x4000 + i)
            with[i + 1] = var(0x4000 + N + i)
        end
        H.log("RESULT without HM: " .. table.concat(without, ","))
        H.log("RESULT with HM:    " .. table.concat(with, ","))
        H.assertTrue("party is the one hatched mon", emu:read8(H.gPlayerPartyCount) == 1)
        local function name(i)
            if i <= #MOVES then return "checkpartymove " .. MOVES[i] end
            return SPECIALS[i - #MOVES]
        end
        for i = 1, N do
            H.assertTrue(name(i) .. " without the HM -> no mon (6)", without[i] == 6)
        end
        for i = 1, N do
            if CM_ON then
                H.assertTrue(name(i) .. " with the HM, CM on -> slot 0", with[i] == 0)
            else
                H.assertTrue(name(i) .. " with the HM, CM off -> no mon (6)", with[i] == 6)
            end
        end
        H.finish()
    end
end)

H.onFrame(function(f)
    if f == 9000 and not finished then
        H.log("timeout: step=" .. step .. " done=" .. tostring(var(VAR_DONE)))
        H.assertTrue("reached the end of the test script (timeout)", false)
        H.finish()
    end
end)
