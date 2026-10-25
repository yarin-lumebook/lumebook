#!/bin/zsh
# Puts sound under the six Genjutsu Lite results: the trend's own audio from the same start
# point as the trimmed reference (refs/README notes), levelled to -14 LUFS, short fades at cuts.
# Book video: generated Seed Audio bed (audio/01-book-3d-sound-seed-v1.wav).
cd "${0:A:h}/.."
mux() { # slug audio_file offset fade_in
  local v=results/$1-v1-1080p.mp4 a=$2 off=$3 fin=$4
  local d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $v)
  local fo=$(python3 -c "print(max(0, $d - 0.5))")
  ffmpeg -loglevel error -y -i $v -ss $off -i $a \
    -filter_complex "[1:a]aresample=48000,apad,atrim=0:$d,asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,afade=t=in:st=0:d=$fin,afade=t=out:st=$fo:d=0.5[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $d results/$1-v1-1080p-sound.mp4
  echo "$1 done"
}
mux 01-book-3d audio/01-book-3d-sound-seed-v1.wav 0 0.05
mux 02-ben-window refs/audio/02-ben-window-original-audio.m4a 0 0.05
mux 03-mom-fridge refs/audio/03-mom-fridge-original-audio.m4a 8.7 0.2
# Higgsfield's copy of this trend is silent until its end card, so the sound comes from the
# original reel (instagram.com/cookie_mat_hongcha/reel/DejGvU3yAS-, frames line up from 0).
mux 04-lume-books-dance refs/audio/04-lume-books-dance-reel-audio.m4a 0 0.05
mux 05-ben-lume-dance refs/audio/05-ben-lume-dance-original-audio.m4a 0 0.05
mux 06-mom-spa refs/audio/06-mom-spa-original-audio.m4a 0 0.05
