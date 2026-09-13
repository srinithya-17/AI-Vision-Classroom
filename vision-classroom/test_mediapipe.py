import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gestures.gesture_smoother import GestureSmoother
from gestures.hand_raised import classify_gesture
from gestures.hand_raised_pose import is_hand_raised
from gestures.hand_raise_smoother import HandRaiseSmoother
from physics.angles import calculate_angle
from vision.pose_tracker import PoseTracker


HAND_MODEL_PATH = "models/hand_landmarker.task"
POSE_MODEL_PATH = "models/pose_landmarker.task"


# -----------------------------
# Hand detector
# -----------------------------
base_options = python.BaseOptions(
    model_asset_path=HAND_MODEL_PATH
)

hand_options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

hand_detector = vision.HandLandmarker.create_from_options(
    hand_options
)


# -----------------------------
# Pose detector
# -----------------------------
pose_tracker = PoseTracker(POSE_MODEL_PATH)


# -----------------------------
# Webcam
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    hand_detector.close()
    pose_tracker.close()
    raise SystemExit


# -----------------------------
# Smoothers
# -----------------------------
gesture_smoother = GestureSmoother(
    buffer_size=12,
    required_ratio=0.70
)

hand_raise_smoother = HandRaiseSmoother(
    buffer_size=15,
    required_ratio=0.70
)


frame_timestamp_ms = 0


# -----------------------------
# Main loop
# -----------------------------
while True:

    success, frame = cap.read()

    if not success:
        print("Could not read frame.")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    # BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    frame_timestamp_ms += 33


    # -------------------------
    # Hand detection
    # -------------------------
    hand_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    hand_result = hand_detector.detect_for_video(
        hand_image,
        frame_timestamp_ms
    )


    # -------------------------
    # Pose detection
    # -------------------------
    pose_result = pose_tracker.detect(
        rgb_frame,
        frame_timestamp_ms
    )


    # -------------------------
    # Variables
    # -------------------------
    any_hand_raised = False
    stable_gesture = "UNKNOWN"

    left_elbow_angle = 0.0
    right_elbow_angle = 0.0


    # -------------------------
    # Process hands
    # -------------------------
    if hand_result.hand_landmarks:

        for hand_landmarks in hand_result.hand_landmarks:

            # Draw hand landmarks
            for landmark in hand_landmarks:

                x = int(
                    landmark.x * frame.shape[1]
                )

                y = int(
                    landmark.y * frame.shape[0]
                )

                cv2.circle(
                    frame,
                    (x, y),
                    4,
                    (0, 255, 0),
                    -1
                )


            # Gesture
            gesture = classify_gesture(
                hand_landmarks
            )

            stable_gesture = gesture_smoother.update(
                gesture
            )


            # Hand raised
            hand_raised = False

            if pose_result.pose_landmarks:

                hand_raised = is_hand_raised(
                    hand_landmarks,
                    pose_result.pose_landmarks[0]
                )

            if hand_raised:
                any_hand_raised = True


    # -------------------------
    # Smooth hand raise
    # -------------------------
    stable_hand_raised = hand_raise_smoother.update(
        any_hand_raised
    )


    # -------------------------
    # Process pose
    # -------------------------
    if pose_result.pose_landmarks:

        pose_landmarks = pose_result.pose_landmarks[0]


        # -------------------------
        # Calculate elbow angles
        # -------------------------

        # Left arm:
        # Shoulder → Elbow → Wrist
        left_elbow_angle = calculate_angle(
            pose_landmarks[11],
            pose_landmarks[13],
            pose_landmarks[15]
        )


        # Right arm:
        # Shoulder → Elbow → Wrist
        right_elbow_angle = calculate_angle(
            pose_landmarks[12],
            pose_landmarks[14],
            pose_landmarks[16]
        )


        # -------------------------
        # Draw important points
        # -------------------------
        important_points = [
            11, 12,
            13, 14,
            15, 16,
            23, 24,
            25, 26,
            27, 28
        ]

        for index in important_points:

            landmark = pose_landmarks[index]

            x = int(
                landmark.x * frame.shape[1]
            )

            y = int(
                landmark.y * frame.shape[0]
            )

            cv2.circle(
                frame,
                (x, y),
                6,
                (255, 0, 0),
                -1
            )


        # -------------------------
        # Draw pose connections
        # -------------------------
        connections = [
            (11, 13),
            (13, 15),

            (12, 14),
            (14, 16),

            (11, 12),

            (11, 23),
            (12, 24),

            (23, 24),

            (23, 25),
            (25, 27),

            (24, 26),
            (26, 28)
        ]

        for start, end in connections:

            p1 = pose_landmarks[start]
            p2 = pose_landmarks[end]

            x1 = int(
                p1.x * frame.shape[1]
            )

            y1 = int(
                p1.y * frame.shape[0]
            )

            x2 = int(
                p2.x * frame.shape[1]
            )

            y2 = int(
                p2.y * frame.shape[0]
            )

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )


        # -------------------------
        # Display elbow angles
        # -------------------------

        cv2.putText(
            frame,
            f"Left Elbow: {left_elbow_angle:.1f} deg",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Right Elbow: {right_elbow_angle:.1f} deg",
            (20, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 255),
            2
        )


    # -------------------------
    # Display gesture
    # -------------------------
    cv2.putText(
        frame,
        f"Gesture: {stable_gesture}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    # -------------------------
    # Hand raise status
    # -------------------------
    if stable_hand_raised:

        cv2.putText(
            frame,
            "HAND RAISED!",
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3
        )

    else:

        cv2.putText(
            frame,
            "Hand down",
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


    # -------------------------
    # Detection counts
    # -------------------------
    hands_count = len(
        hand_result.hand_landmarks
    )

    pose_count = len(
        pose_result.pose_landmarks
    )

    cv2.putText(
        frame,
        f"Hands detected: {hands_count}",
        (20, frame.shape[0] - 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Pose detected: {pose_count}",
        (20, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # -------------------------
    # Show
    # -------------------------
    cv2.imshow(
        "Vision Classroom",
        frame
    )


    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()

hand_detector.close()
pose_tracker.close()