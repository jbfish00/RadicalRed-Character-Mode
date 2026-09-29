#!/bin/sh
# Build this repo's own patched headless mGBA -> tools/mgba_src/build/mgba-headless.
#
# The live test layers need two things stock headless mGBA lacks: a video
# buffer (emu:screenshot segfaults without one) and a debugger attached when
# MGBA_HEADLESS_DEBUGGER=1 (breakpoints silently never fire without one).
# tools/patches/mgba-headless-local.patch adds both. It is the same patch
# Seaglass-Character-Mode carries, at the same upstream commit.
#
# Until 2026-09-29 every runner here used Seaglass's build by path, so the live
# suite could not run from a fresh clone of this repo alone.
#
# The source tree is gitignored; only the patch and this script are tracked.
# Usage: sh tools/build_mgba.sh        (idempotent; re-running rebuilds)
set -e
cd "$(dirname "$0")"          # tools/

PIN=5157ce208a5965e8a47bf5b48b5aae5198c22a5e
SRC=mgba_src
PATCH=patches/mgba-headless-local.patch

if [ ! -d "$SRC/.git" ]; then
    git clone --quiet https://github.com/mgba-emu/mgba "$SRC"
fi
( cd "$SRC"
  git fetch --quiet origin "$PIN" 2>/dev/null || true
  git checkout --quiet --force "$PIN"
  git apply "../$PATCH" )
cmake -B "$SRC/build" -S "$SRC" -DBUILD_HEADLESS=ON -DBUILD_QT=OFF \
      -DBUILD_SDL=OFF -DCMAKE_BUILD_TYPE=Release -DUSE_LIBZIP=OFF > /dev/null
cmake --build "$SRC/build" --target mgba-headless -j"$(nproc)" > /dev/null
echo "built tools/$SRC/build/mgba-headless (mGBA $PIN + $PATCH)"
