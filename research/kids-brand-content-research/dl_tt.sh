#!/bin/zsh
# slow sequential TikTok downloader with retries; args: handle:id ...
for p in "$@"; do h=${p%%:*}; i=${p##*:}
  [ -f videos/tt_$i.mp4 ] && continue
  for t in 1 2 3; do
    yt-dlp -q -o "videos/tt_%(id)s.%(ext)s" --write-info-json "https://www.tiktok.com/@$h/video/$i" 2>/dev/null && break
    sleep $((60*t))
  done
  [ -f videos/tt_$i.mp4 ] && echo "ok $i" || echo "FAIL $i"
  sleep 8
done
