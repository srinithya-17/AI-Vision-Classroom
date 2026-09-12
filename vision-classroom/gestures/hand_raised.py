import math


# ============================================================
# BASIC GEOMETRY
# ============================================================

def distance(a, b):
    """Calculate 3D distance between two MediaPipe landmarks."""

    return math.sqrt(
        (a.x - b.x) ** 2
        + (a.y - b.y) ** 2
        + (
            getattr(a, "z", 0.0)
            - getattr(b, "z", 0.0)
        ) ** 2
    )


def angle(a, b, c):
    """
    Calculate angle ABC in degrees.

    b is the joint being measured.
    """

    ab = (
        a.x - b.x,
        a.y - b.y,
        getattr(a, "z", 0.0)
        - getattr(b, "z", 0.0)
    )

    cb = (
        c.x - b.x,
        c.y - b.y,
        getattr(c, "z", 0.0)
        - getattr(b, "z", 0.0)
    )

    ab_length = math.sqrt(
        sum(value * value for value in ab)
    )

    cb_length = math.sqrt(
        sum(value * value for value in cb)
    )

    if ab_length == 0 or cb_length == 0:
        return 0.0

    dot_product = sum(
        ab[i] * cb[i]
        for i in range(3)
    )

    cosine = (
        dot_product
        / (ab_length * cb_length)
    )

    cosine = max(
        -1.0,
        min(1.0, cosine)
    )

    return math.degrees(
        math.acos(cosine)
    )


# ============================================================
# HAND VALIDATION
# ============================================================

def _valid_hand(hand):
    return (
        hand is not None
        and len(hand) >= 21
    )


# ============================================================
# FINGER DETECTION
# ============================================================

def finger_extended(
    hand,
    tip,
    pip,
    mcp
):
    """
    Determine whether a finger is extended.

    Uses both joint angle and distance from the wrist.
    """

    wrist = hand[0]

    tip_distance = distance(
        hand[tip],
        wrist
    )

    pip_distance = distance(
        hand[pip],
        wrist
    )

    mcp_distance = distance(
        hand[mcp],
        wrist
    )

    joint_angle = angle(
        hand[tip],
        hand[pip],
        hand[mcp]
    )

    # A finger is considered extended when:
    #
    # 1. The finger is relatively straight.
    # 2. The fingertip is farther from the wrist
    #    than the PIP joint.
    #
    # The thresholds are intentionally moderate so
    # slightly rotated hands still work.

    straight = joint_angle > 135

    stretched = (
        tip_distance
        > pip_distance * 1.05
    )

    away_from_mcp = (
        tip_distance
        > mcp_distance * 1.12
    )

    return (
        straight
        and stretched
        and away_from_mcp
    )


# ============================================================
# THUMB DETECTION
# ============================================================

def thumb_extended(hand):
    """
    Determine whether the thumb is extended.

    Thumb geometry is different from the four fingers,
    so it is handled separately.
    """

    thumb_tip = hand[4]
    thumb_ip = hand[3]
    thumb_mcp = hand[2]
    wrist = hand[0]

    tip_distance = distance(
        thumb_tip,
        wrist
    )

    ip_distance = distance(
        thumb_ip,
        wrist
    )

    thumb_angle = angle(
        thumb_tip,
        thumb_ip,
        thumb_mcp
    )

    return (
        tip_distance
        > ip_distance * 1.03
        and thumb_angle > 120
    )


# ============================================================
# FINGER STATE
# ============================================================

def get_finger_states(hand):
    """
    Return the state of the four main fingers.

    Order:
        index
        middle
        ring
        pinky
    """

    index = finger_extended(
        hand,
        8,
        6,
        5
    )

    middle = finger_extended(
        hand,
        12,
        10,
        9
    )

    ring = finger_extended(
        hand,
        16,
        14,
        13
    )

    pinky = finger_extended(
        hand,
        20,
        18,
        17
    )

    return [
        index,
        middle,
        ring,
        pinky
    ]


# ============================================================
# GESTURE CLASSIFICATION
# ============================================================

def classify_gesture_with_confidence(hand):
    """
    Classify a MediaPipe hand.

    Returns:

        (gesture_name, confidence)

    Supported gestures:

        OPEN_PALM
        FIST
        THUMBS_UP
        THUMBS_DOWN
        TWO_FINGERS
        POINTING
        OK_SIGN
        UNKNOWN
    """

    if not _valid_hand(hand):
        return "UNKNOWN", 0.0

    index, middle, ring, pinky = (
        get_finger_states(hand)
    )

    extended_count = sum([
        index,
        middle,
        ring,
        pinky
    ])

    thumb = thumb_extended(hand)

    # --------------------------------------------------------
    # OK SIGN
    # --------------------------------------------------------
    #
    # Thumb tip and index tip should be close.
    # Middle and ring should normally be extended.
    # Pinky is allowed some flexibility because hand
    # orientation can affect the detection.
    #

    thumb_index_distance = distance(
        hand[4],
        hand[8]
    )

    hand_scale = max(
        distance(hand[0], hand[9]),
        0.001
    )

    ok_threshold = hand_scale * 0.45

    if (
        thumb_index_distance < ok_threshold
        and middle
        and ring
    ):
        return "OK_SIGN", 0.90

    # --------------------------------------------------------
    # OPEN PALM
    # --------------------------------------------------------

    if extended_count == 4:
        return "OPEN_PALM", 0.95

    # --------------------------------------------------------
    # TWO FINGERS / PEACE
    # --------------------------------------------------------

    if (
        index
        and middle
        and not ring
        and not pinky
    ):
        return "TWO_FINGERS", 0.92

    # --------------------------------------------------------
    # POINTING
    # --------------------------------------------------------

    if (
        index
        and not middle
        and not ring
        and not pinky
    ):
        return "POINTING", 0.92

    # --------------------------------------------------------
    # CLOSED FIST
    # --------------------------------------------------------
    #
    # All four fingers folded.
    #
    # We check this BEFORE thumbs-up/down.
    #

    if (
        not index
        and not middle
        and not ring
        and not pinky
    ):

        thumb_tip = hand[4]
        thumb_base = hand[2]

        # Thumb pointing upward
        if (
            thumb
            and thumb_tip.y
            < thumb_base.y - 0.03
        ):
            return "THUMBS_UP", 0.90

        # Thumb pointing downward
        if (
            thumb
            and thumb_tip.y
            > thumb_base.y + 0.03
        ):
            return "THUMBS_DOWN", 0.90

        # No extended thumb -> fist
        if not thumb:
            return "FIST", 0.95

        # Sometimes a closed fist has the thumb
        # resting across the fingers.
        return "FIST", 0.82

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return "UNKNOWN", 0.40


# ============================================================
# SIMPLE CLASSIFIER
# ============================================================

def classify_gesture(hand):
    """
    Backward-compatible classifier.

    Existing app.py can continue using:

        classify_gesture(hand)
    """

    gesture, _ = classify_gesture_with_confidence(
        hand
    )

    return gesture