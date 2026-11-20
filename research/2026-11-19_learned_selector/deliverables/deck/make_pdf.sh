#!/bin/bash
# Needs a Chromium headless shell. FONTCONFIG_FILE and LD_LIBRARY_PATH point at local copies of Roboto and missing system libraries.
export LD_LIBRARY_PATH=/tmp/claude-1000/-home-user-CASS-VLA-research-2026-11-06-cass-vla-sota/14d0e54d-be2c-4176-989d-069698752c83/scratchpad/libs/usr/lib/x86_64-linux-gnu
export FONTCONFIG_FILE=/tmp/claude-1000/-home-user-CASS-VLA-research-2026-11-06-cass-vla-sota/14d0e54d-be2c-4176-989d-069698752c83/scratchpad/fonts.conf
cd "$(dirname "$0")"
~/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell --headless --no-sandbox --no-pdf-header-footer --virtual-time-budget=5000 --print-to-pdf=deck.pdf "file://$PWD/deck.html"
