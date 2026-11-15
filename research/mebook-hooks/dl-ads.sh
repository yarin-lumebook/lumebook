#!/bin/zsh
# progress-total: 21
ids=($(python3 -c "import json;print(' '.join(a['id'] for a in json.load(open('raw/ads.json'))['ads']))"))
n=0
for i in $ids; do
  n=$((n+1))
  if [[ ! -f ../../media/projects/2026-11-15-mebook-hooks/ads/$i.mp4 ]]; then
    yt-dlp -q --no-warnings -f "b[ext=mp4]/bv*+ba/b" --merge-output-format mp4 -o "../../media/projects/2026-11-15-mebook-hooks/ads/$i.%(ext)s" "https://www.facebook.com/ads/library/?id=$i" >/dev/null 2>>../../media/projects/2026-11-15-mebook-hooks/ads/errors.log || echo "FAIL $i" >> ../../media/projects/2026-11-15-mebook-hooks/ads/errors.log
  fi
  echo "PROGRESS $n/21 ad $i"
done
