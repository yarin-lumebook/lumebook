#!/bin/zsh
ids=($(python3 -c "import json,os;print(' '.join(a['id'] for a in json.load(open('raw/ads.json'))['ads'] if not os.path.exists('../../media/projects/2026-11-15-mebook-hooks/ads/'+a['id']+'.mp4')))"))
total=${#ids}; n=0
for i in $ids; do
  n=$((n+1))
  yt-dlp -q --no-warnings -f "b[ext=mp4]/bv*+ba/b" --merge-output-format mp4 -o "../../media/projects/2026-11-15-mebook-hooks/ads/$i.%(ext)s" "https://www.facebook.com/ads/library/?id=$i" >/dev/null 2>>../../media/projects/2026-11-15-mebook-hooks/ads/errors.log || echo "FAIL $i" >> ../../media/projects/2026-11-15-mebook-hooks/ads/errors.log
  echo "PROGRESS $n/$total ad $i"
  /bin/sleep 45
done
