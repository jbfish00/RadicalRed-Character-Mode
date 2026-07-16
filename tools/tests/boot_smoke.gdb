# Boot smoke test: let the ROM boot and run ~15s of real gameplay loop
# (intro/title), then verify the game is alive and sane:
#   - gMain.vblankCounter2 (0x03003114) advances between two samples
#   - counter rate is ~60Hz (game loop actually pumping, not stalled)
#   - gMain.callback2 (0x030030F4) points into ROM, odd (Thumb) pointer
# gMain = 0x030030F0 (BPRE), same layout as the Unbound/CFRU harness this
# is ported from. Uses timed self-SIGINT to interrupt `continue` (mGBA's
# stub has no async interrupt from batch mode).

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import threading, os, signal
threading.Timer(10.0, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
end
continue

printf "sample1 PC: 0x%08x\n", (unsigned int)$pc
set $c1 = *(unsigned int*)0x03003114
set $cb1 = *(unsigned int*)0x030030F4
printf "sample1 vblankCounter2: %u  callback2: 0x%08x\n", $c1, $cb1

python
import threading, os, signal
threading.Timer(5.0, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
end
continue

printf "sample2 PC: 0x%08x\n", (unsigned int)$pc
set $c2 = *(unsigned int*)0x03003114
set $cb2 = *(unsigned int*)0x030030F4
printf "sample2 vblankCounter2: %u  callback2: 0x%08x\n", $c2, $cb2

printf "S1 vblank counter advancing (want 1): %d\n", ($c2 > $c1)
printf "S2 counter rate sane 60Hz-ish (want 1): %d\n", (($c2 - $c1) > 100) && (($c2 - $c1) < 2000)
printf "S3 callback2 in ROM (want 1): %d\n", ($cb2 >= 0x08000000) && ($cb2 < 0x0A000000)
printf "S4 callback2 odd Thumb ptr (want 1): %d\n", (($cb2 & 1) == 1)

echo \n=== TESTS DONE ===\n
disconnect
quit
