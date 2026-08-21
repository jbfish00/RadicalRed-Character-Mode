-- RadicalRed Character Mode -- reusable mgba-headless test harness.
-- Ported from the Lazarus/Seaglass sibling projects' harness.lua (same
-- mGBA scripting API), with RadicalRed's own confirmed RAM addresses.
--
-- RAM anchors below are RadicalRed's vanilla-FireRed layout (per this
-- repo's docs/ROUTINE_MAP.md and the already-passing GDB test fixtures
-- tools/tests/shim_test.gdb / tools/tests/wild_encounter_shim_test.py):
--   gSaveBlock1Ptr = 0x03005008 (pointer; SB1 +0x00 x, +0x02 y, +0x04
--     mapGroup, +0x05 mapNum)
--   gPlayerParty = 0x02024284 (stride 100), gPlayerPartyCount = 0x02024029
--   FLAG_CHARACTER_MODE (0x18FE) lives at fixed EWRAM byte 0x0203B373,
--     bit 0x40 -- CONFIRMED working address (not re-derived from SB1+off,
--     since the brief's naive SB1+0xEE0 arithmetic didn't reconcile with
--     this constant -- see session notes; SaveBlock1's EWRAM address is
--     fixed for this ROM/build so the flat constant is trustworthy as
--     long as gSaveBlock1Ptr reads the same value we've seen before,
--     which H.checkSaveBlockAnchor() verifies at runtime).
--   VAR_CHARACTER_ID (0x51FD) lives at fixed EWRAM 0x0203B76E (u16).
local H = {}

H.KEY = {
    A = 0, B = 1, SELECT = 2, START = 3,
    RIGHT = 4, LEFT = 5, UP = 6, DOWN = 7,
    R = 8, L = 9,
}

H.gSaveBlock1Ptr = 0x03005008
H.SB1_POS_X  = 0x00
H.SB1_POS_Y  = 0x02
H.SB1_MAPGRP = 0x04
H.SB1_MAPNUM = 0x05

H.gPlayerParty = 0x02024284
H.PARTY_STRIDE = 100
H.gPlayerPartyCount = 0x02024029

-- Confirmed-working flat addresses (see header comment above).
H.FLAG_BYTE = 0x0203B373
H.FLAG_MASK = 0x40   -- bit 6 == FLAG_CHARACTER_MODE (0x18FE & 7 == 6)
H.VAR_ADDR  = 0x0203B76E

H.SHIM_ENTRY = 0x08CE0000
H.BP_CALL = 0x08CE0052  -- bl <CreateWildMon thunk>; r0 = final species

function H.cmOn()
    emu:write8(H.FLAG_BYTE, emu:read8(H.FLAG_BYTE) | H.FLAG_MASK)
end
function H.cmOff()
    emu:write8(H.FLAG_BYTE, emu:read8(H.FLAG_BYTE) & ~H.FLAG_MASK & 0xFF)
end
function H.cmIsOn()
    return (emu:read8(H.FLAG_BYTE) & H.FLAG_MASK) ~= 0
end
function H.setCharId(id)
    emu:write16(H.VAR_ADDR, id)
end
function H.getCharId()
    return emu:read16(H.VAR_ADDR)
end

function H.checkSaveBlockAnchor()
    return emu:read32(H.gSaveBlock1Ptr)
end

function H.readPos()
    local b = emu:read32(H.gSaveBlock1Ptr)
    if b < 0x02000000 or b >= 0x02040000 then return nil end
    return {
        x = emu:read16(b + H.SB1_POS_X), y = emu:read16(b + H.SB1_POS_Y),
        grp = emu:read8(b + H.SB1_MAPGRP), num = emu:read8(b + H.SB1_MAPNUM),
    }
end

-- ------------------------------------------------------------------- memory
function H.rd8(a)  return emu:read8(a)  end
function H.rd16(a) return emu:read16(a) end
function H.rd32(a) return emu:read32(a) end
function H.wr8(a, v)  emu:write8(a, v)  end
function H.wr16(a, v) emu:write16(a, v) end
function H.wr32(a, v) emu:write32(a, v) end

function H.hex(v, width)
    return string.format("0x%0" .. (width or 8) .. "X", v)
end

-- ------------------------------------------------------------------ assertions
local passes, failures = 0, {}
function H.log(msg)
    console:log("HARNESS " .. tostring(msg))
end
function H.assertEq(what, got, want)
    if got == want then
        passes = passes + 1
        H.log("PASS " .. what .. " = " .. tostring(got))
        return true
    end
    local msg = what .. ": got " .. tostring(got) .. ", want " .. tostring(want)
    table.insert(failures, msg)
    H.log("FAIL " .. msg)
    return false
end
function H.finish()
    -- ⚠️ 2026-08-20 (../game_plans/rowe_parity.md §1): until today this function
    -- emitted RESULT: PASS whenever #failures == 0, while `passes` was printed
    -- and never tested. A layer that asserted NOTHING -- because it
    -- mis-navigated, lost its savestate, wedged before reaching its checks, or
    -- had them edited away -- was indistinguishable from one that passed, and
    -- every runner in this repo greps only the RESULT line. ROWE had the
    -- identical hole: deleting 35 of its 36 Check() calls still reported
    -- ALL RUNS PASS.
    --
    -- Both guards live HERE rather than only in the runners, so an ad-hoc
    -- invocation cannot lie either:
    --   1. zero assertions is a FAIL, unconditionally.
    --   2. CM_EXPECT_CHECKS=<n> pins the tally. A changed tally is a
    --      regression even when every assertion that DID run passed -- that is
    --      how a probe list that generated fewer rows, or a loop that exited
    --      early, goes green while quietly checking less.
    local expected = nil
    if os and os.getenv then
        expected = tonumber(os.getenv("CM_EXPECT_CHECKS") or "")
    end
    -- Count assertions RUN, not assertions PASSED. Comparing against `passes`
    -- means a single genuine failure also trips the tally guard, which reports
    -- a structural change ("expected 3, ran 2") when nothing structural
    -- happened -- misleading on exactly the runs someone is already debugging.
    local ran = passes + #failures
    if ran == 0 then
        table.insert(failures,
            "ZERO assertions ran -- a run that asserts nothing is not a pass")
    elseif expected and ran ~= expected then
        table.insert(failures, string.format(
            "TALLY CHANGED: expected %d assertions, ran %d -- a changed tally is "
            .. "a regression even when the run says PASS. If the change is "
            .. "intentional, update the expected count in the runner.",
            expected, ran))
    end
    H.log("---- SUMMARY ----")
    H.log(string.format("PASSED %d, FAILED %d", passes, #failures))
    for _, f in ipairs(failures) do H.log("  FAILURE: " .. f) end
    H.log("RESULT: " .. (#failures == 0 and "PASS" or "FAIL"))
    if os and os.exit then os.exit(#failures == 0 and 0 or 1) end
end

-- ---------------------------------------------------------------------- input
local frame = 0
local frameHooks = {}
function H.frame() return frame end
function H.onFrame(fn) table.insert(frameHooks, fn) end

local pending = {}
local active = nil
local activeUntil = 0
function H.press(key, frames, gap)
    table.insert(pending, { key = key, frames = frames or 32, gap = gap or 8 })
end
function H.sequence(steps)
    for _, s in ipairs(steps) do H.press(s[1] or s.key, s[2] or s.frames, s[3] or s.gap) end
end
local function pumpInput()
    if active then
        if frame >= activeUntil then
            emu:clearKey(active.key)
            activeUntil = frame + active.gap
            active = nil
        end
        return
    end
    if frame < activeUntil then return end
    local step = table.remove(pending, 1)
    if step then
        emu:addKey(step.key)
        active = step
        activeUntil = frame + step.frames
    end
end
function H.clearQueue()
    pending = {}
    if active then emu:clearKey(active.key); active = nil end
end

-- ------------------------------------------------------------------ breakpoints
-- REQUIRES MGBA_HEADLESS_DEBUGGER=1 (stock headless never creates
-- core->debugger; our sibling projects' patched headless build does when
-- this env var is set).
function H.breakpoint(name, addr, fn)
    local id = emu:setBreakpoint(function()
        local pc = emu:readRegister("pc")
        if fn then fn(frame, pc) end
    end, addr)
    if not id or id < 0 then
        error("H.breakpoint('" .. name .. "') failed to register (id=" ..
            tostring(id) .. ") -- run with MGBA_HEADLESS_DEBUGGER=1")
    end
    return id
end

-- ---------------------------------------------------------------------- driver
callbacks:add("frame", function()
    frame = frame + 1
    pumpInput()
    for _, fn in ipairs(frameHooks) do fn(frame) end
end)

return H
