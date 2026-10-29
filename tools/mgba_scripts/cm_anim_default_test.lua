-- LIVE layer (QoL A3, 2026-10-28): with no save, FireRed's SetDefaultOptions (0x08054954) runs at boot
-- (CB2_InitCopyrightScreenAfterBootup) and its values are what a new game starts with. After it has run, read
-- SaveBlock2+0x15 bit 2 (optionsBattleSceneOff). WANT=1 on the shipped ROM, WANT=0 on the control (base byte).
-- Shared by Radical Red and Unbound (identical SetDefaultOptions address and gSaveBlock2Ptr 0x0300500C).
local H = dofile(os.getenv("CM_HARNESS") or "tools/mgba_scripts/harness.lua")
local want = tonumber(os.getenv("WANT") or "1")
local ran = 0
H.breakpoint("SetDefaultOptions", 0x08054954, function() ran = ran + 1 end)
H.onFrame(function(f)
    if f ~= 600 then return end
    local sb2 = emu:read32(0x0300500C)
    H.assertTrue("SetDefaultOptions ran at boot", ran >= 1)
    H.assertEq("battle animations off (SaveBlock2+0x15 bit 2)", (emu:read8(sb2 + 0x15) >> 2) & 1, want)
    H.finish()
end)
