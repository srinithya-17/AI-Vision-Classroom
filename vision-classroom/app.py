import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse

import requests
import streamlit as st

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gestures.hand_raised import classify_gesture_with_confidence
from gestures.gesture_smoother import GestureSmoother

from gestures.hand_raised_pose import is_hand_raised
from gestures.hand_raise_smoother import HandRaiseSmoother

from vision.pose_tracker import PoseTracker
from physics_engine import PhysicsEngine

from events.event_store import save_event, get_latest_event


BACKEND_URL = "http://127.0.0.1:8000"
PHYSICS_UPDATE_INTERVAL_SECONDS = 0.2


def normalize_google_meet_url(meet_link):
    """Return a safe Google Meet URL, accepting a scheme-less meeting code."""
    candidate = meet_link.strip()
    if not candidate:
        return None

    if not candidate.startswith(("http://", "https://")):
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    meeting_code = parsed.path.strip("/")
    valid_code = re.fullmatch(r"[a-z]{3}-[a-z]{4}-[a-z]{3}", meeting_code)

    if parsed.scheme != "https" or parsed.netloc != "meet.google.com" or not valid_code:
        return None

    return f"https://meet.google.com/{meeting_code}"


def send_physics_update(student_name, physics_update):
    """Send a throttled physics snapshot without interrupting camera processing."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/classroom/physics/{student_name}",
            json=physics_update,
            timeout=2,
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Physics update failed: {error}")


def update_classroom_hand_state(student_name, action):
    """Handle an explicit student hand-state action without affecting vision."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/classroom/hand/{student_name}/{action}",
            timeout=2,
        )
        response.raise_for_status()
        return True

    except requests.RequestException as error:
        st.error(f"Could not update hand status: {error}")
        return False


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Vision-Based Interactive Classroom",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

HAND_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "hand_landmarker.task"
)

POSE_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "pose_landmarker.task"
)


# ============================================================
# CHECK MODEL FILES
# ============================================================

if not os.path.exists(HAND_MODEL_PATH):

    st.error(
        "Hand model not found:\n"
        + HAND_MODEL_PATH
    )

    st.stop()


if not os.path.exists(POSE_MODEL_PATH):

    st.error(
        "Pose model not found:\n"
        + POSE_MODEL_PATH
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

if "student_joined" not in st.session_state:
    st.session_state.student_joined = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎓 Classroom")

    student_name = st.text_input(
        "Student Name",
        value=st.session_state.student_name,
        placeholder="Enter your name"
    )

    st.session_state.student_name = student_name

    if st.button("Join Classroom"):

        if not student_name.strip():
            st.error("Enter your student name before joining the classroom.")

        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/classroom/students",
                    json={"name": student_name.strip()},
                    timeout=3,
                )
                response.raise_for_status()
                st.session_state.student_joined = True
                st.success("Joined the classroom successfully.")

            except requests.RequestException as error:
                st.error(f"Could not join the classroom: {error}")

    st.divider()

    st.subheader("Google Meet")

    meet_link = st.text_input(
        "Google Meet Link",
        placeholder="Paste Meet link here"
    )

    if meet_link:

        normalized_meet_link = normalize_google_meet_url(meet_link)

        if normalized_meet_link:
            st.link_button(
                "🎥 Join Google Meet",
                normalized_meet_link
            )

        else:
            st.error(
                "Enter a valid Google Meet URL, for example "
                "meet.google.com/abc-defg-hij."
            )

    st.divider()

    st.info(
        "Google Meet handles communication.\n\n"
        "Vision Classroom handles AI-based "
        "classroom interaction."
    )


# ============================================================
# MAIN TITLE
# ============================================================

st.title(
    "🎓 Vision-Based Interactive Classroom"
)

st.header("Student Portal")

st.write(
    "AI-powered classroom interaction using "
    "MediaPipe hand and pose tracking."
)

st.caption(
    "Google Meet is the communication layer. AI Vision powers classroom "
    "interaction, while Physics Lab analyzes live pose landmarks."
)


# ============================================================
# STUDENT INFORMATION
# ============================================================

if student_name.strip():

    st.success(
        f"Logged in as: {student_name}"
    )

else:

    st.warning(
        "Enter your student name in the sidebar."
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Vision System",
        "MediaPipe"
    )


with col2:

    st.metric(
        "Gesture Recognition",
        "Active"
    )


with col3:

    st.metric(
        "Classroom Events",
        "Active"
    )

with col4:
    st.metric("Hand Tracking", "Active")

with col5:
    st.metric("Pose Tracking", "Active")


st.divider()


# ============================================================
# CLASSROOM OVERVIEW
# ============================================================

st.subheader("Classroom Overview")


@st.fragment(run_every="1s")
def show_classroom_overview():

    if not student_name.strip() or not st.session_state.student_joined:
        st.info("Enter your name and use Join Classroom to see live classroom status.")
        return

    try:
        response = requests.get(f"{BACKEND_URL}/classroom/state", timeout=2)
        response.raise_for_status()
        state = response.json()

    except requests.RequestException:
        st.info("Classroom status is waiting for the FastAPI backend.")
        return

    students = state.get("students", [])
    raised_hands = state.get("raised_hands", [])
    gesture = state.get("recent_gestures", {}).get(student_name, {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Participants", len(students))
    col2.metric("Your Hand", "Raised" if student_name in raised_hands else "Down")
    col3.metric("Latest Gesture", gesture.get("gesture", "Waiting"))
    col4.metric(
        "Physics Lab",
        "Active" if state.get("physics_lab_active") else "Available",
    )

    st.markdown("#### Teacher Presentation")
    st.write(
        f"Shared presentation state: slide {state.get('current_slide', 1)} "
        f"of {state.get('total_slides', 1)}."
    )
    st.caption(
        "Presentation content is controlled by the teacher; this portal shows "
        "the shared classroom position."
    )

    st.markdown("#### Raise Hand")
    raise_col, clear_col = st.columns(2)
    with raise_col:
        if st.button("Raise Hand", key="manual_raise_hand"):
            if update_classroom_hand_state(student_name, "raise"):
                st.success("Your hand is marked as raised.")
    with clear_col:
        if st.button("Lower Hand", key="manual_clear_hand"):
            if update_classroom_hand_state(student_name, "clear"):
                st.success("Your hand is marked as down.")

    st.caption(
        "You can also raise or lower your hand naturally in view of the camera. "
        "Vision events remain transition-based."
    )


show_classroom_overview()


st.divider()


# ============================================================
# VISION PROCESSOR
# ============================================================

class VisionProcessor(VideoProcessorBase):

    def __init__(self, student_name):

        # ----------------------------------------------------
        # STORE STUDENT NAME
        # ----------------------------------------------------

        self.student_name = student_name


        # ----------------------------------------------------
        # HAND LANDMARKER
        # ----------------------------------------------------

        hand_base_options = python.BaseOptions(
            model_asset_path=HAND_MODEL_PATH
        )

        hand_options = vision.HandLandmarkerOptions(
            base_options=hand_base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.hand_detector = (
            vision.HandLandmarker.create_from_options(
                hand_options
            )
        )


        # ----------------------------------------------------
        # POSE TRACKER
        # ----------------------------------------------------

        self.pose_tracker = PoseTracker(
            POSE_MODEL_PATH
        )


        # ----------------------------------------------------
        # GESTURE SMOOTHER
        # ----------------------------------------------------

        self.gesture_smoother = GestureSmoother(
            buffer_size=12,
            required_ratio=0.70
        )


        # ----------------------------------------------------
        # HAND RAISE SMOOTHER
        # ----------------------------------------------------

        self.hand_raise_smoother = HandRaiseSmoother(
            buffer_size=15,
            required_ratio=0.70
        )


        # ----------------------------------------------------
        # CURRENT STATE
        # ----------------------------------------------------

        self.current_gesture = "UNKNOWN"

        self.hand_raised = False

        self.previous_hand_raised = False

        self.previous_gesture = "UNKNOWN"

        self.frame_timestamp_ms = 0

        # PhysicsEngine keeps the motion history between pose frames. Its
        # combined result is sent at most five times per second.
        self.physics_engine = PhysicsEngine()
        self.last_physics_update_at = 0.0
        self.latest_physics = None


    # ========================================================
    # PROCESS VIDEO FRAME
    # ========================================================

    def recv(self, frame):

        # ----------------------------------------------------
        # CONVERT FRAME
        # ----------------------------------------------------

        image = frame.to_ndarray(
            format="rgb24"
        )


        # ----------------------------------------------------
        # HAND DETECTION
        # ----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image
        )

        hand_result = (
            self.hand_detector.detect_for_video(
                mp_image,
                self.frame_timestamp_ms
            )
        )


        # ----------------------------------------------------
        # POSE DETECTION
        # ----------------------------------------------------

        pose_result = (
            self.pose_tracker.detect(
                image,
                self.frame_timestamp_ms
            )
        )

        # ====================================================
        # PHYSICS METRICS
        # ====================================================
        # PhysicsEngine receives the MediaPipe pose landmarks directly and
        # returns one combined angle/velocity/acceleration snapshot.
        if pose_result.pose_landmarks:
            pose = pose_result.pose_landmarks[0]
            current_time = time.monotonic()

            physics_result = self.physics_engine.process_landmarks(
                pose,
                current_time,
            )

            if physics_result:
                self.latest_physics = {
                    **physics_result,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                }

                if (
                    current_time - self.last_physics_update_at
                    >= PHYSICS_UPDATE_INTERVAL_SECONDS
                ):
                    send_physics_update(self.student_name, self.latest_physics)
                    self.last_physics_update_at = current_time


        # ----------------------------------------------------
        # UPDATE TIMESTAMP
        # ----------------------------------------------------

        self.frame_timestamp_ms += 33


        # ====================================================
        # GESTURE RECOGNITION
        # ====================================================

        gesture = "UNKNOWN"
        gesture_confidence = 0.0


        if hand_result.hand_landmarks:

            first_hand = (
                hand_result.hand_landmarks[0]
            )

            gesture, gesture_confidence = classify_gesture_with_confidence(
                first_hand
            )


        self.current_gesture = (
            self.gesture_smoother.update(
                gesture
            )
        )


        # ====================================================
        # HAND RAISED DETECTION
        # ====================================================

        raw_hand_raised = False


        if (
            hand_result.hand_landmarks
            and pose_result.pose_landmarks
        ):

            first_hand = (
                hand_result.hand_landmarks[0]
            )

            first_pose = (
                pose_result.pose_landmarks[0]
            )

            hand_label = None
            if hand_result.handedness and hand_result.handedness[0]:
                hand_label = hand_result.handedness[0][0]

            raw_hand_raised = is_hand_raised(
                first_hand,
                first_pose,
                hand_label
            )


        self.hand_raised = (
            self.hand_raise_smoother.update(
                raw_hand_raised
            )
        )


        # ====================================================
        # CREATE CLASSROOM EVENT
        # ====================================================

        if (
            self.hand_raised
            and not self.previous_hand_raised
        ):

            save_event(
                self.student_name,
                "HAND_RAISED",
                True,
                self.hand_raise_smoother.stability()
            )


        elif (
            not self.hand_raised
            and self.previous_hand_raised
        ):

            save_event(
                self.student_name,
                "HAND_DOWN",
                False,
                self.hand_raise_smoother.stability()
            )


        # Update previous state

        self.previous_hand_raised = (
            self.hand_raised
        )

        # A gesture event is written only after smoothing changes the stable
        # gesture, so the event file is not rewritten on every video frame.
        if (
            self.current_gesture != self.previous_gesture
            and self.current_gesture != "UNKNOWN"
        ):
            save_event(
                self.student_name,
                "GESTURE_DETECTED",
                self.current_gesture,
                self.gesture_smoother.stability() * gesture_confidence
            )

        self.previous_gesture = self.current_gesture


        # ====================================================
        # DRAW VIDEO
        # ====================================================

        output = image.copy()

        import cv2


        # ----------------------------------------------------
        # DRAW HAND LANDMARKS
        # ----------------------------------------------------

        if hand_result.hand_landmarks:

            for hand in hand_result.hand_landmarks:

                for landmark in hand:

                    x = int(
                        landmark.x
                        * output.shape[1]
                    )

                    y = int(
                        landmark.y
                        * output.shape[0]
                    )

                    if (
                        0 <= x < output.shape[1]
                        and
                        0 <= y < output.shape[0]
                    ):

                        cv2.circle(
                            output,
                            (x, y),
                            4,
                            (0, 255, 0),
                            -1
                        )

                for start, end in [
                    (0, 1), (1, 2), (2, 3), (3, 4),
                    (0, 5), (5, 6), (6, 7), (7, 8),
                    (5, 9), (9, 10), (10, 11), (11, 12),
                    (9, 13), (13, 14), (14, 15), (15, 16),
                    (13, 17), (17, 18), (18, 19), (19, 20),
                    (0, 17)
                ]:
                    start_point = hand[start]
                    end_point = hand[end]
                    cv2.line(
                        output,
                        (int(start_point.x * output.shape[1]), int(start_point.y * output.shape[0])),
                        (int(end_point.x * output.shape[1]), int(end_point.y * output.shape[0])),
                        (0, 180, 0),
                        2
                    )

        if pose_result.pose_landmarks:
            pose = pose_result.pose_landmarks[0]
            for start, end in [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12)]:
                cv2.line(
                    output,
                    (int(pose[start].x * output.shape[1]), int(pose[start].y * output.shape[0])),
                    (int(pose[end].x * output.shape[1]), int(pose[end].y * output.shape[0])),
                    (230, 120, 40),
                    2
                )


        # ----------------------------------------------------
        # DISPLAY STUDENT NAME
        # ----------------------------------------------------

        cv2.putText(
            output,
            f"Student: {self.student_name}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ----------------------------------------------------
        # DISPLAY GESTURE
        # ----------------------------------------------------

        cv2.putText(
            output,
            f"Gesture: {self.current_gesture}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ----------------------------------------------------
        # DISPLAY HAND STATUS
        # ----------------------------------------------------

        cv2.putText(
            output,
            f"Hand Raised: {self.hand_raised}",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            output,
            f"Gesture Stability: {self.gesture_smoother.stability() * 100:.0f}%",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 220, 0),
            2
        )

        if self.latest_physics:
            cv2.putText(
                output,
                f"Elbow: {self.latest_physics['elbow_angle']:.1f} deg",
                (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 220, 0),
                2
            )
            cv2.putText(
                output,
                f"Knee: {self.latest_physics['knee_angle']:.1f} deg",
                (20, 230),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 220, 0),
                2
            )
            cv2.putText(
                output,
                f"Velocity: {self.latest_physics['velocity']:.3f}",
                (20, 260),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 220, 0),
                2
            )
            cv2.putText(
                output,
                f"Acceleration: {self.latest_physics['acceleration']:.3f}",
                (20, 290),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 220, 0),
                2
            )


        # ----------------------------------------------------
        # RETURN FRAME
        # ----------------------------------------------------

        from av import VideoFrame

        return VideoFrame.from_ndarray(
            output,
            format="rgb24"
        )


    # ========================================================
    # CLEANUP
    # ========================================================

    def close(self):

        try:

            self.hand_detector.close()

        except Exception:

            pass


        try:

            self.pose_tracker.close()

        except Exception:

            pass


# ============================================================
# START VISION CLASSROOM
# ============================================================

st.subheader(
    "📷 Vision Classroom"
)

st.write(
    "Allow camera access to enable "
    "AI classroom interaction."
)


if not student_name.strip():

    st.info(
        "Enter your student name before "
        "starting the camera."
    )

elif not st.session_state.student_joined:

    st.info(
        "Use Join Classroom before starting the camera."
    )

else:

    # --------------------------------------------------------
    # IMPORTANT:
    # Pass the student's name into VisionProcessor.
    # --------------------------------------------------------

    def create_processor():

        return VisionProcessor(
            student_name
        )


    webrtc_streamer(
        key="vision-classroom",

        video_processor_factory=(
            create_processor
        ),

        media_stream_constraints={
            "video": True,
            "audio": False
        },

        async_processing=True
    )


# ============================================================
# LATEST CLASSROOM EVENT
# ============================================================

st.divider()

st.subheader(
    "📊 Latest Classroom Event"
)


@st.fragment(run_every="1s")
def show_latest_event():

    event = get_latest_event()


    if event is None:

        st.info(
            "No classroom event detected yet."
        )

        return


    col1, col2 = st.columns(2)


    with col1:

        st.write("**Student**")

        st.write(
            event.get(
                "student",
                "Unknown"
            )
        )


        st.write("**Event**")

        st.write(
            event.get(
                "event_type",
                "Unknown"
            )
        )


    with col2:

        st.write("**Value**")

        st.write(
            str(
                event.get(
                    "value",
                    ""
                )
            )
        )


        st.write("**Detected At**")

        st.write(
            event.get(
                "timestamp",
                "Unknown"
            )
        )


show_latest_event()


# ============================================================
# PHYSICS LAB
# ============================================================

st.divider()

st.subheader("Physics Lab")

st.caption(
    "Current measurements are derived from MediaPipe image coordinates and "
    "are not calibrated to real-world SI units."
)


@st.fragment(run_every="1s")
def show_physics_lab():

    if not student_name.strip():
        st.info("Join the classroom to see your Physics Lab values.")
        return

    try:
        response = requests.get(
            f"{BACKEND_URL}/classroom/state",
            timeout=2,
        )
        response.raise_for_status()
        state = response.json()
        physics = state.get("physics", {}).get(student_name, {})

    except requests.RequestException:
        st.info("Physics Lab is waiting for the classroom backend.")
        return

    if not physics:
        st.info("Move in view of the camera to generate Physics Lab values.")
        return

    st.caption(
        "Physics Lab is "
        + ("active" if state.get("physics_lab_active") else "available")
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Elbow Angle", f"{physics.get('elbow_angle', 0):.1f}°")
    col2.metric("Knee Angle", f"{physics.get('knee_angle', 0):.1f}°")
    col3.metric("Velocity (image units/s)", f"{physics.get('velocity', 0):.3f}")
    col4.metric(
        "Acceleration (image units/s²)",
        f"{physics.get('acceleration', 0):.3f}",
    )


show_physics_lab()


# ============================================================
# SUPPORTED INTERACTIONS
# ============================================================

st.divider()

st.subheader(
    "🧠 Supported Classroom Interactions"
)


col1, col2 = st.columns(2)


with col1:

    st.write("✋ **Hand Raised**")

    st.write(
        "Detects when the student physically "
        "raises their hand."
    )


    st.write("🖐️ **Open Palm**")

    st.write(
        "Recognizes an open-palm gesture."
    )


with col2:

    st.write("👍 **Thumbs Up**")

    st.write(
        "Recognizes a thumbs-up gesture."
    )


    st.write("✌️ **Two Fingers**")

    st.write(
        "Recognizes a two-finger gesture."
    )


# ============================================================
# ARCHITECTURE
# ============================================================

st.divider()

st.subheader(
    "🏗️ Current Architecture"
)

st.code(
    """
Student Browser
      |
      +---- Google Meet
      |       |
      |       +---- Teacher / Students
      |
      +---- Vision Classroom Camera
              |
              v
          MediaPipe
              |
              +---- Hand Detection
              |
              +---- Pose Detection
              |
              +---- Gesture Recognition
              |
              +---- Hand-Raised Detection
              |
              v
       Student-Specific Event
              |
              v
       latest_event.json
              |
              v
        Teacher Dashboard
    """,
    language="text"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Vision-Based Interactive Classroom & "
    "Physics Learning System"
)
