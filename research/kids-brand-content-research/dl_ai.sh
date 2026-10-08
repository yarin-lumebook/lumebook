#!/bin/zsh
while read id url ctry; do
  [ -f videos/ai_$id.mp4 ] && continue
  for t in 1 2 3; do
    yt-dlp -q -f "mp4/best[ext=mp4]/best" --merge-output-format mp4 -o "videos/ai_$id.%(ext)s" --write-info-json "$url" 2>/dev/null && break
    sleep $((30*t))
  done
  [ -f videos/ai_$id.mp4 ] && echo "ok $id" || echo "FAIL $id"
  sleep 4
done < ai_urls.txt
