-- LIVE layer for the any-level relearner (QoL A2, 2026-10-24; inject_character_mode.relearn_any_level)
-- on the TEST-ONLY ROM build/radicalred_cm_reltest[_nohook].gba (tools/tests/build_relearn_testrom.py).
--
-- From the bedroom checkpoint (empty party), Character Mode OFF (the rule is always on): face the console, Yes -> the
-- test script hatches a Magikarp (Lv1, knows Splash), then runs the Move Maniac's own special 0xDB
-- (ChooseMonForMoveRelearner). The layer stops pressing B at the script's marker and picks the lead with A; the party
-- menu leaves the relearnable-move count in VAR_0x8005, copied to 0x4000 (slot -> 0x4001).
--   WANT=pos  : count > 0 (moves above Lv1 are listed)
--   WANT=zero : count == 0 (the --no-hook ROM: the level cut, Splash already known)
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"
local WANT = os.getenv("WANT") or "pos"

local function varAddr(v) return emu:read32(0x03005008) + 0x1000 + 2 * (v - 0x4000) end
local function var(v) return emu:read16(varAddr(v)) end
local VAR_MARK, MARK, VAR_DONE, DONE = 0x401E, 0x600E, 0x401F, 0x600D

local step, at, mashAt, markAt, doneAt = "load", 0, nil, nil, nil
H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE)
        step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        H.cmOff()
        emu:write16(varAddr(VAR_DONE), 0)
        emu:write16(varAddr(VAR_MARK), 0)
        emu:write16(varAddr(0x4000), 0xBEEF)          -- sentinel: the script must overwrite it
        H.log(("start party=%d cm=%s"):format(emu:read8(H.gPlayerPartyCount), tostring(H.cmIsOn())))
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

-- B through the hatch scene until the marker, then A on the lead in the party menu.
H.onFrame(function(f)
    if step ~= "running" or doneAt then return end
    if not markAt then
        if var(VAR_MARK) == MARK then
            emu:clearKey(K.B); markAt = f
            H.log(("marker f=%d party=%d"):format(f, emu:read8(H.gPlayerPartyCount)))
        elseif mashAt and f >= mashAt then
            if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
        end
        return
    end
    if f == markAt + 120 then
        emu:screenshot("/tmp/rr_relearn_" .. WANT .. "_menu.png")
        H.press(K.A, 8)
    end
    if var(VAR_DONE) == DONE then doneAt = f end
end)

local finished = false
H.onFrame(function(f)
    if finished then return end
    if doneAt and f == doneAt + 10 then
        finished = true
        local n, slot = var(0x4000), var(0x4001)
        H.log(("RELEARN count=%d slot=%d"):format(n, slot))
        H.assertTrue("the party menu picked the lead (slot 0)", slot == 0)
        if WANT == "zero" then
            H.assertTrue("level-cut count is 0 (Magikarp Lv1 knows Splash): got " .. n, n == 0)
        else
            H.assertTrue("any-level count > 0 (moves above Lv1): got " .. n, n > 0 and n < 100)
        end
        H.finish()
    elseif f > 6000 then
        finished = true
        H.assertTrue("the script finished (marker " .. tostring(markAt) .. ")", false)
        H.finish()
    end
end)
