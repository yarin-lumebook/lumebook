"""The two takes of the car yap reel, cut, zoomed and captioned the same way so Yarin can compare them (29 Oct 2026).

higgsfield  Seedance 2.5 take 2 on Higgsfield, voiced from the Anush recording through its audio reference
fal         Seedance take 1 with the mouth re-synced to the same Anush recording by fal sync-3
Every build script takes the variant as its first argument (default higgsfield):
  python3 edit_10s.py fal ; python3 zoom_cuts.py fal ; captions_box.py fal   (track_name.py only for captions)
"""
import sys

VARIANTS = {
    "higgsfield": dict(
        take="outputs/car-yap-take2-anush.mp4",
        keep=[(0.00, 3.50), (3.88, 7.06), (7.94, 11.31), (12.08, 13.98)],  # one range per sentence
        flip=True,                          # take 2 rendered the book cover mirrored (title backwards)
        edit="outputs/car-yap-take2-10s.mp4",
        jumps_s=[2.929, 5.590, 8.410],      # jump cuts in the edit: the book jumps, so the tracker searches wider
        sentences=[0, 88, 167, 252, 300],   # sentence k runs from frame [k] to [k + 1] - 1 (cuts measured)
        ref_t=7.0,                          # tracker reference frame, un-zoomed edit
        tpl=(300, 800, 600, 1100),          # cover art used as the template in that frame (x0, y0, x1, y1)
        name=(250, 1118, 405, 1172),        # "סהר דויד" in that frame
        anchor=(540, 1000),                 # push-in centre: keeps the name above Instagram's safe line
        floor=0.65,                         # lowest line a caption box may reach, share of the height
        side=0.06,                          # side margin the box keeps
        track="work/name-track.json",
        zoomed="work/zoomed-1080.mp4",
        boxes="work/boxes",
        final="final/car-yap-10s-final.mp4",
    ),
    "fal": dict(
        take="outputs/car-yap-v2-anush.mp4",
        # sentence 1 ends in a real pause; "זה הוא," (6.98 to 7.54 s) is cut out (Yarin, 29 Oct 2026),
        # both cuts sit in silence below -50 dB (voice/voice-final-anush-12s.wav, 10 ms loudness)
        keep=[(0.00, 3.39), (3.65, 6.95), (7.60, 11.75)],
        flip=False,                          # take 1's cover reads the right way round
        edit="outputs/car-yap-fal-10s.mp4",
        captions=False,                      # hook and push-in only (Yarin, 29 Oct 2026); the name on the cover shows
        anchor=(540, 1000),
        zoomed="work/fal/zoomed-1080.mp4",
        boxes="work/fal/boxes",
        final="final/car-yap-10s-fal.mp4",
    ),
}

VARIANT = sys.argv[1] if len(sys.argv) > 1 else "higgsfield"
V = VARIANTS[VARIANT]
