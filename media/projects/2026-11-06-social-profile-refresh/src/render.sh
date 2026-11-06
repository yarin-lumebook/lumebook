#!/bin/zsh
# Render the two pages to PNG with headless Chrome. Usage: src/render.sh [out-dir]
# Needs src/mascot_cut.png first: /usr/bin/python3 src/cutout.py ../../../shared/brand/mascot_closeup_dark_purple_headroom.png src/mascot_cut.png 30
here="${0:A:h}"
out="${1:-$here/../final}"
mkdir -p "$out"
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
shot() { # page width height output-name
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=4000 --window-size=$2,$3 --screenshot="$out/$4.png" "file://$here/$1.html" 2>/dev/null
}
shot cover 1640 624 lumebook-facebook-cover-1640x624
shot profile 1080 1080 lumebook-profile-1080
shot cover-light 1640 624 lumebook-facebook-cover-light-1640x624
shot profile-light 1080 1080 lumebook-profile-light-1080
ls -la "$out"
