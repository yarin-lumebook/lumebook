# Focus Accountability MVP — Build Spec (v1)

Paste this whole file into Claude Code as the task. Build exactly what's below — no more.

---

## What we're building (one-liner)

A single-page web app that runs a timed focus session, uses the webcam to detect whether I'm looking at my screen, and — when I look away for more than **3 seconds** — dims the entire screen and pauses the timer until I look back. It logs every distraction (when it happened, how long it lasted) and shows a session summary at the end. **All processing happens on-device; no video is ever stored or sent anywhere.**

## Why these constraints (read before coding)

- **On-device only.** The webcam feed is processed in the browser and never leaves the machine, never saved, never uploaded. This is the entire privacy/trust proposition and it keeps running cost at zero. The only network calls allowed are loading the MediaPipe library/model from a CDN.
- **This is a validation MVP.** Its job is to prove the concept is actually useful (to me and a few early testers) — not to be the final shippable product. Prefer the simplest thing that works over robustness, scale, or polish.
- **"Looking at screen" means presence + orientation, NOT precise gaze.** It's "is a face present and roughly facing the screen," not pixel-accurate eye-gaze estimation. Calibrated gaze tracking is unreliable and out of scope — do not build it.

## Tech stack (use exactly this)

- Plain **HTML + CSS + vanilla JavaScript**. No framework, no build step, no bundler, no npm install.
- **MediaPipe Tasks Vision — `FaceLandmarker`**, loaded from the jsDelivr CDN and running fully in-browser via WASM. Load the WASM fileset from the CDN and the `face_landmarker.task` model from Google's model storage. Use the official web/JS pattern (`FilesetResolver.forVisionTasks(...)` → `FaceLandmarker.createFromOptions(...)`, `runningMode: "VIDEO"`).
  - **Known gotcha:** without a bundler, destructured dynamic `import` can break MediaPipe's internal WASM path resolution. Use the documented static ES-module import from the pinned CDN URL, and verify the landmarker actually initializes before relying on it.
- **Webcam** via `getUserMedia`. This needs a secure context, so the page must be served over `http://localhost` — opening the `.html` file directly (`file://`) will not grant camera access.
- **Local persistence via `localStorage` only** (for session history). No backend, no database, no API, no network calls beyond the CDN asset loads.

## File structure

Keep it to exactly three files:

- `index.html` — markup + minimal UI
- `styles.css` — styling + the full-screen overlay
- `app.js` — camera, detection loop, session state machine, logging, summary, history

## Core behavior — the state machine (this is the important part)

Run the detection loop continuously while a session is active. ~10–15 fps is plenty; don't max out the CPU.

**Per-frame signal:**

- `looking_at_screen = TRUE` when **exactly one face is detected** AND head **yaw and pitch are within a "facing forward" threshold**. Otherwise `FALSE` (this single condition covers: no face, face turned away, and user absent).
- Derive head yaw/pitch from the `FaceLandmarker` output — either enable `outputFacialTransformationMatrixes` and read rotation from the matrix, or compute it from landmark geometry. Your call, but it **must tolerate normal small head movements** so it doesn't false-trigger while I'm just reading the screen.
- Put the thresholds as named constants at the top of `app.js` so they're easy to tune. Start around **±20–25° yaw** and **±15–20° pitch**, and the grace period as `GRACE_SECONDS = 3`.

**Session states:** `IDLE → RUNNING → (AWAY_GRACE) → PAUSED → RUNNING → … → ENDED`

- **Start:** I click Start (optionally after typing a task name). Request camera, start the focus timer, state = `RUNNING`.
- **Look away while RUNNING:** the instant `looking_at_screen` becomes `FALSE`, start a 3-second grace countdown (state = `AWAY_GRACE`) but **keep the timer running**. If I look back before 3s, cancel the countdown — no distraction logged. Brief glances are free.
- **Stay away for the full 3s:** state = `PAUSED`. **Pause the focus timer.** Show the full-screen dark overlay (message like "Look back at your screen"). Record the distraction's start timestamp. Decide and document in a comment whether the logged duration includes the 3s grace or starts at the 3s mark — just be consistent.
- **Look back while PAUSED:** hide the overlay, **resume the focus timer**, state = `RUNNING`, and log the distraction event: `{ started_at, ended_at, duration_seconds }`.
- **End:** I click End. Stop the timer, stop the camera stream, state = `ENDED`. Show the summary and save the session to `localStorage`.

**What the timer counts:** the displayed focus timer accumulates **only time spent looking at the screen** — it does not advance while `PAUSED`. So "focused time" = real time on task. Track wall-clock elapsed separately.

## UI (minimal and functional — not designed)

- **Pre-session:** optional text input "What are you working on?"; a Start button; one line of reassurance: *"Your camera feed never leaves this device. Nothing is recorded or uploaded."*
- **During session:** large focused-time display (`mm:ss`); a small status indicator (Focused / Looking away / Paused); a **small live webcam preview** so I can position myself and confirm it's tracking; an End button.
- **Overlay (when PAUSED):** a full-viewport dark layer above all other UI, with a centered message and optionally the current paused focus time. It must fully cover the screen content.
- **Summary (after End):** task name; total focused time; total wall-clock time; number of distractions; total time distracted; and a simple list of each distraction with its duration. A "Start new session" button.
- **History:** below the start screen, a simple list of past sessions from `localStorage` (date, task, focused time, # distractions) and a "Clear history" button.

## Data model (`localStorage`)

Store an array of session objects. **Store only this derived metadata — never frames, images, or video.**

```
{
  id,
  task,
  started_at,
  ended_at,
  focused_seconds,
  wallclock_seconds,
  distractions: [ { started_at, ended_at, duration_seconds } ]
}
```

## Edge cases to handle sanely

- **Camera permission denied** → clear message explaining the app needs the camera and how to re-enable it. Don't crash.
- **No camera present** → same graceful message.
- **Model still loading when Start is pressed** → show a "loading model…" state and don't begin the session until `FaceLandmarker` is ready.
- **Face intermittently lost / poor lighting** → treat "no face" as looking away (correct), but **debounce** so a single dropped frame doesn't flip states. The 3s grace already absorbs most flicker.
- **Multiple faces detected** → require exactly one face for `looking_at_screen` (simplest correct behavior).

## Explicitly out of scope — do NOT build

- No accounts, login, or cloud sync.
- No calibrated or precise gaze estimation.
- No backend, server, or database.
- No packaging into a desktop app yet — that comes only after the concept is validated.
- No analytics, telemetry, or third-party tracking of any kind.
- No design system or heavy styling — keep it minimal and legible.

## Definition of done

- I can serve it locally, click Start, and watch the focus timer run while I look at the screen.
- Looking away for **<3s** does nothing; looking away for **>3s** dims the screen and pauses the timer; looking back restores both.
- Ending a session shows an accurate summary and saves it to history.
- Refreshing the page preserves history.
- **No network calls occur except loading the MediaPipe CDN assets** — confirm this in the browser's Network tab (no video or data is sent anywhere).

## How to run

1. Put the three files in one folder.
2. From that folder, run: `python3 -m http.server 8000`
3. Open `http://localhost:8000` in Chrome and allow camera access.
