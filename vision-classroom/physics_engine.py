from angles import (
    calculate_elbow_angle,
    calculate_knee_angle,
    calculate_shoulder_angle,
)
from projectile import (
    calculate_flight_time,
    calculate_max_height,
    calculate_projectile_velocity,
    calculate_range,
)
from velocity import (
    calculate_acceleration,
    calculate_distance,
    calculate_velocity,
)


class PhysicsEngine:
    """Phase 2 physics calculations with a MediaPipe landmark adapter."""

    def __init__(self):
        self.previous_position = None
        self.previous_velocity = 0.0
        self.previous_timestamp = None

    def get_elbow_angle(self, shoulder, elbow, wrist):
        return calculate_elbow_angle(shoulder, elbow, wrist)

    def get_knee_angle(self, hip, knee, ankle):
        return calculate_knee_angle(hip, knee, ankle)

    def get_shoulder_angle(self, hip, shoulder, elbow):
        return calculate_shoulder_angle(hip, shoulder, elbow)

    def get_velocity(self, previous_position, current_position, dt):
        return calculate_velocity(previous_position, current_position, dt)

    def get_acceleration(self, previous_velocity, current_velocity, dt):
        return calculate_acceleration(previous_velocity, current_velocity, dt)

    def get_projectile_data(self, speed, angle):
        vx, vy = calculate_projectile_velocity(speed, angle)
        return {
            "horizontal_velocity": vx,
            "vertical_velocity": vy,
            "flight_time": calculate_flight_time(speed, angle),
            "maximum_height": calculate_max_height(speed, angle),
            "range": calculate_range(speed, angle),
        }

    def process_landmarks(self, pose_landmarks, timestamp):
        """Return one physics snapshot from MediaPipe Pose landmarks.

        ``timestamp`` must be a monotonically increasing time in seconds.
        Positions use MediaPipe's normalized image coordinates.
        """
        if pose_landmarks is None or len(pose_landmarks) <= 28:
            return None

        left_elbow = self.get_elbow_angle(
            _point(pose_landmarks[11]),
            _point(pose_landmarks[13]),
            _point(pose_landmarks[15]),
        )
        right_elbow = self.get_elbow_angle(
            _point(pose_landmarks[12]),
            _point(pose_landmarks[14]),
            _point(pose_landmarks[16]),
        )
        left_knee = self.get_knee_angle(
            _point(pose_landmarks[23]),
            _point(pose_landmarks[25]),
            _point(pose_landmarks[27]),
        )
        right_knee = self.get_knee_angle(
            _point(pose_landmarks[24]),
            _point(pose_landmarks[26]),
            _point(pose_landmarks[28]),
        )

        current_position = (
            (pose_landmarks[15].x + pose_landmarks[16].x) / 2,
            (pose_landmarks[15].y + pose_landmarks[16].y) / 2,
        )
        velocity = 0.0
        acceleration = 0.0

        if self.previous_position is not None and self.previous_timestamp is not None:
            dt = timestamp - self.previous_timestamp
            velocity = self.get_velocity(self.previous_position, current_position, dt)
            acceleration = self.get_acceleration(self.previous_velocity, velocity, dt)

        self.previous_position = current_position
        self.previous_velocity = velocity
        self.previous_timestamp = timestamp

        return {
            "elbow_angle": round((left_elbow + right_elbow) / 2, 2),
            "knee_angle": round((left_knee + right_knee) / 2, 2),
            "velocity": round(velocity, 4),
            "acceleration": round(acceleration, 4),
        }


def _point(landmark):
    return landmark.x, landmark.y
