#!/bin/zsh
# progress-total: 62
codes=($(python3 -c "import json;print(' '.join(json.load(open('raw/ig-reels-grid.json'))))"))
n=0
for c in $codes; do
  n=$((n+1))
  if [[ ! -f ../../media/projects/2026-11-15-mebook-hooks/reels/$c.mp4 ]]; then
    yt-dlp -q --no-warnings -f "b[ext=mp4]/bv*+ba/b" --merge-output-format mp4 --write-info-json -o "../../media/projects/2026-11-15-mebook-hooks/reels/$c.%(ext)s" "https://www.instagram.com/reel/$c/" >/dev/null 2>>../../media/projects/2026-11-15-mebook-hooks/reels/errors.log || echo "FAIL $c" >> ../../media/projects/2026-11-15-mebook-hooks/reels/errors.log
  fi
  echo "PROGRESS $n/62 $c"
done
