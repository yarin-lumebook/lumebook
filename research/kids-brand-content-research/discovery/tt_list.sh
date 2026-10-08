#!/bin/zsh
# usage: tt_list.sh handle [n]
h=$1; n=${2:-80}
out=discovery/tt_$h.jsonl
yt-dlp --flat-playlist -j --playlist-end $n "https://www.tiktok.com/@$h" > $out 2> discovery/tt_$h.err
echo "$h $(wc -l < $out)"
