#!/bin/zsh
# Downloads the playlist (tools/download.sh since 11 Nov) as mp3 only into _raw/ (11 Nov 2026). Run from the project root.
D=media/projects/2026-11-11-reel-music-library
total=$(wc -l < $D/ids.txt | tr -d ' ')
while read id; do
  if ! ls $D/_raw/*"[$id]".mp3 >/dev/null 2>&1; then
    yt-dlp -q --no-warnings --no-playlist -x --audio-format mp3 --audio-quality 2 --embed-metadata \
      --windows-filenames -o "$D/_raw/%(title).90s [%(id)s].%(ext)s" "https://www.youtube.com/watch?v=$id" 2>&1 | grep -i error
  fi
  echo "PROGRESS $(ls $D/_raw/*.mp3 2>/dev/null | wc -l | tr -d ' ')/$total $id"
done < $D/ids.txt
echo "DONE"
