#!/bin/zsh
# Downloads each listed public Reel (no sign-in) into the media project folder; one at a time, 3 s apart.
OUT=/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-09-matan-nistor-reels/videos
cd $OUT
total=$(wc -l < "$1" | tr -d ' ')
i=0
while read code; do
  i=$((i+1))
  [ -f "$code.mp4" ] && { echo "PROGRESS $i/$total have $code"; continue; }
  yt-dlp --no-warnings -q -o "%(id)s.%(ext)s" --write-info-json "https://www.instagram.com/reel/$code/" || echo "FAIL $code"
  echo "PROGRESS $i/$total $code"
  sleep 3
done < "$1"
echo DONE
