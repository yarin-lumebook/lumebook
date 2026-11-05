"""Reel 1.1 v9 (Yarin, 4 Nov 2026), from build_v8.py: the baby picture comes in right after "מה" and stays to the end
of the opening clip. v8, from build_v7.py: the baby picture through the whole opening clip, the hook
only during the opening clip (reel editor hook_seconds), a bigger screen window, and everything after the opening
clip at 1.1x (picture, voice and captions). The opening clip stays at normal speed."""
import json, re, subprocess
from PIL import Image, ImageDraw, ImageFilter
F = "/usr/local/bin/ffmpeg"
INTRO = 1.55           # end of the opening clip, in the voice track too (build_v5_audio.py HOOK_END)
AFTER = 1.1            # speed after the opening clip
m = lambda t: t if t <= INTRO else INTRO + (t - INTRO) / AFTER     # 1x voice time to v8 time
W, H, X, Y, RAD = 720, 1440, 180, 240, 54      # window: bigger than v7 (550x1100), centred; no hook band after the intro
FILL = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
WIN = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
OUT = "fps=30,format=yuv420p,setsar=1"
SP = "source/sapir/sapir_ivan_mugatz_"
V = "work/v9"

# words: times from the transcript of the 1x studio voice mapped to 1.1x, text from the original transcript
raw = json.load(open("work/v5/words-raw.json"))
fast, orig = raw[8:], json.load(open("voice-words.json"))     # first 8 = the opening clip, the hook says it
assert len(fast) == len(orig), (len(fast), len(orig))
words = []
for f, o in zip(fast, orig):
    t = re.sub(r'[^\w?"]', "", o["w"])                          # Yarin: only ? and " in the subtitles
    t = '"לומי"' if t == "לומי" else t
    words.append({"w": t, "s": round(m(f["s"]), 3), "e": round(m(f["e"]), 3)})
json.dump(words, open("words8.json", "w"), ensure_ascii=False, indent=1)
at = lambda w: next(x for x in words if x["w"] == w)

sound = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "work/v5/voice-studio.wav"]))
end = round(max(m(sound), words[-1]["e"] + 0.32), 2)
cuts = [0, INTRO, at("דומה?")["e"] + 0.04, at("כותבים")["s"] - 0.02, at("ומעלים")["s"], at("רואים")["s"] - 0.02, at("אהבתם?")["s"] - 0.08, end]
# (name, source, start, speed on top of the 1.1x, crop first, in the window)
segs = [("a", "work/hook-sdr.mov", 0.0, 1, "", False),
        ("b", SP + "raw_holding-cover-smile.mov", 0.2, 1, "", False),
        ("c", SP + "screen-recording_site-catalog-to-preview.mov", 3.0, 1, "", True),
        ("d1", "source/wizard-screen-recording.mp4", 2.0, 2, "crop=887:1920:96:0,", True),
        ("d2", SP + "screen-recording_site-catalog-to-preview.mov", 11.9, 1, "", True),
        ("e", SP + "screen-recording_book-preview-pages.mov", 0.0, 1, "", True),
        ("f", SP + "raw_flipping-through-book.mov", 1.5, 1, "", False)]
# window mask and soft shadow
mk = Image.new("L", (W, H), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, W - 1, H - 1), RAD, fill=255); mk.save(f"{V}/mask.png")
sh = Image.new("RGBA", (W + 120, H + 120), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0)
ImageDraw.Draw(a).rounded_rectangle((60, 72, 60 + W, 72 + H), RAD, fill=150); sh.putalpha(a.filter(ImageFilter.GaussianBlur(24))); sh.save(f"{V}/shadow.png")

full, win = [], []
for (n, src, ss, sp, pre, screen), t0, t1 in zip(segs, cuts, cuts[1:]):
    slot = t1 - t0; rate = sp * (1 if n == "a" else AFTER)
    out = f"{V}/{n}.mp4"
    vf = f"{pre}{WIN if screen else FILL},setpts=PTS/{rate},{OUT}"
    subprocess.run([F, "-y", "-v", "error", "-ss", str(ss), "-t", f"{slot * rate:.3f}", "-i", src, "-an", "-vf", vf,
                    "-t", f"{slot:.3f}", "-c:v", "libx264", "-crf", "16", out], check=True)
    (win if screen else full).append((n, out, round(slot, 3)))
    print(f"{n:3} {t0:6.2f} to {t1:6.2f}  ({slot:.2f} s, {rate}x)")
# Yarin as a baby (baby/baby-yarin.png, one OpenAI edit, 4 Nov 2026): a plain 416 px square, no frame, no rounded corners,
# no animation, under his chin from right after "מה" to the end of the opening clip (Yarin, 4 Nov 2026).
SY = 1230                                                       # y 1230 to 1646, centred
B0 = raw[0]["e"]                                                # end of "מה" in the opening clip
subprocess.run([F, "-y", "-v", "error", "-i", f"{V}/a.mp4", "-loop", "1", "-i", "baby/baby-square-plain.png",
                "-filter_complex", f"[0:v][1:v]overlay=x=(W-w)/2:y={SY}:enable='gte(t,{B0})':shortest=1,{OUT}[o]",
                "-map", "[o]", "-c:v", "libx264", "-crf", "16", f"{V}/a-baby.mp4"], check=True)
subprocess.run(["mv", f"{V}/a-baby.mp4", f"{V}/a.mp4"], check=True)
# screen part: the windows in a row over one blurred clip of the boy with the book
open(f"{V}/win.txt", "w").write("".join(f"file '{n}.mp4'\n" for n, _, _ in win))
subprocess.run([F, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{V}/win.txt", "-c", "copy", f"{V}/win.mp4"], check=True)
wlen = round(sum(s for _, _, s in win), 3)
fc = (f"[0:v]{FILL},gblur=sigma=30,eq=brightness=-0.10:saturation=1.15,{OUT}[bg];"
      f"[1:v]format=yuva420p[fw];[2:v]format=gray[mk];[fw][mk]alphamerge[fg];"
      f"[bg][3:v]overlay={X - 60}:{Y - 60}[b2];[b2][fg]overlay={X}:{Y}:shortest=1,{OUT}[o]")
subprocess.run([F, "-y", "-v", "error", "-ss", "3.0", "-t", f"{wlen}", "-i", SP + "raw_flipping-through-book.mov",
                "-i", f"{V}/win.mp4", "-loop", "1", "-i", f"{V}/mask.png", "-loop", "1", "-i", f"{V}/shadow.png",
                "-filter_complex", fc, "-map", "[o]", "-t", f"{wlen}", "-an", "-c:v", "libx264", "-crf", "16", f"{V}/screens.mp4"], check=True)
open(f"{V}/list.txt", "w").write("file 'a.mp4'\nfile 'b.mp4'\nfile 'screens.mp4'\nfile 'f.mp4'\n")
subprocess.run([F, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{V}/list.txt", "-c:v", "libx264", "-crf", "17",
                "-pix_fmt", "yuv420p", f"{V}/video.mp4"], check=True)
# voice: the opening clip as it is, the rest at 1.1x (atempo keeps the pitch)
subprocess.run([F, "-y", "-v", "error", "-i", "work/v5/voice-studio.wav", "-filter_complex",
                f"[0:a]asplit[x][y];[x]atrim=0:{INTRO},asetpts=PTS-STARTPTS[a1];"
                f"[y]atrim=start={INTRO},asetpts=PTS-STARTPTS,atempo={AFTER}[a2];"
                f"[a1][a2]concat=n=2:v=0:a=1,apad,atrim=0:{end},afade=t=out:st={end - 0.25}:d=0.25[o]",
                "-map", "[o]", "-ar", "48000", f"{V}/sound.wav"], check=True)
json.dump({"source": f"{V}/video.mp4", "name": "reel-1-1-v9", "hooks": ["מה אם זה לא ייראה\nכמו הילד שלי?"],
           "hook_seconds": INTRO, "captions": "words8.json",
           "cta": {"text": 'תכתבו לי "לומי"\nואשלח לכם קישור ליצירת הספר', "seconds": round(end - at("תכתבו")["s"] + 0.05, 2), "highlight": True},
           "versions": 1, "flip": False, "audio": f"{V}/sound.wav"}, open("reel9.json", "w"), ensure_ascii=False, indent=1)
print("length", end)
