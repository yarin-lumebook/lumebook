#!/usr/bin/env python3
"""Writes the per-view prompt files for the Lume reference pack. Edit here, rerun, then run.py NAME MODEL ..."""
from pathlib import Path
HERE = Path(__file__).parent

IDENT = ("The exact same character shown in the reference images: Lume, an original stylized 3D animated mascot, a small furry "
 "creature (image 1 is the original design, image 2 is the approved straight-on front view of the same character{extra_ref}). "
 "Keep his design exactly: soft golden-peach fur; lighter cream muzzle, chest and belly; large round ears with pink interiors; "
 "large round blue eyes with big black pupils, white highlights and small lashes at the outer corners; dark expressive eyebrows; "
 "glossy pink-red nose; rosy pink cheeks; long thin dark whiskers; a brown swept-up hair tuft on top of the head; two small upper "
 "front teeth; a large head on a compact rounded body with a round belly, short limbs and rounded paws with the same stubby "
 "fingers and toes as the references; a fluffy golden-peach tail with a purple tip. Same 3D animated-film rendering style, same "
 "colours, same soft detailed fur texture, same head-to-body proportions as the references. Friendly happy expression with the "
 "same open smile showing the two small front teeth.")

TAIL_RULE = ("Tail anatomy, identical in every view: one tail, attached at the base of his spine at the centre of his lower back, "
 "sweeping out toward his own LEFT side and curling slightly upward, golden-peach with a purple tip. Do not move the tail to "
 "another place on the body.")

STUDIO = ("Warm ivory seamless studio background, soft even studio lighting, soft contact shadow under the feet. Camera level at "
 "the height of his chest, no wide-angle distortion. Bare base design: no hat, no clothing, no book, no accessories. No props, no "
 "text, no logos, no watermark. Do not add new markings, stripes or spots. Do not change him into a different animal.")

FULL = ("FULL BODY at the same scale as reference image 2: he stands upright in a relaxed neutral stance, arms relaxed and held "
 "slightly away from his body with the paws lowered beside his hips, feet flat on the floor. The whole character is inside the "
 "frame with a margin of empty background on every side: ears, hair tuft, whiskers, paws, feet and any visible part of the tail.")

PORTRAIT = ("HEAD AND SHOULDERS PORTRAIT: framed from the upper chest up. Both complete ears, the whole hair tuft and the full "
 "length of the whiskers are inside the frame with a margin of empty background above and at the sides. Shoulders and upper chest "
 "visible at the bottom. Head upright, not tilted. His head fills about 60 percent of the frame height.")

REAR = ("Rear design: his back, the back of his head and the backs of his ears are covered in the same plain golden-peach fur "
 "(the cream colour is only on the muzzle, chest and belly; the pink is only inside the ears, on the front). The brown hair tuft "
 "is seen from behind on top of the head.")

PROFILE_FACE = ("In profile he keeps his look: a large round head, a short rounded muzzle that protrudes gently forward with the "
 "glossy pink-red nose at its tip, a full rounded cheek with the rosy patch, whiskers fanning out from the muzzle, one large "
 "blue eye with its dark eyebrow, the open smile with the front teeth seen from the side, one large round ear standing up from "
 "the side of the head with its pink interior facing outward-forward, and the brown hair tuft sweeping up on top. Do not lengthen the snout.")

VIEWS = {
 "front_three_quarter_left": (
  "VIEW: front three-quarter view. His whole body and head are turned together 45 degrees toward the LEFT side of the image, so "
  "the camera sees his front and his own left side. His nose points toward the left edge of the frame and he looks straight ahead "
  "in the direction he is facing. Both eyes are visible, the far eye partly hidden by the muzzle. "
  "Tail in this view: fully visible behind him on the RIGHT side of the image, sweeping toward the camera."),
 "left_profile": (
  "VIEW: strict side profile of the whole body. His head, chest, belly and feet all point at the LEFT edge of the image; the "
  "camera sees only his own left side. " + PROFILE_FACE + " His round belly curves forward in silhouette; the near arm hangs "
  "relaxed at his side. Tail in this view: fully visible behind him on the RIGHT side of the image, attached at the lower back."),
 "rear_three_quarter_left": (
  "VIEW: rear three-quarter view. He stands with his back to the camera, turned 45 degrees so that he faces away toward the far "
  "LEFT of the image. The camera sees his back and his own left side from behind: the back of his head, the back of both ears, "
  "a sliver of his left cheek with whiskers, his left arm. His face is mostly hidden. " + REAR +
  " Tail in this view: fully visible, growing from the centre of his lower back and sweeping toward his left side, the side nearer the camera."),
 "back": (
  "VIEW: straight from behind. He stands with his back squarely to the camera, facing directly away. No part of his face is "
  "visible; only the tips of the whiskers may show past the sides of the head. " + REAR +
  " Tail in this view: fully visible, growing from the centre of his lower back and sweeping out toward the LEFT side of the image "
  "(his own left), curling slightly upward, with the purple tip."),
 "rear_three_quarter_right": (
  "VIEW: rear three-quarter view. He stands with his back to the camera, turned 45 degrees so that he faces away toward the far "
  "RIGHT of the image. The camera sees his back and his own right side from behind: the back of his head, the back of both ears, "
  "a sliver of his right cheek with whiskers, his right arm. His face is mostly hidden. " + REAR +
  " Tail in this view: visible, growing from the centre of his lower back and sweeping away toward the LEFT side of the image (his own left side)."),
 "right_profile": (
  "VIEW: strict side profile of the whole body. His head, chest, belly and feet all point at the RIGHT edge of the image; the "
  "camera sees only his own right side. " + PROFILE_FACE + " His round belly curves forward in silhouette; the near arm hangs "
  "relaxed at his side. Tail in this view: behind him on the LEFT side of the image, attached at the lower back and sweeping "
  "away from the camera toward his far side, so it is partly hidden behind his body with the purple tip visible."),
 "front_three_quarter_right": (
  "VIEW: front three-quarter view. His whole body and head are turned together 45 degrees toward the RIGHT side of the image, so "
  "the camera sees his front and his own right side. His nose points toward the right edge of the frame and he looks straight "
  "ahead in the direction he is facing. Both eyes are visible, the far eye partly hidden by the muzzle. "
  "Tail in this view: it is on his far side, almost entirely hidden behind his body. Do not bring the tail around to the front or to the near side."),
 "front": (
  "VIEW: straight-on front view, facing the camera, looking into the lens, both ears and both sets of whiskers symmetrical."),
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
def strip_tail(v):  # portraits are cropped above the tail
    return v.split(" Tail in this view:")[0].replace(" His round belly curves forward in silhouette; the near arm hangs relaxed at his side.", "")
for name, v in FULL_BODY.items():
    (HERE / f"{name}.txt").write_text("\n\n".join([IDENT.format(extra_ref=""), VIEWS[v], TAIL_RULE, FULL, STUDIO]) + "\n")
for name, v in PORTRAITS.items():
    ident = IDENT.format(extra_ref=", image 3 is a close crop of his head from image 2")
    (HERE / f"{name}.txt").write_text("\n\n".join([ident, PORTRAIT, strip_tail(VIEWS[v]), "The tail is outside the frame.", STUDIO.replace(", soft contact shadow under the feet", "")]) + "\n")

# --- v2 revisions (11 Oct 2026) ---
# 02 v1 and 04 v1: turned only about 15 degrees. 04 v1 also swept the tail to his right.
# 05 v1: style drift (plush-toy look, small head, darker background). 12 v1: camera behind the profile, ear misplaced.
REAR_REF = ", image 3 is an approved rear three-quarter view of the same character that defines his rear design, fur and rendering style"
V2 = {
 "02_front_three_quarter_left_v2": "\n\n".join([
  IDENT.format(extra_ref=""),
  VIEWS["front_three_quarter_left"] + " The turn must be clear: exactly halfway between a front view and a left side profile. "
  "His chest and belly point toward the lower-left corner of the image, his near (left) shoulder and arm are in front, his far "
  "arm is partly hidden behind his body, the far ear is partly hidden behind the head, and the far cheek and far whiskers are "
  "strongly foreshortened. This is not a front view.",
  TAIL_RULE, FULL, STUDIO]),
 "04_rear_three_quarter_left_v2": "\n\n".join([
  IDENT.format(extra_ref=REAR_REF),
  VIEWS["rear_three_quarter_left"].split(" Tail in this view:")[0] +
  " The turn must be clear: exactly halfway between a straight back view and a left side profile, so the tip of his pink-red "
  "nose, the edge of his left eye and his left rosy cheek are just visible past the edge of his head on the LEFT side of the "
  "image. Tail in this view: growing from the centre of his lower back and sweeping toward his own left side, which is the side "
  "nearer the camera, so the tail comes forward toward the camera and toward the LEFT side of the image, with the purple tip "
  "near his left leg. The tail does not go to the right side of the image.",
  TAIL_RULE, FULL, STUDIO]),
 "05_back_v2": "\n\n".join([
  IDENT.format(extra_ref=REAR_REF), VIEWS["back"],
  "Keep exactly the same 3D animated-film rendering and long soft fluffy fur as the references, not a felt or plush toy. Keep "
  "the same big head, the same large round ears, the same compact round body and short legs as reference image 2; the body "
  "silhouette from behind matches the front silhouette of image 2. The tail is thick and fluffy with a saturated purple tip, as in the references.",
  TAIL_RULE, FULL, STUDIO]),
 "12_portrait_right_profile_v2": "\n\n".join([
  IDENT.format(extra_ref=", image 3 is a close crop of his head from image 2, image 4 is his approved LEFT profile portrait"),
  PORTRAIT,
  strip_tail(VIEWS["right_profile"]) + " The camera is exactly at his side, not behind him: this view is the mirror image of "
  "image 4, with the same head shape, the same short muzzle, the same cheek, the same ear position on top of the side of the "
  "head and the same hair tuft, only facing the RIGHT edge of the image instead of the left.",
  "The tail is outside the frame.", STUDIO.replace(", soft contact shadow under the feet", "")]),
}
for name, text in V2.items():
    (HERE / f"{name}.txt").write_text(text + "\n")

# 08 v1: tail swung out behind him on the left of the image; with a left-sweeping tail it should be hidden in this view.
(HERE / "08_front_three_quarter_right_v2.txt").write_text("\n\n".join([
  IDENT.format(extra_ref=""),
  VIEWS["front_three_quarter_right"] + " In this view the tail is completely hidden behind his body and is not visible at all: "
  "there is nothing purple in the image and nothing sticks out behind his back on the left side of the image.",
  TAIL_RULE, FULL, STUDIO]) + "\n")

# 12 v2: still seen from slightly behind, head larger than the other portraits. v3 anchors on the approved full-body right profile.
(HERE / "12_portrait_right_profile_v3.txt").write_text("\n\n".join([
  IDENT.format(extra_ref=", image 3 is a close crop of his head from image 2, image 4 is his approved full-body RIGHT profile"),
  PORTRAIT.replace("about 60 percent", "about 55 percent"),
  strip_tail(VIEWS["right_profile"]) + " This is a close-up of exactly the view in image 4: the same camera position exactly at "
  "his side (not behind him), the same head shape, the same short muzzle, the same ear position, only framed closer as a head "
  "and shoulders portrait. The face takes up the right half of the head; the back of the head does not dominate the image.",
  "The tail is outside the frame.", STUDIO.replace(", soft contact shadow under the feet", "")]) + "\n")

# 06 v1: turned only about 20 degrees from a straight back view. v2 asks for a clear 45 and anchors the rear design on 04 v2.
(HERE / "06_rear_three_quarter_right_v2.txt").write_text("\n\n".join([
  IDENT.format(extra_ref=", image 3 is the approved rear three-quarter view from his other side, which defines his rear design, fur and rendering style"),
  VIEWS["rear_three_quarter_right"].split(" Tail in this view:")[0] +
  " The turn must be clear: exactly halfway between a straight back view and a right side profile, so the tip of his pink-red "
  "nose, the edge of his right eye and his right rosy cheek are just visible past the edge of his head on the RIGHT side of the "
  "image. This view is the opposite side of image 3. Tail in this view: growing from the centre of his lower back and sweeping "
  "toward his own left side, which is the far side, so the tail points toward the LEFT side of the image and away from the camera.",
  TAIL_RULE, FULL, STUDIO]) + "\n")
