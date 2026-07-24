-- From the bedroom checkpoint savestate (pass via -t): open START menu,
-- move the cursor DOWN N times (env RR_CARD_DOWNS, default 1), press A,
-- and screenshot. Used by the sprite pilot to render the trainer card.
local H = dofile("tools/mgba_scripts/harness.lua")
local K = H.KEY
local DOWNS = tonumber(os.getenv("RR_CARD_DOWNS") or "1")

local function tap(f, at, key)
    if f == at then emu:addKey(key) end
    if f == at + 12 then emu:clearKey(key) end
end

H.onFrame(function(f)
    tap(f, 60, K.START)
    if f == 150 then emu:screenshot("/tmp/rr_menu.png") end
    for i = 1, DOWNS do
        tap(f, 150 + i * 40, K.DOWN)
    end
    tap(f, 200 + DOWNS * 40, K.A)
    if f == 420 + DOWNS * 40 then
        emu:screenshot("/tmp/rr_card.png")
        H.log("card shot taken, downs=" .. DOWNS)
        H.finish()
    end
end)
