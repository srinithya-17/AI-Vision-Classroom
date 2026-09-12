# Vision-Based Interactive Classroom

## Person 1 Contribution

- Set up MediaPipe Tasks API hand and pose landmark detection.
- Implemented readable hand gesture recognition for open palm, fist, thumbs up/down, two fingers, pointing, and OK sign.
- Added temporal smoothing so one poor camera frame does not immediately change the displayed gesture.
- Added pose and hand landmark matching for hand-raised detection.
- Added state-change classroom events for `HAND_RAISED`, `HAND_DOWN`, and stable `GESTURE_DETECTED`.
- Added a small stability/confidence value for the overlay and optional event data.
- Added camera overlay feedback for the student, gesture, hand status, landmarks, and tracking status.

## How The Vision Module Works

The camera frame is sent to MediaPipe. The hand landmarker finds 21 points on up to two hands, and the pose landmarker finds body points such as the shoulders and wrists. The gesture classifier compares normalized distances and finger joint angles instead of relying on only one screen coordinate.

The `GestureSmoother` keeps a short history and changes the displayed gesture only when enough recent frames agree. Hand-raised detection compares the wrist with the corresponding shoulder and uses a small margin. `HandRaiseSmoother` then prevents hand state flicker.

When a stable state changes, the event store writes one simple JSON event to `events/latest_event.json`. This is an interface for a future backend or teacher dashboard; the vision module does not depend on that backend. The same frame data can later be passed to the physics module as hand landmarks, pose landmarks, gesture, hand-raised state, and timestamp for angle or motion calculations.

Google Meet remains the communication layer. Vision Classroom only supplies computer-vision classroom interaction.

## Run The Demo

```text
streamlit run app.py
```

The webcam permission must be allowed in the browser. The MediaPipe model files must remain in the `models` directory.