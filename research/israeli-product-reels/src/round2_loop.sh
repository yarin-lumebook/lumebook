#!/bin/zsh
# Round 2 worker. Usage: round2_loop.sh frames|whisper
# Keeps walking priority3.txt until every candidate that has a video is processed and downloads are finished.
PY=/Users/yarinbruner/.claude/skills/watch-video/.venv/bin/python
M=/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels
cd ${0:A:h}
while true; do
  todo=0
  for c in $(cat priority3.txt); do
    [ -f $M/videos/$c.mp4 ] || { todo=1; continue; }
    if [ $1 = frames ]; then [ -f $M/analysis/$c/index.json ] || $PY process.py frames $c
    else [ -f $M/analysis/$c/whisper.srt ] || $PY process.py whisper $c; fi
  done
  dl=$(grep -l DONE $M/download3.log $M/download3b.log $M/download3c.log 2>/dev/null | wc -l)
  [ $todo = 0 ] && break
  [ $dl -ge 3 ] && break
  sleep 20
done
echo "$1 LOOP DONE"
