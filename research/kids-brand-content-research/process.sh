#!/bin/zsh
# usage: process.sh <video-file>   (watch-video acquire + overview contact sheets + dense hook window 0-3s)
f=$1
SK=/Users/yarinbruner/.claude/skills/watch-video
id=$(basename $f .mp4)
d=analysis/$id; mkdir -p $d
[ -f $d/source.json ] || python3 $SK/scripts/run.py acquire $f --output-dir $d > $d/acquire.log 2>&1
[ -f $d/visual-overview/index.md ] || python3 $SK/scripts/run.py sample-frames $f --output-dir $d/visual-overview --mode overview --scene-threshold 0.32 > $d/frames.log 2>&1
[ -f $d/window-hook/index.md ] || python3 $SK/scripts/run.py sample-frames $f --output-dir $d/window-hook --mode dense --start 0 --end 3.5 --fps 4 > $d/hook.log 2>&1
echo "$id frames done"
