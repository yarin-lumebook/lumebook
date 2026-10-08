#!/bin/zsh
# args: prefix code...  (downloads public IG reels one by one)
pre=$1; shift
for c in "$@"; do
  [ -f videos/${pre}_$c.mp4 ] && continue
  yt-dlp -q -o "videos/${pre}_$c.%(ext)s" --write-info-json "https://www.instagram.com/reel/$c/" 2>/dev/null && echo "ok $c" || echo "FAIL $c"
  sleep 3
done
