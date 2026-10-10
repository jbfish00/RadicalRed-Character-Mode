-- Live layer: 100% catch for on-roster species (2026-10-09).
-- On the TEST-ONLY ROM build/radicalred_cm_catchtest.gba
-- (tools/tests/build_catch_testrom.py): the bedroom console runs
--   additem POKE_BALL 10 ; setwildbattle 123 lv30 ; dowildbattle ; end
-- From the bedroom checkpoint (/tmp/rr_ss_bedroom.ss), the layer writes a
-- Pikachu L50 lead (key-0 substructures: personality 0, OTID 0), answers Yes at
-- the console, sets Character Mode as CM_CHAR once the battle has started
-- (CM_ON=1), opens the Bag through the battle menu and throws ONE Poke Ball
-- at the wild Scyther (catch rate 45, full HP). Breakpoints on both successors
-- of the hooked decision (0x0907D556 caught, 0x0907D590 shake path) read r4,
-- the odds the game decides on, the first time either is reached:
--   EXPECT=sure    -> odds 255, and the battle ends (caught)
--   EXPECT=vanilla -> odds below 255; outcome not asserted
--   EXPECT=miss    -> odds below 255 and the throw fails (still in battle)
-- Scyther is on Red's roster (1) and off Ash's (16).
-- Env: CM_ON, CM_CHAR, SEED, EXPECT, CM_EXPECT_CHECKS, SHOTS (dir).
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local SPECIES = 123
local CM_ON = os.getenv("CM_ON") == "1"
local CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT = os.getenv("EXPECT") or "sure"
local SEED = tonumber(os.getenv("SEED") or "1")
local SHOTS = os.getenv("SHOTS")
local RNG = 0x03005000                       -- gRngValue (FireRed LCG)
local odds, battleAt, battleCb2, bagOpenAt, throwAt, keys = nil, nil, nil, nil, nil, {}

local function grab() if odds == nil then odds = emu:readRegister("r4") end end
emu:setBreakpoint(grab, 0x0907D556)
emu:setBreakpoint(grab, 0x0907D590)

-- A Gen 3 party Pokemon with personality 0 and OTID 0: key 0, substructure
-- order GAEM, so the 48 data bytes are plain. Checksum = sum of the 24 words.
local function give_mon(addr, species, level)
    for i = 0, 99 do emu:write8(addr + i, 0) end
    for i = 8, 17 do emu:write8(addr + i, 0xFF) end
    for i = 20, 26 do emu:write8(addr + i, 0xFF) end
    emu:write8(addr + 18, 2); emu:write8(addr + 19, 2)     -- language; hasSpecies
    local w = {}
    for i = 0, 23 do w[i] = 0 end
    local exp = level * level * level                       -- medium-fast growth (Pikachu)
    w[0] = species; w[2] = exp & 0xFFFF; w[3] = exp >> 16; w[4] = 0x7000
    w[6] = 84; w[7] = 98                                    -- ThunderShock, Quick Attack
    w[10] = 0x1E1E
    local sum = 0
    for i = 0, 23 do emu:write16(addr + 32 + 2 * i, w[i]); sum = sum + w[i] end
    emu:write16(addr + 28, sum & 0xFFFF)
    emu:write8(addr + 0x54, level)
    emu:write16(addr + 0x56, 120); emu:write16(addr + 0x58, 120)
    for i = 0, 4 do emu:write16(addr + 0x5A + 2 * i, 80) end
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
        press(K.UP, 20); press(K.A, 70); press(K.A, 200); press(K.A, 330)   -- face the console, talk, Yes
    end
    if battleAt == nil and f > 30 and (emu:read8(0x03003529) >> 1) & 1 == 1 then
        battleAt = f
        H.log("battle started at frame " .. f)
        if CM_ON then H.cmOn(); H.setCharId(CHAR) end
    end
    if battleAt and f == battleAt + 300 then battleCb2 = emu:read32(0x030030F4) end
    if battleCb2 and not bagOpenAt and f > battleAt + 300 then
        if emu:read32(0x030030F4) ~= battleCb2 then
            bagOpenAt = f
            H.log("bag opened at frame " .. f)
        elseif (f - battleAt) % 120 == 0 then
            emu:write8(0x02023FF8, 1); press(K.A, f + 1)      -- gActionSelectionCursor[0] = BAG
        end
    end
    if bagOpenAt and SHOTS and (f - bagOpenAt) % 200 == 0 then shot("g") end
    if bagOpenAt and f == bagOpenAt + 1 then
        local n = 2   -- Items -> Key Items -> Poke Balls
        for i = 1, n do press(K.RIGHT, f + 60 * i) end
        press(K.A, f + 300)                                   -- Poke Ball x10
        throwAt = f + 380
        press(K.A, throwAt)                                   -- Use
        for t = f + 800, f + 3400, 80 do press(K.B, t) end
    end
    if throwAt and f == throwAt - 2 then
        emu:write32(RNG, (SEED * 0x9E3779B9 + 0x7F4A7C15) & 0xFFFFFFFF)
    end
    if f == 9000 then
        -- Caught = the battle is over (gMain.inBattle clear): the lead never
        -- attacks and B never picks Run, so nothing else ends it here.
        local caught = (emu:read8(0x03003529) >> 1) & 1 == 0
        H.log(string.format("odds at the decision=%s battle over=%s", tostring(odds), tostring(caught)))
        H.assertTrue("a wild battle started", battleAt ~= nil)
        if EXPECT == "sure" then
            H.assertEq("odds at the caught/shake decision", odds, 255)
            H.assertTrue("caught on the first throw at full HP (the battle ended)", caught)
        elseif EXPECT == "miss" then
            H.assertTrue("odds are the ball's own (below 255)", odds ~= nil and odds < 255)
            H.assertTrue("this seed's vanilla roll breaks out (still in battle)", not caught)
        else
            H.assertTrue("the throw reached the decision", odds ~= nil)
            H.assertTrue("odds are the ball's own (below 255)", odds ~= nil and odds < 255)
        end
        H.finish()
    end
end)
