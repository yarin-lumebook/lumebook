"""Reel 1.1 v4 picture: cuts follow the 1.2x studio voice (build_v4_audio.py first), screen recordings
in a rounded window in the middle over a blurred clip of the book (4 Nov 2026)."""
import json, re, subprocess
from PIL import Image, ImageDraw, ImageFilter
F = "/usr/local/bin/ffmpeg"
SPEED = 1.2
W, H, X, Y, RAD = 550, 1100, 265, 450, 42      # window: centred, just under the hook band
FILL = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
WIN = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
OUT = "fps=30,format=yuv420p,setsar=1"
SP = "source/sapir/sapir_ivan_mugatz_"

# words: times from the transcript of the finished voice, text from the original transcript
fast = json.load(open("work/v4/words-raw.json"))[8:]            # first 8 = the hook clip, the top text says it
orig = json.load(open("voice-words.json"))
i = [w["w"] for w in fast].index("רואים")
fast[i:i + 4] = [{"w": "רואים", "s": fast[i]["s"], "e": fast[i]["e"]},
                 {"w": "תצוגה", "s": fast[i + 1]["s"], "e": fast[i + 2]["e"]},
                 {"w": "מקדימה", "s": fast[i + 3]["s"], "e": fast[i + 3]["e"]}]
assert len(fast) == len(orig), (len(fast), len(orig))
words = []
for f, o in zip(fast, orig):
    t = re.sub(r'[^\w?"]', "", o["w"])                          # Yarin: only ? and " in the subtitles
    t = '"לומי"' if t == "לומי" else t
    words.append({"w": t, "s": f["s"], "e": f["e"]})
json.dump(words, open("words4.json", "w"), ensure_ascii=False, indent=1)
at = lambda w: next(x for x in words if x["w"] == w)

sound = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "work/v4/voice-studio.wav"]))
end = round(max(sound, words[-1]["e"] + 0.35), 2)
cuts = [0, 1.55 / SPEED, at("דומה?")["e"] + 0.04, at("ככה")["s"] + 0.6, at("ומעלים")["s"], at("רואים")["s"] - 0.02, at("אהבתם?")["s"] - 0.08, end]
cuts[3] = at("כותבים")["s"] - 0.02
# (name, source, start, speed on top of 1.2x, crop first, in the window)
segs = [("a", "work/hook-sdr.mov", 0.0, 1, "", False),
        ("b", SP + "raw_holding-cover-smile.mov", 0.2, 1, "", False),
        ("c", SP + "screen-recording_site-catalog-to-preview.mov", 3.0, 1, "", True),
        ("d1", "source/wizard-screen-recording.mp4", 2.0, 2, "crop=887:1920:96:0,", True),
        ("d2", SP + "screen-recording_site-catalog-to-preview.mov", 11.9, 1, "", True),
        ("e", SP + "screen-recording_book-preview-pages.mov", 0.0, 1, "", True),
        ("f", SP + "raw_flipping-through-book.mov", 1.5, 1, "", False)]
# window mask and soft shadow
m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, W - 1, H - 1), RAD, fill=255); m.save("work/v4/mask.png")
sh = Image.new("RGBA", (W + 120, H + 120), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0)
ImageDraw.Draw(a).rounded_rectangle((60, 72, 60 + W, 72 + H), RAD, fill=150); sh.putalpha(a.filter(ImageFilter.GaussianBlur(24))); sh.save("work/v4/shadow.png")

full, win = [], []
for (n, src, ss, sp, pre, screen), t0, t1 in zip(segs, cuts, cuts[1:]):
    slot = t1 - t0; rate = SPEED * sp
    out = f"work/v4/{n}.mp4"
    vf = f"{pre}{WIN if screen else FILL},setpts=PTS/{rate},{OUT}"
    subprocess.run([F, "-y", "-v", "error", "-ss", str(ss), "-t", f"{slot * rate:.3f}", "-i", src, "-an", "-vf", vf,
                    "-t", f"{slot:.3f}", "-c:v", "libx264", "-crf", "16", out], check=True)
    (win if screen else full).append((n, out, round(slot, 3)))
    print(f"{n:3} {t0:6.2f} to {t1:6.2f}  ({slot:.2f} s)")
# screen part: the windows in a row over one blurred clip of the boy with the book
open("work/v4/win.txt", "w").write("".join(f"file '{n}.mp4'\n" for n, _, _ in win))
subprocess.run([F, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "work/v4/win.txt", "-c", "copy", "work/v4/win.mp4"], check=True)
wlen = round(sum(s for _, _, s in win), 3)
fc = (f"[0:v]{FILL},gblur=sigma=30,eq=brightness=-0.10:saturation=1.15,{OUT}[bg];"
      f"[1:v]format=yuva420p[fw];[2:v]format=gray[mk];[fw][mk]alphamerge[fg];"
      f"[bg][3:v]overlay={X - 60}:{Y - 60}[b2];[b2][fg]overlay={X}:{Y}:shortest=1,{OUT}[o]")
subprocess.run([F, "-y", "-v", "error", "-ss", "4.5", "-t", f"{wlen}", "-i", SP + "raw_flipping-through-book.mov",
                "-i", "work/v4/win.mp4", "-loop", "1", "-i", "work/v4/mask.png", "-loop", "1", "-i", "work/v4/shadow.png",
                "-filter_complex", fc, "-map", "[o]", "-t", f"{wlen}", "-an", "-c:v", "libx264", "-crf", "16", "work/v4/screens.mp4"], check=True)
open("work/v4/list.txt", "w").write("file 'a.mp4'\nfile 'b.mp4'\nfile 'screens.mp4'\nfile 'f.mp4'\n")
subprocess.run([F, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "work/v4/list.txt", "-c:v", "libx264", "-crf", "17",
                "-pix_fmt", "yuv420p", "work/v4/video.mp4"], check=True)
subprocess.run([F, "-y", "-v", "error", "-i", "work/v4/voice-studio.wav", "-af", f"apad,atrim=0:{end},afade=t=out:st={end - 0.25}:d=0.25",
                "work/v4/sound.wav"], check=True)
json.dump({"source": "work/v4/video.mp4", "name": "reel-1-1-v4", "hooks": ["מה אם זה לא ייראה\nכמו הילד שלי?"],
           "captions": "words4.json",
           "cta": {"text": 'תכתבו לי "לומי"\nואשלח לכם קישור ליצירת הספר', "seconds": round(end - at("תכתבו")["s"] + 0.05, 2), "highlight": True},
           "versions": 1, "flip": False, "audio": "work/v4/sound.wav"}, open("reel4.json", "w"), ensure_ascii=False, indent=1)
print("length", end)
