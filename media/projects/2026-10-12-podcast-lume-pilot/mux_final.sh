#!/bin/bash
# Put the original dialogue line back on a generated take, untouched, at a chosen lead-in.
# The video stream is copied (no re-encode). usage: mux_final.sh VIDEO LINE.wav LEAD_MS OUT.mp4 OUT_AUDIO.wav
set -euo pipefail
video="$1"; line="$2"; lead="$3"; out="$4"; outwav="$5"
ffmpeg -hide_banner -loglevel error -y -i "$line" -af "adelay=${lead}:all=1,apad=whole_dur=4.0" -ar 48000 -ac 1 -c:a pcm_s16le "$outwav"
ffmpeg -hide_banner -loglevel error -y -i "$video" -i "$outwav" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -t 4.0 -movflags +faststart "$out"
ffprobe -v error -show_entries stream=codec_name,width,height,avg_frame_rate,nb_frames,sample_rate,channels:format=duration,size -of default=nw=1 "$out" | tr '\n' ' '; echo
