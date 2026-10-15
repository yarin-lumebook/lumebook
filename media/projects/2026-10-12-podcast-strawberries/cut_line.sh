#!/bin/bash
# Cut one dialogue line out of a longer take without touching the voice:
# sample-accurate trim, 15 ms fade in, 40 ms fade out, 48 kHz mono WAV.
# usage: cut_line.sh SRC START END OUT.wav
set -euo pipefail
src="$1"; start="$2"; end="$3"; out="$4"
fo=$(python3 -c "print(round(${end}-${start}-0.04,3))")
ffmpeg -hide_banner -loglevel error -y -i "$src" \
  -af "atrim=start=${start}:end=${end},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.015,afade=t=out:st=${fo}:d=0.04" \
  -ar 48000 -ac 1 -c:a pcm_s16le "$out"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")
lv=$(ffmpeg -hide_banner -nostats -i "$out" -af volumedetect -f null - 2>&1 | grep -E 'mean_volume|max_volume' | sed -E 's/.*(mean|max)_volume: /\1=/' | tr '\n' ' ')
echo "$(basename "$out") dur=${dur} ${lv}"
ffmpeg -hide_banner -nostats -i "$out" -af "silencedetect=noise=-32dB:d=0.05" -f null - 2>&1 | grep -oE "silence_(start|end): [0-9.]+" | paste - - | sed 's/^/    /' || true
