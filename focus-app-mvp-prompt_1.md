# Claude Code Prompt — Focus App MVP (browser prototype)

Paste everything below into Claude Code.

---

You are helping me build the MVP of a focus-accountability tool. I have **zero app-development experience**, so write clean, well-commented code and explain how to run and test it. Build ONLY what's specified — do not add extra features or scope.

## What the product is
A timed focus session where the webcam watches whether I'm facing my screen. If I look away (face gone or head turned away) for more than a few seconds, a dark overlay covers the screen and the session timer pauses. When I face the screen again, the overlay clears and the timer resumes. At the end it shows a log of exactly how many times I got distracted and for how long.

## MVP scope — build this and nothing more
A **single, self-contained web app** that runs locally in a browser. No installer, no desktop wrapper, no accounts, no backend server, no cloud. This is a validation prototype; if the core loop works and feels useful, I'll wrap it in a desktop app later.

## Hard constraints
- **Fully on-device.** The camera stream must never be sent anywhere. All processing happens in the browser. This is a core requirement and a selling point — state it in the UI.
- **Tech stack:** plain HTML + CSS + vanilla JavaScript. No framework, no build step. Use **Google MediaPipe Tasks Vision `FaceLandmarker`** loaded from a CDN for face detection and head-pose (it runs client-side via WebAssembly). Prefer one file (`index.html`) unless splitting into `index.html` / `app.js` / `style.css` is meaningfully cleaner.
- **Runnable by a beginner:** it must run via a one-line local server (e.g. `python3 -m http.server` or `npx serve`), because webcam access and the MediaPipe WASM need `localhost`, not `file://`. Give me the exact command and the URL to open.

## Core logic
1. **Session control:** a Start button begins a session and a running timer (mm:ss). A Stop button ends it and shows a summary.
2. **Attention detection (per video frame):** using FaceLandmarker, decide `focused` vs `away`. `away` = **no face detected** OR **head yaw/pitch beyond a threshold** (turned left/right/up/down away from the screen). No per-user calibration — use head-pose thresholds.
3. **Grace period:** only trigger a distraction after the user has been `away` continuously for **N seconds (default 3, configurable)**. Brief glances under the threshold don't count.
4. **Overlay + pause:** when a distraction triggers, fade in a full-screen dark overlay and **pause the timer**. When the user returns to `focused`, fade the overlay out and **resume the timer**.
5. **Logging:** record each distraction event with start time, duration, and whether it was "no face" or "looked away." Keep total focused time separate from total distracted time.

## UI (minimal)
- Big live session timer + a clear status indicator (Focused / Away).
- Small live camera preview so I can see it's tracking.
- Live count of distractions in the current session.
- **End-of-session summary:** total focus time, total distracted time, number of distractions, and a list of events (time + duration + type).
- A settings panel: grace-period seconds and a sensitivity/threshold control.
- A **debug/calibration mode** that displays the current yaw/pitch numbers live, so I can tune the "looking away" thresholds to my setup.
- A one-line privacy note: video is processed locally and never uploaded.

## Data
- Save each completed session to `localStorage` (local only) and show a simple history list of past sessions. Include a "clear history" button.

## Robustness (MVP-level)
- Handle **no camera / permission denied** gracefully with a clear message.
- Handle the face temporarily not being found without crashing.
- Don't spam overlay flicker at the boundary — debounce so tiny movements around the threshold don't rapidly toggle.

## Explicitly OUT of scope (do not build)
Electron/Tauri/desktop packaging, code signing, auto-update, user accounts, cloud sync, payments, multi-monitor handling, Mac-vs-Windows differences. If any of these seem needed, note it in a `LATER.md` list instead of building it.

## Deliverables
1. The working app files.
2. A short `README.md`: how to run it (exact commands), how to use it, and how to tune the thresholds via debug mode.
3. A `LATER.md` capturing anything you deliberately left out.

## Build order (so I get something runnable early)
1. Camera preview + permission handling working first.
2. Add FaceLandmarker and print live yaw/pitch to the screen (debug mode). Confirm detection works.
3. Add the focused/away decision + status indicator.
4. Add the session timer, grace period, overlay, and pause/resume.
5. Add logging, summary, and localStorage history.
6. Write the README and LATER files.

After each step, tell me how to run and verify it before moving on.

## Acceptance criteria
- I can start a session, and turning my head away or leaving the frame for more than the grace period darkens the screen and pauses the timer; returning restores both.
- At the end I see an accurate count and duration of my distractions.
- Nothing leaves my machine, and there is no server beyond the local static file server.
