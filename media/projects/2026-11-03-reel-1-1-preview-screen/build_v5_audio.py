"""Reel 1.1 v5 sound: hook clip audio + voiceover, pauses cut, studio-style chain, 1x (4 Nov 2026)."""
import json, re, subprocess
F = "/usr/local/bin/ffmpeg"
HOOK_END = 1.55        # hook clip: speech ends at 1.40 s, keep a short tail
VSTART = 0.6           # voiceover: first word at 0.8 s
GAP = 0.10             # every pause inside the voiceover becomes this long
PAD = 0.05             # kept around each spoken stretch
SPEED = 1.0            # back to normal speed (Yarin, 4 Nov 2026); pauses stay cut

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))

subprocess.run([F, "-y", "-v", "error", "-i", "source/yarin/voice-sefer-lo-dome.m4a", "-ss", str(VSTART), "-ac", "1", "-ar", "48000", "work/v5/voice-raw.wav"], check=True)
subprocess.run([F, "-y", "-v", "error", "-i", "work/hook-sdr.mov", "-t", str(HOOK_END), "-vn", "-ac", "1", "-ar", "48000", "work/v5/hook-raw.wav"], check=True)
log = subprocess.run([F, "-v", "info", "-i", "work/v5/voice-raw.wav", "-af", "silencedetect=noise=-38dB:d=0.15", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
total = dur("work/v5/voice-raw.wav")
sil = list(zip(starts, ends + [total] * (len(starts) - len(ends))))
keep, cur = [], 0.0
for s, e in sil:
    if s > cur:
        keep.append((max(0, cur - PAD), s + PAD))
    cur = e
if cur < total:
    keep.append((max(0, cur - PAD), total))
keep = [(a, b) for a, b in keep if b - a > 0.08]
print("silences", [(round(s, 2), round(e, 2)) for s, e in sil])
print("kept", [(round(a, 2), round(b, 2)) for a, b in keep])
# hook + short gap + each spoken stretch with GAP between them
parts, n = [], 0
fc = f"[0:a]anull[h];"
labels = ["[h]"]
fc += f"aevalsrc=0:d={GAP}:s=48000[g0];"
labels.append("[g0]")
for i, (a, b) in enumerate(keep):
    fc += f"[1:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.02:.3f}:d=0.02[k{i}];"
    labels.append(f"[k{i}]")
    if i < len(keep) - 1:
        fc += f"aevalsrc=0:d={GAP}:s=48000[g{i+1}];"
        labels.append(f"[g{i+1}]")
fc += "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[tight]"
subprocess.run([F, "-y", "-v", "error", "-i", "work/v5/hook-raw.wav", "-i", "work/v5/voice-raw.wav", "-filter_complex", fc,
                "-map", "[tight]", "work/v5/tight.wav"], check=True)
# studio chain: rumble cut, light denoise, less boxiness, warmth, presence, air, de-ess, compression, then 1x
chain = ("highpass=f=75,afftdn=nr=12:nf=-45,"
         "equalizer=f=280:t=q:w=1.2:g=-2.5,equalizer=f=110:t=q:w=1:g=2,"
         "equalizer=f=3500:t=q:w=1.4:g=3,equalizer=f=11000:t=q:w=1:g=2,"
         "deesser=i=0.35,acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=4,"
         f"atempo={SPEED}")
subprocess.run([F, "-y", "-v", "error", "-i", "work/v5/tight.wav", "-af", chain, "work/v5/studio-pre.wav"], check=True)
m = subprocess.run([F, "-v", "info", "-i", "work/v5/studio-pre.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run([F, "-y", "-v", "error", "-i", "work/v5/studio-pre.wav", "-af", ln + ",alimiter=limit=0.89", "-ar", "48000", "-ac", "2", "work/v5/voice-studio.wav"], check=True)
print("hook end at", round(HOOK_END / SPEED, 3), "s; sound", round(dur("work/v5/voice-studio.wav"), 2), "s (was", round(HOOK_END + total, 2), ")")
