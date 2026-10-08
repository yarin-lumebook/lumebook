#!/bin/zsh
for f in videos/tt_*.mp4 videos/igen_*.mp4(N); do ./process.sh $f en; ./transcribe.sh $f en; done
