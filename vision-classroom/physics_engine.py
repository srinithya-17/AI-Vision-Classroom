from angles import (
    calculate_elbow_angle,
    calculate_knee_angle,
    calculate_shoulder_angle
)

from velocity import (
    calculate_velocity,
    calculate_acceleration
)

from projectile import (
    calculate_projectile_velocity,
    calculate_flight_time,
    calculate_max_height,
    calculate_range
)


class PhysicsEngine:

    def __init__(self):
        # For real-time velocity and acceleration
        self.previous_position = None
        self.previous_velocity = 0.0
        self.previous_timestamp = None

    # -------------------------------
    # EXISTING ANGLE FUNCTIONS
    # -------------------------------

    def get_elbow_angle(self, shoulder, elbow, wrist):
        return calculate_elbow_angle(shoulder, elbow, wrist)

    def get_knee_angle(self, hip, knee, ankle):
        return calculate_knee_angle(hip, knee, ankle)

    def get_shoulder_angle(self, hip, shoulder, elbow):
        return calculate_shoulder_angle(hip, shoulder, elbow)

    # -------------------------------
    # EXISTING VELOCITY FUNCTIONS
    # -------------------------------

    def get_velocity(self, p1, p2, dt):
        return calculate_velocity(p1, p2, dt)

    def get_acceleration(self, v1, v2, dt):
        return calculate_acceleration(v1, v2, dt)

    # -------------------------------
    # EXISTING PROJECTILE FUNCTIONS
    # -------------------------------

    def get_projectile_data(self, speed, angle):
        vx, vy = calculate_projectile_velocity(speed, angle)
        flight_time = calculate_flight_time(speed, angle)
        max_height = calculate_max_height(speed, angle)
        range_value = calculate_range(speed, angle)

        return {
            "vx": vx,
            "vy": vy,
            "flight_time": flight_time,
            "max_height": max_height,
            "range": range_value
        }

    # -------------------------------
    # NEW REAL-TIME FUNCTION
    # -------------------------------

    def process_landmarks(self, pose_landmarks, timestamp):

        # MediaPipe Pose landmark indexes
        LEFT_SHOULDER = 11
        LEFT_ELBOW = 13
        LEFT_WRIST = 15

        LEFT_HIP = 23
        LEFT_KNEE = 25
        LEFT_ANKLE = 27

        # Make sure enough landmarks are available
        if len(pose_landmarks) < 28:
            return {
                "elbow_angle": 0.0,
                "knee_angle": 0.0,
                "velocity": 0.0,
                "acceleration": 0.0
            }

        # Get landmark coordinates
        shoulder = (
            pose_landmarks[LEFT_SHOULDER].x,
            pose_landmarks[LEFT_SHOULDER].y
        )

        elbow = (
            pose_landmarks[LEFT_ELBOW].x,
            pose_landmarks[LEFT_ELBOW].y
        )

        wrist = (
            pose_landmarks[LEFT_WRIST].x,
            pose_landmarks[LEFT_WRIST].y
        )

        hip = (
            pose_landmarks[LEFT_HIP].x,
            pose_landmarks[LEFT_HIP].y
        )

        knee = (
            pose_landmarks[LEFT_KNEE].x,
            pose_landmarks[LEFT_KNEE].y
        )

        ankle = (
            pose_landmarks[LEFT_ANKLE].x,
            pose_landmarks[LEFT_ANKLE].y
        )

        # Calculate angles
        elbow_angle = self.get_elbow_angle(
            shoulder,
            elbow,
            wrist
        )

        knee_angle = self.get_knee_angle(
            hip,
            knee,
            ankle
        )

        # Wrist position is used for movement calculation
        current_position = wrist

        velocity = 0.0
        acceleration = 0.0

        # Calculate velocity and acceleration
        if (
            self.previous_position is not None
            and self.previous_timestamp is not None
        ):

            dt = timestamp - self.previous_timestamp

            if dt > 0:

                velocity = self.get_velocity(
                    self.previous_position,
                    current_position,
                    dt
                )

                acceleration = self.get_acceleration(
                    self.previous_velocity,
                    velocity,
                    dt
                )

        # Store current values for next frame
        self.previous_position = current_position
        self.previous_velocity = velocity
        self.previous_timestamp = timestamp

        # Return real-time physics values
        return {
            "elbow_angle": elbow_angle,
            "knee_angle": knee_angle,
            "velocity": velocity,
            "acceleration": acceleration
        }