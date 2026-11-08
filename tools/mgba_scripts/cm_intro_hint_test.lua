-- Live layer: the wild-intro roster hint (QoL B9, 2026-11-08; src/battle_marker.c).
-- On the TEST-ONLY ROM build/radicalred_cm_catchtest.gba (tools/tests/build_catch_testrom.py) the
-- bedroom console starts a wild Scyther battle. From the bedroom checkpoint the layer writes a
-- Pikachu lead, answers Yes at the console, and sets Character Mode as CM_CHAR the frame the
-- battle starts (CM_ON=1) -- before the intro is printed. It reads:
--   * r0 at the expander wrapper 0x080D77F4 (the shim's decision, in a real battle), and
--   * gDisplayedStringBattle (0x0202298C, the wrapper's literal) after the intro is expanded,
--     decoded, so the asserted text is what the player reads.
-- EXPECT=marker    -> "destined for <NAME>"  (Scyther is on Red's roster, char 1)
-- EXPECT=offroster -> "It is not on your roster."  (off Ash's, char 16)
-- EXPECT=vanilla   -> neither line (CM off, or the CM_NO_OFFROSTER control ROM)
-- Env: CM_ON, CM_CHAR, EXPECT, CM_EXPECT_CHECKS, SHOTS (dir).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local CM_ON = os.getenv("CM_ON") == "1"
local CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT = os.getenv("EXPECT") or "offroster"
local SHOTS = os.getenv("SHOTS")
local WRAPPER, DISPLAYED = 0x080D77F4, 0x0202298C
local WILD_A, WILD_B = 0x083FD284, 0x083FD297
-- RR's real intro strings (CFRU's BufferStringBattle; "A wild X appeared!")
local CFRU = {[0x090FF0D6] = true, [0x090FF125] = true, [0x090FF10E] = true}
local MARKER_LO, MARKER_HI = 0x08379000, 0x0838D628
local battleAt, introR0, introAt, keys = nil, nil, nil, {}

emu:setBreakpoint(function()
    if introR0 ~= nil or battleAt == nil then return end
    local r0 = emu:readRegister("r0")
    if r0 == WILD_A or r0 == WILD_B or CFRU[r0] or (r0 >= MARKER_LO and r0 < MARKER_HI) then
        introR0 = r0; introAt = H.frame()
    end
end, WRAPPER)

local function give_mon(addr, species, level)
    for i = 0, 99 do emu:write8(addr + i, 0) end
    for i = 8, 17 do emu:write8(addr + i, 0xFF) end
    for i = 20, 26 do emu:write8(addr + i, 0xFF) end
    emu:write8(addr + 18, 2); emu:write8(addr + 19, 2)
    local w = {}
    for i = 0, 23 do w[i] = 0 end
    local exp = level * level * level
    w[0] = species; w[2] = exp & 0xFFFF; w[3] = exp >> 16; w[4] = 0x7000
    w[6] = 84; w[7] = 98
    w[10] = 0x1E1E
    local sum = 0
    for i = 0, 23 do emu:write16(addr + 32 + 2 * i, w[i]); sum = sum + w[i] end
    emu:write16(addr + 28, sum & 0xFFFF)
    emu:write8(addr + 0x54, level)
    emu:write16(addr + 0x56, 120); emu:write16(addr + 0x58, 120)
    for i = 0, 4 do emu:write16(addr + 0x5A + 2 * i, 80) end
end

-- FireRed text: A-Z BB.., a-z D5.., space 00, ! AB, . AD, , B8, newline FE, end FF.
local function decode(addr, n)
    local out = {}
    for i = 0, n - 1 do
        local b = emu:read8(addr + i)
        if b == 0xFF then break
        elseif b >= 0xBB and b <= 0xD4 then out[#out + 1] = string.char(65 + b - 0xBB)
        elseif b >= 0xD5 and b <= 0xEE then out[#out + 1] = string.char(97 + b - 0xD5)
        elseif b == 0x00 then out[#out + 1] = " "
        elseif b == 0xAB then out[#out + 1] = "!"
        elseif b == 0xAD then out[#out + 1] = "."
        elseif b == 0xB8 then out[#out + 1] = ","
        elseif b == 0xFE then out[#out + 1] = "/"
        else out[#out + 1] = string.format("{%02X}", b) end
    end
    return table.concat(out)
end

local function press(k, at, len) keys[#keys + 1] = {k, at, at + (len or 20)} end
local function shot(n) if SHOTS then emu:screenshot(string.format("%s/%05d_%s.png", SHOTS, H.frame(), n)) end end

H.onFrame(function(f)
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    if f == 5 then
        H.cmOff()
        give_mon(H.gPlayerParty, 25, 50)
        emu:write8(H.gPlayerPartyCount, 1)
        press(K.UP, 20); press(K.A, 70); press(K.A, 200); press(K.A, 330)
    end
    if battleAt == nil and f > 30 and (emu:read8(0x03003529) >> 1) & 1 == 1 then
        battleAt = f
        H.log("battle started at frame " .. f)
        if CM_ON then H.cmOn(); H.setCharId(CHAR) end
    end
    if introAt and f == introAt + 90 then shot("intro") end
    if (introAt and f == introAt + 100) or f == 6000 then
        local text = decode(DISPLAYED, 80)
        H.log(string.format("intro r0=%s text=[%s]", introR0 and string.format("%08X", introR0) or "nil", text))
        H.assertTrue("the wild intro was expanded in a real battle", introR0 ~= nil)
        local destined = text:find("destined for", 1, true) ~= nil
        local off = text:find("It is not on your roster.", 1, true) ~= nil
        if EXPECT == "marker" then
            H.assertTrue("the intro names the character (destined for ...)", destined and not off)
        elseif EXPECT == "offroster" then
            H.assertTrue("the intro says 'It is not on your roster.'", off and not destined)
        else
            H.assertTrue("the vanilla intro (no roster line)", introR0 ~= nil and not off and not destined)
        end
        H.finish()
    end
end)
