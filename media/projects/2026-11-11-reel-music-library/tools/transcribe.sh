#!/bin/zsh
# Writes analysis/lyrics/<id>.json for every track: whisper.cpp small.en, greedy, non-speech tokens
# suppressed (-sns) and a "Song lyrics:" prompt (without them 10 of 25 songs came back as only [MUSIC]).
# Used to find where the singing is and to check the lyrics for words a kids' brand cannot use.
# Lyrics are other people's text: analysis/lyrics/ is in .gitignore, never commit or publish it.
# Run from the project root. Skips tracks already done.
D=media/projects/2026-11-11-reel-music-library
OUT=$D/analysis/lyrics
TMP=${TMPDIR:-/tmp}/reel-music-wav
mkdir -p $OUT $TMP
MODEL=~/.cache/whisper/ggml-small.en.bin
files=(${(f)"$(find $D/0* -maxdepth 1 -name '*.mp3' | sort)"})
total=${#files}
n=0
for f in $files; do
  n=$((n+1))
  id=$(echo "$f" | sed -E 's/.*\[([A-Za-z0-9_-]{11})\]\.mp3$/\1/')
  if [[ ! -s $OUT/$id.json ]]; then
    ffmpeg -y -v error -i "$f" -ar 16000 -ac 1 $TMP/$id.wav
    whisper-cli -m $MODEL -f $TMP/$id.wav -t 6 -bs 1 -bo 1 -sns --prompt "Song lyrics:" -oj -of $OUT/$id -np >/dev/null 2>&1 || echo "ERROR $id"
    rm -f $TMP/$id.wav
  fi
  echo "PROGRESS $n/$total $id"
done
echo DONE
