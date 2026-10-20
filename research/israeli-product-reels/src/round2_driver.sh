#!/bin/zsh
# Round 2 (15 Oct): frames for every downloaded Reel, then Whisper in two queues, until every candidate is done.
PY=/Users/yarinbruner/.claude/skills/watch-video/.venv/bin/python
M=/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels
cd ${0:A:h}
wq() { for c in $(cat priority3.txt); do [ -f $M/videos/$c.mp4 ] && $PY process.py whisper $c; done }
for round in $(seq 1 40); do
  for c in $(cat priority3.txt); do
    [ -f $M/videos/$c.mp4 ] && [ ! -f $M/analysis/$c/index.json ] && $PY process.py frames $c
  done
  (wq &) ; wq
  grep -q DONE $M/download3.log && [ $round -gt 1 ] && break
  sleep 30
done
echo DRIVER DONE
