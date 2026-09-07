from angles import (
    calculate_elbow_angle,
    calculate_knee_angle,
    calculate_shoulder_angle
)


# Elbow
shoulder = (0, 1)
elbow = (0, 0)
wrist = (1, 0)

elbow_angle = calculate_elbow_angle(
    shoulder,
    elbow,
    wrist
)


# Knee
hip = (0, 1)
knee = (0, 0)
ankle = (1, 0)

knee_angle = calculate_knee_angle(
    hip,
    knee,
    ankle
)


# Shoulder
hip = (0, 1)
shoulder = (0, 0)
elbow = (1, 0)

shoulder_angle = calculate_shoulder_angle(
    hip,
    shoulder,
    elbow
)


print("Elbow Angle:", elbow_angle)
print("Knee Angle:", knee_angle)
print("Shoulder Angle:", shoulder_angle)