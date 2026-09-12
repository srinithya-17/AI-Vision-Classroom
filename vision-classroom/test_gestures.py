from types import SimpleNamespace

from gestures.gesture_smoother import GestureSmoother
from gestures.hand_raised import classify_gesture, classify_gesture_with_confidence


def landmark(x, y, z=0.0):
    return SimpleNamespace(x=x, y=y, z=z)


def open_palm():
    hand = [landmark(0.0, 0.0) for _ in range(21)]
    hand[1] = landmark(-0.1, -0.05)
    hand[2] = landmark(-0.2, -0.12)
    hand[3] = landmark(-0.35, -0.22)
    hand[4] = landmark(-0.45, -0.35)

    for mcp, pip, tip, x in [
        (5, 6, 8, 0.15),
        (9, 10, 12, 0.05),
        (13, 14, 16, -0.05),
        (17, 18, 20, -0.15),
    ]:
        hand[mcp] = landmark(x, -0.08)
        hand[pip] = landmark(x, -0.28)
        hand[tip] = landmark(x, -0.55)

    return hand


def test_open_palm_uses_geometry():
    gesture, confidence = classify_gesture_with_confidence(open_palm())
    assert gesture == "OPEN_PALM"
    assert confidence > 0.7
    assert classify_gesture(open_palm()) == "OPEN_PALM"


def test_smoother_rejects_single_bad_frame():
    smoother = GestureSmoother(buffer_size=5, required_ratio=0.6)
    for gesture in ["OPEN_PALM", "OPEN_PALM", "UNKNOWN", "OPEN_PALM"]:
        stable = smoother.update(gesture)

    assert stable == "OPEN_PALM"
    assert smoother.stability() == 0.75