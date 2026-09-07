from angles import (
    calculate_elbow_angle,
    calculate_knee_angle,
    calculate_shoulder_angle
)

from velocity import (
    calculate_distance,
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
        self.previous_position = None
        self.previous_velocity = 0.0

    # --------------------------------
    # ANGLE CALCULATIONS
    # --------------------------------

    def get_elbow_angle(self, shoulder, elbow, wrist):
        return calculate_elbow_angle(
            shoulder,
            elbow,
            wrist
        )

    def get_knee_angle(self, hip, knee, ankle):
        return calculate_knee_angle(
            hip,
            knee,
            ankle
        )

    def get_shoulder_angle(self, hip, shoulder, elbow):
        return calculate_shoulder_angle(
            hip,
            shoulder,
            elbow
        )

    # --------------------------------
    # VELOCITY
    # --------------------------------

    def get_velocity(self, previous_position, current_position, dt):

        return calculate_velocity(
            previous_position,
            current_position,
            dt
        )

    # --------------------------------
    # ACCELERATION
    # --------------------------------

    def get_acceleration(
        self,
        previous_velocity,
        current_velocity,
        dt
    ):

        return calculate_acceleration(
            previous_velocity,
            current_velocity,
            dt
        )

    # --------------------------------
    # PROJECTILE MOTION
    # --------------------------------

    def get_projectile_data(self, speed, angle):

        vx, vy = calculate_projectile_velocity(
            speed,
            angle
        )

        flight_time = calculate_flight_time(
            speed,
            angle
        )

        max_height = calculate_max_height(
            speed,
            angle
        )

        range_value = calculate_range(
            speed,
            angle
        )

        return {
            "horizontal_velocity": vx,
            "vertical_velocity": vy,
            "flight_time": flight_time,
            "maximum_height": max_height,
            "range": range_value
        }
