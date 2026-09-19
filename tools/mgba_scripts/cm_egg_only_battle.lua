-- THE EXPERIMENT (rowe_parity.md §13.47): start a real WILD BATTLE with a party
-- that holds nothing but eggs, and watch what the engine does.
--
-- Built by tools/tests/build_eggbattle_testrom.py: the bedroom console runs
--   giveegg 60 ; giveegg 60 ; setwildbattle 16 lv3 ; dowildbattle ; end
-- so the party is [egg, egg] and a real battle starts with no walk to grass.
--
-- ⚠️ This measures the ENGINE, not Character Mode. Nothing of the sweep or the
-- PC hook runs. A verdict here is about what party states Gen 3 tolerates.
--
-- What we watch for, in order of severity:
--   CRASH/HANG  -- pc stops advancing, or the screen freezes
--   BATTLE RAN  -- gBattleOutcome resolves; note WHAT got sent out
--   REFUSED     -- the battle never starts (engine declined)
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local STATE = "/tmp/rr_ss_bedroom.ss"
local PREFIX = os.getenv("CM_SHOT_PREFIX") or "/tmp/rr_eggbattle"

-- gEnemyParty = gPlayerParty - 6*100 (derived, docs/ROUTINE_MAP.md)
local gEnemyParty = H.gPlayerParty - 600
local gBattleOutcome = 0x0202433A   -- FireRed; read loosely, reported not asserted

local function sl(base, i)
    local b = base + i * H.PARTY_STRIDE
    local fl = emu:read8(b + 19)
    return { pers = emu:read32(b), isEgg = (fl & 0x04) ~= 0,
             hasSp = (fl & 0x02) ~= 0, lvl = emu:read8(b + 84),
             hp = emu:read16(b + 86) }
end

local function dump(tag)
    local n = emu:read8(H.gPlayerPartyCount)
    H.log(("---- %s  partyCount=%d"):format(tag, n))
    for i = 0, 5 do
        local s = sl(H.gPlayerParty, i)
        if s.hasSp or s.pers ~= 0 then
            H.log(("   party%d pers=%08X isEgg=%s lvl=%d hp=%d"):format(
                i, s.pers, tostring(s.isEgg), s.lvl, s.hp))
        end
    end
    local e = sl(gEnemyParty, 0)
    if e.hasSp then
        H.log(("   enemy0 pers=%08X isEgg=%s lvl=%d hp=%d"):format(
            e.pers, tostring(e.isEgg), e.lvl, e.hp))
    end
end

local step, at, mashAt = "load", 0, nil
local eggOnlySeen, battleSeen, frozenSince, lastHash = false, false, nil, nil
local pcStalled, lastPC, samePC = false, nil, 0
local shots = 0

H.onFrame(function(f)
    if step == "load" and f == 5 then
        emu:loadStateFile(STATE); step, at = "settle", f
    elseif step == "settle" and f - at == 60 then
        H.cmOff(); dump("start")
        emu:addKey(K.UP); step, at = "faced", f
    elseif step == "faced" and f - at == 20 then
        emu:clearKey(K.UP); step, at = "talk", f
    elseif step == "talk" and f - at == 30 then
        emu:addKey(K.A); step, at = "talk2", f
    elseif step == "talk2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "prompt", f
    elseif step == "prompt" and f - at == 90 then
        emu:addKey(K.A); step, at = "yes2", f
    elseif step == "yes2" and f - at == 12 then
        emu:clearKey(K.A); step, at = "running", f; mashAt = f + 30
    end
end)

-- Liveness: is the game still advancing? A hang is the worst outcome and the
-- easiest to miss -- a frozen screen with a running CPU looks identical to a
-- paused one in a screenshot. gRngValue advances on essentially every frame of
-- normal play, so a long run of identical values means the game stopped doing
-- work, not merely that the picture stopped changing.
local gRngValue = 0x03005000
H.onFrame(function(f)
    if step ~= "running" then return end
    local cur = emu:read32(gRngValue)
    if lastPC ~= nil and cur == lastPC then samePC = samePC + 1
    else samePC = 0 end
    lastPC = cur
    if samePC > 600 and not pcStalled then
        pcStalled = true
        H.log(("*** GAME APPEARS STALLED: gRngValue unchanged (%08X) for "
               .. "600 frames, f=%d ***"):format(cur, f))
    end
end)

H.onFrame(function(f)
    if step ~= "running" then return end
    local n = emu:read8(H.gPlayerPartyCount)
    if not eggOnlySeen and n == 2 then
        local a, b = sl(H.gPlayerParty, 0), sl(H.gPlayerParty, 1)
        if a.isEgg and b.isEgg then
            eggOnlySeen = true
            dump(("EGG-ONLY PARTY at f=%d"):format(f))
            emu:screenshot(PREFIX .. "_eggonly.png")
        end
    end
    local e = sl(gEnemyParty, 0)
    if not battleSeen and e.hasSp and e.hp > 0 then
        battleSeen = true
        dump(("ENEMY PARTY POPULATED (battle starting) at f=%d"):format(f))
        emu:screenshot(PREFIX .. "_battlestart.png")
    end
    if f % 300 == 0 and shots < 8 then
        shots = shots + 1
        emu:screenshot(("%s_t%d.png"):format(PREFIX, shots))
    end
end)

H.onFrame(function(f)
    if step ~= "running" or mashAt == nil or f < mashAt then return end
    if (f // 22) % 2 == 0 then emu:addKey(K.B) else emu:clearKey(K.B) end
end)

H.onFrame(function(f)
    if f == 4200 then
        dump("final")
        emu:screenshot(PREFIX .. "_final.png")
        H.assertTrue("an EGG-ONLY party was reached", eggOnlySeen)
        H.assertTrue("the game never stalled for 600+ frames", not pcStalled)
        H.log(("OBSERVED: eggOnlyParty=%s battleStarted=%s stalled=%s")
              :format(tostring(eggOnlySeen), tostring(battleSeen),
                      tostring(pcStalled)))
        H.finish()
    end
end)
