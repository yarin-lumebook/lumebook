#!/bin/zsh
# usage: transcribe.sh <video-file> <lang he|en>   (machine transcript via local whisper, capped at 120s)
f=$1; lang=$2
id=$(basename $f .mp4); d=analysis/$id; mkdir -p $d
[ -f $d/whisper.srt ] && { echo "$id already"; exit 0; }
ffmpeg -loglevel error -y -i $f -t 120 -ar 16000 -ac 1 $d/audio.wav
if [ $lang = he ]; then M="$HOME/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin"; else M=$HOME/.cache/whisper/ggml-small.en.bin; fi
whisper-cli -m "$M" -l $lang -t 4 -osrt -otxt -of $d/whisper -f $d/audio.wav > $d/whisper.log 2>&1
rm -f $d/audio.wav
echo "$id transcribed ($lang)"
