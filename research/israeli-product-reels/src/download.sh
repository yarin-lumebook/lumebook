#!/bin/zsh
# Downloads each candidate reel (public, no sign-in) into the media project folder.
OUT=/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels/videos
cd $OUT
tail -n +2 "$1" | while IFS=$'\t' read code url src cat; do
  [ -f "$code.mp4" ] && continue
  yt-dlp --no-warnings -q -o "%(id)s.%(ext)s" --write-info-json "$url" || echo "FAIL $code"
  sleep 3
done
echo DONE
