#!/bin/bash
# Place a dialogue line at a lead-in (ms) inside a silent clip of a fixed length (s), for use as a lip-sync reference.
# usage: pad_line.sh LINE.wav LEAD_MS TOTAL_S OUT.wav
set -euo pipefail
ffmpeg -hide_banner -loglevel error -y -i "$1" -af "adelay=${2}:all=1,apad=whole_dur=${3}" -ar 48000 -ac 1 -c:a pcm_s16le "$4"
span=$(ffmpeg -hide_banner -nostats -i "$4" -af "silencedetect=noise=-32dB:d=0.15" -f null - 2>&1 | grep -oE "silence_(start|end): [0-9.]+" | paste - - | tr '\n' ';' | tr '\t' ' ')
echo "$(basename "$4") dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$4") silences: ${span}"
