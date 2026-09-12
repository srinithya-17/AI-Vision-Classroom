def is_hand_raised(hand_landmarks, pose_landmarks, handedness=None):
    """
    Detect whether either hand is physically raised
    above the corresponding shoulder.
    """

    if not hand_landmarks or not pose_landmarks:
        return False

    # Hand wrist
    hand_wrist = hand_landmarks[0]

    # Pose landmarks
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    left_shoulder = pose_landmarks[LEFT_SHOULDER]
    right_shoulder = pose_landmarks[RIGHT_SHOULDER]

    # MediaPipe handedness is preferred. If it is unavailable, the shoulder
    # nearest to the wrist is a simple fallback for a single visible person.
    if handedness:
        label = getattr(handedness, "category_name", "").lower()
        shoulder = right_shoulder if label == "right" else left_shoulder
    else:
        left_distance = abs(hand_wrist.x - left_shoulder.x)
        right_distance = abs(hand_wrist.x - right_shoulder.x)
        shoulder = left_shoulder if left_distance <= right_distance else right_shoulder

    # Add a small margin so normal arm movement
    # isn't immediately considered a raised hand.
    margin = 0.05

    return hand_wrist.y < shoulder.y - margin