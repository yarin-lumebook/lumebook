#!/usr/bin/env python3
"""Writes the per-view prompt files. Edit here, rerun, then run.py NAME ..."""
from pathlib import Path
HERE = Path(__file__).parent

IDENT = ("Photorealistic studio photograph of the exact same toddler boy shown in the reference images "
 "(image 1 is the original photo, image 2 is the approved straight-on front view of the same child{extra_ref}). "
 "He is about three years old. Keep his identity exactly: the same face, very full rounded cheeks, small button nose, "
 "soft round chin, warm olive skin, brown eyes, the same round dark tortoiseshell glasses with clear lenses, the same "
 "dark brown hair slicked back on top with a clean skin fade around the sides and back, the same hairline, the same "
 "toddler head-to-body proportions. Same outfit: plain white crew-neck T-shirt, beige shorts with rolled hems, bare feet.")

STUDIO = ("Warm ivory seamless studio background, soft even studio lighting. Camera at the child's eye level, level horizon, "
 "85mm lens look, no wide-angle distortion. Neutral, gently curious, quietly confident expression, mouth closed. "
 "Natural skin texture and fabric texture, a real photograph. No props, no text, no logos, no labels, no watermark. "
 "Not a cartoon, no enlarged eyes, no plastic skin, no adult facial proportions.")

FULL = ("FULL BODY, the same scale and framing as reference image 2: the whole child from the top of his hair to his toes, "
 "centred, a little space above the head and below the feet, soft contact shadow under the feet. Relaxed standing pose, "
 "arms hanging slightly away from the torso, hands relaxed and open with five natural fingers, feet flat on the floor.")

PORTRAIT = ("HEAD AND SHOULDERS PORTRAIT: framed from mid-chest up, the entire hairstyle inside the frame with space above "
 "it, shoulders inside the frame, head centred, head upright and level, not tilted.")

VIEWS = {
 "front_three_quarter_left": (
  "VIEW: front three-quarter view. His whole body and head are turned together 45 degrees toward the LEFT side of the image, "
  "so the camera sees his front and his own left side. His nose points toward the left edge of the frame and his eyes look "
  "straight ahead in the direction he is facing, not at the camera. The ear facing the camera is his left ear and it has NO "
  "earring. The earring ear is on the far side of his head, hidden from the camera."),
 "left_profile": (
  "VIEW: pure side profile. His whole body and head are turned 90 degrees so that his nose points at the LEFT edge of the "
  "image and the camera sees only his own left side: one eye, the side of the glasses with the temple arm running to the ear, "
  "and his left ear, which has NO earring. In profile his cheek is still very full and round and bulges forward, with a small "
  "button nose, soft lips, a small soft chin and toddler fullness under the chin. Do not flatten the cheek, do not sharpen "
  "the nose or chin. The fade on the side of the head is clearly visible."),
 "rear_three_quarter_left": (
  "VIEW: rear three-quarter view. He stands with his back to the camera, turned 45 degrees so that he faces away toward the "
  "far LEFT of the image. The camera sees his back, the back of his head with the fade, and his own left side from behind: "
  "the back of his left ear (NO earring), the left temple arm of the glasses, and only a small sliver of his full left cheek. "
  "His face is mostly hidden. Plain back of the white T-shirt, plain back of the beige shorts."),
 "back": (
  "VIEW: straight from behind. He stands with his back squarely to the camera, facing directly away. No part of his face is "
  "visible. The camera sees the back of his head: slicked-back dark brown hair on top, clean skin fade tapering to the nape of "
  "the neck, both ears from behind with the curved tips of the glasses temple arms hooked over them. The diamond stud is not "
  "visible from behind. Plain back of the white T-shirt with no tag or print, plain back of the beige shorts with a simple "
  "waistband and no patches, the backs of his legs and his heels."),
 "rear_three_quarter_right": (
  "VIEW: rear three-quarter view. He stands with his back to the camera, turned 45 degrees so that he faces away toward the "
  "far RIGHT of the image. The camera sees his back, the back of his head with the fade, and his own right side from behind: "
  "the back of his right ear with the edge of one small diamond stud just visible on the lobe, the right temple arm of the "
  "glasses, and only a small sliver of his full right cheek. His face is mostly hidden. Plain back of the white T-shirt, "
  "plain back of the beige shorts."),
 "right_profile": (
  "VIEW: pure side profile. His whole body and head are turned 90 degrees so that his nose points at the RIGHT edge of the "
  "image and the camera sees only his own right side: one eye, the side of the glasses with the temple arm running to the "
  "ear, and his right ear with one small diamond stud in the lobe. In profile his cheek is still very full and round and "
  "bulges forward, with a small button nose, soft lips, a small soft chin and toddler fullness under the chin. Do not flatten "
  "the cheek, do not sharpen the nose or chin. The fade on the side of the head is clearly visible."),
 "front_three_quarter_right": (
  "VIEW: front three-quarter view. His whole body and head are turned together 45 degrees toward the RIGHT side of the image, "
  "so the camera sees his front and his own right side. His nose points toward the right edge of the frame and his eyes look "
  "straight ahead in the direction he is facing, not at the camera. The ear facing the camera is his right ear, with one "
  "small diamond stud in the lobe. His other ear is on the far side of his head, hidden from the camera."),
 "front": (
  "VIEW: straight-on front view, facing the camera, looking into the lens. Both ears visible. One small diamond stud in the "
  "ear on the LEFT side of the image (his own right ear). The other ear has no earring."),
}

FULL_BODY = {
 "02_front_three_quarter_left": "front_three_quarter_left", "03_left_profile": "left_profile",
 "04_rear_three_quarter_left": "rear_three_quarter_left", "05_back": "back",
 "06_rear_three_quarter_right": "rear_three_quarter_right", "07_right_profile": "right_profile",
 "08_front_three_quarter_right": "front_three_quarter_right",
}
PORTRAITS = {
 "09_portrait_front": "front", "10_portrait_three_quarter_left": "front_three_quarter_left",
 "11_portrait_left_profile": "left_profile", "12_portrait_right_profile": "right_profile",
 "13_portrait_three_quarter_right": "front_three_quarter_right",
}
for name, v in FULL_BODY.items():
    (HERE / f"{name}.txt").write_text("\n\n".join([IDENT.format(extra_ref=""), VIEWS[v], FULL, STUDIO]) + "\n")
for name, v in PORTRAITS.items():
    ident = IDENT.format(extra_ref=", image 3 is a close crop of his head from image 2")
    (HERE / f"{name}.txt").write_text("\n\n".join([ident, PORTRAIT, VIEWS[v], STUDIO]) + "\n")

# --- v2 revisions (11 Oct 2026) ---
# 03/07 v1: head in profile but torso and feet still three-quarter. 09 v1: seated, framed to the waist.
BODY_SIDE = ("The WHOLE BODY is in strict side profile, not only the head: his chest, belly, hips, knees and both feet all point "
 "at the {edge} edge of the image, exactly the same direction as his nose. The camera sees the side seam of the T-shirt and "
 "of the shorts and the side of one leg, with the far leg almost fully hidden behind the near leg. Both feet are seen from "
 "the side with toes pointing {edge}, no foot pointing at the camera. The near arm hangs relaxed at his side; the far arm is "
 "hidden behind the torso. His toddler belly curves gently forward in silhouette.")
V2 = {
 "03_left_profile_v2": "\n\n".join([IDENT.format(extra_ref=""), VIEWS["left_profile"], BODY_SIDE.format(edge="LEFT"), FULL, STUDIO]),
 "07_right_profile_v2": "\n\n".join([IDENT.format(extra_ref=""), VIEWS["right_profile"], BODY_SIDE.format(edge="RIGHT"), FULL, STUDIO]),
 "09_portrait_front_v2": "\n\n".join([
  IDENT.format(extra_ref=", image 3 is a close crop of his head from image 2"), PORTRAIT,
  "He is STANDING upright, not sitting or crouching, shoulders square to the camera. Tight crop: the bottom edge of the frame "
  "cuts across his upper chest just below the T-shirt sleeves. Only his head, neck, both shoulders and upper chest are in the "
  "frame. No forearms, no hands, no shorts, no legs. His head fills about 45 percent of the frame height.",
  VIEWS["front"], STUDIO]),
}
for name, text in V2.items():
    (HERE / f"{name}.txt").write_text(text + "\n")
