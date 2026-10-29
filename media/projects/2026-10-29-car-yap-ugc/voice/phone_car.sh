#!/bin/zsh
# Make a clean TTS take sound like a phone recording inside a parked car.
# Usage: ./phone_car.sh voice-anush.mp3   ->  voice-anush-car.wav
# The voice gets one fixed gain to -16 LUFS (no dynamic leveling, so pauses stay quiet),
# then a constant low car hum is mixed under it.
set -e
in="$1"
out="${in%.*}-car.wav"
tmp="${in%.*}-car-voice.tmp.wav"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")

# 1. phone mic + small cabin echo + phone-style compression
ffmpeg -v error -y -i "$in" -af "
  aformat=channel_layouts=mono,aresample=44100,
  highpass=f=140,lowpass=f=8500,
  equalizer=f=450:t=q:w=1.2:g=2.5,
  equalizer=f=3200:t=q:w=1.5:g=3,
  aecho=0.85:0.55:9|17|29:0.22|0.14|0.08,
  acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2" "$tmp"

# 2. one fixed gain to -16 LUFS
loud=$(ffmpeg -i "$tmp" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | awk '{print $2}')
gain=$(python3 -c "print(round(-16 - ($loud), 2))")

# 3. constant parked-car hum under the voice, peaks capped at -1.5 dBFS
ffmpeg -v error -y -i "$tmp" \
  -f lavfi -t "$dur" -i "anoisesrc=color=brown:amplitude=0.6:seed=7" \
  -f lavfi -t "$dur" -i "anoisesrc=color=pink:amplitude=0.6:seed=11" \
  -filter_complex "
    [0:a]volume=${gain}dB[v];
    [1:a]aformat=channel_layouts=mono,lowpass=f=220,volume=-44dB[rumble];
    [2:a]aformat=channel_layouts=mono,highpass=f=300,lowpass=f=2500,volume=-56dB[hvac];
    [v][rumble][hvac]amix=inputs=3:duration=first:normalize=0,
      alimiter=limit=0.84:level=0[out]" \
  -map "[out]" -ar 44100 "$out"
rm -f "$tmp"
echo "$out (voice gain ${gain} dB)"
