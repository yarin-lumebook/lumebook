#!/bin/zsh
# Walks all120_codes.txt in order and runs one process.py step per Reel. Waits for videos still downloading,
# skips Reels whose download failed (FAIL line in the download logs; those are fetched through the browser later).
# Usage: queue.sh frames|whisper   (two whisper queues can run at once; the lock file keeps them apart)
cd /Users/yarinbruner/Claude/Projects/Lumebook/research/matan-nistor-reels/src
PY=/Users/yarinbruner/.claude/skills/watch-video/.venv/bin/python
M=/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-09-matan-nistor-reels
total=$(wc -l < all120_codes.txt | tr -d ' ')
i=0
for c in $(cat all120_codes.txt); do
  i=$((i+1))
  while [ ! -f $M/videos/$c.mp4 ]; do
    grep -qs "FAIL $c" $M/download*.log && break
    sleep 10
  done
  if [ -f $M/videos/$c.mp4 ]; then
    $PY process.py $1 $c | grep -v '^PROGRESS'
    echo "PROGRESS $i/$total $1 $c"
  else
    echo "PROGRESS $i/$total $1 $c skipped (no video)"
  fi
done
echo "QUEUE $1 DONE"
