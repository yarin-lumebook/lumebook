# Genjutsu: Lume as the rapper (15 Oct 2026)

Trend recreation. The reference is a crowd clip of a man in a grey suit rapping under red lights (`ref_rapper.mp4`, 15 s, from Downloads). Lume replaces the rapper; the venue, crowd, camera and music stay.

- `lume_front.png`: the Lume still used as the character (copy of `../2026-10-11-lume-character-pack/final/01_front.png`)
- `prompt.txt`: the motion-transfer prompt
- `lume_rapper_v1.mp4`: Higgsfield output, 720x1280, 24 fps, 15 s, original music kept

Job: Higgsfield Genjutsu `hf_mult_motion_control`, 720p, id `63b3f907-0044-4092-a199-03d5ccc18be7`, 105 credits. Run from the CLI (works on the Plus plan).

## Cheaper-model test (16 Oct 2026)

Is Kling 2.6 Standard on fal ($0.07/s) good enough to replace Genjutsu?

- `ref_rapper_3-7s.mp4`: 4 s slice of the reference (3 s to 7 s), the input
- `lume_rapper_kling26std_test_4s.mp4`: fal `fal-ai/kling-video/v2.6/standard/motion-control`, `character_orientation: video`, same Lume still, request `01a14474-7549-7533-a46f-54cec1a11001`. Output 848x1056, 3.1 s, about $0.22 to $0.28.

Result: gestures copied well, but Lume's face drifted (narrower eyes, heavy brows, smirk) and the background is the still's plain cream, not the venue. Kling motion control builds the scene from the still, so it cannot swap a character into the original footage the way Genjutsu does; the output also takes the still's aspect ratio and came out shorter than the slice. Not a Genjutsu replacement for character-swap trends.
