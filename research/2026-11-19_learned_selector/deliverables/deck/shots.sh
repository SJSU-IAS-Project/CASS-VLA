#!/bin/bash
# usage: shots.sh N...  screenshots slides to scratchpad/shots
export LD_LIBRARY_PATH=/tmp/claude-1000/-home-user-CASS-VLA-research-2026-11-06-cass-vla-sota/14d0e54d-be2c-4176-989d-069698752c83/scratchpad/libs/usr/lib/x86_64-linux-gnu
export FONTCONFIG_FILE=/tmp/claude-1000/-home-user-CASS-VLA-research-2026-11-06-cass-vla-sota/14d0e54d-be2c-4176-989d-069698752c83/scratchpad/fonts.conf
B=/home/user/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell
D=/home/user/CASS-VLA/research/2026-11-19_learned_selector/deliverables/deck
O=/tmp/claude-1000/-home-user-CASS-VLA-research-2026-11-06-cass-vla-sota/14d0e54d-be2c-4176-989d-069698752c83/scratchpad/shots
for n in "$@"; do $B --headless --no-sandbox --hide-scrollbars --virtual-time-budget=3000 --window-size=1920,1080 --screenshot=$O/s$n.png "file://$D/deck.html#$n" >/dev/null 2>&1; done
