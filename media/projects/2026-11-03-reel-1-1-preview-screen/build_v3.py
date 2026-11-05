"""Reel 1.1 v3: Yarin's hook clip + Yarin's voiceover over Sapir Ivan's footage (4 Nov 2026)."""
import json, subprocess
F = "/usr/local/bin/ffmpeg"
FILL = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
# screen recordings sit in a window below the hook band, so the hook never covers the site text
FRAME = "scale=-2:1500,pad=1080:1920:(ow-iw)/2:420:color=0x0e0b1a"
OUT = "fps=30,format=yuv420p,setsar=1"
SP = "source/sapir/sapir_ivan_mugatz_"
# (name, source, start, length, speed, crop before scaling, screen=True puts it in the window)
segs = [
    ("a", "work/hook-sdr.mov", 0.0, 2.43, 1.0, "", False),
    ("b", SP + "raw_holding-cover-smile.mov", 0.2, 4.67, 1.0, "", False),
    ("c", SP + "screen-recording_site-catalog-to-preview.mov", 3.0, 1.6, 1.0, "", True),
    ("d1", "source/wizard-screen-recording.mp4", 2.0, 2.8, 2.0, "crop=887:1920:96:0,", True),
    ("d2", SP + "screen-recording_site-catalog-to-preview.mov", 11.9, 1.4, 1.0, "", True),
    ("e", SP + "screen-recording_book-preview-pages.mov", 0.0, 4.7, 1.0, "", True),
    ("f", SP + "raw_flipping-through-book.mov", 1.5, 5.8, 1.0, "", False),
]
parts = []
for n, src, ss, t, sp, pre, screen in segs:
    out = f"work/v3/{n}.mp4"
    vf = f"{pre}{FRAME if screen else FILL},setpts=PTS/{sp},{OUT}"
    subprocess.run([F, "-y", "-v", "error", "-ss", str(ss), "-t", str(t), "-i", src, "-an", "-vf", vf,
                    "-c:v", "libx264", "-crf", "18", out], check=True)
    parts.append(out)
open("work/v3/list.txt", "w").write("".join(f"file '{p.split('/')[-1]}'\n" for p in parts))
subprocess.run([F, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "work/v3/list.txt",
                "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "work/v3/video.mp4"], check=True)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "work/v3/video.mp4"]))
# sound: hook clip's own audio, then the voiceover from 0.6 s, +3 dB to match the hook clip
HOOK, VSTART = 2.43, 0.6
shift = HOOK - VSTART
fc = (f"[0:a]atrim=0:{HOOK},afade=t=out:st={HOOK-0.08}:d=0.08[h];"
      f"[1:a]atrim=start={VSTART},asetpts=PTS-STARTPTS,volume=3dB,afade=t=in:d=0.05,adelay={int(HOOK*1000)}|{int(HOOK*1000)}[v];"
      f"[h][v]amix=inputs=2:normalize=0,apad,atrim=0:{dur},afade=t=out:st={dur-0.3}:d=0.3[o]")
subprocess.run([F, "-y", "-v", "error", "-i", "work/hook-sdr.mov", "-i", "source/yarin/voice-sefer-lo-dome.m4a",
                "-filter_complex", fc, "-map", "[o]", "-ac", "2", "-ar", "48000", "work/v3/sound.wav"], check=True)
words = json.load(open("voice-words.json"))
for w in words:
    w["s"] = round(w["s"] + shift, 2); w["e"] = round(w["e"] + shift, 2)
json.dump(words, open("words3.json", "w"), ensure_ascii=False, indent=1)
json.dump({"source": "work/v3/video.mp4", "name": "reel-1-1-v3", "hooks": ["מה אם זה לא ייראה\nכמו הילד שלי?"],
           "captions": "words3.json",
           "cta": {"text": "תכתבו לי לומי\nואשלח לכם קישור ליצירת הספר", "seconds": 2.6, "highlight": True},
           "versions": 1, "flip": False, "audio": "work/v3/sound.wav"},
          open("reel3.json", "w"), ensure_ascii=False, indent=1)
print("video", round(dur, 2), "s; captions shifted", round(shift, 2))
