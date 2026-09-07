import math

def calculate_angle(a, b, c):
    """
    Calculate the angle ABC in degrees.
    """

    ba = (
        a[0] - b[0],
        a[1] - b[1]
    )

    bc = (
        c[0] - b[0],
        c[1] - b[1]
    )

    dot_product = (
        ba[0] * bc[0] +
        ba[1] * bc[1]
    )

    magnitude_ba = math.sqrt(
        ba[0] ** 2 +
        ba[1] ** 2
    )

    magnitude_bc = math.sqrt(
        bc[0] ** 2 +
        bc[1] ** 2
    )

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    cos_angle = dot_product / (
        magnitude_ba * magnitude_bc
    )

    cos_angle = max(-1.0, min(1.0, cos_angle))

    angle = math.degrees(
        math.acos(cos_angle)
    )

    return angle


def calculate_elbow_angle(shoulder, elbow, wrist):
    return calculate_angle(
        shoulder,
        elbow,
        wrist
    )


def calculate_knee_angle(hip, knee, ankle):
    return calculate_angle(
        hip,
        knee,
        ankle
    )


def calculate_shoulder_angle(hip, shoulder, elbow):
    return calculate_angle(
        hip,
        shoulder,
        elbow
    )